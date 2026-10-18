"""Pure stdlib text transform for the V PCS fixed-local candidate; no I/O.

Inputs are the ALREADY corrected V APC stage, author-original V SVC/RRT,
and the ALREADY aligned collision-v3 stage. This is not an author-native
numerics claim. No H/D/random-helper/five-argument correction is made.
All wrapper bodies and all observation-only expression edits reverse exactly.
Calling this transform performs no model, compiler, collision or RNG operation.
"""
from __future__ import annotations

import hashlib
import re

APC = 'proj_classes/apc_class.cpp'
SVC = 'validity_checkers/StateValidityCheckerPCS.cpp'
COL = 'validity_checkers/collisionDetection.cpp'
RRT = 'planners/RRT_PCS.cpp'
RRT_H = 'planners/RRT_PCS.h'
EXPECTED = {
    APC: '825465213d855f623948c9ee7e263053f67baed7e6907eae4f1549473f516d12',
    SVC: 'beae1a631a7112179bde95b94d518014b6d8ea5cbb7903384189e8fa34ee177e',
    COL: '49e5d675f7d2402ad46cb898287a0dcd08094ca9767ac6cdee3738245b2032ab',
    RRT: '4ea1a052a5e9f2668fd62918c39f5a3820fc0300158f9cef0d51def3cb226b0f',
}


def digest(value):
    return hashlib.sha256(value).hexdigest()


def body_span(text, signature):
    if text.count(signature) != 1:
        raise ValueError('EXACT_SIGNATURE_CARDINALITY_REQUIRED: ' + signature)
    mask = re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
                  lambda match: ' ' * len(match.group()), text, flags=re.S)
    a = mask.index('{', text.index(signature)); i = a + 1; depth = 1
    while depth and i < len(mask):
        depth += (mask[i] == '{') - (mask[i] == '}'); i += 1
    if depth:
        raise ValueError('UNTERMINATED_BODY')
    return a + 1, i - 1


