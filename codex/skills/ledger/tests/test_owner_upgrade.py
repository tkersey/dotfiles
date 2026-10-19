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
SCRIPT = SKILLS / 'ledger/scripts/ensure_custody.py'
spec = importlib.util.spec_from_file_location('custody', SCRIPT)
custody = importlib.util.module_from_spec(spec)
spec.loader.exec_module(custody)


@unittest.skipUnless(os.environ.get('LEDGER_BIN'), 'Native Ledger is required')
class OwnerUpgradeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        env = patch.dict(os.environ, {'LEDGER_HOME': str(self.root / 'home')})
        env.start()
        self.addCleanup(env.stop)
        self.ctx = custody.load_module(SKILLS / 'ledger/scripts/ledger_context.py')
        self.definition = SKILLS / 'review-fold/definitions/ledger/counterexample-corpus.json'
        self.packet = SKILLS / 'review-fold/tests/fixtures/counterexample-capture-valid.json'
        self.binary = os.environ['LEDGER_BIN']
        self.slot = Path('.ledger/review-fold/counterexamples/events.jsonl')

    def capture(self, selector, packet=None):
        result = subprocess.run([self.binary, 'transact', '--definition', str(self.definition),
            *selector, '--operation', 'capture', '--input', 'submission=' + str(packet or self.packet),
            '--format', 'json'], capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def ensure(self, **kwargs):
        return custody.owner_context(self.repo, self.definition, maintain=True, binary=self.binary, **kwargs)

    def command(self, *flags):
        return [sys.executable, str(SCRIPT), '--repo', str(self.repo), '--definition', str(self.definition),
                '--ledger-bin', self.binary, *flags]

    def test_fresh_install_initializes_managed_custody_and_captures(self):
        context = self.ensure()
        self.assertIn('--store-root', context['native_args'])
        self.assertFalse((self.repo / '.ledger').exists())
        self.assertTrue(self.capture(context['native_args'])['valid'])
        self.assertEqual(self.ensure()['store_id'], context['store_id'])

    def test_local_only_install_migrates_without_rewriting_records(self):
        self.capture(['--repo', str(self.repo)])
        original = (self.repo / self.slot).read_bytes()
        context = self.ensure()
        self.assertEqual((Path(context['store_root']) / self.slot).read_bytes(), original)
        self.assertEqual((self.repo / self.slot).read_bytes(), original)
        self.assertTrue(self.capture(context['native_args'])['valid'])

    def test_empty_registered_owner_imports_local_history_without_an_archive(self):
        registered = self.ctx.resolve(self.repo, initialize=True)
        self.capture(['--repo', str(self.repo)])
        original = (self.repo / self.slot).read_bytes()
        context = self.ensure()
        self.assertEqual(context['store_id'], registered['store_id'])
        self.assertEqual((Path(context['store_root']) / self.slot).read_bytes(), original)
        self.assertTrue(self.capture(context['native_args'])['valid'])

    def test_missing_bound_slot_imports_local_copy_without_an_archive(self):
        registered = self.ctx.resolve(self.repo, initialize=True)
        self.capture(['--repo', str(self.repo)])
        store = Path(registered['store_root'])
        for name in custody.ARCHIVES:
            source = self.repo / '.ledger' / name
            if source.exists():
                shutil.copytree(source, store / '.ledger' / name, dirs_exist_ok=True)
        original_binding = {p.name: p.read_bytes() for p in (store / '.ledger/.bindings').glob('*.jsonl')}
        context = self.ensure()
        self.assertEqual(context['store_id'], registered['store_id'])
        self.assertEqual((store / self.slot).read_bytes(), (self.repo / self.slot).read_bytes())
        self.assertEqual(original_binding, {p.name: p.read_bytes() for p in (store / '.ledger/.bindings').glob('*.jsonl')})

    def test_read_only_does_not_initialize_or_migrate(self):
        self.capture(['--repo', str(self.repo)])
        with self.assertRaisesRegex(custody.MigrationError, 'read-only'):
            custody.owner_context(self.repo, self.definition, read_only=True, binary=self.binary)
        self.assertFalse((self.root / 'home').exists())

    def test_corrupt_managed_history_never_falls_back_to_local(self):
        self.capture(['--repo', str(self.repo)])
        context = self.ensure()
        slot = Path(context['store_root']) / self.slot
        slot.write_bytes(b'corrupt\n')
        with self.assertRaises(custody.MigrationError):
            self.ensure()
        self.assertEqual(slot.read_bytes(), b'corrupt\n')

    def test_waits_for_writer_then_migrates(self):
        self.capture(['--repo', str(self.repo)])
        path = Path(str(self.repo / self.slot) + '.cas.lock.advisory')
        with custody.native_lock(path, self.ctx):
            process = subprocess.Popen(self.command('--ensure-owner'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.addCleanup(lambda: process.kill() if process.poll() is None else None)
            self.assertTrue(select.select([process.stderr], [], [], 10)[0])
            self.assertIn(b'Waiting for active Ledger writer', process.stderr.readline())
            self.assertIsNone(process.poll())
        out, err = process.communicate(timeout=15)
        self.assertEqual(process.returncode, 0, out + err)
        context = json.loads(out)
        self.assertEqual((Path(context['store_root']) / self.slot).read_bytes(), (self.repo / self.slot).read_bytes())

    def test_parallel_ensures_converge_on_one_store(self):
        self.capture(['--repo', str(self.repo)])
        processes = [subprocess.Popen(self.command('--ensure-owner'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                     for _ in range(2)]
        for process in processes:
            self.addCleanup(lambda process=process: process.communicate(timeout=20))
        results = []
        for process in processes:
            out, err = process.communicate(timeout=20)
            self.assertEqual(process.returncode, 0, out + err)
            results.append(json.loads(out))
        self.assertEqual(results[0]['store_id'], results[1]['store_id'])

    def test_archive_only_owner_is_imported_without_starting_empty_history(self):
        registered = self.ctx.resolve(self.repo, initialize=True)
        self.capture(registered['native_args'])
        store = Path(registered['store_root'])
        original = (store / self.slot).read_bytes()
        snapshot = custody.inventory([store], [], slots=[str(self.slot.relative_to('.ledger'))])
        archive = store / 'legacy-archive/fixture'
        custody.copy_inventory(snapshot, archive)
        (archive / 'manifest.json').write_text(json.dumps({'schema': 'ledger-legacy-archive/v1', 'sources': snapshot}))
        (store / self.slot).unlink()
        shutil.rmtree(store / '.ledger/.bindings')
        context = self.ensure()
        self.assertEqual(context['store_id'], registered['store_id'])
        self.assertEqual((store / self.slot).read_bytes(), original)

    def test_interrupted_registered_publication_resumes_from_preserved_sources(self):
        registered = self.ctx.resolve(self.repo, initialize=True)
        self.capture(['--repo', str(self.repo)])
        store = Path(registered['store_root'])
        publish = custody.publish_absent

        def interrupt(source, target):
            if target == store / self.slot:
                raise OSError('simulated interruption')
            return publish(source, target)

        with patch.object(custody, 'publish_absent', side_effect=interrupt):
            with self.assertRaisesRegex(OSError, 'simulated interruption'):
                self.ensure()
        self.assertFalse((store / self.slot).exists())
        context = self.ensure()
        self.assertEqual(context['store_id'], registered['store_id'])
        self.assertEqual((store / self.slot).read_bytes(), (self.repo / self.slot).read_bytes())

    def test_linked_worktree_prefix_histories_migrate_as_one_complete_history(self):
        subprocess.run(['git', '-C', str(self.repo), 'init', '-q'], check=True)
        subprocess.run(['git', '-C', str(self.repo), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                        'commit', '--allow-empty', '-qm', 'fixture'], check=True)
        other = self.root / 'other'
        subprocess.run(['git', '-C', str(self.repo), 'worktree', 'add', '--detach', str(other)], check=True, capture_output=True)
        self.capture(['--repo', str(self.repo)])
        shutil.copytree(self.repo / '.ledger', other / '.ledger')
        shutil.rmtree(other / '.ledger/.transactions')
        packet = json.loads(self.packet.read_text())
        packet['record']['observed_fact'] += ' A second witness.'
        changed = self.root / 'changed.json'
        changed.write_text(json.dumps(packet))
        self.capture(['--repo', str(other)], changed)
        context = self.ensure()
        self.assertEqual((Path(context['store_root']) / self.slot).read_bytes(), (other / self.slot).read_bytes())
        self.assertEqual(self.ctx.resolve(other)['store_id'], context['store_id'])

    def test_missing_registered_owner_discovers_history_in_sibling_worktree(self):
        subprocess.run(['git', '-C', str(self.repo), 'init', '-q'], check=True)
        subprocess.run(['git', '-C', str(self.repo), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                        'commit', '--allow-empty', '-qm', 'fixture'], check=True)
        other = self.root / 'other'
        subprocess.run(['git', '-C', str(self.repo), 'worktree', 'add', '--detach', str(other)], check=True, capture_output=True)
        registered = self.ctx.resolve(self.repo, initialize=True)
        self.capture(['--repo', str(other)])
        with self.assertRaisesRegex(custody.MigrationError, 'read-only'):
            custody.owner_context(self.repo, self.definition, read_only=True, binary=self.binary)
        self.assertFalse((Path(registered['store_root']) / self.slot).exists())
        context = self.ensure()
        self.assertEqual(context['store_id'], registered['store_id'])
        self.assertEqual((Path(context['store_root']) / self.slot).read_bytes(), (other / self.slot).read_bytes())

    def test_missing_local_bound_history_does_not_start_an_empty_owner(self):
        registered = self.ctx.resolve(self.repo, initialize=True)
        self.capture(['--repo', str(self.repo)])
        (self.repo / self.slot).unlink()
        with self.assertRaisesRegex(custody.MigrationError, 'StoreBindingWithoutSlot'):
            self.ensure()
        self.assertFalse((Path(registered['store_root']) / self.slot).exists())


if __name__ == '__main__':
    unittest.main()
