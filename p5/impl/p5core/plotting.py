"""Thin matplotlib helpers so every task saves figures the same way."""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def save(fig, rec, name):
    os.makedirs(rec.figures_dir, exist_ok=True)
    path = os.path.join(rec.figures_dir, name)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
    rec.figure(name, path)
    return path
