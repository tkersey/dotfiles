#!/usr/bin/env -S uv run --with pyyaml python
"""Shared helpers for the Codebase Doctrine artifact compilers and validators."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable, Mapping

import yaml

YES = {"yes", True}
NO = {"no", False}
BOOLISH = YES | NO
CONFIDENCE = {"high", "medium", "low", "unknown"}
DOCTRINE_STATUS = {
    "observed_current",
    "documented_intent",
    "explicit_target",
    "proposed",
    "contradicted",
    "retired",
}
EVIDENCE_LANES = {
    "guidance",
    "static_structure",
    "symbols_and_references",
    "behavior_and_tests",
    "authority_and_mutation",
    "history_and_forensics",
    "runtime",
    "agent_history",
    "negative_evidence",
    "user_authority",
}
ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._:-]{1,127}$")


def load_data(path: str | Path) -> dict[str, Any]:
    """Load JSON or YAML from a path or stdin."""
    if str(path) == "-":
        text = sys.stdin.read()
        suffix = ".yaml"
    else:
        p = Path(path)
        text = p.read_text(encoding="utf-8")
        suffix = p.suffix.lower()
    value = json.loads(text) if suffix == ".json" else yaml.safe_load(text)
    if not isinstance(value, dict):
        raise ValueError("artifact must be an object")
    return value


def dump_data(value: Mapping[str, Any], fmt: str = "yaml") -> str:
    if fmt == "json":
        return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    return yaml.safe_dump(
        dict(value),
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256_digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def short_digest(value: Any, length: int = 16) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()[:length]


def deterministic_id(prefix: str, value: Any, length: int = 16) -> str:
    return f"{prefix}-{short_digest(value, length)}"


def unwrap(value: Mapping[str, Any], key: str) -> dict[str, Any]:
    body = value.get(key, value)
    if not isinstance(body, dict):
        raise ValueError(f"{key} must be an object")
    return body


def is_yes(value: Any) -> bool:
    return value in YES


def is_no(value: Any) -> bool:
    return value in NO


def require_object(
    value: Any,
    label: str,
    errors: list[str],
    *,
    nonempty: bool = False,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{label}:must-be-object")
        return {}
    if nonempty and not value:
        errors.append(f"{label}:empty")
    return value


def require_list(
    value: Any,
    label: str,
    errors: list[str],
    *,
    nonempty: bool = False,
) -> list[Any]:
    if not isinstance(value, list):
        errors.append(f"{label}:must-be-list")
        return []
    if nonempty and not value:
        errors.append(f"{label}:empty")
    return value


def require_text(value: Any, label: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}:missing")
        return ""
    return value.strip()


def require_id(value: Any, label: str, errors: list[str]) -> str:
    text = require_text(value, label, errors)
    if text and not ID_RE.match(text):
        errors.append(f"{label}:invalid-id")
    return text


def unique_rows(
    rows: Any,
    key: str,
    label: str,
    errors: list[str],
    *,
    required: bool = False,
) -> tuple[set[str], dict[str, dict[str, Any]]]:
    values = require_list(rows, label, errors, nonempty=required)
    ids: set[str] = set()
    by_id: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(values):
        prefix = f"{label}[{index}]"
        if not isinstance(raw, dict):
            errors.append(f"{prefix}:must-be-object")
            continue
        row_id = require_id(raw.get(key), f"{prefix}.{key}", errors)
        if not row_id:
            continue
        if row_id in ids:
            errors.append(f"{label}:{key}:duplicate:{row_id}")
            continue
        ids.add(row_id)
        by_id[row_id] = raw
    return ids, by_id


def check_refs(
    values: Any,
    allowed: set[str],
    label: str,
    errors: list[str],
    *,
    nonempty: bool = False,
) -> list[str]:
    rows = require_list(values, label, errors, nonempty=nonempty)
    out: list[str] = []
    for value in rows:
        if not isinstance(value, str) or not value:
            errors.append(f"{label}:invalid-ref")
            continue
        out.append(value)
        if value not in allowed:
            errors.append(f"{label}:unknown:{value}")
    return out


def reject_extras(
    value: Mapping[str, Any],
    allowed: Iterable[str],
    label: str,
    errors: list[str],
) -> None:
    extra = sorted(set(value) - set(allowed))
    for field in extra:
        errors.append(f"{label}:unexpected:{field}")


def normalized_bool(value: Any) -> str | None:
    if value in YES:
        return "yes"
    if value in NO:
        return "no"
    return None


def artifact_state_material(state: Mapping[str, Any]) -> dict[str, Any]:
    fields = (
        "repository_root",
        "repository_name",
        "branch",
        "head",
        "dirty_state",
        "tracked_diff_sha256",
        "untracked_path_digest",
        "scope_path_digest",
        "intent_digest",
        "scope",
        "intent_id",
        "captured_at",
    )
    return {field: state.get(field) for field in fields}


def artifact_state_id(state: Mapping[str, Any]) -> str:
    return deterministic_id("AS", artifact_state_material(state))


def validate_artifact_state(
    value: Any,
    errors: list[str],
    *,
    require_id_match: bool = True,
) -> dict[str, Any]:
    state = require_object(value, "artifact_state", errors)
    for field in (
        "artifact_state_id",
        "repository_root",
        "repository_name",
        "branch",
        "head",
        "dirty_state",
        "tracked_diff_sha256",
        "untracked_path_digest",
        "scope_path_digest",
        "intent_digest",
        "scope",
        "intent_id",
        "captured_at",
    ):
        require_text(state.get(field), f"artifact_state.{field}", errors)
    if require_id_match and state.get("artifact_state_id"):
        expected = artifact_state_id(state)
        if state.get("artifact_state_id") != expected:
            errors.append(
                f"artifact_state.artifact_state_id:mismatch:{state.get('artifact_state_id')}:{expected}"
            )
    return state


def report(name: str, errors: list[str], warnings: list[str], **extra: Any) -> dict[str, Any]:
    return {
        name: {
            "verdict": "pass" if not errors else "fail",
            **extra,
            "errors": errors,
            "warnings": warnings,
        }
    }
