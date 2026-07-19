#!/usr/bin/env python3
"""Lightweight, bounded Universalist signal detector.

Heuristic only: output guides inspection and never selects an architecture route.
Candidate-file limits are applied *after* language and repository-relative skip
filters so unrelated assets cannot consume the scan budget.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

PATTERNS = [
    (
        "boolean/status matrix",
        re.compile(
            r"\b(is[A-Z][A-Za-z0-9_]*|has[A-Z][A-Za-z0-9_]*|status|state|deletedAt|publishedAt)\b"
        ),
    ),
    (
        "repeated validation",
        re.compile(r"validate|is_valid|isValid|assert|guard|check|parse[A-Z]", re.I),
    ),
    (
        "shared-id agreement",
        re.compile(r"\b(customerId|accountId|tenantId|userId|version)\b"),
    ),
    (
        "callback/handler boundary",
        re.compile(r"callback|handler|register|subscribe|on[A-Z]|strategy", re.I),
    ),
    (
        "projection/query sprawl",
        re.compile(r"project|view|select|query|toDto|fromDto", re.I),
    ),
    (
        "syntax/execution mix",
        re.compile(r"evaluate|interpret|execute|render|compile", re.I),
    ),
    (
        "typed component wiring",
        re.compile(
            r"wire|pipeline|compose|connect|port|component|plugin|middleware|stage",
            re.I,
        ),
    ),
    (
        "effect ordering",
        re.compile(
            r"parallel|concurrent|sequence|before|after|transaction|commit|rollback|await",
            re.I,
        ),
    ),
]
SKIP_DIRS = {".git", "node_modules", "target", "dist", "build", ".venv", "__pycache__"}
SUFFIXES = {
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".py",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".swift",
    ".hs",
    ".md",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--max-files", type=int, default=10_000)
    parser.add_argument("--max-lines", type=int, default=5_000)
    parser.add_argument("--max-line-length", type=int, default=2_000)
    return parser


def candidate_paths(root: Path, max_files: int) -> list[Path]:
    if max_files < 1:
        raise ValueError("--max-files must be positive")
    if root.is_file():
        return [root] if root.suffix.lower() in SUFFIXES else []
    candidates: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUFFIXES:
            continue
        relative = path.relative_to(root)
        # Evaluate skip components relative to the requested root. A checkout whose
        # parent directory is named "build" must not suppress every source file.
        if any(part in SKIP_DIRS for part in relative.parts[:-1]):
            continue
        candidates.append(path)
        if len(candidates) >= max_files:
            break
    return candidates


def detect(path: Path, *, max_lines: int, max_line_length: int) -> list[str]:
    if max_lines < 1 or max_line_length < 1:
        raise ValueError("line limits must be positive")
    try:
        lines = path.read_text(errors="ignore").splitlines()[:max_lines]
    except OSError:
        return []
    hits: list[str] = []
    for line in lines:
        line = line[:max_line_length]
        for name, pattern in PATTERNS:
            if name not in hits and pattern.search(line):
                hits.append(name)
        if len(hits) >= 4:
            break
    return hits


def main() -> int:
    args = build_parser().parse_args()
    root = args.root.resolve()
    try:
        paths = candidate_paths(root, args.max_files)
        for path in paths:
            hits = detect(
                path, max_lines=args.max_lines, max_line_length=args.max_line_length
            )
            if hits:
                print(f"{path}: {', '.join(hits)}")
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
