"""Owner framing/orchestration regressions; optional real Ledger conformance."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/import_retired_learnings.py'
spec = importlib.util.spec_from_file_location('retired_import', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def record(key='historical-id'):
    return {'id': key, 'captured_at': '2026-01-01T00:00:00Z', 'fingerprint': 'historical-fingerprint',
            'status': 'codify_now', 'learning': 'Preserve original evidence.', 'evidence': ['observed'],
            'application': 'Keep original records.', 'source': 'original session',
            'context': {'repo': '/original/repo', 'branch': 'old', 'paths': ['original.zig']}}


class FakeNative:
    def __init__(self, rows=None):
        self.rows = copy.deepcopy(rows or {})
        self.appended = []
        self.validated = []
        self.revision = 'sha256:' + '0' * 64
        self.on_validate = None
        self.fail_id = None

    def records(self):
        return copy.deepcopy(self.rows), self.revision

    def run(self, command, *args, packet=None, pure=False):
        if command == 'validate':
            self.validated.append(packet['learning_id'])
            if self.on_validate:
                self.on_validate()
            return {'schema': 'ledger-validation-result/v1', 'valid': packet['record'].get('learning') is not None}
        if command == 'doctor':
            return {'schema': 'ledger-doctor-result/v1', 'healthy': True, 'pending_transactions': 0, 'storage_mutated': False}
        if command != 'transact':
            raise AssertionError(command)
        if ((self.revision is not None and f'import_revision={self.revision}' not in args)
                or packet['learning_id'] == self.fail_id):
            raise module.ImportErrorDetail('stale revision')
        key = packet['learning_id']
        self.rows[key] = copy.deepcopy(packet['record'])
        self.appended.append(key)
        self.revision = 'sha256:' + hashlib.sha256(module.canonical(self.rows).encode()).hexdigest()
        return {'schema': 'ledger-transaction-result/v1', 'valid': True,
                'effects': [{'revision_after': self.revision, 'result': 'appended'}]}


class FramingTests(unittest.TestCase):
    def test_multiline_unicode_exact_fields_and_offsets(self):
        row = record(); row['learning'] = 'λ → café'
        raw = b' \n' + json.dumps(row, indent=2, ensure_ascii=False).encode() + b'\n'
        rows, receipt = module.frame(raw)
        self.assertEqual(rows[0]['record'], row)
        self.assertEqual(rows[0]['import_source']['byte_start'], '2')
        self.assertEqual(rows[0]['import_source']['byte_end'], str(len(raw)-1))
        self.assertEqual(receipt['records'], 1)

    def test_duplicate_keys_rejected(self):
        with self.assertRaises(module.ImportErrorDetail):
            module.frame(b'{"id":"a","id":"b"}')

    def test_duplicate_ids_rejected(self):
        with self.assertRaises(module.ImportErrorDetail):
            module.frame((json.dumps(record())+'\n'+json.dumps(record())).encode())

    def test_malformed_identified_record_is_not_skipped(self):
        with self.assertRaises(module.ImportErrorDetail):
            module.frame(json.dumps(record()).encode() + b'\n{"id":"broken",')

    def test_anonymous_fragment_requires_explicit_control(self):
        with self.assertRaises(module.ImportErrorDetail):
            module.frame(b'orphan bytes')

    def test_no_nan_or_infinity(self):
        for token in (b'NaN', b'Infinity', b'-Infinity'):
            with self.assertRaises(module.ImportErrorDetail):
                module.frame(b'{"id":"x","value":'+token+b'}')

    def test_missing_context_is_not_invented(self):
        row = record(); del row['context']
        packets, _ = module.frame(json.dumps(row).encode())
        self.assertNotIn('context', packets[0]['record'])

    def test_legacy_paths_remain_untruncated(self):
        row = record(); row['context']['paths'] = [f'path-{n}' for n in range(179)]
        packets, _ = module.frame(json.dumps(row).encode())
        self.assertEqual(packets[0]['record'], row)

    def test_explicit_quote_repair_and_fragment_preservation(self):
        row = record(); row['tags'] = ['historical']
        raw = json.dumps(row).encode().replace(b'"tags":', b'tags":') + b'\nORPHAN'
        start = raw.index(b'tags":')
        control = {'source_sha256': hashlib.sha256(raw).hexdigest(), 'spans': [
            {'start': start, 'end': start+6, 'kind': 'missing-tags-quote'},
            {'start': len(raw)-6, 'end': len(raw), 'kind': 'anonymous-fragment'}]}
        packets, receipt = module.frame(raw, control)
        self.assertEqual(packets[0]['record'], row)
        self.assertEqual(packets[0]['import_source']['byte_end'], str(len(raw)-7))
        self.assertEqual(receipt['retained_fragments'][0]['base64'], 'T1JQSEFO')

    def test_identified_fragment_cannot_be_discarded(self):
        raw = b'{"id":"lost"}'
        control = {'source_sha256': hashlib.sha256(raw).hexdigest(), 'spans': [
            {'start': 0, 'end': len(raw), 'kind': 'anonymous-fragment'}]}
        with self.assertRaises(module.ImportErrorDetail):
            module.frame(raw, control)

    def test_escaped_identity_key_is_not_an_anonymous_fragment(self):
        raw = b'{"i\\u0064":"lost"}'
        control = {'source_sha256': hashlib.sha256(raw).hexdigest(), 'spans': [
            {'start': 0, 'end': len(raw), 'kind': 'anonymous-fragment'}]}
        with self.assertRaises(module.ImportErrorDetail):
            module.frame(raw, control)

    def test_control_bound_to_exact_source(self):
        with self.assertRaises(module.ImportErrorDetail):
            module.frame(b'{}', {'source_sha256': '0'*64, 'spans': []})

    def test_no_arbitrary_value_repair(self):
        raw = b'{"id":"x"}'
        with self.assertRaises(module.ImportErrorDetail):
            module.frame(raw, {'source_sha256': hashlib.sha256(raw).hexdigest(), 'spans': [
                {'start': 7, 'end': 8, 'kind': 'missing-tags-quote'}]})

    def test_fragment_cannot_remove_a_field_from_a_record(self):
        raw = b'{"id":"x", "context":{}, "learning":"original"}'
        start = raw.index(b'"context"')
        end = raw.index(b'"learning"')
        control = {'source_sha256': hashlib.sha256(raw).hexdigest(), 'spans': [
            {'start': start, 'end': end, 'kind': 'anonymous-fragment'}]}
        with self.assertRaisesRegex(module.ImportErrorDetail, 'between records'):
            module.frame(raw, control)

    def test_json_type_equality_not_python_coercion(self):
        self.assertNotEqual(module.canonical({'x': True}), module.canonical({'x': 1}))


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name).resolve() / 'retired.jsonl'
        self.source.write_text(json.dumps(record())+'\n')
        self.native = FakeNative()

    def test_plan_has_no_appends(self):
        result = module.import_sources(self.native, [self.source])
        self.assertEqual(result['would_append'], 1)
        self.assertEqual(self.native.appended, [])
        self.assertFalse(result['storage_mutated'])

    def test_import_and_idempotent_rerun_preserve_bytes(self):
        before = self.source.read_bytes()
        first = module.import_sources(self.native, [self.source], apply=True)
        second = module.import_sources(self.native, [self.source], apply=True)
        self.assertEqual(first['appended'], 1)
        self.assertEqual(second['appended'], 0)
        self.assertEqual(second['already_present'], 1)
        self.assertEqual(self.source.read_bytes(), before)
        self.assertEqual(self.native.rows['historical-id'], record())

    def test_preflights_all_ids_before_first_append(self):
        self.source.write_text(json.dumps(record('new'))+'\n'+json.dumps(record('conflict'))+'\n')
        self.native.rows['conflict'] = {**record('conflict'), 'learning': 'different'}
        with self.assertRaises(module.ImportErrorDetail):
            module.import_sources(self.native, [self.source], apply=True)
        self.assertEqual(self.native.appended, [])

    def test_validates_complete_packet_set_before_append(self):
        bad = record('bad'); del bad['learning']
        self.source.write_text(json.dumps(record('new'))+'\n'+json.dumps(bad)+'\n')
        with self.assertRaises(module.ImportErrorDetail):
            module.import_sources(self.native, [self.source], apply=True)
        self.assertEqual(self.native.appended, [])

    def test_equal_copies_across_sources_import_once(self):
        other = self.source.with_name('other.jsonl'); other.write_bytes(self.source.read_bytes())
        result = module.import_sources(self.native, [self.source, other], apply=True)
        self.assertEqual(result['appended'], 1)
        self.assertEqual(len(result['sources']), 2)

    def test_divergent_sources_block_before_mutation(self):
        other = self.source.with_name('other.jsonl'); other.write_text(json.dumps({**record(), 'source': 'other'}))
        with self.assertRaises(module.ImportErrorDetail):
            module.import_sources(self.native, [self.source, other], apply=True)
        self.assertEqual(self.native.appended, [])

    def test_changed_source_blocks_before_append(self):
        self.native.on_validate = lambda: self.source.write_text(json.dumps(record('changed')))
        with self.assertRaises(module.ImportErrorDetail):
            module.import_sources(self.native, [self.source], apply=True)
        self.assertEqual(self.native.appended, [])

    def test_stale_revision_stops_and_rerun_reconciles(self):
        self.source.write_text(json.dumps(record('a'))+'\n'+json.dumps(record('b'))+'\n')
        self.native.fail_id = 'b'
        with self.assertRaises(module.ImportErrorDetail):
            module.import_sources(self.native, [self.source], apply=True)
        self.assertEqual(self.native.appended, ['a'])
        self.native.fail_id = None
        result = module.import_sources(self.native, [self.source], apply=True)
        self.assertEqual(result['appended'], 1)
        self.assertEqual(self.native.appended, ['a', 'b'])

    def test_unrelated_current_records_preserved(self):
        current = record('current'); self.native.rows['current'] = current
        module.import_sources(self.native, [self.source], apply=True)
        self.assertEqual(self.native.rows['current'], current)

    def test_absent_store_requires_explicit_initialization_authority(self):
        self.native.revision = None
        with self.assertRaisesRegex(module.ImportErrorDetail, 'initialize_empty'):
            module.import_sources(self.native, [self.source], apply=True)
        self.assertEqual(self.native.appended, [])
        result = module.import_sources(self.native, [self.source], apply=True, initialize_empty=True)
        self.assertEqual(result['appended'], 1)

    def test_native_invalid_transaction_is_not_claimed_as_success(self):
        run = self.native.run
        def invalid(command, *args, **kwargs):
            result = run(command, *args, **kwargs)
            if command == 'transact':
                result['valid'] = False
            return result
        self.native.run = invalid
        with self.assertRaisesRegex(module.ImportErrorDetail, 'receipt'):
            module.import_sources(self.native, [self.source], apply=True)

    def test_symlink_source_rejected(self):
        linked = self.source.with_name('link'); linked.symlink_to(self.source)
        with self.assertRaises(module.ImportErrorDetail):
            module.import_sources(self.native, [linked], apply=True)


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.definition = json.loads(module.DEFINITION.read_text())

    def test_current_event_remains_version_one_and_strict(self):
        current = self.definition['shape']['documents']['event']['tagged']['variants'][0]['node']
        self.assertEqual(current['fields']['v'], {'enum': [1]})
        self.assertIn('regex', current['fields']['record']['fields']['id'])
        self.assertNotIn('optional', current['fields']['record']['fields']['context'])
        self.assertEqual(current['fields']['record']['fields']['context']['fields']['paths']['array']['max'], 128)

    def test_historical_input_has_separate_version_and_laws(self):
        historic = self.definition['shape']['documents']['historical']
        self.assertEqual(historic['fields']['v'], {'enum': [0]})
        self.assertEqual(historic['laws'][0][1]['input'], 'historical')
        self.assertTrue(historic['fields']['record']['fields']['context']['optional'])

    def test_import_has_native_revision_and_retry_controls(self):
        effect = self.definition['operations']['import-record']['effects'][0]
        self.assertEqual(effect['expected_revision_param'], 'import_revision')
        self.assertEqual(effect['idempotency_param'], 'import_key')
        self.assertEqual(effect['input'], 'historical')


@unittest.skipUnless(os.environ.get('LEDGER_BIN'), 'Set LEDGER_BIN for native conformance; mocks do not qualify native custody')
class NativeConformance(unittest.TestCase):
    def test_local_recovery_archives_survive_pr_reads_and_new_writes(self):
        """Exercise the installed recovery protocol, not a guessed v0 envelope."""
        import subprocess
        legacy = Path(__file__).with_name('fixtures') / 'local-recovery-protocol.json'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve(); (root / '.ledger').mkdir()
            identity = 'b' * 32
            (root / '.ledger-root.json').write_text(json.dumps({
                'schema': 'ledger-storage-root/v1', 'store_id': identity}))
            selector = ['--store-root', str(root), '--store-id', identity]

            def transaction(definition, operation, input_name, value, *parameters):
                proc = subprocess.run([os.environ['LEDGER_BIN'], 'transact',
                    '--definition', str(definition), *selector, '--operation', operation,
                    '--input', input_name + '=-', *parameters, '--format', 'json'],
                    input=json.dumps(value).encode(), capture_output=True)
                self.assertEqual(proc.returncode, 0, proc.stdout.decode(errors='replace'))
                return json.loads(proc.stdout)['effects'][0]['revision_after']

            submission = record()
            for key in ('id', 'fingerprint', 'captured_at'):
                del submission[key]
            revision = transaction(legacy, 'capture', 'submission', {'record': submission})
            rows = [record('lrn-20260101T000000Z-descriptive'),
                    record('lrn-20260101T000000Z-long-paths'),
                    record('lrn-20260101T000000Z-no-context')]
            rows[1]['context']['paths'] = [f'path-{n}' for n in range(179)]
            del rows[2]['context']
            for index, row in enumerate(rows):
                packet = {'record': row, 'provenance': {'sha256': 'sha256:' + 'a' * 64,
                    'record_index': index, 'start_byte': index * 100,
                    'end_byte': (index + 1) * 100, 'repairs': []}}
                revision = transaction(legacy, 'import-record', 'historical', packet,
                    '--param', f'import_key=legacy-{index}',
                    '--param', 'expected_revision=' + revision)
            # Hash custody files to prove reads and the no-op rerun preserve all
            # existing event bytes and archived definition/revision material.
            def snapshot():
                return {str(p.relative_to(root)): p.read_bytes()
                        for p in (root / '.ledger').rglob('*') if p.is_file()}

            before = snapshot()
            native = module.Native(os.environ['LEDGER_BIN'], module.DEFINITION, selector)
            stored, witnessed = native.records()
            self.assertEqual(witnessed, revision)
            self.assertEqual(len(stored), 4)
            for row in rows:
                self.assertEqual(stored[row['id']], row)
            self.assertTrue(native.run('doctor')['healthy'])
            source = root / 'retired.jsonl'
            source.write_text('\n'.join(json.dumps(row) for row in rows) + '\n')
            rerun = module.import_sources(native, [source], apply=True)
            self.assertEqual(rerun['appended'], 0)
            self.assertEqual(rerun['already_present'], 3)
            self.assertEqual(snapshot(), before)
            extra = record('new-pr-import')
            source.write_text(json.dumps(extra))
            self.assertEqual(module.import_sources(native, [source], apply=True)['appended'], 1)
            submission['learning'] = 'A new capture after upgrading the owner definition.'
            transaction(module.DEFINITION, 'capture', 'submission', {'record': submission})
            after, _ = native.records()
            self.assertEqual(len(after), 6)
            for key, row in stored.items():
                self.assertEqual(after[key], row)
            self.assertEqual(after[extra['id']], extra)
            self.assertTrue(native.run('doctor')['healthy'])
            self.assertTrue((root / '.ledger/learnings/events.jsonl').read_bytes().startswith(
                before['.ledger/learnings/events.jsonl']))
            for name, contents in before.items():
                if name.startswith('.ledger/.definitions/'):
                    self.assertEqual((root / name).read_bytes(), contents)

    def test_historical_import_current_capture_and_rerun(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve(); (root / '.ledger').mkdir()
            identity = 'a' * 32
            (root / '.ledger-root.json').write_text(json.dumps({'schema': 'ledger-storage-root/v1', 'store_id': identity}))
            source = root / 'retired.jsonl'
            rows = [record('descriptive-id'), record('paths-id'), record('no-context-id')]
            rows[1]['context']['paths'] = [f'path-{n}' for n in range(179)]
            del rows[2]['context']
            source.write_text('\n'.join(json.dumps(row) for row in rows)+'\n')
            native = module.Native(os.environ['LEDGER_BIN'], module.DEFINITION, ['--store-root', str(root), '--store-id', identity])
            result = module.import_sources(native, [source], apply=True, initialize_empty=True)
            self.assertEqual(result['appended'], 3)
            self.assertEqual(module.import_sources(native, [source], apply=True)['appended'], 0)
            stored, _ = native.records()
            self.assertEqual(stored, {row['id']: row for row in rows})
            packet = module.frame(source.read_bytes())[0][0]
            packet['v'] = 1; packet['event'] = 'learning.capture'; del packet['import_source']
            import subprocess
            proc = subprocess.run([os.environ['LEDGER_BIN'], 'validate', '--definition', str(module.DEFINITION),
                                   '--input', 'event=-', '--format', 'json'], input=json.dumps(packet).encode(), capture_output=True)
            self.assertNotEqual(proc.returncode, 0)
            submission = record()
            for key in ('id', 'fingerprint', 'captured_at'):
                del submission[key]
            proc = subprocess.run([os.environ['LEDGER_BIN'], 'transact', '--definition', str(module.DEFINITION),
                '--store-root', str(root), '--store-id', identity, '--operation', 'capture',
                '--input', 'submission=-', '--format', 'json'],
                input=json.dumps({'record': submission}).encode(), capture_output=True)
            self.assertEqual(proc.returncode, 0, proc.stdout.decode(errors='replace'))
            stored, revision = native.records()
            self.assertEqual(len(stored), 4)
            current = next(row for key, row in stored.items() if key not in {row['id'] for row in rows})
            self.assertRegex(current['id'], r'^lrn-[0-9]+T[0-9]+Z-[a-f0-9]+$')
            self.assertEqual(module.import_sources(native, [source], apply=True)['appended'], 0)
            # Stale revision and conflicting retry keys must be rejected by native
            # custody, independently of the constructor's preflight.
            extra = root / 'extra.jsonl'; extra.write_text(json.dumps(record('fourth-id')))
            extra_packet = module.frame(extra.read_bytes())[0][0]
            with self.assertRaises(module.ImportErrorDetail):
                native.run('transact', '--operation', 'import-record', '--param', 'import_key=stale-probe',
                    '--param', 'import_revision=sha256:' + '0'*64, packet=extra_packet)
            original_packet = module.frame(source.read_bytes())[0][1]
            original_packet['record']['learning'] = 'conflicting input'
            with self.assertRaises(module.ImportErrorDetail):
                native.run('transact', '--operation', 'import-record', '--param',
                    'import_key=retired-' + hashlib.sha256(rows[1]['id'].encode()).hexdigest(),
                    '--param', 'import_revision=' + revision, packet=original_packet)
            self.assertEqual(native.records()[0], stored)


if __name__ == '__main__':
    unittest.main()
