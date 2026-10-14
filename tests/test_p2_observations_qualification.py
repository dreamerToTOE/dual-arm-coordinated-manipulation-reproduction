"""Predeclared observation/initialization component qualification, no trials.

Written before observations.py. Frozen A state; PCG64 seed7. Transport streams
EE1/EE2/hK1/hK2/visual1/visual2=1..6, independent precalibration visual=100/101.
Paired conditions use each stream's same sample_index; precalibration indices
0..74 at (index+1)/15s, transport starts a separate stream at t0. R is exactly
original table I. Right Exp/Log checks use scipy matrix oracles, atol1e-10;
75-pair mean uses frozen 20 iterations and 1e-9 component tolerance. Qualification
may only run after Gate D passes, at a recorded science source/hash; no plant
integration, control experiment or parameter/seed search occurs here.
"""
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from scipy.linalg import expm, logm

from baselines.p2_pose_force import mechanics as mech
from baselines.p2_pose_force.observations import (
    FilterState, Observation, ObservationDomainError, ObservationGenerator,
    NoiseBank, STREAM_IDS, calibrate_paired_visuals, initialize_from_fresh,
    declared_grasps,
)

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture
def protocol(): return json.loads((ROOT/'configs/p2_closed_loop_protocol_v1.json').read_text())


def hat(x):
    x=np.asarray(x); v,w=x[:3],x[3:]; a=np.zeros((4,4))
    a[:3,:3]=[[0,-w[2],w[1]],[w[2],0,-w[0]],[-w[1],w[0],0]]; a[:3,3]=v
    return a


def logarithm(T):
    m=logm(T); assert np.max(np.abs(m.imag))<=1e-10; m=m.real
    return np.r_[m[:3,3],m[2,1],m[0,2],m[1,0]]


def test_state_copy_right_retraction_and_no_plant_alias(protocol):
    plant=mech.initial_state(protocol); state=FilterState.from_mechanics(plant)
    for name in mech.STATE_NAMES: assert not np.shares_memory(getattr(state,name),getattr(plant,name))
    d=np.tile([.0002,-.0001,.0003,.02,-.01,.03],7); d[6:12]=[.001,-.002,.003,.01,-.02,.03]
    new=state.retract(d)
    for i,name in enumerate(mech.STATE_NAMES):
        expected=getattr(state,name)+d[6*i:6*i+6] if name=='V' else getattr(state,name)@expm(hat(d[6*i:6*i+6]))
        np.testing.assert_allclose(getattr(new,name),expected,atol=1e-10,rtol=0)
        assert not np.shares_memory(getattr(new,name),getattr(state,name))
    np.testing.assert_allclose(new.local(state),d,atol=1e-10,rtol=0)
    copy=new.copy()
    for name in mech.STATE_NAMES: assert not np.shares_memory(getattr(copy,name),getattr(new,name))


def test_observation_copies_value_covariance_and_checks_delivery(protocol):
    state=mech.initial_state(protocol); R=np.diag(protocol['original_parameters']['R']['EE'])
    obs=Observation('EE1',state.E1,R,'transport:EE1:0',0.,.3)
    assert not np.shares_memory(obs.value,state.E1); assert not np.shares_memory(obs.covariance,R)
    with pytest.raises(ObservationDomainError): Observation('EE1',state.E1,R,0,.3,0.)
    with pytest.raises(ObservationDomainError): Observation('hK1',state.E1,R,0,0.,0.)


def test_stream_id_registration_and_order_independent_sample_noise():
    assert [STREAM_IDS[('transport',k)] for k in ('EE1','EE2','hK1','hK2','visual1','visual2')]==[1,2,3,4,5,6]
    assert [STREAM_IDS[('precalibration',k)] for k in ('visual1','visual2')]==[100,101]
    a=NoiseBank(7); b=NoiseBank(7)
    x=a.standard_normal('transport','EE1',8)
    b.standard_normal('transport','visual2',3)
    for i in range(9): y=b.standard_normal('transport','EE1',i)
    np.testing.assert_array_equal(x,y)
    np.testing.assert_array_equal(x,a.standard_normal('transport','EE1',8))
    assert not np.array_equal(a.standard_normal('precalibration','visual1',0),a.standard_normal('transport','visual1',0))


