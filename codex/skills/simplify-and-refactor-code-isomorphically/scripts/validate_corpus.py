#!/usr/bin/env python3
"""Validate CORPUS.md quote entries.

Checks that every A-*/S-*/K-* quote entry has source, tags, verbatim text,
derived rule, and usage fields. Read-only.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILE = ROOT / "references" / "CORPUS.md"
ENTRY_RE = re.compile(r"^### ([ASK]-\d+)\b.*$", re.MULTILINE)
REQUIRED_FIELDS = [
    "**Source:**",
    "**Tag(s):**",
    "**Verbatim:**",
    "**Rule derived:**",
    "**Used by:**",
]


def iter_entries(text: str) -> list[tuple[int, str, str]]:
    matches = list(ENTRY_RE.finditer(text))
    entries: list[tuple[int, str, str]] = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        line_no = text.count("\n", 0, match.start()) + 1
        entries.append((line_no, match.group(1), text[start:end]))
    return entries


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_FILE
    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    entries = iter_entries(text)

    if not entries:
        failures.append("no quote entries matching A-*/S-*/K-* found")

    seen: set[str] = set()
    for line_no, quote_id, block in entries:
        if quote_id in seen:
            failures.append(f"{path}:{line_no}: duplicate quote id {quote_id}")
        seen.add(quote_id)
        for field in REQUIRED_FIELDS:
            if field not in block:
                failures.append(f"{path}:{line_no}: {quote_id}: missing {field}")
        if "> " not in block:
            failures.append(f"{path}:{line_no}: {quote_id}: missing blockquote body")

    if failures:
        print("corpus validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"corpus validation: PASS ({len(entries)} quote entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
