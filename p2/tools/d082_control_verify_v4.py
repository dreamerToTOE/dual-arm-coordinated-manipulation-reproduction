#!/usr/bin/env python3
"""D082 P2 control law verification V4: final-delivery corrections.

Corrections over V3 (per final-delivery review):
C1. Zero-pose-error fixed point revalidated with pose feedback ACTUALLY
    enabled (t = 20 s >= pose_feedback_on_s = 13 s), so the Eq.25 branch is
    genuinely exercised, not short-circuited by the inactive flag.
C2. Informational diagnostics (real-fixture near-zero h_I, unconditional by
    construction) are labelled "diagnostic" and EXCLUDED from the formal
    PASS count.
C3. Units separated: internal force (N) vs moment (N·m); linear (m/s) vs
    angular (rad/s) components of every wrench/twist residual.
C4. Internal-wrench oracle description corrected to match implementation:
    the oracle re-derives h_I OUTSIDE the controller using the SAME contact
    evaluation (same H, W at zero input) and the SAME projected null-space
    definition as control.py. It verifies the controller arithmetic, sign
    convention and gain plumbing — it is NOT an independent contact model.
C5. Timing check aligned with the frozen protocol (force_on=7 s,
    pose_on=13 s); all three stages asserted.
"""
import json, sys
from pathlib import Path
from types import SimpleNamespace
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from baselines.p2_pose_force import contact_geometry as geo
from baselines.p2_pose_force import mechanics as mech
from baselines.p2_pose_force import control as ctrl
from baselines.p2_pose_force.observations import FilterState

cfg = json.loads((ROOT / "configs" / "p2_closed_loop_protocol_v3.json").read_text())
FORCE_ON_S = cfg["reference"]["force_feedback_on_s"]   # 7
POSE_ON_S = cfg["reference"]["pose_feedback_on_s"]     # 13
physics = mech.physics_from_protocol(cfg, "A")
base = mech.initial_state(cfg, "transport")
modes = ("pivot", "pivot")
U0 = (np.zeros(6), np.zeros(6))
fs = FilterState(base.O, base.V, base.E1, base.E2, base.C, base.G1, base.G2,
                 origin='provided_estimate')
controller = ctrl.PoseForceController.from_protocol(cfg, "exp3", contact_provider=mech.mechanics)
KF = controller.KF
KP = controller.KP

checks = []
def check(cid, desc, ok, residual=None, unit="", *, diagnostic=False):
    checks.append({"id": cid, "desc": desc, "pass": bool(ok),
                   "residual": residual, "unit": unit, "diagnostic": bool(diagnostic)})

def res_str(residual, unit):
    if isinstance(residual, dict):
        return "  " + ", ".join(f"{k}={v:.3e} {u}" for k, (v, u) in residual.items())
    if isinstance(residual, (int, float)) and residual is not None:
        return f"  residual={residual:.3e} {unit}"
    if residual:
        return f"  {residual}"
    return ""

def report(cid, desc, ok, residual=None, unit="", *, diagnostic=False):
    tag = "DIAG" if diagnostic else ("PASS" if ok else "FAIL")
    print(f"{tag} {cid}: {desc}{res_str(residual, unit)}")
    check(cid, desc, ok, residual, unit, diagnostic=diagnostic)

def split_wrench(w):
    """(force_norm N, moment_norm N·m) of a 6-vector or (2,6) wrench stack."""
    w = np.asarray(w, float)
    f = float(np.linalg.norm(w[..., :3]))
    m = float(np.linalg.norm(w[..., 3:]))
    return f, m

def split_twist(u):
    """(linear_norm m/s, angular_norm rad/s) of a 6-vector or (2,6) stack."""
    u = np.asarray(u, float)
    return float(np.linalg.norm(u[..., :3])), float(np.linalg.norm(u[..., 3:]))

def wr(d):  # residual dict for wrench quantities
    return {"force": (d[0], "N"), "moment": (d[1], "N·m")}

def tw(d):  # residual dict for twist quantities
    return {"linear": (d[0], "m/s"), "angular": (d[1], "rad/s")}

def make_ref(pose_offset=None, twist=None):
    pose = base.O @ geo.se3_exp(pose_offset) if pose_offset is not None else base.O.copy()
    return ctrl.ReferenceSample(pose, twist if twist is not None else np.zeros(6), None)

