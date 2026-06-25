from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

try:
    import yaml
except ImportError:  # optional
    yaml = None

PROPOSED_OPEN = "<proposed_plan>"
PROPOSED_CLOSE = "</proposed_plan>"


def read_text(path: str) -> str:
    return sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")


def load_structured_text(text: str, hint: str = "") -> dict[str, Any]:
    stripped = text.strip()
    if not stripped:
        raise ValueError("input is empty")
    if hint.endswith(".json") or stripped.startswith("{"):
        value = json.loads(stripped)
    elif yaml is not None:
        value = yaml.safe_load(stripped)
    else:
        raise ValueError("non-JSON input requires PyYAML")
    if not isinstance(value, dict):
        raise ValueError("document must be an object")
    return value


def extract_proposed_plan(text: str) -> str:
    if text.count(PROPOSED_OPEN) != 1 or text.count(PROPOSED_CLOSE) != 1:
        raise ValueError("Markdown must contain exactly one <proposed_plan> block")
    before, rest = text.split(PROPOSED_OPEN, 1)
    body, after = rest.split(PROPOSED_CLOSE, 1)
    if before.strip() or after.strip():
        raise ValueError("No non-whitespace text is allowed outside <proposed_plan>")
    return body.strip()


def extract_epg_json_from_markdown(text: str) -> tuple[dict[str, Any], str]:
    body = extract_proposed_plan(text)
    blocks = re.findall(r"```json\s*(\{.*?\})\s*```", body, re.I | re.S)
    candidates: list[dict[str, Any]] = []
    for raw in blocks:
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and "execution_policy_graph" in value:
            candidates.append(value)
    if len(candidates) != 1:
        raise ValueError(
            "Markdown must contain exactly one fenced JSON object with execution_policy_graph"
        )
    return candidates[0], body


def load_epg(path: str) -> tuple[dict[str, Any], dict[str, Any]]:
    text = read_text(path)
    if PROPOSED_OPEN in text or path.lower().endswith((".md", ".markdown")):
        wrapper, body = extract_epg_json_from_markdown(text)
        metadata = {"source_kind": "markdown", "markdown_body": body}
    else:
        wrapper = load_structured_text(text, path.lower())
        metadata = {"source_kind": "structured", "markdown_body": None}
    value = wrapper.get("execution_policy_graph", wrapper)
    if not isinstance(value, dict):
        raise ValueError("execution_policy_graph must be an object")
    return value, metadata


def load_wrapped(path: str, key: str) -> dict[str, Any]:
    value = load_structured_text(read_text(path), path.lower())
    body = value.get(key, value)
    if not isinstance(body, dict):
        raise ValueError(f"{key} must be an object")
    return body


def canonical_digest(value: dict[str, Any]) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def valid_digest(value: Any) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"sha256:[0-9a-f]{64}", value))


def valid_id(value: Any) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9._:-]{1,127}", value))


def valid_atom(value: Any) -> bool:
    return isinstance(value, str) and bool(
        re.fullmatch(
            r"(?:fact|obs|action|unknown|obligation|terminal|custom):[A-Za-z0-9._:-]+(?:=[A-Za-z0-9._:-]+)?",
            value,
        )
    )


def validate_iso_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def is_yes(value: Any) -> bool:
    return value is True or value == "yes" or value == "pass"


def is_no(value: Any) -> bool:
    return value is False or value == "no" or value == "fail"


def require(parent: dict[str, Any], key: str, errors: list[str], prefix: str = "") -> Any:
    value = parent.get(key)
    if value is None or value == "":
        errors.append(f"{prefix}{key}:missing")
    return value


def object_field(parent: dict[str, Any], key: str, errors: list[str], prefix: str = "") -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        errors.append(f"{prefix}{key}:must-be-object")
        return {}
    return value


def list_field(parent: dict[str, Any], key: str, errors: list[str], prefix: str = "") -> list[Any]:
    value = parent.get(key)
    if not isinstance(value, list):
        errors.append(f"{prefix}{key}:must-be-list")
        return []
    return value


def unique_rows(rows: list[Any], id_field: str, errors: list[str], prefix: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        label = f"{prefix}[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{label}:must-be-object")
            continue
        row_id = row.get(id_field)
        if not valid_id(row_id):
            errors.append(f"{label}.{id_field}:invalid")
            continue
        if row_id in result:
            errors.append(f"{prefix}:{id_field}:duplicate:{row_id}")
            continue
        result[row_id] = row
    return result


def condition_atoms(condition: dict[str, Any], errors: list[str], prefix: str) -> set[str]:
    result: set[str] = set()
    for key in ("all", "any", "none"):
        values = list_field(condition, key, errors, prefix)
        for index, atom in enumerate(values):
            if not valid_atom(atom):
                errors.append(f"{prefix}{key}[{index}]:invalid-atom")
            else:
                result.add(atom)
    return result


def condition_true(condition: dict[str, Any], satisfied: set[str]) -> bool:
    all_atoms = set(condition.get("all", []))
    any_atoms = set(condition.get("any", []))
    none_atoms = set(condition.get("none", []))
    return all_atoms.issubset(satisfied) and (not any_atoms or bool(any_atoms & satisfied)) and not bool(none_atoms & satisfied)


