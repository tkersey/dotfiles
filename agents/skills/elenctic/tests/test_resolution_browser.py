"""Chromium DOM checks with controlled storage; optional native file qualification."""
import json
import os
from pathlib import Path
import tempfile
import unittest

from test_resolution import report, sample

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


@unittest.skipUnless(sync_playwright, 'Playwright unavailable; browser checks unrun')
class BrowserCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = sync_playwright().start()
        cls.browser = cls.runtime.chromium.launch(executable_path=os.environ.get('ELENCTIC_CHROMIUM'),
                                                  headless=True, args=['--no-sandbox'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close(); cls.runtime.stop()


@unittest.skipUnless(sync_playwright, 'Playwright unavailable; browser checks unrun')
class ResolutionDomTests(BrowserCase):
    def page(self, raw=None, saved=None, storage='local'):
        page = self.browser.new_page(viewport={'width': 1440, 'height': 1080})
        self.addCleanup(page.close)
        errors = []; requests = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: requests.append(request.url))
        self.addCleanup(lambda: self.assertEqual(errors, []))
        self.addCleanup(lambda: self.assertEqual(requests, []))
        page.evaluate('''({saved, storage}) => {
          window.testStores = saved || {local:{},session:{}};
          for (const [name, property] of [['local','localStorage'],['session','sessionStorage']]) {
            const items = testStores[name];
            Object.defineProperty(window,property,{value:{
              getItem:k=>items[k]??null,
              setItem:(k,v)=>{if(storage==='none'||(name==='local'&&storage==='session')) throw Error('Fixture storage failure');items[k]=v;},
              removeItem:k=>{delete items[k]}
            }});
          }
          Object.defineProperty(navigator,'clipboard',{value:{writeText:async text=>{window.copied=text;}}});
        }''', {'saved': saved, 'storage': storage})
        page.set_content(report.render(raw or sample())[0])
        return page

    def test_group_view_uses_original_numbers_and_single_finding_controls(self):
        page = self.page()
        self.assertEqual(page.locator('#show-groups').get_attribute('aria-pressed'), 'true')
        self.assertEqual(page.locator('#resolution-R1 .finding h3').all_text_contents(), [
            '#2 · Cancellation acknowledges before effects stop',
            '#5 · Recovery can admit duplicate work', '#8 · Clarify the pending outcome example'])
        self.assertEqual(page.get_by_role('checkbox').count(), 4)
        self.assertIn('Concerns', page.locator('#resolution-R1 .completion-list').inner_text())
        self.assertIn('Optional:', page.locator('#resolution-R1 .completion-list').inner_text())

    def test_switching_views_and_reconstructing_page_preserves_progress(self):
        page = self.page(); check = page.get_by_role('checkbox').first
        check.focus(); page.keyboard.press('Space')
        page.get_by_role('textbox').first.fill('Implementation done; verification pending')
        self.assertIn('1 of 3 handled', page.locator('#resolution-R1 .group-progress').inner_text())
        page.get_by_role('button', name='Original findings', exact=True).click()
        self.assertTrue(page.get_by_role('checkbox').first.is_checked())
        self.assertEqual(page.locator('#findings article').count(), 4)
        page.get_by_role('button', name='Resolution groups', exact=True).click()
        self.assertEqual(page.get_by_role('checkbox').count(), 4)
        restored = self.page(saved=page.evaluate('window.testStores'))
        self.assertTrue(restored.get_by_role('checkbox').first.is_checked())
        self.assertEqual(restored.get_by_role('textbox').first.input_value(), 'Implementation done; verification pending')
        self.assertEqual(restored.locator('#verdict').inner_text(), 'BLOCKED')

    def test_group_search_and_status_filters_keep_numbers(self):
        page = self.page(); page.get_by_role('checkbox').first.check()
        page.locator('#search').fill('R1'); page.locator('#status').select_option('open')
        self.assertEqual(page.locator('article:visible').count(), 2)
        self.assertEqual(page.locator('article:visible h3').all_text_contents(), [
            '#5 · Recovery can admit duplicate work', '#8 · Clarify the pending outcome example'])
        self.assertIn('1 of 3 handled · 2 shown', page.locator('#resolution-R1 .group-progress').inner_text())
        page.get_by_role('button', name='Clear filters').click()
        page.locator('#search').fill('#11')
        self.assertEqual(page.locator('.resolution-group:visible').count(), 1)
        self.assertTrue(page.locator('#resolution-R2').is_visible())

    def test_member_and_dependency_navigation_reveals_filtered_targets(self):
        page = self.page(); page.locator('#search').fill('R2')
        page.locator('#resolution-R2').get_by_role('link', name='R1', exact=True).click()
        self.assertTrue(page.locator('#resolution-R1').is_visible())
        self.assertEqual(page.locator('#search').input_value(), '')
        page.locator('#resolution-R1 .links').first.get_by_role('link', name='#8', exact=True).click()
        self.assertEqual(page.evaluate('document.activeElement.id'), 'finding-f-docs')

    def test_handoff_contains_canonical_members_and_full_evidence(self):
        page = self.page(); page.get_by_role('button', name='Copy R1 handoff', exact=True).click()
        page.wait_for_function('window.copied !== undefined')
        copied = page.evaluate('window.copied')
        for value in ['Address R1', 'Original findings: #2, #5, #8.', 'Reviewed head: ' + 'b'*40,
                      'Completion evidence:', 'Optional:', 'Nonblocking follow-ups remain optional.',
                      'Original eligible draft (not posted):', 'Existing discussion:']:
            self.assertIn(value, copied)
        self.assertNotIn('#11', copied)
        self.assertEqual(page.locator('#verdict').inner_text(), 'BLOCKED')

    def test_clipboard_failure_reveals_copyable_handoff(self):
        page = self.page()
        page.evaluate("() => {navigator.clipboard.writeText=async()=>{throw Error('denied')};}")
        page.get_by_role('button', name='Copy R1 handoff').click()
        page.wait_for_function("document.getElementById('message').textContent.includes('Clipboard unavailable')")
        self.assertTrue(page.locator('#resolution-R1 .handoff').is_visible())

    def test_portable_copy_rebuilds_one_workspace_with_embedded_progress(self):
        page = self.page(); page.get_by_role('checkbox').first.check()
        page.get_by_role('textbox').first.fill('Saved </script> & note')
        page.evaluate('''() => {
          URL.createObjectURL=blob=>{window.savedBlob=blob;return 'blob:fixture';};
          HTMLAnchorElement.prototype.click=function(){};
        }''')
        page.get_by_role('button', name='Save portable copy').click()
        portable = page.evaluate('window.savedBlob.text()')
        restored = self.browser.new_page(); self.addCleanup(restored.close)
        restored.set_content(portable)
        self.assertTrue(restored.get_by_role('checkbox').first.is_checked())
        self.assertEqual(restored.get_by_role('textbox').first.input_value(), 'Saved </script> & note')
        self.assertEqual(restored.locator('.resolution-group').count(), 2)
        self.assertEqual(restored.get_by_role('checkbox').count(), 4)
        self.assertEqual(restored.locator('#empty').count(), 1)
        self.assertEqual(restored.locator('#categories button').count(), 4)
        self.assertIn('1 of 3 handled', restored.locator('#resolution-R1 .group-progress').inner_text())

    def test_regrouping_keeps_checks_while_changed_evidence_reopens_one(self):
        raw = sample(); page = self.page(raw); page.get_by_role('checkbox').first.check()
        page.get_by_role('textbox').first.fill('Keep this note')
        saved = page.evaluate('window.testStores')
        raw['resolution']['groups'][0]['title'] = 'Refined unit title'; raw['resolution']['groups'].reverse()
        restored = self.page(raw, saved)
        self.assertTrue(restored.locator('#finding-f-cancel input').is_checked())
        raw['findings'][0]['detail'] += ' New material evidence.'
        changed = self.page(raw, saved)
        self.assertFalse(changed.locator('#finding-f-cancel input').is_checked())
        self.assertEqual(changed.locator('#finding-f-cancel textarea').input_value(), 'Keep this note')
        self.assertTrue(changed.locator('#finding-f-cancel .changed').is_visible())

    def test_storage_fallback_and_import_keep_group_counts_derived(self):
        page = self.page(storage='session'); page.get_by_role('checkbox').first.check()
        self.assertIn('Session storage only', page.locator('#storage').inner_text())
        saved = page.evaluate('window.testStores')
        restored = self.page(saved=saved, storage='session')
        self.assertTrue(restored.get_by_role('checkbox').first.is_checked())
        progress = json.loads(next(value for key, value in saved['session'].items() if key.endswith(':handling')))
        self.assertNotIn('groups', progress)
        target = self.page(); target.locator('#import-file').set_input_files({
            'name':'progress.json', 'mimeType':'application/json', 'buffer':json.dumps(progress).encode()})
        target.wait_for_function("document.getElementById('message').textContent.includes('Progress merged')")
        self.assertIn('1 of 3 handled', target.locator('#resolution-R1 .group-progress').inner_text())
        wrong = {**progress, 'report_key':'other-campaign'}
        target.locator('#import-file').set_input_files({'name':'wrong.json', 'mimeType':'application/json', 'buffer':json.dumps(wrong).encode()})
        target.wait_for_function("document.getElementById('message').textContent.includes('another campaign')")
        self.assertTrue(target.get_by_role('checkbox').first.is_checked())

    def test_default_and_unavailable_modes_have_no_group_side_effects(self):
        raw = sample(); raw['workflow'] = 'comments'; raw.pop('resolution')
        default = self.page(raw)
        self.assertTrue(default.locator('#resolution-controls').is_hidden())
        self.assertEqual(default.locator('.resolution-group').count(), 0)
        self.assertEqual(default.locator('#findings article').count(), 4)
        raw = sample(); raw['resolution'] = {'status':'unavailable', 'reason':'Helper source inaccessible.'}
        blocked = self.page(raw)
        self.assertIn('Helper source inaccessible', blocked.locator('#resolution-status').inner_text())
        self.assertTrue(blocked.locator('#show-groups').is_disabled())
        self.assertEqual(blocked.locator('#verdict').inner_text(), 'BLOCKED')
        self.assertEqual(blocked.get_by_role('checkbox').count(), 4)

    def test_empty_incomplete_and_hostile_group_text_remain_honest_and_inert(self):
        raw = sample(); raw['findings'] = []; raw['resolution']['groups'] = []
        raw['identity'].update(verdict='INCOMPLETE', selected_scope_coverage='partial')
        page = self.page(raw)
        self.assertIn('not approval', page.locator('#empty').inner_text())
        raw = sample(); attack = '</script><img src=x onerror="window.pwned=1">'
        raw['resolution']['groups'][0]['title'] = attack
        raw['resolution']['groups'][0]['completion_checks'][0]['evidence'] = attack
        hostile = self.page(raw)
        self.assertEqual(hostile.locator('img,svg').count(), 0)
        self.assertIsNone(hostile.evaluate('window.pwned'))
        self.assertIn(attack, hostile.locator('#resolution-R1 h2').inner_text())

    def test_print_preserves_findings_hidden_by_screen_filters(self):
        page = self.page(); page.locator('#search').fill('R2')
        self.assertEqual(page.locator('article:visible').count(), 1)
        page.emulate_media(media='print')
        self.assertEqual(page.locator('article:visible').count(), 4)
        self.assertEqual(page.locator('.resolution-group:visible').count(), 2)

    def test_mobile_layout_has_no_horizontal_overflow(self):
        page = self.page(); page.set_viewport_size({'width':390, 'height':844})
        self.assertTrue(page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
        page.get_by_role('button', name='Original findings', exact=True).click()
        self.assertTrue(page.evaluate('document.documentElement.scrollWidth <= innerWidth'))


@unittest.skipUnless(sync_playwright and os.environ.get('ELENCTIC_NATIVE_BROWSER') == '1',
                     'Native file-origin qualification not selected; DOM tests are not its substitute')
class NativeResolutionTests(BrowserCase):
    """Actual file refresh, regeneration and downloaded portable reopening."""
    def test_native_refresh(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.html'; raw = sample(); report.write_report(raw, path)
            with self.browser.new_context(accept_downloads=True) as context:
                page = context.new_page(); page.goto(path.as_uri())
                page.get_by_role('checkbox').first.check(); page.get_by_role('textbox').first.fill('Native persisted note')
                page.reload(); self.assertTrue(page.get_by_role('checkbox').first.is_checked())
                self.assertEqual(page.get_by_role('textbox').first.input_value(), 'Native persisted note')
                raw['resolution']['groups'][0]['title'] = 'Regrouped title'; report.write_report(raw, path)
                page.reload(); self.assertTrue(page.get_by_role('checkbox').first.is_checked())
                with page.expect_download() as download:
                    page.get_by_role('button', name='Save portable copy').click()
                portable = Path(directory) / 'portable.html'; download.value.save_as(portable)
            with self.browser.new_context() as fresh:
                page = fresh.new_page(); page.goto(portable.as_uri())
                self.assertTrue(page.get_by_role('checkbox').first.is_checked())
                self.assertEqual(page.locator('.resolution-group').count(), 2)


if __name__ == '__main__':
    unittest.main()