# === null-space injection wrench (deterministic, via mock contact_provider) ===
contact0 = mech.mechanics(fs, U0, modes, physics)
H_mat = np.asarray(contact0.H)
W_mat = np.asarray(contact0.W)
hB0 = np.asarray(contact0.hB, float)
assert np.allclose(hB0, 0.0, atol=1e-12), "hB must vanish at zero input for the C4 oracle identity"
U_svd, s_vals, Vt_svd = np.linalg.svd(W_mat)
rank_W = int(np.sum(s_vals > s_vals[0] * 1e-10))
N_null = Vt_svd[rank_W:].T
INJ_SCALE = 0.5  # 0.5 N internal force amplitude
v_inject = N_null[:, 0] / max(np.linalg.norm(N_null[:, 0]), 1e-300) * INJ_SCALE
h_inject_12 = H_mat.T @ v_inject  # map back to full 12-dim
hK_inject = h_inject_12.reshape(2, 6)
hK_inj_f, hK_inj_m = split_wrench(hK_inject)

def injected_provider(state, U, modes_, phys):
    c = mech.mechanics(state, U, modes_, phys)
    hK_new = np.asarray(c.hK, float).copy() + hK_inject
    h_new = (hK_new + np.asarray(c.hB, float)).ravel()
    return SimpleNamespace(D=c.D, tau=c.tau, hK=hK_new, hB=c.hB, h=h_new,
                           W=c.W, internal=c.internal, singular_values=c.singular_values, H=c.H)

controller_inj = ctrl.PoseForceController.from_protocol(cfg, "exp3", contact_provider=injected_provider)
controller_real = ctrl.PoseForceController.from_protocol(cfg, "exp3", contact_provider=mech.mechanics)

ref0 = make_ref()
pose_off = np.r_[0.005, -0.003, 0.002, 0.01, -0.008, 0.005]
ref_off = make_ref(pose_offset=pose_off)

# ===== C1/V4_01: zero-error fixed point WITH pose feedback enabled (t >= 13 s) =====
cr0_late = controller_real.evaluate(fs, U0, ref0, modes, 20.0)
assert cr0_late.pose_active and cr0_late.force_active
up_f, up_m = split_twist(cr0_late.U_P)
report("V4_01_zero_err_pose_on",
       f"zero pose error, pose feedback ON (t=20s>={POSE_ON_S}s) -> U_P=0 via Eq.25 path",
       bool(cr0_late.pose_active) and np.allclose(cr0_late.U_P, 0, atol=1e-14),
       tw((up_f, up_m)))

# ===== V4_02: injected internal wrench is non-zero (force / moment separated) =====
cr_inj = controller_inj.evaluate(fs, U0, ref0, modes, 20.0)
hI_f, hI_m = split_wrench(cr_inj.h_internal)
report("V4_02_hI_nonzero", "injected internal wrench -> ||h_I|| > 0.01 (N / N·m separated)",
       (hI_f + hI_m) > 0.01, wr((hI_f, hI_m)))

# ===== V4_03: U_F non-zero (linear / angular separated) =====
UF_f, UF_m = split_twist(cr_inj.U_F)
report("V4_03_UF_nonzero", "||U_F|| > 1e-4 (linear m/s / angular rad/s separated)",
       (UF_f + UF_m) > 1e-4, tw((UF_f, UF_m)))

# ===== C4/V4_04: U_F = -KF * h_I, oracle re-derived OUTSIDE the controller =====
# Oracle (C4-corrected description): uses the SAME contact evaluation (same H, W,
# hK, hB at zero input) and the SAME projected null-space definition as
# control.py (H^T (I - pinv(W) W) H h). It verifies controller arithmetic,
# sign convention and KF plumbing — it is NOT an independent contact model.
h_full = (np.asarray(contact0.hK, float).ravel() + h_inject_12.ravel() + hB0.ravel())
transmitted_inj = H_mat @ h_full
hI_oracle = (H_mat.T @ (np.eye(H_mat.shape[0]) -
             np.linalg.pinv(W_mat, rcond=cfg["numerical_qualification"]["svd_rcond"]) @ W_mat)
             @ transmitted_inj).reshape(2, 6)
