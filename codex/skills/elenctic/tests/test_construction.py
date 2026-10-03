"""Construction report contracts, not an evaluation of model causal judgment."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from test_resolution import report, sample as resolution_sample


def sample(*, campaign=False):
    raw = resolution_sample()
    raw['workflow'] = 'construction'
    construction = raw.pop('resolution')
    construction['compatibility'] = 'R1 changes the lifecycle owner. R2 remains an independent deployment evidence gap, not a prerequisite invented by this proposal.'
    construction['adjudications'] = []
    for index, finding in enumerate(raw['findings']):
        disposition, law = [('accepted', 'entailed'), ('accepted', 'entailed'),
                            ('follow-up', 'strengthening'), ('blocked', 'underdetermined')][index]
        construction['adjudications'].append({
            'id': f'A{index + 1}', 'source': f'Original finding #{finding["number"]}; complete source exchange',
            'claim': finding['title'], 'disposition': disposition, 'law_authority': law,
            'basis': 'Illustrative authority, current code trace and strongest countercase; not a real adjudication.',
            'finding_ids': [finding['id']], 'url': raw['pr_url'] + f'#discussion_r{index + 1}'})
    construction['adjudications'].append({
        'id': 'A5', 'source': 'Additional PR comment', 'claim': 'The current route bypasses the existing owner.',
        'disposition': 'rejected', 'law_authority': 'entailed',
        'basis': 'The current call path already crosses that owner; the original comment predates this change.',
        'finding_ids': []})
    construction['groups'][0]['proposal'] = {
        'status': 'proposed',
        'mechanism': 'Callers independently interpret and publish terminal execution state.',
        'exclusion_argument': 'Owner-controlled transitions would reject stale terminal publication; external effects require the separate checks below.',
        'changes': [
            {'path': 'src/queue.ts', 'symbol': 'commitTerminal',
             'change': 'Replace public terminal setters with an owner-controlled generation-checked transition; expose pending cancellation distinctly.'},
            {'path': 'src/recovery.ts', 'symbol': 'recover',
             'change': 'Acquire a new generation through the same owner and retire direct terminal writes.'}],
        'preserve': 'Keep valid execution, supported recovery, wire outcomes and optional documentation optional.',
        'migration': 'Migrate queue and recovery producers plus serialization re-entry; audit sanctioned bypasses before claiming coverage.',
        'retirements': 'Remove duplicate terminal eligibility logic; retain independent effect-boundary checks and test oracles.',
        'verification': 'Use the native lifecycle suite for stale completion, cancellation interleavings and required-valid counterparts; verify effects independently.',
        'limits': 'Not implemented or verified. Recorded-state exclusion alone does not prove external-effect cancellation.'}
    construction['groups'][1]['proposal'] = {
        'status': 'unresolved', 'reason': 'The supported deployment budget is not established; no code change is selected.'}
    raw['construction'] = construction
    if not campaign:
        raw['identity'] = {key: raw['identity'][key] for key in ('repo', 'pr', 'base', 'candidate', 'view')}
        raw['identity'].update(schema='elenctic-construction-identity/v1', mode='analysis', analysis_id='analysis-fixture')
        raw['coverage_note'] = 'Existing PR feedback and its causal code paths only; no file review campaign or whole-PR coverage.'
        raw['report_text'] = 'Illustrative comment analysis. Original findings #2, #5, #8, #11 and A5 rejection. R1 proposed; R2 unresolved. No review verdict.'
    return raw


class ConstructionTests(unittest.TestCase):
    def test_campaign_composition_preserves_identity_findings_and_drafts(self):
        raw = sample(campaign=True)
        parsed = report.prepare(raw)
        self.assertEqual(parsed['identity'], raw['identity'])
        self.assertEqual(parsed['construction'], raw['construction'])
        self.assertNotIn('resolution', parsed)
        actual = {f['id']: f for f in parsed['findings']}
        for original in raw['findings']:
            for key, value in original.items():
                self.assertEqual(actual[original['id']][key], value)
        self.assertEqual(actual['f-recovery']['draft'], '')

    def test_comment_analysis_does_not_manufacture_campaign_coverage(self):
        raw = sample(); parsed = report.prepare(raw)
        self.assertEqual(parsed['identity'], raw['identity'])
        self.assertNotIn('verdict', parsed['identity'])
        self.assertNotIn('campaign_id', parsed['identity'])
        self.assertNotIn('whole_pr_coverage', parsed['identity'])
        self.assertTrue(parsed['report_key'].startswith('elenctic-analysis:'))

    def test_analysis_rejects_all_claims_of_review_credit_even_null(self):
        for key, value in [('verdict', 'APPROVE'), ('coverage', 'complete'),
                           ('selected_scope_coverage', 'complete'), ('whole_pr_coverage', 'partial'),
                           ('campaign_id', 'fake'), ('campaign_context_id', None),
                           ('campaign_seed_thread_id', None), ('campaign_policy_id', None)]:
            raw = sample(); raw['identity'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                report.prepare(raw)

    def test_analysis_identity_requires_its_mode_and_real_instance(self):
        for key, value in [('mode', 'campaign'), ('analysis_id', ''), ('view', 'working-tree'), ('pr', True)]:
            raw = sample(); raw['identity'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): report.prepare(raw)

    def test_wrong_or_mixed_workflows_are_rejected(self):
        for workflow in ('comments', 'resolution', None):
            raw = sample(campaign=True); raw['workflow'] = workflow
            with self.subTest(workflow=workflow), self.assertRaises(ValueError): report.prepare(raw)
        raw = sample(); raw['resolution'] = resolution_sample()['resolution']
        with self.assertRaises(ValueError): report.prepare(raw)
        raw = sample(); raw.pop('construction')
        with self.assertRaises(ValueError): report.prepare(raw)

    def test_proposal_changes_do_not_change_finding_handling_identity(self):
        raw = sample(campaign=True); before = report.prepare(raw)
        raw['construction']['groups'][0]['proposal']['changes'][0]['change'] += ' Refined implementation sketch.'
        after = report.prepare(raw)
        self.assertEqual(before['report_key'], after['report_key'])
        self.assertEqual(before['findings'], after['findings'])
        comments = deepcopy(raw); comments.pop('construction'); comments['workflow'] = 'comments'
        self.assertEqual(report.prepare(comments)['report_key'], before['report_key'])

    def test_new_head_or_analysis_cannot_inherit_handling(self):
        raw = sample(); previous = report.prepare(raw)
        for key in ('candidate', 'base', 'analysis_id'):
            changed = deepcopy(raw); changed['identity'][key] += '-changed'
            with self.subTest(key=key), self.assertRaises(ValueError): report.render(changed, previous=previous)
        with self.assertRaises(ValueError): report.render(sample(campaign=True), previous=previous)

    def test_numbering_and_acyclic_lossless_grouping_are_shared(self):
        mutations = [
            lambda r: r['findings'][0].pop('number'),
            lambda r: r['construction']['groups'].pop(),
            lambda r: r['construction']['groups'][0]['depends_on'].append('R2'),
            lambda r: r['construction']['groups'][0]['completion_checks'].pop(),
            lambda r: r['construction']['groups'][0]['finding_ids'].append('f-migration')]
        for mutate in mutations:
            raw = sample(); mutate(raw)
            with self.subTest(mutation=mutate), self.assertRaises(ValueError): report.prepare(raw)

    def test_complete_adjudication_cannot_omit_or_invent_a_finding(self):
        for change in ('omit', 'unknown', 'duplicate-id', 'duplicate-reference'):
            raw = sample(); judgments = raw['construction']['adjudications']
            if change == 'omit': judgments.pop(0)
            elif change == 'unknown': judgments[0]['finding_ids'] = ['not-present']
            elif change == 'duplicate-id': judgments[1]['id'] = judgments[0]['id']
            else: judgments[0]['finding_ids'] *= 2
            with self.subTest(change=change), self.assertRaises(ValueError): report.prepare(raw)

    def test_feedback_cannot_launder_preference_or_unknown_into_correctness(self):
        for law, disposition, refs in [('preference', 'accepted', ['f-cancel']),
                                       ('underdetermined', 'accepted', ['f-cancel']),
                                       ('strengthening', 'accepted', ['f-cancel']),
                                       ('new-requirement', 'accepted', ['f-cancel']),
                                       ('entailed', 'accepted', []),
                                       ('entailed', 'rejected', ['f-cancel']),
                                       ('strengthening', 'follow-up', ['f-cancel']),
                                       ('underdetermined', 'blocked', ['f-cancel']),
                                       ('entailed', 'blocked', ['f-cancel'])]:
            raw = sample(); raw['construction']['adjudications'][0].update(
                law_authority=law, disposition=disposition, finding_ids=refs)
            with self.subTest(law=law, disposition=disposition), self.assertRaises(ValueError): report.prepare(raw)

    def test_no_change_is_valid_for_refuted_feedback_without_fake_findings(self):
        raw = sample(); raw['findings'] = []; raw['construction']['groups'] = []
        raw['construction']['adjudications'] = [raw['construction']['adjudications'][-1]]
        parsed = report.prepare(raw)
        self.assertEqual(parsed['construction']['groups'], [])
        self.assertEqual(parsed['construction']['adjudications'][0]['disposition'], 'rejected')
        self.assertEqual(parsed['findings'], [])

    def test_refuted_optional_claim_does_not_force_a_followup(self):
        raw = sample()
        for law in ('strengthening', 'new-requirement', 'preference', 'underdetermined'):
            raw['construction']['adjudications'][-1]['law_authority'] = law
            parsed = report.prepare(raw)
            self.assertEqual(parsed['construction']['adjudications'][-1]['disposition'], 'rejected')
            self.assertEqual(parsed['construction']['adjudications'][-1]['finding_ids'], [])

    def test_unavailable_analysis_preserves_supported_report(self):
        raw = sample(campaign=True)
        raw['construction'] = {'status': 'unavailable', 'reason': 'Installed Actuating is unreadable.', 'adjudications': []}
        parsed = report.prepare(raw)
        self.assertEqual(parsed['identity']['verdict'], 'BLOCKED')
        self.assertEqual(len(parsed['findings']), 4)
        raw['construction']['groups'] = sample()['construction']['groups']
        with self.assertRaises(ValueError): report.prepare(raw)

    def test_selected_proposal_requires_code_bound_obligations(self):
        fields = ('mechanism', 'exclusion_argument', 'preserve', 'migration', 'retirements', 'verification', 'limits', 'changes')
        for key in fields:
            raw = sample(); raw['construction']['groups'][0]['proposal'].pop(key)
            with self.subTest(key=key), self.assertRaises(ValueError): report.prepare(raw)
        raw = sample(); raw['construction']['groups'][0]['proposal']['changes'] = []
        with self.assertRaises(ValueError): report.prepare(raw)
        raw = sample(); raw['construction'].pop('compatibility')
        with self.assertRaises(ValueError): report.prepare(raw)

    def test_changes_require_repository_relative_paths_and_symbols(self):
        for path in ('/tmp/file', '../src/file', 'src/../../file', 'C:\\file', 'C:/file', 'src/\nfile'):
            raw = sample(); raw['construction']['groups'][0]['proposal']['changes'][0]['path'] = path
            with self.subTest(path=path), self.assertRaises(ValueError): report.prepare(raw)
        for field in ('path', 'symbol', 'change'):
            raw = sample(); raw['construction']['groups'][0]['proposal']['changes'][0][field] = ''
            with self.subTest(field=field), self.assertRaises(ValueError): report.prepare(raw)

    def test_proposal_status_is_not_an_elimination_or_completion_claim(self):
        for status in ('eliminated', 'verified', 'complete', None):
            raw = sample(); raw['construction']['groups'][0]['proposal']['status'] = status
            with self.subTest(status=status), self.assertRaises(ValueError): report.prepare(raw)
        raw = sample(); raw['construction']['groups'][1]['proposal']['changes'] = [{'path': 'src/a.ts'}]
        with self.assertRaises(ValueError): report.prepare(raw)
        raw = sample(); raw['construction']['groups'][0]['proposal'] = {'status': 'preserve-incumbent', 'reason': 'Prefer no rewrite.'}
        with self.assertRaises(ValueError): report.prepare(raw)
        raw = sample(); raw['construction']['groups'][1]['proposal'] = {'status': 'preserve-incumbent', 'reason': 'This optional change has no demonstrated benefit.'}
        self.assertEqual(report.prepare(raw)['construction']['groups'][1]['proposal']['status'], 'preserve-incumbent')

    def test_untrusted_proposals_and_feedback_remain_plain_text(self):
        raw = sample(); attack = '</script><img src=x onerror="window.pwned=1">'
        raw['construction']['groups'][0]['proposal']['changes'][0]['change'] = attack
        raw['construction']['adjudications'][0]['claim'] = attack
        document, parsed = report.render(raw)
        self.assertNotIn(attack, document)
        self.assertIn('\\u003c/script\\u003e', document)
        self.assertEqual(parsed['construction']['adjudications'][0]['claim'], attack)
        raw['construction']['adjudications'][0]['url'] = 'javascript:alert(1)'
        with self.assertRaises(ValueError): report.prepare(raw)

    def test_atomic_private_regeneration_retains_original_references(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.html'; raw = sample()
            report.write_report(raw, path)
            raw['findings'][0]['number'] = 99
            with self.assertRaises(ValueError): report.write_report(raw, path)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)


if __name__ == '__main__':
    unittest.main()
