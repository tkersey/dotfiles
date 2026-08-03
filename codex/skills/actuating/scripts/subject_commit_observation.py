#!/usr/bin/env python3
"""Prove a scoped Actuating subject advanced only by a direct Git commit."""
from __future__ import annotations

import argparse
import copy
import json
import os
import stat
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
    projected_scopes,
    relevant,
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
    actual: dict[str, dict[str, Any]] = {}
    for entry in observation["entries"]:
        if entry["source"] not in {"tracked", "untracked"}:
            continue
        if entry["worktree"]["kind"] == "deleted":
            continue
        path = entry["path_hex"]
        previous = actual.get(path)
        if previous is not None and previous != entry["worktree"]:
            raise ObservationError("conflicting worktree states for one scoped path")
        actual[path] = entry["worktree"]

    rows_by_path: dict[str, dict[str, Any]] = dict(actual)
    for entry in observation["entries"]:
        source = entry["source"]
        worktree = entry["worktree"]
        path = entry["path_hex"]
        if source in {"tracked", "untracked"}:
            continue
        if source != "scope":
            raise ObservationError("unsupported scoped entry source")
        if path in actual or worktree["kind"] == "file":
            continue
        previous = rows_by_path.get(path)
        if previous is not None and previous != worktree:
            raise ObservationError("conflicting scope states for one scoped path")
        rows_by_path[path] = worktree
    rows = [
        {"path_hex": path, "worktree": worktree}
        for path, worktree in rows_by_path.items()
    ]
    rows.sort(key=lambda row: bytes.fromhex(row["path_hex"]))
    return digest_bytes(canonical_bytes(rows))


def direct_parent(repo: bytes, after_head: str) -> str:
    fields = run_git(
        repo,
        b"--no-replace-objects",
        b"rev-list",
        b"--parents",
        b"-n",
        b"1",
        after_head.encode("ascii"),
    ).split()
    if len(fields) != 2:
        raise ObservationError("successor HEAD must have exactly one parent")
    return fields[1].decode("ascii")


def pathspecs(scope: dict[str, Any]) -> list[bytes]:
    allowed = [os.fsencode(path) for path in scope["allowed_paths"]]
    prohibited = [os.fsencode(path) for path in scope["prohibited_paths"]]
    return [b":(literal)" + path for path in allowed] + [
        b":(exclude,literal)" + path for path in prohibited + list(CONTROL_ROOTS)
    ]


def projected_entry(
    path: bytes,
    mode: str,
    allowed: list[bytes],
    prohibited: list[bytes],
) -> bool:
    return selected(path, allowed, prohibited) or (
        mode == "160000" and relevant(path, allowed, prohibited)
    )


def head_tree(repo: bytes, scope: dict[str, Any]) -> dict[bytes, tuple[str, str]]:
    allowed = [os.fsencode(path) for path in scope["allowed_paths"]]
    prohibited = [os.fsencode(path) for path in scope["prohibited_paths"]]
    roots = sorted(
        {
            path if path == b"." else path.split(b"/", 1)[0]
            for path in allowed
        }
    )
    output = run_git(
        repo,
        b"--no-replace-objects",
        b"ls-tree",
        b"-r",
        b"-z",
        b"--full-tree",
        b"HEAD",
        b"--",
        *(b":(literal)" + path for path in roots),
    )
    result: dict[bytes, tuple[str, str]] = {}
    for record in output.split(b"\0"):
        if not record:
            continue
        header, separator, path = record.partition(b"\t")
        fields = header.split(b" ")
        if not separator or len(fields) != 3:
            raise ObservationError("malformed HEAD tree record")
        mode, kind, object_id = (field.decode("ascii") for field in fields)
        if not projected_entry(path, mode, allowed, prohibited):
            continue
        if kind not in {"blob", "commit"} or path in result:
            raise ObservationError("unsupported or duplicate HEAD tree record")
        result[path] = (mode, object_id)
    return result


