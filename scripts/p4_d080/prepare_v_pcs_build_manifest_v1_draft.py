#!/usr/bin/env python3
"""Pure-stdlib byte manifest helper; no runner, transform, model or compiler import.

This helper can exclusively save a DRAFT manifest. A FROZEN manifest additionally
requires root's explicit latest ledger path+SHA and a matching merged independent
review; it never starts the supervisor/build or any scientific operation.
Existing 219-body/pair and 101 engineering checks are reused, not re-executed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = '20261018_R2_D080_V_PCS_BUILD01'
STAGE = Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/v_pcs_local_v1')
AUTHOR = Path('/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/ckcComau_industrialScene')
APC = ROOT / 'build/p4_full/20261015_R2_SPATIAL01/ckcComau_industrialScene'
COL_ROOT = Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3')
COL = COL_ROOT / 'V_aligned'
PQP = Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/compat02/PQP_v1.3')
OMPL = Path('/opt/ros/humble/include/ompl-1.7/ompl')
LIBDIR = Path('/opt/ros/humble/lib/x86_64-linux-gnu')
POOL = ROOT / 'configs/p4_full/r2_abb_sbl_pcs_engineering_shadow_v2_v1.json'
POOL_SHA = '9f4c2b5efecd352ed9504a00b203a21629009f0c6feb636bea7cbc29e32652fe'
MERGED = ROOT / 'reports/P4_D080_ENV_V_PCS_ENGINEERING_MERGED_INDEPENDENT_PRE_20261018.json'
MERGED_SHA = '87e7843147fbb97c987b8b16a1722c98e9fbd75616ca362008855d672e2e68e4'
BODY = ROOT / 'reports/P4_D080_ENV_V_PCS_INDEPENDENT_BODY_PAIR_STATIC_20261017.json'
BODY_SHA = 'ec7e0fce89e98a052efbd0c34eb32ac41f1da43519cfac33cdb5537c59af9a75'
SELF_STATIC = ROOT / 'reports/P4_D080_ENV_V_PCS_ENGINEERING_SUPERVISION_SELF_STATIC_20261018.json'
PRESERVED = ROOT / 'work/preserved_v_pcs_engineering_before_monotonic_envelope_20261018'
HELPER_PRE = ROOT / 'reports/P4_D080_ENV_V_PCS_MANIFEST_HELPER_INCREMENTAL_INDEPENDENT_PRE_20261018.json'
OWN = [
    'scripts/p4_d080/build_v_pcs_local_v1_draft.py',
    'scripts/p4_d080/supervise_v_pcs_build_v1_draft.py',
    'scripts/p4_d080/prepare_v_pcs_build_manifest_v1_draft.py',
    'scripts/p4_d080/check_v_pcs_engineering_draft_static_20261018.py',
    'configs/p4_d080/v_pcs_local_v1.DRAFT.json',
    'baselines/p4_full/geometry_consistent/comau_v_pcs_observation_v1_draft.hpp',
    'baselines/p4_full/geometry_consistent/comau_v_pcs_local_driver_v1_draft.cpp',
    'baselines/p4_full/geometry_consistent/comau_v_pcs_instrumentation_v1_draft.py',
    'scripts/build_p4_full_r2_abb_cbirrt_d_draft.py',
    'baselines/p4_full/geometry_consistent/abb_cbirrt_d_instrumentation_draft.py',
    'baselines/p4_full/geometry_consistent/abb_pcs_source_corrections_draft.py',
    'reports/P4_D080_ENV_V_PCS_ENGINEERING_SUPERVISION_PRE_DRAFT_20261018.md',
    'reports/P4_D080_ENV_V_PCS_INDEPENDENT_ENGINEERING_GATES_20261017.json',
    'reports/P4_D080_ENV_V_PCS_INDEPENDENT_ENGINEERING_GATES_20261017.md',
    'docs/decisions/D080_P4_RELEVANCE_SCOPE_ACCELERATION_20261017.md',
    'docs/tasks/P4_D080_FAST_TRACK_IMPLEMENTATION_20261017.md',
    'reports/P4_D080_ORIGINAL_VS_APPROVED_VS_ACTUAL_COVERAGE_20261017.csv',
    'reports/P4_D080_SCOPE_MAPPING_VALIDATION_20261017.json',
    'configs/p4_d080/execution_scope_v1.json',
    'results/p4_d080/20261017_SCOPE_RECOVERY/budget_scope_overlay.json',
]
INPUTS = {
    'proj_classes/apc_class.cpp': APC / 'proj_classes/apc_class.cpp',
    'proj_classes/apc_class.h': APC / 'proj_classes/apc_class.h',
    'proj_classes/def.h': APC / 'proj_classes/def.h',
    'validity_checkers/StateValidityCheckerPCS.cpp': AUTHOR / 'validity_checkers/StateValidityCheckerPCS.cpp',
    'validity_checkers/StateValidityCheckerPCS.h': AUTHOR / 'validity_checkers/StateValidityCheckerPCS.h',
    'validity_checkers/collisionDetection.cpp': COL / 'validity_checkers/collisionDetection.cpp',
    'validity_checkers/collisionDetection.h': COL / 'validity_checkers/collisionDetection.h',
    'validity_checkers/model.h': COL / 'validity_checkers/model.h',
    'simulator/MatVec.h': COL / 'simulator/MatVec.h',
    'planners/RRT_PCS.cpp': AUTHOR / 'planners/RRT_PCS.cpp',
    'planners/RRT_PCS.h': AUTHOR / 'planners/RRT_PCS.h',
}
HEADER_ROOTS = (OMPL, Path('/usr/include/kdl'), Path('/usr/include/eigen3'),
                Path('/usr/include/nlohmann'), Path('/usr/include/boost'), PQP / 'include')


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def path(value):
    filename = Path(value)
    return filename if filename.is_absolute() else ROOT / filename


def sha(filename):
    return hashlib.sha256(Path(filename).read_bytes()).hexdigest()


def load(filename):
    return json.loads(Path(filename).read_text())


def exclusive_json(filename, value):
    filename.parent.mkdir(parents=True, exist_ok=True)
    with filename.open('xb') as stream:
        stream.write((json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + '\n').encode())
        stream.flush(); os.fsync(stream.fileno())
    directory = os.open(filename.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def prior_manifest(ledger_path, ledger_sha):
    # Only authoritative snapshot coverage/sums and current byte binding here.
    # POST/receipt/timing semantics are already checked by 101/root review and
    # are revalidated by the build runner; do not repeat a second full audit.
    ledger_path = ledger_path.resolve()
    ledgers = list((ROOT / 'results/p4_full').glob('20261016_RECOVERY_ACTUAL_LEDGER_V*.json'))
    require(ledgers and ledger_path == max(ledgers, key=lambda p: int(p.stem.rsplit('V', 1)[1])).resolve(),
            'ROOT_MUST_CONFIRM_LATEST_VERSIONED_CHARGED_LEDGER')
    require(sha(ledger_path) == ledger_sha, 'ROOT_CONFIRMED_LEDGER_SHA_CHANGED')
    ledger = load(ledger_path)
    actual = {str(p.relative_to(ROOT)): sha(p) for p in (ROOT / 'results/p4_full').glob('*_R2_*/execution.json')}
    actual.update({str(p.relative_to(ROOT)): sha(p) for p in (ROOT / 'results/p4_d080').glob('*/execution.json')})
    require({row['execution']: row['execution_sha256'] for row in ledger['executions']} == actual,
            'WAIT_ALL_REAL_EXECUTIONS_IN_LATEST_LEDGER')
    wall = math.fsum(row.get('charged_wall_s', row['wall_s']) for row in ledger['executions'])
    cpu = math.fsum(row.get('charged_cpu_s', row['cpu_s']) for row in ledger['executions'])
    require(all(math.isfinite(v) and v >= 0 for v in (wall, cpu))
            and wall == ledger['conservative_r2_sum_wall_s'] and cpu == ledger['conservative_r2_sum_cpu_s']
            and wall + 45 <= 3600 and cpu + 90 <= 7200, 'EXACT_PRIOR_BUDGET_AND_ORIGINAL_R2_CAPS_REQUIRED')
    files = {ledger_path}
    for row in ledger['executions']:
        files.add(path(row['execution']))
        if 'charged_wall_s' not in row:
            continue
        charge = path(row['execution']).parent.parent / (row['run_id'] + '.supervision.charge.json')
        metadata = load(charge)
        files.update([path(row['external_post']), path(row['external_time']), charge,
                      path(metadata['receipt']), path(metadata['metadata']), path(metadata['stderr'])])
    for directory in (ROOT / 'results/p4_full', ROOT / 'results/p4_d080'):
        for charge in directory.glob('*.supervision.charge.json'):
            name = charge.name.removesuffix('.supervision.charge.json')
            require((directory / name / 'execution.json').is_file(), 'WAIT_ACCOUNT_ORPHAN_SUPERVISION_' + name)
    return {'ledger': str(ledger_path.relative_to(ROOT)), 'ledger_sha256': ledger_sha,
            'wall_s': wall, 'cpu_s': cpu, 'historical_unmeasured_tail': 'RETAINED_UNKNOWN'}, files


def make_manifest(args):
    frozen = args.freeze
    require(not args.output.exists(), 'NO_OVERWRITE_EXISTING_MANIFEST')
    require(args.output.resolve().is_relative_to(ROOT / 'configs/p4_d080'), 'IN_REPOSITORY_CONFIG_OUTPUT_REQUIRED')
    require(not STAGE.exists() and not (ROOT / 'results/p4_full' / RUN).exists(), 'FRESH_STAGE_AND_RUN_REQUIRED')
    require(not any((ROOT / 'results/p4_full' / (RUN + suffix)).exists() for suffix in
                    ('.supervision.time.txt', '.supervision.jsonl', '.supervision.stderr.log', '.supervision.charge.json')),
            'OLD_SUPERVISION_PREFIX_NO_RETRY')
    require(sha(POOL) == POOL_SHA and sha(BODY) == BODY_SHA, 'REUSED_POOL_OR_219_BODY_CERTIFICATE_CHANGED')
    pool = load(POOL)
    header_files = {Path(name).resolve(): digest for name, digest in pool['bound_files_sha256'].items()
                    if any(Path(name).resolve().is_relative_to(root) for root in HEADER_ROOTS)}
    require(header_files and any(p.is_relative_to(OMPL) for p in header_files)
            and any(p.is_relative_to(Path('/usr/include/boost')) for p in header_files), 'SAVED_SBL_PREBIND_HEADER_POOL_REQUIRED')
    require(all(sha(filename) == digest for filename, digest in header_files.items()), 'REUSED_PREBOUND_HEADER_BYTES_CHANGED')
    bound = {str(filename): digest for filename, digest in header_files.items()}
    prior, prior_files = prior_manifest(args.ledger, args.ledger_sha256)
    files = {*prior_files, *INPUTS.values(), *[ROOT / name for name in OWN], POOL, BODY, SELF_STATIC, HELPER_PRE, PRESERVED / 'manifest.json',
             ROOT / 'reports/P4_D080_ENV_V_PCS_MONOTONIC_COMPAT_ENGINEERING_ADDENDUM_20261018.md',
             COL_ROOT / 'manifest.json', APC / 'p4_geometry_consistent_apc_stage_manifest.json',
             PQP / 'lib/libPQP.a', Path('/usr/bin/x86_64-linux-gnu-g++-11'),
             Path('/usr/lib/gcc/x86_64-linux-gnu/11/cc1plus'), Path('/usr/bin/as'),
             Path('/usr/bin/x86_64-linux-gnu-ld.bfd'), Path('/usr/bin/time'), Path('/usr/bin/python3'), Path('/etc/os-release')}
    collision = load(COL_ROOT / 'manifest.json')
    row, = [row for row in collision['entries'] if row['model'] == 'V' and row['variant'] == 'aligned']
    require(row['active_call_statement_count'] == 87 and row['tcp_observation_version'] == 3
            and len(row['mesh_sha256']) == 27, 'EXACT_V3_87PAIR_27_MESH_PROVENANCE_REQUIRED')
    for name, digest in row['mesh_sha256'].items():
        filename = COL / 'simulator' / name
        require(sha(filename) == digest, 'V_ORIGINAL_MESH_BYTES_CHANGED_' + name)
        files.add(filename)
    libraries = [LIBDIR / 'libompl.so', *[Path('/usr/lib/x86_64-linux-gnu') / ('libboost_' + name + '.so')
                  for name in ('filesystem', 'system', 'serialization', 'program_options')]]
    files.update(filename.resolve(strict=True) for filename in libraries)
    review_status = 'NOT_PRESENT_DRAFT_ONLY'
    if MERGED.exists():
        require(sha(MERGED) == MERGED_SHA, 'ROOT_CONFIRMED_MERGED_PRE_SHA_CHANGED')
        merged = load(MERGED); files.add(MERGED); review_status = merged['status']
        require(sha(SELF_STATIC) == merged['reused_self_review_sha256']
                and BODY_SHA == merged['reused_body_pair_static_sha256'], 'REUSED_SELF_AND_BODY_CERTIFICATE_BYTES_REQUIRED')
        reviewed = merged.get('reviewed_source_sha256', merged.get('source_sha256', {}))
        # Old merged PRE is permanent historical evidence. Only the changed
        # builder/supervisor may bind to their preserved pre-compatibility bytes.
        changed_engineering = set(OWN[:2])
        require(reviewed and all(sha(PRESERVED / name if name in changed_engineering else path(name)) == digest
                                 for name, digest in reviewed.items()), 'HISTORICAL_MERGED_PRE_SOURCE_BINDINGS_MUST_MATCH')
        if frozen:
            minimum = set(OWN[:2]); minimum.update(OWN[4:8])
            require(minimum <= {str(path(name).relative_to(ROOT)) for name in reviewed},
                    'MERGED_REVIEW_MUST_BIND_BUILDER_SUPERVISOR_THREE_SCIENCE_DRAFTS_CONFIG')
            require(merged.get('personnel_independent') is True and merged['status'].startswith('PASS')
                    and merged.get('checks_failed') == 0, 'MERGED_INDEPENDENT_PRE_MUST_PASS')
    elif frozen:
        raise RuntimeError('WAIT_MERGED_INDEPENDENT_PRE')
    compatibility = None
    if args.compat_review is not None:
        require(args.compat_review_sha256 is not None and sha(args.compat_review) == args.compat_review_sha256,
                'EXPLICIT_COMPATIBILITY_REVIEW_SHA_REQUIRED')
        compatible = load(args.compat_review); current = compatible.get('source_sha256', {})
        require(compatible.get('personnel_independent') is True and compatible['status'].startswith('PASS')
                and compatible.get('checks_failed') == 0 and current
                and all(sha(path(name)) == digest for name, digest in current.items())
                and set(OWN[:3]) <= {str(path(name).relative_to(ROOT)) for name in current},
                'CURRENT_BUILDER_SUPERVISOR_HELPER_COMPATIBILITY_INDEPENDENT_PRE_REQUIRED')
        files.add(args.compat_review); files.update(path(name) for name in current)
        compatibility = {'path': str(args.compat_review.relative_to(ROOT)), 'sha256': sha(args.compat_review),
                         'status': compatible['status']}
    if frozen:
        require(compatibility is not None and args.root_freeze_approved,
                'NEW_COMPATIBILITY_REVIEW_AND_EXPLICIT_ROOT_FREEZE_APPROVAL_REQUIRED')
    bound.update({str(filename.resolve()): sha(filename) for filename in files})
    prefix = 'results/p4_full/' + RUN
    return {'schema': 'P4_D080_V_PCS_BUILD_FROZEN_V1' if frozen else 'P4_D080_V_PCS_BUILD_MANIFEST_DRAFT_V1',
            'frozen': frozen, 'independent_review_passed': frozen, 'engineering_execution_authorized': frozen,
            'scientific_execution_authorized': False, 'formal_execution_authorized': False,
            'environment': 'V', 'run_name': RUN, 'stage_root': str(STAGE), 'budget': {'wall_s': 45, 'cpu_s': 90},
            'prior': prior, 'bound_files_sha256': dict(sorted(bound.items())),
            'reused_header_pool': {'path': str(POOL.relative_to(ROOT)), 'sha256': POOL_SHA,
                                   'bound_header_count': len(header_files),
                                   'actual_per_TU_MD_still_required': True, 'unfrozen_actual_dependency_policy': 'STOP_RETAIN_NO_RETROACTIVE_PASS'},
            'monotonic_compatibility_independent_pre': compatibility,
            'new_external_charge_basis': 'EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE',
            'merged_independent_pre': {'path': str(MERGED.relative_to(ROOT)), 'sha256': sha(MERGED) if MERGED.exists() else None,
                                       'status': review_status},
            'source_body_pair_certificate': {'path': str(BODY.relative_to(ROOT)), 'sha256': BODY_SHA, 'checks_reused': 219},
            'engineering_self_static_certificate': {'path': str(SELF_STATIC.relative_to(ROOT)), 'sha256': sha(SELF_STATIC),
                                                     'semantic_certificate_checks_repeated_by_helper': False},
            'external_supervision': {'required': True, 'sibling_path': prefix + '.supervision.time.txt',
                                    'metadata_path': prefix + '.supervision.jsonl', 'stderr_path': prefix + '.supervision.stderr.log',
                                    'charge_path': prefix + '.supervision.charge.json', 'format': '%e %U %S %x',
                                    'time_binary_sha256': sha('/usr/bin/time'), 'python_binary_sha256': sha('/usr/bin/python3'),
                                    'elapsed_decimal_upper_padding_s': .01, 'CPU_user_plus_system_upper_padding_s': .02,
                                    'final_independent_POST_required': True},
            'D080_original_formal_denominator': 22500, 'D080_approved_formal_denominator': 18000,
            'VI_future_execution_authorized': False, 'formal_statistics_authorized': False,
            'new_model_compile_runtime_calls_by_manifest_helper': 0,
            'one_shot': 'Fresh exclusive protocol; commit review before supervisor. Manifest creation never starts build/runtime.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--draft', action='store_true'); group.add_argument('--freeze', action='store_true')
    parser.add_argument('--ledger', required=True, type=Path)
    parser.add_argument('--ledger-sha256', required=True)
    parser.add_argument('--root-freeze-approved', action='store_true')
    parser.add_argument('--compat-review', type=Path)
    parser.add_argument('--compat-review-sha256')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); args.output = args.output.resolve(); args.ledger = path(args.ledger)
    if args.compat_review is not None:
        args.compat_review = path(args.compat_review).resolve()
        require(args.compat_review.is_relative_to(ROOT / 'reports'), 'IN_REPOSITORY_COMPATIBILITY_REVIEW_REQUIRED')
    require(len(args.ledger_sha256) == 64 and all(c in '0123456789abcdef' for c in args.ledger_sha256), 'EXPLICIT_LEDGER_SHA256_REQUIRED')
    require(not args.root_freeze_approved or args.freeze, 'APPROVAL_FLAG_ONLY_WITH_FREEZE')
    value = make_manifest(args); exclusive_json(args.output, value)
    print(json.dumps({'manifest': str(args.output.relative_to(ROOT)), 'sha256': sha(args.output),
                      'frozen': value['frozen'], 'bound_files': len(value['bound_files_sha256']),
                      'compile_model_runtime_calls': 0}))


if __name__ == '__main__':
    main()
