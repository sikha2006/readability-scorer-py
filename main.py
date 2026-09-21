"""
main.py
-------
Command-line entry point for the Code Readability Scorer.

Usage:
    python main.py <path_to_repo_or_folder>

Walks the given directory for .py files, scores each one, prints a
summary table to the console, writes a CSV of results, and generates
two chart images (bar chart + heatmap) into the `output/` folder.
"""

import sys
import os
import csv

from analyzer import analyze_file, find_python_files
from visualize import plot_score_by_file, plot_metric_heatmap


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_python_project>")
        sys.exit(1)

    target = sys.argv[1]
    if not os.path.isdir(target):
        print(f"Error: '{target}' is not a valid directory.")
        sys.exit(1)

    py_files = find_python_files(target)
    if not py_files:
        print("No Python files found.")
        sys.exit(0)

    results = []          # (filepath, overall_score, sub_scores)
    explanations_map = {}  # filepath -> list[str]

    print(f"\nAnalyzing {len(py_files)} Python file(s) in '{target}'...\n")
    print(f"{'File':<45}{'Score':>8}")
    print("-" * 53)

    for filepath in sorted(py_files):
        metrics = analyze_file(filepath)
        if metrics.error:
            print(f"{filepath:<45}{'ERROR':>8}  ({metrics.error})")
            continue
        score, sub_scores = metrics.overall_score()
        results.append((filepath, score, sub_scores))
        explanations_map[filepath] = metrics.explanations()
        rel = os.path.relpath(filepath, target)
        print(f"{rel:<45}{score:>8.1f}")

    if not results:
        print("\nNo files could be analyzed.")
        sys.exit(0)

    avg_score = sum(r[1] for r in results) / len(results)
    print("-" * 53)
    print(f"{'AVERAGE':<45}{avg_score:>8.1f}\n")

    os.makedirs("output", exist_ok=True)

    # CSV report
    csv_path = os.path.join("output", "readability_report.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        header = ["file", "overall_score"] + list(results[0][2].keys()) + ["notes"]
        writer.writerow(header)
        for filepath, score, sub_scores in results:
            row = [os.path.relpath(filepath, target), score] + list(sub_scores.values())
            row.append(" | ".join(explanations_map[filepath]))
            writer.writerow(row)
    print(f"CSV report written to: {csv_path}")

    # Text explanations
    txt_path = os.path.join("output", "readability_notes.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        for filepath, score, _ in results:
            rel = os.path.relpath(filepath, target)
            f.write(f"{rel}  (score: {score:.1f})\n")
            for note in explanations_map[filepath]:
                f.write(f"  - {note}\n")
            f.write("\n")
    print(f"Explanations written to: {txt_path}")

    # Charts
    display_results = [(os.path.relpath(fp, target), s, sub) for fp, s, sub in results]
    plot_score_by_file(display_results, os.path.join("output", "score_by_file.png"))
    plot_metric_heatmap(display_results, os.path.join("output", "metric_heatmap.png"))
    print("Charts written to: output/score_by_file.png, output/metric_heatmap.png\n")


if __name__ == "__main__":
    main()
