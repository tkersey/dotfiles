#!/usr/bin/env python3
"""
Score refactor candidates via the Opportunity Matrix.

Usage:  ./score_candidates.py <duplication_map.md> [--accept-threshold 2.0]
Reads a markdown table with columns | ID | LOC_saved | Conf | Risk | ...
Emits scored_candidates.md alongside it, with Score + Decision columns.

Conventions (per SKILL.md):
  Score = (LOC_saved_pts * Confidence) / Risk
  LOC_saved (1-5):  5: >=200, 4: 50-200, 3: 20-50, 2: 5-20, 1: <5
  Confidence (1-5): 5 high, 3 medium, 1 speculative
  Risk (1-5):       1 single file, 3 cross-module, 5 crosses async/error/observability boundary
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def loc_to_pts(n: int) -> int:
    if n >= 200:
        return 5
    if n >= 50:
        return 4
    if n >= 20:
        return 3
    if n >= 5:
        return 2
    return 1


def parse_int(cell: str) -> int | None:
    cell = cell.strip().lstrip("-")
    m = re.search(r"\d+", cell)
    return int(m.group()) if m else None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("map", help="Path to duplication_map.md (markdown table input)")
    p.add_argument("--accept-threshold", type=float, default=2.0,
                   help="Minimum Score to accept (default 2.0)")
    args = p.parse_args()

    src = Path(args.map)
    if not src.exists():
        print(f"no such file: {src}", file=sys.stderr)
        return 2

    text = src.read_text()
    out_lines: list[str] = []
    out_lines.append(f"# Scored Candidates — generated from {src.name}")
    out_lines.append("")
    out_lines.append("| ID | LOC_saved | LOC pts | Conf | Risk | Score | Decision | Notes |")
    out_lines.append("|----|-----------|---------|------|------|-------|----------|-------|")

    accepted = 0
    rejected = 0
    total_loc_saved = 0

    # Find table rows (very forgiving; expects | ID | ... | columns)
    for line in text.splitlines():
        if not line.startswith("|") or line.startswith("|---") or line.startswith("| ID"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        # Need at least: ID, kind, locations, LOC, count, type
        if len(cells) < 6:
            continue
        cid = cells[0]
        if not cid or cid == "ID" or cid.startswith("-"):
            continue

        loc_each = parse_int(cells[3])
        n = parse_int(cells[4])
        if loc_each is None or n is None:
            continue
        loc_saved = loc_each * n - max(loc_each // 2, 5)  # rough estimate of unified size
        loc_pts = loc_to_pts(loc_saved)

        # Confidence and Risk are not in the input map; default to medium pending review
        confidence = 3
        risk = 2
        score = round((loc_pts * confidence) / max(risk, 1), 2)
        decision = "ACCEPT" if score >= args.accept_threshold else "REJECT"
        if decision == "ACCEPT":
            accepted += 1
            total_loc_saved += loc_saved
        else:
            rejected += 1

        notes = cells[5] if len(cells) > 5 else ""
        out_lines.append(
            f"| {cid} | {loc_saved} | {loc_pts} | {confidence} | {risk} | {score} | {decision} | {notes} |"
        )

    out_lines.append("")
    out_lines.append(
        f"Accepted: {accepted} (~{total_loc_saved} LOC predicted); Rejected: {rejected} "
        f"(threshold: {args.accept_threshold})"
    )
    out_lines.append("")
    out_lines.append("**NOTE:** Confidence and Risk default to 3/2. Re-score by hand per candidate "
                     "after callsite census; do not trust auto-defaults for non-mechanical refactors.")

    dest = src.with_name("scored_candidates.md")
    dest.write_text("\n".join(out_lines) + "\n")
    print(f"wrote: {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
