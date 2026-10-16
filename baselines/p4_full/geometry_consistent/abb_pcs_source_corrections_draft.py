"""Project-owned byte-preserving source-correction candidates, NOT staged/run.

Only two independent single-factor edits are permitted.  Author bodies/assets
remain external. This module imports no numerical model and never writes files,
compiles, executes a binary, seeds/shuffles RNG, or calls a scientific function.
"""
from __future__ import annotations
import hashlib
import re

HELPER_SIGNATURE='bool StateValidityChecker::IKproject(State &q1, State &q2, int active_chain)'
DISTANCE_SIGNATURE='double ompl::geometric::CBiRRT::activeDistance(const Motion *a, const Motion *b)'
FACTORS={
    'HELPER_FIRST_IDENTIFIED_SUCCESS_BREAK':{
        'relative_file':'validity_checkers/StateValidityCheckerPCS.cpp',
        'signature':HELPER_SIGNATURE,
        'before':'\t\tif (ik[0]==-1 || ik[1]==-1)\n\t\t\tcontinue;\n',
        'after':'\t\tif (ik[0]==-1 || ik[1]==-1)\n\t\t\tcontinue;\n\t\tbreak;\n'},
    'CBIRRT_ROLE1_FIRST_STATE_DESTINATION':{
        'relative_file':'planners/CBiRRT_PCS.cpp',
        'signature':DISTANCE_SIGNATURE,
        'before':'\t\tretrieveStateVector(a->state, qa_dummy, qb);',
        'after':'\t\tretrieveStateVector(a->state, qa_dummy, qa);'},
}

def digest(data):return hashlib.sha256(data).hexdigest()

def body_span(text,signature):
    if text.count(signature)!=1:raise ValueError('EXACT_SIGNATURE_CARDINALITY_REQUIRED')
    mask=re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
        lambda m:' '*len(m.group()),text,flags=re.S)
    a=mask.index('{',text.index(signature));i=a+1;depth=1
    while depth:
        depth+=(mask[i]=='{')-(mask[i]=='}');i+=1
    return a+1,i-1

def candidate_bytes(original,factor):
    """Return bytes+manifest; caller may write ONLY to a separately frozen new stage.

    No combined-factor option: each starts from its own unmodified original.
    Frozen future builder must bind allowed original SHA and reject occupied stage.
    """
    edit=FACTORS[factor];text=original.decode('utf-8')
    a,b=body_span(text,edit['signature']);body=text[a:b]
    if body.count(edit['before'])!=1:raise ValueError('EXACT_SINGLE_FACTOR_ANCHOR_REQUIRED')
    changed_body=body.replace(edit['before'],edit['after'],1)
    changed=(text[:a]+changed_body+text[b:]).encode('utf-8')
    restored=changed.decode('utf-8')
    ca,cb=body_span(restored,edit['signature']);current=restored[ca:cb]
    if current.count(edit['after'])!=1:raise ValueError('PATCHED_ANCHOR_CARDINALITY_REQUIRED')
    reverted=(restored[:ca]+current.replace(edit['after'],edit['before'],1)+restored[cb:]).encode('utf-8')
    if reverted!=original:raise ValueError('WHOLE_FILE_BYTE_REVERSIBILITY_REQUIRED')
    return changed,{'factor':factor,'relative_file':edit['relative_file'],
        'signature':edit['signature'],'original_sha256':digest(original),
        'candidate_sha256':digest(changed),'original_body_sha256':digest(body.encode()),
        'candidate_body_sha256':digest(changed_body.encode()),'whole_file_reversible':True,
        'classification':'SOURCE_CONTROL_FLOW_CORRECTION_DRAFT_UNBUILT_UNEXECUTED',
        'combined_factors':False,'files_changed':1,'scientific_calls':0,'compile_calls':0}
