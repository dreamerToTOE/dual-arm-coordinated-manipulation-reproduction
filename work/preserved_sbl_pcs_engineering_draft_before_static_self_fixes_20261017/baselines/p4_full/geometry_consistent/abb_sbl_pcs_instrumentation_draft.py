"""Pure reversible original SBL/PCS observations; no files, processes or models.

No H/D/NR correction. Original complete bodies occur once in returning lambdas.
Lifecycle observers only copy live fields and retire saved tokens after delete.
"""
from __future__ import annotations
import hashlib
from .abb_pcs_source_corrections_draft import body_span
APC='proj_classes/apc_class.cpp'
SVC='validity_checkers/StateValidityCheckerPCS.cpp'
COL='validity_checkers/collisionDetection.cpp'
SBL='planners/SBL_PCS.cpp'
HDR='planners/SBL_PCS.h'
ORIGINAL_SBL='a8ebe8a01ad57347096b03621099f5fdf61f78ebcfb6b1635745cfbf4a8cb407'
ORIGINAL_HDR='76d0ba8df05cae6d79575d5b9d63d875f4c56bbd5a6240065d4c0dcf9d396cfc'
def digest(value):return hashlib.sha256(value).hexdigest()
def instrument_sources(original):
    if set(original)!={APC,SVC,COL,SBL,HDR}:raise ValueError('EXACT_SBL_PCS_SOURCE_SET_REQUIRED')
    if digest(original[SBL])!=ORIGINAL_SBL or digest(original[HDR])!=ORIGINAL_HDR:raise ValueError('EXACT_AUTHOR_SBL_BYTES_REQUIRED')
    current=dict(original);edits=[];inverse=[]
    def J(fields):return 'p4sbl::json{'+','.join('{"'+k+'",'+v+'}'for k,v in fields)+'}'
    def wrap(file,signature,kind,result,args,returns,pre='',post=''):
        text=current[file].decode();a,b=body_span(text,signature);body=text[a:b]
        lead='\n const auto p4_id=p4sbl::enabled ? p4sbl::enter("'+kind+'",'+args+') : 0;\n'+pre
        if result=='void':inserted=lead+' [&]() -> void {'+body+'}();\n'+post+' p4sbl::leave(p4_id,"'+kind+'",'+returns+');\n'
        else:inserted=lead+' '+result+' p4_return=[&]() -> '+result+' {'+body+'}();\n'+post+' p4sbl::leave(p4_id,"'+kind+'",'+returns+');\n return p4_return;\n'
        if inserted.count(body)!=1:raise ValueError('COMPLETE_AUTHOR_BODY_ONCE_REQUIRED')
        inverse.append((file,signature,inserted,body));current[file]=(text[:a]+inserted+text[b:]).encode()
        edits.append(dict(file=file,kind='OBSERVE_COMPLETE_BODY',signature=signature,observation_kind=kind,body_sha256=digest(body.encode())))
    state_args=J([('qa12','p4sbl::q12(s1)'),('qb12','p4sbl::q12(s2)'),('active_chain','active_chain'),('branch','ik_sol')])
    vector_args=J([('qa12','p4sbl::joined(qa1,qa2)'),('qb12','p4sbl::joined(qb1,qb2)'),('active_chain','active_chain'),('branch','ik_sol')])
    wrap(SVC,'bool StateValidityChecker::checkMotionRBS(const ob::State *s1, const ob::State *s2, int active_chain, int ik_sol)','state_rbs','bool',state_args,J([('returned','p4_return')]))
    wrap(SVC,'bool StateValidityChecker::checkMotionRBS(State qa1, State qa2, State qb1, State qb2, int active_chain, int ik_sol, int recursion_depth, int non_decrease_count)','vector_rbs','bool',vector_args,J([('returned','p4_return')]))
    wrap(SVC,'bool StateValidityChecker::reconstructRBS(const ob::State *s1, const ob::State *s2, Matrix &Confs, int active_chain, int ik_sol)','state_reconstruct','bool',state_args,J([('returned','p4_return'),('path_q12','Confs')]))
    wrap(SVC,'bool StateValidityChecker::reconstructRBS(State qa1, State qa2, State qb1, State qb2, int active_chain, int ik_sol, Matrix &M, int iteration, int last_index, int firstORsecond)','vector_reconstruct','bool',vector_args,J([('returned','p4_return')]))
    wrap(SVC,'bool StateValidityChecker::IKproject(State &q1, State &q2, int active_chain, int ik_sol)','fixed_branch_project','bool',J([('q12','p4sbl::joined(q1,q2)'),('active_chain','active_chain'),('branch','ik_sol')]),J([('returned','p4_return'),('q12','p4sbl::joined(q1,q2)')]))
    wrap(SVC,'State StateValidityChecker::identify_state_ik(State q1, State q2, State ik)','identify','State',J([('q12','p4sbl::joined(q1,q2)'),('input_ik','ik')]),J([('returned_ik','p4_return')]))
    wrap(APC,'void two_robots::FKsolve_rob(State q, int robot_num)','native_fk','void',J([('q','q'),('robot_num','robot_num')]),'p4sbl::json::object()')
    wrap(APC,'bool two_robots::IKsolve_rob(Matrix T, int robot_num, int solution_num)','native_ik','bool',J([('target','T'),('robot_num','robot_num'),('branch','solution_num')]),J([('returned','p4_return')]))
    wrap(COL,'int collisionDetection::collision_state(Matrix M, State q1, State q2)','collision','int',J([('q12','p4sbl::joined(q1,q2)')]),J([('returned','p4_return')]))
    wrap(COL,'void collisionDetection::load_models()','mesh_load','void','p4sbl::json::object()','p4sbl::json::object()')
    wrap(SBL,'void ompl::geometric::SBL::addMotion(TreeData &tree, Motion *motion)','addMotion','void','p4sbl::json::object()','p4sbl::json::object()',pre=' const auto p4_registered=p4sbl::register_motion(&tree,motion);\n')
    wrap(SBL,'void ompl::geometric::SBL::removeMotion(TreeData &tree, Motion *motion)','removeMotion','void','p4sbl::json::object()','p4sbl::json::object()',pre=' const auto p4_retirement=p4sbl::prepare_retirement(motion);\n',post=' p4sbl::retire(p4_retirement);\n')
    wrap(SBL,'void ompl::geometric::SBL::freeGridMotions(Grid<MotionInfo> &grid)','freeGridMotions','void','p4sbl::json::object()','p4sbl::json::object()',pre=' const auto p4_retirements=p4sbl::prepare_grid(grid);\n',post=' p4sbl::retire_grid(p4_retirements);\n')
    wrap(SBL,'bool ompl::geometric::SBL::isPathValid(TreeData &tree, Motion *motion)','isPathValid','bool',J([('input_motion','p4sbl::snapshot(motion)')]),J([('returned','p4_return')]))
    wrap(SBL,'bool ompl::geometric::SBL::checkSolution(bool start, TreeData &tree, TreeData &otherTree, Motion *motion, std::vector<Motion*> &solution)','checkSolution','bool',J([('start','start'),('motion','p4sbl::snapshot(motion)')]),J([('returned','p4_return')]),pre=' p4sbl::ConnectionScope p4_connection_scope;\n')
    pre=' const auto p4_paths=p4sbl::paths_snapshot(mpath1,mpath2);\n p4sbl::mark("save_source_mpaths",{{"source_mpaths",p4_paths},{"original_save_may_read_uninitialized_historical_connect_a_chain",true}});\n'
    wrap(SBL,'void ompl::geometric::SBL::save2file(vector<Motion*> mpath1, vector<Motion*> mpath2)','save2file','void','p4sbl::json::object()',J([('source_mpaths','p4_paths'),('return_does_not_certify_complete_reconstruction','true')]),pre=pre)
    restored=dict(current)
    for file,signature,inserted,body in reversed(inverse):
        text=restored[file].decode();a,b=body_span(text,signature)
        if text[a:b]!=inserted:raise ValueError('INVERSE_SBL_WRAPPER_BODY_MISMATCH')
        restored[file]=(text[:a]+body+text[b:]).encode()
    if restored!=original:raise ValueError('WHOLE_SBL_SOURCE_BYTES_NOT_REVERSIBLE')
    return current,dict(classification='ORIGINAL_SBL_PCS_CONTROL_WITH_EXISTING_R2_NUMERICS',whole_files_byte_reversible=True,
        original_sha256={k:digest(v)for k,v in original.items()},staged_sha256={k:digest(v)for k,v in current.items()},changes=edits,
        H_or_D_or_NR_correction_present=False,observer_model_calls=0,observer_RNG_draws=0,
        lifecycle_policy='Generation/lifetime registry; pre-delete snapshots; post-delete token retirement; provenance-null a_chain.',
        original_save_uninitialized_historical_connect_risk='SOURCE_ONLY_UNKNOWN_RUNTIME_NOT_AUTHORIZED',
        source_RNG_library_internals='UNOBSERVED_NOT_INFERRED')
