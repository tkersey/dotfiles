from contextlib import contextmanager
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess

SKILLS = Path(__file__).resolve().parents[2]
ARCHIVES = {'.bindings', '.definitions', '.revisions'}
MAX_BYTES = 2 * 1024**3
MARKER = '.ledger-root.json'
MARKER_SCHEMA = 'ledger-storage-root/v1'
CATALOG = 'catalog.json'
REGISTRATION = 'ledger-store.json'
REGISTRATION_SCHEMA = 'ledger-repository-registration/v1'


class MigrationError(RuntimeError):
    def __init__(self, value):
        super().__init__(json.dumps(value) if isinstance(value, dict) else str(value))
        self.value = value
        self.preparation = value.get('preparation') if isinstance(value, dict) else None
        self.context = value if isinstance(value, dict) else None


ContextError = MigrationError
UnregisteredContext = MigrationError


def storage_home():
    return Path(os.environ['LEDGER_HOME']) if os.environ.get('LEDGER_HOME') else Path(os.environ['CODEX_HOME']) / 'ledger'


def command(repo=None, *, store_id=None, binary=None):
    argv = [str(binary or os.environ['LEDGER_BIN']), 'context', '--catalog-root', str(storage_home())]
    if repo is not None:
        argv += ['--workspace', str(repo)]
    if store_id is not None:
        argv += ['--store-id', store_id]
    return argv


def invoke(argv):
    process = subprocess.run(argv, capture_output=True, timeout=40)
    try:
        value = json.loads(process.stdout)
    except ValueError:
        raise MigrationError({'exit_code': process.returncode, 'stdout': process.stdout.decode(), 'stderr': process.stderr.decode()})
    if process.returncode:
        raise MigrationError(value)
    return value


def resolve(repo=None, *, store_id=None, initialize=False, attach_workspace=False, confirm_no_writers=False, legacy_paths=(), adopt_from=None, definitions=()):
    argv = command(repo, store_id=store_id)
    if initialize:
        argv.append('--initialize')
    for path in legacy_paths:
        argv += ['--legacy-path', path]
    if adopt_from is not None:
        argv += ['--adopt-from', str(adopt_from)]
        for definition in definitions:
            argv += ['--definition', str(definition)]
        if confirm_no_writers:
            argv.append('--confirm-no-writers')
    if attach_workspace:
        argv.append('--attach-workspace')
    return invoke(argv)


def register_root(root, store_id, repo=None):
    return invoke(command(repo, store_id=store_id) + ['--register-root', str(root)])


def ensure(repo=None, *, store_id=None):
    return invoke(command(repo, store_id=store_id) + ['--ensure'])


def owner_command(repo, definition, *, store_id=None, binary=None, mode='--ensure-owner', confirm_no_writers=False):
    manifest = Path(definition).parents[2] / 'migration.json'
    argv = command(repo, store_id=store_id, binary=binary) + [mode, '--definition', str(definition), '--owner-manifest', str(manifest)]
    if confirm_no_writers:
        argv.append('--confirm-no-legacy-writers')
    return argv


def owner_context(repo, definition, *, store_id=None, maintain=False, read_only=False, confirm_no_writers=False, binary=None, skill_root=None):
    return invoke(owner_command(repo, definition, store_id=store_id, binary=binary,
                               mode='--ensure-owner' if maintain else '--read-only', confirm_no_writers=confirm_no_writers))


def restore_archived_slot(context, definition, *, binary=None, skill_root=None, confirm_no_writers=False):
    return invoke(owner_command(context.get('workspace_root'), definition, store_id=context['store_id'], binary=binary,
                               mode='--repair-archive', confirm_no_writers=confirm_no_writers))


def migrate(repo, *, store_id=None, apply=False, confirm_no_writers=False, binary=None, skill_root=None, framing_controls=None, import_receipts=()):
    argv = command(repo, store_id=store_id, binary=binary) + ['--migrate']
    for manifest in sorted((skill_root or SKILLS).glob('*/migration.json')):
        argv += ['--owner-manifest', str(manifest)]
    if apply:
        argv.append('--apply')
    if confirm_no_writers:
        argv.append('--confirm-no-writers')
    if framing_controls is not None:
        controls = Path(repo).parent / 'framing-controls.json'
        controls.write_text(json.dumps(framing_controls))
        argv += ['--framing-controls', str(controls)]
    for receipt in import_receipts:
        argv += ['--owner-import-receipt', str(receipt)]
    return invoke(argv)


def load_module(path):
    spec = importlib.util.spec_from_file_location(Path(path).stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value))


def read_document(path):
    return json.loads(Path(path).read_text())


def inventory(trees, retired, *, slots=()):
    result = {}
    for index, tree in enumerate(trees):
        tree = Path(tree)
        entries = {}
        for name in ['.ledger', *retired]:
            selected = tree / name
            paths = [selected, *sorted(selected.rglob('*'))] if selected.is_dir() else [selected]
            for path in paths:
                relative = str(path.relative_to(tree))
                if path.is_symlink():
                    entries[relative] = {'kind': 'symlink', 'target': os.readlink(path)}
                elif path.is_dir():
                    entries[relative] = {'kind': 'directory'}
                elif path.is_file():
                    raw = path.read_bytes()
                    entries[relative] = {'kind': 'file', 'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
        result[str(index)] = {'workspace': str(tree), 'entries': entries}
    return result


def copy_inventory(snapshot, destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for index, source in snapshot.items():
        for name, entry in source['entries'].items():
            target = destination / ('worktree-' + index) / name
            if entry['kind'] == 'directory':
                target.mkdir(parents=True, exist_ok=True)
            elif entry['kind'] == 'file':
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(Path(source['workspace']) / name, target)


@contextmanager
def native_lock(path, context=None):
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    finally:
        os.close(descriptor)


def list_stores():
    return invoke(command() + ["--list-stores"])


def import_registration(path, repo=None):
    return invoke(command(repo) + ["--import-registration", str(path)])
