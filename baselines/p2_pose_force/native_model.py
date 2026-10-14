"""Qualified-only native numerical provider, preserving the canonical models."""
import ctypes
import hashlib
import json
from pathlib import Path
import subprocess
import numpy as np
from scipy.linalg import block_diag
from .mechanics import State, Contact
from .contact_geometry import selection

POSES=('O','E1','E2','C','G1','G2')
MODES={'tight':0,'pivot':1,'sliding':2}
ROOT=Path(__file__).resolve().parents[2]
FLAGS=['-std=c++17','-O3','-march=native','-DNDEBUG','-shared','-fPIC','-I/usr/include/eigen3']


class NativeNumericalError(RuntimeError):
    def __init__(self,reason,evidence=None):
        super().__init__(reason);self.evidence=evidence or {}


def source_sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build_native(directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    source=Path(__file__).with_name('native_kernel.cpp');binary=directory/'p2_native.so'
    expected={'source_sha256':source_sha(source),'flags':FLAGS,'compiler':subprocess.check_output(['g++','--version'],text=True).splitlines()[0],
              'eigen_version':'3.4.0','boost_version':'1.74.0','machine_flags_use_local_CPU':True}
    stamp=directory/'build.json'
    if not binary.exists() or not stamp.exists() or json.loads(stamp.read_text()).get('build_inputs')!=expected:
        command=['g++',*FLAGS,str(source),'-o',str(binary)]
        result=subprocess.run(command,capture_output=True,text=True)
        (directory/'compile_stdout.txt').write_text(result.stdout)
        (directory/'compile_stderr.txt').write_text(result.stderr)
        if result.returncode:raise NativeNumericalError('NATIVE_COMPILATION_FAILED',{'command':command,'returncode':result.returncode})
        stamp.write_text(json.dumps({'build_inputs':expected,'binary_sha256':source_sha(binary),'command':command},indent=2)+'\n')
    return binary


class NativeModel:
    def __init__(self,binary):
        self.binary=Path(binary);self.library=ctypes.CDLL(str(self.binary.resolve()))
        self.ptr=ctypes.POINTER(ctypes.c_double);self.iptr=ctypes.POINTER(ctypes.c_int)
        self.library.p2_last_error.restype=ctypes.c_char_p
        self.library.p2_field.argtypes=[self.ptr,self.ptr,self.iptr,self.ptr,self.ptr,self.ptr]
        self.library.p2_field_fd50.argtypes=[self.ptr,self.ptr,self.iptr,self.ptr,ctypes.c_double,self.ptr]
        self.library.p2_contact.argtypes=[self.ptr,self.ptr,self.iptr,self.ptr,self.ptr]
        self.library.p2_advance.argtypes=[self.ptr,self.ptr,self.iptr,self.ptr,ctypes.c_double,ctypes.c_int,self.ptr,self.ptr,self.ptr]
        self._H={}

    def pointer(self,x):return x.ctypes.data_as(self.ptr)

    def pack(self,state):return np.ascontiguousarray(np.concatenate([getattr(state,p).ravel() for p in POSES]+[state.V]),dtype=np.float64)

    def parameters(self,physics):return np.ascontiguousarray(np.concatenate([np.array([physics.mass]),physics.inertia_diag,*physics.K,physics.B,physics.Ba,physics.gravity]),dtype=np.float64)

    def arguments(self,state,U,modes,physics):
        return self.pack(state),np.ascontiguousarray(U,dtype=np.float64).ravel(),np.array([MODES[m] for m in modes],dtype=np.int32),self.parameters(physics)

    def check(self,status,evidence=None):
        if status:raise NativeNumericalError(self.library.p2_last_error().decode(),evidence)

    def state_rate(self,state,U,modes,physics):
        x,u,m,p=self.arguments(state,U,modes,physics);f=np.empty(42)
        self.check(self.library.p2_field(self.pointer(x),self.pointer(u),m.ctypes.data_as(self.iptr),self.pointer(p),self.pointer(f),None))
        return f

    def continuous_linearization(self,state,U,modes,physics):
        x,u,m,p=self.arguments(state,U,modes,physics);f=np.empty(42);A=np.empty((42,42))
        self.check(self.library.p2_field(self.pointer(x),self.pointer(u),m.ctypes.data_as(self.iptr),self.pointer(p),self.pointer(f),self.pointer(A)))
        return f,A

    def finite_difference_50digits(self,state,U,modes,physics,epsilon=1e-6):
        """Qualification only: high precision central numerical derivative, no AD."""
        x,u,m,p=self.arguments(state,U,modes,physics);A=np.empty((42,42))
        self.check(self.library.p2_field_fd50(self.pointer(x),self.pointer(u),m.ctypes.data_as(self.iptr),self.pointer(p),float(epsilon),self.pointer(A)))
        return A

    def contact(self,state,U,modes,physics,*,decompose=True):
        x,u,m,p=self.arguments(state,U,modes,physics);out=np.empty(176)
        self.check(self.library.p2_contact(self.pointer(x),self.pointer(u),m.ctypes.data_as(self.iptr),self.pointer(p),self.pointer(out)))
        key=tuple(modes)
        if key not in self._H:self._H[key]=block_diag(*(selection(a) for a in key))
        H=self._H[key];W=out[104:].reshape(6,12)[:,:H.shape[0]].copy()
        return Contact(out[:32].reshape(2,4,4).copy(),out[32:44].reshape(2,6).copy(),out[44:56].reshape(2,6).copy(),out[56:68].reshape(2,6).copy(),out[68:80].reshape(2,6).copy(),H.copy(),W,
                       out[80:86].copy(),out[86:98].reshape(2,6).copy() if decompose else None,out[98:104].copy() if decompose else None)

    def advance(self,state,U,modes,physics,dt,steps=1):
        x,u,m,p=self.arguments(state,U,modes,physics);diag=np.zeros(3);delta=np.zeros(42);residual=np.zeros(24)
        status=self.library.p2_advance(self.pointer(x),self.pointer(u),m.ctypes.data_as(self.iptr),self.pointer(p),float(dt),int(steps),self.pointer(diag),self.pointer(delta),self.pointer(residual))
        values=[x[16*j:16*(j+1)].reshape(4,4).copy() for j in range(6)]
        new=State(values[0],x[96:].copy(),values[1],values[2],values[3],values[4],values[5])
        evidence={'completed_steps':int(diag[0]),'max_newton_iterations':int(diag[1]),'max_accepted_residual_component':float(diag[2]),
                  'last_delta':delta.tolist(),'last_residual':residual.tolist(),'last_accepted_state':new.as_dict()}
        self.check(status,evidence)
        return new,evidence
