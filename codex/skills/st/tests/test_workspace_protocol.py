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


def run(tool: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-S", str(TOOLS / tool), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def load(name: str) -> dict:
    return json.loads((ASSETS / name).read_text(encoding="utf-8"))


def put(root: Path, name: str, value: dict) -> Path:
    path = root / name
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def expect_pass(tool: str, fixture: str, *extra: str) -> None:
    result = run(tool, str(ASSETS / fixture), *extra)
    assert result.returncode == 0, result.stdout + result.stderr


def expect_fail(tool: str, path: Path, needle: str, *extra: str) -> None:
    result = run(tool, str(path), *extra)
    assert result.returncode == 2, result.stdout + result.stderr
    assert needle in result.stdout, result.stdout


def main() -> int:
    expect_pass("workspace_gate.py", "workspace.example.json")
    expect_pass("claim_gate.py", "claim-auth.example.json")
    expect_pass(
        "claim_gate.py",
        "claim-auth.example.json",
        "--against",
        str(ASSETS / "claims-disjoint.example.json"),
    )
    expect_pass("session_view_gate.py", "session-view.example.json")
    expect_pass("gcr_v2_gate.py", "gcr-v2.example.json")
    expect_pass("changeset_gate.py", "changeset.example.json")

    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)

        # `.ledger/st` is mandatory.
        value = load("workspace.example.json")
        value["st_workspace"]["st_root"] = ".step/st"
        path = put(temp, "bad-root.json", value)
        expect_fail("workspace_gate.py", path, "st_root:must-be-.ledger/st")

        # Duplicate plan IDs are rejected.
        value = load("workspace.example.json")
        value["st_workspace"]["plans"][1]["plan_id"] = "auth-hardening"
        value["st_workspace"]["plans"][1]["graph_ref"] = (
            ".ledger/st/plans/auth-hardening/plan.jsonl"
        )
        path = put(temp, "duplicate-plan.json", value)
        expect_fail("workspace_gate.py", path, "duplicate-plan-id:auth-hardening")

        # Cross-plan refs must point to registered plans.
        value = load("workspace.example.json")
        value["st_workspace"]["cross_plan_dependencies"][0]["from"] = (
            "plan://missing/st-001"
        )
        path = put(temp, "unknown-plan-edge.json", value)
        expect_fail("workspace_gate.py", path, "unknown-plan:missing")

        # A path-overlap claim conflicts globally even when plans differ.
        value = load("claim-cache.example.json")
        value["workspace_claim"]["resources"] = [
            {"root": "path:src/auth.zig", "mode": "write"}
        ]
        other = put(temp, "conflicting-claims.json", {"workspace_claims": [value]})
        result = run(
            "claim_gate.py",
            str(ASSETS / "claim-auth.example.json"),
            "--against",
            str(other),
        )
        assert result.returncode == 2
        assert "resource-conflict" in result.stdout

        # Read/read overlap is compatible.
        left = load("claim-auth.example.json")
        left["workspace_claim"]["resources"] = [
            {"root": "path:src/auth.zig", "mode": "read"}
        ]
        right = load("claim-cache.example.json")
        right["workspace_claim"]["resources"] = [
            {"root": "path:src/auth.zig", "mode": "read"}
        ]
        left_path = put(temp, "read-left.json", left)
        right_path = put(temp, "read-right-list.json", {"workspace_claims": [right]})
        result = run(
            "claim_gate.py",
            str(left_path),
            "--against",
            str(right_path),
        )
        assert result.returncode == 0, result.stdout

        # Expired held claim fails.
        path = ASSETS / "claim-auth.example.json"
        result = run("claim_gate.py", str(path), "--now", "2026-06-25T13:00:00Z")
        assert result.returncode == 2
        assert "held-but-expired" in result.stdout

        # Stale fencing prevents execution.
        value = load("gcr-v2.example.json")
        value["graph_control_receipt"]["coordination"]["fencing_current"] = False
        path = put(temp, "stale-fence-gcr.json", value)
        expect_fail("gcr_v2_gate.py", path, "prerequisites-fail")

        # Workspace/plan lineage mismatch prevents execution.
        value = load("gcr-v2.example.json")
        value["graph_control_receipt"]["coordination"]["plan_sequence"] = 10
        path = put(temp, "stale-plan-gcr.json", value)
        expect_fail("gcr_v2_gate.py", path, "prerequisites-fail")

        # Session projection cannot differ from selected graph tasks.
        value = load("gcr-v2.example.json")
        value["graph_control_receipt"]["projection"]["selected_task_ids"] = ["st-001"]
        path = put(temp, "projection-mismatch.json", value)
        expect_fail("gcr_v2_gate.py", path, "projection.selected_task_ids:mismatch")

        # GCR-v2 must include graph intelligence, proof, and aperture rationale.
        value = load("gcr-v2.example.json")
        del value["graph_control_receipt"]["graph"]["selected_frontier"]
        path = put(temp, "missing-selected-frontier.json", value)
        expect_fail("gcr_v2_gate.py", path, "graph.selected_frontier:must-be-list")

        value = load("gcr-v2.example.json")
        del value["graph_control_receipt"]["proof"]
        path = put(temp, "missing-proof.json", value)
        expect_fail("gcr_v2_gate.py", path, "proof:must-be-object")

        value = load("gcr-v2.example.json")
        del value["graph_control_receipt"]["aperture_decision"]
        path = put(temp, "missing-aperture.json", value)
        expect_fail("gcr_v2_gate.py", path, "aperture_decision:must-be-object")

        # A change set cannot touch paths outside the claim.
        value = load("changeset.example.json")
        value["change_set"]["changed_paths"].append("src/cache.zig")
        path = put(temp, "outside-claim.json", value)
        expect_fail("changeset_gate.py", path, "changed_paths:outside-claim")

        # A repo-exclusive resource safely covers arbitrary paths.
        value = load("changeset.example.json")
        value["change_set"]["changed_paths"].append("src/cache.zig")
        value["change_set"]["resource_roots"] = [
            {"root": "repo:all", "mode": "exclusive"}
        ]
        path = put(temp, "repo-exclusive.json", value)
        result = run("changeset_gate.py", str(path))
        assert result.returncode == 0, result.stdout

    print("st multi-plan workspace protocol: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
