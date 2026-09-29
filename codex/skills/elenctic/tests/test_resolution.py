"""Resolution presentation tests; not evidence of LLM grouping quality."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('elenctic_resolution_report', SKILL / 'scripts/report.py')
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


def sample():
    findings = []
    for key, number, disposition, title in [
        ('f-cancel', 2, 'merge-blocker', 'Cancellation acknowledges before effects stop'),
        ('f-recovery', 5, 'merge-blocker', 'Recovery can admit duplicate work'),
        ('f-docs', 8, 'concern', 'Clarify the pending outcome example'),
        ('f-migration', 11, 'risk', 'Deployment shutdown grace period is unconfirmed'),
    ]:
        findings.append({'id': key, 'number': number, 'disposition': disposition, 'title': title,
                         'location': f'src/{key}.ts:12',
                         'detail': f'Illustrative evidence for {title.lower()}. The full report preserves the counter-case.',
                         'required_outcome': 'Preserve the accepted lifecycle and compatibility obligations.',
                         'sources': [{'label': 'Existing discussion', 'url': 'https://github.com/example/service/pull/42#discussion_r123'}]})
    findings[0]['draft'] = 'Cancellation should report its actual outcome because callers use it to decide whether retrying is safe.'
    groups = [
        {'id': 'R1', 'title': 'Establish one cancellation and recovery owner',
         'finding_ids': ['f-cancel', 'f-recovery', 'f-docs'],
         'rationale': 'The lifecycle transition supplies the shared guarantee; the example is an optional clarification, not a merge gate.',
         'objective': 'Coordinate cancellation and recovery without rejecting valid work; keep optional documentation separate from required fixes.',
         'completion_checks': [
             {'finding_id': 'f-cancel', 'evidence': 'Demonstrate the acknowledged cancellation boundary.'},
             {'finding_id': 'f-recovery', 'evidence': 'Demonstrate exactly-once admission across recovery.'},
             {'finding_id': 'f-docs', 'evidence': 'Optional: clarify the example without strengthening the contract.'}],
         'depends_on': []},
        {'id': 'R2', 'title': 'Verify deployment assumptions', 'finding_ids': ['f-migration'],
         'rationale': 'Deployment evidence is distinct from the lifecycle implementation.',
         'objective': 'Confirm the supported grace period; do not assume the risk is a defect.',
         'completion_checks': [{'finding_id': 'f-migration', 'evidence': 'Read the actual deployment configuration and record the assumption.'}],
         'depends_on': ['R1']}]
    return {'schema': 'elenctic-report/v1', 'workflow': 'resolution',
            'identity': {'schema': 'elenctic-review-identity/v1', 'mode': 'campaign', 'repo': 'example/service',
                         'pr': 42, 'campaign_id': 'resolution-fixture', 'campaign_context_id': 'sha256:brief',
                         'campaign_seed_thread_id': 'seed-fixture', 'campaign_policy_id': 'sha256:policy',
                         'base': 'a' * 40, 'candidate': 'b' * 40, 'view': 'pr-head', 'coverage': 'partial',
                         'selected_scope_coverage': 'complete', 'whole_pr_coverage': 'partial', 'verdict': 'BLOCKED'},
            'title': 'Cancellation and recovery — illustrative resolution report',
            'pr_url': 'https://github.com/example/service/pull/42', 'generated_at': '2026-09-29T17:00:00Z',
            'summary': 'Two blockers and two nonblocking findings. This is a fixture, not a real PR review.',
            'coverage_note': 'Selected files complete; a pre-Viewed exclusion lacks current evidence. Whole-PR coverage is partial.',
            'report_text': '#2 and #5 are blockers; #8 is a concern; #11 is a risk.\nR1: #2, #5, #8. R2: #11.\nBLOCKED.',
            'findings': findings, 'resolution': {'status': 'complete', 'groups': groups}}


class ResolutionTests(unittest.TestCase):
    def test_legacy_default_has_no_groups_or_invented_numbers(self):
        raw = sample(); raw.pop('workflow'); raw.pop('resolution')
        for finding in raw['findings']: finding.pop('number')
        parsed = report.prepare(raw)
        self.assertEqual(parsed['workflow'], 'comments')
        self.assertNotIn('resolution', parsed)
        self.assertTrue(all('number' not in f for f in parsed['findings']))

    def test_resolution_is_lossless_and_keeps_draftless_and_optional_findings(self):
        raw = sample(); parsed = report.prepare(raw)
        self.assertEqual(parsed['resolution'], raw['resolution'])
        actual = {f['id']: f for f in parsed['findings']}
        for original in raw['findings']:
            for key, value in original.items(): self.assertEqual(actual[original['id']][key], value)
        self.assertEqual(actual['f-recovery']['draft'], '')
        self.assertEqual(actual['f-docs']['disposition'], 'concern')
        self.assertEqual(parsed['identity'], raw['identity'])

    def test_default_rejects_resolution_data(self):
        raw = sample(); raw['workflow'] = 'comments'
        with self.assertRaises(ValueError): report.prepare(raw)

    def test_unknown_workflow_is_not_silently_inferred(self):
        for value in ['own-pr', '', None, {}, []]:
            raw = sample(); raw['workflow'] = value
            with self.subTest(value=value), self.assertRaises(ValueError): report.prepare(raw)

    def test_numbers_must_be_unique_positive_safe_integers(self):
        for value in [True, 0, -1, '2', 1.5, 2**53, 5, None]:
            raw = sample(); raw['findings'][0]['number'] = value
            with self.subTest(value=value), self.assertRaises(ValueError): report.prepare(raw)

    def test_resolution_cannot_invent_a_missing_number(self):
        raw = sample(); raw['findings'][0].pop('number')
        with self.assertRaises(ValueError): report.prepare(raw)
        raw['finding_numbers'] = {'f-cancel': 2}
        self.assertEqual(report.prepare(raw)['findings'][0]['number'], 2)

    def test_reordering_and_grouping_do_not_change_evidence_fingerprints(self):
        raw = sample(); before = report.prepare(raw)
        raw['findings'].reverse(); raw['resolution']['groups'].reverse()
        raw['resolution']['groups'][1]['title'] = 'A better description of the same unit'
        after = report.prepare(raw)
        self.assertEqual({f['id']: (f['number'], f['fingerprint']) for f in before['findings']},
                         {f['id']: (f['number'], f['fingerprint']) for f in after['findings']})
        raw.pop('resolution'); raw['workflow'] = 'comments'
        comments = report.prepare(raw)
        self.assertEqual(before['report_key'], comments['report_key'])
        self.assertEqual([f['fingerprint'] for f in after['findings']], [f['fingerprint'] for f in comments['findings']])

    def test_changed_evidence_changes_only_that_finding_fingerprint(self):
        raw = sample(); before = report.prepare(raw)
        raw['findings'][0]['detail'] += ' New supported execution path.'
        after = report.prepare(raw)
        for old, new in zip(before['findings'], after['findings']):
            self.assertEqual(old['fingerprint'] == new['fingerprint'], old['id'] != 'f-cancel')

    def test_partition_rejects_missing_unknown_and_repeated_members(self):
        for members in [[], ['not-a-finding'], ['f-cancel', 'f-cancel'], ['f-migration'], ['f-cancel']]:
            raw = sample(); raw['resolution']['groups'][0]['finding_ids'] = members
            with self.subTest(members=members), self.assertRaises(ValueError): report.prepare(raw)
        raw = sample(); raw['resolution']['groups'].pop()
        with self.assertRaises(ValueError): report.prepare(raw)

    def test_checks_cover_each_member_once(self):
        for change in ['missing', 'duplicate', 'other-group', 'empty-evidence']:
            raw = sample(); checks = raw['resolution']['groups'][0]['completion_checks']
            if change == 'missing': checks.pop()
            elif change == 'duplicate': checks.append(deepcopy(checks[0]))
            elif change == 'other-group': checks[0]['finding_id'] = 'f-migration'
            else: checks[0]['evidence'] = ''
            with self.subTest(change=change), self.assertRaises(ValueError): report.prepare(raw)

    def test_invalid_group_ids_and_dependency_graphs(self):
        for value in ['1', 'R0', 'R01', 'R2', '__proto__']:
            raw = sample(); raw['resolution']['groups'][0]['id'] = value
            with self.subTest(value=value), self.assertRaises(ValueError): report.prepare(raw)
        for dependencies in [['R1'], ['R2'], ['R99'], ['R2', 'R2'], 'R2']:
            raw = sample(); raw['resolution']['groups'][0]['depends_on'] = dependencies
            with self.subTest(dependencies=dependencies), self.assertRaises(ValueError): report.prepare(raw)

    def test_singletons_and_non_topological_display_order_are_valid(self):
        raw = sample(); raw['resolution']['groups'].reverse()
        self.assertEqual(report.prepare(raw)['resolution']['groups'][0]['id'], 'R2')

    def test_empty_and_unavailable_synthesis_keep_review_judgment(self):
        raw = sample(); raw['resolution'] = {'status': 'unavailable', 'reason': 'Installed Glaze could not be read.'}
        parsed = report.prepare(raw)
        self.assertEqual(parsed['identity']['verdict'], 'BLOCKED')
        self.assertEqual(len(parsed['findings']), 4)
        raw['resolution']['groups'] = sample()['resolution']['groups']
        with self.assertRaises(ValueError): report.prepare(raw)
        raw = sample(); raw['findings'] = []; raw['resolution']['groups'] = []
        raw['identity'].update(verdict='INCOMPLETE', selected_scope_coverage='partial')
        self.assertEqual(report.prepare(raw)['resolution'], {'status': 'complete', 'groups': []})

    def test_number_history_rejects_renumbering_and_retired_reuse(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'report.html'; raw = sample()
            report.write_report(raw, output)
            changed = deepcopy(raw); changed['findings'][0]['number'] = 99
            with self.assertRaises(ValueError): report.write_report(changed, output)
            raw['workflow'] = 'comments'; raw.pop('resolution')
            raw['findings'] = [f for f in raw['findings'] if f['id'] != 'f-docs']
            report.write_report(raw, output)
            parsed = json.loads(re.search(r'<script id="report-data" type="application/json">(.*?)</script>', output.read_text(), re.S)[1])
            self.assertEqual(parsed['finding_numbers']['f-docs'], 8)
            raw['findings'].append({**deepcopy(raw['findings'][-1]), 'id': 'f-new', 'number': 8})
            with self.assertRaises(ValueError): report.write_report(raw, output)
            raw['findings'][-1]['number'] = 12
            report.write_report(raw, output)

    def test_known_number_survives_legacy_regeneration(self):
        raw = sample(); previous = report.prepare(raw)
        raw['workflow'] = 'comments'; raw.pop('resolution')
        for finding in raw['findings']: finding.pop('number')
        _, parsed = report.render(raw, previous=previous)
        self.assertEqual(parsed['finding_numbers'], previous['finding_numbers'])
        self.assertEqual({f['id']: f['number'] for f in parsed['findings']}, previous['finding_numbers'])

    def test_provided_registry_cannot_rebind_numbers(self):
        raw = sample(); raw['finding_numbers'] = {'f-cancel': 3}
        with self.assertRaises(ValueError): report.prepare(raw)
        raw['finding_numbers'] = {'retired-finding': 2}
        with self.assertRaises(ValueError): report.prepare(raw)

    def test_history_cannot_cross_campaigns(self):
        raw = sample(); previous = report.prepare(raw); raw['identity']['candidate'] = 'c' * 40
        with self.assertRaises(ValueError): report.render(raw, previous=previous)

    def test_untrusted_group_text_is_inert(self):
        raw = sample(); attack = '</script><img src=x onerror="window.pwned=1">'
        raw['resolution']['groups'][0]['title'] = attack
        document, parsed = report.render(raw)
        self.assertNotIn(attack, document)
        self.assertIn('\\u003c/script\\u003e', document)
        self.assertEqual(parsed['resolution']['groups'][0]['title'], attack)


if __name__ == '__main__':
    unittest.main()
