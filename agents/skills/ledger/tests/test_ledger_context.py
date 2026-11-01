from concurrent.futures import ThreadPoolExecutor
import importlib.util
import hashlib
import json
import os
from pathlib import Path
import shutil
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import native_host as context
ensure_module = context
SKILLS = Path(__file__).resolve().parents[2]


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
        definition = SKILLS / 'learnings/tests/fixtures/pre-personal-history/learnings-protocol.json'
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
        argv = context.command(self.repo) + ["--initialize"]
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
            with self.subTest(parameters=parameters), self.assertRaisesRegex(context.ContextError, '[Gg]itCommonDirectory'):
                context.resolve(self.other, **parameters)
        # An unchanged family association and explicit ID access remain usable.
        self.assertEqual(context.resolve(self.repo)['store_id'], first['store_id'])
        self.assertEqual(context.resolve(store_id=first['store_id'])['store_root'], first['store_root'])
        self.assertEqual((context.storage_home() / context.CATALOG).read_bytes(), catalog)
        attached = context.resolve(self.other, store_id=first['store_id'], attach_workspace=True)
        self.assertEqual(attached['store_id'], first['store_id'])
        self.assertEqual(context.resolve(self.other)['store_root'], first['store_root'])

    def test_new_git_identity_on_plain_workspace_requires_explicit_attachment(self):
        plain = self.root / 'plain workspace'; plain.mkdir()
        first = context.resolve(plain, initialize=True)
        self.git(plain, 'init', '-q')
        with self.assertRaisesRegex(context.ContextError, '[Gg]itCommonDirectory'):
            context.resolve(plain)
        attached = context.resolve(plain, store_id=first['store_id'], attach_workspace=True)
        self.assertEqual(attached['store_id'], first['store_id'])
        self.assertEqual(context.resolve(plain)['store_root'], first['store_root'])

    def test_vanished_git_identity_cannot_authenticate_a_workspace_path(self):
        first = context.resolve(self.other, initialize=True)
        catalog_path = context.storage_home() / context.CATALOG
        saved = catalog_path.read_bytes()
        self.git(self.repo, 'worktree', 'remove', str(self.other))
        # Both the absent checkout and an unrelated plain replacement fail.
        for recreated in (False, True):
            if recreated:
                self.other.mkdir()
            for parameters in ({}, {'initialize': True},
                               {'store_id': first['store_id'], 'attach_workspace': True}):
                with self.subTest(recreated=recreated, parameters=parameters):
                    with self.assertRaisesRegex(context.ContextError, '[Gg]itCommonDirectory'):
                        context.resolve(self.other, **parameters)
            self.assertEqual(catalog_path.read_bytes(), saved)
        self.assertEqual(context.resolve(store_id=first['store_id'])['store_root'], first['store_root'])
        self.assertEqual(context.resolve(self.repo)['store_id'], first['store_id'])

    def test_legacy_git_alias_without_provenance_fails_closed(self):
        first = context.resolve(self.other, initialize=True)
        catalog_path = context.storage_home() / context.CATALOG
        catalog = json.loads(catalog_path.read_bytes())
        del catalog['workspace_identities']
        catalog_path.write_text(json.dumps(catalog))
        self.git(self.repo, 'worktree', 'remove', str(self.other))
        self.other.mkdir()
        with self.assertRaisesRegex(context.ContextError, '[Gg]itCommonDirectory'):
            context.resolve(self.other)
        self.assertEqual(context.resolve(store_id=first['store_id'])['store_root'], first['store_root'])

    def test_plain_alias_remains_usable_in_a_store_with_git_associations(self):
        plain = self.root / 'plain workspace'; plain.mkdir()
        first = context.resolve(plain, initialize=True)
        context.resolve(self.repo, store_id=first['store_id'], attach_workspace=True)
        self.assertEqual(context.resolve(plain)['store_id'], first['store_id'])

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
        with self.assertRaisesRegex(context.ContextError, "StorageRootMissing"):
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
                with self.assertRaisesRegex(context.ContextError, "Sym[Ll]ink|NotDir"):
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

    def test_retired_source_blocks_parallel_initialization(self):
        (self.repo / ".learnings.jsonl").write_text("fixture\n")
        with self.assertRaises(context.ContextError):
            context.resolve(self.repo, initialize=True, legacy_paths=(".learnings.jsonl",), confirm_no_writers=True)

    def test_sibling_retired_sources_block_new_family_custody(self):
        for retired in ('.learnings.jsonl', '.ledger/learnings/learnings.jsonl'):
            with self.subTest(retired=retired):
                source = self.other / retired
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_bytes(b'preserved retired source\n')
                with self.assertRaisesRegex(context.ContextError, 'RetiredSource|LinkedWorktreeHistory'):
                    context.resolve(self.repo, initialize=True, legacy_paths=('.learnings.jsonl',))
                self.assertEqual(source.read_bytes(), b'preserved retired source\n')
                self.assertFalse(self.home.exists())
                source.unlink()
                if (self.other / '.ledger').exists():
                    shutil.rmtree(self.other / '.ledger')

    def test_missing_sibling_blocks_creation_but_not_existing_adoption_and_access(self):
        shutil.rmtree(self.other)
        with self.assertRaisesRegex(context.ContextError, 'UnavailableWorktree'):
            context.resolve(self.repo, initialize=True)
        self.assertFalse(self.home.exists())
        custody, store_id = self.existing_root()
        registration = self.repo / '.git' / context.REGISTRATION
        context.write_json(registration, {'schema': context.REGISTRATION_SCHEMA,
                                          'store_id': store_id, 'store_root': str(custody)})
        adopted = context.import_registration(registration, self.repo)
        self.assertEqual(adopted['store_id'], store_id)
        self.assertEqual(context.resolve(self.repo)['store_id'], store_id)
        self.assertEqual(context.resolve(self.repo, initialize=True)['store_id'], store_id)
        self.assertEqual(context.resolve(store_id=store_id)['store_root'], str(custody))

    @unittest.skipUnless(os.environ.get('LEDGER_BIN'), 'Set LEDGER_BIN for the real native legacy fixture')
    def test_native_sibling_history_blocks_empty_family_initialization(self):
        self.capture_legacy_learning()
        original = self.legacy_custody_snapshot()
        with self.assertRaisesRegex(context.ContextError, 'LinkedWorktreeHistoryRequiresMigration'):
            context.resolve(self.repo, initialize=True)
        self.assertFalse(self.home.exists())
        self.assertEqual(self.legacy_custody_snapshot(), original)
        definition = SKILLS / 'learnings/definitions/ledger/learnings-protocol.json'
        projection = subprocess.run([os.environ['LEDGER_BIN'], 'project', '--definition', str(definition),
            '--repo', str(self.other), '--projection', 'import-records', '--format', 'json'], capture_output=True,
            env=dict(os.environ, LEDGER_CACHE_DIR=str(self.root / 'native-cache')))
        self.assertEqual(projection.returncode, 0, (projection.stdout + projection.stderr).decode())
        self.assertEqual(len(json.loads(projection.stdout)['data']), 1)
        self.assertEqual(self.legacy_custody_snapshot(), original)


    def test_personal_store_and_plain_workspace_need_no_git(self):
        with patch.dict(os.environ, {'PATH': '/nonexistent'}):
            first = context.resolve(self.root, initialize=True)
        direct = context.resolve(store_id=first['store_id'])
        self.assertEqual(first['store_root'], direct['store_root'])
        self.assertIsNone(direct['workspace_root'])
        self.assertIsNone(direct['git_common_dir'])
        self.assertEqual(context.resolve(self.root)['store_id'], first['store_id'])

    def test_failed_git_common_lookup_cannot_initialize_a_second_family_identity(self):
        first = context.resolve(self.other, initialize=True)
        before = (context.storage_home() / context.CATALOG).read_bytes()
        roots = sorted(path.name for path in (context.storage_home() / 'repos').iterdir())
        real_git = shutil.which('git')
        wrapper = self.root / 'git-wrapper'
        wrapper.mkdir()
        executable = wrapper / 'git'
        executable.write_text('#!/bin/sh\nfor arg do\n'
            '  if [ "$arg" = "--git-common-dir" ]; then exit 71; fi\n'
            'done\nexec ' + shlex.quote(real_git) + ' "$@"\n')
        executable.chmod(0o700)
        nested = self.repo / 'nested'
        nested.mkdir()
        for workspace in (self.repo, nested):
            with self.subTest(workspace=workspace), patch.dict(os.environ, {'PATH': str(wrapper)}):
                with self.assertRaises(context.ContextError):
                    context.resolve(workspace, initialize=True)
            self.assertEqual((context.storage_home() / context.CATALOG).read_bytes(), before)
            self.assertEqual(sorted(path.name for path in (context.storage_home() / 'repos').iterdir()), roots)
        self.assertEqual(context.resolve(self.repo)['store_id'], first['store_id'])

    def test_missing_git_does_not_hide_repository_or_bare_evidence(self):
        bare = self.root / 'bare'
        self.git(self.root, 'init', '--bare', '-q', str(bare))
        (bare / 'HEAD').unlink()
        nested = self.repo / 'nested'
        nested.mkdir()
        for workspace in (self.repo, nested, self.other, bare):
            with self.subTest(workspace=workspace), patch.dict(os.environ, {'PATH': '/nonexistent'}):
                with self.assertRaises(context.ContextError):
                    context.resolve(workspace, initialize=True)
            self.assertFalse(self.home.exists())

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
        result = context.resolve(self.repo)
        self.assertEqual(result['store_id'], first['store_id'])
        self.assertFalse(result['storage_mutated'])
        self.assertFalse((Path(first['store_root']) / 'migration-receipt.json').exists())

    def test_direct_access_after_all_git_metadata_is_deleted(self):
        first = context.resolve(self.repo, initialize=True)
        shutil.rmtree(self.repo)
        shutil.rmtree(self.other)
        with patch.dict(os.environ, {'PATH': '/nonexistent'}):
            result = context.resolve(store_id=first['store_id'])
        self.assertEqual(result['native_args'], first['native_args'])
        self.assertEqual(result['repository_id'], first['repository_id'])

    def test_absent_explicit_identity_is_never_reinitialized(self):
        with self.assertRaisesRegex(context.ContextError, 'SelectedStoreNotCataloged'):
            context.resolve(store_id='a' * 32, initialize=True)
        self.assertFalse(self.home.exists())

    def test_missing_catalog_never_masks_existing_roots_with_empty_initialization(self):
        first = context.resolve(self.repo, initialize=True)
        (context.storage_home() / context.CATALOG).unlink()
        with self.assertRaisesRegex(context.ContextError, 'ExistingCustodyWithoutCatalog'):
            context.resolve(self.repo, initialize=True)
        restored = context.register_root(Path(first['store_root']), first['store_id'], self.repo)
        self.assertEqual(restored['store_id'], first['store_id'])

    def test_read_only_listing_recovers_store_identity_after_checkout_deletion(self):
        first = context.resolve(self.repo, initialize=True)
        catalog = (context.storage_home() / context.CATALOG).read_bytes()
        shutil.rmtree(self.repo)
        shutil.rmtree(self.other)
        proc = subprocess.run(context.command() + ['--list-stores'], capture_output=True)
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
        with patch.dict(os.environ, {'PATH': '/nonexistent'}):
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
        with self.assertRaisesRegex(context.ContextError, 'RegistrationRequiresImport'):
            context.resolve(self.repo, initialize=True)
        result = context.import_registration(registration, self.repo)
        self.assertEqual(result['store_id'], store_id)
        self.assertEqual(context.resolve(self.other)['store_root'], str(custody))
        self.assertEqual(before, registration.read_bytes())

    def registered_legacy_root(self):
        custody, store_id = self.existing_root()
        registration = self.repo / '.git' / context.REGISTRATION
        context.write_json(registration, {'schema': context.REGISTRATION_SCHEMA,
                                          'store_id': store_id, 'store_root': str(custody)})
        return custody, store_id, registration

    def test_ensure_adopts_from_linked_worktree_once_without_touching_custody(self):
        custody, store_id, registration = self.registered_legacy_root()
        (custody / '.ledger/opaque-fixture').write_bytes(b'preserve existing custody\n')
        before = {str(p.relative_to(custody)): p.read_bytes()
                  for p in custody.rglob('*') if p.is_file()}
        registration_bytes = registration.read_bytes()
        # No family scan is needed, even with an unavailable sibling.
        missing = self.root / 'missing worktree'
        self.git(self.repo, 'worktree', 'add', '--detach', str(missing))
        shutil.rmtree(missing)
        first = ensure_module.ensure(self.other)
        self.assertEqual(first['store_id'], store_id)
        self.assertEqual(first['store_root'], str(custody))
        self.assertTrue(first['storage_mutated'])
        catalog = (context.storage_home() / context.CATALOG).read_bytes()
        self.assertFalse(ensure_module.ensure(self.other)['storage_mutated'])
        self.assertFalse(ensure_module.ensure(self.repo)['storage_mutated'])
        self.assertEqual(context.resolve(store_id=store_id)['store_root'], str(custody))
        self.assertEqual((context.storage_home() / context.CATALOG).read_bytes(), catalog)
        self.assertEqual(registration.read_bytes(), registration_bytes)
        self.assertEqual(before, {str(p.relative_to(custody)): p.read_bytes()
                                  for p in custody.rglob('*') if p.is_file()})

    def test_ensure_does_not_create_history_or_adopt_explicit_unknown_identity(self):
        with self.assertRaises(RuntimeError):
            ensure_module.ensure(self.repo)
        self.assertFalse(self.home.exists())
        self.registered_legacy_root()
        with self.assertRaisesRegex(RuntimeError, 'SelectedStoreNotCataloged'):
            ensure_module.ensure(self.repo, store_id='b' * 32)
        self.assertFalse(self.home.exists())

    def test_ensure_rejects_invalid_registration_without_catalog_publication(self):
        custody, store_id, registration = self.registered_legacy_root()
        original = registration.read_bytes()
        for value in (b'{broken', original.replace(store_id.encode(), b'b' * 32)):
            with self.subTest(value=value):
                registration.write_bytes(value)
                with self.assertRaises(RuntimeError):
                    ensure_module.ensure(self.repo)
                self.assertFalse((context.storage_home() / context.CATALOG).exists())
        registration.write_bytes(original)
        shutil.rmtree(custody)
        with self.assertRaises((RuntimeError, OSError)):
            ensure_module.ensure(self.repo)
        self.assertFalse((context.storage_home() / context.CATALOG).exists())
        self.assertFalse(custody.exists())

    def test_ensure_cannot_replace_cataloged_store_root(self):
        custody, store_id, _ = self.registered_legacy_root()
        other = self.root / 'other custody'
        shutil.copytree(custody, other)
        context.register_root(other, store_id)
        catalog = (context.storage_home() / context.CATALOG).read_bytes()
        with self.assertRaisesRegex(RuntimeError, 'AnotherRoot'):
            ensure_module.ensure(self.repo)
        self.assertEqual((context.storage_home() / context.CATALOG).read_bytes(), catalog)

    def test_concurrent_ensures_adopt_one_identity(self):
        custody, store_id, _ = self.registered_legacy_root()
        argv = context.command(self.other) + ['--ensure']
        def invoke(_):
            return json.loads(subprocess.run(argv, check=True, capture_output=True).stdout)
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(invoke, range(8)))
        self.assertEqual({row['store_id'] for row in results}, {store_id})
        self.assertEqual(sum(row['storage_mutated'] for row in results), 1)
        self.assertEqual(context.resolve(self.repo)['store_root'], str(custody))

    def test_adoption_does_not_hide_a_different_legacy_registration(self):
        custody, store_id = self.existing_root()
        registration = self.repo / '.git' / context.REGISTRATION
        context.write_json(registration, {'schema': context.REGISTRATION_SCHEMA,
                                          'store_id': store_id, 'store_root': str(custody)})
        other = context.resolve(initialize=True)
        with self.assertRaisesRegex(context.ContextError, 'DifferentLegacyRegistration'):
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
        copy = self.root / 'AnotherRoot'
        shutil.copytree(first['store_root'], copy)
        with self.assertRaisesRegex(context.ContextError, 'AnotherRoot'):
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
        with self.assertRaisesRegex(context.ContextError, 'InvalidPersonalCatalog'):
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

    def test_malformed_definition_shape_returns_structured_context_error(self):
        definition = self.root / 'definition.json'
        for malformed in ({'storage': {'slots': []}}, {'storage': {'slots': {'events': []}}}):
            with self.subTest(malformed=malformed):
                definition.write_text(json.dumps(malformed))
                proc = subprocess.run(context.command(self.repo) + ['--initialize',
                    '--adopt-from', str(self.repo), '--definition', str(definition),
                    '--confirm-no-writers'], capture_output=True)
                self.assertEqual(proc.returncode, 3)
                result = json.loads(proc.stdout)
                self.assertEqual(result['schema'], 'ledger-workspace-context-error/v1')
                self.assertEqual(result['status'], 'blocked')
                self.assertFalse((self.home / 'ledger/catalog.json').exists())


    def cold_fixture(self):
        self.capture_legacy_learning()
        return SKILLS / 'learnings/definitions/ledger/learnings-protocol.json'

    def cold_adopt(self, definition, confirm=True):
        return context.resolve(self.repo, initialize=True, adopt_from=self.other,
                               definitions=[definition], confirm_no_writers=confirm)

    def test_cold_adoption_retains_orphan_with_an_existing_catalog_until_registered(self):
        unrelated = context.resolve(initialize=True)
        catalog = context.storage_home() / context.CATALOG
        original_catalog = catalog.read_bytes()
        definition = self.cold_fixture()
        retained = self.cold_adopt(definition)
        # The public root exists but its catalog publication did not survive.
        catalog.write_bytes(original_catalog)
        roots = sorted(path.name for path in (context.storage_home() / 'repos').iterdir())
        before = {str(path.relative_to(context.storage_home())): path.read_bytes()
                  for path in context.storage_home().rglob('*') if path.is_file()}
        for attempt in range(3):
            with self.subTest(attempt=attempt), self.assertRaisesRegex(context.ContextError, 'UnregisteredCustodyExists'):
                self.cold_adopt(definition)
            self.assertEqual(sorted(path.name for path in (context.storage_home() / 'repos').iterdir()), roots)
            self.assertEqual({str(path.relative_to(context.storage_home())): path.read_bytes()
                              for path in context.storage_home().rglob('*') if path.is_file()}, before)
        restored = context.register_root(Path(retained['store_root']), retained['store_id'], self.repo)
        self.assertEqual(restored['store_root'], retained['store_root'])
        self.assertEqual(context.resolve(self.other)['store_id'], retained['store_id'])
        self.assertEqual(context.resolve(store_id=unrelated['store_id'])['store_root'], unrelated['store_root'])
        self.assertEqual(sorted(path.name for path in (context.storage_home() / 'repos').iterdir()), roots)

    def test_cold_adoption_preserves_native_history_and_excludes_advisory_sidecars(self):
        definition = self.cold_fixture()
        before = self.legacy_custody_snapshot()
        result = self.cold_adopt(definition)
        root = Path(result['store_root'])
        self.assertEqual(before, self.legacy_custody_snapshot())
        self.assertFalse(list((root / '.ledger').rglob('*.cas.lock.advisory')))
        source = self.other / '.ledger/learnings/events.jsonl'
        target = root / '.ledger/learnings/events.jsonl'
        self.assertEqual(source.read_bytes(), target.read_bytes())
        self.assertNotEqual(source.stat().st_ino, target.stat().st_ino)
        self.assertEqual(context.resolve(self.other)['store_id'], result['store_id'])
        read = subprocess.run([os.environ['LEDGER_BIN'], 'project', '--definition', str(definition),
            *result['native_args'], '--projection', 'import-records', '--format', 'json'], capture_output=True)
        self.assertEqual(read.returncode, 0, read.stdout + read.stderr)
        self.assertEqual(json.loads(read.stdout)['data'][0]['learning'], 'Preserve the linked worktree history.')

    def cold_event_definition(self, multiple=False):
        fixture = Path(__file__).parent / 'fixtures/event-binding-definition.json'
        if not multiple:
            return fixture
        value = json.loads(fixture.read_text())
        value['storage']['slots']['second'] = dict(value['storage']['slots']['events'], path='example/second.jsonl')
        value['operations']['append-second'] = {'op': 'atomic-transaction', 'effects': [
            {'op': 'compare-and-append', 'slot': 'second', 'input': 'event', 'idempotency_param': 'request'}]}
        value['projections']['second-all'] = dict(value['projections']['all'], slot='second')
        definition = self.root / 'two-slots.json'
        definition.write_text(json.dumps(value))
        return definition

    def cold_event_append(self, definition, tree, request, value=1, operation='append', selector=None):
        args = selector or ['--repo', str(tree)]
        result = subprocess.run([os.environ['LEDGER_BIN'], 'transact', '--definition', str(definition),
            *args, '--operation', operation, '--param', f'request={request}',
            '--input', 'event=-', '--format', 'json'], input=json.dumps({'kind': 'one', 'value': value}).encode(),
            capture_output=True, env=dict(os.environ, LEDGER_CACHE_DIR=str(self.root / 'native-cache')))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def cold_family_snapshot(self):
        return {str(path.relative_to(self.root)): path.read_bytes()
                for tree in (self.repo, self.other) for path in (tree / '.ledger').rglob('*') if path.is_file()}

    def test_cold_adoption_rejects_equal_events_with_different_request_bindings(self):
        definition = self.cold_event_definition()
        self.cold_event_append(definition, self.repo, 'first')
        self.cold_event_append(definition, self.other, 'second')
        self.assertEqual((self.repo / '.ledger/example/events.jsonl').read_bytes(),
                         (self.other / '.ledger/example/events.jsonl').read_bytes())
        before = self.cold_family_snapshot()
        with self.assertRaisesRegex(context.ContextError, 'AdoptionSourceDoesNotCoverHistory'):
            self.cold_adopt(definition)
        self.assertEqual(self.cold_family_snapshot(), before)
        self.assertFalse(context.storage_home().exists())

    def test_cold_adoption_checks_binding_coverage_in_every_slot(self):
        definition = self.cold_event_definition(multiple=True)
        for tree, request in ((self.repo, 'first'), (self.other, 'second')):
            self.cold_event_append(definition, tree, 'shared')
            self.cold_event_append(definition, tree, request, operation='append-second')
        before = self.cold_family_snapshot()
        with self.assertRaisesRegex(context.ContextError, 'AdoptionSourceDoesNotCoverHistory'):
            self.cold_adopt(definition)
        self.assertEqual(self.cold_family_snapshot(), before)
        self.assertFalse(context.storage_home().exists())

    def assert_cold_rejects_damaged_sibling(self, orphan):
        definition = self.cold_event_definition()
        self.cold_event_append(definition, self.other, 'shared')
        shutil.copytree(self.other / '.ledger', self.repo / '.ledger')
        if orphan:
            (self.repo / '.ledger/example/events.jsonl').unlink()
        else:
            next((self.repo / '.ledger/.definitions').glob('*.json')).unlink()
        before = self.cold_family_snapshot()
        with self.assertRaises(context.ContextError):
            self.cold_adopt(definition)
        self.assertEqual(self.cold_family_snapshot(), before)
        self.assertFalse(context.storage_home().exists())

    def test_cold_adoption_rejects_sibling_orphan_binding(self):
        self.assert_cold_rejects_damaged_sibling(orphan=True)

    def test_cold_adoption_rejects_sibling_missing_historical_definition(self):
        self.assert_cold_rejects_damaged_sibling(orphan=False)

    def test_cold_adoption_rejects_pending_sibling_publication(self):
        definition = self.cold_event_definition()
        self.cold_event_append(definition, self.other, 'shared')
        shutil.copytree(self.other / '.ledger', self.repo / '.ledger')
        pending = self.repo / '.ledger/.transactions/dtx-unresolved'
        pending.mkdir()
        before = self.cold_family_snapshot()
        with self.assertRaisesRegex(context.ContextError, 'TransactionRecoveryRequired'):
            self.cold_adopt(definition)
        self.assertEqual(self.cold_family_snapshot(), before)
        self.assertFalse(context.storage_home().exists())

    def test_cold_adoption_preserves_multislot_prefix_and_idempotency(self):
        definition = self.cold_event_definition(multiple=True)
        self.cold_event_append(definition, self.other, 'shared')
        self.cold_event_append(definition, self.other, 'second-one', operation='append-second')
        shutil.copytree(self.other / '.ledger', self.repo / '.ledger')
        self.cold_event_append(definition, self.other, 'second-two', value=2, operation='append-second')
        before = self.cold_family_snapshot()
        selected = self.cold_adopt(definition)
        self.assertEqual(self.cold_family_snapshot(), before)
        result = subprocess.run([os.environ['LEDGER_BIN'], 'project', '--definition', str(definition),
            *selected['native_args'], '--projection', 'second-all', '--format', 'json'], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['data'], [{'kind': 'one', 'value': 1}, {'kind': 'one', 'value': 2}])
        target = Path(selected['store_root']) / '.ledger/example/second.jsonl'
        target_before = target.read_bytes()
        retried = self.cold_event_append(definition, self.other, 'second-two', value=2,
                                       operation='append-second', selector=selected['native_args'])
        self.assertEqual(retried['effects'][0]['result'], 'idempotent')
        self.assertIsNone(retried['transaction_id'])
        self.assertEqual(target.read_bytes(), target_before)
        self.assertEqual(context.resolve(self.repo)['store_id'], selected['store_id'])
        self.assertEqual(context.resolve(self.other)['store_id'], selected['store_id'])

    def test_cold_adoption_preserves_history_beyond_preparation_dependency_count(self):
        value = json.loads(self.cold_event_definition().read_text())
        value['requires']['operators'].append('compare-and-replace')
        value['parameters']['revision'] = {'type': 'digest', 'required': False}
        value['inputs']['event']['required'] = False
        value['inputs']['snapshot'] = {'codec': 'jsonl', 'required': False, 'max_bytes': 4096}
        value['operations']['replace'] = {'effects': [{'op': 'compare-and-replace', 'slot': 'events',
            'input': 'snapshot', 'expected_revision_param': 'revision'}]}
        definition = self.root / 'many-revisions.json'
        definition.write_text(json.dumps(value))
        seeded = self.cold_event_append(definition, self.other, 'seed')
        replaced = subprocess.run([os.environ['LEDGER_BIN'], 'transact', '--definition', str(definition),
            '--repo', str(self.other), '--operation', 'replace', '--param',
            'revision=' + seeded['effects'][0]['revision_after'], '--input', 'snapshot=-', '--format', 'json'],
            input=b'{"kind":"one","value":2}\n', capture_output=True)
        self.assertEqual(replaced.returncode, 0, replaced.stdout + replaced.stderr)
        control = self.other / '.ledger'
        event = control / 'example/events.jsonl'
        binding = next((control / '.bindings').glob('*.jsonl'))
        rows = [json.loads(line) for line in binding.read_text().splitlines()]
        previous = event.read_bytes()
        for number in range(3, 1027):
            current = json.dumps({'kind': 'one', 'value': number}, separators=(',', ':')).encode() + b'\n'
            before = hashlib.sha256(previous).hexdigest()
            after = 'sha256:' + hashlib.sha256(current).hexdigest()
            (control / '.revisions' / (before + '.bin')).write_bytes(previous)
            rows.append(dict(rows[-1], revision_before='sha256:' + before, revision_after=after,
                             input_digest=after, canonical_input_digest=after, extent_end=len(current)))
            previous = current
        event.write_bytes(previous)
        binding.write_text(''.join(json.dumps(row, separators=(',', ':')) + '\n' for row in rows))
        self.assertGreater(len(list((control / '.revisions').glob('*.bin'))), 1023)
        healthy = subprocess.run([os.environ['LEDGER_BIN'], 'doctor', '--definition', str(definition),
            '--repo', str(self.other), '--format', 'json'], capture_output=True)
        self.assertEqual(healthy.returncode, 0, healthy.stdout + healthy.stderr)
        self.assertTrue(json.loads(healthy.stdout)['healthy'])
        before = self.cold_family_snapshot()
        selected = self.cold_adopt(definition)
        self.assertEqual(self.cold_family_snapshot(), before)
        target = Path(selected['store_root']) / '.ledger'
        self.assertEqual((target / 'example/events.jsonl').read_bytes(), previous)
        self.assertEqual((target / '.bindings' / binding.name).read_bytes(), binding.read_bytes())
        self.assertEqual({path.name: path.read_bytes() for path in (target / '.revisions').glob('*.bin')},
                         {path.name: path.read_bytes() for path in (control / '.revisions').glob('*.bin')})
        result = subprocess.run([os.environ['LEDGER_BIN'], 'project', '--definition', str(definition),
            *selected['native_args'], '--projection', 'all', '--format', 'json'], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['data'], [{'kind': 'one', 'value': 1026}])

    def test_cold_adoption_requires_legacy_lease_recovery(self):
        definition = self.cold_fixture()
        (self.other / '.ledger/learnings/events.jsonl.cas.lock').write_text('legacy lease')
        with self.assertRaises(context.ContextError):
            self.cold_adopt(definition)
        self.assertFalse((context.storage_home() / context.CATALOG).exists())

    def test_cold_adoption_requires_explicit_quiescence(self):
        definition = self.cold_fixture()
        with self.assertRaises(context.ContextError):
            self.cold_adopt(definition, confirm=False)
        self.assertFalse(self.home.exists())

    def test_cold_adoption_rejects_corruption_without_publishing(self):
        definition = self.cold_fixture()
        event = self.other / '.ledger/learnings/events.jsonl'
        event.write_bytes(b'{invalid}\n')
        with self.assertRaises(context.ContextError):
            self.cold_adopt(definition)
        self.assertFalse((context.storage_home() / context.CATALOG).exists())
        self.assertEqual(event.read_bytes(), b'{invalid}\n')

    def test_cold_adoption_rejects_divergent_and_partial_sibling(self):
        definition = self.cold_fixture()
        source = self.other / '.ledger/learnings/events.jsonl'
        target = self.repo / '.ledger/learnings/events.jsonl'
        target.parent.mkdir(parents=True)
        for value in (b'{"different":true}\n', source.read_bytes()[:20]):
            target.write_bytes(value)
            with self.assertRaises(context.ContextError):
                self.cold_adopt(definition)
            self.assertFalse((context.storage_home() / context.CATALOG).exists())

    def test_cold_adoption_does_not_relabel_unknown_legacy_data(self):
        definition = self.cold_fixture()
        (self.other / '.ledger/unknown.jsonl').write_text('uncovered\n')
        with self.assertRaises(context.ContextError):
            self.cold_adopt(definition)
        self.assertFalse((context.storage_home() / context.CATALOG).exists())

if __name__ == '__main__':
    unittest.main()
