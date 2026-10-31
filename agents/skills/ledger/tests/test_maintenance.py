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
        user_home = patch.object(maintenance.Path, 'home', return_value=self.root)
        user_home.start()
        self.addCleanup(user_home.stop)
        environment = patch.dict(os.environ, {'LEDGER_HOME': str(self.home)})
        environment.start()
        self.addCleanup(environment.stop)
        self.ctx = maintenance.context_module()
        self.context = self.ctx.resolve(initialize=True)
        self.config = json.loads(maintenance.DEFAULT_CONFIG.read_text())
        self.config['min_free_bytes'] = 100
        self.config_path = self.root / 'config.json'
        self.config_path.write_text(json.dumps(self.config))

    def native(self, *, outcome='healthy', free=200, reclaimed=0):
        return {'schema': 'ledger-maintenance-result/v1', 'outcome': outcome,
                'storage_mutated': reclaimed > 0, 'authority_granted': False, 'free_bytes': free,
                'bytes_read': 20, 'file_reads': 2,
                'preparation': {'phase': 'absent', 'files': 0, 'bytes': 0,
                                'installed': False, 'reclaimed_bytes': reclaimed},
                'measurements': {'coverage': 'top-level-only', 'required_history_bytes': None,
                                 'physical_bytes_freed': None}}

    def run_wrapper(self, **kwargs):
        return maintenance.run(config_path=self.config_path, **kwargs)

    def install_fixture(self, interval=3600):
        self.config['interval_seconds'] = interval
        self.config_path.write_text(json.dumps(self.config))
        path = self.root / 'Library/LaunchAgents' / (maintenance.LABEL + '.plist')
        path.parent.mkdir(parents=True, exist_ok=True)
        value = {'Label': maintenance.LABEL, 'StartInterval': interval,
                 'EnvironmentVariables': {'LEDGER_HOME': str(self.home)},
                 'ProgramArguments': ['/fixture/python', str(SCRIPTS / 'maintain_custody.py'), '--apply', '--scheduled',
                                      '--config', str(self.config_path), '--ledger-bin', '/fixture/ledger']}
        path.write_bytes(plistlib.dumps(value))
        return path

    def record_scheduled(self, completed, *, outcome='healthy'):
        installation = maintenance.installed_context(self.home, self.ctx)
        (self.home / 'maintenance').mkdir(exist_ok=True)
        self.ctx.write_json(self.home / 'maintenance/last-run.json', {
            'schema': 'ledger-maintenance-last-run/v1', 'started_at': completed, 'completed_at': completed,
            'outcome': outcome, 'processed_count': 1, 'selected_count': 1, 'inspection_complete': True,
            'installation': installation['identity'],
        })

    def test_inspection_does_not_persist(self):
        before = {str(path.relative_to(self.home)): path.read_bytes()
                  for path in self.home.rglob('*') if path.is_file()}
        with patch.object(maintenance, 'invoke', return_value=self.native(free=1)) as native:
            result = self.run_wrapper()
        self.assertFalse(native.call_args.kwargs['apply'])
        self.assertEqual(result['outcome'], 'attention')
        self.assertFalse(result['storage_mutated'])
        self.assertFalse((self.home / 'maintenance').exists())
        self.assertEqual(before, {str(path.relative_to(self.home)): path.read_bytes()
                                 for path in self.home.rglob('*') if path.is_file()})

    def test_repeated_pressure_and_resolution_keep_only_one_bounded_run_record(self):
        self.install_fixture()
        with patch.object(maintenance, 'invoke', return_value=self.native(free=1)):
            for _ in range(100):
                result = self.run_wrapper(apply=True, scheduled=True)
        self.assertEqual(result['outcome'], 'attention')
        self.assertEqual(result['stores'][0]['conditions'], ['low-free-space'])
        self.assertEqual(maintenance.observation()['scheduler']['status'], 'attention')
        root = self.home / 'maintenance'
        self.assertEqual({path.name for path in root.iterdir()}, {'last-run.json', 'runner.lock'})
        last = json.loads((root / 'last-run.json').read_bytes())
        self.assertEqual(last['schema'], 'ledger-maintenance-last-run/v1')
        self.assertEqual(last['outcome'], 'attention')
        self.assertTrue(all(path.stat().st_size <= maintenance.MAX_RESULT_BYTES for path in root.iterdir()))
        with patch.object(maintenance, 'invoke', return_value=self.native(reclaimed=17)):
            result = self.run_wrapper(apply=True, scheduled=True)
        self.assertEqual(result['outcome'], 'healthy')
        self.assertEqual(maintenance.observation()['scheduler']['status'], 'current')

    def test_native_commands_share_deadline_and_stop_when_exhausted(self):
        self.ctx.resolve(initialize=True)
        ticks = [299]

        def invoke(*args, **kwargs):
            self.assertEqual(kwargs['timeout'], 1)
            ticks[0] = 300
            return self.native()

        with patch.object(maintenance.time, 'monotonic', side_effect=lambda: ticks[0]), \
             patch.object(maintenance, 'invoke', side_effect=invoke) as native:
            result = self.run_wrapper(apply=True, deadline=300)
        self.assertEqual(native.call_count, 1)
        self.assertEqual(result['outcome'], 'incomplete')
        self.assertEqual(len(result['stores']), 1)
        last = json.loads((self.home / 'maintenance/last-run.json').read_bytes())
        self.assertEqual(last['processed_count'], 1)
        self.assertFalse(last['inspection_complete'])

    def test_expired_deadline_starts_no_native_command(self):
        with patch.object(maintenance.time, 'monotonic', return_value=300), \
             patch.object(maintenance, 'invoke') as native:
            result = self.run_wrapper(apply=True, deadline=300)
        native.assert_not_called()
        self.assertEqual(result['outcome'], 'incomplete')

    def test_existing_per_store_files_are_untouched_and_cannot_block_native_work(self):
        second = self.ctx.resolve(initialize=True)
        root = self.home / 'maintenance'
        root.mkdir()
        path = root / (self.context['store_id'] + '.json')
        path.write_bytes(b'{unknown prior evidence')
        with patch.object(maintenance, 'invoke', return_value=self.native()) as native:
            result = self.run_wrapper(apply=True)
        self.assertEqual(native.call_count, 2)
        self.assertEqual(result['outcome'], 'healthy')
        self.assertEqual(path.read_bytes(), b'{unknown prior evidence')
        self.assertFalse((root / (second['store_id'] + '.json')).exists())

    def test_malformed_or_unknown_last_run_is_retained_and_reported_after_native_work(self):
        self.install_fixture()
        path = self.home / 'maintenance/last-run.json'
        path.parent.mkdir()
        for raw in (b'{malformed', b'{"schema":"unknown"}', b'x' * (maintenance.MAX_RESULT_BYTES + 1)):
            with self.subTest(raw=raw[:20]):
                path.write_bytes(raw)
                with patch.object(maintenance, 'invoke', return_value=self.native()) as native:
                    result = self.run_wrapper(apply=True, scheduled=True)
                native.assert_called_once()
                self.assertEqual(result['outcome'], 'failure')
                self.assertEqual(result['last_run']['status'], 'failed')
                self.assertEqual(result['scheduler']['status'], 'unknown')
                self.assertEqual(path.read_bytes(), raw)

    def test_last_run_write_failure_keeps_prior_evidence_and_reports_failure(self):
        self.install_fixture()
        self.record_scheduled(maintenance.time.time())
        path = self.home / 'maintenance/last-run.json'
        before = path.read_bytes()
        with maintenance.runner_lock(self.home, self.ctx):
            pass
        with patch.object(maintenance, 'context_module', return_value=self.ctx), \
             patch.object(self.ctx, 'write_json', side_effect=OSError('read-only last-run')), \
             patch.object(maintenance, 'invoke', return_value=self.native()):
            result = self.run_wrapper(apply=True, scheduled=True)
        self.assertEqual(result['outcome'], 'failure')
        self.assertEqual(result['scheduler']['status'], 'attention')
        self.assertEqual(result['last_run']['status'], 'failed')
        self.assertIsNone(result['storage_mutated'])
        self.assertEqual(path.read_bytes(), before)

    def test_routine_reports_only_actual_runner_resource_creation(self):
        with patch.object(maintenance, 'invoke', return_value=self.native()):
            first = self.run_wrapper(apply=True, store_ids=[self.context['store_id']])
            repeated = self.run_wrapper(apply=True, store_ids=[self.context['store_id']])
        self.assertTrue(first['storage_mutated'])
        self.assertFalse(repeated['storage_mutated'])
        self.assertEqual({path.name for path in (self.home / 'maintenance').iterdir()}, {'runner.lock'})

    def test_known_native_mutation_dominates_later_unknown_outcome(self):
        second = self.ctx.resolve(initialize=True)
        with maintenance.runner_lock(self.home, self.ctx):
            pass
        with patch.object(maintenance, 'invoke', side_effect=[self.native(reclaimed=17), OSError('unavailable')]):
            result = self.run_wrapper(apply=True, store_ids=[self.context['store_id'], second['store_id']])
        self.assertTrue(result['storage_mutated'])
        self.assertIsNone(result['stores'][1]['storage_mutated'])

    def test_cli_failure_only_returns_structured_health(self):
        with patch.object(sys, 'argv', ['maintain_custody.py', '--apply']), \
             patch.object(maintenance, 'run', side_effect=OSError('unavailable')), \
             patch.object(maintenance.subprocess, 'run') as command, \
             contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(maintenance.main(), 3)
        command.assert_not_called()
        self.assertEqual(json.loads(output.getvalue())['outcome'], 'failure')


    def test_routine_maintenance_does_not_refresh_scheduled_run(self):
        with patch.object(maintenance, 'invoke', return_value=self.native()):
            result = self.run_wrapper(apply=True, store_ids=[self.context['store_id']])
        self.assertEqual(result['scheduler']['status'], 'missing')
        self.assertFalse((self.home / 'maintenance/last-run.json').exists())
        self.install_fixture()
        path = self.home / 'maintenance/last-run.json'
        self.record_scheduled(1)
        before = path.read_bytes()
        with patch.object(maintenance, 'invoke', return_value=self.native()):
            result = self.run_wrapper(apply=True, store_ids=[self.context['store_id']])
        self.assertEqual(result['scheduler']['status'], 'stale')
        self.assertEqual(path.read_bytes(), before)

    def test_normal_observation_and_routine_use_installed_custom_cadence(self):
        for interval, age, expected in ((60, 121, 'stale'), (86400, 7201, 'current')):
            with self.subTest(interval=interval):
                self.install_fixture(interval)
                self.record_scheduled(100000 - age)
                with patch.object(maintenance.time, 'time', return_value=100000), \
                     patch.object(maintenance, 'invoke', return_value=self.native()) as native:
                    self.assertEqual(maintenance.observation()['scheduler']['status'], expected)
                    result = maintenance.routine(self.context)
                self.assertEqual(result['scheduler']['status'], expected)
                self.assertEqual(native.call_args.args[2], self.config)

    def test_installation_changes_and_manual_runs_do_not_certify_scheduler(self):
        self.install_fixture(60)
        with patch.object(maintenance, 'invoke', return_value=self.native()):
            result = self.run_wrapper(apply=True)
            self.assertEqual(result['scheduler']['status'], 'missing')
            result = self.run_wrapper(apply=True, scheduled=True)
            self.assertEqual(result['scheduler']['status'], 'current')
            self.assertFalse(result['scheduler']['activation_verified'])
        self.install_fixture(120)
        self.assertEqual(maintenance.observation()['scheduler']['status'], 'missing')
        other = self.root / 'other.json'
        other.write_text(json.dumps(self.config))
        with patch.object(maintenance, 'invoke', return_value=self.native()):
            result = maintenance.run(config_path=other, apply=True, scheduled=True)
        self.assertEqual(result['scheduler']['status'], 'missing')
        self.assertEqual(result['outcome'], 'attention')

    def test_changed_config_cadence_requires_reinstallation_without_mutation(self):
        self.install_fixture(60)
        self.record_scheduled(100000)
        self.config['interval_seconds'] = 86400
        self.config_path.write_text(json.dumps(self.config))
        before = {str(path): path.read_bytes() for path in self.root.rglob('*') if path.is_file()}
        with patch.object(maintenance, 'invoke') as native:
            observation = maintenance.observation()['scheduler']
            result = maintenance.routine(self.context)
        native.assert_not_called()
        self.assertEqual(observation['status'], 'mismatch')
        self.assertEqual(observation['interval_seconds'], 60)
        self.assertFalse(result['storage_mutated'])
        self.assertEqual(before, {str(path): path.read_bytes() for path in self.root.rglob('*') if path.is_file()})

    def test_missing_unreadable_and_different_home_installations_remain_explicit(self):
        self.assertEqual(maintenance.observation()['scheduler']['status'], 'missing')
        path = self.install_fixture()
        value = plistlib.loads(path.read_bytes())
        value['EnvironmentVariables']['LEDGER_HOME'] = str(self.root / 'different')
        path.write_bytes(plistlib.dumps(value))
        self.assertEqual(maintenance.observation()['scheduler']['status'], 'mismatch')
        for raw in (b'invalid plist', b'<?xml version="1.0"?><plist><dict>',
                    plistlib.dumps([]), b'x' * (maintenance.MAX_RESULT_BYTES + 1)):
            path.write_bytes(raw)
            self.assertEqual(maintenance.observation()['scheduler']['status'], 'unknown')
        self.assertFalse((self.home / 'maintenance').exists())


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
        self.assertFalse(last['inspection_complete'])

    def test_missing_catalog_does_not_hide_retained_custody_roots(self):
        (self.home / self.ctx.CATALOG).unlink()
        with patch.object(maintenance, 'invoke') as native:
            inspected = self.run_wrapper()
            self.assertFalse((self.home / 'maintenance').exists())
            applied = self.run_wrapper(apply=True)
        native.assert_not_called()
        self.assertEqual(inspected['outcome'], 'incomplete')
        self.assertEqual(applied['catalog_status'], 'missing-with-existing-roots')
        self.assertTrue(Path(self.context['store_root']).is_dir())

    def test_native_failure_remains_separate_from_custody_state(self):
        with patch.object(maintenance, 'invoke', side_effect=subprocess.TimeoutExpired('ledger', 30)):
            result = self.run_wrapper(apply=True)
        self.assertEqual(result['stores'][0]['outcome'], 'failure')
        self.assertIsNone(result['stores'][0]['storage_mutated'])
        self.assertEqual(result['stores'][0]['code'], 'TimeoutExpired')
        self.assertEqual(self.ctx.resolve(store_id=self.context['store_id'])['store_root'], self.context['store_root'])

    def test_an_active_runner_prevents_overlapping_sweeps_without_waiting(self):
        with maintenance.runner_lock(self.home, self.ctx) as locked:
            self.assertTrue(locked)
            with patch.object(maintenance, 'invoke') as native:
                result = self.run_wrapper(apply=True)
        self.assertEqual(result['outcome'], 'busy')
        native.assert_not_called()

    def test_native_measurement_limits_are_preserved(self):
        with patch.object(maintenance, 'invoke', return_value=self.native()):
            result = self.run_wrapper()
        self.assertEqual(result['stores'][0]['measurements']['coverage'], 'top-level-only')
        self.assertIsNone(result['stores'][0]['measurements']['required_history_bytes'])
        self.assertIsNone(result['stores'][0]['measurements']['physical_bytes_freed'])

    def test_partial_cleanup_observation_remains_in_cli_result(self):
        value = self.native(outcome='failure', reclaimed=17)
        value['preparation'] = {
            'phase': 'installed', 'installed': True, 'observed_by': 'reconciliation',
            'activity': 'cleanup', 'complete': False, 'files': 2, 'bytes': 31,
            'reclaimed_bytes': 17,
        }
        with patch.object(maintenance, 'invoke', return_value=value):
            result = self.run_wrapper(apply=True)
        self.assertEqual(result['stores'][0]['preparation'], value['preparation'])
        self.assertFalse((self.home / 'maintenance' / (self.context['store_id'] + '.json')).exists())


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
        value = installer.launch_agent('/fixture/python', '/opt/homebrew/opt/ledger/bin/ledger',
                                       Path('/fixture with spaces/config.json'), Path('/fixture/home'), 3600)
        self.assertEqual(plistlib.loads(plistlib.dumps(value)), value)
        self.assertEqual(value['StartInterval'], 3600)
        self.assertEqual(value['ProgramArguments'][0], '/fixture/python')
        self.assertIn('--scheduled', value['ProgramArguments'])
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
        before = foreign.read_bytes()
        inspected = maintenance.run(binary=os.environ['LEDGER_BIN'], config_path=self.config_path)
        self.assertEqual(inspected['stores'][0]['outcome'], 'healthy')
        self.assertFalse((self.home / 'maintenance').exists())
        self.assertEqual(inspected['stores'][0]['bytes_read'], 2 * (store / self.ctx.MARKER).stat().st_size)
        self.assertIsNone(inspected['stores'][0]['measurements']['physical_bytes_freed'])
        MaintenanceTests.install_fixture(self)
        applied = maintenance.run(binary=os.environ['LEDGER_BIN'], config_path=self.config_path, apply=True,
                                  scheduled=True)
        self.assertEqual(applied['stores'][0]['outcome'], 'healthy')
        self.assertEqual(foreign.read_bytes(), before)
        observation = maintenance.scheduler_observation(self.home, self.ctx)
        self.assertEqual(observation['status'], 'current')


if __name__ == '__main__':
    unittest.main()
