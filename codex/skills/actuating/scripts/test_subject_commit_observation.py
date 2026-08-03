#!/usr/bin/env python3
"""Conformance tests for the Actuating subject-commit observer."""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

from subject_commit_observation import (
    ObservationError,
    head_tree_queries,
    observe_commit,
)
from subject_observation import canonical_bytes, observe

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


def write_before(repo: Path, root: Path, allowed: list[str] = ALLOWED, name: str = "before") -> Path:
    before = observe(repo, REPOSITORY_ID, allowed, [])
    path = root / f"{name}.json"
    path.write_bytes(canonical_bytes(before) + b"\n")
    return path


def prepare_dirty(repo: Path, root: Path) -> Path:
    (repo / "scope/value.txt").write_text("changed\n", encoding="utf-8")
    return write_before(repo, root)


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
        git(nested, "add", "value.txt")
        git(nested, "commit", "-m", "nested base")

        repo = new_repo(root)
        git(repo, "-c", "protocol.file.allow=always", "submodule", "add", str(nested), "scope/sub")
        git(repo, "commit", "-m", "add submodule")
        (repo / "scope/value.txt").write_text("changed\n", encoding="utf-8")
        before_path = write_before(
            repo, root, ["scope/sub/value.txt", "scope/value.txt"]
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
