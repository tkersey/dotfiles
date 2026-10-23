"""Presentation and persistence contracts. These do not evaluate model judgment."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("elenctic_report", SKILL / "scripts/report.py")
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


def sample() -> dict:
    return {
        "schema": "elenctic-report/v1",
        "identity": {
            "schema": "elenctic-review-identity/v1", "mode": "campaign", "repo": "example/service",
            "pr": 42, "campaign_id": "campaign-fixture", "campaign_context_id": "sha256:brief",
            "campaign_seed_thread_id": "seed-fixture", "campaign_policy_id": "sha256:policy",
            "base": "a" * 40, "candidate": "b" * 40, "view": "pr-head",
            "coverage": "partial", "selected_scope_coverage": "complete",
            "whole_pr_coverage": "partial", "verdict": "BLOCKED",
        },
        "title": "Review queue cancellation and recovery", "pr_url": "https://github.com/example/service/pull/42",
        "generated_at": "2026-09-28T17:00:00Z", "summary": "One merge blocker, one risk, and one concern.",
        "coverage_note": "3 selected files reviewed; 1 pre-Viewed exclusion has no admitted review evidence.",
        "report_text": "Illustrative fixture, not a real PR review.\nBLOCKED: cancellation can acknowledge before effects stop.",
        "findings": [
            {"id": "f-cancel", "disposition": "merge-blocker", "title": "Cancellation acknowledges before the worker stops",
             "location": "src/queue.ts:81–96 → src/worker.ts:44",
             "detail": "The changed cancellation path returns success while an admitted worker can still commit its side effect. The existing timeout controls waiting, not worker termination.",
             "required_outcome": "Establish the promised cancellation boundary, or return the actual pending outcome under the accepted contract.",
             "draft": "Cancellation should not report completion while the worker can still commit, because callers rely on that result to decide whether retrying is safe.",
             "sources": [{"label": "Source at reviewed head", "url": "https://github.com/example/service/blob/" + "b" * 40 + "/src/queue.ts#L81-L96"}]},
            {"id": "f-recovery", "disposition": "risk", "title": "Recovery depends on the deployment shutdown grace period",
             "location": "src/recovery.ts:27", "detail": "The code preserves pending work, but the supported deployment grace period is not established by this fixture. No mandatory contract violation is asserted.",
             "required_outcome": "Confirm the deployment assumption before changing the recovery policy."},
            {"id": "f-docs", "disposition": "concern", "title": "Clarify the meaning of a pending cancellation result",
             "location": "docs/lifecycle.md:19", "detail": "The documented example does not show the pending outcome. This is nonblocking guidance, not another code defect.",
             "required_outcome": "Clarify the example without changing the accepted lifecycle contract."},
        ],
    }


def composition_sample() -> dict:
    raw = sample()
    raw["schema"] = "ergasterion-report/v1"
    identity = raw["identity"]
    for field in ("campaign_context_id", "campaign_seed_thread_id", "campaign_policy_id"):
        del identity[field]
    identity.update(schema="ergasterion-review-identity/v1", strategy="elenctic", base_tip="c" * 40)
    source = {field: identity[field] for field in ("repo", "pr", "base", "base_tip", "candidate")}
    source.update(source_ref="original-elenctic-report", scope="Fixture selected scope",
                  coverage="complete", whole_pr_coverage="partial")
    identity["assessments"] = {"elenctic": source}
    for finding, number in zip(raw["findings"], (2, 7, 9)):
        finding["number"] = number
        finding["origins"] = [{"owner": "elenctic", "reference": finding["id"],
                               "disposition": finding["disposition"]}]
        if finding.get("draft"):
            finding["draft_owner"] = "elenctic"
    return raw


class ReportTests(unittest.TestCase):
    def test_offline_document_and_all_findings(self):
        document, payload = report.render(sample())
        self.assertIn('connect-src \'none\'', document)
        self.assertNotIn('<script src=', document)
        self.assertNotIn('fetch(', document)
        self.assertEqual(len(payload['findings']), 3)
        self.assertIn('Complete original report and provenance', document)

    def test_untrusted_text_cannot_end_data_script(self):
        raw = sample()
        attack = '</script><img src=x onerror="window.pwned=true"> & <svg/onload=alert(1)>'
        raw['findings'][0]['title'] = attack
        raw['report_text'] = attack
        document, _ = report.render(raw)
        self.assertNotIn(attack, document)
        self.assertIn('\\u003c/script\\u003e', document)
        self.assertIn('&lt;/script&gt;', document)

    def test_dangerous_urls_and_duplicate_ids_rejected(self):
        for url in ('javascript:alert(1)', 'data:text/html,x', 'https://user:secret@example.com', '//example.com'):
            raw = sample(); raw['pr_url'] = url
            with self.subTest(url=url), self.assertRaises(ValueError): report.prepare(raw)
        raw = sample(); raw['findings'][1]['id'] = raw['findings'][0]['id']
        with self.assertRaises(ValueError): report.prepare(raw)

    def test_identity_and_verdict_contradictions_rejected(self):
        for field, value in [('verdict', 'APPROVE'), ('coverage', 'complete'), ('campaign_context_id', None)]:
            raw = sample(); raw['identity'][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError): report.prepare(raw)
        raw = sample(); raw['findings'][1]['draft'] = 'A nonblocker must not gain a draft.'
        with self.assertRaises(ValueError): report.prepare(raw)

    def test_whole_pr_coverage_requires_complete_selected_scope_for_every_verdict(self):
        for verdict in ('BLOCKED', 'INCOMPLETE', 'APPROVE'):
            raw = sample(); raw['identity']['verdict'] = verdict
            if verdict != 'BLOCKED': raw['findings'] = []
            raw['identity'].update(coverage='complete', whole_pr_coverage='complete')
            with self.subTest(verdict=verdict):
                self.assertEqual(report.prepare(raw)['identity']['selected_scope_coverage'], 'complete')
                raw['identity']['selected_scope_coverage'] = 'partial'
                with self.assertRaises(ValueError): report.prepare(raw)
                if verdict != 'APPROVE':
                    raw['identity'].update(coverage='partial', whole_pr_coverage='partial')
                    self.assertEqual(report.prepare(raw)['identity']['selected_scope_coverage'], 'partial')

    def test_seedless_incomplete_and_empty_scopes(self):
        raw = sample(); raw['findings'] = []
        raw['identity'].update(verdict='INCOMPLETE', selected_scope_coverage='partial', whole_pr_coverage='not-established',
                               campaign_context_id=None, campaign_seed_thread_id=None, campaign_policy_id=None)
        _, parsed = report.render(raw)
        self.assertIsNone(parsed['identity']['campaign_seed_thread_id'])
        self.assertEqual(parsed['identity']['verdict'], 'INCOMPLETE')

    def test_subagent_campaigns_render_seedless_incomplete_and_complete_scopes(self):
        for verdict in ('INCOMPLETE', 'APPROVE', 'BLOCKED'):
            raw = sample()
            raw['identity'].update(execution_mode='subagents', campaign_seed_thread_id=None, verdict=verdict)
            if verdict != 'BLOCKED':
                raw['findings'] = []
            if verdict == 'INCOMPLETE':
                raw['identity'].update(selected_scope_coverage='partial', whole_pr_coverage='not-established',
                                       campaign_context_id=None, campaign_policy_id=None)
            else:
                raw['identity'].update(coverage='complete', whole_pr_coverage='complete')
            with self.subTest(verdict=verdict):
                document, parsed = report.render(raw)
                self.assertEqual(parsed['identity'], raw['identity'])
                self.assertIn('"execution_mode":"subagents"', document)
                self.assertIsNone(parsed['identity']['campaign_seed_thread_id'])

    def test_subagent_campaigns_cannot_claim_a_seed(self):
        for seed in ('seed-fixture', '', False):
            raw = sample()
            raw['identity'].update(execution_mode='subagents', campaign_seed_thread_id=seed)
            with self.subTest(seed=seed), self.assertRaises(ValueError):
                report.prepare(raw)

    def test_execution_mode_must_be_an_explicit_known_string(self):
        for value in (None, '', 'default', 'subagent', 'Fork', True, [], {}):
            raw = sample(); raw['identity']['execution_mode'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                report.prepare(raw)

    def test_regeneration_identity_stable_order_independent_fingerprints(self):
        raw = sample(); first = report.prepare(raw)
        raw['generated_at'] = '2026-09-29T17:00:00Z'; raw['findings'].reverse()
        second = report.prepare(raw)
        self.assertEqual(first['report_key'], second['report_key'])
        self.assertEqual({f['id']:f['fingerprint'] for f in first['findings']},
                         {f['id']:f['fingerprint'] for f in second['findings']})
        raw['findings'][0]['detail'] += ' New evidence.'
        self.assertNotEqual(report.prepare(raw)['findings'][-1]['fingerprint'], first['findings'][-1]['fingerprint'])
        raw['identity']['candidate'] = 'c' * 40
        self.assertNotEqual(report.prepare(raw)['report_key'], first['report_key'])

    def test_policy_is_explicit_and_historical_namespace_is_unchanged(self):
        raw = sample(); legacy = report.prepare(raw)
        self.assertEqual(legacy['report_key'],
                         'elenctic:53beaaa087831a215bffb395631cfedc928fde65dbd98d0fe9ad4a97b3730221')
        self.assertNotIn('merge_policy', legacy['identity'])
        keys = {legacy['report_key']}
        for policy in ('pragmatic', 'pedantic'):
            raw['identity']['merge_policy'] = policy
            parsed = report.prepare(raw)
            self.assertEqual(parsed['identity']['merge_policy'], policy)
            keys.add(parsed['report_key'])
            self.assertEqual([f['fingerprint'] for f in legacy['findings']],
                             [f['fingerprint'] for f in parsed['findings']])
        self.assertEqual(len(keys), 3)
        for value in (None, '', 'default', 'Pragmatic', True, [], {}):
            raw['identity']['merge_policy'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                report.prepare(raw)

    def test_policy_cannot_be_changed_or_stripped_on_regeneration(self):
        raw = sample(); raw['identity']['merge_policy'] = 'pragmatic'
        previous = report.prepare(raw)
        self.assertEqual(report.prepare(raw, previous=previous)['report_key'], previous['report_key'])
        for policy in ('pedantic', None):
            changed = deepcopy(raw)
            if policy is None:
                del changed['identity']['merge_policy']
            else:
                changed['identity']['merge_policy'] = policy
            with self.subTest(policy=policy), self.assertRaises(ValueError):
                report.prepare(changed, previous=previous)

    def test_execution_separates_campaign_namespaces_without_relabeling_legacy(self):
        legacy = report.prepare(sample())
        self.assertNotIn('execution_mode', legacy['identity'])
        keys = {legacy['report_key']}
        for execution in ('fork', 'subagents'):
            raw = sample(); raw['identity']['execution_mode'] = execution
            if execution == 'subagents':
                raw['identity']['campaign_seed_thread_id'] = None
            parsed = report.prepare(raw)
            self.assertEqual(parsed['identity']['execution_mode'], execution)
            self.assertEqual([f['fingerprint'] for f in parsed['findings']],
                             [f['fingerprint'] for f in legacy['findings']])
            keys.add(parsed['report_key'])
        self.assertEqual(len(keys), 3)

    def test_execution_cannot_be_changed_or_stripped_on_regeneration(self):
        for execution in (None, 'fork', 'subagents'):
            raw = sample()
            if execution is not None:
                raw['identity']['execution_mode'] = execution
            if execution == 'subagents':
                raw['identity']['campaign_seed_thread_id'] = None
            previous = report.prepare(raw)
            self.assertEqual(report.prepare(raw, previous=previous)['report_key'], previous['report_key'])
            for replacement in (None, 'fork', 'subagents'):
                if replacement == execution:
                    continue
                changed = deepcopy(raw)
                if replacement is None:
                    del changed['identity']['execution_mode']
                else:
                    changed['identity']['execution_mode'] = replacement
                if replacement == 'subagents':
                    changed['identity']['campaign_seed_thread_id'] = None
                with self.subTest(execution=execution, replacement=replacement), self.assertRaises(ValueError):
                    report.prepare(changed, previous=previous)

    def test_feedback_only_analysis_rejects_execution_mode(self):
        raw = sample()
        raw['workflow'] = 'construction'
        raw['identity'] = {field: raw['identity'][field] for field in ('repo', 'pr', 'base', 'candidate', 'view')}
        raw['identity'].update(schema='elenctic-construction-identity/v1', mode='analysis', analysis_id='analysis-1')
        raw['construction'] = {'status': 'unavailable', 'reason': 'No construction was selected.', 'adjudications': []}
        for number, finding in enumerate(raw['findings'], 1):
            finding['number'] = number
        self.assertNotIn('execution_mode', report.prepare(raw)['identity'])
        for execution in (None, 'fork', 'subagents'):
            raw['identity']['execution_mode'] = execution
            with self.subTest(execution=execution), self.assertRaises(ValueError):
                report.prepare(raw)

    def test_composition_binds_elenctic_source_policy_without_relabeling_other_owners(self):
        raw = composition_sample(); legacy = report.prepare(raw)
        keys = {legacy['report_key']}
        for policy in ('pragmatic', 'pedantic'):
            raw['identity']['assessments']['elenctic']['merge_policy'] = policy
            current = report.prepare(raw)
            self.assertEqual(current['identity']['assessments']['elenctic']['merge_policy'], policy)
            self.assertNotIn('merge_policy', current['identity'])
            keys.add(current['report_key'])
        self.assertEqual(len(keys), 1)
        for value in (None, 'default', []):
            raw['identity']['assessments']['elenctic']['merge_policy'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                report.prepare(raw)
        raw = composition_sample(); raw['identity']['merge_policy'] = 'pragmatic'
        with self.assertRaises(ValueError):
            report.prepare(raw)

    def test_composition_preserves_the_actual_elenctic_execution_source(self):
        raw = composition_sample(); legacy = report.prepare(raw)
        keys = {legacy['report_key']}
        for execution in ('fork', 'subagents'):
            raw['identity']['assessments']['elenctic']['execution_mode'] = execution
            current = report.prepare(raw)
            self.assertEqual(current['identity']['assessments']['elenctic']['execution_mode'], execution)
            self.assertNotIn('execution_mode', current['identity'])
            keys.add(current['report_key'])
        self.assertEqual(len(keys), 1)
        for value in (None, '', 'default', []):
            raw['identity']['assessments']['elenctic']['execution_mode'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                report.prepare(raw)
        raw = composition_sample(); raw['identity']['execution_mode'] = 'subagents'
        with self.assertRaises(ValueError):
            report.prepare(raw)

    def test_composition_cannot_change_or_strip_bound_execution_during_recovery(self):
        for execution in (None, 'fork', 'subagents'):
            raw = composition_sample()
            if execution is not None:
                raw['identity']['assessments']['elenctic']['execution_mode'] = execution
            previous = report.prepare(raw)
            self.assertEqual(report.prepare(raw, previous=previous)['report_key'], previous['report_key'])
            for replacement in (None, 'fork', 'subagents'):
                if replacement == execution:
                    continue
                changed = deepcopy(raw)
                source = changed['identity']['assessments']['elenctic']
                if replacement is None:
                    del source['execution_mode']
                else:
                    source['execution_mode'] = replacement
                with self.subTest(execution=execution, replacement=replacement), self.assertRaises(ValueError):
                    report.prepare(changed, previous=previous)

    def test_composition_allows_the_first_execution_source_to_arrive(self):
        previous_raw = composition_sample()
        previous_raw['identity'].update(assessments={}, selected_scope_coverage='partial',
                                        whole_pr_coverage='not-established', verdict='INCOMPLETE')
        previous_raw['findings'] = []
        previous = report.prepare(previous_raw)
        for execution in ('fork', 'subagents'):
            current = composition_sample()
            current['identity']['assessments']['elenctic']['execution_mode'] = execution
            with self.subTest(execution=execution):
                self.assertEqual(report.prepare(current, previous=previous)['report_key'], previous['report_key'])

    def test_disposition_changes_reopen_finding_evidence_within_bound_policy(self):
        raw = sample(); raw['identity']['merge_policy'] = 'pragmatic'
        old = report.prepare(raw)
        raw['findings'][0].update(disposition='risk', draft='',
                                  detail='Established edge failure retained as nonblocking under the bound policy.')
        raw['identity']['verdict'] = 'APPROVE'
        new = report.prepare(raw, previous=old)
        self.assertEqual(old['report_key'], new['report_key'])
        self.assertNotEqual(old['findings'][0]['fingerprint'], new['findings'][0]['fingerprint'])

    def test_atomic_private_output_and_cross_campaign_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.html'
            report.write_report(sample(), path)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            report.write_report(sample(), path)
            raw = sample(); raw['identity']['campaign_id'] = 'another-campaign'
            with self.assertRaises(ValueError): report.write_report(raw, path)
            target = Path(directory) / 'link.html'; target.symlink_to(path)
            with self.assertRaises(ValueError): report.write_report(sample(), target)


NODE = shutil.which('node') or shutil.which(os.environ.get('CODEX_PRIMARY_RUNTIME_NODE', ''))


@unittest.skipUnless(NODE, 'Node unavailable; controlled storage checks unrun')
class StorageScriptTests(unittest.TestCase):
    """Production storage functions/startup with controlled stores; no browser claims."""

    def startup(self, local, session, *, local_failure=None):
        payload = report.prepare(sample())
        result = subprocess.run([NODE, '-e', r'''
          const fs = require('node:fs');
          const input = JSON.parse(fs.readFileSync(0, 'utf8'));
          const html = fs.readFileSync(process.argv[1], 'utf8');
          const start = html.indexOf('  const report = JSON.parse(');
          const end = html.indexOf('  function update(finding, changes) {');
          const initialization = html.match(/\n  (?:status|persist)\(\); setView\(viewMode\);\n/);
          if (start < 0 || end < start || !initialization) throw new Error('Storage harness source boundary changed');
          const node = {textContent:'', classList:{toggle(){}}};
          const document = {getElementById(id) {
            if (id === 'report-data') return {textContent:JSON.stringify(input.report)};
            if (id === 'initial-state') return {textContent:'null'};
            if (id === 'storage') return node;
            throw new Error('Unexpected UI access: ' + id);
          }};
          function storage(items, failure) {
            return {
              getItem:k => items[k] ?? null,
              setItem(k,v) {
                if (failure === 'unavailable') throw new Error('Unavailable');
                if (!k.endsWith(':probe')) {
                  if (failure === 'write') throw new Error('Unavailable');
                  if (failure === 'readback') return;
                }
                items[k] = v;
              },
              removeItem:k => { delete items[k]; }
            };
          }
          const window = {localStorage:storage(input.local, input.local_failure),
                          sessionStorage:storage(input.session)};
          // UI rendering is stubbed; execute the checked-in initialization call,
          // including whether it persists the merged payload before its notice.
          const execute = new Function('window', 'document', html.slice(start,end) +
            '\nfunction setView() {}\n' + initialization[0] +
            '\nreturn {mode, state, notice:document.getElementById("storage").textContent};');
          console.log(JSON.stringify({...execute(window,document), local:input.local, session:input.session}));
        ''', str(SKILL / 'assets/report.html')], input=json.dumps({
            'report': payload, 'local': local, 'session': session, 'local_failure': local_failure,
        }), capture_output=True, text=True, check=True, timeout=10)
        return json.loads(result.stdout)

    def progress(self, checked, updated, note):
        payload = report.prepare(sample()); finding = payload['findings'][0]
        return {payload['report_key'] + ':handling': json.dumps({
            'schema': 'elenctic-handling/v1', 'report_key': payload['report_key'],
            'entries': {finding['id']: {'checked': checked, 'updated': updated,
                                       'note': note, 'fingerprint': finding['fingerprint']}}})}

    def test_current_local_progress_survives_a_new_session(self):
        saved = self.progress(True, 20, 'Already saved locally')
        opened = self.startup(saved, {})
        reopened = self.startup(opened['local'], {})
        self.assertEqual(reopened['state'], opened['state'])
        self.assertEqual(reopened['mode'], 'local')

    def test_recovered_local_store_saves_newer_session_progress_without_an_edit(self):
        older = self.progress(False, 10, 'Old local note')
        newer = self.progress(True, 20, 'Latest fallback note')
        failed = self.startup(older, newer, local_failure='unavailable')
        self.assertEqual(failed['mode'], 'session')
        recovered = self.startup(failed['local'], failed['session'])
        self.assertEqual(recovered['mode'], 'local')
        self.assertIn('Autosaved', recovered['notice'])
        # No edit or import occurs before the tab closes and its session ends.
        reopened = self.startup(recovered['local'], {})
        self.assertEqual(reopened['state'], recovered['state'])
        self.assertEqual(reopened['state']['entries']['f-cancel']['note'], 'Latest fallback note')
        self.assertTrue(reopened['state']['entries']['f-cancel']['checked'])

    def test_startup_requires_payload_readback_before_claiming_local_persistence(self):
        older = self.progress(False, 10, 'Old local note')
        newer = self.progress(True, 20, 'Latest fallback note')
        opened = self.startup(older, newer, local_failure='readback')
        self.assertEqual(opened['mode'], 'session')
        self.assertIn('Session storage only', opened['notice'])
        self.assertTrue(opened['state']['entries']['f-cancel']['checked'])
        self.assertEqual(json.loads(next(iter(opened['session'].values()))), opened['state'])


if __name__ == '__main__':
    unittest.main()
