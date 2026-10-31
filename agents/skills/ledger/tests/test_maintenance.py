import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch


SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


maintenance = load('maintain_custody')
installer = load('install_maintenance')
custody = load('ensure_custody')


class MaintenanceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.home = self.root / 'home'
        environment = patch.dict(os.environ, {'LEDGER_HOME': str(self.home)})
        environment.start()
        self.addCleanup(environment.stop)
        self.ctx = maintenance.context_module()
        self.context = self.ctx.resolve(initialize=True)
        self.config = json.loads(maintenance.DEFAULT_CONFIG.read_text())
        self.config['min_free_bytes'] = 100
        self.config_path = self.root / 'config.json'
        self.config_path.write_text(json.dumps(self.config))
        self.sent = []

    def native(self, *, outcome='healthy', free=200, reclaimed=0):
        return {'schema': 'ledger-maintenance-result/v1', 'outcome': outcome,
                'storage_mutated': reclaimed > 0, 'authority_granted': False, 'free_bytes': free,
                'bytes_read': 20, 'file_reads': 2,
                'preparation': {'phase': 'absent', 'files': 0, 'bytes': 0,
                                'installed': False, 'reclaimed_bytes': reclaimed},
                'measurements': {'coverage': 'top-level-only', 'required_history_bytes': None,
                                 'physical_bytes_freed': None}}

    def run_wrapper(self, **kwargs):
        return maintenance.run(config_path=self.config_path, send=self.sent.append, **kwargs)

    def test_inspection_does_not_persist_or_notify(self):
        before = {str(path.relative_to(self.home)): path.read_bytes()
                  for path in self.home.rglob('*') if path.is_file()}
        with patch.object(maintenance, 'invoke', return_value=self.native(free=1)) as native:
            result = self.run_wrapper()
        self.assertFalse(native.call_args.kwargs['apply'])
        self.assertEqual(result['outcome'], 'attention')
        self.assertFalse(result['storage_mutated'])
        self.assertFalse(self.sent)
        self.assertFalse((self.home / 'maintenance').exists())
        self.assertEqual(before, {str(path.relative_to(self.home)): path.read_bytes()
                                 for path in self.home.rglob('*') if path.is_file()})

    def test_pressure_repeat_and_resolution_use_only_latest_state(self):
        with patch.object(maintenance, 'invoke', return_value=self.native(free=1)):
            for _ in range(100):
                result = self.run_wrapper(apply=True)
        self.assertEqual(result['outcome'], 'attention')
        self.assertEqual(len(self.sent), 1)
        with patch.object(maintenance, 'invoke', return_value=self.native(reclaimed=2048)):
            result = self.run_wrapper(apply=True)
            self.run_wrapper(apply=True)
        self.assertEqual(result['outcome'], 'healthy')
        self.assertEqual(len(self.sent), 2)
        self.assertTrue(self.sent[-1].endswith('resolved.'))
        state = self.home / 'maintenance'
        self.assertEqual({path.name for path in state.iterdir()},
                         {self.context['store_id'] + '.json', 'last-run.json', 'runner.lock'})
        self.assertTrue(all(path.stat().st_size <= maintenance.MAX_RESULT_BYTES for path in state.iterdir()))

    def test_unresolved_condition_is_reminded_after_one_day(self):
        with patch.object(maintenance, 'invoke', return_value=self.native(outcome='blocked')):
            with patch.object(maintenance.time, 'time', return_value=100000):
                self.run_wrapper(apply=True)
            with patch.object(maintenance.time, 'time', return_value=100001):
                self.run_wrapper(apply=True)
            with patch.object(maintenance.time, 'time', return_value=100001 + maintenance.REMINDER_SECONDS):
                self.run_wrapper(apply=True)
        self.assertEqual(len(self.sent), 2)

    def test_notification_failure_is_retained_and_retried(self):
        failed = Mock(side_effect=OSError('unavailable'))
        with patch.object(maintenance, 'invoke', return_value=self.native(free=1)):
            result = maintenance.run(config_path=self.config_path, apply=True, send=failed)
            result = self.run_wrapper(apply=True)
        self.assertGreater(failed.call_count, 0)
        self.assertEqual(result['stores'][0]['notification']['status'], 'submitted')
        self.assertEqual(len(self.sent), 1)

    def test_routine_maintenance_does_not_refresh_scheduled_run(self):
        with patch.object(maintenance, 'invoke', return_value=self.native()):
            result = self.run_wrapper(apply=True, store_ids=[self.context['store_id']])
        self.assertEqual(result['scheduler']['status'], 'missing')
        self.assertFalse((self.home / 'maintenance/last-run.json').exists())
        path = self.home / 'maintenance/last-run.json'
        self.ctx.write_json(path, {'observation': {'completed_at': 1, 'outcome': 'healthy'}})
        before = path.read_bytes()
        with patch.object(maintenance, 'invoke', return_value=self.native()):
            result = self.run_wrapper(apply=True, store_ids=[self.context['store_id']])
        self.assertEqual(result['scheduler']['status'], 'stale')
        self.assertEqual(path.read_bytes(), before)

    def test_catalog_bound_reports_incomplete_without_claiming_eventual_coverage(self):
        self.ctx.resolve(initialize=True)
        self.config['max_stores'] = 1
        self.config_path.write_text(json.dumps(self.config))
        with patch.object(maintenance, 'invoke', return_value=self.native()) as native:
            result = self.run_wrapper(apply=True)
        self.assertEqual(native.call_count, 1)
        self.assertEqual(result['outcome'], 'incomplete')
        self.assertEqual(result['selected_count'], 2)
        last = json.loads((self.home / 'maintenance/last-run.json').read_bytes())
        self.assertFalse(last['observation']['inspection_complete'])
        self.assertIn('incomplete-sweep', self.sent[0])

    def test_missing_catalog_does_not_hide_retained_custody_roots(self):
        (self.home / self.ctx.CATALOG).unlink()
        with patch.object(maintenance, 'invoke') as native:
            inspected = self.run_wrapper()
            self.assertFalse((self.home / 'maintenance').exists())
            applied = self.run_wrapper(apply=True)
        native.assert_not_called()
        self.assertEqual(inspected['outcome'], 'incomplete')
        self.assertEqual(applied['catalog_status'], 'missing-with-existing-roots')
        self.assertEqual(len(self.sent), 1)
        self.assertIn('missing-catalog', self.sent[0])
        self.assertTrue(Path(self.context['store_root']).is_dir())

    def test_native_failure_remains_separate_from_custody_state(self):
        with patch.object(maintenance, 'invoke', side_effect=subprocess.TimeoutExpired('ledger', 30)):
            result = self.run_wrapper(apply=True)
        self.assertEqual(result['stores'][0]['outcome'], 'failure')
        self.assertIsNone(result['stores'][0]['storage_mutated'])
        self.assertEqual(result['stores'][0]['code'], 'TimeoutExpired')
        self.assertEqual(self.ctx.resolve(store_id=self.context['store_id'])['store_root'], self.context['store_root'])

    def test_an_active_runner_prevents_duplicate_notifications_without_waiting(self):
        with maintenance.runner_lock(self.home, self.ctx) as locked:
            self.assertTrue(locked)
            with patch.object(maintenance, 'invoke') as native:
                result = self.run_wrapper(apply=True)
        self.assertEqual(result['outcome'], 'busy')
        native.assert_not_called()
        self.assertFalse(self.sent)

    def test_native_measurement_limits_are_preserved(self):
        with patch.object(maintenance, 'invoke', return_value=self.native()):
            result = self.run_wrapper()
        self.assertEqual(result['stores'][0]['measurements']['coverage'], 'top-level-only')
        self.assertIsNone(result['stores'][0]['measurements']['required_history_bytes'])
        self.assertIsNone(result['stores'][0]['measurements']['physical_bytes_freed'])

    def test_partial_cleanup_observation_survives_persisted_summary(self):
        value = self.native(outcome='failure', reclaimed=17)
        value['preparation'] = {
            'phase': 'installed', 'installed': True, 'observed_by': 'reconciliation',
            'activity': 'cleanup', 'complete': False, 'files': 2, 'bytes': 31,
            'reclaimed_bytes': 17,
        }
        with patch.object(maintenance, 'invoke', return_value=value):
            result = self.run_wrapper(apply=True)
        self.assertEqual(result['stores'][0]['preparation'], value['preparation'])
        latest = json.loads((self.home / 'maintenance' / (self.context['store_id'] + '.json')).read_bytes())
        self.assertEqual(latest['observation']['preparation'], value['preparation'])

    def test_notification_message_is_an_argument_not_script_source(self):
        message = '\"; do shell script \"untrusted\"'
        with patch.object(maintenance.subprocess, 'run') as run:
            maintenance.notify(message)
        arguments = run.call_args.args[0]
        self.assertEqual(arguments[0], '/usr/bin/osascript')
        self.assertEqual(arguments[-1], message)
        self.assertNotIn(message, arguments[2])
        self.assertNotIn('shell', run.call_args.kwargs)

    def test_inspection_cannot_accept_a_native_mutation_claim(self):
        result = self.native(reclaimed=1)
        completed = subprocess.CompletedProcess([], 0, json.dumps(result).encode(), b'')
        with patch.object(maintenance.subprocess, 'run', return_value=completed):
            with self.assertRaisesRegex(ValueError, 'inspection reported mutation'):
                maintenance.invoke('ledger', self.context, self.config, apply=False, timeout=1)

    def test_no_maintenance_alias_never_invokes_housekeeping(self):
        fake = types.SimpleNamespace(routine=Mock(), observation=Mock(return_value={'scheduler': {'status': 'stale'}}))
        argv = ['ensure_custody.py', '--no-maintenance', '--definition', '/fixture/definition.json',
                '--store-id', self.context['store_id']]
        with patch.object(sys, 'argv', argv), patch.object(custody, 'owner_context', return_value=dict(self.context)) as owner, \
             patch.object(custody, 'load_module', return_value=fake), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(custody.main(), 0)
        self.assertTrue(owner.call_args.kwargs['read_only'])
        self.assertFalse(owner.call_args.kwargs['maintain'])
        fake.routine.assert_not_called()
        self.assertEqual(json.loads(output.getvalue())['maintenance']['scheduler']['status'], 'stale')

    def test_housekeeping_failure_does_not_erase_successful_preparation(self):
        fake = types.SimpleNamespace(routine=Mock(return_value={'outcome': 'failure'}))
        context = {**self.context, 'preparation': {'outcome': 'prepared'}}
        argv = ['ensure_custody.py', '--ensure-owner', '--definition', '/fixture/definition.json',
                '--store-id', self.context['store_id']]
        with patch.object(sys, 'argv', argv), patch.object(custody, 'owner_context', return_value=context), \
             patch.object(custody, 'load_module', return_value=fake), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(custody.main(), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result['preparation']['outcome'], 'prepared')
        self.assertEqual(result['maintenance']['outcome'], 'failure')


