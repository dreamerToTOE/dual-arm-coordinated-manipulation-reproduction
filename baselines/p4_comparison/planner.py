"""One bounded bidirectional-tree shell shared by RSS, PCS and NR.

Every accepted tree edge has full strategy-specific RBS qualification.  This is
a joint-space geometric planner, not a timed trajectory or robot controller.
"""

import time

import numpy as np

from .strategies import ProjectResult, Strategy, configured, rbs_connect


def _q_list(q):
    return [float(value) for value in q]


def plan(model, env, method, seed, max_iterations, config=None):
    """Return JSON-compatible raw search, edge, projection and path evidence.

Timing covers model/strategy/search/qualification work, excluding conversion of
the terminal result and file output. PCG64 is actually instantiated with seed.
No goal bias, direct-connection shortcut, path smoothing or hidden retries.
"""
    cfg = configured(config)
    if isinstance(max_iterations, bool) or int(max_iterations) != max_iterations or max_iterations <= 0:
        raise ValueError("a positive explicit outer-iteration budget is required")
    if isinstance(seed, bool) or int(seed) != seed or seed < 0:
        raise ValueError("a nonnegative explicit seed is required")
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    started = time.perf_counter()
    deadline = started + cfg["max_compute_wall_sec"]
    expired = lambda: time.perf_counter() >= deadline
    strategy = Strategy(model, env, method, cfg, rng=rng, expired=expired)
    trees = [[{"q": model.start.copy(), "parent": None, "incoming_attempt": None}],
             [{"q": model.goal.copy(), "parent": None, "incoming_attempt": None}]]
    attempts, samples = [], []
    root_evidence = []
    meeting = None
    counters = {"outer_iterations": 0, "growth_attempts": 0, "nearest_queries": 0,
                "nearest_distance_evaluations": 0, "samples": 0, "accepted_edges": 0,
                "extension_rejections": 0}
    status, reason = "ITERATION_LIMIT", "declared outer-iteration budget exhausted"

    def nearest(tree, q):
        counters["nearest_queries"] += 1
        counters["nearest_distance_evaluations"] += len(tree)
        # First minimum is a stable tie break; no platform-dependent NN tree.
        distances = [float(np.dot(node["q"] - q, node["q"] - q)) for node in tree]
        return int(np.argmin(distances))

    def grow(tree_index, target, iteration, mode, target_kind, *, source_target_index=None):
        nonlocal status, reason
        if expired():
            status, reason = "TIME_LIMIT", "declared compute budget exhausted"
            return None, False, True
        if sum(map(len, trees)) >= cfg["max_nodes"]:
            status, reason = "NODE_LIMIT", "declared tree-node budget exhausted"
            return None, False, True
        tree = trees[tree_index]
        near_index = nearest(tree, target)
        near = tree[near_index]["q"]
        delta = target - near
        distance = float(np.linalg.norm(delta))
        if distance <= cfg["minimum_progress_rad"]:
            # Existing exact node is connected already, not a zero-length new edge.
            return near_index, True, False
        fraction = min(1.0, cfg["extension_range_rad"] / distance)
        raw = near + fraction * delta
        before_projection = len(strategy.projection_log)
        if mode == "CONNECT" and fraction == 1.0 and target_kind == "EXISTING_TREE_NODE":
            # The other tree's node was already qualified. Keep its exact q,
            # allowing RBS to select a genuinely common PCS partition. Closing
            # it again with a random mismatched partition could change the node
            # rather than connect the two trees. RBS still requalifies everything.
            projected = ProjectResult(True, target.copy(), "EXACT_OTHER_TREE_NODE")
            projection_id = None
            candidate_source = "EXACT_QUALIFIED_OTHER_TREE_NODE"
        else:
            projected, projection_id = strategy.ordinary_candidate(raw, near, target)
            candidate_source = "STRATEGY_PROJECTED_RAW_STEER"
        counters["growth_attempts"] += 1
        attempt_index = len(attempts)
        attempt = {"attempt_index": attempt_index, "tree": "START" if tree_index == 0 else "GOAL",
                   "iteration": iteration, "mode": mode, "nearest_node": near_index,
                   "target_kind": target_kind, "target_q": _q_list(target),
                   "target_other_tree_node": source_target_index, "raw_q": _q_list(raw),
                   "candidate_projection_id": projection_id, "accepted": False, "reason": None,
                   "candidate_projection_ids": list(range(before_projection, len(strategy.projection_log))),
                   "candidate_source": candidate_source,
                   "reached": False, "connection": None}
        attempts.append(attempt)
        if not projected.success:
            attempt["reason"] = "CANDIDATE_PROJECTION:" + projected.reason
            counters["extension_rejections"] += 1
            if projected.reason == "TIME_LIMIT":
                status, reason = "TIME_LIMIT", "compute budget exhausted in projection"
                return None, False, True
            return None, False, False
        candidate = projected.q.copy()
        candidate_distance = float(np.linalg.norm(candidate - near))
        attempt.update(candidate_q=_q_list(candidate), candidate_distance_rad=candidate_distance,
                       projection_correction_rad=float(np.linalg.norm(candidate - raw)))
        if candidate_distance <= cfg["minimum_progress_rad"]:
            attempt["reason"] = "NO_PROGRESS"
            strategy.fail("NO_PROGRESS")
            counters["extension_rejections"] += 1
            return None, False, False
        reached = (fraction == 1.0 and
                   np.linalg.norm(candidate - target) <= cfg["meeting_tolerance_rad"])
        if reached:
            # Exact target copy, not relaxed closure: RBS requalifies that target.
            candidate = target.copy()
            attempt["candidate_q"] = _q_list(candidate)
        connection = rbs_connect(model, env, method, near, candidate, cfg, strategy=strategy)
        attempt["connection"] = connection
        if not connection["success"]:
            attempt["reason"] = "LOCAL_CONNECTION:" + connection["reason"]
            counters["extension_rejections"] += 1
            if strategy.expired():
                status, reason = "TIME_LIMIT", "compute budget exhausted in RBS/qualification"
                return None, False, True
            return None, False, False
        if expired():
            attempt["reason"] = "TIME_LIMIT_AFTER_EDGE_CHECK"
            status, reason = "TIME_LIMIT", "compute budget exhausted before tree insertion"
            return None, False, True
        node_index = len(tree)
        tree.append({"q": candidate, "parent": near_index, "incoming_attempt": attempt_index})
        attempt.update(accepted=True, reason="DISCRETE_EDGE_QUALIFIED", reached=reached,
                       added_node=node_index, edge_partition=connection["partition"],
                       edge_branch=connection["branch"])
        counters["accepted_edges"] += 1
        return node_index, reached, False

    try:
        for q in (model.start, model.goal):
            root_evidence.append(strategy.qualify(q))
        if not root_evidence[0]["valid"]:
            status, reason = "START_REJECTED", root_evidence[0]["reason"]
        elif not root_evidence[1]["valid"]:
            status, reason = "GOAL_REJECTED", root_evidence[1]["reason"]
        elif np.array_equal(model.start, model.goal):
            status, reason = "SUCCESS", "identical qualified roots"
            meeting = (0, 0)
        else:
            for iteration in range(int(max_iterations)):
                if expired():
                    status, reason = "TIME_LIMIT", "declared compute budget exhausted"
                    break
                counters["outer_iterations"] = iteration + 1
                active, other = iteration % 2, 1 - iteration % 2
                target, target_kind = strategy.target_sample()
                counters["samples"] += 1
                if target is None:
                    samples.append({"iteration": iteration, "kind": target_kind, "q": None})
                    if target_kind == "TIME_LIMIT":
                        status, reason = "TIME_LIMIT", "compute budget exhausted in sampling"
                        break
                    continue
                samples.append({"iteration": iteration, "kind": target_kind, "q": _q_list(target)})
                active_index, _, stop = grow(active, target, iteration, "EXTEND", target_kind)
                if stop:
                    break
                if active_index is None:
                    continue
                target_existing = trees[active][active_index]["q"].copy()
                for _ in range(cfg["connect_attempts"]):
                    other_index, reached, stop = grow(other, target_existing, iteration, "CONNECT",
                                                      "EXISTING_TREE_NODE", source_target_index=active_index)
                    if stop or other_index is None:
                        break
                    if reached:
                        meeting = ((active_index, other_index) if active == 0
                                   else (other_index, active_index))
                        status, reason = "SUCCESS", "two qualified trees reached one exact configuration"
                        break
                if stop or meeting is not None:
                    break
            else:
                status, reason = "ITERATION_LIMIT", "declared outer-iteration budget exhausted"
    except Exception as error:
        # Preserve all preceding scientific evidence. The runner decides whether
        # this is an interface defect eligible for a recorded correction round.
        status, reason = "INTERNAL_ERROR", type(error).__name__ + ": " + str(error)

    path, path_edges, milestones = [], [], []
    path_metrics = None
    if meeting is not None and status == "SUCCESS":
        def root_edges(side, index):
            result = []
            while trees[side][index]["parent"] is not None:
                node = trees[side][index]
                result.append(node["incoming_attempt"])
                index = node["parent"]
            return list(reversed(result))

        start_edges, goal_edges = root_edges(0, meeting[0]), root_edges(1, meeting[1])
        path = [_q_list(model.start)]
        milestones = [_q_list(model.start)]
        for side, indices, reverse in ((0, start_edges, False), (1, list(reversed(goal_edges)), True)):
            for identity in indices:
                attempt = attempts[identity]
                edge_path = attempt["connection"]["path"]
                if reverse:
                    edge_path = list(reversed(edge_path))
                if not np.allclose(path[-1], edge_path[0], rtol=0.0, atol=1e-12):
                    status, reason = "INTERNAL_ERROR", "path edge provenance does not meet exactly"
                    break
                path.extend(edge_path[1:])
                milestones.append(edge_path[-1])
                path_edges.append({"attempt_index": identity, "tree": "START" if side == 0 else "GOAL",
                                   "reversed": reverse, "partition": attempt["edge_partition"],
                                   "branch": attempt["edge_branch"], "point_count": len(edge_path),
                                   "qualification": "FULL_DISCRETE_RBS"})
            if status != "SUCCESS":
                break
        if status == "SUCCESS":
            states = [strategy.qualify(np.asarray(q)) for q in path]
            if not all(state["valid"] for state in states):
                # Time exhaustion during independent recheck cannot promote an
                # incompletely rechecked path to SUCCESS.
                failing = next(state for state in states if not state["valid"])
                status = "TIME_LIMIT" if failing["reason"] == "TIME_LIMIT" else "PATH_RECHECK_REJECTED"
                reason = "terminal path recheck: " + failing["reason"]
            else:
                array = np.asarray(path)
                d = np.diff(array, axis=0)
                path_metrics = {"joint_path_length_rad": float(np.linalg.norm(d, axis=1).sum()),
                                "milestone_path_length_rad": float(np.linalg.norm(np.diff(np.asarray(milestones), axis=0), axis=1).sum()),
                                "point_count": len(path), "edge_count": len(path_edges),
                                "maximum_position_residual_m": max(x["closure_position"] for x in states),
                                "maximum_rotation_residual_rad": max(x["closure_angle"] for x in states),
                                "minimum_joint_margin_rad": min(x["joint_margin"] for x in states),
                                "minimum_clearance_m": min(x["collision"]["minimum_clearance"] for x in states),
                                "maximum_adjacent_l2_rad": float(np.max(np.linalg.norm(d, axis=1))) if len(d) else 0.0,
                                "maximum_adjacent_linf_rad": float(np.max(np.abs(d))) if len(d) else 0.0,
                                "state_qualifications": states,
                                "collision_source": "real GEOS planar capsule/circle query",
                                "safety_scope": "DISCRETE_CONFIGURATIONS_NOT_CONTINUOUS_SWEEP"}
    elapsed = time.perf_counter() - started
    # Do not pretend a failed/partial path is a qualified solution.
    qualified_path = path if status == "SUCCESS" else []
    result = {"schema": "p4_three_methods.plan.v1", "method": method, "environment": env,
              "seed": int(seed), "rng": "NumPy Generator(PCG64)", "max_iterations": int(max_iterations),
              "config": cfg, "status": status, "terminal_reason": reason,
              "compute_wall_time_sec": elapsed, "time_scope": "search/projection/RBS/model queries/recheck; excludes result serialization and file output",
              "root_evidence": root_evidence, "start": _q_list(model.start), "goal": _q_list(model.goal),
              "trees": {"START": [{**node, "q": _q_list(node["q"])} for node in trees[0]],
                        "GOAL": [{**node, "q": _q_list(node["q"])} for node in trees[1]]},
              "node_count": sum(map(len, trees)), "meeting": None if meeting is None else list(meeting),
              "samples": samples, "attempts": attempts, "projection_log": strategy.projection_log,
              "singular_log": strategy.singular_log,
              "counters": {**counters, **strategy.counters}, "failure_counts": strategy.failure_counts,
              "path": qualified_path, "path_milestones": milestones if status == "SUCCESS" else [],
              "path_edges": path_edges if status == "SUCCESS" else [], "path_metrics": path_metrics,
              "partial_path_for_diagnosis": path if status != "SUCCESS" else [],
              "qualification": "NO_EXECUTION_GEOMETRIC_DISCRETE_PATH" if status == "SUCCESS" else "NO_QUALIFIED_PATH",
              "minimum_distance_source": "GEOS distances; not legacy FCL/PQP and not a sweep certificate"}
    return result
