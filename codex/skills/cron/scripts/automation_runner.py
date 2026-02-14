#!/usr/bin/env -S uv run --with python-dateutil python
"""Headless Codex automation runner.

Runs due automations from ~/.codex/sqlite/codex-dev.db and executes prompts via
`codex exec` without requiring the desktop app to be open.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import textwrap
import time
import uuid
from pathlib import Path
from typing import Any

from dateutil import rrule

from cron import DEFAULT_DB
from cron import STATUS_ACTIVE
from cron import automation_dir
from cron import connect
from cron import write_automation_files

DEFAULT_CODEX_BIN = os.environ.get("CODEX_BIN", "codex")
RUN_STATUS_RUNNING = "RUNNING"
RUN_STATUS_SUCCESS = "PENDING_REVIEW"
RUN_STATUS_FAILED = "FAILED"
FALLBACK_NEXT_INTERVAL_MS = 24 * 60 * 60 * 1000


def now_ms() -> int:
    return int(time.time() * 1000)


def first_line(value: str, *, width: int = 120) -> str:
    for line in value.splitlines():
        cleaned = line.strip()
        if cleaned:
            return cleaned[:width]
    return ""


def first_meaningful_line(value: str, *, width: int = 220) -> str:
    for line in value.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        if cleaned.startswith("Echo:"):
            continue
        return cleaned[:width]
    return ""


def summarize_output(output: str, *, width: int = 220) -> str:
    line = first_meaningful_line(output, width=width)
    if line:
        return line
    compact = " ".join(output.strip().split())
    return compact[:width] if compact else "No output captured."


def parse_cwds(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    return [item for item in parsed if isinstance(item, str) and item.strip()]


def normalize_rrule_text(value: str) -> str:
    trimmed = value.strip()
    if trimmed.upper().startswith("RRULE:"):
        return trimmed.split(":", 1)[1].strip()
    return trimmed


def align_to_minute(value: dt.datetime) -> dt.datetime:
    return value.replace(second=0, microsecond=0)


def compute_next_run_at(row: sqlite3.Row, run_started_ms: int) -> int:
    rule_text = normalize_rrule_text(str(row["rrule"]))
    dtstart_ms = (
        int(row["next_run_at"])
        if row["next_run_at"] is not None
        else int(row["last_run_at"])
        if row["last_run_at"] is not None
        else int(row["created_at"])
    )

    dtstart = align_to_minute(dt.datetime.fromtimestamp(dtstart_ms / 1000))
    anchor = align_to_minute(dt.datetime.fromtimestamp(run_started_ms / 1000))

    parsed = rrule.rrulestr(rule_text, dtstart=dtstart)
    next_dt = parsed.after(anchor, inc=False)
    if next_dt is None:
        return run_started_ms + FALLBACK_NEXT_INTERVAL_MS
    return int(next_dt.timestamp() * 1000)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def resolve_executable(executable: str) -> str | None:
    value = executable.strip()
    if not value:
        return None
    if "/" in value:
        return value if os.path.exists(value) else None
    return shutil.which(value)


def read_file_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def write_memory_summary(automation_id: str, summary: str, run_started_ms: int) -> None:
    folder = Path(automation_dir(automation_id))
    ensure_dir(folder)
    memory_path = folder / "memory.md"

    local = dt.datetime.fromtimestamp(run_started_ms / 1000).astimezone()
    lines = [
        f"Last run summary ({local.date().isoformat()}): {summary}",
        f"Run time: {local.strftime('%Y-%m-%d %H:%M:%S %z')}",
    ]
    block = "\n".join(lines)

    existing = read_file_if_exists(memory_path)
    with memory_path.open("w", encoding="utf-8") as handle:
        if existing:
            handle.write(existing + "\n\n")
        handle.write(block + "\n")


def due_rows(conn: sqlite3.Connection, *, now: int, limit: int, automation_id: str | None) -> list[sqlite3.Row]:
    if automation_id:
        row = conn.execute("select * from automations where id = ?", (automation_id,)).fetchone()
        if row is None:
            return []
        if row["status"] != STATUS_ACTIVE:
            return []
        if row["next_run_at"] is None or int(row["next_run_at"]) <= now:
            return [row]
        return []

    rows = conn.execute(
        textwrap.dedent(
            """
            select *
            from automations
            where status = ?
              and (next_run_at is null or next_run_at <= ?)
            order by coalesce(next_run_at, 0) asc
            limit ?
            """
        ),
        (STATUS_ACTIVE, now, limit),
    ).fetchall()
    return list(rows)


def choose_cwd(row: sqlite3.Row) -> str:
    cwds = parse_cwds(row["cwds"])
    if cwds:
        return cwds[0]
    return os.getcwd()


def close_stale_running_rows(conn: sqlite3.Connection, *, automation_id: str, updated_ms: int) -> None:
    conn.execute(
        textwrap.dedent(
            """
            update automation_runs
            set status = ?,
                inbox_title = ?,
                inbox_summary = ?,
                updated_at = ?,
                archived_reason = ?
            where automation_id = ?
              and status = ?
            """
        ),
        (
            RUN_STATUS_FAILED,
            "Automation run interrupted",
            "Marked failed because a previous headless run did not close cleanly.",
            updated_ms,
            "headless_runner_interrupted",
            automation_id,
            RUN_STATUS_RUNNING,
        ),
    )
    conn.commit()


def insert_run(conn: sqlite3.Connection, row: sqlite3.Row, *, source_cwd: str, started_ms: int) -> str:
    thread_id = str(uuid.uuid4())
    thread_title = first_line(str(row["prompt"])) or str(row["name"])

    conn.execute(
        textwrap.dedent(
            """
            insert into automation_runs (
                thread_id,
                automation_id,
                status,
                read_at,
                thread_title,
                source_cwd,
                inbox_title,
                inbox_summary,
                created_at,
                updated_at,
                archived_user_message,
                archived_assistant_message,
                archived_reason
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
        ),
        (
            thread_id,
            row["id"],
            RUN_STATUS_RUNNING,
            None,
            thread_title,
            source_cwd,
            f"{row['name']} running",
            "Headless runner started this automation.",
            started_ms,
            started_ms,
            None,
            None,
            None,
        ),
    )
    conn.commit()
    return thread_id


