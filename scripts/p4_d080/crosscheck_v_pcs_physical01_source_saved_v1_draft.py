#!/usr/bin/env python3
"""Saved bytes/arithmetic only; no model imports or scientific/runtime calls.

Source-side engineering crosscheck, NOT personnel-independent.  All observations
and independent TCP matrices must already exist.  Never fills a missing node.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[2]
LOCAL = 'results/p4_full/20261018_R2_D080_V_PCS_LOCAL01'
PHYSICAL = 'results/p4_full/20261018_R2_D080_V_PCS_PHYSICAL01'
QUEUE = 'configs/p4_d080/v_pcs_local01_complete_saved_queue_v1.DRAFT.json'
QUEUE_SHA = '6fa6da08e32e92068bad12346e14cf4d68440c6c205147937ea8c912daec8e35'
EXEC_SHA = 'ae553ae764753ecfc0cfba294902ecac2641c8b0784e8dae0c74d8bb62953450'
SOURCE_PROTOCOL = 'configs/p4_d080/v_pcs_local01_v1.json'
SOURCE_PROTOCOL_SHA = 'e2a2388bc37f3ddd0347c9bf6a889976251c19eec922194940d239ba06a9f311'
MANIFEST = '/home/ubuntu2004/lmy/.p4_d079_dependency_audit/v_pcs_local_v1/source_transform_manifest.json'
COL = '/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/V_aligned/validity_checkers/collisionDetection.cpp'
GATE = 1e-5


def path(name):
    p = Path(name)
    return p if p.is_absolute() else ROOT / p


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def key(q):
    if len(q) != 12 or not all(math.isfinite(v) for v in q):
        raise ValueError('FINITE_FULL_Q12_REQUIRED')
    return b''.join(struct.pack('>d', v) for v in q).hex()


def pose_metrics(a, b):
    if len(a) != 4 or len(b) != 4 or any(len(r) != 4 for r in a + b):
        raise ValueError('HOMOGENEOUS_MATRIX_SHAPE_REQUIRED')
    if not all(math.isfinite(v) for row in a + b for v in row):
        raise ValueError('NONFINITE_SAVED_MATRIX')
    return {'position_maxabs_mm': max(abs(a[i][3] - b[i][3]) for i in range(3)),
            'rotation_matrix_maxabs': max(abs(a[i][j] - b[i][j]) for i in range(3) for j in range(3)),
            'homogeneous_last_row_maxabs': max(abs(a[3][j] - b[3][j]) for j in range(4))}


def box_from_saved_tcp(tcp):
    # The original source's box transform, not a new FK or contact model.
    a = -3.1416 / 2
    ry = [[math.cos(a), 0., math.sin(a)], [0., 1., 0.], [-math.sin(a), 0., math.cos(a)]]
    out = [[sum(tcp[i][k] * ry[k][j] for k in range(3)) for j in range(3)]
           + [tcp[i][3] + tcp[i][0] * 435. + tcp[i][2] * 300.] for i in range(3)]
    return out + [[0., 0., 0., 1.]]


def run():
    checks, inputs, source_occurrences, node_rows = [], {}, [], []

    def check(name, condition, evidence=None):
        checks.append({'name': name, 'passed': bool(condition), 'evidence': evidence})

    def read(name, wanted=None):
        raw = path(name).read_bytes()
        got = digest(raw)
        inputs[name] = got
        if wanted is not None:
            check('saved_SHA256 ' + name, got == wanted, {'expected': wanted, 'actual': got})
            if got != wanted:
                raise ValueError('SAVED_INPUT_IDENTITY_MISMATCH ' + name)
        return json.loads(raw)

    report = {'schema': 'P4_D080_V_PCS_PHYSICAL01_SOURCE_SAVED_CROSSCHECK_V1',
              'classification': 'SOURCE_SIDE_SAVED_ARITHMETIC_CROSSCHECK_NOT_PERSONNEL_INDEPENDENT',
              'personnel_independent': False, 'position_gate_mm': GATE, 'rotation_matrix_gate': GATE,
              'gate_changed': False, 'new_model_calls': 0, 'new_binary_calls': 0,
              'new_sampling_or_constructions': 0, 'independent_local_qualified': False,
              'independent_path_qualified': False, 'continuous_collision_certificate': False,
              'independent_per_pair_closer_recomputed': False,
              'independent_per_pair_closer_status': 'UNKNOWN_NOT_EXPOSED_BY_SAVED_ADAPTER_VARIANTS',
              'status': 'STOP_SAVED_DIAGNOSTIC_PREFIX_RETAINED', 'checks': checks,
              'inputs_sha256': inputs, 'collision_occurrences': source_occurrences, 'nodes': node_rows,
              'limitations': ['Uses already saved independent FK matrices; does not run or requalify FK.',
                              'Agreement covers original discrete 87-pair 8mm policy only.',
                              'Source per-pair closer booleans are checked for self-consistency; independent saved variants expose aggregate collision, poses and API codes only.',
                              'Does not certify CAD suction contact, omitted pairs, CCD, local or full path success.',
                              'All original failures and partial reconstructions remain unchanged.']}
    try:
        queue = read(QUEUE, QUEUE_SHA)
        source_spec = read(SOURCE_PROTOCOL, SOURCE_PROTOCOL_SHA)
        physical = read(PHYSICAL + '/execution.json', EXEC_SHA)
        check('physical_complete_original24', physical['completed_original_node_ids'] == list(range(24))
              and physical['completed_nodes'] == 24 and physical['uncompleted_node_ids'] == []
              and physical['status'] == 'COMPLETED_FIXED24_DIAGNOSTIC_PENDING_INDEPENDENT_POST')
        manifest = read(MANIFEST, source_spec['bound_files_sha256'][MANIFEST])
        identities = manifest['active_pair_identities']
        raw_col = path(COL).read_bytes()
        inputs[COL] = digest(raw_col)
        check('bound_original_v3_collision_source', inputs[COL] == source_spec['bound_files_sha256'][COL])
        calls = re.findall(r'^[ \t]*p4_query\(([^;\n]*)\);', raw_col.decode(), re.M)
        parsed_pairs = []
        for call in calls:
            args = [a.strip() for a in call.split(',')]
            if len(args) != 8 or any(not re.fullmatch(r'&[A-Za-z][A-Za-z0-9_]*', args[i]) for i in (3, 6)):
                raise ValueError('ACTIVE_ORIGINAL_PAIR_PARSE_FAILED')
            parsed_pairs.append([args[3][1:], args[6][1:]])
        check('original87_pair_order_matches_saved_transform', len(parsed_pairs) == 87 and parsed_pairs == identities)
        nodes = {}
        for expected_id, node in enumerate(queue['nodes']):
            check('queue_node_identity_' + str(expected_id), node['node_id'] == expected_id and key(node['q12']) == node['binary64_be_key'])
            name = PHYSICAL + f'/node_{expected_id:05d}.json'
            saved = read(name, physical['retained_run_files_sha256'][name])
            check('physical_node_binary64_' + str(expected_id), saved['node_id'] == expected_id and key(saved['q12']) == key(node['q12']))
            nodes[key(node['q12'])] = (node, saved)
        check('unique_original24', len(nodes) == len(queue['nodes']) == 24)
        collision_keys_by_mode, source_records_by_mode = {}, {}
        for mode in ('trace', 'plain'):
            name = LOCAL + '/' + mode + '/parsed_rows.json'
            rows = read(name, queue['saved_inputs_sha256'][name])
            records = [record for row in rows for record in row['observed_records']]
            source_records_by_mode[mode] = records
            by_id = {r['id']: r for r in records}
            collision_keys_by_mode[mode] = set()
            collisions = [r for r in records if r['kind'] == 'collision']
            check(mode + '_complete_source34_collision_occurrences', len(collisions) == 34)
            for record in collisions:
                qkey = key(record['args']['q12'])
                if qkey not in nodes:
                    raise ValueError('SOURCE_COLLISION_NODE_MISSING_FROM_ORIGINAL_QUEUE')
                node, saved = nodes[qkey]
                collision_keys_by_mode[mode].add(qkey)
                result = record['result']
                pairs = result['active_pairs']
                prefix = mode + '_collision_' + str(record['id'])
                pair_order_ok = len(pairs) == 87 and [[p['first'], p['second']] for p in pairs] == identities
                pair_policy_ok = pair_order_ok and all(type(p['pair_index']) is int and p['pair_index'] == i
                    and p['tolerance_mm'] == 8. and type(p['api_code']) is int and p['api_code'] == 0
                    and type(p['closer_than_tolerance']) is bool and p['queue_size'] == 2 for i, p in enumerate(pairs))
                check(prefix + '_87_order_8mm_api0_and_boolean_predicates', pair_policy_ok)
                linked_pqp = [by_id.get(record['id'] + i + 1) for i in range(87)]
                check(prefix + '_all87_linked_original_PQP_records', len(pairs) == 87 and all(
                    p is not None and p['kind'] == 'pqp' and p['event'] == 'completed' and p['result'] == pairs[i]
                    and p['args'] == {k: pairs[i][k] for k in ('first', 'second', 'pair_index', 'queue_size', 'tolerance_mm')}
                    for i, p in enumerate(linked_pqp)))
                aggregate = any(p['closer_than_tolerance'] for p in pairs)
                check(prefix + '_returned_equals_any_closer', type(result['returned']) is int
                    and result['returned'] in (0, 1) and bool(result['returned']) == aggregate)
                check(prefix + '_policy_and_no_CCD', result['policy'] == 'V_ALIGNED_V3_SOURCE_87_PAIRS_8MM'
                    and result['continuous_collision_checked'] is False)
                tcps = result['physical_tcp_poses']
                tcp_metrics = [pose_metrics(tcps[i], saved['poses'][i]) for i in range(2)]
                box = box_from_saved_tcp(saved['poses'][0])
                box_metrics = pose_metrics(result['source_box_pose'], box)
                for i, metric in enumerate(tcp_metrics):
                    check(prefix + '_source_TCP' + str(i + 1) + '_vs_saved_independent', all(v <= GATE for v in metric.values()), metric)
                check(prefix + '_source_box_vs_saved_independent_formula', all(v <= GATE for v in box_metrics.values()), box_metrics)
                aligned = saved['collision']['variants']['aligned']
                check(prefix + '_source_reject_equals_saved_aligned', aggregate == saved['collision']['collision']
                      and aligned['pose_consistency']['passed'] is True and bool(aligned['native_result']) == aggregate)
                source_occurrences.append({'mode': mode, 'source_record_id': record['id'], 'node_id': node['node_id'],
                    'binary64_be_key': qkey, 'canonical_source_record_sha256': digest(canonical(record)),
                    'raw_source_parsed_rows_sha256': inputs[name], 'source_returned': result['returned'],
                    'true_pairs': [p for p in pairs if p['closer_than_tolerance']], 'tcp_metrics': tcp_metrics,
                    'box_metrics': box_metrics, 'box_expected_from_saved_independent_TCP': box})
            check(mode + '_unique17_collision_nodes', len(collision_keys_by_mode[mode]) == 17)
        check('trace_plain_full_saved_record_semantics', canonical(source_records_by_mode['trace']) == canonical(source_records_by_mode['plain']))
        check('trace_plain_same17_collision_binary64_keys', collision_keys_by_mode['trace'] == collision_keys_by_mode['plain'])
        selected = collision_keys_by_mode['trace']
        for qkey, (node, saved) in sorted(nodes.items(), key=lambda row: row[1][0]['node_id']):
            occurrences = [r for r in source_occurrences if r['node_id'] == node['node_id']]
            node_rows.append({'node_id': node['node_id'], 'binary64_be_key': qkey, 'q12': node['q12'],
                'group': 'SOURCE_COLLISION17' if qkey in selected else 'PROJECT_ONLY7_NO_ORIGINAL_COLLISION_QUERY',
                'source_occurrence_count': len(occurrences), 'source_returned_values': [r['source_returned'] for r in occurrences],
                'saved_math_qualified': saved['math_qualified'], 'saved_aligned_collision': saved['collision']['collision'],
                'saved_node_qualified': saved['qualified'], 'saved_native_TCP_status': saved['collision']['variants']['native']['pose_consistency']['status'],
                'source_qualified_original_end_to_end_path': False})
        source_group = [r for r in node_rows if r['group'] == 'SOURCE_COLLISION17']
        only_group = [r for r in node_rows if r['group'] != 'SOURCE_COLLISION17']
        report['summary'] = {label: {'nodes': len(group), 'aligned_clear': sum(r['saved_aligned_collision'] is False for r in group),
            'aligned_reject': sum(r['saved_aligned_collision'] is True for r in group),
            'node_ids': [r['node_id'] for r in group]} for label, group in [('source_collision17', source_group), ('project_only7', only_group)]}
        check('complete17_plus7_partition', len(source_group) == 17 and len(only_group) == 7)
        check('project_only7_are_source_project_outputs', all(any(o['kind'] == 'project_fixed' and o['source_returned'] is True
            for o in nodes[key(r['q12'])][0]['source_occurrences']) for r in only_group))
        report['status'] = 'PASS_SAVED_SOURCE_CROSSCHECK_ONLY' if all(r['passed'] for r in checks) else 'FAIL_SAVED_SOURCE_CROSSCHECK_RETAINED'
    except Exception as exc:
        report['error'] = repr(exc)
    report['checks_total'] = len(checks)
    report['checks_passed'] = sum(r['passed'] for r in checks)
    report['checks_failed'] = sum(not r['passed'] for r in checks)
    report['script_sha256'] = digest(Path(__file__).read_bytes())
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, help='New JSON output; an existing output is never replaced.')
    args = parser.parse_args()
    output = path(args.output)
    if output.exists():
        raise SystemExit('EXCLUSIVE_NEW_SAVED_REPORT_REQUIRED')
    result = run()
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC, 0o644)
    with os.fdopen(fd, 'w') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    print(json.dumps({k: result[k] for k in ('status', 'checks_total', 'checks_passed', 'checks_failed')}))
    return 0 if result['status'] == 'PASS_SAVED_SOURCE_CROSSCHECK_ONLY' else 2


if __name__ == '__main__':
    raise SystemExit(main())
