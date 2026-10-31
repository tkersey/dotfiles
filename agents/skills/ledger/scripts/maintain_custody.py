#!/usr/bin/env -S uv run python
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import plistlib
import subprocess
import stat
import time
from xml.parsers.expat import ExpatError

MAX_RESULT_BYTES = 65536
MAX_RUN_SECONDS = 300
MAX_COMMAND_SECONDS = 30
DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / 'maintenance.json'
LABEL = 'com.tkersey.ledger.maintenance'


def context_module():
    path = Path(__file__).with_name('ledger_context.py')
    spec = importlib.util.spec_from_file_location('ledger_context', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_config(path: Path, ctx) -> dict:
    value = ctx.read_document(path, max_bytes=4096)
    keys = {'schema', 'interval_seconds', 'max_stores', 'max_bytes', 'max_files',
            'max_read_bytes', 'min_free_bytes'}
    if not isinstance(value, dict) or set(value) != keys or value['schema'] != 'ledger-maintenance-config/v1':
        raise ValueError('Invalid maintenance configuration')
    bounds = {'interval_seconds': (60, 86400), 'max_stores': (1, 128),
              'max_bytes': (1, 1024**3), 'max_files': (2, 1023),
              'max_read_bytes': (1, 16 * 1024**3), 'min_free_bytes': (0, 1024**5)}
    if any(type(value[key]) is not int or not low <= value[key] <= high
           for key, (low, high) in bounds.items()):
        raise ValueError('Unsupported maintenance bounds')
    return value


def state_root(home: Path) -> Path:
    return home / 'maintenance'


def installed_context(home: Path, ctx) -> dict:
    path = Path.home() / 'Library/LaunchAgents' / (LABEL + '.plist')
    try:
        ctx.no_symlinks(path)
        if not os.path.lexists(path):
            return {'status': 'missing', 'message': 'Ledger maintenance LaunchAgent is not installed.'}
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, 'rb') as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ValueError('Expected regular LaunchAgent')
            raw = stream.read(MAX_RESULT_BYTES + 1)
        if len(raw) > MAX_RESULT_BYTES:
            raise ValueError('Oversized LaunchAgent')
        value = plistlib.loads(raw)
        if not isinstance(value, dict):
            raise ValueError('Invalid Ledger LaunchAgent')
        args = value.get('ProgramArguments') if isinstance(value, dict) else None
        environment = value.get('EnvironmentVariables', {}) if isinstance(value, dict) else {}
        interval = value.get('StartInterval') if isinstance(value, dict) else None
        if (value.get('Label') != LABEL or not isinstance(args, list) or len(args) != 8
                or not all(isinstance(arg, str) for arg in args)
                or not Path(args[0]).is_absolute()
                or args[1] != str(Path(__file__).resolve())
                or args[2:5] != ['--apply', '--scheduled', '--config']
                or args[6] != '--ledger-bin' or not Path(args[5]).is_absolute()
                or not Path(args[7]).is_absolute() or not isinstance(environment, dict)
                or type(interval) is not int or not 60 <= interval <= 86400):
            raise ValueError('Invalid Ledger LaunchAgent')
        if environment.get('LEDGER_HOME') != str(home):
            return {'status': 'mismatch', 'message': 'Ledger maintenance LaunchAgent selects a different storage home.'}
        config = load_config(Path(args[5]), ctx)
        if config['interval_seconds'] != interval:
            return {'status': 'mismatch', 'interval_seconds': interval,
                    'message': 'Maintenance cadence changed; reinstall the LaunchAgent.'}
        identity = hashlib.sha256(raw + json.dumps(config, sort_keys=True).encode()).hexdigest()
        return {'status': 'configured', 'config_path': args[5], 'config': config,
                'interval_seconds': interval, 'identity': identity}
    except (OSError, ValueError, RuntimeError, plistlib.InvalidFileException, ExpatError):
        return {'status': 'unknown', 'message': 'Ledger maintenance installation or configuration is unreadable.'}


