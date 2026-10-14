"""P2 original Eq17 observations and observation-only initialization.

Qualification declarations precede this module in
tests/test_p2_observations_qualification.py. No dynamics integration, estimator,
controller, trajectory or runtime scheduler is started here. Only the sensor
producer reads plant state. Transport streams 1..6 and pre-calibration streams
100/101 are fixed engineering identifiers, with PCG64 SeedSequence([seed,id])
and the same exogenous sample_index across paired conditions.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

import numpy as np

from . import mechanics as mech
from .contact_geometry import inverse, se3_exp, se3_log, validate_transform

STATE_NAMES=('O','V','E1','E2','C','G1','G2')
KINDS=('EE1','EE2','hK1','hK2','visual1','visual2')
STREAM_IDS={('transport',kind):i+1 for i,kind in enumerate(KINDS)}
STREAM_IDS.update({('precalibration','visual1'):100,('precalibration','visual2'):101})


class ObservationDomainError(ValueError):
    pass


def _vector(value,size):
    a=np.asarray(value,dtype=float)
    if a.shape!=(size,) or not np.isfinite(a).all():
        raise ObservationDomainError('INVALID_FINITE_VECTOR')
    return a.copy()


def _pose(value):
    try: return validate_transform(np.asarray(value,dtype=float)).copy()
    except ValueError as exc: raise ObservationDomainError('INVALID_SE3') from exc


@dataclass
class FilterState:
    """Independent seven-block right-SE3 estimate, no shared plant arrays."""
    O: np.ndarray
    V: np.ndarray
    E1: np.ndarray
    E2: np.ndarray
    C: np.ndarray
    G1: np.ndarray
    G2: np.ndarray
    origin: str='provided_estimate'

    def __post_init__(self):
        for name in STATE_NAMES:
            setattr(self,name,_vector(getattr(self,name),6) if name=='V' else _pose(getattr(self,name)))

    @classmethod
    def from_mechanics(cls,state):
        """Explicit copied GT/math diagnostic; never primary initialization."""
        return cls(*(getattr(state,name) for name in STATE_NAMES),origin='diagnostic_GT')

    def copy(self):
        return type(self)(*(getattr(self,name) for name in STATE_NAMES),origin=self.origin)

    def retract(self,delta):
        delta=_vector(delta,42)
        return type(self)(*(getattr(self,name)+delta[6*i:6*i+6] if name=='V'
                            else getattr(self,name)@se3_exp(delta[6*i:6*i+6])
                            for i,name in enumerate(STATE_NAMES)),origin=self.origin)

    def local(self,reference):
        return np.concatenate([self.V-np.asarray(reference.V) if name=='V'
                               else se3_log(inverse(getattr(reference,name))@getattr(self,name))
                               for name in STATE_NAMES])

    def as_dict(self):
        return {name:getattr(self,name).tolist() for name in STATE_NAMES}


@dataclass(frozen=True)
class Observation:
    kind: str
    value: np.ndarray
    covariance: np.ndarray
    sample_id: str | int
    sample_stamp: float
    delivery_stamp: float

    def __post_init__(self):
        if self.kind not in KINDS: raise ObservationDomainError('UNKNOWN_OBSERVATION_KIND')
        value=_vector(self.value,6) if self.kind.startswith('hK') else _pose(self.value)
        covariance=np.asarray(self.covariance,dtype=float)
        if covariance.shape==(6,): covariance=np.diag(covariance)
        if (covariance.shape!=(6,6) or not np.isfinite(covariance).all()
                or not np.allclose(covariance,covariance.T,atol=1e-10,rtol=0)
                or np.linalg.eigvalsh(covariance)[0]<=0):
            raise ObservationDomainError('INVALID_OBSERVATION_COVARIANCE')
        if (not np.isfinite(self.sample_stamp) or not np.isfinite(self.delivery_stamp)
                or self.delivery_stamp<self.sample_stamp or self.sample_stamp<0):
            raise ObservationDomainError('INVALID_SAMPLE_DELIVERY_CLOCK')
        try: hash(self.sample_id)
        except TypeError as exc: raise ObservationDomainError('INVALID_SAMPLE_ID') from exc
        object.__setattr__(self,'value',value)
        object.__setattr__(self,'covariance',covariance.copy())
        object.__setattr__(self,'sample_stamp',float(self.sample_stamp))
        object.__setattr__(self,'delivery_stamp',float(self.delivery_stamp))

    def as_dict(self):
        return {'kind':self.kind,'value':self.value.tolist(),'covariance':self.covariance.tolist(),
                'sample_id':self.sample_id,'sample_stamp':self.sample_stamp,'delivery_stamp':self.delivery_stamp}


class NoiseBank:
    """Indexed cached Gaussian samples; request order cannot change exogenous noise."""
    def __init__(self,seed):
        if int(seed)!=seed or seed<0: raise ObservationDomainError('INVALID_RNG_SEED')
        self.seed=int(seed); self._generators={}; self._samples={}

    def standard_normal(self,phase,kind,sample_index):
        key=(phase,kind)
        if key not in STREAM_IDS or int(sample_index)!=sample_index or sample_index<0:
            raise ObservationDomainError('INVALID_EXOGENOUS_SAMPLE_INDEX')
        if key not in self._generators:
            self._generators[key]=np.random.Generator(np.random.PCG64(np.random.SeedSequence([self.seed,STREAM_IDS[key]])))
            self._samples[key]=[]
        samples=self._samples[key]
        while len(samples)<=sample_index: samples.append(self._generators[key].standard_normal(6))
        return samples[int(sample_index)].copy()


def declared_grasps(protocol,variant='transport'):
    """Declared geometry only, never read a true plant's evolved G."""
    specs=protocol['suite']['conditional_sliding']['grasps'] if variant=='sliding' else protocol['model']['A_grasps']
    out=[]
    for spec in specs:
        T=np.eye(4); T[:3,:3]=np.array(spec['R_columns_in_object'],dtype=float).T
        T[:3,3]=spec['translation_in_object_m']; out.append(_pose(T))
    return tuple(out)


