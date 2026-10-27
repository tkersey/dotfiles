"""Migration orchestration tests. Native responses/context are explicit test doubles.

The optional integration case instead uses the published context helper and the
real release binary. It must pass before qualifying a custody migration release.
"""
from contextlib import contextmanager
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/ensure_custody.py'
spec = importlib.util.spec_from_file_location('ensure_custody', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ContextFixture:
    REGISTRATION = 'ledger-store.json'
    REGISTRATION_SCHEMA = 'ledger-repository-registration/v1'
    MARKER = '.ledger-root.json'
    MARKER_SCHEMA = 'ledger-storage-root/v1'

    class ContextError(RuntimeError):
        pass

    class UnregisteredContext(ContextError):
        pass

    def __init__(self, root):
        self.root = root
        self.repo = root / 'repo'; self.repo.mkdir()
        self.common = self.repo / '.git'; self.common.mkdir()
        self.other = root / 'other'; self.other.mkdir()
        self.trees = [self.repo, self.other]

    def workspace(self, repo):
        return repo, self.common

    def worktrees(self, repo):
        if any(not tree.is_dir() for tree in self.trees):
            raise RuntimeError('unavailable worktree')
        return self.trees

    def no_symlinks(self, path):
        if any(part.is_symlink() for part in (path, *path.parents)):
            raise RuntimeError('symlink')

    def storage_home(self):
        return self.root / 'home'

    @contextmanager
    def registration_lock(self, common):
        yield

    @contextmanager
    def catalog_lock(self, home):
        yield

    def _register_root_locked(self, custody, store_id, repo, home):
        return self.register_root(custody, store_id, repo)

    def sync_directory(self, path):
        pass

    def write_json(self, path, value):
        self.no_symlinks(path)
        path.write_text(json.dumps(value))

    def checked_registration(self, root, common, *, mutated=False):
        reg = json.loads((common / self.REGISTRATION).read_text())
        return self.checked(root, reg, mutated=mutated)

    def checked(self, root, reg, *, mutated=False):
        custody = Path(reg['store_root']); self.no_symlinks(custody)
        marker = json.loads((custody / self.MARKER).read_text())
        if marker['store_id'] != reg['store_id'] or not (custody / '.ledger').is_dir():
            raise RuntimeError('invalid custody')
        return {'workspace_root': str(root), 'store_root': str(custody), 'store_id': reg['store_id'],
                'repository_id': 'ledger-repository:' + reg['store_id'],
                'native_args': ['--store-root', str(custody), '--store-id', reg['store_id']],
                'storage_mutated': mutated, 'authority_granted': False}

    def resolve(self, repo=None, *, store_id=None):
        catalog = self.storage_home() / 'catalog.json'
        if not catalog.exists():
            raise self.UnregisteredContext('No cataloged store')
        reg = json.loads(catalog.read_text())
        if store_id is not None and reg['store_id'] != store_id:
            raise RuntimeError('Wrong store')
        return self.checked(repo or self.repo, reg)

    def register_root(self, custody, store_id, repo=None):
        catalog = self.storage_home() / 'catalog.json'
        reg = {'store_id': store_id, 'store_root': str(custody)}
        result = self.checked(repo or self.repo, reg)
        changed = not catalog.exists() or json.loads(catalog.read_text()) != reg
        self.storage_home().mkdir(parents=True, exist_ok=True)
        if changed:
            self.write_json(catalog, reg)
        return {**result, 'storage_mutated': changed}


class EnsureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.ctx = ContextFixture(self.root)
        self.skills = self.root / 'skills'; self.owner = self.skills / 'fixture'; self.owner.mkdir(parents=True)
        self.definition = self.owner / 'definition.json'
        self.definition.write_text(json.dumps({'owner': 'fixture', 'storage': {'slots': {'events': {
            'path': 'fixture/events.jsonl', 'kind': 'event-log', 'codec': 'jsonl'}}}}))
        (self.owner / 'migration.json').write_text(json.dumps({'schema': 'ledger-owner-migration/v1',
            'definition': 'definition.json', 'retired_sources': [], 'importer': None}))
        self.calls = []; self.problem = None; self.pending = 0; self.post_copy = None
        self.loader = module.load_module
        patcher = patch.object(module, 'load_module', side_effect=lambda path:
            self.ctx if path.name == 'ledger_context.py' else self.loader(path))
        patcher.start(); self.addCleanup(patcher.stop)
        patcher = patch.object(module, 'native', side_effect=self.native)
        patcher.start(); self.addCleanup(patcher.stop)

    def native(self, binary, owner, selector, command, *args, **kwargs):
        self.calls.append((command, args, selector))
        if command == 'definition':
            return {'schema': 'ledger-definition-description/v1', 'definition': {'id': 'fixture', 'digest': 'fixed'}, 'authority_granted': False}
        if command == 'transact':
            self.problem = None
            return {'schema': 'ledger-transaction-result/v1', 'valid': True, 'semantic_authority_granted': False}
        if self.post_copy and '--store-root' in selector:
            self.post_copy(); self.post_copy = None
        return {'schema': 'ledger-doctor-result/v1', 'healthy': self.problem is None,
                'pending_transactions': self.pending, 'storage_mutated': False,
                'slots': [{'name': 'events', 'healthy': self.problem is None, 'error_code': self.problem}],
                'authority_granted': False}

    def event(self, tree, contents='{"id":"a"}\n'):
        path = tree / '.ledger/fixture/events.jsonl'; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)
        return path

    def ensure(self, **kwargs):
        return module.migrate(self.ctx.repo, skill_root=self.skills, **kwargs)

    def test_inspection_is_read_only(self):
        self.event(self.ctx.repo)
        result = self.ensure()
        self.assertEqual(result['status'], 'planned')
        self.assertFalse(self.ctx.storage_home().exists())
        self.assertFalse((self.ctx.common / self.ctx.REGISTRATION).exists())
        self.assertFalse(any(call[0] == 'transact' for call in self.calls))

    def test_unowned_fifo_is_archived_as_metadata_without_opening_or_recreating(self):
        source = self.event(self.ctx.repo)
        pipe = self.ctx.repo / '.ledger/cas/watchdog.log'
        pipe.parent.mkdir()
        os.mkfifo(pipe, 0o600)
        original = source.read_bytes()
        result = self.ensure(apply=True, confirm_no_writers=True)
        custody = Path(result['context']['store_root'])
        self.assertEqual((custody / '.ledger/fixture/events.jsonl').read_bytes(), original)
        self.assertEqual(source.read_bytes(), original)
        self.assertTrue(stat.S_ISFIFO(pipe.lstat().st_mode))
        manifest_path = next((custody / 'legacy-archive').glob('*/manifest.json'))
        manifest = json.loads(manifest_path.read_text())
        source_tree = next(tree for tree in manifest['sources'].values()
                           if tree['workspace'] == str(self.ctx.repo))
        self.assertEqual(source_tree['entries']['.ledger/cas/watchdog.log'],
                         {'kind': 'fifo', 'mode': 0o600})
        self.assertFalse(any((manifest_path.parent / name / '.ledger/cas/watchdog.log').exists()
                             for name in ('worktree-0', 'worktree-1')))
        self.assertFalse((custody / '.ledger/cas/watchdog.log').exists())

    def test_fifo_cannot_replace_owner_events_or_native_custody(self):
        for relative in ('fixture/events.jsonl', '.bindings/fixture.json', 'fixture', '.bindings'):
            with self.subTest(relative=relative):
                pipe = self.ctx.repo / '.ledger' / relative
                pipe.parent.mkdir(parents=True, exist_ok=True)
                os.mkfifo(pipe, 0o600)
                try:
                    with self.assertRaisesRegex(module.MigrationError, 'Unsupported special source entry'):
                        self.ensure()
                    self.assertFalse(self.ctx.storage_home().exists())
                finally:
                    pipe.unlink()
                    shutil.rmtree(self.ctx.repo / '.ledger')

    def test_apply_needs_real_writer_assertion(self):
        self.event(self.ctx.repo)
        with self.assertRaisesRegex(module.MigrationError, 'confirm-no-writers'):
            self.ensure(apply=True)
        self.assertFalse(self.ctx.storage_home().exists())

    def test_single_source_adoption_preserves_bytes_and_registers(self):
        source = self.event(self.ctx.repo)
        result = self.ensure(apply=True, confirm_no_writers=True)
        target = Path(result['context']['store_root']) / '.ledger/fixture/events.jsonl'
        self.assertEqual(target.read_bytes(), source.read_bytes())
        self.assertEqual(result['status'], 'verified')
        self.assertTrue(source.exists())

    def test_prefix_chain_chooses_complete_extension(self):
        self.event(self.ctx.repo)
        full = self.event(self.ctx.other, '{"id":"a"}\n{"id":"b"}\n')
        result = self.ensure(apply=True, confirm_no_writers=True)
        self.assertEqual((Path(result['context']['store_root']) / '.ledger/fixture/events.jsonl').read_bytes(), full.read_bytes())

    def test_equal_unterminated_copies_are_not_divergence(self):
        self.event(self.ctx.repo, '{"id":"a"}')
        self.event(self.ctx.other, '{"id":"a"}')
        self.assertEqual(self.ensure()['status'], 'planned')

    def test_partial_record_prefix_is_rejected(self):
        self.event(self.ctx.repo, '{"id":')
        self.event(self.ctx.other)
        with self.assertRaisesRegex(module.MigrationError, 'Divergent'):
            self.ensure(apply=True, confirm_no_writers=True)

    def test_divergence_never_initializes_empty(self):
        self.event(self.ctx.repo)
        self.event(self.ctx.other, '{"id":"b"}\n')
        with self.assertRaisesRegex(module.MigrationError, 'Divergent'):
            self.ensure(apply=True, confirm_no_writers=True)
        self.assertFalse((self.ctx.common / self.ctx.REGISTRATION).exists())

    def test_unavailable_worktree_is_not_pruned(self):
        self.ctx.other.rmdir()
        with self.assertRaisesRegex(RuntimeError, 'unavailable'):
            self.ensure(apply=True, confirm_no_writers=True)
        self.assertEqual(len(self.ctx.trees), 2)

    def test_unselected_files_and_link_spelling_are_preserved(self):
        self.event(self.ctx.repo)
        directory = self.ctx.repo / '.ledger/other'; directory.mkdir()
        (directory / 'document').write_text('historical document')
        (directory / 'link').symlink_to(self.root / 'absent-external-target')
        result = self.ensure(apply=True, confirm_no_writers=True)
        custody = Path(result['context']['store_root'])
        archive = custody / 'legacy-archive' / result['fingerprint']
        manifest = json.loads((archive / 'manifest.json').read_text())
        entry = next(t for t in manifest['sources'].values() if t['workspace'] == str(self.ctx.repo))
        self.assertEqual(entry['entries']['.ledger/other/link']['kind'], 'symlink')
        self.assertEqual(len(list(archive.glob('worktree-*/.ledger/other/document'))), 1)
        self.assertEqual(list(archive.glob('worktree-*/.ledger/other/link')), [])
        self.assertFalse((custody / '.ledger/other').exists())

    def test_selected_symlink_is_rejected(self):
        source = self.event(self.ctx.repo); source.unlink(); source.symlink_to(self.root / 'outside')
        with self.assertRaisesRegex(RuntimeError, 'symlink'):
            self.ensure(apply=True, confirm_no_writers=True)

    def test_pending_transactions_and_leases_block(self):
        self.event(self.ctx.repo); self.pending = 1
        with self.assertRaisesRegex(module.MigrationError, 'transaction'):
            self.ensure(apply=True, confirm_no_writers=True)
        self.pending = 0
        (self.ctx.repo / '.ledger/fixture/events.jsonl.cas.lock').write_text('legacy lease')
        with self.assertRaisesRegex(module.MigrationError, 'lease'):
            self.ensure(apply=True, confirm_no_writers=True)

    def test_unbound_store_uses_native_bind_not_metadata_fabrication(self):
        self.event(self.ctx.repo); self.problem = 'InvalidStoreBinding'
        self.ensure(apply=True, confirm_no_writers=True)
        self.assertTrue(any(call[0] == 'transact' and call[1] == ('--operation', 'bind-existing') for call in self.calls))

    def test_known_stale_binding_uses_native_rebind(self):
        self.event(self.ctx.repo); self.problem = 'StoreBindingRecordCountMismatch'
        self.ensure(apply=True, confirm_no_writers=True)
        self.assertTrue(any(call[0] == 'transact' and call[1] == ('--operation', 'rebind-existing') for call in self.calls))

    def test_unknown_binding_failure_is_not_repaired(self):
        self.event(self.ctx.repo); self.problem = 'StoreBindingDefinitionMismatch'
        with self.assertRaisesRegex(module.MigrationError, 'Unknown custody'):
            self.ensure(apply=True, confirm_no_writers=True)
        self.assertFalse(any(call[0] == 'transact' for call in self.calls))
        self.assertFalse((self.ctx.common / self.ctx.REGISTRATION).exists())

    def test_changed_source_before_publication_blocks_registration(self):
        source = self.event(self.ctx.repo)
        self.post_copy = lambda: source.write_text('{"id":"changed"}\n')
        with self.assertRaisesRegex(module.MigrationError, 'changed'):
            self.ensure(apply=True, confirm_no_writers=True)
        self.assertFalse((self.ctx.common / self.ctx.REGISTRATION).exists())

    def test_verified_rerun_has_no_storage_mutation(self):
        self.event(self.ctx.repo)
        first = self.ensure(apply=True, confirm_no_writers=True)
        second = self.ensure()
        self.assertEqual(first['context']['store_id'], second['context']['store_id'])
        self.assertEqual(second['status'], 'verified')
        self.assertFalse(second['storage_mutated'])

    def test_registration_without_receipt_does_not_claim_completion(self):
        self.event(self.ctx.repo)
        first = self.ensure(apply=True, confirm_no_writers=True)
        (Path(first['context']['store_root']) / 'migration-receipt.json').unlink()
        self.assertEqual(self.ensure()['status'], 'planned')
        result = self.ensure(apply=True, confirm_no_writers=True)
        self.assertEqual(result['context']['store_id'], first['context']['store_id'])

    def test_missing_registered_root_is_not_recreated(self):
        self.event(self.ctx.repo)
        first = self.ensure(apply=True, confirm_no_writers=True)
        (Path(first['context']['store_root']) / '.ledger-root.json').unlink()
        with self.assertRaises(FileNotFoundError):
            self.ensure(apply=True, confirm_no_writers=True)

    def test_changed_destination_invalidates_completion_receipt(self):
        self.event(self.ctx.repo)
        first = self.ensure(apply=True, confirm_no_writers=True)
        (Path(first['context']['store_root']) / '.ledger/fixture/events.jsonl').write_text('{"id":"replacement"}\n')
        self.assertEqual(self.ensure()['status'], 'planned')
        with self.assertRaisesRegex(module.MigrationError, 'Additional/divergent'):
            self.ensure(apply=True, confirm_no_writers=True)

    def test_valid_extension_preserves_imported_source_snapshot(self):
        self.event(self.ctx.repo)
        first = self.ensure(apply=True, confirm_no_writers=True)
        event = Path(first['context']['store_root']) / '.ledger/fixture/events.jsonl'
        with event.open('a') as handle:
            handle.write('{"id":"later"}\n')
        second = self.ensure()
        self.assertEqual(second['status'], 'verified')
        self.assertEqual(second['sources'], first['sources'])
        self.assertEqual(second['destination_prefixes'], first['destination_prefixes'])
        self.assertFalse(second['storage_mutated'])

    def test_normal_ensure_needs_neither_worktree_coverage_nor_migration_receipt(self):
        self.event(self.ctx.repo)
        first = self.ensure(apply=True, confirm_no_writers=True)
        (Path(first['context']['store_root']) / 'migration-receipt.json').unlink()
        self.ctx.other.rmdir()
        calls = len(self.calls)
        result = module.ensure(self.ctx.repo)
        self.assertEqual(result['store_id'], first['context']['store_id'])
        self.assertEqual(len(self.calls), calls)
        self.assertFalse(result['storage_mutated'])

    def test_owner_paths_cannot_escape_or_alias_slots(self):
        for name in ('../outside', '/outside', './path', 'a//b', 'a\\b'):
            with self.assertRaises(module.MigrationError):
                module.relative(name)


