#!/usr/bin/env python3
"""Pure read-only report QA; its only write is the report's delivery_check.json."""
import csv
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

import numpy as np
from lxml import etree

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/"reports/p4_report_assets"


def main():
    d=json.loads((A/"report_data.json").read_text())
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==sha for p,sha in d["source_sha256"].items()}
    assert all(hashes.values())
    with (A/"scene_path_1869.csv").open() as f: rows=list(csv.DictReader(f))
    q=json.loads((ROOT/"results/20261012_TASK06_IS_A_nominal_scene03/qualified_joint_path.json").read_text())
    v=json.loads((ROOT/"results/20261012_TASK06_IS_A_nominal_scene03/independent_path_validation.json").read_text())
    assert len(rows)==1869 and np.array_equal([[float(r[n]) for n in q["joint_names"]] for r in rows],q["q_rad"])
    for i,row in enumerate(rows):
        assert int(row["index"])==i
        assert float(row["closure_position_m"])==v["states"][i]["closure"]["position_norm_m"]
        assert float(row["closure_rotation_rad"])==v["states"][i]["closure"]["rotation_norm_rad"]
        for j,n in enumerate(q["joint_names"]):
            original=d["b0"]["joints"][j];angle=q["q_rad"][i][j]
            assert float(row[n+"_margin_rad"])==min(angle-original["lower_rad"],original["upper_rad"]-angle)
    with (A/"task06_trials.csv").open() as f: trials=list(csv.DictReader(f))
    assert len(trials)==18 and sum(t["status"]=="SUCCESS" for t in trials)==14
    for row,original in zip(trials,d["task06_trials"]):
        assert row["status"]==original["status"] and float(row["wall_sec"])==original["compute_wall_time_sec"]
        assert int(row["nodes"])==original["node_count"] and int(row["dense_points"])==original["path_points"]
        if original["status"]=="SUCCESS": assert float(row["length_rad"])==original["path_metrics"]["joint_path_length_rad"]
        else: assert not row["length_rad"]
    with (A/"task04_iteration_traces.csv").open() as f: traces=list(csv.DictReader(f))
    assert len(traces)==1212
    docx=ROOT/"reports/P4_论文复现汇总.docx"
    with zipfile.ZipFile(docx) as z:
        x=etree.fromstring(z.read("word/document.xml"))
        ns={"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main","m":"http://schemas.openxmlformats.org/officeDocument/2006/math"}
        assert len(x.xpath("//m:oMath",namespaces=ns))==16
        assert len(x.xpath("//w:drawing",namespaces=ns))==10
    pdf=ROOT/"reports/P4_论文复现汇总.pdf"
    text=subprocess.check_output(["pdftotext","-layout",str(pdf),"-"],text=True)
    pages=[p for p in text.split("\f") if p.strip()]
    assert len(pages)==23
    for required in ["第一部分","第二部分","PROJECTION_JUMP","219/293","0.236039","RSS","PCS","未实现","执行准备条件不满足"]:
        assert required in text,required
    assert "\ufffd" not in text
    unapproved=subprocess.check_output(["git","diff","--name-only",
        "e32d19d53812f008c6bc3f2d71cbf761e2b954a3"],cwd=ROOT,text=True).splitlines()
    assert not any(p.startswith(("common/","baselines/","platforms/","configs/","results/","tests/","third_party/")) for p in unapproved)
    assert not any(p.startswith("references/private_sources/") for p in subprocess.check_output(
        ["git","ls-files"],cwd=ROOT,text=True).splitlines())
    for name in ["build_p4_report_assets.py","build_p4_paper_report.py"]:
        code=(ROOT/"scripts"/name).read_text()
        assert not any(term in code for term in ["import rclpy","import rclcpp","import omni","from baselines","import mujoco"])
    result={"checks_passed":True,"page_count":len(pages),"source_hashes_verified":len(hashes),
        "q_and_margin_rows_exact":1869,"trial_rows_exact":18,"projection_trace_rows":len(traces),
        "native_editable_equations":16,"chinese_figures":10,"new_scientific_experiments":0,
        "original_scientific_files_changed":False,"private_full_text_tracked":False,
        "docx_sha256":hashlib.sha256(docx.read_bytes()).hexdigest(),"pdf_sha256":hashlib.sha256(pdf.read_bytes()).hexdigest(),
        "visual_page_review":"Main agent reviews rendered page contact sheets plus full-size math/figures; see POST-TASK REPORT"}
    (A/"delivery_check.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False))


if __name__=="__main__": main()
