#!/usr/bin/env -S uv run python
"""Resolve personal Ledger custody; never select a semantic operation.

The personal catalog owns store identity and optional workspace associations.
Normal resolution is read-only and independent of migration completeness.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
from typing import Iterator
import uuid

REGISTRATION = "ledger-store.json"
REGISTRATION_SCHEMA = "ledger-repository-registration/v1"
MARKER = ".ledger-root.json"
MARKER_SCHEMA = "ledger-storage-root/v1"
CONTEXT_SCHEMA = "ledger-workspace-context/v1"
CATALOG = "catalog.json"
CATALOG_SCHEMA = "ledger-personal-catalog/v1"
CONTROL_ARCHIVES = {".bindings", ".definitions", ".revisions"}
TRANSIENT_CONTROLS = {".transactions", ".fencing.counter"}


class ContextError(RuntimeError):
    pass


class UnregisteredContext(ContextError):
    pass


def git(repo: Path, *args: str) -> bytes:
    env = dict(os.environ)
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE"):
        env.pop(key, None)
    proc = subprocess.run(["git", "-C", str(repo), *args], env=env, capture_output=True)
    if proc.returncode:
        raise ContextError(proc.stderr.decode(errors="replace").strip() or "Git context unavailable")
    return proc.stdout


def workspace(repo: Path) -> tuple[Path, Path]:
    if git(repo, "rev-parse", "--is-inside-work-tree").strip() != b"true":
        raise ContextError("A verified Git worktree is required")
    root = Path(os.fsdecode(git(repo, "rev-parse", "--show-toplevel").rstrip(b"\n"))).resolve(strict=True)
    common = Path(os.fsdecode(git(root, "rev-parse", "--path-format=absolute", "--git-common-dir").rstrip(b"\n"))).resolve(strict=True)
    return root, common


def no_symlinks(path: Path) -> None:
    for part in (path, *path.parents):
        try:
            if stat.S_ISLNK(part.lstat().st_mode):
                raise ContextError(f"Symlink custody component: {part}")
        except FileNotFoundError:
            continue


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate metadata key: {key}")
        result[key] = value
    return result


def read_document(path: Path, *, max_bytes: int = 4096) -> object:
    no_symlinks(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            raise ContextError(f"Expected regular metadata file: {path}")
        raw = handle.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise ContextError(f"Oversized metadata: {path}")
    try:
        return json.loads(raw, object_pairs_hook=unique_object)
    except (ValueError, UnicodeError) as exc:
        raise ContextError(f"Invalid metadata: {path}") from exc


def read_json(path: Path, keys: set[str]) -> dict:
    value = read_document(path)
    if not isinstance(value, dict) or set(value) != keys or not all(isinstance(v, str) for v in value.values()):
        raise ContextError(f"Unexpected metadata shape: {path}")
    return value


def sync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_json(path: Path, value: dict) -> None:
    no_symlinks(path)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        sync_directory(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


def storage_home() -> Path:
    # An explicitly selected home is a catalog namespace. Read-only resolution
    # never creates a replacement when that namespace lacks a known store.
    override = os.environ.get("LEDGER_HOME")
    codex = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()
    selected = Path(override).expanduser() if override else codex / "ledger"
    if not selected.is_absolute():
        raise ContextError("Configured Ledger home must be absolute")
    # Check the configured spelling before resolve() hides existing links.
    no_symlinks(selected)
    return selected.resolve()


def valid_store_id(store_id: str) -> None:
    if not isinstance(store_id, str) or len(store_id) != 32 or any(c not in "0123456789abcdef" for c in store_id):
        raise ContextError("Invalid registered store identity")


def read_catalog(home: Path) -> dict:
    path = home / CATALOG
    no_symlinks(path)
    if not os.path.lexists(path):
        return {"schema": CATALOG_SCHEMA, "stores": {}, "aliases": {}}
    value = read_document(path, max_bytes=1048576)
    if (not isinstance(value, dict) or set(value) != {"schema", "stores", "aliases"}
            or value["schema"] != CATALOG_SCHEMA
            or not isinstance(value["stores"], dict) or not isinstance(value["aliases"], dict)):
        raise ContextError("Invalid personal Ledger catalog")
    for store_id, root in value["stores"].items():
        valid_store_id(store_id)
        if not isinstance(root, str) or not Path(root).is_absolute():
            raise ContextError("Catalog custody roots must be absolute")
    for alias, store_id in value["aliases"].items():
        kind, separator, path = alias.partition(":")
        if (kind not in {"workspace", "git-common-dir"} or not separator
                or not Path(path).is_absolute() or not isinstance(store_id, str)
                or store_id not in value["stores"]):
            raise ContextError("Invalid personal Ledger workspace association")
    return value


@contextmanager
def catalog_lock(home: Path) -> Iterator[None]:
    no_symlinks(home)
    home.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = home / "catalog.lock"
    no_symlinks(lock)
    fd = os.open(lock, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ContextError("Expected regular catalog lock")
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def workspace_associations(repo: Path | None) -> tuple[Path | None, Path | None, list[str]]:
    if repo is None:
        return None, None, []
    selected = repo.expanduser().absolute()
    root = selected.resolve()
    common = None
    # Git can supply an association for a live worktree, but it never supplies
    # custody or enumerates sibling worktrees during normal use.
    if root.is_dir():
        try:
            root, common = workspace(root)
        except (ContextError, FileNotFoundError):
            pass
    aliases = ["workspace:" + str(root)]
    if common is not None:
        aliases.append("git-common-dir:" + str(common))
    return root, common, aliases


def catalog_selection(catalog: dict, aliases: list[str], store_id: str | None,
                      *, attach_workspace: bool = False) -> str | None:
    if store_id is not None:
        valid_store_id(store_id)
        if store_id not in catalog["stores"]:
            raise ContextError("Selected store is not cataloged; import its existing registration or register its root explicitly")
    associated = {catalog["aliases"][key] for key in aliases if key in catalog["aliases"]}
    if len(associated) > 1 or (store_id is not None and associated and associated != {store_id}):
        raise ContextError("Conflicting workspace associations; reconcile explicitly without merging histories")
    workspace_ids = {catalog['aliases'][key] for key in aliases
                     if key.startswith('workspace:') and key in catalog['aliases']}
    if not attach_workspace and workspace_ids and any(
            key.startswith('git-common-dir:') and catalog['aliases'].get(key) not in workspace_ids
            for key in aliases):
        raise ContextError("Workspace alias has an unregistered Git common directory; select the intended --store-id and --attach-workspace explicitly")
    return store_id or next(iter(associated), None)


def associate(catalog: dict, aliases: list[str], store_id: str) -> None:
    for alias in aliases:
        existing = catalog["aliases"].get(alias)
        if existing is not None and existing != store_id:
            raise ContextError("Workspace is already associated with another store; refusing replacement")
    catalog["aliases"].update({alias: store_id for alias in aliases})


def publish_catalog(home: Path, catalog: dict) -> None:
    if len((json.dumps(catalog, sort_keys=True) + '\n').encode('utf-8')) > 1048576:
        raise ContextError("Personal Ledger catalog size bound exceeded")
    write_json(home / CATALOG, catalog)


def list_stores() -> dict:
    catalog = read_catalog(storage_home())
    return {
        'schema': 'ledger-personal-store-list/v1',
        'stores': [
            {'store_id': store_id, 'repository_id': 'ledger-repository:' + store_id,
             'store_root': root,
             'aliases': sorted(alias for alias, selected in catalog['aliases'].items() if selected == store_id)}
            for store_id, root in sorted(catalog['stores'].items())
        ],
        'storage_mutated': False,
        'authority_granted': False,
    }


@contextmanager
def registration_lock(common: Path) -> Iterator[None]:
    lock = common / "ledger-store.lock"
    no_symlinks(lock)
    fd = os.open(lock, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def worktrees(root: Path) -> list[Path]:
    result = []
    for field in git(root, "worktree", "list", "--porcelain", "-z").split(b"\0"):
        if field.startswith(b"worktree "):
            path = Path(os.fsdecode(field[len(b"worktree "):]))
            if not path.is_dir():
                raise ContextError(f"Cannot establish legacy coverage for unavailable worktree: {path}")
            result.append(path.resolve(strict=True))
    return result


def legacy_roots(root: Path) -> list[Path]:
    found = []
    for tree in worktrees(root):
        legacy = tree / ".ledger"
        retired = tree / ".learnings.jsonl"
        if os.path.lexists(retired):
            raise ContextError(f"Retired source requires owner recovery: {retired}")
        if os.path.lexists(legacy):
            no_symlinks(legacy)
            if not legacy.is_dir():
                raise ContextError(f"Invalid legacy control root: {legacy}")
            if any(legacy.iterdir()):
                found.append(tree)
    return found


def checked_registration(root: Path, common: Path, *, mutated: bool = False) -> dict:
    """Inspect an explicitly selected legacy registration for maintenance only."""
    registration = read_json(common / REGISTRATION, {"schema", "store_id", "store_root"})
    if registration["schema"] != REGISTRATION_SCHEMA:
        raise ContextError("Unknown repository registration schema")
    return checked_root(Path(registration["store_root"]), registration["store_id"], root, common, mutated=mutated)


def checked_root(custody: Path, store_id: str, root: Path | None = None,
                 common: Path | None = None, *, mutated: bool = False) -> dict:
    valid_store_id(store_id)
    if not custody.is_absolute():
        raise ContextError("Registered custody root must be absolute")
    no_symlinks(custody)
    marker = read_json(custody / MARKER, {"schema", "store_id"})
    if marker != {"schema": MARKER_SCHEMA, "store_id": store_id}:
        raise ContextError("Registered custody identity mismatch")
    control = custody / ".ledger"
    no_symlinks(control)
    if not control.is_dir():
        raise ContextError("Established custody is missing; refusing empty reinitialization")
    return {
        "schema": CONTEXT_SCHEMA,
        "workspace_root": str(root) if root is not None else None,
        "git_common_dir": str(common) if common is not None else None,
        "repository_id": f"ledger-repository:{store_id}",
        "store_id": store_id,
        "store_root": str(custody),
        "native_args": ["--store-root", str(custody), "--store-id", store_id],
        "storage_mutated": mutated,
        "authority_granted": False,
    }


def register_root(custody: Path, store_id: str, repo: Path | None = None) -> dict:
    """Catalog an existing identity without moving, rebinding, or merging data."""
    root, common, aliases = workspace_associations(repo)
    checked_root(custody, store_id, root, common)
    custody = custody.resolve(strict=True)
    if common is not None and os.path.lexists(common / REGISTRATION):
        legacy = checked_registration(root, common)
        if legacy['store_id'] != store_id or Path(legacy['store_root']).resolve(strict=True) != custody:
            raise ContextError("Selected workspace has a different legacy registration; reconcile explicitly")
    home = storage_home()
    with catalog_lock(home):
        catalog = read_catalog(home)
        existing = catalog["stores"].get(store_id)
        if existing is not None and existing != str(custody):
            raise ContextError("Store identity is already cataloged at another root; refusing replacement")
        before = json.dumps(catalog, sort_keys=True)
        catalog["stores"][store_id] = str(custody)
        associate(catalog, aliases, store_id)
        checked_root(custody, store_id, root, common)
        changed = json.dumps(catalog, sort_keys=True) != before
        if changed:
            publish_catalog(home, catalog)
        return checked_root(custody, store_id, root, common, mutated=changed)


def import_registration(path: Path, repo: Path | None = None) -> dict:
    registration = read_json(path, {"schema", "store_id", "store_root"})
    if registration["schema"] != REGISTRATION_SCHEMA:
        raise ContextError("Unknown repository registration schema")
    return register_root(Path(registration["store_root"]), registration["store_id"], repo)


def native_doctor(binary: str, repo: Path, definitions: list[Path], native_args: list[str] | None = None) -> None:
    for definition in definitions:
        proc = subprocess.run(
            [binary, "doctor", "--definition", str(definition), *(native_args or ["--repo", str(repo)]), "--format", "json"],
            capture_output=True,
        )
        try:
            result = json.loads(proc.stdout)
        except (ValueError, UnicodeError) as exc:
            raise ContextError(f"Invalid doctor result for {definition}") from exc
        if (proc.returncode or not isinstance(result, dict) or result.get("schema") != "ledger-doctor-result/v1"
                or result.get("healthy") is not True or result.get("pending_transactions") != 0
                or result.get("storage_mutated") is not False or result.get("authority_granted") is not False):
            raise ContextError(f"Cold adoption requires healthy bound custody with no pending transactions: {repo}; {proc.stdout.decode(errors='replace')}")


def declared_slots(definitions: list[Path]) -> set[str]:
    slots: set[str] = set()
    for definition in definitions:
        try:
            value = json.loads(definition.read_text(encoding="utf-8"))
        except UnicodeError as exc:
            raise ContextError(f"Invalid definition encoding: {definition}") from exc
        if not isinstance(value, dict):
            raise ContextError(f"Invalid definition storage shape: {definition}")
        storage = value.get("storage", {})
        if not isinstance(storage, dict) or not isinstance(storage.get("slots", {}), dict):
            raise ContextError(f"Invalid definition storage shape: {definition}")
        for slot in storage.get("slots", {}).values():
            if not isinstance(slot, dict):
                raise ContextError(f"Invalid definition storage slot: {definition}")
            path = slot.get("path")
            if (not isinstance(path, str) or Path(path).is_absolute() or ".." in Path(path).parts
                    or "{" in path or slot.get("layout", "monolithic") != "monolithic"
                    or slot.get("kind") != "event-log" or slot.get("codec") != "jsonl"):
                raise ContextError("Cold adoption requires explicit static monolithic JSONL event slots")
            slots.add(path)
    if not slots:
        raise ContextError("Supply every owning definition needed to cover the legacy stores")
    return slots


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inventory(source: Path, slots: set[str]) -> dict[str, str]:
    result = {}
    control = source / ".ledger"
    for path in control.rglob("*"):
        no_symlinks(path)
        if path.is_dir():
            continue
        if not path.is_file():
            raise ContextError(f"Unsupported legacy filesystem entry: {path}")
        relative = path.relative_to(control).as_posix()
        first = relative.split("/", 1)[0]
        if first in TRANSIENT_CONTROLS:
            continue
        # Reserved native advisory files carry process-local locks, not history.
        # Never transport a legacy lease; resolve it through native recovery first.
        advisory = ".cas.lock.advisory"
        if relative.endswith(advisory) and (relative[:-len(advisory)] in slots or first in CONTROL_ARCHIVES):
            continue
        if relative.endswith(".cas.lock"):
            raise ContextError(f"Legacy lease requires native recovery before adoption: {relative}")
        if first not in CONTROL_ARCHIVES and relative not in slots:
            raise ContextError(f"Uncovered legacy file; supply its owner or reconcile explicitly: {relative}")
        result[relative] = file_digest(path)
    return result


def complete_prefix(prefix: Path, full: Path) -> bool:
    with prefix.open("rb") as left, full.open("rb") as right:
        last = b""
        for block in iter(lambda: left.read(1024 * 1024), b""):
            if right.read(len(block)) != block:
                return False
            last = block[-1:]
        return last in (b"", b"\n")


def cold_adopt(source: Path, destination: Path, candidates: list[Path], definitions: list[Path], binary: str) -> None:
    slots = declared_slots(definitions)
    native_doctor(binary, source, definitions)
    before = inventory(source, slots)
    for candidate in candidates:
        other = inventory(candidate, slots)
        # Ignore custody differences; never choose among different event bytes.
        for slot in slots:
            if slot in other and before.get(slot) != other[slot]:
                full = source / ".ledger" / slot
                prefix = candidate / ".ledger" / slot
                if slot not in before or not complete_prefix(prefix, full):
                    raise ContextError(f"Divergent or additional legacy history in {candidate}: {slot}")
    for relative in before:
        target = destination / ".ledger" / relative
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        shutil.copyfile(source / ".ledger" / relative, target)
        target.chmod(0o600)
        with target.open("rb") as handle:
            os.fsync(handle.fileno())
    if inventory(source, slots) != before or inventory(destination, slots) != before:
        raise ContextError("Legacy custody changed during cold adoption")
    native_doctor(binary, destination, definitions)
    for directory in sorted((p for p in destination.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        sync_directory(directory)
    sync_directory(destination)


def resolve(
    repo: Path | None = None,
    *,
    store_id: str | None = None,
    initialize: bool = False,
    attach_workspace: bool = False,
    adopt_from: Path | None = None,
    definitions: list[Path] | None = None,
    confirm_no_writers: bool = False,
    ledger_bin: str = "ledger",
) -> dict:
    root, common, aliases = workspace_associations(repo)
    if attach_workspace and (repo is None or store_id is None or initialize or adopt_from is not None):
        raise ContextError("--attach-workspace requires --repo and --store-id without initialization")
    if adopt_from is not None and (not initialize or repo is None or not definitions or not confirm_no_writers):
        raise ContextError("Cold adoption requires --initialize, --repo, all owner definitions, and --confirm-no-writers")
    if definitions and adopt_from is None:
        raise ContextError("Definitions require --adopt-from")
    home = storage_home()
    catalog = read_catalog(home)
    selected_id = catalog_selection(catalog, aliases, store_id, attach_workspace=attach_workspace)
    if selected_id is not None:
        if adopt_from is not None:
            raise ContextError("A store is already cataloged; adoption is not reconciliation")
        custody = Path(catalog["stores"][selected_id])
        if attach_workspace:
            return register_root(custody, selected_id, repo)
        return checked_root(custody, selected_id, root, common)
    if not initialize:
        raise UnregisteredContext("No cataloged workspace association; select --store-id, import an existing registration, or explicitly initialize new custody")

    def reject_known_history(*, check_catalog: bool = False) -> None:
        if check_catalog and not os.path.lexists(home / CATALOG):
            prior_roots = home / 'repos'
            no_symlinks(prior_roots)
            if os.path.lexists(prior_roots) and (not prior_roots.is_dir() or any(prior_roots.iterdir())):
                raise ContextError("Existing custody roots lack a catalog; explicitly register their identities before new initialization")
        if root is not None and not root.is_dir():
            raise ContextError("A new workspace association requires an existing directory")
        legacy_registration = (common if common is not None else root / '.git') / REGISTRATION if root is not None else None
        if legacy_registration is not None and os.path.lexists(legacy_registration):
            raise ContextError("Existing Git registration must be imported explicitly; refusing a parallel empty store")
        if root is not None and adopt_from is None:
            control = root / '.ledger'
            no_symlinks(control)
            if os.path.lexists(root / '.learnings.jsonl') or (os.path.lexists(control) and (not control.is_dir() or any(control.iterdir()))):
                raise ContextError("Selected workspace contains legacy history; use explicit migration without declaring it recovered")
            if common is not None:
                # A new family association must not hide history in another
                # checkout. This coverage check belongs only to creation;
                # existing custody and explicit adoption never reach it.
                candidates = legacy_roots(root)
                if candidates:
                    raise ContextError("Linked worktrees contain legacy history; use explicit migration: "
                                       + ", ".join(map(str, candidates)))

    reject_known_history()
    candidates = []
    source = None
    if adopt_from is not None:
        root, common = workspace(repo)
        candidates = legacy_roots(root)
        source, source_common = workspace(adopt_from)
        if source_common != common or source not in candidates:
            raise ContextError("Adoption source must be an inspected worktree in this repository family")
    with catalog_lock(home):
        catalog = read_catalog(home)
        selected_id = catalog_selection(catalog, aliases, store_id)
        if selected_id is not None:
            if adopt_from is not None:
                raise ContextError("Concurrent registration completed; do not replace its lineage")
            return checked_root(Path(catalog['stores'][selected_id]), selected_id, root, common)
        reject_known_history(check_catalog=True)
        no_symlinks(home)
        repos = home / "repos"
        repos.mkdir(parents=True, exist_ok=True, mode=0o700)
        no_symlinks(repos)
        new_id = uuid.uuid4().hex
        custody = repos / new_id
        stage = Path(tempfile.mkdtemp(prefix=".initializing-", dir=repos))
        try:
            (stage / ".ledger").mkdir(mode=0o700)
            if source is not None:
                cold_adopt(source, stage, candidates, [p.resolve(strict=True) for p in definitions or []], ledger_bin)
            write_json(stage / MARKER, {"schema": MARKER_SCHEMA, "store_id": new_id})
            sync_directory(stage / ".ledger")
            if adopt_from is None:
                reject_known_history()
            os.rename(stage, custody)
            sync_directory(repos)
            if adopt_from is not None:
                native_doctor(ledger_bin, custody, [p.resolve(strict=True) for p in definitions or []],
                              ["--store-root", str(custody), "--store-id", new_id])
            else:
                # Catalog publication associates the family with this identity.
                # Recheck after syncing its final root, before that association.
                reject_known_history()
            # Publish only after validation at the final, identity-checked address.
            catalog['stores'][new_id] = str(custody)
            associate(catalog, aliases, new_id)
            publish_catalog(home, catalog)
        finally:
            if stage.exists():
                shutil.rmtree(stage)
        return checked_root(custody, new_id, root, common, mutated=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--store-id")
    parser.add_argument("--list-stores", action="store_true")
    parser.add_argument("--initialize", action="store_true")
    parser.add_argument("--attach-workspace", action="store_true")
    adoption = parser.add_mutually_exclusive_group()
    adoption.add_argument("--register-root", type=Path)
    adoption.add_argument("--import-registration", type=Path)
    parser.add_argument("--adopt-from", type=Path)
    parser.add_argument("--definition", type=Path, action="append", default=[])
    parser.add_argument("--confirm-no-writers", action="store_true")
    parser.add_argument("--ledger-bin", default="ledger")
    args = parser.parse_args()
    try:
        if args.list_stores and (args.repo is not None or args.store_id is not None or args.initialize
                                or args.attach_workspace or args.register_root or args.import_registration
                                or args.adopt_from or args.definition or args.confirm_no_writers):
            raise ContextError("--list-stores cannot be combined with a selector or mutation")
        if (args.register_root or args.import_registration) and (args.initialize or args.attach_workspace or args.adopt_from or args.definition or args.confirm_no_writers):
            raise ContextError("Catalog adoption cannot be combined with initialization or migration")
        if (args.adopt_from or args.definition or args.confirm_no_writers) and not args.initialize:
            raise ContextError("Initialization flags require --initialize")
        if args.list_stores:
            result = list_stores()
        elif args.register_root:
            if args.store_id is None:
                raise ContextError("--register-root requires the existing --store-id")
            result = register_root(args.register_root, args.store_id, args.repo)
        elif args.import_registration:
            if args.store_id is not None:
                raise ContextError("--import-registration obtains identity from the selected registration")
            result = import_registration(args.import_registration, args.repo)
        else:
            result = resolve(args.repo, store_id=args.store_id, initialize=args.initialize,
                             attach_workspace=args.attach_workspace, adopt_from=args.adopt_from,
                             definitions=args.definition, confirm_no_writers=args.confirm_no_writers,
                             ledger_bin=args.ledger_bin)
    except (ContextError, OSError, ValueError) as exc:
        print(json.dumps({"schema": "ledger-workspace-context-error/v1", "status": "blocked", "error": str(exc), "authority_granted": False}), file=sys.stderr)
        return 3
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
