"""Behavioral checks for the installed history definitions using disposable stores.

Run with LEDGER_BIN set to a native Ledger >=1.5.0 executable. No live history or
memory is read or written; mocks cannot establish these protocol guarantees.
"""
import copy
import datetime
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest


SKILLS = Path(__file__).resolve().parents[2]
LEARNINGS = SKILLS / 'learnings/definitions/ledger/learnings-protocol.json'
NEGATIVE = SKILLS / 'negative-ledger/definitions/ledger/negative-evidence-protocol.json'
PREVIOUS = Path(__file__).with_name('fixtures') / 'pre-personal-history'


class NativeHistory(unittest.TestCase):
    def setUp(self):
        if not os.environ.get('LEDGER_BIN'):
            self.skipTest('Set LEDGER_BIN; these checks require native storage')
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.store_id = 'a' * 32
        (self.root / '.ledger').mkdir()
        (self.root / '.ledger-root.json').write_text(json.dumps({
            'schema': 'ledger-storage-root/v1', 'store_id': self.store_id}))
        self.selector = ['--store-root', str(self.root), '--store-id', self.store_id]
        self.environment = dict(os.environ, LEDGER_CACHE_DIR=str(self.root / 'cache'))

    def native(self, definition, command, *arguments, packet=None, code=0):
        completed = subprocess.run([
            os.environ['LEDGER_BIN'], command, '--definition', str(definition),
            *self.selector, *arguments, '--format', 'json'],
            input=None if packet is None else json.dumps(packet).encode(),
            capture_output=True, cwd=self.root, env=self.environment)
        self.assertEqual(completed.returncode, code,
                         (completed.stdout + completed.stderr).decode(errors='replace'))
        return json.loads(completed.stdout)

    def project(self, definition, name, **parameters):
        args = ['--projection', name]
        for key, value in parameters.items():
            args += ['--param', f'{key}={value}']
        return self.native(definition, 'project', *args)['data']

    def check_definition(self, definition):
        completed = subprocess.run([
            os.environ['LEDGER_BIN'], 'definition', 'check', '--definition', str(definition),
            '--format', 'json'], capture_output=True, cwd=self.root, env=self.environment)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertTrue(json.loads(completed.stdout)['valid'])

    def custody(self):
        return {str(path.relative_to(self.root)): path.read_bytes()
                for path in (self.root / '.ledger').rglob('*') if path.is_file()}

    def assert_archives_preserved(self, before):
        for path, contents in before.items():
            if path.startswith('.ledger/.definitions/'):
                self.assertEqual((self.root / path).read_bytes(), contents)


