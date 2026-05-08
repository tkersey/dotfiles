#!/usr/bin/env python3
"""Check an Agent Skill folder structure and SKILL.md frontmatter.

Usage:
  python scripts/check_skill_structure.py /path/to/algebra-driven-design
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse_frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    if not text.startswith("---\n"):
        return {}, ["SKILL.md must start with YAML frontmatter delimited by ---"]
    end = text.find("\n---", 4)
    if end == -1:
        return {}, ["SKILL.md frontmatter must end with ---"]
    raw = text[4:end].strip().splitlines()
    data: dict[str, str] = {}
    for line in raw:
        if not line.strip() or line.startswith(" ") or line.startswith("-"):
            continue
        if ":" not in line:
            errors.append(f"frontmatter line lacks colon: {line}")
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data, errors


def check(root: Path) -> list[str]:
    errors: list[str] = []
    skill_md = root / "SKILL.md"
    if not skill_md.exists():
        return ["missing SKILL.md"]
    text = skill_md.read_text(encoding="utf-8")
    frontmatter, fm_errors = parse_frontmatter(text)
    errors.extend(fm_errors)

    name = frontmatter.get("name")
    description = frontmatter.get("description")

    if not name:
        errors.append("frontmatter missing required field: name")
    elif not NAME_RE.match(name):
        errors.append("name must contain lowercase letters, numbers, and single hyphens only")
    elif name != root.name:
        errors.append(f"name {name!r} should match folder name {root.name!r}")

    if not description:
        errors.append("frontmatter missing required field: description")
    elif len(description) > 1024:
        errors.append("description exceeds 1024 characters")

    line_count = len(text.splitlines())
    if line_count > 500:
        errors.append(f"SKILL.md has {line_count} lines; consider keeping it under 500 lines")

    for dirname in ["references", "assets", "scripts"]:
        path = root / dirname
        if path.exists() and not path.is_dir():
            errors.append(f"{dirname} exists but is not a directory")

    script_dir = root / "scripts"
    if script_dir.exists():
        for script in script_dir.iterdir():
            if script.suffix == ".py":
                first = script.read_text(encoding="utf-8", errors="ignore").splitlines()[:1]
                if not first or "python" not in first[0]:
                    errors.append(f"script {script.name} should start with a Python shebang")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Agent Skill folder structure.")
    parser.add_argument("root", nargs="?", default=".", help="Skill root folder")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    errors = check(root)
    if errors:
        print("Skill structure check failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Skill structure check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
