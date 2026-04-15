#!/usr/bin/env python3
"""Emit a construction-specific verification checklist."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

CONSTRUCTION_CHECKS = {
    "product": [
        "Constructor builds all parts explicitly",
        "Projection or field access returns the original parts",
        "No hidden coupling if independence is claimed",
    ],
    "coproduct": [
        "Every legal value maps to exactly one variant",
        "Invalid legacy combinations are rejected",
        "At least one consumer handles variants exhaustively",
    ],
    "refined": [
        "Valid values are accepted",
        "Invalid values are rejected",
        "Normalization is idempotent if normalization exists",
        "Construction is the main entry path",
    ],
    "pullback": [
        "Matching projections are accepted",
        "Mismatches are rejected",
        "Both original projections are preserved",
        "Downstream code does not repeat the same agreement check",
    ],
    "exponential": [
        "Injected behavior matches old branch outcomes on fixtures",
        "Composition order is explicit where relevant",
        "No branchy bypass remains in the chosen seam",
    ],
    "free": [
        "Evaluation interpreter matches expected behavior on a corpus",
        "Second interpreter (explain, pretty, log, or compile) aligns where expected",
        "Constructors remain free of execution logic",
    ],
}

LANGUAGE_HINTS = {
    "typescript": {
        "test_name_prefix": "it",
        "runner_hint": "Use the current TS/JS test runner already in the repo.",
    },
    "python": {
        "test_name_prefix": "test_",
        "runner_hint": "Use the current Python test runner already in the repo.",
    },
    "go": {
        "test_name_prefix": "Test",
        "runner_hint": "Use the standard testing package or the repo's existing Go test stack.",
    },
    "java": {
        "test_name_prefix": "test",
        "runner_hint": "Use the repo's JUnit-style stack if present.",
    },
    "kotlin": {
        "test_name_prefix": "test",
        "runner_hint": "Use the repo's Kotlin/JVM test stack if present.",
    },
    "rust": {
        "test_name_prefix": "test_",
        "runner_hint": "Use the standard Rust test module layout.",
    },
}

TRACK_NOTES = {
    "diagnosis": [
        "Name the cheapest future proof signal even if you are not running tests now.",
    ],
    "one-seam": [
        "Prefer one targeted unit or table-driven test.",
        "Prefer compile or typecheck if the encoding itself strengthens guarantees.",
    ],
    "staged-migration": [
        "Add parity or differential tests against the legacy path.",
        "Add decode or adapter tests around the compatibility boundary.",
    ],
}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("construction", help=f"one of: {', '.join(CONSTRUCTION_CHECKS)}")
    parser.add_argument("language", help=f"one of: {', '.join(LANGUAGE_HINTS)}")
    parser.add_argument(
        "--track",
        choices=("diagnosis", "one-seam", "staged-migration"),
        default="one-seam",
        help="execution track",
    )
    parser.add_argument("--write", help="write output to this file")
    return parser.parse_args(argv)


def render(construction: str, language: str, track: str) -> str:
    checks = CONSTRUCTION_CHECKS[construction]
    hint = LANGUAGE_HINTS[language]
    lines = [
        "# Verification Plan",
        "",
        f"- Construction: {construction}",
        f"- Language: {language}",
        f"- Track: {track}",
        f"- Runner hint: {hint['runner_hint']}",
        "",
        "## Minimum checks",
    ]
    for item in checks:
        lines.append(f"- {item}")
    lines.extend(["", "## Track-specific notes"])
    for item in TRACK_NOTES[track]:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Suggested test names",
            f"- {hint['test_name_prefix']}_accepts_valid_input",
            f"- {hint['test_name_prefix']}_rejects_invalid_input",
            f"- {hint['test_name_prefix']}_preserves_boundary_contract",
            "",
            "## Runtime-only leftovers",
            "- State explicitly which guarantees remain runtime-only after this seam.",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    construction = args.construction.lower()
    language = args.language.lower()

    if construction not in CONSTRUCTION_CHECKS:
        print(f"Unsupported construction: {args.construction}", file=sys.stderr)
        return 2
    if language not in LANGUAGE_HINTS:
        print(f"Unsupported language: {args.language}", file=sys.stderr)
        return 2

    output = render(construction, language, args.track)
    if args.write:
        Path(args.write).write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
