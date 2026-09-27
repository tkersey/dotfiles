"""Worktree/storage policy regression tests; native custody is tested separately."""
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/ledger_context.py"
spec = importlib.util.spec_from_file_location("ledger_context", SCRIPT)
context = importlib.util.module_from_spec(spec)
spec.loader.exec_module(context)


class LedgerContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.home = self.root / "codex home"
        self.env = patch.dict(os.environ, {"CODEX_HOME": str(self.home), "LEDGER_HOME": ""})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.repo = self.root / "main repo"
        self.repo.mkdir()
        self.git(self.repo, "init", "-q")
        self.git(self.repo, "config", "user.name", "Fixture")
        self.git(self.repo, "config", "user.email", "fixture@example.invalid")
        self.git(self.repo, "commit", "--allow-empty", "-qm", "fixture")
        self.other = self.root / "linked worktree"
        self.git(self.repo, "worktree", "add", "--detach", str(self.other))

    def git(self, cwd, *args):
        return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True).stdout

    def test_read_only_resolution_does_not_initialize(self):
        with self.assertRaises(context.ContextError):
            context.resolve(self.repo)
        self.assertFalse(self.home.exists())
        self.assertFalse((self.repo / ".git" / context.REGISTRATION).exists())
        self.assertFalse((self.repo / ".git" / "ledger-store.lock").exists())

    def test_fresh_initialization_requires_legacy_writer_quiescence(self):
        with self.assertRaisesRegex(context.ContextError, "--confirm-no-writers"):
            context.resolve(self.repo, initialize=True)
        self.assertFalse(self.home.exists())
        self.assertFalse((self.repo / ".git" / context.REGISTRATION).exists())

    def test_worktrees_share_identity_and_root_but_not_workspace(self):
        first = context.resolve(self.repo, initialize=True, confirm_no_writers=True)
        second = context.resolve(self.other)
        self.assertEqual(first["store_id"], second["store_id"])
        self.assertEqual(first["store_root"], second["store_root"])
        self.assertNotEqual(first["workspace_root"], second["workspace_root"])
        self.assertEqual(second["native_args"], ["--store-root", second["store_root"], "--store-id", second["store_id"]])
        self.assertFalse((self.other / ".ledger").exists())
        self.assertFalse(second["storage_mutated"])

    def test_shared_visibility_is_not_a_copied_worktree_log(self):
        first = context.resolve(self.repo, initialize=True, confirm_no_writers=True)
        control = Path(first["store_root"]) / ".ledger"
        # This is a filesystem-addressing fixture, not a native event mutation.
        fixture = control / "fixture.txt"
        fixture.write_text("shared")
        second = context.resolve(self.other)
        self.assertEqual((Path(second["store_root"]) / ".ledger/fixture.txt").read_text(), "shared")

    def test_concurrent_initializers_publish_one_registration(self):
        argv = [sys.executable, str(SCRIPT), "--repo", str(self.repo), "--initialize", "--confirm-no-writers"]
        def invoke(_):
            return json.loads(subprocess.run(argv, check=True, capture_output=True).stdout)
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(invoke, range(12)))
        self.assertEqual(len({r["store_id"] for r in results}), 1)
        roots = list((self.home / "ledger/repos").iterdir())
        self.assertEqual(len(roots), 1)

    def test_worktree_move_and_removal_preserve_history(self):
        first = context.resolve(self.other, initialize=True, confirm_no_writers=True)
        moved = self.root / "moved worktree"
        self.git(self.repo, "worktree", "move", str(self.other), str(moved))
        self.assertEqual(context.resolve(moved)["store_id"], first["store_id"])
        self.git(self.repo, "worktree", "remove", str(moved))
        self.assertEqual(context.resolve(self.repo)["store_id"], first["store_id"])

    def test_clone_is_not_automatically_attached(self):
        first = context.resolve(self.repo, initialize=True, confirm_no_writers=True)
        clone = self.root / "clone"
        subprocess.run(["git", "clone", "-q", str(self.repo), str(clone)], check=True)
        second = context.resolve(clone, initialize=True, confirm_no_writers=True)
        self.assertNotEqual(first["store_id"], second["store_id"])

    def test_environment_change_does_not_fork_registered_history(self):
        first = context.resolve(self.repo, initialize=True, confirm_no_writers=True)
        with patch.dict(os.environ, {"CODEX_HOME": str(self.root / "different"), "LEDGER_HOME": str(self.root / "override")}):
            second = context.resolve(self.other, initialize=True, confirm_no_writers=True)
        self.assertEqual(first["store_root"], second["store_root"])
        self.assertFalse((self.root / "override").exists())

    def test_missing_established_root_is_never_recreated(self):
        first = context.resolve(self.repo, initialize=True, confirm_no_writers=True)
        shutil.rmtree(first["store_root"])
        with self.assertRaises(FileNotFoundError):
            context.resolve(self.other, initialize=True, confirm_no_writers=True)
        self.assertFalse(Path(first["store_root"]).exists())

    def test_missing_control_directory_is_never_recreated(self):
        first = context.resolve(self.repo, initialize=True, confirm_no_writers=True)
        control = Path(first["store_root"]) / ".ledger"
        control.rmdir()
        with self.assertRaises(context.ContextError):
            context.resolve(self.other, initialize=True, confirm_no_writers=True)
        self.assertFalse(control.exists())

    def test_marker_identity_mismatch_fails_closed(self):
        first = context.resolve(self.repo, initialize=True, confirm_no_writers=True)
        marker = Path(first["store_root"]) / context.MARKER
        marker.write_text(json.dumps({"schema": context.MARKER_SCHEMA, "store_id": "0" * 32}))
        with self.assertRaises(context.ContextError):
            context.resolve(self.other)

    def test_symlinked_root_is_rejected(self):
        first = context.resolve(self.repo, initialize=True, confirm_no_writers=True)
        custody = Path(first["store_root"])
        moved = custody.with_name("redirected")
        custody.rename(moved)
        custody.symlink_to(moved, target_is_directory=True)
        with self.assertRaises(context.ContextError):
            context.resolve(self.repo)

    def test_configured_symlink_is_rejected_before_canonicalization(self):
        target = self.root / "outside"
        target.mkdir()
        link = self.root / "linked home"
        link.symlink_to(target, target_is_directory=True)
        for settings in ({"LEDGER_HOME": str(link)}, {"CODEX_HOME": str(link), "LEDGER_HOME": ""}):
            with self.subTest(settings=settings), patch.dict(os.environ, settings):
                with self.assertRaisesRegex(context.ContextError, "Symlink custody component"):
                    context.resolve(self.repo, initialize=True, confirm_no_writers=True)
        self.assertEqual(list(target.iterdir()), [])
        self.assertFalse((self.repo / ".git" / context.REGISTRATION).exists())

    def test_legacy_history_in_sibling_blocks_empty_initialization(self):
        legacy = self.other / ".ledger/learnings"
        legacy.mkdir(parents=True)
        (legacy / "events.jsonl").write_text("fixture\n")
        with self.assertRaises(context.ContextError):
            context.resolve(self.repo, initialize=True, confirm_no_writers=True)
        self.assertFalse(self.home.exists())

    def test_legacy_history_created_during_initialization_blocks_publication(self):
        inspect = context.legacy_roots
        inspections = 0

        def observe(root):
            nonlocal inspections
            inspections += 1
            if inspections == 2:
                legacy = self.other / ".ledger/learnings"
                legacy.mkdir(parents=True)
                (legacy / "events.jsonl").write_text("late append\n")
            return inspect(root)

        with patch.object(context, "legacy_roots", side_effect=observe):
            with self.assertRaisesRegex(context.ContextError, "appeared during initialization"):
                context.resolve(self.repo, initialize=True, confirm_no_writers=True)
        self.assertEqual(inspections, 2)
        self.assertFalse((self.repo / ".git" / context.REGISTRATION).exists())
        self.assertEqual(list((self.home / "ledger/repos").iterdir()), [])

    def test_retired_source_blocks_parallel_initialization(self):
        (self.other / ".learnings.jsonl").write_text("fixture\n")
        with self.assertRaises(context.ContextError):
            context.resolve(self.repo, initialize=True, confirm_no_writers=True)

    def test_non_repository_is_rejected(self):
        with self.assertRaises(context.ContextError):
            context.resolve(self.root, initialize=True, confirm_no_writers=True)
        self.assertFalse(self.home.exists())

    def test_registration_survives_common_directory_relocation(self):
        first = context.resolve(self.repo, initialize=True, confirm_no_writers=True)
        self.git(self.repo, "worktree", "remove", str(self.other))
        moved = self.root / "renamed repo"
        self.repo.rename(moved)
        self.assertEqual(context.resolve(moved)["store_root"], first["store_root"])

    def test_new_store_permissions_are_private(self):
        first = context.resolve(self.repo, initialize=True, confirm_no_writers=True)
        self.assertEqual(Path(first["store_root"]).stat().st_mode & 0o777, 0o700)
        self.assertEqual((Path(first["store_root"]) / context.MARKER).stat().st_mode & 0o777, 0o600)

    def test_relative_storage_override_is_rejected(self):
        with patch.dict(os.environ, {"LEDGER_HOME": "relative"}), self.assertRaises(context.ContextError):
            context.resolve(self.repo, initialize=True, confirm_no_writers=True)

    def test_duplicate_metadata_keys_are_rejected(self):
        first = context.resolve(self.repo, initialize=True, confirm_no_writers=True)
        marker = Path(first["store_root"]) / context.MARKER
        marker.write_text('{"schema":"ledger-storage-root/v1","store_id":"wrong","store_id":"' + first["store_id"] + '"}')
        with self.assertRaises(context.ContextError):
            context.resolve(self.repo)

    def test_cold_adoption_does_not_transport_native_advisory_sidecars(self):
        definition, event = self.adoption_fixture()
        event.with_name(event.name + ".cas.lock.advisory").write_text("")
        with patch.object(context, "native_doctor"):
            result = context.resolve(self.repo, initialize=True, adopt_from=self.repo,
                                     definitions=[definition], confirm_no_writers=True)
        self.assertFalse((Path(result["store_root"]) / ".ledger/example/events.jsonl.cas.lock.advisory").exists())

    def test_cold_adoption_requires_legacy_lease_recovery(self):
        definition, event = self.adoption_fixture()
        event.with_name(event.name + ".cas.lock").write_text("legacy lease")
        with patch.object(context, "native_doctor"), self.assertRaises(context.ContextError):
            context.resolve(self.repo, initialize=True, adopt_from=self.repo,
                            definitions=[definition], confirm_no_writers=True)

    def adoption_fixture(self):
        definition = self.root / "definition.json"
        definition.write_text(json.dumps({"storage": {"slots": {"events": {"path": "example/events.jsonl", "kind": "event-log", "codec": "jsonl"}}}}))
        source = self.repo / ".ledger/example"
        source.mkdir(parents=True)
        (source / "events.jsonl").write_text("original bytes\n")
        return definition, source / "events.jsonl"

    def test_cold_adoption_preserves_source_and_copies_only_after_doctor(self):
        definition, event = self.adoption_fixture()
        with patch.object(context, "native_doctor") as doctor:
            result = context.resolve(self.repo, initialize=True, adopt_from=self.repo,
                                     definitions=[definition], confirm_no_writers=True)
        self.assertEqual(doctor.call_count, 3)
        self.assertEqual(doctor.call_args.args[3], result["native_args"])
        self.assertEqual(event.read_bytes(), b"original bytes\n")
        copied = Path(result["store_root"]) / ".ledger/example/events.jsonl"
        self.assertEqual(copied.read_bytes(), event.read_bytes())
        self.assertNotEqual(copied.stat().st_ino, event.stat().st_ino)
        self.assertEqual(context.resolve(self.other)["store_id"], result["store_id"])

    def test_cold_adoption_rejects_divergent_sibling_without_registration(self):
        definition, _ = self.adoption_fixture()
        other = self.other / ".ledger/example"
        other.mkdir(parents=True)
        (other / "events.jsonl").write_text("different history\n")
        with patch.object(context, "native_doctor"), self.assertRaises(context.ContextError):
            context.resolve(self.repo, initialize=True, adopt_from=self.repo,
                            definitions=[definition], confirm_no_writers=True)
        self.assertFalse((self.repo / ".git" / context.REGISTRATION).exists())

    def test_cold_adoption_accepts_complete_prefix_without_discarding_rows(self):
        definition, event = self.adoption_fixture()
        event.write_text("first row\nsecond row\n")
        other = self.other / ".ledger/example"
        other.mkdir(parents=True)
        (other / "events.jsonl").write_text("first row\n")
        with patch.object(context, "native_doctor"):
            result = context.resolve(self.repo, initialize=True, adopt_from=self.repo,
                                     definitions=[definition], confirm_no_writers=True)
        self.assertEqual((Path(result["store_root"]) / ".ledger/example/events.jsonl").read_text(), event.read_text())

    def test_partial_record_prefix_is_not_accepted_as_history(self):
        definition, _ = self.adoption_fixture()
        other = self.other / ".ledger/example"
        other.mkdir(parents=True)
        (other / "events.jsonl").write_text("original")
        with patch.object(context, "native_doctor"), self.assertRaises(context.ContextError):
            context.resolve(self.repo, initialize=True, adopt_from=self.repo,
                            definitions=[definition], confirm_no_writers=True)

    def test_cold_adoption_does_not_relabel_unknown_legacy_data(self):
        definition, _ = self.adoption_fixture()
        (self.repo / ".ledger/unknown.jsonl").write_text("uncovered\n")
        with patch.object(context, "native_doctor"), self.assertRaises(context.ContextError):
            context.resolve(self.repo, initialize=True, adopt_from=self.repo,
                            definitions=[definition], confirm_no_writers=True)

    def test_cold_adoption_requires_explicit_quiescence_assertion(self):
        definition, _ = self.adoption_fixture()
        with self.assertRaises(context.ContextError):
            context.resolve(self.repo, initialize=True, adopt_from=self.repo, definitions=[definition])

    def test_malformed_definition_shape_returns_structured_context_error(self):
        definition, _ = self.adoption_fixture()
        for malformed in ({"storage": {"slots": []}},
                          {"storage": {"slots": {"events": []}}}):
            with self.subTest(malformed=malformed):
                definition.write_text(json.dumps(malformed))
                proc = subprocess.run(
                    [sys.executable, str(SCRIPT), "--repo", str(self.repo), "--initialize",
                     "--adopt-from", str(self.repo), "--definition", str(definition),
                     "--confirm-no-writers"], capture_output=True,
                )
                self.assertEqual(proc.returncode, 3)
                error = json.loads(proc.stderr)
                self.assertEqual(error["schema"], "ledger-workspace-context-error/v1")
                self.assertEqual(error["status"], "blocked")
                self.assertFalse((self.repo / ".git" / context.REGISTRATION).exists())

    def test_failed_destination_validation_does_not_publish(self):
        definition, _ = self.adoption_fixture()
        with patch.object(context, "native_doctor", side_effect=[None, context.ContextError("invalid")]):
            with self.assertRaises(context.ContextError):
                context.resolve(self.repo, initialize=True, adopt_from=self.repo,
                                definitions=[definition], confirm_no_writers=True)
        self.assertFalse((self.repo / ".git" / context.REGISTRATION).exists())
        self.assertEqual(list((self.home / "ledger/repos").iterdir()), [])


if __name__ == "__main__":
    unittest.main()
