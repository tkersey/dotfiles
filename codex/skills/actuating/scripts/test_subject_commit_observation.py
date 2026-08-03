#!/usr/bin/env python3
"""Conformance tests for the Actuating subject-commit observer."""
from __future__ import annotations

import argparse
import json
import stat
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

from subject_commit_observation import (
    ObservationError,
    current_index_legacy_projections,
    head_tree_queries,
    observe_commit,
    retained_tree_legacy_projection,
    write_snapshot_entry,
)
from subject_observation import (
    _legacy_tracked_control_projection,
    canonical_bytes,
    digest_bytes,
    file_digest,
    observe,
)

ALLOWED = ["scope/value.txt"]
REPOSITORY_ID = "example/subject-commit"


def git(repo: Path, *args: str) -> str:
    process = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if process.returncode != 0:
        raise RuntimeError(process.stderr.strip())
    return process.stdout.strip()


def new_repo(root: Path) -> Path:
    repo = root / "repo"
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.email", "subject-commit@example.invalid")
    git(repo, "config", "user.name", "Subject Commit Test")
    (repo / "scope").mkdir()
    (repo / "scope/value.txt").write_text("base\n", encoding="utf-8")
    (repo / "outside.txt").write_text("base\n", encoding="utf-8")
    git(repo, "add", "scope/value.txt", "outside.txt")
    git(repo, "commit", "-m", "base")
    return repo


def new_control_repo(root: Path, name: str) -> Path:
    repo = root / name
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.email", "subject-commit@example.invalid")
    git(repo, "config", "user.name", "Subject Commit Test")
    (repo / ".ledger").mkdir()
    (repo / ".ledger/tracked.txt").write_text("control\n", encoding="utf-8")
    (repo / "value.txt").write_text("base\n", encoding="utf-8")
    git(repo, "add", "value.txt")
    git(repo, "add", "--force", ".ledger/tracked.txt")
    git(repo, "commit", "-m", "control base")
    return repo


def add_control_submodule(repo: Path, nested: Path) -> Path:
    git(
        repo,
        "-c",
        "protocol.file.allow=always",
        "submodule",
        "add",
        str(nested),
        "scope/sub",
    )
    git(repo, "commit", "-m", "add control submodule")
    return repo / "scope/sub"


def write_before(
    repo: Path,
    root: Path,
    allowed: list[str] = ALLOWED,
    name: str = "before",
    prohibited: list[str] | None = None,
) -> Path:
    before = observe(repo, REPOSITORY_ID, allowed, prohibited or [])
    path = root / f"{name}.json"
    path.write_bytes(canonical_bytes(before) + b"\n")
    return path


def prepare_dirty(repo: Path, root: Path) -> Path:
    (repo / "scope/value.txt").write_text("changed\n", encoding="utf-8")
    return write_before(repo, root)


def retain_legacy_gitlink_digest(
    before_path: Path,
    nested_repo: Path,
    path: bytes,
    prohibited: list[str] | None = None,
) -> None:
    before = json.loads(before_path.read_bytes())
    legacy_nested = _legacy_tracked_control_projection(
        nested_repo,
        f"gitlink:{path.hex()}",
        ["."],
        prohibited or [],
    )
    for entry in before["entries"]:
        if entry["path_hex"] == path.hex() and entry["source"] == "tracked":
            entry["worktree"]["content_digest"] = digest_bytes(
                canonical_bytes(legacy_nested)
            )
    before["subject_digest"] = None
    before["subject_digest"] = digest_bytes(canonical_bytes(before))
    before_path.write_bytes(canonical_bytes(before) + b"\n")


def commit_scoped(repo: Path) -> None:
    git(repo, "add", "scope/value.txt")
    git(repo, "commit", "-m", "commit scoped worktree")


def expect_rejected(action: Callable[[], object], fragment: str) -> None:
    try:
        action()
    except ObservationError as error:
        if fragment not in str(error):
            raise AssertionError(f"expected {fragment!r}, got {str(error)!r}") from error
    else:
        raise AssertionError(f"expected rejection containing {fragment!r}")


def case_positive() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repo = new_repo(root)
        before_path = prepare_dirty(repo, root)
        before = json.loads(before_path.read_bytes())
        commit_scoped(repo)
        first = observe_commit(repo, before_path)
        second = observe_commit(repo, before_path)
        assert canonical_bytes(first) == canonical_bytes(second)
        assert first["before"]["subject_digest"] == before["subject_digest"]
        assert first["after"]["parent"] == before["head"]
        assert first["before"]["scoped_worktree_digest"] == first["after"]["scoped_worktree_digest"]
        assert first["changed_paths"] == ALLOWED
        assert first["clean_successor"] is True


def case_changed_content() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repo = new_repo(root)
        before_path = prepare_dirty(repo, root)
        (repo / "scope/value.txt").write_text("different\n", encoding="utf-8")
        commit_scoped(repo)
        expect_rejected(lambda: observe_commit(repo, before_path), "worktree meaning changed")


