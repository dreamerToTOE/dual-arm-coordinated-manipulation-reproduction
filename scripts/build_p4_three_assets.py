#!/usr/bin/env python3
"""Generate Chinese report assets from saved P4 comparison evidence only.

No scientific algorithm imports, planning, IK, projection, FK qualification,
collision query, simulator or robot commands. The drawing-only planar coordinates
are the predeclared elementary link-sum formula applied to saved joint arrays.
Every numerical scientific curve comes from a saved measurement field. Gzip
artifacts are independently matched to their trial rows and SHA256 hashes.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import gzip
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyBboxPatch
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
METHODS = ("RSS", "PCS", "NR")
COLORS = {"RSS": "#386b9e", "PCS": "#328576", "NR": "#d27737"}
ENV_NAMES = {"E0_sparse": "稀疏环境 E0", "E1_clutter": "多障碍环境 E1"}
OBSTACLES = {"E0_sparse": ((.45, .72, .045),),
             "E1_clutter": ((.45, .72, .045), (.50, .18, .065), (.72, .60, .05))}
SOURCES, FIGURES, FIELDS = {}, {}, {}


def relative(path):
    return str(path.relative_to(ROOT))


def read(path):
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    SOURCES[relative(path)] = digest
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def save_json(out, name, data):
    (out/name).write_text(json.dumps(data, ensure_ascii=False, indent=2,
                                    allow_nan=False) + "\n", encoding="utf-8")


def csv_out(out, name, headers, rows, provenance):
    with (out/name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)
    FIELDS[name] = {"derived_only": True, "provenance": provenance,
                   "columns": headers, "row_count": len(rows)}


def finish(out, name, fig, sources, qualification, note):
    fig.savefig(out/(name + ".png"), dpi=220, bbox_inches="tight", facecolor="white")
    fig.savefig(out/(name + ".svg"), bbox_inches="tight", facecolor="white")
    FIGURES[name] = {"sources": sources, "qualification": qualification, "note": note}
    plt.close(fig)


def box(ax, x, y, w, h, text, color="#edf3fa", size=10):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=.015",
                              facecolor=color, edgecolor="#3a536d", lw=1))
    ax.text(x+w/2, y+h/2, text, ha="center", va="center", fontsize=size)


def arrow(ax, first, second):
    ax.annotate("", xy=second, xytext=first,
                arrowprops={"arrowstyle": "->", "color": "#3a536d", "lw": 1.2})


def drawing_coordinates(q):
    """Figure placement only; no algorithm or residual/safety computation."""
    angles = np.cumsum(np.asarray(q))[:19]
    step = np.sin(np.pi/38.0) * np.column_stack((np.cos(angles), np.sin(angles)))
    return np.vstack((np.zeros(2), np.cumsum(step, axis=0)))


def background(ax, environment):
    for x, y, radius in OBSTACLES[environment]:
        ax.add_patch(Circle((x, y), radius, ec="#7d6060", fc="#dec8c3", alpha=.75))
    ax.plot([0, 1], [0, 0], "-", c="#555555", lw=3, label="固定基杆")
    ax.scatter([0, 1], [0, 0], c="#555555", s=20)
    ax.set(aspect="equal", xlabel="世界 x / m", ylabel="世界 y / m")
    ax.grid(alpha=.16)


def curves(raw):
    """Copy stored path qualification, never recalculate a constraint/query."""
    path = np.asarray(raw["path"], dtype=float)
    qualifications = raw["path_metrics"]["state_qualifications"]
    assert len(path) == len(qualifications)
    return path, {
        "position_m": [r["closure_position"] for r in qualifications],
        "rotation_rad": [r["closure_angle"] for r in qualifications],
        "joint_margin_rad": [r["joint_margin"] for r in qualifications],
        "clearance_m": [r["collision"]["minimum_clearance"] for r in qualifications],
        "closest_pair": [r["collision"]["pair"] for r in qualifications],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default="20261013_P4_three_methods_round2")
    parser.add_argument("--output", default="reports/p4_three_assets")
    args = parser.parse_args()
    run = ROOT/"results"/args.run_id
    out = ROOT/args.output
    # Refuse unfinished suites; no imputation of absent trials or stale assets.
    for name in ("summary.json", "trials.json", "math_evidence.json", "tests.json"):
        if not (run/name).is_file():
            raise RuntimeError("Completed saved suite required; missing " + str(run/name))
    summary, trials, math, tests, config, versions = [read(run/name) for name in
        ("summary.json", "trials.json", "math_evidence.json", "tests.json",
         "config_snapshot.json", "versions.json")]
    assert len(trials) == summary["trial_count"] == config["statistical_trials"]
    assert all(not trial["repeat"] for trial in trials)
    assert len(set((t["environment"], t["budget"], t["method"], t["seed"]) for t in trials)) == len(trials)
    protocol = ROOT/"reports/P4_THREE_METHOD_PRE_TASK.md"
    SOURCES[relative(protocol)] = hashlib.sha256(protocol.read_bytes()).hexdigest()
    recorded_sources = read(run/"source_sha256.json")
    # Sources recorded by the runner may be absolute; maintain original mapping.
    for source_name, expected in recorded_sources.items():
        source = Path(source_name)
        if not source.is_absolute():
            source = ROOT/source
        observed = hashlib.sha256(source.read_bytes()).hexdigest()
        assert observed == expected, "Scientific source changed after suite: " + source_name
        SOURCES[relative(source)] = observed

    font = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
    if not font.is_file():
        raise RuntimeError("Noto CJK required; refusing missing-glyph figures")
    font_manager.fontManager.addfont(str(font))
    plt.rcParams.update({"font.family": font_manager.FontProperties(fname=str(font)).get_name(),
                         "axes.unicode_minus": False, "font.size": 10,
                         "svg.fonttype": "none"})
    out.mkdir(parents=True, exist_ok=True)

    by_method = {method: [t for t in trials if t["method"] == method] for method in METHODS}
    ordered = sorted(trials, key=lambda t: (t["seed"], config["environments"].index(t["environment"]),
                                           t["budget"]))
    chosen = {method: next((t for t in ordered if t["method"] == method and
                           t["status"] == "SUCCESS"), None) for method in METHODS}
    selected, local_rejections, pcs_tree_partitions, pcs_path_partitions = {}, {}, Counter(), Counter()
    rss_sampling = Counter()
    raw_artifact_count = 0
    roots = None
    for trial in trials:
        source = run/trial["artifact"]
        raw = read(source)
        assert SOURCES[relative(source)] == trial["sha256"], "Raw artifact hash mismatch"
        assert raw["status"] == trial["status"] and raw["counters"] == trial["counters"]
        assert raw["failure_counts"] == trial["failure_counts"]
        assert raw["compute_wall_time_sec"] == trial["wall_sec"]
        assert raw["node_count"] == trial["nodes"]
        for key in ("method", "environment", "seed"):
            assert raw[key] == trial[key]
        assert raw["max_iterations"] == trial["budget"]
        if trial["path_metrics"] is not None:
            observed_metrics = {k: v for k, v in raw["path_metrics"].items()
                                if k != "state_qualifications"}
            assert observed_metrics == trial["path_metrics"]
        else:
            assert raw["status"] != "SUCCESS" and not raw["path"]
        raw_artifact_count += 1
        if roots is None:
            roots = {"start": raw["start"], "goal": raw["goal"]}
        else:
            assert raw["start"] == roots["start"] and raw["goal"] == roots["goal"]
        reasons = local_rejections.setdefault(trial["method"], Counter())
        for attempt in raw["attempts"]:
            connection = attempt.get("connection")
            if connection is not None and not connection["success"]:
                reasons[connection["reason"]] += 1
            if trial["method"] == "PCS" and attempt["accepted"]:
                pcs_tree_partitions[str(connection["partition"])] += 1
        if trial["method"] == "PCS":
            pcs_path_partitions.update(str(edge["partition"]) for edge in raw["path_edges"])
        if trial["method"] == "RSS":
            rss_sampling.update({"construction_attempts": len(raw["singular_log"]),
                                 "qualified_singular_samples": sum(bool(s["success"]) for s in raw["singular_log"]),
                                 "requests": raw["counters"].get("singular_sample_requests", 0),
                                 "qualified_singular_endpoint_edges": raw["counters"].get("rss_singular_endpoint_connections", 0)})
        if chosen[trial["method"]] is trial:
            path, values = curves(raw)
            selected[trial["method"]] = {"trial": trial, "path": path.tolist(),
                "curves": values, "path_edges": raw["path_edges"],
                "selection_rule": "First SUCCESS ordered by seed ascending, then registered environment order, then budget; no best-path selection"}
        del raw
    for repeated in summary["deterministic_repeats"]:
        raw = read(run/repeated["artifact"])
        assert raw["seed"] == 7 and raw["max_iterations"] == 200 and raw["environment"] == "E0_sparse"
        assert raw["method"] == repeated["method"]
        raw_artifact_count += 1
        del raw
    for group in summary["groups"]:
        members = [t for t in trials if all(t[k] == group[k] for k in ("method", "environment", "budget"))]
        successes = [t for t in members if t["status"] == "SUCCESS"]
        assert len(members) == group["trials"] and len(successes) == group["success"]
        assert len(successes)/len(members) == group["success_rate"]
        assert dict(Counter(t["status"] for t in members)) == group["status_counts"]
        assert float(np.mean([t["wall_sec"] for t in members])) == group["wall_all_trials_mean"]

    csv_out(out, "all_trial_metrics.csv", ["environment", "budget", "method", "seed", "status",
        "wall_sec", "nodes", "projection_calls", "ik_calls", "nr_calls", "geometry_queries",
        "local_connections", "local_failures", "path_length_rad", "minimum_clearance_m", "artifact", "sha256"],
        [[t["environment"], t["budget"], t["method"], t["seed"], t["status"], t["wall_sec"], t["nodes"],
          *[t["counters"].get(k, 0) for k in ("projection_calls", "ik_calls", "nr_calls", "geometry_queries",
                                              "local_connection_calls", "local_connection_failures")],
          None if t["path_metrics"] is None else t["path_metrics"]["joint_path_length_rad"],
          None if t["path_metrics"] is None else t["path_metrics"]["minimum_clearance_m"],
          t["artifact"], t["sha256"]] for t in trials],
        "trials.json; every row checked against raw gzip and exact SHA256; failed path fields blank, not zero")
    for method, item in selected.items():
        values = item["curves"]
        csv_out(out, "selected_" + method + "_path.csv", ["state_index"] +
            [f"joint_{j+1:02d}_rad" for j in range(20)] +
            ["closure_position_m", "closure_angle_rad", "joint_margin_rad", "minimum_clearance_m", "closest_pair"],
            [[index, *q, values["position_m"][index], values["rotation_rad"][index],
              values["joint_margin_rad"][index], values["clearance_m"][index],
              " <-> ".join(values["closest_pair"][index])] for index, q in enumerate(item["path"])],
            item["trial"]["artifact"] + ": saved path and path_metrics.state_qualifications; no new mathematical evaluation")

    fig, ax = plt.subplots(figsize=(10, 5.3))
    ax.set(xlim=(0, 10), ylim=(0, 5.3)); ax.axis("off")
    descriptions = [("RSS", "固定被动链 + 20%精确奇异采样\n同分支连接；奇异端点桥接两根"),
                    ("PCS", "两个真实被动划分 + 解析双根\n寻找两端共同分支后切换局部链"),
                    ("NR", "全闭链残差 + Jacobian伪逆\nNewton–SVD投影每个候选/中点")]
    for index, (method, description) in enumerate(descriptions):
        x = .15 + index*3.3
        box(ax, x, 3.4, 3.0, 1.25, method + "\n" + description, size=10)
        arrow(ax, (x+1.5, 3.4), (x+1.5, 2.85))
    box(ax, .15, 1.9, 9.6, .95, "同一20R机构、两环境、起终点、PCG64种子与计算预算\n同一双向树 / RBS / GEOS碰撞 / 原生关节边界", "#e7f1e9")
    arrow(ax, (4.95, 1.9), (4.95, 1.4))
    box(ax, .15, .45, 9.6, .95, "记录全部成功与失败 → 合格路径独立离散重检 → 真实数据统一比较\n不调用NR替代RSS/PCS，不做Isaac执行，不声称连续安全", "#fff0e5")
    ax.set_title("原论文三种策略与本次共同实验流程（原创理论示意，不是运行测量）")
    finish(out, "01_three_strategy_flow", fig, [relative(protocol)], "CONCEPTUAL_THEORY_DIAGRAM",
           "原文III-A/B/C、RBS及冻结协议；此流程图不是统计数据")

    fixture = math["registered_singular_fixture"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), constrained_layout=True)
    for ax, environment in zip(axes, config["environments"]):
        background(ax, environment)
        for label, q, style, color in (("登记起点", roots["start"], "-", "#386b9e"),
                                      ("登记终点（末3R换根）", roots["goal"], "--", "#c87539")):
            vertices = drawing_coordinates(q)
            ax.plot(vertices[:, 0], vertices[:, 1], style, c=color, lw=1.8, label=label)
        if fixture["success"]:
            vertices = drawing_coordinates(fixture["q"])
            ax.plot(vertices[:, 0], vertices[:, 1], ":", c="#348b62", lw=1.7, label="精确奇异单元夹具")
        ax.set_title(ENV_NAMES[environment] + "：19移动杆+固定基杆")
        ax.legend(fontsize=8, loc="upper right")
    finish(out, "02_registered_model_geometries", fig, [relative(run/"math_evidence.json"), relative(protocol)],
           "SAVED_REGISTERED_CONFIGURATIONS_RENDERED_BY_LINK_SUM",
           "仅渲染已保存q；原作者20R几何未公开，本次为预声明同类重建，非Isaac截图")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    width = .24
    for ax, environment in zip(axes, config["environments"]):
        for index, method in enumerate(METHODS):
            groups = [next(g for g in summary["groups"] if g["method"] == method and
                           g["environment"] == environment and g["budget"] == b) for b in config["outer_iteration_budgets"]]
            x = np.arange(len(groups)) + (index-1)*width
            ax.bar(x, [g["success_rate"]*100 for g in groups], width, color=COLORS[method], label=method)
            for xx, group in zip(x, groups):
                ax.text(xx, group["success_rate"]*100+2, f'{group["success"]}/{group["trials"]}', ha="center", fontsize=8)
        ax.set(xticks=range(2), xticklabels=[str(b) for b in config["outer_iteration_budgets"]],
               ylim=(0, 113), xlabel="外层迭代上限（另有5 s预算）", ylabel="实际规划成功率 / %", title=ENV_NAMES[environment])
        ax.legend(fontsize=9)
    finish(out, "03_success_rate_by_budget_env", fig, [relative(run/"trials.json"), relative(run/"summary.json")],
           "ACTUAL_COMPARISON_TRIALS", "每格5个独立固定种子；确定性重复不进入分母；没有统计显著性主张")

    fig, axes = plt.subplots(2, 2, figsize=(10, 6), constrained_layout=True)
    for row_index, environment in enumerate(config["environments"]):
        for column, budget in enumerate(config["outer_iteration_budgets"]):
            ax = axes[row_index, column]
            for index, method in enumerate(METHODS):
                group = sorted([t for t in trials if (t["environment"], t["budget"], t["method"]) ==
                                (environment, budget, method)], key=lambda t: t["seed"])
                for count, trial in enumerate(group):
                    ax.scatter(index + (count-2)*.055, trial["wall_sec"],
                               marker="o" if trial["status"] == "SUCCESS" else "x", s=38,
                               color=COLORS[method])
                ax.hlines(np.mean([t["wall_sec"] for t in group]), index-.22, index+.22, color=COLORS[method], lw=2)
            ax.axhline(config["algorithm"]["max_compute_wall_sec"], color="#777", ls=":", lw=.8)
            ax.set(xticks=range(3), xticklabels=METHODS, ylabel="实际规划计算耗时 / s",
                   title=ENV_NAMES[environment] + f"，迭代预算 {budget}")
    fig.suptitle("圆点：成功；叉号：失败；横线：含失败的全部5次平均（不含文件输出）", fontsize=11)
    finish(out, "04_wall_time_all_trials", fig, [relative(run/"trials.json")], "ACTUAL_COMPUTE_WALL_TIME",
           "含失败；计算预算可能包含最后一次有限操作开销；不是机械臂执行时间，非原论文硬件秒数等同比较")

    fig, axes = plt.subplots(1, 3, figsize=(11, 4), constrained_layout=True)
    fields = [("nodes", "树节点数 / 次均值"), ("projection_calls", "策略投影调用 / 次均值"),
              ("geometry_queries", "GEOS距离项 / 次均值")]
    for ax, (field, label) in zip(axes, fields):
        values = [np.mean([t[field] if field == "nodes" else t["counters"].get(field, 0)
                           for t in by_method[method]]) for method in METHODS]
        ax.bar(METHODS, values, color=[COLORS[m] for m in METHODS])
        for index, value in enumerate(values):
            ax.text(index, value, f"{value:.1f}", ha="center", va="bottom", fontsize=9)
        ax.set(ylabel=label, ylim=(0, max(values)*1.18 if max(values)>0 else 1))
    fig.suptitle("每方法20个真实试验的工作量（包含失败，不等于算法复杂度证明）", fontsize=11)
    finish(out, "05_nodes_projection_geometry_queries", fig, [relative(run/"trials.json")], "ACTUAL_RECORDED_COUNTERS",
           "NR与IK各自运算不同；GEOS项数不是原论文PQP检查次数，不能据此直接比原论文性能")

    reason_keys = sorted(set().union(*(set(c) for c in local_rejections.values())))
    fig, ax = plt.subplots(figsize=(10, max(3.4, len(reason_keys)*.34)), constrained_layout=True)
    for index, method in enumerate(METHODS):
        ax.barh(np.arange(len(reason_keys))+(index-1)*.23,
                [local_rejections[method].get(key, 0) for key in reason_keys],
                height=.23, color=COLORS[method], label=method)
    ax.set(yticks=range(len(reason_keys)), yticklabels=reason_keys,
           xlabel="实际局部连接拒绝次数（全部规划试验）", title="RBS拒绝原因：保留真实失败，不把拒绝改成无解证明")
    ax.legend(fontsize=9)
    finish(out, "06_local_rejection_counts", fig, ["all statistical raw gzip attempts[].connection.reason"],
           "ACTUAL_FAILED_LOCAL_CONNECTIONS", "只计实际调用后失败的RBS；候选投影失败或未调用RBS不冒充碰撞拒绝")

    fig, axes = plt.subplots(1, 3, figsize=(11, 4.2), constrained_layout=True)
    for ax, method in zip(axes, METHODS):
        if method not in selected:
            ax.axis("off")
            ax.text(.5, .5, method + "\n未取得合格规划路径\n不绘制伪造轨迹", ha="center", va="center", transform=ax.transAxes)
            continue
        item = selected[method]
        background(ax, item["trial"]["environment"])
        path = np.asarray(item["path"])
        indices = np.unique(np.linspace(0, len(path)-1, min(9, len(path))).astype(int))
        for index in indices:
            vertices = drawing_coordinates(path[index])
            ax.plot(vertices[:, 0], vertices[:, 1], color=COLORS[method], alpha=.12+.75*index/max(1, len(path)-1), lw=1)
        t = item["trial"]
        ax.set_title(f"{method}：seed={t['seed']}\n{t['environment']}，预算={t['budget']}")
    finish(out, "07_first_qualified_paths", fig, [item["trial"]["artifact"] for item in selected.values()],
           "SAVED_QUALIFIED_PATH_GEOMETRY_RENDERING",
           "每方法按seed→登记环境顺序→预算选择首条成功路径；不是最好路径，无RSS成功则明确空白")

    fig, axes = plt.subplots(4, 3, figsize=(11, 9), constrained_layout=True)
    for column, method in enumerate(METHODS):
        if method not in selected:
            for ax in axes[:, column]:
                ax.axis("off"); ax.text(.5, .5, method + "：无合格路径", ha="center", transform=ax.transAxes)
            continue
        item, color = selected[method], COLORS[method]
        path, values = np.asarray(item["path"]), item["curves"]
        ix = np.arange(len(path))
        axes[0, column].plot(ix, path, lw=.7, alpha=.65)
        axes[0, column].axhline(np.pi, color="#555", ls=":", lw=.6)
        axes[0, column].axhline(-np.pi, color="#555", ls=":", lw=.6)
        axes[0, column].set(ylabel="20关节角 / rad", title=method + " 首条合格路径")
        axes[1, column].plot(ix, values["position_m"], color=color, lw=1)
        axes[1, column].axhline(1e-8, color="#b55", ls=":", lw=.6)
        axes[1, column].set(ylabel="闭链位置残差 / m")
        axes[2, column].plot(ix, values["rotation_rad"], color=color, lw=1)
        axes[2, column].axhline(1e-8, color="#b55", ls=":", lw=.6)
        axes[2, column].set(ylabel="闭链旋转残差 / rad")
        axes[3, column].plot(ix, np.array(values["clearance_m"])*1000, color=color, lw=1)
        axes[3, column].set(ylabel="真实平面几何净距 / mm", xlabel="已保存离散路径点编号（非时间）")
    finish(out, "08_selected_path_joint_residual_clearance", fig, [item["trial"]["artifact"] for item in selected.values()],
           "SAVED_PATH_AND_STATE_QUALIFICATION_FIELDS",
           "关节、位置/旋转残差及GEOS净距逐点来自原日志；没有补时标，无新查询，无连续安全证明")

    bridge = math["rss_registered_bridge"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), constrained_layout=True)
    ax = axes[0]
    if bridge.get("two_branch_bridge_qualified"):
        left, right = bridge["left_connection"]["path"], bridge["right_connection"]["path"]
        joined = np.asarray(left + right[1:])
        ax.plot(range(len(joined)), joined[:, 17], color=COLORS["RSS"], lw=1.8)
        ax.scatter([len(left)-1], [joined[len(left)-1, 17]], color="#b64b3e", label="精确奇异点 q17=0")
        ax.set(xlabel="两段固定RBS夹具路径点编号", ylabel="RSS被动链中关节 q17 / rad",
               title="RSS跨两根：单元桥接证据，非随机规划成功")
        ax.legend(fontsize=8)
        ax.text(.02, .98, f"det(Jp)={bridge['determinant']:.2e}\n"
                f"随机搜索合格奇异样本={rss_sampling['qualified_singular_samples']}",
                ha="left", va="top", transform=ax.transAxes, fontsize=8)
    else:
        ax.axis("off"); ax.text(.5, .5, "RSS固定奇异桥未通过\n"+bridge.get("reason", "真实失败见日志"),
                                  ha="center", va="center", transform=ax.transAxes)
    ax = axes[1]
    x = np.arange(2)
    ax.bar(x-.17, [pcs_tree_partitions[str(p)] for p in (0, 16)], .34, color=COLORS["PCS"], label="两树已接受边")
    ax.bar(x+.17, [pcs_path_partitions[str(p)] for p in (0, 16)], .34, color="#85b5a2", label="成功解路径边")
    ax.set(xticks=x, xticklabels=["被动关节[0,1,2]", "被动关节[16,17,18]"],
           ylabel="实际边数 / 全部试验累计", title="PCS实际使用两个不同被动划分")
    ax.legend(fontsize=8)
    finish(out, "09_rss_fixture_bridge_and_pcs_partitions", fig,
           [relative(run/"math_evidence.json"), "all raw accepted attempts/path_edges/singular_log"],
           "DISTINCT_UNIT_BRIDGE_AND_ACTUAL_SEARCH_PARTITION_EVIDENCE",
           "固定RSS两段RBS单元证据不等于RSS随机搜索成功；PCS边来源是保存的真实划分")

    statuses = sorted(set(t["status"] for t in trials))
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), constrained_layout=True)
    bottom = np.zeros(3)
    palette = {"SUCCESS": "#5c9e79", "TIME_LIMIT": "#b96957", "ITERATION_LIMIT": "#cea260", "NODE_LIMIT": "#9476ad"}
    for status in statuses:
        counts = np.array([sum(t["status"] == status for t in by_method[m]) for m in METHODS])
        axes[0].bar(METHODS, counts, bottom=bottom, color=palette.get(status, "#999999"), label=status)
        bottom += counts
    axes[0].set(ylabel="真实试验数", title="全量终止类型（每方法20次）")
    axes[0].legend(fontsize=8)
    for index, method in enumerate(METHODS):
        qualified = sorted([t for t in by_method[method] if t["status"] == "SUCCESS"],
                           key=lambda t: (t["environment"], t["budget"], t["seed"]))
        if not qualified:
            axes[1].text(index, .5, "无合格路径", ha="center", rotation=90, fontsize=8)
            continue
        lengths = [t["path_metrics"]["joint_path_length_rad"] for t in qualified]
        offsets = np.linspace(-.15, .15, len(lengths)) if len(lengths)>1 else [0]
        axes[1].scatter(index + np.array(offsets), lengths, color=COLORS[method], s=22)
        axes[1].hlines(np.mean(lengths), index-.22, index+.22, color=COLORS[method], lw=2)
    axes[1].set(xticks=range(3), xticklabels=METHODS, ylabel="成功路径关节L2累计长度 / rad",
                title="只统计成功路径：存在条件/存活偏差")
    finish(out, "10_termination_and_qualified_path_length", fig, [relative(run/"trials.json")],
           "ACTUAL_TERMINATION_AND_SUCCESS_CONDITIONAL_PATH_METRICS",
           "失败路径长度留缺失而非零；成功路径长度比较不能推断总体方法优劣")

    aggregates = {method: {"trials": len(by_method[method]),
        "status_counts": dict(Counter(t["status"] for t in by_method[method])),
        "local_rejection_counts": dict(local_rejections[method]),
        "counter_totals": {key: sum(t["counters"].get(key, 0) for t in by_method[method])
                           for key in sorted(set().union(*(t["counters"] for t in by_method[method])))}}
                  for method in METHODS}
    data = {"schema": "p4_three_methods.report_assets.v1", "run_id": args.run_id,
        "summary": summary, "trials": trials, "math_evidence": math, "tests": tests,
        "config": config, "versions": versions, "roots": roots,
        "selected_paths": selected, "aggregates": aggregates,
        "rss_sampling": dict(rss_sampling), "pcs_tree_partitions": dict(pcs_tree_partitions),
        "pcs_path_partitions": dict(pcs_path_partitions), "figures": FIGURES,
        "derived_csv": FIELDS, "source_sha256": SOURCES,
        "original_paper_scope": "Twenty-R planar environment-I-family reconstruction; exact original geometry unavailable",
        "new_algorithm_runs": 0, "no_physical_execution": True,
        "raw_artifacts_verified": raw_artifact_count}
    save_json(out, "report_data.json", data)
    save_json(out, "asset_build_check.json", {"passed": True,
        "statistical_trial_rows": len(trials), "raw_artifacts_verified": raw_artifact_count,
        "figures": len(FIGURES), "source_hashes": len(SOURCES),
        "selected_path_methods": list(selected), "new_algorithm_runs": 0,
        "limitations": ["No missing paths fabricated", "RSS fixed bridge is not global planning success",
                        "Only saved discrete geometry evidence", "Small fixed-seed sample, no superiority claim"]})
    (out/"README.md").write_text(
        "# P4 三策略真实比较图表\n\n"
        f"原始结果：`results/{args.run_id}/`。所有统计行与 gzip 原件及 SHA256 核对。\n\n"
        "10幅PNG/SVG包含原创理论流程、登记机构、全部成功/失败统计和真实合格路径。"
        "图08来自原日志的逐点关节/闭链/GEOS记录；图09严格区分RSS单元桥接与全局规划。\n\n"
        "选例规则：各方法按seed升序、登记环境顺序、预算升序选择首条SUCCESS，未成功的方法不画路径。"
        "全部60次统计见CSV；确定性重复不进入成功率分母。\n\n"
        "复建命令：`python scripts/build_p4_three_assets.py --run-id " + args.run_id + "`。"
        "该脚本只读保存数据，不运行规划、IK、碰撞查询或仿真。\n", encoding="utf-8")
    print(json.dumps({"passed": True, "figures": len(FIGURES), "trials": len(trials),
                      "raw_verified": raw_artifact_count, "selected": list(selected)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
