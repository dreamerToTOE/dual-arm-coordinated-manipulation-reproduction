#!/usr/bin/env python3
"""Qualify RECONSTRUCTED endpoints from immutable R2 saved analytic roots.

No IK, NR, random sampler or planner is called. The original vectors and all
saved branch attempts remain in the output. Execution requires a frozen JSON
protocol and a new run directory. Importing this module performs no execution.
"""
from __future__ import annotations

import argparse
from collections import Counter
import datetime as dt
import hashlib
import itertools
import json
import math
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np

from baselines.p4_full.abb_independent_oracle import abb_fk_and_jacobian
from baselines.p4_full.analyze_comau_native_qualification import geometry, serial_fk

AUTHOR_PI = 3.1416
FLIP = np.diag([-1.0, -1.0, 1.0, 1.0])
ELBOW_SIGN = (1, -1, 1, -1, 1, -1, 1, -1)
WRIST_SIGN = (1, -1, -1, 1, -1, 1, 1, -1)
SOURCE_RUNS = {
    "I": "results/p4_full/20261015_R2_PLANAR01/I_geometry_consistent_raw.jsonl",
    **{e: f"results/p4_full/20261015_R2_SPATIAL01/{e}/observations.json"
       for e in ("II", "III", "IV", "V", "VI")},
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cpu_seconds():
    own = resource.getrusage(resource.RUSAGE_SELF)
    child = resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + own.ru_stime + child.ru_utime + child.ru_stime


def save_new(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


class Budget:
    def __init__(self, wall_s, cpu_s):
        self.started = time.monotonic()
        self.cpu_start = cpu_seconds()
        self.wall_limit = wall_s
        self.cpu_limit = cpu_s

    def check(self):
        if time.monotonic() - self.started >= self.wall_limit:
            raise TimeoutError("ENDPOINT_WALL_LIMIT")
        if cpu_seconds() - self.cpu_start >= self.cpu_limit:
            raise TimeoutError("ENDPOINT_CPU_LIMIT")

    def remaining(self):
        self.check()
        return min(self.wall_limit-(time.monotonic()-self.started),
                   self.cpu_limit-(cpu_seconds()-self.cpu_start))


def bounds_for(environment):
    """Independent transcription of the pinned source validity limits."""
    if environment == "I":
        bound = AUTHOR_PI * 179.9 / 180.0
        return [(-bound, bound)] * 19 + [(0.0, 2.0 * AUTHOR_PI)]
    if environment in ("II", "III"):
        degrees = [(-165, 165), (-110, 110), (-110, 70),
                   (-160, 160), (-120, 120), (-400, 400)]
    else:
        degrees = [(-180, 180), (-60, 125), (-90, 75),
                   (-2700, 2700), (-120, 120), (-400, 400)]
    return [(lo * AUTHOR_PI / 180.0, hi * AUTHOR_PI / 180.0)
            for lo, hi in degrees] * (3 if environment == "VI" else 2)


def limit_score(q, environment):
    bounds = bounds_for(environment)
    violations = [{"index": i, "q_rad": value, "lower_rad": lo, "upper_rad": hi}
                  for i, (value, (lo, hi)) in enumerate(zip(q, bounds))
                  if not lo <= value <= hi]
    return {"legal": not violations, "violations": violations,
            "source_literal_pi_preserved": AUTHOR_PI,
            "planar_q19_policy": "source run chart intersect planner validity"
            if environment == "I" else None}


def arm_fk(q, environment, arm):
    if environment in ("II", "III"):
        distance = 900.0 if environment == "II" else 1200.0
        base = [-distance / 2, 0.0, 0.0] if arm == 1 else [distance / 2, 0.0, AUTHOR_PI]
        return abb_fk_and_jacobian(q, base)[0]
    return serial_fk(q, {"IV": 4, "V": 5, "VI": 6}[environment], arm)


def grasps_for(environment):
    if environment in ("II", "III"):
        grasp = np.eye(4)
        grasp[0, 3] = 300.0 if environment == "II" else 500.0
        return [grasp]
    return geometry({"IV": 4, "V": 5, "VI": 6}[environment])["grasps"]


def matrix_error(actual, target):
    difference = np.asarray(actual) - np.asarray(target)
    return {"position_max_abs": float(np.max(np.abs(difference[:3, 3]))),
            "rotation_matrix_max_abs": float(np.max(np.abs(difference[:3, :3])))}


def planar_metrics(q):
    """Independent cumulative point sum and a separate 3x3 matrix product."""
    angles = [math.fsum(q[:i + 1]) for i in range(19)]
    phi = math.fsum([*q[:19], AUTHOR_PI, -q[19]])
    cumulative = {"position_max_abs": max(abs(math.fsum(math.cos(a) for a in angles) - 7),
                                          abs(math.fsum(math.sin(a) for a in angles) - 4)),
                  "rotation_matrix_max_abs": max(abs(math.sin(phi)), abs(math.cos(phi) - 1))}
    product = np.eye(3)
    for angle in q[:19]:
        c, s = math.cos(angle), math.sin(angle)
        product = product @ np.array([[c, -s, c], [s, c, s], [0., 0., 1.]])
    c, s = math.cos(AUTHOR_PI-q[19]), math.sin(AUTHOR_PI-q[19])
    endpoint = product @ np.array([[c, -s, 0.], [s, c, 0.], [0., 0., 1.]])
    independent = {"position_max_abs": float(max(abs(endpoint[0, 2]-7), abs(endpoint[1, 2]-4))),
                   "rotation_matrix_max_abs": float(np.max(np.abs(endpoint[:2, :2]-np.eye(2))))}
    return {"position_unit": "author_normalized_link_length",
            "position_max_abs": max(cumulative["position_max_abs"], independent["position_max_abs"]),
            "rotation_matrix_max_abs": max(cumulative["rotation_matrix_max_abs"], independent["rotation_matrix_max_abs"]),
            "independent_cumulative_sum": cumulative,
            "independent_matrix_product": independent}


def closure_metrics(q, environment):
    if environment == "I":
        return planar_metrics(q)
    poses = [arm_fk(q[i:i+6], environment, i//6+1) for i in range(0, len(q), 6)]
    errors = [matrix_error(poses[i+1], poses[0] @ grasp @ FLIP)
              for i, grasp in enumerate(grasps_for(environment))]
    return {"position_unit": "mm", "loops": errors,
            "position_max_abs": max(e["position_max_abs"] for e in errors),
            "rotation_matrix_max_abs": max(e["rotation_matrix_max_abs"] for e in errors)}


def sign_or_unknown(value, scale, epsilon):
    return None if abs(value) <= epsilon * scale else (1 if value > 0 else -1)


def branch_identity(q, environment, epsilon):
    """Infer source branch from independent joint geometry, never root distance.

    Shoulder uses the signed wrist-center radius; elbow uses -sin(q3+alpha),
    and spherical wrist uses sin(q5). These are periodic geometric invariants.
    A zero factor denotes a coalesced branch set and cannot be certified unique.
    """
    if environment == "I":
        sine = math.sin(q[1])  # Frozen label 0 has standard middle angle q1.
        sign = sign_or_unknown(sine, 1.0, epsilon)
        return {"unique": sign is not None, "branch_set": [0 if sign > 0 else 1] if sign else [0, 1],
                "passive_label": 0, "canonical_middle_sine": sine,
                "invariant_rule": "label0 branch0 iff sin(q[1])>0"}
    if environment in ("II", "III"):
        l1x, l2, a, c = 0.0, 270.0, 70.0, 149.6+152.4
    else:
        l1x, l2, a, c = 524.5, 1250.0, 210.0, 186.5+1250.0
    alpha = math.atan2(c, a)
    radius = (l1x+l2*math.sin(q[1])+a*math.sin(q[1]+q[2])
              + c*math.cos(q[1]+q[2]))
    radial_sign = sign_or_unknown(radius, l1x+l2+math.hypot(a, c), epsilon)
    elbow = -math.sin(q[2]+alpha)
    wrist = math.sin(q[4])
    elbow_sign = sign_or_unknown(elbow, 1.0, epsilon)
    wrist_sign = sign_or_unknown(wrist, 1.0, epsilon)
    branches = [b for b in range(8)
                if (radial_sign is None or (1 if b < 4 else -1) == radial_sign)
                and (elbow_sign is None or ELBOW_SIGN[b] == elbow_sign)
                and (wrist_sign is None or WRIST_SIGN[b] == wrist_sign)]
    return {"unique": all(v is not None for v in (radial_sign, elbow_sign, wrist_sign)),
            "branch_set": branches, "signed_shoulder_radius_mm": radius,
            "elbow_factor": elbow, "wrist_factor": wrist,
            "shoulder_sign": radial_sign, "elbow_sign": elbow_sign, "wrist_sign": wrist_sign,
            "invariant_rule": "shoulder signed radius; -sin(q3+atan2(c,a)); sin(q5)"}


def all_lifts(base_q, original, passive, environment):
    bounds = bounds_for(environment)
    choices = []
    for i in passive:
        lo, hi = bounds[i]
        choices.append(range(math.ceil((lo-base_q[i])/math.tau),
                             math.floor((hi-base_q[i])/math.tau)+1))
    for lifts in itertools.product(*choices):
        q = list(original)
        for i, k in zip(passive, lifts):
            q[i] = base_q[i] + k*math.tau
        yield q, list(lifts)


def endpoint_sources(environment, rows):
    if environment == "I":
        raw = [r for r in rows if r["kind"] == "raw_endpoint"]
        for r in raw:
            name = r["endpoint"]
            apc = [a for a in rows if a["kind"] == "apc" and a["endpoint"] == name]
            yield name, r["q_original_unchanged"], r, apc
    else:
        for raw in (r for r in rows if r["kind"] == "raw_endpoint_unchanged"):
            fixture = [r for r in rows if r["kind"] == "additional_component_fixture_only"
                       and r["endpoint"] == raw["endpoint"]]
            if len(fixture) != 1 or fixture[0]["original_q"] != raw["q"]:
                raise ValueError("SAVED_ENDPOINT_LINEAGE_MISMATCH")
            yield raw["endpoint"], raw["q"], raw, fixture[0]["raw_branch_attempts"]


def collision_call(environment, q, budget):
    budget.check()
    try:
        from baselines.p4_full.geometry_consistent.collision_adapter import check_collision
        result = check_collision(environment, q, timeout_s=min(30., budget.remaining()))
        if not isinstance(result, dict) or result.get("collision") not in (True, False, None):
            raise ValueError("INVALID_COLLISION_ADAPTER_RESULT")
        if result.get("collision") is not None and (result.get("status") != "CHECKED"
                                                     or type(result["collision"]) is not bool):
            raise ValueError("COLLISION_RESULT_NOT_QUALIFIED_CHECKED_BOOLEAN")
        result["full_physical_geometry_or_CCD_qualified"] = False
        budget.check()
        return result
    except TimeoutError:
        raise
    except Exception as error:
        return {"collision": None, "status": "COLLISION_ADAPTER_UNAVAILABLE",
                "error": repr(error)}


def recover_endpoint(environment, name, original, raw, attempts, protocol, budget, emit):
    epsilon = protocol["branch_zero_relative_epsilon"]
    gate_p, gate_r = protocol["position_gate"], protocol["rotation_matrix_gate"]
    passive = [0, 1, 2] if environment == "I" else list(range(6, len(original)))
    active = [i for i in range(len(original)) if i not in passive]
    original_identity = {str(arm): branch_identity(original[6*(arm-1):6*arm], environment, epsilon)
                         for arm in range(2, len(original)//6+1)} if environment != "I" else {
                             "planar": branch_identity(original, environment, epsilon)}
    original_metrics = closure_metrics(original, environment)
    emit({"event": "original_endpoint", "environment": environment, "endpoint": name,
          "q_rad": original, "metrics": original_metrics, "branch_identity": original_identity})
    original_collision = collision_call(environment, original, budget)
    emit({"event": "original_collision", "result": original_collision})
    source_roots = []
    if environment == "I":
        if sorted((a["partition"], a["branch"]) for a in attempts) != [
                (p, b) for p in range(20) for b in range(2)]:
            raise ValueError("PLANAR_SAVED_BRANCH_ENUMERATION_INCOMPLETE")
        if any(a["q_original_unchanged"] != original for a in attempts):
            raise ValueError("PLANAR_SAVED_ORIGINAL_VECTOR_MISMATCH")
        for attempt in attempts:
            if attempt["partition"] != 0:
                continue  # All other partitions are preserved below, not searched for a favorable answer.
            for j, score in enumerate(attempt["candidate_scores"]):
                source_roots.append({"branch": [attempt["branch"]],
                                     "base_q": score["candidate"]["q"],
                                     "saved_root_indices": [j],
                                     "regular": score["candidate"]["source_regular_eligible"]})
    else:
        for arm in range(2, len(original)//6+1):
            if sorted(a["branch"] for a in attempts if a["arm"] == arm) != list(range(8)):
                raise ValueError("SPATIAL_SAVED_BRANCH_ENUMERATION_INCOMPLETE")
        groups = [[(i, a) for i, a in enumerate(attempts) if a["arm"] == arm and a["success"]]
                  for arm in range(2, len(original)//6+1)]
        for combination in itertools.product(*groups):
            source_roots.append({"branch": [a["branch"] for _, a in combination],
                                 "base_q": original[:6]+[v for _, a in combination for v in a["solution"]],
                                 "saved_root_indices": [i for i, _ in combination], "regular": True})
    candidates = []
    roots_audit = []
    for root_index, source in enumerate(source_roots):
        budget.check()
        if not all(source["base_q"][i] == original[i] for i in active):
            raise ValueError("SAVED_ROOT_ACTIVE_COORDINATES_MISMATCH")
        branches = source["branch"]
        same_original_branch = all(identity["unique"] and identity["branch_set"] == [branch]
                                   for identity, branch in zip(original_identity.values(), branches))
        root_collision = None
        enumerated = []
        for q, lifts in all_lifts(source["base_q"], original, passive, environment):
            budget.check()
            identities = {str(arm): branch_identity(q[6*(arm-1):6*arm], environment, epsilon)
                          for arm in range(2, len(q)//6+1)} if environment != "I" else {
                              "planar": branch_identity(q, environment, epsilon)}
            branch_verified = all(identity["unique"] and identity["branch_set"] == [branch]
                                  for identity, branch in zip(identities.values(), branches))
            metrics = closure_metrics(q, environment)
            limits = limit_score(q, environment)
            unchanged = all(q[i] == original[i] for i in active)
            geometric = metrics["position_max_abs"] <= gate_p and metrics["rotation_matrix_max_abs"] <= gate_r
            pre_collision_eligible = (same_original_branch and branch_verified and source["regular"]
                                      and limits["legal"] and unchanged and geometric)
            # The roots differ only by mathematically exact 2pi joint rotations.
            # One native geometry collision call is shared by periodic representatives;
            # every representative still gets its own independent FK and limit score.
            delta = [a-b for a, b in zip(q, original)]
            record = {"candidate_index": len(candidates), "source_root_index": root_index,
                      "classification": "RECONSTRUCTED", "branch": branches,
                      "passive_indices": passive, "true_2pi_lifts": lifts, "q_rad": q,
                      "delta_q_rad": delta,
                      "passive_l2_delta_rad": math.sqrt(math.fsum(delta[i]**2 for i in passive)),
                      "passive_linf_delta_rad": max(abs(delta[i]) for i in passive),
                      "active_coordinates_exactly_unchanged": unchanged,
                      "original_branch_identity": original_identity, "candidate_branch_identity": identities,
                      "same_original_branch": same_original_branch, "branch_verified": branch_verified,
                      "source_regular_eligible": source["regular"], "limits": limits,
                      "independent_closure_metrics": metrics, "closure_qualified": geometric,
                      "pre_collision_eligible": pre_collision_eligible}
            candidates.append(record)
            enumerated.append(record)
            emit({"event": "candidate_before_collision", "candidate": record})
        first_eligible = next((c for c in enumerated if c["pre_collision_eligible"]), None)
        if first_eligible is not None:
            root_collision = collision_call(environment, first_eligible["q_rad"], budget)
            emit({"event": "periodic_root_collision", "source_root_index": root_index,
                  "representative_candidate_index": first_eligible["candidate_index"],
                  "result": root_collision})
        for record in enumerated:
            record["collision"] = root_collision if record["pre_collision_eligible"] else {
                "collision": None, "status": "NOT_CHECKED_OTHER_BRANCH_OR_INELIGIBLE"}
            record["collision_periodic_equivalence_reuse"] = record["pre_collision_eligible"]
            record["source_policy_collision_qualified"] = (record["collision"].get("status") == "CHECKED"
                                                               and record["collision"].get("collision") is False)
            record["full_physical_geometry_or_CCD_qualified"] = False
            record["all_qualifications_passed"] = (record["pre_collision_eligible"]
                                                     and record["source_policy_collision_qualified"])
        roots_audit.append({**source, "source_root_index": root_index,
                            "same_original_branch": same_original_branch,
                            "legal_periodic_representative_count": len(enumerated)})
    order = lambda candidate: (candidate["passive_l2_delta_rad"],
                               tuple(candidate["branch"]), tuple(candidate["true_2pi_lifts"]))
    eligible = sorted([c for c in candidates if c["all_qualifications_passed"]], key=order)
    prequalified = sorted([c for c in candidates if c["pre_collision_eligible"]], key=order)
    unique = all(x["unique"] for x in original_identity.values())
    selected = eligible[0] if eligible else None
    status = ("RECONSTRUCTED_SOURCE_POLICY_QUALIFIED" if selected else
              "UNKNOWN_ORIGINAL_BRANCH_COALESCENCE" if not unique else
              "UNKNOWN_COLLISION_QUALIFICATION" if any(c["collision"].get("collision") is None for c in prequalified) else
              "FAILED_COLLISION_QUALIFICATION" if prequalified else "FAILED_NO_QUALIFIED_SAME_BRANCH_ROOT")
    return {"environment": environment, "endpoint": name, "status": status,
            "classification": "RECONSTRUCTED", "formal_planning_authorized": False,
            "qualification_scope": "CLOSURE_LIMIT_BRANCH_AND_AUTHOR_DISCRETE_COLLISION_POLICY",
            "source_policy_collision_qualified": bool(selected),
            "full_physical_geometry_or_CCD_qualified": False,
            "collision_scope_limitations": [
                "Only the original discrete collision policy is qualified; omitted pairs and continuous motion are not certified.",
                "Original CAD/link frame conventions are retained; ABB source collinear rod triangle does not certify a solid rod volume."
            ],
            "original_endpoint": {"q_rad": original, "saved_raw_record": raw,
                                  "independent_metrics": original_metrics,
                                  "closure_qualified": original_metrics["position_max_abs"] <= gate_p
                                  and original_metrics["rotation_matrix_max_abs"] <= gate_r,
                                  "limits": limit_score(original, environment),
                                  "branch_identity": original_identity, "collision": original_collision},
            "passive_indices_frozen": passive, "active_indices_frozen": active,
            "selection_rule": "minimum passive Euclidean L2 in source coordinate chart; exact tie branch then lifts lexicographic",
            "saved_analytic_attempts_all": attempts,
            "source_root_enumeration": roots_audit, "candidates_all": candidates,
            "selected_candidate_index": selected["candidate_index"] if selected else None,
            "nearest_pre_collision_candidate_index": prequalified[0]["candidate_index"] if prequalified else None,
            "selected_q_rad": selected["q_rad"] if selected else None,
            "new_ik_calls": 0, "new_nr_calls": 0, "new_sampling_calls": 0,
            "formal_planning_calls": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    args = parser.parse_args()
    protocol_path = args.protocol.resolve()
    protocol = json.loads(protocol_path.read_text())
    required = {"frozen": True, "classification": "RECONSTRUCTED", "planar_passive_label": 0,
                "new_ik_calls": 0, "new_nr_calls": 0, "new_sampling_calls": 0,
                "position_gate": 1e-5, "rotation_matrix_gate": 1e-5}
    if any(protocol.get(k) != v for k, v in required.items()):
        raise ValueError("PROTOCOL_NOT_FROZEN_OR_SCOPE_MISMATCH")
    if protocol["wall_limit_s"] > 120 or protocol["cpu_limit_s"] > 240:
        raise ValueError("ENDPOINT_APPROVED_BUDGET_EXCEEDED")
    if not (0 < protocol["branch_zero_relative_epsilon"] <= 1e-10):
        raise ValueError("BRANCH_ZERO_EPSILON_NOT_FROZEN")
    if Path(args.run_id).name != args.run_id:
        raise ValueError("RUN_ID_MUST_BE_SINGLE_PATH_COMPONENT")
    # This separate, immutable controls result must qualify the exact source
    # policy before any endpoint evaluation or output-directory creation.
    controls_path = ROOT / protocol["collision_controls_result_path"]
    if digest(controls_path) != protocol["collision_controls_result_sha256"]:
        raise ValueError("COLLISION_CONTROLS_RESULT_HASH_MISMATCH")
    controls = json.loads(controls_path.read_text())
    if controls.get("passed") is not True or controls.get("status") != "SOURCE_POLICY_QUALIFIED":
        raise ValueError("COLLISION_SOURCE_POLICY_CONTROLS_NOT_QUALIFIED")
    output = ROOT / "results/p4_full" / args.run_id
    output.mkdir(exist_ok=False)
    budget = Budget(protocol["wall_limit_s"], protocol["cpu_limit_s"])
    inputs = {str(path.relative_to(ROOT)): digest(path) for path in
              [ROOT / source for source in SOURCE_RUNS.values()]}
    code_paths = [Path(__file__), ROOT / "baselines/p4_full/abb_independent_oracle.py",
                  ROOT / "baselines/p4_full/analyze_comau_native_qualification.py",
                  ROOT / "baselines/p4_full/geometry_consistent/collision_adapter.py"]
    execution = {"run_id": args.run_id, "started_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                 "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                 "git_status_at_start": subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True),
                 "protocol_path": str(protocol_path), "protocol_sha256": digest(protocol_path),
                 "collision_controls_result_path": str(controls_path),
                 "collision_controls_result_sha256": digest(controls_path),
                 "collision_controls_status": controls["status"],
                 "full_physical_geometry_or_CCD_qualified": False,
                 "inputs_sha256_before": inputs,
                 "source_files_sha256": {str(p.relative_to(ROOT)): digest(p) for p in code_paths if p.exists()},
                 "new_ik_calls": 0, "new_nr_calls": 0, "new_sampling_calls": 0,
                 "formal_planning_calls": 0, "classification": "RECONSTRUCTED"}
    results = []
    try:
        for environment, source in SOURCE_RUNS.items():
            budget.check()
            path = ROOT / source
            rows = ([json.loads(line) for line in path.read_text().splitlines()]
                    if path.suffix == ".jsonl" else json.loads(path.read_text()))
            endpoints = list(endpoint_sources(environment, rows))
            if len(endpoints) != 2:
                raise ValueError("EXPECTED_TWO_ORIGINAL_ENDPOINTS")
            for name, original, raw, attempts in endpoints:
                # Flush every evaluated candidate before a potentially blocking native
                # collision call so timeout/failure preserves the actual work prefix.
                with (output / f"{environment}_{name}_progress.jsonl").open("x") as progress:
                    def emit(event):
                        progress.write(json.dumps(event, ensure_ascii=False, allow_nan=False)+"\n")
                        progress.flush()
                    result = recover_endpoint(environment, name, original, raw, attempts,
                                              protocol, budget, emit)
                save_new(output / f"{environment}_{name}.json", result)
                results.append({"environment": environment, "endpoint": name, "status": result["status"],
                                "selected_candidate_index": result["selected_candidate_index"],
                                "candidate_count": len(result["candidates_all"]),
                                "original_closure_qualified": result["original_endpoint"]["closure_qualified"]})
        execution["status"] = "QUALIFICATION_EVIDENCE_RECORDED"
    except Exception as error:
        execution["status"] = "STOP"
        execution["error"] = repr(error)
        raise
    finally:
        execution["wall_s"] = time.monotonic() - budget.started
        execution["cpu_s"] = cpu_seconds() - budget.cpu_start
        execution["ended_at_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        execution["endpoint_results"] = results
        execution["endpoint_status_counts"] = dict(Counter(r["status"] for r in results))
        execution["inputs_sha256_after"] = {p: digest(ROOT / p) for p in inputs}
        execution["all_original_inputs_unchanged"] = execution["inputs_sha256_after"] == inputs
        save_new(output / "execution.json", execution)
    print(json.dumps({"output": str(output), "status_counts": execution["endpoint_status_counts"]}))


if __name__ == "__main__":
    main()
