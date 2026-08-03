#!/usr/bin/env python3
"""Prove a scoped Actuating subject advanced only by a direct Git commit."""
from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

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


def normalize_legacy_gitlink_digests(
    repo: bytes,
    before: dict[str, Any],
    after: dict[str, Any],
    scope: dict[str, Any],
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
        if digest_bytes(canonical_bytes(legacy_nested)) != retained_digest:
            index_candidates = current_index_legacy_projections(
                nested_repo,
                legacy_nested,
            )
            if not any(
                digest_bytes(canonical_bytes(candidate)) == retained_digest
                for candidate in index_candidates
            ):
                retained_head = retained_worktree.get("head")
                if not isinstance(retained_head, str):
                    continue
                retained_tree = retained_tree_legacy_projection(
                    nested_repo,
                    legacy_nested,
                    retained_head,
                    nested_allowed,
                    nested_prohibited,
                )
                if digest_bytes(canonical_bytes(retained_tree)) != retained_digest:
                    continue
        retained_worktree["content_digest"] = successor_digest
    return normalized


def legacy_projected_entry(
    path: bytes,
    allowed: list[bytes],
    prohibited: list[bytes],
) -> bool:
    if any(within(path, scope) for scope in prohibited):
        return False
    return any(within(path, scope) for scope in allowed) or bool(
        projected_scopes(path, allowed)
    )


def snapshot_git(
    repo: bytes,
    index_file: Path,
    worktree: Path,
    *args: bytes,
) -> bytes:
    environment = snapshot_environment(index_file, worktree)
    process = subprocess.run(
        [b"git", b"-C", repo, *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
    )
    if process.returncode != 0:
        message = process.stderr.decode("utf-8", "replace").strip()
        raise ObservationError(f"git snapshot command failed: {message}")
    return process.stdout


def snapshot_environment(index_file: Path, worktree: Path) -> dict[bytes, bytes]:
    environment = {
        os.fsencode(key): os.fsencode(value)
        for key, value in os.environ.items()
        if not key.startswith("GIT_")
    }
    environment[b"GIT_INDEX_FILE"] = os.fsencode(index_file)
    environment[b"GIT_WORK_TREE"] = os.fsencode(worktree)
    return environment


def snapshot_index_entries(
    repo: bytes,
    index_file: Path,
    worktree: Path,
) -> dict[bytes, tuple[str, str]]:
    entries: dict[bytes, tuple[str, str]] = {}
    output = snapshot_git(
        repo,
        index_file,
        worktree,
        b"--no-replace-objects",
        b"ls-files",
        b"--stage",
        b"-z",
    )
    for record in output.split(b"\0"):
        if not record:
            continue
        header, separator, path = record.partition(b"\t")
        fields = header.split(b" ")
        if not separator or len(fields) != 3:
            raise ObservationError("malformed snapshot index record")
        mode, object_id, stage = (field.decode("ascii") for field in fields)
        if stage != "0":
            continue
        value = (mode, object_id)
        previous = entries.get(path)
        if previous is not None and previous != value:
            raise ObservationError("conflicting snapshot index records")
        entries[path] = value
    return entries


def snapshot_destination(worktree: Path, path: bytes) -> Path:
    if path.startswith(b"/"):
        raise ObservationError("snapshot index path is absolute")
    parts = path.split(b"/")
    if not parts or any(part in {b"", b".", b".."} for part in parts):
        raise ObservationError("snapshot index path is not canonical")
    current = os.fsencode(worktree)
    for part in parts[:-1]:
        current = os.path.join(current, part)
        try:
            mode = os.lstat(current).st_mode
        except FileNotFoundError:
            os.mkdir(current, 0o755)
        else:
            if not stat.S_ISDIR(mode):
                raise ObservationError("snapshot index path crosses a non-directory")
    return Path(os.fsdecode(os.path.join(current, parts[-1])))


def write_snapshot_entry(
    worktree: Path,
    path: bytes,
    mode: str,
    blob: bytes,
) -> None:
    destination = snapshot_destination(worktree, path)
    try:
        if mode == "120000":
            os.symlink(blob, os.fsencode(destination))
            return
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(destination, flags, 0o755 if mode == "100755" else 0o644)
    except OSError as error:
        raise ObservationError(f"cannot materialize snapshot path: {error}") from error
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(blob)
    except BaseException:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise


def snapshot_blobs(
    repo: bytes,
    index_file: Path,
    worktree: Path,
    entries: dict[bytes, tuple[str, str]],
) -> Iterator[tuple[bytes, str, bytes]]:
    requested = [
        (path, mode, object_id)
        for path, (mode, object_id) in sorted(entries.items())
        if mode in {"100644", "100755", "120000"}
    ]
    request_file = tempfile.TemporaryFile()
    request_file.write(
        b"".join(object_id.encode("ascii") + b"\n" for _, _, object_id in requested)
    )
    request_file.seek(0)
    process = subprocess.Popen(
        [b"git", b"-C", repo, b"--no-replace-objects", b"cat-file", b"--batch"],
        stdin=request_file,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=snapshot_environment(index_file, worktree),
    )
    if process.stdout is None or process.stderr is None:
        process.kill()
        process.wait()
        request_file.close()
        raise ObservationError("git snapshot batch has no output channel")
    try:
        for path, mode, object_id in requested:
            header = process.stdout.readline().rstrip(b"\n").split(b" ")
            if len(header) != 3 or header[0] != object_id.encode("ascii") or header[1] != b"blob":
                raise ObservationError("git snapshot batch returned an unexpected object")
            try:
                length = int(header[2])
            except ValueError as error:
                raise ObservationError("git snapshot batch returned an invalid length") from error
            blob = process.stdout.read(length)
            if len(blob) != length or process.stdout.read(1) != b"\n":
                raise ObservationError("git snapshot batch returned a truncated object")
            yield path, mode, blob
        return_code = process.wait()
        if return_code != 0:
            message = process.stderr.read().decode("utf-8", "replace").strip()
            raise ObservationError(f"git snapshot batch failed: {message}")
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        request_file.close()


def materialize_snapshot_worktree(
    repo: bytes,
    index_file: Path,
    worktree: Path,
    entries: dict[bytes, tuple[str, str]],
) -> None:
    for path, mode, blob in snapshot_blobs(repo, index_file, worktree, entries):
        write_snapshot_entry(worktree, path, mode, blob)
    snapshot_git(
        repo,
        index_file,
        worktree,
        b"--no-replace-objects",
        b"checkout-index",
        b"--all",
        b"--force",
    )


def snapshot_has_custom_filter(
    repo: bytes,
    index_file: Path,
    worktree: Path,
    path: bytes,
) -> bool:
    output = snapshot_git(
        repo,
        index_file,
        worktree,
        b"--no-replace-objects",
        b"check-attr",
        b"--cached",
        b"-z",
        b"filter",
        b"--",
        path,
    ).split(b"\0")
    if len(output) != 4 or output[0] != path or output[1] != b"filter" or output[3] != b"":
        raise ObservationError("git snapshot returned malformed filter attributes")
    return output[2] not in {b"unspecified", b"unset"}


@contextmanager
def snapshot_checkout(
    repo: bytes,
    retained_head: str | None,
) -> Iterator[Any]:
    with tempfile.TemporaryDirectory(prefix="actuating-retained-") as directory:
        root = Path(directory)
        index_file = root / "index"
        worktree = root / "worktree"
        worktree.mkdir()
        if retained_head is None:
            live_index = Path(
                os.fsdecode(run_git(repo, b"rev-parse", b"--git-path", b"index").strip())
            )
            if not live_index.is_absolute():
                live_index = Path(os.fsdecode(repo)) / live_index
            try:
                shutil.copyfile(live_index, index_file)
            except OSError as error:
                raise ObservationError(f"cannot snapshot current index: {error}") from error
        else:
            snapshot_git(
                repo,
                index_file,
                worktree,
                b"--no-replace-objects",
                b"read-tree",
                retained_head.encode("ascii"),
            )

        entries = snapshot_index_entries(repo, index_file, worktree)
        checkout_materialized = False

        def filtered_blob(path: bytes) -> bytes:
            nonlocal checkout_materialized
            entry = entries.get(path)
            if entry is None or entry[0] not in {"100644", "100755"}:
                raise ObservationError("snapshot path is not a stage-zero regular file")
            if (
                not checkout_materialized
                and snapshot_has_custom_filter(repo, index_file, worktree, path)
            ):
                materialize_snapshot_worktree(repo, index_file, worktree, entries)
                checkout_materialized = True
            return snapshot_git(
                repo,
                index_file,
                worktree,
                b"--no-replace-objects",
                b"cat-file",
                b"--filters",
                b"--path=" + path,
                entry[1].encode("ascii"),
            )

        yield filtered_blob


def current_index_legacy_projections(
    repo: Path,
    live: dict[str, Any],
) -> list[dict[str, Any]]:
    live_mode_candidate = copy.deepcopy(live)
    index_mode_candidate = copy.deepcopy(live)
    try:
        with snapshot_checkout(os.fsencode(repo), None) as filtered_blob:
            changed = False
            for live_entry, index_entry in zip(
                live_mode_candidate["entries"],
                index_mode_candidate["entries"],
                strict=True,
            ):
                path = bytes.fromhex(live_entry["path_hex"])
                if live_entry["source"] != "tracked" or not any(
                    within(path.lower(), control) for control in CONTROL_ROOTS
                ):
                    continue
                index = live_entry.get("index")
                worktree = live_entry.get("worktree")
                if (
                    index is None
                    or index["mode"] not in {"100644", "100755"}
                    or not isinstance(worktree, dict)
                    or worktree.get("kind") != "file"
                    or not isinstance(worktree.get("executable"), bool)
                ):
                    return []
                content_digest = digest_bytes(filtered_blob(path))
                live_entry["worktree"] = {
                    "content_digest": content_digest,
                    "executable": worktree["executable"],
                    "kind": "file",
                }
                index_entry["worktree"] = {
                    "content_digest": content_digest,
                    "executable": index["mode"] == "100755",
                    "kind": "file",
                }
                changed = True
    except ObservationError:
        return []
    if not changed:
        return []
    candidates = [live_mode_candidate]
    if index_mode_candidate != live_mode_candidate:
        candidates.append(index_mode_candidate)
    return candidates


def retained_tree_entries(
    repo: bytes,
    head: str,
    allowed_paths: list[str],
    prohibited_paths: list[str],
) -> dict[bytes, tuple[str, str, str]]:
    allowed = [os.fsencode(path) for path in allowed_paths]
    prohibited = [os.fsencode(path) for path in prohibited_paths]
    recursive, ancestors = head_tree_queries(allowed)
    outputs = [
        run_git(
            repo,
            b"--no-replace-objects",
            b"ls-tree",
            b"-r",
            b"-z",
            b"--full-tree",
            head.encode("ascii"),
            b"--",
            *recursive,
        )
    ]
    if ancestors:
        outputs.append(
            run_git(
                repo,
                b"--no-replace-objects",
                b"ls-tree",
                b"-z",
                b"--full-tree",
                head.encode("ascii"),
                b"--",
                *ancestors,
            )
        )
    result: dict[bytes, tuple[str, str, str]] = {}
    for output in outputs:
        for record in output.split(b"\0"):
            if not record:
                continue
            header, separator, path = record.partition(b"\t")
            fields = header.split(b" ")
            if not separator or len(fields) != 3:
                raise ObservationError("malformed retained tree record")
            mode, kind, object_id = (field.decode("ascii") for field in fields)
            if kind == "tree" or not legacy_projected_entry(path, allowed, prohibited):
                continue
            if kind not in {"blob", "commit"}:
                raise ObservationError("unsupported retained tree record")
            value = (mode, kind, object_id)
            previous = result.get(path)
            if previous is not None and previous != value:
                raise ObservationError("conflicting retained tree records")
            result[path] = value
    return result


def retained_blob_worktree(
    path: bytes,
    mode: str,
    filtered_blob: Any,
) -> dict[str, Any]:
    if mode not in {"100644", "100755"}:
        raise ObservationError("retained tree mode is incompatible with a regular file")
    blob = filtered_blob(path)
    return {
        "content_digest": digest_bytes(blob),
        "executable": mode == "100755",
        "kind": "file",
    }


def retained_tree_legacy_projection(
    repo: Path,
    live: dict[str, Any],
    retained_head: str,
    allowed_paths: list[str],
    prohibited_paths: list[str],
    *,
    reconstruct_all: bool = False,
) -> dict[str, Any]:
    """Rebuild only Git-tree-proved legacy rows; never invent dirty predecessor bytes."""
    candidate = copy.deepcopy(live)
    repo_bytes = os.fsencode(repo)
    tree = retained_tree_entries(
        repo_bytes,
        retained_head,
        allowed_paths,
        prohibited_paths,
    )
    allowed = [os.fsencode(path) for path in allowed_paths]
    prohibited = [os.fsencode(path) for path in prohibited_paths]
    rebuilt: list[dict[str, Any]] = []
    with snapshot_checkout(repo_bytes, retained_head) as filtered_blob:
        for entry in candidate["entries"]:
            path = bytes.fromhex(entry["path_hex"])
            if entry["source"] != "tracked":
                if not reconstruct_all or entry["source"] == "scope":
                    rebuilt.append(entry)
                continue
            is_control = any(within(path.lower(), control) for control in CONTROL_ROOTS)
            if reconstruct_all or is_control:
                continue
            index = entry.get("index")
            retained = tree.get(path)
            if (
                index is not None
                and index.get("mode") == "160000"
                and retained is not None
                and retained[0] == "160000"
                and retained[1] == "commit"
            ):
                nested_repo = repo / os.fsdecode(path)
                nested_allowed = projected_scopes(path, allowed)
                nested_prohibited = projected_scopes(path, prohibited)
                nested_live = _legacy_tracked_control_projection(
                    nested_repo,
                    f"gitlink:{path.hex()}",
                    nested_allowed,
                    nested_prohibited,
                )
                nested_candidate = retained_tree_legacy_projection(
                    nested_repo,
                    nested_live,
                    retained[2],
                    nested_allowed,
                    nested_prohibited,
                )
                entry["worktree"]["content_digest"] = digest_bytes(
                    canonical_bytes(nested_candidate)
                )
            rebuilt.append(entry)

        for path, (mode, kind, object_id) in tree.items():
            is_control = any(within(path.lower(), control) for control in CONTROL_ROOTS)
            if not reconstruct_all and not is_control:
                continue
            if kind == "blob":
                worktree = retained_blob_worktree(path, mode, filtered_blob)
            elif kind == "commit" and mode == "160000":
                nested_repo = repo / os.fsdecode(path)
                nested_allowed = projected_scopes(path, allowed)
                nested_prohibited = projected_scopes(path, prohibited)
                nested_live = _legacy_tracked_control_projection(
                    nested_repo,
                    f"gitlink:{path.hex()}",
                    nested_allowed,
                    nested_prohibited,
                )
                nested_candidate = retained_tree_legacy_projection(
                    nested_repo,
                    nested_live,
                    object_id,
                    nested_allowed,
                    nested_prohibited,
                    reconstruct_all=True,
                )
                worktree = {
                    "content_digest": digest_bytes(canonical_bytes(nested_candidate)),
                    "executable": False,
                    "head": object_id,
                    "head_ref": nested_live["head_ref"],
                    "kind": "gitlink",
                }
            else:
                raise ObservationError("retained tree entry has an unsupported kind or mode")
            rebuilt.append(
                {
                    "index": {"mode": mode, "object_id": object_id, "stage": 0},
                    "path_hex": path.hex(),
                    "source": "tracked",
                    "worktree": worktree,
                }
            )

    rebuilt.sort(
        key=lambda entry: (
            bytes.fromhex(entry["path_hex"]),
            entry["source"],
            -1 if entry["index"] is None else entry["index"]["stage"],
        )
    )
    candidate["entries"] = rebuilt
    candidate["head"] = retained_head
    return candidate


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
    compatible_before = normalize_legacy_gitlink_digests(
        repo_bytes, before, after, scope
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
