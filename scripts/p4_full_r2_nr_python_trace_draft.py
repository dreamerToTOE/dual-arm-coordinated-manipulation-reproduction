#!/usr/bin/env python3
"""Observation adapter DRAFT; imports no numerical module at import time.

Observe the immutable original project_nr at its existing line boundaries.
No solver copy, monkeypatch, extra FK/J, SVD, chart, or acceptance evaluation.
The caller must bind original source/library SHA and include trace overhead in
its wall budget. This file has no main/CLI and cannot launch an experiment.
"""
from __future__ import annotations
import inspect
import sys
from copy import deepcopy


def observe_project_nr(reference, q_input, environment, event_sink=None):
    function=reference.project_nr
    lines,first=inspect.getsourcelines(function)
    def unique(fragment):
        matches=[first+i for i,line in enumerate(lines) if fragment in line]
        if len(matches)!=1:raise RuntimeError('EXACT_ORIGINAL_TRACE_ANCHOR_REQUIRED '+fragment)
        return matches[0]
    before_append=unique("trace.append({'iteration': iteration, **metrics})")
    after_update=unique('if not np.isfinite(q).all():')
    details=[];errors=[]
    def emit(kind,step):
        if event_sink is not None:
            try:event_sink({'event':kind,'step':deepcopy(step)})
            except BaseException as exc:errors.append('EVENT_SINK '+repr(exc))
    def observe(frame,event,arg):
        if frame.f_code is not function.__code__:return None
        if event!='line' or errors:return observe
        values=frame.f_locals
        try:
            if frame.f_lineno==before_append:
                details.append({'iteration':int(values['iteration']),
                    'q_before':values['q'].copy().tolist(),'g':values['g'].copy().tolist(),
                    'j':values['j'].copy().tolist(),'metrics':dict(values['metrics']),
                    'singular_values':[],'cutoff':0.,'numerical_rank':0,
                    'observed_delta_q':[],'q_next':[]})
                emit('STEP_SNAPSHOT',details[-1])
            elif frame.f_lineno==after_update:
                step=details[-1];q_next=values['q'].copy().tolist()
                step.update(singular_values=values['s'].copy().tolist(),
                    cutoff=float(values['s'][0]*values['svd_relative']),
                    numerical_rank=int(values['mask'].sum()),q_next=q_next,
                    observed_delta_q=[a-b for a,b in zip(q_next,step['q_before'])])
                emit('STEP_UPDATE',step)
        except BaseException as exc:
            # A logger failure cannot change the solver's numerical outcome.
            errors.append(repr(exc))
        return observe
    previous=sys.gettrace()
    try:
        sys.settrace(observe)
        result=function(q_input,environment)  # Exact original defaults/body.
    finally:
        sys.settrace(previous)
    if len(details)!=len(result['trace']):errors.append('METRIC_AND_DETAILED_TRACE_LENGTH_MISMATCH')
    for basic,detailed in zip(result['trace'],details):
        if basic!={'iteration':detailed['iteration'],**detailed['metrics']}:
            errors.append('METRIC_AND_DETAILED_TRACE_VALUE_MISMATCH')
    return {'schema':'P4_NR_ABB_PYTHON_ORIGINAL_OBSERVATION_DRAFT_V1',
        'result':result,'detailed_trace':details,'observer_errors':errors,
        'original_body_modified':False,'additional_FK_J_SVD_calls':0,
        'delta_semantics':'Observed rounded q_next minus saved q_before; not an independently recomputed proposal.',
        'accepted_updates_observed':sum(bool(s['q_next']) for s in details)}
