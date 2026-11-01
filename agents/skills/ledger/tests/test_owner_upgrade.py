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
        self.ctx = custody
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
        mode = '--read-only' if '--read-only' in flags else '--ensure-owner'
        return custody.owner_command(self.repo, self.definition, binary=self.binary, mode=mode)

    def test_fresh_install_initializes_managed_custody_and_captures(self):
        context = self.ensure()
        self.assertIn('--store-root', context['native_args'])
        self.assertFalse((self.repo / '.ledger').exists())
        self.assertTrue(self.capture(context['native_args'])['valid'])
        self.assertEqual(self.ensure()['store_id'], context['store_id'])

    def test_oversized_unrelated_payload_is_neither_copied_nor_archived(self):
        self.capture(['--repo', str(self.repo)])
        original = (self.repo / self.slot).read_bytes()
        unrelated = self.repo / '.ledger/cas/oversized'
        unrelated.parent.mkdir(parents=True)
        with unrelated.open('wb') as handle:
            handle.truncate(3 * 1024**3)
        context = self.ensure()
        target = Path(context['store_root'])
        self.assertEqual((target / self.slot).read_bytes(), original)
        self.assertEqual((self.repo / self.slot).read_bytes(), original)
        self.assertEqual(unrelated.stat().st_size, 3 * 1024**3)
        self.assertFalse((target / '.ledger/cas').exists())
        self.assertFalse((target / 'legacy-archive').exists())

    def assert_current_owner_transfer(self, owner, filename, fixture_class, input_name, projection):
        history = custody.load_module(SKILLS / 'learnings/tests/test_native_history.py')
        fixture = getattr(history, fixture_class)()
        fixture.store_id = 'a' * 32
        record = fixture.record()
        definition = SKILLS / owner / 'definitions/ledger' / filename
        arguments = ['--param', 'capture_key=owner-transfer'] if owner == 'negative-ledger' else []
        capture = subprocess.run([self.binary, 'transact', '--definition', str(definition),
            '--repo', str(self.repo), '--operation', 'capture', '--input', input_name + '=-',
            *arguments, '--format', 'json'], input=json.dumps({'record': record}).encode(), capture_output=True, timeout=15)
        self.assertEqual(capture.returncode, 0, capture.stdout + capture.stderr)
        slot = Path('.ledger') / owner / 'events.jsonl'
        original = (self.repo / slot).read_bytes()
        context = custody.owner_context(self.repo, definition, maintain=True, binary=self.binary)
        projected = subprocess.run([self.binary, 'project', '--definition', str(definition),
            *context['native_args'], '--projection', projection, '--payload-only', '--format', 'json'],
            capture_output=True, timeout=15)
        self.assertEqual(projected.returncode, 0, projected.stdout + projected.stderr)
        records = json.loads(projected.stdout)
        if owner == 'learnings':
            self.assertEqual(records, [json.loads(line)['record'] for line in original.splitlines()])
            for key, value in record.items():
                self.assertEqual(records[0][key], value)
        else:
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]['record'], record)
            self.assertEqual(records[0]['neg_id'], json.loads(original.splitlines()[0])['neg_id'])
        target = Path(context['store_root'])
        self.assertEqual((target / slot).read_bytes(), original)
        self.assertEqual((self.repo / slot).read_bytes(), original)
        self.assertFalse((target / 'legacy-archive').exists())

    def test_current_learnings_prepares_and_projects_actual_owner_records(self):
        self.assert_current_owner_transfer('learnings', 'learnings-protocol.json',
                                           'LearningHistoryTests', 'submission', 'import-records')

    def test_current_negative_ledger_prepares_and_projects_actual_owner_records(self):
        self.assert_current_owner_transfer('negative-ledger', 'negative-evidence-protocol.json',
                                           'NegativeHistoryTests', 'capture', 'current-records')

    def test_local_history_prepares_for_projection_without_new_capture(self):
        self.capture(['--repo', str(self.repo)])
        original = (self.repo / self.slot).read_bytes()
        records = [json.loads(line)['record'] for line in original.splitlines()]
        prepared = subprocess.run(self.command('--ensure-owner'), stdin=subprocess.DEVNULL,
                                  capture_output=True, timeout=15)
        self.assertEqual(prepared.returncode, 0, prepared.stdout + prepared.stderr)
        context = json.loads(prepared.stdout)
        projected = subprocess.run([self.binary, 'project', '--definition', str(self.definition),
            *context['native_args'], '--projection', 'basis',
            '--param', 'repository=' + records[0]['repository_id'], '--payload-only', '--format', 'json'],
            capture_output=True, timeout=15)
        self.assertEqual(projected.returncode, 0, projected.stdout + projected.stderr)
        self.assertEqual(json.loads(projected.stdout), records)
        retried = subprocess.run(self.command('--ensure-owner'), stdin=subprocess.DEVNULL,
                                 capture_output=True, timeout=15)
        self.assertEqual(retried.returncode, 0, retried.stdout + retried.stderr)
        repeated = json.loads(retried.stdout)
        self.assertEqual(repeated['store_id'], context['store_id'])
        self.assertEqual(repeated['native_args'], context['native_args'])
        self.assertFalse(repeated['storage_mutated'])
        self.assertEqual((Path(context['store_root']) / self.slot).read_bytes(), original)
        self.assertEqual((self.repo / self.slot).read_bytes(), original)

    def test_empty_registered_owner_imports_local_history_without_an_archive(self):
        registered = self.ctx.resolve(self.repo, initialize=True)
        self.capture(['--repo', str(self.repo)])
        original = (self.repo / self.slot).read_bytes()
        context = self.ensure()
        self.assertEqual(context['store_id'], registered['store_id'])
        self.assertEqual((Path(context['store_root']) / self.slot).read_bytes(), original)
        self.assertTrue(self.capture(context['native_args'])['valid'])

    def binding_fixture(self, local_request='first'):
        owner = self.root / 'fixture-owner'
        self.definition = owner / 'definitions/ledger/events.json'
        self.definition.parent.mkdir(parents=True)
        shutil.copyfile(Path(__file__).parent / 'fixtures/event-binding-definition.json', self.definition)
        (owner / 'migration.json').write_text(json.dumps({
            'schema': 'ledger-owner-migration/v1', 'definition': 'definitions/ledger/events.json',
            'retired_sources': [], 'importer': None}))
        self.slot = Path('.ledger/example/events.jsonl')
        context = self.ensure()
        for selector, request in [(context['native_args'], 'first'), (['--repo', str(self.repo)], local_request)]:
            appended = subprocess.run([self.binary, 'transact', '--definition', str(self.definition),
                *selector, '--operation', 'append', '--input', 'event=-', '--param', 'request=' + request,
                '--format', 'json'], input=b'{"kind":"one","value":1}', capture_output=True, timeout=15)
            self.assertEqual(appended.returncode, 0, appended.stdout + appended.stderr)
        self.assertEqual((self.repo / self.slot).read_bytes(), (Path(context['store_root']) / self.slot).read_bytes())
        return context

    def tree_bytes(self, root):
        return {str(path.relative_to(root)): path.read_bytes() for path in root.rglob('*') if path.is_file()}

    def test_equal_payload_with_divergent_binding_is_not_covered(self):
        context = self.binding_fixture(local_request='second')
        before = self.tree_bytes(self.root)
        for read_only, code in [(True, 'OwnerPreparationRequired'), (False, 'PreparationDivergentHistory')]:
            with self.subTest(read_only=read_only), self.assertRaisesRegex(custody.MigrationError, code):
                custody.owner_context(self.repo, self.definition, read_only=read_only,
                                      maintain=not read_only, binary=self.binary)
            self.assertEqual(self.tree_bytes(self.root), before)
        self.assertEqual(self.ctx.resolve(self.repo)['store_id'], context['store_id'])
        self.assertEqual(self.tree_bytes(self.root), before)

    def test_equal_payload_and_binding_remains_covered(self):
        context = self.binding_fixture()
        before = self.tree_bytes(self.root)
        observed = custody.owner_context(self.repo, self.definition, read_only=True, binary=self.binary)
        self.assertEqual(observed['store_id'], context['store_id'])
        self.assertEqual(self.tree_bytes(self.root), before)
        self.assertEqual(self.ensure()['store_id'], context['store_id'])
        self.assertEqual(self.tree_bytes(self.root), before)
        projected = subprocess.run([self.binary, 'project', '--definition', str(self.definition),
            *context['native_args'], '--projection', 'all', '--payload-only', '--format', 'json'],
            capture_output=True, timeout=15)
        self.assertEqual(projected.returncode, 0, projected.stdout + projected.stderr)
        self.assertEqual(json.loads(projected.stdout), [{'kind': 'one', 'value': 1}])

    def test_orphan_local_binding_is_not_empty_history(self):
        self.binding_fixture()
        (self.repo / self.slot).unlink()
        before = self.tree_bytes(self.root)
        for read_only in (True, False):
            with self.subTest(read_only=read_only), self.assertRaises(custody.MigrationError):
                custody.owner_context(self.repo, self.definition, read_only=read_only,
                                      maintain=not read_only, binary=self.binary)
            self.assertEqual(self.tree_bytes(self.root), before)

    def test_missing_local_definition_is_not_covered(self):
        self.binding_fixture()
        shutil.rmtree(self.repo / '.ledger/.definitions')
        before = self.tree_bytes(self.root)
        for read_only in (True, False):
            with self.subTest(read_only=read_only), self.assertRaises(custody.MigrationError):
                custody.owner_context(self.repo, self.definition, read_only=read_only,
                                      maintain=not read_only, binary=self.binary)
            self.assertEqual(self.tree_bytes(self.root), before)

    def test_missing_registered_owner_rejects_declared_retired_history(self):
        registered = self.ctx.resolve(self.repo, initialize=True)
        self.definition = SKILLS / 'learnings/definitions/ledger/learnings-protocol.json'
        retired = self.repo / '.learnings.jsonl'
        retired.write_text('{"retired":"owner conversion required"}\n')
        before = self.tree_bytes(self.root)
        for read_only in (True, False):
            with self.subTest(read_only=read_only), self.assertRaisesRegex(
                    custody.MigrationError, 'RetiredSourceRequiresOwnerImporter'):
                custody.owner_context(self.repo, self.definition, read_only=read_only,
                                      maintain=not read_only, binary=self.binary)
            self.assertEqual(self.tree_bytes(self.root), before)
        self.assertEqual(self.ctx.resolve(self.repo)['store_id'], registered['store_id'])

    def test_missing_registered_owner_without_retired_history_remains_usable(self):
        registered = self.ctx.resolve(self.repo, initialize=True)
        self.definition = SKILLS / 'learnings/definitions/ledger/learnings-protocol.json'
        self.assertEqual(self.ensure()['store_id'], registered['store_id'])
        observed = custody.owner_context(self.repo, self.definition, read_only=True, binary=self.binary)
        self.assertEqual(observed['store_id'], registered['store_id'])

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
        with self.assertRaisesRegex(custody.MigrationError, 'OwnerPreparationRequired'):
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

    @unittest.skipUnless(os.environ.get('LEDGER_LEGACY_BIN'), 'Set LEDGER_LEGACY_BIN to qualify the 1.5.5 writer')
    def test_legacy_155_writer_coordinates_with_preparation_and_remains_usable(self):
        legacy = os.environ['LEDGER_LEGACY_BIN']
        version = subprocess.run([legacy, 'version'], capture_output=True, text=True, check=True).stdout.strip()
        self.assertEqual(version, '1.5.5')

        def capture(selector, packet=self.packet):
            return subprocess.run([legacy, 'transact', '--definition', str(self.definition), *selector,
                '--operation', 'capture', '--input', 'submission=' + str(packet), '--format', 'json'],
                capture_output=True, timeout=15)

        original_capture = capture(['--repo', str(self.repo)])
        self.assertEqual(original_capture.returncode, 0, original_capture.stdout + original_capture.stderr)
        original = (self.repo / self.slot).read_bytes()
        writer_lock = Path(str(self.repo / self.slot) + '.cas.lock.advisory')
        self.assertTrue(writer_lock.is_file())
        with custody.native_lock(writer_lock, self.ctx):
            busy = capture(['--repo', str(self.repo)])
            self.assertNotEqual(busy.returncode, 0)
            self.assertEqual(json.loads(busy.stdout)['code'], 'LockBusy')
            process = subprocess.Popen(self.command('--ensure-owner'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.addCleanup(lambda: process.kill() if process.poll() is None else None)
            self.assertTrue(select.select([process.stderr], [], [], 10)[0])
            self.assertIn(b'Waiting for active Ledger writer', process.stderr.readline())
            self.assertIsNone(process.poll())
        out, err = process.communicate(timeout=20)
        self.assertEqual(process.returncode, 0, out + err)
        context = json.loads(out)
        target = Path(context['store_root']) / self.slot
        self.assertEqual(target.read_bytes(), original)
        self.assertEqual((self.repo / self.slot).read_bytes(), original)
        repository = json.loads(self.packet.read_text())['record']['repository_id']
        projection = subprocess.run([legacy, 'project', '--definition', str(self.definition),
            *context['native_args'], '--projection', 'basis', '--param', 'repository=' + repository,
            '--payload-only', '--format', 'json'], capture_output=True, timeout=15)
        self.assertEqual(projection.returncode, 0, projection.stdout + projection.stderr)
        self.assertEqual(json.loads(projection.stdout), [json.loads(line)['record'] for line in original.splitlines()])
        changed = json.loads(self.packet.read_text())
        changed['record']['observed_fact'] += ' Legacy writer after preparation.'
        next_packet = self.root / 'legacy-next.json'
        next_packet.write_text(json.dumps(changed))
        subsequent = capture(context['native_args'], next_packet)
        self.assertEqual(subsequent.returncode, 0, subsequent.stdout + subsequent.stderr)
        self.assertEqual(len(target.read_bytes().splitlines()), 2)
        self.assertEqual(json.loads(target.read_bytes().splitlines()[1])['record']['observed_fact'],
                         changed['record']['observed_fact'])
        self.assertEqual(self.ensure()['store_id'], context['store_id'])
        self.assertEqual((self.repo / self.slot).read_bytes(), original)

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
        with self.assertRaisesRegex(custody.MigrationError, 'PreparationRequiresQuiescence'):
            self.ensure()
        context = self.ensure(confirm_no_writers=True)
        self.assertEqual(context['store_id'], registered['store_id'])
        self.assertEqual((store / self.slot).read_bytes(), original)

    def test_interrupted_registered_publication_resumes_from_preserved_sources(self):
        registered = self.ctx.resolve(self.repo, initialize=True)
        self.capture(['--repo', str(self.repo)])
        original = (self.repo / self.slot).read_bytes()
        store = Path(registered['store_root'])
        probe = Path(os.environ.get('LEDGER_PREPARATION_PROBE_BIN',
                                    str(Path(self.binary).with_name('ledger-preparation-probe'))))
        self.assertTrue(probe.is_file(), 'Build the native preparation probe before adapter qualification')
        with patch.dict(os.environ, {'LEDGER_PREPARATION_FAULT': 'publication'}):
            interrupted = subprocess.run(custody.owner_command(self.repo, self.definition, binary=probe),
                                         capture_output=True, timeout=20)
        self.assertEqual(interrupted.returncode, 99, interrupted.stdout + interrupted.stderr)
        self.assertEqual(self.ctx.resolve(self.repo)['store_id'], registered['store_id'])
        self.assertFalse((store / self.slot).exists())
        self.assertEqual((self.repo / self.slot).read_bytes(), original)
        context = self.ensure()
        self.assertEqual(context['store_id'], registered['store_id'])
        self.assertEqual((store / self.slot).read_bytes(), original)
        self.assertEqual((self.repo / self.slot).read_bytes(), original)
        self.assertFalse((store / 'legacy-archive').exists())
        self.assertTrue(self.capture(context['native_args'])['valid'])

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
        with self.assertRaisesRegex(custody.MigrationError, 'OwnerPreparationRequired'):
            custody.owner_context(self.repo, self.definition, read_only=True, binary=self.binary)
        self.assertFalse((Path(registered['store_root']) / self.slot).exists())
        with self.assertRaisesRegex(custody.MigrationError, 'PreparationRequiresQuiescence'):
            self.ensure()
        context = self.ensure(confirm_no_writers=True)
        self.assertEqual(context['store_id'], registered['store_id'])
        self.assertEqual((Path(context['store_root']) / self.slot).read_bytes(), (other / self.slot).read_bytes())

    def test_missing_local_bound_history_does_not_start_an_empty_owner(self):
        registered = self.ctx.resolve(self.repo, initialize=True)
        self.capture(['--repo', str(self.repo)])
        (self.repo / self.slot).unlink()
        with self.assertRaisesRegex(custody.MigrationError, 'StoreBindingWithoutSlot'):
            self.ensure()
        self.assertFalse((Path(registered['store_root']) / self.slot).exists())


    def test_one_hundred_capture_interruptions_keep_one_pending_identity_and_workspace(self):
        self.capture(['--repo', str(self.repo)])
        original = (self.repo / self.slot).read_bytes()
        unrelated = self.repo / '.ledger/unrelated/large'
        unrelated.parent.mkdir(parents=True)
        with unrelated.open('wb') as handle:
            handle.truncate(3 * 1024**3)
        home = self.root / 'home'
        probe = os.environ['LEDGER_PREPARATION_PROBE_BIN']
        identity = None
        retained = None
        with patch.dict(os.environ, {'LEDGER_PREPARATION_FAULT': 'capture'}):
            for attempt in range(100):
                failed = subprocess.run(custody.owner_command(self.repo, self.definition, binary=probe),
                                        capture_output=True, timeout=20)
                self.assertEqual(failed.returncode, 99, failed.stdout + failed.stderr)
                locators = list((home / 'preparations').glob('*/registration.json'))
                self.assertEqual(len(locators), 1)
                current = json.loads(locators[0].read_bytes())
                if identity is None:
                    identity = current
                self.assertEqual(current, identity)
                roots = list((home / 'repos').iterdir())
                self.assertEqual(roots, [Path(identity['store_root'])])
                files = {str(p.relative_to(roots[0])): p.stat().st_size
                         for p in roots[0].rglob('*') if p.is_file()}
                transactions = list((roots[0] / '.ledger/.transactions').glob('dtx-*'))
                self.assertEqual(len(transactions), 1)
                staged = list(transactions[0].glob('.ledger-dtx-stage-*'))
                self.assertEqual(len(staged), 1)
                self.assertFalse((roots[0] / self.slot).exists())
                record = transactions[0] / 'transaction.json'
                transaction = json.loads(record.read_bytes())
                self.assertEqual(transaction['state'], 'preparing')
                self.assertEqual(transaction['owner']['session_id'], 'ledger-preparation-v1')
                first_write = transaction['writes'][0]
                self.assertEqual(first_write['staged_ref'], staged[0].name)
                self.assertEqual(staged[0].read_bytes(),
                                 (self.repo / '.ledger' / first_write['path']).read_bytes())
                files['native-transaction-record'] = files.pop(str(record.relative_to(roots[0])))
                files['native-selected-stage'] = files.pop(str(staged[0].relative_to(roots[0])))
                recovery_lock = '.ledger/.transactions/.recovery.advisory'
                if attempt == 0:
                    self.assertNotIn(recovery_lock, files)
                else:
                    self.assertEqual(files.pop(recovery_lock), 0)
                if retained is None:
                    retained = files
                self.assertEqual(files, retained)
                self.assertFalse((home / 'catalog.json').exists())
                self.assertFalse((roots[0] / 'legacy-archive').exists())
                self.assertFalse((roots[0] / '.ledger/unrelated').exists())
                self.assertEqual((self.repo / self.slot).read_bytes(), original)
        resumed = self.ensure()
        self.assertEqual(resumed['store_id'], identity['store_id'])
        self.assertEqual((Path(resumed['store_root']) / self.slot).read_bytes(), original)
        self.assertEqual(unrelated.stat().st_size, 3 * 1024**3)

    def test_one_hundred_catalog_failures_preserve_one_native_commit(self):
        self.capture(['--repo', str(self.repo)])
        original = (self.repo / self.slot).read_bytes()
        probe = Path(os.environ['LEDGER_PREPARATION_PROBE_BIN'])
        selected = None
        stable = None
        for attempt in range(100):
            with patch.dict(os.environ, {'LEDGER_PREPARATION_FAULT': 'catalog_association'}):
                result = subprocess.run(custody.owner_command(self.repo, self.definition, binary=probe),
                                        capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            value = json.loads(result.stdout)
            self.assertEqual(value['error_code'], 'AccessDenied')
            self.assertIn(value['preparation']['outcome'], ('prepared', 'covered'))
            self.assertEqual(value['storage_mutated'], True if attempt == 0 else None)
            identity = (value['store_id'], value['store_root'])
            if selected is None:
                selected = identity
            self.assertEqual(identity, selected)
            store = Path(value['store_root'])
            self.assertEqual((store / self.slot).read_bytes(), original)
            self.assertEqual((self.repo / self.slot).read_bytes(), original)
            self.assertFalse((self.root / 'home/catalog.json').exists())
            self.assertFalse((store / 'legacy-archive').exists())
            self.assertFalse(list((store / '.ledger').rglob('.ledger-dtx-stage-*')))
            snapshot = {str(p.relative_to(store)): p.read_bytes() for p in store.rglob('*') if p.is_file()}
            if attempt == 1:
                stable = snapshot
            elif attempt > 1:
                self.assertEqual(snapshot, stable)
        resumed = self.ensure()
        self.assertEqual((resumed['store_id'], resumed['store_root']), selected)
        expected = json.loads(self.packet.read_text())['record']
        projected = subprocess.run([self.binary, 'project', '--definition', str(self.definition),
            *resumed['native_args'], '--projection', 'basis', '--param', 'repository=' + expected['repository_id'],
            '--payload-only', '--format', 'json'], capture_output=True, timeout=15)
        self.assertEqual(projected.returncode, 0, projected.stdout + projected.stderr)
        records = json.loads(projected.stdout)
        self.assertEqual(len(records), 1)
        for key, value in expected.items():
            self.assertEqual(records[0][key], value)

    def test_native_verification_failure_retains_commit_and_retries_without_recapture(self):
        self.capture(['--repo', str(self.repo)])
        original = (self.repo / self.slot).read_bytes()
        probe = Path(os.environ['LEDGER_PREPARATION_PROBE_BIN'])
        with patch.dict(os.environ, {'LEDGER_PREPARATION_FAULT': 'verification'}):
            failed = subprocess.run(custody.owner_command(self.repo, self.definition, binary=probe), capture_output=True, timeout=20)
        self.assertEqual(failed.returncode, 3, failed.stdout + failed.stderr)
        value = json.loads(failed.stdout)
        self.assertEqual(value['preparation']['outcome'], 'committed-with-later-failure')
        self.assertTrue(value['storage_mutated'])
        store = Path(value['store_root'])
        self.assertEqual((store / self.slot).read_bytes(), original)
        stable = None
        for attempt in range(100):
            resumed = self.ensure()
            self.assertEqual(resumed['store_id'], value['store_id'])
            self.assertEqual((store / self.slot).read_bytes(), original)
            snapshot = {str(p.relative_to(store)): p.read_bytes() for p in store.rglob('*') if p.is_file()}
            if attempt == 0:
                stable = snapshot
            else:
                self.assertFalse(resumed['storage_mutated'])
                self.assertEqual(snapshot, stable)


if __name__ == '__main__':
    unittest.main()