def tracked_index(
    observation: dict[str, Any], scope: dict[str, Any]
) -> dict[bytes, dict[str, Any]]:
    allowed = [os.fsencode(path) for path in scope["allowed_paths"]]
    prohibited = [os.fsencode(path) for path in scope["prohibited_paths"]]
    result: dict[bytes, dict[str, Any]] = {}
    for entry in observation["entries"]:
        if entry["source"] != "tracked":
            continue
        path = bytes.fromhex(entry["path_hex"])
        index = entry["index"]
        if index is None or not projected_entry(path, index["mode"], allowed, prohibited):
            continue
        if index["stage"] != 0 or path in result:
            raise ObservationError("successor index is unmerged or duplicated within the subject scope")
        result[path] = entry
    return result


def require_clean(repo: bytes, observation: dict[str, Any], scope: dict[str, Any]) -> None:
    if any(entry["source"] == "untracked" for entry in observation["entries"]):
        raise ObservationError("successor worktree has untracked paths within the subject scope")
    ignored = run_git(
        repo,
        b"ls-files",
        b"--others",
        b"--ignored",
        b"--exclude-standard",
        b"-z",
        b"--",
        *pathspecs(scope),
    )
    if ignored:
        raise ObservationError("successor worktree has ignored paths within the subject scope")

    index_entries = tracked_index(observation, scope)
    tree_entries = head_tree(repo, scope)
    index_tree = {
        path: (entry["index"]["mode"], entry["index"]["object_id"])
        for path, entry in index_entries.items()
    }
    if tree_entries != index_tree:
        raise ObservationError("successor index differs from HEAD within the subject scope")

    allowed = [os.fsencode(path) for path in scope["allowed_paths"]]
    prohibited = [os.fsencode(path) for path in scope["prohibited_paths"]]
    for path, entry in index_entries.items():
        index = entry["index"]
        worktree = entry["worktree"]
        if worktree["kind"] == "deleted":
            raise ObservationError("successor worktree has a deleted tracked path within the subject scope")
        if index["mode"] == "160000":
            if worktree["kind"] != "gitlink" or worktree["head"] != index["object_id"]:
                raise ObservationError("successor gitlink differs from the index")
            nested_allowed = projected_scopes(path, allowed)
            nested_prohibited = projected_scopes(path, prohibited)
            nested = observe(
                Path(os.fsdecode(os.path.join(repo, path))),
                f"gitlink:{path.hex()}",
                nested_allowed,
                nested_prohibited,
            )
            require_clean(
                os.path.join(repo, path),
                nested,
                {
                    "allowed_paths": nested_allowed,
                    "prohibited_paths": nested_prohibited,
                },
            )
            continue
        if worktree["kind"] != "file":
            raise ObservationError("successor worktree entry has an unsupported kind")
        if index["mode"] not in {"100644", "100755"}:
            raise ObservationError("successor index mode is incompatible with a regular file")
        object_id = run_git(
            repo,
            b"hash-object",
            b"--path=" + path,
            b"--",
            path,
        ).strip().decode("ascii")
        if object_id != index["object_id"]:
            raise ObservationError("successor worktree content differs from the index")
        expected_executable = index["mode"] == "100755"
        metadata = os.lstat(os.path.join(repo, path))
        owner_executable = bool(metadata.st_mode & stat.S_IXUSR)
        if owner_executable != expected_executable:
            raise ObservationError("successor worktree mode differs from the index")


def changed_paths(repo: bytes, before_head: str, after_head: str, scope: dict[str, Any]) -> list[str]:
    allowed = [os.fsencode(path) for path in scope["allowed_paths"]]
    prohibited = [os.fsencode(path) for path in scope["prohibited_paths"]]
    output = run_git(
        repo,
        b"--no-replace-objects",
        b"diff-tree",
        b"--no-commit-id",
        b"--name-only",
        b"-r",
        b"-z",
        b"--ignore-submodules=none",
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
    require_clean(repo_bytes, after, scope)
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
