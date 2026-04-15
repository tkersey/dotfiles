#!/usr/bin/env python3
"""Heuristic scanner for Universalist-style structural signals.

The goal is not perfect static analysis. The goal is to surface likely seams
that deserve human review.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Iterator

TEXT_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".go", ".rs", ".swift",
    ".java", ".kt", ".kts", ".scala", ".rb", ".php", ".cs", ".json", ".yaml",
    ".yml", ".toml", ".sh", ".md",
}
IGNORED_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "dist", "build", "target", "vendor",
    ".next", ".venv", "venv", "__pycache__", ".mypy_cache", ".pytest_cache",
    ".ruff_cache", "coverage",
}

LINE_PATTERNS = {
    "flags_to_coproduct": [
        re.compile(r"\b(status|state|phase|stage)\b", re.IGNORECASE),
        re.compile(r"\b(approved|published|archived|draft|pending|active|disabled)\b", re.IGNORECASE),
        re.compile(r"\b(is[A-Z]\w+|has[A-Z]\w+|can[A-Z]\w+|should[A-Z]\w+)\b"),
        re.compile(r"\b(null|None|nil|undefined)\b"),
        re.compile(r"\?\s*[:=]"),
    ],
    "repeated_validation": [
        re.compile(r"\b(validate|validator|is_valid|isValid|assert|guard|parse|normalize|sanitize)\b"),
        re.compile(r"\b(trim|strip|lowercase|lower|upper|regex|pattern)\b", re.IGNORECASE),
        re.compile(r"\b(email|slug|tenant|account|identifier|id|version|locale)\b", re.IGNORECASE),
    ],
    "shared_key_pullback": [
        re.compile(r"\b(account|tenant|schema|locale|customer|organization|org|project)_?id\b", re.IGNORECASE),
        re.compile(r"(==|===|!=|!==)"),
        re.compile(r"\b(mismatch|must match|same account|same tenant|same schema)\b", re.IGNORECASE),
    ],
    "branchy_to_exponential": [
        re.compile(r"\b(if|elif|else if|switch|case|match)\b"),
        re.compile(r"\b(policy|pricing|price|render|formatter|strategy|handler|calculate|rule)\b", re.IGNORECASE),
        re.compile(r"\b(return|yield)\b"),
    ],
    "syntax_to_free": [
        re.compile(r"\b(ast|expr|expression|node|rule|workflow|command|instruction|token)\b", re.IGNORECASE),
        re.compile(r"\b(eval|evaluate|execute|interpret|visit|fold|pretty|explain)\b", re.IGNORECASE),
        re.compile(r"\b(class|interface|enum|sealed|datatype|struct)\b", re.IGNORECASE),
    ],
    "fields_to_product": [
        re.compile(r"\b(data class|record|struct|interface|type)\b", re.IGNORECASE),
        re.compile(r"\b(amount|currency|name|title|body|metadata|context|config|options)\b", re.IGNORECASE),
        re.compile(r"[:,]"),
    ],
}

METADATA = {
    "flags_to_coproduct": {
        "construction": "coproduct",
        "why": "exclusive variants are probably being modeled with flag or nullable matrices",
        "first_seam": "decoder or adapter from legacy row/DTO into an internal tagged union",
    },
    "repeated_validation": {
        "construction": "refined type / equalizer",
        "why": "a stable predicate appears to be re-enforced in several places",
        "first_seam": "constructor, parser, or controller boundary",
    },
    "shared_key_pullback": {
        "construction": "pullback witness",
        "why": "two views appear to require agreement on a shared projection",
        "first_seam": "checked aggregate constructor",
    },
    "branchy_to_exponential": {
        "construction": "exponential",
        "why": "behavior selection may want a function or strategy seam",
        "first_seam": "policy or handler injection point",
    },
    "syntax_to_free": {
        "construction": "free construction / initial algebra",
        "why": "syntax and interpretation may be mixed together",
        "first_seam": "AST + interpreter around one rule family",
    },
    "fields_to_product": {
        "construction": "product",
        "why": "several fields may simply belong together in one explicit product type",
        "first_seam": "constructor or value object",
    },
}


@dataclass
class Evidence:
    path: str
    line_number: int
    line: str


@dataclass
class Finding:
    signal: str
    construction: str
    score: int
    why: str
    first_seam: str
    evidence: list[Evidence]


def iter_files(root: Path) -> Iterator[Path]:
    if root.is_file():
        yield root
        return

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in IGNORED_DIRS]
        for filename in filenames:
            path = Path(dirpath) / filename
            if path.suffix.lower() in TEXT_EXTENSIONS:
                yield path


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return None
    except OSError:
        return None


def collect_evidence(path: Path, lines: list[str]) -> dict[str, list[Evidence]]:
    out: dict[str, list[Evidence]] = {name: [] for name in LINE_PATTERNS}
    for idx, line in enumerate(lines, start=1):
        compact = line.strip()
        if not compact:
            continue
        for signal, patterns in LINE_PATTERNS.items():
            hits = sum(1 for pattern in patterns if pattern.search(compact))
            threshold = 2 if signal != "fields_to_product" else 3
            if hits >= threshold:
                out[signal].append(Evidence(str(path), idx, compact[:220]))
    return out


def merge_findings(evidence_sets: Iterable[dict[str, list[Evidence]]]) -> list[Finding]:
    merged: dict[str, list[Evidence]] = {name: [] for name in LINE_PATTERNS}
    for evidence_set in evidence_sets:
        for signal, items in evidence_set.items():
            merged[signal].extend(items)

    findings: list[Finding] = []
    for signal, evidence in merged.items():
        if not evidence:
            continue
        score = min(100, len(evidence) * 8)
        meta = METADATA[signal]
        findings.append(
            Finding(
                signal=signal,
                construction=meta["construction"],
                score=score,
                why=meta["why"],
                first_seam=meta["first_seam"],
                evidence=evidence[:8],
            )
        )
    findings.sort(key=lambda item: item.score, reverse=True)
    return findings


def markdown(findings: list[Finding]) -> str:
    if not findings:
        return "# Universalist Signal Report\n\nNo strong heuristic findings.\n"
    lines = ["# Universalist Signal Report", ""]
    for finding in findings:
        lines.extend(
            [
                f"## {finding.signal} -> {finding.construction}",
                "",
                f"- Score: {finding.score}",
                f"- Why it may fit: {finding.why}",
                f"- First seam to try: {finding.first_seam}",
                "- Evidence:",
            ]
        )
        for item in finding.evidence:
            lines.append(f"  - `{item.path}:{item.line_number}` — {item.line}")
        lines.append("")
    lines.append(
        "Heuristic scan only. Review the evidence before choosing a construction."
    )
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", help="path to scan")
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="output format",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = Path(args.path)
    if not root.exists():
        print(f"Path does not exist: {root}", file=sys.stderr)
        return 2

    evidence_sets = []
    for path in iter_files(root):
        text = read_text(path)
        if text is None:
            continue
        evidence_sets.append(collect_evidence(path, text.splitlines()))

    findings = merge_findings(evidence_sets)

    if args.format == "json":
        print(json.dumps([asdict(finding) for finding in findings], indent=2))
    else:
        print(markdown(findings))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
