"""P2 unchanged Eq19/20/21/25 controller and frozen own-estimate references.

Predeclared component inputs/oracles: tests/test_p2_control_qualification.py.
No plant reference, sensor, estimator or runtime scheduler is stored here.
Contact modelling consumes only the estimated state and OLD published held
H-selected input. Publication ZOH and delayed actuation belong to the runner.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

import numpy as np
from scipy.spatial.transform import Rotation

from . import mechanics as mech
from .contact_geometry import adjoint, inverse, se3_exp, se3_log, selection, validate_transform
from .observations import FilterState


class ControlDomainError(ValueError):
    pass


def _pose(value):
    try: return validate_transform(np.asarray(value,dtype=float)).copy()
    except ValueError as exc: raise ControlDomainError('INVALID_REFERENCE_SE3') from exc


def _six(value):
    out=np.asarray(value,dtype=float)
    if out.shape!=(6,) or not np.isfinite(out).all(): raise ControlDomainError('INVALID_REFERENCE_TWIST')
    return out.copy()


def quintic(s):
    return 10*s**3-15*s**4+6*s**5,30*s**2-60*s**3+30*s**4


def _goal(spec):
    T=np.eye(4); T[:3,3]=spec['position_m']
    if spec['rotation']=='Rz(pi/2)': T[:3,:3]=Rotation.from_rotvec([0,0,np.pi/2]).as_matrix()
    elif spec['rotation']!='I3': raise ControlDomainError('UNREGISTERED_REFERENCE_ROTATION')
    return T


@dataclass(frozen=True)
class ReferenceSample:
    pose: np.ndarray
    body_twist: np.ndarray
    segment: int | None

    def __post_init__(self):
        object.__setattr__(self,'pose',_pose(self.pose))
        object.__setattr__(self,'body_twist',_six(self.body_twist))


class QuinticReference:
    """13/23/55s segment starts from this run's own estimate; final hold at76."""
    def __init__(self,protocol):
        self.reference=deepcopy(protocol['reference']); self._segment=None
        self._start=None; self._xi=None; self._last_time=-np.inf

    def sample(self,time_s,O_hat):
        if not np.isfinite(time_s) or time_s<0 or time_s<self._last_time:
            raise ControlDomainError('REFERENCE_TIME_WENT_BACKWARDS')
        self._last_time=float(time_s); O_hat=_pose(O_hat); specs=self.reference['waypoints']
        if time_s<specs[0]['start_s']: return ReferenceSample(O_hat,np.zeros(6),None)
        if time_s>=specs[-1]['end_s']: return ReferenceSample(_goal(specs[-1]),np.zeros(6),len(specs))
        index=next(i for i,s in enumerate(specs) if s['start_s']<=time_s<s['end_s'])
        spec=specs[index]
        if index!=self._segment:
            if abs(time_s-spec['start_s'])>1e-12: raise ControlDomainError('REFERENCE_SEGMENT_START_MISSING')
            self._segment=index; self._start=O_hat.copy(); self._xi=se3_log(inverse(self._start)@_goal(spec))
        alpha=(time_s-spec['start_s'])/(spec['end_s']-spec['start_s'])
        value,rate=quintic(alpha)
        return ReferenceSample(self._start@se3_exp(value*self._xi),
                               self._xi*rate/(spec['end_s']-spec['start_s']),index)


class SlidingReference:
    """Hold own t0 pose; at5s start declared world-z drop, then hold at25s."""
    def __init__(self,protocol):
        self.spec=deepcopy(protocol['suite']['conditional_sliding']); self._initial=None
        self._start=None; self._goal=None; self._xi=None; self._last_time=-np.inf

    def sample(self,time_s,O_hat):
        if not np.isfinite(time_s) or time_s<0 or time_s<self._last_time:
            raise ControlDomainError('REFERENCE_TIME_WENT_BACKWARDS')
        self._last_time=float(time_s); O_hat=_pose(O_hat)
        if self._initial is None:
            if abs(time_s)>1e-12: raise ControlDomainError('SLIDING_T0_REFERENCE_MISSING')
            self._initial=O_hat.copy()
        on=self.spec['sliding_on_s']; off=self.spec['sliding_off_s']
        if time_s<on: return ReferenceSample(self._initial,np.zeros(6),None)
        if self._start is None:
            if abs(time_s-on)>1e-12: raise ControlDomainError('SLIDING_SEGMENT_START_MISSING')
            self._start=O_hat.copy(); self._goal=O_hat.copy()
            self._goal[:3,3]+=[0,0,-self.spec['desired_world_drop_m']]
            self._xi=se3_log(inverse(self._start)@self._goal)
        if time_s>=off: return ReferenceSample(self._goal,np.zeros(6),1)
        alpha=(time_s-on)/(off-on); value,rate=quintic(alpha)
        return ReferenceSample(self._start@se3_exp(value*self._xi),self._xi*rate/(off-on),0)


