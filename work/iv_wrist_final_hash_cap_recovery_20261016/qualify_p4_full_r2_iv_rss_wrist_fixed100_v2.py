#!/usr/bin/env python3
"""V2 IV fixed100 wrist mathematics only; no sampling, collision or planner.

Describe/validate read saved evidence only. Execution requires independent
review, root freeze, committed sources and a fresh one-shot claim. Existing
batch/oracles and common Evidence/RunBudget are reused without modification.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

THREAD_ENV_BEFORE = {k: os.environ.get(k) for k in (
    'OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS',
    'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS')}
for key in THREAD_ENV_BEFORE:
    os.environ[key] = '1'
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT/'scripts'))
import qualify_p4_full_r2_vi_rss_reconstructed as common
from baselines.p4_full.geometry_consistent import physical_nr as physical
from baselines.p4_full.geometry_consistent.rss_geometry import apply_mode
from build_p4_full_r2_abb_rrt_pcs_e2e import live_group_cpu

SCHEMA = 'P4_R2_IV_RSS_WRIST_FIXED100_MATH_QUALIFICATION_V2'
RUN_ID = '20261015_R2_IV_RSS_WRIST_FIXED100_01'
CLAIM_ID = 'P4_R2_IV_RSS_WRIST_FIXED100_800IK_30W_60CPU_20261015'
PRE = 'reports/P4_FULL_R2_IV_RSS_WRIST_FIXED100_PRE_V2_DRAFT_20261016.md'
RAW = 'results/p4_full/20261014T1545_R1_COMAU02/IV_native.jsonl'
RAW_SHA = '3ae03596a6e5e52ba9e4c5b99fa10e61c713dcb9741860c7064563e4ca87b2f6'
BINARY = 'build/p4_full/20261015_R2_SPATIAL01/comau_iv_batch'
BINARY_SHA = 'acb44b837629fb8d822c4a238ab5014f78fd594dd1eb2e075015645e7370882a'
STAGE = 'build/p4_full/20261015_R2_SPATIAL01/ckcComau2'
AUTHOR = '/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/ckcComau2'
LEDGER = 'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V9.json'
ABB_EXECUTION = 'results/p4_full/20261015_R2_ABB_PCS_LOCAL01/execution.json'
LEGACY = ['scripts/qualify_p4_full_r2_iv_rss_wrist_fixed100.py',
    'configs/p4_full/r2_iv_rss_wrist_fixed100_qualification_v1.draft.json',
    'reports/P4_FULL_R2_IV_RSS_WRIST_FIXED100_PRE_DRAFT_20261015.md',
    'reports/P4_FULL_R2_IV_RSS_WRIST_FIXED100_PRE_REVIEW_20261015.md']
SOURCES = [str(Path(__file__).resolve().relative_to(ROOT)), PRE,
    'scripts/build_p4_full_r2_abb_rrt_pcs_e2e.py',
    'scripts/qualify_p4_full_r2_vi_rss_reconstructed.py',
    'baselines/p4_full/geometry_consistent/physical_nr.py',
    'baselines/p4_full/analyze_comau_native_qualification.py',
    'baselines/p4_full/abb_independent_oracle.py',
    'baselines/p4_full/geometry_consistent/rss_geometry.py',
    'baselines/p4_full/geometry_consistent/spatial_ik_patch.py',
    'baselines/p4_full/geometry_consistent/spatial_batch_driver.cpp']
GATES = {'position_maxabs_mm': 1e-5, 'rotation_matrix_maxabs': 1e-5,
    'rank_relative': 1e-6, 'rank_position_mm_to_m': .001,
    'branch_zero_relative_epsilon': 64*sys.float_info.epsilon,
    'G0_passive_rank_strictly_below': 6, 'G1_passive_rank': 5,
    'G1_full_physical_constraint_rank': 6}


def path(value):
    p = Path(value)
    return p if p.is_absolute() else ROOT/p


def load(value):
    return json.loads(path(value).read_text())


def fixed_inputs():
    """Transcribe saved bytes/angles; no FK/J, apply_mode, IK or RNG call."""
    if common.sha(path(RAW)) != RAW_SHA:
        raise common.StopQualification('R1_RAW_HASH_CHANGED')
    rows, metadata = [], None
    for line1, raw in enumerate(path(RAW).read_bytes().splitlines(keepends=True), 1):
        row = json.loads(raw)
        if row['type'] == 'metadata':
            metadata = row
        if row['type'] != 'fk_sample':
            continue
        q = row['q_rad']
        if len(q) != 12 or not all(math.isfinite(v) for v in q):
            raise common.StopQualification('INVALID_R1_FIXED_ARRAY')
        passive = q[6:12]; forced = list(passive); forced[4] = 0.
        rows.append({'sample': row['sample'], 'source_line1': line1,
            'source_line_sha256_including_original_newline': hashlib.sha256(raw).hexdigest(),
            'source_q12_rad': q, 'source_passive_q6_rad': passive,
            'forced_passive_q6_rad': forced,
            'branch_request_ids': [f'IV_s{row["sample"]:03d}_b{b}' for b in range(8)]})
    if ([r['sample'] for r in rows] != list(range(100)) or metadata is None
            or metadata['seed'] != 20261014 or metadata['effective_seed'] != 20265014
            or metadata['model'] != 4 or metadata['arms'] != 2
            or metadata['rng'] != 'std::mt19937_64'
            or metadata['author_properties_mm'] != [344, 524.5, 199, 1250, 186.5, 210, 1250, 116.5, 22]
            or metadata['base_xyz_yaw_mm_rad'] != [[-3000, 0, 0, 0], [3000, 0, 0, -3.1416]]):
        raise common.StopQualification('R1_METADATA_OR_100_SAMPLE_ORDER_CHANGED')
    return metadata, rows


def prior_state():
    ledger = load(LEDGER)
    actual = sorted(str(p.relative_to(ROOT)) for p in (ROOT/'results/p4_full').glob(
        '20261015_R2_*/execution.json') if p.parent.name != RUN_ID)
    entries = ledger['executions']
    if (ledger['schema'] != 'P4_R2_RECOVERY_ACTUAL_LEDGER_V9'
            or ledger['count'] != len(actual)
            or ledger['science_count']+ledger['engineering_count'] != len(actual) or ABB_EXECUTION not in actual
            or sorted(r['execution'] for r in entries) != actual
            or ledger['vi_B_candidate_cap'] != 974
            or ledger['vi_B_remaining']['candidate_constructions'] != 0):
        raise common.StopQualification('ROOT_PRIOR_LEDGER_REQUIRES_NEW_REVIEW')
    for r in entries:
        saved = load(r['execution'])
        if (common.sha(path(r['execution'])) != r['execution_sha256']
                or saved['wall_s'] != r['wall_s'] or saved['cpu_s'] != r['cpu_s']):
            raise common.StopQualification('PRIOR_EXECUTION_HASH_OR_COST_CHANGED')
    wall = math.fsum(float(r['wall_s']) for r in entries)
    cpu = math.fsum(float(r['cpu_s']) for r in entries)
    if (wall != ledger['conservative_r2_sum_wall_s']
            or cpu != ledger['conservative_r2_sum_cpu_s']):
        raise common.StopQualification('ROOT_PRIOR_LEDGER_SUM_MISMATCH')
    return actual, ledger, wall, cpu


def draft_protocol():
    metadata, rows = fixed_inputs(); prior, ledger, wall, cpu = prior_state()
    manifest = load(STAGE+'/p4_geometry_consistent_apc_stage_manifest.json')
    built = load('results/p4_full/20261015_R2_SPATIAL01/comau_iv_staging.json')
    if (common.sha(path(BINARY)) != BINARY_SHA
            or manifest['source_provenance']['commit'] != '80089340f0f1f6822e5b2821a63c998b6ae0413f'
            or common.sha(path(STAGE+'/proj_classes/apc_class.cpp')) != manifest['cpp_after_sha256']
            or common.sha(path(STAGE+'/proj_classes/apc_class.h')) != manifest['header_unchanged_sha256']):
        raise common.StopQualification('EXISTING_IV_BINARY_OR_STAGE_CHANGED')
    if (built['exit_code'] != 0 or built['model'] != 'comau_iv'
            or path(built['manifest']).resolve() != path(STAGE+'/p4_geometry_consistent_apc_stage_manifest.json').resolve()
            or built['manifest_sha256'] != common.sha(path(STAGE+'/p4_geometry_consistent_apc_stage_manifest.json'))
            or built['cpp_after_sha256'] != manifest['cpp_after_sha256']
            or '-DP4_MODEL=4' not in built['build_command']
            or path(built['build_command'][-1]).resolve() != path(BINARY).resolve()
            or manifest['patcher_sha256'] != common.sha(path('baselines/p4_full/geometry_consistent/spatial_ik_patch.py'))
            or manifest['source_provenance']['sha256'] != common.sha(path('configs/p4_full/author_source_manifest.json'))):
        raise common.StopQualification('SAVED_IV_SUCCESSFUL_BUILD_SOURCE_CHAIN_CHANGED')
    files = SOURCES+[RAW, BINARY, LEDGER,
        STAGE+'/p4_geometry_consistent_apc_stage_manifest.json',
        'configs/p4_full/author_source_manifest.json',
        'configs/p4_full/r2_geometry_consistent_qualification_v1.json',
        'configs/p4_full/r2_rss_fixed_construction_addendum_v1.json',
        'configs/p4_full/r2_iv_nr_local_qualification_v1.json',
        'results/p4_full/20261015_R2_SPATIAL01/IV/observations.json',
        'results/p4_full/20261015_R2_SPATIAL01/IV/checks.json',
        'results/p4_full/20261015_R2_IV_NR_LOCAL01/execution.json',
        'results/p4_full/20261015_R2_SPATIAL01/comau_iv_staging.json']+prior+LEGACY
    files += [root+'/'+name for root in (STAGE, AUTHOR) for name in (
        'proj_classes/apc_class.cpp', 'proj_classes/apc_class.h', 'proj_classes/def.h')]
    files += [AUTHOR+'/validity_checkers/StateValidityCheckerRSS.cpp']
    return {'schema': SCHEMA, 'frozen': False, 'run_id': RUN_ID, 'claim_id': CLAIM_ID,
        'classification': 'RECONSTRUCTED / IV-SOURCE-WRIST-ONLY / FIXED-MATH-COMPONENT',
        'execution_readiness': 'WAIT_INDEPENDENT_STATIC_REVIEW_AND_ROOT_FREEZE',
        'reviews': {'independent_static_review_passed': False, 'root_freeze_approved': False,
            'prior_execution_ledger_confirmed': False},
        'prerequisite_history': 'Original V1 remains byte-preserved and unexecuted; V2 only refreshes actual root V9 own-cost ledger/source provenance and hard live-CPU/finalization guards. Fixed100/800 scientific inputs, mode, geometry and gates unchanged.',
        'environment': 'IV', 'active_arm': 1, 'passive_arm': 2, 'source_singular_mode': 1,
        'source_seed': metadata['seed'], 'source_effective_seed': metadata['effective_seed'],
        'source_rng_not_rerun': metadata['rng'], 'fixed_inputs': rows,
        'request_order': 'Original sample0..99, branch0..7 ascending. One existing batch process per target, exactly8 K requests. No sample/root/periodic representative replacement.',
        'passive_rule': 'Only q5(index4)=0; other5 angles exact R1 arm2 values. Runtime apply_mode(COMAU,1) must equal frozen array.',
        'target_rule': 'Independent physical T2 from forced passive once; T1*=T2 S Q^-1, Q=Tx1800mm, S=diag(-1,-1,1,1). Actual target saved before K dispatch.',
        'geometry': {'properties_mm': metadata['author_properties_mm'],
            'bases_mm_rad': metadata['base_xyz_yaw_mm_rad'],
            'grasp_transforms': metadata['grasp_transforms'],
            'limits_low_rad': metadata['joint_low_rad'], 'limits_high_rad': metadata['joint_high_rad'],
            'author_pi_for_base_and_limits': 3.1416},
        'binary': BINARY, 'binary_sha256': BINARY_SHA,
        'gates': GATES, 'budget': {'max_fixed_targets': 100, 'max_K_requests': 800,
            'max_mathematical_arm_FK_J': 900, 'max_native_accepted_K_internal_FK': 800,
            'wall_s': 30., 'cpu_s': 60., 'r2_total_wall_s': 3600., 'r2_total_cpu_s': 7200.},
        'call_accounting': {'mathematical_FK_J': 'One passive call/started target + one active call/source-accepted finite root; same pose/J reused for roundtrip, closure and full physical6x12 J. Fully completed total100+A<=900, actual starts/completions logged separately.',
            'native': 'external_K_dispatched records requests, valid saved JSON rows confirm JSON_completed. Existing K internally executes one native FK per accepted root; native_accepted_FK_observed counts finite accepted JSON returns. No explicit F requests. Internal true K/FK started has no start hook: UNOBSERVED, never inferred from dispatched or caps. Interrupted unreported rows remain UNKNOWN.',
            'full_constraint_J': 'physical_nr closure derivative assembled from cached T1,J1,T2,J2 with its skew/log_so3/left_jacobian_inverse; no extra arm FK/J, FD or NR.',
            'VI_B_new_candidate_constructions': 0},
        'G0_gate': 'passive scaled rank<6 + independent physical closure + all12 unchanged source bounds; old700-target comparison only.',
        'G1_gate': 'G0 + passive rank exactly5 + requested active label in independent geometric branch_set (meeting sets retained) + physical full6x12 constraint rank6.',
        'positive_component_gate': 'At least one G1 target among fixed100, plus all source-accepted roots sound. Report G0/G1 branch/target denominators separately. No collision/RBS/fullRSS certificate.',
        'soundness_stop': 'Any source-accepted nonfinite/unsound root stops before the next target. Retain target8-request batch, all native returns and processed prefix; remaining diagnostics and targets explicitly unexecuted. No retry/fallback.',
        'zero_calls': {'collision': 0, 'RBS': 0, 'NR': 0, 'RNG': 0, 'solve': 0,
            'explicit_native_F': 0, 'new_VI_candidate_constructions': 0},
        'original_failures_unchanged': True, 'VI_B_candidate_cap': 974,
        'VI_B_candidate_remaining': 0, 'full_RSS_or_planning_pass': False,
        'source_files': SOURCES, 'prior_executions': prior,
        'root_prior_ledger': LEDGER, 'previous_r2_wall_s': wall, 'previous_r2_cpu_s': cpu,
        'prior_science_count': ledger['science_count'], 'prior_engineering_count': ledger['engineering_count'],
        'prior_budget_rule': 'Each actual execution own cost once; engineering cost conservatively included in R2 cap and separately labelled. No cumulative field or science/engineering conflation.',
        'legacy_v1_preserved': {p: common.sha(path(p)) for p in LEGACY},
        'engineering_only_v2_delta': ['Refresh root actual V9 ledger and every prior own cost/source hash.',
            'Bind original successful comau_iv_staging build record and unchanged V1 assets.',
            'Add parent plus live process-group CPU guard, preserve raw process prefix on stop.',
            'Final wall/CPU or preservation error cannot receive mathematical-component PASS.'],
        'resource_guard': 'Parent hard wall timer and live aggregate child-process-group CPU sampled every<=20ms; one-thread environment; actual cleanup/finalization cost included once.',
        'bound_files_sha256': {p: common.sha(path(p)) for p in dict.fromkeys(files)},
        'one_shot_policy': 'Atomic fixed claim, no reset/retry/resume on crash; retain prefix and actual cost. No new VI candidate quota.'}


def validate(spec, protocol, execute=False):
    expected = draft_protocol()
    if set(spec) != set(expected):
        raise common.StopQualification('PROTOCOL_FIELD_SET_CHANGED')
    for key, value in expected.items():
        if key not in ('frozen', 'reviews', 'execution_readiness') and spec[key] != value:
            raise common.StopQualification('PROTOCOL_OR_SOURCE_CHANGED_'+key)
    if (type(spec['frozen']) is not bool or set(spec['reviews']) != set(expected['reviews'])
            or any(type(v) is not bool for v in spec['reviews'].values())):
        raise common.StopQualification('INVALID_FREEZE_OR_REVIEW_FIELDS')
    if execute:
        if (not spec['frozen'] or not all(spec['reviews'].values())
                or spec['execution_readiness'] != 'FROZEN_REVIEWED_READY'):
            raise common.StopQualification('INDEPENDENT_REVIEW_ROOT_FREEZE_REQUIRED')
        for relative in SOURCES+LEGACY+[str(protocol.relative_to(ROOT))]:
            subprocess.run(['git', 'ls-files', '--error-unmatch', relative], cwd=ROOT,
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if subprocess.check_output(['git', 'status', '--porcelain', '--', relative], cwd=ROOT, text=True):
                raise common.StopQualification('UNCOMMITTED_SOURCE_OR_PROTOCOL_'+relative)


def rank_data(matrix):
    np = common.np
    scaled = np.asarray(matrix, dtype=float).copy(); scaled[:3] *= .001
    sigma = np.linalg.svd(scaled, compute_uv=False)
    cutoff = GATES['rank_relative']*float(sigma[0])
    return {'rank': int(np.count_nonzero(sigma > cutoff)), 'singular_values': sigma.tolist(),
        'cutoff': cutoff, 'relative_threshold': GATES['rank_relative'], 'linear_rows': 'mm to m'}


def cached_closure(p1, j1, p2, j2, grasp):
    """Reuse physical_nr's derivative formula with already observed pose/J."""
    np = common.np; target = p1@grasp@physical.FLIP
    e = p2[:3, :3]@target[:3, :3].T; phi = physical.log_so3(e)
    j = np.zeros((6, 12)); offset = p1[:3, :3]@grasp[:3, 3]
    j[:3, :6] = -j1[:3]+physical.skew(offset)@j1[3:]; j[:3, 6:] = j2[:3]
    log_j = physical.left_jacobian_inverse(phi)
    j[3:, :6] = -log_j@e@j1[3:]; j[3:, 6:] = log_j@j2[3:]
    return {'residual_vector_mm_rad': list(p2[:3, 3]-target[:3, 3])+list(phi),
        'constraint_jacobian_6_by_12': j.tolist(), 'full_rank_report': rank_data(j)}


