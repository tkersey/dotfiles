"""Independent updates do not conflict merely because they share a source ID."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

scripts = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(scripts))
spec = importlib.util.spec_from_file_location('chain_reconcile', scripts / 'source-memory-reconcile.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class IndependentChainTests(unittest.TestCase):
    def report(self, notes):
        raw = json.dumps({'payload': {'neg_id': 'NEG-000001'}}).encode()
        with patch.object(module, 'native_export', return_value=(raw, None)), \
             patch.object(module, 'negative_admission', return_value=raw), \
             patch.object(module, 'writer_fingerprint', side_effect=lambda source, kind, data: kind), \
             patch.object(module, 'validated_update', side_effect=lambda source, raw, note, inventory, repo:
                 (raw, True) if note['kind'] == 'ledger-retraction' else None), \
             patch.object(module, 'matches_negative_predecessor', return_value=False):
            return module.source_report('negative-ledger', [{'neg_id': 'NEG-000001'}], notes,
                ledger='unused', cwd=Path('/tmp'), eligibility={}, compiled_corpus=[], unreadable_phase2=[],
                synesthesia_adapter=None, repository_identity='repo', standalone_note_ids=set(),
                fallback_show_count=0, codex_home=Path('/tmp'), native_args=[])['records'][0]

    def note(self, note_id, kind, prior=None):
        note = {'id': note_id, 'kind': kind, 'fingerprint': kind, 'scope': {'kind': 'global'},
                'payload': {'neg_id': 'NEG-000001'}}
        if prior:
            note['payload']['memory_update'] = {'prior_note_id': prior}
            note['operation'] = 'retract'
        return note

    def test_two_independent_withdrawals(self):
        notes = [self.note('A', 'ledger-projection'), self.note('B', 'ledger-status-transition'),
                 self.note('U', 'ledger-retraction', 'A'), self.note('V', 'ledger-retraction', 'B')]
        row = self.report(notes)
        self.assertEqual(row['status'], 'admitted')
        self.assertEqual(row['memory_guidance']['state'], 'withdrawn')
        self.assertEqual({chain['update_note_id'] for chain in row['memory_guidance']['chains']}, {'U', 'V'})

    def test_same_admission_fork_remains_unresolved(self):
        notes = [self.note('A', 'ledger-projection'), self.note('U', 'ledger-retraction', 'A'),
                 self.note('V', 'ledger-retraction', 'A')]
        row = self.report(notes)
        self.assertEqual(row['status'], 'incomplete-projection')
        self.assertEqual(row['memory_guidance']['state'], 'unresolved')

    def test_unwithdrawn_admission_not_reported_fully_withdrawn(self):
        notes = [self.note('A', 'ledger-projection'), self.note('B', 'ledger-status-transition'),
                 self.note('C', 'ledger-projection'), self.note('U', 'ledger-retraction', 'A'),
                 self.note('V', 'ledger-retraction', 'B')]
        self.assertEqual(self.report(notes)['memory_guidance']['state'], 'mixed')

    def test_single_withdrawal_keeps_independent_admission_active(self):
        notes = [self.note('A', 'ledger-projection'), self.note('B', 'ledger-status-transition'),
                 self.note('U', 'ledger-retraction', 'A')]
        row = self.report(notes)
        self.assertEqual(row['status'], 'admitted')
        self.assertEqual(row['memory_guidance']['state'], 'mixed')
        self.assertEqual(row['memory_guidance']['live_admission_note_ids'], ['B'])
        self.assertEqual(row['memory_guidance']['chains'][0]['state'], 'withdrawn')
