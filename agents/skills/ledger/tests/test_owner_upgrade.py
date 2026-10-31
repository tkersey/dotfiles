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


class PreparationAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.home = self.root / 'home'
        environment = patch.dict(os.environ, {'LEDGER_HOME': str(self.home)})
        environment.start()
        self.addCleanup(environment.stop)
        self.ctx = custody.load_module(SKILLS / 'ledger/scripts/ledger_context.py')
        self.definition = SKILLS / 'review-fold/definitions/ledger/counterexample-corpus.json'
        loader = patch.object(custody, 'load_module', return_value=self.ctx)
        loader.start()
        self.addCleanup(loader.stop)
        runtime = patch.object(custody, 'preparation_runtime')
        runtime.start()
        self.addCleanup(runtime.stop)

    def prepare(self, **kwargs):
        return custody.migrate_owner(self.repo, self.definition, **kwargs)

    def receipt(self, outcome='prepared'):
        return {'schema': 'ledger-preparation-result/v1', 'outcome': outcome,
                'storage_mutated': outcome == 'prepared', 'authority_granted': False}

    def test_genuine_new_owner_uses_existing_initialization_without_transfer(self):
        with patch.object(custody, 'prepare_native', side_effect=AssertionError('unnecessary transfer')):
            context = custody.owner_context(self.repo, self.definition, maintain=True)
        self.assertEqual(self.ctx.resolve(self.repo)['store_id'], context['store_id'])
        self.assertFalse((self.home / 'preparations').exists())
        self.assertFalse((self.repo / '.ledger').exists())

    def test_unrelated_local_evidence_cannot_take_fresh_initialization_path(self):
        evidence = self.repo / '.ledger/cas/evidence'
        evidence.parent.mkdir(parents=True)
        evidence.write_bytes(b'not disposable')
        with patch.object(custody, 'prepare_native', side_effect=custody.MigrationError('needs native preparation')):
            with self.assertRaisesRegex(custody.MigrationError, 'needs native preparation'):
                custody.owner_context(self.repo, self.definition, maintain=True)
        self.assertFalse((self.home / 'catalog.json').exists())
        self.assertEqual(evidence.read_bytes(), b'not disposable')

    def test_one_hundred_failed_preparations_keep_one_target_without_copying_unrelated_payload(self):
        unrelated = self.repo / '.ledger/cas/oversized'
        unrelated.parent.mkdir(parents=True)
        with unrelated.open('wb') as handle:
            handle.truncate(custody.MAX_BYTES + 1)
        selected = self.repo / '.ledger/review-fold/counterexamples/events.jsonl'
        selected.parent.mkdir(parents=True)
        selected.write_bytes(b'original selected evidence\n')
        targets = []

        def failed(binary, owner, context, sources, **kwargs):
            targets.append((context['store_id'], context['store_root']))
            self.assertIn(str(self.repo), sources)
            self.assertFalse((self.home / 'catalog.json').exists())
            with self.ctx.catalog_lock(self.home):
                pass
            raise custody.MigrationError('native fixture failure')

        with patch.object(custody, 'prepare_native', side_effect=failed), \
             patch.object(custody, 'inventory', side_effect=AssertionError('broad inventory')), \
             patch.object(custody, 'copy_inventory', side_effect=AssertionError('broad copying')):
            for _ in range(100):
                with self.assertRaisesRegex(custody.MigrationError, 'native fixture failure'):
                    self.prepare()
        self.assertEqual(len(set(targets)), 1)
        self.assertEqual(len(list((self.home / 'repos').iterdir())), 1)
        self.assertEqual(len(list((self.home / 'preparations').glob('*/registration.json'))), 1)
        self.assertFalse(list(self.home.rglob('legacy-archive')))
        self.assertEqual(selected.read_bytes(), b'original selected evidence\n')
        self.assertEqual(unrelated.stat().st_size, custody.MAX_BYTES + 1)

    def test_catalog_failure_retries_native_with_same_committed_identity(self):
        targets = []

        def prepared(binary, owner, context, sources, **kwargs):
            targets.append((context['store_id'], context['store_root']))
            return self.receipt('prepared' if len(targets) == 1 else 'covered')

        with patch.object(custody, 'prepare_native', side_effect=prepared), \
             patch.object(custody, 'healthy', return_value={'healthy': True, 'preparation_pending': False}):
            with patch.object(self.ctx, 'register_root', side_effect=OSError('catalog unavailable')):
                with self.assertRaisesRegex(custody.MigrationError, 'Preparation committed') as caught:
                    self.prepare()
            self.assertEqual(caught.exception.preparation['outcome'], 'prepared')
            self.assertTrue(Path(caught.exception.context['store_root']).is_dir())
            result = self.prepare()
        self.assertEqual(len(set(targets)), 1)
        self.assertEqual(result['store_id'], targets[0][0])
        self.assertEqual(result['preparation']['outcome'], 'covered')
        self.assertEqual(self.ctx.resolve(self.repo)['store_id'], result['store_id'])

    def test_current_learnings_does_not_require_retired_import(self):
        self.definition = SKILLS / 'learnings/definitions/ledger/learnings-protocol.json'
        with patch.object(custody, 'prepare_native', return_value=self.receipt()), \
             patch.object(custody, 'healthy', return_value={'healthy': True, 'preparation_pending': False}):
            result = self.prepare()
        self.assertEqual(result['preparation']['outcome'], 'prepared')

    def test_actual_retired_evidence_blocks_before_initialization(self):
        self.definition = SKILLS / 'learnings/definitions/ledger/learnings-protocol.json'
        (self.repo / '.learnings.jsonl').write_bytes(b'retired evidence\n')
        with patch.object(custody, 'prepare_native') as native:
            with self.assertRaisesRegex(custody.MigrationError, 'Retired-format evidence'):
                self.prepare()
        native.assert_not_called()
        self.assertFalse(self.home.exists())

    def test_broken_git_is_not_plain_workspace_initialization(self):
        (self.repo / '.git').write_text('gitdir: /missing/fixture-git\n')
        with self.assertRaisesRegex(custody.MigrationError, 'Git family coverage'):
            self.prepare()
        self.assertFalse(self.home.exists())

    def test_unregistered_root_is_not_replaced_by_new_owner_identity(self):
        orphan = self.home / 'repos' / ('b' * 32)
        (orphan / '.ledger').mkdir(parents=True)
        self.ctx.write_json(orphan / self.ctx.MARKER,
                            {'schema': self.ctx.MARKER_SCHEMA, 'store_id': 'b' * 32})
        with patch.object(custody, 'prepare_native') as prepare:
            with self.assertRaisesRegex(custody.MigrationError, 'Unregistered custody exists'):
                self.prepare()
        prepare.assert_not_called()
        self.assertEqual(list((self.home / 'repos').iterdir()), [orphan])

    def test_unknown_native_outcome_preserves_result_and_target(self):
        owner = custody.selected_owner(self.definition, self.ctx)
        context = {'native_args': ['--store-root', '/fixture', '--store-id', 'a' * 32]}
        expected = self.receipt('unknown')
        with patch.object(custody, 'native', return_value=expected):
            with self.assertRaises(custody.MigrationError) as caught:
                custody.prepare_native('ledger', owner, context, ['--source-root', str(self.repo)])
        self.assertEqual(caught.exception.preparation, expected)
        self.assertEqual(caught.exception.context, context)

    def test_quiescence_is_only_forwarded_when_explicit(self):
        owner = custody.selected_owner(self.definition, self.ctx)
        context = {'native_args': []}
        with patch.object(custody, 'native', return_value=self.receipt()) as native:
            custody.prepare_native('ledger', owner, context, [])
            self.assertNotIn('--confirm-no-legacy-writers', native.call_args.args)
            custody.prepare_native('ledger', owner, context, [], confirm_no_writers=True)
            self.assertIn('--confirm-no-legacy-writers', native.call_args.args)

    def test_native_busy_wait_is_bounded(self):
        owner = custody.selected_owner(self.definition, self.ctx)
        busy = subprocess.CompletedProcess([], 1, json.dumps(self.receipt('busy')).encode(), b'')
        with patch.object(custody.subprocess, 'run', return_value=busy), \
             patch.object(custody.time, 'monotonic', side_effect=[0, custody.BUSY_WAIT_SECONDS + 1]):
            with self.assertRaisesRegex(custody.MigrationError, 'remained busy'):
                custody.native('ledger', owner, [], 'prepare', wait_busy=True)

    def segmented_fixture(self):
        skills = self.root / 'skills'
        owner = skills / 'fixture'
        owner.mkdir(parents=True)
        definition = owner / 'definition.json'
        definition.write_text(json.dumps({'owner': 'fixture', 'storage': {'slots': {'events': {
            'path': 'fixture/events.jsonl', 'kind': 'event-log', 'codec': 'jsonl', 'layout': 'segmented'}}}}))
        (owner / 'migration.json').write_text(json.dumps({'schema': 'ledger-owner-migration/v1',
            'definition': 'definition.json', 'retired_sources': [], 'importer': None}))
        return skills, definition

    def test_healthy_segmented_access_never_prepares_or_scans_archives(self):
        skills, definition = self.segmented_fixture()
        context = self.ctx.resolve(self.repo, initialize=True)
        doctor = {'healthy': True, 'pending_transactions': 0, 'preparation_pending': False,
                  'slots': [{'status': 'healthy'}]}
        with patch.object(custody, 'native', return_value=doctor), \
             patch.object(custody, 'archive_entries', side_effect=AssertionError('archive scan')), \
             patch.object(custody, 'prepare_native', side_effect=AssertionError('preparation')):
            selected = custody.owner_context(self.repo, definition, maintain=True, skill_root=skills)
        self.assertEqual(selected['store_id'], context['store_id'])

    def test_segmented_preparation_is_unsupported_before_initialization(self):
        skills, definition = self.segmented_fixture()
        with self.assertRaises(custody.MigrationError) as caught:
            custody.migrate_owner(self.repo, definition, skill_root=skills)
        self.assertEqual(caught.exception.preparation['outcome'], 'unsupported')
        self.assertFalse(self.home.exists())

    def test_pending_preparation_bypasses_fast_path_without_archive_discovery(self):
        context = self.ctx.resolve(self.repo, initialize=True)
        doctor = {'healthy': True, 'pending_transactions': 0, 'preparation_pending': True,
                  'slots': [{'status': 'healthy'}]}
        with patch.object(custody, 'native', return_value=doctor), \
             patch.object(custody, 'archive_entries', side_effect=AssertionError('archive scan')), \
             patch.object(custody, 'migrate_owner', return_value=context) as prepare:
            custody.owner_context(self.repo, self.definition, maintain=True)
        self.assertIs(prepare.call_args.kwargs['discover_archives'], False)

    def test_catalog_identity_cannot_replace_unresolved_pending_target(self):
        with patch.object(custody, 'prepare_native', side_effect=custody.MigrationError('fixture failure')):
            with self.assertRaisesRegex(custody.MigrationError, 'fixture failure'):
                self.prepare()
        replacement = self.root / 'replacement'
        (replacement / '.ledger').mkdir(parents=True)
        self.ctx.write_json(replacement / self.ctx.MARKER,
                            {'schema': self.ctx.MARKER_SCHEMA, 'store_id': 'a' * 32})
        self.ctx.register_root(replacement, 'a' * 32, self.repo)
        with patch.object(custody, 'prepare_native') as prepare:
            with self.assertRaisesRegex(custody.MigrationError, 'Pending custody conflicts'):
                self.prepare()
        prepare.assert_not_called()

    def test_pending_target_is_shared_across_linked_worktree_retries(self):
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)
        subprocess.run(['git', '-C', str(self.repo), '-c', 'user.name=Fixture', '-c',
                        'user.email=fixture@example.test', 'commit', '--allow-empty', '-qm', 'fixture'], check=True)
        other = self.root / 'other'
        subprocess.run(['git', '-C', str(self.repo), 'worktree', 'add', '-q', '-b', 'other', str(other)], check=True)
        identities = []

        def failed(binary, owner, context, sources, **kwargs):
            identities.append(context['store_id'])
            raise custody.MigrationError('fixture failure')

        with patch.object(custody, 'prepare_native', side_effect=failed):
            for repo in (self.repo, other):
                with self.assertRaisesRegex(custody.MigrationError, 'fixture failure'):
                    custody.migrate_owner(repo, self.definition)
        self.assertEqual(len(set(identities)), 1)


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
        run = subprocess.run
        exit_codes = []

        def witnessed(arguments, **kwargs):
            result = run(arguments, **kwargs)
            if arguments[:2] == [str(probe), 'prepare']:
                exit_codes.append(result.returncode)
            return result

        with patch.dict(os.environ, {'LEDGER_PREPARATION_FAULT': 'publication'}), \
             patch.object(custody.subprocess, 'run', side_effect=witnessed):
            with self.assertRaises(custody.MigrationError) as caught:
                custody.owner_context(self.repo, self.definition, maintain=True, binary=str(probe))
        self.assertEqual(exit_codes, [99])
        self.assertEqual(caught.exception.context['store_id'], registered['store_id'])
        self.assertEqual(caught.exception.preparation['outcome'], 'unknown')
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
        with self.assertRaisesRegex(custody.MigrationError, 'read-only'):
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


if __name__ == '__main__':
    unittest.main()
