#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ACT_TOOLS = ROOT / "tools"
ACT_ASSETS = ROOT / "assets"
FP_ROOT = ROOT.parent / "fixed-point-driver"
FP_TOOLS = FP_ROOT / "tools"
FP_ASSETS = FP_ROOT / "assets"


def run(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(root: Path, name: str, value: dict) -> Path:
    path = root / name
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def main() -> int:
    afr_result = run(ACT_TOOLS / "afr_gate.py", str(ACT_ASSETS / "afr-v1.example.json"))
    assert afr_result.returncode == 0, afr_result.stdout + afr_result.stderr
    afr_gate = json.loads(afr_result.stdout)["afr_gate"]
    assert afr_gate["verdict"] == "pass"
    assert afr_gate["mutation_allowed"] is True

    asr_result = run(
        ACT_TOOLS / "asr_gate.py",
        str(ACT_ASSETS / "asr-v2.example.json"),
        "--mode",
        "ship",
    )
    assert asr_result.returncode == 0, asr_result.stdout + asr_result.stderr
    assert json.loads(asr_result.stdout)["asr_gate"]["ship_ready"] is True

    arh_result = run(FP_TOOLS / "arh_gate.py", str(FP_ASSETS / "arh-v1.example.json"))
    assert arh_result.returncode == 0, arh_result.stdout + arh_result.stderr
    assert json.loads(arh_result.stdout)["arh_gate"]["implementation_allowed"] is True

    fpsr_result = run(
        FP_TOOLS / "fpsr_gate.py",
        str(FP_ASSETS / "fpsr-v1.example.json"),
        "--handoff",
        str(FP_ASSETS / "arh-v1.example.json"),
    )
    assert fpsr_result.returncode == 0, fpsr_result.stdout + fpsr_result.stderr
    assert json.loads(fpsr_result.stdout)["fpsr_gate"]["result"] == "valid"

    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)

        # Material mutation must fail with blocking graph debt.
        afr = load(ACT_ASSETS / "afr-v1.example.json")
        afr["actuation_frontier"]["graph_binding"]["blocking_debt"] = ["debt-001"]
        path = write_json(temp, "afr-debt.json", afr)
        result = run(ACT_TOOLS / "afr_gate.py", str(path))
        assert result.returncode == 2
        assert "blocking_debt:not-empty" in result.stdout

        # Selected route must be declared as an alternative.
        afr = load(ACT_ASSETS / "afr-v1.example.json")
        afr["actuation_frontier"]["decision"]["selected_route"] = "canonicalize"
        path = write_json(temp, "afr-route.json", afr)
        result = run(ACT_TOOLS / "afr_gate.py", str(path))
        assert result.returncode == 2
        assert "not-in-alternatives" in result.stdout

        # A return-to-frontier result never authorizes more mutation under the old AFR.
        afr = load(ACT_ASSETS / "afr-v1.example.json")
        afr["actuation_frontier"]["realization"]["result"] = "return_to_frontier"
        afr["actuation_frontier"]["realization"]["new_observations"] = ["new class"]
        path = write_json(temp, "afr-return.json", afr)
        result = run(ACT_TOOLS / "afr_gate.py", str(path))
        assert result.returncode == 0
        payload = json.loads(result.stdout)["afr_gate"]
        assert payload["mutation_allowed"] is False
        assert "realization:return-to-frontier-requires-new-afr" in payload["warnings"]

        # Ship gate fails with an open frontier.
        asr = load(ACT_ASSETS / "asr-v2.example.json")
        asr["actuation_state"]["frontiers"].update(
            {"terminal": 0, "open": 1}
        )
        path = write_json(temp, "asr-open.json", asr)
        result = run(ACT_TOOLS / "asr_gate.py", str(path), "--mode", "ship")
        assert result.returncode == 2
        assert "ship:gate-not-satisfied" in result.stdout

        # A non-implementation route cannot be handed to fixed-point realization.
        arh = load(FP_ASSETS / "arh-v1.example.json")
        arh["actuation_realization_handoff"]["selected_route"] = "validate_only"
        path = write_json(temp, "arh-invalid-route.json", arh)
        result = run(FP_TOOLS / "arh_gate.py", str(path))
        assert result.returncode == 2
        assert "not-implementation-capable" in result.stdout

        # A valid result cannot contain a new observation.
        fpsr = load(FP_ASSETS / "fpsr-v1.example.json")
        fpsr["fixed_point_slice_result"]["new_observations"] = ["different owner"]
        path = write_json(temp, "fpsr-observation.json", fpsr)
        result = run(FP_TOOLS / "fpsr_gate.py", str(path))
        assert result.returncode == 2
        assert "valid:new-observations" in result.stdout

        # Surface budget is checked against the handoff.
        fpsr = load(FP_ASSETS / "fpsr-v1.example.json")
        fpsr["fixed_point_slice_result"]["surfaces"]["helpers_added"] = 1
        path = write_json(temp, "fpsr-budget.json", fpsr)
        result = run(
            FP_TOOLS / "fpsr_gate.py",
            str(path),
            "--handoff",
            str(FP_ASSETS / "arh-v1.example.json"),
        )
        assert result.returncode == 2
        assert "surface-budget-exceeded:helpers_added" in result.stdout

        # Resume requires the same run/GCR/artifact state.
        state = load(ACT_ASSETS / "asr-v2.example.json")
        frontier = load(ACT_ASSETS / "afr-v1.example.json")
        # Align final state with active frontier for a valid resume fixture.
        state["actuation_state"]["artifact_state"] = frontier["actuation_frontier"]["artifact_state"]
        state["actuation_state"]["control"]["gcr_id"] = frontier["actuation_frontier"]["graph_binding"]["gcr_id"]
        state_path = write_json(temp, "resume-state.json", state)
        frontier_path = write_json(temp, "resume-frontier.json", frontier)
        result = run(
            ACT_TOOLS / "actuation_resume.py",
            "--state",
            str(state_path),
            "--frontier",
            str(frontier_path),
            "--format",
            "json",
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert json.loads(result.stdout)["actuation_resume"]["valid"] is True

    print("actuating frontier-control tools: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
