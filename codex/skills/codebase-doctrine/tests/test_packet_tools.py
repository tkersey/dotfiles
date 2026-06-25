#!/usr/bin/env -S uv run --with pyyaml python
from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ASSETS = ROOT / "assets"
CODEX_ROOT = ROOT.parents[1]
REPO = ROOT.parents[2]
sys.path.insert(0, str(TOOLS))

import handoff_gate
import packet_gate
import worker_suite_check


class PacketAndHandoffTests(unittest.TestCase):
    def load(self, name: str):
        return yaml.safe_load((ASSETS / name).read_text(encoding="utf-8"))

    def test_packet_matches_assignment(self) -> None:
        errors, warnings, receipt = packet_gate.validate_packet(
            self.load("specialist-packet.example.yaml"),
            self.load("specialist-assignment.example.yaml"),
        )
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertEqual(receipt["accepted"], "yes")

    def test_packet_rejects_wrong_question(self) -> None:
        packet = self.load("specialist-packet.example.yaml")
        packet["codebase_doctrine_packet"]["questions_addressed"] = ["Q-OTHER"]
        errors, _warnings, _receipt = packet_gate.validate_packet(
            packet,
            self.load("specialist-assignment.example.yaml"),
        )
        self.assertTrue(any("questions_addressed:not-assigned" in item for item in errors))

    def test_packet_rejects_worker_authority_escape(self) -> None:
        packet = self.load("specialist-packet.example.yaml")
        packet["codebase_doctrine_packet"]["proposed_doctrine_updates"][
            "focused_skill_candidates"
        ] = []
        errors, _warnings, _receipt = packet_gate.validate_packet(
            packet,
            self.load("specialist-assignment.example.yaml"),
        )
        self.assertTrue(any("outside-worker-authority" in item for item in errors))

    def test_packet_rejects_stale_state(self) -> None:
        packet = self.load("specialist-packet.example.yaml")
        packet["codebase_doctrine_packet"]["artifact_state_id"] = "AS-stale"
        errors, _warnings, _receipt = packet_gate.validate_packet(
            packet,
            self.load("specialist-assignment.example.yaml"),
        )
        self.assertIn("artifact_state_id:mismatch", errors)

    def test_handoff_binds_candidate_and_authorization(self) -> None:
        errors, warnings = handoff_gate.validate_handoff(
            self.load("codebase-skill-handoff.example.yaml"),
            self.load("codebase-doctrine.example.yaml"),
        )
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_handoff_rejects_missing_authorization(self) -> None:
        handoff = self.load("codebase-skill-handoff.example.yaml")
        handoff["codebase_skill_handoff"]["explicit_user_authorization"][
            "authorized"
        ] = "no"
        errors, _warnings = handoff_gate.validate_handoff(
            handoff,
            self.load("codebase-doctrine.example.yaml"),
        )
        self.assertTrue(any("authorized:not-yes" in item for item in errors))

    def test_worker_suite(self) -> None:
        errors, warnings, counts = worker_suite_check.validate_suite(CODEX_ROOT / "agents")
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertEqual(counts["present"], 7)


if __name__ == "__main__":
    unittest.main()