class LiveEvidence(common.Evidence):
    """Existing evidence API with the already-qualified live group CPU guard."""
    def process(self, command, input_text, label, environment=None):
        self.budget.remaining(); self.process_number += 1
        stem = f'{self.process_number:05d}_{label}'
        inp, stdout, stderr = [self.folder/(stem+s) for s in ('.input.txt','.stdout.txt','.stderr.txt')]
        with inp.open('x') as f: f.write(input_text)
        begun=time.monotonic(); proc=None
        self.event('process_started',label=label,command=command,input=str(inp.relative_to(ROOT)))
        try:
            with inp.open() as fin, stdout.open('x') as out, stderr.open('x') as err:
                proc=subprocess.Popen(command,stdin=fin,stdout=out,stderr=err,cwd=ROOT,
                    start_new_session=True,env={**os.environ,**(environment or {})})
                while proc.poll() is None:
                    self.budget.remaining()
                    if self.budget.cpu()-self.budget.cpu_start+live_group_cpu(proc.pid)>=self.budget.cpu_cap:
                        raise common.StopQualification('IV_WRIST_PARENT_PLUS_LIVE_GROUP_CPU_CAP')
                    try:proc.wait(timeout=.02)
                    except subprocess.TimeoutExpired:pass
        except BaseException:
            if proc is not None and proc.poll() is None:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
            self.event('process_interrupted',label=label,wall_s=time.monotonic()-begun);raise
        self.event('process_finished',label=label,exit_code=proc.returncode,wall_s=time.monotonic()-begun,
            stdout_sha256=common.sha(stdout),stderr_sha256=common.sha(stderr))
        self.budget.remaining()
        if proc.returncode:raise common.StopQualification('PROCESS_FAILED_'+label+'_'+str(proc.returncode))
        return stdout.read_text()


