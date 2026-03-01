#!/usr/bin/env -S uv run python
"""Deterministic regression tests for zig_trigger_audit.py."""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


def load_module():
    module_path = Path(__file__).with_name("zig_trigger_audit.py")
    spec = importlib.util.spec_from_file_location("zig_trigger_audit", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fake_run_seq_query(seq_runner, root, spec, since, until):
    _ = (seq_runner, root, since, until)
    dataset = spec.get("dataset")
    if dataset == "skill_mentions":
        return [
            {"path": "s-explicit", "timestamp": "2026-02-20T10:00:00Z"},
            {"path": "s-clean-1", "timestamp": "2026-02-20T10:00:00Z"},
            {"path": "s-lint-clean", "timestamp": "2026-02-20T10:00:00Z"},
        ]

    where = spec.get("where", [{}, {}])
    if len(where) > 1:
        # Regression guard: dotted Zig cues must use literal contains matching,
        # not regex, so seq does not fail with UnsupportedRegexConstruct.
        if where[1].get("op") != "contains":
            raise AssertionError(f"unexpected where.op: {where[1].get('op')}")

    term = spec.get("where", [{}, {}])[1].get("value")
    if term == "zig":
        return [
            {
                "path": "s-explicit",
                "text": "please run $zig on this patch",
                "timestamp": "2026-02-20T10:00:00Z",
            },
            {
                "path": "s-low",
                "text": "zig maybe?",
                "timestamp": "2026-02-20T10:00:00Z",
            },
            {
                "path": "s-noise",
                "text": "<instructions> automatic orchestration policy zig",
                "timestamp": "2026-02-20T10:00:00Z",
            },
        ]
    if term in (".zig", "build.zig"):
        return [
            {
                "path": "s-clean-1",
                "text": "edit build.zig for CI",
                "timestamp": "2026-02-20T10:00:00Z",
            }
        ]
    if term == "comptime":
        return [
            {
                "path": "s-clean-2",
                "text": "add comptime assertion",
                "timestamp": "2026-02-20T10:00:00Z",
            }
        ]
    if term == "zig build lint":
        return [
            {
                "path": "s-lint-clean",
                "text": "run zig build lint before tests",
                "timestamp": "2026-02-20T10:00:00Z",
            }
        ]
    if term == "zlinter":
        return [
            {
                "path": "s-lint-clean",
                "text": "wire zlinter into build.zig",
                "timestamp": "2026-02-20T10:00:00Z",
            }
        ]
    return []


class ZigTriggerAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def run_main(self, argv):
        with (
            patch.object(sys, "argv", argv),
            patch.object(self.mod, "run_seq_query", side_effect=fake_run_seq_query),
            patch.object(
                self.mod,
                "resolve_seq_script",
                return_value=Path("/tmp/seq.py"),
            ),
            patch.object(
                self.mod,
                "resolve_seq_runner",
                return_value=["seq"],
            ),
        ):
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                rc = self.mod.main()
            return rc, buffer.getvalue()

    def test_json_output_strict_mode(self):
        with tempfile.TemporaryDirectory() as td:
            out_path = Path(td) / "report.json"
            argv = [
                "zig_trigger_audit.py",
                "--root",
                "/tmp/unused",
                "--since",
                "2026-02-20T00:00:00Z",
                "--until",
                "2026-02-20T23:59:59Z",
                "--max-misses",
                "3",
                "--strict-implicit",
                "--format",
                "json",
                "--output",
                str(out_path),
            ]

            rc, stdout = self.run_main(argv)
            self.assertEqual(rc, 0)
            self.assertEqual(stdout, "")
            report = json.loads(out_path.read_text(encoding="utf-8"))

            self.assertTrue(report["flags"]["strict_implicit"])
            counts = report["counts"]
            self.assertEqual(counts["zig_intent_sessions_total"], 4)
            self.assertEqual(counts["explicit_zig_intent_sessions"], 1)
            self.assertEqual(counts["implicit_zig_intent_sessions_raw"], 5)
            self.assertEqual(counts["implicit_noise_filtered_sessions"], 1)
            self.assertEqual(counts["implicit_low_signal_total_sessions"], 1)
            self.assertEqual(counts["implicit_low_signal_filtered_sessions"], 1)
            self.assertEqual(counts["implicit_low_signal_included_sessions"], 0)
            self.assertEqual(counts["implicit_zig_intent_sessions"], 3)
            self.assertEqual(counts["assistant_mentioned_$zig_sessions"], 3)
            self.assertEqual(counts["matched_sessions"], 3)
            self.assertEqual(counts["matched_explicit_sessions"], 1)
            self.assertEqual(counts["matched_implicit_sessions"], 2)

            rates = report["rates"]
            self.assertAlmostEqual(rates["session_recall_proxy_pct"], 75.0, places=3)
            self.assertAlmostEqual(rates["session_precision_proxy_pct"], 100.0, places=3)
            self.assertAlmostEqual(rates["explicit_session_recall_proxy_pct"], 100.0, places=3)
            self.assertAlmostEqual(rates["implicit_session_recall_proxy_pct"], 66.6666666, places=3)

            samples = report["samples"]
            self.assertEqual(len(samples["explicit_miss_sample"]), 0)
            self.assertEqual(len(samples["implicit_miss_sample"]), 1)
            self.assertEqual(
                samples["implicit_miss_sample"][0]["reason"],
                "assistant_missing_skill",
            )
            self.assertEqual(
                samples["filtered_noise_sample"][0]["reason"],
                "filtered_noise",
            )
            self.assertEqual(
                samples["filtered_low_signal_sample"][0]["reason"],
                "filtered_low_signal",
            )

    def test_text_output_has_reason_labels(self):
        argv = [
            "zig_trigger_audit.py",
            "--root",
            "/tmp/unused",
            "--since",
            "2026-02-20T00:00:00Z",
            "--until",
            "2026-02-20T23:59:59Z",
            "--max-misses",
            "3",
            "--strict-implicit",
        ]
        rc, stdout = self.run_main(argv)
        self.assertEqual(rc, 0)
        self.assertIn("strict_implicit_mode: true", stdout)
        self.assertIn("miss_sample", stdout)
        self.assertIn("filtered_implicit_sample", stdout)
        self.assertIn("reason=assistant_missing_skill", stdout)
        self.assertIn("reason=filtered_low_signal", stdout)
        self.assertIn("reason=filtered_noise", stdout)


if __name__ == "__main__":
    unittest.main()
