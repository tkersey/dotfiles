#!/usr/bin/env python3
"""Conservative cache cleanup; dependency working state is never disposable."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time


class CacheError(RuntimeError):
    pass


def command(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=30,
                              env={**os.environ, "LC_ALL": "C"})
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CacheError(f"command unavailable: {args[0]}: {exc}") from exc


def require_quiet() -> None:
    result = command("pgrep", "-x", "zig")
    if result.returncode == 0:
        raise CacheError("CACHE_ACTIVE_BUILD_REFUSED: stop Zig processes before deletion")
    if result.returncode != 1:
        raise CacheError("CACHE_PROCESS_CHECK_UNAVAILABLE: cannot establish quiescence")


def directory(text: str | Path) -> Path:
    try:
        path = Path(text).expanduser().resolve(strict=True)
    except OSError as exc:
        raise CacheError(f"CACHE_PATH_UNDISCOVERED: {text}: {exc}") from exc
    if not path.is_dir():
        raise CacheError(f"not a directory: {path}")
    return path


def discovered_global(root: Path) -> Path:
    result = command("zig", "env", cwd=root)
    if result.returncode:
        raise CacheError(f"CACHE_PATH_UNDISCOVERED: zig env failed: {result.stderr.strip()}")
    try:
        value = json.loads(result.stdout)["global_cache_dir"]
    except (ValueError, KeyError, TypeError):
        match = re.search(
            r'^\s*\.?global_cache_dir\s*=\s*("(?:[^"\\]|\\.)*")\s*,?\s*$',
            result.stdout, re.MULTILINE,
        )
        if not match:
            raise CacheError("CACHE_PATH_UNDISCOVERED: unrecognized zig env output")
        try:
            value = json.loads(match[1])
        except ValueError as exc:
            raise CacheError("CACHE_PATH_UNDISCOVERED: unsupported path encoding") from exc
    if not isinstance(value, str) or not Path(value).is_absolute():
        raise CacheError("CACHE_PATH_UNDISCOVERED: global cache must be an absolute path")
    return directory(value)


def descendants(path: Path):
    def fail(exc: OSError) -> None:
        raise exc
    for here, dirs, files in os.walk(path, followlinks=False, onerror=fail):
        for name in dirs + files:
            yield Path(here) / name


def inspect_candidate(path: Path) -> tuple[int, float, tuple[int, int]]:
    if path.is_symlink() or not path.is_dir() or os.path.ismount(path):
        raise CacheError(f"CACHE_PATH_REFUSED: not a real directory: {path}")
    stat = path.stat()
    size, newest = 0, stat.st_mtime
    for entry in descendants(path):
        if entry.name == ".git" or os.path.ismount(entry):  # Worktrees and mounted contents are not cache.
            raise CacheError(f"CACHE_REPOSITORY_UNTOUCHED: {entry.parent}")
        info = entry.lstat()
        newest = max(newest, info.st_mtime)
        if not entry.is_symlink() and entry.is_file():
            size += info.st_size
    probe = command("git", "-C", str(path.parent), "rev-parse", "--show-toplevel")
    if probe.returncode == 0:
        tracked = command("git", "-C", str(path.parent), "ls-files", "-z", "--", str(path))
        if tracked.returncode:
            raise CacheError(f"CACHE_GIT_CHECK_UNAVAILABLE: {path}")
        if tracked.stdout:
            raise CacheError(f"CACHE_TRACKED_FILES_UNTOUCHED: {path}")
    elif probe.returncode != 128 or "not a git repository" not in probe.stderr.lower():
        raise CacheError(f"CACHE_GIT_CHECK_UNAVAILABLE: {probe.stderr.strip()}")
    return size, newest, (stat.st_dev, stat.st_ino)


def candidates(args: argparse.Namespace, root: Path) -> list[tuple[str, Path]]:
    if args.include_zig_pkg:
        raise CacheError("CACHE_ZIG_PKG_REFUSED: dependencies require repository-specific preservation; nothing deleted")
    if args.global_path and not args.include_global:
        raise CacheError("--global-path requires --include-global")
    protected = {Path("/"), Path.home().resolve(), directory("/tmp"), Path("/home"), Path("/Users"), Path("/var")}
    if root in protected:
        raise CacheError(f"CACHE_ROOT_REFUSED: {root}")
    plan = []
    for name in (".zig-cache", "zig-cache") + (("zig-out",) if args.include_zig_out else ()):
        path = root / name
        if path.exists() or path.is_symlink():
            plan.append(("OUTPUT" if name == "zig-out" else "LOCAL", path))
    if args.include_global:
        cache = discovered_global(root)
        if args.global_path and directory(args.global_path) != cache:
            raise CacheError("CACHE_PATH_REFUSED: --global-path must match zig env; it is not a deletion override")
        if cache in protected or root == cache or cache in root.parents:
            raise CacheError(f"CACHE_PATH_REFUSED: global cache overlaps a protected root: {cache}")
        # Deliberately support object-store directories, not arbitrary contents.
        # Package storage (p) is preserved, even when it is in a global cache.
        entries = list(cache.iterdir())
        if any(p.name not in {"o", "h", "z", "b", "tmp", "p"} for p in entries):
            raise CacheError(f"CACHE_LAYOUT_REFUSED: unknown global cache contents: {cache}")
        for entry in entries:
            if entry.name == "p":
                print(f"CACHE_DEPENDENCIES_UNTOUCHED: {entry}")
            else:
                plan.append(("GLOBAL", entry))
    for i, (_, left) in enumerate(plan):
        for _, right in plan[i + 1:]:
            if left == right or left in right.parents or right in left.parents:
                raise CacheError("CACHE_PATH_REFUSED: overlapping deletion candidates")
    return plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="one project root; nested projects are not traversed")
    parser.add_argument("--yes", action="store_true", help="delete; otherwise inspect only")
    parser.add_argument("--include-zig-out", action="store_true")
    parser.add_argument("--include-zig-pkg", action="store_true", help="retired; always refuses before deletion")
    parser.add_argument("--include-global", action="store_true")
    parser.add_argument("--global-path", help="optional assertion of the path reported by zig env")
    parser.add_argument("--older-than", type=int, metavar="DAYS", help="require every descendant to be older")
    args = parser.parse_args(argv)
    if args.older_than is not None and args.older_than < 0:
        parser.error("--older-than must be nonnegative")
    try:
        root = directory(args.root)
        plan = candidates(args, root)
        # Validate the entire selection before performing any deletion.
        inspected = [(kind, path, inspect_candidate(path)) for kind, path in plan]
        cutoff = time.time() - args.older_than * 86400 if args.older_than is not None else None
        selected = []
        for kind, path, (size, newest, identity) in inspected:
            if cutoff is not None and newest >= cutoff:
                print(f"CACHE_SKIPPED_RECENT: {path}")
            else:
                print(f"{'candidate' if args.yes else 'would delete'}: {path} ({size} bytes)")
                selected.append((kind, path, identity))
        if not args.yes:
            print("CACHE_DRY_RUN_ONLY")
            return 0
        if selected and not shutil.rmtree.avoids_symlink_attacks:
            raise CacheError("CACHE_DELETE_UNAVAILABLE: platform lacks symlink-resistant rmtree")
        for kind, path, identity in selected:
            require_quiet()
            _, newest, current_identity = inspect_candidate(path)
            if current_identity != identity:
                raise CacheError(f"CACHE_CHANGED_REFUSED: {path}")
            if cutoff is not None and newest >= cutoff:
                print(f"CACHE_SKIPPED_RECENT: {path}")
                continue
            shutil.rmtree(path)
            print(f"CACHE_{kind}_DRAINED: {path}")
        if not selected:
            print("CACHE_NO_CHANGES")
        return 0
    except (CacheError, OSError) as exc:
        print(f"CACHE_REFUSED_OR_FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
