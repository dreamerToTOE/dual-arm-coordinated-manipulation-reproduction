"""P4 strategy operators in the independently specified planar 20R model.

[ORIGINAL] Moore--Penrose NR, one-passive-chain RSS and common-branch PCS.
[ADAPTATION] Three independent planar residuals, periodic joint coordinates.
[ENGINEERING] Explicit finite limits and complete accepted/failed local evidence.
This module never imports or invokes ROS, MoveIt, Isaac or a robot executor.
"""

from dataclasses import dataclass, field
import math
import time

import numpy as np


DEFAULT_CONFIG = {
    "extension_range_rad": 0.6,
    "rbs_resolution_rad": 0.05,
    "rbs_max_depth": 20,
    "rbs_max_projections": 4096,
    "nr_max_iterations": 100,
    "position_tolerance_m": 1e-8,
    "rotation_tolerance_rad": 1e-8,
    "svd_absolute_cutoff": 1e-12,
    "svd_relative_cutoff": 1e-10,
    "stagnation_step_rad": 1e-14,
    "max_nodes": 2000,
    "connect_attempts": 25,
    "max_compute_wall_sec": 5.0,
    "singular_attempts": 32,
    "singular_probability": 0.2,
    "minimum_progress_rad": 1e-12,
    "meeting_tolerance_rad": 1e-9,
}


def configured(config=None):
    result = dict(DEFAULT_CONFIG)
    if config is not None:
        unknown = set(config) - set(result)
        if unknown:
            raise ValueError("unknown algorithm config keys: " + repr(sorted(unknown)))
        result.update(config)
    for name in ("extension_range_rad", "rbs_resolution_rad", "position_tolerance_m",
                 "rotation_tolerance_rad", "svd_relative_cutoff", "max_compute_wall_sec",
                 "minimum_progress_rad", "meeting_tolerance_rad"):
        if not math.isfinite(result[name]) or result[name] <= 0:
            raise ValueError("invalid positive option " + name)
    for name in ("rbs_max_depth", "rbs_max_projections", "nr_max_iterations", "max_nodes",
                 "connect_attempts", "singular_attempts"):
        if isinstance(result[name], bool) or int(result[name]) != result[name] or result[name] <= 0:
            raise ValueError("invalid integer option " + name)
    if result["max_nodes"] < 2 or result["rbs_max_depth"] > 64:
        raise ValueError("invalid node/depth limits")
    if not 0 <= result["singular_probability"] <= 1:
        raise ValueError("invalid singular probability")
    for name in ("svd_absolute_cutoff", "stagnation_step_rad"):
        if not math.isfinite(result[name]) or result[name] < 0:
            raise ValueError("invalid nonnegative option " + name)
    return result


def wrap(q):
    """Periodic coordinate representative; not joint-limit clamping."""
    return (np.asarray(q, dtype=float) + np.pi) % (2 * np.pi) - np.pi


def _numbers(q):
    return [float(x) for x in np.asarray(q).ravel()]


def _norms(residual):
    return {"position_m": float(np.linalg.norm(residual[:2])),
            "rotation_rad": float(abs(residual[2]))}


def _converged(residual, config):
    return (np.linalg.norm(residual[:2]) <= config["position_tolerance_m"] and
            abs(residual[2]) <= config["rotation_tolerance_rad"])


@dataclass
class ProjectResult:
    success: bool
    q: np.ndarray | None
    reason: str
    trace: list = field(default_factory=list)
    partition: int | None = None
    branch: int | None = None
    initial_q: np.ndarray | None = None

    def evidence(self):
        return {"success": self.success, "reason": self.reason,
                "partition": self.partition, "branch": self.branch,
                "initial_q": None if self.initial_q is None else _numbers(self.initial_q),
                "q": None if self.q is None else _numbers(self.q), "trace": self.trace}


