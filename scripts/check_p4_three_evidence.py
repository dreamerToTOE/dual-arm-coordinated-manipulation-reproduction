#!/usr/bin/env python3
"""Read-only saved-evidence audit; never imports any planner or simulator."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/"results/20261013_P4_three_methods_round3"


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix==".gz" else raw)


def untimed(x):
    if isinstance(x,dict):return {k:untimed(v) for k,v in x.items() if k!="compute_wall_time_sec"}
    if isinstance(x,list):return [untimed(v) for v in x]
    return x


def main():
    trials,summary=read(RUN/"trials.json"),read(RUN/"summary.json")
    assert len(trials)==60 and len({(r["environment"],r["budget"],r["method"],r["seed"]) for r in trials})==60
    protected=read(RUN/"protected_sha256.json")
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in protected.items())
    source=read(RUN/"source_sha256.json")
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in source.items())
    exact={};switches=Counter();path_partitions=Counter();extrema={};raw_hashes={}
    for row in trials:
        p=RUN/row["artifact"]
        raw_hashes[row["artifact"]]=hashlib.sha256(p.read_bytes()).hexdigest()
        assert raw_hashes[row["artifact"]]==row["sha256"]
        raw=read(p)
        for name,key in [("status","status"),("nodes","node_count"),("counters","counters"),("failure_counts","failure_counts"),("wall_sec","compute_wall_time_sec")]:
            assert row[name]==raw[key]
        assert raw["seed"]==row["seed"] and raw["environment"]==row["environment"] and raw["method"]==row["method"]
        if raw["status"]=="SUCCESS":
            assert raw["path"][0]==raw["start"] and raw["path"][-1]==raw["goal"]
            assert row["independent_validation"]["status"]=="PASS"
            assert len(raw["path"])==raw["path_metrics"]["point_count"]
            assert row["path_metrics"]=={k:v for k,v in raw["path_metrics"].items() if k!="state_qualifications"}
            for state in raw["path_metrics"]["state_qualifications"]:
                assert state["valid"] and state["joint_margin"]>=0 and not state["collision"]["collision"]
                assert state["closure_position"]<=1e-8 and state["closure_angle"]<=1e-8
            for edge in raw["path_edges"]:
                a=raw["attempts"][edge["attempt_index"]]
                assert a["accepted"] and a["connection"]["success"]
                assert a["connection"]["partition"]==edge["partition"]
                path_partitions[(raw["method"],str(edge["partition"]))]+=1
            m=raw["path_metrics"]
            info=extrema.setdefault(raw["method"],{"max_position_residual_m":0.,"max_rotation_residual_rad":0.,
                "min_joint_margin_rad":float("inf"),"min_clearance_m":float("inf"),"qualified_path_points":0})
            info["max_position_residual_m"]=max(info["max_position_residual_m"],m["maximum_position_residual_m"])
            info["max_rotation_residual_rad"]=max(info["max_rotation_residual_rad"],m["maximum_rotation_residual_rad"])
            info["min_joint_margin_rad"]=min(info["min_joint_margin_rad"],m["minimum_joint_margin_rad"])
            info["min_clearance_m"]=min(info["min_clearance_m"],m["minimum_clearance_m"])
            info["qualified_path_points"]+=m["point_count"]
        else:assert raw["path"]==[] and row["path_metrics"] is None
        if raw["method"]=="PCS":
            for tree in raw["trees"].values():
                for node in tree:
                    if node["parent"] is None:continue
                    incoming=node["incoming_attempt"]
                    parent=tree[node["parent"]]
                    if parent["incoming_attempt"] is None:continue
                    before=raw["attempts"][parent["incoming_attempt"]]["edge_partition"]
                    after=raw["attempts"][incoming]["edge_partition"]
                    if before!=after:switches[f"{before}->{after}"]+=1
        if row["environment"]=="E0_sparse" and row["budget"]==200 and row["seed"]==7:
            exact[row["method"]]=raw
    repeats=[]
    for item in summary["deterministic_repeats"]:
        p=RUN/item["artifact"];raw_hashes[item["artifact"]]=hashlib.sha256(p.read_bytes()).hexdigest()
        repeated=read(p);original=exact[item["method"]]
        same=untimed(original)==untimed(repeated)
        assert same==item["exact_nontiming_payload_match"]
        prefix=0
        for a,b in zip(original["attempts"],repeated["attempts"]):
            if untimed(a)!=untimed(b):break
            prefix+=1
        repeats.append({**item,"identical_attempt_prefix":prefix,
            "attempt_counts":[len(original["attempts"]),len(repeated["attempts"])],
            "qualification":"PASS" if same else "FIXED_DEADLINE_FULL_PAYLOAD_DIFFERENCE_RETAINED"})
    counts={m:dict(Counter(r["status"] for r in trials if r["method"]==m)) for m in ["RSS","PCS","NR"]}
    assert counts=={"RSS":{"TIME_LIMIT":20},"PCS":{"SUCCESS":20},"NR":{"SUCCESS":20}}
    check={"passed_saved_evidence_audit":True,"statistical_trials":60,"raw_artifacts":len(raw_hashes),
        "protected_original_files":len(protected),"original_files_unchanged":True,"source_hashes_unchanged":True,
        "status_counts":counts,"qualified_path_extrema":extrema,"pcs_tree_partition_transitions":dict(switches),
        "solution_edge_partitions":{str(k):v for k,v in path_partitions.items()},"repeat_evidence":repeats,
        "rss_bridge":read(RUN/"math_evidence.json")["rss_registered_bridge"]["two_branch_bridge_qualified"],
        "raw_sha256":raw_hashes,"new_planning_calls":0,"physical_runs":0,
        "scientific_protocol_overall":"PARTIAL: RSS no global path, RSS repeat full payload mismatch, exact original environment unavailable"}
    out=ROOT/"reports/P4_THREE_METHOD_EVIDENCE_QA.json"
    out.write_text(json.dumps(check,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:v for k,v in check.items() if k!="raw_sha256"},ensure_ascii=False,indent=2))


if __name__=="__main__":main()
