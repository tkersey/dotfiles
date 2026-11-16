import importlib
from types import SimpleNamespace
import unittest
from unittest.mock import patch


BROWSER_CASES = (
    ('test_report_browser', 'BrowserTests'),
    ('test_construction_browser', 'ConstructionBrowserTests'),
    ('test_resolution_browser', 'BrowserCase'),
    ('test_report_dom', 'DomTests'),
)


def run_setup(base, fail_after_setup=False):
    class Probe(base):
        __unittest_skip__ = False

        @classmethod
        def setUpClass(cls):
            super().setUpClass()
            if fail_after_setup:
                raise RuntimeError('later setup failed')

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def runTest(self):
            pass

    result = unittest.TestResult()
    unittest.TestSuite([Probe()]).run(result)
    return result


class BrowserCleanupTests(unittest.TestCase):
    def test_failures_release_acquired_resources_without_poisoning_the_next_class(self):
        for module_name, class_name in BROWSER_CASES:
            module = importlib.import_module(module_name)
            base = getattr(module, class_name)
            for failure in (None, 'start', 'launch', 'setup', 'close'):
                with self.subTest(module=module_name, failure=failure):
                    active = False
                    events = []
                    fault = failure

                    def start():
                        nonlocal active
                        if fault == 'start':
                            raise RuntimeError('runtime startup failed')
                        if active:
                            raise RuntimeError('previous runtime is still active')
                        active = True
                        return runtime

                    def stop():
                        nonlocal active
                        events.append('runtime stopped')
                        active = False

                    def launch(**kwargs):
                        if fault == 'launch':
                            raise RuntimeError('browser launch failed')
                        return browser

                    def close():
                        events.append('browser close attempted')
                        if fault == 'close':
                            raise RuntimeError('browser close failed')

                    browser = SimpleNamespace(close=close)
                    runtime = SimpleNamespace(chromium=SimpleNamespace(launch=launch), stop=stop)
                    with patch.object(module, 'sync_playwright', return_value=SimpleNamespace(start=start)):
                        first = run_setup(base, fail_after_setup=failure == 'setup')
                        self.assertEqual(len(first.errors), int(failure is not None))
                        self.assertEqual(first.failures, [])
                        if failure:
                            self.assertIn({
                                'start': 'runtime startup failed',
                                'launch': 'browser launch failed',
                                'setup': 'later setup failed',
                                'close': 'browser close failed',
                            }[failure], first.errors[0][1])
                        self.assertFalse(active)
                        expected = []
                        if failure not in ('start', 'launch'):
                            expected.append('browser close attempted')
                        if failure != 'start':
                            expected.append('runtime stopped')
                        self.assertEqual(events, expected)

                        fault = None
                        events.clear()
                        second = run_setup(base)
                        self.assertTrue(second.wasSuccessful(), second.errors)
                        self.assertEqual(second.testsRun, 1)
                        self.assertFalse(active)
                        self.assertEqual(events, ['browser close attempted', 'runtime stopped'])


if __name__ == '__main__':
    unittest.main()
