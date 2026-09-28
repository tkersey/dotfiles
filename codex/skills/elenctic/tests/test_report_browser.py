"""Browser interactions. Default: file URLs. ELENCTIC_TEST_HTTP=1 is loopback-only diagnostic evidence, NOT file-origin qualification."""
from __future__ import annotations

import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import threading
import os
from pathlib import Path
import tempfile
import unittest

from test_report import report, sample

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


@unittest.skipUnless(sync_playwright, 'Playwright is not installed; browser checks unrun')
class BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = sync_playwright().start()
        executable = os.environ.get('ELENCTIC_CHROMIUM')
        cls.browser = cls.runtime.chromium.launch(executable_path=executable, headless=True, args=['--no-sandbox'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close(); cls.runtime.stop()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'report.html'
        self.raw = sample(); report.write_report(self.raw, self.path)
        self.server = None
        if os.environ.get('ELENCTIC_TEST_HTTP') == '1':
            handler = partial(SimpleHTTPRequestHandler, directory=self.temp.name)
            self.server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
            threading.Thread(target=self.server.serve_forever, daemon=True).start()
            self.addCleanup(self.server.server_close)
            self.addCleanup(self.server.shutdown)
        self.context = self.browser.new_context(accept_downloads=True)
        self.addCleanup(self.context.close)
        self.page = self.context.new_page()
        self.errors = []; self.requests = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.on('request', lambda request: self.requests.append(request.url))
        self.page.goto(self.url(self.path))

    def tearDown(self):
        self.assertEqual(self.errors, [])
        self.assertFalse(any(u.startswith(('http:', 'https:')) and not u.startswith('http://127.0.0.1:') for u in self.requests))

    def url(self, path):
        if self.server:
            return f'http://127.0.0.1:{self.server.server_port}/{path.name}'
        return path.as_uri()

    def check(self):
        return self.page.get_by_role('checkbox').first

    def notes(self):
        return self.page.get_by_role('textbox', name='Handling notes: Cancellation acknowledges before the worker stops')

    def test_checks_notes_refresh_and_reopen(self):
        self.check().check(); self.notes().fill('Fixed in commit abc; awaiting verification.')
        self.page.reload()
        self.assertTrue(self.check().is_checked())
        self.assertEqual(self.notes().input_value(), 'Fixed in commit abc; awaiting verification.')
        self.page.close(); self.page = self.context.new_page(); self.page.goto(self.url(self.path))
        self.assertTrue(self.check().is_checked())
        self.assertEqual(self.page.locator('#verdict').inner_text(), 'BLOCKED')
        self.assertIn('Autosaved', self.page.locator('#storage').inner_text())

    def test_filter_search_and_keyboard_checkbox(self):
        self.check().focus(); self.page.keyboard.press('Space')
        self.page.locator('#status').select_option('open')
        self.assertEqual(self.page.locator('article:visible').count(), 2)
        self.page.locator('#search').fill('grace period')
        self.assertEqual(self.page.locator('article:visible').count(), 1)
        self.page.get_by_role('button', name='Clear filters').click()
        self.assertEqual(self.page.locator('article:visible').count(), 3)
        self.page.get_by_role('button', name='Concerns').click()
        self.assertEqual(self.page.locator('article:visible').count(), 1)

    def test_changed_finding_reopens_but_keeps_notes(self):
        self.check().check(); self.notes().fill('Original handling note')
        self.raw['findings'][0]['detail'] += ' Newly verified cancellation path.'
        report.write_report(self.raw, self.path); self.page.reload()
        self.assertFalse(self.check().is_checked())
        self.assertEqual(self.notes().input_value(), 'Original handling note')
        self.assertTrue(self.page.locator('.changed').first.is_visible())

    def test_portable_copy_reopens_with_embedded_progress(self):
        self.check().check(); self.notes().fill('Portable </script> & note')
        with self.page.expect_download() as download:
            self.page.get_by_role('button', name='Save portable copy').click()
        copy = Path(self.temp.name) / 'portable.html'; download.value.save_as(copy)
        # New browser context has no saved state: persistence must come from the file.
        with self.browser.new_context() as fresh:
            page = fresh.new_page(); page.goto(self.url(copy))
            self.assertTrue(page.get_by_role('checkbox').first.is_checked())
            self.assertEqual(page.get_by_role('textbox', name='Handling notes: Cancellation acknowledges before the worker stops').input_value(), 'Portable </script> & note')
            self.assertEqual(page.locator('#categories button').count(), 4)

    def test_storage_denied_is_explicit_and_portable_still_works(self):
        self.page.add_init_script("for (const key of ['localStorage','sessionStorage']) Object.defineProperty(window,key,{get(){throw new DOMException('Denied','SecurityError')}})")
        self.page.reload(); self.check().check()
        self.assertIn('Not saved', self.page.locator('#storage').inner_text())
        with self.page.expect_download() as download:
            self.page.get_by_role('button', name='Save portable copy').click()
        copy = Path(self.temp.name) / 'denied-copy.html'; download.value.save_as(copy)
        self.page.goto(self.url(copy)); self.assertTrue(self.check().is_checked())

    def test_session_fallback_survives_refresh(self):
        self.page.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new DOMException('Denied','SecurityError')}})")
        self.page.reload(); self.check().check(); self.page.reload()
        self.assertTrue(self.check().is_checked())
        self.assertIn('Session storage only', self.page.locator('#storage').inner_text())

    def test_export_import_rejects_wrong_campaign_without_erasure(self):
        self.check().check()
        with self.page.expect_download() as download:
            self.page.get_by_role('button', name='Export progress').click()
        backup = Path(self.temp.name) / 'progress.json'; download.value.save_as(backup)
        data = json.loads(backup.read_text()); data['report_key'] = 'another-campaign'
        wrong = Path(self.temp.name) / 'wrong.json'; wrong.write_text(json.dumps(data))
        self.page.locator('#import-file').set_input_files(wrong)
        self.page.wait_for_function("document.getElementById('message').textContent.includes('another campaign')")
        self.assertTrue(self.check().is_checked())
        self.page.evaluate('localStorage.clear()'); self.page.reload()
        self.page.locator('#import-file').set_input_files(backup)
        self.page.wait_for_function("document.getElementById('message').textContent.includes('Progress merged')")
        self.assertTrue(self.check().is_checked())

    def test_adversarial_text_and_object_keys_are_inert(self):
        self.raw['findings'][0]['id'] = 'constructor'
        self.raw['findings'][0]['title'] = '</script><img src=x onerror="window.pwned=1"> __REPORT_TEXT__'
        self.raw['report_text'] = '"__REPORT_DATA__" <svg/onload="window.pwned=1">'
        report.write_report(self.raw, self.path); self.page.reload(); self.check().check(); self.page.reload()
        self.assertTrue(self.check().is_checked())
        self.assertIsNone(self.page.evaluate('window.pwned'))
        self.assertEqual(self.page.locator('img,svg').count(), 0)
        self.assertIn('__REPORT_TEXT__', self.page.locator('h3').first.inner_text())

    def test_other_tab_updates_distinct_findings(self):
        second = self.context.new_page(); second.goto(self.url(self.path))
        self.check().check(); second.get_by_role('checkbox').nth(1).check()
        self.page.reload()
        self.assertTrue(self.check().is_checked())
        self.assertTrue(self.page.get_by_role('checkbox').nth(1).is_checked())

    def test_empty_incomplete_is_not_vacuous_approval(self):
        self.raw['findings'] = []; self.raw['identity'].update(verdict='INCOMPLETE', selected_scope_coverage='partial')
        report.write_report(self.raw, self.path); self.page.reload()
        self.assertIn('not approval', self.page.locator('#empty').inner_text())
        self.assertEqual(self.page.get_by_role('checkbox').count(), 0)

    def test_mobile_has_no_horizontal_overflow(self):
        self.page.set_viewport_size({'width':390, 'height':844})
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'))


if __name__ == '__main__':
    unittest.main()
