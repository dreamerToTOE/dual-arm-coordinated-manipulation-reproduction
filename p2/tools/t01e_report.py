#!/usr/bin/env python3
"""Render a human-readable summary of the frozen T01-E equivalence oracle."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "p2" / "tools"))
from p2_md_report import render                                    # noqa: E402

BASE = ROOT / "p2" / "reviews" / "t01e_baseline"


def main() -> int:
    index = json.loads((BASE / "index.json").read_text())
    cases = [json.loads(l) for l in (BASE / "cases.jsonl").read_text().splitlines() if l]
    selfcheck = json.loads((BASE / "selfcheck.json").read_text())

    numeric = [c for c in cases if c["kind"] != "invalid_input"]
    invalid = [c for c in cases if c["kind"] == "invalid_input"]

    rows = []
    for c in numeric:
        rows.append([c["id"], "/".join(c["modes"]), f"{c.get('tau_frobenius', 0):.2e}",
                     f"{sum(v * v for v in c['velocity'][:3]) ** 0.5:.2e}", c["W_rank"],
                     c.get("update_iterations", "-"), c["note"]])

    inv_rows = [[c["id"], c["rejected"], c["exception_type"], c["message"][:60]] for c in invalid]

    spec = {
        "title": "T01-E 优化前等价性基线（冻结）",
        "filename": "../T01_E_BASELINE_REPORT.md",
        "meta": {
            "冻结时间": index["date"],
            "代码版本": f"`{index['git_commit'][:12]}`",
            "种子": index["seed"],
            "夹具": f"{index['case_count']}（{len(numeric)} 数值 + {len(invalid)} 异常）",
            "数组": f"{len(index['array_keys'])}（`arrays.npz` {index['arrays_npz_sha256'][:12]}…）",
            "生成命令": f"`{index['command']}`",
            "耗时": f"{index['wall_s']:.2f} s",
            "自检": f"{selfcheck['verdict']}：{selfcheck['arrays_bitwise_equal']}/{selfcheck['arrays_compared']} 位相同",
        },
        "summary": (
            "本基线在任何优化之前冻结，用于 O1/O2 的逐元素等价性判定。"
            "它保存完整输入、状态、`f/A/F/Lw/Qd`、`P0/P_pred`、接触与 grasp-rate 数组、"
            "六类观测的 `H/z/residual`，以及一次完整更新的创新、迭代次数与后验协方差；"
            "不以范数或哈希代替矩阵比较。"
        ),
        "sections": [
            {"heading": "1. 数值夹具", "table": {
                "columns": ["ID", "模式", "‖τ‖ (Fro)", "‖v‖ (m/s)", "rank(W)", "更新迭代", "说明"],
                "rows": rows}},
            {"heading": "2. 异常输入夹具", "table": {
                "columns": ["ID", "被拒绝", "异常类型", "消息（截断）"], "rows": inv_rows},
                "paragraphs": [
                    "这些夹具保证优化后公共 API 仍然拒绝无效输入；消息必须逐字一致。",
                ]},
            {"heading": "3. 比较方法与判据", "paragraphs": [
                "`p2/tools/t01e_compare.py --baseline … --candidate … --output …` 逐数组输出 "
                "`max_abs`、`max_rel`、最大差异位置与是否位相同。",
                "严格项（无浮点重排）：位相同。其余：绝对/相对均 ≤1e-12。"
                "元数据（迭代次数、收敛、异常类型与消息、`rank(W)`）完全一致。",
                f"自检：同一代码生成两次，{selfcheck['arrays_bitwise_equal']}/{selfcheck['arrays_compared']} "
                f"数组位相同，失败 {len(selfcheck['failed_keys'])} 项，"
                f"最坏绝对差 {selfcheck['worst_abs']:.1e}。",
            ]},
            {"heading": "4. 哈希记录", "table": {
                "columns": ["对象", "SHA256（前 12 位）"],
                "rows": [[k, v[:12]] for k, v in sorted(index["source_sha256"].items())]
                        + [[k, v[:12]] for k, v in sorted(index["tool_sha256"].items())]
                        + [["arrays.npz", index["arrays_npz_sha256"][:12]]]}},
            {"heading": "5. 局限", "paragraphs": [
                "C08（近 π）有意落在 pad 域外，只用于 Jacobian/异常覆盖，不得进入控制实验。",
                "本基线只冻结**单步**算子与单次更新，不含时间积分；长时行为属 T03/T04。",
                "基线不是论文实验结果，不构成任何复现成功的证据。",
            ]},
        ],
    }
    path = render(spec, BASE)
    print("wrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