def nr_project(model, q, config=None, *, expired=lambda: False, count=None):
    """Full planar Jacobian SVD update, with separate metre/radian acceptance.

The accepted historical NR update math is reused, not its FR3-specific rank6
guard. Singular values below the stated cutoff have zero pseudoinverse weight;
the actual rank is recorded. A rank-deficient residual may still be correctable.
No damping, row weighting, line search or random restart is used.
"""
    cfg = configured(config)
    initial = np.asarray(q, dtype=float).copy()
    q = initial.copy()
    history = []
    if count is not None:
        count("nr_calls")

    def end(success, reason):
        if count is not None and not success:
            count("nr_failures")
        return ProjectResult(success, q.copy(), reason, history, initial_q=initial)

    if q.shape != (model.n,) or not np.all(np.isfinite(q)):
        return end(False, "INVALID_INPUT")
    if np.any(q < -np.pi) or np.any(q > np.pi):
        return end(False, "INITIAL_JOINT_LIMIT")
    for update in range(cfg["nr_max_iterations"] + 1):
        if expired():
            return end(False, "TIME_LIMIT")
        residual = np.asarray(model.closure(q), dtype=float)
        if count is not None:
            count("constraint_evaluations")
        if residual.shape != (3,) or not np.all(np.isfinite(residual)):
            return end(False, "NONFINITE_EVALUATION")
        sample = {"update_index": update, "residual": _numbers(residual), **_norms(residual)}
        if _converged(residual, cfg):
            sample["converged"] = True
            history.append(sample)
            return end(True, "CONVERGED")
        if update == cfg["nr_max_iterations"]:
            history.append(sample)
            return end(False, "ITERATION_LIMIT")
        jac = np.asarray(model.jacobian(q), dtype=float)
        if count is not None:
            count("jacobian_evaluations")
        if jac.shape != (3, model.n) or not np.all(np.isfinite(jac)):
            history.append(sample)
            return end(False, "NONFINITE_JACOBIAN")
        try:
            u, sigma, vt = np.linalg.svd(jac, full_matrices=False)
        except np.linalg.LinAlgError:
            history.append(sample)
            return end(False, "SVD_ERROR")
        cutoff = max(cfg["svd_absolute_cutoff"], cfg["svd_relative_cutoff"] * sigma[0])
        active = sigma > cutoff
        inverse = np.divide(1.0, sigma, out=np.zeros_like(sigma), where=active)
        sample.update(singular_values=_numbers(sigma), cutoff=float(cutoff),
                      numerical_rank=int(np.count_nonzero(active)))
        if not np.any(active):
            history.append(sample)
            return end(False, "RANK_ZERO")
        delta = -(vt.T @ (inverse * (u.T @ residual)))
        sample["delta_q"] = _numbers(delta)
        if not np.all(np.isfinite(delta)):
            history.append(sample)
            return end(False, "NONFINITE_UPDATE")
        next_q = wrap(q + delta)
        if np.linalg.norm(delta) <= cfg["stagnation_step_rad"] or np.array_equal(q, next_q):
            history.append(sample)
            return end(False, "STAGNATION")
        # Every update is a finite periodic representation inside native limits.
        # This is wrap, not clamp; the trace preserves the unwrapped Newton delta.
        sample["update_accepted"] = True
        history.append(sample)
        q = next_q
        if count is not None:
            count("nr_updates")
    raise AssertionError("bounded Newton loop fell through")