@dataclass(frozen=True)
class ControlResult:
    time_s: float
    U_F: np.ndarray
    U_P: np.ndarray
    U_cmd: np.ndarray
    U_selected: np.ndarray
    U_published: np.ndarray
    h_internal: np.ndarray
    h_model_K: np.ndarray
    h_model_B: np.ndarray
    error: np.ndarray
    feedforward_current_body: np.ndarray
    force_active: bool
    pose_active: bool
    diagnostic_GT: bool

    def __post_init__(self):
        for name in ('U_F','U_P','U_cmd','U_selected','U_published','h_internal','h_model_K','h_model_B','error','feedforward_current_body'):
            object.__setattr__(self,name,np.array(getattr(self,name),dtype=float,copy=True))

    def as_dict(self):
        return {name:(getattr(self,name).tolist() if isinstance(getattr(self,name),np.ndarray) else getattr(self,name))
                for name in self.__dataclass_fields__}


class PoseForceController:
    @classmethod
    def from_protocol(cls,protocol,condition,*,object_id='A',variant='transport',contact_provider=None):
        return cls(protocol,condition,object_id=object_id,variant=variant,contact_provider=contact_provider)

    def __init__(self,protocol,condition,*,object_id='A',variant='transport',contact_provider=None):
        if condition not in ('exp1','exp2','exp3','exp4'): raise ControlDomainError('UNKNOWN_EXPERIMENT_CONDITION')
        if variant=='sliding' and condition!='exp3': raise ControlDomainError('UNREGISTERED_SLIDING_CONDITION')
        self.protocol=deepcopy(protocol); self.condition=condition; self.variant=variant
        if variant=='sliding': object_id='C'
        self.physics=mech.physics_from_protocol(protocol,object_id,condition,observer=True)
        self.contact_provider=contact_provider or mech.mechanics
        self.KF=np.array([protocol['original_parameters']['KF1'],protocol['original_parameters']['KF2']],dtype=float)
        self.KP=np.array(protocol['original_parameters']['KP'],dtype=float)
        if condition=='exp1': self.KF[:]=0
        if condition=='exp2': self.KP[:]=0

    def evaluate(self,estimated,U_published,reference,modes,time_s,*,diagnostic_GT=False):
        if not isinstance(estimated,FilterState): raise ControlDomainError('CONTROLLER_REQUIRES_INDEPENDENT_ESTIMATE')
        if estimated.origin=='diagnostic_GT' and not diagnostic_GT:
            raise ControlDomainError('GT_CONTROLLER_REQUIRES_EXPLICIT_DIAGNOSTIC')
        if not isinstance(reference,ReferenceSample): raise ControlDomainError('CONTROLLER_REQUIRES_REFERENCE_SAMPLE')
        held=np.asarray(U_published,dtype=float)
        if held.shape!=(2,6) or not np.isfinite(held).all(): raise ControlDomainError('INVALID_PUBLISHED_HELD_INPUT')
        if not np.isfinite(time_s) or time_s<0: raise ControlDomainError('INVALID_CONTROL_TIME')
        held=held.copy()
        # Causal Eq10 model input: do not recompute hB with this step's new U.
        contact=self.contact_provider(estimated,(held[0],held[1]),modes,self.physics)
        H=np.asarray(contact.H); W=np.asarray(contact.W); h=(np.asarray(contact.hK)+np.asarray(contact.hB)).ravel()
        transmitted=H@h
        hI=(H.T@(np.eye(H.shape[0])-np.linalg.pinv(W,rcond=self.protocol['numerical_qualification']['svd_rcond'])@W)@transmitted).reshape(2,6)
        current_to_desired=inverse(estimated.O)@reference.pose
        error=se3_log(current_to_desired)
        ff=adjoint(current_to_desired)@reference.body_twist
        if self.variant=='sliding':
            events=self.protocol['suite']['conditional_sliding']; settings=events['controller']
            force_on=settings['force_feedback_on_s']; pose_on=settings['pose_feedback_on_s']; end=events['duration_s']
        else:
            settings=self.protocol['reference']; force_on=settings['force_feedback_on_s']; pose_on=settings['pose_feedback_on_s']; end=settings['end_s']
        force_active=bool(force_on<=time_s<end); pose_active=bool(pose_on<=time_s<=end)
        UF=-self.KF*hI if force_active else np.zeros((2,6)); UP=np.zeros((2,6))
        if pose_active:
            common_E=(estimated.E1,inverse(estimated.C)@estimated.E2)
            UP=np.array([adjoint(inverse(inverse(estimated.O)@E))@(ff+self.KP*error) for E in common_E])
        command=UF+UP
        if self.variant!='sliding':
            lift=self.protocol['reference']['manual_lift']
            if lift['start_s']<=time_s<=lift['end_s']:
                alpha=(time_s-lift['start_s'])/(lift['end_s']-lift['start_s']); _,rate=quintic(alpha)
                world_v=np.array(lift['EE_world_translation_m'])*rate/(lift['end_s']-lift['start_s'])
                common_E=(estimated.E1,inverse(estimated.C)@estimated.E2)
                command=np.array([np.r_[E[:3,:3].T@world_v,np.zeros(3)] for E in common_E])
        selected=np.array([selection(mode).T@selection(mode)@command[r] for r,mode in enumerate(modes)])
        if not np.isfinite(command).all() or np.any(np.abs(command[:,:3])>.15) or np.any(np.abs(command[:,3:])>.5):
            raise ControlDomainError('COMMAND_DOMAIN_INVALID_NO_SATURATION')
        return ControlResult(float(time_s),UF,UP,command,selected,held,hI,contact.hK,contact.hB,
                             error,ff,force_active,pose_active,bool(diagnostic_GT))