class LegacySourceSelection(unittest.TestCase):
    def test_invalid_sources_never_fall_back_to_single_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            missing = root / 'missing'
            broken = root / 'broken'; broken.mkdir()
            (broken / '.git').write_text('gitdir: /unavailable-legacy-worktree\n')
            nested = broken / 'nested'; nested.mkdir()
            bare = root / 'bare.git'
            subprocess.run(['git', 'init', '--bare', '-q', str(bare)], check=True, capture_output=True)
            damaged_bare = root / 'damaged-bare.git'
            subprocess.run(['git', 'init', '--bare', '-q', str(damaged_bare)], check=True, capture_output=True)
            (damaged_bare / 'HEAD').write_text('damaged HEAD\n')
            missing_bare_head = root / 'missing-head.git'
            subprocess.run(['git', 'init', '--bare', '-q', str(missing_bare_head)], check=True, capture_output=True)
            (missing_bare_head / 'HEAD').unlink()
            managed = root / 'managed'; managed.mkdir()
            (managed / '.ledger-root.json').write_text('{}')
            link = root / 'linked-source'; link.symlink_to(managed, target_is_directory=True)
            git_parent = root / 'git-parent'; git_parent.mkdir()
            subprocess.run(['git', '-C', str(git_parent), 'init', '-q'], check=True, capture_output=True)
            nested_managed = git_parent / 'old-managed'; (nested_managed / '.ledger').mkdir(parents=True)
            marker = {'schema': 'ledger-storage-root/v1', 'store_id': 'a' * 32}
            (nested_managed / '.ledger-root.json').write_text(json.dumps(marker))
            managed_worktree = root / 'managed-worktree'; managed_worktree.mkdir()
            subprocess.run(['git', '-C', str(managed_worktree), 'init', '-q'], check=True, capture_output=True)
            (managed_worktree / '.ledger-root.json').write_text(json.dumps(marker))
            (managed_worktree / '.ledger').mkdir()
            child = managed_worktree / 'child'; child.mkdir()
            with patch.dict(os.environ, {'LEDGER_HOME': str(root / 'home')}), \
                    patch.object(module, 'native', side_effect=AssertionError('Invalid source reached native')) as engine:
                for source in (missing, broken, nested, bare, damaged_bare, missing_bare_head,
                               managed, link, nested_managed, child):
                    with self.subTest(source=source), self.assertRaises(RuntimeError):
                        module.migrate(source, apply=True, confirm_no_writers=True, binary='must-not-run-ledger')
                    self.assertFalse((root / 'home').exists())
                engine.assert_not_called()


