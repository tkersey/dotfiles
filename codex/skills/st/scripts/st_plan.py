#!/usr/bin/env -S uv run python
"""Manage a persistent repo-committed plan in append-only JSONL format."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any

DEFAULT_FILE = Path(".step/st-plan.jsonl")
DEFAULT_CHECKPOINT_INTERVAL = 50

try:  # Support package and script-style imports.
    from .st_eventlog_v3 import (
        SCHEMA_VERSION,
        append_record,
        build_checkpoint_record,
        build_record,
        latest_seq,
        materialize_v3,
        needs_checkpoint,
        next_id,
        normalize_status,
        now_utc_iso,
        parse_cli_deps,
        read_records,
        validate_state,
    )
    from .st_read_views import blocked_items, enrich_items, ready_items
    from .st_translate import build_update_plan_payload
except ImportError:  # pragma: no cover
    from st_eventlog_v3 import (
        SCHEMA_VERSION,
        append_record,
        build_checkpoint_record,
        build_record,
        latest_seq,
        materialize_v3,
        needs_checkpoint,
        next_id,
        normalize_status,
        now_utc_iso,
        parse_cli_deps,
        read_records,
        validate_state,
    )
    from st_read_views import blocked_items, enrich_items, ready_items
    from st_translate import build_update_plan_payload


def normalize_record_for_read(record: dict[str, Any]) -> dict[str, Any]:
    if record.get("v") != SCHEMA_VERSION:
        return record

    normalized = dict(record)
    if "lane" not in normalized:
        kind = str(normalized.get("kind", "")).strip().lower()
        if kind in {"event", "checkpoint"}:
            normalized["lane"] = kind

    if normalized.get("op") == "replace_all":
        normalized["op"] = "replace"

    return normalized


def read_plan_records(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    raw_records = read_records(path)
    normalized_records = [normalize_record_for_read(record) for record in raw_records]
    return raw_records, normalized_records


def load_state(path: Path) -> OrderedDict[str, dict[str, Any]]:
    _, normalized_records = read_plan_records(path)
    return materialize_v3(normalized_records)


def load_validated_state(
    path: Path,
    *,
    allow_multiple_in_progress: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], OrderedDict[str, dict[str, Any]]]:
    raw_records, normalized_records = read_plan_records(path)
    state = materialize_v3(normalized_records)
    validate_state(state, allow_multiple_in_progress=allow_multiple_in_progress)
    return raw_records, normalized_records, state


def dep_token(dep: Any) -> str:
    if isinstance(dep, dict):
        dep_id = str(dep.get("id", "")).strip()
        dep_type = str(dep.get("type", "blocks")).strip() or "blocks"
    else:
        dep_id = str(dep).strip()
        dep_type = "blocks"

    if dep_type == "blocks":
        return dep_id
    return f"{dep_id}:{dep_type}"


def format_deps(deps: list[Any]) -> str:
    return ", ".join(dep_token(dep) for dep in deps)


def render_markdown(items: OrderedDict[str, dict[str, Any]]) -> str:
    if not items:
        return "- [ ] (empty plan)"

    marker_map = {
        "pending": "[ ]",
        "in_progress": "[~]",
        "completed": "[x]",
        "blocked": "[!]",
        "deferred": "[-]",
        "canceled": "[ ]",
    }

    enriched_items = enrich_items(items)
    sections: list[tuple[str, list[dict[str, Any]]]] = [
        ("In Progress", [item for item in enriched_items if item["status"] == "in_progress"]),
        (
            "Ready",
            [
                item
                for item in enriched_items
                if item["status"] == "pending" and item["dep_state"] == "ready"
            ],
        ),
        (
            "Waiting on Dependencies",
            [
                item
                for item in enriched_items
                if item["status"] == "pending" and item["dep_state"] == "waiting_on_deps"
            ],
        ),
        ("Blocked", [item for item in enriched_items if item["status"] == "blocked"]),
        ("Deferred", [item for item in enriched_items if item["status"] == "deferred"]),
        ("Canceled", [item for item in enriched_items if item["status"] == "canceled"]),
        ("Completed", [item for item in enriched_items if item["status"] == "completed"]),
    ]

    lines: list[str] = []
    for section_title, section_items in sections:
        if not section_items:
            continue
        lines.append(f"### {section_title}")
        for item in section_items:
            status = item["status"]
            marker = marker_map[status]
            step = item["step"]
            if status == "canceled":
                step = f"~~{step}~~"

            details: list[str] = []
            dep_state = str(item.get("dep_state", ""))
            if dep_state != "n/a":
                details.append(f"dep_state: {dep_state}")
            if item["deps"]:
                details.append(f"deps: {format_deps(item['deps'])}")
            waiting_on = item.get("waiting_on", [])
            if waiting_on:
                details.append(f"waiting: {', '.join(waiting_on)}")
            if status not in {"pending", "completed"}:
                details.append(f"status: {status}")

            suffix = f" ({'; '.join(details)})" if details else ""
            lines.append(f"- {marker} {item['id']} {step}{suffix}")
        lines.append("")

    if lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def render_item_list_markdown(items: list[dict[str, Any]]) -> str:
    if not items:
        return "- (none)"

    lines: list[str] = []
    for item in items:
        details: list[str] = []
        dep_state = str(item.get("dep_state", ""))
        if dep_state:
            details.append(f"dep_state: {dep_state}")
        deps = item.get("deps", [])
        if deps:
            details.append(f"deps: {format_deps(deps)}")
        waiting_on = item.get("waiting_on", [])
        if waiting_on:
            details.append(f"waiting: {', '.join(waiting_on)}")
        suffix = f" ({'; '.join(details)})" if details else ""
        lines.append(f"- {item['id']} {item['step']}{suffix}")
    return "\n".join(lines)


def print_table(items: list[dict[str, Any]]) -> None:
    header = f"{'ID':<10} {'STATUS':<12} {'DEP_STATE':<18} {'WAITING_ON':<20} {'DEPS':<20} STEP"
    print(header)
    print("-" * len(header))

    for item in items:
        waiting_on = item.get("waiting_on", [])
        waiting_text = ", ".join(waiting_on) if waiting_on else "-"
        deps = item.get("deps", [])
        deps_text = format_deps(deps) if deps else "-"
        dep_state = str(item.get("dep_state", "-"))
        print(
            f"{item['id']:<10} {item['status']:<12} {dep_state:<18} {waiting_text:<20} {deps_text:<20} {item['step']}"
        )


def render_items(items: list[dict[str, Any]], output_format: str) -> None:
    if output_format == "markdown":
        print(render_item_list_markdown(items))
        return
    if output_format == "json":
        print(json.dumps({"items": items}, indent=2))
        return
    print_table(items)


def parse_snapshot(snapshot: Any) -> list[dict[str, Any]]:
    if isinstance(snapshot, list):
        raw_items = snapshot
    elif isinstance(snapshot, dict) and isinstance(snapshot.get("items"), list):
        raw_items = snapshot["items"]
    else:
        raise ValueError("snapshot must be an array of items or object with items")

    seen_ids: set[str] = set()
    for index, raw_item in enumerate(raw_items):
        if not isinstance(raw_item, dict):
            raise ValueError(f"snapshot item at index {index} must be an object")
        raw_id = raw_item.get("id")
        if isinstance(raw_id, str):
            item_id = raw_id.strip()
            if item_id:
                if item_id in seen_ids:
                    raise ValueError(f"duplicate item id in snapshot: '{item_id}'")
                seen_ids.add(item_id)

    preview_records = [{"v": SCHEMA_VERSION, "lane": "event", "op": "replace", "items": raw_items}]
    state = materialize_v3(preview_records)
    return list(state.values())


def checkpoint_interval_from_env() -> int:
    raw_interval = os.environ.get("ST_CHECKPOINT_INTERVAL", str(DEFAULT_CHECKPOINT_INTERVAL)).strip()
    try:
        interval = int(raw_interval)
    except ValueError as exc:
        raise ValueError(f"invalid ST_CHECKPOINT_INTERVAL '{raw_interval}'; expected integer > 0") from exc
    if interval <= 0:
        raise ValueError(f"invalid ST_CHECKPOINT_INTERVAL '{raw_interval}'; expected integer > 0")
    return interval


def append_mutation_records(
    path: Path,
    raw_records: list[dict[str, Any]],
    normalized_records: list[dict[str, Any]],
    event_payloads: list[dict[str, Any]],
    *,
    allow_multiple_in_progress: bool,
) -> None:
    working_records = list(normalized_records)
    next_seq_value = latest_seq(working_records) + 1
    for payload in event_payloads:
        event_record = build_record("event", seq=next_seq_value, **payload)
        append_record(path, event_record)
        working_records.append(event_record)
        next_seq_value += 1

    interval = checkpoint_interval_from_env()
    if needs_checkpoint(working_records, interval):
        state = materialize_v3(working_records)
        validate_state(state, allow_multiple_in_progress=allow_multiple_in_progress)
        checkpoint_record = build_checkpoint_record(state, seq=latest_seq(working_records))
        append_record(path, checkpoint_record)
        working_records.append(checkpoint_record)


def emit_update_plan(path: Path, *, allow_multiple_in_progress: bool, prefixed: bool) -> None:
    state = load_state(path)
    validate_state(state, allow_multiple_in_progress=allow_multiple_in_progress)
    payload = build_update_plan_payload(enrich_items(state))
    serialized = json.dumps(payload, separators=(",", ":"))
    if prefixed:
        print(f"update_plan: {serialized}")
    else:
        print(serialized)


def default_comment_author() -> str:
    for key in ("ST_COMMENT_AUTHOR", "USER", "LOGNAME"):
        value = os.environ.get(key, "").strip()
        if value:
            return value
    return "unknown"


def cmd_init(args: argparse.Namespace) -> int:
    path = args.file
    if not path.exists() or path.stat().st_size == 0:
        append_record(path, build_record("event", seq=1, op="init"))
        print(f"initialized {path}")
    else:
        print(f"already initialized: {path}")

    if args.replace:
        raw_records, normalized_records = read_plan_records(path)
        append_mutation_records(
            path,
            raw_records,
            normalized_records,
            [{"op": "replace", "items": []}],
            allow_multiple_in_progress=True,
        )
        print(f"cleared plan in {path}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    raw_records, normalized_records, state = load_validated_state(
        args.file,
        allow_multiple_in_progress=args.allow_multiple_in_progress,
    )
    item_id = args.id.strip() if args.id else next_id(state)
    step = args.step.strip()
    if not item_id:
        raise ValueError("--id cannot be empty")
    if not step:
        raise ValueError("--step cannot be empty")

    item = {
        "id": item_id,
        "step": step,
        "status": normalize_status(args.status),
        "deps": parse_cli_deps(args.deps),
        "notes": "",
        "comments": [],
    }
    proposed = copy.deepcopy(state)
    proposed[item_id] = item
    validate_state(proposed, allow_multiple_in_progress=args.allow_multiple_in_progress)

    append_mutation_records(
        args.file,
        raw_records,
        normalized_records,
        [{"op": "upsert", "item": item}],
        allow_multiple_in_progress=args.allow_multiple_in_progress,
    )
    print(f"upserted {item_id}")
    emit_update_plan(args.file, allow_multiple_in_progress=args.allow_multiple_in_progress, prefixed=True)
    return 0


def cmd_set_status(args: argparse.Namespace) -> int:
    raw_records, normalized_records, state = load_validated_state(
        args.file,
        allow_multiple_in_progress=args.allow_multiple_in_progress,
    )
    item_id = args.id.strip()
    if item_id not in state:
        raise ValueError(f"unknown id '{item_id}'")

    status = normalize_status(args.status)
    proposed = copy.deepcopy(state)
    proposed[item_id]["status"] = status
    validate_state(proposed, allow_multiple_in_progress=args.allow_multiple_in_progress)

    append_mutation_records(
        args.file,
        raw_records,
        normalized_records,
        [{"op": "set_status", "id": item_id, "status": status}],
        allow_multiple_in_progress=args.allow_multiple_in_progress,
    )
    print(f"updated {item_id} -> {status}")
    emit_update_plan(args.file, allow_multiple_in_progress=args.allow_multiple_in_progress, prefixed=True)
    return 0


def cmd_set_deps(args: argparse.Namespace) -> int:
    raw_records, normalized_records, state = load_validated_state(
        args.file,
        allow_multiple_in_progress=args.allow_multiple_in_progress,
    )
    item_id = args.id.strip()
    if item_id not in state:
        raise ValueError(f"unknown id '{item_id}'")

    deps = parse_cli_deps(args.deps)
    proposed = copy.deepcopy(state)
    proposed[item_id]["deps"] = deps
    validate_state(proposed, allow_multiple_in_progress=args.allow_multiple_in_progress)

    append_mutation_records(
        args.file,
        raw_records,
        normalized_records,
        [{"op": "set_deps", "id": item_id, "deps": deps}],
        allow_multiple_in_progress=args.allow_multiple_in_progress,
    )
    if deps:
        print(f"updated {item_id} deps -> {format_deps(deps)}")
    else:
        print(f"updated {item_id} deps -> (none)")
    emit_update_plan(args.file, allow_multiple_in_progress=args.allow_multiple_in_progress, prefixed=True)
    return 0


def cmd_set_notes(args: argparse.Namespace) -> int:
    raw_records, normalized_records, state = load_validated_state(
        args.file,
        allow_multiple_in_progress=args.allow_multiple_in_progress,
    )
    item_id = args.id.strip()
    if item_id not in state:
        raise ValueError(f"unknown id '{item_id}'")

    notes = args.notes
    proposed = copy.deepcopy(state)
    proposed[item_id]["notes"] = notes
    validate_state(proposed, allow_multiple_in_progress=args.allow_multiple_in_progress)

    append_mutation_records(
        args.file,
        raw_records,
        normalized_records,
        [{"op": "set_notes", "id": item_id, "notes": notes}],
        allow_multiple_in_progress=args.allow_multiple_in_progress,
    )
    print(f"updated {item_id} notes")
    emit_update_plan(args.file, allow_multiple_in_progress=args.allow_multiple_in_progress, prefixed=True)
    return 0


def cmd_add_comment(args: argparse.Namespace) -> int:
    raw_records, normalized_records, state = load_validated_state(
        args.file,
        allow_multiple_in_progress=args.allow_multiple_in_progress,
    )
    item_id = args.id.strip()
    if item_id not in state:
        raise ValueError(f"unknown id '{item_id}'")

    text = args.text.strip()
    if not text:
        raise ValueError("--text cannot be empty")

    author = args.author.strip() if args.author else default_comment_author()
    if not author:
        raise ValueError("--author cannot be empty")

    comment = {"ts": now_utc_iso(), "author": author, "text": text}
    proposed = copy.deepcopy(state)
    proposed[item_id]["comments"].append(comment)
    validate_state(proposed, allow_multiple_in_progress=args.allow_multiple_in_progress)

    append_mutation_records(
        args.file,
        raw_records,
        normalized_records,
        [{"op": "add_comment", "id": item_id, "comment": comment}],
        allow_multiple_in_progress=args.allow_multiple_in_progress,
    )
    print(f"added comment to {item_id}")
    emit_update_plan(args.file, allow_multiple_in_progress=args.allow_multiple_in_progress, prefixed=True)
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    raw_records, normalized_records, state = load_validated_state(
        args.file,
        allow_multiple_in_progress=args.allow_multiple_in_progress,
    )
    item_id = args.id.strip()
    if item_id not in state:
        raise ValueError(f"unknown id '{item_id}'")

    proposed = copy.deepcopy(state)
    proposed.pop(item_id)
    validate_state(proposed, allow_multiple_in_progress=args.allow_multiple_in_progress)

    append_mutation_records(
        args.file,
        raw_records,
        normalized_records,
        [{"op": "remove", "id": item_id}],
        allow_multiple_in_progress=args.allow_multiple_in_progress,
    )
    print(f"removed {item_id}")
    emit_update_plan(args.file, allow_multiple_in_progress=args.allow_multiple_in_progress, prefixed=True)
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    _, _, state = load_validated_state(
        args.file,
        allow_multiple_in_progress=args.allow_multiple_in_progress,
    )
    enriched_items = enrich_items(state)

    if args.format == "markdown":
        print(render_markdown(state))
        return 0
    if args.format == "json":
        print(json.dumps({"items": enriched_items}, indent=2))
        return 0

    print_table(enriched_items)
    return 0


def cmd_ready(args: argparse.Namespace) -> int:
    _, _, state = load_validated_state(
        args.file,
        allow_multiple_in_progress=args.allow_multiple_in_progress,
    )
    render_items(ready_items(state), args.format)
    return 0


def cmd_blocked(args: argparse.Namespace) -> int:
    _, _, state = load_validated_state(
        args.file,
        allow_multiple_in_progress=args.allow_multiple_in_progress,
    )
    render_items(blocked_items(state), args.format)
    return 0


def cmd_emit_update_plan(args: argparse.Namespace) -> int:
    emit_update_plan(
        args.file,
        allow_multiple_in_progress=args.allow_multiple_in_progress,
        prefixed=False,
    )
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    _, _, state = load_validated_state(
        args.file,
        allow_multiple_in_progress=args.allow_multiple_in_progress,
    )

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
    raw_records, normalized_records, current_state = load_validated_state(
        args.file,
        allow_multiple_in_progress=args.allow_multiple_in_progress,
    )

    proposed_state = copy.deepcopy(current_state)
    if args.replace:
        proposed_state = OrderedDict((item["id"], item) for item in items)
        event_payloads: list[dict[str, Any]] = [{"op": "replace", "items": items}]
    else:
        for item in items:
            proposed_state[item["id"]] = item
        event_payloads = [{"op": "upsert", "item": item} for item in items]

    validate_state(proposed_state, allow_multiple_in_progress=args.allow_multiple_in_progress)

    append_mutation_records(
        args.file,
        raw_records,
        normalized_records,
        event_payloads,
        allow_multiple_in_progress=args.allow_multiple_in_progress,
    )

    if args.replace:
        print(f"replaced plan from {args.input}")
    else:
        print(f"imported {len(items)} item(s) from {args.input}")
    emit_update_plan(args.file, allow_multiple_in_progress=args.allow_multiple_in_progress, prefixed=True)
    return 0


def add_common_file_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE, help="Path to plan JSONL file")


def add_common_status_policy_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--allow-multiple-in-progress",
        action="store_true",
        help="Allow multiple items with in_progress status",
    )


def add_common_list_format_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--format",
        choices=["markdown", "table", "json"],
        default="markdown",
        help="Output format",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage append-only dependency-aware JSONL v3 plan state")
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
    add_parser.add_argument(
        "--deps",
        default="",
        help="Comma-separated deps as id or id:type tokens (default: none)",
    )
    add_parser.set_defaults(func=cmd_add)

    set_status_parser = subparsers.add_parser("set-status", help="Set item status")
    add_common_file_argument(set_status_parser)
    add_common_status_policy_argument(set_status_parser)
    set_status_parser.add_argument("--id", required=True, help="Plan item ID")
    set_status_parser.add_argument("--status", required=True, help="New status")
    set_status_parser.set_defaults(func=cmd_set_status)

    set_deps_parser = subparsers.add_parser("set-deps", help="Set item dependencies")
    add_common_file_argument(set_deps_parser)
    add_common_status_policy_argument(set_deps_parser)
    set_deps_parser.add_argument("--id", required=True, help="Plan item ID")
    set_deps_parser.add_argument(
        "--deps",
        default="",
        help="Comma-separated deps as id or id:type tokens (empty string clears deps)",
    )
    set_deps_parser.set_defaults(func=cmd_set_deps)

    set_notes_parser = subparsers.add_parser("set-notes", help="Set item notes")
    add_common_file_argument(set_notes_parser)
    add_common_status_policy_argument(set_notes_parser)
    set_notes_parser.add_argument("--id", required=True, help="Plan item ID")
    set_notes_parser.add_argument("--notes", required=True, help="Notes text (use empty string to clear)")
    set_notes_parser.set_defaults(func=cmd_set_notes)

    add_comment_parser = subparsers.add_parser("add-comment", help="Add a comment to an item")
    add_common_file_argument(add_comment_parser)
    add_common_status_policy_argument(add_comment_parser)
    add_comment_parser.add_argument("--id", required=True, help="Plan item ID")
    add_comment_parser.add_argument("--text", required=True, help="Comment text")
    add_comment_parser.add_argument("--author", help="Comment author (default: env user)")
    add_comment_parser.set_defaults(func=cmd_add_comment)

    remove_parser = subparsers.add_parser("remove", help="Remove item")
    add_common_file_argument(remove_parser)
    add_common_status_policy_argument(remove_parser)
    remove_parser.add_argument("--id", required=True, help="Plan item ID")
    remove_parser.set_defaults(func=cmd_remove)

    show_parser = subparsers.add_parser("show", help="Show current plan")
    add_common_file_argument(show_parser)
    add_common_status_policy_argument(show_parser)
    add_common_list_format_argument(show_parser)
    show_parser.set_defaults(func=cmd_show)

    ready_parser = subparsers.add_parser("ready", help="Show ready pending items")
    add_common_file_argument(ready_parser)
    add_common_status_policy_argument(ready_parser)
    add_common_list_format_argument(ready_parser)
    ready_parser.set_defaults(func=cmd_ready)

    blocked_parser = subparsers.add_parser("blocked", help="Show blocked or waiting items")
    add_common_file_argument(blocked_parser)
    add_common_status_policy_argument(blocked_parser)
    add_common_list_format_argument(blocked_parser)
    blocked_parser.set_defaults(func=cmd_blocked)

    emit_update_plan_parser = subparsers.add_parser(
        "emit-update-plan",
        help="Emit update_plan JSON payload derived from durable state",
    )
    add_common_file_argument(emit_update_plan_parser)
    add_common_status_policy_argument(emit_update_plan_parser)
    emit_update_plan_parser.set_defaults(func=cmd_emit_update_plan)

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
