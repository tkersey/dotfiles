#!/usr/bin/env -S uv run python
"""Resolve personal custody, or explicitly maintain selected legacy history.

Normal use resolves the personal catalog, automatically adopting a selected
Git family's existing registration when absent. This only updates catalog
metadata. --migrate selects historical inspection; --apply additionally requires
actual writer quiescence. --ensure-owner migrates an opted-in owner's current
history under writer locks; --read-only selects that owner without maintenance.
Use ledger_context.py for strictly read-only identity lookup.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager, ExitStack
import ctypes
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import uuid

SCHEMA = 'ledger-custody-migration/v2'
ARCHIVES = {'.bindings', '.definitions', '.revisions'}
MAX_FILES = 100000
MAX_BYTES = 2 * 1024**3


class MigrationError(RuntimeError):
    pass


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def unique(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise MigrationError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise MigrationError(f'Cannot load trusted skill helper: {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise MigrationError(f'Not a regular file: {path}')
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def relative(value: str) -> Path:
    if not isinstance(value, str) or not value or '\\' in value:
        raise MigrationError('Invalid relative owner path')
    path = Path(value)
    if path.is_absolute() or any(p in ('', '.', '..') for p in value.split('/')):
        raise MigrationError(f'Unsafe owner path: {value}')
    return path


def owners(skill_root: Path, ctx) -> list[dict]:
    """Only installed sibling skills opt in. Repository files never supply code."""
    found = []
    claimed = set()
    for manifest in sorted(skill_root.glob('*/migration.json')):
        ctx.no_symlinks(manifest)
        raw = manifest.read_bytes()
        if len(raw) > 16384:
            raise MigrationError('Oversized owner migration declaration')
        owner = json.loads(raw, object_pairs_hook=unique)
        if not isinstance(owner, dict) or set(owner) != {'schema', 'definition', 'retired_sources', 'importer'} or owner['schema'] != 'ledger-owner-migration/v1':
            raise MigrationError(f'Invalid owner migration declaration: {manifest}')
        base = manifest.parent
        definition = base / relative(owner['definition'])
        ctx.no_symlinks(definition)
        definition = definition.resolve(strict=True)
        value = json.loads(definition.read_bytes(), object_pairs_hook=unique)
        slots = value.get('storage', {}).get('slots', {})
        if not slots:
            raise MigrationError(f'Owner has no migration slots: {manifest}')
        paths = []
        for slot in slots.values():
            path = relative(slot.get('path'))
            if (slot.get('kind') != 'event-log' or slot.get('codec') != 'jsonl'
                    or slot.get('layout', 'monolithic') != 'monolithic' or '{' in str(path)):
                raise MigrationError(f'Unsupported owner slot layout: {manifest}')
            if str(path) in claimed:
                raise MigrationError(f'Multiple migration owners for slot: {path}')
            claimed.add(str(path))
            paths.append(str(path))
        retired = owner['retired_sources']
        if not isinstance(retired, list) or len(retired) > 16:
            raise MigrationError('Invalid retired source list')
        for name in retired:
            relative(name)
        importer = owner['importer']
        if bool(retired) != bool(importer):
            raise MigrationError('Retired sources require an owner importer')
        if importer:
            importer = base / relative(importer)
            ctx.no_symlinks(importer)
            importer = importer.resolve(strict=True)
        found.append({'name': value['owner'], 'definition': str(definition), 'slots': paths,
                      'retired_sources': retired, 'importer': str(importer) if importer else None,
                      'manifest_sha256': hashlib.sha256(raw).hexdigest()})
    if not found or len(found) > 128:
        raise MigrationError('No supported installed migration owners, or owner bound exceeded')
    return found


def inventory(trees: list[Path], retired: list[str], *, slots: list[str] | tuple[str, ...] = ()) -> dict:
    """Account for every regular byte and link spelling; never follow links."""
    protected = set(retired) | {'.ledger/' + slot for slot in slots}
    protected.update('.ledger/' + name for name in ARCHIVES)
    for slot in slots:
        protected.update(parent.as_posix() for parent in Path('.ledger', slot).parents)
    archives = tuple('.ledger/' + name + '/' for name in ARCHIVES)
    result = {}
    size = 0
    count = 0
    for index, tree in enumerate(trees):
        entries = {}
        roots = [tree / '.ledger', *(tree / name for name in retired)]
        visited = set()
        pending = list(roots)
        while pending:
            path = pending.pop()
            spelling = path.relative_to(tree).as_posix()
            if spelling in visited:
                continue
            visited.add(spelling)
            try:
                info = path.lstat()
            except FileNotFoundError:
                continue
            if stat.S_ISLNK(info.st_mode):
                entries[spelling] = {'kind': 'symlink', 'target': os.readlink(path)}
            elif stat.S_ISDIR(info.st_mode):
                entries[spelling] = {'kind': 'directory'}
                pending.extend(sorted(path.iterdir(), reverse=True))
            elif stat.S_ISREG(info.st_mode):
                size += info.st_size
                entries[spelling] = {'kind': 'file', 'size': info.st_size, 'sha256': digest_file(path)}
            elif stat.S_ISFIFO(info.st_mode) and spelling not in protected and not spelling.startswith(archives):
                # A pipe has no retained byte stream. Preserve its topology in
                # the archive manifest, without opening or recreating it.
                entries[spelling] = {'kind': 'fifo', 'mode': stat.S_IMODE(info.st_mode)}
            else:
                raise MigrationError(f'Unsupported special source entry: {path}')
            count += 1
            if count > MAX_FILES or size > MAX_BYTES:
                raise MigrationError('Migration inventory bound exceeded')
        result[str(index)] = {'workspace': str(tree), 'entries': entries}
    return result


def prefix(left: Path, right: Path) -> bool:
    if left.stat().st_size == right.stat().st_size and digest_file(left) == digest_file(right):
        return True
    with left.open('rb') as a, right.open('rb') as b:
        last = b''
        for block in iter(lambda: a.read(1024 * 1024), b''):
            if b.read(len(block)) != block:
                return False
            last = block[-1:]
    return last in (b'', b'\n')


def select_source(trees: list[Path], slots: list[str], ctx) -> Path | None:
    candidates = []
    for tree in trees:
        for slot in slots:
            path = tree / '.ledger' / slot
            ctx.no_symlinks(path)
            if os.path.lexists(path) and not path.is_file():
                raise MigrationError(f'Unsupported selected slot: {path}')
        if any((tree / '.ledger' / slot).exists() for slot in slots):
            candidates.append(tree)
    covering = []
    for candidate in candidates:
        if all(not (other / '.ledger' / slot).exists() or
               ((candidate / '.ledger' / slot).exists() and prefix(other / '.ledger' / slot, candidate / '.ledger' / slot))
               for other in candidates for slot in slots):
            covering.append(candidate)
    if candidates and not covering:
        raise MigrationError('Divergent/additional selected histories; no unique complete history. Owner reconciliation required')
    # Ties are byte-equivalent histories, not timestamp/path-based authority.
    return min(covering, key=str) if covering else None


def native(binary: str, owner: dict, selector: list[str], command: str, *args: str,
           allow_unhealthy: bool = False, wait_busy: bool = False) -> dict:
    subcommand = []
    if command == 'definition':
        if not args:
            raise MigrationError('Missing definition subcommand')
        subcommand, args = [args[0]], args[1:]
    waiting = False
    while True:
        proc = subprocess.run([binary, command, *subcommand, '--definition', owner['definition'], *selector, *args, '--format', 'json'], capture_output=True)
        try:
            result = json.loads(proc.stdout, object_pairs_hook=unique)
        except (ValueError, UnicodeError) as exc:
            raise MigrationError(f'Invalid native {command} result for {owner["name"]}') from exc
        busy_codes = ('LockBusy', 'EventStoreBusy')
        busy = isinstance(result, dict) and (result.get('code') in busy_codes or
               any(slot.get('error_code') in busy_codes for slot in result.get('slots', [])))
        if not (wait_busy and command == 'doctor' and busy):
            break
        if not waiting:
            print(f'Waiting for active Ledger writer: {owner["name"]}', file=sys.stderr, flush=True)
            waiting = True
        time.sleep(0.1)
    if not isinstance(result, dict) or result.get('authority_granted', result.get('semantic_authority_granted')) is not False:
        raise MigrationError('Native result omitted its authority boundary')
    if proc.returncode and not (allow_unhealthy and result.get('schema') == 'ledger-doctor-result/v1'):
        raise MigrationError(f'Native {command} failed: {canonical(result)}')
    return result


def healthy(binary: str, owner: dict, selector: list[str], *, repair: bool = False,
            wait_busy: bool = False) -> dict:
    result = native(binary, owner, selector, 'doctor', allow_unhealthy=True, wait_busy=wait_busy)
    if (result.get('schema') != 'ledger-doctor-result/v1' or result.get('pending_transactions') != 0
            or result.get('storage_mutated') is not False):
        raise MigrationError(f'Unresolved transaction/coverage for {owner["name"]}')
    if result.get('healthy') is True:
        return result
    if not repair:
        raise MigrationError(f'Owner custody requires native maintenance: {canonical(result)}')
    failed = [slot for slot in result.get('slots', []) if slot.get('healthy') is not True]
    if len(failed) != 1 or len(owner['slots']) != 1:
        raise MigrationError(f'Ambiguous custody failure; refusing automatic repair: {canonical(result)}')
    code = failed[0].get('error_code')
    if code == 'InvalidStoreBinding':
        operation = 'bind-existing'  # Native must prove binding is absent, not malformed.
    elif code in ('StoreBindingRecordCountMismatch', 'StoreBindingRevisionMismatch'):
        operation = 'rebind-existing'
    else:
        raise MigrationError(f'Unknown custody failure; refusing automatic repair: {canonical(result)}')
    repaired = native(binary, owner, selector, 'transact', '--operation', operation)
    if repaired.get('schema') != 'ledger-transaction-result/v1' or repaired.get('valid') is not True:
        raise MigrationError('Unverified binding maintenance receipt')
    return healthy(binary, owner, selector, wait_busy=wait_busy)


def copy_inventory(snapshot: dict, destination: Path) -> None:
    for index, tree in snapshot.items():
        root = Path(tree['workspace'])
        for name, entry in tree['entries'].items():
            target = destination / ('worktree-' + index) / name
            if entry['kind'] == 'directory':
                target.mkdir(parents=True, exist_ok=True, mode=0o700)
            elif entry['kind'] == 'file':
                target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                shutil.copyfile(root / name, target, follow_symlinks=False)
                if target.is_symlink() or digest_file(target) != entry['sha256']:
                    raise MigrationError(f'Changed source while archiving: {root / name}')
                target.chmod(0o600)
            # Symlink spellings and FIFO metadata stay in the manifest, not live.


def sync_tree(path: Path, ctx) -> None:
    directories = []
    for root, dirs, files in os.walk(path):
        directories.append(Path(root))
        for name in files:
            with (Path(root) / name).open('rb') as handle:
                os.fsync(handle.fileno())
    for directory in reversed(directories):
        ctx.sync_directory(directory)


def ensure(repo: Path | None = None, *, store_id: str | None = None) -> dict:
    """Resolve custody or catalog an existing Git registration without moving it."""
    ctx = load_module(Path(__file__).with_name('ledger_context.py'))
    try:
        return ctx.resolve(repo, store_id=store_id)
    except ctx.UnregisteredContext:
        # Only absence permits adoption: corrupt catalog/root, conflicting
        # aliases and explicit unknown identities must retain their failures.
        if repo is None or store_id is not None:
            raise
        root, common, _ = ctx.workspace_associations(repo)
        if common is None or not os.path.lexists(common / ctx.REGISTRATION):
            raise
        # The existing import validates the registration and root and publishes
        # under the catalog lock, rejecting races with conflicting associations.
        return ctx.import_registration(common / ctx.REGISTRATION, root)


def selected_owner(definition: Path, ctx, skill_root: Path | None = None) -> dict:
    selected = [owner for owner in owners(skill_root or Path(__file__).resolve().parents[2], ctx)
                if Path(owner['definition']) == definition.resolve(strict=True)]
    if len(selected) != 1 or len(selected[0]['slots']) != 1:
        raise MigrationError('Owner selection requires one installed owner with one static event slot')
    return selected[0]


def archive_entries(custody: Path, slot: str, ctx):
    archive_root = custody / 'legacy-archive'
    ctx.no_symlinks(archive_root)
    manifests = sorted(archive_root.glob('*/manifest.json'))
    if len(manifests) > 128:
        raise MigrationError('Archive repair manifest bound exceeded')
    total = 0
    for manifest in manifests:
        value = ctx.read_document(manifest, max_bytes=32 * 1024**2)
        total += manifest.stat().st_size
        if total > MAX_BYTES:
            raise MigrationError('Archive manifest byte bound exceeded')
        if (not isinstance(value, dict) or value.get('schema') != 'ledger-legacy-archive/v1'
                or not isinstance(value.get('sources'), dict) or len(value['sources']) > 128):
            raise MigrationError('Invalid archive manifest')
        for index, tree in value['sources'].items():
            if not index.isascii() or not index.isdigit():
                raise MigrationError('Invalid archive worktree index')
            if (not isinstance(tree, dict) or not isinstance(tree.get('entries'), dict)
                    or len(tree['entries']) > MAX_FILES):
                raise MigrationError('Invalid archive source inventory')
            entry = tree['entries'].get('.ledger/' + slot)
            if entry is not None:
                if not isinstance(entry, dict):
                    raise MigrationError('Invalid archived slot entry')
                yield manifest.parent / ('worktree-' + index) / '.ledger' / slot, entry


def verify_local_prefix(context: dict, owner: dict, ctx) -> None:
    if not context.get('workspace_root'):
        return
    for slot in owner['slots']:
        local = Path(context['workspace_root']) / '.ledger' / slot
        active = Path(context['store_root']) / '.ledger' / slot
        ctx.no_symlinks(local)
        ctx.no_symlinks(active)
        if local.exists() and (not active.exists() or not prefix(local, active)):
            raise MigrationError('Local history is not covered by managed custody; select explicit migration or reconciliation')


def owner_context(repo: Path | None, definition: Path, *, store_id: str | None = None,
                  maintain: bool = False, read_only: bool = False,
                  binary: str = 'ledger', skill_root: Path | None = None) -> dict:
    if maintain and read_only:
        raise MigrationError('Read-only owner selection cannot repair or migrate')
    ctx = load_module(Path(__file__).with_name('ledger_context.py'))
    owner = selected_owner(definition, ctx, skill_root)
    try:
        context = ctx.resolve(repo, store_id=store_id)
    except ctx.UnregisteredContext:
        if store_id is not None:
            raise
        root, common, _ = ctx.workspace_associations(repo)
        if common is not None and os.path.lexists(common / ctx.REGISTRATION):
            context = ctx.checked_registration(root, common) if read_only else ctx.import_registration(common / ctx.REGISTRATION, root)
        else:
            context = None

    def has_local_history():
        if context is None or not context.get('workspace_root'):
            return False
        root = Path(context['workspace_root'])
        trees = ctx.worktrees(root) if context.get('git_common_dir') else [root]
        binding = '.bindings/' + hashlib.sha256(owner['slots'][0].encode()).hexdigest() + '.jsonl'
        return any(os.path.lexists(tree / '.ledger' / name) for tree in trees
                   for name in (owner['slots'][0], binding))

    if context is not None:
        result = native(binary, owner, context['native_args'], 'doctor', allow_unhealthy=True, wait_busy=maintain)
        if result.get('healthy') is True and result.get('pending_transactions') == 0:
            if any(slot.get('status') != 'missing' for slot in result['slots']):
                verify_local_prefix(context, owner, ctx)
                return context
            local_exists = has_local_history()
            archived = any(archive_entries(Path(context['store_root']), owner['slots'][0], ctx))
            if not local_exists and not archived:
                return context
        elif not maintain:
            raise MigrationError(f'Selected managed custody is unhealthy: {canonical(result)}')
        elif any(slot.get('error_code') == 'StoreBindingWithoutSlot' for slot in result.get('slots', [])):
            if not has_local_history() and any(archive_entries(Path(context['store_root']), owner['slots'][0], ctx)):
                return restore_archived_slot(context, definition, binary=binary, skill_root=skill_root)
        else:
            raise MigrationError(f'Selected managed custody needs native recovery: {canonical(result)}')
    if read_only or not maintain:
        raise MigrationError('Owner history needs --ensure-owner preparation; read-only selection leaves custody unchanged')
    return migrate_owner(repo, definition, store_id=store_id, binary=binary, skill_root=skill_root)


@contextmanager
def native_lock(path: Path, ctx, *, wait: bool = True):
    ctx.no_symlinks(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise MigrationError(f'Invalid native advisory resource: {path}')
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            if not wait:
                raise
            print(f'Waiting for active Ledger writer: {path}', file=sys.stderr, flush=True)
            fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def publish_absent(source: Path, target: Path) -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform == 'darwin':
        rename = libc.renamex_np
        rename.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        args = (os.fsencode(source), os.fsencode(target), 4)
    elif sys.platform.startswith('linux') and hasattr(libc, 'renameat2'):
        rename = libc.renameat2
        rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        args = (-100, os.fsencode(source), -100, os.fsencode(target), 1)
    else:
        raise MigrationError('This platform lacks atomic no-replace publication')
    rename.restype = ctypes.c_int
    if rename(*args) != 0:
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code), str(target))


def restore_archived_slot(context: dict, definition: Path, *, binary: str = 'ledger',
                          skill_root: Path | None = None) -> dict:
    ctx = load_module(Path(__file__).with_name('ledger_context.py'))
    owner = selected_owner(definition, ctx, skill_root)
    custody = Path(context['store_root'])
    slot = owner['slots'][0]
    target = custody / '.ledger' / slot

    def diagnose():
        result = native(binary, owner, context['native_args'], 'doctor', allow_unhealthy=True, wait_busy=True)
        if (result.get('schema') != 'ledger-doctor-result/v1' or result.get('pending_transactions') != 0
                or result.get('storage_mutated') is not False):
            raise MigrationError('Archive repair refuses unresolved transactions or coverage')
        if result.get('healthy') is True:
            return result
        failed = result.get('slots', [])
        if (len(failed) != 1 or failed[0].get('logical_ref') != slot
                or failed[0].get('error_code') != 'StoreBindingWithoutSlot'):
            raise MigrationError(f'Archive repair cannot resolve this failure: {canonical(result)}')
        ctx.no_symlinks(target)
        if os.path.lexists(target):
            raise MigrationError('Archive repair never replaces an existing slot')
        return result

    if diagnose().get('healthy') is True:
        verify_local_prefix(context, owner, ctx)
        if not target.exists() and any(archive_entries(custody, slot, ctx)):
            raise MigrationError('Archived owner history needs explicit migration; refusing an empty replacement')
        return context
    version = subprocess.run([binary, 'version'], capture_output=True, text=True, check=True).stdout.strip()
    if not re.fullmatch(r'\d+\.\d+\.\d+', version) or not (1, 3, 0) <= tuple(map(int, version.split('.'))) < (2, 0, 0):
        raise MigrationError('Archive repair requires Ledger >=1.3.0 and <2.0.0')
    with ExitStack() as locks:
        transactions = custody / '.ledger/.transactions'
        locks.enter_context(native_lock(transactions / '.recovery.advisory', ctx))
        if diagnose().get('healthy') is True:
            return context
        binding = custody / '.ledger/.bindings' / (hashlib.sha256(slot.encode()).hexdigest() + '.jsonl')
        for path in sorted((binding, target)):
            locks.enter_context(native_lock(Path(str(path) + '.cas.lock.advisory'), ctx))
            if os.path.lexists(Path(str(path) + '.cas.lock')):
                raise MigrationError('Legacy lease requires native recovery before archive repair')
        locks.enter_context(native_lock(transactions / '.journal.advisory', ctx))
        candidates = {}
        total = 0
        for source, entry in archive_entries(custody, slot, ctx):
            ctx.no_symlinks(source)
            total += source.stat().st_size
            if total > MAX_BYTES or len(candidates) >= 128:
                raise MigrationError('Archive repair candidate bound exceeded')
            if (entry.get('kind') != 'file' or source.stat().st_size != entry.get('size')
                    or digest_file(source) != entry.get('sha256')):
                raise MigrationError('Archived slot no longer matches its inventory')
            candidates.setdefault(entry['sha256'], source)
        if not candidates:
            raise MigrationError('No archived bytes exist for the missing slot')
        with tempfile.TemporaryDirectory(prefix='.slot-repair-', dir=custody) as temporary:
            stage = Path(temporary)
            sources = [custody / ctx.MARKER]
            for name in sorted(ARCHIVES):
                directory = custody / '.ledger' / name
                ctx.no_symlinks(directory)
                for root, dirs, files in os.walk(directory, followlinks=False):
                    for child in dirs + files:
                        ctx.no_symlinks(Path(root) / child)
                    sources.extend(Path(root) / name for name in files if not name.endswith('.advisory'))
                    if len(sources) > MAX_FILES:
                        raise MigrationError('Archive repair custody file bound exceeded')
            for source in sources:
                ctx.no_symlinks(source)
                total += source.stat().st_size
                if total > MAX_BYTES:
                    raise MigrationError('Archive repair byte bound exceeded')
                destination = stage / source.relative_to(custody)
                destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                before = digest_file(source)
                shutil.copyfile(source, destination, follow_symlinks=False)
                destination.chmod(0o600)
                if digest_file(destination) != before or digest_file(source) != before:
                    raise MigrationError('Custody changed while staging archive repair')
            staged_slot = stage / '.ledger' / slot
            staged_slot.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            for digest, source in candidates.items():
                shutil.copyfile(source, staged_slot, follow_symlinks=False)
                staged_slot.chmod(0o600)
                if digest_file(staged_slot) != digest:
                    raise MigrationError('Archive changed while staging repair')
                result = native(binary, owner, ['--store-root', str(stage), '--store-id', context['store_id']],
                                'doctor', allow_unhealthy=True)
                if result.get('healthy') is not True or result.get('pending_transactions') != 0:
                    continue
                workspace = context.get('workspace_root')
                if workspace:
                    local = Path(workspace) / '.ledger' / slot
                    ctx.no_symlinks(local)
                    if local.exists() and digest_file(local) != digest:
                        raise MigrationError('Local history differs from the bound archive; reconcile explicitly')
                sync_tree(stage, ctx)
                ctx.no_symlinks(target)
                publish_absent(staged_slot, target)
                ctx.sync_directory(target.parent)
                break
            else:
                raise MigrationError('No archive satisfies the existing native binding; refusing rebind')
    result = healthy(binary, owner, context['native_args'], wait_busy=True)
    return {**context, 'storage_mutated': True,
            'custody_repair': {'slot': slot, 'archive': str(source), 'sha256': digest, 'doctor': result}}


def migrate_owner(repo: Path | None, definition: Path, *, store_id: str | None = None,
                  binary: str = 'ledger', skill_root: Path | None = None) -> dict:
    ctx = load_module(Path(__file__).with_name('ledger_context.py'))
    owner = selected_owner(definition, ctx, skill_root)
    if owner['retired_sources']:
        raise MigrationError('Retired-format imports require the owner historical importer')
    version = subprocess.run([binary, 'version'], capture_output=True, text=True, check=True).stdout.strip()
    if not re.fullmatch(r'\d+\.\d+\.\d+', version) or not (1, 3, 0) <= tuple(map(int, version.split('.'))) < (2, 0, 0):
        raise MigrationError('Automatic owner migration requires Ledger >=1.3.0 and <2.0.0')
    root, common, _ = ctx.workspace_associations(repo)
    if root is not None and not root.is_dir():
        raise MigrationError('Migration requires an existing selected workspace')
    slot = owner['slots'][0]
    binding_ref = '.ledger/.bindings/' + hashlib.sha256(slot.encode()).hexdigest() + '.jsonl'
    home = ctx.storage_home()
    with ExitStack() as held:
        if common is not None:
            held.enter_context(ctx.registration_lock(common))
        held.enter_context(ctx.catalog_lock(home))
        try:
            context = ctx.resolve(repo, store_id=store_id)
        except ctx.UnregisteredContext:
            if store_id is not None:
                raise
            context = ctx.checked_registration(root, common) if common is not None and os.path.lexists(common / ctx.REGISTRATION) else None
        trees = sorted(ctx.worktrees(root), key=str) if common is not None else ([root] if root is not None else [])
        for tree in trees:
            ctx.no_symlinks(tree / '.ledger')
        sources = [tree for tree in trees if os.path.lexists(tree / '.ledger' / slot) or os.path.lexists(tree / binding_ref)]
        if context is None:
            if root is None:
                raise MigrationError('New owner custody requires a selected workspace')
            repos = home / 'repos'
            ctx.no_symlinks(repos)
            catalog = ctx.read_catalog(home)
            if repos.exists() and any(p.is_dir() and str(p) not in catalog['stores'].values() for p in repos.iterdir()):
                raise MigrationError('Unregistered custody exists; resolve its identity before creating a replacement')
            repos.mkdir(parents=True, exist_ok=True, mode=0o700)
            selected_id = uuid.uuid4().hex
            custody = Path(held.enter_context(tempfile.TemporaryDirectory(prefix='.migrating-', dir=repos)))
            (custody / '.ledger').mkdir(mode=0o700)
            ctx.write_json(custody / ctx.MARKER, {'schema': ctx.MARKER_SCHEMA, 'store_id': selected_id})
        else:
            custody = Path(context['store_root'])
            selected_id = context['store_id']
        mutable = sorted(set([*sources, custody]), key=str)
        for tree in mutable:
            held.enter_context(native_lock(tree / '.ledger/.transactions/.recovery.advisory', ctx))
            for path in sorted((tree / binding_ref, tree / '.ledger' / slot)):
                held.enter_context(native_lock(Path(str(path) + '.cas.lock.advisory'), ctx))
                if os.path.lexists(Path(str(path) + '.cas.lock')):
                    raise MigrationError('An abandoned legacy lease requires native recovery')
            held.enter_context(native_lock(tree / '.ledger/.transactions/.journal.advisory', ctx))
        if context is not None:
            sources.append(custody)
            for archived, entry in archive_entries(custody, slot, ctx):
                ctx.no_symlinks(archived)
                if entry.get('kind') != 'file' or digest_file(archived) != entry.get('sha256'):
                    raise MigrationError('Archived migration source differs from its manifest')
                sources.append(archived.parents[len(Path(slot).parts)])
        sources = sorted(set(sources), key=str)
        snapshot = inventory(sources, [], slots=[slot])
        fingerprint = hashlib.sha256(canonical(snapshot).encode()).hexdigest()
        archive = custody / 'legacy-archive' / fingerprint
        ctx.no_symlinks(archive)
        archive.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if not archive.exists():
            with tempfile.TemporaryDirectory(prefix='.owner-archive-', dir=archive.parent) as temporary:
                staged_archive = Path(temporary) / 'snapshot'
                staged_archive.mkdir(mode=0o700)
                copy_inventory(snapshot, staged_archive)
                ctx.write_json(staged_archive / 'manifest.json', {'schema': 'ledger-legacy-archive/v1', 'sources': snapshot})
                sync_tree(staged_archive, ctx)
                publish_absent(staged_archive, archive)
                ctx.sync_directory(archive.parent)
        else:
            saved = ctx.read_document(archive / 'manifest.json', max_bytes=32 * 1024**2)
            if saved.get('sources') != snapshot:
                raise MigrationError('Existing migration archive has different sources')
        copies = [archive / ('worktree-' + str(index)) for index in range(len(sources))]
        for index, tree in enumerate(copies):
            for name, entry in snapshot[str(index)]['entries'].items():
                if entry['kind'] == 'file' and digest_file(tree / name) != entry['sha256']:
                    raise MigrationError('Migration archive failed byte verification')
            if ((tree / '.ledger' / slot).exists()
                    or (sources[index] != custody and (tree / binding_ref).exists())):
                healthy(binary, owner, ['--repo', str(tree)])
        source = select_source(copies, [slot], ctx)
        with tempfile.TemporaryDirectory(prefix='.owner-import-', dir=custody) as temporary:
            proposal = Path(temporary)
            ctx.write_json(proposal / ctx.MARKER, {'schema': ctx.MARKER_SCHEMA, 'store_id': selected_id})
            (proposal / '.ledger').mkdir(mode=0o700)
            origins = []
            if context is not None:
                origins.append(copies[sources.index(custody)])
            if source is not None and source not in origins:
                origins.append(source)
            for origin in origins:
                index = copies.index(origin)
                for name, entry in snapshot[str(index)]['entries'].items():
                    if name not in ('.ledger/' + slot, binding_ref) and not name.startswith(('.ledger/.definitions/', '.ledger/.revisions/')):
                        continue
                    if entry['kind'] != 'file' or name.endswith('.advisory'):
                        continue
                    destination = proposal / name
                    if destination.exists():
                        if name in ('.ledger/' + slot, binding_ref):
                            continue
                        if digest_file(destination) != entry['sha256']:
                            raise MigrationError('Conflicting immutable native custody archive')
                        continue
                    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                    shutil.copyfile(origin / name, destination)
                    destination.chmod(0o600)
            if source is not None:
                proposed_slot = proposal / '.ledger' / slot
                if proposed_slot.exists() and not prefix(source / '.ledger' / slot, proposed_slot):
                    raise MigrationError('Managed and local histories need owner reconciliation')
            staged_selector = ['--store-root', str(proposal), '--store-id', selected_id]
            healthy(binary, owner, staged_selector)
            sync_tree(proposal, ctx)
            if common is not None and sorted(ctx.worktrees(root), key=str) != trees:
                raise MigrationError('Worktree coverage changed during migration; retry')
            files = sorted(path for path in (proposal / '.ledger').rglob('*') if path.is_file())
            event = proposal / '.ledger' / slot
            files = [path for path in files if path != event] + ([event] if event.exists() else [])
            for path in files:
                destination = custody / path.relative_to(proposal)
                ctx.no_symlinks(destination)
                if destination.exists():
                    if digest_file(path) != digest_file(destination):
                        raise MigrationError('Existing managed bytes changed; refusing replacement')
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                publish_absent(path, destination)
                ctx.sync_directory(destination.parent)
        if context is None:
            final = custody.parent / selected_id
            publish_absent(custody, final)
            ctx.sync_directory(final.parent)
            custody = final
        result = ctx._register_root_locked(custody, selected_id, root, home)
        result['storage_mutated'] = True
        result['owner_migration'] = {'owner': owner['name'], 'archive': str(custody / 'legacy-archive' / fingerprint),
                                     'source_count': len(sources)}
    healthy(binary, owner, result['native_args'], wait_busy=True)
    return result


def migration_source(repo: Path, ctx) -> tuple[Path, Path | None]:
    """Select a verified Git family or one explicitly named surviving directory."""
    selected = repo.expanduser().absolute()
    ctx.no_symlinks(selected)
    if not selected.is_dir():
        raise MigrationError(f'Legacy source must be an existing directory: {selected}')
    if os.path.lexists(selected / ctx.MARKER):
        raise MigrationError('Existing managed root requires --register-root with its original store ID, not migration')
    try:
        root, common = ctx.workspace(selected)
    except ctx.ContextError as exc:
        # A broken checkout is not evidence that its other worktrees disappeared.
        # Bare controls also survive an unreadable or missing HEAD.
        if any(
            os.path.lexists(parent / '.git')
            or all(os.path.lexists(parent / name) for name in ('config', 'objects', 'refs'))
            for parent in (selected, *selected.parents)
        ):
            raise MigrationError(f'Cannot establish Git family coverage for legacy source: {selected}') from exc
        try:
            ctx.git(selected, 'rev-parse', '--git-dir')
        except ctx.ContextError:
            pass
        else:
            raise MigrationError(f'Legacy source is Git metadata, not a verified worktree: {selected}') from exc
    else:
        if os.path.lexists(root / ctx.MARKER):
            raise MigrationError('Existing managed root requires --register-root with its original store ID, not migration')
        return root, common
    return selected.resolve(strict=True), None


def migrate(repo: Path, *, store_id: str | None = None, apply: bool = False, confirm_no_writers: bool = False,
           binary: str = 'ledger', skill_root: Path | None = None, framing_controls: dict | None = None) -> dict:
    if apply and not confirm_no_writers:
        raise MigrationError('--apply requires --confirm-no-writers after actually quiescing legacy and managed writers')
    ctx = load_module(Path(__file__).with_name('ledger_context.py'))
    workspace, common = migration_source(repo, ctx)
    installed = skill_root or Path(__file__).resolve().parents[2]
    selected = owners(installed, ctx)
    slots = [slot for owner in selected for slot in owner['slots']]
    retired = sorted({name for owner in selected for name in owner['retired_sources']})

    def inspect():
        if migration_source(repo, ctx) != (workspace, common):
            raise MigrationError('Legacy source/Git association changed; inspect and retry')
        trees = sorted(ctx.worktrees(workspace), key=str) if common is not None else [workspace]
        for tree in trees:
            ctx.no_symlinks(tree / '.ledger')
            for name in retired:
                ctx.no_symlinks(tree / name)
        snapshot = inventory(trees, retired, slots=slots)
        source = select_source(trees, slots, ctx)
        # Native owns pending transaction interpretation; never infer from lock age.
        for tree in trees:
            for owner in selected:
                if any((tree / '.ledger' / slot).exists() for slot in owner['slots']):
                    result = native(binary, owner, ['--repo', str(tree)], 'doctor', allow_unhealthy=True)
                    if result.get('pending_transactions') != 0:
                        raise MigrationError(f'Legacy transaction coverage is not clear: {tree}')
            for name, entry in snapshot[str(trees.index(tree))]['entries'].items():
                if name.endswith('.cas.lock'):
                    raise MigrationError(f'Legacy lease requires native recovery: {tree / name}')
        return trees, snapshot, source

    def current_context():
        try:
            context = ctx.resolve(workspace, store_id=store_id)
        except ctx.UnregisteredContext:
            # This is explicit maintenance, not a fallback in ordinary lookup.
            if common is not None and os.path.lexists(common / ctx.REGISTRATION):
                context = ctx.checked_registration(workspace, common)
            else:
                return None
        if common is not None and os.path.lexists(common / ctx.REGISTRATION):
            legacy = ctx.checked_registration(workspace, common)
            if (legacy['store_id'] != context['store_id']
                    or Path(legacy['store_root']).resolve(strict=True) != Path(context['store_root']).resolve(strict=True)):
                raise MigrationError('Selected workspace has a different legacy registration; reconcile explicitly before migration')
        return context

    trees, snapshot, source = inspect()
    context = current_context()
    registered = context is not None
    fingerprint = hashlib.sha256(canonical({'sources': snapshot, 'owners': selected,
        'definitions': {o['definition']: digest_file(Path(o['definition'])) for o in selected},
        'importers': {o['importer']: digest_file(Path(o['importer'])) for o in selected if o['importer']},
        'framing': framing_controls or {}}).encode()).hexdigest()
    descriptions = []
    for owner in selected:
        descriptions.append(native(binary, owner, [], 'definition', 'describe'))
    fingerprint = hashlib.sha256((fingerprint + canonical([d.get('definition') for d in descriptions])).encode()).hexdigest()
    def destination_prefixes(custody):
        revisions = {}
        for slot in slots:
            path = custody / '.ledger' / slot
            ctx.no_symlinks(path)
            revisions[slot] = {'bytes': path.stat().st_size, 'sha256': digest_file(path)} if path.exists() else None
        return revisions

    def preserves_imported_prefixes(custody, witnessed):
        if not isinstance(witnessed, dict) or set(witnessed) != set(slots):
            return False
        for slot, witness in witnessed.items():
            if witness is None:
                continue
            if (not isinstance(witness, dict) or set(witness) != {'bytes', 'sha256'}
                    or type(witness['bytes']) is not int or witness['bytes'] < 0
                    or not isinstance(witness['sha256'], str)):
                return False
            path = custody / '.ledger' / slot
            ctx.no_symlinks(path)
            if not path.is_file() or path.stat().st_size < witness['bytes']:
                return False
            remaining = witness['bytes']
            digest = hashlib.sha256()
            with path.open('rb') as handle:
                while remaining:
                    block = handle.read(min(1048576, remaining))
                    if not block:
                        return False
                    digest.update(block)
                    remaining -= len(block)
            if digest.hexdigest() != witness['sha256']:
                return False
        return True

    if registered:
        receipt_path = Path(context['store_root']) / 'migration-receipt.json'
        ctx.no_symlinks(receipt_path)
        if receipt_path.exists():
            saved = json.loads(receipt_path.read_bytes(), object_pairs_hook=unique)
            if (saved.get('schema') == SCHEMA and saved.get('fingerprint') == fingerprint
                    and saved.get('status') == 'verified'
                    and saved.get('store_id') == context['store_id']
                    and preserves_imported_prefixes(Path(context['store_root']), saved.get('destination_prefixes'))):
                for owner in selected:
                    healthy(binary, owner, context['native_args'])
                if apply:
                    if inspect()[1] != snapshot:
                        raise MigrationError('Source view changed before catalog adoption; inspect and retry')
                    context = ctx.register_root(Path(context['store_root']), context['store_id'], workspace)
                return {**saved, 'context': context, 'storage_mutated': context.get('storage_mutated', False)}
    if not apply:
        return {'schema': SCHEMA, 'status': 'planned', 'registered': registered, 'context': context,
                'fingerprint': fingerprint, 'sources': snapshot, 'selected_source': str(source) if source else None,
                'owners': selected, 'requires': ['--migrate', '--apply', '--confirm-no-writers'],
                'storage_mutated': False, 'authority_granted': False}
    lock_root = common
    if lock_root is None:
        # The surviving source may be read-only; control state belongs to custody.
        lock_root = ctx.storage_home()
        ctx.no_symlinks(lock_root)
        lock_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    home = ctx.storage_home()
    with ctx.registration_lock(lock_root), ctx.catalog_lock(home):
        # Reject a changed view rather than silently applying a new migration.
        current = current_context()
        if inspect()[1] != snapshot or (current is not None) != registered:
            raise MigrationError('Migration inputs changed; inspect and retry')
        if registered:
            if current['store_id'] != context['store_id'] or current['store_root'] != context['store_root']:
                raise MigrationError('Registered identity changed')
            custody = Path(context['store_root'])
            selector = context['native_args']
            for tree in trees:
                for slot in slots:
                    old = tree / '.ledger' / slot
                    active = custody / '.ledger' / slot
                    ctx.no_symlinks(active)
                    if old.exists() and (not active.exists() or not prefix(old, active)):
                        raise MigrationError(f'Additional/divergent history after registration: {old}')
        else:
            repos = ctx.storage_home() / 'repos'
            ctx.no_symlinks(repos)
            repos.mkdir(parents=True, exist_ok=True, mode=0o700)
            new_id = uuid.uuid4().hex
            custody = Path(tempfile.mkdtemp(prefix='.migrating-', dir=repos))
            (custody / '.ledger').mkdir(mode=0o700)
            ctx.write_json(custody / ctx.MARKER, {'schema': ctx.MARKER_SCHEMA, 'store_id': new_id})
            selector = ['--store-root', str(custody), '--store-id', new_id]
        # Keep interrupted evidence for inspection. Never auto-select an orphan.
        archive = custody / 'legacy-archive' / fingerprint
        ctx.no_symlinks(archive)
        if not archive.exists():
            archive.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            temporary = Path(tempfile.mkdtemp(prefix='.archiving-', dir=archive.parent))
            copy_inventory(snapshot, temporary)
            ctx.write_json(temporary / 'manifest.json', {'schema': 'ledger-legacy-archive/v1', 'sources': snapshot})
            sync_tree(temporary, ctx)
            os.rename(temporary, archive)
            ctx.sync_directory(archive.parent)
        else:
            ctx.no_symlinks(archive / 'manifest.json')
            archived = json.loads((archive / 'manifest.json').read_bytes(), object_pairs_hook=unique)
            if archived.get('sources') != snapshot:
                raise MigrationError('Existing archive does not match selected migration')
        # Validate reused archives, too: a prior receipt is not a byte witness.
        for index, tree in snapshot.items():
            for name, entry in tree['entries'].items():
                archived_path = archive / ('worktree-' + index) / name
                ctx.no_symlinks(archived_path)
                if entry['kind'] == 'file' and digest_file(archived_path) != entry['sha256']:
                    raise MigrationError('Archived bytes no longer match source inventory')
        if not registered and source is not None:
            index = str(trees.index(source))
            for name, entry in snapshot[index]['entries'].items():
                if not name.startswith('.ledger/'):
                    continue
                control_name = name[len('.ledger/'):]
                first = control_name.split('/')[0]
                if control_name not in slots and first not in ARCHIVES:
                    continue
                if entry['kind'] == 'symlink':
                    raise MigrationError(f'Symlink in selected custody: {name}')
                if entry['kind'] == 'file' and not name.endswith('.cas.lock.advisory'):
                    target = custody / name
                    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                    shutil.copyfile(archive / ('worktree-' + index) / name, target)
                    target.chmod(0o600)
        imports = []
        for owner in selected:
            before_bytes = {slot: digest_file(custody / '.ledger' / slot) for slot in owner['slots'] if (custody / '.ledger' / slot).exists()}
            healthy(binary, owner, selector, repair=True)
            if any(digest_file(custody / '.ledger' / slot) != digest for slot, digest in before_bytes.items()):
                raise MigrationError('Binding maintenance changed canonical event bytes')
            if owner['importer']:
                importer = load_module(Path(owner['importer']))
                sources = [archive / ('worktree-' + index) / name for index, tree in snapshot.items()
                           for name in owner['retired_sources'] if tree['entries'].get(name, {}).get('kind') == 'file']
                if sources:
                    engine = importer.Native(binary, Path(owner['definition']), selector)
                    imports.append(importer.import_sources(engine, sources, apply=True, controls=framing_controls, initialize_empty=True))
            healthy(binary, owner, selector)
        if inspect()[1] != snapshot:
            raise MigrationError('Source/worktree view changed during migration; reconcile on retry')
        selected_id = context['store_id'] if registered else new_id
        published_root = custody if registered else custody.parent / selected_id
        for imported in imports:
            for item in imported['sources']:
                # Only a transport locator changes; never rewrite record provenance.
                item['source'] = str(published_root / Path(item['source']).relative_to(custody))
        receipt = {'schema': SCHEMA, 'status': 'verified', 'fingerprint': fingerprint, 'sources': snapshot,
                   'owners': selected, 'definitions': descriptions, 'imports': imports,
                   'store_id': selected_id, 'destination_prefixes': destination_prefixes(custody),
                   'unselected_disposition': 'preserved in source and archive; not semantically imported',
                   'storage_mutated': True, 'authority_granted': False}
        ctx.write_json(custody / 'migration-receipt.json', receipt)
        sync_tree(custody, ctx)
        if not registered:
            destination = custody.parent / selected_id
            os.rename(custody, destination)
            ctx.sync_directory(destination.parent)
            final_selector = ['--store-root', str(destination), '--store-id', selected_id]
            for owner in selected:
                healthy(binary, owner, final_selector)
        if inspect()[1] != snapshot:
            raise MigrationError(f'Source changed before publication; destination retained: {published_root}')
        receipt['context'] = ctx._register_root_locked(published_root, selected_id, workspace, home)
        return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path)
    parser.add_argument('--store-id')
    parser.add_argument('--migrate', action='store_true')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--confirm-no-writers', action='store_true')
    parser.add_argument('--ledger-bin', default='ledger')
    parser.add_argument('--framing-controls', type=Path)
    parser.add_argument('--repair-archive', action='store_true')
    parser.add_argument('--ensure-owner', action='store_true',
                        help='Automatically prepare opted-in owner custody before projection or capture')
    parser.add_argument('--read-only', action='store_true',
                        help='Select owner custody without initialization, migration, or repair')
    parser.add_argument('--definition', type=Path)
    args = parser.parse_args()
    try:
        controls = json.loads(args.framing_controls.read_bytes(), object_pairs_hook=unique) if args.framing_controls else None
        owner_modes = sum((args.repair_archive, args.ensure_owner, args.read_only))
        if owner_modes != int(args.definition is not None) or (owner_modes and args.migrate):
            raise MigrationError('Select one of --ensure-owner, --read-only, --repair-archive with --definition; not --migrate')
        if args.confirm_no_writers and not args.apply:
            raise MigrationError('--confirm-no-writers requires --apply')
        if (args.apply or args.confirm_no_writers or args.framing_controls) and not args.migrate:
            raise MigrationError('Migration effects require explicit --migrate')
        if args.migrate:
            if args.repo is None:
                raise MigrationError('--migrate requires the selected legacy --repo')
            result = migrate(args.repo, store_id=args.store_id, apply=args.apply, confirm_no_writers=args.confirm_no_writers,
                             binary=args.ledger_bin, framing_controls=controls)
        elif args.ensure_owner or args.read_only:
            result = owner_context(args.repo, args.definition, store_id=args.store_id, maintain=args.ensure_owner,
                                   read_only=args.read_only, binary=args.ledger_bin)
        else:
            result = ensure(args.repo, store_id=args.store_id)
            if args.repair_archive:
                result = restore_archived_slot(result, args.definition, binary=args.ledger_bin)
    except (MigrationError, OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(json.dumps({'schema': SCHEMA if args.migrate else 'ledger-workspace-context-error/v1', 'status': 'blocked', 'error': str(exc),
                          'storage_mutated': None if args.apply or args.repair_archive or args.ensure_owner else False, 'authority_granted': False}), file=sys.stderr)
        return 3
    print(canonical(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
