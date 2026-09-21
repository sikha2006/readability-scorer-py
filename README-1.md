# Code Readability Scorer

A lightweight Python tool that scans a Python codebase and scores each file
on **readability** — how easy the code is for a human to read and maintain —
using the built-in `ast` module (no external code-quality service required).

It outputs:
- A console summary table
- A CSV report (`output/readability_report.csv`)
- A plain-language notes file explaining *why* each file scored the way it
  did (`output/readability_notes.txt`)
- Two charts: a per-file score bar chart and a sub-metric heatmap

## Why this project

Most "code quality" tools (SonarQube, Pylint, flake8, etc.) are built for
enterprise CI pipelines: heavy setup, config files, and dashboards that
report style/bug issues rather than plain-language readability. This
project is intentionally the opposite:

| | Code Readability Scorer | SonarQube / Pylint |
|---|---|---|
| Setup | Single command, zero config | Server / config files |
| Output | Plain-language explanations | Rule codes / warnings |
| Focus | Human readability specifically | Bugs, style, security, etc. |
| Audience | Students, solo devs, small repos | Enterprise teams / CI |
| Transparency | Scoring formula fully visible in `analyzer.py` | Mostly black-box rules |

It's designed to be simple enough to explain end-to-end in a report, while
still producing genuinely useful, visual output.

## How scoring works

Each file is parsed with Python's `ast` module (no regex-guessing at code
structure) and scored on 5 metrics, each normalized to 0–100:

| Metric | What it measures | Weight |
|---|---|---|
| Comment density | Ratio of comment lines to code lines (ideal ~18%) | 15% |
| Function length | Average lines per function (shorter = better) | 25% |
| Variable naming | % of names following `snake_case` | 20% |
| Nesting depth | Deepest nested block (if/for/while/try) | 20% |
| Docstring coverage | % of functions/classes with docstrings | 20% |

The weighted average becomes the file's overall **Readability Score**.
Weights are plain constants in `analyzer.py` (`WEIGHTS` dict) — easy to
tune or justify in a report.

## Usage

```bash
pip install -r requirements.txt
python main.py <path_to_python_project>
```

Example (using the included demo folder):

```bash
python main.py sample_project
```

This analyzes `sample_project/clean_example.py` (well-documented, simple
functions) against `sample_project/messy_example.py` (deeply nested,
uncommented, poorly named) — a clear before/after demonstration of the
scoring logic.

## Project structure

```
code-readability-scorer/
├── analyzer.py        # Core metric-computation engine (ast-based)
├── visualize.py        # Chart generation (matplotlib)
├── main.py              # CLI entry point
├── sample_project/      # Demo files (clean vs. messy) for testing
├── requirements.txt
└── output/              # Generated on run: CSV, notes, charts
```

## Possible extensions

- Cyclomatic complexity (branch counting) as a 6th metric
- HTML report instead of / in addition to CSV
- GitHub Action that runs the scorer on every PR and comments the score
- Support for analyzing a live GitHub repo URL directly (clone + scan)

## Author's note

This tool intentionally favors **explainability over completeness** — it
would rather clearly justify a lower score with plain-language reasoning
than silently produce a number nobody can interpret.
