import importlib.util
import json
import os
from pathlib import Path
import select
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SKILLS = Path(__file__).resolve().parents[2]
import native_host as custody


@unittest.skipUnless(os.environ.get('LEDGER_BIN'), 'LEDGER_BIN required for native repair proof')
class ArchiveRepairTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        env = patch.dict(os.environ, {'LEDGER_HOME': str(self.root / 'home')})
        env.start()
        self.addCleanup(env.stop)
        self.ctx = custody
        self.context = self.ctx.resolve(initialize=True)
        self.store = Path(self.context['store_root'])
        self.definition = SKILLS / 'review-fold/definitions/ledger/counterexample-corpus.json'
        self.packet = SKILLS / 'review-fold/tests/fixtures/counterexample-capture-valid.json'
        self.binary = os.environ['LEDGER_BIN']
        self.capture()
        self.slot = self.store / '.ledger/review-fold/counterexamples/events.jsonl'
        self.original = self.slot.read_bytes()
        self.archive = self.store / 'legacy-archive/fixture'
        snapshot = custody.inventory([self.store], [], slots=['review-fold/counterexamples/events.jsonl'])
        custody.copy_inventory(snapshot, self.archive)
        (self.archive / 'manifest.json').write_text(json.dumps({'schema': 'ledger-legacy-archive/v1', 'sources': snapshot}))
        self.archived_slot = self.archive / 'worktree-0/.ledger/review-fold/counterexamples/events.jsonl'

    def capture(self, packet=None, *, success=True):
        result = subprocess.run([self.binary, 'transact', '--definition', str(self.definition),
                                 *self.context['native_args'], '--operation', 'capture',
                                 '--input', 'submission=' + str(packet or self.packet), '--format', 'json'],
                                capture_output=True, timeout=15)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return json.loads(result.stdout)

    def repair(self):
        return custody.restore_archived_slot(self.context, self.definition, binary=self.binary)

    def test_native_restore_preserves_binding_bytes_and_allows_next_capture(self):
        bindings = {p.name: p.read_bytes() for p in (self.store / '.ledger/.bindings').glob('*.jsonl')}
        self.slot.unlink()
        result = self.repair()
        self.assertEqual(result['preparation']['outcome'], 'prepared')
        self.assertEqual(self.slot.read_bytes(), self.original)
        self.assertEqual(self.archived_slot.read_bytes(), self.original)
        self.assertEqual(bindings, {p.name: p.read_bytes() for p in (self.store / '.ledger/.bindings').glob('*.jsonl')})
        self.assertTrue(self.capture()['valid'])
        self.assertNotIn('preparation', self.repair())

    def test_healthy_store_never_scans_archives(self):
        (self.archive / 'manifest.json').write_text('invalid')
        self.assertNotIn('preparation', self.repair())

    def test_archive_repair_cannot_install_unbound_live_history(self):
        workspace = self.root / 'workspace'
        workspace.mkdir()
        shutil.copytree(self.store / '.ledger', workspace / '.ledger')
        self.ctx.register_root(self.store, self.context['store_id'], workspace)
        self.slot.unlink()
        shutil.rmtree(self.store / '.ledger/.bindings')
        shutil.rmtree(self.store / 'legacy-archive')
        before = {str(path.relative_to(self.root)): path.read_bytes()
                  for path in self.root.rglob('*') if path.is_file()}
        command = custody.owner_command(workspace, self.definition, binary=self.binary, mode='--repair-archive')
        result = subprocess.run(command, capture_output=True, timeout=15)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['error_code'], 'ArchiveRepairRequiresBoundMissingSlot')
        self.assertEqual(before, {str(path.relative_to(self.root)): path.read_bytes()
                                 for path in self.root.rglob('*') if path.is_file()})

    def test_archive_repair_requires_an_archive_even_with_matching_live_copy(self):
        workspace = self.root / 'workspace'
        workspace.mkdir()
        shutil.copytree(self.store / '.ledger', workspace / '.ledger')
        self.ctx.register_root(self.store, self.context['store_id'], workspace)
        self.slot.unlink()
        shutil.rmtree(self.store / 'legacy-archive')
        before = {str(path.relative_to(self.root)): path.read_bytes()
                  for path in self.root.rglob('*') if path.is_file()}
        command = custody.owner_command(workspace, self.definition, binary=self.binary, mode='--repair-archive')
        result = subprocess.run(command, capture_output=True, timeout=15)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['error_code'], 'ArchiveRepairRequiresArchiveEvidence')
        self.assertEqual(before, {str(path.relative_to(self.root)): path.read_bytes()
                                 for path in self.root.rglob('*') if path.is_file()})

    def test_direct_repair_of_empty_workspace_requires_and_accepts_quiescence(self):
        workspace = self.root / 'workspace'
        workspace.mkdir()
        self.ctx.register_root(self.store, self.context['store_id'], workspace)
        binding = {path.name: path.read_bytes() for path in (self.store / '.ledger/.bindings').glob('*.jsonl')}
        self.slot.unlink()
        command = custody.owner_command(workspace, self.definition, binary=self.binary, mode='--repair-archive')
        refused = subprocess.run(command, capture_output=True, timeout=15)
        self.assertEqual(refused.returncode, 3, refused.stdout + refused.stderr)
        self.assertEqual(json.loads(refused.stdout)['preparation']['error_code'], 'PreparationRequiresQuiescence')
        self.assertFalse(self.slot.exists())
        restored = subprocess.run(command + ['--confirm-no-legacy-writers'], capture_output=True, timeout=15)
        self.assertEqual(restored.returncode, 0, restored.stdout + restored.stderr)
        self.assertEqual(json.loads(restored.stdout)['store_id'], self.context['store_id'])
        self.assertEqual(self.slot.read_bytes(), self.original)
        self.assertEqual(self.archived_slot.read_bytes(), self.original)
        self.assertEqual(binding, {path.name: path.read_bytes() for path in (self.store / '.ledger/.bindings').glob('*.jsonl')})
        self.assertFalse((workspace / '.ledger').exists())

    def test_present_corruption_is_not_replaced(self):
        self.slot.write_bytes(b'bad\n')
        with self.assertRaises(custody.MigrationError):
            self.repair()
        self.assertEqual(self.slot.read_bytes(), b'bad\n')

    def test_tampered_archive_is_refused(self):
        self.slot.unlink()
        self.archived_slot.write_bytes(b'bad\n')
        bindings = {path.name: path.read_bytes() for path in (self.store / '.ledger/.bindings').glob('*.jsonl')}
        with self.assertRaises(custody.MigrationError) as caught:
            self.repair()
        self.assertEqual(caught.exception.preparation['error_code'], 'StoreBindingRevisionMismatch')
        self.assertFalse(caught.exception.preparation['storage_mutated'])
        self.assertFalse(self.slot.exists())
        self.assertEqual(self.archived_slot.read_bytes(), b'bad\n')
        self.assertEqual(bindings, {path.name: path.read_bytes() for path in (self.store / '.ledger/.bindings').glob('*.jsonl')})

    def test_stale_archive_cannot_roll_back_newer_binding(self):
        packet = json.loads(self.packet.read_text())
        packet['record']['observed_fact'] += ' Additional independent fixture.'
        changed = self.root / 'changed.json'
        changed.write_text(json.dumps(packet))
        self.capture(changed)
        self.slot.unlink()
        bindings = {path.name: path.read_bytes() for path in (self.store / '.ledger/.bindings').glob('*.jsonl')}
        with self.assertRaises(custody.MigrationError) as caught:
            self.repair()
        self.assertEqual(caught.exception.preparation['error_code'], 'PreparationBindingConflict')
        self.assertFalse(caught.exception.preparation['storage_mutated'])
        self.assertFalse(self.slot.exists())
        self.assertEqual(self.archived_slot.read_bytes(), self.original)
        self.assertEqual(bindings, {path.name: path.read_bytes() for path in (self.store / '.ledger/.bindings').glob('*.jsonl')})

    def test_busy_native_lock_waits_then_repairs(self):
        self.slot.unlink()
        with custody.native_lock(Path(str(self.slot) + '.cas.lock.advisory'), self.ctx):
            import sys
            process = subprocess.Popen(custody.owner_command(None, self.definition, store_id=self.context['store_id'],
                binary=self.binary, mode='--repair-archive'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.addCleanup(lambda: process.kill() if process.poll() is None else None)
            self.addCleanup(lambda: process.communicate(timeout=15))
            self.assertTrue(select.select([process.stderr], [], [], 10)[0])
            self.assertIn(b'Waiting for active Ledger writer', process.stderr.readline())
            self.assertIsNone(process.poll())
            self.assertFalse(self.slot.exists())
        out, err = process.communicate(timeout=15)
        self.assertEqual(process.returncode, 0, out + err)
        self.assertEqual(self.slot.read_bytes(), self.original)

    def test_native_writer_obeys_helper_lock(self):
        with custody.native_lock(Path(str(self.slot) + '.cas.lock.advisory'), self.ctx):
            result = self.capture(success=False)
            self.assertEqual(result['code'], 'LockBusy')
        self.assertEqual(self.slot.read_bytes(), self.original)

    def test_pending_transactions_prevent_repair(self):
        self.slot.unlink()
        pending = self.store / '.ledger/.transactions/interrupted'
        pending.mkdir()
        (pending / 'transaction.json').write_text('{')
        before = {str(p.relative_to(self.store)): p.read_bytes() for p in self.store.rglob('*') if p.is_file()}
        with self.assertRaises(custody.MigrationError):
            self.repair()
        self.assertEqual(before, {str(p.relative_to(self.store)): p.read_bytes() for p in self.store.rglob('*') if p.is_file()})
        self.assertFalse(self.slot.exists())

    def test_unbound_local_history_cannot_trigger_archive_restoration(self):
        local = self.root / 'workspace/.ledger/review-fold/counterexamples/events.jsonl'
        local.parent.mkdir(parents=True)
        local.write_bytes(self.original + b'new local history\n')
        self.context['workspace_root'] = str(self.root / 'workspace')
        self.slot.unlink()
        with self.assertRaises(custody.MigrationError) as caught:
            self.repair()
        self.assertEqual(caught.exception.preparation['error_code'], 'StoreSlotWithoutBinding')
        self.assertFalse(caught.exception.preparation['storage_mutated'])
        self.assertFalse(self.slot.exists())
        self.assertEqual(local.read_bytes(), self.original + b'new local history\n')

    def test_local_divergence_requires_reconciliation(self):
        workspace = self.root / 'workspace'
        local = workspace / '.ledger/review-fold/counterexamples/events.jsonl'
        local.parent.mkdir(parents=True)
        local.write_bytes(self.original)
        for name in custody.ARCHIVES:
            source = self.store / '.ledger' / name
            if source.exists():
                shutil.copytree(source, workspace / '.ledger' / name)
        packet = json.loads(self.packet.read_text())
        packet['record']['observed_fact'] += ' Independent local extension.'
        captured = subprocess.run([self.binary, 'transact', '--definition', str(self.definition),
            '--repo', str(workspace), '--operation', 'capture', '--input', 'submission=-', '--format', 'json'],
            input=json.dumps(packet).encode(), capture_output=True, timeout=15)
        self.assertEqual(captured.returncode, 0, captured.stdout + captured.stderr)
        local_before = local.read_bytes()
        bindings = {path.name: path.read_bytes() for path in (self.store / '.ledger/.bindings').glob('*.jsonl')}
        self.context['workspace_root'] = str(workspace)
        self.slot.unlink()
        with self.assertRaises(custody.MigrationError) as caught:
            self.repair()
        self.assertEqual(caught.exception.preparation['error_code'], 'PreparationBindingConflict')
        self.assertFalse(caught.exception.preparation['storage_mutated'])
        self.assertFalse(self.slot.exists())
        self.assertEqual(local.read_bytes(), local_before)
        self.assertEqual(bindings, {path.name: path.read_bytes() for path in (self.store / '.ledger/.bindings').glob('*.jsonl')})

    def test_archive_symlink_is_refused(self):
        self.slot.unlink()
        outside = self.root / 'outside.jsonl'
        outside.write_bytes(self.original)
        self.archived_slot.unlink()
        self.archived_slot.symlink_to(outside)
        with self.assertRaises(RuntimeError):
            self.repair()
        self.assertFalse(self.slot.exists())

    def test_malformed_archive_manifest_is_refused(self):
        self.slot.unlink()
        (self.archive / 'manifest.json').write_text('[]')
        with self.assertRaisesRegex(custody.MigrationError, 'InvalidArchiveManifest'):
            self.repair()
        self.assertFalse(self.slot.exists())


if __name__ == '__main__':
    unittest.main()
