#!/usr/bin/env python3
"""Prove a scoped Actuating subject advanced only by a direct Git commit."""
from __future__ import annotations

import argparse
import copy
import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any

from subject_observation import (
    CONTROL_ROOTS,
    ObservationError,
    _legacy_tracked_control_projection,
    canonical_bytes,
    canonical_scope,
    digest_bytes,
    observe,
    projected_scopes,
    relevant,
    run_git,
    selected,
    within,
)

SCHEMA = "actuating-subject-commit-observation/v1"
INPUT_SCHEMA = "actuating-subject-commit-input/v1"


def validate_before(value: Any) -> dict[str, Any]:
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


def validate_witness(row: Any, *, top_level: bool) -> dict[str, Any]:
    expected = {"nested_gitlinks", "projection"}
    if top_level:
        expected.add("path_hex")
    if not isinstance(row, dict) or set(row) != expected:
        raise ObservationError("prior commit input has malformed witness")
    if top_level:
        path_hex = row.get("path_hex")
        if not isinstance(path_hex, str):
            raise ObservationError("prior commit input has malformed witness")
        try:
            bytes.fromhex(path_hex)
        except ValueError as error:
            raise ObservationError("prior commit input has invalid witness path") from error
    if not isinstance(row.get("projection"), dict) or not isinstance(
        row.get("nested_gitlinks"), list
    ):
        raise ObservationError("prior commit input has malformed witness")
    for nested in row["nested_gitlinks"]:
        validate_witness(nested, top_level=True)
    return row


def load_before(path: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    try:
        value = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError) as error:
        raise ObservationError(f"invalid prior observation: {error}") from error
    if isinstance(value, dict) and value.get("schema") == INPUT_SCHEMA:
        if set(value) != {"legacy_gitlink_witnesses", "observation", "schema"}:
            raise ObservationError("prior commit input has unexpected fields")
        observation = validate_before(value.get("observation"))
        rows = value.get("legacy_gitlink_witnesses")
        if not isinstance(rows, list):
            raise ObservationError("prior commit input has malformed witnesses")
        witnesses: dict[str, dict[str, Any]] = {}
        for row in rows:
            validate_witness(row, top_level=True)
            path_hex = row["path_hex"]
            if path_hex in witnesses:
                raise ObservationError("prior commit input has duplicate witness path")
            witnesses[path_hex] = row
        return observation, witnesses
    return validate_before(value), {}


def prepare_commit_input(repo: Path, before_path: Path) -> dict[str, Any]:
    before, existing = load_before(before_path)
    if existing:
        return {
            "legacy_gitlink_witnesses": [
                witness for _, witness in sorted(existing.items())
            ],
            "observation": before,
            "schema": INPUT_SCHEMA,
        }
    scope = before.get("scope")
    if not isinstance(scope, dict):
        raise ObservationError("prior observation has malformed scope")
    allowed = [os.fsencode(path) for path in scope.get("allowed_paths", [])]
    prohibited = [os.fsencode(path) for path in scope.get("prohibited_paths", [])]
    rows: list[dict[str, Any]] = []
    for entry in before.get("entries", []):
        index = entry.get("index")
        worktree = entry.get("worktree")
        if (
            entry.get("source") != "tracked"
            or not isinstance(index, dict)
            or index.get("mode") != "160000"
            or not isinstance(worktree, dict)
        ):
            continue
        path = bytes.fromhex(entry["path_hex"])
        nested = capture_legacy_witness(
            repo / os.fsdecode(path),
            f"gitlink:{path.hex()}",
            projected_scopes(path, allowed),
            projected_scopes(path, prohibited),
        )
        if digest_bytes(canonical_bytes(nested["projection"])) != worktree.get("content_digest"):
            continue
        rows.append({"path_hex": path.hex(), **nested})
    return {
        "legacy_gitlink_witnesses": rows,
        "observation": before,
        "schema": INPUT_SCHEMA,
    }


def semantic_worktree_digest(observation: dict[str, Any]) -> str:
    actual: dict[str, dict[str, Any]] = {}
    for entry in observation["entries"]:
        path = bytes.fromhex(entry["path_hex"]).lower()
        if any(within(path, control) for control in CONTROL_ROOTS):
            continue
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
        encoded_path = bytes.fromhex(entry["path_hex"]).lower()
        if any(within(encoded_path, control) for control in CONTROL_ROOTS):
            continue
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


