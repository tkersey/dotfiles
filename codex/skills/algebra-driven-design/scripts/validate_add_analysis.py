#!/usr/bin/env python3
"""Validate that a Markdown ADD analysis contains the required sections.

Usage:
  python scripts/validate_add_analysis.py report.md
  python scripts/validate_add_analysis.py report.md --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = {
    "domain_frame": [r"domain frame", r"context", r"goal"],
    "carriers": [r"carriers?", r"types?", r"domain values?"],
    "operations": [r"operations?", r"signatures?", r"commands?"],
    "observations": [r"observations?", r"equality", r"semantics?"],
    "laws": [r"laws?", r"invariants?", r"non-laws?"],
    "architecture": [r"architecture", r"boundaries", r"components"],
    "implementation": [r"implementation", r"codebase", r"interfaces?", r"ports?"],
    "tests": [r"tests?", r"property", r"validation", r"trace"],
    "risks": [r"risks?", r"assumptions?", r"open questions?", r"counterexamples?"],
}

QUALITY_SIGNALS = {
    "has_formulas": r"[a-zA-Z0-9_()]+\s*(=|==|≡|->|→)",
    "has_signatures": r"\w+\s*:\s*[^\n]+(->|→)",
    "has_counterexamples": r"counterexample|non-law|does not hold|false law",
    "has_law_to_architecture": r"law.*architecture|architecture.*law|boundary.*law|law.*boundary",
    "has_law_to_test": r"law.*test|test.*law|property test|trace test|parity test",
    "has_effect_boundary": r"interpreter|port|adapter|effectful|external effect|tool",
}


def normalize(text: str) -> str:
    return text.lower()


def section_present(text: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if re.search(rf"(^|\n)\s*#+\s+.*({pattern})", text, flags=re.IGNORECASE):
            return True
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True
    return False


def validate(text: str) -> dict[str, object]:
    lowered = normalize(text)
    sections = {name: section_present(lowered, patterns) for name, patterns in REQUIRED_SECTIONS.items()}
    signals = {name: bool(re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)) for name, pattern in QUALITY_SIGNALS.items()}
    missing = [name for name, present in sections.items() if not present]
    weak_signals = [name for name, present in signals.items() if not present]
    score = round((sum(sections.values()) / len(sections)) * 0.7 + (sum(signals.values()) / len(signals)) * 0.3, 3)
    return {
        "score": score,
        "sections": sections,
        "signals": signals,
        "missing_required_sections": missing,
        "missing_quality_signals": weak_signals,
        "passed": not missing and score >= 0.75,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Markdown ADD analysis.")
    parser.add_argument("path", help="Path to Markdown report")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    result = validate(text)

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"ADD analysis score: {result['score']}")
        print(f"Passed: {result['passed']}")
        missing = result["missing_required_sections"]
        if missing:
            print("Missing required sections:")
            for item in missing:  # type: ignore[assignment]
                print(f"  - {item}")
        weak = result["missing_quality_signals"]
        if weak:
            print("Missing/weak quality signals:")
            for item in weak:  # type: ignore[assignment]
                print(f"  - {item}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
