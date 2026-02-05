#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import sqlite3
import sys
import time
import uuid

DEFAULT_DB = os.path.expanduser("~/.codex/sqlite/codex-dev.db")
STATUS_ACTIVE = "ACTIVE"
STATUS_PAUSED = "PAUSED"


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def connect(db_path: str) -> sqlite3.Connection:
    if not os.path.exists(db_path):
        fail(f"db not found: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def normalize_rrule(rrule: str | None) -> str | None:
    if rrule is None:
        return None
    value = rrule.strip()
    upper = value.upper()
    if upper.startswith("RRULE:"):
        rule_part = value.split(":", 1)[1].strip()
        if "FREQ=" not in rule_part.upper():
            fail("rrule must include FREQ=... (RFC5545). Cron expressions are not supported.")
        return f"RRULE:{rule_part}"
    if "FREQ=" not in upper:
        fail("rrule must include FREQ=... (RFC5545). Cron expressions are not supported.")
    return value


def parse_cwds(args: argparse.Namespace, allow_default: bool) -> list[str] | None:
    if args.clear_cwds:
        return []
    if args.cwds_json is not None:
        try:
            cwds = json.loads(args.cwds_json)
        except json.JSONDecodeError as exc:
            fail(f"cwds_json must be valid JSON: {exc}")
        if not isinstance(cwds, list) or not all(isinstance(item, str) for item in cwds):
            fail("cwds_json must be a JSON array of strings")
        return cwds
    if args.cwd:
        return args.cwd
    if allow_default:
        return [os.getcwd()]
    return None


def parse_timestamp(value: str | None, value_iso: str | None) -> int | None:
    if value is not None:
        try:
            raw = int(value)
        except ValueError as exc:
            fail(f"timestamp must be an integer unix value: {exc}")
        # Accept seconds (10 digits) or milliseconds (13 digits). Store ms.
        return raw * 1000 if raw < 10_000_000_000 else raw
    if value_iso is not None:
        try:
            parsed = dt.datetime.fromisoformat(value_iso)
        except ValueError as exc:
            fail(f"timestamp ISO must be ISO-8601: {exc}")
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return int(parsed.timestamp() * 1000)
    return None


def resolve_automation(conn: sqlite3.Connection, automation_id: str | None, name: str | None) -> sqlite3.Row:
    if automation_id:
        row = conn.execute("select * from automations where id = ?", (automation_id,)).fetchone()
        if not row:
            fail(f"no automation with id {automation_id}")
        return row
    if name:
        rows = conn.execute("select * from automations where name = ?", (name,)).fetchall()
        if not rows:
            fail(f"no automation named {name}")
        if len(rows) > 1:
            fail(f"multiple automations named {name}; use --id")
        return rows[0]
    fail("provide --id or --name")


def row_to_dict(row: sqlite3.Row) -> dict:
    return {key: row[key] for key in row.keys()}


def cmd_list(args: argparse.Namespace) -> None:
    conn = connect(args.db)
    query = "select * from automations"
    params: tuple = ()
    if args.status:
        query += " where status = ?"
        params = (args.status,)
    query += " order by created_at desc"
    rows = conn.execute(query, params).fetchall()
    if args.json:
        print(json.dumps([row_to_dict(row) for row in rows], indent=2, sort_keys=True))
        return
    if not rows:
        print("no automations")
        return
    for row in rows:
        print(f"{row['id']}\t{row['status']}\t{row['name']}\t{row['rrule']}\t{row['next_run_at']}")


def cmd_show(args: argparse.Namespace) -> None:
    conn = connect(args.db)
    row = resolve_automation(conn, args.id, args.name)
    if args.json:
        print(json.dumps(row_to_dict(row), indent=2, sort_keys=True))
    else:
        for key in row.keys():
            print(f"{key}: {row[key]}")


def read_prompt(args: argparse.Namespace) -> str:
    if args.prompt and args.prompt_file:
        fail("use either --prompt or --prompt-file")
    if args.prompt:
        return args.prompt
    if args.prompt_file:
        try:
            with open(args.prompt_file, "r", encoding="utf-8") as handle:
                return handle.read().strip()
        except OSError as exc:
            fail(f"unable to read prompt file: {exc}")
    fail("prompt is required (--prompt or --prompt-file)")


def cmd_create(args: argparse.Namespace) -> None:
    conn = connect(args.db)
    prompt = read_prompt(args)
    rrule = normalize_rrule(args.rrule)
    if rrule is None:
        fail("rrule is required")
    cwds = parse_cwds(args, allow_default=True)
    status = args.status or STATUS_ACTIVE
    created_at = int(time.time() * 1000)
    next_run_at = parse_timestamp(args.next_run_at, args.next_run_at_iso)
    automation_id = str(uuid.uuid4())
    conn.execute(
        """
        insert into automations (
            id, name, prompt, status, next_run_at, last_run_at, cwds, rrule, created_at, updated_at
        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            automation_id,
            args.name,
            prompt,
            status,
            next_run_at,
            None,
            json.dumps(cwds),
            rrule,
            created_at,
            created_at,
        ),
    )
    conn.commit()
    print(automation_id)


def cmd_update(args: argparse.Namespace) -> None:
    conn = connect(args.db)
    row = resolve_automation(conn, args.id, args.name)
    updates: dict[str, object] = {}

    if args.new_name:
        updates["name"] = args.new_name
    if args.prompt or args.prompt_file:
        updates["prompt"] = read_prompt(args)
    if args.rrule is not None:
        updates["rrule"] = normalize_rrule(args.rrule)
    if args.status is not None:
        updates["status"] = args.status
    if args.clear_next_run_at:
        updates["next_run_at"] = None
    else:
        next_run_at = parse_timestamp(args.next_run_at, args.next_run_at_iso)
        if next_run_at is not None:
            updates["next_run_at"] = next_run_at

    cwds = parse_cwds(args, allow_default=False)
    if cwds is not None:
        updates["cwds"] = json.dumps(cwds)

    if not updates:
        fail("no updates provided")

    updates["updated_at"] = int(time.time() * 1000)
    assignments = ", ".join(f"{key} = ?" for key in updates.keys())
    values = list(updates.values())
    values.append(row["id"])
    conn.execute(f"update automations set {assignments} where id = ?", values)
    conn.commit()
    print(row["id"])


def cmd_enable(args: argparse.Namespace) -> None:
    conn = connect(args.db)
    row = resolve_automation(conn, args.id, args.name)
    now_ms = int(time.time() * 1000)
    conn.execute(
        "update automations set status = ?, updated_at = ? where id = ?",
        (STATUS_ACTIVE, now_ms, row["id"]),
    )
    conn.commit()
    print(row["id"])


def cmd_disable(args: argparse.Namespace) -> None:
    conn = connect(args.db)
    row = resolve_automation(conn, args.id, args.name)
    now_ms = int(time.time() * 1000)
    conn.execute(
        "update automations set status = ?, updated_at = ? where id = ?",
        (STATUS_PAUSED, now_ms, row["id"]),
    )
    conn.commit()
    print(row["id"])


def cmd_run_now(args: argparse.Namespace) -> None:
    conn = connect(args.db)
    row = resolve_automation(conn, args.id, args.name)
    now_ms = int(time.time() * 1000)
    conn.execute(
        "update automations set next_run_at = ?, updated_at = ? where id = ?",
        (now_ms, now_ms, row["id"]),
    )
    conn.commit()
    print(row["id"])


def cmd_delete(args: argparse.Namespace) -> None:
    conn = connect(args.db)
    row = resolve_automation(conn, args.id, args.name)
    conn.execute("delete from automations where id = ?", (row["id"],))
    conn.commit()
    print(row["id"])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage Codex automations in SQLite.")
    parser.add_argument("--db", default=DEFAULT_DB, help="Path to codex-dev.db")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List automations")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--json", action="store_true", help="Output JSON")
    list_parser.set_defaults(func=cmd_list)

    show_parser = subparsers.add_parser("show", help="Show a single automation")
    show_parser.add_argument("--id")
    show_parser.add_argument("--name")
    show_parser.add_argument("--json", action="store_true", help="Output JSON")
    show_parser.set_defaults(func=cmd_show)

    create_parser = subparsers.add_parser("create", help="Create a new automation")
    create_parser.add_argument("--name", required=True)
    create_parser.add_argument("--prompt")
    create_parser.add_argument("--prompt-file")
    create_parser.add_argument("--rrule", required=True)
    create_parser.add_argument("--status")
    create_parser.add_argument("--cwd", action="append", help="Repeat to add multiple cwd entries")
    create_parser.add_argument("--cwds-json", help="JSON array of cwd strings")
    create_parser.add_argument("--clear-cwds", action="store_true", help="Store empty cwds list")
    create_parser.add_argument("--next-run-at", help="Unix time (ms preferred; seconds accepted)")
    create_parser.add_argument("--next-run-at-iso", help="ISO timestamp (assumes UTC if no TZ)")
    create_parser.set_defaults(func=cmd_create)

    update_parser = subparsers.add_parser("update", help="Update an automation")
    update_parser.add_argument("--id")
    update_parser.add_argument("--name")
    update_parser.add_argument("--new-name")
    update_parser.add_argument("--prompt")
    update_parser.add_argument("--prompt-file")
    update_parser.add_argument("--rrule")
    update_parser.add_argument("--status")
    update_parser.add_argument("--cwd", action="append", help="Repeat to add multiple cwd entries")
    update_parser.add_argument("--cwds-json", help="JSON array of cwd strings")
    update_parser.add_argument("--clear-cwds", action="store_true", help="Store empty cwds list")
    update_parser.add_argument("--next-run-at", help="Unix time (ms preferred; seconds accepted)")
    update_parser.add_argument("--next-run-at-iso", help="ISO timestamp (assumes UTC if no TZ)")
    update_parser.add_argument("--clear-next-run-at", action="store_true")
    update_parser.set_defaults(func=cmd_update)

    enable_parser = subparsers.add_parser("enable", help="Enable an automation")
    enable_parser.add_argument("--id")
    enable_parser.add_argument("--name")
    enable_parser.set_defaults(func=cmd_enable)

    disable_parser = subparsers.add_parser("disable", help="Disable an automation")
    disable_parser.add_argument("--id")
    disable_parser.add_argument("--name")
    disable_parser.set_defaults(func=cmd_disable)

    run_now_parser = subparsers.add_parser("run-now", help="Set next_run_at to now")
    run_now_parser.add_argument("--id")
    run_now_parser.add_argument("--name")
    run_now_parser.set_defaults(func=cmd_run_now)

    delete_parser = subparsers.add_parser("delete", help="Delete an automation")
    delete_parser.add_argument("--id")
    delete_parser.add_argument("--name")
    delete_parser.set_defaults(func=cmd_delete)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
