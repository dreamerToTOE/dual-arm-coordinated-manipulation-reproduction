"""Pure byte transform of the already qualified V local SVC only.

No I/O, imports of robot modules, model queries, compilation or execution.
Adds the already used II post-return observation ABI, without double-wrapping
the existing V vector-identify wrapper. State-level reconstruction is wrapped.
Reversal must restore the complete input file, including all V local wrappers.
The RRT search file is never an input to this transform and stays unchanged.
"""
from __future__ import annotations
import hashlib
import re

EXPECTED_SVC_SHA256 = 'bdbe5b29125a32c4890f4af5ca77f28bd8830f463d195327f223eab3b6b20509'
RECON = 'bool StateValidityChecker::reconstructRBS(const ob::State *s1, const ob::State *s2, Matrix &Confs, int active_chain, int ik_sol)'
IDENTIFY = 'State StateValidityChecker::identify_state_ik(State q1, State q2, State ik)'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def body_span(source, signature):
    if source.count(signature) != 1:
        raise ValueError('EXACT_BODY_SIGNATURE_REQUIRED')
    mask = re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
                  lambda m: ' ' * len(m.group()), source, flags=re.S)
    begin = mask.index('{', source.index(signature)); at = begin + 1; depth = 1
    while depth and at < len(mask):
        depth += (mask[at] == '{') - (mask[at] == '}'); at += 1
    if depth:
        raise ValueError('UNTERMINATED_SOURCE_BODY')
    return begin + 1, at - 1


def instrument_svc(original):
    if digest(original) != EXPECTED_SVC_SHA256:
        raise ValueError('QUALIFIED_V_LOCAL_SVC_REQUIRED')
    source = original.decode(); changes = []; edits = []
    for signature in (RECON, IDENTIFY):
        a, b = body_span(source, signature); body = source[a:b]
        if signature == RECON:
            inserted = '\n const bool p4_return=[&]() -> bool {' + body + '}();\n p4e2e::observe_reconstruction(s1,s2,active_chain,ik_sol,Confs,p4_return);\n return p4_return;\n'
            if inserted.count(body) != 1:
                raise ValueError('COMPLETE_CURRENT_BODY_RETAINED_ONCE_REQUIRED')
        else:
            anchor = ' p4vpcs::leave(p4_id,"identify",p4vpcs::json{{"returned_ik",p4_return}});'
            if body.count(anchor) != 1 or body.count('State p4_return=[&]() -> State {') != 1:
                raise ValueError('EXACT_QUALIFIED_IDENTIFY_WRAPPER_ANCHOR_REQUIRED')
            inserted = '\n const State p4_input_ik=ik;\n' + body.replace(anchor,
                ' p4e2e::observe_identify(q1,q2,p4_input_ik,p4_return);\n' + anchor)
            if inserted.replace('\n const State p4_input_ik=ik;\n', '', 1).replace(
                    ' p4e2e::observe_identify(q1,q2,p4_input_ik,p4_return);\n', '', 1) != body:
                raise ValueError('IDENTIFY_OBSERVATION_EXPRESSION_REVERSIBILITY_FAILED')
        source = source[:a] + inserted + source[b:]
        changes.append({'signature': signature, 'current_full_body_sha256': digest(body.encode()),
                        'observation': 'EXISTING_II_ABI_POST_RETURN_ONLY_NO_EXTRA_SCIENCE'})
        edits.append((signature, body, inserted))
    restored = source
    for signature, body, inserted in reversed(edits):
        a, b = body_span(restored, signature)
        if restored[a:b] != inserted:
            raise ValueError('EXACT_INSERTED_BODY_REQUIRED_FOR_REVERSAL')
        restored = restored[:a] + body + restored[b:]
    if restored.encode() != original:
        raise ValueError('WHOLE_QUALIFIED_V_SVC_REVERSIBILITY_FAILED')
    return source.encode(), {'schema': 'P4_D080_V_RRT_PCS_E2E_SVC_POST_RETURN_TRANSFORM_V1',
        'input_sha256': digest(original), 'output_sha256': digest(source.encode()),
        'whole_input_file_byte_reversible': True, 'changes': changes,
        'RRT_search_or_save2file_changed': False, 'random_helper_correction': False,
        'five_argument_helper_correction': False, 'additional_model_calls': 0, 'additional_rng_calls': 0}
