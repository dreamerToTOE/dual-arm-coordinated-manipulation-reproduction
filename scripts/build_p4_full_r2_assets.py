"""Render R2 spatial component figures from saved JSON only; never solve or plan.

The R1 and R2 accepted/rejected denominators are kept separately.  Saved NR
traces are numerical iterations, not a physical controller's time response.
No project dynamics, kinematics, IK, NR, RSS or planner module is imported.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENTS = ("II", "III", "IV", "V", "VI")
R2_RUN = "20261015_R2_SPATIAL01"
R1_RUNS = {
    "II": "20261014T1528_R1_ABB01", "III": "20261014T1528_R1_ABB01",
    "IV": "20261014T1545_R1_COMAU02", "V": "20261014T1545_R1_COMAU02",
    "VI": "20261014T1550_R1_VI03",
}
DEFAULT_OUTPUT = ROOT / "reports/p4_full_r2_assets_20261015_v2"
GROUPS = ("R1_original_saved_target", "R2_original_saved_target", "R2_physical_continuous_target")
GROUP_LABELS = ("R1 原生 / 原保存目标", "R2 修复 / 原保存目标", "R2 修复 / 连续物理目标")
COLORS = ("#bd594d", "#4379b4", "#398a76")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SavedInputs:
    def __init__(self) -> None:
        self.sha256: dict[str, str] = {}

    def read(self, path: Path):
        self.sha256[str(path.relative_to(ROOT))] = digest(path)
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".jsonl":
            return [json.loads(line) for line in text.splitlines() if line.strip()]
        return json.loads(text)


def new_json(path: Path, value) -> None:
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def new_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No saved rows for {path.name}")
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def qualified(position, rotation, gates: dict) -> bool:
    return (position is not None and rotation is not None
            and position <= gates["projection_translation_maxabs_mm_or_planar_source_units"]
            and rotation <= gates["projection_rotation_matrix_maxabs"])


def prepare() -> tuple[dict, dict[str, str]]:
    saved = SavedInputs()
    protocol = saved.read(ROOT / "configs/p4_full/r2_geometry_consistent_qualification_v1.json")
    execution = saved.read(ROOT / "results/p4_full" / R2_RUN / "execution.json")
    source_manifest = saved.read(ROOT / "configs/p4_full/author_source_manifest.json")
    gates = protocol["gates"]
    ik, nr_trace, nr_summary, raw_endpoints, rank_rows, rank_specs = [], [], [], [], [], []
    environment_summary, checks = [], []
    iv_limits = []
    for env in ENVIRONMENTS:
        r1_dir = ROOT / "results/p4_full" / R1_RUNS[env]
        r2_dir = ROOT / "results/p4_full" / R2_RUN / env
        r1 = saved.read(r1_dir / (env + "_independent.json"))
        raw_path = r1_dir / (env + ("_native.json" if env in ("II", "III") else "_native.jsonl"))
        raw = saved.read(raw_path)
        raw_rows = raw["rows"] if isinstance(raw, dict) else raw
        observed = saved.read(r2_dir / "observations.json")
        summary = saved.read(r2_dir / "summary.json")
        check_rows = saved.read(r2_dir / "checks.json")
        environment_summary.append(summary)
        checks.extend({"environment": env, "check": row["check"], "passed": row["passed"]}
                      for row in check_rows)
        if env in ("II", "III"):
            native_targets = {(row["index"], row["robot"], row["branch"]): row
                              for row in raw_rows if row["kind"] == "ik"}
            native_ik = [row for row in r1["evidence"] if row["kind"] == "ik"]
        else:
            native_targets = {(row["sample"], row["arm"], row["branch"]): row
                              for row in raw_rows if row["type"] == "ik_roundtrip"}
            native_ik = [row for row in r1["details"] if row["type"] == "ik_roundtrip"]
        if len(native_ik) != 80 or len(native_targets) != 80:
            raise ValueError(f"{env}: original IK denominator must be 80")
        for row in native_ik:
            abb = env in ("II", "III")
            errors = row.get("target_errors" if abb else "independent_target_error") or {}
            position = errors.get("translation_max_abs_mm" if abb else "translation_abs_max_mm")
            rotation = errors.get("rotation_matrix_max_abs" if abb else "rotation_matrix_abs_max")
            accepted = row["native_success"] if abb else row["accepted"]
            index, arm = (row["index"], row["robot"]) if abb else (row["sample"], row["arm"])
            ik.append({"environment": env, "group": GROUPS[0], "index": index,
                       "arm": arm, "branch": row["branch"], "attempt": index * 8 + row["branch"],
                       "accepted": accepted, "position_maxabs_mm": position,
                       "rotation_matrix_maxabs": rotation,
                       "qualified": bool(accepted and qualified(position, rotation, gates)),
                       "source": str((r1_dir / (env + "_independent.json")).relative_to(ROOT))})
        old_replays = [row for row in observed if row["kind"] == "ik_replay"
                       and row["target_kind"] == "original_saved_target"]
        continuous_replays = [row for row in observed if row["kind"] == "ik_replay"
                              and row["target_kind"] == "physical_continuous_target"]
        if len(old_replays) != 80 or len(continuous_replays) != 80:
            raise ValueError(f"{env}: each R2 target denominator must remain 80")
        for row in old_replays + continuous_replays:
            index, arm, branch = row["index"], row["arm"], row["branch"]
            original = native_targets[(index, arm, branch)]
            original_q = original["q"] if env in ("II", "III") else original["source_q_rad"]
            if row["source_q"] != original_q:
                raise ValueError(f"{env}: report found changed R1 source q")
            if row["target_kind"] == "original_saved_target" and row["target"] != original["target"]:
                raise ValueError(f"{env}: original saved target was replaced")
            errors = row["errors"] or {}
            accepted = row["native"]["success"]
            position, rotation = errors.get("position_abs_max"), errors.get("rotation_matrix_abs_max")
            ik.append({"environment": env, "group": "R2_" + row["target_kind"],
                       "index": index, "arm": arm, "branch": branch, "attempt": index * 8 + branch,
                       "accepted": accepted, "position_maxabs_mm": position,
                       "rotation_matrix_maxabs": rotation,
                       "qualified": bool(accepted and qualified(position, rotation, gates)),
                       "source": str((r2_dir / "observations.json").relative_to(ROOT))})
        original_nr = [row for row in observed if row["kind"] == "nr_reference"
                       and row["fixture_kind"] == "original_input"]
        if len(original_nr) != 10:
            raise ValueError(f"{env}: original NR denominator must remain 10")
        for row in original_nr:
            result = row["result"]
            metrics = result["metrics"]
            nr_summary.append({"environment": env, "input": int(row["fixture"]),
                               "status": result["status"], "iterations_saved": len(result["trace"]),
                               "position_maxabs_mm": metrics["translation_max_abs"],
                               "rotation_matrix_maxabs": metrics["rotation_matrix_max_abs"],
                               "rotation_angle_max_rad": metrics["rotation_angle_max_rad"],
                               "wall_s": result["wall_s"], "collision_checked": result["collision_checked"]})
            for point in result["trace"]:
                nr_trace.append({"environment": env, "input": int(row["fixture"]),
                                 "status": result["status"], "iteration": point["iteration"],
                                 "position_maxabs_mm": point["translation_max_abs"],
                                 "rotation_matrix_maxabs": point["rotation_matrix_max_abs"],
                                 "rotation_angle_max_rad": point["rotation_angle_max_rad"]})
            if env == "IV" and result["status"] != "CONVERGED":
                for arm in (1, 2):
                    joint = 6 * (arm - 1) + 2
                    iv_limits.append({"environment": env, "input": int(row["fixture"]),
                                      "status": result["status"], "arm": arm,
                                      "input_q3_rad": result["input_q_rad"][joint],
                                      "candidate_q3_rad": result["candidate_q_rad"][joint],
                                      "source_q3_lower_rad": -90 * 3.1416 / 180,
                                      "source_q3_upper_rad": 75 * 3.1416 / 180})
        endpoint_rows = [row for row in observed if row["kind"] == "raw_endpoint_unchanged"]
        if len(endpoint_rows) != 2:
            raise ValueError(f"{env}: expected both unchanged source endpoints")
        for row in endpoint_rows:
            metrics = row["metrics"]
            if row["formal_endpoint_repaired"]:
                raise ValueError("Raw endpoint graph cannot contain a repaired endpoint")
            raw_endpoints.append({"environment": env, "endpoint": row["endpoint"],
                                  "position_maxabs_mm": metrics["translation_max_abs"],
                                  "rotation_matrix_maxabs": metrics["rotation_matrix_max_abs"],
                                  "rotation_angle_max_rad": metrics["rotation_angle_max_rad"],
                                  "formal_endpoint_repaired": False})
        fixtures = [row for row in observed if row["kind"] == "rank_fixture"]
        for row in fixtures:
            rank_specs.append({"environment": env, "arm": row["arm"], "fixture": row["name"],
                               "analytic_rank": row["ranks"][0], "native_fd_rank": row["ranks"][1],
                               "q_rad": row["q"]})
            for method_index, method in enumerate(("analytic", "native_fk_central_difference")):
                values = row["singular_values"][method_index]
                for index, sigma in enumerate(values):
                    rank_rows.append({"environment": env, "arm": row["arm"], "fixture": row["name"],
                                      "method": method, "rank": row["ranks"][method_index],
                                      "singular_value_index": index + 1,
                                      "sigma_after_translation_mm_to_m": sigma,
                                      "sigma_over_sigma1": sigma / values[0],
                                      "relative_rank_threshold": gates["rank_relative"]})
    group_summary = []
    for env in ENVIRONMENTS:
        for group in GROUPS:
            rows = [row for row in ik if row["environment"] == env and row["group"] == group]
            accepted = [row for row in rows if row["accepted"]]
            group_summary.append({"environment": env, "group": group, "attempts": len(rows),
                                  "accepted": len(accepted), "rejected": len(rows) - len(accepted),
                                  "qualified_accepted": sum(row["qualified"] for row in accepted),
                                  "accepted_but_unqualified": sum(not row["qualified"] for row in accepted),
                                  "position_maxabs_mm": max(row["position_maxabs_mm"] for row in accepted),
                                  "rotation_matrix_maxabs": max(row["rotation_matrix_maxabs"] for row in accepted)})
    data = {"schema": "P4_R2_SPATIAL_SAVED_LOG_REPORT_DATA_V1", "run_id": R2_RUN,
            "scope": "Saved spatial component evidence only; no controller time response or planning success rates",
            "formal_planning_calls": execution["formal_planning_calls"], "collision_checked": False,
            "source_commit": execution["source_commit"], "execution": execution,
            "gates": gates, "environment_summaries": environment_summary,
            "checks": checks, "ik_groups": group_summary, "ik_attempts": ik,
            "nr_original_input_summary": nr_summary, "nr_original_input_trace": nr_trace,
            "nr_original_status_counts": dict(Counter(row["status"] for row in nr_summary)),
            "raw_endpoints": raw_endpoints, "iv_rejected_q3": iv_limits,
            "rank_fixture_specs": rank_specs, "rank_spectra": rank_rows,
            "nr_extra_fixture_scope": "Each environment has separately logged 22 additional component cases; excluded from the original10 response plots and denominators",
            "q3_bound_provenance": "Comau author APC constructor q3min=deg2rad(-90), q3max=deg2rad(75), original PI_=3.1416 retained; copied as display constants only, no solver call",
            "source_manifest_repositories": [{"repository": row["repository"], "branch": row["branch"],
                                              "commit": row["commit"]} for row in source_manifest["repositories"]],
            "zero_plot_policy": "Exact zeros remain zero in CSV/JSON; log figures display zeros at annotated floor without changing qualification",
            "plot_zero_floors": {"position_mm": 1e-14, "rotation_matrix": 1e-17,
                                 "relative_singular_value": 1e-18}}
    return data, saved.sha256


def configure_plotting() -> None:
    installed = {font.name for font in font_manager.fontManager.ttflist}
    for name in ("Noto Sans CJK SC", "Noto Sans CJK JP", "WenQuanYi Zen Hei"):
        if name in installed:
            plt.rcParams["font.sans-serif"] = [name]
            break
    plt.rcParams.update({"axes.unicode_minus": False, "font.size": 9,
                         "figure.dpi": 150, "savefig.facecolor": "white",
                         "svg.fonttype": "none", "axes.spines.top": False,
                         "axes.spines.right": False})


def save_figure(out: Path, name: str, fig) -> None:
    fig.savefig(out / (name + ".png"), dpi=220, bbox_inches="tight")
    fig.savefig(out / (name + ".svg"), bbox_inches="tight")
    plt.close(fig)


def plot_ik(out: Path, data: dict) -> None:
    fig, axes = plt.subplots(2, 5, figsize=(15, 6.4), sharex=True, sharey="row")
    keys = ("position_maxabs_mm", "rotation_matrix_maxabs")
    floors = (1e-14, 1e-17)
    markers = ("o", "x", "+")
    for col, env in enumerate(ENVIRONMENTS):
        counts = [next(row for row in data["ik_groups"] if row["environment"] == env and row["group"] == group)
                  for group in GROUPS]
        axes[0, col].set_title(env + "\n返回 " + " / ".join(f"{r['accepted']}/80" for r in counts)
                               + "\n拒绝 " + " / ".join(str(r["rejected"]) for r in counts), fontsize=9)
        for row_index, key in enumerate(keys):
            ax = axes[row_index, col]
            for group_index, group in enumerate(GROUPS):
                rows = [row for row in data["ik_attempts"] if row["environment"] == env
                        and row["group"] == group and row["accepted"]]
                ax.scatter([row["attempt"] + (group_index - 1) * .24 for row in rows],
                           [max(row[key], floors[row_index]) for row in rows],
                           marker=markers[group_index], color=COLORS[group_index],
                           s=17 if group_index == 0 else 24, alpha=.76, linewidths=.8)
            ax.set_yscale("log")
            ax.axhline(1e-5, color="#444444", ls="--", lw=.8)
            ax.grid(alpha=.18)
            ax.set_xlim(-2, 81)
            ax.set_xticks((0, 40, 79))
        axes[1, col].set_xlabel("原分支尝试序号")
    axes[0, 0].set_ylabel("回代位置分量最大误差（mm）")
    axes[1, 0].set_ylabel("回代旋转矩阵最大误差（无量纲）")
    axes[0, 0].set_ylim(5e-15, 2e4)
    axes[1, 0].set_ylim(5e-18, 1e-3)
    handles = [Line2D([], [], color=COLORS[i], marker=markers[i], ls="", label=label)
               for i, label in enumerate(GROUP_LABELS)]
    handles.append(Line2D([], [], color="#444444", ls="--", label="原固定资格门"))
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(.52, .93), ncol=4, frameon=False)
    fig.suptitle("同一批 qa 与八分支：R1 原生和 R2 几何一致版本的真实返回误差", y=1.01, fontsize=13)
    fig.text(.5, .005, "每栏计数依次为 R1 / R2原目标 / R2连续目标；拒绝保留在80分母内。精确零仅在对数图显示为位置1e−14、旋转1e−17，CSV保留零。",
             ha="center", fontsize=8)
    fig.subplots_adjust(left=.065, right=.995, bottom=.12, top=.77, wspace=.13, hspace=.22)
    save_figure(out, "01_ik_r1_r2_same_inputs", fig)


def plot_nr(out: Path, data: dict) -> None:
    fig, axes = plt.subplots(2, 5, figsize=(15, 6.3), sharex=True, sharey="row")
    palette = plt.get_cmap("tab10")
    for col, env in enumerate(ENVIRONMENTS):
        summaries = [row for row in data["nr_original_input_summary"] if row["environment"] == env]
        converged = sum(row["status"] == "CONVERGED" for row in summaries)
        axes[0, col].set_title(f"{env}\n原10输入：合法收敛{converged}/10", fontsize=10)
        for index in range(10):
            rows = [row for row in data["nr_original_input_trace"]
                    if row["environment"] == env and row["input"] == index]
            rejected = rows[0]["status"] != "CONVERGED"
            for row_index, key in enumerate(("position_maxabs_mm", "rotation_matrix_maxabs")):
                ax = axes[row_index, col]
                values = [max(row[key], (1e-14, 1e-17)[row_index]) for row in rows]
                ax.plot([row["iteration"] for row in rows], values, marker=".", lw=1,
                        ls="--" if rejected else "-", color=palette(index), alpha=.8)
                if rejected:
                    ax.scatter([rows[-1]["iteration"]], [values[-1]], color="#b74336", marker="x", s=38, zorder=5)
        for ax in axes[:, col]:
            ax.set_yscale("log")
            ax.axhline(1e-5, color="#444444", ls="--", lw=.8)
            ax.grid(alpha=.18)
            ax.set_xticks((0, 1, 2, 3))
            ax.set_xlim(-.12, 3.18)
        axes[1, col].set_xlabel("NR 数值迭代次数")
        if env == "IV":
            axes[0, col].text(.04, .05, "输入2/4/8：闭合后限位拒绝", transform=axes[0, col].transAxes,
                              color="#a43d32", fontsize=8)
    axes[0, 0].set_ylabel("真实闭合位置分量最大误差（mm）")
    axes[1, 0].set_ylabel("真实闭合旋转矩阵最大误差（无量纲）")
    axes[0, 0].set_ylim(5e-15, 2e3)
    axes[1, 0].set_ylim(5e-18, .3)
    handles = [Line2D([], [], color=palette(i), label=str(i)) for i in range(10)]
    fig.legend(handles=handles, title="原输入编号", loc="upper center", bbox_to_anchor=(.52, .95),
               ncol=10, frameon=False, handlelength=1.3, columnspacing=1.3)
    fig.suptitle("原10组近端点输入：NR 真实数值迭代响应（非控制时间响应）", y=1.015, fontsize=13)
    fig.text(.5, .005, "仅原10输入；额外组件fixture未并入。虚线+红叉保留限位拒绝；几何误差达门不能替代合法性。精确零仅按图1地板显示。",
             ha="center", fontsize=8)
    fig.subplots_adjust(left=.065, right=.995, bottom=.12, top=.78, wspace=.13, hspace=.2)
    save_figure(out, "02_nr_original10_iteration_response", fig)


def plot_endpoints(out: Path, data: dict) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.9))
    rows = data["raw_endpoints"]
    labels = [row["environment"] + "-" + {"start": "0", "goal": "1"}.get(row["endpoint"], row["endpoint"])
              for row in rows]
    for ax, key, ylabel in zip(axes, ("position_maxabs_mm", "rotation_matrix_maxabs"),
                               ("原始闭合位置分量最大误差（mm）", "原始闭合旋转矩阵最大误差（无量纲）")):
        for index, row in enumerate(rows):
            ax.scatter(index, max(row[key], 1e-17), color="#4379b4" if index % 2 == 0 else "#398a76",
                       marker="o" if index % 2 == 0 else "^", s=42)
        ax.set_xticks(range(len(rows)), labels, rotation=35)
        ax.set_yscale("log")
        ax.axhline(1e-5, color="#a43d32", ls="--", label="原资格门")
        ax.set_ylabel(ylabel)
        ax.set_xlabel("未修改的作者端点：0=起点，1=终点")
        ax.grid(axis="y", alpha=.2)
        ax.legend(fontsize=8)
    fig.suptitle("五个空间环境的10个原始端点：不重闭合、不替换", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, .94))
    save_figure(out, "03_raw10_endpoints_separate_units", fig)


def plot_iv_limits(out: Path, data: dict) -> None:
    rows = data["iv_rejected_q3"]
    indices = sorted({row["input"] for row in rows})
    if indices != [2, 4, 8]:
        raise ValueError(f"Expected the saved IV original-input failures2/4/8, got {indices}")
    lower, upper = rows[0]["source_q3_lower_rad"], rows[0]["source_q3_upper_rad"]
    fig, axes = plt.subplots(1, 2, figsize=(10.7, 4))
    for arm, color in ((1, "#b95549"), (2, "#4379b4")):
        arm_rows = [row for row in rows if row["arm"] == arm]
        x = np.arange(len(arm_rows)) + (arm - 1.5) * .15
        axes[0].scatter(x - .025, [row["input_q3_rad"] for row in arm_rows],
                        marker="o", s=38, facecolors="none", edgecolors=color, label=f"臂{arm} 输入")
        axes[0].scatter(x + .025, [row["candidate_q3_rad"] for row in arm_rows],
                        marker="x", s=38, color=color, label=f"臂{arm} 终止候选")
        if arm == 1:
            axes[1].scatter(range(3), [row["input_q3_rad"] for row in arm_rows], marker="o",
                            s=45, facecolors="none", edgecolors=color, label="输入 q3")
            axes[1].scatter(range(3), [row["candidate_q3_rad"] for row in arm_rows], marker="x",
                            s=45, color=color, label="终止候选 q3")
            for index, row in enumerate(arm_rows):
                axes[1].annotate(f"{row['candidate_q3_rad']:.6f}", (index, row["candidate_q3_rad"]),
                                 xytext=(0, -15), textcoords="offset points", ha="center", fontsize=8)
    axes[0].axhline(lower, ls="--", color="#333333", lw=1, label=f"原下限 {lower:.4f}")
    axes[0].axhline(upper, ls=":", color="#333333", lw=1, label=f"原上限 {upper:.3f}")
    axes[0].set_ylim(-1.74, 1.48)
    axes[0].set_title("两臂 q3 与原上下限")
    axes[0].legend(fontsize=8, ncol=2, loc="upper right")
    axes[1].axhline(lower, ls="--", color="#333333", lw=1, label=f"原下限 {lower:.4f}")
    axes[1].set_ylim(-1.5855, -1.5675)
    axes[1].set_title("臂1下限附近放大：三次均为真实拒绝")
    axes[1].legend(fontsize=8, loc="upper right")
    for ax in axes:
        ax.set_xticks(range(3), ["输入" + str(index) for index in indices])
        ax.set_ylabel("q3（rad）")
        ax.grid(alpha=.18)
    fig.suptitle("IV 原10输入中的3次限位失败：输入与终止候选（未记录中间关节轨迹）", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, .93))
    save_figure(out, "04_iv_three_rejections_q3_bounds", fig)


def plot_rss(out: Path, data: dict) -> None:
    fixtures = ("regular", "original_elbow", "true_elbow", "wrist", "true_elbow_wrist")
    labels = ("常规对照", "原肘固定值", "几何真肘奇异", "腕零角", "真肘+腕零角")
    palette = ("#66747c", "#b16b48", "#4379b4", "#398a76", "#9564a0")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), sharey=True)
    for ax, env in zip(axes, ("II", "IV")):
        for name, label, color in zip(fixtures, labels, palette):
            for method in ("analytic", "native_fk_central_difference"):
                rows = [row for row in data["rank_spectra"] if row["environment"] == env
                        and row["arm"] == 1 and row["fixture"] == name and row["method"] == method]
                rows.sort(key=lambda row: row["singular_value_index"])
                ax.plot([row["singular_value_index"] for row in rows],
                        [max(row["sigma_over_sigma1"], 1e-18) for row in rows], color=color,
                        ls="-" if method == "analytic" else "--",
                        marker="o" if method == "analytic" else "x", ms=4, lw=1,
                        label=label + f"（rank{rows[0]['rank']}）" if method == "analytic" else None)
        ax.set_yscale("log")
        ax.axhline(1e-6, color="#a43d32", ls=":", lw=1)
        ax.set_xticks(range(1, 7))
        ax.set_xlabel("奇异值序号")
        ax.set_title(env + "，臂1；解析 / 连续原生FK中央差分")
        ax.grid(alpha=.18)
    axes[0].set_ylabel("sigma_i / sigma_1（平移行先由mm缩放至m）")
    axes[0].set_ylim(3e-19, 2.5)
    fixture_handles = [Line2D([], [], color=color, marker="o", label=label + ("（rank6）" if i < 2 else "（rank5）"))
                       for i, (label, color) in enumerate(zip(labels, palette))]
    fig.legend(handles=fixture_handles, loc="lower center", ncol=5, frameon=False,
               bbox_to_anchor=(.5, .04), fontsize=8, handlelength=1.3, columnspacing=1.15)
    fig.legend(handles=[Line2D([], [], color="#444444", ls="-", marker="o", label="独立解析Jacobian"),
                        Line2D([], [], color="#444444", ls="--", marker="x", label="连续原生FK中央差分"),
                        Line2D([], [], color="#a43d32", ls=":", label="预声明相对秩门1e−6")],
               loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(.5, -.015))
    fig.suptitle("RSS 五类固定几何诊断：原肘固定值仍满秩；奇异交集不必再降一秩", fontsize=12)
    fig.tight_layout(rect=(0, .14, 1, .94))
    save_figure(out, "05_rss_five_fixtures_singular_spectra", fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        raise FileExistsError(f"Refusing to overwrite an existing asset directory: {out}")
    data, sources = prepare()
    configure_plotting()
    out.mkdir(parents=True, exist_ok=False)
    tables = {
        "ik_attempts_all_denominators.csv": data["ik_attempts"], "ik_group_summary.csv": data["ik_groups"],
        "nr_original10_iteration_trace.csv": data["nr_original_input_trace"],
        "nr_original10_summary.csv": data["nr_original_input_summary"],
        "raw10_endpoints.csv": data["raw_endpoints"], "iv_three_rejections_q3.csv": data["iv_rejected_q3"],
        "rss_all_arms_singular_values.csv": data["rank_spectra"], "r2_spatial_checks.csv": data["checks"],
    }
    for name, rows in tables.items():
        new_csv(out / name, rows)
    plot_ik(out, data)
    plot_nr(out, data)
    plot_endpoints(out, data)
    plot_iv_limits(out, data)
    plot_rss(out, data)
    data["source_sha256"] = sources
    data["plot_script_sha256"] = digest(Path(__file__))
    data["report_only_revision"] = {
        "preserved_first_render": "reports/p4_full_r2_assets_20261015_v1",
        "change": "Replace missing subscript glyphs with ASCII; move legends clear of data; normalize endpoint display labels to0/1",
        "scientific_data_changed": False,
    }
    data["figure_data_tables"] = list(tables)
    data["figures_png"] = [path.name for path in sorted(out.glob("*.png"))]
    new_json(out / "report_data.json", data)
    new_json(out / "source_sha256.json", sources)
    notes = ("# P4 R2 空间组件图表口径\n\n"
             "本目录全部图表由已保存的R1/R2日志生成，不导入或调用任何求解器。五空间环境II–VI；不含本轮尚未交付的I环境。\n\n"
             "IK每模型保留R1原生80、R2原保存目标80、R2连续物理目标80三个独立分母。拒绝行保留在CSV/JSON，未用误差零填充。\n\n"
             "NR曲线仅为原10输入的数值迭代，横轴不是物理时间。额外22组件fixture未混入原10分母。IV输入2/4/8几何闭合后仍因原限位拒绝，未改判合法收敛。\n\n"
             "原始10端点未重闭合；q3图仅画输入和终止候选，中间关节路径未被记录。原上下限保留作者3.1416字面。\n\n"
             "RSS图仅示例II/IV臂1，其它环境/各臂的全部已保存奇异值也在CSV。五类固定fixture不是全局合法随机RSS目标或规划成功证明。\n\n"
             "位置误差为mm，旋转矩阵误差无量纲，角误差另存rad。对数图中的精确零按声明地板显示，原CSV/JSON仍为零。\n")
    with (out / "FIGURE_SCOPE.md").open("x", encoding="utf-8") as handle:
        handle.write(notes)
    generated = {path.name: digest(path) for path in sorted(out.iterdir()) if path.is_file()}
    new_json(out / "asset_manifest.json", {"schema": "P4_R2_SPATIAL_FIGURE_ASSETS_V1", "files": generated,
                                          "plot_script_sha256": data["plot_script_sha256"],
                                          "source_files": len(sources), "solver_calls_during_render": 0})
    print(json.dumps({"output": str(out), "figures": len(data["figures_png"]),
                      "ik_rows": len(data["ik_attempts"]), "nr_original_inputs": len(data["nr_original_input_summary"]),
                      "nr_status": data["nr_original_status_counts"], "source_files": len(sources),
                      "solver_calls_during_render": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
