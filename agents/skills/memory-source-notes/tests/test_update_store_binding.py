"""Updates must bind to the selected source, not merely a reused local ID."""
import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import source_memory_note as adapter


class UpdateStoreBindingTests(unittest.TestCase):
    def envelope(self, repo):
        return {'operation': 'assert', 'authority': 'ledger-cli', 'summary': 'source',
            'scope': {'kind': 'repo', 'repo': repo},
            'source_refs': [{'kind': 'negative-ledger', 'ref': repo + ':.ledger/negative-ledger/events.jsonl#NEG-000001'}],
            'related_ids': [], 'supersedes_id': None,
            'payload': {'neg_id': 'NEG-000001', 'repository_id': repo,
                'ledger_path': '.ledger/negative-ledger/events.jsonl', 'capture_event_count': 1,
                'status_event_count': 0, 'source_event_count': 1, 'status': 'active',
                'event_chain_fingerprint': 'a' * 64, 'projection_fingerprint': 'b' * 64,
                'previous_projection_fingerprint': None, 'attempted_change': 'attempt'}}

    def update(self, current):
        prior = copy.deepcopy(current)
        prior.update(schema='memory-source-note/v1', id='MSN-20261122T000000Z-0123456789abcdef',
                     extension='negative-ledger', kind='ledger-projection', fingerprint='c' * 64)
        raw = adapter.canonical_bytes(current)
        encoded = adapter.build_update('negative-ledger', 'retract', raw, prior,
            prior_note_id=prior['id'], reason='resolved', evidence_refs=['test:law'],
            repository_identity=current['scope']['repo'])
        note = json.loads(encoded)
        note.update(id='MSN-20261122T000001Z-0123456789abcdef', extension='negative-ledger',
                    kind='ledger-retraction', fingerprint=adapter.writer_fingerprint('negative-ledger', 'ledger-retraction', encoded))
        return note, {prior['id']: prior}

    def test_foreign_store_with_same_id_cannot_claim_local_withdrawal(self):
        local = self.envelope('ledger-repository:' + 'a' * 32)
        foreign = self.envelope('ledger-repository:' + 'b' * 32)
        note, prior = self.update(foreign)
        self.assertIsNone(adapter.validated_update('negative-ledger', adapter.canonical_bytes(local), note, prior, local['scope']['repo']))
        note, prior = self.update(local)
        self.assertTrue(adapter.validated_update('negative-ledger', adapter.canonical_bytes(local), note, prior, local['scope']['repo'])[1])

    def test_lifecycle_change_preserves_managed_capture_but_not_a_different_capture(self):
        old = self.envelope('ledger-repository:' + 'a' * 32)
        note, prior = self.update(old)
        current = copy.deepcopy(old)
        current['payload'].update(status='stale', status_event_count=2, source_event_count=3,
                                  event_chain_fingerprint='d' * 64, projection_fingerprint='e' * 64,
                                  previous_projection_fingerprint='f' * 64)
        result = adapter.validated_update('negative-ledger', adapter.canonical_bytes(current), note, prior, current['scope']['repo'])
        self.assertIsNotNone(result)
        self.assertFalse(result[1])
        current['payload']['attempted_change'] = 'different attempt'
        self.assertIsNone(adapter.validated_update('negative-ledger', adapter.canonical_bytes(current), note, prior, current['scope']['repo']))


if __name__ == '__main__':
    unittest.main()
