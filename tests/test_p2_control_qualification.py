"""Predeclared Gate C component qualification; written before implementation.

No trajectories/control trials. Fixed frozen A fixture, seed-free synthetic right
perturbation, published U=[(.003,-.002,.001,.02,-.01,.01),0]. Matrix Exp/Log
oracles are scipy.linalg.expm/logm, not controller geometry. Original algebra
atol=1e-10 and projection residual=1e-9 are retained component-wise. Fixed
reference times 0/3/7/13/17/23/55/76/95; no threshold or parameter search.
Root runs only after the independently registered Gate D passes and records the
science source/hash; a component qualification is not a primary control case.
"""
import json
from pathlib import Path

import numpy as np
import pytest
from scipy.linalg import expm, logm, block_diag

from baselines.p2_pose_force import mechanics as mech
from baselines.p2_pose_force.observations import FilterState
from baselines.p2_pose_force.control import (
    ControlDomainError, PoseForceController, QuinticReference, SlidingReference,
    ReferenceSample,
)

ROOT=Path(__file__).resolve().parents[1]
ATOL=1e-10


@pytest.fixture
def protocol(): return json.loads((ROOT/'configs/p2_closed_loop_protocol_v1.json').read_text())


def hat(x):
    a=np.zeros((4,4)); x=np.asarray(x); v,w=x[:3],x[3:]
    a[:3,:3]=[[0,-w[2],w[1]],[w[2],0,-w[0]],[-w[1],w[0],0]]; a[:3,3]=v
    return a


def logarithm(T):
    m=logm(T); assert np.max(np.abs(m.imag))<1e-10; m=m.real
    return np.r_[m[:3,3],m[2,1],m[0,2],m[1,0]]


def ad(T):
    R=T[:3,:3]; x,y,z=T[:3,3]; S=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
    return np.block([[R,S@R],[np.zeros((3,3)),R]])


@pytest.fixture
def estimate(protocol):
    s=FilterState.from_mechanics(mech.initial_state(protocol))
    d=np.zeros(42); d[:6]=[.0002,-.0001,.0001,.02,-.015,.01]
    d[12:18]=[.0001,-.0001,0,.01,0,-.005]
    d[24:30]=[.0005,-.0002,.0001,0,.002,.001]
    s=s.retract(d); s.V=np.array([.005,-.003,.002,.02,-.015,.01]); return s


def oracle(state,U,modes,physics):
    Hs=[np.eye(6) if m=='tight' else np.eye(6)[:5] if m=='pivot' else np.eye(6)[2:] for m in modes]
    H=block_diag(*Hs); forces=[]; maps=[]; As=[]
    Es=(state.E1,np.linalg.inv(state.C)@state.E2)
    for r,(E,G) in enumerate(zip(Es,(state.G1,state.G2))):
        D=np.linalg.inv(E)@state.O@G; Rbar=block_diag(D[:3,:3],D[:3,:3])
        forces.append(-physics.K[r]*logarithm(D)-physics.B*(Rbar@ad(np.linalg.inv(G))@state.V-U[r]))
        A=np.linalg.inv(state.O)@E; As.append(A); maps.append(ad(np.linalg.inv(A)).T)
    W=np.hstack(maps)@H.T; h=np.array(forces).ravel()
    hI=H.T@(np.eye(H.shape[0])-np.linalg.pinv(W,rcond=1e-12)@W)@H@h
    return hI.reshape(2,6),H,W,As


@pytest.mark.parametrize('condition',['exp1','exp2','exp3','exp4'])
def test_original_laws_and_condition_switches(protocol,estimate,condition):
    ctrl=PoseForceController.from_protocol(protocol,condition)
    ref=QuinticReference(protocol); ref.sample(13,estimate.O); desired=ref.sample(17,estimate.O)
    held=np.array([[.003,-.002,.001,.02,-.01,.01],[0,0,0,0,0,0]])
    result=ctrl.evaluate(estimate,held,desired,('pivot','pivot'),17,diagnostic_GT=True)
    physics=mech.physics_from_protocol(protocol,condition=condition,observer=True)
    hI,H,W,As=oracle(estimate,held,('pivot','pivot'),physics)
    np.testing.assert_allclose(result.h_internal,hI,atol=ATOL,rtol=0)
    np.testing.assert_allclose(W@(H@result.h_internal.ravel()),0,atol=1e-9,rtol=0)
    error=logarithm(np.linalg.inv(estimate.O)@desired.pose)
    ff=ad(np.linalg.inv(estimate.O)@desired.pose)@desired.body_twist
    gains=protocol['original_parameters']
    UF=np.array([-np.array(gains['KF'+str(r+1)])*hI[r] for r in range(2)])
    if condition=='exp1': UF[:]=0
    kp=np.zeros(6) if condition=='exp2' else np.array(gains['KP'])
    UP=np.array([ad(np.linalg.inv(A))@(ff+kp*error) for A in As])
    np.testing.assert_allclose(result.U_F,UF,atol=ATOL,rtol=0)
    np.testing.assert_allclose(result.U_P,UP,atol=ATOL,rtol=0)
    np.testing.assert_allclose(result.U_cmd,UF+UP,atol=ATOL,rtol=0)
    np.testing.assert_allclose(result.U_selected,(H.T@H@(UF+UP).ravel()).reshape(2,6),atol=ATOL,rtol=0)
    if condition=='exp2': assert np.linalg.norm(result.U_P)>0
    nominal=mech.physics_from_protocol(protocol)
    np.testing.assert_array_equal(nominal.K[0],gains['K_nominal'])
    if condition=='exp4': np.testing.assert_array_equal(ctrl.physics.K[0],gains['exp4_model_K1'])


