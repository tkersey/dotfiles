#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import unittest


def load_module():
    path = Path(__file__).with_name("zig_trigger_audit.py")
    spec = importlib.util.spec_from_file_location("zig_trigger_audit", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TriggerAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def test_family_cues_require_zig_context(self):
        args = argparse.Namespace(
            root="/tmp",
            since=None,
            until=None,
            strict_implicit=True,
            max_misses=10,
        )
        base_rows = [
            {"path": "zig-family", "text": "edit build.zig; the receipt fingerprint is weak"},
            {"path": "explicit", "text": "please use $zig"},
            {"path": "noise", "text": "<instructions> build.zig"},
        ]
        family_rows = {
            family: [] for family in self.mod.FAMILY_TERMS
        }
        family_rows["claim-binding"] = [
            {"path": "zig-family", "text": "edit build.zig; fingerprint receipt"},
            {"path": "not-zig", "text": "financial receipt fingerprint"},
        ]
        skill_rows = [{"path": "zig-family"}, {"path": "explicit"}]

        report = self.mod.build_report(args, base_rows, family_rows, skill_rows)
        self.assertEqual(report["counts"]["zig_intent_sessions_total"], 2)
        self.assertEqual(
            report["semantic_families"]["claim-binding"]["opportunity_sessions"],
            1,
        )
        self.assertEqual(
            report["semantic_families"]["claim-binding"]["zig_activated_sessions"],
            1,
        )

    def test_low_signal_filtered(self):
        args = argparse.Namespace(
            root="/tmp",
            since=None,
            until=None,
            strict_implicit=True,
            max_misses=10,
        )
        report = self.mod.build_report(
            args,
            [{"path": "low", "text": "zig maybe?"}],
            {family: [] for family in self.mod.FAMILY_TERMS},
            [],
        )
        self.assertEqual(report["counts"]["zig_intent_sessions_total"], 0)
        self.assertEqual(report["counts"]["implicit_low_signal_filtered_sessions"], 1)


if __name__ == "__main__":
    unittest.main()
