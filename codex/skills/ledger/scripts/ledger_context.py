#!/usr/bin/env -S uv run python
"""Resolve caller-owned Ledger custody; never select a semantic operation.

This module is the single storage-location policy for the Ledger skill. Normal
resolution is read-only. Initialization and cold adoption require explicit flags.
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
CONTROL_ARCHIVES = {".bindings", ".definitions", ".revisions"}
TRANSIENT_CONTROLS = {".transactions", ".fencing.counter"}


class ContextError(RuntimeError):
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


def read_json(path: Path, keys: set[str]) -> dict:
    no_symlinks(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            raise ContextError(f"Expected regular metadata file: {path}")
        raw = handle.read(4097)
    if len(raw) > 4096:
        raise ContextError(f"Oversized metadata: {path}")
    try:
        value = json.loads(raw, object_pairs_hook=unique_object)
    except (ValueError, UnicodeError) as exc:
        raise ContextError(f"Invalid metadata: {path}") from exc
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
    # Only this module defines the default location. Existing registration always
    # wins over environment changes; changing CODEX_HOME cannot fork a history.
    override = os.environ.get("LEDGER_HOME")
    codex = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()
    selected = Path(override).expanduser() if override else codex / "ledger"
    if not selected.is_absolute():
        raise ContextError("Configured Ledger home must be absolute")
    # Check the configured spelling before resolve() hides existing links.
    no_symlinks(selected)
    return selected.resolve()


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
    registration = read_json(common / REGISTRATION, {"schema", "store_id", "store_root"})
    if registration["schema"] != REGISTRATION_SCHEMA:
        raise ContextError("Unknown repository registration schema")
    store_id = registration["store_id"]
    if len(store_id) != 32 or any(c not in "0123456789abcdef" for c in store_id):
        raise ContextError("Invalid registered store identity")
    custody = Path(registration["store_root"])
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
        "workspace_root": str(root),
        "git_common_dir": str(common),
        "repository_id": f"ledger-repository:{store_id}",
        "store_id": store_id,
        "store_root": str(custody),
        "native_args": ["--store-root", str(custody), "--store-id", store_id],
        "storage_mutated": mutated,
        "authority_granted": False,
    }


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
    repo: Path,
    *,
    initialize: bool = False,
    adopt_from: Path | None = None,
    definitions: list[Path] | None = None,
    confirm_no_writers: bool = False,
    ledger_bin: str = "ledger",
) -> dict:
    root, common = workspace(repo)
    registration = common / REGISTRATION
    if os.path.lexists(registration):
        if adopt_from is not None:
            raise ContextError("A store is already registered; adoption is not reconciliation")
        return checked_registration(root, common)
    if not initialize:
        raise ContextError("Repository custody is unregistered; authorize initialization or cold adoption through $ledger")
    if not confirm_no_writers:
        raise ContextError("Initialization requires --confirm-no-writers after quiescing legacy writers")
    if adopt_from is not None and not definitions:
        raise ContextError("Cold adoption requires all owner definitions")
    with registration_lock(common):
        if os.path.lexists(registration):
            if adopt_from is not None:
                raise ContextError("Concurrent registration completed; do not replace its lineage")
            return checked_registration(root, common)
        candidates = legacy_roots(root)
        if candidates and adopt_from is None:
            raise ContextError("Legacy histories exist; explicit cold adoption or reconciliation is required: " + ", ".join(map(str, candidates)))
        if adopt_from is not None:
            source, source_common = workspace(adopt_from)
            if source_common != common or source not in candidates:
                raise ContextError("Adoption source must be an inspected worktree in this repository family")
        home = storage_home()
        no_symlinks(home)
        repos = home / "repos"
        repos.mkdir(parents=True, exist_ok=True, mode=0o700)
        no_symlinks(repos)
        store_id = uuid.uuid4().hex
        custody = repos / store_id
        stage = Path(tempfile.mkdtemp(prefix=".initializing-", dir=repos))
        try:
            (stage / ".ledger").mkdir(mode=0o700)
            if adopt_from is not None:
                cold_adopt(source, stage, candidates, [p.resolve(strict=True) for p in definitions or []], ledger_bin)
            write_json(stage / MARKER, {"schema": MARKER_SCHEMA, "store_id": store_id})
            sync_directory(stage / ".ledger")
            if adopt_from is None:
                late_candidates = legacy_roots(root)
                if late_candidates:
                    raise ContextError("Legacy history appeared during initialization; reconcile before registration: "
                                       + ", ".join(map(str, late_candidates)))
            os.rename(stage, custody)
            sync_directory(repos)
            if adopt_from is not None:
                native_doctor(ledger_bin, custody, [p.resolve(strict=True) for p in definitions or []],
                              ["--store-root", str(custody), "--store-id", store_id])
            # Publish only after validation at the final, identity-checked address.
            write_json(registration, {"schema": REGISTRATION_SCHEMA, "store_id": store_id, "store_root": str(custody)})
        finally:
            if stage.exists():
                shutil.rmtree(stage)
        return checked_registration(root, common, mutated=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--initialize", action="store_true")
    parser.add_argument("--adopt-from", type=Path)
    parser.add_argument("--definition", type=Path, action="append", default=[])
    parser.add_argument("--confirm-no-writers", action="store_true")
    parser.add_argument("--ledger-bin", default="ledger")
    args = parser.parse_args()
    try:
        if (args.adopt_from or args.definition or args.confirm_no_writers) and not args.initialize:
            raise ContextError("Initialization flags require --initialize")
        if args.definition and args.adopt_from is None:
            raise ContextError("Definitions require --adopt-from")
        result = resolve(args.repo, initialize=args.initialize, adopt_from=args.adopt_from,
                         definitions=args.definition, confirm_no_writers=args.confirm_no_writers,
                         ledger_bin=args.ledger_bin)
    except (ContextError, OSError, ValueError) as exc:
        print(json.dumps({"schema": "ledger-workspace-context-error/v1", "status": "blocked", "error": str(exc), "authority_granted": False}), file=sys.stderr)
        return 3
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
