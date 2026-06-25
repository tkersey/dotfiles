from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None


PLAN_ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,63}$")
HEX_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


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


def require(parent: dict[str, Any], key: str, errors: list[str], prefix: str = "") -> Any:
    value = parent.get(key)
    if value is None or value == "":
        errors.append(f"{prefix}{key}:missing")
    return value


def object_field(
    parent: dict[str, Any], key: str, errors: list[str], prefix: str = ""
) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        errors.append(f"{prefix}{key}:must-be-object")
        return {}
    return value


def list_field(
    parent: dict[str, Any], key: str, errors: list[str], prefix: str = ""
) -> list[Any]:
    value = parent.get(key)
    if not isinstance(value, list):
        errors.append(f"{prefix}{key}:must-be-list")
        return []
    return value


def valid_digest(value: Any) -> bool:
    return isinstance(value, str) and bool(HEX_DIGEST_RE.fullmatch(value))


def valid_plan_id(value: Any) -> bool:
    return isinstance(value, str) and bool(PLAN_ID_RE.fullmatch(value))


def valid_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def normalized_repo_path(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    if value.startswith("/") or "\\" in value or "\x00" in value:
        return False
    path = PurePosixPath(value)
    return not any(part in {"", ".", ".."} for part in path.parts)


def emit(
    name: str,
    fields: dict[str, Any],
    errors: list[str],
    warnings: list[str],
) -> int:
    print(
        json.dumps(
            {
                name: {
                    "verdict": "pass" if not errors else "fail",
                    **fields,
                    "errors": errors,
                    "warnings": warnings,
                }
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not errors else 2


def parse_resource_root(root: str) -> tuple[str, str]:
    if ":" not in root:
        raise ValueError("resource root lacks kind prefix")
    kind, value = root.split(":", 1)
    if kind == "symbol":
        if "#" not in value:
            raise ValueError("symbol resource lacks #symbol")
        path, symbol = value.split("#", 1)
        if not normalized_repo_path(path) or not symbol:
            raise ValueError("invalid symbol resource")
    elif kind == "path":
        if not normalized_repo_path(value):
            raise ValueError("invalid path resource")
    elif kind == "git":
        if value != "index" and not value.startswith("branch:"):
            raise ValueError("invalid git resource")
    elif kind == "repo":
        if value != "all":
            raise ValueError("invalid repo resource")
    elif kind not in {"generated", "schema", "service"}:
        raise ValueError(f"unknown resource kind:{kind}")
    elif not value:
        raise ValueError("empty resource value")
    return kind, value


def _path_overlap(left: str, right: str) -> bool:
    l = PurePosixPath(left).parts
    r = PurePosixPath(right).parts
    limit = min(len(l), len(r))
    return l[:limit] == r[:limit]


def resource_overlap(left: str, right: str) -> bool:
    lk, lv = parse_resource_root(left)
    rk, rv = parse_resource_root(right)

    if lk == "repo" or rk == "repo":
        return True

    if lk == rk:
        if lk == "path":
            return _path_overlap(lv, rv)
        if lk == "symbol":
            lp, ls = lv.split("#", 1)
            rp, rs = rv.split("#", 1)
            return lp == rp and ls == rs
        return lv == rv

    if {lk, rk} == {"path", "symbol"}:
        path_value = lv if lk == "path" else rv
        symbol_value = rv if rk == "symbol" else lv
        symbol_path = symbol_value.split("#", 1)[0]
        return _path_overlap(path_value, symbol_path)

    return False


def resource_modes_conflict(left: str, right: str) -> bool:
    if left == "read" and right == "read":
        return False
    return True
