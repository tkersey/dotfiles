#!/usr/bin/env python3
"""Contract linter for codex/skills/resolve/SKILL.md."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_HEADINGS = [
    "# Resolve",
    "## Intent",
    "## Reporting",
    "## Actionable finding bar",
    "## Internal saturation state",
    "## Scope selection",
    "## Hard rules",
    "## Native review commands",
    "## Loop",
    "## How to invoke `$fixed-point-driver`",
    "## Minimal final response",
]

REQUIRED_PHRASES = [
    "codex review --base <base_branch>",
    "codex review --commit <commit_sha>",
    "$fixed-point-driver",
    "fresh native review",
    "git status --porcelain --untracked-files=all",
    "git merge-base HEAD <base_branch>",
    "**Status**",
    "**Review**",
    "**Validation**",
    "**Do Next**",
    "stdout and stderr from `codex review`",
    "There is no wall-clock timeout and no cycle cap inside `$resolve`.",
    "MUST NOT impose a wall-clock timeout or cycle cap.",
    "MUST NOT stop, skip, downgrade, or truncate a review round just because it is taking a long time.",
    "MUST NOT treat elapsed time, patience limits, or long review duration as a blocker.",
    "Wait for the review command to finish; long-running review rounds are acceptable.",
    "Never use `@{upstream}`",
    "Never pass remote-tracking refs like `origin/main`",
    "Do not compare a branch against itself.",
    "native-review saturation",
    "candidate clean",
    "two consecutive clean",
    "MUST NOT stop on the first clean.",
    "MUST NOT claim success based on only one clean review.",
    "resolve the seeded findings to non-recurrence",
    "proof-hook",
    "adjacent-seam",
    "review_reconciliation",
    "clean_streak",
    "Origin=review_seed|proof_hook|adjacent_seam|validation_gap",
]

REQUIRED_FRONTMATTER = {
    "name": "resolve",
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing file: {path}") from exc


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise SystemExit("SKILL.md is missing YAML frontmatter")

    front: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        front[key.strip()] = value.strip().strip('"')
    return front


def lint_skill(skill_path: Path) -> list[str]:
    errors: list[str] = []
    text = read_text(skill_path)
    front = parse_frontmatter(text)

    for key, expected in REQUIRED_FRONTMATTER.items():
        actual = front.get(key)
        if actual != expected:
            errors.append(f"frontmatter {key!r}: expected {expected!r}, found {actual!r}")

    if "description" not in front or not front["description"]:
        errors.append("frontmatter 'description' must be present and non-empty")

    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"missing heading: {heading}")

    for phrase in REQUIRED_PHRASES:
        if phrase not in text:
            errors.append(f"missing required phrase: {phrase}")

    intent_match = re.search(r"## Intent\n(.*?)(?:\n## |\Z)", text, re.DOTALL)
    if intent_match:
        intent = intent_match.group(1)
        if "candidate clean" not in intent or "native-review saturation" not in intent:
            errors.append("intent must define candidate clean and native-review saturation")
    else:
        errors.append("could not parse Intent section")

    loop_match = re.search(r"## Loop\n(.*?)(?:\n## |\Z)", text, re.DOTALL)
    if loop_match:
        loop_text = loop_match.group(1)
        ordered_phrases = [
            "Candidate clean",
            "Saturation confirmation",
            "Repair",
            "Validation gate",
            "Re-review",
        ]
        cursor = 0
        for phrase in ordered_phrases:
            idx = loop_text.find(phrase, cursor)
            if idx == -1:
                errors.append(f"loop is missing ordered phrase: {phrase}")
                break
            cursor = idx + len(phrase)
        if "Do not finish on this first clean." not in loop_text:
            errors.append("loop must explicitly forbid finishing on the first clean")
    else:
        errors.append("could not parse Loop section")

    handoff_match = re.search(r"## How to invoke `\$fixed-point-driver`\n(.*?)(?:\n## |\Z)", text, re.DOTALL)
    if handoff_match:
        handoff = handoff_match.group(1)
        for phrase in [
            "seeded_findings_closed",
            "seeded_findings_still_open",
            "fix_discovered_count",
            "Origin=review_seed|proof_hook|adjacent_seam|validation_gap",
        ]:
            if phrase not in handoff:
                errors.append(f"handoff section missing phrase: {phrase}")
    else:
        errors.append("could not parse fixed-point-driver handoff section")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "skill_path",
        nargs="?",
        default=Path(__file__).resolve().parents[1] / "SKILL.md",
        type=Path,
        help="Path to SKILL.md (defaults to ../SKILL.md relative to this script)",
    )
    args = parser.parse_args()

    errors = lint_skill(args.skill_path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("resolve skill contract OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
