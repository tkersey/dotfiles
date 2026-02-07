#!/usr/bin/env -S uv run python
"""Smoke test for `$st` to `update_plan` sync behavior."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ST_PLAN_SCRIPT = Path(__file__).with_name("st_plan.py")
STATUS_MAP = {
    "in_progress": "in_progress",
    "completed": "completed",
    "pending": "pending",
    "blocked": "pending",
    "deferred": "pending",
    "canceled": "pending",
}


def run_st_plan(*args: str, expect_success: bool = True) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(ST_PLAN_SCRIPT), *args]
    proc = subprocess.run(command, capture_output=True, text=True)
    if expect_success and proc.returncode != 0:
        joined = " ".join(command)
        raise AssertionError(
            f"command failed: {joined}\nexit={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
    return proc


def show_json(plan_file: Path) -> list[dict[str, Any]]:
    proc = run_st_plan("show", "--file", str(plan_file), "--format", "json")
    payload = json.loads(proc.stdout)
    return payload["items"]


def item_map(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in items}


def build_codex_plan(items: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [{"step": item["step"], "status": STATUS_MAP[item["status"]]} for item in items]


def assert_no_drift(st_items: list[dict[str, Any]], codex_plan: list[dict[str, str]]) -> None:
    if len(st_items) != len(codex_plan):
        raise AssertionError("drift: item count mismatch between st and codex plan")

    for st_item, codex_item in zip(st_items, codex_plan):
        expected_status = STATUS_MAP[st_item["status"]]
        if codex_item["step"] != st_item["step"] or codex_item["status"] != expected_status:
            raise AssertionError(
                "drift: codex plan differs from st mapping for "
                f"{st_item['id']} (expected step={st_item['step']}, status={expected_status})"
            )
        if st_item["dep_state"] == "waiting_on_deps" and codex_item["status"] == "in_progress":
            raise AssertionError(
                f"drift: {st_item['id']} is waiting_on_deps but codex plan marked it in_progress"
            )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="st-smoke-sync-") as tmp_dir:
        plan_file = Path(tmp_dir) / "st-plan.jsonl"

        run_st_plan("init", "--file", str(plan_file))
        run_st_plan(
            "add",
            "--file",
            str(plan_file),
            "--id",
            "st-001",
            "--step",
            "Reproduce failing test",
            "--status",
            "pending",
            "--deps",
            "",
        )
        run_st_plan(
            "add",
            "--file",
            str(plan_file),
            "--id",
            "st-002",
            "--step",
            "Patch core logic",
            "--status",
            "pending",
            "--deps",
            "st-001",
        )
        run_st_plan(
            "add",
            "--file",
            str(plan_file),
            "--id",
            "st-003",
            "--step",
            "Document rollout",
            "--status",
            "blocked",
            "--deps",
            "",
        )

        initial_items = show_json(plan_file)
        by_id = item_map(initial_items)
        if by_id["st-001"]["dep_state"] != "ready":
            raise AssertionError("st-001 should be ready")
        if by_id["st-002"]["dep_state"] != "waiting_on_deps":
            raise AssertionError("st-002 should be waiting_on_deps")
        if by_id["st-002"]["waiting_on"] != ["st-001"]:
            raise AssertionError("st-002 should be waiting on st-001")
        if by_id["st-003"]["dep_state"] != "blocked_manual":
            raise AssertionError("st-003 should be blocked_manual")

        codex_initial = build_codex_plan(initial_items)
        assert_no_drift(initial_items, codex_initial)

        blocked_progress = run_st_plan(
            "set-status",
            "--file",
            str(plan_file),
            "--id",
            "st-002",
            "--status",
            "in_progress",
            expect_success=False,
        )
        error_text = f"{blocked_progress.stdout}\n{blocked_progress.stderr}"
        if blocked_progress.returncode == 0 or "unresolved dependencies" not in error_text:
            raise AssertionError("dependency gating failed: st-002 advanced before deps completed")

        run_st_plan("set-status", "--file", str(plan_file), "--id", "st-001", "--status", "completed")
        run_st_plan("set-status", "--file", str(plan_file), "--id", "st-002", "--status", "in_progress")
        run_st_plan("set-status", "--file", str(plan_file), "--id", "st-003", "--status", "pending")
        run_st_plan("set-deps", "--file", str(plan_file), "--id", "st-003", "--deps", "st-002")

        mid_items = show_json(plan_file)
        mid_by_id = item_map(mid_items)
        if mid_by_id["st-003"]["dep_state"] != "waiting_on_deps":
            raise AssertionError("st-003 should be waiting_on_deps after set-deps")
        if mid_by_id["st-003"]["waiting_on"] != ["st-002"]:
            raise AssertionError("st-003 should be waiting on st-002")

        codex_mid = build_codex_plan(mid_items)
        assert_no_drift(mid_items, codex_mid)

        invalid_complete = run_st_plan(
            "set-status",
            "--file",
            str(plan_file),
            "--id",
            "st-003",
            "--status",
            "completed",
            expect_success=False,
        )
        invalid_text = f"{invalid_complete.stdout}\n{invalid_complete.stderr}"
        if invalid_complete.returncode == 0 or "unresolved dependencies" not in invalid_text:
            raise AssertionError("dependency gating failed: st-003 completed before deps completed")

        run_st_plan("set-status", "--file", str(plan_file), "--id", "st-002", "--status", "completed")
        run_st_plan("set-status", "--file", str(plan_file), "--id", "st-003", "--status", "completed")

        final_items = show_json(plan_file)
        codex_final = build_codex_plan(final_items)
        assert_no_drift(final_items, codex_final)

    print("st smoke sync: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
