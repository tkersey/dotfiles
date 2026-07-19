#!/usr/bin/env python3
"""Focused proof for Universalist card routing and SDR-v1 observability."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Sequence

import yaml


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[2]
SKILL = SKILL_ROOT / "SKILL.md"
CONTRACT = SKILL_ROOT / "references" / "decision-contract.yaml"
PLAN_TEMPLATE = SKILL_ROOT / "templates" / "universalist-plan.md"
SDR_GATE = SKILL_ROOT.parent / "tune" / "tools" / "sdr_gate.py"
ACTIVATION_GOLDEN = SKILL_ROOT / "tests" / "golden" / "activation.yml"
OUTPUT_GOLDEN = SKILL_ROOT / "tests" / "golden" / "output-invariants.yml"
LEDGER = os.environ.get("LEDGER_BIN", "ledger")


def run(
    command: Sequence[str],
    *,
    expected: int = 0,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    if completed.returncode != expected:
        raise AssertionError(
            f"expected exit {expected}, got {completed.returncode}: {' '.join(command)}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    return completed


class DecisionObservabilityTest(unittest.TestCase):
    maxDiff = None

    def test_trigger_to_evidence_kernel_precedes_doctrine(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        trigger = text.index("## Boundary-trigger mandate")
        kernel = text.index("## Trigger-to-evidence kernel")
        cards = text.index("## Construction card decision table")
        doctrine = text.index("## Doctrine index")
        step_zero = text.index("## Step 0 — Allocate a ledger-addressed plan")
        observability = text.index("## Decision observability")

        self.assertLess(trigger, kernel)
        self.assertLess(kernel, cards)
        self.assertLess(cards, doctrine)
        self.assertLess(doctrine, step_zero)
        self.assertLess(step_zero, observability)
        for required in (
            "Record the compact boundary disposition immediately",
            "allocate one fresh ledger-addressed Universalist plan",
            "complete this gate before mutating the seam",
            "Do not allocate a plan or emit `SDR-v1` solely because the skill activated",
            "at least two plausible routes materially differ",
            "selected**, **rejected**, **contradicted**, or **unresolved",
            "ledger --source universalist create",
            "ledger --source universalist emit",
        ):
            self.assertIn(required, text)

    def receipt_command(self) -> list[str]:
        return [
            LEDGER,
            "--source",
            "universalist",
            "emit",
            "--plan",
            str(PLAN_TEMPLATE),
            "--contract",
            str(CONTRACT),
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

    def test_native_plan_address_commands(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            run(["git", "init", "--quiet"], cwd=repo)
            created = json.loads(
                run(
                    [
                        LEDGER,
                        "--source",
                        "universalist",
                        "create",
                        "--repo",
                        str(repo),
                        "--template",
                        str(PLAN_TEMPLATE),
                    ]
                ).stdout
            )
            self.assertEqual(created["schema"], "universalist-plan-address/v1")
            plan_id = created["plan_id"]
            path = Path(created["path"])
            self.assertTrue(path.is_file())

            resolved = Path(
                run(
                    [
                        LEDGER,
                        "--source",
                        "universalist",
                        "path",
                        "--repo",
                        str(repo),
                        "--id",
                        plan_id,
                    ]
                ).stdout.strip()
            )
            latest = json.loads(
                run(
                    [
                        LEDGER,
                        "--source",
                        "universalist",
                        "latest",
                        "--repo",
                        str(repo),
                    ]
                ).stdout
            )
            self.assertEqual(resolved, path)
            self.assertEqual(latest["plan_id"], plan_id)

    def test_golden_activation_and_output_contracts(self) -> None:
        activation = yaml.safe_load(ACTIVATION_GOLDEN.read_text(encoding="utf-8"))
        by_prompt = {case["prompt"]: case for case in activation["cases"]}
        self.assertIs(
            by_prompt[
                "Implement the DTO-to-domain adapter for this endpoint while keeping its JSON wire shape stable."
            ]["should_use_skill"],
            True,
        )
        self.assertIs(
            by_prompt[
                "Rename a local variable inside a private helper without changing its inputs, outputs, effects, or ownership."
            ]["should_use_skill"],
            False,
        )

        output = yaml.safe_load(OUTPUT_GOLDEN.read_text(encoding="utf-8"))
        by_name = {item["name"]: item for item in output["invariants"]}
        consequential = by_name["consequential_route_requires_one_root_receipt"]
        self.assertIn("at least two plausible routes", consequential["when"])
        self.assertIn("relevant construction cards", consequential["required"])
        self.assertIn("one root SDR-v1 receipt", consequential["required"])

    def test_plan_append_is_exactly_once(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            run(["git", "init", "--quiet"], cwd=repo)
            plan_id = "20260715T120000000000000Z-0000"
            plan = repo / ".ledger" / "universalist" / f"plan-{plan_id}.md"
            plan.parent.mkdir(parents=True)
            plan.write_text(
                "---\nschema: universalist-plan/v1\n"
                f"plan_id: {plan_id}\n"
                "created_at: 2026-07-15T12:00:00.000000000Z\n---\n\n"
                + PLAN_TEMPLATE.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            run(["git", "add", str(plan.relative_to(repo))], cwd=repo)
            run(
                [
                    "git",
                    "-c",
                    "user.name=Universalist Test",
                    "-c",
                    "user.email=universalist-test@example.invalid",
                    "commit",
                    "--quiet",
                    "-m",
                    "Add plan fixture",
                ],
                cwd=repo,
            )

            command = self.receipt_command()
            plan_index = command.index("--plan") + 1
            command[plan_index] = str(plan)
            decision_index = command.index("--decision-id")
            del command[decision_index : decision_index + 2]
            command.append("--write-plan")
            invalid = command.copy()
            selected_index = invalid.index("--selected-route") + 1
            invalid[selected_index] = "UNI-UNKNOWN"
            before_invalid = plan.read_text(encoding="utf-8")
            run(invalid, expected=2)
            self.assertEqual(plan.read_text(encoding="utf-8"), before_invalid)

            emitted = run(command)
            receipt = json.loads(emitted.stdout)
            self.assertEqual(
                receipt["skill_decision_receipt"]["decision_id"],
                f"UNI-{plan_id}",
            )
            text = plan.read_text(encoding="utf-8")
            self.assertEqual(text.count('"skill_decision_receipt"'), 1)
            self.assertIn(
                f"## Root decision receipt: emitted (UNI-{plan_id})",
                text,
            )
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
            run(command, expected=2)

    def test_projection_does_not_require_plan_directory_write_access(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            run(["git", "init", "--quiet"], cwd=repo)
            plan_dir = repo / "readonly"
            plan_dir.mkdir()
            plan = plan_dir / "universalist-template.md"
            plan.write_text(PLAN_TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")
            run(["git", "add", str(plan.relative_to(repo))], cwd=repo)
            run(
                [
                    "git",
                    "-c",
                    "user.name=Universalist Test",
                    "-c",
                    "user.email=universalist-test@example.invalid",
                    "commit",
                    "--quiet",
                    "-m",
                    "Add read-only fixture",
                ],
                cwd=repo,
            )
            original = plan.read_text(encoding="utf-8")
            plan.chmod(0o444)
            plan_dir.chmod(0o555)
            try:
                command = self.receipt_command()
                plan_index = command.index("--plan") + 1
                command[plan_index] = str(plan)
                run(command)
                self.assertEqual(plan.read_text(encoding="utf-8"), original)
            finally:
                plan_dir.chmod(0o755)
                plan.chmod(0o644)

    def test_receipt_validates_and_becomes_one_seq_episode(self) -> None:
        emitted = run(self.receipt_command())
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