def capture_legacy_witness(
    repo: Path,
    repository_id: str,
    allowed_paths: list[str],
    prohibited_paths: list[str],
) -> dict[str, Any]:
    projection = _legacy_tracked_control_projection(
        repo, repository_id, allowed_paths, prohibited_paths
    )
    allowed = [os.fsencode(path) for path in allowed_paths]
    prohibited = [os.fsencode(path) for path in prohibited_paths]
    nested_gitlinks: list[dict[str, Any]] = []
    for entry in projection["entries"]:
        index = entry.get("index")
        worktree = entry.get("worktree")
        if (
            entry.get("source") != "tracked"
            or not isinstance(index, dict)
            or index.get("mode") != "160000"
            or not isinstance(worktree, dict)
        ):
            continue
        path = bytes.fromhex(entry["path_hex"])
        child = capture_legacy_witness(
            repo / os.fsdecode(path),
            f"gitlink:{path.hex()}",
            projected_scopes(path, allowed),
            projected_scopes(path, prohibited),
        )
        if digest_bytes(canonical_bytes(child["projection"])) != worktree.get(
            "content_digest"
        ):
            raise ObservationError("nested compatibility witness does not match its parent")
        nested_gitlinks.append({"path_hex": path.hex(), **child})
    return {"nested_gitlinks": nested_gitlinks, "projection": projection}


def semantic_projection_from_witness(witness: dict[str, Any]) -> dict[str, Any]:
    projection = copy.deepcopy(witness["projection"])
    nested = {
        row["path_hex"]: row
        for row in witness["nested_gitlinks"]
    }
    if len(nested) != len(witness["nested_gitlinks"]):
        raise ObservationError("prior commit input has duplicate nested witness path")
    rows: list[dict[str, Any]] = []
    for entry in projection.get("entries", []):
        path = bytes.fromhex(entry["path_hex"])
        if any(within(path.lower(), control) for control in CONTROL_ROOTS):
            nested.pop(entry["path_hex"], None)
            continue
        index = entry.get("index")
        worktree = entry.get("worktree")
        if (
            entry.get("source") == "tracked"
            and isinstance(index, dict)
            and index.get("mode") == "160000"
            and isinstance(worktree, dict)
        ):
            child = nested.pop(entry["path_hex"], None)
            if child is None:
                raise ObservationError("prior commit input is missing a nested witness")
            if digest_bytes(canonical_bytes(child["projection"])) != worktree.get(
                "content_digest"
            ):
                raise ObservationError("prior commit input nested witness digest mismatch")
            worktree["content_digest"] = digest_bytes(
                canonical_bytes(semantic_projection_from_witness(child))
            )
        rows.append(entry)
    if nested:
        raise ObservationError("prior commit input has an unused nested witness")
    projection["entries"] = rows
    return projection


