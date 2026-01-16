#!/usr/bin/env uv run python
"""Summarize staged vs unstaged diff size for micro-commit scoping."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run_git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout


def parse_numstat(output: str):
    entries = []
    for line in output.strip().splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        add_raw, del_raw, path = parts
        binary = add_raw == "-" or del_raw == "-"
        add = 0 if not add_raw.isdigit() else int(add_raw)
        delete = 0 if not del_raw.isdigit() else int(del_raw)
        entries.append(
            {
                "path": path,
                "add": add,
                "delete": delete,
                "binary": binary,
            }
        )
    return entries


def summarize(label: str, args: list[str]):
    output = run_git(*args)
    entries = parse_numstat(output)
    files = len(entries)
    add = sum(e["add"] for e in entries)
    delete = sum(e["delete"] for e in entries)
    binaries = sum(1 for e in entries if e["binary"])

    print(f"{label}: {files} files, +{add}/-{delete}, binaries: {binaries}")
    if files:
        for entry in entries:
            print(f"  {entry['path']} (+{entry['add']}/-{entry['delete']})")
    else:
        print("  (no changes)")


def main() -> int:
    try:
        root = run_git("rev-parse", "--show-toplevel").strip()
    except RuntimeError as exc:
        print(f"Not a git repository: {exc}")
        return 1

    print("Micro-scope summary")
    print(f"Repo: {root}")
    print()

    status = run_git("status", "-sb").strip()
    print("Status")
    print(status if status else "(clean)")
    print()

    summarize("Staged", ["diff", "--cached", "--numstat"])
    print()
    summarize("Unstaged", ["diff", "--numstat"])
    print()
    print("Reminder: micro commits should contain one precise, coherent change.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