class InstallationTests(unittest.TestCase):
    def test_launchagent_uses_direct_arguments_and_hourly_cadence_without_logs(self):
        value = installer.launch_agent('/opt/homebrew/bin/uv', '/opt/homebrew/opt/ledger/bin/ledger',
                                       Path('/fixture with spaces/config.json'), Path('/fixture/home'), 3600)
        self.assertEqual(plistlib.loads(plistlib.dumps(value)), value)
        self.assertEqual(value['StartInterval'], 3600)
        self.assertEqual(value['ProgramArguments'][0], '/opt/homebrew/bin/uv')
        self.assertIn('/fixture with spaces/config.json', value['ProgramArguments'])
        self.assertIn('/opt/homebrew/opt/ledger/bin/ledger', value['ProgramArguments'])
        self.assertEqual(value['StandardOutPath'], '/dev/null')
        self.assertEqual(value['StandardErrorPath'], '/dev/null')
        self.assertNotIn('sh', value['ProgramArguments'])

    def test_install_inspection_never_creates_or_activates_agent(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            calls = []

            def execute(arguments, **kwargs):
                calls.append(arguments)
                output = '/opt/homebrew/opt/ledger\n' if '--prefix' in arguments else '1.6.0\n'
                return subprocess.CompletedProcess(arguments, 0, output, '')

            with patch.dict(os.environ, {'LEDGER_HOME': str(root / 'ledger')}), \
                 patch.object(installer.Path, 'home', return_value=root), \
                 patch.object(installer.Path, 'is_file', return_value=True), \
                 patch.object(installer.shutil, 'which', side_effect=lambda name: '/opt/homebrew/bin/' + name), \
                 patch.object(installer.subprocess, 'run', side_effect=execute):
                result = installer.install()
            self.assertFalse(result['activated'])
            self.assertFalse(result['storage_mutated'])
            self.assertFalse(list(root.iterdir()))
            self.assertFalse(any('/bin/launchctl' in command for command in calls))

    def test_apply_installs_plist_and_reloads_only_its_own_service(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            calls = []

            def execute(arguments, **kwargs):
                calls.append(arguments)
                output = '/opt/homebrew/opt/ledger\n' if '--prefix' in arguments else '1.6.0\n'
                return subprocess.CompletedProcess(arguments, 0, output, '')

            with patch.dict(os.environ, {'LEDGER_HOME': str(root / 'ledger')}), \
                 patch.object(installer.Path, 'home', return_value=root), \
                 patch.object(installer.Path, 'is_file', return_value=True), \
                 patch.object(installer.shutil, 'which', side_effect=lambda name: '/opt/homebrew/bin/' + name), \
                 patch.object(installer.subprocess, 'run', side_effect=execute):
                result = installer.install(apply=True)
            target = root / 'Library/LaunchAgents' / (installer.LABEL + '.plist')
            value = plistlib.loads(target.read_bytes())
            self.assertEqual(value['Label'], installer.LABEL)
            self.assertEqual(value['StartInterval'], 3600)
            self.assertTrue(result['activated'])
            self.assertFalse(result['notification_delivery_verified'])
            service = 'gui/' + str(os.getuid()) + '/' + installer.LABEL
            self.assertIn(['/bin/launchctl', 'bootout', service], calls)
            self.assertIn(['/bin/launchctl', 'bootstrap', 'gui/' + str(os.getuid()), str(target)], calls)
            self.assertEqual(list(target.parent.iterdir()), [target])

    def test_old_installed_runtime_cannot_activate_new_adapter(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()

            def execute(arguments, **kwargs):
                output = '/opt/homebrew/opt/ledger\n' if '--prefix' in arguments else '1.5.5\n'
                return subprocess.CompletedProcess(arguments, 0, output, '')

            with patch.dict(os.environ, {'LEDGER_HOME': str(root / 'ledger')}), \
                 patch.object(installer.Path, 'home', return_value=root), \
                 patch.object(installer.shutil, 'which', side_effect=lambda name: '/opt/homebrew/bin/' + name), \
                 patch.object(installer.subprocess, 'run', side_effect=execute):
                with self.assertRaisesRegex(RuntimeError, 'installed Homebrew Ledger'):
                    installer.install(apply=True)
            self.assertFalse(list(root.iterdir()))


@unittest.skipUnless(os.environ.get('LEDGER_BIN'), 'Native Ledger maintenance is required')
class NativeMaintenanceTests(unittest.TestCase):
    def setUp(self):
        MaintenanceTests.setUp(self)

    def test_real_native_inspection_and_apply_preserve_owner_bytes(self):
        store = Path(self.context['store_root'])
        foreign = store / '.ledger/foreign'
        foreign.write_bytes(b'owner evidence retained')
        sent = []
        before = foreign.read_bytes()
        inspected = maintenance.run(binary=os.environ['LEDGER_BIN'], config_path=self.config_path, send=sent.append)
        self.assertEqual(inspected['stores'][0]['outcome'], 'healthy')
        self.assertFalse((self.home / 'maintenance').exists())
        self.assertEqual(inspected['stores'][0]['bytes_read'], 2 * (store / self.ctx.MARKER).stat().st_size)
        self.assertIsNone(inspected['stores'][0]['measurements']['physical_bytes_freed'])
        applied = maintenance.run(binary=os.environ['LEDGER_BIN'], config_path=self.config_path, apply=True, send=sent.append)
        self.assertEqual(applied['stores'][0]['outcome'], 'healthy')
        self.assertEqual(foreign.read_bytes(), before)
        self.assertFalse(sent)
        observation = maintenance.scheduler_observation(self.home, self.config, self.ctx)
        self.assertEqual(observation['status'], 'current')


if __name__ == '__main__':
    unittest.main()
