from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None


def load_document(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    if path.endswith(".json") or yaml is None:
        value = json.loads(text)
    else:
        value = yaml.safe_load(text)
    if not isinstance(value, dict):
        raise ValueError("document must be an object")
    return value


def unwrap(value: dict[str, Any], key: str) -> dict[str, Any]:
    body = value.get(key, value)
    if not isinstance(body, dict):
        raise ValueError(f"{key} must be an object")
    return body


def yes(value: Any) -> bool:
    return value is True or value == "yes" or value == "pass"


def no(value: Any) -> bool:
    return value is False or value == "no" or value == "fail"


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


def require(parent: dict[str, Any], key: str, errors: list[str], prefix: str = "") -> Any:
    value = parent.get(key)
    if value is None or value == "":
        errors.append(f"{prefix}{key}:missing")
    return value


def unique_ids(rows: list[Any], field: str, errors: list[str], prefix: str) -> set[str]:
    result: set[str] = set()
    for index, row in enumerate(rows):
        item = f"{prefix}[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{item}:must-be-object")
            continue
        value = row.get(field)
        if not isinstance(value, str) or not value:
            errors.append(f"{item}.{field}:missing")
            continue
        if value in result:
            errors.append(f"{prefix}:{field}:duplicate:{value}")
        result.add(value)
    return result


def emit(name: str, body: dict[str, Any], errors: list[str], warnings: list[str]) -> int:
    payload = {
        name: {
            "verdict": "pass" if not errors else "fail",
            **body,
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not errors else 2
