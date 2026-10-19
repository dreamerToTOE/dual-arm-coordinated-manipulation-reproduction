#!/usr/bin/env python3
"""P2-native minimal Markdown + figure renderer.

Deliberately independent of P4 reporting code and of python-docx: the P2 branch
must be able to produce its own audit reports from JSON without importing any
P4 module. Markdown only; PDF/Word export is a T10 decision.

Usage
    from p2_md_report import render, bar_chart
    render(spec, out_dir)
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIGS = Path("figures")


def bar_chart(labels, values, path, title, ylabel, log=False, color="#4c72b0",
              colors=None):
    """Horizontal bar chart; labels stay ASCII to avoid missing CJK glyphs."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, max(2.4, 0.32 * len(labels))))
    y = range(len(labels))
    ax.barh(list(y), values, color=colors if colors else color)
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel(ylabel)
    ax.set_title(title)
    if log:
        ax.set_xscale("log")
    ax.grid(axis="x", alpha=0.3)
    for yi, v in zip(y, values):
        ax.text(v, yi, f" {v:.3g}", va="center", fontsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return path


def _table(columns, rows):
    out = ["| " + " | ".join(str(c) for c in columns) + " |",
           "|" + "|".join(["---"] * len(columns)) + "|"]
    for row in rows:
        out.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(out)


def render(spec, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = [f"# {spec['title']}", ""]
    for k, v in spec.get("meta", {}).items():
        lines.append(f"- **{k}**：{v}")
    lines.append("")
    if spec.get("summary"):
        lines += [spec["summary"], ""]
    for section in spec.get("sections", []):
        lines += [f"## {section['heading']}", ""]
        for para in section.get("paragraphs", []):
            lines += [para, ""]
        if section.get("table"):
            lines += [_table(section["table"]["columns"], section["table"]["rows"]), ""]
        fig = section.get("figure")
        if fig:
            rel = Path(fig["path"])
            lines += [f"![{fig.get('caption', 'figure')}]({rel.as_posix()})", "",
                      f"*{fig.get('caption', '')}*", ""]
    path = out_dir / spec.get("filename", "REPORT.md")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