expected_UF = -KF * hI_oracle
dUF = np.abs(cr_inj.U_F - expected_UF)
lin_res = float(np.max(dUF[:, :3]))   # m/s
ang_res = float(np.max(dUF[:, 3:]))   # rad/s
report("V4_04_UF_formula",
       "U_F = -KF*h_I; oracle = same-contact re-derivation outside controller (C4 desc)",
       lin_res < 1e-14 and ang_res < 1e-14, tw((lin_res, ang_res)))

# ===== V4_05: proportional response (2x injection -> 2x U_F) =====
hK_inject_2x = hK_inject * 2.0
def injected_provider_2x(state, U, modes_, phys):
    c = mech.mechanics(state, U, modes_, phys)
    hK_new = np.asarray(c.hK, float).copy() + hK_inject_2x
    return SimpleNamespace(D=c.D, tau=c.tau, hK=hK_new, hB=c.hB,
                           h=(hK_new + np.asarray(c.hB, float)).ravel(),
                           W=c.W, internal=c.internal, singular_values=c.singular_values, H=c.H)
controller_2x = ctrl.PoseForceController.from_protocol(cfg, "exp3", contact_provider=injected_provider_2x)
cr_2x = controller_2x.evaluate(fs, U0, ref0, modes, 20.0)
scale_ratio = float(np.linalg.norm(cr_2x.U_F) / max(np.linalg.norm(cr_inj.U_F), 1e-300))
report("V4_05_scaling", "2x injection -> 2x U_F (proportional response)",
       abs(scale_ratio - 2.0) < 1e-6, scale_ratio, "ratio")

# ===== V4_06: hybrid mode: non-zero U_F AND non-zero U_P =====
cr_hybrid = controller_inj.evaluate(fs, U0, ref_off, modes, 20.0)
hyUF = split_twist(cr_hybrid.U_F); hyUP = split_twist(cr_hybrid.U_P)
hyb_ok = (hyUF[0] + hyUF[1]) > 0.001 and (hyUP[0] + hyUP[1]) > 0.001
report("V4_06_hybrid_nonzero",
       "hybrid: both U_F and U_P non-zero",
       hyb_ok,
       {"U_F_lin": (hyUF[0], "m/s"), "U_F_ang": (hyUF[1], "rad/s"),
        "U_P_lin": (hyUP[0], "m/s"), "U_P_ang": (hyUP[1], "rad/s")})

# ===== V4_07: hybrid: U_cmd = U_F + U_P =====
dCmd = np.abs(cr_hybrid.U_cmd - cr_hybrid.U_F - cr_hybrid.U_P)
report("V4_07_hybrid_sum", "U_cmd = U_F + U_P",
       float(np.max(dCmd)) < 1e-14, tw(split_twist(dCmd)))

# ===== V4_08: U_P matches independent Eq.25 re-derivation =====
common_E = (fs.E1, np.linalg.inv(fs.C) @ fs.E2)
error_indep = geo.se3_log(geo.inverse(fs.O) @ ref_off.pose)
ff_indep = geo.adjoint(geo.inverse(fs.O) @ ref_off.pose) @ ref_off.body_twist
UP_indep = np.array([geo.adjoint(geo.inverse(geo.inverse(fs.O) @ E)) @ (ff_indep + KP * error_indep)
                     for E in common_E])
dUP = np.abs(cr_hybrid.U_P - UP_indep)
report("V4_08_UP_oracle", "U_P matches independent Eq.25 re-derivation",
       float(np.max(dUP)) < 1e-14, tw((float(np.max(dUP[:, :3])), float(np.max(dUP[:, 3:])))))

# ===== V4_09: selection filtering (pivot) =====
sel_p = geo.selection("pivot")
U_sel_p = sel_p.T @ sel_p @ cr_hybrid.U_cmd[0]
dSelP = np.abs(cr_hybrid.U_selected[0] - U_sel_p)
report("V4_09_sel_pivot", "selection pivot filtering",
       float(np.max(dSelP)) < 1e-14, tw((float(np.max(dSelP[:3])), float(np.max(dSelP[3:])))))

