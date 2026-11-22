"""Reconcile adapter-normalized legacy admissions without weakening binding."""
import copy
import unittest
from test_source_memory_reconcile import NegativePredecessorTests, MODULE


class NormalizedPredecessorTests(unittest.TestCase):
    def setUp(self):
        self.fixture = NegativePredecessorTests(methodName='test_source_predecessor_is_stale_and_keeps_historical_scope')
        self.fixture.setUp()
        self.note = copy.deepcopy(self.fixture.note)
        self.note['payload']['previous_projection_fingerprint'] = 'd' * 64
        self.note['source_refs'].append({
            'kind': 'negative-ledger-canonical-relationship', 'ref': 'projection:' + 'd' * 64,
            'summary': 'Canonical projection predecessor; not a memory-note identity.'})

    def test_normalized_predecessor_keeps_stale_attribution(self):
        result = self.fixture.report([self.note])
        self.assertEqual(result['records'][0]['status'], 'stale-note')
        self.assertEqual(result['records'][0]['scope_binding'], 'canonical-predecessor')
        self.assertEqual(result['foreign_repo_note_ids'], [])

    def test_unbound_or_malformed_extra_references_cannot_claim_predecessor(self):
        for change in ('hash', 'summary', 'extra', 'canonical'):
            note = copy.deepcopy(self.note)
            if change == 'hash': note['source_refs'][-1]['ref'] = 'projection:' + 'e' * 64
            elif change == 'summary': note['source_refs'][-1]['summary'] = 'forged'
            elif change == 'extra': note['source_refs'].append(copy.deepcopy(note['source_refs'][-1]))
            else: note['source_refs'][0]['ref'] = 'foreign'
            self.assertFalse(MODULE.matches_negative_predecessor(note, self.fixture.current, self.fixture.record_id), change)


if __name__ == '__main__':
    unittest.main()
