#!/usr/bin/env -S uv run python
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "actuation_authority_gate.py"
ASSETS = ROOT / "assets"
SPEC = importlib.util.spec_from_file_location("actuation_authority_gate", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ActuationAuthorityGateTests(unittest.TestCase):
    def gcr(self, name: str = "gcr-v2.allowed.example.json"):
        return json.loads((ASSETS / name).read_text())["graph_control_receipt"]

    def test_authorize_valid_gcr_for_path(self) -> None:
        apma = MODULE.make_apma(
            self.gcr(),
            "run-1",
            [MODULE.parse_resource("write:path:src/main.zig")],
        )["actuation_pre_mutation_authority"]
        self.assertEqual(apma["version"], "APMA-v1")
        self.assertEqual(apma["verdict"], "mutation-authorized")
        self.assertEqual(apma["coordination"]["claim_id"], "claim-001")

    def test_denies_when_gcr_execution_not_allowed(self) -> None:
        with self.assertRaisesRegex(MODULE.GateError, "execution_allowed:not-yes"):
            MODULE.make_apma(
                self.gcr("gcr-v2.self-invalidating.example.json"),
                "run-1",
                [MODULE.parse_resource("write:path:src/main.zig")],
            )

    def test_denies_uncovered_path(self) -> None:
        with self.assertRaisesRegex(MODULE.GateError, "not-covered"):
            MODULE.make_apma(
                self.gcr(),
                "run-1",
                [MODULE.parse_resource("write:path:other/file.zig")],
            )

    def test_diagnoses_self_invalidating_gcr_candidate(self) -> None:
        report = MODULE.diagnose_gcr(self.gcr("gcr-v2.self-invalidating.example.json"))
        body = report["actuation_gcr_diagnosis"]
        self.assertEqual(body["stage"], "blocked-self-invalidating-gcr-candidate")
        self.assertIn("plan_sequence", body["sequence_mismatches"])
        self.assertTrue(body["hard_stop"])

    def test_check_apma_covers_requested_path(self) -> None:
        apma = json.loads((ASSETS / "apma-v1.example.json").read_text())
        result = MODULE.validate_apma(apma, [MODULE.parse_resource("write:path:src/main.zig")])
        self.assertEqual(result["actuation_authority_check"]["verdict"], "pass")

    def test_check_apma_denies_out_of_claim_path(self) -> None:
        apma = json.loads((ASSETS / "apma-v1.example.json").read_text())
        with self.assertRaisesRegex(MODULE.GateError, "not-covered"):
            MODULE.validate_apma(apma, [MODULE.parse_resource("write:path:README.md")])

    def test_cli_authorize_writes_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "apma.json"
            code = MODULE.main([
                "authorize",
                "--gcr",
                str(ASSETS / "gcr-v2.allowed.example.json"),
                "--run-id",
                "run-cli",
                "--path",
                "src/main.zig",
                "--out",
                str(out),
            ])
            self.assertEqual(code, 0)
            data = json.loads(out.read_text())
            self.assertEqual(data["actuation_pre_mutation_authority"]["verdict"], "mutation-authorized")


if __name__ == "__main__":
    unittest.main()
