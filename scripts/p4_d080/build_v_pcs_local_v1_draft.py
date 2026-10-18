#!/usr/bin/env python3
"""V PCS fixed-local engineering candidate. DRAFT: do not execute yet.

Stdlib only plus our pure byte-transform. No describe, model import, binary
execution or scientific query. A separately frozen build protocol and live
external group supervisor are mandatory; the checked-in DRAFT cannot build.
The supervisor's final independent accounting, not this provisional record,
determines the charged cost. A build is never a local/path qualification.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import resource
import signal
import shlex
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
AUTHOR = Path('/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/ckcComau_industrialScene')
APC_STAGE = ROOT / 'build/p4_full/20261015_R2_SPATIAL01/ckcComau_industrialScene'
COL_ROOT = Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3')
COL_STAGE = COL_ROOT / 'V_aligned'
PQP = Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/compat02/PQP_v1.3')
STAGE = Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/v_pcs_local_v1')
RUN_NAME = '20261018_R2_D080_V_PCS_BUILD01'
RUN = ROOT / 'results/p4_full' / RUN_NAME
BASE = ROOT / 'baselines/p4_full/geometry_consistent'
OBSERVER = BASE / 'comau_v_pcs_observation_v1_draft.hpp'
DRIVER = BASE / 'comau_v_pcs_local_driver_v1_draft.cpp'
TRANSFORM = BASE / 'comau_v_pcs_instrumentation_v1_draft.py'
COMPILER = Path('/usr/bin/x86_64-linux-gnu-g++-11')
OMPL = Path('/opt/ros/humble/include/ompl-1.7')
LIBDIR = Path('/opt/ros/humble/lib/x86_64-linux-gnu')
SCOPE = ROOT / 'configs/p4_d080/execution_scope_v1.json'
OVERLAY = ROOT / 'results/p4_d080/20261017_SCOPE_RECOVERY/budget_scope_overlay.json'
SCOPE_SHA = 'edbf914187f449d0ce145987cbf38bc7d668c69b536f806a86b28b6da1bded41'
OVERLAY_SHA = '7fe6eb5eaaf9002c7e1f62192acb472788225bd6207dc181a5d41baca4f52ac7'
SUPERVISOR = ROOT / 'scripts/p4_d080/supervise_v_pcs_build_v1_draft.py'
TIME = Path('/usr/bin/time')
PYTHON = Path('/usr/bin/python3')
# Reuse the audited SBL BUILD02 group CPU/active-P4 infrastructure unchanged.
sys.path.insert(0, str(ROOT / 'scripts'))
import build_p4_full_r2_abb_cbirrt_d_draft as lifecycle
THREADS = lifecycle.THREADS
INPUTS = {
    'proj_classes/apc_class.cpp': APC_STAGE / 'proj_classes/apc_class.cpp',
    'proj_classes/apc_class.h': APC_STAGE / 'proj_classes/apc_class.h',
    'proj_classes/def.h': APC_STAGE / 'proj_classes/def.h',
    'validity_checkers/StateValidityCheckerPCS.cpp': AUTHOR / 'validity_checkers/StateValidityCheckerPCS.cpp',
    'validity_checkers/StateValidityCheckerPCS.h': AUTHOR / 'validity_checkers/StateValidityCheckerPCS.h',
    'validity_checkers/collisionDetection.cpp': COL_STAGE / 'validity_checkers/collisionDetection.cpp',
    'validity_checkers/collisionDetection.h': COL_STAGE / 'validity_checkers/collisionDetection.h',
    'validity_checkers/model.h': COL_STAGE / 'validity_checkers/model.h',
    'simulator/MatVec.h': COL_STAGE / 'simulator/MatVec.h',
    'planners/RRT_PCS.cpp': AUTHOR / 'planners/RRT_PCS.cpp',
    'planners/RRT_PCS.h': AUTHOR / 'planners/RRT_PCS.h',
}
SOURCE_KEYS = ('proj_classes/apc_class.cpp', 'validity_checkers/StateValidityCheckerPCS.cpp',
               'validity_checkers/collisionDetection.cpp', 'planners/RRT_PCS.cpp', 'planners/RRT_PCS.h')


def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def sha(filename):
    return hashlib.sha256(Path(filename).read_bytes()).hexdigest()


def load(filename):
    return json.loads(Path(filename).read_text())


def write_once(filename, data):
    filename = Path(filename); filename.parent.mkdir(parents=True, exist_ok=True)
    value = data if isinstance(data, bytes) else (json.dumps(data, ensure_ascii=False, allow_nan=False, indent=2) + '\n').encode()
    with filename.open('xb') as stream:
        stream.write(value); stream.flush(); os.fsync(stream.fileno())


def cpu():
    own = resource.getrusage(resource.RUSAGE_SELF); children = resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime + own.ru_stime + children.ru_utime + children.ru_stime


def path(value):
    filename = Path(value)
    return filename if filename.is_absolute() else ROOT / filename


def certificate_json(filename):
    # Historical .jsonl receipts include both a single pretty JSON object and
    # one-object-per-line variants. Parse saved bytes, never execute a runner.
    raw = Path(filename).read_text()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
        require(bool(rows), 'NONEMPTY_SAVED_RECEIPT_REQUIRED')
        return rows[-1]


def validate_prior(spec):
    ledger_path = path(spec['prior']['ledger']).resolve()
    ledgers = list((ROOT / 'results/p4_full').glob('20261016_RECOVERY_ACTUAL_LEDGER_V*.json'))
    require(ledgers and ledger_path == max(ledgers, key=lambda p: int(p.stem.rsplit('V', 1)[1])).resolve(),
            'LATEST_VERSIONED_CHARGED_LEDGER_REQUIRED')
    require(sha(ledger_path) == spec['prior']['ledger_sha256'], 'PRIOR_LEDGER_CHANGED')
    ledger = load(ledger_path)
    actual = {str(p.relative_to(ROOT)): sha(p) for p in (ROOT / 'results/p4_full').glob('*_R2_*/execution.json') if p.parent != RUN}
    actual.update({str(p.relative_to(ROOT)): sha(p) for p in (ROOT / 'results/p4_d080').glob('*/execution.json') if p.parent != RUN})
    require({r['execution']: r['execution_sha256'] for r in ledger['executions']} == actual,
            'PRIOR_LEDGER_MUST_COVER_EVERY_ACTUAL_EXECUTION')
    evidence = {str(ledger_path): sha(ledger_path)}
    for row in ledger['executions']:
        evidence[str(path(row['execution']))] = row['execution_sha256']
        if 'charged_wall_s' not in row:
            continue  # Historical unmeasured persistence tails remain UNKNOWN.
        post_path = path(row['external_post']); post = load(post_path)
        time_path = path(row['external_time'])
        charge_path = path(row['execution']).parent.parent / (row['run_id'] + '.supervision.charge.json')
        charge = load(charge_path)
        require(sha(post_path) == row['external_post_sha256'] and post['personnel_independent'] is True
                and post['external_supervision_qualified'] is True and post['checks_total'] == post['checks_passed']
                and post['checks_failed'] == 0 and post['execution_sha256'] == row['execution_sha256']
                and post['upper_wall_s'] == row['charged_wall_s'] and post['upper_cpu_s'] == row['charged_cpu_s']
                and sha(time_path) == row['external_time_sha256'] == post['external_time_sha256'],
                'PRIOR_EXTERNAL_POST_EXECUTION_TIMING_CERTIFICATE_REQUIRED')
        require(sha(charge_path) == post.get('external_charge_sha256', post.get('receipt_sha256'))
                and charge['execution_sha256'] == row['execution_sha256']
                and path(charge['source_execution']).resolve() == path(row['execution']).resolve()
                and path(charge['time_file']).resolve() == time_path.resolve()
                and charge['time_sha256'] == row['external_time_sha256']
                and charge['timing_valid'] is True and charge['time_inode_unchanged'] is True,
                'PRIOR_HASHED_EXTERNAL_CHARGE_BINDING_REQUIRED')
        receipt_path = path(charge['receipt']); receipt = certificate_json(receipt_path)
        require(sha(receipt_path) == charge['receipt_sha256'] and receipt['execution_sha256'] == row['execution_sha256'],
                'PRIOR_INTERNAL_PERSISTENCE_RECEIPT_REQUIRED')
        fields = time_path.read_text().strip().split()
        require(len(fields) == 4 and fields == charge['time_fields'], 'PRIOR_EXACT_FOUR_GNUTIME_FIELDS_REQUIRED')
        elapsed, user, system = (Decimal(v) for v in fields[:3]); exit_code = int(fields[3])
        require(all(v.is_finite() and v >= 0 for v in (elapsed, user, system))
                and exit_code == charge['measured_child_exit'] == charge['time_returncode'],
                'PRIOR_FINITE_TIME_AND_EXACT_SAVED_EXIT_REQUIRED')
        basis = row['charge_basis']
        raw_wall = float(elapsed + Decimal('.01')); raw_cpu = float(user + system + Decimal('.02'))
        if basis == 'EXTERNAL_TIME_DECIMAL_UPPER_BOUND_REPLACES_INTERNAL_SAMPLE_ONCE':
            require(raw_wall == row['charged_wall_s'] == charge['wall_s']
                    and raw_cpu == row['charged_cpu_s'] == charge['cpu_s'],
                    'PRIOR_DECIMAL_UPPER_REPLACEMENT_ONCE_REQUIRED')
        elif basis == 'EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE':
            # The one historical raw-time discrepancy is independently charged
            # without rewriting its original charge. Future V charges declare
            # this basis and retain raw fields separately at their first write.
            if charge.get('charge_basis') != basis:
                require(row['run_id'] == '20261018_R2_ABB_SBL_PCS_PATH01'
                        and row['execution_sha256'] == 'cee39aae1538742e1ab54e19d28ff42a8de2c4165cf2511bb1477d69847bc1e0'
                        and sha(charge_path) == '110293de768c992b99cd75da371de7c68a189271fcfc4687da785ea4fff16a27'
                        and raw_wall == charge['wall_s'] and raw_cpu == charge['cpu_s'],
                        'ONLY_IMMUTABLE_PATH01_OLD_RAW_CHARGE_EXCEPTION_ALLOWED')
            observations = (charge['fallback_observed_outer_wait_wall_s'], charge['fallback_reaped_children_CPU_s'],
                            receipt['wall_s_through_execution_persistence'], receipt['cpu_s_through_execution_persistence'])
            require(all(type(v) in (int, float) and math.isfinite(v) and v >= 0 for v in observations),
                    'FINITE_SAVED_OUTER_AND_RECEIPT_ENVELOPE_REQUIRED')
            expected_wall = float(max(elapsed + Decimal('.01'), Decimal(str(observations[0])) + Decimal('.01'),
                                      Decimal(str(observations[2])) + Decimal('.01')))
            expected_cpu = float(max(user + system + Decimal('.02'), Decimal(str(observations[1])) + Decimal('.02'),
                                     Decimal(str(observations[3])) + Decimal('.02')))
            require(post['charge_basis'] == basis and post['external_charge_sha256'] == sha(charge_path)
                    and post['internal_receipt_sha256'] == sha(receipt_path)
                    and row['charged_wall_s'] == post['upper_wall_s'] == expected_wall
                    and row['charged_cpu_s'] == post['upper_cpu_s'] == expected_cpu,
                    'PRIOR_INDEPENDENT_EXACT_MONOTONIC_ENVELOPE_CERTIFICATE_REQUIRED')
            execution = load(path(row['execution']))
            breach = {'wall': expected_wall > execution['budget']['wall_s'],
                      'cpu': expected_cpu > execution['budget']['cpu_s']}
            if any(breach.values()):
                require(row['execution_cap_breach'] == breach and post['execution_cap_breach_retained'] is True,
                        'REAL_PRIOR_CAP_BREACH_MUST_REMAIN_RECORDED_NOT_REJECTED')
            if charge.get('charge_basis') == basis:
                require(charge['wall_s'] == expected_wall and charge['cpu_s'] == expected_cpu
                        and charge['raw_GNUtime_upper_wall_s'] == raw_wall
                        and charge['raw_GNUtime_upper_cpu_s'] == raw_cpu,
                        'NEW_ENVELOPE_CHARGE_MUST_SEPARATELY_RETAIN_RAW_TIME')
        else:
            raise RuntimeError('UNKNOWN_PRIOR_CHARGE_BASIS_NO_SILENT_FALLBACK')
        for filename in (post_path, charge_path, receipt_path, time_path):
            evidence[str(filename.resolve())] = sha(filename)
        for key in ('metadata', 'stderr'):
            filename = path(charge[key])
            require(sha(filename) == charge[key + '_sha256'], 'PRIOR_SUPERVISION_LOG_CHANGED')
            evidence[str(filename.resolve())] = sha(filename)
        if 'internal_receipt' in post:
            require(path(post['internal_receipt']).resolve() == receipt_path.resolve()
                    and post['internal_receipt_sha256'] == sha(receipt_path), 'PRIOR_POST_INTERNAL_RECEIPT_CHANGED')
    for folder in (ROOT / 'results/p4_full', ROOT / 'results/p4_d080'):
        for charge in folder.glob('*.supervision.charge.json'):
            name = charge.name.removesuffix('.supervision.charge.json')
            if name == RUN_NAME:
                continue
            require((charge.parent / name / 'execution.json').is_file(), 'UNACCOUNTED_SUPERVISED_ATTEMPT_' + name)
    wall = math.fsum(row.get('charged_wall_s', row['wall_s']) for row in ledger['executions'])
    used = math.fsum(row.get('charged_cpu_s', row['cpu_s']) for row in ledger['executions'])
    require(all(math.isfinite(v) and v >= 0 for v in (wall, used))
            and wall == ledger['conservative_r2_sum_wall_s'] and used == ledger['conservative_r2_sum_cpu_s'],
            'EXACT_CURRENT_CHARGED_SUMS_REQUIRED')
    require(wall + spec['budget']['wall_s'] <= 3600 and used + spec['budget']['cpu_s'] <= 7200,
            'NO_R2_TOTAL_BUDGET_INCREASE')
    require(wall == spec['prior']['wall_s'] and used == spec['prior']['cpu_s'], 'EXACT_FROZEN_CHARGED_PRIOR_REQUIRED')
    return {'path': str(ledger_path.relative_to(ROOT)), 'sha256': sha(ledger_path),
            'wall_s': wall, 'cpu_s': used, 'evidence_sha256': evidence,
            'historical_unmeasured_tail': 'RETAINED_UNKNOWN'}


def compiler_group_members(pgid):
    # Direct port of the audited SBL BUILD02 cleanup evidence.
    members = []
    for stat in Path('/proc').glob('[0-9]*/stat'):
        try:
            row = stat.read_text().rsplit(')', 1)[1].split()
            if int(row[2]) == pgid:
                members.append(int(stat.parent.name))
        except (OSError, ValueError, IndexError):
            pass
    return sorted(members)


def validate_supervision(spec, protocol):
    # Actual GNUtime parent, grandparent supervisor, argv and held O_EXCL inode;
    # a JSON ACTIVE boolean is deliberately insufficient.
    ext = spec['external_supervision']
    raw = path(ext['metadata_path']).read_bytes().splitlines(keepends=True)[0]
    planned = json.loads(raw); parent = os.getppid()
    row = Path('/proc', str(parent), 'stat').read_text().rsplit(')', 1)[1].split()
    require(int(row[1]) == planned['supervisor_pid'] and sha(Path('/proc', str(parent), 'exe')) == sha(TIME),
            'ACTUAL_GNUTIME_PARENT_AND_SUPERVISOR_GRANDPARENT_REQUIRED')
    argv = [str(TIME), '--quiet', '-f', '%e %U %S %x', '-o', f"/proc/self/fd/{planned['time_fd']}",
            str(PYTHON), str(Path(__file__).resolve()), '--build', '--protocol', str(protocol)]
    require(planned['event'] == 'planned_launch' and planned['run_id'] == RUN_NAME
            and planned['protocol_sha256'] == sha(protocol) and planned['runner_sha256'] == sha(__file__)
            and planned['supervisor_source_sha256'] == sha(SUPERVISOR) and planned['argv'] == argv
            and Path('/proc', str(parent), 'cmdline').read_bytes().rstrip(b'\0').split(b'\0') == [s.encode() for s in argv],
            'EXACT_PARENT_ARGV_SOURCE_PROTOCOL_REQUIRED')
    output = path(ext['sibling_path']).stat(); held = []
    for descriptor in Path('/proc', str(parent), 'fd').iterdir():
        try:
            value = descriptor.stat()
            if (value.st_dev, value.st_ino) == (output.st_dev, output.st_ino):
                held.append(int(descriptor.name))
        except FileNotFoundError:
            pass
    require(held and (output.st_dev, output.st_ino) == (planned['time_device'], planned['time_inode']),
            'EXCLUSIVE_SUPERVISION_INODE_REQUIRED')
    return {'actual_time_pid': parent, 'actual_time_start_ticks': int(row[19]),
            'supervisor_pid': planned['supervisor_pid'], 'actual_argv': argv,
            'planned_launch_line_sha256': hashlib.sha256(raw).hexdigest(),
            'time_inode': output.st_ino, 'time_device': output.st_dev, 'actual_time_output_fds': sorted(held),
            'external_POST_required': True}


def frozen_assets(spec, protocol):
    required = [*INPUTS.values(), OBSERVER, DRIVER, TRANSFORM, Path(__file__).resolve(), SUPERVISOR, COMPILER, TIME, PYTHON,
                ROOT / 'scripts/build_p4_full_r2_abb_cbirrt_d_draft.py',
                ROOT / 'baselines/p4_full/geometry_consistent/abb_cbirrt_d_instrumentation_draft.py',
                ROOT / 'baselines/p4_full/geometry_consistent/abb_pcs_source_corrections_draft.py',
                Path('/usr/lib/gcc/x86_64-linux-gnu/11/cc1plus'), Path('/usr/bin/as'),
                Path('/usr/bin/x86_64-linux-gnu-ld.bfd'),
                SCOPE, OVERLAY, COL_ROOT / 'manifest.json',
                APC_STAGE / 'p4_geometry_consistent_apc_stage_manifest.json',
                PQP / 'lib/libPQP.a', Path('/etc/os-release')]
    require(sha(SCOPE) == SCOPE_SHA and sha(OVERLAY) == OVERLAY_SHA, 'D080_SOURCE_SCOPE_CHANGED')
    scope = load(SCOPE)
    require(scope['allowed_environments'] == ['I', 'II', 'III', 'IV', 'V']
            and scope['VI_future_science_authorized'] is False
            and scope['formal_execution_authorized'] is False, 'D080_SCOPE_GUARD_REQUIRED')
    collision = load(COL_ROOT / 'manifest.json')
    row, = [r for r in collision['entries'] if r['model'] == 'V' and r['variant'] == 'aligned']
    require(row['active_call_statement_count'] == 87 and row['tcp_observation_version'] == 3,
            'EXACT_PREVIOUS_V3_ALIGNED_COLLISION_CERTIFICATE_REQUIRED')
    require(sha(COL_ROOT / 'manifest.json') == 'c5df871adeea01d6487454dfd16fa217dde779958b5ba08b86ffff0e4f4a6388',
            'V3_COLLISION_MANIFEST_CHANGED')
    meshes = {COL_STAGE / 'simulator' / name: want for name, want in row['mesh_sha256'].items()}
    require(len(meshes) == 27 and all(sha(p) == want for p, want in meshes.items()), 'EXACT_27_V_MESH_BYTES_REQUIRED')
    required.extend(meshes)
    libraries = [LIBDIR / 'libompl.so', *[Path('/usr/lib/x86_64-linux-gnu') / ('libboost_' + name + '.so')
                  for name in ('filesystem', 'system', 'serialization', 'program_options')]]
    required.extend(p.resolve(strict=True) for p in libraries)
    bound = {str(Path(name).resolve()): want for name, want in spec['bound_files_sha256'].items()}
    require(bound and all(bound.get(str(p.resolve())) == sha(p) for p in required), 'ALL_REQUIRED_INPUT_TOOLCHAIN_LIBRARY_ASSETS_MUST_BE_PREBOUND')
    require(all(Path(name).is_file() and sha(name) == want for name, want in bound.items()), 'ANY_FROZEN_INPUT_DRIFT')
    return bound, meshes, [p.resolve(strict=True) for p in libraries]


def dependency_evidence(filename, target, source, staged, bound, state):
    raw = filename.read_bytes()
    require(raw.endswith(b'\n') and b'\r' not in raw and b'$' not in raw and b'#' not in raw,
            'EXACT_SUPPORTED_GCC_MD_FORMAT_REQUIRED')
    logical = raw.replace(b'\\\n', b' ').decode()
    require(logical.count(':') == 1, 'EXACTLY_ONE_GCC_MD_RULE_REQUIRED')
    head, tail = logical.split(':', 1)
    require(shlex.split(head) == [str(target)], 'DEPENDENCY_TARGET_MISMATCH')
    deps = [Path(p).resolve(strict=True) for p in shlex.split(tail)]
    require(deps and deps[0] == source.resolve(), 'SOURCE_FIRST_DEPENDENCY_REQUIRED')
    protected = (ROOT, STAGE, AUTHOR, APC_STAGE, COL_STAGE, PQP, OMPL, Path('/usr/include/boost'),
                 Path('/usr/include/eigen3'), Path('/usr/include/nlohmann'))
    observed = {str(p): sha(p) for p in deps}
    state['dependencies'].update(observed)  # Also retain failure-path dependency provenance.
    for name, digest in observed.items():
        p = Path(name)
        if any(p.is_relative_to(root) for root in protected):
            require(staged.get(name, bound.get(name)) == digest, 'UNFROZEN_ACTUAL_PROTECTED_DEPENDENCY_' + name)
    return {'raw_path': str(filename.relative_to(STAGE)), 'raw_sha256': sha(filename),
            'target': str(target), 'source': str(source), 'actual_dependencies_sha256': observed,
            'system_header_scope': 'Actual headers retained; generic libc/libstdc++ use compiler/OS provenance, not a complete OS image certificate.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='store_true', required=True)
    parser.add_argument('--protocol', type=Path, required=True)
    args = parser.parse_args(); args.protocol = args.protocol.resolve()
    spec = load(args.protocol)
    require(spec['schema'] == 'P4_D080_V_PCS_BUILD_FROZEN_V1' and spec['frozen'] is True
            and spec['engineering_execution_authorized'] is True and spec['independent_review_passed'] is True
            and spec['scientific_execution_authorized'] is False and spec['formal_execution_authorized'] is False
            and spec['environment'] == 'V' and spec['run_name'] == RUN_NAME
            and spec['stage_root'] == str(STAGE) and spec['budget'] == {'wall_s': 45, 'cpu_s': 90},
            'DRAFT_NOT_EXECUTABLE_REQUIRES_SEPARATELY_FROZEN_ENGINEERING_PROTOCOL')
    supervisor = validate_supervision(spec, args.protocol)
    own_files = [OBSERVER, DRIVER, TRANSFORM, Path(__file__).resolve(), SUPERVISOR, args.protocol]
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    for filename in own_files:
        relative = str(filename.relative_to(ROOT))
        require(subprocess.check_output(['git', 'show', commit + ':' + relative], cwd=ROOT) == filename.read_bytes(),
                'FROZEN_OWN_SOURCE_AND_PROTOCOL_MUST_BE_COMMITTED_' + relative)
    require(not lifecycle.active_p4(), 'OTHER_ACTIVE_P4_EXECUTION')
    require(signal.getitimer(signal.ITIMER_REAL) == (0., 0.), 'EXISTING_TIMER_REFUSE_REPLACE')
    require(not STAGE.exists() and not RUN.exists(), 'OCCUPIED_STAGE_OR_RUN_STOP_NO_OVERWRITE')
    started = time.monotonic(); before_cpu = cpu()
    RUN.mkdir(parents=True, exist_ok=False)
    record = {'source_commit': commit, 'schema': 'P4_D080_V_PCS_BUILD_EXECUTION_V1', 'run_name': RUN_NAME, 'run_id': RUN_NAME, 'classification': 'ENGINEERING_BUILD_ONLY_V_PCS_ORIGINAL_SCIENTIFIC_CONTROL',
              'engineering_only': True, 'status': 'STARTED',
              'execution_type': 'engineering', 'environment': 'V', 'scientific_calls': 0, 'query_calls': 0, 'solve_calls': 0,
              'budget': dict(spec['budget']), 'working_budget': {'wall_s': 40, 'cpu_s': 80},
              'rng_calls': 0, 'binary_execution_calls': 0, 'protocol_sha256': sha(args.protocol),
              'supervisor_contract': supervisor, 'targets': [], 'author_original_planning_qualified': False,
              'external_supervision_and_independent_post_required': True}
    code = 2; diagnostics = []; state = {'proc': None, 'groups': [], 'dependencies': {}, 'staged': {}}
    old_handler = signal.getsignal(signal.SIGALRM)
    def check():
        proc = state['proc']
        live = 0. if proc is None or proc.returncode is not None else lifecycle.live_group_cpu(proc.pid)
        require(time.monotonic() - started < 40 and cpu() - before_cpu + live < 80, 'BUILD_WORKING_CAP40W80CPU_RESERVE_FINAL45W90CPU')
    def alarm(*_):
        check()
    try:
        write_once(RUN / 'claim.json', record)
        record['claim_sha256'] = sha(RUN / 'claim.json')
        signal.signal(signal.SIGALRM, alarm); signal.setitimer(signal.ITIMER_REAL, .02, .02); check()
        record['prior'] = validate_prior(spec)
        bound, meshes, libraries = frozen_assets(spec, args.protocol)
        require(all(bound.get(name) == digest for name, digest in record['prior']['evidence_sha256'].items()),
                'ALL_PRIOR_EXECUTION_POST_RECEIPT_TIMING_BYTES_MUST_BE_PREBOUND')
        record['bound_files_sha256'] = bound
        record['protocol_sha256'] = sha(args.protocol)
        spec_module = importlib.util.spec_from_file_location('p4_v_pcs_pure_transform_v1', TRANSFORM)
        transform = importlib.util.module_from_spec(spec_module); spec_module.loader.exec_module(transform)
        original = {name: INPUTS[name].read_bytes() for name in SOURCE_KEYS}
        changed, proof = transform.instrument_sources(original)
        STAGE.mkdir(exist_ok=False)
        write_once(STAGE / 'source_transform_manifest.json', proof)
        for mode, trace in (('plain', 0), ('trace', 1)):
            dest = STAGE / mode; dest.mkdir()
            for name, source in INPUTS.items():
                write_once(dest / name, changed.get(name, source.read_bytes()))
            write_once(dest / OBSERVER.name, OBSERVER.read_bytes()); write_once(dest / DRIVER.name, DRIVER.read_bytes())
            for mesh in meshes:
                write_once(dest / 'simulator' / mesh.name, mesh.read_bytes())
            require((dest / 'proj_classes/def.h').read_bytes() == (COL_STAGE / 'proj_classes/def.h').read_bytes(),
                    'COLLISION_AND_APC_MUST_SHARE_IDENTICAL_DEF_BYTES')
            staged = {str(p.resolve()): sha(p) for p in dest.rglob('*') if p.is_file()}
            state['staged'].update(staged)
            sources = [dest / DRIVER.name, *[dest / name for name in SOURCE_KEYS if name.endswith('.cpp')]]
            require(len(sources) == 5, 'EXACTLY_FIVE_TRANSLATION_UNITS_REQUIRED')
            target = {'mode': mode, 'source_sha256': staged, 'commands': [], 'dependencies': [],
                      'binary_execution_calls': 0, 'status': 'COMPILING'}
            record['targets'].append(target); objects = []
            common = [str(COMPILER), '-std=c++17', '-O2', '-Wall', '-Wextra', '-pthread', '-DP4V_TRACE_MODE=' + str(trace),
                      '-I' + str(OMPL), '-I/usr/include/eigen3', '-I' + str(PQP / 'include'),
                      '-I' + str(dest), '-I' + str(dest / 'proj_classes'), '-I' + str(dest / 'validity_checkers'),
                      '-include', str(dest / OBSERVER.name)]
            for index, source in enumerate(sources):
                obj = dest / (str(index) + '_' + source.stem + '.o'); dep = obj.with_suffix('.d'); objects.append(obj)
                command = [*common, '-MD', '-MF', str(dep), '-MT', str(obj), '-c', str(source), '-o', str(obj)]
                invoke(command, dest, RUN / (mode + '_' + str(index)), target, state, check)
                # Keep even a dependency-parser failure's raw evidence on the
                # same final-hash path; no successful certificate is fabricated.
                state['dependencies'][str(dep.resolve())] = sha(dep)
                evidence = dependency_evidence(dep, obj, source, staged, bound, state)
                target['dependencies'].append(evidence)
                state['dependencies'].update(evidence['actual_dependencies_sha256'])
                state['dependencies'][str(dep.resolve())] = sha(dep)
            binary = dest / 'v_pcs_local'
            invoke([str(COMPILER), '-pthread', *map(str, objects), str(PQP / 'lib/libPQP.a'), *map(str, libraries),
                    '-Wl,-rpath,' + str(LIBDIR), '-o', str(binary)], dest, RUN / (mode + '_link'), target, state, check)
            require(all(sha(name) == want for name, want in staged.items()), 'STAGED_SOURCE_DRIFT_DURING_BUILD')
            target.update(status='BUILT_NOT_QUERIED', binary=str(binary), binary_sha256=sha(binary))
        require(all(sha(name) == want for name, want in bound.items()), 'BOUND_SOURCE_DRIFT_DURING_BUILD')
        record['status'] = 'BUILT_NOT_QUERIED'; code = 0
    except BaseException as error:
        record['status'] = 'STOP_ENGINEERING_FAILURE_RETAINED_PREFIX'; record['error'] = type(error).__name__ + ': ' + str(error)
    finally:
        # Same success/failure finalization as SBL BUILD02. Disable only our
        # timer, kill/reap every compiler group, then prove source/dep/prior bytes.
        previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
        try:
            signal.setitimer(signal.ITIMER_REAL, 0)
            while signal.SIGALRM in signal.sigpending():
                signal.sigwait({signal.SIGALRM})
            signal.signal(signal.SIGALRM, old_handler)
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
        for entry in state['groups']:
            proc = entry.pop('_process')
            try:
                entry['members_before_cleanup'] = compiler_group_members(proc.pid)
                entry['live_group_cpu_before_cleanup_s'] = lifecycle.live_group_cpu(proc.pid)
                if entry['members_before_cleanup']:
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                proc.wait(timeout=2.)
                entry['reaped'] = True; entry['returncode_after_cleanup'] = proc.returncode
                entry['members_after_cleanup'] = compiler_group_members(proc.pid)
                require(not entry['members_after_cleanup'], 'COMPILER_GROUP_NOT_EMPTY_AFTER_KILL_WAIT')
            except BaseException as error:
                diagnostics.append({'stage': 'compiler_cleanup', 'error': repr(error)})
        record['compiler_groups'] = state['groups']
        for label, expected in (('bound_files', record.get('bound_files_sha256', spec['bound_files_sha256'])),
                                ('staged', state['staged']), ('dependencies', state['dependencies'])):
            observed = {}; errors = []
            for name, digest in expected.items():
                try:
                    observed[name] = sha(name)
                    require(observed[name] == digest, 'FINAL_HASH_CHANGED_' + name)
                except BaseException as error:
                    errors.append({'path': name, 'error': repr(error)})
            record[label + '_after_sha256'] = observed
            if errors:
                diagnostics.append({'stage': label + '_final_hashes', 'errors': errors})
        try:
            record['protocol_after_sha256'] = sha(args.protocol)
            record['claim_after_sha256'] = sha(RUN / 'claim.json')
            require(record['protocol_after_sha256'] == record['protocol_sha256']
                    and record['claim_after_sha256'] == record.get('claim_sha256'), 'PROTOCOL_OR_CLAIM_CHANGED')
            record['prior_after'] = validate_prior(spec)
            require(record['prior_after'] == record['prior'], 'LATEST_CHARGED_PRIOR_CHANGED_DURING_BUILD')
        except BaseException as error:
            diagnostics.append({'stage': 'final_protocol_claim_prior', 'error': repr(error)})
        try:
            record['compile_log_sha256'] = {str(p.relative_to(ROOT)): sha(p) for p in sorted(RUN.glob('*.log')) if p.is_file()}
        except BaseException as error:
            diagnostics.append({'stage': 'compile_log_hashes', 'error': repr(error)})
        record['diagnostics'] = diagnostics
        record['wall_s'] = time.monotonic() - started; record['cpu_s'] = cpu() - before_cpu
        if diagnostics:
            record['status'] = 'STOP_CLEANUP_OR_EVIDENCE_ERROR'; code = 2
        if record['wall_s'] >= 45 or record['cpu_s'] >= 90:
            record['status'] = 'STOP_FINAL_WALL_OR_CPU_BUDGET'; code = 2
        record['cost_status'] = 'PROVISIONAL_REQUIRES_EXTERNAL_SUPERVISION_POST_NO_AUTO_CHARGE_REPLACEMENT'
        write_once(RUN / 'execution.json', record)
        receipt = {'schema': 'P4_D080_V_PCS_BUILD_COST_RECEIPT_V1', 'execution_sha256': sha(RUN / 'execution.json'),
                   'status': record['status'], 'wall_s_through_execution_persistence': time.monotonic() - started,
                   'cpu_s_through_execution_persistence': cpu() - before_cpu,
                   'last_receipt_persistence_tail': 'UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED',
                   'external_supervision_qualified': False}
        if receipt['wall_s_through_execution_persistence'] >= 45 or receipt['cpu_s_through_execution_persistence'] >= 90:
            receipt['status'] = 'STOP_FINAL_WALL_OR_CPU_BUDGET'; code = 2
        write_once(RUN / 'cost_receipt.json', receipt)
    return code


def invoke(command, cwd, log, target, state, check):
    check(); row = {'argv': command, 'cwd': str(cwd)}; target['commands'].append(row)
    # Direct port: SBL BUILD02 SIGALRM/live-group CPU watchdog. Each compiler
    # session has a retained PGID; children cannot evade cap by outliving g++.
    with Path(str(log) + '.stdout.log').open('xb') as out, Path(str(log) + '.stderr.log').open('xb') as err:
        previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
        try:
            def limits():
                signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
                resource.setrlimit(resource.RLIMIT_CPU, (90, 90))
            proc = subprocess.Popen(command, cwd=cwd, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                    start_new_session=True, preexec_fn=limits,
                                    env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', **THREADS})
            state['proc'] = proc
            entry = {'pid': proc.pid, 'pgid': proc.pid, '_process': proc}
            state['groups'].append(entry); row['compiler_pid'] = proc.pid
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
        while proc.poll() is None:
            check()
            try:
                proc.wait(timeout=.02)
            except subprocess.TimeoutExpired:
                pass
        out.flush(); os.fsync(out.fileno()); err.flush(); os.fsync(err.fileno())
    row['returncode'] = proc.returncode
    require(proc.returncode == 0, 'COMPILER_OR_LINKER_FAILED_RETAIN_LOGS')
    require(not compiler_group_members(proc.pid), 'COMPILER_DESCENDANT_SURVIVES_COMMAND_REAP')
    check()


if __name__ == '__main__':
    sys.exit(main())
