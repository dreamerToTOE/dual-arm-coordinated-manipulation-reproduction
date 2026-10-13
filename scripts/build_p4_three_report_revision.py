#!/usr/bin/env python3
"""Preserve the original report; revise figure-9 layout and save a named Word.

All research content, editable equations and data stay identical. Existing
outputs are refused. No planner/model/IK/collision modules are imported.
"""
import hashlib
import json
from pathlib import Path
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    original = ROOT / "reports/P4_三方法复现汇总.docx"
    target = ROOT / "reports/第一篇P4闭链运动规划论文复现汇总.docx"
    data_path = ROOT / "reports/p4_three_assets/report_data.json"
    data = json.loads(data_path.read_text())
    for name, expected in data["source_sha256"].items():
        if sha((ROOT / name).read_bytes()) != expected:
            raise ValueError("saved research source differs: " + name)
    if target.exists():
        raise FileExistsError(target)
    out = ROOT / "reports/p4_three_layout_revision"
    out.mkdir(exist_ok=False)
    font = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
    font_manager.fontManager.addfont(str(font))
    plt.rcParams.update({"font.family": font_manager.FontProperties(fname=str(font)).get_name(),
                         "axes.unicode_minus": False, "font.size": 10, "svg.fonttype": "none"})
    bridge = data["math_evidence"]["rss_registered_bridge"]
    if not bridge["two_branch_bridge_qualified"]:
        raise ValueError("cannot draw an unqualified bridge")
    left = bridge["left_connection"]["path"]
    right = bridge["right_connection"]["path"]
    path = np.asarray(left + right[1:])
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), constrained_layout=True)
    ax = axes[0]
    ax.plot(range(len(path)), path[:, 17], color="#386b9e", lw=1.8)
    ax.scatter([len(left)-1], [path[len(left)-1, 17]], color="#b64b3e", label="精确奇异点 q17=0")
    ax.set(xlabel="两段固定RBS夹具路径点编号", ylabel="RSS被动链中关节 q17 / rad",
           title="RSS跨两根：单元桥接证据，非随机规划成功")
    ax.legend(fontsize=8, loc="lower right")
    ax.text(.02, .98, f"det(Jp)={bridge['determinant']:.2e}\n"
            f"随机搜索合格奇异样本={data['rss_sampling']['qualified_singular_samples']}",
            ha="left", va="top", transform=ax.transAxes, fontsize=8)
    ax = axes[1]
    x = np.arange(2)
    ax.bar(x-.17, [data["pcs_tree_partitions"].get(str(p), 0) for p in (0, 16)], .34,
           color="#328576", label="两树已接受边")
    ax.bar(x+.17, [data["pcs_path_partitions"].get(str(p), 0) for p in (0, 16)], .34,
           color="#85b5a2", label="成功解路径边")
    ax.set(xticks=x, xticklabels=["被动关节[0,1,2]", "被动关节[16,17,18]"],
           ylabel="实际边数 / 全部试验累计", title="PCS实际使用两个不同被动划分")
    ax.legend(fontsize=8)
    for extension in ("png", "svg"):
        fig.savefig(out / ("09_rss_fixture_bridge_and_pcs_partitions." + extension),
                    dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    original_image = ROOT / "reports/p4_three_assets/09_rss_fixture_bridge_and_pcs_partitions.png"
    revised_image = out / "09_rss_fixture_bridge_and_pcs_partitions.png"
    changes = []
    with zipfile.ZipFile(original) as source, zipfile.ZipFile(target, "x") as destination:
        original_xml = source.read("word/document.xml")
        for item in source.infolist():
            content = source.read(item.filename)
            if item.filename.startswith("word/media/") and sha(content) == sha(original_image.read_bytes()):
                content = revised_image.read_bytes()
                changes.append(item.filename)
            if item.filename.startswith("word/footer") and item.filename.endswith(".xml"):
                content = content.replace("科研 Benchmark：草案 / 未定稿".encode(),
                                          "P4 三方法复现 · 部分完成".encode())
            destination.writestr(item, content)
    if len(changes) != 1:
        raise ValueError("expected exactly one embedded figure replacement")
    with zipfile.ZipFile(target) as document:
        if document.read("word/document.xml") != original_xml:
            raise ValueError("research text or editable equations changed")
    check = {"original_docx_sha256": sha(original.read_bytes()),
             "original_figure_sha256": sha(original_image.read_bytes()),
             "revised_docx_sha256": sha(target.read_bytes()),
             "revised_figure_sha256": sha(revised_image.read_bytes()),
             "data_sha256": sha(data_path.read_bytes()), "replaced_media": changes,
             "body_xml_unchanged": True, "editable_equations": original_xml.count(b"<m:oMath>"),
             "embedded_figures": original_xml.count(b"<w:drawing>"),
             "changes": ["figure9 legend moved to lower right", "footer states P4 partial reproduction"],
             "new_planning_calls": 0, "changed_research_values": 0, "original_outputs_unchanged": True}
    with (out / "revision_check.json").open("x", encoding="utf-8") as handle:
        json.dump(check, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(check, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
