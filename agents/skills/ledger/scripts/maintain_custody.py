#!/usr/bin/env -S uv run python
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import stat
import time

MAX_RESULT_BYTES = 65536
MAX_RUN_SECONDS = 300
MAX_COMMAND_SECONDS = 30
REMINDER_SECONDS = 86400
DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / 'maintenance.json'


def context_module():
    path = Path(__file__).with_name('ledger_context.py')
    spec = importlib.util.spec_from_file_location('ledger_context', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_config(path: Path, ctx) -> dict:
    value = ctx.read_document(path, max_bytes=4096)
    keys = {'schema', 'interval_seconds', 'max_stores', 'max_bytes', 'max_files',
            'max_read_bytes', 'min_free_bytes', 'notification_route'}
    if not isinstance(value, dict) or set(value) != keys or value['schema'] != 'ledger-maintenance-config/v1':
        raise ValueError('Invalid maintenance configuration')
    bounds = {'interval_seconds': (60, 86400), 'max_stores': (1, 128),
              'max_bytes': (1, 1024**3), 'max_files': (2, 1023),
              'max_read_bytes': (1, 16 * 1024**3), 'min_free_bytes': (0, 1024**5)}
    if any(type(value[key]) is not int or not low <= value[key] <= high
           for key, (low, high) in bounds.items()) or value['notification_route'] != 'osascript':
        raise ValueError('Unsupported maintenance bounds or notification route')
    return value


def state_root(home: Path) -> Path:
    return home / 'maintenance'


def scheduler_observation(home: Path, config: dict, ctx, *, now: float | None = None) -> dict:
    now = time.time() if now is None else now
    path = state_root(home) / 'last-run.json'
    ctx.no_symlinks(path)
    if not os.path.lexists(path):
        return {'status': 'missing', 'message': 'Scheduled Ledger maintenance has no recorded run.'}
    try:
        value = ctx.read_document(path, max_bytes=MAX_RESULT_BYTES)
        value = value.get('observation', value) if isinstance(value, dict) else {}
        completed = value.get('completed_at') if isinstance(value, dict) else None
        if type(completed) not in (int, float) or completed > now + 60:
            raise ValueError('Invalid maintenance completion time')
        if now - completed > config['interval_seconds'] * 2:
            return {'status': 'stale', 'completed_at': completed,
                    'message': 'Scheduled Ledger maintenance has not completed within two intervals.'}
        return {'status': 'current' if value.get('outcome') == 'healthy' else 'attention',
                'completed_at': completed, 'outcome': value.get('outcome', 'unknown')}
    except (ValueError, RuntimeError, OSError):
        return {'status': 'unknown', 'message': 'Scheduled Ledger maintenance state is unreadable.'}


@contextmanager
def runner_lock(home: Path, ctx):
    root = state_root(home)
    ctx.no_symlinks(root)
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = root / 'runner.lock'
    ctx.no_symlinks(path)
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
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


def notify(message: str) -> None:
    script = 'on run argv\ndisplay notification (item 2 of argv) with title (item 1 of argv)\nend run'
    subprocess.run(['/usr/bin/osascript', '-e', script, 'Ledger maintenance', message],
                   stdin=subprocess.DEVNULL, capture_output=True, check=True, timeout=15)


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
        result['preparation'] = {key: preparation[key] for key in ('phase', 'installed', 'files', 'bytes', 'reclaimed_bytes')
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


def update_state(path: Path, observation: dict, condition: list[str], message: str, ctx,
                 *, now: float, send=None) -> dict:
    send = notify if send is None else send
    ctx.no_symlinks(path)
    previous = ctx.read_document(path, max_bytes=MAX_RESULT_BYTES) if os.path.lexists(path) else {}
    if not isinstance(previous, dict):
        raise ValueError('Invalid latest maintenance state')
    notified = previous.get('notified_condition', [])
    notified_at = previous.get('notified_at')
    if not isinstance(notified, list) or (notified_at is not None and type(notified_at) not in (int, float)):
        raise ValueError('Invalid latest notification state')
    changed = condition != notified
    reminder = bool(condition) and notified_at is not None and now - notified_at >= REMINDER_SECONDS
    notification = {'status': 'quiet'}
    if (condition and (changed or reminder)) or (not condition and notified):
        try:
            send(message if condition else message + ' resolved.')
            notified, notified_at = condition, now
            notification = {'status': 'submitted'}
        except (OSError, ValueError, subprocess.SubprocessError):
            notification = {'status': 'failed', 'message': 'The configured local notification command failed.'}
    state = {'schema': 'ledger-maintenance-latest/v1', 'observed_at': now, 'condition': condition,
             'notified_condition': notified, 'notified_at': notified_at, 'notification': notification,
             'observation': observation}
    if len(json.dumps(state).encode()) > MAX_RESULT_BYTES:
        raise ValueError('Latest maintenance state exceeds its bound')
    ctx.write_json(path, state)
    return notification


def run(*, binary: str = 'ledger', config_path: Path = DEFAULT_CONFIG, apply: bool = False,
        store_ids: list[str] | None = None, send=None) -> dict:
    ctx = context_module()
    home = ctx.storage_home()
    config = load_config(config_path, ctx)
    catalog = ctx.read_catalog(home)
    repos = home / 'repos'
    ctx.no_symlinks(repos)
    missing_catalog = not os.path.lexists(home / ctx.CATALOG) and repos.exists() and next(repos.iterdir(), None) is not None
    selected = sorted(catalog['stores']) if store_ids is None else sorted(set(store_ids))
    for store_id in selected:
        ctx.valid_store_id(store_id)
        if store_id not in catalog['stores']:
            raise ValueError('Maintenance selected an uncataloged store')
    observed_scheduler = scheduler_observation(home, config, ctx)
    result = {'schema': 'ledger-maintenance-run/v1',
              'outcome': 'attention' if store_ids is not None and observed_scheduler['status'] != 'current' else 'healthy', 'stores': [],
              'catalog_count': len(catalog['stores']), 'selected_count': len(selected),
              'catalog_status': 'missing-with-existing-roots' if missing_catalog else 'selected',
              'storage_mutated': False, 'authority_granted': False, 'scheduler': observed_scheduler}

    def execute():
        started = time.time()
        deadline = time.monotonic() + MAX_RUN_SECONDS
        incomplete = missing_catalog or len(selected) > config['max_stores']
        for store_id in selected[:config['max_stores']]:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                incomplete = True
                break
            try:
                context = ctx.resolve(store_id=store_id)
                native = invoke(binary, context, config, apply=apply, timeout=min(MAX_COMMAND_SECONDS, remaining))
            except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
                native = {'outcome': 'failure', 'storage_mutated': None if apply else False,
                          'code': type(exc).__name__}
            item = {'store_id': store_id, **summary(native)}
            condition = conditions(native, config)
            if condition:
                result['outcome'] = 'attention'
            if apply:
                item['notification'] = update_state(state_root(home) / (store_id + '.json'), item, condition,
                    'Store ' + store_id + ': ' + (', '.join(condition) if condition else 'maintenance condition'),
                    ctx, now=time.time(), send=send)
                if item['notification']['status'] == 'failed':
                    result['outcome'] = 'attention'
                result['storage_mutated'] = True
            result['stores'].append(item)
        if incomplete:
            result['outcome'] = 'incomplete'
        if apply and store_ids is None:
            last = {'schema': 'ledger-maintenance-last-run/v1', 'started_at': started, 'completed_at': time.time(),
                    'outcome': result['outcome'], 'processed_count': len(result['stores']),
                    'selected_count': len(selected), 'inspection_complete': not incomplete}
            last_condition = ['missing-catalog'] if missing_catalog else (['incomplete-sweep'] if incomplete else [])
            if any(item.get('notification', {}).get('status') == 'failed' for item in result['stores']):
                last_condition.append('notification-failure')
            notification = update_state(state_root(home) / 'last-run.json', last, last_condition,
                'Scheduled sweep: ' + (', '.join(last_condition) if last_condition else 'maintenance condition'),
                ctx, now=time.time(), send=send)
            result['notification'] = notification
            result['scheduler'] = scheduler_observation(home, config, ctx)
            result['storage_mutated'] = True
        return result

    if not apply:
        return execute()
    with runner_lock(home, ctx) as locked:
        if not locked:
            return {**result, 'outcome': 'busy'}
        return execute()


def observation() -> dict:
    ctx = context_module()
    try:
        return {'scheduler': scheduler_observation(ctx.storage_home(), load_config(DEFAULT_CONFIG, ctx), ctx)}
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
    parser.add_argument('--config', type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    try:
        result = run(binary=args.ledger_bin, config_path=args.config, apply=args.apply, store_ids=args.store_id)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        result = {'schema': 'ledger-maintenance-run/v1', 'outcome': 'failure', 'code': type(exc).__name__,
                  'storage_mutated': None if args.apply else False, 'authority_granted': False}
        if args.apply:
            try:
                notify('Scheduled maintenance failed: ' + type(exc).__name__)
                result['notification'] = {'status': 'submitted', 'duplicate_suppression': 'unavailable'}
            except (OSError, subprocess.SubprocessError):
                result['notification'] = {'status': 'failed', 'duplicate_suppression': 'unavailable'}
    print(json.dumps(result, sort_keys=True))
    return 0 if result['outcome'] in ('healthy', 'busy') else 3


if __name__ == '__main__':
    raise SystemExit(main())
