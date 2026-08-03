#!/usr/bin/env python3
"""Conformance tests for the Actuating subject-commit observer."""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

from subject_commit_observation import ObservationError, observe_commit
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


def write_before(repo: Path, root: Path) -> Path:
    before = observe(repo, REPOSITORY_ID, ALLOWED, [])
    path = root / "before.json"
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
        expect_rejected(lambda: observe_commit(repo, before_path), "not clean")

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
    "positive": case_positive,
    "negative": case_negative,
    "changed-content": case_changed_content,
    "non-parent": case_non_parent,
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