def normalize_legacy_gitlink_digests(
    repo: bytes,
    before: dict[str, Any],
    after: dict[str, Any],
    scope: dict[str, Any],
    witnesses: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    normalized = copy.deepcopy(before)
    after_entries = {
        (entry["source"], entry["path_hex"]): entry
        for entry in after["entries"]
    }
    allowed = [os.fsencode(path) for path in scope["allowed_paths"]]
    prohibited = [os.fsencode(path) for path in scope["prohibited_paths"]]
    for entry in normalized["entries"]:
        index = entry.get("index")
        if entry["source"] != "tracked" or index is None or index["mode"] != "160000":
            continue
        successor = after_entries.get((entry["source"], entry["path_hex"]))
        if successor is None:
            continue
        retained_worktree = entry["worktree"]
        successor_worktree = successor["worktree"]
        if retained_worktree == successor_worktree:
            continue
        retained_shape = dict(retained_worktree)
        successor_shape = dict(successor_worktree)
        retained_digest = retained_shape.pop("content_digest", None)
        successor_digest = successor_shape.pop("content_digest", None)
        if retained_shape != successor_shape or not isinstance(retained_digest, str):
            continue
        path = bytes.fromhex(entry["path_hex"])
        nested_repo = Path(os.fsdecode(os.path.join(repo, path)))
        nested_allowed = projected_scopes(path, allowed)
        nested_prohibited = projected_scopes(path, prohibited)
        legacy_nested = _legacy_tracked_control_projection(
            nested_repo,
            f"gitlink:{path.hex()}",
            nested_allowed,
            nested_prohibited,
        )
        witness = witnesses.pop(entry["path_hex"], None)
        if (
            witness is not None
            and digest_bytes(canonical_bytes(witness["projection"])) != retained_digest
        ):
            raise ObservationError("prior commit input witness digest does not match the observation")
        if witness is not None:
            semantic_witness = semantic_projection_from_witness(witness)
            semantic_current = observe(
                nested_repo,
                f"gitlink:{path.hex()}",
                nested_allowed,
                nested_prohibited,
            )
            semantic_current["subject_digest"] = None
            if canonical_bytes(semantic_witness) != canonical_bytes(semantic_current):
                raise ObservationError("scoped worktree meaning changed across the commit")
        if digest_bytes(canonical_bytes(legacy_nested)) != retained_digest:
            if witness is None:
                continue
        retained_worktree["content_digest"] = successor_digest
    if witnesses:
        raise ObservationError("prior commit input has an unused witness")
    return normalized



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
    allowed: list[bytes],
    prohibited: list[bytes],
) -> bool:
    return relevant(path, allowed, prohibited)


def head_tree_queries(allowed: list[bytes]) -> tuple[list[bytes], list[bytes]]:
    recursive = sorted({b":(literal)" + path for path in allowed})
    ancestors: set[bytes] = set()
    for path in allowed:
        if path == b".":
            continue
        parts = path.split(b"/")
        ancestors.update(
            b":(literal)" + b"/".join(parts[:index])
            for index in range(1, len(parts))
        )
    return recursive, sorted(ancestors)


def head_tree(repo: bytes, scope: dict[str, Any]) -> dict[bytes, tuple[str, str]]:
    allowed = [os.fsencode(path) for path in scope["allowed_paths"]]
    prohibited = [os.fsencode(path) for path in scope["prohibited_paths"]]
    recursive, ancestors = head_tree_queries(allowed)
    outputs = [run_git(
        repo,
        b"--no-replace-objects",
        b"ls-tree",
        b"-r",
        b"-z",
        b"--full-tree",
        b"HEAD",
        b"--",
        *recursive,
    )]
    if ancestors:
        outputs.append(run_git(
            repo,
            b"--no-replace-objects",
            b"ls-tree",
            b"-z",
            b"--full-tree",
            b"HEAD",
            b"--",
            *ancestors,
        ))
    result: dict[bytes, tuple[str, str]] = {}
    for output in outputs:
        for record in output.split(b"\0"):
            if not record:
                continue
            header, separator, path = record.partition(b"\t")
            fields = header.split(b" ")
            if not separator or len(fields) != 3:
                raise ObservationError("malformed HEAD tree record")
            mode, kind, object_id = (field.decode("ascii") for field in fields)
            if kind == "tree" or not projected_entry(path, allowed, prohibited):
                continue
            if kind not in {"blob", "commit"}:
                raise ObservationError("unsupported HEAD tree record")
            value = (mode, object_id)
            previous = result.get(path)
            if previous is not None and previous != value:
                raise ObservationError("conflicting HEAD tree records")
            result[path] = value
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
        if index is None or not projected_entry(path, allowed, prohibited):
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
    before, witnesses = load_before(before_path)
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
    compatible_before = normalize_legacy_gitlink_digests(
        repo_bytes, before, after, scope, witnesses
    )
    before_worktree = semantic_worktree_digest(compatible_before)
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
    parser.add_argument(
        "--prepare-before",
        action="store_true",
        help="emit a digest-bound pre-commit input instead of observing a commit",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        observation = (
            prepare_commit_input(args.repo, args.before)
            if args.prepare_before
            else observe_commit(args.repo, args.before)
        )
    except ObservationError as error:
        print(f"subject-commit-observation: {error}", file=sys.stderr)
        return 2
    sys.stdout.buffer.write(canonical_bytes(observation) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