def case_non_parent() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repo = new_repo(root)
        before_path = prepare_dirty(repo, root)
        commit_scoped(repo)
        git(repo, "commit", "--allow-empty", "-m", "intervening commit")
        expect_rejected(lambda: observe_commit(repo, before_path), "not the direct child")


def case_deletion() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repo = new_repo(root)
        (repo / "scope/value.txt").unlink()
        before_path = write_before(repo, root)
        git(repo, "add", "--update", "scope/value.txt")
        git(repo, "commit", "-m", "commit scoped deletion")
        result = observe_commit(repo, before_path)
        assert result["changed_paths"] == ALLOWED
        assert result["before"]["scoped_worktree_digest"] == result["after"]["scoped_worktree_digest"]

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repo = new_repo(root)
        (repo / "scope/value.txt").unlink()
        (repo / "scope").rmdir()
        before_path = write_before(repo, root, ["scope"])
        git(repo, "add", "--update", "scope")
        git(repo, "commit", "-m", "commit scoped directory deletion")
        result = observe_commit(repo, before_path)
        assert result["changed_paths"] == ALLOWED
        assert result["before"]["scoped_worktree_digest"] == result["after"]["scoped_worktree_digest"]


def case_large_scope() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repo = new_repo(root)
        paths = [f"scope/value-{index:04}.txt" for index in range(256)]
        for path in paths:
            (repo / path).write_text("base\n", encoding="utf-8")
        git(repo, "add", "scope")
        git(repo, "commit", "-m", "add large scope")
        for path in paths:
            (repo / path).write_text("changed\n", encoding="utf-8")
        before_path = write_before(repo, root, ["scope"])
        git(repo, "add", "scope")
        git(repo, "commit", "-m", "commit large scope")
        result = observe_commit(repo, before_path)
        assert len(result["changed_paths"]) == len(paths)


def case_clean_filter() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repo = new_repo(root)
        git(repo, "config", "filter.rewrite.clean", "sed s/worktree/index/g")
        git(repo, "config", "filter.rewrite.smudge", "cat")
        (repo / ".git/info/attributes").write_text(
            "scope/value.txt filter=rewrite\n", encoding="utf-8"
        )
        (repo / "scope/value.txt").write_text("worktree\n", encoding="utf-8")
        before_path = write_before(repo, root)
        commit_scoped(repo)
        assert git(repo, "status", "--porcelain=v1", "--", "scope/value.txt") == ""
        result = observe_commit(repo, before_path)
        assert result["before"]["scoped_worktree_digest"] == result["after"]["scoped_worktree_digest"]


