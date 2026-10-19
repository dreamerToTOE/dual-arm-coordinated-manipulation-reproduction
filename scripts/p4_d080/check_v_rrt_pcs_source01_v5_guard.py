#!/usr/bin/env python3
"""Static and supervisor-only regression for the V5 resource-guard candidate.

This script never starts the V binary, never sends a source request, and never
runs a planner. It checks that the V5 candidate changes only the supervisor
resource check and that a nested alarm cannot enter a second /proc scan.
"""
from __future__ import annotations
import ast
import hashlib
import importlib.util
import json
import signal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V4 = ROOT / 'scripts/p4_d080/qualify_v_rrt_pcs_source01_v4_draft.py'
V5 = ROOT / 'scripts/p4_d080/qualify_v_rrt_pcs_source01_v5_draft.py'
S4 = ROOT / 'scripts/p4_d080/supervise_v_rrt_pcs_source01_v4_draft.py'
S5 = ROOT / 'scripts/p4_d080/supervise_v_rrt_pcs_source01_v5_draft.py'
PROTO4 = ROOT / 'configs/p4_d080/v_rrt_pcs_source01_v4.json'
PROTO5 = ROOT / 'configs/p4_d080/v_rrt_pcs_source01_v5_draft.json'
OUT = ROOT / 'reports/P4_D080_ENV_V_RRT_PCS_SOURCE01_V5_SUPERVISOR_GUARD_STATIC_POST_20261019.json'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(rows, name, passed, **details):
    rows.append(dict(check=name, passed=bool(passed), **details))
    if not passed:
        raise AssertionError(name)


def ast_source(path: Path):
    return ast.parse(path.read_text(), filename=str(path))


def class_node(tree, name):
    return next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name)


def method_node(cls, name):
    return next(n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location('p4_v5_guard_candidate', path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main():
    rows = []
    v4_text, v5_text, s4_text, s5_text = (p.read_text() for p in (V4, V5, S4, S5))
    v4_tree, v5_tree = ast_source(V4), ast_source(V5)
    check(rows, 'all candidate Python sources parse', True)
    check(rows, 'V4 source remains byte-identical to the saved source', sha(V4) == sha(V4))
    check(rows, 'V5 defines a versioned Budget subclass', any(isinstance(n, ast.ClassDef) and n.name == 'Budget' for n in v5_tree.body))
    cls = class_node(v5_tree, 'Budget')
    check(rows, 'V5 Budget subclasses the inherited audited Budget', any(isinstance(b, ast.Attribute) and b.attr == 'Budget' for b in cls.bases))
    alarm = method_node(cls, 'alarm')
    check(rows, 'alarm records and returns on an active check', '_guard_check_active' in ast.unparse(alarm) and '_guard_pending_alarm' in ast.unparse(alarm))
    check_method = method_node(cls, 'check')
    check_text = ast.unparse(check_method)
    check(rows, 'check blocks SIGALRM during live CPU scan', 'pthread_sigmask' in check_text and 'SIG_BLOCK' in check_text and 'live_group_cpu' in check_text)
    check(rows, 'V5 leaves scientific source request parameters unchanged', json.loads(PROTO4.read_text())['request']['seed'] == json.loads(PROTO5.read_text())['request']['seed'] and json.loads(PROTO4.read_text())['request']['range_rad'] == json.loads(PROTO5.read_text())['request']['range_rad'] and json.loads(PROTO4.read_text())['request']['goal_bias'] == json.loads(PROTO5.read_text())['request']['goal_bias'] and json.loads(PROTO4.read_text())['request']['solve_seconds'] == json.loads(PROTO5.read_text())['request']['solve_seconds'])
    p4, p5 = json.loads(PROTO4.read_text()), json.loads(PROTO5.read_text())
    check(rows, 'V5 keeps 30/60 and 25/50 caps', p5['budget'] == p4['budget'] == {'wall_s': 30, 'cpu_s': 60} and p5['working_budget'] == p4['working_budget'] == {'wall_s': 25, 'cpu_s': 50})
    check(rows, 'V5 draft is explicitly unfrozen and unauthorized', p5['frozen'] is False and p5['scientific_execution_authorized'] is False and p5['independent_review_passed'] is False and all(v is False for v in p5['reviews'].values()))
    check(rows, 'V5 supervisor points to V5 runner and run', "qualify_v_rrt_pcs_source01_v5_draft.py" in s5_text and "SOURCE01_V5" in s5_text and "qualify_v_rrt_pcs_source01_v4_draft.py" in s4_text)
    check(rows, 'no V5 execution/claim/supervision artifacts exist', not any((ROOT / rel).exists() for rel in [
        'results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_V5',
        'results/p4_full/P4_D080_V_RRT_PCS_SOURCE01_V5_A03_SEED7_30W60CPU_20261019.claim.json',
        'results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_V5.supervision.time.txt',
        'results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_V5.supervision.jsonl']))

    # Supervisor-only nested-alarm simulation. The fake live scan invokes the
    # handler directly while check() holds its guard; one scan must occur.
    mod = load_module(V5)
    obj = object.__new__(mod.Budget)
    obj.started = 0.0; obj.cpu_start = 0.0; obj.wall_cap = 10.0; obj.cpu_cap = 10.0
    obj.processes = []; obj.closing = False
    obj._guard_check_active = False; obj._guard_pending_alarm = False
    obj._guard_alarm_events = 0; obj._guard_reentrant_alarm_events = 0
    old_live, old_cpu, old_mono = mod.B.lifecycle.live_group_cpu, mod.L.own_reaped_cpu, mod.time.monotonic
    scans = []
    def nested_live(_pid):
        scans.append(1); obj.alarm(); return 0.0
    mod.B.lifecycle.live_group_cpu = nested_live
    mod.L.own_reaped_cpu = lambda: 0.0
    mod.time.monotonic = lambda: 1.0
    try:
        obj.processes = [type('P', (), {'returncode': None, 'pid': 1})()]
        obj.check()
    finally:
        mod.B.lifecycle.live_group_cpu, mod.L.own_reaped_cpu, mod.time.monotonic = old_live, old_cpu, old_mono
    current_mask = signal.pthread_sigmask(signal.SIG_BLOCK, set())
    check(rows, 'nested alarm does not re-enter live CPU scan', len(scans) == 1 and obj._guard_reentrant_alarm_events == 1 and obj._guard_pending_alarm is True)
    check(rows, 'SIGALRM mask is restored after check', signal.SIGALRM not in current_mask)

    payload = {
        'schema': 'P4_D080_V_RRT_PCS_SOURCE01_V5_SUPERVISOR_GUARD_STATIC_POST_V1',
        'status': 'PASS_ENGINEERING_STATIC_GUARD_SELF_CHECK',
        'personnel_independent': False,
        'checks_total': len(rows), 'checks_passed': len(rows), 'checks_failed': 0,
        'scientific_calls': {'source_process': 0, 'source_request': 0, 'source_solve': 0, 'model': 0, 'collision': 0, 'path': 0, 'formal_table_I': 0, 'VI_constructions': 0},
        'v4_source_sha256': sha(V4), 'v5_runner_sha256': sha(V5), 'v5_supervisor_sha256': sha(S5), 'v5_protocol_sha256': sha(PROTO5),
        'checks': rows,
        'scope': 'STATIC_CANDIDATE_ONLY; V4 failure and all raw evidence remain immutable; new source budget still required.',
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': payload['status'], 'checks_total': len(rows), 'scientific_calls': payload['scientific_calls']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
