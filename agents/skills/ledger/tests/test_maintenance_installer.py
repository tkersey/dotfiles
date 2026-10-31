import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
spec = importlib.util.spec_from_file_location('installer_regressions', SCRIPTS / 'install_maintenance.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstalledRuntimeTests(unittest.TestCase):
    def test_qualified_formula_and_current_interpreter_are_scheduled_directly(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            calls = []

            def execute(arguments, **kwargs):
                calls.append(arguments)
                if '--prefix' in arguments:
                    self.assertEqual(arguments, ['/fixture/brew', '--prefix', 'tkersey/tap/ledger'])
                    output = '/fixture/qualified-ledger\n'
                elif arguments[-1] == 'version':
                    output = '1.6.0\n'
                else:
                    output = ''
                return subprocess.CompletedProcess(arguments, 0, output, '')

            with patch.dict(os.environ, {'LEDGER_HOME': str(root / 'ledger')}), \
                 patch.object(installer.Path, 'home', return_value=root), \
                 patch.object(installer.Path, 'is_file', return_value=True), \
                 patch.object(installer.shutil, 'which', return_value='/fixture/brew'), \
                 patch.object(installer.subprocess, 'run', side_effect=execute):
                result = installer.install()
            arguments = result['launch_agent']['ProgramArguments']
            self.assertEqual(arguments[0], str(Path(sys.executable).resolve(strict=True)))
            self.assertEqual(arguments[1], str(SCRIPTS / 'maintain_custody.py'))
            self.assertIn('--scheduled', arguments)
            self.assertIn('/fixture/qualified-ledger/bin/ledger', arguments)
            self.assertTrue(any(command[:2] == [arguments[0], '-I'] for command in calls))
            self.assertNotIn('uv', arguments)
            self.assertFalse(list(root.iterdir()))

    def test_unusable_interpreter_cannot_publish_or_activate_an_agent(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            with patch.dict(os.environ, {'LEDGER_HOME': str(root / 'ledger')}), \
                 patch.object(installer.Path, 'home', return_value=root), \
                 patch.object(installer.shutil, 'which', return_value='/fixture/brew'), \
                 patch.object(installer.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'python')):
                with self.assertRaises(subprocess.CalledProcessError):
                    installer.install(apply=True)
            self.assertFalse(list(root.iterdir()))


if __name__ == '__main__':
    unittest.main()
