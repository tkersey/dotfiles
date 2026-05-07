#!/usr/bin/env python3
"""Heuristic scanner for Universalist-style structural signals.

The goal is not perfect static analysis. The goal is to surface likely seams that deserve human review.
Output includes altitude-aware and reduce-preflight fields so the scan can feed an Abstraction Move Packet.
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
    ".yml", ".toml", ".sh", ".md", ".sql", ".graphql", ".proto",
}

IGNORED_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "dist", "build", "target", "vendor", ".next",
    ".nuxt", ".venv", "venv", "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    "coverage", ".turbo", ".nx", "generated", ".generated",
}

LINE_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "flags_to_coproduct": [
        re.compile(r"\b(status|state|phase|stage|kind|type)\b", re.IGNORECASE),
        re.compile(r"\b(approved|published|archived|draft|pending|active|disabled|deleted|cancelled|failed)\b", re.IGNORECASE),
        re.compile(r"\b(is[A-Z]\w+|has[A-Z]\w+|can[A-Z]\w+|should[A-Z]\w+)\b"),
        re.compile(r"\b(null|None|nil|undefined|Optional|Maybe)\b"),
        re.compile(r"\?\s*[:=]"),
    ],
    "repeated_validation": [
        re.compile(r"\b(validate|validator|is_valid|isValid|assert|guard|parse|normalize|sanitize|coerce)\b"),
        re.compile(r"\b(trim|strip|lowercase|lower|upper|regex|pattern|matches|match)\b", re.IGNORECASE),
        re.compile(r"\b(email|slug|tenant|account|identifier|id|version|locale|currency|amount)\b", re.IGNORECASE),
    ],
    "shared_key_pullback": [
        re.compile(r"\b(account|tenant|schema|locale|customer|organization|org|project|workspace)_?id\b", re.IGNORECASE),
        re.compile(r"(==|===|!=|!==|\.equals\(|Objects\.equals)"),
        re.compile(r"\b(mismatch|must match|same account|same tenant|same schema|foreign tenant)\b", re.IGNORECASE),
    ],
    "branchy_to_exponential": [
        re.compile(r"\b(if|elif|else if|switch|case|match|when)\b"),
        re.compile(r"\b(policy|pricing|price|render|formatter|strategy|handler|calculate|rule|discount)\b", re.IGNORECASE),
        re.compile(r"\b(return|yield|=>)\b"),
    ],
    "syntax_to_free": [
        re.compile(r"\b(ast|expr|expression|node|rule|workflow|command|instruction|token|dsl)\b", re.IGNORECASE),
        re.compile(r"\b(eval|evaluate|execute|interpret|visit|fold|pretty|explain|render|serialize)\b", re.IGNORECASE),
        re.compile(r"\b(class|interface|enum|sealed|datatype|struct|record|type)\b", re.IGNORECASE),
    ],
    "fields_to_product": [
        re.compile(r"\b(data class|record|struct|interface|type|class)\b", re.IGNORECASE),
        re.compile(r"\b(amount|currency|name|title|body|metadata|context|config|options|address)\b", re.IGNORECASE),
        re.compile(r"[:,]"),
    ],
    "protocol_state": [
        re.compile(r"\b(transition|nextState|reducer|dispatch|command|event|workflow|step|phase|allowed|guard)\b", re.IGNORECASE),
        re.compile(r"\b(cancel|approve|publish|retry|complete|start|submit|advance|rollback)\b", re.IGNORECASE),
        re.compile(r"\b(status|state|phase|stage)\b", re.IGNORECASE),
    ],
}

METADATA = {
    "flags_to_coproduct": {
        "construction": "coproduct",
        "current_altitude": "1-2: primitive fields pretending to be exclusive states",
        "proposed_altitude": "2: explicit domain invariant",
        "why": "exclusive variants are probably being modeled with flag or nullable matrices",
        "first_seam": "decoder or adapter from legacy row/DTO into an internal tagged union",
        "boundary_hint": "preserve wire/storage shape behind a decoder until migration is explicit",
        "proof_hint": "exhaustive handling plus invalid legacy fixture rejection",
        "reduce_preflight": "reject if a simple enum or local branch captures all cases without impossible combinations",
    },
    "repeated_validation": {
        "construction": "refined type / equalizer",
        "current_altitude": "1: raw primitive plus repeated call-site discipline",
        "proposed_altitude": "2: checked value at parse/constructor boundary",
        "why": "a stable predicate appears to be re-enforced in several places",
        "first_seam": "constructor, parser, or controller boundary",
        "boundary_hint": "convert raw input once, then pass the checked value internally",
        "proof_hint": "valid, invalid, and normalization-idempotence tests",
        "reduce_preflight": "reject if the predicate is unstable or appears in only one local place",
    },
    "shared_key_pullback": {
        "construction": "pullback witness",
        "current_altitude": "1: plain pairs plus scattered agreement checks",
        "proposed_altitude": "2: checked aggregate/witness for shared projection agreement",
        "why": "two views appear to require agreement on a shared projection",
        "first_seam": "checked aggregate constructor",
        "boundary_hint": "do not alter source records; add a checked join type at the seam",
        "proof_hint": "mismatch rejection plus preserved projections",
        "reduce_preflight": "reject if agreement is checked once and can remain a local assertion",
    },
    "branchy_to_exponential": {
        "construction": "exponential",
        "current_altitude": "1: branchy local policy selection",
        "proposed_altitude": "2-3: behavior supplied as a function/strategy table",
        "why": "behavior selection may want a function or strategy seam",
        "first_seam": "policy or handler injection point",
        "boundary_hint": "keep caller shape stable; introduce function/strategy parameter locally",
        "proof_hint": "fixture parity against old branch",
        "reduce_preflight": "reject if a table or direct conditional is clearer",
    },
    "syntax_to_free": {
        "construction": "free construction / initial algebra",
        "current_altitude": "1-3: syntax and interpretation mixed",
        "proposed_altitude": "3: syntax data separated from interpreters",
        "why": "syntax and interpretation may be mixed together",
        "first_seam": "AST plus one interpreter around one rule family",
        "boundary_hint": "keep serialized syntax compatible unless explicitly migrating",
        "proof_hint": "interpreter consistency plus differential tests",
        "reduce_preflight": "reject if there is only one interpreter and no need to persist/explain/render syntax",
    },
    "fields_to_product": {
        "construction": "product",
        "current_altitude": "0-1: loose field bundle",
        "proposed_altitude": "1-2: explicit product/value object",
        "why": "several fields may simply belong together in one explicit product type",
        "first_seam": "constructor or value object",
        "boundary_hint": "prefer native record/struct/object before a heavier model",
        "proof_hint": "constructor and projection consistency",
        "reduce_preflight": "reject if existing object shape is already explicit enough",
    },
    "protocol_state": {
        "construction": "protocol / coproduct + transition table",
        "current_altitude": "1-4: state rules hidden in branches/framework hooks",
        "proposed_altitude": "2-3: explicit allowed transitions",
        "why": "allowed operations may depend on current state",
        "first_seam": "command handler or reducer path",
        "boundary_hint": "preserve external commands/events while internal transitions become explicit",
        "proof_hint": "valid transition fixtures plus invalid transition rejection",
        "reduce_preflight": "split if a high-tax workflow/state framework wraps a real protocol",
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
    current_altitude: str
    proposed_altitude: str
    why: str
    first_seam: str
    boundary_hint: str
    blast_radius_estimate: str
    proof_hint: str
    reduce_preflight: str
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
            threshold = 2 if signal not in {"fields_to_product", "protocol_state"} else 3
            if hits >= threshold:
                out[signal].append(Evidence(str(path), idx, compact[:240]))
    return out


def blast_radius(evidence: list[Evidence]) -> str:
    files = {item.path for item in evidence}
    if len(files) <= 2:
        return "low: evidence is concentrated in one or two files"
    if len(files) <= 6:
        return "medium: evidence spans several files; choose a boundary seam"
    return "high: evidence is broad; start with diagnosis or one adapter seam"


def merge_findings(evidence_sets: Iterable[dict[str, list[Evidence]]], max_evidence: int) -> list[Finding]:
    merged: dict[str, list[Evidence]] = {name: [] for name in LINE_PATTERNS}
    for evidence_set in evidence_sets:
        for signal, items in evidence_set.items():
            merged[signal].extend(items)

    findings: list[Finding] = []
    for signal, evidence in merged.items():
        if not evidence:
            continue
        unique_files = len({item.path for item in evidence})
        score = min(100, len(evidence) * 6 + unique_files * 10)
        meta = METADATA[signal]
        findings.append(
            Finding(
                signal=signal,
                construction=meta["construction"],
                score=score,
                current_altitude=meta["current_altitude"],
                proposed_altitude=meta["proposed_altitude"],
                why=meta["why"],
                first_seam=meta["first_seam"],
                boundary_hint=meta["boundary_hint"],
                blast_radius_estimate=blast_radius(evidence),
                proof_hint=meta["proof_hint"],
                reduce_preflight=meta["reduce_preflight"],
                evidence=evidence[:max_evidence],
            )
        )
    findings.sort(key=lambda item: item.score, reverse=True)
    return findings


def markdown(findings: list[Finding]) -> str:
    if not findings:
        return "# Universalist Signal Report\n\nNo strong heuristic findings.\n"

    lines = ["# Universalist Signal Report", "", "Heuristic scan only. Review evidence before choosing a construction.", ""]
    for finding in findings:
        lines.extend([
            f"## {finding.signal} -> {finding.construction}",
            "",
            f"- Score: {finding.score}",
            f"- Current altitude: {finding.current_altitude}",
            f"- Proposed altitude: {finding.proposed_altitude}",
            f"- Why it may fit: {finding.why}",
            f"- First seam to try: {finding.first_seam}",
            f"- Boundary hint: {finding.boundary_hint}",
            f"- Blast radius estimate: {finding.blast_radius_estimate}",
            f"- Proof hint: {finding.proof_hint}",
            f"- Reduction preflight: {finding.reduce_preflight}",
            "- Evidence:",
        ])
        for item in finding.evidence:
            lines.append(f"  - `{item.path}:{item.line_number}` — {item.line}")
        lines.append("")
    lines.append("## Next step")
    lines.append("")
    lines.append("Pick one seam, run reduction preflight, and verify with the fastest credible proof signal.")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", help="path to scan")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="output format")
    parser.add_argument("--max-evidence", type=int, default=8, help="evidence lines per finding")
    parser.add_argument("--min-score", type=int, default=1, help="minimum finding score to emit")
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

    findings = [f for f in merge_findings(evidence_sets, args.max_evidence) if f.score >= args.min_score]
    if args.format == "json":
        print(json.dumps([asdict(finding) for finding in findings], indent=2))
    else:
        print(markdown(findings))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
