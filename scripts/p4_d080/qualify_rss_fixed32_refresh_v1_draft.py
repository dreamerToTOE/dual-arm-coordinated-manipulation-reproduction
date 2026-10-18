#!/usr/bin/env python3
"""Unfrozen D080 thin adapter: reuse exact saved V2 fixed32 mathematics.

No preparation-time imports or model work are requested. Only a separately
committed frozen protocol can reach the unchanged legacy execute() body.
Latest prior is deliberately absent from the checked-in DRAFT.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
SELF=Path(__file__).resolve()
sys.path.insert(0,str(ROOT/'scripts'))
import qualify_p4_full_r2_abb_rss_branch_fixed32_supervised_v2_draft as V
sys.path.insert(0,str(SELF.parent))
import build_v_pcs_local_v1_draft as B

RUN='20261018_R2_D080_ABB_RSS_BRANCH_MATH01'
CLAIM='P4_D080_ABB_RSS_FIXED32_MATH01_THIN_V1_10W20CPU_20261018'
SCHEMA='P4_D080_ABB_RSS_FIXED32_BRANCH_MATH_REFRESH_V1'
TEMPLATE=ROOT/'configs/p4_d080/rss_fixed32_refresh_v1.DRAFT.json'
SUPERVISOR=ROOT/'scripts/p4_d080/supervise_rss_fixed32_refresh_v1_draft.py'
PRE=ROOT/'reports/P4_D080_RSS_FIXED32_THIN_ENGINEERING_REFRESH_PRE_DRAFT_20261018.md'
LEGACY_RUNNER=ROOT/'scripts/qualify_p4_full_r2_abb_rss_branch_fixed32_supervised_v2_draft.py'
LEGACY_SUPERVISOR=ROOT/'scripts/supervise_p4_full_r2_abb_rss_branch_fixed32_v2_draft.py'
LEGACY_TEMPLATE=ROOT/'configs/p4_full/r2_abb_rss_branch_fixed32_math_supervised_v2.draft.json'
LEGACY_PRE=ROOT/'reports/P4_FULL_R2_ABB_RSS_BRANCH_FIXED32_SUPERVISED_V2_PRE_DRAFT_20261017.md'
LEGACY_SHA='4839efdf5b6bb921e1ec82a06074d20dda007365b1d8744f9e72abd343a49862'
LEGACY_SUPERVISOR_SHA='fada7f5aaf9e94d06aeb7572c062ba2dff7b843286ebaa571bf3af293a590619'
LEGACY_TEMPLATE_SHA='da3431b145d1100c26b5dd5593edcbc74e012da08c451bcd800f7d00a204d691'
LEGACY_PRE_SHA='d182443483d429014e1d7cc0016ae3482daf12bcd5cd1e8d08c083d7fec11b02'
B_SHA='1f79c14d02368959fce03c88c4c2f39b99cbdb0bbb5ffd149330a4ef91170578'
OWN=[SELF,SUPERVISOR,PRE,TEMPLATE,LEGACY_RUNNER,LEGACY_SUPERVISOR,LEGACY_TEMPLATE,LEGACY_PRE,
    Path(B.__file__).resolve(),ROOT/'scripts/build_p4_full_r2_abb_cbirrt_d_draft.py',
    ROOT/'baselines/p4_full/geometry_consistent/abb_cbirrt_d_instrumentation_draft.py',
    ROOT/'baselines/p4_full/geometry_consistent/abb_pcs_source_corrections_draft.py']
SCIENCE=('classification','runtime_layer','literal_native_scope','active_arm','passive_arm','passive_branches_in_order',
    'fixed_cases','ik_binary','ik_binary_sha256','budget','gates','target_policy','branch_policy','collision_scope',
    'positive_coverage_gate','stop_policy','new_VI_candidate_constructions','formal_table_I_calls','zero_calls','RSS_gamma_preserved')
require=V.require;path=V.path;sha=V.sha;load=V.load
ORIGINAL_ACTIVE=V.active_p4;ORIGINAL_PROOF=V.supervisor_proof
ACTIVE_SPEC=None;LAUNCH=None


def current_prior():
    # Reuse the reviewed complete prior/Decimal policy; no local substitute.
    require(ACTIVE_SPEC is not None,'NO_IMPLICIT_PRIOR_OR_DESCRIBE_PROTOCOL')
    saved=B.validate_prior(ACTIVE_SPEC);ledger=load(saved['path'])
    require(ledger['d080_scope_config_sha256']==B.SCOPE_SHA and ledger['d080_formal_table_I_required_calls']==18000
        and ledger['d080_formal_table_I_calls']==0 and ledger['d080_VI_status']=='ARCHIVED_OUT_OF_APPROVED_SCOPE_NO_NEW_EXECUTION',
        'D080_LATEST_PRIOR_SCOPE_REQUIRED')
    evidence=dict(saved['evidence_sha256'])
    return {'ledger':saved['path'],'ledger_sha256':saved['sha256'],
        'execution_sha256':{r['execution']:r['execution_sha256']for r in ledger['executions']},
        'wall_s':saved['wall_s'],'cpu_s':saved['cpu_s'],'historical_unmeasured_tail':'RETAINED_UNKNOWN; REMAINING_IS_UPPER_BOUND',
        'evidence_sha256':evidence}


def validate(spec,protocol,execute=False):
    global ACTIVE_SPEC
    require(sha(LEGACY_RUNNER)==LEGACY_SHA and sha(LEGACY_SUPERVISOR)==LEGACY_SUPERVISOR_SHA
        and sha(LEGACY_TEMPLATE)==LEGACY_TEMPLATE_SHA and sha(LEGACY_PRE)==LEGACY_PRE_SHA
        and sha(B.__file__)==B_SHA,'EXACT_UNCHANGED_REUSED_INFRASTRUCTURE_REQUIRED')
    template=load(TEMPLATE);legacy=load(LEGACY_TEMPLATE)
    require(template['frozen']is False and all(v is False for v in template['reviews'].values())
        and all(template[k]is None for k in ('prior','accounting_snapshot','actual_charge_prior','previous_r2_wall_s','previous_r2_cpu_s')),
        'DRAFT_TEMPLATE_MUST_STAY_UNFROZEN_PRIOR_EMPTY')
    require(all(spec[k]==template[k]==legacy[k]for k in SCIENCE),'ALL_ORIGINAL_FIXED32_SCIENCE_BYTES_POLICY_REQUIRED')
    require(spec['schema']==SCHEMA and spec['run_id']==RUN and spec['claim_id']==CLAIM
        and spec['engineering_execution_authorized']is False and spec['formal_execution_authorized']is False,
        'MATH_ONLY_VERSION_IDENTITY_NO_ENGINEERING_OR_FORMAL_EXECUTION')
    mutable={'frozen','reviews','prior','accounting_snapshot','actual_charge_prior','previous_r2_wall_s','previous_r2_cpu_s',
        'own_source_sha256','bound_files_sha256','external_supervision','review_evidence_sha256','qualification_execution_authorized','status'}
    require(set(spec)==set(template)and all(spec[k]==template[k]for k in template if k not in mutable),'EXACT_D080_REFRESH_RECIPE_REQUIRED')
    require(spec['status']=='FROZEN_FIXED32_MATH_ONLY'and spec['frozen']is True
        and spec['qualification_execution_authorized']is True and set(spec['reviews'])==set(template['reviews'])
        and all(type(v)is bool and v for v in spec['reviews'].values()),'EXPLICIT_INDEPENDENT_ROOT_LATEST_PRIOR_FREEZE_REQUIRED')
    require(sha(B.SCOPE)==B.SCOPE_SHA and sha(B.OVERLAY)==B.OVERLAY_SHA,'APPROVED_D080_SCOPE_BYTES_REQUIRED')
    scope=load(B.SCOPE)
    require(scope['allowed_environments']==['I','II','III','IV','V']and scope['formal_table_I_D080']==18000
        and scope['VI_future_science_authorized']is False and scope['formal_execution_authorized']is False,'APPROVED_D080_SCOPE_REQUIRED')
    ACTIVE_SPEC=spec;prior=current_prior()
    require(spec['actual_charge_prior']==prior and spec['accounting_snapshot']=={'path':prior['ledger'],'sha256':prior['ledger_sha256']}
        and spec['previous_r2_wall_s']==prior['wall_s']and spec['previous_r2_cpu_s']==prior['cpu_s'],'EXACT_LATEST_PRIOR_ALL_FIELDS_REQUIRED')
    own={str(q.relative_to(ROOT)):sha(q)for q in OWN}
    require(spec['own_source_sha256']==own,'EXACT_COMMITTED_REFRESH_OWN_SOURCES_REQUIRED')
    expected={str(path(n).resolve()):w for n,w in legacy['bound_files_sha256'].items()}
    expected.update({str(path(n).resolve()):w for n,w in own.items()})
    expected.update({str(B.SCOPE):sha(B.SCOPE),str(B.OVERLAY):sha(B.OVERLAY),'/usr/bin/time':sha('/usr/bin/time'),'/usr/bin/python3':sha('/usr/bin/python3')})
    expected.update(prior['evidence_sha256'])
    require(spec['review_evidence_sha256']and all(sha(n)==w for n,w in spec['review_evidence_sha256'].items()),'PRECISE_INDEPENDENT_REVIEW_EVIDENCE_REQUIRED')
    expected.update({str(path(n).resolve()):w for n,w in spec['review_evidence_sha256'].items()})
    bound={str(path(n).resolve()):w for n,w in spec['bound_files_sha256'].items()}
    require(bound==expected and all(sha(n)==w for n,w in bound.items()),'EXACT_ALL_CURRENT_SCIENCE_OWN_PRIOR_REVIEW_BINDINGS_REQUIRED')
    ext=dict(spec['external_supervision']);expected_ext=dict(template['external_supervision'])
    expected_ext.update(time_binary_sha256=sha('/usr/bin/time'),python_binary_sha256=sha('/usr/bin/python3'))
    require(ext==expected_ext,'EXACT_EXCLUSIVE_SUPERVISION_PATHS_AND_TOOLS_REQUIRED')
    require(tuple(c['case_id']for c in spec['fixed_cases'])==V.IDS and spec['passive_branches_in_order']==list(range(8)),
        'ORIGINAL_FIXED4_BY8_ORDER_REQUIRED')
    for case in spec['fixed_cases']:
        obs=load(case['observations_path'])[case['observation_index0']]
        require(sha(case['observations_path'])==case['observations_sha256']and obs['candidate_q_rad']==case['q12_rad']
            and obs['branch']==case['original_arm1_construction_branch']==1,'ORIGINAL_Q12_SOURCE_RECORD_REQUIRED')
        require(hashlib.sha256(json.dumps(obs,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
            ==case['original_record_canonical_sha256'],'ORIGINAL_RECORD_CANONICAL_BYTES_REQUIRED')
    if not execute:return None
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for name in [*own,*spec['review_evidence_sha256'],str(protocol.relative_to(ROOT))]:
        filename=path(name);relative=str(filename.relative_to(ROOT))
        require(subprocess.check_output(['git','show',commit+':'+relative],cwd=ROOT)==filename.read_bytes(),'COMMITTED_REFRESH_INPUT_REQUIRED_'+relative)
    return commit


def supervisor_proof(spec,protocol):
    global LAUNCH
    LAUNCH=ORIGINAL_PROOF(spec,protocol)
    return LAUNCH


def active_p4():
    require(LAUNCH is not None,'PROVEN_SUPERVISOR_CHAIN_REQUIRED_BEFORE_ACTIVITY_GUARD')
    allowed={os.getpid(),LAUNCH['actual_time_pid'],LAUNCH['supervisor_pid']};rows=ORIGINAL_ACTIVE()
    for entry in Path('/proc').glob('[0-9]*/cmdline'):
        pid=int(entry.parent.name)
        if pid in allowed:continue
        try:parts=entry.read_bytes().split(b'\0')
        except OSError:continue
        exe=parts[0].decode(errors='replace')if parts else ''
        scripts=[v.decode(errors='replace')for v in parts[1:3]]if 'python'in exe else []
        for script in scripts:
            if script.startswith('-'):continue
            try:resolved=(Path('/proc',str(pid),'cwd')/script).resolve(strict=True)
            except OSError:continue
            if resolved.parent==SELF.parent and resolved.name.startswith(('build_','qualify_','supervise_')):
                rows.append({'pid':pid,'command':b' '.join(parts).decode(errors='replace')});break
    return rows


# Only engineering globals/hooks change. V.execute, Budget, NativeOnce and the
# complete mathematical/serialization loop are the original function objects.
V.__file__=str(SELF);V.RUN=RUN;V.CLAIM=CLAIM;V.SCHEMA=SCHEMA;V.SUPERVISOR=str(SUPERVISOR.relative_to(ROOT))
V.OWN=[str(q.relative_to(ROOT))for q in OWN]
V.validate=validate;V.current_prior=current_prior;V.supervisor_proof=supervisor_proof;V.active_p4=active_p4
B.RUN_NAME=RUN;B.RUN=ROOT/'results/p4_full'/RUN


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--protocol',type=Path,required=True)
    args=parser.parse_args();V.execute(args.protocol.resolve())


if __name__=='__main__':main()
