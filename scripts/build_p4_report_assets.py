#!/usr/bin/env python3
"""Report-only reader/plotter. Never imports or invokes a planner or simulator."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/p4_report_assets"
SOURCES: dict[str, str] = {}
FIGURES: dict[str, dict] = {}
DATA_FIELDS: dict[str, dict] = {}


def read(relative: str):
    path = ROOT / relative
    raw = path.read_bytes()
    SOURCES[relative] = hashlib.sha256(raw).hexdigest()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def write_json(name: str, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def csv_out(name, columns, rows, source, fields):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(rows)
    DATA_FIELDS[name] = {"source": source, "fields": fields, "derived_only": True}


def figure(name, fig, sources, qualification, note):
    fig.savefig(OUT / (name + ".png"), dpi=220, bbox_inches="tight", facecolor="white")
    fig.savefig(OUT / (name + ".svg"), bbox_inches="tight", facecolor="white")
    FIGURES[name] = {"sources": sources, "qualification": qualification, "note": note}
    plt.close(fig)


def box(ax, x, y, w, h, text, color="#eef4fb", size=11):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02", linewidth=1,
                              edgecolor="#33536d", facecolor=color))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=size)


def arrow(ax, a, b):
    ax.annotate("", xy=b, xytext=a, arrowprops={"arrowstyle": "->", "color": "#33536d", "lw": 1.4})


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    font = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
    if not font.exists():
        raise RuntimeError("Chinese font missing: install Noto CJK; do not produce missing-glyph figures")
    font_manager.fontManager.addfont(str(font))
    plt.rcParams.update({"font.family": font_manager.FontProperties(fname=str(font)).get_name(),
                         "axes.unicode_minus": False, "font.size": 10, "svg.fonttype": "none"})
    p3 = "results/20261009_TASK03_closure02/model_metrics.json"
    p4 = "results/20261009_TASK04_projection03/projection_metrics.json"
    p5 = "results/20261009_TASK05_local_connection02/local_connection_metrics.json"
    p6 = "results/20261012_TASK06_constrained_search02/planning_metrics.json"
    a = "results/20261012_TASK06_IS_A_nominal_scene03/"
    b = "results/20261012_TASK06_IS_B0_path_review01/summary.json"
    m3, m4, m5, m6 = (read(p) for p in [p3, p4, p5, p6])
    path, validation, planning, review = (read(p) for p in
        [a + "qualified_joint_path.json", a + "independent_path_validation.json", a + "planning_summary.json", b])
    start, goal = read(a + "start_endpoint.json"), read(a + "goal_endpoint.json")
    # Hash-only source provenance. No FK, IK, projection, FCL, service or execution call.
    for rel in ["tests/fixtures/task03/robot.urdf", "tests/fixtures/task03/robot.srdf",
                "baselines/p4_closed_chain/closure.cpp", "baselines/p4_closed_chain/projection.cpp",
                "baselines/p4_closed_chain/local_connection.cpp", "baselines/p4_closed_chain/constrained_rrtconnect.cpp",
                "configs/engineering/task04_projection_test_v1.json",
                "configs/engineering/task05_local_connection_test_v1.json",
                "configs/engineering/task06_constrained_rrtconnect_test_v1.json",
                "configs/engineering/task06_is_a_task26_scene_v2.yaml", "configs/benchmark/benchmark_v1.yaml"]:
        file = ROOT / rel
        if file.exists(): SOURCES[rel] = hashlib.sha256(file.read_bytes()).hexdigest()

    # Two original conceptual drawings, explicitly not measurement or simulation snapshots.
    fig, ax = plt.subplots(figsize=(10, 4.1))
    ax.set(xlim=(0, 10), ylim=(0, 4.1)); ax.axis("off")
    steps = [(0.15, "明确起终点\n关节/闭链/FCL资格"), (2.65, "14维均匀采样\n最近邻与有界推进"),
             (5.15, "NR–SVD投影\n分别检查位置/旋转"), (7.65, "RBS中点递归\n原限位与真实FCL")]
    for x, text in steps: box(ax, x, 2.7, 2.1, 0.9, text)
    for x in [.15, 2.65, 5.15]: arrow(ax, (x+2.1,3.15),(x+2.5,3.15))
    box(ax, 5.15, 1.1, 4.6, 0.85, "合格边加入两棵树 → 精确汇合 → 父链回溯", "#e9f3e8")
    arrow(ax, (8.7,2.7),(8.7,1.95))
    box(ax, .15, 1.1, 4.1, .85, "任一拒绝：保存原因和已核验前缀\n预算耗尽：返回失败，不推断无解", "#fff1e9")
    arrow(ax,(5.15,3.15),(4.2,1.95));arrow(ax,(7.65,2.75),(4.2,1.55))
    ax.text(5, .33, "未汇合则交替扩展两树；输出为空间关节路径，不含执行时间", ha="center", fontsize=11)
    figure("01_nr_planning_flow", fig, ["P4 pp.2–3,5–6; author source audit; CONSTRAINED_RRTCONNECT.md"],
           "ORIGINAL_CONCEPTUAL_DIAGRAM", "原创流程示意，非新运行结果")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set(xlim=(-5,5),ylim=(-2,2));ax.axis("off")
    for x, text in [(-4,"世界系 W\n左基座 B_L"),(4,"世界系 W\n右基座 B_R")]:
        box(ax,x-.75,-.7,1.5,1.2,text)
    ax.add_patch(Rectangle((-.75,-.85),1.5,1.7,fc="#ffe6a5",ec="#a27d20"))
    ax.text(0,0,"同一刚体 O\nCube",ha="center",va="center",fontsize=12)
    for x, label in [(-1.55,"TCP_L"),(1.55,"TCP_R")]:
        ax.scatter(x,0,s=150,c="#268899" if x<0 else "#bc5c41")
        ax.text(x,.35,label,ha="center")
    arrow(ax,(-3.25,0),(-1.7,0));arrow(ax,(3.25,0),(1.7,0))
    arrow(ax,(-1.4,0),(-.75,0));arrow(ax,(1.4,0),(.75,0))
    ax.text(-2.55,-1.15,"F_L(q_L)：左TCP在W中的位姿",ha="center")
    ax.text(2.55,-1.15,"F_R(q_R)：右TCP在W中的位姿",ha="center")
    ax.text(-1.45,1.3,"G_L：O在TCP_L中的位姿",ha="center");ax.text(1.45,1.3,"G_R：O在TCP_R中的位姿",ha="center")
    ax.text(0,-1.75,"闭链要求：两条 FK × 固定抓取链预测的物体位姿相同；并非要求物体世界位姿不动",ha="center",fontsize=10)
    figure("02_frames",fig,["baselines/p4_closed_chain/README.md"],"ORIGINAL_CONCEPTUAL_DIAGRAM",
           "变换箭头表示坐标变换链，不是机械臂模型形状/实测位置")

    hist = m3["historical_fixed_grasp"]
    records = hist["per_state"]
    position = np.array([v["position_closure_m"] for v in records])
    assert int(np.count_nonzero(position > 5e-8)) == 219 and len(records) == 293
    csv_out("task03_historical.csv",["state_index","position_m","rotation_rad","central_h1e5","central_h3e6","central_h1e6","five_point_h3e6"],
            [[v["state_index"],v["position_closure_m"],v["rotation_closure_rad"],
              *[c["max_abs_entry_error"] for c in v["jacobian_validation"]["central"]],
              v["jacobian_validation"]["five_point_max_abs_entry_error"]] for v in records],p3,
            "historical_fixed_grasp.per_state[]; central[] in logged order")
    fig, axes = plt.subplots(2,1,figsize=(9,5.8),constrained_layout=True)
    ix=np.array([v["state_index"] for v in records])
    axes[0].plot(ix,position*1e6,c="#225a86",lw=1.1,label="历史原抓取残差（293条）")
    axes[0].axhline(.05,c="#b33f38",ls="--",label="原工程精度 0.05 μm（未修改）")
    axes[0].scatter([196],[position[ix.tolist().index(196)]*1e6],c="#b33f38")
    axes[0].set(xlabel="历史状态编号",ylabel="位置闭合残差 / μm",title="原历史构型：219/293位置超限，精度验收未通过")
    axes[0].legend(fontsize=9,loc="upper left")
    for i,label in enumerate(["中央差分 h=1e-5 rad","中央差分 h=3e-6 rad","中央差分 h=1e-6 rad"]):
        axes[1].semilogy(ix,[v["jacobian_validation"]["central"][i]["max_abs_entry_error"] for v in records],label=label,lw=.8)
    axes[1].semilogy(ix,[v["jacobian_validation"]["five_point_max_abs_entry_error"] for v in records],label="五点差分 h=3e-6 rad",lw=.8)
    axes[1].axhline(2e-7,c="#b33f38",ls="--",label="预声明数值门限 2e-7")
    axes[1].set(xlabel="历史状态编号",ylabel="雅可比最大元素差",title="逐状态真实FR3导数核验（位置行 m/rad；旋转行 rad/rad）")
    axes[1].legend(fontsize=8,ncol=2)
    figure("03_closure_and_jacobian",fig,[p3],"REAL_FR3_OFFLINE_MATH",
           "图展示293历史记录；全部435配置的最差统计另列正文。不混合量纲称物理误差")

    rows=[]
    for group in ["neighborhood_trials","historical_diagnostic_trials"]:
        for t in m4[group]:
            tid=t.get("trial_id",str(t.get("source_state_index")))
            sequence=[(0,t["initial_residual"])]+[(h["update_index"],h["residual_after"]) for h in t["history"] if h["update_accepted"]]
            for k,r in sequence:
                rows.append([group,tid,t.get("repeat_index"),k,r["position_norm_m"],r["rotation_norm_rad"]])
    csv_out("task04_iteration_traces.csv",["group","trial_id","repeat_index","update_index","position_m","rotation_rad"],rows,p4,
            "initial_residual and history[update_accepted].residual_after; no filling after convergence")
    trials=[t for t in m4["neighborhood_trials"] if t["repeat_index"]==0]
    assert len(trials)==97 and len(m4["neighborhood_trials"])==194
    selected=next(t for t in trials if t["trial_id"]=="joint_0_sign_-1_amplitude_2")
    fig, axes=plt.subplots(1,2,figsize=(10,4.2),constrained_layout=True)
    for ax,key,label in zip(axes,["position_norm_m","rotation_norm_rad"],["位置残差 / m","旋转残差 / rad"]):
        for t in trials:
            if not t["history"]: continue  # exact fixture zero needs no projection, not fabricated iterations
            seq=[t["initial_residual"]]+[h["residual_after"] for h in t["history"] if h["update_accepted"]]
            vals=np.array([r[key] for r in seq]); positive=vals>0
            ax.semilogy(np.arange(len(seq))[positive],vals[positive],color="#879bad",alpha=.27,lw=.7)
        seq=[selected["initial_residual"]]+[h["residual_after"] for h in selected["history"]]
        ax.semilogy(range(len(seq)),[r[key] for r in seq],"o-",c="#d46c32",label="左J1 −0.03 rad：实际3步",lw=2)
        ax.axhline(1e-8,c="#b33f38",ls="--",label="分别收敛门限 1e-8")
        ax.set(xlabel="已接受Newton更新次数",ylabel=label,xticks=range(4),title="97个唯一邻域输入（灰线不补齐）")
        ax.legend(fontsize=8)
    figure("04_projection_convergence",fig,[p4],"REAL_FR3_OFFLINE_PROJECTION",
           "96条非零扰动曲线+1个零更新夹具；97输入各重复2次，原始194条全部保存CSV")

    trial_rows=[]
    paired=[]
    for case in m6["cases"]:
        for seed in m6["protocol"]["seeds"]:
            pair=sorted([t for t in case["trials"] if t["seed"]==seed],key=lambda t:t["repeat"])
            assert len(pair)==2
            payloads=[]
            for t in pair:
                rel="results/20261012_TASK06_constrained_search02/"+t["artifact"]+".gz"
                raw=read(rel)
                assert raw["status"]==t["status"] and raw["counters"]==t["summary"]
                assert raw["path_metrics"]==t["path_metrics"]
                payloads.append(raw["deterministic_payload"])
                trial_rows.append({"case":case["case"],**t})
            assert payloads[0]==payloads[1]
            paired.append({"case":case["case"],"seed":seed,"repeats":pair,"deterministic_match":True})
    assert Counter(t["status"] for t in trial_rows)=={"SUCCESS":14,"NODE_LIMIT":4}
    csv_out("task06_trials.csv",["case","seed","repeat","status","wall_sec","nodes","path_edges","dense_points","length_rad","projection_calls","fcl_state_queries"],
            [[t["case"],t["seed"],t["repeat"],t["status"],t["compute_wall_time_sec"],t["node_count"],t["path_tree_edges"],t["path_points"],
              t["path_metrics"]["joint_path_length_rad"] if t["status"]=="SUCCESS" else None,
              t["summary"]["candidate_projection_calls"]+t["summary"]["rbs_midpoint_projection_calls"],t["summary"]["collision_queries"]] for t in trial_rows],p6,
            "cases[].trials[]; independently matched to every raw *.json.gz")
    fig,axes=plt.subplots(1,2,figsize=(10,4.5),constrained_layout=True)
    labels=["简单端点","非平凡端点","固定私有障碍"]
    axes[0].bar(labels,[6,6,2],color="#438778",label="成功")
    axes[0].bar(labels,[0,0,4],bottom=[6,6,2],color="#b65b4c",label="NODE_LIMIT（600节点）")
    axes[0].set(ylabel="实际调用次数",ylim=(0,7.2),title="18次调用 / 9对重复，非18独立样本")
    axes[0].legend(fontsize=9)
    for i, pair in enumerate(paired):
        color="#438778" if pair["repeats"][0]["status"]=="SUCCESS" else "#b65b4c"
        axes[1].plot([i-.1,i+.1],[t["compute_wall_time_sec"] for t in pair["repeats"]],"o-",c=color,ms=4)
    axes[1].set(xticks=range(9),xticklabels=[f"{labels[i//3]}\n{p['seed']}" for i,p in enumerate(paired)],ylabel="规划函数计算耗时 / s",title="全部成功与预算耗尽的计算时间")
    axes[1].tick_params(axis="x",labelsize=7)
    figure("05_planning_statistics",fig,[p6],"REAL_FR3_OFFLINE_SEARCH",
           "每输入两次，时间不同不影响确定性；失败不隐藏，不计算统计显著性")
    obstacle=read("results/20261012_TASK06_constrained_search02/obstacle_seed20261012_repeat0.json.gz")
    fig,ax=plt.subplots(figsize=(9,4.5))
    for tree,color,label in [(obstacle["start_tree"],"#5382a4","起点树"),(obstacle["goal_tree"],"#bd8860","终点树")]:
        for node in tree:
            if node["parent"] is None or node["parent"]<0: continue
            u=np.array(tree[node["parent"]]["q_rad"]);v=np.array(node["q_rad"])
            ax.plot([u[3],v[3]],[u[10],v[10]],color=color,alpha=.35,lw=.7)
        q=np.array([n["q_rad"] for n in tree]);ax.scatter(q[:,3],q[:,10],s=5,c=color,label=label)
    q=np.array(obstacle["dense_path_rad"]);ax.plot(q[:,3],q[:,10],c="#274c36",lw=1.6,label="148条解树边 / 2261密集点")
    ax.set(xlabel="左J4 / rad",ylabel="右J4 / rad",title="553节点成功搜索的二维投影（仅可视化，不代表配置空间障碍形状）")
    ax.legend(fontsize=9);ax.grid(alpha=.2)
    figure("06_tree_search_projection",fig,["results/20261012_TASK06_constrained_search02/obstacle_seed20261012_repeat0.json.gz"],
           "REAL_FR3_OFFLINE_SEARCH_2D_PROJECTION", "只投影实际节点/树边，不在此二维图推断碰撞或连续安全")

    q=np.array(path["q_rad"]);states=validation["states"];names=path["joint_names"]
    assert q.shape==(1869,14) and np.array_equal(q,np.array([s["q_rad"] for s in states]))
    assert all(s["qualified"] and s["collision"]["complete"] and not s["collision"]["self_collision"] and
               not s["collision"]["world_collision"] and not s["collision"]["contacts"] for s in states)
    low=np.array([j["lower_rad"] for j in review["joints"]]);high=np.array([j["upper_rad"] for j in review["joints"]])
    margins=np.minimum(q-low,high-q)
    assert np.argmin(margins)==860*14+3 and abs(margins.min()-review["critical"]["min_margin_rad"])<1e-15
    assert SOURCES[a+"qualified_joint_path.json"]==review["path_sha256"]
    pos=np.array([s["closure"]["position_norm_m"] for s in states]);rot=np.array([s["closure"]["rotation_norm_rad"] for s in states])
    csv_out("scene_path_1869.csv",["index",*names,"closure_position_m","closure_rotation_rad",*[n+"_margin_rad" for n in names]],
            [[i,*q[i],pos[i],rot[i],*margins[i]] for i in range(len(q))],[a+"qualified_joint_path.json",a+"independent_path_validation.json",b],
            "q_rad / states[].closure / B0 joints[].lower_rad,upper_rad; no timing")
    for which,name,ylabel in [(q,"07_joint_positions","关节角 / rad"),(np.rad2deg(margins),"09_joint_margins","限位余量 / °")]:
        fig,axes=plt.subplots(7,2,figsize=(9,9.6),sharex=True,constrained_layout=True)
        for j,ax in enumerate(axes.T.flat):
            ax.plot(range(len(q)),which[:,j],c="#276e87" if j<7 else "#b65c42",lw=1)
            ax.axvline(860,c="#999999",ls=":",lw=.7)
            if name=="07_joint_positions":
                ax.axhline(low[j],c="#a45353",ls="--",lw=.7);ax.axhline(high[j],c="#a45353",ls="--",lw=.7)
            ax.set_title(("左臂" if j<7 else "右臂")+f" J{j%7+1}",loc="left",fontsize=9)
            ax.grid(alpha=.2);ax.tick_params(labelsize=8)
        for ax in axes[-1]: ax.set_xlabel("路径点序号（零基，无执行时间）",fontsize=9)
        fig.supylabel(ylabel,fontsize=11)
        figure(name,fig,[a+"qualified_joint_path.json",b],"REAL_FR3_OFFLINE_PATH_NOT_TIME_TRAJECTORY",
               "1869点；灰竖线860为树汇合点；原路径未改")
    fig,axes=plt.subplots(3,1,figsize=(9,6.2),constrained_layout=True)
    for ax,values,label in [(axes[0],pos*1e9,"位置闭链残差 / nm"),(axes[1],rot*1e9,"旋转闭链残差 / 1e-9 rad")]:
        ax.plot(range(len(q)),values,c="#276e87",lw=.8);ax.axhline(10,c="#b33f38",ls="--",label="原工程门限 1e-8")
        ax.set(ylabel=label,xlabel="路径点序号（零基）");ax.legend(fontsize=8)
    axes[2].plot(range(len(q)),np.rad2deg(margins[:,3]),c="#b33f38",label="左J4余量")
    axes[2].scatter([860],[np.rad2deg(margins[860,3])],color="#b33f38")
    axes[2].annotate("第861点：0.236039°",(860,np.rad2deg(margins[860,3])),xytext=(1100,35),arrowprops={"arrowstyle":"->"},fontsize=9)
    axes[2].set(xlabel="路径点序号（零基，无执行时间）",ylabel="最近限位余量 / °")
    figure("08_path_residual_and_risk",fig,[a+"independent_path_validation.json",a+"qualified_joint_path.json",b],
           "REAL_FR3_OFFLINE_DISCRETE_PATH", "闭链合格不表示执行余量充分；无最近FCL距离数据")
    fig,ax=plt.subplots(figsize=(10,4.4))
    ix=np.arange(14)
    ax.bar(ix-.18,[j["cumulative_travel_rad"] for j in review["joints"]],width=.36,label="累计 |Δq|",color="#276e87")
    ax.bar(ix+.18,[abs(j["net_displacement_rad"]) for j in review["joints"]],width=.36,label="端点净变化绝对值",color="#bd8860")
    ax.set(xticks=ix,xticklabels=[("左" if j<7 else "右")+f"J{j%7+1}" for j in ix],ylabel="关节变化量 / rad",title="1869点原路径：绕行诊断，不把端点直线当合格替代路径")
    ax.legend(fontsize=9)
    figure("10_joint_travel",fig,[b,a+"qualified_joint_path.json"],"READ_ONLY_EXECUTION_QUALIFICATION_REVIEW", "只是几何行程，没有关节速度/加速度结论")

    summary={"report_scope":"P4_EXISTING_EVIDENCE_ONLY_NO_NEW_EXPERIMENTS","planning_calls_this_report":0,
             "isaac_ros_controller_started":False,"task03_original_precision_failures":219,"task03_records":293,
             "task04_neighborhood_calls":194,"task04_unique_inputs":97,"task04_history_calls":293,
             "task05":m5["summary"],"task06_calls":len(trial_rows),"task06_status_counts":dict(Counter(t["status"] for t in trial_rows)),
             "task06_repeat_pairs":len(paired),"task06_repeat_pairs_matched":len(paired),
             "task06_trials":trial_rows,"task06_pairs":paired,"scene_plan":planning["trials"][0],
             "start_q_rad":start["actual14q_offline_rad"],"goal_q_rad":goal["actual14q_offline_rad"],
             "b0":review,"source_sha256":SOURCES,"figure_provenance":FIGURES,"data_provenance":DATA_FIELDS}
    write_json("report_data.json",summary)
    write_json("build_assets_check.json",{"checks_passed":True,"scientific_runs":0,"raw_trial_readbacks":18,
        "deterministic_pairs_matched":9,"historical_failure_preserved":True,"path_points_identical":1869,
        "fcl_evidence_read_only_points":1869,"critical_point_matched":860,"source_sha256":SOURCES,
        "note":"Only reads saved FCL output, does not execute collision queries"})
    print(json.dumps({"figures":len(FIGURES),"csv_files":len(DATA_FIELDS),"raw_readbacks":18,"scientific_runs":0}))


if __name__=="__main__": main()