def scheduler_observation(home: Path, ctx, *, now: float | None = None, installation: dict | None = None) -> dict:
    installation = installed_context(home, ctx) if installation is None else installation
    if installation['status'] != 'configured':
        return installation
    now = time.time() if now is None else now
    path = state_root(home) / 'last-run.json'
    try:
        ctx.no_symlinks(path)
        if not os.path.lexists(path):
            return {'status': 'missing', 'message': 'Scheduled Ledger maintenance has no recorded run.'}
        value = validate_last_run(ctx.read_document(path, max_bytes=MAX_RESULT_BYTES))
        if value['installation'] != installation['identity']:
            return {'status': 'missing', 'message': 'No run is recorded for this maintenance installation.'}
        completed = value['completed_at']
        if completed > now + 60:
            raise ValueError('Invalid maintenance completion time')
        if now - completed > installation['interval_seconds'] * 2:
            return {'status': 'stale', 'completed_at': completed,
                    'message': 'Scheduled Ledger maintenance has not completed within two intervals.'}
        outcome = value['outcome']
        return {'status': 'current' if outcome == 'healthy' else 'attention',
                'completed_at': completed, 'outcome': outcome,
                'execution_evidence': 'installed-wrapper', 'activation_verified': False}
    except (ValueError, RuntimeError, OSError):
        return {'status': 'unknown', 'message': 'Scheduled Ledger maintenance state is unreadable.'}


@contextmanager
def runner_lock(home: Path, ctx, result: dict | None = None):
    root = state_root(home)
    ctx.no_symlinks(root)
    try:
        root.mkdir(parents=True, mode=0o700)
        if result is not None:
            result['storage_mutated'] = True
    except FileExistsError:
        pass
    path = root / 'runner.lock'
    ctx.no_symlinks(path)
    flags = os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK
    try:
        fd = os.open(path, flags | os.O_CREAT | os.O_EXCL, 0o600)
        if result is not None:
            result['storage_mutated'] = True
    except FileExistsError:
        fd = os.open(path, flags)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError('Invalid maintenance runner lock')
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            yield False
        else:
            yield True
    finally:
        os.close(fd)


def invoke(binary: str, context: dict, config: dict, *, apply: bool, timeout: float) -> dict:
    args = [binary, 'maintain', *context['native_args'], '--format', 'json']
    for name in ('max_bytes', 'max_files', 'max_read_bytes'):
        args.extend(('--' + name.replace('_', '-'), str(config[name])))
    if apply:
        args.append('--apply')
    completed = subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, timeout=timeout)
    if len(completed.stdout) > MAX_RESULT_BYTES:
        raise ValueError('Oversized native maintenance result')
    value = json.loads(completed.stdout, object_pairs_hook=context_module().unique_object)
    if (not isinstance(value, dict)
            or value.get('authority_granted', value.get('semantic_authority_granted')) is not False):
        raise ValueError('Native maintenance omitted its authority boundary')
    if not apply and value.get('storage_mutated') is not False:
        raise ValueError('Native maintenance inspection reported mutation')
    if value.get('schema') != 'ledger-maintenance-result/v1':
        return {'schema': 'ledger-maintenance-result/v1', 'outcome': 'failure',
                'storage_mutated': value.get('storage_mutated'), 'code': value.get('code', 'UnknownNativeResult')}
    if value.get('outcome') not in ('healthy', 'blocked', 'incomplete', 'failure'):
        raise ValueError('Unknown native maintenance outcome')
    if completed.returncode and value['outcome'] == 'healthy':
        raise ValueError('Native maintenance returned conflicting success')
    return value


def summary(value: dict) -> dict:
    result = {key: value[key] for key in ('outcome', 'phase', 'storage_mutated', 'code', 'error_code', 'bytes_read', 'file_reads', 'free_bytes')
              if key in value and (value[key] is None or type(value[key]) in (str, int, bool))}
    preparation = value.get('preparation')
    if isinstance(preparation, dict):
        result['preparation'] = {key: preparation[key] for key in ('phase', 'installed', 'observed_by', 'activity', 'complete', 'files', 'bytes', 'reclaimed_bytes')
                                 if key in preparation and (preparation[key] is None or type(preparation[key]) in (str, int, bool))}
    measurements = value.get('measurements')
    if isinstance(measurements, dict):
        result['measurements'] = {key: measurements[key] for key in (
            'scope', 'method', 'coverage', 'observed_entries', 'observed_regular_bytes',
            'directories_with_unknown_size', 'foreign_entry_count', 'required_history_bytes',
            'retained_legacy_bytes', 'physical_bytes_freed')
            if key in measurements and (measurements[key] is None or type(measurements[key]) in (str, int, bool))}
    result['measurement_scope'] = 'bounded native observation; unreported sizes unknown'
    return result