@unittest.skipUnless(os.environ.get('LEDGER_BIN'), 'Set LEDGER_BIN for real native/context conformance')
class NativeIntegration(unittest.TestCase):
    def test_attachment_before_migration_lock_rejects_before_destination_effects(self):
        ctx = module.load_module(SCRIPT.with_name('ledger_context.py'))
        loader = module.load_module
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); source = root / 'source'; source.mkdir()
            with patch.dict(os.environ, {'LEDGER_HOME': str(root / 'home'), 'LEDGER_CACHE_DIR': str(root / 'cache')}):
                competing = ctx.resolve(initialize=True)
                lock = ctx.registration_lock

                @contextmanager
                def attach_before_lock(lock_root):
                    ctx.register_root(Path(competing['store_root']), competing['store_id'], source)
                    with lock(lock_root):
                        yield

                with patch.object(module, 'load_module', side_effect=lambda path:
                        ctx if path.name == 'ledger_context.py' else loader(path)), \
                        patch.object(ctx, 'registration_lock', side_effect=attach_before_lock):
                    with self.assertRaisesRegex(module.MigrationError, 'Migration inputs changed'):
                        module.migrate(source, apply=True, confirm_no_writers=True,
                                       binary=os.environ['LEDGER_BIN'], skill_root=SCRIPT.parents[2])
                self.assertEqual(ctx.resolve(source)['store_id'], competing['store_id'])
                self.assertEqual(list((root / 'home/repos').iterdir()), [Path(competing['store_root'])])
                self.assertFalse((Path(competing['store_root']) / 'legacy-archive').exists())

    def test_catalog_attachment_is_serialized_through_migration_publication(self):
        ctx = module.load_module(SCRIPT.with_name('ledger_context.py'))
        skills = SCRIPT.parents[2]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); source = root / 'source'; source.mkdir()
            environment = {'LEDGER_HOME': str(root / 'home'), 'LEDGER_CACHE_DIR': str(root / 'cache')}
            with patch.dict(os.environ, environment):
                competing = ctx.resolve(initialize=True)
                ready = root / 'attacher-ready'
                worker = None
                copy = module.copy_inventory

                def copy_while_attacher_waits(snapshot, destination):
                    nonlocal worker
                    code = ('import importlib.util, pathlib, sys; '
                            's=importlib.util.spec_from_file_location("ctx",sys.argv[1]); '
                            'm=importlib.util.module_from_spec(s); s.loader.exec_module(m); '
                            'pathlib.Path(sys.argv[5]).write_text("ready"); '
                            'm.register_root(pathlib.Path(sys.argv[2]),sys.argv[3],pathlib.Path(sys.argv[4]))')
                    worker = subprocess.Popen([sys.executable, '-c', code, str(SCRIPT.with_name('ledger_context.py')),
                        competing['store_root'], competing['store_id'], str(source), str(ready)],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    self.addCleanup(lambda: worker.kill() if worker.poll() is None else None)
                    # A real register_root must wait, rather than publish a
                    # competing alias while migration mutates its destination.
                    with self.assertRaises(subprocess.TimeoutExpired):
                        worker.communicate(timeout=0.5)
                    self.assertTrue(ready.exists())
                    copy(snapshot, destination)

                with patch.object(module, 'copy_inventory', side_effect=copy_while_attacher_waits):
                    migrated = module.migrate(source, apply=True, confirm_no_writers=True,
                                              binary=os.environ['LEDGER_BIN'], skill_root=skills)
                output, error = worker.communicate(timeout=10)
                self.assertNotEqual(worker.returncode, 0, output + error)
                self.assertIn(b'already associated', error)
                self.assertEqual(ctx.resolve(source)['store_id'], migrated['store_id'])
                self.assertEqual(ctx.resolve(store_id=competing['store_id'])['store_root'], competing['store_root'])
                self.assertEqual(len(list((root / 'home/repos').iterdir())), 2)

    def test_surviving_directory_preserves_old_native_history_and_retired_import(self):
        skills = SCRIPT.parents[2]
        binary = os.environ['LEDGER_BIN']
        definition = skills / 'learnings/definitions/ledger/learnings-protocol.json'
        previous = skills / 'learnings/tests/fixtures/pre-personal-history/learnings-protocol.json'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); source = root / 'surviving source'; source.mkdir()
            subprocess.run(['git', '-C', str(source), 'init', '-q'], check=True, capture_output=True)
            environment = {'LEDGER_HOME': str(root / 'home'), 'LEDGER_CACHE_DIR': str(root / 'cache')}
            def native(selector, command, *arguments, packet=None, selected_definition=definition):
                result = subprocess.run([binary, command, '--definition', str(selected_definition),
                    *selector, *arguments, '--format', 'json'], capture_output=True,
                    input=None if packet is None else json.dumps(packet).encode())
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                return json.loads(result.stdout)
            def snapshot(directory):
                return {path.relative_to(directory).as_posix(): path.read_bytes()
                        for path in directory.rglob('*') if path.is_file()}
            with patch.dict(os.environ, environment):
                old_selector = ['--repo', str(source)]
                record = {'status': 'codify_now', 'learning': 'Retain a surviving native claim.',
                    'evidence': ['original fixture'], 'application': 'Keep identity after Git is deleted.',
                    'source': 'old session', 'context': {'repo': str(source), 'branch': 'main', 'paths': []}}
                native(old_selector, 'transact', '--operation', 'capture', '--input', 'submission=-',
                       packet={'record': record}, selected_definition=previous)
                original = native(old_selector, 'project', '--projection', 'import-records',
                                  selected_definition=previous)['data'][0]
                old_note = native(old_selector, 'project', '--projection', 'memory-note', '--param',
                                  'id=' + original['id'], selected_definition=previous)['data']
                historical = {'id': 'retired-surviving-claim', 'captured_at': '2026-01-01T00:00:00Z',
                    'fingerprint': 'retained-retired-fingerprint', 'status': 'codify_now',
                    'learning': 'Preserve the separate retired record.', 'evidence': ['fixture'],
                    'application': 'Import without inventing a replacement ID.', 'source': 'retired session'}
                (source / '.learnings.jsonl').write_text(json.dumps(historical) + '\n')
                shutil.rmtree(source / '.git')
                before = snapshot(source)
                planned = module.migrate(source, binary=binary, skill_root=skills)
                self.assertEqual(planned['status'], 'planned')
                self.assertEqual([item['workspace'] for item in planned['sources'].values()], [str(source)])
                self.assertFalse((root / 'home').exists())
                self.assertEqual(snapshot(source), before)

                migrated = module.migrate(source, apply=True, confirm_no_writers=True,
                                          binary=binary, skill_root=skills)
                selected = migrated['context']
                custody = Path(selected['store_root'])
                self.assertIsNone(selected['git_common_dir'])
                self.assertEqual(snapshot(source), before)
                self.assertEqual(snapshot(custody / 'legacy-archive' / migrated['fingerprint'] / 'worktree-0'), before)
                self.assertEqual(native(selected['native_args'], 'project', '--projection', 'import-records')['data'],
                                 [original, historical])
                self.assertEqual(native(selected['native_args'], 'project', '--projection', 'memory-note',
                                        '--param', 'id=' + original['id'])['data'], old_note)
                for name, contents in before.items():
                    if name.startswith('.ledger/.definitions/') and not name.endswith('.cas.lock.advisory'):
                        self.assertEqual((custody / name).read_bytes(), contents)
                self.assertTrue((custody / '.ledger/learnings/events.jsonl').read_bytes().startswith(
                    before['.ledger/learnings/events.jsonl']))
                self.assertTrue((root / 'home/ledger-store.lock').is_file())
                again = module.migrate(source, apply=True, confirm_no_writers=True,
                                       binary=binary, skill_root=skills)
                self.assertEqual(again['context']['store_id'], selected['store_id'])
                self.assertFalse(again['storage_mutated'])
                record['learning'] = 'Append after the surviving-directory cutover.'
                record['context']['repo'] = selected['repository_id']
                native(selected['native_args'], 'transact', '--operation', 'capture', '--input', 'submission=-',
                       packet={'record': record})
                self.assertEqual(module.migrate(source, binary=binary, skill_root=skills)['status'], 'verified')
                shutil.rmtree(source)
                direct = module.ensure(store_id=selected['store_id'])
                self.assertEqual(len(native(direct['native_args'], 'project', '--projection', 'import-records')['data']), 3)

    def test_surviving_directory_gaining_git_before_publication_is_rejected(self):
        skills = SCRIPT.parents[2]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); source = root / 'surviving'; source.mkdir()
            historical = {'id': 'retired-before-git-change', 'captured_at': '2026-01-01T00:00:00Z',
                'fingerprint': 'retired-fingerprint', 'status': 'codify_now', 'learning': 'Preserve old history.',
                'evidence': ['fixture'], 'application': 'Do not change migration coverage during publication.',
                'source': 'fixture'}
            (source / '.learnings.jsonl').write_text(json.dumps(historical) + '\n')
            real_sync = module.sync_tree
            changed = False
            def sync_and_change(path, ctx):
                nonlocal changed
                real_sync(path, ctx)
                if (path / 'migration-receipt.json').exists() and not changed:
                    subprocess.run(['git', '-C', str(source), 'init', '-q'], check=True, capture_output=True)
                    changed = True
            with patch.dict(os.environ, {'LEDGER_HOME': str(root / 'home'), 'LEDGER_CACHE_DIR': str(root / 'cache')}), \
                    patch.object(module, 'sync_tree', side_effect=sync_and_change):
                with self.assertRaisesRegex(module.MigrationError, 'association changed'):
                    module.migrate(source, apply=True, confirm_no_writers=True,
                                   binary=os.environ['LEDGER_BIN'], skill_root=skills)
                self.assertTrue(changed)
                self.assertFalse((root / 'home/catalog.json').exists())
                self.assertEqual(json.loads((source / '.learnings.jsonl').read_bytes()), historical)

    def test_conflicting_legacy_registration_blocks_before_destination_mutation(self):
        skills = SCRIPT.parents[2]
        binary = os.environ['LEDGER_BIN']
        definition = skills / 'learnings/definitions/ledger/learnings-protocol.json'
        ctx = module.load_module(SCRIPT.with_name('ledger_context.py'))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); repo = root / 'repo'; repo.mkdir()
            subprocess.run(['git', '-C', str(repo), 'init', '-q'], check=True, capture_output=True)
            subprocess.run(['git', '-C', str(repo), '-c', 'user.name=Fixture', '-c',
                            'user.email=fixture@example.invalid', 'commit', '--allow-empty', '-qm', 'fixture'],
                           check=True, capture_output=True)
            with patch.dict(os.environ, {'LEDGER_HOME': str(root / 'home'), 'LEDGER_CACHE_DIR': str(root / 'cache')}):
                selected = ctx.resolve(initialize=True)
                custody = Path(selected['store_root'])
                submission = {'record': {'status': 'codify_now', 'learning': 'Existing selected-store claim.',
                    'evidence': ['fixture'], 'application': 'Preserve this unrelated history.', 'source': 'fixture',
                    'context': {'repo': selected['repository_id'], 'branch': 'not-applicable', 'paths': []}}}
                capture = subprocess.run([binary, 'transact', '--definition', str(definition), *selected['native_args'],
                    '--operation', 'capture', '--input', 'submission=-', '--format', 'json'],
                    input=json.dumps(submission).encode(), capture_output=True)
                self.assertEqual(capture.returncode, 0, capture.stdout.decode() + capture.stderr.decode())
                legacy = root / 'old registered custody'; (legacy / '.ledger').mkdir(parents=True)
                legacy_id = 'a' * 32
                ctx.write_json(legacy / ctx.MARKER, {'schema': ctx.MARKER_SCHEMA, 'store_id': legacy_id})
                registration = repo / '.git' / ctx.REGISTRATION
                ctx.write_json(registration, {'schema': ctx.REGISTRATION_SCHEMA, 'store_id': legacy_id,
                                              'store_root': str(legacy)})
                historical = {'id': 'legacy-source-claim', 'captured_at': '2026-01-01T00:00:00Z',
                    'fingerprint': 'legacy-source-fingerprint', 'status': 'codify_now', 'learning': 'Legacy claim.',
                    'evidence': ['fixture'], 'application': 'Retain the original store.', 'source': 'fixture'}
                source = repo / '.learnings.jsonl'; source.write_text(json.dumps(historical) + '\n')
                def snapshot():
                    return {path.relative_to(custody).as_posix(): path.read_bytes()
                            for path in custody.rglob('*') if path.is_file()}
                before = snapshot()
                catalog = (ctx.storage_home() / ctx.CATALOG).read_bytes()
                original_registration = registration.read_bytes()
                original_source = source.read_bytes()
                with self.assertRaisesRegex(module.MigrationError, 'different legacy registration'):
                    module.migrate(repo, store_id=selected['store_id'], apply=True, confirm_no_writers=True,
                                   binary=binary, skill_root=skills)
                self.assertEqual(snapshot(), before)
                self.assertFalse((custody / 'legacy-archive').exists())
                self.assertEqual((ctx.storage_home() / ctx.CATALOG).read_bytes(), catalog)
                self.assertEqual(registration.read_bytes(), original_registration)
                self.assertEqual(source.read_bytes(), original_source)

    def test_retired_only_repository_and_linked_worktree(self):
        skills = SCRIPT.parents[2]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); repo = root / 'repo'; repo.mkdir()
            def git(*args):
                return subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True)
            git('init', '-q'); git('config', 'user.name', 'Fixture'); git('config', 'user.email', 'fixture@example.invalid')
            git('commit', '--allow-empty', '-qm', 'fixture')
            other = root / 'linked'; git('worktree', 'add', '--detach', str(other))
            source = repo / '.learnings.jsonl'
            row = {'id': 'original-descriptive-id', 'captured_at': '2026-01-01T00:00:00Z',
                   'fingerprint': 'original-fingerprint', 'status': 'codify_now', 'learning': 'Preserve history.',
                   'evidence': ['witnessed'], 'application': 'Retain original identity.', 'source': 'original session'}
            source.write_text(json.dumps(row) + '\n'); original = source.read_bytes()
            with patch.dict(os.environ, {'LEDGER_HOME': str(root / 'home')}):
                result = module.migrate(repo, apply=True, confirm_no_writers=True, binary=os.environ['LEDGER_BIN'], skill_root=skills)
                self.assertEqual(result['imports'][0]['appended'], 1)
                self.assertTrue(Path(result['imports'][0]['sources'][0]['source']).is_file())
                again = module.ensure(other)
                self.assertEqual(again['store_id'], result['context']['store_id'])
                self.assertFalse(again['storage_mutated'])
                self.assertEqual(source.read_bytes(), original)
                definition = skills / 'learnings/definitions/ledger/learnings-protocol.json'
                submission = {'record': {'status': 'codify_now', 'learning': 'Later native capture.',
                    'evidence': ['observed'], 'application': 'Keep imported evidence.', 'source': 'fixture',
                    'context': {'repo': again['repository_id'], 'branch': 'main', 'paths': []}}}
                capture = subprocess.run([os.environ['LEDGER_BIN'], 'transact', '--definition', str(definition),
                    *again['native_args'], '--operation', 'capture', '--input', 'submission=-', '--format', 'json'],
                    input=json.dumps(submission).encode(), capture_output=True)
                self.assertEqual(capture.returncode, 0, capture.stdout.decode() + capture.stderr.decode())
                verified = module.migrate(repo, binary=os.environ['LEDGER_BIN'], skill_root=skills)
                self.assertEqual(verified['status'], 'verified')
                self.assertEqual(verified['destination_prefixes'], result['destination_prefixes'])
                self.assertFalse(verified['storage_mutated'])
                shutil.rmtree(other)
                self.assertEqual(module.ensure(repo)['store_id'], again['store_id'])
                shutil.rmtree(repo)
                direct = module.ensure(store_id=again['store_id'])
                projection = subprocess.run([os.environ['LEDGER_BIN'], 'project', '--definition', str(definition),
                    *direct['native_args'], '--projection', 'import-records', '--format', 'json'], capture_output=True)
                self.assertEqual(projection.returncode, 0, projection.stdout.decode() + projection.stderr.decode())
                self.assertEqual(len(json.loads(projection.stdout)['data']), 2)


    def test_bound_prefix_adoption_rebind_archive_and_registered_recovery(self):
        import shutil
        skills = SCRIPT.parents[2]
        binary = os.environ['LEDGER_BIN']
        definition = skills / 'learnings/definitions/ledger/learnings-protocol.json'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); repo = root / 'repo'; repo.mkdir()
            def git(*args):
                return subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True)
            git('init', '-q'); git('config', 'user.name', 'Fixture'); git('config', 'user.email', 'fixture@example.invalid')
            git('commit', '--allow-empty', '-qm', 'fixture')
            other = root / 'linked'; git('worktree', 'add', '--detach', str(other))
            submission = {'record': {'status': 'codify_now', 'learning': 'First original.', 'evidence': ['observed'],
                'application': 'Keep history.', 'source': 'fixture', 'context': {'repo': str(repo), 'branch': 'main', 'paths': []}}}
            def capture():
                result = subprocess.run([binary, 'transact', '--definition', str(definition), '--repo', str(repo),
                    '--operation', 'capture', '--input', 'submission=-', '--format', 'json'],
                    input=json.dumps(submission).encode(), capture_output=True)
                self.assertEqual(result.returncode, 0, result.stdout.decode())
            capture()
            shutil.copytree(repo / '.ledger', other / '.ledger')
            submission['record']['learning'] = 'Second original.'; capture()
            event_path = repo / '.ledger/learnings/events.jsonl'; original_events = event_path.read_bytes()
            # Deliberately stale metadata in an isolated fixture, never a live store.
            shutil.rmtree(repo / '.ledger/.bindings')
            shutil.copytree(other / '.ledger/.bindings', repo / '.ledger/.bindings')
            (repo / '.ledger/unselected').mkdir()
            (repo / '.ledger/unselected/document').write_text('retain this document')
            (repo / '.ledger/unselected/external').symlink_to(root / 'not-followed')
            historical = {'id': 'old-descriptive-id', 'captured_at': '2026-01-01T00:00:00Z',
                'fingerprint': 'old-fingerprint', 'status': 'codify_now', 'learning': 'Historical original.',
                'evidence': ['observed'], 'application': 'Preserve fields.', 'source': 'retired fixture'}
            source = repo / '.learnings.jsonl'; source.write_text(json.dumps(historical) + '\n')
            original_source = source.read_bytes()
            with patch.dict(os.environ, {'LEDGER_HOME': str(root / 'home')}):
                result = module.migrate(repo, apply=True, confirm_no_writers=True, binary=binary, skill_root=skills)
                self.assertEqual(result['imports'][0]['appended'], 1)
                custody = Path(result['context']['store_root'])
                archive = custody / 'legacy-archive' / result['fingerprint']
                self.assertEqual(len(list(archive.glob('worktree-*/.ledger/unselected/document'))), 1)
                self.assertFalse((custody / '.ledger/unselected').exists())
                self.assertEqual(event_path.read_bytes(), original_events)
                self.assertEqual(source.read_bytes(), original_source)
                # A registration alone must not skip historical reconciliation.
                (custody / 'migration-receipt.json').unlink()
                recovered = module.migrate(other, apply=True, confirm_no_writers=True, binary=binary, skill_root=skills)
                self.assertEqual(recovered['context']['store_id'], result['context']['store_id'])
                self.assertEqual(recovered['imports'][0]['appended'], 0)
                projection = subprocess.run([binary, 'project', '--definition', str(definition),
                    *result['context']['native_args'], '--projection', 'import-records', '--format', 'json'], capture_output=True)
                self.assertEqual(projection.returncode, 0, projection.stdout.decode())
                rows = json.loads(projection.stdout)['data']
                self.assertEqual(len(rows), 3)
                self.assertEqual(next(row for row in rows if row['id'] == historical['id']), historical)


if __name__ == '__main__':
    unittest.main()
