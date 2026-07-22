from __future__ import annotations
import importlib.util
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock
SCRIPT = Path(__file__).parents[1] / "scripts" / "subject_observation.py"
SPEC = importlib.util.spec_from_file_location("subject_observation", SCRIPT)
assert SPEC and SPEC.loader
subject_observation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(subject_observation)
def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


class SubjectObservationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.email", "test@example.com")
        git(self.repo, "config", "user.name", "Test")
        (self.repo / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")
        (self.repo / "scope").mkdir()
        (self.repo / "outside").mkdir()
        (self.repo / "scope" / "tracked.txt").write_text("one\n", encoding="utf-8")
        (self.repo / "outside" / "tracked.txt").write_text("outside\n", encoding="utf-8")
        git(self.repo, "add", ".gitignore", "scope/tracked.txt", "outside/tracked.txt")
        git(self.repo, "commit", "-qm", "fixture")

    def tearDown(self) -> None:
        self.temp.cleanup()
    def observe(self, prohibited: list[str] | None = None):
        return subject_observation.observe(
            self.repo,
            "example/repo",
            ["scope"],
            prohibited or [],
        )
    def test_capture_is_stable_and_structural(self) -> None:
        first = self.observe()
        second = self.observe()
        self.assertEqual(first, second)
        self.assertEqual("actuating-subject-observation/v1", first["schema"])
        self.assertTrue(first["subject_digest"].startswith("sha256:"))
        self.assertEqual(["scope"], first["scope"]["allowed_paths"])
    def test_in_scope_tracked_change_changes_digest(self) -> None:
        before = self.observe()["subject_digest"]
        (self.repo / "scope" / "tracked.txt").write_text("two\n", encoding="utf-8")
        self.assertNotEqual(before, self.observe()["subject_digest"])
    def test_in_scope_untracked_change_changes_digest(self) -> None:
        before = self.observe()["subject_digest"]
        (self.repo / "scope" / "new.txt").write_text("new\n", encoding="utf-8")
        self.assertNotEqual(before, self.observe()["subject_digest"])
    def test_out_of_scope_and_ignored_changes_do_not_change_digest(self) -> None:
        before = self.observe()["subject_digest"]
        (self.repo / "outside" / "tracked.txt").write_text("changed\n", encoding="utf-8")
        (self.repo / "ignored.txt").write_text("ignored\n", encoding="utf-8")
        (self.repo / ".ledger").mkdir()
        (self.repo / ".ledger" / "state").write_text("control\n", encoding="utf-8")
        self.assertEqual(before, self.observe()["subject_digest"])
    def test_prohibited_descendant_does_not_change_digest(self) -> None:
        (self.repo / "scope" / "private").mkdir()
        (self.repo / "scope" / "private" / "secret.txt").write_text("one\n", encoding="utf-8")
        before = self.observe(["scope/private"])["subject_digest"]
        (self.repo / "scope" / "private" / "secret.txt").write_text("two\n", encoding="utf-8")
        self.assertEqual(before, self.observe(["scope/private"])["subject_digest"])

    def test_deletion_executable_bit_and_symlink_target_change_digest(self) -> None:
        tracked = self.repo / "scope" / "tracked.txt"
        before = self.observe()["subject_digest"]
        tracked.chmod(tracked.stat().st_mode | stat.S_IXUSR)
        executable = self.observe()["subject_digest"]
        self.assertNotEqual(before, executable)
        tracked.unlink()
        deleted = self.observe()["subject_digest"]
        self.assertNotEqual(executable, deleted)
        os.symlink("tracked.txt", self.repo / "scope" / "link")
        symlink = self.observe()["subject_digest"]
        (self.repo / "scope" / "link").unlink()
        os.symlink("other.txt", self.repo / "scope" / "link")
        self.assertNotEqual(symlink, self.observe()["subject_digest"])

    def test_double_capture_fails_closed_on_drift(self) -> None:
        first = {
            "entries": [],
            "head": "a",
            "repository_id": "example/repo",
            "schema": subject_observation.SCHEMA,
            "scope": {},
            "subject_digest": None,
        }
        second = {**first, "head": "b"}
        with mock.patch.object(subject_observation, "capture", side_effect=[first, second]):
            with self.assertRaises(subject_observation.ObservationError):
                subject_observation.observe(self.repo, "example/repo", ["scope"], [])

    def test_gitlink_worktree_drift_changes_digest(self) -> None:
        source = self.repo / "submodule-source"
        source.mkdir()
        git(source, "init", "-q")
        git(source, "config", "user.email", "test@example.com")
        git(source, "config", "user.name", "Test")
        (source / "tracked.txt").write_text("one\n", encoding="utf-8")
        git(source, "add", "tracked.txt")
        git(source, "commit", "-qm", "fixture")
        subprocess.run(
            ["git", "-C", str(self.repo), "-c", "protocol.file.allow=always", "submodule", "add", "-q", str(source), "scope/nested"],
            check=True,
            capture_output=True,
        )
        git(self.repo, "commit", "-qam", "add gitlink")
        before = self.observe()["subject_digest"]
        (self.repo / "scope" / "nested" / "tracked.txt").write_text("two\n", encoding="utf-8")
        self.assertNotEqual(before, self.observe()["subject_digest"])

    def test_unborn_head_has_explicit_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            git(repo, "init", "-q")
            (repo / "file.txt").write_text("one\n", encoding="utf-8")
            observed = subject_observation.observe(repo, "example/unborn", ["."], [])
            self.assertTrue(observed["head"].startswith("unborn:refs/heads/"))

    def test_scope_validation_is_canonical(self) -> None:
        self.assertEqual(["a", "b"], subject_observation.canonical_scope(["b", "a", "b"], require_nonempty=True))
        with self.assertRaises(subject_observation.ObservationError):
            subject_observation.canonical_scope(["../escape"], require_nonempty=True)
        with self.assertRaises(subject_observation.ObservationError):
            subject_observation.observe(self.repo, "example/repo", [".git"], [])
        os.symlink("/tmp", self.repo / "scope-link")
        with self.assertRaises(subject_observation.ObservationError):
            subject_observation.observe(self.repo, "example/repo", ["scope-link"], [])
