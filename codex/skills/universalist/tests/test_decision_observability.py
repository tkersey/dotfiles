#!/usr/bin/env python3
"""Focused proof for Universalist SKDC-v1 and SDR-v1 observability."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Sequence


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[2]
SKILL = SKILL_ROOT / "SKILL.md"
EMITTER = SKILL_ROOT / "scripts" / "emit_decision_receipt.py"
CONTRACT = SKILL_ROOT / "references" / "decision-contract.yaml"
PLAN_TEMPLATE = SKILL_ROOT / "templates" / "universalist-plan.md"
SDR_GATE = SKILL_ROOT.parent / "tune" / "tools" / "sdr_gate.py"


def run(command: Sequence[str], *, expected: int = 0) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != expected:
        raise AssertionError(
            f"expected exit {expected}, got {completed.returncode}: {' '.join(command)}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    return completed


def load_emitter() -> Any:
    spec = importlib.util.spec_from_file_location("universalist_receipt", EMITTER)
    if spec is None or spec.loader is None:
        raise AssertionError("unable to load the decision receipt emitter")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DecisionObservabilityTest(unittest.TestCase):
    maxDiff = None

    def test_trigger_to_evidence_kernel_precedes_doctrine(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        trigger = text.index("## Boundary-trigger mandate")
        kernel = text.index("## Trigger-to-evidence kernel")
        doctrine = text.index("## Doctrine index")
        step_zero = text.index("## Step 0 — Allocate a ledger-addressed plan")
        observability = text.index("## Decision observability")

        self.assertLess(trigger, kernel)
        self.assertLess(kernel, doctrine)
        self.assertLess(doctrine, step_zero)
        self.assertLess(step_zero, observability)
        for required in (
            "Record the compact boundary disposition immediately",
            "allocate one fresh ledger-addressed Universalist plan",
            "complete this gate before mutating the seam",
            "Do not allocate a plan or emit `SDR-v1` solely because the skill activated",
        ):
            self.assertIn(required, text)

    def emitter_command(self) -> list[str]:
        return [
            sys.executable,
            str(EMITTER),
            "--plan",
            str(PLAN_TEMPLATE),
            "--decision-id",
            "UNI-TEST-001",
            "--question",
            "Which boundary route makes the decision observable?",
            "--selected-route",
            "UNI-ORDINARY",
            "--rejected-route",
            "UNI-CANONICAL",
            "--expected-outcome",
            "One plan-bound root receipt becomes a Seq decision episode.",
            "--disposition",
            "introduced",
            "--construction",
            "SKDC-v1 plus one SDR-v1 projection",
            "--law",
            "One consequential seam produces exactly one valid root receipt.",
            "--falsifier",
            "A duplicate receipt or unknown route is rejected.",
            "--advanced-mechanics",
            "none",
            "--evidence-ref",
            "test:decision-observability",
        ]

    def test_plan_append_is_exactly_once(self) -> None:
        emitter = load_emitter()
        with tempfile.TemporaryDirectory() as directory:
            plan = Path(directory) / "plan-test.md"
            plan.write_text(
                "---\nschema: universalist-plan/v1\nplan_id: test\n---\n\n"
                + PLAN_TEMPLATE.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            receipt = json.dumps(
                {
                    "skill_decision_receipt": {
                        "receipt_version": "SDR-v1",
                        "decision_id": "UNI-TEST-001",
                        "skill": "universalist",
                        "selected_route": "UNI-ORDINARY",
                        "rejected_routes": ["UNI-CANONICAL"],
                        "artifact_state": {"plan_id": "test"},
                    }
                },
                separators=(",", ":"),
                sort_keys=True,
            )
            emitter.append_receipt(plan, receipt, "UNI-TEST-001")
            text = plan.read_text(encoding="utf-8")
            self.assertEqual(text.count('"skill_decision_receipt"'), 1)
            self.assertIn("## Root decision receipt: emitted (UNI-TEST-001)", text)
            validation = run(
                [
                    "seq",
                    "skill-decision-receipt",
                    "validate",
                    "--file",
                    str(plan),
                    "--format",
                    "json",
                ]
            )
            self.assertTrue(
                json.loads(validation.stdout)["skill_decision_receipt"]["valid"]
            )
            with self.assertRaises(emitter.ReceiptError):
                emitter.append_receipt(plan, receipt, "UNI-TEST-001")

    def test_receipt_validates_and_becomes_one_seq_episode(self) -> None:
        emitted = run(self.emitter_command())
        receipt = json.loads(emitted.stdout)
        body = receipt["skill_decision_receipt"]
        self.assertEqual(body["selected_route"], "UNI-ORDINARY")
        self.assertEqual(body["rejected_routes"], ["UNI-CANONICAL"])
        self.assertEqual(body["artifact_state"]["advanced_mechanics"], "none")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            receipt_path = root / "receipt.json"
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            seq_validation = run(
                [
                    "seq",
                    "skill-decision-receipt",
                    "validate",
                    "--file",
                    str(receipt_path),
                    "--format",
                    "json",
                ]
            )
            self.assertTrue(
                json.loads(seq_validation.stdout)["skill_decision_receipt"]["valid"]
            )
            python_validation = run([sys.executable, str(SDR_GATE), str(receipt_path)])
            self.assertEqual(
                json.loads(python_validation.stdout)["sdr_gate"]["verdict"], "pass"
            )

            session_id = "019f0000-0000-7000-8000-000000000001"
            session_dir = root / "2026" / "07" / "15"
            session_dir.mkdir(parents=True)
            session_path = session_dir / f"rollout-test-{session_id}.jsonl"
            rows = [
                {
                    "type": "session_meta",
                    "timestamp": "2026-07-15T12:00:00Z",
                    "payload": {"id": session_id, "cwd": str(REPO_ROOT)},
                },
                {
                    "type": "response_item",
                    "timestamp": "2026-07-15T12:00:01Z",
                    "payload": {
                        "type": "message",
                        "role": "assistant",
                        "content": [
                            {"type": "output_text", "text": json.dumps(receipt)}
                        ],
                    },
                },
            ]
            session_path.write_text(
                "".join(json.dumps(row) + "\n" for row in rows),
                encoding="utf-8",
            )
            audit = run(
                [
                    "seq",
                    "skill-decision-audit",
                    "--root",
                    str(root),
                    "--skill",
                    "universalist",
                    "--contract",
                    str(CONTRACT),
                    "--path",
                    str(session_path),
                    "--mode",
                    "episodes",
                    "--format",
                    "json",
                ]
            )
            episodes = json.loads(audit.stdout)
            self.assertEqual(len(episodes), 1)
            self.assertEqual(episodes[0]["decision_id"], "UNI-TEST-001")
            self.assertEqual(episodes[0]["selected_route"], "UNI-ORDINARY")


if __name__ == "__main__":
    unittest.main()
