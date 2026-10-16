"""Pure byte transforms for H only. No file writes or numerical imports.

Original complete bodies are retained literally inside returning lambdas.
Three explicit helper observation insertions are byte-reversible. Every edit
is undone in reverse order and the entire source map must equal its input.
"""
from __future__ import annotations
import hashlib
from baselines.p4_full.geometry_consistent.abb_pcs_source_corrections_draft import (
    HELPER_SIGNATURE,body_span,candidate_bytes,
)
SVC='validity_checkers/StateValidityCheckerPCS.cpp'
APC='proj_classes/apc_class.cpp'
COL='validity_checkers/collisionDetection.cpp'
FACTORS=('source_control','success_break')
def digest(b):return hashlib.sha256(b).hexdigest()
def instrument_sources(sources,factor):
    if factor not in FACTORS:raise ValueError('ONLY_H_INDEPENDENT_FACTOR_ALLOWED')
    original=dict(sources);data=dict(sources);operations=[];correction=None
    if factor=='success_break':
        data[SVC],correction=candidate_bytes(data[SVC],'HELPER_FIRST_IDENTIFIED_SUCCESS_BREAK')
    corrected=dict(data)
    def replace_body(path,sig,transform):
        text=data[path].decode('utf-8');a,b=body_span(text,sig);before=text[a:b]
        after=transform(before)
        if before==after:raise ValueError('NO_OBSERVATION_INSERTED')
        data[path]=(text[:a]+after+text[b:]).encode('utf-8')
        operations.append((path,sig,before,after))
    def wrap(path,sig,kind,args,result,return_type):
        def change(body):
            lead='\n auto p4h_id=p4helper::enter("'+kind+'",'+args+');\n'
            if return_type=='void':
                middle=' [&]() -> void {'+body+'}();\n'
                tail=' p4helper::leave(p4h_id,"'+kind+'",'+result+');\n'
            else:
                middle=' '+return_type+' p4h_return=[&]() -> '+return_type+' {'+body+'}();\n'
                tail=' p4helper::leave(p4h_id,"'+kind+'",'+result+');\n return p4h_return;\n'
            assert middle.count(body)==1
            return lead+middle+tail
        replace_body(path,sig,change)
    def helper_marks(body):
        anchors=[
            ('\tstd::random_shuffle( IKsol.begin(), IKsol.end() );',
             '\n\tp4helper::mark("shuffle_completed",{{"order",IKsol}});'),
            ('\tfor (i = 0; i < IKsol.size(); i++) {',
             '\n\t\tp4helper::mark("branch_entered",{{"loop_index",i},{"branch",IKsol[i]},{"active_chain",active_chain},{"q1",q1},{"q2",q2}});'),
            ('\t\tState ik = identify_state_ik(q1, q2);',
             '\n\t\tp4helper::mark("identify_completed_in_helper",{{"loop_index",i},{"branch",IKsol[i]},{"q1",q1},{"q2",q2},{"ik",ik}});'),
        ]
        changed=body
        for anchor,insert in anchors:
            if changed.count(anchor)!=1:raise ValueError('HELPER_OBSERVER_ANCHOR_CARDINALITY')
            changed=changed.replace(anchor,anchor+insert,1)
        restored=changed
        for anchor,insert in reversed(anchors):restored=restored.replace(anchor+insert,anchor,1)
        if restored!=body:raise ValueError('HELPER_MARKS_NOT_BYTE_REVERSIBLE')
        return changed
    replace_body(SVC,HELPER_SIGNATURE,helper_marks)
    wrap(SVC,HELPER_SIGNATURE,'helper_three',
         '{{"q1",q1},{"q2",q2},{"active_chain",active_chain}}',
         '{{"returned",p4h_return},{"q1",q1},{"q2",q2}}','bool')
    wrap(SVC,'State StateValidityChecker::identify_state_ik(State q1, State q2, State ik)',
         'identify','{{"q1",q1},{"q2",q2},{"input_ik",ik}}','{{"ik",p4h_return}}','State')
    wrap(APC,'void two_robots::FKsolve_rob(State q, int robot_num)','native_fk',
         '{{"q6",q},{"arm",robot_num}}','p4helper::json::object()','void')
    wrap(APC,'bool two_robots::IKsolve_rob(Matrix T, int robot_num, int solution_num)',
         'native_ik','{{"T",T},{"arm",robot_num},{"branch",solution_num}}',
         '{{"returned",p4h_return}}','bool')
    for role in (1,2):
        wrap(APC,f'bool two_robots::calc_specific_IK_solution_R{role}(Matrix T, State q{role}, int IKsol)',
             'calc_R'+str(role),'{{"T",T},{"active_q",q'+str(role)+'},{"branch",IKsol}}',
             '{{"returned",p4h_return}}','bool')
    wrap(APC,'bool two_robots::check_angle_limits(State q)','source_limits',
         '{{"q",q}}','{{"returned",p4h_return}}','bool')
    wrap(COL,'int collisionDetection::collision_state(Matrix M, State q1, State q2)',
         'collision','{{"q1",q1},{"q2",q2}}','{{"returned",p4h_return}}','int')
    restored=dict(data)
    for path,sig,before,after in reversed(operations):
        text=restored[path].decode('utf-8');a,b=body_span(text,sig)
        if text[a:b]!=after:raise ValueError('REVERSE_OBSERVER_BODY_MISMATCH')
        restored[path]=(text[:a]+before+text[b:]).encode('utf-8')
    if restored!=corrected:raise ValueError('WHOLE_SOURCE_OBSERVER_REVERSAL_FAILED')
    if factor=='source_control' and restored!=original:raise ValueError('SOURCE_CONTROL_CHANGED')
    return data,{'factor':factor,'correction':correction,'observer_reversible_to_corrected_bytes':True,
        'source_control_reversible_to_original_bytes':factor=='source_control',
        'complete_body_wrappers':len(operations)-1,'helper_observation_insertions':3,
        'original_sha256':{p:digest(v) for p,v in original.items()},
        'corrected_pre_observation_sha256':{p:digest(v) for p,v in corrected.items()},
        'instrumented_sha256':{p:digest(v) for p,v in data.items()},
        'query_calls':0,'compile_calls':0,'scientific_calls':0,'internal_caps':False}
