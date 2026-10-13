#!/usr/bin/env python3
"""Run exactly the predeclared P4 three-strategy suite; retain every trial.

Never imports Isaac/ROS/MoveIt/MuJoCo or executes robot commands.
TASK02 metadata/result logger is reused without inventing a physical timestamp.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import unittest

import numpy as np
import shapely

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from baselines.p4_comparison.model import PlanarModel
from baselines.p4_comparison.strategies import rbs_connect
from baselines.p4_comparison.planner import plan
from common.interfaces.exchange import RunMetadata,BenchmarkResult,ResultStatus,MeasurementQualification
from common.logging.run import RunLogger,source_ref


def save(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+"\n")


def protected():
    names=subprocess.check_output(["git","ls-tree","-r","--name-only",
        "d5b5096bd287a09039b9b8c1911acdf5bfeb5a46","results","baselines/p4_closed_chain",
        "common","configs/benchmark","reports/P4_论文复现汇总.docx","reports/P4_论文复现汇总.pdf"],
        cwd=ROOT,text=True).splitlines()
    return {n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names}


def without_timing(value):
    if isinstance(value,dict):
        return {k:without_timing(v) for k,v in value.items() if k not in ("compute_wall_time_sec",)}
    if isinstance(value,list):return [without_timing(v) for v in value]
    return value


def math_evidence(model):
    roots={env:{"start":model.valid(model.start,env),"goal":model.valid(model.goal,env)} for env in model.environments}
    fixture=model.singular_fixture()
    out={"roots":roots,"registered_singular_fixture":{"success":fixture.success,"reason":fixture.reason,
        "cosine":fixture.cosine,"q":None if fixture.q is None else fixture.q.tolist()},
        "branch_labels":{"start":[model.branch(model.start,p) for p in model.partitions],
            "goal":[model.branch(model.goal,p) for p in model.partitions]}}
    out["direct_connections"]={m:rbs_connect(model,"E0_sparse",m,model.start,model.goal) for m in ["RSS","PCS","NR"]}
    if fixture.success:
        Jp=model.jacobian(fixture.q)[:,16:19]
        left=rbs_connect(model,"E0_sparse","RSS",model.start,fixture.q)
        right=rbs_connect(model,"E0_sparse","RSS",fixture.q,model.goal)
        out["rss_registered_bridge"]={"passive_jacobian":Jp.tolist(),
            "determinant":float(np.linalg.det(Jp)),"singular_values":np.linalg.svd(Jp,compute_uv=False).tolist(),
            "middle_angle_rad":float(fixture.q[17]),"qualification":model.valid(fixture.q,"E0_sparse"),
            "left_connection":left,"right_connection":right,
            "two_branch_bridge_qualified":left["success"] and right["success"]}
    else:
        out["rss_registered_bridge"]={"two_branch_bridge_qualified":False,"reason":fixture.reason}
    return out


def validate_result(result,model):
    if result["status"]!="SUCCESS":return {"status":"NOT_APPLICABLE_NO_QUALIFIED_PATH"}
    path=np.asarray(result["path"])
    assert path.ndim==2 and path.shape[1]==20 and len(path)>0
    assert np.array_equal(path[0],model.start) and np.array_equal(path[-1],model.goal)
    rows=[model.valid(q,result["environment"]) for q in path]
    assert all(r["valid"] for r in rows)
    adjacent=np.linalg.norm(np.diff(path,axis=0),axis=1)
    assert len(adjacent)==0 or np.max(adjacent)<=result["config"]["rbs_resolution_rad"]+1e-12
    for edge in result["path_edges"]:
        source=result["attempts"][edge["attempt_index"]]
        assert source["accepted"] and source["connection"]["success"]
        assert edge["partition"]==source["connection"]["partition"]
        if result["method"]=="RSS":assert edge["partition"]==16
        elif result["method"]=="PCS":assert edge["partition"] in model.partitions
        else:assert edge["partition"] is None
    return {"status":"PASS","states":len(rows),"path_edge_sources":len(result["path_edges"]),
        "max_position_residual_m":max(r["closure_position"] for r in rows),
        "max_rotation_residual_rad":max(r["closure_angle"] for r in rows),
        "minimum_joint_margin_rad":min(r["joint_margin"] for r in rows),
        "minimum_planar_clearance_m":min(r["collision"]["minimum_clearance"] for r in rows),
        "minimum_pair":min((r["collision"] for r in rows),key=lambda r:r["minimum_clearance"])["pair"],
        "max_adjacent_l2_rad":float(np.max(adjacent)) if len(adjacent) else 0.0,
        "qualification":"INDEPENDENT_DISCRETE_RECHECK_NO_SWEEP_CERTIFICATE"}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id",required=True)
    args=parser.parse_args()
    cfg_path=ROOT/"configs/engineering/p4_three_methods_v1.json"
    cfg=json.loads(cfg_path.read_text())
    sources=tuple(source_ref(f"s{i}",ROOT/n) for i,n in enumerate([
        "configs/engineering/p4_three_methods_v1.json","reports/P4_THREE_METHOD_PRE_TASK.md",
        "baselines/p4_comparison/model.py","baselines/p4_comparison/strategies.py","baselines/p4_comparison/planner.py",
        "tests/test_p4_comparison_model.py","tests/test_p4_comparison_strategies.py",
        "scripts/run_p4_three_methods.py","common/logging/run.py"]))
    commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    meta=RunMetadata(args.run_id,"P4_THREE_METHOD_COMPARISON","P4","PLANAR_GEOMETRIC_OFFLINE",
        commit,0,None,tuple([sys.executable,*sys.argv]),("p4_three_v1",),(str(cfg_path),),sources)
    before=protected()
    with RunLogger(ROOT/"results",meta) as logger:
        out=logger.path
        save(out/"config_snapshot.json",cfg);save(out/"protected_sha256.json",before)
        save(out/"source_sha256.json",{s.path:s.sha256 for s in sources})
        save(out/"versions.json",{"python":sys.version,"numpy":np.__version__,"shapely":shapely.__version__,
            "geos":shapely.geos_version_string,"platform":platform.platform(),"processor":platform.processor(),
            "native_physics_runs":0,"time_qualification":"planning perf_counter compute only"})
        stream=io.StringIO()
        suite=unittest.defaultTestLoader.discover(str(ROOT/"tests"),pattern="test_p4_comparison_*.py")
        tests=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
        (out/"tests.log").write_text(stream.getvalue())
        save(out/"tests.json",{"tests":tests.testsRun,"passed":tests.wasSuccessful(),
            "failures":[{"test":str(t),"trace":s} for t,s in tests.failures],
            "errors":[{"test":str(t),"trace":s} for t,s in tests.errors]})
        print(stream.getvalue(),flush=True)
        model=PlanarModel()
        evidence=math_evidence(model);save(out/"math_evidence.json",evidence)
        if not tests.wasSuccessful() or not all(r[k]["valid"] for r in evidence["roots"].values() for k in ["start","goal"]):
            logger.finish(BenchmarkResult(args.run_id,"P4",ResultStatus.FAILURE,
                "initial fixed software/model gate failed; no comparison planning conducted",
                MeasurementQualification.SYNTHETIC,("tests.json","math_evidence.json"),("p4_three_v1",),
                tuple(s.source_id for s in sources),failure_stage="INITIAL_MATH_OR_ENDPOINT_GATE",
                reason="retain actual failure; do not alter endpoints or acceptance criteria"))
            return 1
        rows=[];raw_first={};repeats=[]
        def execute(env,budget,method,seed,repeat=False):
            result=plan(model,env,method,seed,budget,cfg["algorithm"])
            name=f"{env}_budget{budget}_{method}_seed{seed}"+("_repeat" if repeat else "")
            validation=validate_result(result,model)
            result["independent_validation"]=validation
            filename=name+".json.gz"
            with gzip.open(out/filename,"wt",encoding="utf-8") as f:
                json.dump(result,f,ensure_ascii=False,allow_nan=False)
            row={"environment":env,"budget":budget,"method":method,"seed":seed,"repeat":repeat,
                "status":result["status"],"wall_sec":result["compute_wall_time_sec"],"nodes":result["node_count"],
                "counters":result["counters"],"failure_counts":result["failure_counts"],
                "path_metrics":None if result["status"]!="SUCCESS" else {k:v for k,v in result["path_metrics"].items() if k!="state_qualifications"},
                "independent_validation":validation,"artifact":filename,
                "sha256":hashlib.sha256((out/filename).read_bytes()).hexdigest(),"terminal_reason":result["terminal_reason"]}
            print(json.dumps({k:row[k] for k in ["environment","budget","method","seed","repeat","status","wall_sec","nodes"]}),flush=True)
            if result["status"] in ["INTERNAL_ERROR","START_REJECTED","GOAL_REJECTED","PATH_RECHECK_REJECTED"]:
                save(out/"stopped_error.json",row)
                raise RuntimeError("stop for source/model qualification error; original evidence retained: "+result["terminal_reason"])
            return result,row
        for env in cfg["environments"]:
            for budget in cfg["outer_iteration_budgets"]:
                for index,seed in enumerate(cfg["seeds"]):
                    order=cfg["methods"][index%3:]+cfg["methods"][:index%3]
                    for method in order:
                        result,row=execute(env,budget,method,seed)
                        rows.append(row)
                        save(out/"trials_so_far.json",rows)
                        if env=="E0_sparse" and budget==200 and seed==7:raw_first[method]=result
        for method in cfg["methods"]:
            result,row=execute("E0_sparse",200,method,7,True)
            # Independent validation is untimed; strip only compute profiling.
            match=without_timing(result)==without_timing(raw_first[method])
            repeats.append({"method":method,"exact_nontiming_payload_match":match,
                "statuses":[raw_first[method]["status"],result["status"]],"artifact":row["artifact"]})
        assert len(rows)==cfg["statistical_trials"]
        summary={"trial_count":len(rows),"deterministic_repeats":repeats,"groups":[],
            "protected_files":len(before),"protected_files_unchanged":before==protected(),
            "physical_runs":0,"geometry_is_original_exact":False,
            "rss_registered_bridge_qualified":evidence["rss_registered_bridge"]["two_branch_bridge_qualified"],
            "overall_scope":"three-method same-model reconstruction; not full original-six-environment reproduction"}
        assert summary["protected_files_unchanged"]
        for env in cfg["environments"]:
            for budget in cfg["outer_iteration_budgets"]:
                for method in cfg["methods"]:
                    group=[r for r in rows if (r["environment"],r["budget"],r["method"])==(env,budget,method)]
                    success=[r for r in group if r["status"]=="SUCCESS"]
                    summary["groups"].append({"environment":env,"budget":budget,"method":method,
                        "trials":len(group),"success":len(success),"success_rate":len(success)/len(group),
                        "status_counts":dict(Counter(r["status"] for r in group)),
                        "wall_all_trials_mean":float(np.mean([r["wall_sec"] for r in group])),
                        "wall_success_mean":None if not success else float(np.mean([r["wall_sec"] for r in success])),
                        "nodes_mean":float(np.mean([r["nodes"] for r in group])),
                        "path_length_success_mean":None if not success else float(np.mean([r["path_metrics"]["joint_path_length_rad"] for r in success]))})
        save(out/"trials.json",rows);save(out/"summary.json",summary)
        with (out/"trials.csv").open("x",newline="") as f:
            names=["environment","budget","method","seed","status","wall_sec","nodes","path_length_rad","artifact","sha256"]
            w=csv.DictWriter(f,fieldnames=names,lineterminator="\n");w.writeheader()
            for r in rows:w.writerow({**{k:r[k] for k in names if k!="path_length_rad"},
                "path_length_rad":"" if r["path_metrics"] is None else r["path_metrics"]["joint_path_length_rad"]})
        complete=summary["rss_registered_bridge_qualified"] and all(r["exact_nontiming_payload_match"] for r in repeats)
        logger.finish(BenchmarkResult(args.run_id,"P4",ResultStatus.SUCCESS if complete else ResultStatus.INCOMPLETE,
            "bounded three-strategy reconstructed planar comparison; not original full-paper/robot benchmark",
            MeasurementQualification.SYNTHETIC,("tests.json","math_evidence.json","trials.json","summary.json"),
            ("p4_three_v1",),tuple(s.source_id for s in sources),
            failure_stage=None if complete else "BRIDGE_OR_DETERMINISM_EVIDENCE",
            reason=None if complete else "do not infer bridge or repeat equality without actual evidence",
            limitations=("original exact planar geometry not public","no continuous collision proof",
                "small fixed-seed sample not original500 trials","no physical execution")))
        print(json.dumps(summary,ensure_ascii=False),flush=True)
    return 0


if __name__=="__main__":sys.exit(main())