class Strategy:
    def __init__(self, model, env, method, config=None, *, rng=None, expired=lambda: False):
        if method not in ("RSS", "PCS", "PCS_FIXED_0", "PCS_FIXED_16", "NR"):
            raise ValueError("unknown P4 strategy")
        if method == "PCS_FIXED_0" and 0 not in model.partitions:
            raise ValueError("fixed PCS partition 0 is not declared by this model")
        if method == "PCS_FIXED_16" and 16 not in model.partitions:
            raise ValueError("fixed PCS partition 16 is not declared by this model")
        self.model, self.env, self.method = model, env, method
        self.config = configured(config)
        self.rng = rng if rng is not None else np.random.Generator(np.random.PCG64(0))
        self.expired = expired
        self.counters = {}
        self.failure_counts = {}
        self.projection_log = []
        self.singular_log = []

    def count(self, key, amount=1):
        self.counters[key] = self.counters.get(key, 0) + amount

    def fail(self, reason):
        self.failure_counts[reason] = self.failure_counts.get(reason, 0) + 1

    def qualify(self, q):
        if self.expired():
            return {"valid": False, "reason": "TIME_LIMIT"}
        self.count("state_qualification_calls")
        result = self.model.valid(q, self.env)
        collision = result.get("collision") or {}
        if collision:
            self.count("collision_queries")
            self.count("geometry_queries", collision.get("geometry_queries", 0))
        if collision.get("collision"):
            self.count("collision_rejections")
        if not result["valid"]:
            self.fail(result["reason"])
        return result

    def project(self, q, partition=None, branch=None, *, phase):
        self.count("projection_calls")
        if self.method == "NR":
            result = nr_project(self.model, q, self.config, expired=self.expired, count=self.count)
        else:
            if self.method == "RSS":
                allowed = (16,)
            elif self.method.startswith("PCS_FIXED_"):
                allowed = (int(self.method.rsplit("_", 1)[1]),)
            else:
                allowed = self.model.partitions
            if partition not in allowed:
                raise ValueError("method cannot use this passive chain")
            self.count("ik_calls")
            if self.expired():
                result = ProjectResult(False, None, "TIME_LIMIT", partition=partition, branch=branch,
                                       initial_q=np.asarray(q).copy())
            else:
                residual = self.model.closure(q)
                existing_branch = self.model.branch(q, partition)
                # Exact singular inputs belong to both incident analytic branches.
                # Re-solving them with acos(D) could introduce roundoff that
                # destroys their exact singular identity. Acceptance uses the
                # same unchanged residual and native-joint criteria, and RBS
                # still performs real geometry qualification.
                if (_converged(residual, self.config) and existing_branch in (0, branch) and
                        np.all(np.asarray(q) >= -np.pi) and np.all(np.asarray(q) <= np.pi)):
                    result = ProjectResult(True, np.asarray(q).copy(), "ALREADY_CLOSED_BRANCH",
                                           [{"residual": _numbers(residual),
                                             "observed_branch": existing_branch}],
                                           partition, branch, np.asarray(q).copy())
                    self.count("already_closed_apc_inputs")
                else:
                    self.count("ik_solver_calls")
                    ik = self.model.ik(q, partition, branch)
                    result = ProjectResult(bool(ik.success), None if ik.q is None else ik.q.copy(),
                                           ik.reason, [{"cosine": ik.cosine}], partition, branch,
                                           np.asarray(q).copy())
                    if not result.success:
                        self.count("ik_failures")
        if not result.success:
            self.count("projection_failures")
            self.fail(result.reason)
        record = result.evidence()
        record["phase"] = phase
        record["projection_id"] = len(self.projection_log)
        self.projection_log.append(record)
        return result, record["projection_id"]

    def ordinary_candidate(self, raw, near, target):
        """Source-audited APC choice/fallback; never falls back to NR.

        PCS first chooses a passive partition using the actual seeded RNG. If
        its analytic closure fails, it tries the other available partition once
        as the authors' CBiRRT_PCS does. Both projection records are preserved.
        """
        if self.method == "NR":
            projected, identity = self.project(raw, phase="TREE_CANDIDATE")
            return projected, identity
        if self.method == "RSS":
            partitions = (16,)
        elif self.method.startswith("PCS_FIXED_"):
            partitions = (int(self.method.rsplit("_", 1)[1]),)
        else:
            first_partition = int(self.rng.choice(self.model.partitions))
            self.count("partition_choices")
            self.count("rng_draws")
            partitions = (first_partition,) + tuple(p for p in self.model.partitions if p != first_partition)
        for choice_index, partition in enumerate(partitions):
            branch = self.model.branch(near, partition)
            if branch == 0:
                branch = self.model.branch(target, partition)
                if branch == 0:
                    self.count("rng_draws")
                    branch = int(self.rng.choice((-1, 1)))
            if choice_index:
                self.count("pcs_other_partition_retries")
            result, identity = self.project(raw, partition, branch, phase="TREE_CANDIDATE")
            self.projection_log[identity]["partition_choice_index"] = choice_index
            self.projection_log[identity]["partition_order"] = list(partitions)
            if result.success or result.reason == "TIME_LIMIT":
                return result, identity
        return result, identity

    def target_sample(self):
        self.count("ambient_samples")
        if self.method == "RSS":
            self.count("rng_draws")
            singular_request = self.rng.random() < self.config["singular_probability"]
        else:
            singular_request = False
        if singular_request:
            self.count("singular_sample_requests")
            for attempt in range(self.config["singular_attempts"]):
                if self.expired():
                    return None, "TIME_LIMIT"
                raw = self.rng.uniform(-np.pi, np.pi, self.model.n)
                self.count("rng_draws", self.model.n + 2)
                # Fixed RSS passive middle joint is truly straight or folded.
                raw[17] = float(self.rng.choice((0.0, np.pi)))
                branch = int(self.rng.choice((-1, 1)))
                self.count("singular_construction_attempts")
                self.count("ik_calls")
                self.count("ik_solver_calls")
                ik = self.model.ik(raw, 0, branch)
                record = {"attempt": attempt, "generator_partition": 0,
                          "generator_branch": branch, "rss_partition": 16,
                          "raw_q": _numbers(raw), "reason": ik.reason, "success": False}
                if ik.success:
                    qualification = self.qualify(ik.q)
                    record.update(q=_numbers(ik.q), qualification=qualification)
                    if qualification["valid"] and self.model.branch(ik.q, 16) == 0:
                        self.count("singular_samples")
                        record["success"] = True
                        self.singular_log.append(record)
                        return ik.q.copy(), "SINGULAR"
                else:
                    self.count("ik_failures")
                self.singular_log.append(record)
            self.count("singular_sample_failures")
            self.fail("SINGULAR_SAMPLER_BUDGET")
            # Failed singular requests do not secretly become ambient samples.
            return None, "SINGULAR_SAMPLER_BUDGET"
        self.count("rng_draws", self.model.n)
        return self.rng.uniform(-np.pi, np.pi, self.model.n), "AMBIENT"

    def connection_choices(self, start, goal):
        if self.method == "NR":
            return [(None, None)]
        if self.method == "RSS":
            partitions = (16,)
        elif self.method.startswith("PCS_FIXED_"):
            partitions = (int(self.method.rsplit("_", 1)[1]),)
        else:
            partitions = self.model.partitions
        choices = []
        for partition in partitions:
            a, b = self.model.branch(start, partition), self.model.branch(goal, partition)
            if a == b or a == 0 or b == 0:
                choices.append((int(partition), int(a or b or 1)))
        return choices


