#!/usr/bin/env -S uv run python
"""Lint contract sections for codex/skills/fix/SKILL.md."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

EXPECTED_MAIN_HEADINGS = [
    "Contract",
    "Findings (severity order)",
    "Changes applied",
    "Pass trace",
    "Validation",
    "Residual risks / open questions",
]

EXPECTED_EMBEDDED_HEADINGS = [
    "Findings (severity order)",
    "Changes applied",
    "Pass trace",
    "Validation",
    "Residual risks / open questions",
]

EXPECTED_VALIDATION_KEYS = [
    "baseline_cmd",
    "baseline_result",
    "proof_hook",
    "final_cmd",
    "final_result",
]

EXPECTED_FINDINGS_LINES = [
    "Proof strength: `<characterization|targeted_regression|property_or_fuzz>`",
    "Compatibility impact: `<none|tightening|additive|breaking>`",
]

ALLOWED_BLOCKED_BY = [
    "product_ambiguity",
    "breaking_change",
    "no_repro_or_proof",
    "scope_guardrail",
    "generated_output",
    "external_dependency",
    "perf_unmeasurable",
]

EXPECTED_RESIDUAL_LINE = (
    "- Otherwise: `- <file:line or token> — blocked_by=<"
    + "|".join(ALLOWED_BLOCKED_BY)
    + "> — next=<one action>`"
)

SECTION_PATTERN = re.compile(r"^\*\*(.+?)\*\*$", re.MULTILINE)
JSON_LINE_PATTERN = re.compile(r"^\s*-\s*`(\{.*\})`\s*\(single-line JSON\)\s*$", re.MULTILINE)


def line_no(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def extract_block(text: str, start_marker: str, end_marker: str) -> tuple[str, int]:
    start = text.find(start_marker)
    if start < 0:
        raise ValueError(f"missing marker: {start_marker!r}")
    end = text.find(end_marker, start)
    if end < 0:
        raise ValueError(f"missing marker: {end_marker!r}")
    return text[start:end], start


def extract_heading_lines(block: str, base_offset: int, full_text: str) -> list[tuple[str, int]]:
    results: list[tuple[str, int]] = []
    for match in SECTION_PATTERN.finditer(block):
        heading = match.group(1).strip()
        results.append((heading, line_no(full_text, base_offset + match.start())))
    return results


def extract_validation_json_keys(
    block: str, base_offset: int, full_text: str, label: str, errors: list[str]
) -> list[str] | None:
    validation_idx = block.find("**Validation**")
    if validation_idx < 0:
        errors.append(f"{label}: missing **Validation** section")
        return None

    post_validation = block[validation_idx:]
    match = JSON_LINE_PATTERN.search(post_validation)
    if not match:
        errors.append(
            f"{label}: missing single-line JSON template under Validation "
            f"(line {line_no(full_text, base_offset + validation_idx)})"
        )
        return None

    raw_json = match.group(1)
    raw_line = line_no(full_text, base_offset + validation_idx + match.start())
    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        errors.append(f"{label}: parse_error at line {raw_line}: {exc.msg}")
        return None

    keys = list(parsed.keys())
    if keys != EXPECTED_VALIDATION_KEYS:
        errors.append(
            f"{label}: validation_json_keys mismatch at line {raw_line}: "
            f"expected={EXPECTED_VALIDATION_KEYS} actual={keys}"
        )
    return keys


def check_heading_order(
    found: list[tuple[str, int]], expected: list[str], label: str, errors: list[str]
) -> None:
    found_names = [name for name, _ in found]
    if found_names != expected:
        errors.append(f"{label}: heading_order mismatch: expected={expected} actual={found_names}")


def extract_heading_section(
    block: str, heading: str, next_heading: str | None, label: str, errors: list[str]
) -> tuple[str, int] | None:
    start_match = re.search(rf"(?m)^\*\*{re.escape(heading)}\*\*$", block)
    if not start_match:
        errors.append(f"{label}: missing **{heading}** section")
        return None

    start = start_match.start()
    if next_heading is None:
        end = len(block)
    else:
        end_match = re.search(rf"(?m)^\*\*{re.escape(next_heading)}\*\*$", block[start + 1 :])
        if not end_match:
            errors.append(f"{label}: missing **{next_heading}** section after **{heading}**")
            return None
        end = start + 1 + end_match.start()
    return block[start:end], start


def require_line(
    section: str,
    expected_line: str,
    label: str,
    section_name: str,
    section_line: int,
    errors: list[str],
) -> None:
    if expected_line not in section:
        errors.append(
            f"{label}: missing template line in **{section_name}** "
            f"(line {section_line}): {expected_line}"
        )


def run(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    try:
        main_block, main_offset = extract_block(
            text, "## Deliverable format (chat)", "### Fix Record (embedded mode only)"
        )
        embedded_block, embedded_offset = extract_block(
            text, "### Fix Record (embedded mode only)", "## Pitfalls"
        )
    except ValueError as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1

    main_headings = extract_heading_lines(main_block, main_offset, text)
    embedded_headings = extract_heading_lines(embedded_block, embedded_offset, text)
    check_heading_order(main_headings, EXPECTED_MAIN_HEADINGS, "main", errors)
    check_heading_order(embedded_headings, EXPECTED_EMBEDDED_HEADINGS, "embedded", errors)

    main_keys = extract_validation_json_keys(main_block, main_offset, text, "main", errors)
    embedded_keys = extract_validation_json_keys(
        embedded_block, embedded_offset, text, "embedded", errors
    )
    if main_keys and embedded_keys and main_keys != embedded_keys:
        errors.append(
            "validation_json_sync mismatch: "
            f"main={main_keys} embedded={embedded_keys}"
        )

    for label, block, offset in (("main", main_block, main_offset), ("embedded", embedded_block, embedded_offset)):
        findings = extract_heading_section(
            block, "Findings (severity order)", "Changes applied", label, errors
        )
        if findings:
            findings_block, findings_start = findings
            findings_line = line_no(text, offset + findings_start)
            for expected_line in EXPECTED_FINDINGS_LINES:
                require_line(
                    findings_block,
                    expected_line,
                    label,
                    "Findings (severity order)",
                    findings_line,
                    errors,
                )

        residual = extract_heading_section(
            block, "Residual risks / open questions", None, label, errors
        )
        if residual:
            residual_block, residual_start = residual
            residual_line = line_no(text, offset + residual_start)
            require_line(
                residual_block,
                EXPECTED_RESIDUAL_LINE,
                label,
                "Residual risks / open questions",
                residual_line,
                errors,
            )

    if errors:
        print("[FAIL] fix skill contract lint errors:", file=sys.stderr)
        for err in errors:
            print(f" - {err}", file=sys.stderr)
        return 1

    print(f"[OK] fix skill contract checks passed: {path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint fix skill contract sections.")
    parser.add_argument(
        "path",
        nargs="?",
        default="codex/skills/fix/SKILL.md",
        help="Path to fix SKILL.md (default: codex/skills/fix/SKILL.md)",
    )
    args = parser.parse_args()
    return run(Path(args.path))


if __name__ == "__main__":
    raise SystemExit(main())
