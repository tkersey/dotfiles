#!/usr/bin/env -S uv run --with pyyaml python
"""Validate the Synesthesia skill package, eval corpus, and memory admissions."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - surfaced as a clear CLI error
    yaml = None

SKILL_ROOT = Path(__file__).resolve().parents[1]
NOTE_ID_RE = re.compile(r"^MSN-[0-9]{8}T[0-9]{6}Z-[a-f0-9]{16}$")
SCOPE_KINDS = {"global", "repo", "path-family", "task-family", "workflow", "tool"}
MODALITIES = {"visual", "auditory", "spatial", "tactile", "thermal", "pressure"}
MODES = {"diagnose", "explain", "compare", "implementation-lens"}

KIND_OPERATIONS: dict[str, set[str]] = {
    "mapping-endorsement": {"assert", "confirm", "reopen"},
    "mapping-correction": {"supersede"},
    "mapping-rejection": {"reject"},
    "activation-boundary": {"assert", "confirm", "supersede", "reopen"},
    "boundary-retraction": {"retract"},
}

PRIOR_REQUIRED: set[tuple[str, str]] = {
    ("mapping-endorsement", "confirm"),
    ("mapping-endorsement", "reopen"),
    ("mapping-correction", "supersede"),
    ("activation-boundary", "confirm"),
    ("activation-boundary", "supersede"),
    ("activation-boundary", "reopen"),
    ("boundary-retraction", "retract"),
}

ALLOWED_AUTHORITIES = {
    "explicit-user-endorsement",
    "explicit-user-correction",
    "explicit-user-rejection",
    "explicit-user-retraction",
    "explicit-user-remember-request",
    "repeated-accepted-use",
}

OPERATION_AUTHORITIES: dict[str, set[str]] = {
    "assert": {
        "explicit-user-endorsement",
        "explicit-user-remember-request",
        "repeated-accepted-use",
    },
    "confirm": {"explicit-user-endorsement", "repeated-accepted-use"},
    "supersede": {"explicit-user-correction"},
    "reject": {"explicit-user-rejection"},
    "retract": {"explicit-user-retraction"},
    "reopen": {
        "explicit-user-endorsement",
        "explicit-user-correction",
        "repeated-accepted-use",
    },
}

ALLOWED_PAYLOAD_FIELDS = {
    "sensory_phrase",
    "engineering_translation",
    "activation_boundary",
    "non_activation_boundary",
    "verification",
}

DUPLICATED_ENVELOPE_FIELDS = {
    "operation",
    "authority",
    "scope",
    "scope_anchor",
    "endorsement_type",
    "source_refs",
    "related_ids",
    "supersedes_id",
}

EXPECTED_PACKAGE_FILES = {
    "SKILL.md",
    "agents/openai.yaml",
    "references/decision-contract.yaml",
    "references/modality-selection.md",
    "references/memory-admission.md",
    "evals/routing-cases.json",
    "evals/translation-cases.json",
    "evals/memory-cases.json",
    "scripts/validate_synesthesia.py",
    "tests/test_validate_synesthesia.py",
}


class ValidationFailure(Exception):
    """Raised for invalid user-supplied admission data."""


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_yaml(path: Path) -> Any:
    if yaml is None:
        raise RuntimeError("PyYAML is required; run with `uv run --with pyyaml python ...`")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def canonical_text(value: Any) -> str:
    return _canonical_bytes(value).decode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def validate_package(skill_root: Path = SKILL_ROOT) -> list[str]:
    errors: list[str] = []
    present = {
        str(path.relative_to(skill_root))
        for path in skill_root.rglob("*")
        if path.is_file()
    }
    for expected in sorted(EXPECTED_PACKAGE_FILES):
        if expected not in present:
            errors.append(f"package:missing:{expected}")

    skill_path = skill_root / "SKILL.md"
    if skill_path.is_file():
        text = skill_path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            errors.append("skill:frontmatter-missing")
        else:
            try:
                _, raw, _ = text.split("---\n", 2)
                frontmatter = yaml.safe_load(raw) if yaml is not None else {}
            except Exception as exc:  # noqa: BLE001
                errors.append(f"skill:frontmatter-invalid:{exc}")
                frontmatter = {}
            if frontmatter.get("name") != "synesthesia":
                errors.append("skill:name")
            metadata = frontmatter.get("metadata", {})
            if not isinstance(metadata, dict) or metadata.get("version") != "3.0.0":
                errors.append("skill:version")
            description = frontmatter.get("description")
            if not _string(description) or "Reversible" not in description:
                errors.append("skill:description-reversibility")

        required_phrases = {
            "## Activation boundary",
            "## Mapping record",
            "## Modes",
            "## Cross-skill routing",
            "## Memory admission boundary",
            "## Stop conditions",
            "minimum sufficient modalities",
            "falsifier",
        }
        for phrase in sorted(required_phrases):
            if phrase not in text:
                errors.append(f"skill:missing-phrase:{phrase}")
        prohibited_phrases = {
            "Build at least 2 and at most 4 sensory representations",
            "Use these default correspondences unless",
            "Help with Synesthesia tasks",
        }
        for phrase in sorted(prohibited_phrases):
            if phrase in text:
                errors.append(f"skill:legacy-phrase:{phrase}")

    interface_path = skill_root / "agents/openai.yaml"
    if interface_path.is_file():
        try:
            interface = _read_yaml(interface_path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"interface:parse:{exc}")
            interface = {}
        implicit = interface.get("policy", {}).get("allow_implicit_invocation")
        if implicit is not True:
            errors.append("interface:implicit-policy")
        data = interface.get("interface", {})
        if data.get("display_name") != "Synesthesia":
            errors.append("interface:display-name")
        short = data.get("short_description", "")
        prompt = data.get("default_prompt", "")
        for needle in ("reversible", "evidence"):
            if needle not in short.lower() and needle not in prompt.lower():
                errors.append(f"interface:missing:{needle}")
        for needle in ("falsifier", "owning technical workflow"):
            if needle not in prompt.lower():
                errors.append(f"interface:prompt-missing:{needle}")

    errors.extend(validate_decision_contract(skill_root / "references/decision-contract.yaml"))
    return errors


def validate_decision_contract(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        raw = _read_yaml(path)
    except Exception as exc:  # noqa: BLE001
        return [f"contract:parse:{exc}"]
    contract = raw.get("skill_decision_contract", raw) if isinstance(raw, dict) else {}
    if contract.get("contract_version") != "SKDC-v1":
        errors.append("contract:version")
    skill = contract.get("skill", {})
    if skill.get("name") != "synesthesia" or skill.get("kind") != "mixed":
        errors.append("contract:skill")

    def collect(rows: Any, key: str, prefix: str) -> set[str]:
        ids: set[str] = set()
        if not isinstance(rows, list):
            errors.append(f"contract:{prefix}:not-list")
            return ids
        for index, row in enumerate(rows):
            if not isinstance(row, dict) or not _string(row.get(key)):
                errors.append(f"contract:{prefix}[{index}]:id")
                continue
            value = row[key]
            if value in ids:
                errors.append(f"contract:{prefix}:duplicate:{value}")
            ids.add(value)
        return ids

    trigger_ids = collect(contract.get("triggers"), "trigger_id", "triggers")
    route_ids = collect(contract.get("routes"), "route_id", "routes")
    clause_ids = collect(contract.get("clauses"), "clause_id", "clauses")
    required_clause_ids = {"SYN-ACT-001", "SYN-MAP-001", "SYN-MEM-001"}
    if not required_clause_ids.issubset(clause_ids):
        errors.append("contract:required-clauses")

    for row in contract.get("clauses", []) if isinstance(contract.get("clauses"), list) else []:
        for ref in row.get("trigger_refs", []):
            if ref not in trigger_ids:
                errors.append(f"contract:unknown-trigger:{ref}")
        for field in ("expected_routes", "prohibited_routes"):
            for ref in row.get(field, []):
                if ref not in route_ids:
                    errors.append(f"contract:unknown-route:{ref}")
    return errors


def validate_routing_corpus(path: Path) -> list[str]:
    errors: list[str] = []
    value = _read_json(path)
    if value.get("schema") != "synesthesia-routing-cases/v1":
        errors.append("routing:schema")
    cases = value.get("cases")
    if not isinstance(cases, list):
        return errors + ["routing:cases-not-list"]
    ids: set[str] = set()
    positives = 0
    negatives = 0
    owners: set[str] = set()
    for index, case in enumerate(cases):
        prefix = f"routing[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{prefix}:not-object")
            continue
        case_id = case.get("id")
        if not _string(case_id) or case_id in ids:
            errors.append(f"{prefix}:id")
        else:
            ids.add(case_id)
        if not _string(case.get("prompt")):
            errors.append(f"{prefix}:prompt")
        activation = case.get("expected_activation")
        if not isinstance(activation, bool):
            errors.append(f"{prefix}:activation")
        elif activation:
            positives += 1
        else:
            negatives += 1
            if case.get("expected_route") != "SYN-R6-NO-SYNESTHESIA":
                errors.append(f"{prefix}:negative-route")
        if not _string(case.get("expected_route")):
            errors.append(f"{prefix}:route")
        owner = case.get("governing_owner")
        if not _string(owner):
            errors.append(f"{prefix}:owner")
        else:
            owners.add(owner)
        if not _string(case.get("reason")):
            errors.append(f"{prefix}:reason")
    if positives < 4:
        errors.append("routing:insufficient-positive-cases")
    if negatives < 8:
        errors.append("routing:insufficient-negative-cases")
    expected_owners = {"lift", "codebase-audit", "complexity-mitigator", "universalist", "logophile"}
    if not expected_owners.issubset(owners):
        errors.append("routing:missing-owner-near-miss")
    return errors


def validate_translation_candidate(candidate: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(candidate, dict):
        return ["candidate:not-object"]
    mode = candidate.get("mode")
    if mode not in MODES:
        errors.append("candidate:mode")
    observations = candidate.get("literal_observations")
    if not isinstance(observations, list) or not observations or not all(_string(item) for item in observations):
        errors.append("candidate:literal-observations")
    for field in (
        "sensory_model",
        "engineering_translation",
        "uncertainty",
        "falsifier",
        "decision_delta",
    ):
        if not _string(candidate.get(field)):
            errors.append(f"candidate:{field}")
    if str(candidate.get("decision_delta", "")).strip().lower() in {"none", "no change", "n/a"}:
        errors.append("candidate:no-material-delta")
    refs = candidate.get("evidence_refs")
    if not isinstance(refs, list) or not refs or not all(_string(item) for item in refs):
        errors.append("candidate:evidence-refs")
    modalities = candidate.get("modalities")
    if not isinstance(modalities, list) or not modalities:
        errors.append("candidate:modalities")
        modalities = []
    elif len(modalities) != len(set(modalities)):
        errors.append("candidate:duplicate-modalities")
    elif len(modalities) > 3:
        errors.append("candidate:modality-inflation")
    for modality in modalities:
        if modality not in MODALITIES:
            errors.append(f"candidate:unknown-modality:{modality}")
    dimensions = candidate.get("modality_dimensions")
    if not isinstance(dimensions, dict):
        errors.append("candidate:modality-dimensions")
    else:
        if set(dimensions) != set(modalities):
            errors.append("candidate:dimension-keys")
        values = [str(value).strip().lower() for value in dimensions.values() if _string(value)]
        if len(values) != len(modalities):
            errors.append("candidate:dimension-values")
        if len(values) != len(set(values)):
            errors.append("candidate:redundant-modalities")
    if len(modalities) == 3 and not _string(candidate.get("multi_dimensional_justification")):
        errors.append("candidate:three-modality-justification")
    return errors


def validate_translation_corpus(path: Path) -> list[str]:
    errors: list[str] = []
    value = _read_json(path)
    if value.get("schema") != "synesthesia-translation-cases/v1":
        errors.append("translation:schema")
    cases = value.get("cases")
    if not isinstance(cases, list):
        return errors + ["translation:cases-not-list"]
    ids: set[str] = set()
    for index, case in enumerate(cases):
        prefix = f"translation[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{prefix}:not-object")
            continue
        case_id = case.get("id")
        if not _string(case_id) or case_id in ids:
            errors.append(f"{prefix}:id")
        else:
            ids.add(case_id)
        expected = case.get("expected_valid")
        if not isinstance(expected, bool):
            errors.append(f"{prefix}:expected-valid")
            continue
        actual_errors = validate_translation_candidate(case.get("candidate"))
        if expected and actual_errors:
            errors.append(f"{prefix}:unexpected-invalid:{','.join(actual_errors)}")
        if not expected and not actual_errors:
            errors.append(f"{prefix}:unexpected-valid")
    return errors


def _validate_source_refs(value: Any, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append("memory:source-refs")
        return
    for index, row in enumerate(value):
        if not isinstance(row, dict):
            errors.append(f"memory:source-ref[{index}]:not-object")
            continue
        if set(row) != {"kind", "ref", "summary"}:
            errors.append(f"memory:source-ref[{index}]:fields")
        for field in ("kind", "ref", "summary"):
            if not _string(row.get(field)):
                errors.append(f"memory:source-ref[{index}]:{field}")


def _prior_ids(value: dict[str, Any]) -> list[str]:
    out: list[str] = []
    supersedes = value.get("supersedes_id")
    if isinstance(supersedes, str):
        out.append(supersedes)
    related = value.get("related_ids")
    if isinstance(related, list):
        out.extend(item for item in related if isinstance(item, str))
    return out


def validate_memory_envelope(value: Any, kind: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["memory:not-object"]
    if kind not in KIND_OPERATIONS:
        return [f"memory:unknown-kind:{kind}"]
    required = {
        "operation",
        "authority",
        "summary",
        "scope",
        "source_refs",
        "related_ids",
        "supersedes_id",
        "payload",
    }
    missing = required - set(value)
    if missing:
        errors.append(f"memory:missing:{','.join(sorted(missing))}")
    operation = value.get("operation")
    if operation not in KIND_OPERATIONS[kind]:
        errors.append("memory:kind-operation")
    authority = value.get("authority")
    if authority not in ALLOWED_AUTHORITIES:
        errors.append("memory:authority")
    if operation in OPERATION_AUTHORITIES and authority not in OPERATION_AUTHORITIES[operation]:
        errors.append("memory:operation-authority")
    if not _string(value.get("summary")):
        errors.append("memory:summary")

    scope = value.get("scope")
    if not isinstance(scope, dict):
        errors.append("memory:scope")
    else:
        if set(scope) != {"kind", "repo", "paths"}:
            errors.append("memory:scope-fields")
        if scope.get("kind") not in SCOPE_KINDS:
            errors.append("memory:scope-kind")
        if scope.get("repo") is not None and not _string(scope.get("repo")):
            errors.append("memory:scope-repo")
        paths = scope.get("paths")
        if not isinstance(paths, list) or not all(_string(item) for item in paths):
            errors.append("memory:scope-paths")
        if scope.get("kind") in {"repo", "path-family"} and not _string(scope.get("repo")):
            errors.append("memory:scope-repo-required")

    _validate_source_refs(value.get("source_refs"), errors)
    related = value.get("related_ids")
    if not isinstance(related, list):
        errors.append("memory:related-ids")
        related = []
    else:
        for item in related:
            if not isinstance(item, str) or not NOTE_ID_RE.match(item):
                errors.append("memory:related-id-format")
    supersedes = value.get("supersedes_id")
    if supersedes is not None and (not isinstance(supersedes, str) or not NOTE_ID_RE.match(supersedes)):
        errors.append("memory:supersedes-id-format")

    if (kind, operation) in PRIOR_REQUIRED and not _prior_ids(value):
        errors.append("memory:prior-note-required")

    payload = value.get("payload")
    if not isinstance(payload, dict):
        errors.append("memory:payload")
        return errors
    extras = set(payload) - ALLOWED_PAYLOAD_FIELDS
    if extras:
        errors.append(f"memory:payload-extra:{','.join(sorted(extras))}")
    duplicated = set(payload) & DUPLICATED_ENVELOPE_FIELDS
    if duplicated:
        errors.append(f"memory:payload-duplicates-envelope:{','.join(sorted(duplicated))}")

    required_payload = {
        "sensory_phrase",
        "activation_boundary",
        "non_activation_boundary",
        "verification",
    }
    if kind not in {"mapping-rejection", "boundary-retraction"}:
        required_payload.add("engineering_translation")
    for field in sorted(required_payload):
        if not _string(payload.get(field)):
            errors.append(f"memory:payload:{field}")
    if "engineering_translation" in payload and not _string(payload.get("engineering_translation")):
        errors.append("memory:payload:engineering_translation")
    return errors


def validate_memory_corpus(path: Path) -> list[str]:
    errors: list[str] = []
    value = _read_json(path)
    if value.get("schema") != "synesthesia-memory-cases/v1":
        errors.append("memory-corpus:schema")
    cases = value.get("cases")
    if not isinstance(cases, list):
        return errors + ["memory-corpus:cases-not-list"]
    ids: set[str] = set()
    for index, case in enumerate(cases):
        prefix = f"memory-corpus[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{prefix}:not-object")
            continue
        case_id = case.get("id")
        if not _string(case_id) or case_id in ids:
            errors.append(f"{prefix}:id")
        else:
            ids.add(case_id)
        kind = case.get("kind")
        expected = case.get("expected_valid")
        if not isinstance(expected, bool):
            errors.append(f"{prefix}:expected-valid")
            continue
        actual_errors = validate_memory_envelope(case.get("input"), kind)
        if expected and actual_errors:
            errors.append(f"{prefix}:unexpected-invalid:{','.join(actual_errors)}")
        if not expected and not actual_errors:
            errors.append(f"{prefix}:unexpected-valid")

    pairs = value.get("canonical_pairs")
    if not isinstance(pairs, list) or not pairs:
        errors.append("memory-corpus:canonical-pairs")
    else:
        for index, pair in enumerate(pairs):
            if canonical_text(pair.get("left")) != canonical_text(pair.get("right")):
                errors.append(f"memory-corpus:canonical-pair[{index}]")
    return errors


def run_all(skill_root: Path = SKILL_ROOT) -> dict[str, list[str]]:
    return {
        "package": validate_package(skill_root),
        "routing": validate_routing_corpus(skill_root / "evals/routing-cases.json"),
        "translation": validate_translation_corpus(skill_root / "evals/translation-cases.json"),
        "memory": validate_memory_corpus(skill_root / "evals/memory-cases.json"),
    }


def print_result(results: dict[str, list[str]]) -> int:
    errors = [f"{section}:{error}" for section, rows in results.items() for error in rows]
    payload = {
        "synesthesia_validation": {
            "verdict": "pass" if not errors else "fail",
            "sections": {name: {"errors": rows} for name, rows in results.items()},
            "errors": errors,
        }
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not errors else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("all", "package", "routing", "translation", "memory-evals"):
        child = sub.add_parser(command)
        child.add_argument("--skill-root", type=Path, default=SKILL_ROOT)
    memory_file = sub.add_parser("memory-file")
    memory_file.add_argument("file", type=Path)
    memory_file.add_argument("--kind", required=True, choices=sorted(KIND_OPERATIONS))
    memory_file.add_argument("--emit-canonical", action="store_true")

    args = parser.parse_args()
    if args.command == "memory-file":
        try:
            value = _read_json(args.file)
        except Exception as exc:  # noqa: BLE001
            print(json.dumps({"synesthesia_memory_preflight": {"verdict": "fail", "errors": [str(exc)]}}, indent=2))
            return 2
        errors = validate_memory_envelope(value, args.kind)
        if errors:
            print(json.dumps({"synesthesia_memory_preflight": {"verdict": "fail", "errors": errors}}, indent=2), file=sys.stderr)
            return 2
        if args.emit_canonical:
            sys.stdout.write(canonical_text(value))
        else:
            print(
                json.dumps(
                    {
                        "synesthesia_memory_preflight": {
                            "verdict": "pass",
                            "kind": args.kind,
                            "canonical_sha256": canonical_sha256(value),
                        }
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
        return 0

    root = args.skill_root.resolve()
    if args.command == "all":
        return print_result(run_all(root))
    if args.command == "package":
        return print_result({"package": validate_package(root)})
    if args.command == "routing":
        return print_result({"routing": validate_routing_corpus(root / "evals/routing-cases.json")})
    if args.command == "translation":
        return print_result({"translation": validate_translation_corpus(root / "evals/translation-cases.json")})
    if args.command == "memory-evals":
        return print_result({"memory": validate_memory_corpus(root / "evals/memory-cases.json")})
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
