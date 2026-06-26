#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

RESOLVE = Path(__file__).resolve().parents[1]
TOOL = RESOLVE / "tools/resolve_closure_gate.py"
FORBIDDEN_TEXT = ("closed", "resolved", "complete", "ready", "landed", "shipped", "all set")


def write_case(root: Path, summary: dict, rows: list[dict]) -> tuple[Path, Path]:
    summary_path = root / "summary.json"
    runs_path = root / "runs.jsonl"
    summary_path.write_text(json.dumps(summary), encoding="utf-8")
    runs_path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    return summary_path, runs_path


def run(summary: Path, runs: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(TOOL),
            "--campaign",
            "C3-test",
            "--summary",
            str(summary),
            "--runs",
            str(runs),
            *extra,
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def body(result: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(result.stdout)


def healthy_row(**overrides: object) -> dict:
    row = {
        "campaign_id": "C3-test",
        "run_id": "run-1",
        "c3_required": True,
        "c3_entered": True,
        "c3_closed": True,
        "compression_state": "CEB-v2",
        "finding_bearing_workflow": True,
        "batches_total": 2,
        "kernel": {"accepted": True},
        "potential": {"strict_progress": 1},
        "delivery_closed": True,
        "terminal_closed": True,
        "orphan_code_constructs": 0,
        "unmapped_proof_actions": 0,
        "wound_specific_tests": 0,
        "semantic_surface_delta": 0,
    }
    row.update(overrides)
    return row


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        summary, runs = write_case(root, {"campaign_id": "C3-test", "c3_required": True, "strict_progress": 1}, [healthy_row()])
        result = run(summary, runs)
        assert result.returncode == 0, result.stdout + result.stderr
        assert body(result)["closure_allowed"] is True

        blockers = {
            "c3_required_without_c3_closure": {"c3_closed": False},
            "c3_required_without_c3_entry": {"c3_entered": False},
            "compression_state_none": {"compression_state": "NONE"},
            "finding_workflow_without_batches": {"batches_total": 0},
            "delivery_closed_without_terminal_closure": {"terminal_closed": False},
            "strict_progress_zero": {"potential": {"strict_progress": 0}},
            "kernel_not_accepted": {"kernel": {"accepted": False}},
            "orphan_code_constructs": {"orphan_code_constructs": 1},
            "unmapped_proof_actions": {"unmapped_proof_actions": 1},
            "unmapped_wound_specific_tests": {"wound_specific_tests": 1},
            "semantic_surface_delta_without_ac_rebase": {"semantic_surface_delta": 1},
        }
        for code, overrides in blockers.items():
            summary, runs = write_case(root, {"campaign_id": "C3-test", "c3_required": True, "strict_progress": 1}, [healthy_row(**overrides)])
            result = run(summary, runs)
            assert result.returncode == 2, (code, result.stdout, result.stderr)
            codes = {item["code"] for item in body(result)["violations"]}
            assert code in codes, (code, codes, result.stdout)

        summary, runs = write_case(root, {"campaign_id": "C3-test", "c3_required": True, "strict_progress": 1}, [healthy_row(wound_specific_tests=1, wound_specific_tests_class_mapped=True)])
        assert run(summary, runs).returncode == 0

        summary, runs = write_case(root, {"campaign_id": "C3-test", "c3_required": True, "strict_progress": 1}, [healthy_row(semantic_surface_delta=1, explicit_ac_rebase=True)])
        assert run(summary, runs).returncode == 0

        summary, runs = write_case(root, {"campaign_id": "C3-test", "finding_bearing_workflow": True, "strict_progress": 0}, [])
        result = run(summary, runs)
        assert result.returncode == 2, result.stdout
        assert "material_campaign_without_runs" in {item["code"] for item in body(result)["violations"]}

        summary, runs = write_case(root, {"campaign_id": "C3-test"}, [{"campaign_id": "C3-test", "run_id": "incidental", "path": ".step/resolve-c3-st-plan.jsonl"}])
        result = run(summary, runs)
        assert result.returncode == 0, result.stdout

        summary, runs = write_case(root, {"campaign_id": "C3-test", "c3_required": True, "strict_progress": 1}, [healthy_row(campaign_id="other")])
        result = run(summary, runs)
        assert result.returncode == 2, result.stdout

        summary, runs = write_case(root, {"campaign_id": "C3-test", "c3_required": True, "strict_progress": 1}, [healthy_row(terminal_closed=False)])
        result = run(summary, runs, "--format", "text")
        assert result.returncode == 2, result.stdout
        lowered = result.stdout.lower()
        for word in FORBIDDEN_TEXT:
            assert word not in lowered, (word, result.stdout)
        assert "closure gate failed" in lowered, result.stdout

        bad = root / "bad.json"
        bad.write_text("{bad", encoding="utf-8")
        result = run(bad, runs)
        assert result.returncode == 3, result.stdout + result.stderr
        assert body(result)["status"] == "error"

    print("resolve closure gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