class Qualification:
    def __init__(self, spec, folder, budget):
        self.spec, self.folder, self.budget = spec, folder, budget
        self.evidence = LiveEvidence(folder, budget); self.counts = Counter()
        self.targets, self.observations, self.dispatched = [], [], []
        self.native_batches = []

    def fk(self, q, arm, case):
        self.budget.remaining()
        if self.counts['mathematical_arm_FK_J_started'] >= 900:
            raise common.StopQualification('MATHEMATICAL_FK_J_CAP')
        self.counts['mathematical_arm_FK_J_started'] += 1
        self.evidence.event('mathematical_arm_FK_J_started', arm=arm, case_id=case, q6_rad=list(q))
        p, j = physical.arm_fk_jac(q, 'IV', arm)
        self.counts['mathematical_arm_FK_J_completed'] += 1
        self.evidence.event('mathematical_arm_FK_J_completed', arm=arm, case_id=case,
            pose=p.tolist(), jacobian=j.tolist())
        if not common.np.isfinite(p).all() or not common.np.isfinite(j).all():
            raise common.StopQualification('NONFINITE_MATHEMATICAL_FK_J')
        self.budget.remaining()
        return p, j

    def native(self, item, target):
        sample = item['sample']; ids = item['branch_request_ids']
        output = self.folder/f'native_s{sample:03d}.jsonl'
        text = ''.join('K 1 '+str(branch)+' '+' '.join(format(float(v), '.17g')
            for v in target.ravel())+'\n' for branch in range(8))
        if self.counts['external_K_dispatched']+8 > 800:
            raise common.StopQualification('EXTERNAL_K_REQUEST_CAP')
        self.counts['external_K_dispatched'] += 8; self.dispatched.extend(ids)
        self.native_batches.append({'sample': sample, 'path': str(output.relative_to(ROOT)),
            'request_ids': ids, 'target': target.tolist()})
        self.evidence.event('external_K_dispatched', request_ids=ids, target=target.tolist(),
            internal_K_started='UNOBSERVED_NO_NATIVE_START_HOOK')
        stdout = self.evidence.process([str(path(BINARY)), str(output)], text, f'IV_s{sample:03d}_8K')
        if stdout != output.read_text():
            raise common.StopQualification('NATIVE_STDOUT_AND_SAVED_OUTPUT_DIFFER')
        rows = [json.loads(line) for line in output.read_text().splitlines()]
        if len(rows) != 8:
            raise common.StopQualification('NATIVE_EIGHT_ROW_CARDINALITY')
        for branch, row in enumerate(rows):
            if (row.get('schema') != 'P4_SPATIAL_BATCH_V1' or row.get('model') != 4
                    or row.get('input_line') != branch+1 or row.get('op') != 'K'
                    or row.get('arm') != 1 or row.get('branch') != branch
                    or row.get('target') != target.tolist() or row.get('error')
                    or type(row.get('success')) is not bool or type(row.get('finite')) is not bool):
                raise common.StopQualification('NATIVE_K_INTERFACE_CHANGED')
        return rows

    def run(self):
        np = common.np; geometry = physical.model_geometry('IV')
        grasp = geometry['grasps'][0]; bounds = physical.source_limits('IV')
        expected = self.spec['geometry']
        if (geometry['bases'] != expected['bases_mm_rad']
                or grasp.tolist() != expected['grasp_transforms'][0]
                or bounds[:6, 0].tolist() != expected['limits_low_rad']
                or bounds[:6, 1].tolist() != expected['limits_high_rad']):
            raise common.StopQualification('RUNTIME_GEOMETRY_OR_SOURCE_LIMITS_CHANGED')
        for item in self.spec['fixed_inputs']:
            self.budget.remaining(); sample = item['sample']
            self.counts['fixed_targets_started'] += 1
            qp = apply_mode(item['source_passive_q6_rad'], 'COMAU', 1)
            if qp.tolist() != item['forced_passive_q6_rad']:
                raise common.StopQualification('APPLY_MODE_DIFFERS_FROM_FIXED_INPUT')
            p2, j2 = self.fk(qp, 2, f'IV_s{sample:03d}_passive')
            passive_rank = rank_data(j2); passive_branch = common.geometric_branch_identity(qp)
            target = p2@physical.FLIP@np.linalg.inv(grasp)
            saved = {'fixed_input': item, 'passive_pose': p2.tolist(),
                'passive_world_jacobian': j2.tolist(), 'passive_rank_report': passive_rank,
                'passive_branch_identity': passive_branch, 'active_target': target.tolist()}
            self.targets.append(saved); common.new_json(self.folder/f'target_s{sample:03d}.json', saved)
            self.evidence.event('target_ready', **saved)
            rows = self.native(item, target)
            for branch, row in enumerate(rows):
                self.budget.remaining(); case = item['branch_request_ids'][branch]
                self.counts['branch_diagnostics_started'] += 1
                result = {'case_id': case, 'sample': sample, 'branch': branch,
                    'native_active_ik': row, 'source_accepted': row['success'],
                    'candidate_q12_rad': None, 'G0_qualified': False, 'G1_qualified': False,
                    'G0_reasons': [], 'G1_additional_reasons': [], 'collision_checked': False,
                    'RBS_checked': False, 'full_RSS_or_planning_pass': False}
                self.observations.append(result)
                if not row['success']:
                    result['G0_reasons'].append('ACTIVE_IK_REJECTED')
                else:
                    self.counts['source_accepted_roots_diagnostics_started'] += 1
                    qa = np.asarray(row['solution'], dtype=float)
                    if not row['finite'] or qa.shape != (6,) or not np.isfinite(qa).all():
                        result['soundness_failure'] = 'SOURCE_ACCEPTED_NONFINITE_OR_INVALID_ROOT'
                        self.evidence.event('source_accepted_soundness_failure', result=result)
                        raise common.StopQualification(result['soundness_failure'])
                    p1, j1 = self.fk(qa, 1, case); q = np.r_[qa, qp]
                    result.update(candidate_q12_rad=q.tolist(), active_pose=p1.tolist(),
                        active_world_jacobian=j1.tolist(), active_roundtrip=common.errors(p1, target),
                        physical_closure=common.errors(p2, p1@grasp@physical.FLIP))
                    if not common.closed(result['active_roundtrip']) or not common.closed(result['physical_closure']):
                        result['soundness_failure'] = 'SOURCE_ACCEPTED_INDEPENDENT_ROUNDTRIP_OR_CLOSURE_FAILED'
                        self.evidence.event('source_accepted_soundness_failure', result=result)
                        raise common.StopQualification(result['soundness_failure'])
                    legal = bool(np.all((bounds[:, 0] <= q)&(q <= bounds[:, 1])))
                    identity = common.geometric_branch_identity(qa)
                    physical_report = cached_closure(p1, j1, p2, j2, grasp)
                    result.update(source_all12_bounds_legal=legal,
                        source_bounds_rad=bounds.tolist(), active_branch_identity=identity,
                        active_rank_report=rank_data(j1), physical_constraint=physical_report,
                        passive_rank_report=passive_rank, passive_branch_identity=passive_branch)
                    if not legal: result['G0_reasons'].append('JOINT_LIMIT_REJECTED')
                    if passive_rank['rank'] != 5:
                        result['G1_additional_reasons'].append('PASSIVE_RANK_NOT_5')
                    if branch not in identity['branch_set']:
                        result['G1_additional_reasons'].append('REQUESTED_ACTIVE_BRANCH_NOT_IN_GEOMETRIC_MEETING_SET')
                    if physical_report['full_rank_report']['rank'] != 6:
                        result['G1_additional_reasons'].append('FULL_PHYSICAL_CONSTRAINT_RANK_NOT_6')
                    self.counts['source_accepted_roots_diagnostics_completed'] += 1
                if passive_rank['rank'] >= 6:
                    result['G0_reasons'].append('PASSIVE_FULL_RANK')
                result['G0_qualified'] = not result['G0_reasons']
                result['G1_qualified'] = result['G0_qualified'] and not result['G1_additional_reasons']
                self.counts['branch_diagnostics_completed'] += 1
                common.new_json(self.folder/(case+'.json'), result)
                self.evidence.event('branch_diagnostics_completed', result=result)
            self.counts['fixed_targets_completed'] += 1

    def native_prefix_accounting(self):
        """Read retained output after return/interruption, never infer starts."""
        confirmed = []; unknown = []; accepted = 0; incomplete_tails = []
        for batch in self.native_batches:
            p = path(batch['path']); rows = []
            if p.exists():
                for line0, raw in enumerate(p.read_bytes().splitlines(keepends=True)):
                    try:
                        row = json.loads(raw)
                    except (ValueError, UnicodeDecodeError):
                        incomplete_tails.append({'path': batch['path'], 'line1': line0+1,
                            'raw_sha256': hashlib.sha256(raw).hexdigest()}); break
                    branch = len(rows)
                    if (branch >= 8 or row.get('schema') != 'P4_SPATIAL_BATCH_V1'
                            or row.get('model') != 4 or row.get('op') != 'K' or row.get('arm') != 1
                            or row.get('input_line') != branch+1 or row.get('branch') != branch
                            or row.get('target') != batch['target']):
                        incomplete_tails.append({'path': batch['path'], 'line1': line0+1,
                            'reason': 'UNQUALIFIED_INTERFACE_ROW'}); break
                    rows.append(row); confirmed.append(batch['request_ids'][branch])
                    # Existing K calls native FK before emitting any success row.
                    if row.get('success') is True and row.get('finite') is True and not row.get('error'):
                        accepted += 1
            unknown.extend(batch['request_ids'][len(rows):])
        self.counts['external_K_JSON_completed'] = len(confirmed)
        self.counts['native_accepted_FK_observed'] = accepted
        return {'external_K_dispatched': self.counts['external_K_dispatched'],
            'external_K_JSON_completed': len(confirmed), 'JSON_completed_request_ids': confirmed,
            'native_accepted_FK_observed': accepted, 'explicit_native_F_operations': 0,
            'internal_true_K_started': 'UNOBSERVED_NO_NATIVE_START_HOOK',
            'internal_true_native_FK_started': 'UNOBSERVED_NO_NATIVE_START_HOOK',
            'unconfirmed_dispatched_request_ids': unknown, 'incomplete_or_unqualified_tails': incomplete_tails,
            'interruption_rule': 'A dispatched unreported request may be unstarted, started or completed; UNKNOWN. Never equate requested cap with actual starts/completions.'}


