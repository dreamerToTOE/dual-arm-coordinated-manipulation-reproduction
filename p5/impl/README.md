# P5 implementation (clean room)

Numerical reproduction of Mirrazavi Salehian, Figueroa, Billard, *A Unified Framework for
Coordinated Multi-Arm Motion Planning*, IJRR 37(6):583–603, 2018,
DOI `10.1177/0278364918765952`.

Nothing here is translated from the official sources: every module is written from the paper's
equations plus the *behaviour* recorded in `p5/P5_OFFICIAL_CODE_AUDIT.md`. Five of the nine official
repositories are LGPL-3.0 and four carry no licence, so no official file is vendored.

## Running

```bash
cd p5/impl
PYTHONPATH=. /usr/bin/python3.10 run_all.py                 # everything, all gates
PYTHONPATH=. /usr/bin/python3.10 run_all.py --gate G1       # one gate
PYTHONPATH=. /usr/bin/python3.10 run_all.py --only T04      # one task
PYTHONPATH=. /usr/bin/python3.10 run_all.py --list          # registry
```

`/usr/bin/python3.10` is the interpreter that carries `numpy`/`scipy`/`matplotlib`; no package is
installed by this project (review decision Q6).

Outputs:

| Path | Content |
|---|---|
| `p5/evidence/P5_impl_checks.json` | full ledger: per-check detail, per-gate status, totals |
| `p5/evidence/P5_impl_checks.md` | paste-ready summary for plan §6 |
| `p5/evidence/impl_checks/<TID>.json` | per-task ledger, written as soon as the task ends |
| `p5/evidence/figures/impl/*.png` | task figures |

Exit code is 0 only when every check passed and no gate failed.

## External data

T06/T07 read the pre-trained models published with `nbfigueroa/SCA-Boundary-Learning`. That
repository has **no licence**, so the files are read in place and never copied:

```bash
export P5_OFFICIAL_REF=/home/ubuntu2004/lmy/p5-official-ref/SCA-Boundary-Learning
```

The default points at the read-only checkout on this machine. If it is missing the task fails loudly
(precondition in `require`) rather than skipping silently; the sha256 of each `.mat` is recorded in
the ledger instead of the file itself.

## Layout

```
p5core/results.py      Recorder: positive checks vs negative controls, JSON ledger
p5core/kinematics.py   planar arms, analytic Jacobians (relative joint angles)
p5core/tau.py          Eq.(8) + the divergent upstream variant (reference only)
p5core/lpv.py          LPV mixture, GMR scheduling, common Lyapunov P under trace(P)=1
p5core/qp_ik.py        Eq.(17)-(18): six-state classifier, exact active-set / SLSQP
p5core/lvi.py          Eq.(19)-(23): projector, dynamics, fixed point, passivity terms
p5core/svm_sca.py      Eq.(24)-(25): RBF-SVM, calibration, log barrier, metrics
p5core/multiarm_ds.py  Eq.(2),(9)-(11),(36) virtual-object DS
p5core/plotting.py     one Agg backend, one save() so figures look the same
tasks/tNN_*.py         one module per plan task, each exposing run(rec)
run_all.py             orchestration, gate logic, ledger
```

## Fidelity labels

`ORIGINAL` / `ADAPTATION` / `DEVIATION_REFERENCE` / `NOT_REPRODUCIBLE` / `ENGINEERING` — defined in
`p5core/__init__.py` and applied per task in `p5/reviews/P5_T0*_POST.md`. The rule that matters:
an `ADAPTATION` is always reported as such and never used to make an acceptance check pass.
