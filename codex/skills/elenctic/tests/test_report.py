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
