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


def run(summary: Path, runs: Path, *extra: str, campaign: str | None = "C3-test") -> subprocess.CompletedProcess[str]:
    args = [
        sys.executable,
        str(TOOL),
    ]
    if campaign is not None:
        args.extend(["--campaign", campaign])
    args.extend(
        [
            "--summary",
            str(summary),
            "--runs",
            str(runs),
            *extra,
        ]
    )
    return subprocess.run(
        args,
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
        "closure_gate": {"status": "passed"},
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

        result = run(summary, runs, campaign=None)
        assert result.returncode == 0, result.stdout + result.stderr
        assert body(result)["closure_allowed"] is True

        blockers = {
            "c3_required_without_c3_closure": {"c3_closed": False},
            "c3_required_without_c3_entry": {"c3_required": False, "c3_entered": False},
            "compression_state_none": {"compression_state": "NONE"},
            "finding_workflow_without_batches": {"batches_total": 0},
            "open_batches": {"open_batch_ids": ["RB-open"]},
            "delivery_not_closed": {"delivery_closed": False},
            "delivery_closed_without_terminal_closure": {"terminal_closed": False},
            "strict_progress_zero": {"potential": {"strict_progress": 0}},
            "strict_progress_negative": {"potential": {"strict_progress": -1}},
            "closure_gate_not_passed": {"closure_gate": {"status": "blocked"}},
            "kernel_not_accepted": {"kernel": {"accepted": False}},
            "orphan_code_constructs": {"orphan_code_constructs": 1},
            "unmapped_proof_actions": {"unmapped_proof_actions": 1},
            "unmapped_wound_specific_tests": {"wound_specific_tests": 1},
            "semantic_surface_delta_without_ac_rebase": {"semantic_surface_delta": 1},
            "unresolved_conformance_evidence": {"conformance": {"novel_in_horizon_counterexamples": 1}},
            "unresolved_terminal_holdout_evidence": {"terminal_holdout": {"unknown_counterexamples": 1}},
            "proof_or_delivery_not_current": {"proof_basis": {"all_laws_covered": "no"}},
        }
        for code, overrides in blockers.items():
            summary, runs = write_case(root, {"campaign_id": "C3-test", "c3_required": True, "strict_progress": 1}, [healthy_row(**overrides)])
            result = run(summary, runs)
            assert result.returncode == 2, (code, result.stdout, result.stderr)
            codes = {item["code"] for item in body(result)["violations"]}
            expected = "strict_progress_zero" if code == "strict_progress_negative" else code
            assert expected in codes, (code, codes, result.stdout)

        summary, runs = write_case(root, {"campaign_id": "C3-test", "c3_required": True, "strict_progress": 1}, [healthy_row(compression_state="")])
        result = run(summary, runs)
        assert result.returncode == 2, result.stdout
        assert "compression_state_none" in {item["code"] for item in body(result)["violations"]}

        summary, runs = write_case(root, {"campaign_id": "C3-test", "c3_required": True, "strict_progress": 1}, [healthy_row(compression_state=" NONE ")])
        result = run(summary, runs)
        assert result.returncode == 2, result.stdout
        assert "compression_state_none" in {item["code"] for item in body(result)["violations"]}

        summary, runs = write_case(root, {"campaign_id": "C3-test", "c3_required": True, "strict_progress": 1}, [healthy_row(material=False, compression_state="NONE")])
        result = run(summary, runs)
        assert result.returncode == 2, result.stdout
        assert "compression_state_none" in {item["code"] for item in body(result)["violations"]}

        summary, runs = write_case(root, {"campaign_id": "C3-test", "c3_required": True, "strict_progress": 1}, [healthy_row(realization_map={"orphan_code_constructs": ["helper"]})])
        result = run(summary, runs)
        assert result.returncode == 2, result.stdout
        assert "orphan_code_constructs" in {item["code"] for item in body(result)["violations"]}

        summary, runs = write_case(root, {"campaign_id": "C3-test", "c3_required": True, "strict_progress": 1}, [healthy_row(proof_basis={"unmapped_proof_actions": ["manual"], "wound_specific_tests": ["test"]})])
        result = run(summary, runs)
        codes = {item["code"] for item in body(result)["violations"]}
        assert "unmapped_proof_actions" in codes, result.stdout
        assert "unmapped_wound_specific_tests" in codes, result.stdout

        summary, runs = write_case(root, {"campaign_id": "C3-test", "c3_required": True, "strict_progress": 1}, [healthy_row(delivery={"current_head_validation_passed": "no"})])
        result = run(summary, runs)
        assert result.returncode == 2, result.stdout
        assert "proof_or_delivery_not_current" in {item["code"] for item in body(result)["violations"]}

        summary, runs = write_case(root, {"campaign_id": "C3-test", "c3_required": True, "strict_progress": 1}, [healthy_row(wound_specific_tests=1, wound_specific_tests_class_mapped=True)])
        assert run(summary, runs).returncode == 0

        summary, runs = write_case(root, {"campaign_id": "C3-test", "c3_required": True, "strict_progress": 1}, [healthy_row(semantic_surface_delta=1, explicit_ac_rebase=True)])
        assert run(summary, runs).returncode == 0

        summary, runs = write_case(root, {"campaign_id": "C3-test", "finding_bearing_workflow": True, "strict_progress": 0, "runs_total": 4}, [])
        result = run(summary, runs)
        assert result.returncode == 2, result.stdout
        assert "material_campaign_without_runs" in {item["code"] for item in body(result)["violations"]}

        summary, runs = write_case(root, {"campaigns": [{"campaign_id": "C3-test", "finding_bearing_workflow": True, "strict_progress": 0}]}, [])
        result = run(summary, runs)
        assert result.returncode == 2, result.stdout
        assert "material_campaign_without_runs" in {item["code"] for item in body(result)["violations"]}

        summary, runs = write_case(root, {"campaigns": {"C3-test": {"finding_bearing_workflow": True, "strict_progress": 0}}}, [])
        result = run(summary, runs)
        assert result.returncode == 2, result.stdout
        assert "material_campaign_without_runs" in {item["code"] for item in body(result)["violations"]}

        result = run(summary, runs, campaign=None)
        assert result.returncode == 2, result.stdout
        assert "material_campaign_without_runs" in {item["code"] for item in body(result)["violations"]}

        summary, runs = write_case(root, {"campaign_id": "C3-test"}, [{"campaign_id": "C3-test", "run_id": "incidental", "path": ".step/resolve-c3-st-plan.jsonl"}])
        result = run(summary, runs)
        assert result.returncode == 0, result.stdout

        summary, runs = write_case(root, {"campaign_id": "C3-test", "c3_required": True, "strict_progress": 1}, [healthy_row(campaign_id="other")])
        result = run(summary, runs)
        assert result.returncode == 2, result.stdout

        flat_campaign = healthy_row()
        flat_campaign.pop("campaign_id")
        flat_campaign["campaign"] = "C3-test"
        summary, runs = write_case(root, {"campaign_id": "C3-test", "c3_required": True, "strict_progress": 1}, [flat_campaign])
        result = run(summary, runs)
        assert result.returncode == 0, result.stdout

        summary, runs = write_case(
            root,
            {"campaigns": [{"campaign_id": "C3-test"}, {"campaign_id": "other"}]},
            [healthy_row(), healthy_row(campaign_id="other", run_id="run-other")],
        )
        result = run(summary, runs, campaign=None)
        assert result.returncode == 3, result.stdout + result.stderr
        assert body(result)["status"] == "error"
        assert "multiple campaigns" in body(result)["violations"][0]["detail"]

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