def graph_cycles(dependencies: dict[str, list[str]]) -> list[list[str]]:
    state = {node: 0 for node in dependencies}
    stack: list[str] = []
    cycles: list[list[str]] = []

    def visit(node: str) -> None:
        marker = state.get(node, 0)
        if marker == 2:
            return
        if marker == 1:
            if node in stack:
                start = stack.index(node)
                cycles.append(stack[start:] + [node])
            return
        state[node] = 1
        stack.append(node)
        for dep in dependencies.get(node, []):
            if dep in dependencies:
                visit(dep)
        stack.pop()
        state[node] = 2

    for node in dependencies:
        visit(node)
    return cycles


def bool_claim(parent: dict[str, Any], key: str, derived: bool, errors: list[str], prefix: str = "") -> None:
    value = parent.get(key)
    if not (is_yes(value) or is_no(value)):
        errors.append(f"{prefix}{key}:must-be-yes-or-no")
    elif is_yes(value) != derived:
        errors.append(f"{prefix}{key}:contradicts-derived-value")


def state_digest(state: dict[str, Any]) -> str:
    value = dict(state)
    value.pop("state_digest", None)
    return canonical_digest(value)


def emit(name: str, fields: dict[str, Any], errors: list[str], warnings: list[str]) -> int:
    print(json.dumps({name: {"verdict": "pass" if not errors else "fail", **fields, "errors": errors, "warnings": warnings}}, indent=2, sort_keys=True))
    return 0 if not errors else 2


def apply_potential_delta(
    current: dict[str, Any],
    delta: dict[str, Any],
    dimension_ids: set[str],
) -> dict[str, float | int]:
    """Apply a numeric potential delta without permitting unknown dimensions."""
    if not isinstance(current, dict) or not isinstance(delta, dict):
        raise ValueError("potential current/delta must be objects")
    if set(current) != set(dimension_ids):
        missing = sorted(set(dimension_ids) - set(current))
        extra = sorted(set(current) - set(dimension_ids))
        raise ValueError(f"current dimension mismatch missing={missing} extra={extra}")
    unknown = sorted(set(delta) - set(dimension_ids))
    if unknown:
        raise ValueError(f"unknown delta dimensions: {unknown}")
    result: dict[str, float | int] = {}
    for dimension_id in sorted(dimension_ids):
        before = current.get(dimension_id)
        change = delta.get(dimension_id, 0)
        if not isinstance(before, (int, float)) or isinstance(before, bool):
            raise ValueError(f"non-numeric current value: {dimension_id}")
        if not isinstance(change, (int, float)) or isinstance(change, bool):
            raise ValueError(f"non-numeric delta value: {dimension_id}")
        result[dimension_id] = before + change
    return result


def compare_potential(
    before: dict[str, Any],
    after: dict[str, Any],
    dimensions: dict[str, dict[str, Any]],
    order: list[str],
) -> dict[str, Any]:
    """Lexicographically compare potential using each dimension's direction."""
    if set(before) != set(dimensions) or set(after) != set(dimensions):
        raise ValueError("potential dimension set mismatch")
    if list(dict.fromkeys(order)) != order or set(order) != set(dimensions):
        raise ValueError("potential order must list every dimension exactly once")
    for dimension_id in order:
        left = before.get(dimension_id)
        right = after.get(dimension_id)
        if not isinstance(left, (int, float)) or isinstance(left, bool):
            raise ValueError(f"non-numeric before value: {dimension_id}")
        if not isinstance(right, (int, float)) or isinstance(right, bool):
            raise ValueError(f"non-numeric after value: {dimension_id}")
        if left == right:
            continue
        direction = dimensions.get(dimension_id, {}).get("direction")
        if direction == "minimize":
            relation = "improved" if right < left else "worsened"
        elif direction == "maximize":
            relation = "improved" if right > left else "worsened"
        else:
            raise ValueError(f"unknown direction for {dimension_id}: {direction}")
        return {
            "relation": relation,
            "first_difference": dimension_id,
            "before": left,
            "after": right,
            "direction": direction,
        }
    return {
        "relation": "equal",
        "first_difference": None,
        "before": None,
        "after": None,
        "direction": None,
    }


def terminal_thresholds_met(
    potential: dict[str, Any],
    dimensions: dict[str, dict[str, Any]],
    order: list[str],
) -> tuple[bool, list[str]]:
    """Return whether every potential dimension meets its terminal threshold."""
    failed: list[str] = []
    if set(potential) != set(dimensions):
        return False, sorted(set(dimensions) ^ set(potential))
    for dimension_id in order:
        row = dimensions.get(dimension_id, {})
        value = potential.get(dimension_id)
        threshold = row.get("terminal_threshold")
        direction = row.get("direction")
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not isinstance(threshold, (int, float))
            or isinstance(threshold, bool)
        ):
            failed.append(dimension_id)
            continue
        if direction == "minimize" and value > threshold:
            failed.append(dimension_id)
        elif direction == "maximize" and value < threshold:
            failed.append(dimension_id)
        elif direction not in {"minimize", "maximize"}:
            failed.append(dimension_id)
    return not failed, failed
