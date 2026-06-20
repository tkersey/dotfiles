#!/usr/bin/env python3
"""Read-only locator for repository contracts affected by Zig file/output changes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Iterable

CONTRACT_NAME_RE = re.compile(
    r"(manifest|registry|paths?|golden|expected|compile[-_ ]?fail|generated|fixture|snapshot|checksum)",
    re.IGNORECASE,
)
RELEVANT_SUFFIXES = {
    ".zig",
    ".zon",
    ".golden",
    ".expected",
    ".out",
    ".stderr",
    ".stdout",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".md",
}
EXCLUDED_DIRS = {".git", ".zig-cache", "zig-cache", "zig-out", "zig-pkg", "node_modules"}


class ScanError(RuntimeError):
    pass


def run(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        list(args),
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and proc.returncode != 0:
        raise ScanError(proc.stderr.strip() or proc.stdout.strip() or "command failed")
    return proc


def discover_root(start: str) -> Path:
    path = Path(start).expanduser().resolve()
    proc = run(path, "git", "rev-parse", "--show-toplevel", check=False)
    if proc.returncode != 0:
        raise ScanError(f"not a git repository: {path}")
    return Path(proc.stdout.strip()).resolve()


def parse_name_status(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        if status.startswith("R") or status.startswith("C"):
            if len(parts) >= 3:
                rows.append({"status": status, "old_path": parts[1], "path": parts[2]})
        elif len(parts) >= 2:
            rows.append({"status": status, "path": parts[1]})
    return rows


def changed_paths(root: Path, base: str | None, head: str | None) -> list[dict[str, str]]:
    if base:
        target = head or "HEAD"
        proc = run(root, "git", "diff", "--name-status", f"{base}...{target}", "--")
        rows = parse_name_status(proc.stdout)
    else:
        rows = parse_name_status(run(root, "git", "diff", "--name-status", "HEAD", "--").stdout)
        rows += parse_name_status(run(root, "git", "diff", "--cached", "--name-status", "--").stdout)
        untracked = run(root, "git", "ls-files", "--others", "--exclude-standard").stdout
        rows += [{"status": "??", "path": line} for line in untracked.splitlines() if line.strip()]

    dedup: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in rows:
        key = (row.get("status", ""), row.get("old_path", ""), row.get("path", ""))
        dedup[key] = row
    return sorted(dedup.values(), key=lambda row: (row.get("path", ""), row.get("status", "")))


def walk_files(root: Path, max_bytes: int) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in EXCLUDED_DIRS]
        base = Path(dirpath)
        for name in filenames:
            path = base / name
            try:
                if path.is_symlink() or path.stat().st_size > max_bytes:
                    continue
            except OSError:
                continue
            yield path


def is_contract_candidate(path: Path, root: Path) -> bool:
    rel = path.relative_to(root).as_posix()
    name = path.name
    if name in {"build.zig", "build.zig.zon", "AGENTS.md"}:
        return True
    if CONTRACT_NAME_RE.search(rel):
        return True
    if path.suffix in {".yml", ".yaml"} and (".github/workflows/" in rel or "ci" in rel.lower()):
        return True
    return False


def relevant_change(path_text: str) -> bool:
    path = Path(path_text)
    if path.name in {"build.zig", "build.zig.zon"}:
        return True
    if path.suffix in RELEVANT_SUFFIXES:
        return True
    lower = path_text.lower()
    return any(token in lower for token in ("testdata/", "fixtures/", "examples/", "generated/"))


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def references_for(change: dict[str, str], candidates: list[Path], root: Path) -> list[dict[str, str]]:
    path_text = change["path"]
    old_path = change.get("old_path")
    needles = {
        path_text,
        Path(path_text).name,
        Path(path_text).stem,
    }
    if old_path:
        needles.update({old_path, Path(old_path).name, Path(old_path).stem})
    needles = {needle for needle in needles if len(needle) >= 3}

    hits: list[dict[str, str]] = []
    for candidate in candidates:
        rel = candidate.relative_to(root).as_posix()
        if rel == path_text or rel == old_path:
            continue
        text = read_text(candidate)
        if text is None:
            continue
        for needle in sorted(needles, key=len, reverse=True):
            if needle in text:
                hits.append({"contract_path": rel, "matched": needle})
                break
    return hits


def repository_fingerprint(root: Path, candidates: list[Path]) -> str:
    h = hashlib.sha256()
    for path in sorted(candidates):
        rel = path.relative_to(root).as_posix()
        h.update(rel.encode())
        try:
            h.update(path.read_bytes())
        except OSError:
            continue
    return "sha256:" + h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--base")
    parser.add_argument("--head")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--max-file-bytes", type=int, default=2_000_000)
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()

    try:
        root = discover_root(args.root)
        changes = [row for row in changed_paths(root, args.base, args.head) if relevant_change(row["path"])]
        files = list(walk_files(root, args.max_file_bytes))
        candidates = [path for path in files if is_contract_candidate(path, root)]

        rows = []
        likely_gaps = []
        has_registry_like = any(
            CONTRACT_NAME_RE.search(path.relative_to(root).as_posix()) for path in candidates
        )
        for change in changes:
            refs = references_for(change, candidates, root)
            row = {**change, "contract_references": refs}
            rows.append(row)
            added_or_moved = change["status"].startswith(("A", "R", "C")) or change["status"] == "??"
            if added_or_moved and has_registry_like and not refs:
                likely_gaps.append(change["path"])

        result = {
            "zig_repo_closure_scan": {
                "root": str(root),
                "base": args.base,
                "head": args.head,
                "contract_fingerprint": repository_fingerprint(root, candidates),
                "contract_candidates": [
                    path.relative_to(root).as_posix() for path in sorted(candidates)
                ],
                "changes": rows,
                "likely_unregistered_paths": likely_gaps,
                "verdict": "review-required" if changes else "no-relevant-changes",
                "limitations": [
                    "Name/reference matching is a locator, not proof of repository closure.",
                    "Generated ownership and dynamic build enumeration require manual inspection.",
                ],
            }
        }

        if args.format == "json":
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            body = result["zig_repo_closure_scan"]
            print(f"root: {body['root']}")
            print(f"verdict: {body['verdict']}")
            for row in rows:
                print(f"- {row['status']} {row['path']}: {len(row['contract_references'])} contract refs")
            for path in likely_gaps:
                print(f"LIKELY_UNREGISTERED: {path}")

        return 2 if args.strict and likely_gaps else 0
    except ScanError as exc:
        print(json.dumps({"zig_repo_closure_scan": {"verdict": "error", "error": str(exc)}}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
