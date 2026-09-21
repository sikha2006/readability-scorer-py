"""
analyzer.py
------------
Core engine for the Code Readability Scorer.

Parses Python source files using the built-in `ast` module and computes
a set of readability metrics for each file:

    1. Comment density      - ratio of comment lines to code lines
    2. Avg function length  - average number of lines per function
    3. Avg variable name len- average length of variable/parameter names
    4. Max nesting depth    - deepest level of nested blocks (if/for/while/etc.)
    5. Naming convention    - % of functions/variables following snake_case
    6. Docstring coverage   - % of functions/classes that have a docstring

Each metric is normalized to a 0-100 scale and combined into a single
weighted "Readability Score". The engine also returns human-readable
explanations for why a file scored the way it did (explainability was
a deliberate design goal — see README.md).
"""

import ast
import re
import os


SNAKE_CASE_RE = re.compile(r"^[a-z_][a-z0-9_]*$")

# Weights used to combine individual metrics into the final score.
# These are intentionally exposed as constants so they're easy to tune.
WEIGHTS = {
    "comment_density": 0.15,
    "function_length": 0.25,
    "variable_naming": 0.20,
    "nesting_depth": 0.20,
    "docstring_coverage": 0.20,
}


class FileMetrics:
    """Container for the computed metrics of a single file."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.total_lines = 0
        self.code_lines = 0
        self.comment_lines = 0
        self.function_lengths = []
        self.variable_name_lengths = []
        self.max_nesting_depth = 0
        self.naming_conforming = 0
        self.naming_total = 0
        self.docstring_present = 0
        self.docstring_total = 0
        self.error = None

    # ---- normalized sub-scores (0-100, higher = better) ----

    def comment_density_score(self):
        if self.code_lines == 0:
            return 0
        ratio = self.comment_lines / self.code_lines
        # Sweet spot ~10-25% comments. Too little or too much both penalized.
        ideal = 0.18
        score = 100 - min(100, abs(ratio - ideal) / ideal * 100)
        return max(0, round(score, 1))

    def function_length_score(self):
        if not self.function_lengths:
            return 100.0  # no functions to penalize
        avg = sum(self.function_lengths) / len(self.function_lengths)
        # Functions under 20 lines score well; longer functions decay.
        if avg <= 20:
            return 100.0
        score = max(0, 100 - (avg - 20) * 2)
        return round(score, 1)

    def variable_naming_score(self):
        if self.naming_total == 0:
            return 100.0
        return round(100 * self.naming_conforming / self.naming_total, 1)

    def nesting_depth_score(self):
        # Depth of 1-2 is fine, penalize heavily beyond 4
        if self.max_nesting_depth <= 2:
            return 100.0
        score = max(0, 100 - (self.max_nesting_depth - 2) * 20)
        return round(score, 1)

    def docstring_coverage_score(self):
        if self.docstring_total == 0:
            return 100.0
        return round(100 * self.docstring_present / self.docstring_total, 1)

    def overall_score(self):
        scores = {
            "comment_density": self.comment_density_score(),
            "function_length": self.function_length_score(),
            "variable_naming": self.variable_naming_score(),
            "nesting_depth": self.nesting_depth_score(),
            "docstring_coverage": self.docstring_coverage_score(),
        }
        total = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)
        return round(total, 1), scores

    def explanations(self):
        """Return plain-language reasons behind the score (explainability)."""
        notes = []
        cd = self.comment_density_score()
        if cd < 60:
            ratio = (self.comment_lines / self.code_lines * 100) if self.code_lines else 0
            notes.append(f"Comment density is {ratio:.1f}% — aim for ~15-20% for good balance.")

        fl = self.function_length_score()
        if fl < 70 and self.function_lengths:
            avg = sum(self.function_lengths) / len(self.function_lengths)
            notes.append(f"Average function length is {avg:.1f} lines — consider splitting long functions.")

        vn = self.variable_naming_score()
        if vn < 80 and self.naming_total:
            notes.append(f"Only {vn:.0f}% of names follow snake_case convention.")

        nd = self.nesting_depth_score()
        if nd < 80:
            notes.append(f"Max nesting depth is {self.max_nesting_depth} — deeply nested code is harder to follow.")

        ds = self.docstring_coverage_score()
        if ds < 60 and self.docstring_total:
            notes.append(f"Only {ds:.0f}% of functions/classes have docstrings.")

        if not notes:
            notes.append("No major readability issues detected. Nice work!")
        return notes


def _max_depth(node, current=0):
    """Recursively compute the deepest nested block inside a function."""
    depth = current
    nesting_nodes = (ast.If, ast.For, ast.While, ast.With, ast.Try)
    for child in ast.iter_child_nodes(node):
        if isinstance(child, nesting_nodes):
            depth = max(depth, _max_depth(child, current + 1))
        else:
            depth = max(depth, _max_depth(child, current))
    return depth


def analyze_file(filepath):
    """Analyze a single .py file and return a populated FileMetrics object."""
    metrics = FileMetrics(filepath)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        metrics.error = str(e)
        return metrics

    lines = source.splitlines()
    metrics.total_lines = len(lines)
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            metrics.comment_lines += 1
        else:
            metrics.code_lines += 1

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as e:
        metrics.error = f"SyntaxError: {e}"
        return metrics

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # function length
            if hasattr(node, "end_lineno") and node.end_lineno:
                length = node.end_lineno - node.lineno + 1
                metrics.function_lengths.append(length)

            # naming convention for function name
            metrics.naming_total += 1
            if SNAKE_CASE_RE.match(node.name):
                metrics.naming_conforming += 1

            # parameter naming
            for arg in node.args.args:
                metrics.naming_total += 1
                metrics.variable_name_lengths.append(len(arg.arg))
                if SNAKE_CASE_RE.match(arg.arg) or arg.arg == "self":
                    metrics.naming_conforming += 1

            # docstring coverage
            metrics.docstring_total += 1
            if ast.get_docstring(node):
                metrics.docstring_present += 1

            # nesting depth within this function
            metrics.max_nesting_depth = max(metrics.max_nesting_depth, _max_depth(node))

        elif isinstance(node, ast.ClassDef):
            metrics.docstring_total += 1
            if ast.get_docstring(node):
                metrics.docstring_present += 1

        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    metrics.naming_total += 1
                    metrics.variable_name_lengths.append(len(target.id))
                    if SNAKE_CASE_RE.match(target.id):
                        metrics.naming_conforming += 1

    return metrics


def find_python_files(root):
    """Recursively find all .py files under `root`, skipping common noise dirs."""
    skip_dirs = {".git", "__pycache__", "venv", ".venv", "node_modules", "output"}
    py_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fname in filenames:
            if fname.endswith(".py"):
                py_files.append(os.path.join(dirpath, fname))
    return py_files
