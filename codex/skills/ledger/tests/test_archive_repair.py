import importlib.util
import json
import os
from pathlib import Path
import select
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SKILLS = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('custody', SKILLS / 'ledger/scripts/ensure_custody.py')
custody = importlib.util.module_from_spec(spec)
spec.loader.exec_module(custody)


class PublicationTests(unittest.TestCase):
    def test_publication_is_atomic_without_extra_links(self):
        with tempfile.TemporaryDirectory() as temporary:
            source, target = Path(temporary) / 'source', Path(temporary) / 'target'
            source.write_bytes(b'archive')
            custody.publish_absent(source, target)
            self.assertEqual(target.read_bytes(), b'archive')
            self.assertEqual(target.stat().st_nlink, 1)
            self.assertFalse(source.exists())

    def test_existing_target_is_never_replaced(self):
        with tempfile.TemporaryDirectory() as temporary:
            source, target = Path(temporary) / 'source', Path(temporary) / 'target'
            source.write_bytes(b'archive')
            target.write_bytes(b'current')
            with self.assertRaises(FileExistsError):
                custody.publish_absent(source, target)
            self.assertEqual(target.read_bytes(), b'current')
            self.assertEqual(source.read_bytes(), b'archive')


@unittest.skipUnless(os.environ.get('LEDGER_BIN'), 'LEDGER_BIN required for native repair proof')
class ArchiveRepairTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        env = patch.dict(os.environ, {'LEDGER_HOME': str(self.root / 'home')})
        env.start()
        self.addCleanup(env.stop)
        self.ctx = custody.load_module(SKILLS / 'ledger/scripts/ledger_context.py')
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
        self.assertTrue(result['custody_repair']['doctor']['healthy'])
        self.assertEqual(self.slot.read_bytes(), self.original)
        self.assertEqual(self.archived_slot.read_bytes(), self.original)
        self.assertEqual(bindings, {p.name: p.read_bytes() for p in (self.store / '.ledger/.bindings').glob('*.jsonl')})
        self.assertTrue(self.capture()['valid'])
        self.assertNotIn('custody_repair', self.repair())

    def test_healthy_store_never_scans_archives(self):
        (self.archive / 'manifest.json').write_text('invalid')
        self.assertNotIn('custody_repair', self.repair())

    def test_present_corruption_is_not_replaced(self):
        self.slot.write_bytes(b'bad\n')
        with self.assertRaises(custody.MigrationError):
            self.repair()
        self.assertEqual(self.slot.read_bytes(), b'bad\n')

    def test_tampered_archive_is_refused(self):
        self.slot.unlink()
        self.archived_slot.write_bytes(b'bad\n')
        with self.assertRaisesRegex(custody.MigrationError, 'inventory'):
            self.repair()
        self.assertFalse(self.slot.exists())

    def test_stale_archive_cannot_roll_back_newer_binding(self):
        packet = json.loads(self.packet.read_text())
        packet['record']['observed_fact'] += ' Additional independent fixture.'
        changed = self.root / 'changed.json'
        changed.write_text(json.dumps(packet))
        self.capture(changed)
        self.slot.unlink()
        with self.assertRaisesRegex(custody.MigrationError, 'existing native binding'):
            self.repair()
        self.assertFalse(self.slot.exists())

    def test_busy_native_lock_waits_then_repairs(self):
        self.slot.unlink()
        with custody.native_lock(Path(str(self.slot) + '.cas.lock.advisory'), self.ctx):
            import sys
            process = subprocess.Popen([sys.executable, str(SKILLS / 'ledger/scripts/ensure_custody.py'),
                '--store-id', self.context['store_id'], '--repair-archive', '--definition', str(self.definition),
                '--ledger-bin', self.binary], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
        real = custody.native

        def pending(*args, **kwargs):
            result = real(*args, **kwargs)
            if args[3] == 'doctor':
                result['pending_transactions'] = 1
            return result

        with patch.object(custody, 'native', side_effect=pending):
            with self.assertRaisesRegex(custody.MigrationError, 'unresolved transactions'):
                self.repair()
        self.assertFalse(self.slot.exists())

    def test_local_divergence_requires_reconciliation(self):
        local = self.root / 'workspace/.ledger/review-fold/counterexamples/events.jsonl'
        local.parent.mkdir(parents=True)
        local.write_bytes(self.original + b'new local history\n')
        self.context['workspace_root'] = str(self.root / 'workspace')
        self.slot.unlink()
        with self.assertRaisesRegex(custody.MigrationError, 'Local history differs'):
            self.repair()
        self.assertFalse(self.slot.exists())

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
        with self.assertRaisesRegex(custody.MigrationError, 'Invalid archive manifest'):
            self.repair()
        self.assertFalse(self.slot.exists())


if __name__ == '__main__':
    unittest.main()
