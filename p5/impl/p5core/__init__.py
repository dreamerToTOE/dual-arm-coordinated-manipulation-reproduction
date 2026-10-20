"""P5 clean-room numerical reproduction of

    Mirrazavi Salehian, Figueroa, Billard,
    "A Unified Framework for Coordinated Multi-Arm Motion Planning",
    IJRR 37(6):583-603, 2018, DOI 10.1177/0278364918765952

Every module here is written from the paper's equations and from the *behaviour*
of the official code, never by translating the official sources (see
p5/P5_OFFICIAL_CODE_AUDIT.md and manifest `license_policy`: five repositories are
LGPL-3.0 and four carry no licence at all).

Fidelity labels used across this package
----------------------------------------
ORIGINAL              the equation is implemented as printed
ADAPTATION            a component (solver, geometry, model, calibration) is replaced
DEVIATION_REFERENCE   a divergent official behaviour, reproduced only so that the
                      difference can be measured
ENGINEERING           implementation detail, carries no scientific claim
"""

__all__ = ["results", "kinematics", "tau", "lpv", "qp_ik", "lvi", "svm_sca",
           "calibration", "multiarm_ds"]

#: frozen calibration scale for Gamma_cal = 1 + Gamma_raw / KAPPA (see docs/DECISIONS.md D007)
KAPPA = 1.0