def conditions(value: dict, config: dict) -> list[str]:
    found = []
    if value.get('outcome') != 'healthy':
        found.append(value.get('outcome', 'failure'))
        code = value.get('error_code') or value.get('code')
        if isinstance(code, str) and code.isascii() and code.isalnum() and len(code) <= 128:
            found.append(code)
    free = value.get('free_bytes')
    if type(free) is int and free < config['min_free_bytes']:
        found.append('low-free-space')
    return found


def validate_last_run(value: object) -> dict:
    keys = {'schema', 'started_at', 'completed_at', 'outcome', 'processed_count',
            'selected_count', 'inspection_complete', 'installation'}
    if (not isinstance(value, dict) or set(value) != keys
            or value['schema'] != 'ledger-maintenance-last-run/v1'
            or value['outcome'] not in ('healthy', 'attention', 'incomplete')
            or any(type(value[key]) not in (int, float) or not math.isfinite(value[key])
                   for key in ('started_at', 'completed_at'))
            or value['completed_at'] < value['started_at']
            or any(type(value[key]) is not int or value[key] < 0 for key in ('processed_count', 'selected_count'))
            or value['processed_count'] > value['selected_count']
            or type(value['inspection_complete']) is not bool
            or value['inspection_complete'] and value['processed_count'] != value['selected_count']):
        raise ValueError('Invalid latest maintenance run')
    installation = value['installation']
    if installation is not None and (not isinstance(installation, str) or len(installation) != 64
                                     or any(char not in '0123456789abcdef' for char in installation)):
        raise ValueError('Invalid maintenance installation identity')
    return value


def save_last_run(path: Path, value: dict, ctx) -> None:
    ctx.no_symlinks(path)
    if os.path.lexists(path):
        validate_last_run(ctx.read_document(path, max_bytes=MAX_RESULT_BYTES))
    validate_last_run(value)
    if len(json.dumps(value).encode()) > MAX_RESULT_BYTES:
        raise ValueError('Latest maintenance run exceeds its bound')
    ctx.write_json(path, value)


