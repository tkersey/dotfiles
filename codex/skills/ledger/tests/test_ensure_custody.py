"""Migration orchestration tests. Native responses/context are explicit test doubles.

The optional integration case instead uses the published context helper and the
real release binary. It must pass before qualifying a custody migration release.
"""
from contextlib import contextmanager
import importlib.util
import json
import os
from pathlib import Path
import subprocess
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

    def sync_directory(self, path):
        pass

    def write_json(self, path, value):
        self.no_symlinks(path)
        path.write_text(json.dumps(value))

    def checked_registration(self, root, common, *, mutated=False):
        reg = json.loads((common / self.REGISTRATION).read_text())
        custody = Path(reg['store_root']); self.no_symlinks(custody)
        marker = json.loads((custody / self.MARKER).read_text())
        if marker['store_id'] != reg['store_id'] or not (custody / '.ledger').is_dir():
            raise RuntimeError('invalid custody')
        return {'workspace_root': str(root), 'store_root': str(custody), 'store_id': reg['store_id'],
                'repository_id': 'ledger-repository:' + reg['store_id'],
                'native_args': ['--store-root', str(custody), '--store-id', reg['store_id']],
                'storage_mutated': mutated, 'authority_granted': False}


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
        return module.ensure(self.ctx.repo, skill_root=self.skills, **kwargs)

    def test_inspection_is_read_only(self):
        self.event(self.ctx.repo)
        result = self.ensure()
        self.assertEqual(result['status'], 'planned')
        self.assertFalse(self.ctx.storage_home().exists())
        self.assertFalse((self.ctx.common / self.ctx.REGISTRATION).exists())
        self.assertFalse(any(call[0] == 'transact' for call in self.calls))

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

    def test_owner_paths_cannot_escape_or_alias_slots(self):
        for name in ('../outside', '/outside', './path', 'a//b', 'a\\b'):
            with self.assertRaises(module.MigrationError):
                module.relative(name)


@unittest.skipUnless(os.environ.get('LEDGER_BIN'), 'Set LEDGER_BIN for real native/context conformance')
class NativeIntegration(unittest.TestCase):
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
                result = module.ensure(repo, apply=True, confirm_no_writers=True, binary=os.environ['LEDGER_BIN'], skill_root=skills)
                self.assertEqual(result['imports'][0]['appended'], 1)
                self.assertTrue(Path(result['imports'][0]['sources'][0]['source']).is_file())
                again = module.ensure(other, binary=os.environ['LEDGER_BIN'], skill_root=skills)
                self.assertEqual(again['context']['store_id'], result['context']['store_id'])
                self.assertFalse(again['storage_mutated'])
                self.assertEqual(source.read_bytes(), original)


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
                result = module.ensure(repo, apply=True, confirm_no_writers=True, binary=binary, skill_root=skills)
                self.assertEqual(result['imports'][0]['appended'], 1)
                custody = Path(result['context']['store_root'])
                archive = custody / 'legacy-archive' / result['fingerprint']
                self.assertEqual(len(list(archive.glob('worktree-*/.ledger/unselected/document'))), 1)
                self.assertFalse((custody / '.ledger/unselected').exists())
                self.assertEqual(event_path.read_bytes(), original_events)
                self.assertEqual(source.read_bytes(), original_source)
                # A registration alone must not skip historical reconciliation.
                (custody / 'migration-receipt.json').unlink()
                recovered = module.ensure(other, apply=True, confirm_no_writers=True, binary=binary, skill_root=skills)
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
