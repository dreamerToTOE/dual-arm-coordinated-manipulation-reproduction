#!/usr/bin/env python3
"""Materialize only immutable V LOCAL01 saved JSON/trace; stdlib, no model calls."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]
RUN = 'results/p4_full/20261018_R2_D080_V_PCS_LOCAL01'
EXECUTION_SHA = 'a0549cd8207b0a4c16e5adb71aab0f063859458a803916ba72db287e419d7985'
MARKER = b'P4_V_PCS_TRACE '
MAX_NODES = 256
LEAF_GATE = .05


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def canonical(v):
    return json.dumps(v, sort_keys=True, separators=(',', ':'), allow_nan=False)


def key(q):
    require(isinstance(q, list) and len(q) == 12 and
            all(type(x) in (int, float) and math.isfinite(x) for x in q), 'FINITE_Q12_REQUIRED')
    return b''.join(struct.pack('>d', float(v)) for v in q).hex()


def distance(a, b):
    key(a); key(b)
    return math.sqrt(sum((x-y)**2 for x, y in zip(a, b)))


def trace_lifetimes(raw):
    stack = []; records = {}; order = []; next_id = 1
    for line_index, line in enumerate(raw.splitlines()):
        if not line.startswith(MARKER):
            continue
        row = json.loads(line[len(MARKER):]); ident = row['id']; event = row['event']
        if event == 'entered':
            require(ident == next_id and ident not in records, 'TRACE_ENTRY_ID_ORDER')
            next_id += 1
            parent = None if not stack else stack[-1]
            public = ident if row['kind'] == 'public_request' else (
                None if parent is None else records[parent]['public_record_id'])
            records[ident] = dict(row, parent_id=parent, public_record_id=public,
                                  entered_stderr_line=line_index, child_ids=[])
            if parent is not None:
                records[parent]['child_ids'].append(ident)
            stack.append(ident); order.append(ident)
        else:
            require(event == 'completed' and stack and stack[-1] == ident, 'COMPLETE_LIFO_TRACE_REQUIRED')
            stack.pop(); stored = records[ident]
            require(stored['kind'] == row['kind'], 'TRACE_RETURN_KIND_CHANGED')
            stored.update(event='completed', result=row['result'], completed_stderr_line=line_index)
    require(not stack and len(records) == 3309 and all('result' in r for r in records.values()),
            'COMPLETE_ORIGINAL3309_LIFETIMES_REQUIRED')
    return [records[i] for i in order], records


def context(record, by_id):
    current = record
    while current is not None:
        args = current['args']
        if 'active_chain' in args:
            return args['active_chain'], args.get('branch')
        current = by_id.get(current['parent_id'])
    return None, None


def materialize(rows_by_mode, raw_trace, pending):
    records, by_id = trace_lifetimes(raw_trace)
    for mode, rows in rows_by_mode.items():
        require(len(rows) == 19 and rows[0]['status'] == 'SETUP_COMPLETED', 'ONE_SETUP18_REQUESTS_REQUIRED')
        observed = [r for row in rows for r in row['observed_records']]
        expected = [{k: r[k] for k in ('event', 'id', 'kind', 'args', 'result')} for r in records]
        require(canonical(observed) == canonical(expected), 'RAW_TRACE_PARSED_'+mode+'_RECORDS_DIFFER')
        require(all(row['solve_calls'] == row['rng_calls'] == 0 for row in rows), 'NO_SOLVE_RNG_REQUIRED')
    left = [{k: r[k] for k in ('request', 'result', 'status')} for r in rows_by_mode['trace'][1:]]
    right = [{k: r[k] for k in ('request', 'result', 'status')} for r in rows_by_mode['plain'][1:]]
    require(canonical(left) == canonical(right), 'PLAIN_TRACE_SEMANTICS_DIFFER')
    nodes = []; lookup = {}; leaves = []; paths = []; collisions = []; failures = []; publics = []
    successful_output_keys = set()

    def add(q, record, occurrence, extra=None):
        packed = key(q)
        if packed not in lookup:
            lookup[packed] = len(nodes)
            nodes.append(dict(node_id=len(nodes), binary64_be_key=packed, q12=q,
                              source_occurrences=[], role_branch_assignments=[], qualification_status='NOT_EXECUTED'))
        node = nodes[lookup[packed]]; role, branch = context(record, by_id)
        pub = by_id.get(record['public_record_id'])
        for mode in ('trace', 'plain'):
            ref = dict(mode=mode, public_request_id=None if pub is None else pub['args']['id'],
                       source_record_id=record['id'], parent_trace_id=record['parent_id'],
                       kind=record['kind'], occurrence=occurrence, active_chain=role,
                       requested_branch=branch, source_returned=record['result'].get('returned'))
            if extra:
                ref.update(extra)
            node['source_occurrences'].append(ref)
        if role is not None:
            assignment = dict(active_chain=role, passive_arm=2-role, requested_branch=branch)
            if assignment not in node['role_branch_assignments']:
                node['role_branch_assignments'].append(assignment)
        return node['node_id']

    for r in records:
        kind = r['kind']; args = r['args']; result = r['result']; returned = result.get('returned')
        role, branch = context(r, by_id)
        identity = dict(source_record_id=r['id'], parent_trace_id=r['parent_id'],
                        public_record_id=r['public_record_id'], kind=kind, active_chain=role,
                        requested_branch=branch, modes=['trace', 'plain'])
        if returned is False or (kind == 'collision' and returned != 0) or result.get('source_call_started') is False:
            failures.append(dict(identity, args=args, result=result))
        if kind in ('project_fixed', 'is_valid_rbs') and returned is True:
            add(result['q12'], r, 'SUCCESSFUL_SOURCE_OUTPUT')
            successful_output_keys.add(key(result['q12']))
        if kind == 'reconstruct':
            qs = result['path_q12']; ids = [add(q, r, 'ALL_SOURCE_RECONSTRUCT_M', {'path_index': i}) for i, q in enumerate(qs)]
            ds = [distance(a, b) for a, b in zip(qs, qs[1:])]
            paths.append(dict(identity, returned=returned, ordered_node_ids=ids,
                              adjacent_full12_L2_rad=ds, all_adjacent_strict_lt05=all(v < LEAF_GATE for v in ds),
                              path_status='SOURCE_TRUE_PENDING_PHYSICAL' if returned else 'SOURCE_FALSE_PARTIAL_M_NOT_ACCEPTED'))
        if kind in ('rbs', 'reconstruct') and returned is True and not any(by_id[i]['kind'] == kind for i in r['child_ids']):
            a, b = args['qa12'], args['qb12']; d = distance(a, b)
            ids = [add(a, r, 'SOURCE_TRUE_RECURSIVE_LEAF_A'), add(b, r, 'SOURCE_TRUE_RECURSIVE_LEAF_B')]
            leaves.append(dict(identity, node_ids=ids, full12_L2_rad=d, strict_lt05=d < LEAF_GATE))
        if kind == 'collision':
            node_id = add(args['q12'], r, 'ORIGINAL_COLLISION_INPUT', {'collision_returned': returned})
            collisions.append(dict(identity, node_id=node_id, source_collision_returned=returned,
                                   source_rejected=returned != 0, source_pair_count=len(result['active_pairs']),
                                   source_result=result))
        if kind == 'public_request':
            entry = dict(identity, request=args, result_status=result.get('status', 'SOURCE_CALL_COMPLETED'),
                         returned=returned, resolved_branch=result.get('resolved_branch'))
            if 'q12' in result:
                entry['output_binary64_be_key'] = key(result['q12'])
            if 'path_q12' in result:
                entry['path_binary64_be_keys'] = [key(q) for q in result['path_q12']]
            entry['source_result'] = result
            publics.append(entry)
    require(successful_output_keys == set(pending['nodes']) and len(successful_output_keys) == 24,
            'ORIGINAL_PENDING24_SUCCESS_KEYS_CHANGED')
    require(len(publics) == 18 and all(type(r['strict_lt05']) is bool for r in leaves), 'COMPLETE_PUBLIC_AND_LEAF_DATA')
    rejected = [r for r in collisions if r['source_rejected']]
    stats = dict(unique_nodes=len(nodes), original_pending_success_nodes=len(successful_output_keys),
                 all_reconstruct_records=len(paths), all_reconstruct_unique_nodes=len({i for p in paths for i in p['ordered_node_ids']}),
                 true_recursive_leaves=len(leaves), all_true_leaf_distances_strict_lt05=all(r['strict_lt05'] for r in leaves),
                 collision_records_per_mode=len(collisions), collision_unique_nodes=len({r['node_id'] for r in collisions}),
                 rejected_collision_records_per_mode=len(rejected), rejected_collision_unique_nodes=len({r['node_id'] for r in rejected}),
                 source_failure_identities_per_mode=len(failures), public_requests_per_mode=len(publics),
                 public_outcomes=dict(Counter(p['result_status'] if p['returned'] is None else
                                             ('SOURCE_TRUE' if p['returned'] else 'SOURCE_FALSE') for p in publics)),
                 source_lifetimes_per_mode=len(records), physical_node_limit=MAX_NODES, complete_union_under_limit=len(nodes) <= MAX_NODES)
    return dict(schema='P4_D080_V_PCS_LOCAL01_SAVED_COMPLETE_QUEUE_DRAFT_V1',
                status='DRAFT_SAVED_ONLY_PENDING_INDEPENDENT_PHYSICAL_FREEZE' if len(nodes) <= MAX_NODES else
                       'STOP_COMPLETE_SAVED_UNION_EXCEEDS256_NO_TRUNCATION',
                frozen=False, executable=False, environment='V', method='PCS',
                classification='CORRECTED_COMAU_APC_ALIGNED_V3_ORIGINAL_FIXED_PCS_RBS_CONTROL_RECONSTRUCTED_A02',
                stats=stats, nodes=nodes, recursive_true_leaves=leaves, all_reconstruct_paths=paths,
                all_original_collision_occurrences=collisions, rejected_collision_occurrences=rejected,
                rejected_collision_node_ids=sorted({r['node_id'] for r in rejected}),
                all_failure_identities=failures, all_public_request_identities=publics,
                input_policy='Only original stored binary64 q12; no new construction, interpolation, wrapped angles, replacement or truncated tail.',
                deduplication='Full big-endian binary64 q12 including signed zero; every original ordered ref and both mode identities retained.',
                independent_model_calls=0, binary_calls=0, solve_calls=0, new_VI_candidate_constructions=0,
                independent_local_qualified=False, independent_path_qualified=False,
                continuous_collision_certificate=False, formal_table_I_calls=0,
                limitations=['Source false partial reconstruction is never an accepted local path.',
                             'No independent FK, branch, limits or collision calculation is performed by this materializer.',
                             'This DRAFT data is not an execution protocol or resource authorization.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True); args = parser.parse_args()
    ep = ROOT/RUN/'execution.json'; require(sha(ep) == EXECUTION_SHA, 'FIXED_EXECUTION_HASH_REQUIRED')
    execution = json.loads(ep.read_text())
    require(execution['status'] == 'SOURCE_FIXED_LOCAL_OBSERVED_PENDING_INDEPENDENT_POST'
            and execution['plain_trace_semantics_equal'] is True, 'FIXED_COMPLETED_SOURCE_EXECUTION_REQUIRED')
    names = [RUN+'/trace/parsed_rows.json', RUN+'/plain/parsed_rows.json',
             RUN+'/process0_stderr.bin', RUN+'/process1_stderr.bin', RUN+'/independent_nodes_PENDING.json']
    bound = {str(ep.relative_to(ROOT)): EXECUTION_SHA}
    for name in names:
        require(sha(ROOT/name) == execution['retained_run_files_sha256'][name], 'RETAINED_INPUT_HASH_CHANGED '+name)
        bound[name] = sha(ROOT/name)
    require(not any(line.startswith(MARKER) for line in (ROOT/names[3]).read_bytes().splitlines()), 'PLAIN_TRACE_MARKERS_FORBIDDEN')
    rows = {mode: json.loads((ROOT/RUN/mode/'parsed_rows.json').read_text()) for mode in ('trace', 'plain')}
    data = materialize(rows, (ROOT/names[2]).read_bytes(), json.loads((ROOT/names[4]).read_text()))
    data.update(source_execution=RUN+'/execution.json', source_execution_sha256=EXECUTION_SHA,
                source_commit=execution['source_commit'], source_protocol=execution['protocol'],
                source_protocol_sha256=execution['protocol_sha256'], saved_inputs_sha256=bound,
                materializer_source_sha256=sha(__file__))
    require(all(sha(ROOT/n) == digest for n, digest in bound.items()), 'INPUT_BYTES_CHANGED_DURING_MATERIALIZATION')
    output = args.output if args.output.is_absolute() else ROOT/args.output
    require(not output.exists(), 'FRESH_OUTPUT_REQUIRED_NO_OVERWRITE')
    with output.open('x') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False); stream.write('\n')
    print(json.dumps(dict(status=data['status'], stats=data['stats'], output=str(output), sha256=sha(output)), ensure_ascii=False))
    if not data['stats']['complete_union_under_limit']:
        raise SystemExit(3)


if __name__ == '__main__':
    main()