def instrument_sources(original):
    if set(original) != {APC, SVC, COL, RRT, RRT_H}:
        raise ValueError('EXACT_FIVE_SOURCE_INPUTS_REQUIRED')
    for name, want in EXPECTED.items():
        if digest(original[name]) != want:
            raise ValueError('FROZEN_V_INPUT_CHANGED: ' + name)
    current = dict(original); expression_edits = []; wrappers = []; changes = []

    # Name each ACTIVE existing pair, preserving every original PQP argument.
    # Commented-out pairs stay commented out and are not counted or activated.
    text = current[COL].decode('utf-8')
    calls = list(re.finditer(r'^[ \t]*p4_query\(([^;\n]*)\);', text, re.M))
    if len(calls) != 87:
        raise ValueError('EXACT_87_ACTIVE_V3_PAIR_STATEMENTS_REQUIRED')
    identities = []
    for match in reversed(calls):
        args = [part.strip() for part in match.group(1).split(',')]
        if len(args) != 8 or not all(re.fullmatch(r'&[A-Za-z][A-Za-z0-9_]*', args[i]) for i in (3, 6)):
            raise ValueError('EXPECTED_SIMPLE_ORIGINAL_PQP_ARGUMENTS_REQUIRED')
        first, second = args[3][1:], args[6][1:]
        before = match.group(0)
        after = before.replace('p4_query(', 'p4_query_named("' + first + '","' + second + '",', 1)
        expression_edits.append((COL, before, after))
        text = text[:match.start()] + after + text[match.end():]
        identities.insert(0, [first, second])
    before = '\tp4_pose(R6,T6,422.7); p4_pose(R62,T72,400.7);'
    after = before + '\n\tp4vpcs::capture_box(Rbox,Tbox);'
    if text.count(before) != 1:
        raise ValueError('EXACT_V3_TCP_CAPTURE_ANCHOR_REQUIRED')
    expression_edits.append((COL, before, after)); text = text.replace(before, after, 1)
    current[COL] = text.encode('utf-8')

    def J(fields):
        return 'p4vpcs::json{' + ','.join('{"' + k + '",' + v + '}' for k, v in fields) + '}'

    def wrap(file, signature, kind, result, args, returns, pre='', failure='p4vpcs::json::object()'):
        text = current[file].decode('utf-8'); a, b = body_span(text, signature); body = text[a:b]
        lead = '\n const auto p4_id=p4vpcs::enter("' + kind + '",' + args + ');\n try {\n' + pre
        if result == 'void':
            inserted = lead + ' [&]() -> void {' + body + '}();\n p4vpcs::leave(p4_id,"' + kind + '",' + returns + ');\n'
        else:
            inserted = lead + ' ' + result + ' p4_return=[&]() -> ' + result + ' {' + body + '}();\n p4vpcs::leave(p4_id,"' + kind + '",' + returns + ');\n return p4_return;\n'
        inserted += ' } catch (...) { p4vpcs::aborted(p4_id,"' + kind + '",' + failure + '); throw; }\n'
        if inserted.count(body) != 1:
            raise ValueError('EXACT_INPUT_BODY_ONCE_REQUIRED')
        wrappers.append((file, signature, inserted, body))
        current[file] = (text[:a] + inserted + text[b:]).encode('utf-8')
        changes.append(dict(file=file, signature=signature, observation_kind=kind,
                            input_body_sha256=digest(body.encode('utf-8')),
                            full_input_body_unchanged_once=True))

    q = 'p4vpcs::joined(q1,q2)'
    vector_args = [('qa12', 'p4vpcs::joined(qa1,qa2)'), ('qb12', 'p4vpcs::joined(qb1,qb2)'),
                   ('active_chain', 'active_chain'), ('branch', 'ik_sol')]
    wrap(SVC, 'bool StateValidityChecker::IKproject(State &q1, State &q2, int active_chain, int ik_sol)',
         'project_fixed', 'bool', J([('q12', q), ('active_chain', 'active_chain'), ('branch', 'ik_sol')]),
         J([('returned', 'p4_return'), ('q12', q)]))
    wrap(SVC, 'State StateValidityChecker::identify_state_ik(State q1, State q2, State ik)',
         'identify', 'State', J([('q12', q), ('input_ik', 'ik')]), J([('returned_ik', 'p4_return')]))
    wrap(SVC, 'bool StateValidityChecker::isValidRBS(State &q1, State &q2, int active_chain, int IK_sol)',
         'is_valid_rbs', 'bool', J([('q12', q), ('active_chain', 'active_chain'), ('branch', 'IK_sol')]),
         J([('returned', 'p4_return'), ('q12', q)]))
    wrap(SVC, 'bool StateValidityChecker::checkMotionRBS(State qa1, State qa2, State qb1, State qb2, int active_chain, int ik_sol, int recursion_depth, int non_decrease_count)',
         'rbs', 'bool', J(vector_args + [('recursion_depth', 'recursion_depth'), ('non_decrease_count', 'non_decrease_count')]),
         J([('returned', 'p4_return')]))
    wrap(SVC, 'bool StateValidityChecker::reconstructRBS(State qa1, State qa2, State qb1, State qb2, int active_chain, int ik_sol, Matrix &M, int iteration, int last_index, int firstORsecond)',
         'reconstruct', 'bool', J(vector_args + [('iteration', 'iteration'), ('last_index', 'last_index'), ('first_or_second', 'firstORsecond')]),
         J([('returned', 'p4_return'), ('path_q12', 'M')]), failure=J([('partial_path_q12', 'M')]))
    wrap(APC, 'void two_robots::FKsolve_rob(State q, int robot_num)', 'native_fk', 'void',
         J([('q', 'q'), ('robot_num', 'robot_num')]), 'p4vpcs::json::object()')
    wrap(APC, 'bool two_robots::IKsolve_rob(Matrix T, int robot_num, int solution_num)', 'native_ik', 'bool',
         J([('target', 'T'), ('robot_num', 'robot_num'), ('branch', 'solution_num')]), J([('returned', 'p4_return')]))
    for robot, arg in ((1, 'q1'), (2, 'q2')):
        wrap(APC, 'bool two_robots::calc_specific_IK_solution_R' + str(robot) + '(State ' + arg + ', int IKsol)',
             'specific_ik', 'bool', J([('active_q', arg), ('active_chain', str(robot - 1)), ('branch', 'IKsol')]),
             J([('returned', 'p4_return')]))
    wrap(APC, 'bool two_robots::check_angle_limits(State q)', 'limits', 'bool', J([('q12', 'q')]), J([('returned', 'p4_return')]))
    wrap(COL, 'int collisionDetection::collision_state(State q1, State q2)', 'collision', 'int',
         J([('q12', q)]), 'p4vpcs::collision_result(p4_return)', pre=' p4vpcs::begin_collision();\n',
         failure='p4vpcs::json{{"partial_tcp_poses",p4vpcs::poses},{"partial_box_pose",p4vpcs::box_pose},{"partial_pairs",p4vpcs::pairs}}')
    wrap(COL, 'void collisionDetection::load_models()', 'mesh_load', 'void', 'p4vpcs::json::object()', 'p4vpcs::json::object()')

    restored = dict(current)
    for file, signature, inserted, body in reversed(wrappers):
        text = restored[file].decode('utf-8'); a, b = body_span(text, signature)
        if text[a:b] != inserted:
            raise ValueError('EXACT_WRAPPER_INVERSE_REQUIRED')
        restored[file] = (text[:a] + body + text[b:]).encode('utf-8')
    for file, before, after in reversed(expression_edits):
        text = restored[file].decode('utf-8')
        if text.count(after) != 1:
            raise ValueError('EXACT_EXPRESSION_INVERSE_REQUIRED')
        restored[file] = text.replace(after, before, 1).encode('utf-8')
    if restored != original or current[RRT] != original[RRT] or current[RRT_H] != original[RRT_H]:
        raise ValueError('WHOLE_INPUT_FILE_REVERSIBILITY_AND_ORIGINAL_RRT_REQUIRED')
    return current, dict(
        classification='CORRECTED_COMAU_V_APC_WITH_ALIGNED_V3_COLLISION_AND_OBSERVATION_ONLY_PCS',
        status='DRAFT_NOT_BUILT_NOT_QUERIED', whole_input_files_byte_reversible=True,
        input_sha256={k: digest(v) for k, v in original.items()},
        staged_sha256={k: digest(v) for k, v in current.items()}, wrappers=changes,
        active_pair_identities=identities, active_pair_count=87,
        collision_argument_or_pair_changes=0, additional_model_calls=0, additional_rng_calls=0,
        H_random_helper_correction=False, D_CBiRRT_correction=False, five_argument_project_correction=False,
        RRT_search_source_byte_unchanged=True, planner_instantiation_permitted=False,
        author_original_vs_input_stage='APC corrections and collision alignment reuse existing separate certificates; not raw author numerical qualification.')
