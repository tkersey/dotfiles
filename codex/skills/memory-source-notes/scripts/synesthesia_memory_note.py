#!/usr/bin/env -S uv run python
"""Validate, persist, synchronize, and diagnose Synesthesia memory-source notes.

This adapter deliberately keeps the live memory extension instruction file as a
regular copy. It never creates or follows a symlink in the live extension path.
"""

from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Iterable

NOTE_ID_RE = re.compile(r"^MSN-[0-9]{8}T[0-9]{6}Z-[a-f0-9]{16}$")
ALLOWED_SCOPE_KINDS = {"global", "repo", "path-family", "task-family", "workflow", "tool"}
SENSITIVE_KEYS = {
    "password",
    "passwd",
    "secret",
    "api_key",
    "apikey",
    "access_token",
    "refresh_token",
    "private_key",
    "client_secret",
}

LOGICAL_TO_PHYSICAL_KIND = {
    "mapping-endorsement": "mapping-endorsement",
    "mapping-confirmation": "mapping-endorsement",
    "mapping-correction": "mapping-correction",
    "mapping-rejection": "mapping-rejection",
    "activation-boundary": "activation-boundary",
    "boundary-retraction": "boundary-retraction",
}

ALLOWED_OPERATIONS = {
    "mapping-endorsement": {"assert", "confirm", "reopen"},
    "mapping-confirmation": {"confirm"},
    "mapping-correction": {"supersede"},
    "mapping-rejection": {"reject"},
    "activation-boundary": {"assert", "confirm", "supersede", "reopen"},
    "boundary-retraction": {"retract"},
}

ALLOWED_AUTHORITIES = {
    "mapping-endorsement": {"explicit-user-endorsement", "repeated-accepted-use"},
    "mapping-confirmation": {"explicit-user-endorsement", "repeated-accepted-use"},
    "mapping-correction": {"explicit-user-correction"},
    "mapping-rejection": {"explicit-user-rejection"},
    "activation-boundary": {
        "explicit-user-endorsement",
        "explicit-user-correction",
        "repeated-accepted-use",
    },
    "boundary-retraction": {"explicit-user-correction", "explicit-user-rejection"},
}

PRIOR_RELATION_OPERATIONS = {"confirm", "supersede", "reject", "retract", "reopen"}

COMPAT_SCOPE = {
    "global": "global_default",
    "repo": "repo_scoped",
    "path-family": "path_family_scoped",
    "task-family": "task_family_scoped",
    "workflow": "workflow_scoped",
    "tool": "tool_scoped",
}


class ValidationError(ValueError):
    """A deterministic validation failure suitable for user-facing reporting."""


def _nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field}: expected non-empty string")
    return value.strip()


def _require_strings(mapping: dict[str, Any], fields: Iterable[str], prefix: str) -> None:
    for field in fields:
        _nonempty_string(mapping.get(field), f"{prefix}.{field}")


def _validate_note_id(value: Any, field: str) -> str:
    text = _nonempty_string(value, field)
    if not NOTE_ID_RE.match(text):
        raise ValidationError(f"{field}: invalid memory-source note id")
    return text