def exercise_retained_control_rows(repo: Path, root: Path) -> None:
    (repo / "scope/sub/.ledger/tracked.txt").write_text(
        "captured staged control\n", encoding="utf-8"
    )
    git(repo / "scope/sub", "add", "--force", ".ledger/tracked.txt")
    (repo / "scope/value.txt").write_text("staged before capture\n", encoding="utf-8")
    before_path = write_before(
        repo, root, ["scope/sub", "scope/value.txt"], "legacy-staged-before-capture"
    )
    retain_legacy_gitlink_digest(before_path, repo / "scope/sub", b"scope/sub")
    (repo / "scope/sub/.ledger/tracked.txt").write_text(
        "worktree drift after capture\n", encoding="utf-8"
    )
    commit_scoped(repo)
    assert observe_commit(repo, before_path)["changed_paths"] == ALLOWED
    git(repo / "scope/sub", "reset", "--hard", "HEAD")

    (repo / "scope/value.txt").write_text("staged control\n", encoding="utf-8")
    before_path = write_before(
        repo, root, ["scope/sub", "scope/value.txt"], "legacy-staged-control"
    )
    retain_legacy_gitlink_digest(before_path, repo / "scope/sub", b"scope/sub")
    (repo / "scope/sub/.ledger/tracked.txt").write_text(
        "staged drift\n", encoding="utf-8"
    )
    git(repo / "scope/sub", "add", "--force", ".ledger/tracked.txt")
    commit_scoped(repo)
    assert observe_commit(repo, before_path)["changed_paths"] == ALLOWED
    git(repo / "scope/sub", "reset", "--hard", "HEAD")

    (repo / "scope/value.txt").write_text("added control\n", encoding="utf-8")
    before_path = write_before(
        repo, root, ["scope/sub", "scope/value.txt"], "legacy-added-control"
    )
    retain_legacy_gitlink_digest(before_path, repo / "scope/sub", b"scope/sub")
    (repo / "scope/sub/.ledger/added.txt").write_text("added\n", encoding="utf-8")
    git(repo / "scope/sub", "add", "--force", ".ledger/added.txt")
    commit_scoped(repo)
    assert observe_commit(repo, before_path)["changed_paths"] == ALLOWED
    git(repo / "scope/sub", "reset", "--hard", "HEAD")
    (repo / "scope/sub/.ledger/added.txt").unlink(missing_ok=True)

    (repo / "scope/value.txt").write_text("removed control\n", encoding="utf-8")
    before_path = write_before(
        repo, root, ["scope/sub", "scope/value.txt"], "legacy-removed-control"
    )
    retain_legacy_gitlink_digest(before_path, repo / "scope/sub", b"scope/sub")
    git(repo / "scope/sub", "rm", "--cached", ".ledger/tracked.txt")
    commit_scoped(repo)
    assert observe_commit(repo, before_path)["changed_paths"] == ALLOWED
    git(repo / "scope/sub", "reset", "--hard", "HEAD")

    fake_oid = "f" * 40
    git(
        repo / "scope/sub",
        "update-index",
        "--info-only",
        "--cacheinfo",
        f"100644,{fake_oid},.ledger/tracked.txt",
    )
    (repo / "scope/value.txt").write_text("unavailable fallback\n", encoding="utf-8")
    before_path = write_before(
        repo, root, ["scope/sub", "scope/value.txt"], "legacy-unavailable-fallback"
    )
    retain_legacy_gitlink_digest(before_path, repo / "scope/sub", b"scope/sub")
    commit_scoped(repo)
    assert observe_commit(repo, before_path)["changed_paths"] == ALLOWED
    git(repo / "scope/sub", "reset", "--hard", "HEAD")

    (repo / "scope/value.txt").write_text("control drift\n", encoding="utf-8")
    before_path = write_before(
        repo, root, ["scope/sub", "scope/value.txt"], "legacy-control-drift"
    )
    retain_legacy_gitlink_digest(before_path, repo / "scope/sub", b"scope/sub")
    (repo / "scope/sub/.ledger/tracked.txt").write_text(
        "ignored drift\n", encoding="utf-8"
    )
    commit_scoped(repo)
    assert observe_commit(repo, before_path)["changed_paths"] == ALLOWED

    (repo / "scope/sub/value.txt").write_text("dirty\n", encoding="utf-8")
    (repo / "scope/value.txt").write_text("second\n", encoding="utf-8")
    before_path = write_before(
        repo, root, ["scope/sub", "scope/value.txt"], "legacy-dirty-gitlink"
    )
    retain_legacy_gitlink_digest(before_path, repo / "scope/sub", b"scope/sub")
    (repo / "scope/sub/value.txt").write_text("base\n", encoding="utf-8")
    commit_scoped(repo)
    expect_rejected(lambda: observe_commit(repo, before_path), "worktree meaning changed")


