#!/usr/bin/env -S uv run python
"""Read-only reconciliation of canonical source records and memory admissions."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any
from urllib.parse import urlparse


SOURCES = ("learnings", "synesthesia", "negative-ledger")
ELIGIBILITY = {"eligible", "not-eligible"}


class ReconcileError(RuntimeError):
    """A deterministic read-side failure."""


def resolve_binary(explicit: str | None, env_name: str, name: str) -> str:
    value = explicit or os.environ.get(env_name) or shutil.which(name)
    if not value:
        raise ReconcileError(f"{name}: unavailable")
    return value


def run_bytes(argv: list[str], *, cwd: Path) -> bytes:
    try:
        proc = subprocess.run(argv, cwd=cwd, capture_output=True, check=False)
    except OSError as exc:
        raise ReconcileError(f"{Path(argv[0]).name}: {exc}") from exc
    if proc.returncode != 0:
        detail = proc.stderr.decode("utf-8", errors="replace").strip()
        raise ReconcileError(
            f"{' '.join(argv[1:3])}: {detail or f'exit {proc.returncode}'}"
        )
    return proc.stdout


def parse_json(raw: bytes, stage: str) -> Any:
    try:
        return json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReconcileError(f"{stage}: invalid JSON: {exc}") from exc


def run_json(argv: list[str], *, cwd: Path) -> Any:
    return parse_json(run_bytes(argv, cwd=cwd), " ".join(argv[1:3]))


def writer_fingerprint(extension: str, kind: str, raw: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(extension.encode())
    digest.update(b"\n")
    digest.update(kind.encode())
    digest.update(b"\n")
    digest.update(raw)
    return digest.hexdigest()


def load_eligibility(path: str | None) -> dict[str, dict[str, dict[str, str]]]:
    empty = {source: {} for source in SOURCES}
    if not path:
        return empty
    try:
        value = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReconcileError(f"eligibility: {exc}") from exc
    if (
        not isinstance(value, dict)
        or value.get("schema") != "source-memory-eligibility/v1"
    ):
        raise ReconcileError("eligibility: expected source-memory-eligibility/v1")
    decisions = value.get("decisions")
    if not isinstance(decisions, dict) or set(decisions) - set(SOURCES):
        raise ReconcileError("eligibility.decisions: unexpected source")
    result = {source: {} for source in SOURCES}
    for source, rows in decisions.items():
        if not isinstance(rows, dict):
            raise ReconcileError(f"eligibility.decisions.{source}: expected object")
        for record_id, decision in rows.items():
            if not isinstance(decision, dict):
                raise ReconcileError(
                    f"eligibility {source}/{record_id}: expected object"
                )
            disposition = decision.get("disposition")
            reason = decision.get("reason")
            if (
                disposition not in ELIGIBILITY
                or not isinstance(reason, str)
                or not reason.strip()
            ):
                raise ReconcileError(
                    f"eligibility {source}/{record_id}: expected eligible|not-eligible and reason"
                )
            result[source][record_id] = {
                "disposition": disposition,
                "reason": reason.strip(),
            }
    return result


def load_notes(
    memory_note: str,
    source: str,
    *,
    cwd: Path,
    codex_home: str | None,
) -> list[dict[str, Any]]:
    list_argv = [
        memory_note,
        "list",
        "--extension",
        source,
        "--limit",
        "10000",
        "--format",
        "json",
    ]
    if codex_home:
        list_argv.extend(["--codex-home", codex_home])
    listing = run_json(list_argv, cwd=cwd)
    if not isinstance(listing, dict) or not isinstance(listing.get("notes"), list):
        raise ReconcileError(f"memory-note list {source}: invalid result")
    notes = []
    for row in listing["notes"]:
        note_id = row.get("id") if isinstance(row, dict) else None
        if not isinstance(note_id, str):
            raise ReconcileError(f"memory-note list {source}: note id missing")
        show_argv = [
            memory_note,
            "show",
            "--extension",
            source,
            "--id",
            note_id,
            "--format",
            "json",
        ]
        if codex_home:
            show_argv.extend(["--codex-home", codex_home])
        note = run_json(show_argv, cwd=cwd)
        if not isinstance(note, dict):
            raise ReconcileError(f"memory-note show {note_id}: invalid result")
        notes.append(note)
    return notes


def load_compiled_corpus(codex_home: Path) -> str:
    root = codex_home / "memories"
    paths = [root / "memory_summary.md", root / "MEMORY.md"]
    skills = root / "skills"
    if skills.is_dir():
        paths.extend(path for path in skills.rglob("*") if path.is_file())
    chunks: list[str] = []
    for path in paths:
        try:
            chunks.append(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
    return "\n".join(chunks)


def normalize_repository(value: str) -> str:
    candidate = value.strip().rstrip("/")
    if candidate.startswith("git@") and ":" in candidate:
        candidate = candidate.split(":", 1)[1]
    elif "://" in candidate:
        parsed = urlparse(candidate)
        candidate = parsed.path.lstrip("/")
    if candidate.endswith(".git"):
        candidate = candidate[:-4]
    return candidate.casefold()


def repository_aliases(cwd: Path) -> set[str]:
    aliases = {
        normalize_repository(cwd.name),
        normalize_repository(cwd.name.lstrip(".")),
    }
    proc = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode == 0 and proc.stdout.strip():
        remote = normalize_repository(proc.stdout)
        aliases.add(remote)
        basename = remote.rsplit("/", 1)[-1]
        aliases.add(basename)
        aliases.add(f".{basename}")
    return {value for value in aliases if value}


def note_repository(note: dict[str, Any]) -> str | None:
    scope = note.get("scope")
    if isinstance(scope, dict) and isinstance(scope.get("repo"), str):
        value = normalize_repository(scope["repo"])
        if value:
            return value
    payload = note.get("payload")
    if isinstance(payload, dict):
        for field in ("repository_id", "repo"):
            if isinstance(payload.get(field), str):
                value = normalize_repository(payload[field])
                if value:
                    return value
    return None


def note_source_id(source: str, note: dict[str, Any]) -> str | None:
    payload = note.get("payload")
    if not isinstance(payload, dict):
        return None
    field = "learning_id" if source == "learnings" else "neg_id"
    value = payload.get(field)
    return value if isinstance(value, str) and value else None


def classify_record(
    *,
    record_id: str,
    note: dict[str, Any] | None,
    expected_fingerprint: str | None,
    export_error: str | None,
    eligibility: dict[str, str] | None,
    compiled_corpus: str,
) -> dict[str, Any]:
    note_id = note.get("id") if note else None
    note_fingerprint = note.get("fingerprint") if note else None
    current = bool(
        note and expected_fingerprint and note_fingerprint == expected_fingerprint
    )
    compiled = record_id in compiled_corpus or bool(
        note_id and note_id in compiled_corpus
    )

    if note and current:
        status = "admitted"
    elif note:
        status = "stale-note"
    elif export_error:
        status = "incomplete-projection"
    elif eligibility and eligibility["disposition"] == "eligible":
        status = "eligible-unadmitted"
    elif eligibility and eligibility["disposition"] == "not-eligible":
        status = "not-eligible"
    else:
        status = "needs-source-review"

    return {
        "record_id": record_id,
        "status": status,
        "note_id": note_id,
        "note_fingerprint": note_fingerprint,
        "expected_fingerprint": expected_fingerprint,
        "export_error": export_error,
        "eligibility": eligibility,
        "compiled_memory_visible": compiled,
        "phase2_lag": status == "admitted" and not compiled,
    }


def learning_records(ledger: str, *, cwd: Path) -> list[dict[str, Any]]:
    spec = json.dumps(
        {
            "dataset": "learnings",
            "select": ["id", "captured_at", "status", "fingerprint"],
            "sort": ["-captured_at"],
            "limit": 10000,
            "format": "json",
        },
        separators=(",", ":"),
    )
    value = run_json(
        [ledger, "query", "--source", "learnings", "--spec", spec], cwd=cwd
    )
    if not isinstance(value, list):
        raise ReconcileError("ledger query learnings: expected array")
    return value


def negative_records(ledger: str, *, cwd: Path) -> list[dict[str, Any]]:
    value = run_json([ledger, "query", "--source", "negative-ledger"], cwd=cwd)
    if not isinstance(value, dict) or not isinstance(value.get("records"), list):
        raise ReconcileError("ledger query negative-ledger: expected records")
    return value["records"]


def synesthesia_records(ledger: str, *, cwd: Path) -> list[dict[str, Any]]:
    raw = run_bytes(
        [ledger, "recent", "--source", "synesthesia", "--limit", "10000"], cwd=cwd
    )
    records = []
    for line in raw.decode("utf-8").splitlines():
        record_id = line.split(maxsplit=1)[0] if line.strip() else ""
        if not record_id.startswith("SYN-"):
            continue
        value = run_json(
            [ledger, "show", "--source", "synesthesia", "--id", record_id], cwd=cwd
        )
        if isinstance(value, dict):
            records.append(value)
    return records


def native_export(
    ledger: str,
    source: str,
    record_id: str,
    *,
    cwd: Path,
) -> tuple[bytes | None, str | None]:
    argv = [
        ledger,
        "export",
        "--source",
        source,
        "--id",
        record_id,
        "--format",
        "memory-note",
    ]
    try:
        return run_bytes(argv, cwd=cwd), None
    except ReconcileError as exc:
        return None, str(exc)


def canonical_record_id(source: str, record: dict[str, Any]) -> str | None:
    field = {
        "learnings": "id",
        "synesthesia": "syn_id",
        "negative-ledger": "neg_id",
    }[source]
    value = record.get(field)
    return value if isinstance(value, str) and value else None


def validate_eligibility_ids(
    eligibility: dict[str, dict[str, dict[str, str]]],
    records: dict[str, list[dict[str, Any]]],
) -> None:
    for source in SOURCES:
        canonical_ids = {
            record_id
            for record in records[source]
            if (record_id := canonical_record_id(source, record)) is not None
        }
        unknown = sorted(set(eligibility[source]) - canonical_ids)
        if unknown:
            raise ReconcileError(
                f"eligibility {source}: unknown canonical ids: {', '.join(unknown)}"
            )


def load_synesthesia_adapter(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("synesthesia_memory_note", path)
    if spec is None or spec.loader is None:
        raise ReconcileError(f"synesthesia adapter: cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_report(
    source: str,
    records: list[dict[str, Any]],
    notes: list[dict[str, Any]],
    *,
    ledger: str,
    cwd: Path,
    eligibility: dict[str, dict[str, str]],
    compiled_corpus: str,
    synesthesia_adapter: Any,
    repo_aliases: set[str],
) -> dict[str, Any]:
    foreign_notes: list[dict[str, Any]] = []
    local_notes: list[dict[str, Any]] = []
    for note in notes:
        repository = note_repository(note)
        if source != "synesthesia" and repository and repository not in repo_aliases:
            foreign_notes.append(note)
        else:
            local_notes.append(note)

    notes_by_id: dict[str, list[dict[str, Any]]] = {}
    for note in local_notes:
        source_id = note_source_id(source, note)
        if source_id is not None:
            notes_by_id.setdefault(source_id, []).append(note)
    notes_by_fingerprint = {
        note.get("fingerprint"): note
        for note in local_notes
        if isinstance(note.get("fingerprint"), str)
    }
    rows = []
    canonical_ids: set[str] = set()

    for record in records:
        candidate_notes: list[dict[str, Any]] = []
        record_id = canonical_record_id(source, record)
        if source == "learnings":
            logical_kind = "learning-admission"
        elif source == "negative-ledger":
            logical_kind = "ledger-projection"
        else:
            logical_kind = record.get("logical_kind") or record.get("kind")
        if not isinstance(record_id, str):
            continue
        canonical_ids.add(record_id)
        candidate_notes = notes_by_id.get(record_id, [])

        should_export = (
            source != "learnings" or bool(candidate_notes) or record_id in eligibility
        )
        if should_export:
            raw, export_error = native_export(ledger, source, record_id, cwd=cwd)
        else:
            raw, export_error = None, None
        expected = None
        note = candidate_notes[0] if candidate_notes else None
        if raw is not None and source == "synesthesia":
            try:
                value = parse_json(raw, f"ledger export {record_id}")
                physical, normalized = synesthesia_adapter.validate_and_normalize(
                    logical_kind, value
                )
                expected = synesthesia_adapter.canonical_fingerprint(
                    physical, normalized
                )
                note = notes_by_fingerprint.get(expected)
            except Exception as exc:
                export_error = f"synesthesia adapter: {exc}"
        elif raw is not None:
            if candidate_notes:
                for candidate in candidate_notes:
                    candidate_kind = candidate.get("kind")
                    if not isinstance(candidate_kind, str):
                        continue
                    candidate_expected = writer_fingerprint(source, candidate_kind, raw)
                    if candidate.get("fingerprint") == candidate_expected:
                        note = candidate
                        expected = candidate_expected
                        break
                if expected is None and note is not None:
                    note_kind = note.get("kind")
                    if isinstance(note_kind, str):
                        expected = writer_fingerprint(source, note_kind, raw)
            else:
                expected = writer_fingerprint(source, logical_kind, raw)

        rows.append(
            classify_record(
                record_id=record_id,
                note=note,
                expected_fingerprint=expected,
                export_error=export_error,
                eligibility=eligibility.get(record_id),
                compiled_corpus=compiled_corpus,
            )
        )

    orphan_notes = []
    for note in local_notes:
        source_id = note_source_id(source, note)
        if source == "synesthesia":
            if note.get("fingerprint") not in {
                row["expected_fingerprint"]
                for row in rows
                if row["expected_fingerprint"]
            }:
                orphan_notes.append(note.get("id"))
        elif source_id not in canonical_ids:
            orphan_notes.append(note.get("id"))

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    counts["phase2-lag"] = sum(1 for row in rows if row["phase2_lag"])
    return {
        "canonical_records": len(rows),
        "admission_notes": len(local_notes),
        "counts": counts,
        "records": rows,
        "orphan_note_ids": [value for value in orphan_notes if isinstance(value, str)],
        "foreign_repo_note_ids": [
            note["id"] for note in foreign_notes if isinstance(note.get("id"), str)
        ],
    }


def reconcile(args: argparse.Namespace) -> dict[str, Any]:
    cwd = Path(args.repo).expanduser().resolve()
    if not cwd.is_dir():
        raise ReconcileError(f"repo: not a directory: {cwd}")
    ledger = resolve_binary(args.ledger_bin, "LEDGER_BIN", "ledger")
    memory_note = resolve_binary(args.memory_note_bin, "MEMORY_NOTE_BIN", "memory-note")
    codex_home = (
        Path(
            args.codex_home or os.environ.get("CODEX_HOME") or (Path.home() / ".codex")
        )
        .expanduser()
        .resolve()
    )
    eligibility = load_eligibility(args.eligibility)
    compiled = load_compiled_corpus(codex_home)
    repo_aliases = repository_aliases(cwd)

    doctors = {}
    for source in SOURCES:
        doctors[source] = run_json([ledger, "doctor", "--source", source], cwd=cwd)
    note_doctor_argv = [memory_note, "doctor", "--format", "json"]
    if args.codex_home:
        note_doctor_argv.extend(["--codex-home", args.codex_home])
    doctors["memory-note"] = run_json(note_doctor_argv, cwd=cwd)

    notes = {
        source: load_notes(
            memory_note,
            source,
            cwd=cwd,
            codex_home=args.codex_home,
        )
        for source in SOURCES
    }
    records = {
        "learnings": learning_records(ledger, cwd=cwd),
        "negative-ledger": negative_records(ledger, cwd=cwd),
        "synesthesia": synesthesia_records(ledger, cwd=cwd),
    }
    validate_eligibility_ids(eligibility, records)
    adapter_path = (
        Path(__file__).resolve().parents[2]
        / "memory-source-notes/scripts/synesthesia_memory_note.py"
    )
    synesthesia_adapter = load_synesthesia_adapter(adapter_path)
    source_reports = {
        source: source_report(
            source,
            records[source],
            notes[source],
            ledger=ledger,
            cwd=cwd,
            eligibility=eligibility[source],
            compiled_corpus=compiled,
            synesthesia_adapter=synesthesia_adapter,
            repo_aliases=repo_aliases,
        )
        for source in SOURCES
    }
    gaps = sum(
        report["counts"].get("eligible-unadmitted", 0)
        + report["counts"].get("stale-note", 0)
        for report in source_reports.values()
    )
    blocked = sum(
        report["counts"].get("incomplete-projection", 0)
        for report in source_reports.values()
    )
    return {
        "schema": "source-memory-reconciliation/v1",
        "verdict": "gaps" if gaps or blocked else "ok",
        "read_only": True,
        "authority_granted": False,
        "storage_mutated": False,
        "repo": str(cwd),
        "codex_home": str(codex_home),
        "doctors": doctors,
        "sources": source_reports,
        "summary": {
            "eligible_unadmitted_or_stale": gaps,
            "incomplete_projections": blocked,
            "phase2_lag": sum(
                report["counts"].get("phase2-lag", 0)
                for report in source_reports.values()
            ),
        },
    }


def print_text(report: dict[str, Any]) -> None:
    print(f"source-memory reconciliation: {report['verdict']}")
    for source in SOURCES:
        value = report["sources"][source]
        counts = " ".join(
            f"{key}={count}" for key, count in sorted(value["counts"].items())
        )
        print(
            f"{source}: canonical={value['canonical_records']} notes={value['admission_notes']} {counts}"
        )
    summary = report["summary"]
    print(
        "summary: "
        f"eligible_unadmitted_or_stale={summary['eligible_unadmitted_or_stale']} "
        f"incomplete_projections={summary['incomplete_projections']} "
        f"phase2_lag={summary['phase2_lag']}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only source-memory reconciliation"
    )
    parser.add_argument("--repo", default=".")
    parser.add_argument("--codex-home")
    parser.add_argument("--eligibility")
    parser.add_argument("--ledger-bin")
    parser.add_argument("--memory-note-bin")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = reconcile(args)
    except ReconcileError as exc:
        print(
            json.dumps(
                {
                    "source_memory_reconciliation": {
                        "verdict": "blocked",
                        "error": str(exc),
                        "read_only": True,
                        "authority_granted": False,
                        "storage_mutated": False,
                    }
                },
                indent=2,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    if args.format == "text":
        print_text(report)
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
