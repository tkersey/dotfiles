#!/usr/bin/env python3
"""Run and validate Zig proof commands with an exact ZPE-v1 context."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import uuid
from typing import Any


class EpochError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run_text(cwd: Path, *args: str, check: bool = True) -> str:
    proc = subprocess.run(
        list(args),
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and proc.returncode != 0:
        raise EpochError(proc.stderr.strip() or proc.stdout.strip() or "command failed")
    return proc.stdout.strip()


def discover_root(cwd: Path) -> Path:
    proc = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise EpochError("proof command must run inside a git repository")
    return Path(proc.stdout.strip()).resolve()


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def normalize_ignored(root: Path, ignored_paths: list[Path] | None) -> set[str]:
    ignored = {'.zig-proof', '.zig-proof/'}
    for path in ignored_paths or []:
        try:
            rel = path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            continue
        ignored.add(rel)
        if path.is_dir() or rel.endswith('/'):
            ignored.add(rel.rstrip('/') + '/')
    return ignored


def path_is_ignored(rel: str, ignored: set[str]) -> bool:
    rel = rel.replace('\\', '/')
    for item in ignored:
        if item.endswith('/'):
            if rel.startswith(item):
                return True
        elif rel == item or rel.startswith(item.rstrip('/') + '/'):
            return True
    return False


def porcelain_rows(root: Path) -> list[tuple[str, str]]:
    raw = subprocess.run(
        ['git', 'status', '--porcelain=v1', '-z', '--untracked-files=all'],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    ).stdout
    parts = raw.split(b'\0')
    rows: list[tuple[str, str]] = []
    index = 0
    while index < len(parts):
        part = parts[index]
        index += 1
        if not part:
            continue
        text = part.decode('utf-8', 'surrogateescape')
        status = text[:2]
        path = text[3:]
        if status[0] in {'R', 'C'} and index < len(parts):
            new_path = parts[index].decode('utf-8', 'surrogateescape')
            index += 1
            rows.append((status, path))
            rows.append((status, new_path))
        else:
            rows.append((status, path))
    return rows


def git_state(root: Path, ignored_paths: list[Path] | None = None) -> dict[str, Any]:
    head = run_text(root, 'git', 'rev-parse', 'HEAD')
    branch = run_text(root, 'git', 'branch', '--show-current', check=False) or '(detached)'
    ignored = normalize_ignored(root, ignored_paths)
    rows = [(status, rel) for status, rel in porcelain_rows(root) if not path_is_ignored(rel, ignored)]

    h = hashlib.sha256()
    status_lines: list[str] = []
    for status, rel in sorted(rows, key=lambda row: (row[1], row[0])):
        status_lines.append(f'{status} {rel}')
        h.update(status.encode() + b'\0' + rel.encode('utf-8', 'surrogateescape') + b'\0')
        path = root / rel
        try:
            h.update(path.read_bytes())
        except OSError:
            h.update(b'<missing>')
        staged = subprocess.run(
            ['git', 'show', f':{rel}'],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if staged.returncode == 0:
            h.update(b'\0<index>\0' + staged.stdout)

    return {
        'branch': branch,
        'head': head,
        'dirty': bool(rows),
        'dirty_fingerprint': 'sha256:' + h.hexdigest(),
        'status': status_lines,
    }


def hash_files(root: Path, names: list[str]) -> str:
    h = hashlib.sha256()
    for name in names:
        path = root / name
        h.update(name.encode() + b"\0")
        if path.is_file():
            h.update(path.read_bytes())
        else:
            h.update(b"<missing>")
    return "sha256:" + h.hexdigest()


def generated_fingerprint(root: Path) -> str:
    names = []
    for candidate in (
        "build.zig",
        "build.zig.zon",
        "repo_zig_paths.txt",
        "MANIFEST.files",
        "MANIFEST.sha256",
    ):
        if (root / candidate).exists():
            names.append(candidate)
    for directory_name in ("generated", "golden", "testdata"):
        directory = root / directory_name
        if directory.is_dir():
            for path in sorted(directory.rglob("*")):
                if path.is_file() and path.stat().st_size <= 2_000_000:
                    names.append(path.relative_to(root).as_posix())
    return hash_files(root, names)


def zig_version(cwd: Path) -> str:
    proc = subprocess.run(
        ["zig", "version"],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        return "UNAVAILABLE"
    return proc.stdout.strip()


def parse_command_context(command: list[str]) -> dict[str, Any]:
    target = None
    optimize = None
    build_options = []
    fork_overrides = []
    for token in command:
        if token.startswith("-Dtarget="):
            target = token.split("=", 1)[1]
        elif token.startswith("-Doptimize="):
            optimize = token.split("=", 1)[1]
        elif token.startswith("-D"):
            build_options.append(token)
        elif token.startswith("--fork"):
            fork_overrides.append(token)
    return {
        "target": target,
        "optimize_mode": optimize,
        "build_options": build_options,
        "fork_overrides": fork_overrides,
    }


def capture(
    cwd: Path,
    command: list[str],
    ignored_paths: list[Path] | None = None,
) -> dict[str, Any]:
    root = discover_root(cwd)
    state = git_state(root, ignored_paths)
    parsed = parse_command_context(command)
    return {
        "cwd": str(cwd),
        "repository_root": str(root),
        **state,
        "zig_version": zig_version(cwd),
        **parsed,
        "dependency_fingerprint": hash_files(root, ["build.zig", "build.zig.zon"]),
        "generated_artifact_fingerprint": generated_fingerprint(root),
        "cache_environment": {
            "ZIG_GLOBAL_CACHE_DIR": os.environ.get("ZIG_GLOBAL_CACHE_DIR"),
            "ZIG_LOCAL_CACHE_DIR": os.environ.get("ZIG_LOCAL_CACHE_DIR"),
        },
    }


def invalidators(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    fields = {
        "cwd": "cwd-changed",
        "repository_root": "repository-root-changed",
        "head": "head-changed",
        "dirty_fingerprint": "tree-changed",
        "zig_version": "zig-version-changed",
        "dependency_fingerprint": "dependency-changed",
        "generated_artifact_fingerprint": "generated-artifact-changed",
        "target": "target-changed",
        "optimize_mode": "optimize-mode-changed",
        "build_options": "build-options-changed",
        "fork_overrides": "fork-overrides-changed",
        "cache_environment": "cache-environment-changed",
    }
    return [reason for field, reason in fields.items() if before.get(field) != after.get(field)]


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


def run_epoch(args: argparse.Namespace) -> int:
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise EpochError("run requires a command after --")

    cwd = Path(args.cwd).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    log_path = Path(args.log).expanduser().resolve() if args.log else output.with_suffix(".log")

    ignored_paths = [output, log_path]
    start = capture(cwd, command, ignored_paths)
    started_at = now()
    proc = subprocess.run(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    ended_at = now()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        "$ " + shlex.join(command) + "\n"
        + f"exit_code={proc.returncode}\n\n"
        + proc.stdout,
        encoding="utf-8",
    )
    end = capture(cwd, command, ignored_paths)
    stale = invalidators(start, end)
    result = "pass" if proc.returncode == 0 and not stale else "fail"
    if proc.returncode == 0 and stale:
        result = "blocked"

    epoch = {
        "zig_proof_epoch": {
            "epoch_version": "ZPE-v1",
            "epoch_id": "ZPE-" + uuid.uuid4().hex[:16],
            "command": command,
            "started_at": started_at,
            "ended_at": ended_at,
            "exit_code": proc.returncode,
            "result": result,
            "state_before": start,
            "state_after": end,
            "invalidators": stale,
            "log_ref": str(log_path),
            "ignored_paths": [str(path) for path in ignored_paths],
        }
    }
    write_json(output, epoch)
    print(json.dumps(epoch, indent=2, sort_keys=True))
    return 0 if result == "pass" else 2


def check_epoch(args: argparse.Namespace) -> int:
    path = Path(args.epoch).expanduser().resolve()
    value = json.loads(path.read_text(encoding="utf-8"))
    body = value.get("zig_proof_epoch", value)
    if body.get("epoch_version") != "ZPE-v1":
        raise EpochError("unsupported proof epoch")
    command = body.get("command")
    if not isinstance(command, list) or not command:
        raise EpochError("epoch command missing")
    after = body.get("state_after")
    if not isinstance(after, dict):
        raise EpochError("epoch state_after missing")
    ignored_paths = [Path(value) for value in body.get("ignored_paths", [])]
    current = capture(
        Path(after["cwd"]),
        [str(item) for item in command],
        ignored_paths,
    )
    stale = invalidators(after, current)
    errors = []
    if body.get("result") != "pass":
        errors.append(f"epoch-result:{body.get('result')}")
    if stale:
        errors.extend(stale)
    result = {
        "zig_proof_epoch_check": {
            "verdict": "pass" if not errors else "stale",
            "epoch_id": body.get("epoch_id"),
            "errors": errors,
            "current_state": current,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="subcommand", required=True)

    run_parser = sub.add_parser("run")
    run_parser.add_argument("--output", required=True)
    run_parser.add_argument("--log")
    run_parser.add_argument("--cwd", default=".")
    run_parser.add_argument("command", nargs=argparse.REMAINDER)
    run_parser.set_defaults(func=run_epoch)

    check_parser = sub.add_parser("check")
    check_parser.add_argument("--epoch", required=True)
    check_parser.set_defaults(func=check_epoch)

    args = parser.parse_args()
    try:
        return int(args.func(args))
    except (EpochError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"zig_proof_epoch_error": {"message": str(exc)}}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
