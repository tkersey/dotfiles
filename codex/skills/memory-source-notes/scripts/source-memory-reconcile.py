#!/usr/bin/env -S uv run python
"""Read-only reconciliation of canonical source records and memory admissions."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from memory_layout import LayoutError, MemoryLayout, compiled_documents, resolve_layout
from negative_ledger_memory_note import AdapterError, resolve_custody
from memory_source_layout import instruction_status

SOURCES = ("learnings", "synesthesia", "negative-ledger")
LEDGER_ABI = "ledger-artifact-abi/v1"
DEFAULT_LIMIT = 10_000
MAX_LIMIT = 100_000
SKILLS_ROOT = Path(__file__).resolve().parents[2]
ELIGIBILITY_DEFINITION = (
    SKILLS_ROOT
    / "memory-source-notes/definitions/ledger/source-memory-eligibility.json"
)
SOURCE_DEFINITIONS = {
    "learnings": SKILLS_ROOT
    / "learnings/definitions/ledger/learnings-protocol.json",
    "negative-ledger": SKILLS_ROOT
    / "negative-ledger/definitions/ledger/negative-evidence-protocol.json",
    "synesthesia": SKILLS_ROOT
    / "synesthesia/definitions/ledger/synesthesia-protocol.json",
}
SOURCE_DEFINITION_IDS = {
    "learnings": "learnings/protocol",
    "negative-ledger": "negative-ledger/negative-evidence-protocol",
    "synesthesia": "synesthesia/protocol",
}
MEMORY_NOTE_PROJECTIONS = {source: "memory-note" for source in SOURCES}
TOKEN_CHARS = r"A-Za-z0-9_-"


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
    if proc.returncode:
        detail = (
            proc.stderr.decode("utf-8", errors="replace").strip()
            or proc.stdout.decode("utf-8", errors="replace").strip()
        )
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


def ledger_envelope(
    value: Any, *, schema: str, definition_id: str, stage: str
) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("schema") != schema:
        raise ReconcileError(f"{stage}: invalid result schema")
    definition = value.get("definition")
    if (
        not isinstance(definition, dict)
        or definition.get("id") != definition_id
        or definition.get("abi") != LEDGER_ABI
    ):
        raise ReconcileError(f"{stage}: definition identity mismatch")
    if value.get("authority_granted") is not False:
        raise ReconcileError(f"{stage}: authority boundary violated")
    if value.get("storage_mutated") is not False:
        raise ReconcileError(f"{stage}: unexpected storage mutation")
    return value


def ledger_validation(value: Any, *, definition_id: str, stage: str) -> None:
    result = ledger_envelope(
        value,
        schema="ledger-validation-result/v1",
        definition_id=definition_id,
        stage=stage,
    )
    if result.get("valid") is not True or result.get("errors") != []:
        raise ReconcileError(f"{stage}: structurally invalid")


def ledger_doctor(value: Any, *, definition_id: str, stage: str) -> dict[str, Any]:
    result = ledger_envelope(
        value,
        schema="ledger-doctor-result/v1",
        definition_id=definition_id,
        stage=stage,
    )
    if result.get("healthy") is not True:
        raise ReconcileError(f"{stage}: unhealthy store")
    return result


def memory_note_result(value: Any, *, command: str, stage: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReconcileError(f"{stage}: expected object result")
    if command == "doctor" and (
        value.get("command") != "doctor" or value.get("issues") != 0
    ):
        raise ReconcileError(f"{stage}: unhealthy memory-note store")
    return value


def writer_fingerprint(extension: str, kind: str, raw: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(extension.encode())
    digest.update(b"\n")
    digest.update(kind.encode())
    digest.update(b"\n")
    digest.update(raw)
    return digest.hexdigest()


def load_eligibility(
    path: str | None, *, ledger: str, cwd: Path
) -> dict[str, dict[str, dict[str, str]]]:
    result = {source: {} for source in SOURCES}
    if not path:
        return result
    eligibility_path = Path(path).expanduser().resolve()
    ledger_validation(
        run_json(
            [
                ledger,
                "validate",
                "--definition",
                str(ELIGIBILITY_DEFINITION),
                "--input",
                f"eligibility={eligibility_path}",
                "--format",
                "json",
            ],
            cwd=cwd,
        ),
        definition_id="memory-source-notes/source-memory-eligibility",
        stage="ledger eligibility validation",
    )
    try:
        value = json.loads(eligibility_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReconcileError(f"eligibility: {exc}") from exc
    decisions = value.get("decisions")
    if not isinstance(decisions, dict):
        raise ReconcileError("eligibility: decisions object missing")
    for source, rows in decisions.items():
        if source not in result or not isinstance(rows, dict):
            raise ReconcileError(f"eligibility: invalid source {source!r}")
        for record_id, decision in rows.items():
            disposition = decision.get("disposition") if isinstance(decision, dict) else None
            reason = decision.get("reason") if isinstance(decision, dict) else None
            if (
                not isinstance(record_id, str)
                or disposition not in ("eligible", "not-eligible")
                or not isinstance(reason, str)
                or not reason.strip()
            ):
                raise ReconcileError(f"eligibility {source}: invalid decision")
            result[source][record_id] = {
                "disposition": disposition,
                "reason": reason.strip(),
            }
    return result


def list_is_complete(row: Any, source: str) -> bool:
    return bool(
        isinstance(row, dict)
        and isinstance(row.get("id"), str)
        and row.get("extension") == source
        and isinstance(row.get("kind"), str)
        and isinstance(row.get("fingerprint"), str)
        and isinstance(row.get("payload"), dict)
    )


def inventory_is_truncated(listing: dict[str, Any], returned: int, limit: int) -> bool:
    total = listing.get("total")
    if isinstance(total, int):
        return total > returned
    truncated = listing.get("truncated")
    if isinstance(truncated, bool):
        return truncated
    return returned >= limit


def load_notes(
    memory_note: str,
    source: str,
    *,
    cwd: Path,
    layout: MemoryLayout,
    limit: int,
) -> tuple[list[dict[str, Any]], int]:
    argv = [
        memory_note,
        "list",
        "--extension",
        source,
        "--limit",
        str(limit),
        "--format",
        "json",
        *layout.writer_args(),
    ]
    listing = memory_note_result(
        run_json(argv, cwd=cwd), command="list", stage=f"memory-note list {source}"
    )
    rows = listing.get("notes")
    if listing.get("extension") != source or not isinstance(rows, list):
        raise ReconcileError(f"memory-note list {source}: invalid result")
    if inventory_is_truncated(listing, len(rows), limit):
        raise ReconcileError(f"memory-note list {source}: inventory reached limit {limit}")

    notes: list[dict[str, Any]] = []
    show_count = 0
    for row in rows:
        if list_is_complete(row, source):
            notes.append(row)
            continue
        note_id = row.get("id") if isinstance(row, dict) else None
        if not isinstance(note_id, str):
            raise ReconcileError(f"memory-note list {source}: note id missing")
        show = [
            memory_note,
            "show",
            "--extension",
            source,
            "--id",
            note_id,
            "--format",
            "json",
            *layout.writer_args(),
        ]
        note = memory_note_result(
            run_json(show, cwd=cwd),
            command="show",
            stage=f"memory-note show {note_id}",
        )
        if note.get("id") != note_id or note.get("extension") != source:
            raise ReconcileError(f"memory-note show {note_id}: invalid result")
        notes.append(note)
        show_count += 1
    return notes, show_count


def load_compiled_corpus(layout: MemoryLayout) -> tuple[list[str], list[str]]:
    documents, unavailable = compiled_documents(layout)
    return list(documents.values()), unavailable


def contains_token(corpus: list[str], value: str | None) -> bool:
    if not value:
        return False
    pattern = re.compile(
        rf"(?<![{TOKEN_CHARS}]){re.escape(value)}(?![{TOKEN_CHARS}])"
    )
    return any(pattern.search(text) is not None for text in corpus)


def normalize_repository(value: str) -> str:
    candidate = value.strip().rstrip("/")
    if candidate.startswith("git@") and ":" in candidate:
        candidate = candidate.split(":", 1)[1]
    elif "://" in candidate:
        candidate = urlparse(candidate).path.lstrip("/")
    if candidate.endswith(".git"):
        candidate = candidate[:-4]
    return candidate.strip("/").casefold()


def canonical_repository(cwd: Path) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if proc.returncode or not proc.stdout.strip():
        return None
    identity = normalize_repository(proc.stdout)
    parts = [part for part in identity.split("/") if part]
    return "/".join(parts) if len(parts) == 2 else None


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


def note_binding(note: dict[str, Any]) -> tuple[str, str | None]:
    identity = note_repository(note)
    if identity is not None:
        return "repository", identity
    scope = note.get("scope")
    if (
        isinstance(scope, dict)
        and scope.get("kind") == "global"
        and scope.get("repo") is None
    ):
        return "global", None
    return "unscoped", None


def partition_notes(
    notes: list[dict[str, Any]], repository_identity: str | None
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    local: list[dict[str, Any]] = []
    foreign: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    unscoped: list[dict[str, Any]] = []
    for note in notes:
        binding, identity = note_binding(note)
        if binding == "global":
            local.append(note)
        elif binding == "unscoped":
            unscoped.append(note)
        elif repository_identity is None:
            unresolved.append(note)
        elif identity == repository_identity:
            local.append(note)
        else:
            foreign.append(note)
    return local, foreign, unresolved, unscoped


def note_source_id(source: str, note: dict[str, Any]) -> str | None:
    if source == "synesthesia":
        refs = note.get("source_refs")
        ids = {
            ref.get("ref") for ref in refs
            if isinstance(ref, dict)
            and ref.get("kind") == "synesthesia-canonical-event"
            and isinstance(ref.get("ref"), str)
            and re.fullmatch(r"SYN-[0-9]{8}T[0-9]{6}Z-[a-f0-9]{16}", ref["ref"])
        } if isinstance(refs, list) else set()
        return next(iter(ids)) if len(ids) == 1 else None
    payload = note.get("payload")
    if not isinstance(payload, dict):
        return None
    field = {"learnings": "learning_id", "negative-ledger": "neg_id"}.get(source)
    value = payload.get(field) if field else None
    return value if isinstance(value, str) and value else None


def classify_record(
    *,
    record_id: str,
    note: dict[str, Any] | None,
    expected_fingerprint: str | None,
    export_error: str | None,
    eligibility: dict[str, str] | None,
    compiled_corpus: list[str],
    unreadable_phase2: list[str],
) -> dict[str, Any]:
    note_id = note.get("id") if note else None
    note_fingerprint = note.get("fingerprint") if note else None
    current = bool(note and expected_fingerprint == note_fingerprint)
    if note and current:
        status = "admitted"
    elif export_error:
        status = "incomplete-projection"
    elif note:
        status = "stale-note"
    elif eligibility and eligibility["disposition"] == "eligible":
        status = "eligible-unadmitted"
    elif eligibility and eligibility["disposition"] == "not-eligible":
        status = "not-eligible"
    else:
        status = "needs-source-review"

    # A bare canonical ID may collide across stores or arrive through ordinary
    # session memory. Only this immutable note's exact ID is an observed link.
    visible = contains_token(compiled_corpus, note_id if isinstance(note_id, str) else None)
    if visible:
        phase2_status = "note-id-observed"
        visible_value: bool | None = True
    elif unreadable_phase2:
        phase2_status = "unknown"
        visible_value = None
    elif status == "admitted":
        phase2_status = "not-observed"
        visible_value = False
    else:
        phase2_status = "not-applicable"
        visible_value = False

    return {
        "record_id": record_id,
        "status": status,
        "note_id": note_id,
        "note_fingerprint": note_fingerprint,
        "expected_fingerprint": expected_fingerprint,
        "export_error": export_error,
        "eligibility": eligibility,
        "compiled_note_reference": visible_value,
        "phase2_status": phase2_status,
    }


def source_records(
    ledger: str, source: str, *, cwd: Path, limit: int, native_args: list[str]
) -> list[dict[str, Any]]:
    stage = f"ledger project {source} reconciliation-index"
    envelope = ledger_envelope(
        run_json(
            [
                ledger,
                "project",
                "--definition",
                str(SOURCE_DEFINITIONS[source]),
                "--projection",
                "reconciliation-index",
                *native_args,
                "--param",
                f"limit={limit}",
                "--format",
                "json",
            ],
            cwd=cwd,
        ),
        schema="ledger-projection-result/v1",
        definition_id=SOURCE_DEFINITION_IDS[source],
        stage=stage,
    )
    if envelope.get("projection") != "reconciliation-index":
        raise ReconcileError(f"{stage}: projection identity mismatch")
    records = envelope.get("data")
    if not isinstance(records, list):
        raise ReconcileError(f"{stage}: expected array payload")
    if len(records) >= limit:
        raise ReconcileError(f"{stage}: inventory reached limit {limit}")
    return records


def native_export(
    ledger: str, source: str, record_id: str, *, cwd: Path, native_args: list[str]
) -> tuple[bytes | None, str | None]:
    stage = f"ledger project {source} {record_id}"
    argv = [
        ledger,
        "project",
        "--definition",
        str(SOURCE_DEFINITIONS[source]),
        "--projection",
        MEMORY_NOTE_PROJECTIONS[source],
        *native_args,
        "--param",
        f"id={record_id}",
        "--payload-only",
        "--format",
        "json",
    ]
    try:
        raw = run_bytes(argv, cwd=cwd)
        payload = parse_json(raw, stage)
        if not isinstance(payload, dict):
            raise ReconcileError(f"{stage}: expected object payload")
        note_payload = payload.get("payload")
        key = {"learnings": "learning_id", "negative-ledger": "neg_id"}.get(source)
        if key and (not isinstance(note_payload, dict) or note_payload.get(key) != record_id):
            raise ReconcileError(f"{stage}: canonical record identity mismatch")
        # Admission fingerprints cover exact native bytes, including formatting.
        return raw, None
    except ReconcileError as exc:
        return None, str(exc)


def canonical_record_id(source: str, record: dict[str, Any]) -> str:
    field = {"learnings": "id", "synesthesia": "syn_id", "negative-ledger": "neg_id"}[source]
    value = record.get(field)
    if not isinstance(value, str) or not value:
        raise ReconcileError(f"{source} reconciliation-index: canonical id missing")
    return value


def validate_eligibility_ids(
    eligibility: dict[str, dict[str, dict[str, str]]],
    records: dict[str, list[dict[str, Any]]],
) -> None:
    for source in eligibility:
        canonical = {canonical_record_id(source, row) for row in records[source]}
        unknown = sorted(set(eligibility[source]) - canonical)
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
    compiled_corpus: list[str],
    unreadable_phase2: list[str],
    synesthesia_adapter: Any,
    repository_identity: str | None,
    standalone_note_ids: set[str],
    fallback_show_count: int,
    codex_home: Path | MemoryLayout,
    native_args: list[str] | None = None,
) -> dict[str, Any]:
    local_notes, foreign_notes, unresolved_notes, unscoped_notes = partition_notes(
        notes, repository_identity
    )
    notes_by_id: dict[str, list[dict[str, Any]]] = {}
    scoped_ids = {note.get("id") for note in local_notes}
    exact_export_ids: set[str] = set()
    for note in notes:
        source_id = note_source_id(source, note)
        if source_id:
            notes_by_id.setdefault(source_id, []).append(note)
    notes_by_fingerprint = {
        note["fingerprint"]: note
        for note in notes
        if isinstance(note.get("fingerprint"), str)
    }

    resolver = None
    if source == "synesthesia" and records:
        try:
            resolver = synesthesia_adapter.AdmissionResolver(cwd, codex_home, ledger_bin=ledger)
        except Exception as exc:
            raise ReconcileError(f"synesthesia admission resolver: {exc}") from exc

    rows: list[dict[str, Any]] = []
    canonical_ids: set[str] = set()
    for record in records:
        record_id = canonical_record_id(source, record)
        canonical_ids.add(record_id)
        candidates = notes_by_id.get(record_id, [])
        logical_kind = {
            "learnings": "learning-admission",
            "negative-ledger": "ledger-projection",
        }.get(source, record.get("logical_kind") or record.get("kind"))
        if not isinstance(logical_kind, str) or not logical_kind:
            raise ReconcileError(f"{source} {record_id}: logical kind missing")

        should_export = source != "learnings" or bool(candidates) or record_id in eligibility
        raw, export_error = None, None
        if should_export and source != "synesthesia":
            if native_args is None:
                export_error = "managed source selector unavailable"
            else:
                raw, export_error = native_export(ledger, source, record_id, cwd=cwd, native_args=native_args)
        expected = None
        scoped_candidates = [candidate for candidate in candidates if candidate.get("id") in scoped_ids]
        note = scoped_candidates[0] if scoped_candidates else None
        if source == "synesthesia":
            try:
                prepared = resolver.prepare(record_id)
                expected = prepared["writer_fingerprint"]
                note = notes_by_fingerprint.get(expected)
                if note and isinstance(note.get("id"), str):
                    exact_export_ids.add(note["id"])
            except Exception as exc:
                export_error = f"synesthesia adapter: {exc}"
        elif raw is not None:
            for candidate in candidates:
                kind = candidate.get("kind")
                if not isinstance(kind, str):
                    continue
                candidate_expected = writer_fingerprint(source, kind, raw)
                if candidate.get("fingerprint") == candidate_expected:
                    note, expected = candidate, candidate_expected
                    if isinstance(candidate.get("id"), str):
                        exact_export_ids.add(candidate["id"])
            if expected is None:
                kind = note.get("kind") if note else logical_kind
                if isinstance(kind, str):
                    expected = writer_fingerprint(source, kind, raw)

        row = classify_record(
                record_id=record_id,
                note=note,
                expected_fingerprint=expected,
                export_error=export_error,
                eligibility=eligibility.get(record_id),
                compiled_corpus=compiled_corpus,
                unreadable_phase2=unreadable_phase2,
            )
        row["scope_binding"] = "canonical-export" if note and note.get("id") in exact_export_ids else "declared-scope"
        rows.append(row)

    # Old immutable snapshots retain their historical scope. Exact native export
    # bytes can establish correspondence without inventing a repository alias.
    local_notes = [note for note in notes if note.get("id") in scoped_ids | exact_export_ids]
    foreign_notes = [note for note in foreign_notes if note.get("id") not in exact_export_ids]
    unresolved_notes = [note for note in unresolved_notes if note.get("id") not in exact_export_ids]
    unscoped_notes = [note for note in unscoped_notes if note.get("id") not in exact_export_ids]

    expected_fingerprints = {
        row["expected_fingerprint"] for row in rows if row["expected_fingerprint"]
    }
    orphans: list[str] = []
    for note in local_notes:
        note_id = note.get("id")
        if not isinstance(note_id, str) or note_id in standalone_note_ids:
            continue
        if source == "synesthesia":
            orphaned = note.get("fingerprint") not in expected_fingerprints
        else:
            orphaned = note_source_id(source, note) not in canonical_ids
        if orphaned:
            orphans.append(note_id)

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    counts["phase2-not-observed"] = sum(row["phase2_status"] == "not-observed" for row in rows)
    counts["phase2-unknown"] = sum(
        row["phase2_status"] == "unknown" for row in rows
    )
    return {
        "canonical_records": len(rows),
        "admission_notes": len(local_notes),
        "counts": counts,
        "records": rows,
        "orphan_note_ids": sorted(orphans),
        "standalone_compatible_note_ids": sorted(standalone_note_ids),
        "foreign_repo_note_ids": sorted(
            note["id"] for note in foreign_notes if isinstance(note.get("id"), str)
        ),
        "unresolved_repo_note_ids": sorted(
            note["id"] for note in unresolved_notes if isinstance(note.get("id"), str)
        ),
        "unscoped_note_ids": sorted(
            note["id"] for note in unscoped_notes if isinstance(note.get("id"), str)
        ),
        "fallback_show_count": fallback_show_count,
        "exact_export_note_ids": sorted(exact_export_ids),
    }


def reconcile(args: argparse.Namespace) -> dict[str, Any]:
    cwd = Path(args.repo or ".").expanduser().absolute()
    if not cwd.is_dir():
        raise ReconcileError(f"repo: not a directory: {cwd}")
    if not 1 <= args.limit <= MAX_LIMIT:
        raise ReconcileError(f"limit: must be between 1 and {MAX_LIMIT}")
    selected_sources = list(dict.fromkeys(getattr(args, "source", None) or SOURCES))
    ledger = resolve_binary(args.ledger_bin, "LEDGER_BIN", "ledger")
    eligibility = load_eligibility(args.eligibility, ledger=ledger, cwd=cwd)
    memory_note, writer_error = None, None
    try:
        memory_note = resolve_binary(args.memory_note_bin, "MEMORY_NOTE_BIN", "memory-note")
    except ReconcileError as exc:
        writer_error = str(exc)

    managed_context, managed_error = None, None
    if any(source != "synesthesia" for source in selected_sources):
        try:
            managed_context = resolve_custody(cwd, getattr(args, "store_id", None))
        except (AdapterError, OSError) as exc:
            managed_error = str(exc)

    pinned_home, pinned_version = args.codex_home, getattr(args, "memory_version", None)
    sources: dict[str, Any] = {}
    for source in selected_sources:
        result: dict[str, Any] = {
            "canonical_records": None, "admission_notes": None,
            "records": [], "counts": {}, "diagnostics": [],
            "orphan_note_ids": [], "foreign_repo_note_ids": [],
            "unresolved_repo_note_ids": [], "unscoped_note_ids": [],
        }
        records, notes, layout = None, None, None
        native_args, repository_identity = None, None
        stage = "canonical-context"
        try:
            if source == "synesthesia":
                native_args = ["--repo", str(cwd)]
                repository_identity = canonical_repository(cwd)
                result["storage_context"] = {"mode": "explicit-unmanaged", "root": str(cwd)}
            else:
                if managed_error or managed_context is None:
                    raise ReconcileError(managed_error or "managed context unavailable")
                native_args = managed_context["native_args"]
                repository_identity = managed_context["repository_id"]
                result["storage_context"] = managed_context
            stage = "canonical-doctor"
            result["canonical_doctor"] = ledger_doctor(
                run_json([ledger, "doctor", "--definition", str(SOURCE_DEFINITIONS[source]),
                          *native_args, "--format", "json"], cwd=cwd),
                definition_id=SOURCE_DEFINITION_IDS[source], stage=f"ledger doctor {source}",
            )
            stage = "canonical-records"
            records = source_records(ledger, source, cwd=cwd, limit=args.limit, native_args=native_args)
            result["canonical_records"] = len(records)
            result["repository_identity"] = repository_identity
            stage = "canonical-eligibility"
            validate_eligibility_ids({source: eligibility[source]}, {source: records})
        except (ReconcileError, OSError) as exc:
            records = None
            result["diagnostics"].append({"stage": stage, "error": str(exc)})

        stage = "memory-layout"
        try:
            if writer_error or memory_note is None:
                raise ReconcileError(writer_error or "memory-note unavailable")
            layout = resolve_layout(source, codex_home=pinned_home, memory_version=pinned_version,
                                    memory_note_bin=memory_note, cwd=cwd)
            pinned_home, pinned_version = layout.codex_home, layout.memory_version
            result["memory_layout"] = layout.as_dict()
            compiled_corpus, unreadable_phase2 = load_compiled_corpus(layout)
            result["compiled_memory"] = {
                "readable_documents": len(compiled_corpus),
                "unavailable_paths": unreadable_phase2,
            }
            stage = "memory-note-doctor"
            result["memory_note_doctor"] = memory_note_result(
                run_json([memory_note, "doctor", "--extension", source, *layout.writer_args(),
                          "--format", "json"], cwd=cwd),
                command="doctor", stage=f"memory-note doctor {source}",
            )
            stage = "memory-note-inventory"
            notes, show_count = load_notes(memory_note, source, cwd=cwd, layout=layout, limit=args.limit)
            result["inventory_notes"] = len(notes)
            result["extension_instructions"] = instruction_status(
                layout, SKILLS_ROOT.parent / "memories/extensions" / source / "instructions.md"
            )
            if result["extension_instructions"]["status"] != "current":
                result["diagnostics"].append({
                    "stage": "extension-instructions",
                    "error": result["extension_instructions"]["status"],
                })
        except (ReconcileError, LayoutError, OSError) as exc:
            result["diagnostics"].append({"stage": stage, "error": str(exc)})

        if records is not None and notes is not None and layout is not None:
            try:
                adapter, standalone = None, set()
                if source == "synesthesia":
                    adapter = load_synesthesia_adapter(
                        SKILLS_ROOT / "memory-source-notes/scripts/synesthesia_memory_note.py"
                    )
                    stored, invalid, _, _ = adapter.load_stored_notes(layout, ledger_bin=ledger)
                    if invalid:
                        raise ReconcileError("synesthesia stored-note validation failed")
                    if {note.get("id") for note in notes} != {note.id for note in stored}:
                        raise ReconcileError("synesthesia note inventory mismatch")
                    standalone = {note.id for note in stored if note.validation_profile == "stored-legacy-corridor-v1"}
                result.update(source_report(
                    source, records, notes, ledger=ledger, cwd=cwd, eligibility=eligibility[source],
                    compiled_corpus=compiled_corpus, unreadable_phase2=unreadable_phase2,
                    synesthesia_adapter=adapter, repository_identity=repository_identity,
                    standalone_note_ids=standalone, fallback_show_count=show_count,
                    codex_home=layout, native_args=native_args,
                ))
            except (ReconcileError, LayoutError, OSError, ValueError) as exc:
                result["diagnostics"].append({"stage": "reconciliation", "error": str(exc)})
        sources[source] = result

    def count(name: str) -> int:
        return sum(source["counts"].get(name, 0) for source in sources.values())

    diagnostics = sum(len(source["diagnostics"]) for source in sources.values())
    gaps = count("eligible-unadmitted") + count("stale-note")
    unresolved = sum(len(source["unresolved_repo_note_ids"]) + len(source["unscoped_note_ids"])
                     for source in sources.values())
    incomplete = diagnostics + count("incomplete-projection") + count("phase2-unknown") + unresolved
    return {
        "schema": "source-memory-reconciliation/v3",
        "verdict": "incomplete" if incomplete else "gaps" if gaps else "ok",
        "read_only": True, "authority_granted": False, "storage_mutated": False,
        "repo": str(cwd), "store_id": getattr(args, "store_id", None),
        "codex_home": str(pinned_home) if pinned_home else None,
        "memory_version": pinned_version, "limit": args.limit, "sources": sources,
        "summary": {
            "eligible_unadmitted_or_stale": gaps,
            "incomplete_projections": count("incomplete-projection"),
            "phase2_not_observed": count("phase2-not-observed"),
            "phase2_unknown": count("phase2-unknown"),
            "unresolved_scope_notes": unresolved,
            "diagnostic_errors": diagnostics,
        },
    }


def print_text(report: dict[str, Any]) -> None:
    print(f"source-memory reconciliation/v3: {report['verdict']}")
    for source, value in report["sources"].items():
        counts = " ".join(f"{key}={count}" for key, count in sorted(value["counts"].items()))
        print(f"{source}: canonical={value['canonical_records']} notes={value['admission_notes']} {counts}")
        for diagnostic in value["diagnostics"]:
            print(f"  {diagnostic['stage']}: {diagnostic['error']}")
        for key in ("unresolved_repo_note_ids", "unscoped_note_ids"):
            if value[key]:
                print(f"  {key}: " + ", ".join(value[key]))
    print("summary: " + " ".join(f"{key}={value}" for key, value in report["summary"].items()))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only source-memory reconciliation")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--store-id", help="Registered personal store; no workspace or Git required")
    parser.add_argument("--source", action="append", choices=SOURCES)
    parser.add_argument("--codex-home")
    parser.add_argument("--memory-version", choices=("v1", "v2"))
    parser.add_argument("--eligibility")
    parser.add_argument("--ledger-bin")
    parser.add_argument("--memory-note-bin")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
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
                        "schema": "source-memory-reconciliation/v3",
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