# ===== V4_10: selection filtering (sliding) =====
cr_sl = controller_inj.evaluate(fs, U0, ref0, ("sliding", "sliding"), 20.0)
sel_s = geo.selection("sliding")
U_sel_s = sel_s.T @ sel_s @ cr_sl.U_cmd[0]
dSelS = np.abs(cr_sl.U_selected[0] - U_sel_s)
report("V4_10_sel_sliding", "selection sliding filtering",
       float(np.max(dSelS)) < 1e-14, tw((float(np.max(dSelS[:3])), float(np.max(dSelS[3:])))))

# ===== V4_11: command domain (linear and angular bounds checked separately) =====
lin_ok = bool(np.all(np.abs(cr_hybrid.U_cmd[:, :3]) < 0.15))
ang_ok = bool(np.all(np.abs(cr_hybrid.U_cmd[:, 3:]) < 0.5))
report("V4_11_cmd_domain", "|lin|<0.15 m/s AND |ang|<0.5 rad/s (separate gates)",
       lin_ok and ang_ok,
       {"max_lin": (float(np.max(np.abs(cr_hybrid.U_cmd[:, :3]))), "m/s"),
        "max_ang": (float(np.max(np.abs(cr_hybrid.U_cmd[:, 3:]))), "rad/s")})

# ===== C5/V4_12: activation timing aligned with frozen protocol (7 s / 13 s) =====
cr_t5 = controller_inj.evaluate(fs, U0, ref0, modes, 5.0)
cr_t10 = controller_inj.evaluate(fs, U0, ref0, modes, 10.0)
timing_ok = ((not cr_t5.force_active) and (not cr_t5.pose_active)
             and cr_t10.force_active and (not cr_t10.pose_active)
             and cr0_late.force_active and cr0_late.pose_active)
report("V4_12_timing",
       f"t=5s: both off; t=10s: force on (>={FORCE_ON_S}s), pose off; t=20s: both on (>={POSE_ON_S}s)",
       timing_ok)

# ===== V4_13: invalid inputs =====
for tn, fn in (("NaN_held", lambda: controller_inj.evaluate(fs, np.full((2, 6), np.nan), ref0, modes, 10.0)),
               ("bad_type", lambda: controller_inj.evaluate("bad", U0, ref0, modes, 10.0))):
    try:
        fn(); report(f"V4_13_{tn}", f"{tn} rejected", False)
    except (ctrl.ControlDomainError, ValueError):
        report(f"V4_13_{tn}", f"{tn} rejected", True)

# ===== C2/V4_D1: DIAGNOSTIC (excluded from formal PASS count) =====
# Real physical fixture at zero input produces near-zero internal wrench by
# construction (symmetric contact deformation). This is informational and
# unconditional; it must not inflate the formal PASS count (C2).
cr_real = controller_real.evaluate(fs, U0, ref0, modes, 20.0)
hI_real = split_wrench(cr_real.h_internal)
report("V4_D1_real_near_zero",
       "real fixture: h_I near zero at zero input (physical symmetry; info only, C2 excluded)",
       True, wr(hI_real), diagnostic=True)

# ===== summary: formal checks only (C2) =====
formal = [c for c in checks if not c["diagnostic"]]
diags = [c for c in checks if c["diagnostic"]]
passes = sum(1 for c in formal if c["pass"])
total = len(formal)
print(f"\nformal: {passes}/{total} PASS | diagnostics(excluded): {len(diags)}")
out = {"kind": "D082_CONTROL_VERIFICATION_V4",
       "corrections": {
           "C1": "zero-error fixed point revalidated with pose feedback active (t=20s >= 13s)",
           "C2": "informational diagnostics excluded from formal PASS count",
           "C3": "force(N)/moment(N·m) and linear(m/s)/angular(rad/s) units separated",
           "C4": "internal-wrench oracle description corrected: same-contact re-derivation, not independent model",
           "C5": "timing gates aligned with frozen protocol (force_on=7s, pose_on=13s)"},
       "checks": checks,
       "summary": {"pass": passes, "formal_total": total,
                   "diagnostics_excluded": len(diags),
                   "verdict": "PASS" if passes == total else "FAIL"}}
(ROOT / "p2" / "reviews" / "D082_CONTROL_VERIFICATION_V4.json").write_text(
    json.dumps(out, indent=2, ensure_ascii=False) + "\n")
sys.exit(0 if passes == total else 1)