def case_scope_projection() -> None:
    recursive, ancestors = head_tree_queries([b"vendor/package/file"])
    assert recursive == [b":(literal)vendor/package/file"]
    assert ancestors == [b":(literal)vendor", b":(literal)vendor/package"]

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        nested = root / "nested"
        nested.mkdir()
        git(nested, "init", "-b", "main")
        git(nested, "config", "user.email", "subject-commit@example.invalid")
        git(nested, "config", "user.name", "Subject Commit Test")
        (nested / "value.txt").write_text("base\n", encoding="utf-8")
        (nested / ".ledger").mkdir()
        (nested / ".ledger/tracked.txt").write_text("control\n", encoding="utf-8")
        git(nested, "add", "value.txt")
        git(nested, "add", "--force", ".ledger/tracked.txt")
        git(nested, "commit", "-m", "nested base")

        repo = new_repo(root)
        git(repo, "-c", "protocol.file.allow=always", "submodule", "add", str(nested), "scope/sub")
        git(repo, "commit", "-m", "add submodule")
        (repo / "scope/value.txt").write_text("changed\n", encoding="utf-8")
        before_path = write_before(repo, root, ["scope/sub", "scope/value.txt"])
        retain_legacy_gitlink_digest(before_path, repo / "scope/sub", b"scope/sub")
        commit_scoped(repo)
        result = observe_commit(repo, before_path)
        assert result["changed_paths"] == ALLOWED
        exercise_retained_control_rows(repo, root)

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        deep = root / "control-deep"
        deep.mkdir()
        git(deep, "init", "-b", "main")
        git(deep, "config", "user.email", "subject-commit@example.invalid")
        git(deep, "config", "user.name", "Subject Commit Test")
        (deep / "1:foo").write_text("base\n", encoding="utf-8")
        git(deep, "add", "1:foo")
        git(deep, "commit", "-m", "control deep base")

        nested = root / "control-gitlink-nested"
        nested.mkdir()
        git(nested, "init", "-b", "main")
        git(nested, "config", "user.email", "subject-commit@example.invalid")
        git(nested, "config", "user.name", "Subject Commit Test")
        (nested / "value.txt").write_text("base\n", encoding="utf-8")
        git(nested, "add", "value.txt")
        git(nested, "commit", "-m", "control gitlink nested base")
        git(
            nested,
            "-c",
            "protocol.file.allow=always",
            "submodule",
            "add",
            "--force",
            str(deep),
            ".ledger/deep",
        )
        git(nested, "commit", "-m", "add control gitlink")

        repo = new_repo(root)
        git(
            repo,
            "-c",
            "protocol.file.allow=always",
            "submodule",
            "add",
            str(nested),
            "scope/sub",
        )
        git(
            repo / "scope/sub",
            "-c",
            "protocol.file.allow=always",
            "submodule",
            "update",
            "--init",
        )
        git(repo, "commit", "-m", "add control-gitlink submodule")
        (repo / "scope/value.txt").write_text("control gitlink\n", encoding="utf-8")
        before_path = write_before(repo, root, ["scope/sub", "scope/value.txt"])
        retained_nested = _legacy_tracked_control_projection(
            repo / "scope/sub", "gitlink:73636f70652f737562", ["."], []
        )
        retain_legacy_gitlink_digest(before_path, repo / "scope/sub", b"scope/sub")
        (repo / "scope/sub/.ledger/deep/1:foo").write_text(
            "excluded semantic drift\n", encoding="utf-8"
        )
        commit_scoped(repo)
        live_nested = _legacy_tracked_control_projection(
            repo / "scope/sub", "gitlink:73636f70652f737562", ["."], []
        )
        reconstructed_nested = retained_tree_legacy_projection(
            repo / "scope/sub",
            live_nested,
            retained_nested["head"],
            ["."],
            [],
        )
        assert canonical_bytes(reconstructed_nested) == canonical_bytes(retained_nested), (
            reconstructed_nested,
            retained_nested,
        )
        result = observe_commit(repo, before_path)
        assert result["changed_paths"] == ALLOWED

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        nested = root / "filtered-nested"
        nested.mkdir()
        git(nested, "init", "-b", "main")
        git(nested, "config", "user.email", "subject-commit@example.invalid")
        git(nested, "config", "user.name", "Subject Commit Test")
        git(nested, "config", "filter.rewrite.clean", "sed s/worktree/index/g")
        git(nested, "config", "filter.rewrite.smudge", "sed s/index/worktree/g")
        (nested / ".ledger").mkdir()
        (nested / ".gitattributes").write_text(
            ".ledger/tracked.txt filter=rewrite\n", encoding="utf-8"
        )
        (nested / ".ledger/tracked.txt").write_text("worktree\n", encoding="utf-8")
        (nested / "value.txt").write_text("base\n", encoding="utf-8")
        git(nested, "add", ".gitattributes", "value.txt")
        git(nested, "add", "--force", ".ledger/tracked.txt")
        git(nested, "commit", "-m", "filtered nested base")

        repo = new_repo(root)
        git(
            repo,
            "-c",
            "protocol.file.allow=always",
            "submodule",
            "add",
            str(nested),
            "scope/sub",
        )
        filtered_sub = repo / "scope/sub"
        git(filtered_sub, "config", "filter.rewrite.clean", "sed s/worktree/index/g")
        git(filtered_sub, "config", "filter.rewrite.smudge", "sed s/index/worktree/g")
        (filtered_sub / ".ledger/tracked.txt").write_text(
            "worktree\n", encoding="utf-8"
        )
        git(repo, "commit", "-m", "add filtered submodule")
        (repo / "scope/value.txt").write_text("filtered control\n", encoding="utf-8")
        before_path = write_before(repo, root, ["scope/sub", "scope/value.txt"])
        retain_legacy_gitlink_digest(before_path, filtered_sub, b"scope/sub")
        (filtered_sub / ".ledger/tracked.txt").write_text("drift\n", encoding="utf-8")
        git(filtered_sub, "add", "--force", ".ledger/tracked.txt")
        commit_scoped(repo)
        result = observe_commit(repo, before_path)
        assert result["changed_paths"] == ALLOWED

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        nested = root / "retained-attributes-nested"
        nested.mkdir()
        git(nested, "init", "-b", "main")
        git(nested, "config", "user.email", "subject-commit@example.invalid")
        git(nested, "config", "user.name", "Subject Commit Test")
        git(nested, "config", "filter.rewrite.clean", "sed s/worktree/index/g")
        git(nested, "config", "filter.rewrite.smudge", "sed s/index/worktree/g")
        (nested / ".ledger").mkdir()
        (nested / ".ledger/.gitattributes").write_text(
            "tracked.txt filter=rewrite\n", encoding="utf-8"
        )
        (nested / ".ledger/tracked.txt").write_text("worktree\n", encoding="utf-8")
        (nested / "value.txt").write_text("base\n", encoding="utf-8")
        git(nested, "add", "value.txt")
        git(
            nested,
            "add",
            "--force",
            ".ledger/.gitattributes",
            ".ledger/tracked.txt",
        )
        git(nested, "commit", "-m", "retained attributes base")

        repo = new_repo(root)
        git(
            repo,
            "-c",
            "protocol.file.allow=always",
            "submodule",
            "add",
            str(nested),
            "scope/sub",
        )
        retained_sub = repo / "scope/sub"
        git(retained_sub, "config", "filter.rewrite.clean", "sed s/worktree/index/g")
        git(retained_sub, "config", "filter.rewrite.smudge", "sed s/index/worktree/g")
        git(retained_sub, "checkout", "--", ".ledger/tracked.txt")
        git(repo, "commit", "-m", "add retained-attributes submodule")

        (repo / "scope/value.txt").write_text("retained attributes\n", encoding="utf-8")
        before_path = write_before(repo, root, ["scope/sub", "scope/value.txt"])
        retain_legacy_gitlink_digest(before_path, retained_sub, b"scope/sub")
        (retained_sub / ".ledger/.gitattributes").write_text(
            "tracked.txt -filter\n", encoding="utf-8"
        )
        (retained_sub / ".ledger/tracked.txt").write_text(
            "successor\n", encoding="utf-8"
        )
        git(
            retained_sub,
            "add",
            "--force",
            ".ledger/.gitattributes",
            ".ledger/tracked.txt",
        )
        commit_scoped(repo)
        result = observe_commit(repo, before_path)
        assert result["changed_paths"] == ALLOWED

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        deep = root / "deep"
        deep.mkdir()
        git(deep, "init", "-b", "main")
        git(deep, "config", "user.email", "subject-commit@example.invalid")
        git(deep, "config", "user.name", "Subject Commit Test")
        (deep / "value.txt").write_text("base\n", encoding="utf-8")
        (deep / ".ledger").mkdir()
        (deep / ".ledger/tracked.txt").write_text("control\n", encoding="utf-8")
        git(deep, "add", "value.txt")
        git(deep, "add", "--force", ".ledger/tracked.txt")
        git(deep, "commit", "-m", "deep base")

        nested = root / "recursive-nested"
        nested.mkdir()
        git(nested, "init", "-b", "main")
        git(nested, "config", "user.email", "subject-commit@example.invalid")
        git(nested, "config", "user.name", "Subject Commit Test")
        (nested / "value.txt").write_text("base\n", encoding="utf-8")
        git(nested, "add", "value.txt")
        git(nested, "commit", "-m", "nested base")
        git(
            nested,
            "-c",
            "protocol.file.allow=always",
            "submodule",
            "add",
            str(deep),
            "deep",
        )
        git(nested, "commit", "-m", "add deep submodule")

        repo = new_repo(root)
        git(
            repo,
            "-c",
            "protocol.file.allow=always",
            "submodule",
            "add",
            str(nested),
            "scope/sub",
        )
        git(
            repo / "scope/sub",
            "-c",
            "protocol.file.allow=always",
            "submodule",
            "update",
            "--init",
        )
        git(repo, "commit", "-m", "add recursive submodule")
        (repo / "scope/value.txt").write_text("recursive control\n", encoding="utf-8")
        before_path = write_before(repo, root, ["scope/sub", "scope/value.txt"])
        retain_legacy_gitlink_digest(before_path, repo / "scope/sub", b"scope/sub")
        (repo / "scope/sub/deep/.ledger/tracked.txt").write_text(
            "recursive drift\n", encoding="utf-8"
        )
        commit_scoped(repo)
        result = observe_commit(repo, before_path)
        assert result["changed_paths"] == ALLOWED

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repo = new_repo(root)
        (repo / ".ledger").mkdir()
        (repo / ".ledger/tracked.txt").write_text("control\n", encoding="utf-8")
        git(repo, "add", "--force", ".ledger/tracked.txt")
        git(repo, "commit", "-m", "add tracked control path")
        (repo / "scope/value.txt").write_text("changed\n", encoding="utf-8")
        before_path = write_before(repo, root, ["."])
        before = json.loads(before_path.read_bytes())
        mode, object_id, stage, _ = git(
            repo, "ls-files", "--stage", "--", ".ledger/tracked.txt"
        ).split()
        before["entries"].append(
            {
                "index": {
                    "mode": mode,
                    "object_id": object_id,
                    "stage": int(stage),
                },
                "path_hex": b".ledger/tracked.txt".hex(),
                "source": "tracked",
                "worktree": {
                    "content_digest": file_digest(repo / ".ledger/tracked.txt"),
                    "executable": False,
                    "kind": "file",
                },
            }
        )
        before["entries"].sort(
            key=lambda entry: (
                bytes.fromhex(entry["path_hex"]),
                entry["source"],
                -1 if entry["index"] is None else entry["index"]["stage"],
            )
        )
        before["subject_digest"] = None
        before["subject_digest"] = digest_bytes(canonical_bytes(before))
        before_path.write_bytes(canonical_bytes(before) + b"\n")
        (repo / ".ledger/tracked.txt").write_text("ignored drift\n", encoding="utf-8")
        commit_scoped(repo)
        result = observe_commit(repo, before_path)
        assert result["changed_paths"] == ALLOWED

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repo = new_repo(root)
        (repo / "ancestor").write_text("tracked ancestor\n", encoding="utf-8")
        git(repo, "add", "ancestor")
        git(repo, "commit", "-m", "add tracked ancestor")
        (repo / "ancestor").unlink()
        (repo / "scope/value.txt").write_text("changed\n", encoding="utf-8")
        before_path = write_before(
            repo, root, ["ancestor/descendant", "scope/value.txt"]
        )
        commit_scoped(repo)
        expect_rejected(
            lambda: observe_commit(repo, before_path), "deleted tracked path"
        )


