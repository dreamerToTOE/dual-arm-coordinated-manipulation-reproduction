#!/usr/bin/env python3
"""Build P3 equation-comparison and scope-matrix CSVs (UTF-8 BOM for Excel)."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "p3" / "reports" / "final"
OUT.mkdir(parents=True, exist_ok=True)

EQ_ROWS = [
    ("16", "w=[w1 w2 w3 w4 w5 w6]^T; [w1..w3] translation force, [w4..w6] moment (x,y,z)",
     "patterns.WRENCH_ORDER / COMPONENT_UNITS", "LITERAL", "T01"),
    ("17", "w_i = a_i sin(b_i t + c_i) + d_i, i=1..6",
     "GeneralPattern.wrench()", "LITERAL", "T01_01..05"),
    ("18", "w = diag(a) vsin(t b + c) + d",
     "GeneralPattern.wrench() with time-varying amplitude a(t)", "LITERAL (notation loose: Eq.22 makes a time-varying)", "T01_05"),
    ("19", "push: a=b=c=0; d=[0 0 f_push 0 0 0]^T (along +z)",
     "patterns.Push", "LITERAL", "T01_01"),
    ("20", "rub: a=[0 0 0 0 0 f_rub]^T, b=[0 0 0 0 0 v_rub]^T, c=d=0 (about z)",
     "patterns.Rub (f_rub in N*m)", "LITERAL", "T01_02"),
    ("21", "wiggle: a=[0 0 0 f f 0]^T, b=[0 0 0 v v 0]^T, c=[0 0 0 0 pi/2 0]^T, d=0",
     "patterns.Wiggle (my is cosine)", "LITERAL", "T01_03"),
    ("22", "spiral: a=[f_s(t) f_s(t) 0 0 0 0]^T, b=[v v 0 0 0 0]^T, c=[0 pi/2 0 0 0 0]^T, f_s=alpha sin(vt)+beta",
     "patterns.Spiral.amplitude()", "LITERAL", "T01_04"),
    ("23", "w_approach = w_push", "stages.COMPOSITION['approach']", "LITERAL", "T02_01"),
    ("24", "w_search = w_push + w_spiral", "stages.COMPOSITION['search']", "LITERAL", "T02_02"),
    ("25", "w_align = w_push + w_wiggle + w_rub", "stages.COMPOSITION['align']", "LITERAL", "T02_03"),
    ("26", "w_insert = w_push", "stages.COMPOSITION['insert']", "LITERAL", "T02_04"),
    ("27", "tau = J^T[[Omega,0],[0,I]]K_p dx + J^T[[R_h,0],[0,R_h]]w - D qdot + tau_g + tau_f",
     "control.torque_terms()", "LITERAL (+ A1 frame relabelling, ADAPTATION)", "T04_01..14, T06"),
    ("28", "Omega = R_h Sigma R_h^T, Sigma = diag([0 1 1])",
     "control.omega()", "LITERAL", "T03_01..12"),
    ("stage switching", "manual in the paper (p.8572); no criterion given",
     "stages.StageSchedule (externally prescribed)", "ADAPTATION", "T02_06"),
    ("task frame vs hole frame", "push along z (Eq.19) vs Sigma zeroes x (Sec.IV-D)",
     "explicit R_task_to_hole (e_z -> e_x); literal reading kept for audit", "ADAPTATION (frame naming; source ambiguity retained)", "T03_12, T03_15, T06_09"),
    ("numeric parameters", "none published (only 500 <= k_p <= 1000 for the hole arm)",
     "fixtures.TEST_FIXTURE", "TEST_FIXTURE", "T04_14"),
]

SCOPE_ROWS = [
    ("1", "Eq.16-18 general perturbation form", "reproduce", "implemented + validated", "21 checks (T01)", "ORIGINAL"),
    ("2", "Eq.19 push pattern", "reproduce", "implemented + validated", "T01_01/06/13", "ORIGINAL"),
    ("3", "Eq.20 rub pattern", "reproduce", "implemented + validated", "T01_02/07/13", "ORIGINAL"),
    ("4", "Eq.21 wiggle pattern", "reproduce", "implemented + validated", "T01_03/08/13", "ORIGINAL"),
    ("5", "Eq.22 spiral pattern", "reproduce", "implemented + validated", "T01_04/09/10", "ORIGINAL"),
    ("6", "Eq.23-26 stage compositions", "reproduce", "implemented + validated", "T02_01..05", "ORIGINAL"),
    ("7", "four documented stage sequences", "reproduce sequences", "all four traced", "T02_06, T06_01", "ORIGINAL"),
    ("8", "stage boundary timing", "manual switching", "externally prescribed schedule", "T02_06, T06_02", "ADAPTATION"),
    ("9", "Eq.28 Omega selection", "reproduce", "implemented + validated", "T03_01..08", "ORIGINAL"),
    ("10", "Eq.27 position/force blocks", "reproduce", "implemented + validated", "T03_07/08, T04_02..05", "ORIGINAL"),
    ("11", "Eq.27 wrench frame rotation", "reproduce", "implemented + validated", "T03_09/10, T04_M2", "ORIGINAL"),
    ("12", "Eq.27 damping/gravity/friction", "reproduce", "implemented + validated", "T04_09/10, T04_M4/M5", "ORIGINAL"),
    ("13", "no force feedback", "preserve absence", "verified structurally + behaviourally", "T04_12/13", "ORIGINAL"),
    ("14", "joint torques (complete law)", "reproduce", "implemented + validated", "T04_01..11, T06_04", "ORIGINAL"),
    ("15", "Eq.27 task->hole axis naming", "not stated (source ambiguity)", "explicit e_z->e_x relabelling; literal variant tested and rejected for push-axis alignment", "T03_12 (8.5e-17), T03_15 (1.0)", "ADAPTATION"),
    ("16", "numeric parameter values", "not published", "TEST_FIXTURE only", "fixtures.py", "TEST_FIXTURE"),
    ("17", "Eq.1-15 dexterous hand", "full", "not reproduced", "-", "OUT_OF_SCOPE_D082"),
    ("18", "50-DOF robot / KITECH hand", "full", "not reproduced", "-", "OUT_OF_SCOPE_D082"),
    ("19", "87% success / 13.86 s mean", "hardware statistics", "not reproduced", "-", "OUT_OF_SCOPE_D082"),
    ("20", "Fig.8/9/11 trajectories", "full", "not reproduced (no calibrated dynamics)", "-", "OUT_OF_SCOPE_D082"),
    ("21", "automatic stage recognition", "future work in the paper", "not implemented", "-", "OUT_OF_SCOPE_D082"),
    ("22", "quasi-static contact/jam surrogate", "optional", "not executed", "-", "NOT_EXECUTED_OPTIONAL"),
    ("23", "MuJoCo / Isaac deployment", "separate task (TASK15)", "not started", "-", "OUT_OF_SCOPE_D082"),
    ("24", "peg motion / insertion outcome", "not a numerical claim", "explicitly not claimed", "report §9", "OUT_OF_SCOPE_D082"),
]

for name, header, rows in (
    ("P3_EQUATION_COMPARISON.csv",
     ["equation", "original_paper", "implementation", "status", "evidence"], EQ_ROWS),
    ("P3_SCOPE_MATRIX.csv",
     ["id", "paper_item", "paper_requirement", "actual_reproduction", "evidence", "label"], SCOPE_ROWS),
):
    with open(OUT / name, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    print(f"wrote {OUT / name} ({len(rows)} rows)")
