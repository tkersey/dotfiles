#!/usr/bin/env -S uv run python
"""Validate and transport one source-authorized Negative Ledger projection."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any


NEG_ID_RE = re.compile(r"^NEG-[A-Za-z0-9][A-Za-z0-9._:-]*$")
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
ALLOWED_KINDS = {
    "ledger-projection",
    "ledger-status-transition",
    "ledger-supersession",
    "ledger-retraction",
}
INCOMPLETE_STATUSES = {"capture_candidate", "need-evidence", "unknown"}
COMPLETE_STATUSES = {"active", "accepted_risk", "stale", "reopened", "superseded"}
REQUIRED_PAYLOAD_STRINGS = {
    "neg_id",
    "record_version",
    "repository_id",
    "ledger_path",
    "projection_fingerprint",
    "event_chain_fingerprint",
    "status",
    "kind",
    "artifact_state_id",
    "hypothesis",
    "attempted_change",
    "observed_outcome",
    "failure_class",
    "exclusion_scope",
    "confidence",
    "next_search_hint",
}


class AdapterError(RuntimeError):
    """Deterministic adapter failure suitable for a checkpoint receipt."""


def _nonempty(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AdapterError(f"{field}: expected non-empty string")
    return value.strip()


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


def validate_projection(raw: bytes, expected_id: str) -> dict[str, Any]:
    envelope = _parse_json(raw, "ledger export")
    if not isinstance(envelope, dict):
        raise AdapterError("ledger export: expected object")
    if envelope.get("authority") != "ledger-cli":
        raise AdapterError("ledger export.authority: expected ledger-cli")
    _nonempty(envelope.get("operation"), "ledger export.operation")
    _nonempty(envelope.get("summary"), "ledger export.summary")
    payload = envelope.get("payload")
    if not isinstance(payload, dict):
        raise AdapterError("ledger export.payload: expected object")
    for field in sorted(REQUIRED_PAYLOAD_STRINGS):
        _nonempty(payload.get(field), f"ledger export.payload.{field}")
    if payload["neg_id"] != expected_id:
        raise AdapterError(
            f"ledger export.payload.neg_id: expected {expected_id}, got {payload['neg_id']}"
        )
    if not NEG_ID_RE.fullmatch(expected_id):
        raise AdapterError(f"id: invalid Negative Ledger id: {expected_id}")
    if payload["status"] in INCOMPLETE_STATUSES:
        raise AdapterError(
            f"ledger export.payload.status: incomplete projection {payload['status']}"
        )
    if payload["status"] not in COMPLETE_STATUSES:
        raise AdapterError(f"ledger export.payload.status: unknown {payload['status']}")
    for field in ("projection_fingerprint", "event_chain_fingerprint"):
        if not SHA256_RE.fullmatch(payload[field]):
            raise AdapterError(f"ledger export.payload.{field}: invalid sha256")

    source_refs = payload.get("source_refs")
    if not isinstance(source_refs, list) or not source_refs:
        raise AdapterError("ledger export.payload.source_refs: expected witness rows")

    if payload["status"] == "active":
        for field in ("applicability_conditions", "reopening_criteria"):
            value = payload.get(field)
            if not isinstance(value, list) or not value:
                raise AdapterError(
                    f"ledger export.payload.{field}: active projection requires rows"
                )
        _nonempty(payload.get("exclusion_rule"), "ledger export.payload.exclusion_rule")
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
    doctor_argv = [ledger, "doctor", "--source", "negative-ledger"]
    export_argv = [
        ledger,
        "export",
        "--source",
        "negative-ledger",
        "--id",
        args.id,
        "--format",
        "memory-note",
    ]
    if args.file:
        doctor_argv.extend(["--file", args.file])
        export_argv.extend(["--file", args.file])
    doctor_raw = _require_success(_run(doctor_argv, cwd=repo), "ledger doctor")
    doctor = _parse_json(doctor_raw, "ledger doctor")
    export_raw = _require_success(_run(export_argv, cwd=repo), "ledger export")
    envelope = validate_projection(export_raw, args.id)
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
        command.add_argument("--file")
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
