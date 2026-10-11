"""Personal catalog policy tests; native custody is tested separately."""
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

    def capture_legacy_learning(self):
        definition = SCRIPT.parents[2] / 'learnings/tests/fixtures/pre-personal-history/learnings-protocol.json'
        submission = {'record': {'status': 'codify_now', 'learning': 'Preserve the linked worktree history.',
            'evidence': ['fixture:prior-native-capture'], 'application': 'Adopt before creating new custody.',
            'source': 'prior session', 'context': {'repo': str(self.repo), 'branch': 'original', 'paths': []}}}
        result = subprocess.run([os.environ['LEDGER_BIN'], 'transact', '--definition', str(definition),
            '--repo', str(self.other), '--operation', 'capture', '--input', 'submission=-', '--format', 'json'],
            input=json.dumps(submission).encode(), capture_output=True,
            env=dict(os.environ, LEDGER_CACHE_DIR=str(self.root / 'native-cache')))
        self.assertEqual(result.returncode, 0, (result.stdout + result.stderr).decode())
        self.assertEqual(json.loads(result.stdout)['effects'][0]['result'], 'appended')

    def legacy_custody_snapshot(self):
        control = self.other / '.ledger'
        return {str(path.relative_to(control)): path.read_bytes()
                for path in control.rglob('*') if path.is_file()}

    def test_read_only_resolution_does_not_initialize(self):
        with self.assertRaises(context.ContextError):
            context.resolve(self.repo)
        self.assertFalse(self.home.exists())
        self.assertFalse((self.repo / ".git" / context.REGISTRATION).exists())
        self.assertFalse((self.repo / ".git" / "ledger-store.lock").exists())

    def test_new_private_store_does_not_require_legacy_writer_quiescence(self):
        result = context.resolve(self.repo, initialize=True)
        self.assertTrue(Path(result['store_root']).is_dir())
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

    def test_reused_worktree_path_cannot_select_the_previous_git_family(self):
        first = context.resolve(self.other, initialize=True)
        catalog = (context.storage_home() / context.CATALOG).read_bytes()
        self.git(self.repo, 'worktree', 'remove', str(self.other))
        self.other.mkdir()
        self.git(self.other, 'init', '-q')
        for parameters in ({}, {'initialize': True}):
            with self.subTest(parameters=parameters), self.assertRaisesRegex(context.ContextError, 'Git common directory'):
                context.resolve(self.other, **parameters)
        # An unchanged family association and explicit ID access remain usable.
        self.assertEqual(context.resolve(self.repo)['store_id'], first['store_id'])
        self.assertEqual(context.resolve(store_id=first['store_id'])['store_root'], first['store_root'])
        self.assertEqual((context.storage_home() / context.CATALOG).read_bytes(), catalog)

    def test_new_git_identity_on_plain_workspace_requires_explicit_attachment(self):
        plain = self.root / 'plain workspace'; plain.mkdir()
        first = context.resolve(plain, initialize=True)
        self.git(plain, 'init', '-q')
        with self.assertRaisesRegex(context.ContextError, 'Git common directory'):
            context.resolve(plain)
        attached = context.resolve(plain, store_id=first['store_id'], attach_workspace=True)
        self.assertEqual(attached['store_id'], first['store_id'])
        self.assertEqual(context.resolve(plain)['store_root'], first['store_root'])

    def test_clone_is_not_automatically_attached(self):
        first = context.resolve(self.repo, initialize=True, confirm_no_writers=True)
        clone = self.root / "clone"
        subprocess.run(["git", "clone", "-q", str(self.repo), str(clone)], check=True)
        second = context.resolve(clone, initialize=True, confirm_no_writers=True)
        self.assertNotEqual(first["store_id"], second["store_id"])

    def test_environment_change_never_implicitly_initializes_an_unknown_catalog(self):
        first = context.resolve(self.repo, initialize=True, confirm_no_writers=True)
        with patch.dict(os.environ, {"CODEX_HOME": str(self.root / "different"), "LEDGER_HOME": str(self.root / "override")}):
            with self.assertRaises(context.UnregisteredContext):
                context.resolve(self.other)
            with self.assertRaises(context.ContextError):
                context.resolve(store_id=first['store_id'], initialize=True)
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

    def test_known_selected_legacy_history_blocks_parallel_empty_initialization(self):
        legacy = self.repo / ".ledger/learnings"
        legacy.mkdir(parents=True)
        (legacy / "events.jsonl").write_text("fixture\n")
        with self.assertRaises(context.ContextError):
            context.resolve(self.repo, initialize=True, confirm_no_writers=True)
        self.assertFalse(self.home.exists())

    def test_selected_legacy_history_created_during_initialization_blocks_publication(self):
        write = context.write_json

        def observe(path, value):
            write(path, value)
            if path.name == context.MARKER:
                legacy = self.repo / ".ledger/learnings"
                legacy.mkdir(parents=True)
                (legacy / "events.jsonl").write_text("late append\n")

        with patch.object(context, "write_json", side_effect=observe):
            with self.assertRaisesRegex(context.ContextError, "legacy history"):
                context.resolve(self.repo, initialize=True, confirm_no_writers=True)
        self.assertFalse((self.repo / ".git" / context.REGISTRATION).exists())
        self.assertEqual(list((self.home / "ledger/repos").iterdir()), [])

    def test_retired_source_blocks_parallel_initialization(self):
        (self.repo / ".learnings.jsonl").write_text("fixture\n")
        with self.assertRaises(context.ContextError):
            context.resolve(self.repo, initialize=True, confirm_no_writers=True)

    def test_sibling_retired_sources_block_new_family_custody(self):
        for retired in ('.learnings.jsonl', '.ledger/learnings/learnings.jsonl'):
            with self.subTest(retired=retired):
                source = self.other / retired
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_bytes(b'preserved retired source\n')
                with self.assertRaisesRegex(context.ContextError, 'Retired source|legacy history'):
                    context.resolve(self.repo, initialize=True)
                self.assertEqual(source.read_bytes(), b'preserved retired source\n')
                self.assertFalse(self.home.exists())
                source.unlink()
                if (self.other / '.ledger').exists():
                    shutil.rmtree(self.other / '.ledger')

    def test_missing_sibling_blocks_creation_but_not_existing_adoption_and_access(self):
        shutil.rmtree(self.other)
        with self.assertRaisesRegex(context.ContextError, 'unavailable worktree'):
            context.resolve(self.repo, initialize=True)
        self.assertFalse(self.home.exists())
        custody, store_id = self.existing_root()
        registration = self.repo / '.git' / context.REGISTRATION
        context.write_json(registration, {'schema': context.REGISTRATION_SCHEMA,
                                          'store_id': store_id, 'store_root': str(custody)})
        with patch.object(context, 'worktrees', side_effect=AssertionError('existing custody needs no family inventory')):
            adopted = context.import_registration(registration, self.repo)
            self.assertEqual(adopted['store_id'], store_id)
            self.assertEqual(context.resolve(self.repo)['store_id'], store_id)
            self.assertEqual(context.resolve(self.repo, initialize=True)['store_id'], store_id)
            self.assertEqual(context.resolve(store_id=store_id)['store_root'], str(custody))

    @unittest.skipUnless(os.environ.get('LEDGER_BIN'), 'Set LEDGER_BIN for the real native legacy fixture')
    def test_native_sibling_history_blocks_empty_family_initialization(self):
        self.capture_legacy_learning()
        original = self.legacy_custody_snapshot()
        with self.assertRaisesRegex(context.ContextError, 'Linked worktrees contain legacy history'):
            context.resolve(self.repo, initialize=True)
        self.assertFalse(self.home.exists())
        self.assertEqual(self.legacy_custody_snapshot(), original)
        definition = SCRIPT.parents[2] / 'learnings/definitions/ledger/learnings-protocol.json'
        projection = subprocess.run([os.environ['LEDGER_BIN'], 'project', '--definition', str(definition),
            '--repo', str(self.other), '--projection', 'import-records', '--format', 'json'], capture_output=True,
            env=dict(os.environ, LEDGER_CACHE_DIR=str(self.root / 'native-cache')))
        self.assertEqual(projection.returncode, 0, (projection.stdout + projection.stderr).decode())
        self.assertEqual(len(json.loads(projection.stdout)['data']), 1)
        self.assertEqual(self.legacy_custody_snapshot(), original)

    @unittest.skipUnless(os.environ.get('LEDGER_BIN'), 'Set LEDGER_BIN for the real native legacy fixture')
    def test_late_native_sibling_history_blocks_catalog_publication(self):
        sync = context.sync_directory
        captured = False

        def append_after_final_root_sync(path):
            nonlocal captured
            sync(path)
            if path == self.home / 'ledger/repos' and not captured:
                captured = True
                self.capture_legacy_learning()

        with patch.object(context, 'sync_directory', side_effect=append_after_final_root_sync):
            with self.assertRaisesRegex(context.ContextError, 'Linked worktrees contain legacy history'):
                context.resolve(self.repo, initialize=True)
        self.assertTrue(captured)
        self.assertFalse((self.home / 'ledger/catalog.json').exists())
        self.assertEqual(context.list_stores()['stores'], [])
        self.assertEqual(len((self.other / '.ledger/learnings/events.jsonl').read_bytes().splitlines()), 1)
        with self.assertRaises(context.UnregisteredContext):
            context.resolve(self.repo)

    def test_personal_store_and_plain_workspace_need_no_git(self):
        with patch.object(context, 'git', side_effect=FileNotFoundError('Git is not installed')):
            first = context.resolve(self.root, initialize=True)
        direct = context.resolve(store_id=first['store_id'])
        self.assertEqual(first['store_root'], direct['store_root'])
        self.assertIsNone(direct['workspace_root'])
        self.assertIsNone(direct['git_common_dir'])
        self.assertEqual(context.resolve(self.root)['store_id'], first['store_id'])

    def test_registration_survives_common_directory_relocation(self):
        first = context.resolve(self.repo, initialize=True, confirm_no_writers=True)
        self.git(self.repo, "worktree", "remove", str(self.other))
        moved = self.root / "renamed repo"
        self.repo.rename(moved)
        second = context.resolve(moved, store_id=first['store_id'], attach_workspace=True)
        self.assertEqual(second['store_root'], first['store_root'])
        self.assertEqual(context.resolve(moved)['store_id'], first['store_id'])

    def test_new_store_permissions_are_private(self):
        first = context.resolve(self.repo, initialize=True, confirm_no_writers=True)
        self.assertEqual(Path(first["store_root"]).stat().st_mode & 0o777, 0o700)
        self.assertEqual((Path(first["store_root"]) / context.MARKER).stat().st_mode & 0o777, 0o600)
        self.assertEqual((context.storage_home() / context.CATALOG).stat().st_mode & 0o777, 0o600)

    def test_missing_sibling_and_append_do_not_requalify_existing_custody(self):
        first = context.resolve(self.repo, initialize=True)
        # Addressing fixture only: native event validity belongs to owner tests.
        (Path(first['store_root']) / '.ledger/fixture').write_text('later append\n')
        shutil.rmtree(self.other)
        with patch.object(context, 'worktrees', side_effect=AssertionError('normal use must not enumerate worktrees')):
            result = context.resolve(self.repo)
        self.assertEqual(result['store_id'], first['store_id'])
        self.assertFalse(result['storage_mutated'])
        self.assertFalse((Path(first['store_root']) / 'migration-receipt.json').exists())

    def test_direct_access_after_all_git_metadata_is_deleted(self):
        first = context.resolve(self.repo, initialize=True)
        shutil.rmtree(self.repo)
        shutil.rmtree(self.other)
        with patch.object(context, 'git', side_effect=AssertionError('direct selection must not run Git')):
            result = context.resolve(store_id=first['store_id'])
        self.assertEqual(result['native_args'], first['native_args'])
        self.assertEqual(result['repository_id'], first['repository_id'])

    def test_absent_explicit_identity_is_never_reinitialized(self):
        with self.assertRaisesRegex(context.ContextError, 'not cataloged'):
            context.resolve(store_id='a' * 32, initialize=True)
        self.assertFalse(self.home.exists())

    def test_missing_catalog_never_masks_existing_roots_with_empty_initialization(self):
        first = context.resolve(self.repo, initialize=True)
        (context.storage_home() / context.CATALOG).unlink()
        with self.assertRaisesRegex(context.ContextError, 'lack a catalog'):
            context.resolve(self.repo, initialize=True)
        restored = context.register_root(Path(first['store_root']), first['store_id'], self.repo)
        self.assertEqual(restored['store_id'], first['store_id'])

    def test_read_only_listing_recovers_store_identity_after_checkout_deletion(self):
        first = context.resolve(self.repo, initialize=True)
        catalog = (context.storage_home() / context.CATALOG).read_bytes()
        shutil.rmtree(self.repo)
        shutil.rmtree(self.other)
        proc = subprocess.run([sys.executable, str(SCRIPT), '--list-stores'], capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr.decode())
        result = json.loads(proc.stdout)
        self.assertFalse(result['storage_mutated'])
        self.assertEqual(result['stores'][0]['store_id'], first['store_id'])
        self.assertIn('workspace:' + str(self.repo), result['stores'][0]['aliases'])
        self.assertNotIn('healthy', result['stores'][0])
        self.assertEqual(catalog, (context.storage_home() / context.CATALOG).read_bytes())

    def test_empty_catalog_listing_is_read_only(self):
        self.assertEqual(context.list_stores()['stores'], [])
        self.assertFalse(self.home.exists())

    def test_oversized_catalog_update_preserves_readable_metadata(self):
        first = context.resolve(self.repo, initialize=True)
        home = context.storage_home()
        before = (home / context.CATALOG).read_bytes()
        catalog = context.read_catalog(home)
        catalog['aliases']['workspace:/' + 'x' * 1048576] = first['store_id']
        with self.assertRaisesRegex(context.ContextError, 'size bound'):
            context.publish_catalog(home, catalog)
        self.assertEqual(before, (home / context.CATALOG).read_bytes())
        self.assertEqual(context.resolve(store_id=first['store_id'])['store_root'], first['store_root'])

    def existing_root(self):
        custody = self.root / 'existing custody'
        (custody / '.ledger').mkdir(parents=True)
        store_id = 'a' * 32
        context.write_json(custody / context.MARKER, {'schema': context.MARKER_SCHEMA, 'store_id': store_id})
        return custody, store_id

    def test_explicit_root_catalog_adoption_needs_no_checkout(self):
        custody, store_id = self.existing_root()
        shutil.rmtree(self.repo)
        shutil.rmtree(self.other)
        before = (custody / context.MARKER).read_bytes()
        with patch.object(context, 'git', side_effect=AssertionError('no Git')):
            first = context.register_root(custody, store_id)
            second = context.resolve(store_id=store_id)
        self.assertEqual(first['store_id'], second['store_id'])
        self.assertEqual(before, (custody / context.MARKER).read_bytes())
        self.assertFalse(context.register_root(custody, store_id)['storage_mutated'])

    def test_legacy_registration_is_imported_explicitly_without_fallback(self):
        custody, store_id = self.existing_root()
        registration = self.repo / '.git' / context.REGISTRATION
        context.write_json(registration, {'schema': context.REGISTRATION_SCHEMA,
                                          'store_id': store_id, 'store_root': str(custody)})
        before = registration.read_bytes()
        with self.assertRaises(context.UnregisteredContext):
            context.resolve(self.repo)
        with self.assertRaisesRegex(context.ContextError, 'must be imported'):
            context.resolve(self.repo, initialize=True)
        result = context.import_registration(registration, self.repo)
        self.assertEqual(result['store_id'], store_id)
        self.assertEqual(context.resolve(self.other)['store_root'], str(custody))
        self.assertEqual(before, registration.read_bytes())

    def test_adoption_does_not_hide_a_different_legacy_registration(self):
        custody, store_id = self.existing_root()
        registration = self.repo / '.git' / context.REGISTRATION
        context.write_json(registration, {'schema': context.REGISTRATION_SCHEMA,
                                          'store_id': store_id, 'store_root': str(custody)})
        other = context.resolve(initialize=True)
        with self.assertRaisesRegex(context.ContextError, 'different legacy registration'):
            context.register_root(Path(other['store_root']), other['store_id'], self.repo)
        with self.assertRaises(context.UnregisteredContext):
            context.resolve(self.repo)

    def test_alias_conflict_never_overwrites_an_established_history(self):
        first = context.resolve(self.repo, initialize=True)
        second = context.resolve(initialize=True)
        catalog = (context.storage_home() / context.CATALOG).read_bytes()
        with self.assertRaisesRegex(context.ContextError, 'Conflicting'):
            context.resolve(self.repo, store_id=second['store_id'], attach_workspace=True)
        self.assertEqual((context.storage_home() / context.CATALOG).read_bytes(), catalog)
        self.assertEqual(context.resolve(self.repo)['store_id'], first['store_id'])

    def test_store_root_conflict_is_not_a_relocation(self):
        first = context.resolve(self.repo, initialize=True)
        copy = self.root / 'another root'
        shutil.copytree(first['store_root'], copy)
        with self.assertRaisesRegex(context.ContextError, 'another root'):
            context.register_root(copy, first['store_id'])

    def test_catalog_symlink_and_duplicate_metadata_are_rejected(self):
        first = context.resolve(self.repo, initialize=True)
        catalog = context.storage_home() / context.CATALOG
        saved = catalog.read_bytes()
        target = self.root / 'catalog-copy.json'
        target.write_bytes(saved)
        catalog.unlink()
        catalog.symlink_to(target)
        with self.assertRaisesRegex(context.ContextError, 'Symlink'):
            context.resolve(store_id=first['store_id'])
        catalog.unlink()
        catalog.write_text('{"schema":"bad","schema":"duplicate","stores":{},"aliases":{}}')
        with self.assertRaisesRegex(context.ContextError, 'Invalid metadata'):
            context.resolve(store_id=first['store_id'])

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