def execute(spec, protocol):
    started=time.monotonic();cpu_start=common.RunBudget.cpu()
    folder = ROOT/'results/p4_full'/RUN_ID
    if folder.exists(): raise common.StopQualification('OUTPUT_EXISTS_NO_OVERWRITE')
    common.new_json(ROOT/'results/p4_full'/(CLAIM_ID+'.claim.json'),
        {'claim_id': CLAIM_ID, 'parent_pid': os.getpid(), 'protocol_sha256': common.sha(protocol),
         'created_at_utc': common.utc(), 'budget': spec['budget'], 'no_retry_or_reset': True})
    folder.mkdir(parents=True, exist_ok=False)
    budget = common.RunBudget(spec, spec['previous_r2_wall_s'], spec['previous_r2_cpu_s'])
    budget.started=started;budget.cpu_start=cpu_start
    signal.setitimer(signal.ITIMER_REAL,max(.000001,budget.wall_cap-(time.monotonic()-started)))
    q = Qualification(spec, folder, budget); error = None
    record = {'schema': SCHEMA, 'run_id': RUN_ID, 'classification': spec['classification'],
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'command': [sys.executable, str(Path(__file__).resolve()), '--protocol', str(protocol)],
        'started_at_utc': common.utc(), 'protocol_sha256': common.sha(protocol),
        'protocol':str(protocol.relative_to(ROOT)),
        'claim':str((ROOT/'results/p4_full'/(CLAIM_ID+'.claim.json')).relative_to(ROOT)),
        'claim_sha256':common.sha(ROOT/'results/p4_full'/(CLAIM_ID+'.claim.json')),
        'bound_files_sha256': spec['bound_files_sha256'], 'prior_executions': spec['prior_executions'],
        'previous_r2_wall_s': spec['previous_r2_wall_s'], 'previous_r2_cpu_s': spec['previous_r2_cpu_s'],
        'seed': {'source': 20261014, 'effective': 20265014, 'new_RNG_draws': 0},
        'VI_B_budget_charged': False, 'new_VI_candidate_constructions': 0,
        'collision_queries': 0, 'RBS_calls': 0, 'NR_calls': 0, 'RNG_calls': 0,
        'solve_calls': 0, 'formal_planning_calls': 0, 'full_RSS_or_planning_pass': False,
        'original_failures_unchanged': True}
    q.evidence.event('run_started', metadata=record, thread_env_before=THREAD_ENV_BEFORE)
    try:
        q.run(); record['status'] = 'FIXED_100_WRIST_MATHEMATICS_RECORDED'
    except BaseException as exc:
        error = exc; record.update(status='STOP_PREFIX_RETAINED', termination_reason=repr(exc))
        q.evidence.event('run_stopped', termination_reason=repr(exc))
    finally:
        budget.close(); native = q.native_prefix_accounting()
        after = {p: common.sha(path(p)) for p in spec['bound_files_sha256']}
        record['bound_files_after_sha256'] = after
        if after != spec['bound_files_sha256']:
            record.update(status='STOP_BOUND_FILE_CHANGED', source_or_old_input_changed=True)
            if error is None: error = common.StopQualification('BOUND_FILE_CHANGED')
        g0 = [r for r in q.observations if r['G0_qualified']]
        g1 = [r for r in q.observations if r['G1_qualified']]
        done = {r['case_id'] for r in q.observations if 'soundness_failure' not in r
            and (folder/(r['case_id']+'.json')).exists()}
        complete = error is None and q.counts['fixed_targets_completed'] == 100 and len(done) == 800
        soundness_failed = any('soundness_failure' in r for r in q.observations)
        record.update(ended_at_utc=common.utc(), counts=dict(q.counts), native_call_accounting=native,
            target_results=q.targets, branch_observations=q.observations,
            G0_qualified_branches=len(g0), G0_qualified_targets=len({r['sample'] for r in g0}),
            G1_qualified_branches=len(g1), G1_qualified_targets=len({r['sample'] for r in g1}),
            fixed_target_denominator=100, branch_request_denominator=800,
            mathematical_component_gate='PASS_RECONSTRUCTED_MATH_ONLY' if complete and g1 else 'UNKNOWN_OR_FAILED',
            all_source_accepted_roots_sound=True if complete else (False if soundness_failed else None),
            uncompleted_branch_diagnostic_ids=[case for item in spec['fixed_inputs']
                for case in item['branch_request_ids'] if case not in done],
            zero_collision_RBS_NR_RNG_solve=True,
            wall_s=time.monotonic()-budget.started, cpu_s=budget.cpu()-budget.cpu_start)
        record['cumulative_execution_wall_s'] = spec['previous_r2_wall_s']+record['wall_s']
        record['cumulative_execution_cpu_s'] = spec['previous_r2_cpu_s']+record['cpu_s']
        record['r2_remaining'] = {'wall_s': 3600.-record['cumulative_execution_wall_s'],
            'cpu_s': 7200.-record['cumulative_execution_cpu_s']}
        record['protocol_after_sha256']=common.sha(protocol)
        record['claim_after_sha256']=common.sha(ROOT/record['claim'])
        if (record['protocol_after_sha256']!=record['protocol_sha256']or
                record['claim_after_sha256']!=record['claim_sha256']):
            record.update(status='STOP_PROTOCOL_OR_CLAIM_CHANGED',mathematical_component_gate='UNKNOWN_OR_FAILED')
            error=error or common.StopQualification('PROTOCOL_OR_CLAIM_CHANGED')
        if record['wall_s']>=budget.wall_cap or record['cpu_s']>=budget.cpu_cap:
            record.update(status='STOP_WALL_OR_CPU_BUDGET_PREFIX_RETAINED',mathematical_component_gate='UNKNOWN_OR_FAILED')
            error=error or common.StopQualification('WALL_OR_CPU_FINALIZATION_CAP')
        common.new_json(folder/'execution.json', record); q.evidence.events.close()
    print(json.dumps({'status': record['status'], 'counts': record['counts'],
        'component_gate': record['mathematical_component_gate'],
        'wall_s': record['wall_s'], 'cpu_s': record['cpu_s']}, ensure_ascii=False))
    if error is not None: raise error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--describe-protocol', action='store_true')
    parser.add_argument('--validate-draft', type=Path)
    parser.add_argument('--protocol', type=Path)
    args = parser.parse_args()
    if sum(bool(v) for v in vars(args).values()) != 1: parser.error('Choose exactly one mode')
    if args.describe_protocol:
        print(json.dumps(draft_protocol(), ensure_ascii=False, indent=2)); return
    protocol = (args.validate_draft or args.protocol).resolve()
    spec = load(protocol); validate(spec, protocol, execute=bool(args.protocol))
    if args.validate_draft:
        print(json.dumps({'status': 'STATIC_DRAFT_VALIDATED', 'frozen': spec['frozen'],
            'fixed_targets': len(spec['fixed_inputs']), 'K_requests': 800,
            'new_scientific_calls': 0, 'VI_B_remaining': 0,
            'execution_readiness': spec['execution_readiness']}, ensure_ascii=False)); return
    execute(spec, protocol)


if __name__ == '__main__': main()
