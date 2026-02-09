#!/usr/bin/env -S uv run python
"""Event-log helpers for st schema v3."""

from __future__ import annotations

import json
import re
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

SCHEMA_VERSION = 3
VALID_LANES = {"event", "checkpoint"}
VALID_STATUSES = {
    "pending",
    "in_progress",
    "completed",
    "blocked",
    "deferred",
    "canceled",
}
STATUS_ALIASES = {
    "open": "pending",
    "queued": "pending",
    "active": "in_progress",
    "doing": "in_progress",
    "in-progress": "in_progress",
    "done": "completed",
    "closed": "completed",
    "cancelled": "canceled",
}
DEFAULT_DEP_TYPE = "blocks"
DEP_TYPE_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_status(raw_status: str) -> str:
    key = raw_status.strip().lower()
    key = STATUS_ALIASES.get(key, key)
    if key not in VALID_STATUSES:
        values = ", ".join(sorted(VALID_STATUSES))
        raise ValueError(f"invalid status '{raw_status}'; expected one of: {values}")
    return key


def _require_non_empty_string(value: Any, field: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{field} must be non-empty")
    return text


def _normalize_dep_type(raw_dep_type: Any) -> str:
    dep_type = str(raw_dep_type).strip().lower()
    if not dep_type:
        dep_type = DEFAULT_DEP_TYPE
    if not DEP_TYPE_PATTERN.match(dep_type):
        raise ValueError(
            f"invalid dependency type '{raw_dep_type}'; expected kebab-case (e.g. '{DEFAULT_DEP_TYPE}')"
        )
    return dep_type


def _canonical_dep_edge(raw_dep: Any) -> dict[str, str]:
    if isinstance(raw_dep, str):
        dep_id = _require_non_empty_string(raw_dep, "dependency id")
        return {"id": dep_id, "type": DEFAULT_DEP_TYPE}

    if not isinstance(raw_dep, dict):
        raise ValueError("dependency edges must be objects with {id,type}")

    dep_id = _require_non_empty_string(raw_dep.get("id", ""), "dependency id")
    dep_type = _normalize_dep_type(raw_dep.get("type", DEFAULT_DEP_TYPE))
    return {"id": dep_id, "type": dep_type}


def normalize_deps(raw_deps: Any) -> list[dict[str, str]]:
    if not isinstance(raw_deps, list):
        raise ValueError("item.deps must be an array")

    deps: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for raw_dep in raw_deps:
        dep = _canonical_dep_edge(raw_dep)
        key = (dep["id"], dep["type"])
        if key in seen:
            continue
        seen.add(key)
        deps.append(dep)
    return deps


def parse_cli_deps(raw: str) -> list[dict[str, str]]:
    text = raw.strip()
    if not text:
        return []

    deps: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for token in text.split(","):
        part = token.strip()
        if not part:
            raise ValueError("--deps contains an empty dependency token")

        if ":" in part:
            dep_id, dep_type = part.split(":", 1)
            dep_id = _require_non_empty_string(dep_id, "dependency id")
            dep_type = _normalize_dep_type(dep_type)
        else:
            dep_id = _require_non_empty_string(part, "dependency id")
            dep_type = DEFAULT_DEP_TYPE

        key = (dep_id, dep_type)
        if key in seen:
            continue
        seen.add(key)
        deps.append({"id": dep_id, "type": dep_type})

    return deps


def _normalize_notes(raw_notes: Any) -> str:
    if raw_notes is None:
        return ""
    if not isinstance(raw_notes, str):
        raise ValueError("item.notes must be a string")
    return raw_notes


def _canonical_comment(raw_comment: Any) -> dict[str, str]:
    if not isinstance(raw_comment, dict):
        raise ValueError("item.comments entries must be objects")

    ts = _require_non_empty_string(raw_comment.get("ts", ""), "comment.ts")
    author = _require_non_empty_string(raw_comment.get("author", ""), "comment.author")
    text = _require_non_empty_string(raw_comment.get("text", ""), "comment.text")
    return {"ts": ts, "author": author, "text": text}


def _normalize_comments(raw_comments: Any) -> list[dict[str, str]]:
    if raw_comments is None:
        return []
    if not isinstance(raw_comments, list):
        raise ValueError("item.comments must be an array")
    return [_canonical_comment(comment) for comment in raw_comments]


def canonical_item(raw_item: Any) -> dict[str, Any]:
    if not isinstance(raw_item, dict):
        raise ValueError("item must be an object")

    item_id = _require_non_empty_string(raw_item.get("id", ""), "item.id")
    step = _require_non_empty_string(raw_item.get("step", ""), f"item '{item_id}' step")
    status = normalize_status(str(raw_item.get("status", "pending")))
    if "deps" not in raw_item:
        raise ValueError(f"item '{item_id}' deps must be provided")

    return {
        "id": item_id,
        "step": step,
        "status": status,
        "deps": normalize_deps(raw_item.get("deps")),
        "notes": _normalize_notes(raw_item.get("notes", "")),
        "comments": _normalize_comments(raw_item.get("comments", [])),
    }


def read_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                data = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON at line {line_number}: {exc}") from exc
            if not isinstance(data, dict):
                raise ValueError(f"invalid record at line {line_number}: expected object")
            records.append(data)
    return records


def detect_stream_version(records: list[dict[str, Any]]) -> int:
    if not records:
        return 0

    saw_v3 = False
    saw_v2_after_v3 = False
    for index, record in enumerate(records, start=1):
        version = record.get("v")
        if version not in {2, 3}:
            raise ValueError(f"unsupported schema version '{version}' at record {index}")
        if version == 3:
            saw_v3 = True
        elif saw_v3:
            saw_v2_after_v3 = True

    if saw_v2_after_v3:
        raise ValueError("invalid stream: v2 record found after v3 record")
    return 3 if saw_v3 else 2


def _apply_event_op(
    state: OrderedDict[str, dict[str, Any]],
    record: Mapping[str, Any],
    *,
    source: str,
) -> None:
    op = str(record.get("op", "")).strip()
    if op == "init":
        return

    if op in {"replace", "replace_all"}:
        raw_items = record.get("items")
        if not isinstance(raw_items, list):
            raise ValueError(f"{source} replace requires 'items' array")
        snapshot: OrderedDict[str, dict[str, Any]] = OrderedDict()
        for raw_item in raw_items:
            item = canonical_item(raw_item)
            snapshot[item["id"]] = item
        state.clear()
        state.update(snapshot)
        return

    if op in {"upsert", "upsert_item"}:
        item = canonical_item(record.get("item"))
        state[item["id"]] = item
        return

    item_id = _require_non_empty_string(record.get("id", ""), f"{source} id")
    if item_id not in state and op != "remove":
        raise ValueError(f"{op} references unknown id '{item_id}'")

    if op == "set_status":
        state[item_id]["status"] = normalize_status(str(record.get("status", "")))
        return

    if op == "set_deps":
        state[item_id]["deps"] = normalize_deps(record.get("deps"))
        return

    if op == "set_notes":
        state[item_id]["notes"] = _normalize_notes(record.get("notes", ""))
        return

    if op in {"add_comment", "append_comment", "comment"}:
        raw_comment = record.get("comment")
        if raw_comment is None:
            raw_comment = {
                "ts": record.get("ts", ""),
                "author": record.get("author", ""),
                "text": record.get("text", ""),
            }
        state[item_id]["comments"].append(_canonical_comment(raw_comment))
        return

    if op == "remove":
        state.pop(item_id, None)
        return

    raise ValueError(f"unknown op '{op}'")


def _materialize_checkpoint(record: Mapping[str, Any], *, source: str) -> OrderedDict[str, dict[str, Any]]:
    raw_items = record.get("items")
    if not isinstance(raw_items, list):
        raise ValueError(f"{source} checkpoint requires 'items' array")

    state: OrderedDict[str, dict[str, Any]] = OrderedDict()
    for raw_item in raw_items:
        item = canonical_item(raw_item)
        state[item["id"]] = item
    return state


def materialize_v3(records: list[dict[str, Any]]) -> OrderedDict[str, dict[str, Any]]:
    state: OrderedDict[str, dict[str, Any]] = OrderedDict()

    for index, record in enumerate(records, start=1):
        version = record.get("v")
        source = f"record {index}"

        if version == 2:
            _apply_event_op(state, record, source=source)
            continue

        if version != 3:
            raise ValueError(f"unsupported schema version '{version}' at {source}")

        lane = str(record.get("lane", "")).strip().lower()
        if lane not in VALID_LANES:
            raise ValueError(f"{source} has invalid lane '{record.get('lane')}'")

        if lane == "checkpoint":
            state = _materialize_checkpoint(record, source=source)
            continue

        _apply_event_op(state, record, source=source)

    return state


def unresolved_dependency_ids(
    item: Mapping[str, Any],
    items: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    deps = normalize_deps(item.get("deps"))
    unresolved: list[str] = []
    seen: set[str] = set()

    for dep in deps:
        dep_id = dep["id"]
        dep_item = items.get(dep_id)
        if dep_item is None:
            if dep_id not in seen:
                seen.add(dep_id)
                unresolved.append(dep_id)
            continue
        dep_status = normalize_status(str(dep_item.get("status", "pending")))
        if dep_status != "completed" and dep_id not in seen:
            seen.add(dep_id)
            unresolved.append(dep_id)

    return unresolved


def dependency_state(item: Mapping[str, Any], items: Mapping[str, Mapping[str, Any]]) -> str:
    status = normalize_status(str(item.get("status", "pending")))
    if status == "blocked":
        return "blocked_manual"
    if status in {"completed", "deferred", "canceled"}:
        return "n/a"
    if unresolved_dependency_ids(item, items):
        return "waiting_on_deps"
    return "ready"


def _ensure_no_cycles(items: OrderedDict[str, dict[str, Any]]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def dfs(node_id: str) -> None:
        if node_id in visited:
            return
        if node_id in visiting:
            start_index = stack.index(node_id)
            cycle = stack[start_index:] + [node_id]
            raise ValueError(f"dependency cycle detected: {' -> '.join(cycle)}")

        visiting.add(node_id)
        stack.append(node_id)
        for dep in items[node_id]["deps"]:
            dfs(dep["id"])
        stack.pop()
        visiting.remove(node_id)
        visited.add(node_id)

    for item_id in items.keys():
        dfs(item_id)


def validate_state(
    items: OrderedDict[str, dict[str, Any]],
    allow_multiple_in_progress: bool = False,
) -> None:
    normalized: OrderedDict[str, dict[str, Any]] = OrderedDict()

    for key, raw_item in items.items():
        item = canonical_item(raw_item)
        if key != item["id"]:
            raise ValueError(f"item key '{key}' does not match item.id '{item['id']}'")
        normalized[item["id"]] = item

    for item_id, item in normalized.items():
        for dep in item["deps"]:
            dep_id = dep["id"]
            if dep_id == item_id:
                raise ValueError(f"item '{item_id}' cannot depend on itself")
            if dep_id not in normalized:
                raise ValueError(f"item '{item_id}' references unknown dependency '{dep_id}'")

    _ensure_no_cycles(normalized)

    in_progress_ids = [item["id"] for item in normalized.values() if item["status"] == "in_progress"]
    if not allow_multiple_in_progress and len(in_progress_ids) > 1:
        raise ValueError(f"multiple in_progress items found: {', '.join(in_progress_ids)}")

    for item in normalized.values():
        status = item["status"]
        if status not in {"in_progress", "completed"}:
            continue
        unresolved = unresolved_dependency_ids(item, normalized)
        if unresolved:
            unresolved_text = ", ".join(unresolved)
            raise ValueError(
                f"item '{item['id']}' cannot be {status}; unresolved dependencies: {unresolved_text}"
            )


def next_id(items: Mapping[str, Mapping[str, Any]]) -> str:
    max_seen = 0
    for item_id in items.keys():
        match = re.match(r"(?i)^(?:st|kt)-(\d+)$", item_id)
        if match:
            max_seen = max(max_seen, int(match.group(1)))
    return f"st-{max_seen + 1:03d}"


def build_record(lane: str, **payload: Any) -> dict[str, Any]:
    lane_key = lane.strip().lower()
    if lane_key not in VALID_LANES:
        allowed = ", ".join(sorted(VALID_LANES))
        raise ValueError(f"invalid lane '{lane}'; expected one of: {allowed}")

    if "seq" in payload:
        seq = payload["seq"]
        if not isinstance(seq, int) or seq < 0:
            raise ValueError("record.seq must be a non-negative integer")

    record: dict[str, Any] = {
        "v": SCHEMA_VERSION,
        "ts": now_utc_iso(),
        "lane": lane_key,
    }
    record.update(payload)
    return record


def append_record(path: Path, record: dict[str, Any]) -> None:
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    if record.get("v") != SCHEMA_VERSION:
        raise ValueError(f"record.v must be {SCHEMA_VERSION}")
    lane = str(record.get("lane", "")).strip().lower()
    if lane not in VALID_LANES:
        raise ValueError(f"record.lane must be one of: {', '.join(sorted(VALID_LANES))}")

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def latest_seq(records: list[dict[str, Any]]) -> int:
    max_seq = 0
    for index, record in enumerate(records, start=1):
        seq = record.get("seq")
        if seq is None:
            continue
        if not isinstance(seq, int) or seq < 0:
            raise ValueError(f"invalid seq at record {index}: {seq!r}")
        if seq > max_seq:
            max_seq = seq
    return max_seq


def needs_checkpoint(records: list[dict[str, Any]], interval: int) -> bool:
    if interval <= 0:
        raise ValueError("interval must be > 0")

    events_since_checkpoint = 0
    for index, record in enumerate(reversed(records), start=1):
        version = record.get("v")
        if version == 3:
            lane = str(record.get("lane", "")).strip().lower()
            if lane not in VALID_LANES:
                raise ValueError(f"invalid lane in trailing record {index}: {record.get('lane')!r}")
            if lane == "checkpoint":
                break
            events_since_checkpoint += 1
            continue

        if version == 2:
            events_since_checkpoint += 1
            continue

        raise ValueError(f"unsupported schema version in trailing record {index}: {version!r}")

    return events_since_checkpoint >= interval


def build_checkpoint_record(items: Mapping[str, Mapping[str, Any]], seq: int) -> dict[str, Any]:
    if not isinstance(seq, int) or seq < 0:
        raise ValueError("seq must be a non-negative integer")

    snapshot_items: list[dict[str, Any]] = []
    for raw_item in items.values():
        snapshot_items.append(canonical_item(raw_item))

    return build_record("checkpoint", seq=seq, items=snapshot_items)


__all__ = [
    "SCHEMA_VERSION",
    "append_record",
    "build_checkpoint_record",
    "build_record",
    "dependency_state",
    "detect_stream_version",
    "latest_seq",
    "materialize_v3",
    "needs_checkpoint",
    "next_id",
    "normalize_status",
    "now_utc_iso",
    "parse_cli_deps",
    "read_records",
    "unresolved_dependency_ids",
    "validate_state",
]
