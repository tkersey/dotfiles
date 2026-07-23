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
        self.temp = tempfile.TemporaryDirectory(); self.repo = Path(self.temp.name)
        git(self.repo, "init", "-q"); git(self.repo, "config", "user.email", "test@example.com")
        git(self.repo, "config", "user.name", "Test")
        (self.repo / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")
        (self.repo / "scope").mkdir(); (self.repo / "outside").mkdir()
        (self.repo / "scope/tracked.txt").write_text("one\n", encoding="utf-8")
        (self.repo / "outside/tracked.txt").write_text("outside\n", encoding="utf-8")
        git(self.repo, "add", ".gitignore", "scope/tracked.txt", "outside/tracked.txt")
        git(self.repo, "commit", "-qm", "fixture")
    def tearDown(self) -> None: self.temp.cleanup()
    def observe(self, prohibited: list[str] | None = None, allowed: list[str] | None = None):
        return subject_observation.observe(self.repo, "example/repo", allowed or ["scope"], prohibited or [])
    def reject(self, allowed: list[str] | None = None) -> None:
        with self.assertRaises(subject_observation.ObservationError): self.observe(allowed=allowed)
    def test_capture_and_selected_content_are_exact(self) -> None:
        first = self.observe(); self.assertEqual(first, self.observe())
        self.assertEqual(subject_observation.SCHEMA, first["schema"])
        self.assertTrue(first["subject_digest"].startswith("sha256:"))
        self.assertEqual(["scope"], first["scope"]["allowed_paths"])
        tracked = self.repo / "scope/tracked.txt"; before = first["subject_digest"]
        tracked.write_text("two\n", encoding="utf-8"); self.assertNotEqual(before, self.observe()["subject_digest"])
        git(self.repo, "update-index", "--skip-worktree", "scope/tracked.txt"); self.reject()
        git(self.repo, "update-index", "--no-skip-worktree", "scope/tracked.txt")
        git(self.repo, "update-index", "--assume-unchanged", "scope/tracked.txt"); self.reject()
        git(self.repo, "update-index", "--no-assume-unchanged", "scope/tracked.txt")
        before_override = self.observe()["subject_digest"]
        alternate = self.repo / "alternate-index"; alternate.write_bytes((self.repo / ".git/index").read_bytes())
        tracked.write_text("three\n", encoding="utf-8"); git(self.repo, "add", "scope/tracked.txt"); tracked.write_text("two\n", encoding="utf-8")
        with mock.patch.dict(os.environ, {"GIT_INDEX_FILE": str(alternate)}): self.assertNotEqual(before_override, self.observe()["subject_digest"])
    def test_untracked_ignored_and_structural_scope_changes_digest(self) -> None:
        with mock.patch.object(subject_observation, "run_git", return_value=b"") as run:
            subject_observation.untracked_entries(b"/repo", [b"scope"], [b"scope/private"]); run.assert_called_once_with(b"/repo", b"ls-files", b"--others", b"-z", b"--", b":(literal)scope", b":(exclude,literal)scope/private", b":(exclude,literal).git", b":(exclude,literal).ledger")
        new = self.repo / "scope/new.txt"; before = self.observe()["subject_digest"]
        new.write_text("new\n", encoding="utf-8"); self.assertNotEqual(before, self.observe()["subject_digest"])
        (self.repo / ".gitignore").write_text("ignored.txt\nscope/ignored.txt\n", encoding="utf-8")
        ignored = self.repo / "scope/ignored.txt"; ignored.write_text("one\n", encoding="utf-8")
        before = self.observe()["subject_digest"]; ignored.write_text("two\n", encoding="utf-8")
        self.assertNotEqual(before, self.observe()["subject_digest"])
        empty = self.repo / "scope/empty"; empty.mkdir()
        before = self.observe(allowed=["scope/empty"])["subject_digest"]; empty.rmdir()
        self.assertNotEqual(before, self.observe(allowed=["scope/empty"])["subject_digest"])
    def test_excluded_content_does_not_change_digest(self) -> None:
        before = self.observe()["subject_digest"]
        (self.repo / "outside/tracked.txt").write_text("changed\n", encoding="utf-8")
        (self.repo / "ignored.txt").write_text("ignored\n", encoding="utf-8")
        (self.repo / ".ledger").mkdir(); (self.repo / ".ledger/state").write_text("control\n", encoding="utf-8")
        self.assertEqual(before, self.observe()["subject_digest"])
        private = self.repo / "scope/private"; private.mkdir(); secret = private / "secret.txt"
        secret.write_text("one\n", encoding="utf-8"); before = self.observe(["scope/private"])["subject_digest"]
        secret.write_text("two\n", encoding="utf-8"); self.assertEqual(before, self.observe(["scope/private"])["subject_digest"])
    def test_worktree_aliases_fail_closed(self) -> None:
        tracked = self.repo / "scope/tracked.txt"; before = self.observe()["subject_digest"]
        tracked.chmod(tracked.stat().st_mode | stat.S_IXUSR); executable = self.observe()["subject_digest"]
        self.assertNotEqual(before, executable); tracked.unlink(); self.assertNotEqual(executable, self.observe()["subject_digest"])
        link = self.repo / "scope/external"; os.symlink("/tmp", link); self.reject(); link.unlink()
        shared = self.repo / "outside/shared.txt"; shared.write_text("shared\n", encoding="utf-8")
        os.link(shared, self.repo / "scope/shared.txt"); self.reject()
    def test_double_capture_fails_closed_on_drift(self) -> None:
        first = {"entries": [], "head": "a", "head_ref": "refs/heads/main", "repository_id": "example/repo",
                 "repository_root_digest": "sha256:" + "0" * 64, "schema": subject_observation.SCHEMA,
                 "scope": {}, "subject_digest": None}
        with mock.patch.object(subject_observation, "capture", side_effect=[first, {**first, "head": "b"}]):
            with self.assertRaises(subject_observation.ObservationError): self.observe()
    def test_gitlink_worktree_drift_changes_digest(self) -> None:
        source = self.repo / "submodule-source"; source.mkdir(); git(source, "init", "-q")
        git(source, "config", "user.email", "test@example.com"); git(source, "config", "user.name", "Test")
        nested = source / "tracked.txt"; nested.write_text("one\n", encoding="utf-8")
        git(source, "add", "tracked.txt"); git(source, "commit", "-qm", "fixture")
        subprocess.run(["git", "-C", str(self.repo), "-c", "protocol.file.allow=always", "submodule", "add", "-q",
                        str(source), "scope/nested"], check=True, capture_output=True)
        git(self.repo, "commit", "-qam", "add gitlink"); target = self.repo / "scope/nested/tracked.txt"
        before = self.observe()["subject_digest"]; target.write_text("two\n", encoding="utf-8")
        self.assertNotEqual(before, self.observe()["subject_digest"])
        before = self.observe(allowed=["scope/nested/tracked.txt"])["subject_digest"]
        target.write_text("three\n", encoding="utf-8")
        self.assertNotEqual(before, self.observe(allowed=["scope/nested/tracked.txt"])["subject_digest"])
    def test_repository_and_head_identity_change_digest(self) -> None:
        git(self.repo, "branch", "same-commit"); before = self.observe()["subject_digest"]
        git(self.repo, "switch", "-q", "same-commit"); self.assertNotEqual(before, self.observe()["subject_digest"])
        with tempfile.TemporaryDirectory() as directory:
            clone = Path(directory) / "clone"
            subprocess.run(["git", "clone", "-q", str(self.repo), str(clone)], check=True)
            other = subject_observation.observe(clone, "example/repo", ["scope"], [])["subject_digest"]
            self.assertNotEqual(self.observe()["subject_digest"], other)
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory); git(repo, "init", "-q"); (repo / "file.txt").write_text("one\n", encoding="utf-8")
            observed = subject_observation.observe(repo, "example/unborn", ["."], [])
            self.assertTrue(observed["head"].startswith("unborn:refs/heads/"))
            self.assertTrue(observed["head_ref"].startswith("refs/heads/"))
    def test_scope_validation_is_canonical_and_exact(self) -> None:
        self.assertEqual(["a", "b"], subject_observation.canonical_scope(["b", "a", "b"], require_nonempty=True))
        for path in ("../escape", r"..\escape", r"C:\escape", "cafe\u0301"):
            with self.subTest(path=path), self.assertRaises(subject_observation.ObservationError):
                subject_observation.canonical_scope([path], require_nonempty=True)
        for path in ([".git"], ["SCOPE"]):
            with self.subTest(path=path): self.reject(path)
        os.symlink("/tmp", self.repo / "scope-link"); self.reject(["scope-link"])