def run(*, binary: str = 'ledger', config_path: Path | None = None, apply: bool = False,
        store_ids: list[str] | None = None, scheduled: bool = False,
        deadline: float | None = None) -> dict:
    deadline = time.monotonic() + MAX_RUN_SECONDS if deadline is None else deadline
    ctx = context_module()
    home = ctx.storage_home()
    installation = installed_context(home, ctx)
    if config_path is None:
        if installation['status'] not in ('configured', 'missing'):
            return {'schema': 'ledger-maintenance-run/v1', 'outcome': 'attention',
                    'scheduler': installation, 'stores': [], 'storage_mutated': False, 'authority_granted': False}
        config_path = Path(installation['config_path']) if installation['status'] == 'configured' else DEFAULT_CONFIG
    config = load_config(config_path, ctx)
    installation_id = None
    if (scheduled and store_ids is None and installation['status'] == 'configured'
            and config_path.resolve() == Path(installation['config_path'])
            and config == installation['config']):
        installation_id = installation['identity']
    catalog = ctx.read_catalog(home)
    repos = home / 'repos'
    ctx.no_symlinks(repos)
    missing_catalog = not os.path.lexists(home / ctx.CATALOG) and repos.exists() and next(repos.iterdir(), None) is not None
    selected = sorted(catalog['stores']) if store_ids is None else sorted(set(store_ids))
    for store_id in selected:
        ctx.valid_store_id(store_id)
        if store_id not in catalog['stores']:
            raise ValueError('Maintenance selected an uncataloged store')
    observed_scheduler = scheduler_observation(home, ctx, installation=installation)
    result = {'schema': 'ledger-maintenance-run/v1',
              'outcome': 'attention' if (store_ids is not None and observed_scheduler['status'] != 'current')
              or (scheduled and installation_id is None) else 'healthy', 'stores': [],
              'catalog_count': len(catalog['stores']), 'selected_count': len(selected),
              'catalog_status': 'missing-with-existing-roots' if missing_catalog else 'selected',
              'storage_mutated': False, 'authority_granted': False, 'scheduler': observed_scheduler}

    def execute():
        started = time.time()
        incomplete = missing_catalog or len(selected) > config['max_stores']

        for store_id in selected[:config['max_stores']]:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                incomplete = True
                break
            try:
                context = ctx.resolve(store_id=store_id)
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    incomplete = True
                    break
                native = invoke(binary, context, config, apply=apply, timeout=min(MAX_COMMAND_SECONDS, remaining))
            except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
                native = {'outcome': 'failure', 'storage_mutated': None if apply else False,
                          'code': type(exc).__name__}
            item = {'store_id': store_id, **summary(native)}
            condition = conditions(native, config)
            if condition:
                result['outcome'] = 'attention'
            item['conditions'] = condition
            if apply and result['storage_mutated'] is not True and native.get('storage_mutated') is not False:
                result['storage_mutated'] = native.get('storage_mutated')
            result['stores'].append(item)
        if incomplete:
            result['outcome'] = 'incomplete'
        if apply and store_ids is None:
            last = {'schema': 'ledger-maintenance-last-run/v1', 'started_at': started, 'completed_at': time.time(),
                    'outcome': result['outcome'], 'processed_count': len(result['stores']),
                    'selected_count': len(selected), 'inspection_complete': not incomplete,
                    'installation': installation_id}
            try:
                save_last_run(state_root(home) / 'last-run.json', last, ctx)
                result['last_run'] = {'status': 'saved'}
                result['storage_mutated'] = True
            except (OSError, ValueError, RuntimeError) as exc:
                result['last_run'] = {'status': 'failed', 'code': type(exc).__name__,
                                      'message': 'Latest maintenance run could not be read or saved.'}
                result['outcome'] = 'failure'
                if result['storage_mutated'] is not True:
                    result['storage_mutated'] = None
            result['scheduler'] = scheduler_observation(home, ctx)
            if result['last_run']['status'] == 'failed' and result['scheduler']['status'] == 'current':
                result['scheduler'] = {**result['scheduler'], 'status': 'attention', 'outcome': 'failure',
                                       'last_run': result['last_run']}
        return result

    if not apply:
        return execute()
    with runner_lock(home, ctx, result) as locked:
        if not locked:
            return {**result, 'outcome': 'busy'}
        return execute()


def observation() -> dict:
    ctx = context_module()
    try:
        return {'scheduler': scheduler_observation(ctx.storage_home(), ctx)}
    except (OSError, ValueError, RuntimeError):
        return {'scheduler': {'status': 'unknown', 'message': 'Maintenance configuration or state is unavailable.'}}


def routine(context: dict, *, binary: str = 'ledger') -> dict:
    try:
        return run(binary=binary, apply=True, store_ids=[context['store_id']])
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        return {'schema': 'ledger-maintenance-run/v1', 'outcome': 'failure',
                'code': type(exc).__name__, 'storage_mutated': None, 'authority_granted': False}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--store-id', action='append')
    parser.add_argument('--ledger-bin', default='ledger')
    parser.add_argument('--config', type=Path)
    parser.add_argument('--scheduled', action='store_true')
    args = parser.parse_args()
    deadline = time.monotonic() + MAX_RUN_SECONDS
    try:
        result = run(binary=args.ledger_bin, config_path=args.config, apply=args.apply, store_ids=args.store_id,
                     scheduled=args.scheduled, deadline=deadline)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        result = {'schema': 'ledger-maintenance-run/v1', 'outcome': 'failure', 'code': type(exc).__name__,
                  'storage_mutated': None if args.apply else False, 'authority_granted': False}
    print(json.dumps(result, sort_keys=True))
    return 0 if result['outcome'] in ('healthy', 'busy') else 3


if __name__ == '__main__':
    raise SystemExit(main())
