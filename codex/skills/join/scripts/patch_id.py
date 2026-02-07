#!/usr/bin/env python3
"""Compute canonical Patch-Id values from unified diffs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


FENCE_RE = re.compile(r"```diff\s*\n(.*?)\n```", re.IGNORECASE | re.DOTALL)

DIFF_METADATA_PREFIXES = (
    "diff --git ",
    "index ",
    "--- ",
    "+++ ",
    "@@ ",
    "old mode ",
    "new mode ",
    "new file mode ",
    "deleted file mode ",
    "rename from ",
    "rename to ",
    "copy from ",
    "copy to ",
    "similarity index ",
    "dissimilarity index ",
    "Binary files ",
    "GIT binary patch",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute canonical Patch-Id values.")
    parser.add_argument("--input", help="Read payload from file instead of stdin.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument(
        "--raw-diff",
        action="store_true",
        help="Treat input as a single raw diff payload (skip fenced block extraction).",
    )
    return parser.parse_args()


def read_payload(path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


def extract_diff_blocks(payload: str, raw_diff: bool) -> list[str]:
    if raw_diff:
        return [payload]
    blocks = [match.group(1) for match in FENCE_RE.finditer(payload)]
    if blocks:
        return blocks
    if "diff --git " in payload:
        return [payload]
    return []


def is_metadata_line(line: str) -> bool:
    return line.startswith(DIFF_METADATA_PREFIXES)


def normalize_diff(diff_text: str) -> str:
    normalized = diff_text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    while lines and lines[0] == "":
        lines.pop(0)
    while lines and lines[-1] == "":
        lines.pop()

    normalized_lines = []
    for line in lines:
        if is_metadata_line(line):
            normalized_lines.append(line.rstrip())
        else:
            normalized_lines.append(line)
    return "\n".join(normalized_lines)


def patch_id(normalized_diff: str) -> str:
    return hashlib.sha256(normalized_diff.encode("utf-8")).hexdigest()


def main() -> int:
    args = parse_args()
    payload = read_payload(args.input)
    blocks = extract_diff_blocks(payload, args.raw_diff)
    if not blocks:
        print("No diff blocks found.", file=sys.stderr)
        return 1

    results = []
    for idx, block in enumerate(blocks, start=1):
        norm = normalize_diff(block)
        results.append(
            {
                "index": idx,
                "patch_id": patch_id(norm),
                "line_count": 0 if not norm else norm.count("\n") + 1,
            }
        )

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for row in results:
            print(f"{row['index']}\t{row['patch_id']}\t{row['line_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