def run_codex(*, codex_bin: str, cwd: str, prompt: str, output_file: Path) -> tuple[int, str, str, str]:
    cmd = [
        codex_bin,
        "exec",
        "--full-auto",
        "--skip-git-repo-check",
        "--cd",
        cwd,
        "--output-last-message",
        str(output_file),
        prompt,
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    output_text = output_file.read_text(encoding="utf-8").strip() if output_file.exists() else ""
    return proc.returncode, proc.stdout, proc.stderr, output_text


def update_run(
    conn: sqlite3.Connection,
    *,
    thread_id: str,
    row: sqlite3.Row,
    status: str,
    summary: str,
    assistant_message: str,
    finished_ms: int,
) -> None:
    conn.execute(
        textwrap.dedent(
            """
            update automation_runs
            set status = ?,
                inbox_title = ?,
                inbox_summary = ?,
                updated_at = ?,
                archived_user_message = ?,
                archived_assistant_message = ?,
                archived_reason = ?
            where thread_id = ?
            """
        ),
        (
            status,
            f"{row['name']} drafted" if status == RUN_STATUS_SUCCESS else f"{row['name']} failed",
            summary,
            finished_ms,
            row["prompt"],
            assistant_message,
            "headless_runner_auto_archive",
            thread_id,
        ),
    )
    conn.commit()


def update_automation_times(conn: sqlite3.Connection, *, row: sqlite3.Row, run_started_ms: int, next_run_at: int) -> None:
    conn.execute(
        "update automations set last_run_at = ?, next_run_at = ?, updated_at = ? where id = ?",
        (run_started_ms, next_run_at, now_ms(), row["id"]),
    )
    conn.commit()


def run_one(conn: sqlite3.Connection, *, row: sqlite3.Row, codex_bin: str, dry_run: bool) -> dict[str, Any]:
    started = now_ms()
    cwd = choose_cwd(row)
    close_stale_running_rows(conn, automation_id=str(row["id"]), updated_ms=started)
    thread_id = insert_run(conn, row, source_cwd=cwd, started_ms=started)

    if dry_run:
        summary = f"[dry-run] would execute in {cwd}"
        finished = now_ms()
        try:
            next_run = compute_next_run_at(row, started)
        except Exception:
            next_run = started + FALLBACK_NEXT_INTERVAL_MS
        update_run(
            conn,
            thread_id=thread_id,
            row=row,
            status=RUN_STATUS_SUCCESS,
            summary=summary,
            assistant_message=summary,
            finished_ms=finished,
        )
        update_automation_times(conn, row=row, run_started_ms=started, next_run_at=next_run)
        write_automation_files(conn, str(row["id"]))
        write_memory_summary(str(row["id"]), summary, started)
        return {"id": row["id"], "status": "dry_run", "thread_id": thread_id, "cwd": cwd}

    tmp_dir = Path.home() / ".codex" / "tmp" / "automation-runner"
    ensure_dir(tmp_dir)
    output_file = tmp_dir / f"{thread_id}.txt"

    code, stdout, stderr, output_text = run_codex(
        codex_bin=codex_bin,
        cwd=cwd,
        prompt=str(row["prompt"]),
        output_file=output_file,
    )

    finished = now_ms()
    success = code == 0
    core_text = output_text.strip() or stdout.strip() or stderr.strip()
    summary = summarize_output(core_text)
    if not success:
        summary = f"Command failed (exit {code}): {summary}"

    details = core_text
    if stderr.strip() and stderr.strip() not in details:
        details = (details + "\n\n--- STDERR ---\n" + stderr.strip()).strip()
    if not details:
        details = summary

    try:
        next_run = compute_next_run_at(row, started)
    except Exception as exc:
        next_run = started + FALLBACK_NEXT_INTERVAL_MS
        details = (details + f"\n\nRRULE parse fallback applied: {exc}").strip()

    update_run(
        conn,
        thread_id=thread_id,
        row=row,
        status=RUN_STATUS_SUCCESS if success else RUN_STATUS_FAILED,
        summary=summary,
        assistant_message=details,
        finished_ms=finished,
    )

    update_automation_times(conn, row=row, run_started_ms=started, next_run_at=next_run)
    write_automation_files(conn, str(row["id"]))
    write_memory_summary(str(row["id"]), summary, started)

    return {
        "id": row["id"],
        "status": "ok" if success else "failed",
        "thread_id": thread_id,
        "cwd": cwd,
        "next_run_at": next_run,
        "exit_code": code,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run due Codex automations without Codex.app")
    parser.add_argument("--db", default=DEFAULT_DB, help="Path to codex-dev.db")
    parser.add_argument("--once", action="store_true", help="Run one polling sweep and exit")
    parser.add_argument("--limit", type=int, default=10, help="Max due automations per sweep")
    parser.add_argument("--id", help="Run only this automation id if due")
    parser.add_argument("--dry-run", action="store_true", help="Update run metadata without calling codex exec")
    parser.add_argument(
        "--codex-bin",
        default=DEFAULT_CODEX_BIN,
        help="Codex executable name or absolute path (default: $CODEX_BIN or codex in PATH)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    codex_bin = resolve_executable(args.codex_bin)
    if codex_bin is None:
        print(f"error: codex executable not found: {args.codex_bin}", file=sys.stderr)
        sys.exit(1)

    conn = connect(args.db)
    start = now_ms()
    rows = due_rows(conn, now=start, limit=max(args.limit, 1), automation_id=args.id)

    if not rows:
        print("no due automations")
        return

    results = []
    for row in rows:
        try:
            result = run_one(conn, row=row, codex_bin=codex_bin, dry_run=args.dry_run)
        except Exception as exc:  # pragma: no cover - last-resort guard for scheduler resiliency
            result = {"id": row["id"], "status": "error", "error": str(exc)}
        results.append(result)

    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