def case_snapshot_witnesses() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        nested = new_control_repo(root, "unreadable-index-nested")
        repo = new_repo(root)
        sub = add_control_submodule(repo, nested)
        (repo / "scope/value.txt").write_text("unreadable index\n", encoding="utf-8")
        before_path = write_before(repo, root, ["scope/sub", "scope/value.txt"])
        retain_legacy_gitlink_digest(before_path, sub, b"scope/sub")
        git(
            sub,
            "update-index",
            "--info-only",
            "--cacheinfo",
            f"100644,{'f' * 40},.ledger/tracked.txt",
        )
        (sub / ".ledger/tracked.txt").write_text(
            "post-capture drift\n", encoding="utf-8"
        )
        commit_scoped(repo)
        assert observe_commit(repo, before_path)["changed_paths"] == ALLOWED

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        nested = new_control_repo(root, "unrelated-index-nested")
        repo = new_repo(root)
        sub = add_control_submodule(repo, nested)
        (sub / ".ledger/tracked.txt").write_text("staged\n", encoding="utf-8")
        git(sub, "add", "--force", ".ledger/tracked.txt")
        (repo / "scope/value.txt").write_text("unrelated index\n", encoding="utf-8")
        before_path = write_before(
            repo,
            root,
            ["scope/sub", "scope/value.txt"],
            prohibited=["scope/sub/.ledger/unavailable.txt"],
        )
        retain_legacy_gitlink_digest(
            before_path,
            sub,
            b"scope/sub",
            prohibited=[".ledger/unavailable.txt"],
        )
        git(
            sub,
            "update-index",
            "--info-only",
            "--add",
            "--cacheinfo",
            f"100644,{'f' * 40},.ledger/unavailable.txt",
        )
        (sub / ".ledger/tracked.txt").write_text(
            "post-capture drift\n", encoding="utf-8"
        )
        retained_digest = next(
            entry["worktree"]["content_digest"]
            for entry in json.loads(before_path.read_bytes())["entries"]
            if entry["source"] == "tracked" and entry["path_hex"] == b"scope/sub".hex()
        )
        legacy_current = _legacy_tracked_control_projection(
            sub,
            "gitlink:73636f70652f737562",
            ["."],
            [".ledger/unavailable.txt"],
        )
        assert any(
            digest_bytes(canonical_bytes(candidate)) == retained_digest
            for candidate in current_index_legacy_projections(sub, legacy_current)
        )
        commit_scoped(repo)
        assert observe_commit(repo, before_path)["changed_paths"] == ALLOWED

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        nested = new_control_repo(root, "index-mode-nested")
        repo = new_repo(root)
        sub = add_control_submodule(repo, nested)
        git(sub, "update-index", "--chmod=+x", ".ledger/tracked.txt")
        assert not (sub / ".ledger/tracked.txt").stat().st_mode & stat.S_IXUSR
        (repo / "scope/value.txt").write_text("index mode\n", encoding="utf-8")
        before_path = write_before(repo, root, ["scope/sub", "scope/value.txt"])
        retain_legacy_gitlink_digest(before_path, sub, b"scope/sub")
        (sub / ".ledger/tracked.txt").write_text(
            "post-capture content drift\n", encoding="utf-8"
        )
        commit_scoped(repo)
        assert observe_commit(repo, before_path)["changed_paths"] == ALLOWED

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        nested = new_control_repo(root, "index-mode-successor-nested")
        repo = new_repo(root)
        sub = add_control_submodule(repo, nested)
        git(sub, "update-index", "--chmod=+x", ".ledger/tracked.txt")
        (sub / ".ledger/tracked.txt").chmod(0o755)
        (repo / "scope/value.txt").write_text("index mode candidate\n", encoding="utf-8")
        before_path = write_before(repo, root, ["scope/sub", "scope/value.txt"])
        retain_legacy_gitlink_digest(before_path, sub, b"scope/sub")
        (sub / ".ledger/tracked.txt").chmod(0o644)
        (sub / ".ledger/tracked.txt").write_text(
            "post-capture content drift\n", encoding="utf-8"
        )
        commit_scoped(repo)
        assert observe_commit(repo, before_path)["changed_paths"] == ALLOWED

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        nested = root / "filter-context-nested"
        nested.mkdir()
        git(nested, "init", "-b", "main")
        git(nested, "config", "user.email", "subject-commit@example.invalid")
        git(nested, "config", "user.name", "Subject Commit Test")
        (nested / ".ledger").mkdir()
        (nested / ".gitattributes").write_text(
            ".ledger/tracked.txt filter=context\n"
            "filter-helper.txt filter=helper\n",
            encoding="utf-8",
        )
        (nested / ".ledger/tracked.txt").write_text("index\n", encoding="utf-8")
        (nested / "filter-helper.txt").write_text("context\n", encoding="utf-8")
        (nested / "value.txt").write_text("base\n", encoding="utf-8")
        git(nested, "config", "filter.context.clean", "cat")
        git(
            nested,
            "config",
            "filter.context.smudge",
            "sh -c 'cat; cat \"$(git rev-parse --show-toplevel)/filter-helper.txt\"'",
        )
        git(nested, "config", "filter.context.required", "true")
        git(
            nested,
            "config",
            "filter.helper.clean",
            "sh -c 'sed \"/^converted$/d\"'",
        )
        git(
            nested,
            "config",
            "filter.helper.smudge",
            "sh -c 'cat; printf \"converted\\n\"'",
        )
        git(nested, "config", "filter.helper.required", "true")
        git(nested, "add", ".gitattributes", "filter-helper.txt", "value.txt")
        git(nested, "add", "--force", ".ledger/tracked.txt")
        git(nested, "commit", "-m", "filter context base")

        repo = new_repo(root)
        sub = add_control_submodule(repo, nested)
        git(sub, "config", "filter.context.clean", "cat")
        git(
            sub,
            "config",
            "filter.context.smudge",
            "sh -c 'cat; cat \"$(git rev-parse --show-toplevel)/filter-helper.txt\"'",
        )
        git(sub, "config", "filter.context.required", "true")
        git(
            sub,
            "config",
            "filter.helper.clean",
            "sh -c 'sed \"/^converted$/d\"'",
        )
        git(
            sub,
            "config",
            "filter.helper.smudge",
            "sh -c 'cat; printf \"converted\\n\"'",
        )
        git(sub, "config", "filter.helper.required", "true")
        (sub / "filter-helper.txt").unlink()
        git(sub, "checkout", "--", "filter-helper.txt")
        (sub / ".ledger/tracked.txt").unlink()
        git(sub, "checkout", "--", ".ledger/tracked.txt")
        assert (sub / ".ledger/tracked.txt").read_text(encoding="utf-8") == (
            "index\ncontext\nconverted\n"
        )
        (repo / "scope/value.txt").write_text("filter context\n", encoding="utf-8")
        before_path = write_before(repo, root, ["scope/sub", "scope/value.txt"])
        retain_legacy_gitlink_digest(before_path, sub, b"scope/sub")
        (sub / ".ledger/tracked.txt").write_text("successor\n", encoding="utf-8")
        git(sub, "add", "--force", ".ledger/tracked.txt")
        commit_scoped(repo)
        assert observe_commit(repo, before_path)["changed_paths"] == ALLOWED

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        worktree = root / "worktree"
        worktree.mkdir()
        outside = root / "outside.txt"
        outside.write_text("safe\n", encoding="utf-8")
        (worktree / "target").symlink_to(outside)
        expect_rejected(
            lambda: write_snapshot_entry(worktree, b"target", "100644", b"unsafe\n"),
            "cannot materialize snapshot path",
        )
        assert outside.read_text(encoding="utf-8") == "safe\n"


