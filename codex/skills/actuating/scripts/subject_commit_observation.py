#!/usr/bin/env python3
"""Prove a scoped Actuating subject advanced only by a direct Git commit."""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from pathlib import Path
from typing import Any

from subject_observation import (
    CONTROL_ROOTS,
    ObservationError,
    canonical_bytes,
    canonical_scope,
    digest_bytes,
    observe,
    run_git,
    selected,
)

SCHEMA = "actuating-subject-commit-observation/v1"


def load_before(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError) as error:
        raise ObservationError(f"invalid prior observation: {error}") from error
    if not isinstance(value, dict) or value.get("schema") != "actuating-subject-observation/v1":
        raise ObservationError("prior observation has the wrong schema")
    supplied_digest = value.get("subject_digest")
    if not isinstance(supplied_digest, str):
        raise ObservationError("prior observation has no subject digest")
    unhashed = copy.deepcopy(value)
    unhashed["subject_digest"] = None
    if digest_bytes(canonical_bytes(unhashed)) != supplied_digest:
        raise ObservationError("prior observation subject digest does not match its body")
    return value


def semantic_worktree_digest(observation: dict[str, Any]) -> str:
    actual_paths = {
        entry["path_hex"]
        for entry in observation["entries"]
        if entry["source"] in {"tracked", "untracked"}
    }
    rows: list[dict[str, Any]] = []
    for entry in observation["entries"]:
        source = entry["source"]
        worktree = entry["worktree"]
        if source == "scope" and (
            entry["path_hex"] in actual_paths or worktree["kind"] == "file"
        ):
            continue
        row = {"path_hex": entry["path_hex"], "worktree": worktree}
        if row in rows:
            continue
        rows.append(row)
    rows.sort(key=lambda row: (bytes.fromhex(row["path_hex"]), canonical_bytes(row["worktree"])))
    return digest_bytes(canonical_bytes(rows))


def direct_parent(repo: bytes, after_head: str) -> str:
    fields = run_git(repo, b"rev-list", b"--parents", b"-n", b"1", after_head.encode("ascii")).split()
    if len(fields) != 2:
        raise ObservationError("successor HEAD must have exactly one parent")
    return fields[1].decode("ascii")


def pathspecs(scope: dict[str, Any]) -> list[bytes]:
    allowed = [os.fsencode(path) for path in scope["allowed_paths"]]
    prohibited = [os.fsencode(path) for path in scope["prohibited_paths"]]
    return [b":(literal)" + path for path in allowed] + [
        b":(exclude,literal)" + path for path in prohibited + list(CONTROL_ROOTS)
    ]


def require_clean(repo: bytes, scope: dict[str, Any]) -> None:
    status = run_git(
        repo,
        b"status",
        b"--porcelain=v1",
        b"-z",
        b"--untracked-files=all",
        b"--",
        *pathspecs(scope),
    )
    if status:
        raise ObservationError("successor worktree is not clean within the subject scope")


def changed_paths(repo: bytes, before_head: str, after_head: str, scope: dict[str, Any]) -> list[str]:
    allowed = [os.fsencode(path) for path in scope["allowed_paths"]]
    prohibited = [os.fsencode(path) for path in scope["prohibited_paths"]]
    output = run_git(
        repo,
        b"diff-tree",
        b"--no-commit-id",
        b"--name-only",
        b"-r",
        b"-z",
        before_head.encode("ascii"),
        after_head.encode("ascii"),
    )
    paths = [path for path in output.split(b"\0") if path]
    outside = [path for path in paths if not selected(path, allowed, prohibited)]
    if outside:
        raise ObservationError(f"commit changes a path outside the subject scope: {outside[0].hex()}")
    if not paths:
        raise ObservationError("subject commit has no scoped changed paths")
    return sorted(os.fsdecode(path) for path in paths)


def capture(repo: Path, before_path: Path) -> dict[str, Any]:
    before = load_before(before_path)
    scope = before.get("scope")
    if not isinstance(scope, dict) or scope.get("implicit_exclusions") != [".git", ".ledger"]:
        raise ObservationError("prior observation has an unsupported scope")
    allowed = scope.get("allowed_paths")
    prohibited = scope.get("prohibited_paths")
    repository_id = before.get("repository_id")
    if not isinstance(allowed, list) or not isinstance(prohibited, list) or not isinstance(repository_id, str):
        raise ObservationError("prior observation has malformed repository or scope fields")
    if canonical_scope(allowed, require_nonempty=True) != allowed:
        raise ObservationError("prior observation allowed scope is not canonical")
    if canonical_scope(prohibited, require_nonempty=False) != prohibited:
        raise ObservationError("prior observation prohibited scope is not canonical")

    after = observe(repo, repository_id, allowed, prohibited)
    if after["repository_root_digest"] != before.get("repository_root_digest"):
        raise ObservationError("repository root changed")
    if after["head_ref"] != before.get("head_ref") or after["head_ref"] is None:
        raise ObservationError("symbolic HEAD changed or is detached")
    if after["scope"] != scope:
        raise ObservationError("subject scope changed")
    if after["subject_digest"] == before["subject_digest"]:
        raise ObservationError("subject did not advance")

    repo_bytes = os.fsencode(repo.resolve())
    parent = direct_parent(repo_bytes, after["head"])
    if parent != before.get("head"):
        raise ObservationError("successor HEAD is not the direct child of the prior HEAD")
    require_clean(repo_bytes, scope)
    before_worktree = semantic_worktree_digest(before)
    after_worktree = semantic_worktree_digest(after)
    if before_worktree != after_worktree:
        raise ObservationError("scoped worktree meaning changed across the commit")

    return {
        "after": {
            "head": after["head"],
            "parent": parent,
            "scoped_worktree_digest": after_worktree,
            "subject_digest": after["subject_digest"],
        },
        "before": {
            "head": before["head"],
            "scoped_worktree_digest": before_worktree,
            "subject_digest": before["subject_digest"],
        },
        "changed_paths": changed_paths(repo_bytes, before["head"], after["head"], scope),
        "clean_successor": True,
        "head_ref": after["head_ref"],
        "repository_id": repository_id,
        "repository_root_digest": after["repository_root_digest"],
        "schema": SCHEMA,
        "scope": {
            "allowed_paths": allowed,
            "prohibited_paths": prohibited,
        },
    }


def observe_commit(repo: Path, before_path: Path) -> dict[str, Any]:
    first = capture(repo, before_path)
    second = capture(repo, before_path)
    if canonical_bytes(first) != canonical_bytes(second):
        raise ObservationError("repository changed during double capture")
    return first


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--before", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        observation = observe_commit(args.repo, args.before)
    except ObservationError as error:
        print(f"subject-commit-observation: {error}", file=sys.stderr)
        return 2
    sys.stdout.buffer.write(canonical_bytes(observation) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
