#!/usr/bin/env python3
"""Render previously saved ABB Environment II paths; never plan or qualify.

The four inputs are frozen D080/D082 saved node queues.  This script reads
their saved poses and certificates, computes only display mesh frames for the
three selected snapshots per path, and writes a provenance manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SCOPE = "RECONSTRUCTED_ALIGNED_DISCRETE_SOURCE_COLLISION_POLICY_ONLY"
MESH_NAMES = [
    "Base_r.tris", "Link1_r.tris", "Link2_r.tris", "Link3_r.tris",
    "Link4_r.tris", "Link5_r.tris", "Link6.tris", "EE_r.tris",
    "table.tris", "obs.tris",
]
MESH_SHA256 = {
    "Base_r.tris": "eee302c275cf58a88e0a64206f25867202a717261bf04d072d668cf3603d5085",
    "Link1_r.tris": "f3ec4f811dfc1ef33e4703e82c350d9d99fd01474fbb81125b930d1ee8c7bff8",
    "Link2_r.tris": "5e9da2c8ddcc4bf549dd675626fdca629146d120be381c7178dd73e4107f1747",
    "Link3_r.tris": "bee15986ab5fe4064c5b97ab0109d88b2a1981b3a765ecd8c99210c96793b954",
    "Link4_r.tris": "c0b04b1c8f8dd3234d73d027c1e8f77392d28d7caba1c11c621c03ae185f5859",
    "Link5_r.tris": "8a734337bc601235fb80062fdc3674b6dc996d3e318ec7ded3474363995577a2",
    "Link6.tris": "74cf29a9e69615f49324e11ce4c93e436c996210da4851771858f96113f545ec",
    "EE_r.tris": "b6e2b7af54d6e2d90dde325f3d52b680abff884d6f31e0fbc7b25eec132c87ca",
    "table.tris": "756597cb4dbf32b731375844be6adf94d1d77e57775f4506cf31442723fc1bce",
    "obs.tris": "76b04d378e0084c19ff31957f0c9425eae6056622fd88300ac0a8a651fbd93b8",
}
PATHS = [
    {
        "key": "RRT_PCS",
        "label": "RRT / PCS",
        "family": "PCS",
        "run": "results/p4_full/20261015_R2_ABB_RRT_PATH01",
        "config": "configs/p4_full/r2_abb_rrt_path_qualification_v1.json",
        "certificate": "reports/P4_FULL_R2_ABB_RRT_PATH_INDEPENDENT_SAVED_POST_REVIEW_20261015.json",
    },
    {
        "key": "CBIRRT_PCS",
        "label": "CBiRRT / PCS",
        "family": "PCS",
        "run": "results/p4_full/20261015_R2_ABB_CBIRRT_D_PATH01",
        "config": "configs/p4_full/r2_abb_cbirrt_d_complete_path_v1.json",
        "certificate": "reports/P4_FULL_R2_ABB_CBIRRT_D_PATH01_SAVED_INDEPENDENT_POST_20261016.json",
    },
    {
        "key": "RRT_NR",
        "label": "RRT / NR",
        "family": "NR",
        "run": "results/p4_full/20261015_R2_ABB_RRT_NR_PATH01",
        "config": "configs/p4_full/r2_abb_rrt_nr_path_qualification_v1.json",
        "certificate": "reports/P4_FULL_R2_ABB_RRT_NR_PATH_ROOT_INDEPENDENT_POST_20261016.json",
    },
    {
        "key": "CBIRRT_NR",
        "label": "CBiRRT / NR",
        "family": "NR",
        "run": "results/p4_full/20261016_R2_ABB_CBIRRT_NR_PATH01",
        "config": "configs/p4_full/r2_abb_cbirrt_nr_full_path_v1.json",
        "certificate": "reports/P4_FULL_R2_ABB_CBIRRT_NR_PATH01_SAVED_INDEPENDENT_POST_20261017.json",
    },
]
ARM_COLORS = ["#d8752d", "#3e79ad"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    return json.loads(path.read_text())


def rot(axis: str, angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    if axis == "x":
        return np.array([[1., 0, 0], [0, c, -s], [0, s, c]])
    if axis == "y":
        return np.array([[c, 0, s], [0, 1., 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.]])


def mesh_frames(q: list[float], arm: int):
    """The same aligned source CAD-frame convention as render_spatial.py."""
    distance = 900.
    r = (rot("z", math.pi / 2) @ rot("z", math.pi / 2)) if arm else np.eye(3)
    p = np.array([(-1 if arm == 0 else 1) * distance / 2, 0., 0.])
    frames = [(r.copy(), p.copy())]
    p = p + r @ np.array([0., 0., 290.])
    offsets = [(0, 0, 0), (0, 0, 270), (134, 0, 70), (168, 0, 0), (66, 0, 0), (66, 0, 0)]
    for angle, axis, offset in zip(q, ["z", "y", "y", "x", "y", "x"], offsets):
        r = r @ rot(axis, float(angle))
        frames.append((r.copy(), p.copy()))
        p = p + r @ np.asarray(offset)
    frames.append((r.copy(), p.copy()))
    return frames


def transformed(tris: np.ndarray, r: np.ndarray, p: np.ndarray):
    return (tris @ r.T + p) / 1000.


def draw_tri(ax, tris, r, p, color, alpha=1., edge=False):
    ax.add_collection3d(Poly3DCollection(
        transformed(tris, r, p), facecolor=color,
        edgecolor=("#75828c" if edge else "none"), linewidth=.15,
        alpha=alpha, zsort="average"))


def setup_ax(ax):
    ax.set_xlim(-.92, .92); ax.set_ylim(-.66, .66); ax.set_zlim(-.03, .97)
    ax.set_box_aspect((1.84, 1.32, 1.0)); ax.view_init(elev=22, azim=-58)
    ax.set_xlabel("x / m", labelpad=-2); ax.set_ylabel("y / m", labelpad=-2); ax.set_zlabel("z / m", labelpad=-3)
    ax.tick_params(labelsize=7, pad=0)
    for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
        axis.pane.set_facecolor((.98, .985, .99, 1)); axis._axinfo["grid"]["color"] = (.85, .88, .91, .65)


def load_meshes(mesh_root: Path):
    meshes = {}
    for name in MESH_NAMES:
        path = mesh_root / name
        if sha(path) != MESH_SHA256[name]:
            raise ValueError(f"private mesh SHA mismatch: {path}")
        values = np.fromstring(path.read_text(), sep=" ")
        if len(values) != 1 + int(values[0]) * 9:
            raise ValueError(f"invalid mesh record: {path}")
        meshes[name] = values[1:].reshape(-1, 3, 3)
    return meshes


def load_path(spec):
    run = ROOT / spec["run"]
    config_path = ROOT / spec["config"]
    cert_path = ROOT / spec["certificate"]
    config = read(config_path); cert = read(cert_path); queue = config["fixed_queue"]
    summary = cert.get("summary", cert)
    normalized = {
        "nodes": summary.get("nodes", summary.get("unique_nodes", cert.get("nodes"))),
        "edges": summary.get("edges", summary.get("reconstruction_edges", cert.get("edges"))),
        "leaves": summary.get("leaves", summary.get("full_dense_leaf_count", cert.get("leaves"))),
        "maximum_full12_leaf_rad": summary.get("max_leaf_rad", summary.get("max_leaf_full12_L2_rad", cert.get("maximum_full12_leaf_rad"))),
        "maximum_saved_closure_position_mm": summary.get("max_saved_pose_closure_position_mm", cert.get("maximum_saved_closure_position_mm")),
        "maximum_saved_closure_rotation": summary.get("max_saved_pose_closure_rotation", summary.get("max_saved_pose_closure_rotation_matrix", cert.get("maximum_saved_closure_rotation"))),
        "minimum_source_mechanical_margin_rad": summary.get("minimum_mechanical_limit_margin_rad", summary.get("min_original_mechanical_limit_margin_rad", cert.get("minimum_source_mechanical_margin_rad"))),
        "native_collision_nodes": summary.get("native_collision_nodes", cert.get("native_collision_nodes")),
        "aligned_collision_nodes": summary.get("aligned_collision_nodes", cert.get("aligned_collision_nodes")),
        "continuous_collision_certificate": bool(cert.get("continuous_collision_certificate", False)),
    }
    if normalized["nodes"] is None or normalized["edges"] is None:
        raise ValueError(f"certificate does not expose node/edge counts: {cert_path}")
    if normalized["leaves"] is None:
        normalized["leaves"] = normalized["nodes"] - 1
    raw_nodes = queue["nodes"]
    q_nodes = [n["q12"] if isinstance(n, dict) else n for n in raw_nodes]
    order = []
    for edge in queue["edges"]:
        ids = edge["node_ids"]
        if order:
            if ids[0] != order[-1]:
                raise ValueError(f"disconnected edge queue in {spec['key']}")
            order.extend(ids[1:])
        else:
            order.extend(ids)
    if len(q_nodes) != normalized["nodes"] or len(order) != normalized["nodes"]:
        raise ValueError(f"node count mismatch in {spec['key']}")
    nodes = []
    for index in range(len(q_nodes)):
        node_path = run / f"node_{index:05d}.json"
        node = read(node_path)
        if node["q12"] != q_nodes[index]:
            raise ValueError(f"queue/node mismatch in {node_path}")
        nodes.append({"q": node["q12"], "poses": np.asarray(node["poses"], dtype=float), "node_id": index})
    ordered = [nodes[index] for index in order]
    return {
        **spec,
        "run_path": run,
        "config_path": config_path,
        "certificate_path": cert_path,
        "config_data": config,
        "certificate_data": cert,
        "normalized": normalized,
        "nodes": nodes,
        "ordered": ordered,
        "order": order,
    }


def draw_scene(ax, path, index, meshes):
    record = path["ordered"][index]
    poses = np.asarray([node["poses"] for node in path["ordered"]])
    for arm in range(2):
        tcp = poses[:, arm, :3, 3] / 1000.
        ax.plot(*tcp.T, color=ARM_COLORS[arm], lw=1.15, alpha=.78)
        ax.scatter(*tcp[0], c="#27874e", marker="o", s=18, depthshade=False)
        ax.scatter(*tcp[-1], c="#a52b39", marker="*", s=36, depthshade=False)
    q = record["q"]
    for arm in range(2):
        frames = mesh_frames(q[6 * arm:6 * arm + 6], arm)
        for name, (r, p) in zip(MESH_NAMES[:8], frames):
            draw_tri(ax, meshes[name], r, p, ARM_COLORS[arm], .22)
    draw_tri(ax, meshes["table.tris"], np.eye(3), np.array([-450., 0., 0.]), "#cbd2d9", .08)
    for dx, dy in [(0, 0), (250, 250), (-250, -250)]:
        draw_tri(ax, meshes["obs.tris"], np.eye(3), np.array([dx, dy, 0.]), "#7f8992", .15, True)
    rod = np.stack([record["poses"][0, :3, 3], record["poses"][1, :3, 3]]) / 1000.
    ax.plot(*rod.T, color="#243d49", lw=3.0, solid_capstyle="round", zorder=20)
    ax.scatter(*rod.T, c="#243d49", s=10, depthshade=False)
    setup_ax(ax)


def render(paths, meshes, output: Path):
    output.mkdir(parents=True, exist_ok=False)
    fig = plt.figure(figsize=(15.4, 14.0))
    fig.suptitle("Environment II | four saved dual-ABB trajectories", x=.035, ha="left", fontsize=17, fontweight="bold", y=.994)
    fig.text(.035, .962, "Start, saved midpoint, and goal snapshots from previously qualified discrete node records.", fontsize=10.5, color="#53616e")
    render_fk_calls = 0
    for row, path in enumerate(paths):
        n = len(path["ordered"]); indices = [0, n // 2, n - 1]
        for col, index in enumerate(indices):
            ax = fig.add_subplot(4, 3, row * 3 + col + 1, projection="3d")
            draw_scene(ax, path, index, meshes); render_fk_calls += 2
            phase = "start" if col == 0 else "goal" if col == 2 else "saved midpoint"
            ax.set_title(f"{path['label']} | {phase} | {index + 1}/{n}", fontsize=9.5, pad=0)
    fig.text(.035, .032, "Orange/blue: arm TCP traces; green circle/start and red star/goal; dark bar: object.", fontsize=9.5)
    fig.text(.035, .015, "Source CAD surfaces and aligned frames. Discrete source collision policy only; no native TCP or continuous CCD certificate.", fontsize=8.5, color="#92444b")
    fig.subplots_adjust(left=.005, right=.99, bottom=.055, top=.935, wspace=-.02, hspace=.12)
    png = output / "fig_S1_abb_ii_four_saved_paths.png"; pdf = output / "fig_S1_abb_ii_four_saved_paths.pdf"
    fig.savefig(png, dpi=220, facecolor="white"); fig.savefig(pdf, facecolor="white"); plt.close(fig)

    metric_rows = []
    for path in paths:
        cert = path["certificate_data"]
        norm = path["normalized"]
        metric_rows.append({
            "key": path["key"], "label": path["label"], "family": path["family"],
            "node_count": norm["nodes"], "leaf_count": norm["leaves"], "edge_count": norm["edges"],
            "max_leaf_l2_rad": norm["maximum_full12_leaf_rad"],
            "max_saved_closure_position_mm": norm["maximum_saved_closure_position_mm"],
            "max_saved_closure_rotation": norm["maximum_saved_closure_rotation"],
            "min_source_mechanical_margin_rad": norm["minimum_source_mechanical_margin_rad"],
            "native_collision_nodes": norm["native_collision_nodes"],
            "aligned_collision_nodes": norm["aligned_collision_nodes"],
            "certificate": path["certificate"], "certificate_sha256": sha(path["certificate_path"]),
            "execution": cert.get("execution", path["run"] + "/execution.json"),
            "execution_sha256": cert.get("execution_sha256"),
            "continuous_collision_certificate": norm["continuous_collision_certificate"],
        })
    (output / "abb_ii_metrics.json").write_text(json.dumps({"schema": "P4_D084_S1_ABB_II_METRICS_V1", "scope": SCOPE, "rows": metric_rows}, ensure_ascii=False, indent=2) + "\n")
    source_hashes = {
        "canonical_render_script": sha(ROOT / "scripts/p4_d083/render_spatial.py"),
        "s1_render_script": sha(ROOT / "scripts/p4_d084/render_abb_ii.py"),
    }
    for path in paths:
        source_hashes[path["config"]] = sha(path["config_path"])
        source_hashes[path["certificate"]] = sha(path["certificate_path"])
        for index in [0, len(path["nodes"]) // 2, len(path["nodes"]) - 1]:
            node_path = path["run_path"] / f"node_{index:05d}.json"
            source_hashes[str(node_path.relative_to(ROOT))] = sha(node_path)
    source_hashes["mesh_root_sha256"] = {name: MESH_SHA256[name] for name in MESH_NAMES}
    manifest = {
        "schema": "P4_D084_S1_ABB_II_RECOVERY_MANIFEST_V1",
        "status": "PASS_SAVED_PATH_RENDER_ONLY",
        "environment": "II",
        "qualification_scope": SCOPE,
        "new_planner_calls": 0,
        "new_ik_calls": 0,
        "new_collision_calls": 0,
        "render_fk_arm_calls": render_fk_calls,
        "paths": [{"key": p["key"], "label": p["label"], "node_count": len(p["nodes"]), "certificate": p["certificate"], "run": p["run"]} for p in paths],
        "input_sha256": source_hashes,
        "outputs_sha256": {"png": sha(png), "pdf": sha(pdf), "metrics": sha(output / "abb_ii_metrics.json")},
        "limitations": [
            "Snapshots and TCP traces come from saved discrete nodes; the rod is a display glyph.",
            "Aligned source collision-policy evidence is inherited from the named certificates.",
            "Native TCP equivalence, continuous CCD, minimum clearance, omitted pairs, and dynamic execution are not certified.",
            "This package adds no planner, IK, collision, or path qualification call.",
        ],
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mesh-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "reports/p4_d084_abb_ii")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {output}")
    meshes = load_meshes(args.mesh_root)
    paths = [load_path(spec) for spec in PATHS]
    render(paths, meshes, output)
    print(json.dumps({"output": str(output), "paths": [p["key"] for p in paths], "new_science_calls": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
