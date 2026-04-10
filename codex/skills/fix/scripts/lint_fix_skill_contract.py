#!/usr/bin/env python3
"""Minimal contract linter for codex/skills/fix/SKILL.md."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_HEADINGS = [
    "# Fix",
    "## Intent",
    "## Reporting",
    "## Actionable finding bar",
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
    "There is no wall-clock timeout and no cycle cap inside `$fix`.",
    "MUST NOT impose a wall-clock timeout or cycle cap.",
    "MUST NOT stop, skip, downgrade, or truncate a review round just because it is taking a long time.",
    "MUST NOT treat elapsed time, patience limits, or long review duration as a blocker.",
    "Wait for the review command to finish; long-running review rounds are acceptable.",
    "Never use `@{upstream}`",
    "Never pass remote-tracking refs like `origin/main`",
    "Do not compare a branch against itself.",
]

REQUIRED_FRONTMATTER = {
    "name": "fix",
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"missing file: {path}")


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise SystemExit("SKILL.md is missing YAML frontmatter")
    front = {}
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

    print("fix skill contract OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
