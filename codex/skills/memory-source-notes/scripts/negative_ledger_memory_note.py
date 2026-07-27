#!/usr/bin/env -S uv run python
"""Validate and transport one source-authorized Negative Ledger projection."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


ALLOWED_KINDS = {
    "ledger-projection",
    "ledger-status-transition",
    "ledger-supersession",
    "ledger-retraction",
}
SKILLS_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DEFINITION = (
    SKILLS_ROOT
    / "negative-ledger/definitions/ledger/negative-evidence-protocol.json"
)
NOTE_DEFINITION = (
    SKILLS_ROOT
    / "memory-source-notes/definitions/ledger/"
    "negative-ledger-memory-note-payload.json"
)


class AdapterError(RuntimeError):
    """Deterministic adapter failure suitable for a checkpoint receipt."""


def _resolve_binary(explicit: str | None, env_name: str, name: str) -> str:
    candidate = explicit or os.environ.get(env_name) or shutil.which(name)
    if not candidate:
        raise AdapterError(f"{name}: unavailable")
    path = Path(candidate).expanduser()
    if path.is_absolute() and not path.is_file():
        raise AdapterError(f"{name}: not a file: {path}")
    return str(path if path.is_absolute() else candidate)


def _run(
    argv: list[str],
    *,
    cwd: Path,
    input_bytes: bytes | None = None,
) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            argv,
            cwd=cwd,
            input=input_bytes,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        raise AdapterError(f"{Path(argv[0]).name}: {exc}") from exc


def _require_success(proc: subprocess.CompletedProcess[bytes], stage: str) -> bytes:
    if proc.returncode != 0:
        detail = proc.stderr.decode("utf-8", errors="replace").strip()
        raise AdapterError(f"{stage}: {detail or f'exit {proc.returncode}'}")
    return proc.stdout


def _parse_json(raw: bytes, stage: str) -> Any:
    try:
        return json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AdapterError(f"{stage}: invalid JSON: {exc}") from exc


def validate_projection(
    raw: bytes,
    expected_id: str,
    *,
    ledger: str,
    repo: Path,
) -> dict[str, Any]:
    validation_raw = _require_success(
        _run(
            [
                ledger,
                "validate",
                "--definition",
                str(NOTE_DEFINITION),
                "--input",
                "note=-",
                "--format",
                "json",
            ],
            cwd=repo,
            input_bytes=raw,
        ),
        "ledger validate note",
    )
    validation = _parse_json(validation_raw, "ledger validate note")
    if not isinstance(validation, dict) or validation.get("valid") is not True:
        raise AdapterError("ledger validate note: invalid result")
    envelope = _parse_json(raw, "ledger project")
    if not isinstance(envelope, dict):
        raise AdapterError("ledger project: expected object")
    payload = envelope.get("payload")
    if not isinstance(payload, dict):
        raise AdapterError("ledger project.payload: expected object")
    if payload["neg_id"] != expected_id:
        raise AdapterError(
            f"ledger project.payload.neg_id: expected {expected_id}, got {payload['neg_id']}"
        )
    return envelope


def expected_writer_fingerprint(kind: str, raw: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(b"negative-ledger\n")
    digest.update(kind.encode("utf-8"))
    digest.update(b"\n")
    digest.update(raw)
    return digest.hexdigest()


def inspect_projection(args: argparse.Namespace) -> tuple[bytes, dict[str, Any]]:
    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        raise AdapterError(f"repo: not a directory: {repo}")
    ledger = _resolve_binary(args.ledger_bin, "LEDGER_BIN", "ledger")
    doctor_argv = [
        ledger,
        "doctor",
        "--definition",
        str(SOURCE_DEFINITION),
        "--repo",
        str(repo),
        "--format",
        "json",
    ]
    export_argv = [
        ledger,
        "project",
        "--definition",
        str(SOURCE_DEFINITION),
        "--projection",
        "memory-note",
        "--repo",
        str(repo),
        "--param",
        f"id={args.id}",
        "--payload-only",
        "--format",
        "json",
    ]
    doctor_raw = _require_success(_run(doctor_argv, cwd=repo), "ledger doctor")
    doctor = _parse_json(doctor_raw, "ledger doctor")
    export_raw = _require_success(_run(export_argv, cwd=repo), "ledger project")
    envelope = validate_projection(
        export_raw,
        args.id,
        ledger=ledger,
        repo=repo,
    )
    return export_raw, {
        "schema": "negative-ledger-admission-inspection/v1",
        "status": "exportable",
        "neg_id": args.id,
        "kind": args.kind,
        "projection_status": envelope["payload"]["status"],
        "projection_fingerprint": envelope["payload"]["projection_fingerprint"],
        "writer_fingerprint": expected_writer_fingerprint(args.kind, export_raw),
        "doctor": doctor,
        "authority_granted": False,
        "storage_mutated": False,
    }


def cmd_inspect(args: argparse.Namespace) -> int:
    _, report = inspect_projection(args)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def cmd_admit(args: argparse.Namespace) -> int:
    export_raw, _ = inspect_projection(args)
    repo = Path(args.repo).expanduser().resolve()
    memory_note = _resolve_binary(
        args.memory_note_bin, "MEMORY_NOTE_BIN", "memory-note"
    )
    argv = [
        memory_note,
        "append",
        "--extension",
        "negative-ledger",
        "--kind",
        args.kind,
        "--json",
        "-",
    ]
    if args.codex_home:
        argv.extend(["--codex-home", args.codex_home])
    if args.dry_run:
        argv.append("--dry-run")
    proc = _run(argv, cwd=repo, input_bytes=export_raw)
    stdout = _require_success(proc, "memory-note append")
    result = _parse_json(stdout, "memory-note append")
    if not isinstance(result, dict):
        raise AdapterError("memory-note append: expected object result")
    sys.stdout.buffer.write(stdout)
    if proc.stderr:
        sys.stderr.buffer.write(proc.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and transport a source-authorized Negative Ledger projection"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name, handler in (("inspect", cmd_inspect), ("admit", cmd_admit)):
        command = sub.add_parser(name)
        command.add_argument("--id", required=True)
        command.add_argument(
            "--kind", choices=sorted(ALLOWED_KINDS), default="ledger-projection"
        )
        command.add_argument("--repo", default=".")
        command.add_argument("--ledger-bin")
        if name == "admit":
            command.add_argument("--memory-note-bin")
            command.add_argument("--codex-home")
            command.add_argument("--dry-run", action="store_true")
        command.set_defaults(func=handler)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return int(args.func(args))
    except AdapterError as exc:
        print(
            json.dumps(
                {
                    "negative_ledger_memory_note": {
                        "verdict": "blocked",
                        "error": str(exc),
                        "canonical_rollback": False,
                    }
                },
                indent=2,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
