#!/usr/bin/env python3
"""Emit a deterministic, scoped Git subject observation for Actuating."""
from __future__ import annotations
import argparse
import hashlib
import json
import ntpath
import os
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any
SCHEMA = "actuating-subject-observation/v1"
CONTROL_ROOTS = (b".git", b".ledger")
class ObservationError(RuntimeError):
    pass
def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
def digest_bytes(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"
def validate_path(value: str) -> str:
    if value == ".": return value
    drive, _ = ntpath.splitdrive(value)
    if not value or value.startswith("/") or value.endswith("/") or "\\" in value or drive:
        raise ObservationError(f"invalid repository path: {value!r}")
    if any(part in {"", ".", ".."} for part in value.split("/")):
        raise ObservationError(f"invalid repository path: {value!r}")
    return value
def canonical_scope(values: list[str], *, require_nonempty: bool) -> list[str]:
    result = sorted({validate_path(value) for value in values})
    if require_nonempty and not result:
        raise ObservationError("at least one --allow path is required")
    return result
def within(path: bytes, scope: bytes) -> bool:
    return scope == b"." or path == scope or path.startswith(scope + b"/")
def projected_scopes(path: bytes, scopes: list[bytes]) -> list[str]:
    projected: set[str] = set()
    for scope in scopes:
        if scope == b"." or within(path, scope): projected.add(".")
        elif within(scope, path): projected.add(os.fsdecode(scope[len(path) + 1:]))
    return sorted(projected)
def validate_scope_paths(repo: bytes, allowed: list[str], prohibited: list[str]) -> None:
    for value in allowed:
        encoded = os.fsencode(value)
        if any(within(encoded.lower(), control) for control in CONTROL_ROOTS):
            raise ObservationError(f"allowed path enters control root: {value!r}")
    for value in allowed + prohibited:
        current = repo
        for part in [] if value == "." else os.fsencode(value).split(b"/"):
            try: names = os.listdir(current)
            except NotADirectoryError: raise ObservationError(f"scope path traverses non-directory: {value!r}") from None
            if part not in names:
                folded = os.fsdecode(part).casefold()
                if any(os.fsdecode(name).casefold() == folded for name in names):
                    raise ObservationError(f"scope path spelling mismatch: {value!r}")
                break
            current = os.path.join(current, part)
            try: metadata = os.lstat(current)
            except FileNotFoundError: break
            if stat.S_ISLNK(metadata.st_mode): raise ObservationError(f"scope path traverses symlink: {value!r}")
def selected(path: bytes, allowed: list[bytes], prohibited: list[bytes]) -> bool:
    folded = path.lower()
    if any(within(folded, control) for control in CONTROL_ROOTS): return False
    if any(within(path, scope) for scope in prohibited): return False
    return any(within(path, scope) for scope in allowed)
def relevant(path: bytes, allowed: list[bytes], prohibited: list[bytes]) -> bool:
    blocked = any(within(path, scope) for scope in prohibited)
    return selected(path, allowed, prohibited) or (not blocked and bool(projected_scopes(path, allowed)))
def git_result(repo: bytes, *args: bytes) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run([b"git", b"-C", repo, *args], check=False,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
def run_git(repo: bytes, *args: bytes) -> bytes:
    process = git_result(repo, *args)
    if process.returncode != 0:
        message = process.stderr.decode("utf-8", "replace").strip()
        raise ObservationError(f"git command failed: {message}")
    return process.stdout
def head_identity(repo: bytes) -> str:
    result = git_result(repo, b"rev-parse", b"--verify", b"HEAD")
    if result.returncode == 0: return result.stdout.strip().decode("ascii")
    symbolic = git_result(repo, b"symbolic-ref", b"-q", b"HEAD")
    if symbolic.returncode == 0:
        return f"unborn:{symbolic.stdout.strip().decode('utf-8')}"
    message = result.stderr.decode("utf-8", "replace").strip()
    raise ObservationError(f"git command failed: {message}")
def head_ref(repo: bytes) -> str | None:
    symbolic = git_result(repo, b"symbolic-ref", b"-q", b"HEAD")
    return symbolic.stdout.strip().decode("utf-8") if symbolic.returncode == 0 else None
def file_digest(path: bytes) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while chunk := handle.read(1024 * 1024): digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"
def worktree_state(repo: bytes, path: bytes, index_mode: str | None,
                   allowed: list[bytes], prohibited: list[bytes]) -> dict[str, Any]:
    absolute = os.path.join(repo, path)
    try: metadata = os.lstat(absolute)
    except FileNotFoundError:
        return {"content_digest": None, "executable": False, "kind": "deleted"}
    if index_mode == "160000":
        if not stat.S_ISDIR(metadata.st_mode):
            raise ObservationError(f"unsupported gitlink worktree entry: {path.hex()}")
        nested = capture(Path(os.fsdecode(absolute)), f"gitlink:{path.hex()}",
                         projected_scopes(path, allowed), projected_scopes(path, prohibited))
        return {
            "content_digest": digest_bytes(canonical_bytes(nested)),
            "executable": False, "head": nested["head"], "head_ref": nested["head_ref"], "kind": "gitlink",
        }
    executable = bool(metadata.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
    if stat.S_ISREG(metadata.st_mode):
        if metadata.st_nlink > 1: raise ObservationError(f"hard-linked worktree entry: {path.hex()}")
        return {"content_digest": file_digest(absolute), "executable": executable, "kind": "file"}
    if stat.S_ISLNK(metadata.st_mode): raise ObservationError(f"symlinked worktree entry: {path.hex()}")
    raise ObservationError(f"unsupported worktree entry: {path.hex()}")
def scope_entries(repo: bytes, allowed: list[bytes], prohibited: list[bytes]) -> list[dict[str, Any]]:
    paths: set[bytes] = set()
    for scope in allowed:
        if scope == b".": paths.add(scope)
        else:
            parts = scope.split(b"/")
            paths.update(b"/".join(parts[:index]) for index in range(1, len(parts) + 1))
    entries: list[dict[str, Any]] = []
    for path in sorted(paths):
        if path != b"." and not relevant(path, allowed, prohibited): continue
        absolute = repo if path == b"." else os.path.join(repo, path)
        try: metadata = os.lstat(absolute)
        except FileNotFoundError: kind = "missing"
        else:
            if stat.S_ISLNK(metadata.st_mode): raise ObservationError(f"symlinked scope entry: {path.hex()}")
            if stat.S_ISREG(metadata.st_mode) and metadata.st_nlink > 1: raise ObservationError(f"hard-linked scope entry: {path.hex()}")
            if stat.S_ISDIR(metadata.st_mode): kind = "directory"
            elif stat.S_ISREG(metadata.st_mode): kind = "file"
            else: raise ObservationError(f"unsupported scope entry: {path.hex()}")
        entries.append({"index": None, "path_hex": path.hex(), "source": "scope", "worktree": {"kind": kind}})
    return entries
def tracked_entries(repo: bytes, allowed: list[bytes], prohibited: list[bytes]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for record in run_git(repo, b"ls-files", b"-v", b"-z").split(b"\0"):
        if record and relevant(record[2:], allowed, prohibited) and record[:1] != b"H":
            raise ObservationError(f"unsupported index flag: {record[:1].decode('ascii')}")
    for record in run_git(repo, b"ls-files", b"--stage", b"-z").split(b"\0"):
        if not record: continue
        header, separator, path = record.partition(b"\t")
        if not separator: raise ObservationError("malformed git index record")
        fields = header.split(b" ")
        if len(fields) != 3: raise ObservationError("malformed git index header")
        mode, object_id, stage = (field.decode("ascii") for field in fields)
        if not relevant(path, allowed, prohibited): continue
        entries.append({"index": {"mode": mode, "object_id": object_id, "stage": int(stage)},
                        "path_hex": path.hex(), "source": "tracked",
                        "worktree": worktree_state(repo, path, mode, allowed, prohibited)})
    return entries
def untracked_entries(repo: bytes, allowed: list[bytes], prohibited: list[bytes]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    output = run_git(repo, b"ls-files", b"--others", b"-z")
    for path in output.split(b"\0"):
        if not path or not selected(path, allowed, prohibited): continue
        entries.append({"index": None, "path_hex": path.hex(), "source": "untracked",
                        "worktree": worktree_state(repo, path, None, allowed, prohibited)})
    return entries
def capture(repo: Path, repository_id: str, allowed_paths: list[str],
            prohibited_paths: list[str]) -> dict[str, Any]:
    resolved_repo = repo.resolve()
    repo_bytes = os.fsencode(resolved_repo)
    if not repository_id.strip(): raise ObservationError("repository identity must be nonblank")
    root_bytes = run_git(repo_bytes, b"rev-parse", b"--show-toplevel").strip()
    if Path(os.fsdecode(root_bytes)).resolve() != resolved_repo:
        raise ObservationError("--repo must name the repository root")
    validate_scope_paths(repo_bytes, allowed_paths, prohibited_paths)
    allowed = [os.fsencode(path) for path in allowed_paths]
    prohibited = [os.fsencode(path) for path in prohibited_paths]
    entries = scope_entries(repo_bytes, allowed, prohibited) + tracked_entries(repo_bytes, allowed, prohibited)
    entries += untracked_entries(repo_bytes, allowed, prohibited)
    entries.sort(key=lambda entry: (bytes.fromhex(entry["path_hex"]), entry["source"],
                                    -1 if entry["index"] is None else entry["index"]["stage"]))
    return {
        "entries": entries, "head": head_identity(repo_bytes), "head_ref": head_ref(repo_bytes),
        "repository_id": repository_id, "schema": SCHEMA,
        "repository_root_digest": digest_bytes(repo_bytes),
        "scope": {
            "allowed_paths": allowed_paths,
            "implicit_exclusions": [".git", ".ledger"],
            "prohibited_paths": prohibited_paths,
        },
        "subject_digest": None,
    }
def observe(repo: Path, repository_id: str, allowed_paths: list[str],
            prohibited_paths: list[str]) -> dict[str, Any]:
    first = capture(repo, repository_id, allowed_paths, prohibited_paths)
    second = capture(repo, repository_id, allowed_paths, prohibited_paths)
    if canonical_bytes(first) != canonical_bytes(second):
        raise ObservationError("repository changed during double capture")
    first["subject_digest"] = digest_bytes(canonical_bytes(first))
    return first
def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--repository-id", required=True)
    parser.add_argument("--allow", action="append", default=[])
    parser.add_argument("--prohibit", action="append", default=[])
    return parser.parse_args(argv)
def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        allowed = canonical_scope(args.allow, require_nonempty=True)
        prohibited = canonical_scope(args.prohibit, require_nonempty=False)
        observation = observe(args.repo, args.repository_id, allowed, prohibited)
    except ObservationError as error:
        print(f"subject-observation: {error}", file=sys.stderr)
        return 2
    sys.stdout.buffer.write(canonical_bytes(observation) + b"\n")
    return 0
if __name__ == "__main__": raise SystemExit(main())