def test_old_published_input_is_the_only_model_input(protocol,estimate):
    calls=[]
    def provider(state,U,modes,physics):
        calls.append(np.array(U,copy=True)); return mech.mechanics(state,U,modes,physics)
    ctrl=PoseForceController.from_protocol(protocol,'exp3',contact_provider=provider)
    held=np.array([[.003,-.002,.001,.02,-.01,.01],[0,0,0,0,0,0]])
    desired=ReferenceSample(estimate.O.copy(),np.zeros(6),None)
    result=ctrl.evaluate(estimate,held,desired,('pivot','pivot'),7,diagnostic_GT=True)
    assert len(calls)==1; np.testing.assert_array_equal(calls[0],held)
    assert not np.shares_memory(result.U_published,held)
    assert not np.array_equal(result.U_cmd,held)


def test_truth_requires_explicit_diagnostic_and_mechanics_state_is_not_controller_input(protocol,estimate):
    ctrl=PoseForceController.from_protocol(protocol,'exp3')
    desired=ReferenceSample(estimate.O.copy(),np.zeros(6),None)
    with pytest.raises(ControlDomainError): ctrl.evaluate(estimate,np.zeros((2,6)),desired,('pivot','pivot'),7)
    with pytest.raises(ControlDomainError): ctrl.evaluate(mech.initial_state(protocol),np.zeros((2,6)),desired,('pivot','pivot'),7,diagnostic_GT=True)


def test_manual_lift_and_feedback_timing(protocol,estimate):
    ctrl=PoseForceController.from_protocol(protocol,'exp3')
    desired=ReferenceSample(estimate.O.copy(),np.zeros(6),None)
    for t in (0.,1.5,3.,6.,7.,13.,95.):
        r=ctrl.evaluate(estimate,np.zeros((2,6)),desired,('pivot','pivot'),t,diagnostic_GT=True)
        if 0<t<3:
            speed=.01*(30*.5**2-60*.5**3+30*.5**4)/3
            for side,E in enumerate((estimate.E1,estimate.E2)):
                commonR=E[:3,:3] if side==0 else estimate.C[:3,:3].T@E[:3,:3]
                np.testing.assert_allclose(commonR@r.U_cmd[side,:3],[0,0,speed],atol=ATOL,rtol=0)
        if t<7 or t==95: np.testing.assert_array_equal(r.U_F,np.zeros((2,6)))
        if 3<=t<7: np.testing.assert_array_equal(r.U_cmd,np.zeros((2,6)))
        assert r.force_active==(7<=t<95)
        assert r.pose_active==(13<=t<=95)


def test_geodesic_reference_body_velocity_and_own_segment_starts(protocol,estimate):
    ref=QuinticReference(protocol)
    first=ref.sample(13,estimate.O)
    np.testing.assert_array_equal(first.pose,estimate.O)
    np.testing.assert_array_equal(first.body_twist,np.zeros(6))
    mid=ref.sample(17,estimate.O)
    target=np.eye(4); target[:3,3]=[0,0,.5]
    xi=logarithm(np.linalg.inv(estimate.O)@target)
    a=.4; s=10*a**3-15*a**4+6*a**5; rate=(30*a*a-60*a**3+30*a**4)/10
    np.testing.assert_allclose(mid.pose,estimate.O@expm(hat(s*xi)),atol=ATOL,rtol=0)
    np.testing.assert_allclose(mid.body_twist,rate*xi,atol=ATOL,rtol=0)
    other=estimate.O@expm(hat([.001,-.002,.003,.01,.02,-.01]))
    np.testing.assert_allclose(ref.sample(23,other).pose,other,atol=ATOL,rtol=0)
    ref.sample(55,other); final=ref.sample(76,other)
    np.testing.assert_allclose(final.pose[:3,3],[.15,.08,.35],atol=ATOL,rtol=0)
    np.testing.assert_array_equal(final.body_twist,np.zeros(6))
    np.testing.assert_array_equal(ref.sample(95,estimate.O).pose,final.pose)
    with pytest.raises(ControlDomainError): QuinticReference(protocol).sample(17,estimate.O)


def test_sliding_reference_independent_fixed_schedule(protocol,estimate):
    ref=SlidingReference(protocol); start=ref.sample(0,estimate.O)
    other=estimate.O@expm(hat([.001,0,0,0,0,0]))
    np.testing.assert_array_equal(ref.sample(3,other).pose,start.pose)
    np.testing.assert_array_equal(ref.sample(5,other).pose,other)
    end=ref.sample(25,other)
    np.testing.assert_allclose(end.pose[:3,3],other[:3,3]+[0,0,-.2],atol=ATOL,rtol=0)
    np.testing.assert_array_equal(ref.sample(30,estimate.O).pose,end.pose)


def test_command_limit_rejects_instead_of_saturation(protocol,estimate):
    ctrl=PoseForceController.from_protocol(protocol,'exp3')
    desired=ReferenceSample(estimate.O.copy(),np.array([1.,0,0,0,0,0]),None)
    with pytest.raises(ControlDomainError):
        ctrl.evaluate(estimate,np.zeros((2,6)),desired,('pivot','pivot'),13,diagnostic_GT=True)
