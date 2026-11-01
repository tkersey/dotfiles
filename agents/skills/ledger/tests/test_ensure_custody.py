import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

import native_host as module

SKILLS = Path(__file__).resolve().parents[2]
DEFINITION = SKILLS / 'learnings/definitions/ledger/learnings-protocol.json'
PREVIOUS = SKILLS / 'learnings/tests/fixtures/pre-personal-history/learnings-protocol.json'
SLOT = Path('.ledger/learnings/events.jsonl')


@unittest.skipUnless(os.environ.get('LEDGER_BIN'), 'Native Ledger is required')
class NativeMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.binary = os.environ['LEDGER_BIN']
        environment = patch.dict(os.environ, {'LEDGER_HOME': str(self.root / 'home'),
                                              'LEDGER_CACHE_DIR': str(self.root / 'cache')})
        environment.start()
        self.addCleanup(environment.stop)
        self.git('init', '-q')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 'commit', '--allow-empty', '-qm', 'fixture')

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.repo), *args], capture_output=True,
                              check=True, timeout=15)

    def linked(self):
        other = self.root / 'linked'
        self.git('worktree', 'add', '--detach', str(other))
        return other

    def native(self, selector, command, *args, packet=None, definition=DEFINITION):
        result = subprocess.run([self.binary, command, '--definition', str(definition),
            *selector, *args, '--format', 'json'], capture_output=True, timeout=20,
            input=None if packet is None else json.dumps(packet).encode())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def capture(self, tree=None, learning='Preserve the original claim.', selector=None, definition=DEFINITION):
        record = {'status': 'codify_now', 'learning': learning, 'evidence': ['original evidence'],
                  'application': 'Preserve identity and every field.', 'source': 'original session',
                  'context': {'repo': str(tree or self.repo), 'branch': 'main', 'paths': ['src/a.zig']}}
        self.native(selector or ['--repo', str(tree or self.repo)], 'transact',
                    '--operation', 'capture', '--input', 'submission=-', packet={'record': record},
                    definition=definition)
        return (tree or self.repo) / SLOT

    def migrate(self, **kwargs):
        return module.migrate(self.repo, **kwargs)

    def apply(self, **kwargs):
        return self.migrate(apply=True, confirm_no_writers=True, **kwargs)

    def snapshot(self, root):
        return {str(path.relative_to(root)): path.read_bytes() for path in root.rglob('*')
                if path.is_file() and not path.is_symlink() and '.git' not in path.relative_to(root).parts}

    def retired(self, tree=None):
        record = {'id': 'retired-independent-id', 'captured_at': '2026-01-01T00:00:00Z',
                  'fingerprint': 'retired-independent-fingerprint', 'status': 'codify_now',
                  'learning': 'Retain the separate retired record.', 'evidence': ['retired evidence'],
                  'application': 'Preserve original identity.', 'source': 'retired session'}
        (tree or self.repo).joinpath('.learnings.jsonl').write_text(json.dumps(record) + '\n')
        return record

    def stage(self):
        with self.assertRaises(module.MigrationError) as raised:
            self.apply()
        result = raised.exception.value
        self.assertEqual(result['status'], 'owner-import-required', result)
        self.assertFalse((self.root / 'home/catalog.json').exists())
        return result

    def import_owner(self, staged):
        selected = staged['context']
        owner = staged['owner_imports'][0]
        argv = ['uv', 'run', '--no-project', owner['importer'], '--definition', owner['definition'],
                '--ledger-bin', self.binary, '--store-root', selected['store_root'],
                '--store-id', selected['store_id'], '--apply', '--initialize-empty', '--confirm-no-writers']
        for source in owner['sources']:
            argv += ['--source', source['source']]
        imported = subprocess.run(argv, capture_output=True, timeout=30)
        self.assertEqual(imported.returncode, 0, imported.stdout + imported.stderr)
        receipt = self.root / 'owner-receipt.json'
        receipt.write_bytes(imported.stdout)
        return receipt

    def test_inspection_is_read_only(self):
        self.capture()
        before = self.snapshot(self.repo)
        result = self.migrate()
        self.assertEqual(result['status'], 'planned')
        self.assertFalse(result['storage_mutated'])
        self.assertFalse((self.root / 'home').exists())
        self.assertEqual(self.snapshot(self.repo), before)

    def test_apply_requires_writer_assertion(self):
        self.capture()
        with self.assertRaisesRegex(module.MigrationError, 'MigrationRequiresWriterQuiescence'):
            self.migrate(apply=True)
        self.assertFalse((self.root / 'home').exists())

    def test_single_source_preserves_bytes_and_full_records(self):
        source = self.capture()
        original = source.read_bytes()
        records = self.native(['--repo', str(self.repo)], 'project', '--projection', 'import-records')['data']
        result = self.apply()
        self.assertEqual(result['status'], 'verified')
        self.assertEqual((Path(result['context']['store_root']) / SLOT).read_bytes(), original)
        self.assertEqual(source.read_bytes(), original)
        self.assertEqual(self.native(result['context']['native_args'], 'project', '--projection', 'import-records')['data'], records)

    def test_prefix_chain_chooses_complete_extension(self):
        self.capture()
        other = self.linked()
        shutil.copytree(self.repo / '.ledger', other / '.ledger')
        full = self.capture(self.repo, 'Second independent original.')
        result = self.apply()
        self.assertEqual((Path(result['context']['store_root']) / SLOT).read_bytes(), full.read_bytes())

    def test_equal_unterminated_copies_are_not_divergence(self):
        source = self.capture()
        source.write_bytes(source.read_bytes().rstrip(b'\n'))
        other = self.linked()
        shutil.copytree(self.repo / '.ledger', other / '.ledger')
        self.assertEqual(self.migrate()['status'], 'planned')

    def test_partial_record_prefix_is_rejected(self):
        source = self.capture()
        other = self.linked()
        shutil.copytree(self.repo / '.ledger', other / '.ledger')
        source.write_bytes(source.read_bytes()[:30])
        before = [self.snapshot(tree) for tree in (self.repo, other)]
        with self.assertRaisesRegex(module.MigrationError,
                                   'Divergent|ExistingStoreValidationFailed'):
            self.apply()
        self.assertEqual([self.snapshot(tree) for tree in (self.repo, other)], before)
        self.assertFalse((self.root / 'home').exists())

    def test_divergence_never_initializes_empty(self):
        self.capture()
        self.capture(self.linked(), 'Different independent record.')
        with self.assertRaisesRegex(module.MigrationError, 'Divergent'):
            self.apply()
        self.assertFalse((self.root / 'home').exists())

    def test_unavailable_worktree_is_not_pruned(self):
        other = self.linked()
        shutil.rmtree(other)
        before = self.git('worktree', 'list', '--porcelain').stdout
        with self.assertRaises(module.MigrationError):
            self.apply()
        self.assertEqual(self.git('worktree', 'list', '--porcelain').stdout, before)
        self.assertFalse((self.root / 'home').exists())

    def test_unowned_fifo_and_link_are_metadata_only(self):
        self.capture()
        directory = self.repo / '.ledger/unselected'
        directory.mkdir()
        (directory / 'document').write_text('historical document')
        (directory / 'link').symlink_to(self.root / 'absent-external-target')
        os.mkfifo(directory / 'pipe', 0o600)
        result = self.apply()
        custody = Path(result['context']['store_root'])
        archive = custody / 'legacy-archive' / result['fingerprint']
        entries = json.loads((archive / 'manifest.json').read_text())['sources']['0']['entries']
        self.assertEqual(entries['.ledger/unselected/pipe'], {'kind': 'fifo', 'mode': 0o600})
        self.assertEqual(entries['.ledger/unselected/link']['target'], str(self.root / 'absent-external-target'))
        self.assertEqual((archive / 'worktree-0/.ledger/unselected/document').read_text(), 'historical document')
        self.assertFalse((archive / 'worktree-0/.ledger/unselected/pipe').exists())
        self.assertFalse((archive / 'worktree-0/.ledger/unselected/link').is_symlink())
        self.assertFalse((custody / '.ledger/unselected').exists())
        self.assertTrue(stat.S_ISFIFO((directory / 'pipe').lstat().st_mode))

    def test_selected_fifo_and_symlink_are_rejected(self):
        for relative in ('learnings/events.jsonl', '.bindings/fixture.json', 'learnings', '.bindings'):
            for kind in ('fifo', 'symlink'):
                with self.subTest(relative=relative, kind=kind):
                    shutil.rmtree(self.repo / '.ledger', ignore_errors=True)
                    shutil.rmtree(self.root / 'home', ignore_errors=True)
                    path = self.repo / '.ledger' / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    if kind == 'fifo':
                        os.mkfifo(path, 0o600)
                    else:
                        path.symlink_to(self.root / 'outside')
                    with self.assertRaises(module.MigrationError):
                        self.apply()
                    self.assertFalse((self.root / 'home').exists())
                    shutil.rmtree(self.repo / '.ledger')

    def test_pending_transactions_and_leases_block(self):
        self.capture()
        pending = self.repo / '.ledger/.transactions/dtx-broken'
        pending.mkdir(parents=True)
        (pending / 'transaction.json').write_text('{}')
        with self.assertRaises(module.MigrationError):
            self.apply()
        self.assertFalse((self.root / 'home').exists())
        shutil.rmtree(pending.parent)
        self.repo.joinpath(str(SLOT) + '.cas.lock').write_text('legacy lease')
        with self.assertRaisesRegex(module.MigrationError, 'LegacyLeaseRequiresRecovery'):
            self.apply()
        self.assertFalse((self.root / 'home').exists())

    def test_unbound_history_uses_native_binding(self):
        source = self.capture()
        original = source.read_bytes()
        shutil.rmtree(self.repo / '.ledger/.bindings')
        result = self.apply()
        self.assertEqual((Path(result['context']['store_root']) / SLOT).read_bytes(), original)
        self.assertTrue(self.native(result['context']['native_args'], 'doctor')['healthy'])

    def binding_owner(self):
        owner = self.root / 'binding-owner'
        owner.mkdir()
        self.binding_definition = owner / 'events.json'
        shutil.copyfile(Path(__file__).parent / 'fixtures/event-binding-definition.json',
                        self.binding_definition)
        self.binding_manifest = owner / 'migration.json'
        self.binding_manifest.write_text(json.dumps({
            'schema': 'ledger-owner-migration/v1', 'definition': 'events.json',
            'retired_sources': [], 'importer': None}))
        self.binding_slot = Path('.ledger/example/events.jsonl')

    def append_request(self, selector, request):
        return self.native(selector, 'transact', '--operation', 'append', '--input', 'event=-',
                           '--param', 'request=' + request, packet={'kind': 'one', 'value': 1},
                           definition=self.binding_definition)

    def migrate_bindings(self, apply=True):
        args = module.command(self.repo) + ['--migrate', '--owner-manifest',
                                            str(self.binding_manifest)]
        if apply:
            args += ['--apply', '--confirm-no-writers']
        return module.invoke(args)

    def test_migration_rejects_equal_payload_with_divergent_requests(self):
        self.binding_owner()
        other = self.linked()
        for tree, request in [(self.repo, 'first'), (other, 'second')]:
            self.append_request(['--repo', str(tree)], request)
        self.assertEqual((self.repo / self.binding_slot).read_bytes(),
                         (other / self.binding_slot).read_bytes())
        before = [self.snapshot(tree) for tree in (self.repo, other)]
        for apply in (False, True):
            with self.subTest(apply=apply), self.assertRaises(module.MigrationError):
                self.migrate_bindings(apply)
        self.assertEqual([self.snapshot(tree) for tree in (self.repo, other)], before)
        self.assertFalse((self.root / 'home').exists())

    def test_migration_equal_native_histories_preserve_request_idempotency(self):
        self.binding_owner()
        self.append_request(['--repo', str(self.repo)], 'first')
        other = self.linked()
        shutil.copytree(self.repo / '.ledger', other / '.ledger')
        result = self.migrate_bindings()
        self.assertEqual(result['status'], 'verified')
        target = Path(result['context']['store_root'])
        before = (target / self.binding_slot).read_bytes()
        self.append_request(result['context']['native_args'], 'first')
        self.assertEqual((target / self.binding_slot).read_bytes(), before)
        self.assertEqual(self.native(result['context']['native_args'], 'project',
            '--projection', 'all', definition=self.binding_definition)['data'],
            [{'kind': 'one', 'value': 1}])

    def test_registered_migration_rejects_equal_payload_with_other_binding(self):
        self.binding_owner()
        target = module.resolve(self.repo, initialize=True)
        self.append_request(target['native_args'], 'second')
        self.append_request(['--repo', str(self.repo)], 'first')
        before = self.snapshot(Path(target['store_root']))
        with self.assertRaises(module.MigrationError):
            self.migrate_bindings()
        self.assertEqual(self.snapshot(Path(target['store_root'])), before)
        self.assertEqual(module.resolve(self.repo)['store_id'], target['store_id'])

    def replace_migrated_binding(self):
        self.binding_owner()
        self.append_request(['--repo', str(self.repo)], 'first')
        result = self.migrate_bindings()
        target = Path(result['context']['store_root'])
        other = self.root / 'independent'
        other.mkdir()
        self.append_request(['--repo', str(other)], 'second')
        shutil.rmtree(target / '.ledger')
        shutil.copytree(other / '.ledger', target / '.ledger')
        shutil.rmtree(target / '.ledger/.transactions')
        self.assertEqual((target / self.binding_slot).read_bytes(),
                         (self.repo / self.binding_slot).read_bytes())
        self.assertTrue(self.native(result['context']['native_args'], 'doctor',
                                   definition=self.binding_definition)['healthy'])
        return target

    def test_registered_repair_cannot_discard_healthy_source_admissions(self):
        self.binding_owner()
        context = module.resolve(self.repo, initialize=True)
        target = Path(context['store_root'])
        self.append_request(context['native_args'], 'first')
        binding = next((target / '.ledger/.bindings').glob('*.jsonl'))
        first_binding = binding.read_bytes()
        self.append_request(context['native_args'], 'second')
        binding.write_bytes(first_binding)
        for request in ('first', 'second'):
            self.append_request(['--repo', str(self.repo)], request)
        self.assertEqual((target / self.binding_slot).read_bytes(),
                         (self.repo / self.binding_slot).read_bytes())
        before = self.snapshot(target)
        with self.assertRaises(module.MigrationError):
            self.migrate_bindings()
        self.assertEqual(self.snapshot(target), before)

    def test_verified_receipt_rejects_healthy_replacement_binding(self):
        target = self.replace_migrated_binding()
        before = self.snapshot(target)
        for apply in (False, True):
            with self.subTest(apply=apply), self.assertRaises(module.MigrationError):
                self.migrate_bindings(apply)
        self.assertEqual(self.snapshot(target), before)

    def test_pending_migration_rejects_healthy_replacement_binding(self):
        target = self.replace_migrated_binding()
        (self.root / 'home/catalog.json').unlink()
        (target / 'migration-receipt.json').unlink()
        before = self.snapshot(target / '.ledger')
        with self.assertRaises(module.MigrationError):
            self.migrate_bindings()
        self.assertEqual(self.snapshot(target / '.ledger'), before)
        self.assertFalse((self.root / 'home/catalog.json').exists())

    def test_stale_binding_uses_native_rebinding(self):
        self.capture()
        saved = self.root / 'bindings'
        shutil.copytree(self.repo / '.ledger/.bindings', saved)
        source = self.capture(learning='Second retained record.')
        original = source.read_bytes()
        shutil.rmtree(self.repo / '.ledger/.bindings')
        shutil.copytree(saved, self.repo / '.ledger/.bindings')
        result = self.apply()
        self.assertEqual((Path(result['context']['store_root']) / SLOT).read_bytes(), original)
        self.assertTrue(self.native(result['context']['native_args'], 'doctor')['healthy'])

    def test_unknown_binding_failure_is_not_repaired(self):
        self.capture()
        binding = next((self.repo / '.ledger/.bindings').glob('*.jsonl'))
        record = json.loads(binding.read_bytes())
        record['definition_id'] = 'foreign/protocol'
        binding.write_text(json.dumps(record) + '\n')
        original = binding.read_bytes()
        before = self.snapshot(self.repo)
        with self.assertRaisesRegex(module.MigrationError,
                'UnknownBindingFailure|StoreBindingDefinitionMismatch') as raised:
            self.apply()
        context = raised.exception.value.get('context')
        if context is not None:
            target = Path(context['store_root']) / binding.relative_to(self.repo)
            self.assertEqual(target.read_bytes(), original)
        else:
            self.assertFalse((self.root / 'home').exists())
        self.assertEqual(binding.read_bytes(), original)
        self.assertEqual(self.snapshot(self.repo), before)
        self.assertFalse((self.root / 'home/catalog.json').exists())

    def test_verified_rerun_has_no_storage_mutation(self):
        self.capture()
        first = self.apply()
        before = self.snapshot(Path(first['context']['store_root']))
        for result in (self.migrate(), self.apply()):
            self.assertEqual(result['status'], 'verified')
            self.assertEqual(result['context']['store_id'], first['context']['store_id'])
            self.assertFalse(result['storage_mutated'])
        self.assertEqual(self.snapshot(Path(first['context']['store_root'])), before)

    def test_verified_receipt_requires_its_preserved_archive(self):
        self.capture()
        first = self.apply()
        store = Path(first['context']['store_root'])
        archive = store / 'legacy-archive' / first['fingerprint']
        backup = self.root / 'archive-backup'
        shutil.copytree(archive, backup)
        for damage in ('missing', 'manifest', 'payload'):
            with self.subTest(damage=damage):
                if damage == 'missing':
                    shutil.rmtree(archive)
                elif damage == 'manifest':
                    (archive / 'manifest.json').write_text('{}')
                else:
                    next(archive.glob('worktree-*/.ledger/learnings/events.jsonl')).write_text('{}\n')
                before = self.snapshot(store)
                for apply in (False, True):
                    with self.subTest(apply=apply), self.assertRaises(module.MigrationError):
                        self.migrate(apply=apply, confirm_no_writers=apply)
                    self.assertEqual(self.snapshot(store), before)
                if archive.exists():
                    shutil.rmtree(archive)
                shutil.copytree(backup, archive)
        self.assertEqual(self.apply()['status'], 'verified')

    def test_first_pending_transaction_blocks_without_a_canonical_slot(self):
        pending = self.repo / '.ledger/.transactions/dtx-first'
        pending.mkdir(parents=True)
        # Native admission counts the created transaction directory as pending
        # even before its initial journal and canonical slot are published.
        self.assertFalse((self.repo / SLOT).exists())
        before = self.snapshot(self.repo)
        for apply in (False, True):
            with self.subTest(apply=apply), self.assertRaisesRegex(
                    module.MigrationError, 'UnresolvedLegacyTransactionCoverage'):
                self.migrate(apply=apply, confirm_no_writers=apply)
            self.assertEqual(self.snapshot(self.repo), before)
            self.assertTrue(pending.is_dir())
            self.assertFalse((self.root / 'home').exists())

    def test_declared_retired_directory_is_not_verified_as_empty_history(self):
        retired = self.repo / '.learnings.jsonl'
        retired.mkdir()
        (retired / 'records.jsonl').write_text('{"retired":"must not disappear"}\n')
        before = self.snapshot(self.repo)
        for apply in (False, True):
            with self.subTest(apply=apply), self.assertRaisesRegex(
                    module.MigrationError, 'UnsupportedRetiredSource'):
                self.migrate(apply=apply, confirm_no_writers=apply)
            self.assertEqual(self.snapshot(self.repo), before)
            self.assertFalse((self.root / 'home').exists())

    def test_registration_without_receipt_requires_reconciliation(self):
        self.capture()
        first = self.apply()
        (Path(first['context']['store_root']) / 'migration-receipt.json').unlink()
        self.assertEqual(self.migrate()['status'], 'planned')
        self.assertEqual(self.apply()['context']['store_id'], first['context']['store_id'])

    def test_missing_registered_root_is_not_recreated(self):
        self.capture()
        first = self.apply()
        marker = Path(first['context']['store_root']) / '.ledger-root.json'
        marker.unlink()
        with self.assertRaises(module.MigrationError):
            self.apply()
        self.assertFalse(marker.exists())

    def test_changed_destination_invalidates_receipt(self):
        self.capture()
        first = self.apply()
        target = Path(first['context']['store_root'])
        (target / SLOT).write_text('{}\n')
        before = self.snapshot(target)
        self.assertEqual(self.migrate()['status'], 'planned')
        with self.assertRaisesRegex(module.MigrationError,
                                   'AdditionalOrDivergentHistory|ExistingStoreValidationFailed'):
            self.apply()
        self.assertEqual(self.snapshot(target), before)
        self.assertEqual(module.resolve(self.repo)['store_id'], first['context']['store_id'])

    def test_valid_extension_preserves_source_snapshot(self):
        self.capture()
        first = self.apply()
        self.capture(learning='Later native claim.', selector=first['context']['native_args'])
        second = self.migrate()
        self.assertEqual(second['status'], 'verified')
        self.assertEqual(second['sources'], first['sources'])
        self.assertEqual(second['destination_prefixes'], first['destination_prefixes'])
        self.assertFalse(second['storage_mutated'])

    def test_normal_ensure_needs_neither_worktree_coverage_nor_receipt(self):
        self.capture()
        other = self.linked()
        first = self.apply()
        (Path(first['context']['store_root']) / 'migration-receipt.json').unlink()
        shutil.rmtree(other)
        selected = module.ensure(self.repo)
        self.assertEqual(selected['store_id'], first['context']['store_id'])
        self.assertFalse(selected['storage_mutated'])

    def test_owner_paths_cannot_escape_or_alias_slots(self):
        owner = self.root / 'skills/learnings'
        shutil.copytree(SKILLS / 'learnings', owner)
        definition = owner / 'definitions/ledger/learnings-protocol.json'
        original = json.loads(definition.read_text())
        for name in ('../outside', '/outside', './path', 'a//b', 'a\\b'):
            changed = copy.deepcopy(original)
            next(iter(changed['storage']['slots'].values()))['path'] = name
            definition.write_text(json.dumps(changed))
            with self.subTest(name=name), self.assertRaises(module.MigrationError):
                self.migrate(skill_root=owner.parent)
            self.assertFalse((self.root / 'home').exists())

    def test_invalid_sources_never_fall_back_to_single_directory(self):
        broken = self.root / 'broken'
        broken.mkdir()
        (broken / '.git').write_text('gitdir: /unavailable-legacy-worktree\n')
        nested = broken / 'nested'
        nested.mkdir()
        bare = self.root / 'bare.git'
        subprocess.run(['git', 'init', '--bare', '-q', str(bare)], check=True, capture_output=True)
        damaged_bare = self.root / 'damaged-bare.git'
        shutil.copytree(bare, damaged_bare)
        (damaged_bare / 'HEAD').write_text('damaged HEAD\n')
        missing_head = self.root / 'missing-head.git'
        shutil.copytree(bare, missing_head)
        (missing_head / 'HEAD').unlink()
        nested_managed = self.repo / 'nested-managed'
        nested_managed.mkdir()
        (nested_managed / '.ledger-root.json').write_text('{}')
        managed_worktree = self.root / 'managed-worktree'
        subprocess.run(['git', 'init', '-q', str(managed_worktree)], check=True, capture_output=True)
        (managed_worktree / '.ledger-root.json').write_text('{}')
        child = managed_worktree / 'child'
        child.mkdir()
        managed = self.root / 'managed'
        managed.mkdir()
        (managed / '.ledger-root.json').write_text('{}')
        link = self.root / 'linked-source'
        link.symlink_to(managed, target_is_directory=True)
        for source in (self.root / 'missing', broken, nested, bare, damaged_bare, missing_head,
                       managed, link, nested_managed, child):
            with self.subTest(source=source), self.assertRaises(module.MigrationError):
                module.migrate(source, apply=True, confirm_no_writers=True)
            self.assertFalse((self.root / 'home').exists())

    def test_retired_import_requires_external_owner_and_scoped_receipt(self):
        record = self.retired()
        original = self.snapshot(self.repo)
        staged = self.stage()
        repeated = self.stage()
        self.assertEqual(repeated['context']['store_id'], staged['context']['store_id'])
        receipt_path = self.import_owner(staged)
        original_receipt = json.loads(receipt_path.read_bytes())
        for field, value in (('store_id', 'b' * 32), ('full_record_parity_verified', False),
                             ('revision', 'wrong-revision'), ('sources', []), ('authority_granted', True)):
            receipt = copy.deepcopy(original_receipt)
            receipt[field] = value
            receipt_path.write_text(json.dumps(receipt))
            with self.subTest(field=field), self.assertRaises(module.MigrationError):
                self.apply(import_receipts=[receipt_path])
            self.assertFalse((self.root / 'home/catalog.json').exists())
        receipt_path.write_text(json.dumps(original_receipt))
        result = self.apply(import_receipts=[receipt_path])
        self.assertEqual(result['status'], 'verified')
        self.assertEqual(self.native(result['context']['native_args'], 'project', '--projection', 'import-records')['data'], [record])
        self.assertEqual(self.snapshot(self.repo), original)

    def test_surviving_directory_preserves_old_native_and_retired_full_records(self):
        self.capture(definition=PREVIOUS)
        original_record = self.native(['--repo', str(self.repo)], 'project', '--projection', 'import-records', definition=PREVIOUS)['data'][0]
        old_note = self.native(['--repo', str(self.repo)], 'project', '--projection', 'memory-note',
                               '--param', 'id=' + original_record['id'], definition=PREVIOUS)['data']
        retired = self.retired()
        shutil.rmtree(self.repo / '.git')
        before = self.snapshot(self.repo)
        self.assertEqual(self.migrate()['status'], 'planned')
        staged = self.stage()
        receipt = self.import_owner(staged)
        result = self.apply(import_receipts=[receipt])
        selected = result['context']
        self.assertIsNone(selected['git_common_dir'])
        self.assertEqual(self.snapshot(self.repo), before)
        archive = Path(selected['store_root']) / 'legacy-archive' / result['fingerprint'] / 'worktree-0'
        self.assertEqual(self.snapshot(archive), before)
        self.assertEqual(self.native(selected['native_args'], 'project', '--projection', 'import-records')['data'], [original_record, retired])
        self.assertEqual(self.native(selected['native_args'], 'project', '--projection', 'memory-note', '--param', 'id=' + original_record['id'])['data'], old_note)
        for name, raw in before.items():
            if name.startswith('.ledger/.definitions/') and not name.endswith('.cas.lock.advisory'):
                self.assertEqual((Path(selected['store_root']) / name).read_bytes(), raw)
        self.assertTrue((Path(selected['store_root']) / SLOT).read_bytes().startswith(before[str(SLOT)]))
        self.assertFalse(self.apply()['storage_mutated'])
        shutil.rmtree(self.repo)
        self.assertEqual(module.ensure(store_id=selected['store_id'])['store_root'], selected['store_root'])

    def test_retired_only_linked_worktree_and_direct_recovery(self):
        other = self.linked()
        retired = self.retired()
        staged = self.stage()
        result = self.apply(import_receipts=[self.import_owner(staged)])
        selected = module.ensure(other)
        self.assertEqual(selected['store_id'], result['context']['store_id'])
        self.capture(learning='Post-migration native record.', selector=selected['native_args'])
        self.assertEqual(self.migrate()['status'], 'verified')
        shutil.rmtree(other)
        shutil.rmtree(self.repo)
        direct = module.ensure(store_id=selected['store_id'])
        records = self.native(direct['native_args'], 'project', '--projection', 'import-records')['data']
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0], retired)

    def test_registered_import_recovery_preserves_full_records(self):
        self.capture()
        retired = self.retired()
        staged = self.stage()
        result = self.apply(import_receipts=[self.import_owner(staged)])
        custody = Path(result['context']['store_root'])
        (custody / 'migration-receipt.json').unlink()
        with self.assertRaises(module.MigrationError) as raised:
            self.apply()
        required = raised.exception.value
        self.assertEqual(required['status'], 'owner-import-required')
        receipt = self.import_owner(required)
        self.assertEqual(json.loads(receipt.read_bytes())['appended'], 0)
        recovered = self.apply(import_receipts=[receipt])
        self.assertEqual(recovered['context']['store_id'], result['context']['store_id'])
        rows = self.native(recovered['context']['native_args'], 'project', '--projection', 'import-records')['data']
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[-1], retired)

    def test_bound_prefix_rebind_archive_and_registered_recovery_together(self):
        self.capture()
        other = self.linked()
        shutil.copytree(self.repo / '.ledger', other / '.ledger')
        source = self.capture(learning='Second original before cutover.')
        original = source.read_bytes()
        records = self.native(['--repo', str(self.repo)], 'project', '--projection', 'import-records')['data']
        shutil.rmtree(self.repo / '.ledger/.bindings')
        shutil.copytree(other / '.ledger/.bindings', self.repo / '.ledger/.bindings')
        unselected = self.repo / '.ledger/unselected'
        unselected.mkdir()
        (unselected / 'document').write_text('retain this document')
        (unselected / 'external').symlink_to(self.root / 'not-followed')
        retired = self.retired()
        staged = self.stage()
        result = self.apply(import_receipts=[self.import_owner(staged)])
        custody = Path(result['context']['store_root'])
        archive = custody / 'legacy-archive' / result['fingerprint']
        self.assertEqual(len(list(archive.glob('worktree-*/.ledger/unselected/document'))), 1)
        self.assertFalse((custody / '.ledger/unselected').exists())
        self.assertEqual(source.read_bytes(), original)
        self.assertTrue((custody / SLOT).read_bytes().startswith(original))
        (custody / 'migration-receipt.json').unlink()
        with self.assertRaises(module.MigrationError) as raised:
            module.migrate(other, apply=True, confirm_no_writers=True)
        required = raised.exception.value
        self.assertEqual(required['status'], 'owner-import-required')
        receipt = self.import_owner(required)
        self.assertEqual(json.loads(receipt.read_bytes())['appended'], 0)
        recovered = module.migrate(other, apply=True, confirm_no_writers=True, import_receipts=[receipt])
        self.assertEqual(recovered['context']['store_id'], result['context']['store_id'])
        self.assertEqual(self.native(recovered['context']['native_args'], 'project',
                                     '--projection', 'import-records')['data'], records + [retired])

    def test_conflicting_legacy_registration_has_no_destination_effects(self):
        selected = module.resolve(initialize=True)
        self.capture(selector=selected['native_args'])
        legacy = self.root / 'old registered custody'
        (legacy / '.ledger').mkdir(parents=True)
        legacy_id = 'a' * 32
        module.write_json(legacy / module.MARKER, {'schema': module.MARKER_SCHEMA, 'store_id': legacy_id})
        registration = self.repo / '.git' / module.REGISTRATION
        module.write_json(registration, {'schema': 'ledger-repository-registration/v1', 'store_id': legacy_id, 'store_root': str(legacy)})
        self.retired()
        registration_before = registration.read_bytes()
        before = self.snapshot(self.root)
        with self.assertRaisesRegex(module.MigrationError, 'ConflictingLegacyRegistration'):
            self.apply(store_id=selected['store_id'])
        self.assertEqual(self.snapshot(self.root), before)
        self.assertEqual(registration.read_bytes(), registration_before)

    def migration_process(self):
        argv = module.command(self.repo) + ['--migrate', '--apply', '--confirm-no-writers']
        for manifest in sorted(SKILLS.glob('*/migration.json')):
            argv += ['--owner-manifest', str(manifest)]
        process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(lambda: process.kill() if process.poll() is None else None)
        return process

    def wait_for_path(self, path, process):
        deadline = time.monotonic() + 15
        while not path.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue(path.exists())
        self.assertIsNone(process.poll())

    def test_attachment_before_migration_lock_rejects_without_destination_effects(self):
        self.capture()
        competing = module.resolve(initialize=True)
        with module.native_lock(self.repo / '.git/ledger-store.lock'):
            process = self.migration_process()
            preparations = self.root / 'home/preparations'
            self.wait_for_path(preparations, process)
            module.register_root(Path(competing['store_root']), competing['store_id'], self.repo)
        out, err = process.communicate(timeout=20)
        self.assertNotEqual(process.returncode, 0, out + err)
        self.assertEqual(json.loads(out)['error_code'], 'MigrationIdentityChanged')
        self.assertEqual(module.resolve(self.repo)['store_id'], competing['store_id'])
        self.assertFalse((Path(competing['store_root']) / 'legacy-archive').exists())
        self.assertEqual(list((self.root / 'home/repos').iterdir()), [Path(competing['store_root'])])

    def test_changed_source_while_waiting_blocks_publication(self):
        source = self.capture()
        with module.native_lock(self.repo / '.git/ledger-store.lock'):
            process = self.migration_process()
            self.wait_for_path(self.root / 'home/preparations', process)
            source.write_bytes(source.read_bytes() + b'{}\n')
        out, err = process.communicate(timeout=20)
        self.assertNotEqual(process.returncode, 0, out + err)
        self.assertEqual(json.loads(out)['error_code'], 'MigrationSourceChanged')
        self.assertFalse((self.root / 'home/catalog.json').exists())

    def test_surviving_directory_gaining_git_blocks_publication(self):
        self.capture()
        shutil.rmtree(self.repo / '.git')
        home = self.root / 'home'
        home.mkdir()
        digest = hashlib.sha256(json.dumps({'workspace_root': str(self.repo)}, separators=(',', ':')).encode()).hexdigest()
        with module.native_lock(home / 'catalog.lock'):
            process = self.migration_process()
            self.wait_for_path(home / 'preparations' / digest / 'ledger-store.lock', process)
            self.git('init', '-q')
        out, err = process.communicate(timeout=20)
        self.assertNotEqual(process.returncode, 0, out + err)
        self.assertEqual(json.loads(out)['error_code'], 'MigrationSourceChanged')
        self.assertFalse((home / 'catalog.json').exists())

    def test_catalog_attachment_and_migration_cannot_publish_competing_aliases(self):
        self.capture()
        competing = module.resolve(initialize=True)
        process = self.migration_process()
        attacher = subprocess.Popen(module.command(self.repo, store_id=competing['store_id']) +
                                    ['--register-root', competing['store_root']],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(lambda: attacher.kill() if attacher.poll() is None else None)
        out, err = process.communicate(timeout=25)
        attached, attach_error = attacher.communicate(timeout=25)
        selected = module.resolve(self.repo)
        if process.returncode == 0:
            self.assertEqual(selected['store_id'], json.loads(out)['context']['store_id'])
            self.assertNotEqual(attacher.returncode, 0, attached + attach_error)
        else:
            self.assertEqual(attacher.returncode, 0, attached + attach_error)
            self.assertEqual(selected['store_id'], competing['store_id'])
            self.assertFalse((Path(competing['store_root']) / 'legacy-archive').exists())
        self.assertEqual(module.resolve(store_id=competing['store_id'])['store_root'], competing['store_root'])

    def test_registration_preserves_staged_identity_and_same_id_import_resume(self):
        unrelated = module.resolve(initialize=True)
        self.capture()
        self.retired()
        with self.assertRaises(module.MigrationError) as raised:
            self.apply()
        staged = raised.exception.value
        self.assertEqual(staged['status'], 'owner-import-required', staged)
        selected = staged['context']
        catalog = self.root / 'home/catalog.json'
        before = catalog.read_bytes()
        with self.assertRaisesRegex(module.MigrationError, 'PendingCustodyConflictsWithCatalog'):
            module.register_root(unrelated['store_root'], unrelated['store_id'], self.repo)
        self.assertEqual(catalog.read_bytes(), before)
        registered = module.register_root(selected['store_root'], selected['store_id'], self.repo)
        self.assertEqual(registered['store_id'], selected['store_id'])
        receipt = self.import_owner(staged)
        completed = self.apply(import_receipts=[receipt])
        self.assertEqual(completed['status'], 'verified')
        self.assertEqual(completed['context']['store_id'], selected['store_id'])
        self.assertEqual(module.resolve(self.repo)['store_id'], selected['store_id'])
        self.assertFalse(self.apply()['storage_mutated'])

    def test_multi_slot_retired_import_checks_every_revision(self):
        skills = self.root / 'fixture-skills'
        owner = skills / 'two-slot'
        owner.mkdir(parents=True)
        definition = owner / 'definition.json'
        plan = json.loads((Path(__file__).parent / 'fixtures/event-binding-definition.json').read_bytes())
        plan['storage']['slots']['audits'] = dict(plan['storage']['slots']['events'], path='example/audits.jsonl')
        plan['operations']['append-audit'] = copy.deepcopy(plan['operations']['append'])
        plan['operations']['append-audit']['effects'][0]['slot'] = 'audits'
        plan['projections']['audits'] = copy.deepcopy(plan['projections']['all'])
        plan['projections']['audits']['slot'] = 'audits'
        definition.write_text(json.dumps(plan))
        (owner / 'importer.py').write_text('owner fixture constructor')
        (owner / 'migration.json').write_text(json.dumps({
            'schema': 'ledger-owner-migration/v1', 'definition': 'definition.json',
            'retired_sources': ['.retired-two-slot.jsonl'], 'importer': 'importer.py'}))
        expected = {'events': [{'kind': 'historical', 'value': 1}],
                    'audits': [{'kind': 'independent-audit', 'value': 7}]}
        source = self.repo / '.retired-two-slot.jsonl'
        source.write_text(json.dumps(expected) + '\n')
        with self.assertRaises(module.MigrationError) as raised:
            self.apply(skill_root=skills)
        staged = raised.exception.value
        self.assertEqual(staged['status'], 'owner-import-required', staged)
        selected = staged['context']
        requested = staged['owner_imports'][0]
        self.assertEqual(len(requested['sources']), 1)
        archived = Path(requested['sources'][0]['source'])
        self.assertEqual(archived.read_bytes(), source.read_bytes())
        self.assertEqual(hashlib.sha256(archived.read_bytes()).hexdigest(),
                         requested['sources'][0]['source_sha256'])
        original = json.loads(archived.read_text())
        for slot, operation, projection in [('events', 'append', 'all'),
                                            ('audits', 'append-audit', 'audits')]:
            for record in original[slot]:
                self.native(selected['native_args'], 'transact', '--operation', operation,
                            '--input', 'event=-', '--param', 'request=import-' + slot,
                            packet=record, definition=definition)
            projected = self.native(selected['native_args'], 'project', '--projection', projection,
                                    definition=definition)['data']
            self.assertEqual(projected, expected[slot])
        health = self.native(selected['native_args'], 'doctor', definition=definition)
        revisions = {slot['logical_ref']: slot['revision'] for slot in health['slots']}
        self.assertEqual(len(set(revisions.values())), 2)
        receipt = {'schema': 'two-slot-owner-import/v1', 'status': 'verified',
                   'definition_path': str(definition), 'store_root': selected['store_root'],
                   'store_id': selected['store_id'], 'authority_granted': False,
                   'full_record_parity_verified': True,
                   'definition': health['definition'],
                   'sources': requested['sources'], 'revisions': revisions}
        receipt_path = self.root / 'two-slot-receipt.json'
        for altered in [{}, {**revisions, 'example/audits.jsonl': 'wrong'},
                        {**revisions, 'unknown': None}, {**revisions, 'example/events.jsonl': None}]:
            receipt_path.write_text(json.dumps(dict(receipt, revisions=altered)))
            with self.assertRaisesRegex(module.MigrationError, 'OwnerImportRevisionMismatch'):
                self.apply(skill_root=skills, import_receipts=[receipt_path])
            self.assertFalse((self.root / 'home/catalog.json').exists())
        receipt_path.write_text(json.dumps(receipt))
        completed = self.apply(skill_root=skills, import_receipts=[receipt_path])
        self.assertEqual(completed['status'], 'verified')
        self.assertEqual(completed['context']['store_id'], selected['store_id'])
        self.assertFalse(self.apply(skill_root=skills)['storage_mutated'])
        for slot, projection in [('events', 'all'), ('audits', 'audits')]:
            self.assertEqual(self.native(selected['native_args'], 'project', '--projection', projection,
                                         definition=definition)['data'], expected[slot])

    def test_all_actual_owners_preserve_independent_full_records(self):
        self.capture()
        history = module.load_module(SKILLS / 'learnings/tests/test_native_history.py')
        fixture = history.NegativeHistoryTests()
        fixture.store_id = 'a' * 32
        negative_record = fixture.record()
        negative = SKILLS / 'negative-ledger/definitions/ledger/negative-evidence-protocol.json'
        self.native(['--repo', str(self.repo)], 'transact', '--operation', 'capture', '--input', 'capture=-',
                    '--param', 'capture_key=migration-independent-record', packet={'record': negative_record}, definition=negative)
        review = SKILLS / 'review-fold/definitions/ledger/counterexample-corpus.json'
        review_packet = json.loads((SKILLS / 'review-fold/tests/fixtures/counterexample-capture-valid.json').read_bytes())
        self.native(['--repo', str(self.repo)], 'transact', '--operation', 'capture', '--input', 'submission=-',
                    packet=review_packet, definition=review)
        before = self.snapshot(self.repo)
        negatives = self.native(['--repo', str(self.repo)], 'project', '--projection', 'current-records', definition=negative)['data']
        reviews = self.native(['--repo', str(self.repo)], 'project', '--projection', 'basis',
                              '--param', 'repository=' + review_packet['record']['repository_id'], definition=review)['data']
        selected = self.apply()['context']
        self.assertEqual(self.snapshot(self.repo), before)
        for name, raw in before.items():
            if name.endswith('events.jsonl'):
                self.assertEqual((Path(selected['store_root']) / name).read_bytes(), raw)
        self.assertEqual(self.native(selected['native_args'], 'project', '--projection', 'current-records', definition=negative)['data'], negatives)
        self.assertEqual(negatives[0]['record'], negative_record)
        self.assertEqual(self.native(selected['native_args'], 'project', '--projection', 'basis',
                                     '--param', 'repository=' + review_packet['record']['repository_id'], definition=review)['data'], reviews)
        self.assertEqual(len(reviews), 1)
        for key, value in review_packet['record'].items():
            self.assertEqual(reviews[0][key], value)


if __name__ == '__main__':
    unittest.main()