class NegativeHistoryTests(NativeHistory):
    def record(self, *, route='world-system-link-v1:component-admission-repeated-body-evaluation',
               artifact='a' * 40, status='active'):
        return {
            'record_version': 'NER-v2', 'kind': 'realization_route',
            'repository_id': 'ledger-repository:' + self.store_id,
            'status': status, 'artifact_state_id': artifact,
            'route_id': route, 'exclusion_scope': 'route',
            'hypothesis': 'Repeated component admission in every body accessor is acceptable.',
            'attempted_change': 'Evaluate the admission body again on every component lookup.',
            'observed_outcome': 'The fixture counted three admissions for one component.',
            'failure_class': 'local-regression', 'confidence': 'high',
            'source_refs': [{'kind': 'test', 'ref': 'fixture:component-admission-count',
                             'summary': 'Expected one admission; observed three.'}],
            'falsifying_evidence': ['One component was admitted three times.'],
            'exclusion_rule': 'Do not repeat admission in the body accessor.',
            'applicability_conditions': ['The accessor re-evaluates admission on every call.'],
            'reopening_criteria': [{'id': 'admission-memoized',
                                   'condition': 'The accessor carries an already admitted projection.'}],
            'next_search_hint': 'Admit each component once and carry its authenticated projection.',
            'applicable_paths': ['src/component.zig'],
        }

    def capture(self, record, key, *, code=0):
        return self.native(NEGATIVE, 'transact', '--operation', 'capture',
                           '--param', 'capture_key=' + key, '--input', 'capture=-',
                           packet={'record': record}, code=code)

    def gate(self, *, route, artifact='a' * 40, code=0):
        return self.native(NEGATIVE, 'project', '--projection', 'route-gate',
                           '--param', 'identity=' + route, '--param', 'artifact=' + artifact,
                           code=code)

    def test_mechanism_query_recovers_record_after_route_label_miss(self):
        original = self.record()
        self.capture(original, 'finding-admission')
        # The historical failure: a different label misses the exact gate.
        self.assertEqual(self.gate(route='admit-components-in-body')['data'], [])
        candidates = self.project(NEGATIVE, 'route-candidates',
                                  query='component admission repeated body evaluation', limit=8)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]['record']['route_id'], original['route_id'])
        self.assertEqual(candidates[0]['record']['source_refs'], original['source_refs'])
        # Confirming route identity, not lexical resemblance, enables the exact gate.
        self.assertEqual(len(self.gate(route=original['route_id'], code=2)['data']), 1)

    def test_similar_candidate_does_not_ban_different_route_or_artifact(self):
        original = self.record()
        self.capture(original, 'finding-admission')
        candidates = self.project(NEGATIVE, 'route-candidates',
                                  query='component admission memoized body', limit=8)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(self.gate(route='admit-once-carry-projection')['data'], [])
        self.assertEqual(self.gate(route=original['route_id'], artifact='b' * 40)['data'], [])

    def test_candidate_lifecycle_does_not_become_exclusion_authority(self):
        original = self.record(status='need-evidence')
        self.capture(original, 'incomplete-witness')
        candidates = self.project(NEGATIVE, 'route-candidates', query='component admission', limit=8)
        self.assertEqual(candidates[0]['status'], 'need-evidence')
        self.assertEqual(self.gate(route=original['route_id'])['data'], [])
        self.assertEqual(self.project(NEGATIVE, 'route-candidates', query='unrelated-quartz', limit=8), [])

    def test_retry_preserves_identity_after_other_appends_and_rejects_changed_input(self):
        original = self.record()
        first = self.capture(original, 'root-one-finding-one')
        self.assertEqual(first['effects'][0]['result'], 'appended')
        self.capture(self.record(route='different-route'), 'root-two-finding-one')
        before = self.project(NEGATIVE, 'current-records', limit=20)
        log = self.root / '.ledger/negative-ledger/events.jsonl'
        original_bytes = log.read_bytes()
        retry = self.capture(original, 'root-one-finding-one')
        self.assertEqual(retry['effects'][0]['result'], 'idempotent')
        self.assertEqual(self.project(NEGATIVE, 'current-records', limit=20), before)
        self.assertEqual(log.read_bytes(), original_bytes)
        changed = copy.deepcopy(original)
        changed['observed_outcome'] = 'Different evidence belongs to another operation.'
        conflict = self.capture(changed, 'root-one-finding-one', code=2)
        self.assertIn('IdempotencyConflict', json.dumps(conflict))
        self.assertEqual(log.read_bytes(), original_bytes)

    def test_missing_retry_key_is_rejected_without_capture(self):
        result = self.native(NEGATIVE, 'transact', '--operation', 'capture',
                             '--input', 'capture=-', packet={'record': self.record()}, code=2)
        self.assertIn('MissingOperationParameter', json.dumps(result))
        self.assertFalse((self.root / '.ledger/negative-ledger/events.jsonl').exists())

    def test_previous_bound_history_supports_current_reads_and_new_retry_keys(self):
        previous = PREVIOUS / NEGATIVE.name
        original = self.record()
        self.native(previous, 'transact', '--operation', 'capture',
                    '--input', 'capture=-', packet={'record': original})
        old_rows = self.project(previous, 'current-records', limit=20)
        old_id = old_rows[0]['neg_id']
        old_note = self.project(previous, 'memory-note', id=old_id)
        before = self.custody()

        self.check_definition(NEGATIVE)
        self.assertEqual(self.project(NEGATIVE, 'current-records', limit=20), old_rows)
        self.assertEqual(self.project(NEGATIVE, 'memory-note', id=old_id), old_note)
        self.assertTrue(self.native(NEGATIVE, 'doctor')['healthy'])
        candidates = self.project(NEGATIVE, 'route-candidates', query='component admission', limit=8)
        self.assertEqual(candidates[0]['neg_id'], old_id)
        self.assertEqual(self.custody(), before)

        followup = self.record(route='another-admission-route')
        self.capture(followup, 'post-upgrade-finding')
        rows = self.project(NEGATIVE, 'current-records', limit=20)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], old_rows[0])
        self.assertEqual(len({row['neg_id'] for row in rows}), 2)
        self.assertEqual(self.project(NEGATIVE, 'memory-note', id=old_id), old_note)
        self.assertTrue(self.native(NEGATIVE, 'doctor')['healthy'])
        self.assertTrue((self.root / '.ledger/negative-ledger/events.jsonl').read_bytes().startswith(
            before['.ledger/negative-ledger/events.jsonl']))
        self.assert_archives_preserved(before)
        after = self.custody()
        self.assertEqual(self.capture(followup, 'post-upgrade-finding')['effects'][0]['result'],
                         'idempotent')
        self.assertEqual((self.root / '.ledger/negative-ledger/events.jsonl').read_bytes(),
                         after['.ledger/negative-ledger/events.jsonl'])
        self.assert_archives_preserved(after)


