"""D-only byte-preserving observation transforms; no files/processes/models.

Each complete author function body is retained once in a returning lambda.
Inverse transform is checked against the complete original file, including CRLF.
H/random-helper corrections are not available from this module.
"""
from __future__ import annotations
import hashlib
from .abb_pcs_source_corrections_draft import body_span,candidate_bytes
APC='proj_classes/apc_class.cpp'
SVC='validity_checkers/StateValidityCheckerPCS.cpp'
COL='validity_checkers/collisionDetection.cpp'
CBI='planners/CBiRRT_PCS.cpp'
FACTORS=('source_control','distance_destination_fix')
ORIGINAL_CBI='60f6a483c533f61749bc7e741acc72bfc8cc2e137d719b25392e73831e458d93'
FIXED_CBI='5b87ed08d674251594efc899ad922398f9c29a0a42f74494cafa7fa2424ae5c2'
DIST='double ompl::geometric::CBiRRT::activeDistance(const Motion *a, const Motion *b)'
def digest(b):return hashlib.sha256(b).hexdigest()

def instrument_sources(original,factor):
    if factor not in FACTORS or set(original)!={APC,SVC,COL,CBI}:raise ValueError('EXACT_D_TARGET_AND_FILES_REQUIRED')
    if digest(original[CBI])!=ORIGINAL_CBI:raise ValueError('ORIGINAL_CBI_BYTES_REQUIRED')
    current=dict(original);edits=[]
    if factor=='distance_destination_fix':
        current[CBI],m=candidate_bytes(original[CBI],'CBIRRT_ROLE1_FIRST_STATE_DESTINATION')
        if digest(current[CBI])!=FIXED_CBI:raise ValueError('SINGLE_TOKEN_CANDIDATE_HASH_REQUIRED')
        edits.append(dict(file=CBI,kind='D_SINGLE_TOKEN',manifest=m))
    inverse=[]
    def wrap(file,signature,kind,result,args,returns,pre='',post=''):
        text=current[file].decode();a,b=body_span(text,signature);body=text[a:b]
        leading='\n const auto p4_id=p4cb::enabled ? p4cb::enter("'+kind+'",'+args+') : 0;\n'+pre
        if result=='void':
            inserted=leading+' [&]() -> void {'+body+'}();\n'+post+' p4cb::leave(p4_id,"'+kind+'",'+returns+');\n'
        else:
            inserted=leading+' '+result+' p4_return=[&]() -> '+result+' {'+body+'}();\n'+post+' p4cb::leave(p4_id,"'+kind+'",'+returns+');\n return p4_return;\n'
        changed=(text[:a]+inserted+text[b:]).encode()
        if inserted.count(body)!=1:raise ValueError('COMPLETE_BODY_RETAINED_ONCE_REQUIRED')
        inverse.append((file,signature,inserted,body));current[file]=changed
        edits.append(dict(file=file,kind='OBSERVE_COMPLETE_BODY',signature=signature,
            body_sha256=digest(body.encode()),observation_kind=kind))
    J=lambda fields:'p4cb::json{'+','.join('{"'+k+'",'+v+'}'for k,v in fields)+'}'
    state_args=J([('qa12','p4cb::q12(s1)'),('qb12','p4cb::q12(s2)'),('active_chain','active_chain'),('branch','ik_sol')])
    vector_args=J([('qa12','p4cb::joined(qa1,qa2)'),('qb12','p4cb::joined(qb1,qb2)'),('active_chain','active_chain'),('branch','ik_sol')])
    wrap(CBI,DIST,'activeDistance','double',J([('a_motion_id','p4cb::identity(a)'),('b_motion_id','p4cb::identity(b)'),('qa12','p4cb::q12(a->state)'),('qb12','p4cb::q12(b->state)'),('active_chain','active_chain')]),J([('distance','p4_return')]))
    wrap(SVC,'bool StateValidityChecker::checkMotionRBS(const ob::State *s1, const ob::State *s2, int active_chain, int ik_sol)','state_rbs','bool',state_args,J([('returned','p4_return')]))
    wrap(SVC,'bool StateValidityChecker::checkMotionRBS(State qa1, State qa2, State qb1, State qb2, int active_chain, int ik_sol, int recursion_depth, int non_decrease_count)','vector_rbs','bool',vector_args,J([('returned','p4_return')]))
    wrap(SVC,'bool StateValidityChecker::reconstructRBS(const ob::State *s1, const ob::State *s2, Matrix &Confs, int active_chain, int ik_sol)','state_reconstruct','bool',state_args,J([('returned','p4_return'),('path_q12','Confs')]))
    wrap(SVC,'bool StateValidityChecker::reconstructRBS(State qa1, State qa2, State qb1, State qb2, int active_chain, int ik_sol, Matrix &M, int iteration, int last_index, int firstORsecond)','vector_reconstruct','bool',vector_args,J([('returned','p4_return')]))
    wrap(SVC,'bool StateValidityChecker::IKproject(State &q1, State &q2, int active_chain, int ik_sol)','fixed_branch_project','bool',J([('q12','p4cb::joined(q1,q2)'),('active_chain','active_chain'),('branch','ik_sol')]),J([('returned','p4_return'),('q12','p4cb::joined(q1,q2)')]))
    wrap(SVC,'State StateValidityChecker::identify_state_ik(State q1, State q2, State ik)','identify','State',J([('q12','p4cb::joined(q1,q2)'),('input_ik','ik')]),J([('returned_ik','p4_return')]))
    wrap(APC,'void two_robots::FKsolve_rob(State q, int robot_num)','native_fk','void',J([('q','q'),('robot_num','robot_num')]),'p4cb::json::object()')
    wrap(APC,'bool two_robots::IKsolve_rob(Matrix T, int robot_num, int solution_num)','native_ik','bool',J([('target','T'),('robot_num','robot_num'),('branch','solution_num')]),J([('returned','p4_return')]))
    wrap(COL,'int collisionDetection::collision_state(Matrix M, State q1, State q2)','collision','int',J([('q12','p4cb::joined(q1,q2)')]),J([('returned','p4_return')]))
    wrap(COL,'void collisionDetection::load_models()','mesh_load','void','p4cb::json::object()','p4cb::json::object()')
    grow='ompl::geometric::CBiRRT::Motion* ompl::geometric::CBiRRT::growTree(TreeData &tree, TreeGrowingInfo &tgi, Motion *nmotion, Motion *tmotion, Motion *rmotion, int mode, int count_iterations)'
    wrap(CBI,grow,'growTree','Motion*',J([('nearest_id','p4cb::identity(nmotion)'),('target_id','p4cb::identity(tmotion)'),('mode','mode'),('iteration_limit','count_iterations')]),J([('returned_motion_id','p4cb::identity(p4_return)'),('returned_q12','p4cb::q12(p4_return->state)'),('active_chain','active_chain'),('reached','growTree_reached')]))
    # Observe only initialized tree motions. Do not read branch/a_chain fields
    # from temporary probe/sample motions, whose author constructor omits them.
    save='void ompl::geometric::CBiRRT::save2file(vector<Motion*> mpath1, vector<Motion*> mpath2)'
    save_pre=' p4cb::json p4_paths=p4cb::json::array();\n if(p4cb::enabled)for(const auto& side:{mpath1,mpath2}) {p4cb::json p=p4cb::json::array();for(auto* m:side)p.push_back({{"motion_id",p4cb::identity(m)},{"parent_id",p4cb::identity(m->parent)},{"q12",p4cb::q12(m->state)},{"ik_q1_active",m->ik_q1_active},{"ik_q2_active",m->ik_q2_active},{"a_chain",m->a_chain}});p4_paths.push_back(p);}\n p4cb::mark("save_source_mpaths",{{"source_mpaths",p4_paths}});\n'
    wrap(CBI,save,'save2file','void','p4cb::json::object()',J([('source_mpaths','p4_paths'),('return_does_not_certify_complete_reconstruction','true')]),pre=save_pre)
    needle=b'std::remove("./paths/temp.txt");';replacement=b'/* P4 D I/O observation: retain ./paths/temp.txt verbatim. */'
    if current[CBI].count(needle)!=1:raise ValueError('EXACT_TEMP_REMOVE_REQUIRED')
    current[CBI]=current[CBI].replace(needle,replacement);edits.append(dict(file=CBI,kind='RETAIN_TEMP_IO_ONLY'))
    restored=dict(current);restored[CBI]=restored[CBI].replace(replacement,needle)
    for file,signature,inserted,body in reversed(inverse):
        text=restored[file].decode();a,b=body_span(text,signature)
        if text[a:b]!=inserted:raise ValueError('INVERSE_BODY_MISMATCH')
        restored[file]=(text[:a]+body+text[b:]).encode()
    if factor=='distance_destination_fix':
        restored[CBI]=restored[CBI].replace(b'\t\tretrieveStateVector(a->state, qa_dummy, qa);',b'\t\tretrieveStateVector(a->state, qa_dummy, qb);',1)
    if restored!=original:raise ValueError('WHOLE_SOURCE_BYTES_NOT_REVERSIBLE')
    return current,dict(factor=factor,H_patch_present=False,whole_files_byte_reversible=True,
        original_sha256={k:digest(v)for k,v in original.items()},staged_sha256={k:digest(v)for k,v in current.items()},
        changes=edits,observer_model_calls=0,observer_RNG_draws=0,
        unhooked_source_RNG_internals='UNOBSERVED_NOT_INFERRED_FROM_SOURCE_RETURNS')