def rbs_connect(model, env, method, start, goal, config=None, *, strategy=None):
    """Qualify every recursive midpoint; return full evidence and ordered prefix.

RSS singular endpoints are eligible for either incident branch. Unlike the old
author-specific RSS shortcut, no endpoint-distance threshold skips qualification.
"""
    s = strategy if strategy is not None else Strategy(model, env, method, config)
    s.count("local_connection_calls")
    start, goal = np.asarray(start, dtype=float), np.asarray(goal, dtype=float)
    started = time.perf_counter()
    trials = []
    total_projections = 0
    last_reason = "NO_COMMON_PASSIVE_BRANCH"
    if (start.shape != (model.n,) or goal.shape != (model.n,) or
            not np.all(np.isfinite(start)) or not np.all(np.isfinite(goal))):
        s.count("local_connection_failures")
        s.fail("INVALID_INPUT")
        return {"success": False, "reason": "INVALID_INPUT", "trials": [], "path": [],
                "verified_prefix": [], "projection_calls": 0,
                "compute_wall_time_sec": time.perf_counter() - started}
    choices = s.connection_choices(start, goal)
    if not choices:
        s.count("local_connection_failures")
        s.fail(last_reason)
        return {"success": False, "reason": last_reason, "trials": [], "path": [],
                "verified_prefix": [], "projection_calls": 0,
                "compute_wall_time_sec": time.perf_counter() - started}

    for partition, branch in choices:
        checked, prefix, leaf_edges = [], [], []
        trial = {"partition": partition, "branch": branch, "checked_points": checked,
                 "leaf_edges": leaf_edges, "success": False, "reason": None}
        trials.append(trial)
        per_trial_projections = 0
        failed_reason = None

        def add(q, role, depth, projection_id=None):
            evidence = s.qualify(q)
            index = len(checked)
            checked.append({"q": _numbers(q), "role": role, "depth": depth,
                            "projection_id": projection_id, "qualification": evidence})
            return index, evidence

        def segment(a, b, depth):
            nonlocal failed_reason, total_projections, per_trial_projections
            if s.expired():
                failed_reason = "TIME_LIMIT"
                return False
            qa, qb = np.asarray(checked[a]["q"]), np.asarray(checked[b]["q"])
            distance = float(np.linalg.norm(qb - qa))
            if distance <= s.config["rbs_resolution_rad"]:
                leaf_edges.append({"from": a, "to": b, "distance_rad": distance,
                                   "qualified": True})
                prefix.append(b)
                return True
            if depth >= s.config["rbs_max_depth"]:
                failed_reason = "RBS_DEPTH_LIMIT"
                return False
            # One connection call owns one total midpoint budget, including all
            # PCS partition trials. Trying a second partition cannot double it.
            if total_projections >= s.config["rbs_max_projections"]:
                failed_reason = "RBS_PROJECTION_LIMIT"
                return False
            seed = (qa + qb) * 0.5
            projected, projection_id = s.project(seed, partition, branch, phase="RBS_MIDPOINT")
            total_projections += 1
            per_trial_projections += 1
            s.count("rbs_midpoint_projections")
            if not projected.success:
                failed_reason = "RBS_PROJECTION:" + projected.reason
                checked.append({"q": None if projected.q is None else _numbers(projected.q),
                                "seed_q": _numbers(seed), "role": "REJECTED_MIDPOINT",
                                "depth": depth + 1, "projection_id": projection_id,
                                "qualification": {"valid": False, "reason": failed_reason}})
                return False
            mid, qualification = add(projected.q, "PROJECTED_MIDPOINT", depth + 1, projection_id)
            if not qualification["valid"]:
                failed_reason = "RBS_STATE:" + qualification["reason"]
                return False
            if partition is not None and model.branch(projected.q, partition) not in (0, branch):
                failed_reason = "RBS_BRANCH_MISMATCH"
                return False
            return segment(a, mid, depth + 1) and segment(mid, b, depth + 1)

        a, start_evidence = add(start, "EXACT_START", 0)
        if not start_evidence["valid"]:
            failed_reason = "START:" + start_evidence["reason"]
        else:
            prefix.append(a)
            b, goal_evidence = add(goal, "EXACT_GOAL", 0)
            if not goal_evidence["valid"]:
                failed_reason = "GOAL:" + goal_evidence["reason"]
            elif segment(a, b, 0):
                path = [checked[i]["q"] for i in prefix]
                trial.update(success=True, reason="DISCRETE_RBS_QUALIFIED",
                             verified_prefix_indices=prefix, projection_calls=per_trial_projections)
                s.count("local_connections_accepted")
                if method == "RSS" and (model.branch(start, 16) == 0 or model.branch(goal, 16) == 0):
                    s.count("rss_singular_endpoint_connections")
                if method == "PCS" or method.startswith("PCS_FIXED_"):
                    s.count("pcs_partition_" + str(partition) + "_connections")
                return {"success": True, "reason": "DISCRETE_RBS_QUALIFIED", "partition": partition,
                        "branch": branch, "trials": trials, "path": path,
                        "verified_prefix": path, "projection_calls": total_projections,
                        "compute_wall_time_sec": time.perf_counter() - started,
                        "qualification": "DISCRETE_POINTS_ONLY_NOT_CONTINUOUS_SWEEP"}
        last_reason = failed_reason or "UNKNOWN_RBS_REJECTION"
        trial.update(reason=last_reason, verified_prefix_indices=prefix,
                     projection_calls=per_trial_projections)
        if last_reason == "TIME_LIMIT" or last_reason.endswith(":TIME_LIMIT"):
            break
    s.count("local_connection_failures")
    s.fail(last_reason)
    last = trials[-1]
    return {"success": False, "reason": last_reason, "trials": trials, "path": [],
            "verified_prefix": [last["checked_points"][i]["q"] for i in last["verified_prefix_indices"]],
            "projection_calls": total_projections,
            "compute_wall_time_sec": time.perf_counter() - started,
            "qualification": "FAILED_CONNECTION_PREFIX_NOT_A_SOLUTION"}
