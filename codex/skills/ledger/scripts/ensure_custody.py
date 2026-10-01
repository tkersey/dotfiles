#!/usr/bin/env -S uv run python
"""Ensure usable owner-defined custody without making the resolver a writer.

Inspection is read-only. --apply authorizes lossless cold transport, owner-bound
binding maintenance and supported historical import as one operation. It still
requires a real --confirm-no-writers assertion; no process scan fabricates it.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid

SCHEMA = 'ledger-custody-ensure/v1'
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


def inventory(trees: list[Path], retired: list[str]) -> dict:
    """Account for every regular byte and link spelling; never follow links."""
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


def native(binary: str, owner: dict, selector: list[str], command: str, *args: str, allow_unhealthy: bool = False) -> dict:
    subcommand = []
    if command == 'definition':
        if not args:
            raise MigrationError('Missing definition subcommand')
        subcommand, args = [args[0]], args[1:]
    proc = subprocess.run([binary, command, *subcommand, '--definition', owner['definition'], *selector, *args, '--format', 'json'], capture_output=True)
    try:
        result = json.loads(proc.stdout, object_pairs_hook=unique)
    except (ValueError, UnicodeError) as exc:
        raise MigrationError(f'Invalid native {command} result for {owner["name"]}') from exc
    if not isinstance(result, dict) or result.get('authority_granted', result.get('semantic_authority_granted')) is not False:
        raise MigrationError('Native result omitted its authority boundary')
    if proc.returncode and not (allow_unhealthy and result.get('schema') == 'ledger-doctor-result/v1'):
        raise MigrationError(f'Native {command} failed: {canonical(result)}')
    return result


def healthy(binary: str, owner: dict, selector: list[str], *, repair: bool = False) -> dict:
    result = native(binary, owner, selector, 'doctor', allow_unhealthy=True)
    if (result.get('schema') != 'ledger-doctor-result/v1' or result.get('pending_transactions') != 0
            or result.get('storage_mutated') is not False):
        raise MigrationError(f'Unresolved transaction/coverage for {owner["name"]}')
    if result.get('healthy') is True:
        return result
    if not repair:
        raise MigrationError(f'Owner custody needs authorized maintenance: {canonical(result)}')
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
    return healthy(binary, owner, selector)


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
            # Symlink spellings are retained in the manifest, not made live.


def sync_tree(path: Path, ctx) -> None:
    directories = []
    for root, dirs, files in os.walk(path):
        directories.append(Path(root))
        for name in files:
            with (Path(root) / name).open('rb') as handle:
                os.fsync(handle.fileno())
    for directory in reversed(directories):
        ctx.sync_directory(directory)


def ensure(repo: Path, *, apply: bool = False, confirm_no_writers: bool = False,
           binary: str = 'ledger', skill_root: Path | None = None, framing_controls: dict | None = None) -> dict:
    ctx = load_module(Path(__file__).with_name('ledger_context.py'))
    workspace, common = ctx.workspace(repo)
    installed = skill_root or Path(__file__).resolve().parents[2]
    selected = owners(installed, ctx)
    slots = [slot for owner in selected for slot in owner['slots']]
    retired = sorted({name for owner in selected for name in owner['retired_sources']})

    def inspect():
        trees = sorted(ctx.worktrees(workspace), key=str)
        for tree in trees:
            ctx.no_symlinks(tree / '.ledger')
            for name in retired:
                ctx.no_symlinks(tree / name)
        snapshot = inventory(trees, retired)
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

    trees, snapshot, source = inspect()
    registered = os.path.lexists(common / ctx.REGISTRATION)
    context = ctx.checked_registration(workspace, common) if registered else None
    fingerprint = hashlib.sha256(canonical({'sources': snapshot, 'owners': selected,
        'definitions': {o['definition']: digest_file(Path(o['definition'])) for o in selected},
        'importers': {o['importer']: digest_file(Path(o['importer'])) for o in selected if o['importer']},
        'framing': framing_controls or {}}).encode()).hexdigest()
    descriptions = []
    for owner in selected:
        descriptions.append(native(binary, owner, [], 'definition', 'describe'))
    fingerprint = hashlib.sha256((fingerprint + canonical([d.get('definition') for d in descriptions])).encode()).hexdigest()
    def destination_revisions(custody):
        revisions = {}
        for slot in slots:
            path = custody / '.ledger' / slot
            ctx.no_symlinks(path)
            revisions[slot] = digest_file(path) if path.exists() else None
        return revisions

    if registered:
        receipt_path = Path(context['store_root']) / 'migration-receipt.json'
        ctx.no_symlinks(receipt_path)
        if receipt_path.exists():
            saved = json.loads(receipt_path.read_bytes(), object_pairs_hook=unique)
            if (saved.get('schema') == SCHEMA and saved.get('fingerprint') == fingerprint
                    and saved.get('status') == 'verified'
                    and saved.get('destination_revisions') == destination_revisions(Path(context['store_root']))):
                for owner in selected:
                    healthy(binary, owner, context['native_args'])
                return {**saved, 'context': context, 'storage_mutated': False}
    if not apply:
        return {'schema': SCHEMA, 'status': 'planned', 'registered': registered, 'context': context,
                'fingerprint': fingerprint, 'sources': snapshot, 'selected_source': str(source) if source else None,
                'owners': selected, 'requires': ['--apply', '--confirm-no-writers'],
                'storage_mutated': False, 'authority_granted': False}
    if not confirm_no_writers:
        raise MigrationError('--apply requires --confirm-no-writers after actually quiescing legacy and managed writers')
    with ctx.registration_lock(common):
        # Reject a changed view rather than silently applying a new migration.
        if inspect()[1] != snapshot or os.path.lexists(common / ctx.REGISTRATION) != registered:
            raise MigrationError('Migration inputs changed; inspect and retry')
        if registered:
            current = ctx.checked_registration(workspace, common)
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
            store_id = uuid.uuid4().hex
            custody = Path(tempfile.mkdtemp(prefix='.migrating-', dir=repos))
            (custody / '.ledger').mkdir(mode=0o700)
            ctx.write_json(custody / ctx.MARKER, {'schema': ctx.MARKER_SCHEMA, 'store_id': store_id})
            selector = ['--store-root', str(custody), '--store-id', store_id]
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
        published_root = custody if registered else custody.parent / store_id
        for imported in imports:
            for item in imported['sources']:
                # Only a transport locator changes; never rewrite record provenance.
                item['source'] = str(published_root / Path(item['source']).relative_to(custody))
        receipt = {'schema': SCHEMA, 'status': 'verified', 'fingerprint': fingerprint, 'sources': snapshot,
                   'owners': selected, 'definitions': descriptions, 'imports': imports,
                   'destination_revisions': destination_revisions(custody),
                   'unselected_disposition': 'preserved in source and archive; not semantically imported',
                   'storage_mutated': True, 'authority_granted': False}
        ctx.write_json(custody / 'migration-receipt.json', receipt)
        sync_tree(custody, ctx)
        if not registered:
            destination = custody.parent / store_id
            os.rename(custody, destination)
            ctx.sync_directory(destination.parent)
            final_selector = ['--store-root', str(destination), '--store-id', store_id]
            for owner in selected:
                healthy(binary, owner, final_selector)
            if inspect()[1] != snapshot:
                raise MigrationError(f'Source changed before publication; unregistered destination retained: {destination}')
            ctx.write_json(common / ctx.REGISTRATION, {'schema': ctx.REGISTRATION_SCHEMA,
                                                      'store_id': store_id, 'store_root': str(destination)})
        receipt['context'] = ctx.checked_registration(workspace, common, mutated=True)
        return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--confirm-no-writers', action='store_true')
    parser.add_argument('--ledger-bin', default='ledger')
    parser.add_argument('--framing-controls', type=Path)
    args = parser.parse_args()
    try:
        controls = json.loads(args.framing_controls.read_bytes(), object_pairs_hook=unique) if args.framing_controls else None
        if args.confirm_no_writers and not args.apply:
            raise MigrationError('--confirm-no-writers requires --apply')
        result = ensure(args.repo, apply=args.apply, confirm_no_writers=args.confirm_no_writers,
                        binary=args.ledger_bin, framing_controls=controls)
    except (MigrationError, OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({'schema': SCHEMA, 'status': 'blocked', 'error': str(exc),
                          'storage_mutated': None if args.apply else False, 'authority_granted': False}), file=sys.stderr)
        return 3
    print(canonical(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
