#!/usr/bin/env -S uv run --with pyyaml python
"""Shared helpers for Codebase Doctrine artifact operations."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping

import yaml


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
