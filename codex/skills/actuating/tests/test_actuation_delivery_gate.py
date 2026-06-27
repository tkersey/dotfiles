#!/usr/bin/env -S uv run python
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "actuation_delivery_gate.py"
ASSETS = ROOT / "assets"
SPEC = importlib.util.spec_from_file_location("actuation_delivery_gate", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ActuationDeliveryGateTests(unittest.TestCase):
    def context(self, name: str = "delivery-context.ready.example.json"):
        return json.loads((ASSETS / name).read_text())["actuation_delivery_context"]

    def decision(self, name: str):
        return json.loads((ASSETS / name).read_text())

    def test_ready_context_hands_off_to_ship(self) -> None:
        decision = MODULE.make_decision(self.context())
        body = decision["actuation_delivery_decision"]
        self.assertEqual(body["verdict"], "handoff_to_ship")
        self.assertEqual(body["ship_handoff"]["next_owner"], "$ship")
        self.assertEqual(body["ship_handoff"]["ship_input"]["branch"], "feature/example")
        self.assertEqual(body["ship_handoff"]["ship_input"]["head_sha"], "abc123")

    def test_no_pr_intent_is_not_ship(self) -> None:
        decision = MODULE.make_decision(self.context("delivery-context.no-pr-intent.example.json"))
        body = decision["actuation_delivery_decision"]
        self.assertEqual(body["verdict"], "shipping_not_requested")
        self.assertIsNone(body["ship_handoff"])

    def test_blocked_context_names_reasons(self) -> None:
        decision = MODULE.make_decision(self.context("delivery-context.blocked.example.json"))
        body = decision["actuation_delivery_decision"]
        self.assertEqual(body["verdict"], "blocked")
        self.assertIn("proof_complete_receipt:not-current", body["blocked_reasons"])
        self.assertIn("integration.queue_quiescent:not-yes", body["blocked_reasons"])

    def test_check_valid_handoff_decision(self) -> None:
        result = MODULE.validate_decision(self.decision("add-v1.handoff.example.json"))
        self.assertEqual(result["actuation_delivery_gate"]["verdict"], "pass")

    def test_check_rejects_handoff_without_ship(self) -> None:
        decision = self.decision("add-v1.handoff.example.json")
        decision["actuation_delivery_decision"]["ship_handoff"] = None
        with self.assertRaisesRegex(MODULE.DeliveryError, "ship_handoff"):
            MODULE.validate_decision(decision)

    def test_check_shipping_not_requested_example(self) -> None:
        result = MODULE.validate_decision(self.decision("add-v1.shipping-not-requested.example.json"))
        self.assertEqual(result["actuation_delivery_gate"]["decision_verdict"], "shipping_not_requested")

    def test_check_blocked_example(self) -> None:
        result = MODULE.validate_decision(self.decision("add-v1.blocked.example.json"))
        self.assertEqual(result["actuation_delivery_gate"]["decision_verdict"], "blocked")

    def test_cli_decide_writes_handoff_decision(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "delivery.json"
            code = MODULE.main([
                "decide",
                "--context",
                str(ASSETS / "delivery-context.ready.example.json"),
                "--out",
                str(out),
            ])
            self.assertEqual(code, 0)
            body = json.loads(out.read_text())["actuation_delivery_decision"]
            self.assertEqual(body["verdict"], "handoff_to_ship")


if __name__ == "__main__":
    unittest.main()
