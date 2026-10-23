"""Documentation-consistency regression tests (D010 R4).

These are lightweight guards against the stale statements that D008/D010 had to
correct: wrong confidence-interval wording, wrong stage-2 attribution, treating
the empirical scaling slope as a physical dimension, and stale test counts.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P1 = ROOT
REP = ROOT / "reports"

DOCS = [
    P1 / "D008_AUDIT.md",
    P1 / "P1_NUMERICAL_STATUS.md",
    P1 / "OPEN_ISSUES.md",
    P1 / "CHINESE_REPORT_OUTLINE.md",
    REP / "G3_ACCEPTANCE.md",
    REP / "G3B_VARIANTS.md",
    REP / "N3_SINGULARITY_AUDIT.md",
]

BANNED = [
    "CI 含 0",
    "都低于完整两阶段",
    "L^{2.71}",
    "L^{2.712}",
    "31 项",
]


def test_no_stale_statements():
    for doc in DOCS:
        text = doc.read_text(encoding="utf-8")
        for phrase in BANNED:
            assert phrase not in text, f"{doc.name} still contains stale phrase: {phrase}"


def test_d2_reports_the_measured_ci():
    data = json.loads((REP / "G3_ACCEPTANCE.json").read_text(encoding="utf-8"))
    md = (REP / "G3_ACCEPTANCE.md").read_text(encoding="utf-8")
    d2 = data["D2"]
    mean = f"{d2['paired_goal_diff_mean']:.4f}"
    lo = f"{d2['paired_goal_diff_ci'][0]:.4f}"
    hi = f"{d2['paired_goal_diff_ci'][1]:.4f}"
    assert mean in md and lo in md and hi in md
    assert "排除 0" in md
    assert d2["paired_goal_diff_ci"][0] > 0.0


def test_stage2_attribution_matches_counts():
    data = json.loads((REP / "G3_ACCEPTANCE.json").read_text(encoding="utf-8"))
    md = (REP / "G3_ACCEPTANCE.md").read_text(encoding="utf-8")
    f2 = data["F2"]
    assert f2["stage1_only"]["success_count"] == 13
    assert f2["stage1_only_budget_matched"]["success_count"] == 12
    assert f2["full"]["success_count"] == 12
    assert "13/20" in md and "12/20" in md
    assert "没有带来成功数提升" in md


def test_n3_wording_is_empirical_not_dimensional():
    md = (REP / "N3_SINGULARITY_AUDIT.md").read_text(encoding="utf-8")
    assert "经验斜率" in md
    assert "不是物理量纲" in md
    assert "量纲是" not in md


def test_clipping_and_control_limits_distinguished():
    md = (REP / "G3B_VARIANTS.md").read_text(encoding="utf-8")
    assert "±0.3" in md and "±1.0" in md
    data = json.loads((REP / "G3B_VARIANTS.json").read_text(encoding="utf-8"))
    assert data["profiles"]["ours_two_stage"]["control_limit"] == 1.0
    assert data["profiles"]["ours_two_stage"]["stage1"]["max_abs"] == 0.3


def test_historical_measurement_is_labelled():
    md = (REP / "G3_ACCEPTANCE.md").read_text(encoding="utf-8")
    data = json.loads((REP / "G3_ACCEPTANCE.json").read_text(encoding="utf-8"))
    assert "D2_historical_cluster_local_lambda" in data
    assert "历史测量" in md
    assert "不可与上表直接比较" in md


def test_final_report_is_consistent():
    md = (ROOT / "reports" / "final" / "P1_FINAL_REPORT.md").read_text(encoding="utf-8")
    for phrase in ["CI 含 0", "都低于完整两阶段", "L^{2.71}", "31 项"]:
        assert phrase not in md
    assert "PARTIALLY_VERIFIED" in md
    assert "0.00859" in md and "0.02135" in md
    assert "排除 0" in md
    assert "13/20" in md and "12/20" in md
    assert "不是物理量纲" in md
