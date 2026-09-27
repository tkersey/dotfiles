#!/usr/bin/env python3
"""Read-only locator for contracts affected by an explicit Zig change scope."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

CONTRACT_NAME_RE = re.compile(r"(manifest|registry|paths?|golden|expected|compile[-_ ]?fail|generated|fixture|snapshot|checksum)", re.I)
RELEVANT_SUFFIXES = {".zig", ".zon", ".golden", ".expected", ".out", ".stderr", ".stdout", ".json", ".yaml", ".yml", ".toml", ".md"}
EXCLUDED_DIRS = {".git", ".zig-cache", "zig-cache", "zig-out", "zig-pkg", "node_modules"}


class ScanError(RuntimeError):
    pass


def run(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    try:
        proc = subprocess.run(args, cwd=root, capture_output=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ScanError(str(exc)) from exc
    if check and proc.returncode:
        raise ScanError(os.fsdecode(proc.stderr).strip() or "command failed")
    return proc


def discover_root(start: str) -> Path:
    return Path(os.fsdecode(run(Path(start).expanduser().resolve(), "git", "rev-parse", "--show-toplevel").stdout).rstrip("\n")).resolve()


def parse_name_status(data: bytes) -> list[dict[str, str]]:
    fields = data.split(b"\0")
    if fields.pop() != b"":
        raise ScanError("unterminated Git path record")
    rows, index = [], 0
    while index < len(fields):
        status = fields[index].decode("ascii")
        width = 3 if status.startswith(("R", "C")) else 2
        if not re.fullmatch(r"[ACDMRTUXB][0-9]*", status) or index + width > len(fields):
            raise ScanError("malformed Git name-status record")
        row = {"status": status, "path": os.fsdecode(fields[index + width - 1])}
        if width == 3:
            row["old_path"] = os.fsdecode(fields[index + 1])
        rows.append(row)
        index += width
    return rows


def resolve_commit(root: Path, ref: str) -> str:
    return run(root, "git", "rev-parse", "--verify", "--end-of-options", ref + "^{commit}").stdout.decode().strip()


def changed_paths(root: Path, base: str | None, head: str | None) -> tuple[list[dict[str, str]], dict]:
    untracked = run(root, "git", "ls-files", "--others", "--exclude-standard", "-z").stdout
    current = run(root, "git", "rev-parse", "--verify", "HEAD", check=False)
    if base:
        base_sha, head_sha = resolve_commit(root, base), resolve_commit(root, head or "HEAD")
        if current.returncode or current.stdout.decode().strip() != head_sha:
            raise ScanError("review scope requires the checked-out HEAD to match --head")
        if run(root, "git", "status", "--porcelain", "-z").stdout:
            raise ScanError("review scope requires a clean worktree; use working-tree scope for uncommitted work")
        data = run(root, "git", "diff", "--name-status", "-z", "--find-renames", f"{base_sha}...{head_sha}", "--").stdout
        scope = {"kind": "review", "base": base_sha, "head": head_sha}
        return parse_name_status(data), scope
    if head:
        raise ScanError("--head requires --base")
    if current.returncode == 0:
        data = run(root, "git", "diff", "--name-status", "-z", "--find-renames", "HEAD", "--").stdout
    else:
        data = run(root, "git", "diff", "--cached", "--name-status", "-z", "--").stdout
    rows = parse_name_status(data)
    rows += [{"status": "??", "path": os.fsdecode(p)} for p in untracked.split(b"\0") if p]
    return rows, {"kind": "working-tree", "head": current.stdout.decode().strip() or None}


def relevant_change(path_text: str) -> bool:
    path = Path(path_text)
    return path.suffix in RELEVANT_SUFFIXES or any(x in path_text.lower() for x in ("testdata/", "fixtures/", "examples/", "generated/"))


def is_contract_candidate(path: Path, root: Path) -> bool:
    rel = path.relative_to(root).as_posix()
    return bool(path.name in {"build.zig", "build.zig.zon", "AGENTS.md"} or CONTRACT_NAME_RE.search(rel)
                or path.suffix in {".yml", ".yaml"} and (".github/workflows/" in rel or "ci" in rel.lower()))


def read_contracts(root: Path, max_bytes: int) -> tuple[dict[str, str], list[dict[str, str]], str]:
    texts, skipped = {}, []
    def walk_error(exc: OSError) -> None:
        skipped.append({"path": str(exc.filename), "reason": str(exc)})
    for dirpath, dirs, files in os.walk(root, onerror=walk_error):
        for name in dirs[:]:
            path = Path(dirpath) / name
            if name in EXCLUDED_DIRS:
                dirs.remove(name)
            elif path.is_symlink():
                dirs.remove(name)
                skipped.append({"path": str(path.relative_to(root)), "reason": "symlink directory not followed"})
        for name in files:
            path = Path(dirpath) / name
            if not is_contract_candidate(path, root):
                continue
            rel = path.relative_to(root).as_posix()
            try:
                if path.is_symlink():
                    raise ValueError("symlink not followed")
                if path.stat().st_size > max_bytes:
                    raise ValueError("exceeds --max-file-bytes")
                with path.open("rb") as handle:
                    raw = handle.read(max_bytes + 1)
                if len(raw) > max_bytes:
                    raise ValueError("exceeds --max-file-bytes")
                texts[rel] = raw.decode("utf-8")
            except (ValueError, OSError) as exc:
                skipped.append({"path": rel, "reason": str(exc)})
    digest = hashlib.sha256()
    for rel, text in sorted(texts.items()):
        for part in (os.fsencode(rel), text.encode("utf-8")):
            digest.update(len(part).to_bytes(8, "big"))
            digest.update(part)
    return texts, skipped, "sha256:" + digest.hexdigest()


def references_for(change: dict[str, str], texts: dict[str, str]) -> list[dict[str, str]]:
    paths = {change["path"], change.get("old_path", change["path"])}
    needles = {item for p in paths for item in (p, Path(p).name, Path(p).stem) if len(item) >= 3}
    hits = []
    for rel, text in sorted(texts.items()):
        if rel in paths:
            continue
        for needle in sorted(needles, key=lambda n: (-len(n), n)):
            if needle in text:
                hits.append({"contract_path": rel, "matched": needle})
                break
    return hits


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--base", help="review committed merge-base..head changes in a clean checkout")
    parser.add_argument("--head", help="defaults to HEAD; requires --base and a matching checkout")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--max-file-bytes", type=int, default=2_000_000)
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args(argv)
    if args.max_file_bytes <= 0:
        parser.error("--max-file-bytes must be positive")
    try:
        root = discover_root(args.root)
        changes, scope = changed_paths(root, args.base, args.head)
        changes = [c for c in changes if relevant_change(c["path"]) or relevant_change(c.get("old_path", ""))]
        texts, skipped, fingerprint = read_contracts(root, args.max_file_bytes)
        rows, gaps = [], []
        registry_exists = any(CONTRACT_NAME_RE.search(p) for p in texts)
        for change in changes:
            refs = references_for(change, texts)
            rows.append({**change, "contract_references": refs})
            if (change["status"].startswith(("A", "R", "C")) or change["status"] == "??") and registry_exists and not refs:
                gaps.append(change["path"])
        body = {
            "root": str(root), "base": args.base, "head": args.head, "scope": scope,
            "contract_fingerprint": fingerprint, "contract_candidates": sorted(texts),
            "changes": rows, "likely_unregistered_paths": gaps, "skipped": skipped,
            "coverage": "partial" if skipped else "complete-within-locator-scope",
            "verdict": "incomplete" if skipped else "review-required" if changes else "no-relevant-changes",
            "limitations": [
                "Name/reference matching is a locator, not proof of repository closure.",
                "Dynamic enumeration, excluded dependency/output directories and generated ownership require inspection.",
                "Working-tree scope does not review committed branch changes; supply --base in a clean checkout.",
            ],
        }
        if args.format == "json":
            print(json.dumps({"zig_repo_closure_scan": body}, indent=2, sort_keys=True))
        else:
            print(f"scope: {scope['kind']}\nverdict: {body['verdict']}")
            for row in rows:
                print(f"{row['status']} {row['path']!r}: {len(row['contract_references'])} contract refs")
            for item in skipped:
                print(f"SKIPPED: {item['path']!r}: {item['reason']}")
            for gap in gaps:
                print(f"LIKELY_UNREGISTERED: {gap!r}")
        return 1 if args.strict and skipped else 2 if args.strict and gaps else 0
    except (ScanError, OSError, ValueError) as exc:
        print(json.dumps({"zig_repo_closure_scan": {"verdict": "error", "error": str(exc)}}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
