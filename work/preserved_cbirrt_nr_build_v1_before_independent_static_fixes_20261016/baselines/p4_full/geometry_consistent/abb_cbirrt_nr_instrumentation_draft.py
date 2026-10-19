"""Pure byte transforms for original CBiRRT_NR plus the qualified GD seam.

No files, processes, models, protocol or claims. Complete original bodies are
retained in wrappers, except the explicitly preserved original GD numerical
body. Inverse transforms recover every original byte, including CRLF.
"""
from __future__ import annotations
import hashlib
from .abb_pcs_source_corrections_draft import body_span
KDL='proj_classes/kdl_class.cpp'
SVC='validity_checkers/StateValidityCheckerNR.cpp'
COL='validity_checkers/collisionDetection.cpp'
CBI='planners/CBiRRT_NR.cpp'
HDR='planners/CBiRRT_NR.h'
ORIGINAL_CBI='436a89887a7c233f1515800f216e9d626f9f29dee3c230fd8d1ff86567367804'
ORIGINAL_HDR='fe47f4b4d0bd9ab38792ca42c6c3280f622f8a4b0babbce910b4600ba8303338'
GD='bool kdl::GD(State q_init_flip)'
GD_SEAM='\n return p4nr_iface::physical_gd(q_init_flip,T_pose[0][3],L,include_joint_limits,q_solution,IK_counter,IK_time);\n'
def digest(blob):return hashlib.sha256(blob).hexdigest()
def instrument_sources(original):
    if set(original)!={KDL,SVC,COL,CBI,HDR}:raise ValueError('EXACT_CBIRRT_NR_FILES_REQUIRED')
    if digest(original[CBI])!=ORIGINAL_CBI or digest(original[HDR])!=ORIGINAL_HDR:raise ValueError('ORIGINAL_CBIRRT_NR_BYTES_REQUIRED')
    current=dict(original);edits=[];inverse=[]
    text=current[KDL].decode();a,b=body_span(text,GD);gd_original=text[a:b]
    current[KDL]=(text[:a]+GD_SEAM+text[b:]).encode()
    edits.append(dict(file=KDL,kind='EXISTING_QUALIFIED_GD_ONLY_NUMERICAL_SEAM',signature=GD,
        original_body_sha256=digest(gd_original.encode()),seam_body_sha256=digest(GD_SEAM.encode()),
        seam_source='baselines/p4_full/geometry_consistent/abb_nr_interface_kernel_draft.cpp'))
    def J(fields):return 'p4cbnr::json{'+','.join('{"'+k+'",'+v+'}'for k,v in fields)+'}'
    def wrap(file,signature,kind,result,args,returns,pre=''):
        text=current[file].decode();a,b=body_span(text,signature);body=text[a:b]
        lead='\n const auto p4_id=p4cbnr::enabled ? p4cbnr::enter("'+kind+'",'+args+') : 0;\n'+pre
        if result=='void':inserted=lead+' [&]() -> void {'+body+'}();\n if(p4cbnr::enabled)p4cbnr::leave(p4_id,"'+kind+'",'+returns+');\n'
        else:inserted=lead+' '+result+' p4_return=[&]() -> '+result+' {'+body+'}();\n if(p4cbnr::enabled)p4cbnr::leave(p4_id,"'+kind+'",'+returns+');\n return p4_return;\n'
        if inserted.count(body)!=1:raise ValueError('COMPLETE_ORIGINAL_BODY_ONCE_REQUIRED')
        inverse.append((file,signature,inserted,body));current[file]=(text[:a]+inserted+text[b:]).encode()
        edits.append(dict(file=file,kind='OBSERVE_COMPLETE_BODY',signature=signature,observation_kind=kind,body_sha256=digest(body.encode())))
    wrap(HDR,'double distanceFunction(const Motion *a, const Motion *b) const','distanceFunction','double',
        J([('a_motion_id','p4cbnr::identity(a)'),('b_motion_id','p4cbnr::identity(b)'),('qa12','p4cbnr::q12(a->state)'),('qb12','p4cbnr::q12(b->state)')]),J([('distance','p4_return')]))
    wrap(KDL,GD,'nr_gd','bool',J([('input_q12','q_init_flip')]),
        J([('returned','p4_return'),('solution_q12','p4_return ? p4cbnr::json(q_solution) : p4cbnr::json(nullptr)')]))
    wrap(SVC,'bool StateValidityChecker::IKproject(const ob::State *state, bool includeObs)','state_project','bool',
        J([('q12','p4cbnr::q12(state)'),('includeObs','includeObs')]),J([('returned','p4_return'),('q12','p4cbnr::q12(state)')]))
    wrap(SVC,'bool StateValidityChecker::IKproject(State &q, bool includeObs)','vector_project','bool',
        J([('q12','q'),('includeObs','includeObs')]),J([('returned','p4_return'),('q12','q')]))
    wrap(SVC,'bool StateValidityChecker::isValidRBS(State &q)','nr_valid_midpoint','bool',J([('q12','q')]),J([('returned','p4_return'),('q12','q')]))
    state_args=J([('qa12','p4cbnr::q12(s1)'),('qb12','p4cbnr::q12(s2)')])
    wrap(SVC,'bool StateValidityChecker::checkMotionRBS(const ob::State *s1, const ob::State *s2)','state_rbs','bool',state_args,J([('returned','p4_return')]))
    wrap(SVC,'bool StateValidityChecker::checkMotionRBS(State s1, State s2, int recursion_depth, int non_decrease_count)','vector_rbs','bool',
        J([('qa12','s1'),('qb12','s2'),('recursion_depth','recursion_depth'),('non_decrease_count','non_decrease_count')]),J([('returned','p4_return')]))
    wrap(SVC,'bool StateValidityChecker::reconstructRBS(const ob::State *s1, const ob::State *s2, Matrix &Confs)','state_reconstruct','bool',state_args,J([('returned','p4_return'),('path_q12','Confs')]))
    wrap(SVC,'bool StateValidityChecker::reconstructRBS(State q1, State q2, Matrix &M, int iteration, int last_index, int firstORsecond)','vector_reconstruct','bool',
        J([('qa12','q1'),('qb12','q2'),('iteration','iteration'),('last_index','last_index'),('firstORsecond','firstORsecond')]),J([('returned','p4_return')]))
    wrap(COL,'int collisionDetection::collision_state(Matrix M, State q1, State q2)','collision','int',J([('q1','q1'),('q2','q2')]),J([('returned','p4_return')]))
    wrap(COL,'void collisionDetection::load_models()','mesh_load','void','p4cbnr::json::object()','p4cbnr::json::object()')
    wrap(CBI,'ompl::geometric::CBiRRT::Motion* ompl::geometric::CBiRRT::growTree(TreeData &tree, TreeGrowingInfo &tgi, Motion *nmotion, Motion *tmotion, Motion *rmotion, int mode, int count_iterations)',
        'growTree','Motion*',J([('nearest_id','p4cbnr::identity(nmotion)'),('target_id','p4cbnr::identity(tmotion)'),('mode','mode'),('iteration_limit','count_iterations')]),
        J([('returned_motion_id','p4cbnr::identity(p4_return)'),('returned_q12','p4cbnr::q12(p4_return->state)'),('reached','growTree_reached')]))
    pre=' p4cbnr::json p4_paths=p4cbnr::json::array();\n if(p4cbnr::enabled)for(const auto& side:{mpath1,mpath2}){p4cbnr::json p=p4cbnr::json::array();for(auto* m:side)p.push_back({{"motion_id",p4cbnr::identity(m)},{"parent_id",p4cbnr::identity(m->parent)},{"state_id",p4cbnr::identity(m->state)},{"q12",p4cbnr::q12(m->state)}});p4_paths.push_back(p);}\n p4cbnr::mark("save_source_mpaths",{{"source_mpaths",p4_paths}});\n'
    wrap(CBI,'void ompl::geometric::CBiRRT::save2file(vector<Motion*> mpath1, vector<Motion*> mpath2)','save2file','void','p4cbnr::json::object()',
        J([('source_mpaths','p4_paths'),('return_does_not_certify_complete_reconstruction','true')]),pre)
    needle=b'std::remove("./paths/temp.txt");';replacement=b'/* P4 CBiNR I/O observation: retain ./paths/temp.txt verbatim. */'
    if current[CBI].count(needle)!=1:raise ValueError('UNIQUE_ORIGINAL_TEMP_REMOVE_REQUIRED')
    current[CBI]=current[CBI].replace(needle,replacement);edits.append(dict(file=CBI,kind='RETAIN_TEMP_IO_ONLY'))
    restored=dict(current);restored[CBI]=restored[CBI].replace(replacement,needle)
    for file,signature,inserted,body in reversed(inverse):
        text=restored[file].decode();a,b=body_span(text,signature)
        if text[a:b]!=inserted:raise ValueError('INVERSE_WRAPPER_BODY_MISMATCH')
        restored[file]=(text[:a]+body+text[b:]).encode()
    text=restored[KDL].decode();a,b=body_span(text,GD)
    if text[a:b]!=GD_SEAM:raise ValueError('INVERSE_GD_SEAM_MISMATCH')
    restored[KDL]=(text[:a]+gd_original+text[b:]).encode()
    if restored!=original:raise ValueError('WHOLE_FILES_NOT_BYTE_REVERSIBLE')
    return current,dict(classification='ORIGINAL_CBIRRT_NR_CONTROL_WITH_EXISTING_PHYSICAL_GD_SEAM',whole_files_byte_reversible=True,
        original_sha256={n:digest(v)for n,v in original.items()},staged_sha256={n:digest(v)for n,v in current.items()},changes=edits,
        full12_distance_original=True,active_role_or_analytic_branch=False,H_or_D_correction_present=False,
        observer_model_calls=0,observer_RNG_draws=0,source_RNG_library_internals='UNOBSERVED_NOT_INFERRED')
