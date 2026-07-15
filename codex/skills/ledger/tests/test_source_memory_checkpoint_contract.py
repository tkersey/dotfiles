#!/usr/bin/env -S uv run python
from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
import unittest


REPO_ROOT = Path(__file__).resolve().parents[4]
SKILLS = REPO_ROOT / "codex/skills"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
PARTICIPANTS = {"learnings", "synesthesia", "negative-ledger"}


def aggregate_status(receipt: dict) -> str:
    participants = receipt["participants"]
    if set(participants) != PARTICIPANTS:
        return "blocked"
    if any(value["disposition"] == "blocked" for value in participants.values()):
        return "blocked"
    if any(value["admission"] == "blocked" for value in participants.values()):
        return "degraded"
    return "complete"


class SourceMemoryCheckpointContractTests(unittest.TestCase):
    def test_coordinator_and_participants_publish_one_non_recursive_contract(
        self,
    ) -> None:
        agents = (REPO_ROOT / "codex/AGENTS.md").read_text(encoding="utf-8")
        ledger = (SKILLS / "ledger/SKILL.md").read_text(encoding="utf-8")
        reference = (
            SKILLS / "ledger/references/source-memory-checkpoint.md"
        ).read_text(encoding="utf-8")
        learnings = (SKILLS / "learnings/SKILL.md").read_text(encoding="utf-8")
        synesthesia = (SKILLS / "synesthesia/SKILL.md").read_text(encoding="utf-8")
        negative = (SKILLS / "negative-ledger/SKILL.md").read_text(encoding="utf-8")

        for text in (agents, ledger, reference, learnings, synesthesia, negative):
            self.assertIn("source-memory-checkpoint/v1", text)
        self.assertIn(
            "exactly `$learnings`, `$synesthesia`, and `$negative-ledger`", ledger
        )
        self.assertIn("Continue collecting all three results", ledger)
        self.assertIn("Do not rerun\n`$ledger ensure`", learnings)
        self.assertIn("Do not\nrerun `$ledger ensure`", synesthesia)
        self.assertIn("Do not\nrerun `$ledger ensure`", negative)
        self.assertIn(
            "This lifecycle evaluation is distinct from the pre-route map", negative
        )
        self.assertIn("SYN-LEDGER-CHECKPOINT", synesthesia)
        self.assertIn("staging alone must not change it", reference)

    def test_learnings_to_synesthesia_fallback_is_removed(self) -> None:
        corpus = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (SKILLS / "synesthesia").rglob("*")
            if path.is_file() and path.suffix in {".md", ".yaml", ".yml"}
        )
        self.assertNotIn("SYN-LEARNINGS-LIFECYCLE", corpus)
        learnings = (SKILLS / "learnings/SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn(
            "evaluate `$synesthesia` in the same lifecycle point", learnings
        )

    def test_fixture_statuses_and_freshness_cover_required_cases(self) -> None:
        for name in (
            "source-memory-all-no-op.json",
            "source-memory-learning-append.json",
            "source-memory-canonical-blocked.json",
            "source-memory-admission-degraded.json",
            "source-memory-negative-admission-created.json",
        ):
            receipt = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
            with self.subTest(name=name):
                self.assertEqual(PARTICIPANTS, set(receipt["participants"]))
                self.assertEqual(receipt["status"], aggregate_status(receipt))

        stale = json.loads(
            (FIXTURES / "source-memory-stale.json").read_text(encoding="utf-8")
        )
        receipt = stale["receipt"]
        current = stale["current"]
        fresh = (
            receipt["subject_fingerprint"] == current["subject_fingerprint"]
            and receipt["evidence_fingerprint"] == current["evidence_fingerprint"]
        )
        self.assertEqual(stale["expected_fresh"], fresh)

    def test_native_validator_accepts_current_receipt_fixtures_when_available(
        self,
    ) -> None:
        ledger = shutil.which("ledger")
        if ledger is None:
            self.skipTest("ledger unavailable")
        version = subprocess.run(
            [ledger, "--version"], capture_output=True, text=True, check=False
        ).stdout
        match = re.search(r"(\d+)\.(\d+)\.(\d+)", version)
        if match is None or tuple(map(int, match.groups())) < (0, 10, 0):
            self.skipTest("ledger 0.10.0 required")
        for name in (
            "source-memory-all-no-op.json",
            "source-memory-learning-append.json",
            "source-memory-canonical-blocked.json",
            "source-memory-admission-degraded.json",
            "source-memory-negative-admission-created.json",
        ):
            proc = subprocess.run(
                [
                    ledger,
                    "validate",
                    "source-memory-checkpoint",
                    "--input",
                    str(FIXTURES / name),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            with self.subTest(name=name):
                self.assertEqual(0, proc.returncode, proc.stderr or proc.stdout)


if __name__ == "__main__":
    unittest.main()
