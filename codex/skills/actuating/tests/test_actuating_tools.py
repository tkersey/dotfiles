#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ASSETS = ROOT / "assets"
sys.path.insert(0, str(TOOLS))

from actuation_slice_gate import validate_slice  # noqa: E402


def run(tool: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOLS / tool), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=20,
    )


def load(name: str) -> dict:
    return json.loads((ASSETS / name).read_text(encoding="utf-8"))


def put(root: Path, name: str, value: dict) -> Path:
    path = root / name
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def assert_cli_pass(tool: str, fixture: str, key: str) -> dict:
    result = run(tool, str(ASSETS / fixture))
    assert result.returncode == 0, result.stdout + result.stderr
    body = json.loads(result.stdout)[key]
    assert body["verdict"] == "pass", body
    return body


def main() -> int:
    standard = load("actuation-slice.example.json")["actuation_slice"]
    errors, warnings = validate_slice(standard)
    assert not errors, errors

    policy_slice = load("actuation-slice.policy.example.json")["actuation_slice"]
    errors, warnings = validate_slice(policy_slice)
    assert not errors, errors
    assert policy_slice["policy_control"]["action_id"] == "ACT-MUTATE-1"

    bad_asl = deepcopy(standard)
    bad_asl["task_control"]["gcr_current"] = "no"
    errors, _ = validate_slice(bad_asl)
    assert "gate.mutation_allowed:prerequisites-fail" in errors

    bad_policy = deepcopy(policy_slice)
    bad_policy["task_control"]["policy_action_id"] = "ACT-OTHER"
    errors, _ = validate_slice(bad_policy)
    assert "task_control.policy_action_id:mismatch" in errors

    bad_authority = deepcopy(policy_slice)
    bad_authority["policy_control"]["decision_mutation_authority"] = "yes"
    errors, _ = validate_slice(bad_authority)
    assert "policy_control.decision_mutation_authority:must-be-no" in errors

    new_observation = deepcopy(standard)
    new_observation["semantic_control"]["new_observations"] = [
        "new authority owner"
    ]
    errors, _ = validate_slice(new_observation)
    assert "new-observation-with-mutation-allowed" in errors

    # Keep CLI smoke coverage for matrix and proof DAG validators.
    assert_cli_pass(
        "validation_matrix_gate.py",
        "validation-matrix.example.json",
        "validation_matrix_gate",
    )
    assert_cli_pass(
        "proof_dag_gate.py",
        "proof-dag.example.json",
        "proof_dag_gate",
    )
    quick = run("quick_validate.py")
    assert quick.returncode == 0, quick.stdout + quick.stderr
    quick_body = json.loads(quick.stdout)["actuating_quick_validate"]
    quick_paths = {row["path"] for row in quick_body["tests"]}
    assert "tests/test_actuation_terminal_gate.py" in quick_paths

    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)

        duplicate = load("validation-matrix.example.json")
        rows = duplicate["validation_matrix"]["rows"]
        clone = deepcopy(rows[0])
        clone["row_id"] = "VMX-row-duplicate"
        clone["status"] = "open"
        rows.append(clone)
        path = put(temp, "duplicate-matrix.json", duplicate)
        result = run("validation_matrix_gate.py", str(path))
        assert result.returncode == 2
        assert "duplicate-semantic-row" in result.stdout

        cyclic = load("proof-dag.example.json")
        nodes = cyclic["proof_dag"]["nodes"]
        nodes[0]["depends_on"] = [nodes[-1]["proof_id"]]
        path = put(temp, "cyclic-proof.json", cyclic)
        result = run("proof_dag_gate.py", str(path))
        assert result.returncode == 2
        assert "cycle:" in result.stdout

        # Checkpoint persistence and resume remain part of the complete overlay.
        store = temp / "store"
        result = run(
            "actuation_checkpoint.py",
            "write",
            "--input",
            str(ASSETS / "actuation-slice.example.json"),
            "--root",
            str(store),
        )
        assert result.returncode == 0, result.stdout + result.stderr
        current = store / "ACT-example-001" / "current.json"
        assert current.exists()

        result = run(
            "actuation_checkpoint.py",
            "resume",
            "--root",
            str(store),
            "--run-id",
            "ACT-example-001",
        )
        assert result.returncode == 0, result.stdout + result.stderr
        packet = json.loads(result.stdout)["actuation_resume_packet"]
        assert packet["verdict"] == "pass"
        assert packet["semantic_frontier"]["selected_rows"] == ["VMX-row-002"]

        default_result = subprocess.run(
            [
                sys.executable,
                str(TOOLS / "actuation_checkpoint.py"),
                "write",
                "--input",
                str(ASSETS / "actuation-slice.example.json"),
            ],
            cwd=temp,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=20,
        )
        assert default_result.returncode == 0, default_result.stdout + default_result.stderr
        assert (temp / ".ledger" / "actuating" / "ACT-example-001" / "current.json").exists()

    print("actuating frontier tools: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
