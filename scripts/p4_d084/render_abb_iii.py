#!/usr/bin/env python3
"""Package saved ABB Environment III evidence and render a role-edge timeline.

This script reads only the saved CSV/provenance and copies existing D083
figures. It makes no planner, IK, collision, or qualification calls.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SCOPE = "RECONSTRUCTED_ALIGNED_DISCRETE_SOURCE_COLLISION_POLICY_ONLY"
SOURCE_CSV = ROOT / "results/20261022_D083_spatial_visualization01/III_PCS_saved_path.csv"
SOURCE_PROVENANCE = ROOT / "results/20261022_D083_spatial_visualization01/III_PCS_provenance_and_metrics.json"
CERTIFICATE = ROOT / "reports/P4_D080_ENV_III_RRT_PCS_PHYSICAL01_SAVED_INDEPENDENT_POST_20261018.json"
ASSET_ROOT = ROOT / "reports/p4_d083_spatial_assets_20261022"
ASSETS = [
    "fig_A2_environment_III_narrow_passage_v2.png",
    "fig_A2_environment_III_narrow_passage_v2.pdf",
    "fig_A3_environment_III_four_switch_frames.png",
    "fig_A3_environment_III_four_switch_frames.pdf",
    "fig_A4_environment_III_roles_and_evidence.png",
    "fig_A4_environment_III_roles_and_evidence.pdf",
    "fig_A5_spatial_saved_trajectories.png",
    "fig_A5_spatial_saved_trajectories.pdf",
    "environment_III_saved_states.gif",
]
CANONICAL_RENDERER = ROOT / "scripts/p4_d083/render_spatial.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text())


def read_csv(path: Path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def render_timeline(rows, provenance, output: Path):
    roles = provenance["active_roles"]
    switches = provenance["role_switches"]
    edge_x = np.arange(1, len(roles) + 1)
    edge_colors = ["#d8752d" if role == 0 else "#3e79ad" for role in roles]
    node_by_index = {int(row["traversal_index"]): int(row["source_node_id"]) for row in rows}
    mismatch = np.asarray([float(row["native_TCP_translation_mismatch_mm"]) for row in rows])
    switch_indices = [int(item["traversal_index"]) for item in switches]
    fig, (ax_role, ax_native) = plt.subplots(2, 1, figsize=(12.5, 6.8), gridspec_kw={"height_ratios": [1.2, 1.0]})
    ax_role.bar(edge_x, [role + 1 for role in roles], color=edge_colors, width=.88, edgecolor="white", linewidth=.6)
    ax_role.set_xlim(.35, len(roles) + .65); ax_role.set_ylim(.4, 2.6)
    ax_role.set_yticks([1, 2], ["A1 active", "A2 active"])
    ax_role.set_xticks(edge_x, [str(i) for i in edge_x])
    ax_role.set_xlabel("accepted solution edge (1-indexed)")
    ax_role.set_title("Environment III | active arm by accepted path edge", loc="left", fontsize=14, fontweight="bold")
    ax_role.grid(axis="y", alpha=.25)
    for item in switches:
        boundary = int(item["previous_edge_zero_based"]) + 1.5
        ax_role.axvline(boundary, color="#9b2c2c", linestyle="--", linewidth=1.2)
        ax_role.annotate(
            f"node {item['source_node_id']}\nA{item['from_active'] + 1}→A{item['to_active'] + 1}",
            xy=(boundary, 2.02 if item["to_active"] else 1.02), xytext=(boundary, 2.48),
            ha="center", va="bottom", fontsize=8, color="#842b2b",
            arrowprops={"arrowstyle": "-", "color": "#9b2c2c", "lw": .8},
        )
    ax_native.plot(np.arange(len(rows)), mismatch, color="#596775", linewidth=1.0)
    ax_native.scatter(np.arange(len(rows)), mismatch, s=4, color="#596775", alpha=.65)
    for item in switches:
        i = int(item["traversal_index"]); ax_native.axvline(i, color="#9b2c2c", linestyle="--", linewidth=1.0)
        ax_native.scatter([i], [mismatch[i]], color="#9b2c2c", s=24, zorder=4)
    ax_native.set_xlim(0, len(rows) - 1); ax_native.set_xlabel("saved traversal index / source node")
    ax_native.set_ylabel("native TCP mismatch / mm")
    ax_native.set_title("Switch nodes over the saved native-TCP mismatch trace", loc="left", fontsize=11)
    ax_native.grid(alpha=.22)
    fig.text(.015, .012, "Saved discrete evidence only; role changes describe edge ownership, not a continuous physical handoff. Native TCP and continuous CCD are not certified.", fontsize=8.5, color="#92444b")
    fig.subplots_adjust(left=.09, right=.98, bottom=.10, top=.92, hspace=.42)
    png = output / "fig_S2_abb_iii_role_timeline.png"; pdf = output / "fig_S2_abb_iii_role_timeline.pdf"
    fig.savefig(png, dpi=220, facecolor="white"); fig.savefig(pdf, facecolor="white"); plt.close(fig)
    return png, pdf, switch_indices, node_by_index


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "reports/p4_d084_abb_iii")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    output.mkdir(parents=True)
    rows = read_csv(SOURCE_CSV); provenance = read_json(SOURCE_PROVENANCE); certificate = read_json(CERTIFICATE)
    if len(rows) != 649 or provenance["node_count"] != 649 or provenance["source_edge_count"] != 14:
        raise SystemExit("saved ABB III counts do not match the frozen evidence")
    roles = provenance["active_roles"]
    if roles != [0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0]:
        raise SystemExit("unexpected role sequence")
    if len(provenance["role_switches"]) != 4:
        raise SystemExit("unexpected switch count")
    for name in ASSETS:
        shutil.copy2(ASSET_ROOT / name, output / name)
    png, pdf, switch_indices, node_by_index = render_timeline(rows, provenance, output)
    timeline_rows = []
    switches_by_edge = {int(s["next_edge_zero_based"]): s for s in provenance["role_switches"]}
    for i, role in enumerate(roles):
        item = switches_by_edge.get(i)
        timeline_rows.append({
            "edge_index_1based": i + 1, "active_arm": role + 1,
            "switch_at_edge_boundary": bool(item),
            "switch_source_node_id": item["source_node_id"] if item else "",
            "from_active_arm": item["from_active"] + 1 if item else "",
            "to_active_arm": item["to_active"] + 1 if item else "",
        })
    with (output / "role_timeline.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(timeline_rows[0]), lineterminator="\n"); writer.writeheader(); writer.writerows(timeline_rows)
    manifest = {
        "schema": "P4_D084_S2_ABB_III_ROLE_SWITCH_MANIFEST_V1",
        "status": "PASS_SAVED_PATH_ROLE_RENDER_ONLY",
        "environment": "III", "qualification_scope": SCOPE,
        "saved_node_count": len(rows), "saved_edge_count": len(roles), "milestone_count": provenance["milestones"],
        "active_roles": roles, "switch_count": len(provenance["role_switches"]),
        "switches": provenance["role_switches"], "switch_traversal_indices": switch_indices,
        "new_planner_calls": 0, "new_ik_calls": 0, "new_collision_calls": 0,
        "render_only_timeline_rows": len(rows),
        "source_sha256": {
            "saved_csv": sha(SOURCE_CSV), "provenance": sha(SOURCE_PROVENANCE),
            "certificate": sha(CERTIFICATE), "canonical_renderer": sha(CANONICAL_RENDERER),
            "s2_render_script": sha(ROOT / "scripts/p4_d084/render_abb_iii.py"),
        },
        "certificate": "reports/P4_D080_ENV_III_RRT_PCS_PHYSICAL01_SAVED_INDEPENDENT_POST_20261018.json",
        "certificate_sha256": sha(CERTIFICATE),
        "outputs_sha256": {name: sha(output / name) for name in ASSETS} | {
            "role_timeline_csv": sha(output / "role_timeline.csv"),
            "role_timeline_png": sha(png), "role_timeline_pdf": sha(pdf),
        },
        "metrics_inherited": {
            "maximum_saved_position_residual_mm": provenance["maximum_saved_position_residual_mm"],
            "maximum_saved_rotation_matrix_residual": provenance["maximum_saved_rotation_matrix_residual"],
            "aligned_pose_pass_nodes": provenance["aligned_pose_pass_nodes"],
            "native_pose_pass_nodes": provenance["native_pose_pass_nodes"],
            "maximum_native_tcp_position_mismatch_mm": provenance["maximum_native_tcp_position_mismatch_mm"],
            "maximum_native_tcp_rotation_matrix_mismatch": provenance["maximum_native_tcp_rotation_matrix_mismatch"],
        },
        "limitations": [
            "Role changes describe active/passive ownership of accepted discrete edges, not a continuous physical handoff.",
            "The source exact flag is not an independent certificate; the named saved certificate is the evidence boundary.",
            "Native TCP equivalence, continuous CCD, minimum clearance, omitted pairs, solid-rod safety, and dynamic execution are not certified.",
            "Four switches alone do not establish PCS superiority.",
        ],
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(output), "switch_count": 4, "new_science_calls": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
