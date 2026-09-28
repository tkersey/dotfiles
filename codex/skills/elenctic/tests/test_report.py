"""Presentation and persistence contracts. These do not evaluate model judgment."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
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


if __name__ == '__main__':
    unittest.main()