def case_index_worktree_mode() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repo = new_repo(root)
        executable = repo / "scope/executable"
        executable.write_text("executable\n", encoding="utf-8")
        executable.chmod(0o755)
        git(repo, "add", "scope/executable")
        git(repo, "commit", "-m", "add executable")
        executable.chmod(0o654)
        (repo / "scope/value.txt").write_text("changed\n", encoding="utf-8")
        before_path = write_before(repo, root, ["scope"])
        commit_scoped(repo)
        expect_rejected(lambda: observe_commit(repo, before_path), "mode differs")

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repo = new_repo(root)
        link = repo / "scope/link"
        link.symlink_to("target")
        git(repo, "add", "scope/link")
        git(repo, "commit", "-m", "add symlink")
        link.unlink()
        link.write_text("target", encoding="utf-8")
        (repo / "scope/value.txt").write_text("changed\n", encoding="utf-8")
        before_path = write_before(repo, root, ["scope"])
        commit_scoped(repo)
        expect_rejected(lambda: observe_commit(repo, before_path), "index mode is incompatible")


def case_ambient_git_state() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repo = new_repo(root)
        (repo / ".git/info/exclude").write_text("scope/ignored.tmp\n", encoding="utf-8")
        (repo / "scope/ignored.tmp").write_text("ignored\n", encoding="utf-8")
        (repo / "scope/value.txt").write_text("changed\n", encoding="utf-8")
        before_path = write_before(repo, root, ["scope"])
        commit_scoped(repo)
        expect_rejected(lambda: observe_commit(repo, before_path), "untracked paths")

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repo = new_repo(root)
        before_path = prepare_dirty(repo, root)
        commit_scoped(repo)
        git(repo, "config", "core.fileMode", "false")
        (repo / "scope/value.txt").chmod(0o755)
        expect_rejected(lambda: observe_commit(repo, before_path), "mode differs")

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        nested = root / "nested"
        nested.mkdir()
        git(nested, "init", "-b", "main")
        git(nested, "config", "user.email", "subject-commit@example.invalid")
        git(nested, "config", "user.name", "Subject Commit Test")
        (nested / "value.txt").write_text("base\n", encoding="utf-8")
        git(nested, "add", "value.txt")
        git(nested, "commit", "-m", "nested base")

        repo = new_repo(root)
        git(repo, "-c", "protocol.file.allow=always", "submodule", "add", str(nested), "scope/sub")
        git(repo, "commit", "-m", "add submodule")
        (repo / "scope/sub/value.txt").write_text("committed\n", encoding="utf-8")
        git(repo / "scope/sub", "add", "value.txt")
        git(repo / "scope/sub", "commit", "-m", "nested successor")
        before_path = write_before(repo, root, ["scope/sub"])
        git(repo, "add", "scope/sub")
        git(repo, "commit", "-m", "advance submodule")
        git(repo, "config", "submodule.scope/sub.ignore", "all")
        (repo / "scope/sub/value.txt").write_text("residual dirty\n", encoding="utf-8")
        expect_rejected(lambda: observe_commit(repo, before_path), "content differs")

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repo = new_repo(root)
        before_path = prepare_dirty(repo, root)
        before = json.loads(before_path.read_bytes())
        git(repo, "commit", "--allow-empty", "-m", "intervening commit")
        commit_scoped(repo)
        successor = git(repo, "rev-parse", "HEAD")
        tree = git(repo, "rev-parse", f"{successor}^{{tree}}")
        synthetic = git(repo, "commit-tree", tree, "-p", before["head"], "-m", "synthetic parent")
        git(repo, "replace", successor, synthetic)
        expect_rejected(lambda: observe_commit(repo, before_path), "not the direct child")