class ObservationGenerator:
    def __init__(self,protocol,seed,*,variant='transport',tick_scale=1,contact_provider=None,delivery_delays_s=None):
        if tick_scale not in (1,2): raise ObservationDomainError('UNREGISTERED_CLOCK_SCALE')
        self.protocol=deepcopy(protocol); self.noise=NoiseBank(seed); self.variant=variant
        self.tick_scale=int(tick_scale); self.tick_s=protocol['clocks']['plant_tick_s']/self.tick_scale
        self.contact_provider=contact_provider or mech.mechanics
        self.physics=mech.physics_from_protocol(protocol,'C' if variant=='sliding' else 'A',observer=False)
        self.delays={kind:0. for kind in KINDS}
        if delivery_delays_s: self.delays.update(delivery_delays_s)
        if any(not np.isfinite(x) or x<0 for x in self.delays.values()):
            raise ObservationDomainError('INVALID_SENSOR_DELIVERY_DELAY')
        self._issued=set(); self._last_stamp={}

    def covariance(self,kind):
        key='hK' if kind.startswith('hK') else 'EE' if kind.startswith('EE') else 'visual_object'
        return np.diag(self.protocol['original_parameters']['R'][key])

    def sample(self,state,kind,sample_index,sample_stamp,*,phase='transport',delivery_stamp=None,contact=None,modes=('pivot','pivot')):
        if kind not in KINDS: raise ObservationDomainError('UNKNOWN_OBSERVATION_KIND')
        key=(phase,kind,int(sample_index))
        if key in self._issued: raise ObservationDomainError('REPEATED_SENSOR_SAMPLE_ID')
        if (phase,kind) not in STREAM_IDS or int(sample_index)!=sample_index or sample_index<0:
            raise ObservationDomainError('INVALID_SENSOR_SAMPLE_INDEX')
        if sample_stamp<self._last_stamp.get((phase,kind),-np.inf):
            raise ObservationDomainError('SENSOR_TIME_WENT_BACKWARDS')
        R=self.covariance(kind); perturb=np.sqrt(np.diag(R))*self.noise.standard_normal(phase,kind,sample_index)
        if kind.startswith('EE'):
            value=getattr(state,'E'+kind[-1])@se3_exp(perturb)
        elif kind.startswith('hK'):
            if contact is None: contact=self.contact_provider(state,(np.zeros(6),np.zeros(6)),modes,self.physics)
            elastic=np.asarray(contact.hK,dtype=float)
            if elastic.shape!=(2,6) or not np.isfinite(elastic).all(): raise ObservationDomainError('INVALID_ELASTIC_CONTACT_SAMPLE')
            value=elastic[int(kind[-1])-1]+perturb
        else:
            camera=int(kind[-1]); ideal=state.O if camera==1 else state.C@state.O
            bias=np.array(self.protocol['estimator']['visual_bias_body_cam'+str(camera)],dtype=float)
            value=ideal@se3_exp(bias)@se3_exp(perturb)
        delivered=sample_stamp+self.delays[kind] if delivery_stamp is None else delivery_stamp
        result=Observation(kind,value,R,f'{phase}:{kind}:{int(sample_index)}',sample_stamp,delivered)
        self._issued.add(key); self._last_stamp[(phase,kind)]=float(sample_stamp)
        return result

    def sample_packet(self,state,tick,contact=None,*,modes=('pivot','pivot')):
        if int(tick)!=tick or tick<0: raise ObservationDomainError('INVALID_INTEGER_SENSOR_TICK')
        tick=int(tick); clocks=self.protocol['clocks']; time_s=tick*self.tick_s
        periods={'EE1':clocks['EE_sensor_period_ticks'][0],'EE2':clocks['EE_sensor_period_ticks'][1],
                 'hK1':clocks['tactile_period_ticks'],'hK2':clocks['tactile_period_ticks'],
                 'visual1':clocks['visual_period_ticks'],'visual2':clocks['visual_period_ticks']}
        off=None if self.variant=='sliding' else self.protocol['reference']['robot2_visual_off_s']
        kinds=[kind for kind in KINDS if tick%(periods[kind]*self.tick_scale)==0
               and not (kind=='visual2' and off is not None and time_s>=off)]
        if contact is None and any(kind.startswith('hK') for kind in kinds):
            contact=self.contact_provider(state,(np.zeros(6),np.zeros(6)),modes,self.physics)
        return tuple(self.sample(state,kind,tick//(periods[kind]*self.tick_scale),time_s,
                                 contact=contact,modes=modes) for kind in kinds)

    def precalibration_pairs(self,stationary_fixture):
        if not np.array_equal(np.asarray(stationary_fixture.V),np.zeros(6)):
            raise ObservationDomainError('PRECALIBRATION_FIXTURE_NOT_STATIONARY')
        return tuple((self.sample(stationary_fixture,'visual1',i,(i+1)/15,phase='precalibration'),
                      self.sample(stationary_fixture,'visual2',i,(i+1)/15,phase='precalibration'))
                     for i in range(75))