def _reject_sensitive_keys(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in SENSITIVE_KEYS:
                raise ValidationError(f"{path}.{key}: sensitive key is not allowed")
            _reject_sensitive_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_sensitive_keys(child, f"{path}[{index}]")


def _validate_scope(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError("scope: expected object")
    extra = set(value) - {"kind", "repo", "paths"}
    if extra:
        raise ValidationError(f"scope: unexpected fields: {', '.join(sorted(extra))}")
    kind = _nonempty_string(value.get("kind"), "scope.kind")
    if kind not in ALLOWED_SCOPE_KINDS:
        raise ValidationError(f"scope.kind: unsupported value {kind!r}")
    repo = value.get("repo")
    if repo is not None and not isinstance(repo, str):
        raise ValidationError("scope.repo: expected string or null")
    paths = value.get("paths")
    if not isinstance(paths, list) or any(not isinstance(item, str) or not item for item in paths):
        raise ValidationError("scope.paths: expected list of non-empty strings")
    if kind in {"repo", "path-family"} and not repo:
        raise ValidationError(f"scope.repo: required for {kind}")
    if kind == "path-family" and not paths:
        raise ValidationError("scope.paths: required for path-family")
    return {"kind": kind, "repo": repo, "paths": list(paths)}


def _validate_source_refs(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise ValidationError("source_refs: expected at least one source reference")
    refs: list[dict[str, str]] = []
    for index, row in enumerate(value):
        if not isinstance(row, dict):
            raise ValidationError(f"source_refs[{index}]: expected object")
        extra = set(row) - {"kind", "ref", "summary"}
        if extra:
            raise ValidationError(
                f"source_refs[{index}]: unexpected fields: {', '.join(sorted(extra))}"
            )
        refs.append(
            {
                "kind": _nonempty_string(row.get("kind"), f"source_refs[{index}].kind"),
                "ref": _nonempty_string(row.get("ref"), f"source_refs[{index}].ref"),
                "summary": _nonempty_string(
                    row.get("summary"), f"source_refs[{index}].summary"
                ),
            }
        )
    return refs


def _validate_relationships(data: dict[str, Any], operation: str) -> tuple[list[str], str | None]:
    related_raw = data.get("related_ids", [])
    if not isinstance(related_raw, list):
        raise ValidationError("related_ids: expected list")
    related_ids = [_validate_note_id(value, "related_ids[]") for value in related_raw]
    if len(set(related_ids)) != len(related_ids):
        raise ValidationError("related_ids: duplicate note id")

    supersedes_raw = data.get("supersedes_id")
    supersedes_id = None
    if supersedes_raw is not None:
        supersedes_id = _validate_note_id(supersedes_raw, "supersedes_id")

    if operation in PRIOR_RELATION_OPERATIONS and not related_ids and supersedes_id is None:
        raise ValidationError(f"operation {operation!r} requires a prior note relationship")
    if operation == "confirm" and not related_ids:
        raise ValidationError("confirmation requires the prior note in related_ids")
    return related_ids, supersedes_id


def _compat_scope_anchor(scope: dict[str, Any]) -> str:
    if scope["paths"]:
        return scope["paths"][0]
    if scope["repo"]:
        return str(scope["repo"])
    return str(scope["kind"])


def _set_compat_field(payload: dict[str, Any], field: str, expected: str) -> None:
    current = payload.get(field)
    if current is not None and current != expected:
        raise ValidationError(
            f"payload.{field}: conflicts with canonical envelope value {expected!r}"
        )
    payload[field] = expected


def validate_and_normalize(logical_kind: str, raw: Any) -> tuple[str, dict[str, Any]]:
    """Validate a skill-facing payload and return physical kind plus normalized input."""
    if logical_kind not in LOGICAL_TO_PHYSICAL_KIND:
        raise ValidationError(f"kind: unsupported Synesthesia kind {logical_kind!r}")
    if not isinstance(raw, dict):
        raise ValidationError("input: expected JSON object")
    data = copy.deepcopy(raw)

    allowed_top = {
        "operation",
        "authority",
        "summary",
        "scope",
        "source_refs",
        "related_ids",
        "supersedes_id",
        "slug",
        "payload",
    }
    extra = set(data) - allowed_top
    if extra:
        raise ValidationError(f"input: unexpected fields: {', '.join(sorted(extra))}")

    operation = _nonempty_string(data.get("operation"), "operation")
    if operation not in ALLOWED_OPERATIONS[logical_kind]:
        allowed = ", ".join(sorted(ALLOWED_OPERATIONS[logical_kind]))
        raise ValidationError(
            f"operation: {operation!r} is invalid for {logical_kind}; expected {allowed}"
        )

    authority = _nonempty_string(data.get("authority"), "authority")
    if authority not in ALLOWED_AUTHORITIES[logical_kind]:
        allowed = ", ".join(sorted(ALLOWED_AUTHORITIES[logical_kind]))
        raise ValidationError(
            f"authority: {authority!r} is invalid for {logical_kind}; expected {allowed}"
        )

    summary = _nonempty_string(data.get("summary"), "summary")
    scope = _validate_scope(data.get("scope"))
    source_refs = _validate_source_refs(data.get("source_refs"))
    related_ids, supersedes_id = _validate_relationships(data, operation)

    payload_raw = data.get("payload")
    if not isinstance(payload_raw, dict) or not payload_raw:
        raise ValidationError("payload: expected non-empty object")
    payload = copy.deepcopy(payload_raw)

    if logical_kind in {"mapping-endorsement", "mapping-confirmation", "mapping-correction"}:
        _require_strings(
            payload,
            (
                "sensory_phrase",
                "engineering_translation",
                "activation_boundary",
                "non_activation_boundary",
                "verification",
            ),
            "payload",
        )
    elif logical_kind == "mapping-rejection":
        _require_strings(
            payload,
            (
                "sensory_phrase",
                "activation_boundary",
                "non_activation_boundary",
                "rejection_reason",
                "verification",
            ),
            "payload",
        )
        if payload.get("engineering_translation") not in (None, ""):
            _nonempty_string(payload.get("engineering_translation"), "payload.engineering_translation")
    elif logical_kind == "activation-boundary":
        _require_strings(
            payload,
            ("activation_boundary", "non_activation_boundary", "verification"),
            "payload",
        )
    elif logical_kind == "boundary-retraction":
        _require_strings(
            payload,
            ("retracted_boundary", "reason", "verification"),
            "payload",
        )

    _set_compat_field(payload, "scope", COMPAT_SCOPE[scope["kind"]])
    _set_compat_field(payload, "scope_anchor", _compat_scope_anchor(scope))
    _set_compat_field(payload, "endorsement_type", authority)

    normalized: dict[str, Any] = {
        "operation": operation,
        "authority": authority,
        "summary": summary,
        "scope": scope,
        "source_refs": source_refs,
        "related_ids": related_ids,
        "supersedes_id": supersedes_id,
        "payload": payload,
    }
    slug = data.get("slug")
    if slug is not None:
        slug_text = _nonempty_string(slug, "slug")
        if not re.match(r"^[a-z0-9][a-z0-9-]{0,79}$", slug_text):
            raise ValidationError("slug: invalid slug")
        normalized["slug"] = slug_text

    _reject_sensitive_keys(normalized)
    return LOGICAL_TO_PHYSICAL_KIND[logical_kind], normalized


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def canonical_fingerprint(physical_kind: str, normalized: dict[str, Any]) -> str:
    digest = hashlib.sha256()
    digest.update(b"synesthesia\n")
    digest.update(physical_kind.encode("utf-8"))
    digest.update(b"\n")
    digest.update(canonical_json_bytes(normalized))
    return digest.hexdigest()


def read_json_input(path: str) -> Any:
    if path == "-":
        text = sys.stdin.read()
    else:
        text = Path(path).read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"json: {exc}") from exc


def find_memory_note_binary() -> Path | None:
    override = os.environ.get("MEMORY_NOTE_BIN")
    if override:
        path = Path(override).expanduser()
        if path.is_file() and os.access(path, os.X_OK):
            return path
    discovered = shutil.which("memory-note")
    if discovered:
        return Path(discovered)
    candidates: list[Path] = []
    skills_repo = os.environ.get("SKILLS_ZIG_REPO")
    if skills_repo:
        candidates.append(Path(skills_repo).expanduser() / "zig-out/bin/memory-note")
    candidates.append(Path.home() / "workspace/tk/skills-zig/zig-out/bin/memory-note")
    for path in candidates:
        if path.is_file() and os.access(path, os.X_OK):
            return path
    return None


def codex_home(override: str | None = None) -> Path:
    if override:
        return Path(override).expanduser().resolve()
    env = os.environ.get("CODEX_HOME")
    if env:
        return Path(env).expanduser().resolve()
    return (Path.home() / ".codex").resolve()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def source_instructions_path() -> Path:
    return repo_root() / "codex/memories/extensions/synesthesia/instructions.md"


def live_instructions_path(home: Path) -> Path:
    return home / "memories/extensions/synesthesia/instructions.md"


def _existing_components(path: Path) -> list[Path]:
    absolute = path.absolute()
    parts = absolute.parts
    if not parts:
        return []
    current = Path(parts[0])
    rows: list[Path] = []
    for part in parts[1:]:
        current = current / part
        if current.exists() or current.is_symlink():
            rows.append(current)
        else:
            break
    return rows


def ensure_no_symlink_components(path: Path) -> None:
    for component in _existing_components(path):
        if component.is_symlink():
            raise ValidationError(
                f"live memory path contains symlink component: {component}"
            )


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sync_instructions(home: Path, source: Path | None = None) -> dict[str, Any]:
    source_path = (source or source_instructions_path()).resolve()
    if not source_path.is_file():
        raise ValidationError(f"source instructions not found: {source_path}")
    destination = live_instructions_path(home)
    ensure_no_symlink_components(destination)
    if destination.is_symlink():
        raise ValidationError(f"destination is a symlink: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    ensure_no_symlink_components(destination.parent)

    source_bytes = source_path.read_bytes()
    before = destination.read_bytes() if destination.is_file() else None
    status = "current" if before == source_bytes else "copied"
    if status == "copied":
        fd, temp_name = tempfile.mkstemp(
            prefix=".synesthesia-instructions-", dir=str(destination.parent)
        )
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(source_bytes)
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(temp_name, 0o644)
            os.replace(temp_name, destination)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
    return {
        "status": status,
        "source": str(source_path),
        "destination": str(destination),
        "sha256": hashlib.sha256(source_bytes).hexdigest(),
        "symlink": destination.is_symlink(),
    }


class StoredNote:
    __slots__ = (
        "path", "id", "captured_at", "kind", "operation", "authority",
        "summary", "scope", "source_refs", "related_ids", "supersedes_id",
        "fingerprint", "payload", "file_sha256",
    )

    def __init__(
        self, *, path: Path, id: str, captured_at: str, kind: str,
        operation: str, authority: str, summary: str, scope: dict[str, Any],
        source_refs: list[dict[str, str]], related_ids: list[str],
        supersedes_id: str | None, fingerprint: str, payload: dict[str, Any],
        file_sha256: str,
    ) -> None:
        self.path = path
        self.id = id
        self.captured_at = captured_at
        self.kind = kind
        self.operation = operation
        self.authority = authority
        self.summary = summary
        self.scope = scope
        self.source_refs = source_refs
        self.related_ids = related_ids
        self.supersedes_id = supersedes_id
        self.fingerprint = fingerprint
        self.payload = payload
        self.file_sha256 = file_sha256


DIGEST_VERSION = "synesthesia-digest/v1"
DIGEST_FILENAME = "latest_synesthesia_digest.md"
PHYSICAL_ALLOWED_OPERATIONS = {
    "mapping-endorsement": {"assert", "confirm", "reopen"},
    "mapping-correction": {"supersede"},
    "mapping-rejection": {"reject"},
    "activation-boundary": {"assert", "confirm", "supersede", "reopen"},
    "boundary-retraction": {"retract"},
}
PHYSICAL_ALLOWED_AUTHORITIES = {
    "mapping-endorsement": {"explicit-user-endorsement", "repeated-accepted-use"},
    "mapping-correction": {"explicit-user-correction"},
    "mapping-rejection": {"explicit-user-rejection"},
    "activation-boundary": {
        "explicit-user-endorsement",
        "explicit-user-correction",
        "repeated-accepted-use",
    },
    "boundary-retraction": {"explicit-user-correction", "explicit-user-rejection"},
}
SCOPE_SPECIFICITY = {
    "path-family": 6,
    "repo": 5,
    "task-family": 4,
    "workflow": 3,
    "tool": 3,
    "global": 1,
}


def _parse_iso_datetime(value: Any, field: str) -> str:
    text = _nonempty_string(value, field)
    try:
        datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError(f"{field}: invalid ISO-8601 timestamp") from exc
    return text


def _validate_stored_payload(kind: str, payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict) or not payload:
        raise ValidationError("payload: expected non-empty object")
    value = copy.deepcopy(payload)
    if kind in {"mapping-endorsement", "mapping-correction"}:
        _require_strings(
            value,
            (
                "sensory_phrase",
                "engineering_translation",
                "activation_boundary",
                "non_activation_boundary",
                "verification",
            ),
            "payload",
        )
    elif kind == "mapping-rejection":
        _require_strings(
            value,
            (
                "sensory_phrase",
                "activation_boundary",
                "non_activation_boundary",
                "rejection_reason",
                "verification",
            ),
            "payload",
        )
    elif kind == "activation-boundary":
        _require_strings(
            value,
            ("activation_boundary", "non_activation_boundary", "verification"),
            "payload",
        )
    elif kind == "boundary-retraction":
        _require_strings(
            value,
            ("retracted_boundary", "reason", "verification"),
            "payload",
        )
    return value


def _stored_note_from_value(path: Path, value: Any, file_sha256: str) -> StoredNote:
    if not isinstance(value, dict):
        raise ValidationError("note: expected JSON object")
    if value.get("schema") != "memory-source-note/v1":
        raise ValidationError("schema: expected memory-source-note/v1")
    note_id = _validate_note_id(value.get("id"), "id")
    captured_at = _parse_iso_datetime(value.get("captured_at"), "captured_at")
    if value.get("extension") != "synesthesia":
        raise ValidationError("extension: expected synesthesia")
    kind = _nonempty_string(value.get("kind"), "kind")
    if kind not in PHYSICAL_ALLOWED_OPERATIONS:
        raise ValidationError(f"kind: unsupported stored kind {kind!r}")
    operation = _nonempty_string(value.get("operation"), "operation")
    if operation not in PHYSICAL_ALLOWED_OPERATIONS[kind]:
        allowed = ", ".join(sorted(PHYSICAL_ALLOWED_OPERATIONS[kind]))
        raise ValidationError(
            f"operation: {operation!r} is invalid for stored kind {kind}; expected {allowed}"
        )
    authority = _nonempty_string(value.get("authority"), "authority")
    if authority not in PHYSICAL_ALLOWED_AUTHORITIES[kind]:
        allowed = ", ".join(sorted(PHYSICAL_ALLOWED_AUTHORITIES[kind]))
        raise ValidationError(
            f"authority: {authority!r} is invalid for stored kind {kind}; expected {allowed}"
        )
    summary = _nonempty_string(value.get("summary"), "summary")
    scope = _validate_scope(value.get("scope"))
    source_refs = _validate_source_refs(value.get("source_refs"))
    related_ids, supersedes_id = _validate_relationships(value, operation)
    fingerprint = _nonempty_string(value.get("fingerprint"), "fingerprint")
    if not re.fullmatch(r"[a-f0-9]{64}", fingerprint):
        raise ValidationError("fingerprint: expected 64 lowercase hex characters")
    payload = _validate_stored_payload(kind, value.get("payload"))
    _reject_sensitive_keys(value)
    return StoredNote(
        path=path,
        id=note_id,
        captured_at=captured_at,
        kind=kind,
        operation=operation,
        authority=authority,
        summary=summary,
        scope=scope,
        source_refs=source_refs,
        related_ids=related_ids,
        supersedes_id=supersedes_id,
        fingerprint=fingerprint,
        payload=payload,
        file_sha256=file_sha256,
    )


def parse_note(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def notes_directory(home: Path) -> Path:
    return home / "memories/extensions/synesthesia/notes"


def resources_directory(home: Path) -> Path:
    return home / "memories/extensions/synesthesia/resources"


def default_digest_path(home: Path) -> Path:
    return resources_directory(home) / DIGEST_FILENAME


def _source_manifest_fingerprint(
    notes: list[StoredNote], invalid_notes: list[dict[str, Any]]
) -> str:
    manifest: list[dict[str, Any]] = []
    for note in sorted(notes, key=lambda item: item.id):
        manifest.append(
            {
                "id": note.id,
                "fingerprint": note.fingerprint,
                "kind": note.kind,
                "operation": note.operation,
                "file_sha256": note.file_sha256,
            }
        )
    for row in sorted(invalid_notes, key=lambda item: str(item.get("path", ""))):
        manifest.append(
            {
                "invalid_path": row.get("path"),
                "file_sha256": row.get("file_sha256"),
                "error": row.get("error"),
            }
        )
    return hashlib.sha256(canonical_json_bytes(manifest)).hexdigest()


def load_stored_notes(
    home: Path,
) -> tuple[list[StoredNote], list[dict[str, Any]], str, int]:
    directory = notes_directory(home)
    if directory.is_symlink():
        raise ValidationError(f"notes directory is a symlink: {directory}")
    ensure_no_symlink_components(directory)
    if not directory.exists():
        empty = hashlib.sha256(canonical_json_bytes([])).hexdigest()
        return [], [], empty, 0
    if not directory.is_dir():
        raise ValidationError(f"notes path is not a directory: {directory}")

    notes: list[StoredNote] = []
    invalid: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    paths = sorted(directory.glob("*.md"), key=lambda item: item.name)
    for path in paths:
        if path.is_symlink():
            invalid.append(
                {
                    "path": str(path),
                    "file_sha256": None,
                    "error": "source note is a symlink",
                }
            )
            continue
        if not path.is_file():
            continue
        try:
            raw = path.read_bytes()
            file_sha256 = hashlib.sha256(raw).hexdigest()
            value = json.loads(raw.decode("utf-8"))
            note = _stored_note_from_value(path, value, file_sha256)
            if note.id in seen_ids:
                raise ValidationError(f"id: duplicate source note id {note.id}")
            seen_ids.add(note.id)
            notes.append(note)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValidationError) as exc:
            try:
                file_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError:
                file_sha256 = None
            invalid.append(
                {
                    "path": str(path),
                    "file_sha256": file_sha256,
                    "error": str(exc),
                }
            )
    notes.sort(key=lambda item: (item.captured_at, item.id, item.path.name))
    return notes, invalid, _source_manifest_fingerprint(notes, invalid), len(paths)


def _note_category(note: StoredNote) -> str | None:
    if note.kind in {"mapping-endorsement", "mapping-correction", "mapping-rejection"}:
        return "mapping"
    if note.kind == "activation-boundary":
        return "boundary"
    return None


def _prior_ids(note: StoredNote) -> list[str]:
    values: list[str] = []
    if note.supersedes_id:
        values.append(note.supersedes_id)
    for value in note.related_ids:
        if value not in values:
            values.append(value)
    return values


def _lineage_signature(note: StoredNote, category: str) -> tuple[str, ...]:
    scope = json.dumps(note.scope, sort_keys=True, separators=(",", ":"))
    if category == "mapping":
        fields = (
            "sensory_phrase",
            "engineering_translation",
            "activation_boundary",
            "non_activation_boundary",
            "verification",
        )
    else:
        fields = ("activation_boundary", "non_activation_boundary", "verification")
    return (scope, *(str(note.payload.get(field, "")).strip() for field in fields))


def _unresolved_event(note: StoredNote, reason: str) -> dict[str, Any]:
    return {
        "id": note.id,
        "captured_at": note.captured_at,
        "kind": note.kind,
        "operation": note.operation,
        "prior_ids": _prior_ids(note),
        "reason": reason,
        "path": str(note.path),
    }


def build_digest_projection(home: Path) -> dict[str, Any]:
    notes, invalid_notes, source_fingerprint, source_file_count = load_stored_notes(home)
    lineages: dict[str, dict[str, Any]] = {}
    note_to_lineage: dict[str, str] = {}
    unresolved: list[dict[str, Any]] = []

    for note in notes:
        category = _note_category(note)
        if note.operation == "assert":
            if category not in {"mapping", "boundary"}:
                unresolved.append(_unresolved_event(note, "assert-kind-does-not-create-lineage"))
                continue
            lineage = {
                "root_id": note.id,
                "category": category,
                "active": True,
                "state": "asserted",
                "current_note": note,
                "last_active_note": note,
                "terminal_note": None,
                "events": [note],
                "confirmation_count": 0,
            }
            lineages[note.id] = lineage
            note_to_lineage[note.id] = note.id
            continue

        prior_ids = _prior_ids(note)
        if not prior_ids:
            unresolved.append(_unresolved_event(note, "missing-prior-note-relationship"))
            continue
        missing = [value for value in prior_ids if value not in note_to_lineage]
        if missing:
            unresolved.append(
                _unresolved_event(note, f"missing-or-forward-prior-note:{','.join(missing)}")
            )
            continue
        roots = {note_to_lineage[value] for value in prior_ids}
        if len(roots) != 1:
            unresolved.append(_unresolved_event(note, "prior-notes-cross-lineages"))
            continue
        root_id = next(iter(roots))
        lineage = lineages[root_id]

        if note.operation == "confirm":
            if not lineage["active"]:
                unresolved.append(_unresolved_event(note, "cannot-confirm-inactive-lineage"))
                continue
            if category != lineage["category"]:
                unresolved.append(_unresolved_event(note, "confirmation-category-mismatch"))
                continue
            current = lineage["current_note"]
            if _lineage_signature(note, category) != _lineage_signature(current, category):
                unresolved.append(_unresolved_event(note, "confirmation-content-mismatch"))
                continue
            lineage["events"].append(note)
            lineage["confirmation_count"] += 1
            lineage["state"] = "confirmed"
            note_to_lineage[note.id] = root_id
            continue

        if note.operation == "supersede":
            if not lineage["active"]:
                unresolved.append(_unresolved_event(note, "cannot-supersede-inactive-lineage"))
                continue
            if category != lineage["category"]:
                unresolved.append(_unresolved_event(note, "supersession-category-mismatch"))
                continue
            lineage["events"].append(note)
            lineage["current_note"] = note
            lineage["last_active_note"] = note
            lineage["terminal_note"] = None
            lineage["state"] = "corrected"
            note_to_lineage[note.id] = root_id
            continue

        if note.operation == "reject":
            if lineage["category"] != "mapping":
                unresolved.append(_unresolved_event(note, "rejection-target-is-not-mapping"))
                continue
            if not lineage["active"]:
                unresolved.append(_unresolved_event(note, "cannot-reject-inactive-lineage"))
                continue
            lineage["events"].append(note)
            lineage["active"] = False
            lineage["state"] = "rejected"
            lineage["terminal_note"] = note
            note_to_lineage[note.id] = root_id
            continue

        if note.operation == "retract":
            if not lineage["active"]:
                unresolved.append(_unresolved_event(note, "cannot-retract-inactive-lineage"))
                continue
            lineage["events"].append(note)
            lineage["active"] = False
            lineage["state"] = "retracted"
            lineage["terminal_note"] = note
            note_to_lineage[note.id] = root_id
            continue

        if note.operation == "reopen":
            if lineage["active"]:
                unresolved.append(_unresolved_event(note, "cannot-reopen-active-lineage"))
                continue
            if category != lineage["category"]:
                unresolved.append(_unresolved_event(note, "reopening-category-mismatch"))
                continue
            lineage["events"].append(note)
            lineage["active"] = True
            lineage["state"] = "reopened"
            lineage["current_note"] = note
            lineage["last_active_note"] = note
            lineage["terminal_note"] = None
            note_to_lineage[note.id] = root_id
            continue

        unresolved.append(_unresolved_event(note, "unsupported-event-operation"))

    def lineage_sort_key(lineage: dict[str, Any]) -> tuple[Any, ...]:
        note: StoredNote = lineage["current_note"]
        specificity = SCOPE_SPECIFICITY.get(note.scope["kind"], 0)
        label = (
            note.payload.get("sensory_phrase")
            if lineage["category"] == "mapping"
            else note.payload.get("activation_boundary")
        )
        return (-specificity, str(label).lower(), lineage["root_id"])

    active_mappings = sorted(
        [row for row in lineages.values() if row["active"] and row["category"] == "mapping"],
        key=lineage_sort_key,
    )
    active_boundaries = sorted(
        [row for row in lineages.values() if row["active"] and row["category"] == "boundary"],
        key=lineage_sort_key,
    )
    inactive = sorted(
        [row for row in lineages.values() if not row["active"]],
        key=lambda row: (row["state"], lineage_sort_key(row)),
    )
    unresolved.sort(key=lambda row: (row["captured_at"], row["id"]))

    kind_counts: dict[str, int] = {}
    operation_counts: dict[str, int] = {}
    for note in notes:
        kind_counts[note.kind] = kind_counts.get(note.kind, 0) + 1
        operation_counts[note.operation] = operation_counts.get(note.operation, 0) + 1

    return {
        "home": home,
        "notes": notes,
        "source_file_count": source_file_count,
        "valid_note_count": len(notes),
        "invalid_notes": invalid_notes,
        "source_fingerprint": source_fingerprint,
        "source_latest_at": notes[-1].captured_at if notes else None,
        "kind_counts": kind_counts,
        "operation_counts": operation_counts,
        "lineages": lineages,
        "active_mappings": active_mappings,
        "active_boundaries": active_boundaries,
        "inactive_entries": inactive,
        "unresolved_events": unresolved,
    }


def _markdown_text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _lineage_note_ids(lineage: dict[str, Any]) -> list[str]:
    return [note.id for note in lineage["events"]]


def _aggregate_source_refs(lineage: dict[str, Any]) -> list[dict[str, str]]:
    seen: set[tuple[str, str, str]] = set()
    rows: list[dict[str, str]] = []
    for note in lineage["events"]:
        for ref in note.source_refs:
            key = (ref["kind"], ref["ref"], ref["summary"])
            if key in seen:
                continue
            seen.add(key)
            rows.append(ref)
    rows.sort(key=lambda row: (row["kind"], row["ref"], row["summary"]))
    return rows


def _scope_lines(note: StoredNote) -> list[str]:
    lines = [f"- scope_kind: `{note.scope['kind']}`"]
    lines.append(f"- scope_repo: `{_markdown_text(note.scope.get('repo') or 'none')}`")
    paths = note.scope.get("paths", [])
    lines.append(f"- scope_paths: `{', '.join(paths) if paths else 'none'}`")
    return lines


def _suggested_target(lineage: dict[str, Any]) -> str:
    note: StoredNote = lineage["current_note"]
    if lineage["category"] == "boundary" and note.scope["kind"] == "global":
        return "memory_summary.md"
    return "MEMORY.md"


def _render_source_provenance(lines: list[str], lineage: dict[str, Any]) -> None:
    lines.append("- source_note_ids:")
    for note_id in _lineage_note_ids(lineage):
        lines.append(f"  - `{note_id}`")
    lines.append("- source_refs:")
    refs = _aggregate_source_refs(lineage)
    if not refs:
        lines.append("  - none")
    else:
        for ref in refs:
            lines.append(
                f"  - `{_markdown_text(ref['kind'])}` `{_markdown_text(ref['ref'])}` — "
                f"{_markdown_text(ref['summary'])}"
            )


def _render_active_mapping(lines: list[str], lineage: dict[str, Any]) -> None:
    note: StoredNote = lineage["current_note"]
    payload = note.payload
    phrase = _markdown_text(payload.get("sensory_phrase"))
    lines.extend(
        [
            f"### {phrase}",
            "",
            f"- state: `{lineage['state']}`",
            f"- lineage_root: `{lineage['root_id']}`",
            f"- authority: `{note.authority}`",
            f"- confirmation_count: `{lineage['confirmation_count']}`",
            f"- latest_event_at: `{note.captured_at}`",
            f"- suggested_target: `{_suggested_target(lineage)}`",
        ]
    )
    lines.extend(_scope_lines(note))
    lines.extend(
        [
            f"- sensory_phrase: {_markdown_text(payload.get('sensory_phrase'))}",
            f"- engineering_translation: {_markdown_text(payload.get('engineering_translation'))}",
            f"- activation_boundary: {_markdown_text(payload.get('activation_boundary'))}",
            f"- non_activation_boundary: {_markdown_text(payload.get('non_activation_boundary'))}",
            f"- verification: {_markdown_text(payload.get('verification'))}",
            "- retrieval_terms:",
            f"  - {_markdown_text(payload.get('sensory_phrase'))}",
            f"  - {_markdown_text(payload.get('engineering_translation'))}",
        ]
    )
    _render_source_provenance(lines, lineage)
    lines.append("")


def _render_active_boundary(lines: list[str], lineage: dict[str, Any]) -> None:
    note: StoredNote = lineage["current_note"]
    payload = note.payload
    title = _markdown_text(payload.get("activation_boundary"))[:96]
    lines.extend(
        [
            f"### {title}",
            "",
            f"- state: `{lineage['state']}`",
            f"- lineage_root: `{lineage['root_id']}`",
            f"- authority: `{note.authority}`",
            f"- confirmation_count: `{lineage['confirmation_count']}`",
            f"- latest_event_at: `{note.captured_at}`",
            f"- suggested_target: `{_suggested_target(lineage)}`",
        ]
    )
    lines.extend(_scope_lines(note))
    lines.extend(
        [
            f"- activation_boundary: {_markdown_text(payload.get('activation_boundary'))}",
            f"- non_activation_boundary: {_markdown_text(payload.get('non_activation_boundary'))}",
            f"- verification: {_markdown_text(payload.get('verification'))}",
        ]
    )
    _render_source_provenance(lines, lineage)
    lines.append("")


def _render_inactive_entry(lines: list[str], lineage: dict[str, Any]) -> None:
    active_note: StoredNote = lineage["last_active_note"]
    terminal: StoredNote = lineage["terminal_note"]
    if lineage["category"] == "mapping":
        title = _markdown_text(active_note.payload.get("sensory_phrase"))
        prior_rule = _markdown_text(active_note.payload.get("engineering_translation"))
    else:
        title = _markdown_text(active_note.payload.get("activation_boundary"))[:96]
        prior_rule = _markdown_text(active_note.payload.get("activation_boundary"))
    reason = _markdown_text(
        terminal.payload.get("rejection_reason")
        or terminal.payload.get("reason")
        or terminal.summary
    )
    lines.extend(
        [
            f"### {title}",
            "",
            f"- state: `{lineage['state']}`",
            f"- category: `{lineage['category']}`",
            f"- lineage_root: `{lineage['root_id']}`",
            f"- terminal_event: `{terminal.id}`",
            f"- prior_rule: {prior_rule}",
            f"- reason: {reason}",
            "- suggested_target: `none`",
        ]
    )
    _render_source_provenance(lines, lineage)
    lines.append("")


def render_memory_digest(
    projection: dict[str, Any],
    generated_at: str,
    *,
    include_inactive: bool = True,
    limit: int = 0,
) -> str:
    active_mappings = list(projection["active_mappings"])
    active_boundaries = list(projection["active_boundaries"])
    if limit > 0:
        combined = [*(('mapping', row) for row in active_mappings), *(('boundary', row) for row in active_boundaries)]
        combined = combined[:limit]
        active_mappings = [row for category, row in combined if category == 'mapping']
        active_boundaries = [row for category, row in combined if category == 'boundary']

    lines = [
        "# Synesthesia Digest",
        "",
        f"generated_at: {generated_at}",
        f"generator: synesthesia_memory_note.py memory-digest",
        f"digest_version: {DIGEST_VERSION}",
        "canonical: false",
        "source: immutable memory-source-note/v1 events",
        f"source_fingerprint: sha256:{projection['source_fingerprint']}",
        f"source_latest_at: {projection['source_latest_at'] or 'none'}",
        f"source_note_count: {projection['source_file_count']}",
        f"valid_note_count: {projection['valid_note_count']}",
        f"invalid_note_count: {len(projection['invalid_notes'])}",
        f"active_mapping_count: {len(projection['active_mappings'])}",
        f"active_boundary_count: {len(projection['active_boundaries'])}",
        f"inactive_entry_count: {len(projection['inactive_entries'])}",
        f"unresolved_event_count: {len(projection['unresolved_events'])}",
        f"render_mode: {'full' if include_inactive else 'active-only'}",
        f"entry_limit: {limit}",
        "",
        "This is a generated current-state projection of immutable Synesthesia source notes.",
        "It is not independent evidence and must not replace the source-note event history.",
        "Phase 2 must resolve every `source_note_id` before promoting an entry.",
        "",
        "## Active mappings",
        "",
    ]
    if not active_mappings:
        lines.append("No active mappings.\n")
    else:
        for lineage in active_mappings:
            _render_active_mapping(lines, lineage)

    lines.extend(["## Active activation boundaries", ""])
    if not active_boundaries:
        lines.append("No active activation boundaries.\n")
    else:
        for lineage in active_boundaries:
            _render_active_boundary(lines, lineage)

    if include_inactive:
        lines.extend(["## Rejected or retracted mappings and boundaries", ""])
        if not projection["inactive_entries"]:
            lines.append("No rejected or retracted entries.\n")
        else:
            for lineage in projection["inactive_entries"]:
                _render_inactive_entry(lines, lineage)

    lines.extend(["## Unresolved event chains", ""])
    if not projection["unresolved_events"]:
        lines.append("No unresolved event chains.\n")
    else:
        for row in projection["unresolved_events"]:
            lines.extend(
                [
                    f"- `{row['id']}` kind=`{row['kind']}` operation=`{row['operation']}`",
                    f"  reason: {_markdown_text(row['reason'])}",
                    f"  prior_ids: {', '.join(row['prior_ids']) if row['prior_ids'] else 'none'}",
                ]
            )
        lines.append("")

    lines.extend(["## Invalid source notes", ""])
    if not projection["invalid_notes"]:
        lines.append("No invalid source notes.\n")
    else:
        for row in projection["invalid_notes"]:
            lines.extend(
                [
                    f"- `{_markdown_text(row.get('path'))}`",
                    f"  error: {_markdown_text(row.get('error'))}",
                ]
            )
        lines.append("")

    lines.extend(
        [
            "## Promotion rules",
            "",
            "- Use this digest as an index; immutable notes remain authoritative.",
            "- Promote only entries with resolvable source-note IDs and a current event chain.",
            "- Put compact global activation boundaries in `memory_summary.md`.",
            "- Put scoped mappings and verification rules in `MEMORY.md`.",
            "- Do not recreate the installed Synesthesia skill in memory.",
            "- Regenerate this digest after source-note changes before Phase 2 consolidation.",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _digest_metadata(path: Path) -> dict[str, str] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    lines = text.splitlines()
    if not lines or lines[0].strip() != "# Synesthesia Digest":
        return None
    out: dict[str, str] = {}
    for line in lines[1:40]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if re.fullmatch(r"[a-z_]+", key):
            out[key] = value.strip()
    return out


def _metadata_int(metadata: dict[str, str], key: str) -> int:
    try:
        return int(metadata.get(key, "0") or 0)
    except ValueError as exc:
        raise ValidationError(f"digest metadata {key}: expected integer") from exc


def inspect_digest(
    home: Path,
    projection: dict[str, Any],
    path: Path | None = None,
) -> dict[str, Any]:
    digest_path = path or default_digest_path(home)
    expected = f"sha256:{projection['source_fingerprint']}"
    if digest_path.is_symlink():
        return {"path": str(digest_path), "status": "symlinked", "expected_source_fingerprint": expected}
    if not digest_path.exists():
        return {"path": str(digest_path), "status": "missing", "expected_source_fingerprint": expected}
    if not digest_path.is_file():
        return {"path": str(digest_path), "status": "not-file", "expected_source_fingerprint": expected}
    metadata = _digest_metadata(digest_path)
    if metadata is None or metadata.get("digest_version") != DIGEST_VERSION:
        return {
            "path": str(digest_path),
            "status": "invalid",
            "expected_source_fingerprint": expected,
            "metadata": metadata,
        }
    full_projection = metadata.get("render_mode") == "full" and metadata.get("entry_limit") == "0"
    status = (
        "current"
        if metadata.get("source_fingerprint") == expected and full_projection
        else "stale"
    )
    try:
        counts = {
            "active_mappings": _metadata_int(metadata, "active_mapping_count"),
            "active_boundaries": _metadata_int(metadata, "active_boundary_count"),
            "inactive_entries": _metadata_int(metadata, "inactive_entry_count"),
            "unresolved_events": _metadata_int(metadata, "unresolved_event_count"),
            "invalid_notes": _metadata_int(metadata, "invalid_note_count"),
        }
    except ValidationError:
        return {
            "path": str(digest_path),
            "status": "invalid",
            "expected_source_fingerprint": expected,
            "metadata": metadata,
        }
    return {
        "path": str(digest_path),
        "status": status,
        "generated_at": metadata.get("generated_at"),
        "source_fingerprint": metadata.get("source_fingerprint"),
        "expected_source_fingerprint": expected,
        **counts,
        "render_mode": metadata.get("render_mode"),
        "entry_limit": metadata.get("entry_limit"),
    }


def _atomic_write_regular(path: Path, content: bytes) -> None:
    ensure_no_symlink_components(path)
    if path.is_symlink():
        raise ValidationError(f"digest destination is a symlink: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    ensure_no_symlink_components(path.parent)
    fd, temp_name = tempfile.mkstemp(prefix=".synesthesia-digest-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_name, 0o644)
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_memory_digest(
    home: Path,
    *,
    output: Path | None = None,
    include_inactive: bool = True,
    limit: int = 0,
    force: bool = False,
    generated_at: str | None = None,
) -> dict[str, Any]:
    if limit < 0:
        raise ValidationError("limit: expected zero or a positive integer")
    destination = output.expanduser().absolute() if output else default_digest_path(home)
    if output is None and (not include_inactive or limit != 0):
        raise ValidationError(
            "partial digest options require --output; the default latest digest must be complete"
        )
    projection = build_digest_projection(home)
    before = inspect_digest(home, projection, destination)
    if before["status"] == "current" and not force:
        return {
            "status": "current",
            "path": str(destination),
            "source_fingerprint": f"sha256:{projection['source_fingerprint']}",
            "source_notes": projection["source_file_count"],
            "active_mappings": len(projection["active_mappings"]),
            "active_boundaries": len(projection["active_boundaries"]),
            "inactive_entries": len(projection["inactive_entries"]),
            "unresolved_events": len(projection["unresolved_events"]),
            "invalid_notes": len(projection["invalid_notes"]),
        }
    timestamp = generated_at or now_utc()
    digest = render_memory_digest(
        projection,
        timestamp,
        include_inactive=include_inactive,
        limit=limit,
    )
    _atomic_write_regular(destination, digest.encode("utf-8"))
    return {
        "status": "written",
        "path": str(destination),
        "generated_at": timestamp,
        "source_fingerprint": f"sha256:{projection['source_fingerprint']}",
        "source_notes": projection["source_file_count"],
        "active_mappings": len(projection["active_mappings"]),
        "active_boundaries": len(projection["active_boundaries"]),
        "inactive_entries": len(projection["inactive_entries"]),
        "unresolved_events": len(projection["unresolved_events"]),
        "invalid_notes": len(projection["invalid_notes"]),
    }


def _scan_compiled_memory(home: Path, note_ids: list[str]) -> dict[str, Any]:
    roots = [home / "memories/memory_summary.md", home / "memories/MEMORY.md"]
    skills_root = home / "memories/skills"
    if skills_root.is_dir():
        roots.extend(path for path in skills_root.rglob("*") if path.is_file())
    mentions: list[dict[str, Any]] = []
    terms = ["synesthesia", "sensory_phrase", "engineering_translation", *note_ids]
    for path in roots:
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        hits = [term for term in terms if term and term in text]
        if hits:
            mentions.append({"path": str(path), "terms": hits[:20]})
    return {"files_checked": len(roots), "mentions": mentions}


def doctor(home: Path) -> dict[str, Any]:
    source = source_instructions_path()
    live = live_instructions_path(home)
    if live.is_symlink():
        adapter_status = "symlinked"
    elif not live.exists():
        adapter_status = "missing"
    elif not live.is_file():
        adapter_status = "not-file"
    elif source.is_file() and sha256_file(source) == sha256_file(live):
        adapter_status = "current"
    else:
        adapter_status = "stale-or-local"

    projection = build_digest_projection(home)
    note_ids = [note.id for note in projection["notes"]]
    latest = [
        {
            "id": note.id,
            "kind": note.kind,
            "operation": note.operation,
            "captured_at": note.captured_at,
            "path": str(note.path),
        }
        for note in projection["notes"][-10:][::-1]
    ]

    binary = find_memory_note_binary()
    writer_result: dict[str, Any] = {
        "available": binary is not None,
        "binary": str(binary) if binary else None,
    }
    if binary:
        proc = subprocess.run(
            [str(binary), "doctor", "--extension", "synesthesia"],
            text=True,
            capture_output=True,
            check=False,
        )
        writer_result.update(
            {
                "exit_code": proc.returncode,
                "stdout": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
            }
        )

    digest = inspect_digest(home, projection)
    compiled = _scan_compiled_memory(home, note_ids)
    if projection["source_file_count"] == 0:
        stage = "no-source-notes"
        recommendation = "Create a note only after a qualifying durable user event."
    elif adapter_status != "current":
        stage = "adapter-not-current"
        recommendation = "Run sync-instructions, then regenerate the digest."
    elif digest["status"] == "missing":
        stage = "source-notes-digest-missing"
        recommendation = "Run memory-digest to materialize the current Synesthesia state."
    elif digest["status"] in {"stale", "invalid", "symlinked", "not-file"}:
        stage = f"source-notes-digest-{digest['status']}"
        recommendation = "Repair the digest path if needed, then run memory-digest --force."
    elif compiled["mentions"]:
        stage = "compiled-memory-present"
        recommendation = "Verify retrieval scope and wording if the mapping is still not recalled."
    else:
        stage = "source-notes-digest-current-awaiting-promotion"
        recommendation = (
            "The current digest is ready for Phase 2. Resolve any invalid or unresolved chains, "
            "then inspect Phase 2 scheduling and promotion output."
        )

    return {
        "synesthesia_memory_doctor": {
            "codex_home": str(home),
            "stage": stage,
            "recommendation": recommendation,
            "adapter": {
                "status": adapter_status,
                "source": str(source),
                "live": str(live),
                "source_sha256": sha256_file(source) if source.is_file() else None,
                "live_sha256": sha256_file(live) if live.is_file() and not live.is_symlink() else None,
            },
            "notes": {
                "directory": str(notes_directory(home)),
                "count": projection["source_file_count"],
                "valid_count": projection["valid_note_count"],
                "kind_counts": projection["kind_counts"],
                "operation_counts": projection["operation_counts"],
                "parse_errors": projection["invalid_notes"],
                "latest": latest,
            },
            "digest": digest,
            "projection": {
                "active_mappings": len(projection["active_mappings"]),
                "active_boundaries": len(projection["active_boundaries"]),
                "inactive_entries": len(projection["inactive_entries"]),
                "unresolved_events": len(projection["unresolved_events"]),
                "invalid_notes": len(projection["invalid_notes"]),
            },
            "writer": writer_result,
            "compiled_memory": compiled,
        }
    }


def print_doctor_text(report: dict[str, Any]) -> None:
    body = report["synesthesia_memory_doctor"]
    print(f"stage: {body['stage']}")
    print(f"codex_home: {body['codex_home']}")
    print(f"adapter: {body['adapter']['status']} ({body['adapter']['live']})")
    print(f"source_notes: {body['notes']['count']} valid={body['notes']['valid_count']}")
    print(f"digest: {body['digest']['status']} ({body['digest']['path']})")
    print(
        "projection: "
        f"mappings={body['projection']['active_mappings']} "
        f"boundaries={body['projection']['active_boundaries']} "
        f"inactive={body['projection']['inactive_entries']} "
        f"unresolved={body['projection']['unresolved_events']} "
        f"invalid={body['projection']['invalid_notes']}"
    )
    print(f"compiled_mentions: {len(body['compiled_memory']['mentions'])}")
    print(f"memory_note_available: {str(body['writer']['available']).lower()}")
    print(f"recommendation: {body['recommendation']}")
    if body["notes"]["latest"]:
        print("latest:")
        for row in body["notes"]["latest"]:
            print(
                f"  {row.get('id')} kind={row.get('kind')} operation={row.get('operation')} "
                f"captured_at={row.get('captured_at')}"
            )


def cmd_validate(args: argparse.Namespace) -> int:
    raw = read_json_input(args.json)
    physical_kind, normalized = validate_and_normalize(args.kind, raw)
    result = {
        "valid": True,
        "logical_kind": args.kind,
        "physical_kind": physical_kind,
        "canonical_fingerprint": canonical_fingerprint(physical_kind, normalized),
        "normalized": normalized,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


def cmd_append(args: argparse.Namespace) -> int:
    raw = read_json_input(args.json)
    physical_kind, normalized = validate_and_normalize(args.kind, raw)
    binary = find_memory_note_binary()
    if binary is None:
        print("memory-note: not-attempted: cli unavailable", file=sys.stderr)
        return 127
    command = [
        str(binary),
        "append",
        "--extension",
        "synesthesia",
        "--kind",
        physical_kind,
        "--json",
        "-",
    ]
    if args.codex_home:
        command.extend(["--codex-home", args.codex_home])
    if args.dry_run:
        command.append("--dry-run")
    proc = subprocess.run(
        command,
        input=canonical_json_bytes(normalized),
        capture_output=True,
        check=False,
    )
    if proc.stdout:
        sys.stdout.buffer.write(proc.stdout)
    if proc.stderr:
        sys.stderr.buffer.write(proc.stderr)
    if proc.returncode == 0 and not args.dry_run:
        try:
            generate_memory_digest(codex_home(args.codex_home))
        except Exception as exc:  # Digest failure must never roll back source-note capture.
            print(f"memory-digest warning: {exc}", file=sys.stderr)
    return proc.returncode


def cmd_memory_digest(args: argparse.Namespace) -> int:
    output = Path(args.output).expanduser() if args.output else None
    result = generate_memory_digest(
        codex_home(args.codex_home),
        output=output,
        include_inactive=args.include_inactive,
        limit=args.limit,
        force=args.force,
    )
    if args.format == "json":
        print(json.dumps({"synesthesia_memory_digest": result}, indent=2, sort_keys=True))
    else:
        print(
            f"memory-digest: {result['status']} {result['path']} "
            f"mappings={result['active_mappings']} boundaries={result['active_boundaries']} "
            f"inactive={result['inactive_entries']} unresolved={result['unresolved_events']} "
            f"invalid={result['invalid_notes']}"
        )
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    result = sync_instructions(
        codex_home(args.codex_home), Path(args.source).expanduser() if args.source else None
    )
    print(json.dumps({"synesthesia_instruction_sync": result}, indent=2, sort_keys=True))
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    report = doctor(codex_home(args.codex_home))
    if args.format == "text":
        print_doctor_text(report)
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    body = report["synesthesia_memory_doctor"]
    if body["adapter"]["status"] in {"symlinked", "not-file"}:
        return 2
    if body["digest"]["status"] in {"symlinked", "not-file", "invalid"}:
        return 2
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Synesthesia memory-source note, digest, and deployment adapter"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    validate_parser = sub.add_parser("validate", help="Validate and normalize one append input")
    validate_parser.add_argument("--kind", required=True, choices=sorted(LOGICAL_TO_PHYSICAL_KIND))
    validate_parser.add_argument("--json", required=True, help="JSON input file or - for stdin")
    validate_parser.set_defaults(func=cmd_validate)

    append_parser = sub.add_parser("append", help="Validate, append, and refresh the digest")
    append_parser.add_argument("--kind", required=True, choices=sorted(LOGICAL_TO_PHYSICAL_KIND))
    append_parser.add_argument("--json", required=True, help="JSON input file or - for stdin")
    append_parser.add_argument("--codex-home")
    append_parser.add_argument("--dry-run", action="store_true")
    append_parser.set_defaults(func=cmd_append)

    digest_parser = sub.add_parser(
        "memory-digest", help="Fold Synesthesia events into a current-state digest"
    )
    digest_parser.add_argument("--codex-home")
    digest_parser.add_argument("--output")
    digest_parser.add_argument("--limit", type=int, default=0)
    digest_parser.add_argument("--force", action="store_true")
    digest_mode = digest_parser.add_mutually_exclusive_group()
    digest_mode.add_argument(
        "--include-inactive", dest="include_inactive", action="store_true", default=True
    )
    digest_mode.add_argument(
        "--active-only", dest="include_inactive", action="store_false"
    )
    digest_parser.add_argument("--format", choices=("text", "json"), default="text")
    digest_parser.set_defaults(func=cmd_memory_digest)

    sync_parser = sub.add_parser(
        "sync-instructions", help="Copy the checked-in adapter into the live memory root"
    )
    sync_parser.add_argument("--codex-home")
    sync_parser.add_argument("--source")
    sync_parser.set_defaults(func=cmd_sync)

    doctor_parser = sub.add_parser("doctor", help="Diagnose note, digest, and Phase 2 state")
    doctor_parser.add_argument("--codex-home")
    doctor_parser.add_argument("--format", choices=("json", "text"), default="json")
    doctor_parser.set_defaults(func=cmd_doctor)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except ValidationError as exc:
        print(
            json.dumps(
                {"synesthesia_memory_note": {"verdict": "fail", "error": str(exc)}},
                indent=2,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    except OSError as exc:
        print(
            json.dumps(
                {"synesthesia_memory_note": {"verdict": "fail", "error": str(exc)}},
                indent=2,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
