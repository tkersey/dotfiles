#!/usr/bin/env -S uv run python
"""Validate, persist, synchronize, and diagnose Synesthesia memory-source notes.

This adapter deliberately keeps the live memory extension instruction file as a
regular copy. It never creates or follows a symlink in the live extension path.
"""

from __future__ import annotations

import argparse
import copy
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


def parse_note(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


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

    notes_dir = home / "memories/extensions/synesthesia/notes"
    note_paths = sorted(notes_dir.glob("*.md")) if notes_dir.is_dir() else []
    kind_counts: dict[str, int] = {}
    operation_counts: dict[str, int] = {}
    parse_errors: list[str] = []
    latest: list[dict[str, Any]] = []
    note_ids: list[str] = []
    for path in note_paths:
        note = parse_note(path)
        if note is None:
            parse_errors.append(str(path))
            continue
        kind = str(note.get("kind", "unknown"))
        operation = str(note.get("operation", "unknown"))
        kind_counts[kind] = kind_counts.get(kind, 0) + 1
        operation_counts[operation] = operation_counts.get(operation, 0) + 1
        note_id = note.get("id")
        if isinstance(note_id, str):
            note_ids.append(note_id)
        latest.append(
            {
                "id": note_id,
                "kind": kind,
                "operation": operation,
                "captured_at": note.get("captured_at"),
                "path": str(path),
            }
        )
    latest = latest[-10:][::-1]

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

    compiled = _scan_compiled_memory(home, note_ids)
    if not note_paths:
        stage = "no-source-notes"
        recommendation = "Create a note only after a qualifying durable user event."
    elif adapter_status != "current":
        stage = "adapter-not-current"
        recommendation = "Run sync-instructions, then trigger Phase 2 consolidation."
    elif not compiled["mentions"]:
        stage = "source-notes-awaiting-or-not-promoted"
        recommendation = (
            "Source notes exist. Check Phase 2 scheduling and promotion output; explicit durable "
            "authority should not require repetition."
        )
    else:
        stage = "compiled-memory-present"
        recommendation = "Verify retrieval scope and wording if the mapping is still not recalled."

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
                "directory": str(notes_dir),
                "count": len(note_paths),
                "kind_counts": kind_counts,
                "operation_counts": operation_counts,
                "parse_errors": parse_errors,
                "latest": latest,
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
    print(f"source_notes: {body['notes']['count']}")
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
    return proc.returncode


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
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Synesthesia memory-source note validation and deployment adapter"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    validate_parser = sub.add_parser("validate", help="Validate and normalize one append input")
    validate_parser.add_argument("--kind", required=True, choices=sorted(LOGICAL_TO_PHYSICAL_KIND))
    validate_parser.add_argument("--json", required=True, help="JSON input file or - for stdin")
    validate_parser.set_defaults(func=cmd_validate)

    append_parser = sub.add_parser("append", help="Validate, canonicalize, and invoke memory-note")
    append_parser.add_argument("--kind", required=True, choices=sorted(LOGICAL_TO_PHYSICAL_KIND))
    append_parser.add_argument("--json", required=True, help="JSON input file or - for stdin")
    append_parser.add_argument("--codex-home")
    append_parser.add_argument("--dry-run", action="store_true")
    append_parser.set_defaults(func=cmd_append)

    sync_parser = sub.add_parser(
        "sync-instructions", help="Copy the checked-in adapter into the live memory root"
    )
    sync_parser.add_argument("--codex-home")
    sync_parser.add_argument("--source")
    sync_parser.set_defaults(func=cmd_sync)

    doctor_parser = sub.add_parser("doctor", help="Diagnose source-note and Phase 2 state")
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
