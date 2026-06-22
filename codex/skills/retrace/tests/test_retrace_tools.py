#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ASSETS = ROOT / "assets"


def run(tool: str, path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOLS / tool), str(path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def load(name: str) -> dict:
    return json.loads((ASSETS / name).read_text(encoding="utf-8"))


def write_json(root: Path, name: str, value: dict) -> Path:
    path = root / name
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def assert_pass(tool: str, fixture: str) -> dict:
    result = run(tool, ASSETS / fixture)
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    gate_name = tool.removesuffix(".py")
    assert payload[gate_name]["verdict"] == "pass"
    return payload[gate_name]


def main() -> int:
    fixtures = [
        ("source_governance_gate.py", "source-governance.example.json"),
        ("source_governance_gate.py", "source-governance-incidental.example.json"),
        ("dcp_gate.py", "dcp-v1.example.json"),
        ("rip_gate.py", "inquiry-plan.example.json"),
        ("fir_gate.py", "fir-v1.example.json"),
        ("fir_gate.py", "fir-v1-rollout.example.json"),
        ("drr_gate.py", "drr-v1.example.json"),
    ]
    for tool, fixture in fixtures:
        assert_pass(tool, fixture)

    rollout = assert_pass("fir_gate.py", "fir-v1-rollout.example.json")
    assert rollout["lineage_mode"] == "rollout_transcript"

    incidental = assert_pass(
        "source_governance_gate.py",
        "source-governance-incidental.example.json",
    )
    assert incidental["state"] == "incidental"
    assert incidental["replay_allowed"] is False

    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)

        bad_governance = load("source-governance-incidental.example.json")
        bad_governance["source_governance_gate"]["verdict"]["replay_allowed"] = True
        result = run(
            "source_governance_gate.py",
            write_json(temp, "bad-governance.json", bad_governance),
        )
        assert result.returncode == 2
        assert "blocked-state-must-deny" in result.stdout

        bad_authoritative = load("source-governance.example.json")
        bad_authoritative["source_governance_gate"]["classification"][
            "governance_provenance"
        ] = "filename_or_path_mention"
        result = run(
            "source_governance_gate.py",
            write_json(temp, "bad-authoritative.json", bad_authoritative),
        )
        assert result.returncode == 2
        assert "controller-governance-required" in result.stdout

        bad_dcp = load("dcp-v1.example.json")
        bad_dcp["decision_context_packet"]["anchors"]["pre_decision"][
            "drop_last_n_turns"
        ] = 1
        result = run("dcp_gate.py", write_json(temp, "bad-dcp.json", bad_dcp))
        assert result.returncode == 2
        assert "keep-plus-drop-must-equal-total" in result.stdout

        bad_plan = load("inquiry-plan.example.json")
        bad_plan["retrace_inquiry_plan"]["budgets"]["max_forks"] = 1
        result = run("rip_gate.py", write_json(temp, "bad-plan.json", bad_plan))
        assert result.returncode == 2
        assert "max-forks-exceeded" in result.stdout

        bad_fir = load("fir-v1.example.json")
        bad_fir["fork_inquiry_receipt"]["answer"]["hindsight_available"] = True
        result = run("fir_gate.py", write_json(temp, "bad-fir.json", bad_fir))
        assert result.returncode == 2
        assert "outcome-blind-must-be-false" in result.stdout

        bad_rollout = load("fir-v1-rollout.example.json")
        bad_rollout["fork_inquiry_receipt"]["workspace_reconstruction"][
            "mode"
        ] = "head_only"
        result = run(
            "fir_gate.py",
            write_json(temp, "bad-rollout.json", bad_rollout),
        )
        assert result.returncode == 2
        assert "workspace-must-be-transcript-only" in result.stdout

        bad_drr = load("drr-v1.example.json")
        bad_drr["decision_reconstruction_record"]["hindsight"][
            "kept_separate"
        ] = "no"
        result = run("drr_gate.py", write_json(temp, "bad-drr.json", bad_drr))
        assert result.returncode == 2
        assert "hindsight.kept_separate" in result.stdout

        blocked_drr = load("drr-v1.example.json")
        sg = blocked_drr["decision_reconstruction_record"]["source_governance"]
        sg["verdict"] = "incidental"
        sg["replay_allowed"] = False
        blocked_drr["decision_reconstruction_record"]["fork_population"][
            "valid_receipts"
        ] = ["FIR-should-not-exist"]
        result = run(
            "drr_gate.py",
            write_json(temp, "blocked-drr.json", blocked_drr),
        )
        assert result.returncode == 2
        assert "blocked-verdict-has-valid-receipts" in result.stdout

    print("retrace tools: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
