#!/usr/bin/env python3
"""Validate OPERATOR-CARDS.md against the skill's operator-card contract.

Read-only. Exits non-zero on missing required sections.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILE = ROOT / "references" / "OPERATOR-CARDS.md"

REQUIRED_MARKERS = {
    "definition": r"\*\*Definition\*\*:",
    "triggers": r"\*\*Triggers\*\*:",
    "failure modes": r"\*\*Failure modes\*\*:",
    "prompt module": r"\*\*Prompt module\*\*:",
}


def operator_blocks(text: str) -> list[tuple[int, str, str]]:
    blocks: list[tuple[int, str, str]] = []
    lines = text.splitlines()
    stop_at = len(lines)
    for idx, line in enumerate(lines):
        if line.strip() == "## Composition rules":
            stop_at = idx
            break

    current: tuple[int, str] | None = None
    start_idx = 0
    for idx, line in enumerate(lines[:stop_at]):
        if line.startswith("### "):
            if current is not None:
                line_no, title = current
                blocks.append((line_no, title, "\n".join(lines[start_idx:idx])))
            current = (idx + 1, line.removeprefix("### ").strip())
            start_idx = idx
    if current is not None:
        line_no, title = current
        blocks.append((line_no, title, "\n".join(lines[start_idx:stop_at])))
    return blocks


def count_list_items(section: str, marker: str) -> int:
    start = section.find(marker)
    if start == -1:
        return 0
    rest = section[start + len(marker) :]
    next_marker = re.search(r"\n\*\*[^*]+\*\*:", rest)
    if next_marker:
        rest = rest[: next_marker.start()]
    return sum(1 for line in rest.splitlines() if line.strip().startswith("- "))


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_FILE
    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    blocks = operator_blocks(text)

    if not blocks:
        failures.append("no operator headings found before '## Composition rules'")

    for line_no, title, block in blocks:
        for name, pattern in REQUIRED_MARKERS.items():
            if not re.search(pattern, block):
                failures.append(f"{path}:{line_no}: {title}: missing {name}")
        trigger_count = count_list_items(block, "**Triggers**:")
        if trigger_count < 3:
            failures.append(
                f"{path}:{line_no}: {title}: expected at least 3 triggers, found {trigger_count}"
            )
        failure_count = count_list_items(block, "**Failure modes**:")
        if failure_count < 2:
            failures.append(
                f"{path}:{line_no}: {title}: expected at least 2 failure modes, found {failure_count}"
            )

    if failures:
        print("operator validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"operator validation: PASS ({len(blocks)} operators)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
