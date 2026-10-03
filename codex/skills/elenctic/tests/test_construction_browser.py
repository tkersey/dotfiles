"""Default: file URLs. ELENCTIC_TEST_HTTP=1 is loopback diagnostic evidence only."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import threading
import os
from pathlib import Path
import tempfile
import unittest

from test_construction import report, sample
from test_report import sample as comments_sample
from test_resolution import sample as resolution_sample

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


@unittest.skipUnless(sync_playwright, 'Playwright is not installed; browser checks unrun')
class ConstructionBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = sync_playwright().start()
        cls.browser = cls.runtime.chromium.launch(executable_path=os.environ.get('ELENCTIC_CHROMIUM'),
                                                  headless=True, args=['--no-sandbox'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close(); cls.runtime.stop()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'report.html'
        self.raw = sample(); report.write_report(self.raw, self.path)
        self.context = self.browser.new_context(accept_downloads=True); self.addCleanup(self.context.close)
        self.page = self.context.new_page()
        self.errors, self.requests = [], []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.on('request', lambda request: self.requests.append(request.url))
        self.server = None
        if os.environ.get('ELENCTIC_TEST_HTTP') == '1':
            handler = partial(SimpleHTTPRequestHandler, directory=self.temp.name)
            self.server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
            threading.Thread(target=self.server.serve_forever, daemon=True).start()
            self.addCleanup(self.server.server_close); self.addCleanup(self.server.shutdown)
        self.page.goto(self.url(self.path))

    def url(self, path):
        if self.server:
            return f'http://127.0.0.1:{self.server.server_port}/{path.name}'
        return path.as_uri()

    def tearDown(self):
        self.assertEqual(self.errors, [])
        self.assertFalse(any(url.startswith(('http:', 'https:')) and not url.startswith('http://127.0.0.1:') for url in self.requests))

    def test_proposals_and_original_references_without_a_review_verdict(self):
        self.assertEqual(self.page.locator('#verdict').inner_text(), 'No review verdict')
        self.assertEqual(self.page.locator('#show-groups').inner_text(), 'Change proposals')
        self.assertTrue(self.page.locator('#resolution-groups').is_visible())
        self.assertEqual(self.page.locator('.finding').count(), 4)
        self.assertIn('commitTerminal', self.page.locator('#resolution-R1 .proposal').inner_text())
        self.assertIn('unresolved', self.page.locator('#resolution-R2 .proposal').inner_text())
        self.assertIn('not implemented or verified', self.page.locator('#resolution-status').inner_text())
        self.assertNotIn('undefined', self.page.locator('body').inner_text())
        self.assertEqual(self.page.locator('#adjudication-entries > section').count(), 5)
        self.page.locator('#search').fill('commitTerminal')
        self.assertEqual(self.page.locator('.finding:visible').count(), 3)

    def test_same_handling_state_in_both_views_and_after_proposal_revision(self):
        check = self.page.locator('#finding-f-cancel input[type=checkbox]')
        note = self.page.locator('#finding-f-cancel textarea')
        check.check(); note.fill('Investigating the owner transition; not verified fixed.')
        self.page.get_by_role('button', name='Original findings', exact=True).click()
        self.assertTrue(check.is_checked())
        self.raw['construction']['groups'][0]['proposal']['migration'] += ' Include one more documented adapter.'
        report.write_report(self.raw, self.path); self.page.reload()
        self.assertTrue(check.is_checked())
        self.assertIn('Investigating', note.input_value())
        self.raw['findings'][0]['detail'] += ' Newly established bypass.'
        report.write_report(self.raw, self.path); self.page.reload()
        self.assertFalse(check.is_checked())
        self.assertIn('Investigating', note.input_value())
        self.assertTrue(self.page.locator('#finding-f-cancel .changed').is_visible())

    def test_handoff_contains_selected_changes_limits_and_evidence_on_clipboard_failure(self):
        self.page.evaluate("Object.defineProperty(navigator, 'clipboard', {configurable:true, value:{writeText:async()=>{throw new Error('denied')}}})")
        self.page.get_by_role('button', name='Copy R1 handoff', exact=True).click()
        handoff = self.page.locator('#resolution-R1 .handoff')
        self.assertTrue(handoff.is_visible())
        for text in ('#2', '#5', '#8', 'src/queue.ts', 'commitTerminal', 'Retirements',
                     'Inspected head:', 'Analysis: analysis-fixture', 'not implemented or verified',
                     'Obtain explicit implementation authority', 'A1: accepted', 'External'):
            self.assertIn(text.lower(), handoff.inner_text().lower())
        self.assertNotIn('Campaign: undefined', handoff.inner_text())

    def test_portable_copy_preserves_proposals_checks_and_single_feedback_inventory(self):
        self.page.locator('#finding-f-cancel input[type=checkbox]').check()
        self.page.locator('#finding-f-cancel textarea').fill('Portable handling note')
        with self.page.expect_download() as download:
            self.page.get_by_role('button', name='Save portable copy').click()
        path = Path(self.temp.name) / 'portable.html'; download.value.save_as(path)
        self.page.goto(self.url(path))
        self.assertTrue(self.page.locator('#finding-f-cancel input[type=checkbox]').is_checked())
        self.assertEqual(self.page.locator('#finding-f-cancel textarea').input_value(), 'Portable handling note')
        self.assertEqual(self.page.locator('#adjudication-entries > section').count(), 5)
        self.assertEqual(self.page.locator('.resolution-group').count(), 2)
        self.assertIn('commitTerminal', self.page.locator('#resolution-R1 .proposal').inner_text())
        self.page.reload()
        self.assertEqual(self.page.locator('#adjudication-entries > section').count(), 5)

    def test_refuted_feedback_stays_visible_without_a_fake_fix_or_approval(self):
        self.raw['findings'] = []; self.raw['construction']['groups'] = []
        self.raw['construction']['adjudications'] = [self.raw['construction']['adjudications'][-1]]
        report.write_report(self.raw, self.path); self.page.reload()
        self.assertIn('rejected', self.page.locator('#adjudication-entries').inner_text())
        self.assertTrue(self.page.locator('#adjudication-entries').is_visible())
        self.assertEqual(self.page.locator('.finding').count(), 0)
        self.assertEqual(self.page.locator('#verdict').inner_text(), 'No review verdict')
        self.assertIn('not PR approval', self.page.locator('#empty').inner_text())

    def test_unavailable_construction_does_not_hide_supported_findings(self):
        self.raw['construction'] = {'status': 'unavailable', 'reason': 'Installed Actuating unreadable.', 'adjudications': []}
        report.write_report(self.raw, self.path); self.page.reload()
        self.assertIn('unavailable', self.page.locator('#resolution-status').inner_text())
        self.assertEqual(self.page.locator('.finding:visible').count(), 4)
        self.assertTrue(self.page.get_by_role('button', name='Change proposals').is_disabled())

    def test_untrusted_source_and_proposal_text_remain_inert(self):
        attack = '</script><img src=https://invalid.example onerror="window.pwned=1">'
        self.raw['construction']['groups'][0]['proposal']['changes'][0]['change'] = attack
        self.raw['construction']['adjudications'][0]['claim'] = attack
        report.write_report(self.raw, self.path); self.page.reload()
        self.assertIn(attack, self.page.locator('#resolution-R1 .proposal').inner_text())
        self.assertEqual(self.page.locator('img').count(), 0)
        self.assertIsNone(self.page.evaluate('window.pwned'))

    def test_new_analysis_head_and_foreign_import_cannot_transfer_progress(self):
        self.page.locator('#finding-f-cancel input[type=checkbox]').check()
        with self.page.expect_download() as download:
            self.page.get_by_role('button', name='Export progress', exact=True).click()
        state = Path(self.temp.name) / 'progress.json'; download.value.save_as(state)
        self.raw['identity']['candidate'] = 'c' * 40
        new_path = Path(self.temp.name) / 'new-head.html'; report.write_report(self.raw, new_path)
        self.page.goto(self.url(new_path))
        self.assertFalse(self.page.locator('#finding-f-cancel input[type=checkbox]').is_checked())
        self.page.locator('#import-file').set_input_files(state)
        self.page.wait_for_function("document.getElementById('message').textContent.includes('another campaign')")
        self.assertIn('another campaign', self.page.locator('#message').inner_text())
        self.assertFalse(self.page.locator('#finding-f-cancel input[type=checkbox]').is_checked())

    def test_existing_comment_and_resolution_views_keep_their_decisions(self):
        for index, raw in enumerate((comments_sample(), resolution_sample())):
            path = Path(self.temp.name) / f'legacy-{index}.html'; report.write_report(raw, path)
            self.page.goto(self.url(path))
            self.assertEqual(self.page.locator('#verdict').inner_text(), 'BLOCKED')
            self.assertFalse(self.page.locator('#construction-adjudications').is_visible())
            self.assertEqual(self.page.locator('.finding').count(), len(raw['findings']))
            if index == 1:
                self.assertEqual(self.page.locator('#show-groups').inner_text(), 'Resolution groups')
                self.assertTrue(self.page.locator('#resolution-groups').is_visible())


if __name__ == '__main__':
    unittest.main()