def test_original_sensor_formula_bias_and_elastic_only(protocol):
    state=mech.initial_state(protocol); state.V=np.array([.01,-.02,.03,.04,-.05,.06])
    g=ObservationGenerator(protocol,7)
    packet=g.sample_packet(state,0)
    obs={x.kind:x for x in packet}; R=protocol['original_parameters']['R']
    noise=NoiseBank(7)
    base={'EE1':state.E1,'EE2':state.E2,'visual1':state.O,'visual2':state.C@state.O}
    for kind in ('EE1','EE2','visual1','visual2'):
        covariance=np.array(R['EE' if kind.startswith('EE') else 'visual_object'])
        bias=np.array(protocol['estimator']['visual_bias_body_cam'+kind[-1]]) if kind.startswith('visual') else np.zeros(6)
        expected=base[kind]@expm(hat(bias))@expm(hat(np.sqrt(covariance)*noise.standard_normal('transport',kind,0)))
        np.testing.assert_allclose(obs[kind].value,expected,atol=1e-10,rtol=0)
        assert not np.shares_memory(obs[kind].value,base[kind])
    for side in (0,1):
        E=state.E1 if side==0 else np.linalg.inv(state.C)@state.E2
        G=state.G1 if side==0 else state.G2
        elastic=-np.array(protocol['original_parameters']['K_nominal'])*logarithm(np.linalg.inv(E)@state.O@G)
        kind='hK'+str(side+1)
        expected=elastic+np.sqrt(R['hK'])*noise.standard_normal('transport',kind,0)
        np.testing.assert_allclose(obs[kind].value,expected,atol=1e-10,rtol=0)
    with pytest.raises(ObservationDomainError): g.sample_packet(state,0)


def test_reuses_true_contact_hK_and_never_adds_hB(protocol):
    plant=mech.initial_state(protocol); calls=[]
    def provider(*args): calls.append(args); raise AssertionError('provided true contact should be reused')
    g=ObservationGenerator(protocol,7,contact_provider=provider)
    c=SimpleNamespace(hK=np.array([[1,2,3,.01,.02,.03],[4,5,6,.04,.05,.06]]),hB=np.full((2,6),999.))
    obs={x.kind:x for x in g.sample_packet(plant,0,contact=c)}
    bank=NoiseBank(7); R=protocol['original_parameters']['R']['hK']
    for i in (0,1):
        kind='hK'+str(i+1)
        np.testing.assert_allclose(obs[kind].value,c.hK[i]+np.sqrt(R)*bank.standard_normal('transport',kind,0),atol=1e-10,rtol=0)
    assert not calls


def test_fixed_sensor_clocks_half_step_and_76_visual_off(protocol):
    state=mech.initial_state(protocol)
    a=ObservationGenerator(protocol,7); b=ObservationGenerator(protocol,7,tick_scale=2)
    expected={0:{'EE1','EE2','hK1','hK2','visual1','visual2'},15:{'EE1'},30:{'EE1','hK1','hK2'},60:{'EE1','EE2','hK1','hK2'},200:{'visual1','visual2'}}
    for tick,kinds in expected.items():
        pa=a.sample_packet(state,tick); pb=b.sample_packet(state,2*tick)
        assert {o.kind for o in pa}==kinds
        for x,y in zip(pa,pb):
            assert x.sample_id==y.sample_id and x.sample_stamp==y.sample_stamp
            np.testing.assert_array_equal(x.value,y.value)
    assert 'visual2' not in {o.kind for o in a.sample_packet(state,76*3000)}
    assert 'visual2' in {o.kind for o in ObservationGenerator(protocol,7,variant='sliding').sample_packet(mech.initial_state(protocol,'sliding'),76*3000)}


def synthetic_calibration(protocol,state):
    R=np.diag(protocol['original_parameters']['R']['visual_object']); pairs=[]
    for i in range(75):
        t=(i+1)/15
        pairs.append((Observation('visual1',state.O,R,f'precalibration:visual1:{i}',t,t),
                      Observation('visual2',state.C@state.O,R,f'precalibration:visual2:{i}',t,t)))
    return calibrate_paired_visuals(pairs,protocol)


def test_75_pairs_calibration_direction_iteration_and_fresh_initialization(protocol):
    state=mech.initial_state(protocol); result=synthetic_calibration(protocol,state)
    np.testing.assert_allclose(result.C,state.C,atol=1e-10,rtol=0)
    assert result.pair_count==75 and 1<=result.iterations<=20
    assert result.maximum_mean_component<=1e-9
    g=ObservationGenerator(protocol,7); pairs=g.precalibration_pairs(state)
    assert len(pairs)==75 and pairs[0][0].sample_stamp==1/15 and pairs[-1][0].sample_stamp==5
    assert len({o.sample_id for pair in pairs for o in pair})==150
    packet=g.sample_packet(state,0); G1,G2=declared_grasps(protocol)
    init=initialize_from_fresh(packet,result,G1,G2)
    by_kind={o.kind:o for o in packet}
    np.testing.assert_array_equal(init.state.O,by_kind['visual1'].value)
    np.testing.assert_array_equal(init.state.E1,by_kind['EE1'].value)
    np.testing.assert_array_equal(init.state.E2,by_kind['EE2'].value)
    np.testing.assert_array_equal(init.state.V,np.zeros(6))
    assert init.state.origin=='observations'
    assert init.consumed_observations==tuple(packet)
    for name in mech.STATE_NAMES: assert not np.shares_memory(getattr(init.state,name),getattr(state,name))
    with pytest.raises(ObservationDomainError): initialize_from_fresh(packet,state.C,G1,G2)
    with pytest.raises(ObservationDomainError): initialize_from_fresh(packet+packet[:1],result,G1,G2)