class LearningHistoryTests(NativeHistory):
    def record(self):
        return {
            'status': 'codify_now', 'learning': 'Reuse immutable parsed configuration.',
            'application': 'Reuse only when all semantic inputs are in the cache key.',
            'context': {'repo': 'ledger-repository:' + self.store_id,
                        'branch': 'worktree-one', 'paths': ['src/config.zig']},
            'source': 'root-one', 'evidence': ['fixture:immutable-cache passed'],
        }

    def capture(self, record):
        return self.native(LEARNINGS, 'transact', '--operation', 'capture',
                           '--input', 'submission=-', packet={'record': record})

    def test_same_words_retain_distinct_scope_and_applicability(self):
        original = self.record()
        self.capture(original)
        distinct_path = copy.deepcopy(original)
        distinct_path['context']['paths'] = ['src/session.zig']
        self.capture(distinct_path)
        distinct_application = copy.deepcopy(original)
        distinct_application['application'] = 'Reuse only within the same immutable request snapshot.'
        self.capture(distinct_application)
        records = self.project(LEARNINGS, 'import-records')
        self.assertEqual(len(records), 3)
        self.assertEqual(len({record['id'] for record in records}), 3)
        self.assertEqual(len({record['fingerprint'] for record in records}), 3)

    def test_time_worktree_source_and_repeated_evidence_do_not_create_novelty(self):
        original = self.record()
        self.capture(original)
        before = self.project(LEARNINGS, 'import-records')
        log = self.root / '.ledger/learnings/events.jsonl'
        original_bytes = log.read_bytes()
        time.sleep(1.05)  # Cross the event timestamp's one-second resolution.
        repeat = copy.deepcopy(original)
        repeat['learning'] = repeat['learning'].upper()
        repeat['context']['branch'] = 'worktree-two'
        repeat['source'] = 'root-two'
        repeat['evidence'] = ['fixture:immutable-cache passed again at a later time']
        result = self.capture(repeat)
        self.assertEqual(result['effects'][0]['result'], 'idempotent')
        self.assertEqual(self.project(LEARNINGS, 'import-records'), before)
        self.assertEqual(log.read_bytes(), original_bytes)

    def test_correction_supersedes_without_rewriting_prior_record(self):
        original = self.record()
        self.capture(original)
        first = self.project(LEARNINGS, 'import-records')[0]
        log = self.root / '.ledger/learnings/events.jsonl'
        original_bytes = log.read_bytes()
        correction = copy.deepcopy(original)
        correction['application'] = 'Reuse only immutable inputs and copy values before request-local mutation.'
        correction['supersedes_id'] = first['id']
        correction['evidence'].append('fixture:request-isolation exposed shared mutation')
        self.capture(correction)
        records = self.project(LEARNINGS, 'import-records')
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0], first)
        self.assertTrue(log.read_bytes().startswith(original_bytes))
        now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        recalled = self.project(LEARNINGS, 'recall', query='immutable configuration cache',
                                now=now, drop_superseded='true', search_limit=8)
        self.assertEqual([record['id'] for record in recalled], [records[1]['id']])

    def test_previous_fingerprints_and_exports_survive_new_scoped_captures(self):
        previous = PREVIOUS / LEARNINGS.name
        original = self.record()
        self.native(previous, 'transact', '--operation', 'capture',
                    '--input', 'submission=-', packet={'record': original})
        old_rows = self.project(previous, 'import-records')
        old_id = old_rows[0]['id']
        old_note = self.project(previous, 'memory-note', id=old_id)
        before = self.custody()

        self.check_definition(LEARNINGS)
        self.assertEqual(self.project(LEARNINGS, 'import-records'), old_rows)
        self.assertEqual(self.project(LEARNINGS, 'record', id=old_id), old_rows[0])
        self.assertEqual(self.project(LEARNINGS, 'memory-note', id=old_id), old_note)
        self.assertTrue(self.native(LEARNINGS, 'doctor')['healthy'])
        self.assertEqual(self.custody(), before)
        now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        recalled = self.project(LEARNINGS, 'recall', query='immutable configuration cache',
                                now=now, drop_superseded='true', search_limit=8)
        self.assertEqual([record['id'] for record in recalled], [old_id])
        self.assertEqual(self.project(LEARNINGS, 'record', id=old_id), old_rows[0])

        scoped = copy.deepcopy(original)
        scoped['application'] = 'Reuse only within the immutable request snapshot.'
        self.capture(scoped)
        rows = self.project(LEARNINGS, 'import-records')
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], old_rows[0])
        self.assertNotEqual(rows[1]['id'], old_id)
        self.assertNotEqual(rows[1]['fingerprint'], old_rows[0]['fingerprint'])
        self.assertEqual(self.project(LEARNINGS, 'memory-note', id=old_id), old_note)
        self.assertTrue(self.native(LEARNINGS, 'doctor')['healthy'])
        self.assertTrue((self.root / '.ledger/learnings/events.jsonl').read_bytes().startswith(
            before['.ledger/learnings/events.jsonl']))
        self.assert_archives_preserved(before)
        after = self.custody()
        self.assertEqual(self.capture(scoped)['effects'][0]['result'], 'idempotent')
        self.assertEqual((self.root / '.ledger/learnings/events.jsonl').read_bytes(),
                         after['.ledger/learnings/events.jsonl'])
        self.assert_archives_preserved(after)


if __name__ == '__main__':
    unittest.main()