def case_negative() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repo = new_repo(root)
        before_path = prepare_dirty(repo, root)
        tampered = json.loads(before_path.read_bytes())
        tampered["repository_id"] = "other/repository"
        before_path.write_bytes(canonical_bytes(tampered) + b"\n")
        expect_rejected(lambda: observe_commit(repo, before_path), "digest does not match")

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repo = new_repo(root)
        before_path = prepare_dirty(repo, root)
        commit_scoped(repo)
        (repo / "scope/value.txt").write_text("dirty\n", encoding="utf-8")
        expect_rejected(lambda: observe_commit(repo, before_path), "content differs")

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repo = new_repo(root)
        before_path = prepare_dirty(repo, root)
        (repo / "outside.txt").write_text("outside changed\n", encoding="utf-8")
        git(repo, "add", "scope/value.txt", "outside.txt")
        git(repo, "commit", "-m", "mixed-scope commit")
        expect_rejected(lambda: observe_commit(repo, before_path), "outside the subject scope")

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repo = new_repo(root)
        before_path = prepare_dirty(repo, root)
        commit_scoped(repo)
        git(repo, "branch", "-m", "other")
        expect_rejected(lambda: observe_commit(repo, before_path), "symbolic HEAD changed")

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repo = new_repo(root)
        before_path = prepare_dirty(repo, root)
        other = root / "other"
        git(root, "clone", str(repo), str(other))
        expect_rejected(lambda: observe_commit(other, before_path), "repository root changed")


CASES: dict[str, Callable[[], None]] = {
    "ambient-git-state": case_ambient_git_state,
    "clean-filter": case_clean_filter,
    "positive": case_positive,
    "negative": case_negative,
    "changed-content": case_changed_content,
    "deletion": case_deletion,
    "index-worktree-mode": case_index_worktree_mode,
    "large-scope": case_large_scope,
    "non-parent": case_non_parent,
    "scope-projection": case_scope_projection,
    "snapshot-witnesses": case_snapshot_witnesses,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=sorted(CASES))
    args = parser.parse_args()
    selected = [args.case] if args.case else sorted(CASES)
    for name in selected:
        CASES[name]()
        print(f"subject_commit_observation_{name}=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
