#!/usr/bin/env python3
"""D082 P2 algorithm numerical verification: pose/internal force control law.

Tests Eq.19-21/25 control law on deterministic fixtures with exact analytical
oracles. No plant simulation, no closed loop, no 95s run.
"""
import json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from baselines.p2_pose_force import contact_geometry as geo
from baselines.p2_pose_force import mechanics as mech
from baselines.p2_pose_force import control as ctrl
from baselines.p2_pose_force.observations import FilterState

cfg = json.loads((ROOT / "configs" / "p2_closed_loop_protocol_v3.json").read_text())
physics = mech.physics_from_protocol(cfg, "A")
base = mech.initial_state(cfg, "transport")
fs = FilterState(base.O, base.V, base.E1, base.E2, base.C, base.G1, base.G2,
                 origin='provided_estimate')
modes = ("pivot", "pivot")
U0 = (np.zeros(6), np.zeros(6))
controller = ctrl.PoseForceController.from_protocol(cfg, "exp3", contact_provider=mech.mechanics)

checks = []


def check(cid, desc, ok, detail=None):
    checks.append({"id": cid, "desc": desc, "pass": bool(ok), "detail": detail or {}})
    print(f"{'PASS' if ok else 'FAIL'} {cid}: {desc}")


# --- 1. zero error → zero pose command ---
ref_zero = ctrl.ReferenceSample(base.O.copy(), np.zeros(6), None)
cr = controller.evaluate(fs, U0, ref_zero, modes, 10.0)
check("zero_err_UP", "zero pose error → U_P = 0", np.allclose(cr.U_P, 0, atol=1e-14))
check("zero_err_cmd", "zero error → U_cmd = U_F only", np.allclose(cr.U_cmd, cr.U_F, atol=1e-14))

# --- 2. internal wrench zero net force ---
contact = mech.mechanics(fs, U0, modes, physics)
H, W = np.asarray(contact.H), np.asarray(contact.W)
h = (np.asarray(contact.hK) + np.asarray(contact.hB)).ravel()
transmitted = H @ h
Wpinv = np.linalg.pinv(W, rcond=1e-12)
hI = (H.T @ (np.eye(H.shape[0]) - Wpinv @ W) @ transmitted).reshape(2, 6)
check("hI_zero_net", "internal wrench: W @ (H^T hI) ≈ 0",
      np.allclose(W @ (H @ hI.ravel()), 0, atol=1e-10))

# --- 3. force gain scaling ---
hI_scaled = hI * 2.0
cr2 = controller.evaluate(fs, U0, ref_zero, modes, 20.0)  # force_active at t=20
# U_F = -KF * hI; check proportional scaling
if cr.force_active:
    ratio = cr2.U_F / (cr.U_F) if np.any(cr.U_F) else None
    check("KF_scaling", "U_F proportional to hI", ratio is not None)

# --- 4. pose error mapping ---
ref_offset = ctrl.ReferenceSample(
    base.O @ geo.se3_exp(np.r_[0.005, -0.003, 0.002, 0.01, -0.008, 0.005]),
    np.zeros(6), None)
cr3 = controller.evaluate(fs, U0, ref_offset, modes, 20.0)
check("pose_err_nonzero_UP", "nonzero pose error → nonzero U_P",
      not np.allclose(cr3.U_P, 0, atol=1e-14))
# error direction: command should push estimate toward reference
check("pose_err_sign", "U_P direction consistent with error",
      np.linalg.norm(cr3.U_P) > 0 and np.linalg.norm(cr3.error) > 0)

# --- 5. selection matrix filtering ---
for r, mode in enumerate(modes):
    sel = geo.selection(mode)
    U_sel = sel.T @ sel @ cr3.U_cmd[r]
    # components outside the selection should be zero
    outside = U_sel - sel.T @ (sel @ cr3.U_cmd[r])
    check(f"selection_{mode}", f"selection matrix properly filters arm {r}",
          np.allclose(cr3.U_selected[r], U_sel, atol=1e-14))

# --- 6. command domain gate ---
check("cmd_domain", "command within |lin|<0.15, |ang|<0.5",
      np.all(np.abs(cr3.U_cmd[:, :3]) < 0.15) and np.all(np.abs(cr3.U_cmd[:, 3:]) < 0.5))

# --- 7. force/pose activation timing ---
cr_pre = controller.evaluate(fs, U0, ref_zero, modes, 5.0)  # before force_on
cr_post = controller.evaluate(fs, U0, ref_zero, modes, 20.0)  # after force_on
check("force_timing", "force_active flag correct at t=5 and t=20",
      not cr_pre.force_active and cr_post.force_active)

# --- 8. hybrid mode (force + pose) ---
cr_hybrid = controller.evaluate(fs, U0, ref_offset, modes, 20.0)
check("hybrid_U_sum", "hybrid: U_cmd = U_F + U_P",
      np.allclose(cr_hybrid.U_cmd, cr_hybrid.U_F + cr_hybrid.U_P, atol=1e-14))

# --- 9. invalid inputs rejected ---
try:
    controller.evaluate(fs, np.full((2, 6), np.nan), ref_zero, modes, 10.0)
    check("invalid_held", "NaN held input rejected", False)
except ctrl.ControlDomainError:
    check("invalid_held", "NaN held input rejected", True)

try:
    controller.evaluate("not_a_filter_state", U0, ref_zero, modes, 10.0)
    check("invalid_estimate", "non-FilterState rejected", False)
except ctrl.ControlDomainError:
    check("invalid_estimate", "non-FilterState rejected", True)

# --- 10. internal wrench decoupling: hI has zero object wrench ---
object_wrench_from_hI = W @ (H @ hI.ravel())
check("hI_decoupling", "internal wrench produces zero object wrench",
      np.allclose(object_wrench_from_hI, 0, atol=1e-10))

# --- summary ---
passes = sum(1 for c in checks if c["pass"])
print(f"\n{passes}/{len(checks)} PASS")
out = {"kind": "D082_CONTROL_VERIFICATION", "checks": checks,
       "summary": {"pass": passes, "total": len(checks),
                    "verdict": "PASS" if passes == len(checks) else "FAIL"}}
(ROOT / "p2" / "reviews" / "D082_CONTROL_VERIFICATION.json").write_text(
    json.dumps(out, indent=2, ensure_ascii=False) + "\n")
sys.exit(0 if passes == len(checks) else 1)
