#!/usr/bin/env -S uv run python
"""Manage a persistent repo-committed plan in append-only JSONL format."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_FILE = Path(".codex/st-plan.jsonl")
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


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_status(raw_status: str) -> str:
    key = raw_status.strip().lower()
    key = STATUS_ALIASES.get(key, key)
    if key not in VALID_STATUSES:
        values = ", ".join(sorted(VALID_STATUSES))
        raise ValueError(f"invalid status '{raw_status}'; expected one of: {values}")
    return key


def read_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    events: list[dict[str, Any]] = []
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
                raise ValueError(f"invalid event at line {line_number}: expected object")
            events.append(data)
    return events


def canonical_item(raw_item: dict[str, Any]) -> dict[str, str]:
    if not isinstance(raw_item, dict):
        raise ValueError("item must be an object")
    item_id = str(raw_item.get("id", "")).strip()
    step = str(raw_item.get("step", "")).strip()
    status = normalize_status(str(raw_item.get("status", "pending")))
    if not item_id:
        raise ValueError("item.id must be non-empty")
    if not step:
        raise ValueError(f"item '{item_id}' step must be non-empty")
    return {"id": item_id, "step": step, "status": status}


def apply_events(events: list[dict[str, Any]]) -> OrderedDict[str, dict[str, str]]:
    state: OrderedDict[str, dict[str, str]] = OrderedDict()

    for event in events:
        op = event.get("op")
        if op == "init":
            continue
        if op == "replace":
            state = OrderedDict()
            for raw_item in event.get("items", []):
                item = canonical_item(raw_item)
                state[item["id"]] = item
            continue
        if op == "upsert":
            item = canonical_item(event.get("item", {}))
            state[item["id"]] = item
            continue
        if op == "set_status":
            item_id = str(event.get("id", "")).strip()
            if item_id not in state:
                raise ValueError(f"set_status references unknown id '{item_id}'")
            state[item_id]["status"] = normalize_status(str(event.get("status", "")))
            continue
        if op == "remove":
            item_id = str(event.get("id", "")).strip()
            state.pop(item_id, None)
            continue
        raise ValueError(f"unknown op '{op}'")

    return state


def ensure_single_in_progress(items: OrderedDict[str, dict[str, str]]) -> None:
    in_progress = [item for item in items.values() if item["status"] == "in_progress"]
    if len(in_progress) > 1:
        ids = ", ".join(item["id"] for item in in_progress)
        raise ValueError(f"multiple in_progress items found: {ids}")


def next_id(items: OrderedDict[str, dict[str, str]]) -> str:
    max_seen = 0
    for item_id in items.keys():
        match = re.match(r"(?i)^(?:st|kt)-(\d+)$", item_id)
        if match:
            max_seen = max(max_seen, int(match.group(1)))
    return f"st-{max_seen + 1:03d}"


def append_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, separators=(",", ":")) + "\n")


def build_event(op: str, **payload: Any) -> dict[str, Any]:
    event: dict[str, Any] = {"v": 1, "ts": now_utc_iso(), "op": op}
    event.update(payload)
    return event


def load_state(path: Path) -> OrderedDict[str, dict[str, str]]:
    return apply_events(read_events(path))


def render_markdown(items: OrderedDict[str, dict[str, str]]) -> str:
    if not items:
        return "- [ ] (empty plan)"

    lines: list[str] = []
    for item in items.values():
        status = item["status"]
        marker = {
            "pending": "[ ]",
            "in_progress": "[~]",
            "completed": "[x]",
            "blocked": "[!]",
            "deferred": "[-]",
            "canceled": "[ ]",
        }[status]
        step = item["step"]
        if status == "canceled":
            step = f"~~{step}~~"
        suffix = "" if status in {"pending", "completed"} else f" ({status})"
        lines.append(f"- {marker} {item['id']} {step}{suffix}")
    return "\n".join(lines)


def parse_snapshot(snapshot: Any) -> list[dict[str, str]]:
    if isinstance(snapshot, list):
        raw_items = snapshot
    elif isinstance(snapshot, dict) and isinstance(snapshot.get("items"), list):
        raw_items = snapshot["items"]
    else:
        raise ValueError("snapshot must be an array of items or object with items")

    items: list[dict[str, str]] = []
    for raw_item in raw_items:
        items.append(canonical_item(raw_item))
    return items


def cmd_init(args: argparse.Namespace) -> int:
    path = args.file
    if not path.exists() or path.stat().st_size == 0:
        append_event(path, build_event("init"))
        print(f"initialized {path}")
    else:
        print(f"already initialized: {path}")

    if args.replace:
        append_event(path, build_event("replace", items=[]))
        print(f"cleared plan in {path}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    state = load_state(args.file)
    item_id = args.id.strip() if args.id else next_id(state)
    step = args.step.strip()
    if not item_id:
        raise ValueError("--id cannot be empty")
    if not step:
        raise ValueError("--step cannot be empty")

    item = {"id": item_id, "step": step, "status": normalize_status(args.status)}
    proposed = copy.deepcopy(state)
    proposed[item_id] = item
    if not args.allow_multiple_in_progress:
        ensure_single_in_progress(proposed)

    append_event(args.file, build_event("upsert", item=item))
    print(f"upserted {item_id}")
    return 0


def cmd_set_status(args: argparse.Namespace) -> int:
    state = load_state(args.file)
    item_id = args.id.strip()
    if item_id not in state:
        raise ValueError(f"unknown id '{item_id}'")

    status = normalize_status(args.status)
    proposed = copy.deepcopy(state)
    proposed[item_id]["status"] = status
    if not args.allow_multiple_in_progress:
        ensure_single_in_progress(proposed)

    append_event(args.file, build_event("set_status", id=item_id, status=status))
    print(f"updated {item_id} -> {status}")
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    state = load_state(args.file)
    item_id = args.id.strip()
    if item_id not in state:
        raise ValueError(f"unknown id '{item_id}'")

    append_event(args.file, build_event("remove", id=item_id))
    print(f"removed {item_id}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    state = load_state(args.file)
    if not args.allow_multiple_in_progress:
        ensure_single_in_progress(state)

    if args.format == "markdown":
        print(render_markdown(state))
        return 0
    if args.format == "json":
        print(json.dumps({"items": list(state.values())}, indent=2))
        return 0

    header = f"{'ID':<10} {'STATUS':<12} STEP"
    print(header)
    print("-" * len(header))
    for item in state.values():
        print(f"{item['id']:<10} {item['status']:<12} {item['step']}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    state = load_state(args.file)
    if not args.allow_multiple_in_progress:
        ensure_single_in_progress(state)

    payload = {"items": list(state.values())}
    text = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(text, end="")
    return 0


def cmd_import_plan(args: argparse.Namespace) -> int:
    snapshot = json.loads(args.input.read_text(encoding="utf-8"))
    items = parse_snapshot(snapshot)
    state = OrderedDict((item["id"], item) for item in items)
    if not args.allow_multiple_in_progress:
        ensure_single_in_progress(state)

    if args.replace:
        append_event(args.file, build_event("replace", items=items))
        print(f"replaced plan from {args.input}")
        return 0

    for item in items:
        append_event(args.file, build_event("upsert", item=item))
    print(f"imported {len(items)} item(s) from {args.input}")
    return 0


def add_common_file_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE, help="Path to plan JSONL file")


def add_common_status_policy_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--allow-multiple-in-progress",
        action="store_true",
        help="Allow multiple items with in_progress status",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage append-only JSONL plan state")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize plan storage")
    add_common_file_argument(init_parser)
    init_parser.add_argument("--replace", action="store_true", help="Clear current plan state")
    init_parser.set_defaults(func=cmd_init)

    add_parser = subparsers.add_parser("add", help="Add or upsert a plan item")
    add_common_file_argument(add_parser)
    add_common_status_policy_argument(add_parser)
    add_parser.add_argument("--id", help="Plan item ID (default: auto st-###)")
    add_parser.add_argument("--step", required=True, help="Plan step text")
    add_parser.add_argument("--status", default="pending", help="Item status")
    add_parser.set_defaults(func=cmd_add)

    set_status_parser = subparsers.add_parser("set-status", help="Set item status")
    add_common_file_argument(set_status_parser)
    add_common_status_policy_argument(set_status_parser)
    set_status_parser.add_argument("--id", required=True, help="Plan item ID")
    set_status_parser.add_argument("--status", required=True, help="New status")
    set_status_parser.set_defaults(func=cmd_set_status)

    remove_parser = subparsers.add_parser("remove", help="Remove item")
    add_common_file_argument(remove_parser)
    remove_parser.add_argument("--id", required=True, help="Plan item ID")
    remove_parser.set_defaults(func=cmd_remove)

    show_parser = subparsers.add_parser("show", help="Show current plan")
    add_common_file_argument(show_parser)
    add_common_status_policy_argument(show_parser)
    show_parser.add_argument(
        "--format",
        choices=["markdown", "table", "json"],
        default="markdown",
        help="Output format",
    )
    show_parser.set_defaults(func=cmd_show)

    export_parser = subparsers.add_parser("export", help="Export snapshot JSON")
    add_common_file_argument(export_parser)
    add_common_status_policy_argument(export_parser)
    export_parser.add_argument("--output", type=Path, help="Write output to file")
    export_parser.set_defaults(func=cmd_export)

    import_parser = subparsers.add_parser("import-plan", help="Import snapshot JSON")
    add_common_file_argument(import_parser)
    add_common_status_policy_argument(import_parser)
    import_parser.add_argument("--input", type=Path, required=True, help="Snapshot JSON input")
    import_parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace current plan with imported items",
    )
    import_parser.set_defaults(func=cmd_import_plan)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
