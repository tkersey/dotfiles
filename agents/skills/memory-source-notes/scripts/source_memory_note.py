#!/usr/bin/env -S uv run python
"""Transport source-approved learning admissions and managed memory updates."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import negative_ledger_memory_note as negative
from memory_layout import LayoutError, memory_note_binary, selected_layout

AdapterError = negative.AdapterError
SKILLS_ROOT = Path(__file__).resolve().parents[2]
ENVELOPE = SKILLS_ROOT / "memory-source-notes/definitions/ledger/source-note-envelope.json"
LEARNINGS = SKILLS_ROOT / "learnings/definitions/ledger/learnings-protocol.json"
MSN_ID = re.compile(r"MSN-[0-9]{8}T[0-9]{6}Z-[a-f0-9]{16}")
KINDS = {
    ("learnings", "admit"): "learning-admission",
    ("learnings", "supersede"): "learning-supersession",
    ("learnings", "retract"): "learning-withdrawal",
    ("negative-ledger", "supersede"): "ledger-supersession",
    ("negative-ledger", "retract"): "ledger-retraction",
}
SOURCE_ENVELOPE_FIELDS = ("operation", "summary", "source_refs", "related_ids", "supersedes_id")
NEGATIVE_LIFECYCLE_FIELDS = {
    "status", "status_event_count", "source_event_count", "event_chain_fingerprint",
    "previous_projection_fingerprint", "projection_fingerprint",
}
PRIOR_OPERATIONS = {
    "learning-admission": {"assert"}, "learning-confirmation": {"confirm", "reopen"},
    "learning-supersession": {"supersede"}, "learning-withdrawal": {"retract"},
    "ledger-projection": {"assert", "reopen"}, "ledger-status-transition": {"assert", "reopen"},
    "ledger-supersession": {"supersede"}, "ledger-retraction": {"retract"},
}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def writer_fingerprint(source: str, kind: str, raw: bytes) -> str:
    return hashlib.sha256(source.encode() + b"\n" + kind.encode() + b"\n" + raw).hexdigest()


def source_id(source: str, envelope: dict[str, Any]) -> str | None:
    payload = envelope.get("payload")
    key = "learning_id" if source == "learnings" else "neg_id"
    return payload.get(key) if isinstance(payload, dict) else None


def check_prior(source: str, prior: dict[str, Any]) -> None:
    canonical_id = source_id(source, prior)
    payload, scope = prior.get("payload"), prior.get("scope")
    if (not isinstance(payload, dict) or not isinstance(scope, dict)
            or not canonical_id or not isinstance(prior.get("kind"), str)
            or prior.get("operation") not in PRIOR_OPERATIONS.get(prior["kind"], set())
            or not prior["kind"].startswith("learning-" if source == "learnings" else "ledger-")):
        raise AdapterError("prior admission: invalid kind, operation, or canonical identity")
    repository = payload.get("repo" if source == "learnings" else "repository_id")
    path = ".ledger/learnings/events.jsonl" if source == "learnings" else ".ledger/negative-ledger/events.jsonl"
    path_field = "source_path" if source == "learnings" else "ledger_path"
    ref_kind = "learning" if source == "learnings" else "negative-ledger"
    ref_value = f"{path}#{canonical_id}" if source == "learnings" else f"{repository}:{path}#{canonical_id}"
    references = prior.get("source_refs")
    if (scope.get("kind") != "repo" or not isinstance(repository, str)
            or scope.get("repo") != repository or payload.get(path_field) != path
            or not isinstance(references, list)
            or not any(isinstance(ref, dict) and ref.get("kind") == ref_kind
                       and ref.get("ref") == ref_value for ref in references)
            or not isinstance(prior.get("fingerprint"), str)
            or not re.fullmatch(r"[a-f0-9]{64}", prior["fingerprint"])):
        raise AdapterError("prior admission: canonical provenance is incomplete or inconsistent")


def learning_admission(raw: bytes) -> bytes:
    """Keep canonical relationship IDs as provenance, never note relationships."""
    envelope = negative._parse_json(raw, "learning projection")
    related = envelope.get("related_ids", [])
    supersedes = envelope.get("supersedes_id")
    if not related and supersedes is None:
        return raw
    for relationship, ids in (("related", related), ("supersedes", [supersedes] if supersedes else [])):
        for canonical_id in ids:
            envelope["source_refs"].append({
                "kind": "learning-canonical-relationship", "ref": canonical_id,
                "summary": f"Canonical {relationship} relationship; not a memory-note identity.",
            })
    envelope["related_ids"] = []
    envelope["supersedes_id"] = None
    return canonical_bytes(envelope)


def same_managed_capture(previous: dict[str, Any], current: dict[str, Any],
                         repository_identity: str | None) -> bool:
    """Bind old lifecycle snapshots by their managed store and unchanged capture."""
    if (not isinstance(repository_identity, str)
            or not re.fullmatch(r"ledger-repository:[a-f0-9]{32}", repository_identity)
            or previous.get("repository_id") != repository_identity
            or current.get("repository_id") != repository_identity):
        return False
    for payload in (previous, current):
        counts = [payload.get(key) for key in ("capture_event_count", "status_event_count", "source_event_count")]
        if (any(type(value) is not int or value < 0 for value in counts)
                or counts[0] < 1 or counts[0] + counts[1] != counts[2]):
            return False
        for key in ("projection_fingerprint", "event_chain_fingerprint"):
            if not isinstance(payload.get(key), str) or not re.fullmatch(r"[a-f0-9]{64}", payload[key]):
                return False
    if any(previous[key] > current[key] for key in ("source_event_count", "status_event_count")):
        return False
    return ({key: value for key, value in previous.items() if key not in NEGATIVE_LIFECYCLE_FIELDS}
            == {key: value for key, value in current.items() if key not in NEGATIVE_LIFECYCLE_FIELDS})


def build_update(source: str, operation: str, raw: bytes, prior: dict[str, Any],
                 *, prior_note_id: str, reason: str, evidence_refs: list[str],
                 repository_identity: str | None = None) -> bytes:
    """Bind a source decision to one observed immutable admission, without source mutation."""
    if operation not in ("supersede", "retract") or (source, operation) not in KINDS:
        raise AdapterError("memory update: unsupported source or operation")
    if not MSN_ID.fullmatch(prior_note_id):
        raise AdapterError("memory update: --prior-note-id must be an exact MSN-* identity")
    if not reason.strip() or not evidence_refs or any(not ref.strip() for ref in evidence_refs):
        raise AdapterError("memory update: a source-owned reason and evidence reference are required")
    current = negative._parse_json(raw, "canonical projection")
    if not isinstance(current, dict) or not isinstance(current.get("payload"), dict):
        raise AdapterError("memory update: invalid canonical projection")
    check_prior(source, prior)
    canonical_id, previous_id = source_id(source, current), source_id(source, prior)
    if (prior.get("schema") != "memory-source-note/v1" or prior.get("id") != prior_note_id
            or prior.get("extension") != source or prior.get("authority") != "ledger-cli"
            or current.get("authority") != "ledger-cli"
            or not canonical_id or not previous_id
            or not isinstance(prior.get("scope"), dict) or not isinstance(current.get("scope"), dict)
            or prior["scope"].get("repo") != current["scope"].get("repo")):
        raise AdapterError("memory update: prior admission identity or repository does not match")
    if operation == "retract" and previous_id != canonical_id:
        raise AdapterError("memory withdrawal must reference the same canonical source record")
    if operation == "retract" and prior["scope"] != current["scope"]:
        raise AdapterError("memory withdrawal requires exact prior scope; use a source-approved replacement for scope changes")
    if operation == "supersede" and previous_id != canonical_id:
        if source != "learnings" or current.get("supersedes_id") != previous_id:
            raise AdapterError("memory supersession requires the canonical predecessor relationship")
    previous_payload = {key: value for key, value in prior["payload"].items() if key != "memory_update"}
    if source == "learnings" and previous_id == canonical_id and previous_payload != current["payload"]:
        raise AdapterError("prior learning admission does not match the immutable canonical record")
    if source == "negative-ledger":
        previous_fingerprint = previous_payload.get("projection_fingerprint")
        exact_snapshot = previous_fingerprint and previous_fingerprint in {
                current["payload"].get("projection_fingerprint"),
                current["payload"].get("previous_projection_fingerprint")}
        if not exact_snapshot and not same_managed_capture(previous_payload, current["payload"], repository_identity):
            raise AdapterError("prior negative admission lacks an exact snapshot or unchanged managed-capture binding")
    if prior.get("operation") == "retract":
        raise AdapterError("memory update: prior admission is already withdrawn")
    if "memory_update" in current["payload"]:
        raise AdapterError("canonical projection uses reserved memory_update metadata")
    normalized = negative._parse_json(learning_admission(raw), "learning admission") if source == "learnings" else copy.deepcopy(current)
    normalized["operation"] = operation
    normalized["summary"] = f"{'Withdraw' if operation == 'retract' else 'Replace'} memory guidance {prior_note_id}: {reason}"
    normalized["related_ids"] = [prior_note_id]
    normalized["supersedes_id"] = prior_note_id if operation == "supersede" else None
    normalized["source_refs"].extend({
        "kind": "memory-guidance-change", "ref": ref, "summary": reason,
    } for ref in evidence_refs)
    normalized["payload"]["memory_update"] = {
        "prior_note_id": prior_note_id, "reason": reason, "evidence_refs": evidence_refs,
        "source_envelope": {field: copy.deepcopy(current.get(field)) for field in SOURCE_ENVELOPE_FIELDS},
    }
    return canonical_bytes(normalized)


def validated_update(source: str, raw: bytes, note: dict[str, Any],
                     notes_by_id: dict[str, dict[str, Any]],
                     repository_identity: str | None = None) -> tuple[bytes, bool] | None:
    """Reconstruct adapter bytes for read-only reconciliation; no eligibility decision."""
    payload = note.get("payload")
    update = payload.get("memory_update") if isinstance(payload, dict) else None
    if not isinstance(update, dict) or set(update) != {"prior_note_id", "reason", "evidence_refs", "source_envelope"}:
        return None
    prior_id, reason, refs = update["prior_note_id"], update["reason"], update["evidence_refs"]
    if (not isinstance(prior_id, str) or not isinstance(reason, str) or not isinstance(refs, list)
            or any(not isinstance(ref, str) for ref in refs)):
        return None
    prior = notes_by_id.get(prior_id)
    operation = note.get("operation")
    if prior is None or note.get("extension") != source or note.get("kind") != KINDS.get((source, operation)):
        return None
    retained = update["source_envelope"]
    if not isinstance(retained, dict) or set(retained) != set(SOURCE_ENVELOPE_FIELDS):
        return None
    frozen = {field: copy.deepcopy(note.get(field)) for field in (
        "operation", "authority", "summary", "scope", "source_refs", "related_ids", "supersedes_id", "payload")}
    frozen.update(retained)
    del frozen["payload"]["memory_update"]
    try:
        expected = build_update(source, operation, canonical_bytes(frozen), prior, prior_note_id=prior_id,
                                reason=reason, evidence_refs=refs, repository_identity=repository_identity)
    except AdapterError:
        return None
    projected = negative._parse_json(expected, "memory update")
    if (any(note.get(field) != value for field, value in projected.items())
            or note.get("fingerprint") != writer_fingerprint(source, note["kind"], expected)):
        return None
    current = negative._parse_json(raw, "canonical projection")
    if source_id(source, current) != source_id(source, frozen):
        return None
    if frozen != current:
        if source != "negative-ledger" or frozen.get("scope") != current.get("scope"):
            return None
        previous, latest = frozen.get("payload"), current.get("payload")
        if not isinstance(previous, dict) or not isinstance(latest, dict):
            return None
        # A lifecycle successor may differ, but a reused local ID is not a
        # cross-store identity. Require the current managed store and capture.
        fingerprint = previous.get("projection_fingerprint")
        linked_predecessor = (isinstance(fingerprint, str)
            and re.fullmatch(r"[a-f0-9]{64}", fingerprint)
            and fingerprint == latest.get("previous_projection_fingerprint")
            and previous.get("repository_id") == latest.get("repository_id"))
        if not linked_predecessor and not same_managed_capture(previous, latest, repository_identity):
            return None
    return expected, frozen == current


def validate_envelope(raw: bytes, ledger: str, repo: Path) -> None:
    result = negative._require_success(negative._run([
        ledger, "validate", "--definition", str(ENVELOPE), "--input", "note=-", "--format", "json",
    ], cwd=repo, input_bytes=raw), "source-note validation")
    checked = negative._require_passive_result(negative._parse_json(result, "source-note validation"),
        stage="source-note validation", schema="ledger-validation-result/v1",
        definition_id="memory-source-notes/source-note-envelope")
    if checked.get("valid") is not True:
        raise AdapterError("source-note validation: invalid result")


def inspect_source(args: argparse.Namespace, ledger: str, repo: Path) -> tuple[bytes, dict[str, Any]]:
    if args.source == "negative-ledger":
        source_args = copy.copy(args)
        source_args.kind = "ledger-projection"
        raw, report = negative.inspect_projection(source_args, transport=False)
        return raw, report["storage_context"]
    context = negative.resolve_custody(repo, args.store_id, catalog_root=args.catalog_root, ledger=ledger)
    doctor_raw = negative._require_success(negative._run([
        ledger, "doctor", "--definition", str(LEARNINGS), *context["native_args"], "--format", "json",
    ], cwd=repo), "ledger doctor")
    doctor = negative._require_passive_result(negative._parse_json(doctor_raw, "ledger doctor"),
        stage="ledger doctor", schema="ledger-doctor-result/v1", definition_id="learnings/protocol")
    if doctor.get("healthy") is not True:
        raise AdapterError("ledger doctor: source store is not healthy")
    raw = negative._require_success(negative._run([
        ledger, "project", "--definition", str(LEARNINGS), "--projection", "memory-note",
        *context["native_args"], "--param", f"id={args.id}", "--payload-only", "--format", "json",
    ], cwd=repo), "ledger project")
    validate_envelope(raw, ledger, repo)
    envelope = negative._parse_json(raw, "ledger project")
    if source_id("learnings", envelope) != args.id:
        raise AdapterError("learning projection: canonical identity mismatch")
    return raw, context


def prepare(args: argparse.Namespace) -> tuple[bytes, str, Any]:
    kind = KINDS.get((args.source, args.operation))
    if kind is None:
        raise AdapterError("use negative_ledger_memory_note.py for ordinary Negative Ledger admission")
    repo = Path(args.repo).expanduser().resolve()
    ledger = negative._resolve_binary(args.ledger_bin, "LEDGER_BIN", "ledger")
    raw, context = inspect_source(args, ledger, repo)
    args.memory_note_bin = memory_note_binary(args.memory_note_bin)
    layout = selected_layout(args, args.source)
    if args.operation == "admit":
        if args.prior_note_id or args.reason or args.evidence_ref:
            raise AdapterError("ordinary admission does not accept update arguments")
        raw = learning_admission(raw)
    else:
        if not args.prior_note_id or not args.reason or not args.evidence_ref:
            raise AdapterError("memory update requires --prior-note-id, --reason, and --evidence-ref")
        if not MSN_ID.fullmatch(args.prior_note_id):
            raise AdapterError("memory update: --prior-note-id must be an exact MSN-* identity")
        prior_raw = negative._require_success(negative._run([
            args.memory_note_bin, "show", "--extension", args.source, "--id", args.prior_note_id,
            *layout.writer_args(), "--format", "json",
        ], cwd=repo), "prior memory-note show")
        prior = negative._parse_json(prior_raw, "prior memory-note show")
        if not isinstance(prior, dict):
            raise AdapterError("prior memory-note show: expected a stored note")
        if args.source == "learnings" and source_id(args.source, prior) != args.id:
            predecessor_args = copy.copy(args)
            predecessor_args.id = source_id(args.source, prior)
            if not isinstance(predecessor_args.id, str):
                raise AdapterError("prior learning admission has no canonical ID")
            predecessor_raw, _ = inspect_source(predecessor_args, ledger, repo)
            predecessor = negative._parse_json(predecessor_raw, "canonical predecessor")
            if {key: value for key, value in prior["payload"].items() if key != "memory_update"} != predecessor["payload"]:
                raise AdapterError("prior learning admission does not match the canonical predecessor in this store")
        raw = build_update(args.source, args.operation, raw, prior, prior_note_id=args.prior_note_id,
                           reason=args.reason, evidence_refs=args.evidence_ref,
                           repository_identity=context["repository_id"])
    validate_envelope(raw, ledger, repo)
    return raw, kind, layout


def run(args: argparse.Namespace) -> int:
    raw, kind, layout = prepare(args)
    if args.command == "inspect":
        print(json.dumps({"source": args.source, "kind": kind,
            "writer_fingerprint": writer_fingerprint(args.source, kind, raw),
            "envelope": json.loads(raw), "authority_granted": False, "storage_mutated": False}, indent=2))
        return 0
    argv = [args.memory_note_bin, "append", "--extension", args.source, "--kind", kind,
            *layout.writer_args(), "--json", "-"]
    if args.dry_run:
        argv.append("--dry-run")
    output = negative._require_success(negative._run(argv, cwd=Path(args.repo).resolve(), input_bytes=raw), "memory-note append")
    sys.stdout.buffer.write(output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("inspect", "append"):
        command = sub.add_parser(name)
        command.add_argument("--source", choices=("learnings", "negative-ledger"), required=True)
        command.add_argument("--operation", choices=("admit", "supersede", "retract"), required=True)
        command.add_argument("--id", required=True)
        command.add_argument("--prior-note-id")
        command.add_argument("--reason")
        command.add_argument("--evidence-ref", action="append", default=[])
        command.add_argument("--repo", default=".")
        command.add_argument("--catalog-root", required=True)
        command.add_argument("--store-id")
        command.add_argument("--ledger-bin")
        command.add_argument("--memory-note-bin")
        command.add_argument("--codex-home")
        command.add_argument("--memory-version", choices=("v1", "v2"))
        command.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    try:
        return run(build_parser().parse_args())
    except (AdapterError, LayoutError) as exc:
        print(json.dumps({"source_memory_note": {"verdict": "blocked", "error": str(exc),
                                                "canonical_rollback": False}}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