@dataclass(frozen=True)
class CalibrationResult:
    C: np.ndarray
    pair_count: int
    iterations: int
    maximum_mean_component: float
    sample_ids: tuple

    def __post_init__(self): object.__setattr__(self,'C',_pose(self.C))


def calibrate_paired_visuals(pairs,protocol):
    pairs=tuple(pairs)
    if len(pairs)!=75: raise ObservationDomainError('PRECALIBRATION_REQUIRES_75_PAIRS')
    values=[]; identities=[]
    for i,(first,second) in enumerate(pairs):
        if first.kind!='visual1' or second.kind!='visual2': raise ObservationDomainError('INVALID_CALIBRATION_VIEW_PAIR')
        stamp=(i+1)/15
        if abs(first.sample_stamp-stamp)>1e-12 or abs(second.sample_stamp-stamp)>1e-12:
            raise ObservationDomainError('INVALID_CALIBRATION_SAMPLE_CLOCK')
        values.append(second.value@inverse(first.value)); identities.extend([first.sample_id,second.sample_id])
    if len(set(identities))!=150: raise ObservationDomainError('REPEATED_CALIBRATION_SAMPLE_ID')
    settings=protocol['estimator']['initial_calibration_mean']; mean=values[0].copy()
    for iteration in range(1,settings['iteration_max']+1):
        delta=np.mean([se3_log(inverse(mean)@value) for value in values],axis=0)
        largest=float(np.max(np.abs(delta)))
        if largest<=settings['tangent_component_tolerance']:
            return CalibrationResult(mean,75,iteration,largest,tuple(identities))
        mean=mean@se3_exp(delta)
    raise ObservationDomainError('PRECALIBRATION_RIGHT_MEAN_NOT_CONVERGED')


@dataclass(frozen=True)
class InitializationResult:
    state: FilterState
    consumed_observations: tuple


def initialize_from_fresh(packet,calibration,G1,G2,*,time_s=0.):
    """Only current observations, calibrated C and declared G; no GT argument."""
    if not isinstance(calibration,CalibrationResult) or calibration.pair_count!=75:
        raise ObservationDomainError('INITIALIZATION_REQUIRES_OBSERVED_CALIBRATION')
    packet=tuple(packet); observations={}
    for observation in packet:
        if observation.kind in observations: raise ObservationDomainError('DUPLICATE_INITIAL_OBSERVATION_KIND')
        if abs(observation.sample_stamp-time_s)>1e-12 or observation.delivery_stamp>time_s+1e-12:
            raise ObservationDomainError('INITIALIZATION_REQUIRES_FRESH_DELIVERED_PACKET')
        observations[observation.kind]=observation
    if not {'EE1','EE2','visual1'}.issubset(observations):
        raise ObservationDomainError('MISSING_INITIAL_POSE_OBSERVATION')
    state=FilterState(observations['visual1'].value,np.zeros(6),observations['EE1'].value,
                      observations['EE2'].value,calibration.C,G1,G2,origin='observations')
    return InitializationResult(state,packet)
