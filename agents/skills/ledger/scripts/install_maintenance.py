#!/usr/bin/env -S uv run python
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile

LABEL = 'com.tkersey.ledger.maintenance'


def maintenance_module():
    path = Path(__file__).with_name('maintain_custody.py')
    spec = importlib.util.spec_from_file_location('maintain_custody', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def launch_agent(python: str, ledger: str, config: Path, home: Path, interval: int) -> dict:
    return {'Label': LABEL,
            'ProgramArguments': [python, str(Path(__file__).with_name('maintain_custody.py').resolve()),
                                 '--apply', '--scheduled', '--config', str(config), '--ledger-bin', ledger],
            'EnvironmentVariables': {'LEDGER_HOME': str(home), 'PATH': '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin'},
            'RunAtLoad': True, 'StartInterval': interval, 'ProcessType': 'Background',
            'StandardOutPath': '/dev/null', 'StandardErrorPath': '/dev/null'}


def install(*, apply: bool = False, config_path: Path | None = None) -> dict:
    maintenance = maintenance_module()
    ctx = maintenance.context_module()
    config_path = config_path or maintenance.DEFAULT_CONFIG
    config = maintenance.load_config(config_path, ctx)
    home = ctx.storage_home()
    brew = shutil.which('brew')
    if brew is None:
        raise RuntimeError('Install the supported Homebrew Ledger tools first')
    python = str(Path(sys.executable).resolve(strict=True))
    subprocess.run([python, '-I', '-c', 'import argparse, fcntl, importlib.util, json, pathlib, plistlib, subprocess'],
                   stdin=subprocess.DEVNULL, capture_output=True, check=True, timeout=30)
    prefix = subprocess.run([brew, '--prefix', 'tkersey/tap/ledger'], capture_output=True, text=True, check=True, timeout=30).stdout.strip()
    ledger = str(Path(prefix) / 'bin/ledger')
    version = subprocess.run([ledger, 'version'], capture_output=True, text=True, check=True, timeout=30).stdout.strip()
    if not re.fullmatch(r'\d+\.\d+\.\d+', version) or not (1, 6, 0) <= tuple(map(int, version.split('.'))) < (2, 0, 0):
        raise RuntimeError('Scheduled maintenance requires the installed Homebrew Ledger >=1.6.0 and <2.0.0')
    target = Path.home() / 'Library/LaunchAgents' / (LABEL + '.plist')
    specification = launch_agent(python, ledger, config_path.resolve(strict=True), home, config['interval_seconds'])
    payload = plistlib.dumps(specification)
    result = {'schema': 'ledger-maintenance-install/v1', 'label': LABEL, 'path': str(target),
              'runtime': ledger, 'version': version, 'interval_seconds': config['interval_seconds'],
              'storage_mutated': False, 'activated': False,
              'authority_granted': False}
    if not apply:
        return {**result, 'launch_agent': specification}
    ctx.no_symlinks(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix='.ledger-maintenance-', dir=target.parent)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
        ctx.sync_directory(target.parent)
    finally:
        if os.path.lexists(temporary):
            os.unlink(temporary)
    domain = 'gui/' + str(os.getuid())
    service = domain + '/' + LABEL
    loaded = subprocess.run(['/bin/launchctl', 'print', service], capture_output=True, timeout=30)
    if loaded.returncode == 0:
        subprocess.run(['/bin/launchctl', 'bootout', service], capture_output=True, check=True, timeout=30)
    subprocess.run(['/bin/launchctl', 'bootstrap', domain, str(target)], capture_output=True, check=True, timeout=30)
    subprocess.run(['/bin/launchctl', 'print', service], capture_output=True, check=True, timeout=30)
    return {**result, 'storage_mutated': True, 'activated': True}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--config', type=Path)
    args = parser.parse_args()
    try:
        result = install(apply=args.apply, config_path=args.config)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        result = {'schema': 'ledger-maintenance-install/v1', 'outcome': 'failure',
                  'error': str(exc), 'storage_mutated': None if args.apply else False,
                  'activated': None if args.apply else False, 'authority_granted': False}
        print(json.dumps(result, sort_keys=True))
        return 3
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
