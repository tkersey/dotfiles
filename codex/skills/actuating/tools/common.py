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
    return value is True or value == "yes"


def no(value: Any) -> bool:
    return value is False or value == "no"


def require_object(parent: dict[str, Any], key: str, errors: list[str]) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        errors.append(f"{key}:must-be-object")
        return {}
    return value


def require_list(parent: dict[str, Any], key: str, errors: list[str]) -> list[Any]:
    value = parent.get(key)
    if not isinstance(value, list):
        errors.append(f"{key}:must-be-list")
        return []
    return value
