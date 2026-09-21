"""
visualize.py
------------
Generates chart images from the analysis results:

    1. score_by_file.png  - horizontal bar chart of overall score per file
    2. metric_heatmap.png - heatmap of the 5 sub-metrics across all files
"""

import matplotlib
matplotlib.use("Agg")  # headless-safe backend
import matplotlib.pyplot as plt
import numpy as np


def plot_score_by_file(results, output_path):
    """results: list of (filename, overall_score, sub_scores_dict)."""
    if not results:
        return

    names = [n.split("/")[-1] for n, _, _ in results]
    scores = [s for _, s, _ in results]

    colors = ["#2ecc71" if s >= 80 else "#f1c40f" if s >= 60 else "#e74c3c" for s in scores]

    fig, ax = plt.subplots(figsize=(9, max(3, len(names) * 0.5)))
    y_pos = np.arange(len(names))
    ax.barh(y_pos, scores, color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names)
    ax.invert_yaxis()
    ax.set_xlabel("Readability Score (0-100)")
    ax.set_title("Code Readability Score by File")
    ax.set_xlim(0, 100)
    for i, s in enumerate(scores):
        ax.text(s + 1, i, f"{s:.1f}", va="center")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_metric_heatmap(results, output_path):
    """results: list of (filename, overall_score, sub_scores_dict)."""
    if not results:
        return

    metric_names = list(results[0][2].keys())
    file_names = [n.split("/")[-1] for n, _, _ in results]
    matrix = np.array([[r[2][m] for m in metric_names] for r in results])

    fig, ax = plt.subplots(figsize=(8, max(3, len(file_names) * 0.5)))
    im = ax.imshow(matrix, cmap="RdYlGn", vmin=0, vmax=100, aspect="auto")

    ax.set_xticks(np.arange(len(metric_names)))
    ax.set_xticklabels([m.replace("_", " ").title() for m in metric_names], rotation=30, ha="right")
    ax.set_yticks(np.arange(len(file_names)))
    ax.set_yticklabels(file_names)

    for i in range(len(file_names)):
        for j in range(len(metric_names)):
            ax.text(j, i, f"{matrix[i, j]:.0f}", ha="center", va="center", color="black", fontsize=8)

    ax.set_title("Readability Sub-Metric Heatmap")
    fig.colorbar(im, ax=ax, label="Score (0-100)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
