"""Actual browser DOM with controlled storage fixtures; NOT file-origin persistence proof."""
import json
import os
import unittest

from test_report import report, sample

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


@unittest.skipUnless(sync_playwright, 'Playwright unavailable; DOM checks unrun')
class DomTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = sync_playwright().start()
        cls.browser = cls.runtime.chromium.launch(executable_path=os.environ.get('ELENCTIC_CHROMIUM'),
                                                  headless=True, args=['--no-sandbox'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close(); cls.runtime.stop()

    def page(self, raw=None, stored=None):
        page = self.browser.new_page(viewport={'width':1440, 'height':1000})
        page.evaluate('''items => {
          window.testItems=items;
          Object.defineProperty(window,'localStorage',{value:{
            getItem:k=>items[k]??null,setItem:(k,v)=>{items[k]=v},removeItem:k=>{delete items[k]}
          }});
        }''', stored or {})
        page.set_content(report.render(raw or sample())[0])
        return page

    def test_check_note_state_roundtrip_filters_and_mobile(self):
        page = self.page()
        page.get_by_role('checkbox').first.check()
        page.get_by_role('textbox').first.fill('Handled; await verification')
        saved = page.evaluate('window.testItems')
        page.locator('#status').select_option('open')
        self.assertEqual(page.locator('article:visible').count(), 2)
        page.locator('#search').fill('grace period')
        self.assertEqual(page.locator('article:visible').count(), 1)
        page.get_by_role('button', name='Clear filters').click()
        page.set_viewport_size({'width':390,'height':844})
        self.assertTrue(page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
        restored = self.page(stored=saved)
        self.assertTrue(restored.get_by_role('checkbox').first.is_checked())
        self.assertEqual(restored.get_by_role('textbox').first.input_value(), 'Handled; await verification')
        self.assertEqual(restored.locator('#verdict').inner_text(), 'BLOCKED')
        page.close(); restored.close()

    def test_portable_bytes_preserve_handling_without_browser_store(self):
        page = self.page()
        page.get_by_role('checkbox').first.check()
        page.get_by_role('textbox').first.fill('</script> & a private handling note')
        # Capture bytes instead of depending on this environment's download policy.
        page.evaluate('''() => {
          URL.createObjectURL = blob => {window.exportedBlob=blob;return 'blob:test';};
          HTMLAnchorElement.prototype.click = function() {};
        }''')
        page.get_by_role('button', name='Save portable copy').click()
        portable = page.evaluate('window.exportedBlob.text()')
        restored = self.browser.new_page()
        restored.set_content(portable)
        self.assertTrue(restored.get_by_role('checkbox').first.is_checked())
        self.assertEqual(restored.get_by_role('textbox').first.input_value(), '</script> & a private handling note')
        self.assertEqual(restored.locator('#categories button').count(), 4)
        self.assertIn('Not saved', restored.locator('#storage').inner_text())
        page.close(); restored.close()

    def test_hostile_text_and_changed_fingerprint(self):
        raw=sample();raw['findings'][0]['id']='constructor'
        raw['findings'][0]['title']='</script><img src=x onerror="window.pwned=1"> __REPORT_TEXT__'
        page=self.page(raw)
        page.get_by_role('checkbox').first.check()
        page.get_by_role('textbox').first.fill('Prior note')
        saved=page.evaluate('window.testItems')
        self.assertIsNone(page.evaluate('window.pwned'))
        self.assertEqual(page.locator('img,svg').count(),0)
        raw['findings'][0]['detail']+=' New verified evidence.'
        restored=self.page(raw,saved)
        self.assertFalse(restored.get_by_role('checkbox').first.is_checked())
        self.assertEqual(restored.get_by_role('textbox').first.input_value(),'Prior note')
        self.assertTrue(restored.locator('.changed').first.is_visible())
        page.close();restored.close()


    def test_failed_local_write_uses_session_storage(self):
        page = self.browser.new_page()
        page.evaluate("""() => {
          window.sessionItems = {};
          const localItems = {};
          Object.defineProperty(window, 'localStorage', {value:{
            getItem:k=>localItems[k]??null,
            setItem:(k,v)=>{if (!k.endsWith(':probe')) throw new DOMException('Quota','QuotaExceededError');localItems[k]=v;},
            removeItem:k=>{delete localItems[k]}
          }});
          Object.defineProperty(window, 'sessionStorage', {value:{
            getItem:k=>sessionItems[k]??null,setItem:(k,v)=>{sessionItems[k]=v;},
            removeItem:k=>{delete sessionItems[k]}
          }});
        }""")
        page.set_content(report.render(sample())[0])
        page.get_by_role('checkbox').first.check()
        page.get_by_role('textbox').first.fill('Saved through session fallback')
        self.assertIn('Session storage only', page.locator('#storage').inner_text())
        saved = page.evaluate('window.sessionItems')
        restored = self.browser.new_page()
        restored.evaluate("""items => {
          Object.defineProperty(window, 'localStorage', {get(){throw new DOMException('Denied','SecurityError');}});
          Object.defineProperty(window, 'sessionStorage', {value:{
            getItem:k=>items[k]??null,setItem:(k,v)=>{items[k]=v;},removeItem:k=>{delete items[k]}
          }});
        }""", saved)
        restored.set_content(report.render(sample())[0])
        self.assertTrue(restored.get_by_role('checkbox').first.is_checked())
        self.assertEqual(restored.get_by_role('textbox').first.input_value(), 'Saved through session fallback')
        self.assertIn('Session storage only', restored.locator('#storage').inner_text())
        page.close(); restored.close()

    def test_import_rejects_other_campaign_and_restores_valid_progress(self):
        page = self.page()
        page.get_by_role('checkbox').first.check()
        saved = page.evaluate('window.testItems')
        progress = json.loads(next(value for key, value in saved.items() if key.endswith(':handling')))
        wrong = {**progress, 'report_key':'another-campaign'}
        page.locator('#import-file').set_input_files({
            'name':'wrong.json','mimeType':'application/json','buffer':json.dumps(wrong).encode()})
        page.wait_for_function("document.getElementById('message').textContent.includes('another campaign')")
        self.assertTrue(page.get_by_role('checkbox').first.is_checked())
        restored = self.page()
        restored.locator('#import-file').set_input_files({
            'name':'progress.json','mimeType':'application/json','buffer':json.dumps(progress).encode()})
        restored.wait_for_function("document.getElementById('message').textContent.includes('Progress merged')")
        self.assertTrue(restored.get_by_role('checkbox').first.is_checked())
        self.assertEqual(restored.locator('#verdict').inner_text(), 'BLOCKED')
        page.close(); restored.close()

if __name__=='__main__':
    unittest.main()
