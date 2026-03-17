#!/usr/bin/env -S uv run python
"""Deterministic regression tests for zig_ops_scorecard.py."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


def load_module():
    module_path = Path(__file__).with_name("zig_ops_scorecard.py")
    spec = importlib.util.spec_from_file_location("zig_ops_scorecard", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ZigOpsScorecardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def test_run_routing_gap_falls_back_when_since_unsupported(self):
        calls: list[list[str]] = []

        def fake_run_cmd(cmd: list[str]) -> str:
            calls.append(cmd)
            if "--since" in cmd:
                raise RuntimeError(
                    "seq routing-gap -> error: option --since is not supported for routing_gap"
                )
            return json.dumps(
                [
                    {
                        "cue": "__all__",
                        "cue_sessions": 3,
                        "invoked_rate_pct": 12.5,
                    }
                ]
            )

        config = self.mod.ScorecardConfig(
            root="/tmp/root", since="2026-02-01T00:00:00Z"
        )

        with patch.object(self.mod, "run_cmd", side_effect=fake_run_cmd):
            rows, since_applied = self.mod.run_routing_gap(config)

        self.assertFalse(since_applied)
        self.assertEqual(rows[0]["cue"], "__all__")
        self.assertEqual(len(calls), 2)
        self.assertIn("--since", calls[0])
        self.assertNotIn("--since", calls[1])

    def test_run_routing_gap_falls_back_when_since_output_is_not_json(self):
        calls: list[list[str]] = []

        def fake_run_cmd(cmd: list[str]) -> str:
            calls.append(cmd)
            if "--since" in cmd:
                return ""
            return json.dumps(
                [
                    {
                        "cue": "__all__",
                        "cue_sessions": 2,
                        "invoked_rate_pct": 50.0,
                    }
                ]
            )

        config = self.mod.ScorecardConfig(
            root="/tmp/root", since="2026-02-01T00:00:00Z"
        )

        with patch.object(self.mod, "run_cmd", side_effect=fake_run_cmd):
            rows, since_applied = self.mod.run_routing_gap(config)

        self.assertFalse(since_applied)
        self.assertEqual(rows[0]["cue"], "__all__")
        self.assertEqual(len(calls), 2)
        self.assertIn("--since", calls[0])
        self.assertNotIn("--since", calls[1])

    def test_recommendations_cover_frontier_cues(self):
        audit = {
            "counts": {
                "implicit_zig_intent_sessions": 1,
                "implicit_noise_filtered_sessions": 2,
            },
            "rates": {
                "explicit_session_recall_proxy_pct": 60.0,
            },
        }
        routing = [
            {"cue": "zig_build", "cue_sessions": 10, "invoked_rate_pct": None},
            {"cue": "zig_fetch", "cue_sessions": 5, "invoked_rate_pct": 20.0},
            {"cue": "extern_fn", "cue_sessions": 4, "invoked_rate_pct": 25.0},
            {"cue": "link_system_library", "cue_sessions": 4, "invoked_rate_pct": 75.0},
            {"cue": "link_libc", "cue_sessions": 3, "invoked_rate_pct": 40.0},
            {"cue": "compare_exchange", "cue_sessions": 2, "invoked_rate_pct": 30.0},
            {"cue": "__all__", "cue_sessions": 20, "invoked_rate_pct": None},
        ]

        recs = self.mod.recommendations(501, audit, routing)
        joined = "\n".join(recs)

        self.assertIn("Reduce codex/skills/zig/SKILL.md below 500 lines.", joined)
        self.assertIn("Improve explicit $zig handling", joined)
        self.assertIn("zig build workflows", joined)
        self.assertIn("dependency/provenance trigger cues", joined)
        self.assertIn("FFI boundary trigger cues", joined)
        self.assertIn("concurrency/atomics trigger cues", joined)
        self.assertIn("overall invoked rate is below 30%", joined)

    def test_render_text_includes_routing_gap_mode(self):
        report = {
            "generated_at": "2026-03-16T00:00:00+00:00",
            "root": "/tmp/root",
            "since": "2026-02-01T00:00:00Z",
            "routing_gap_since_applied": False,
            "skill_lines": 400,
            "audit_counts": {},
            "audit_rates": {},
            "routing_gap_rates": [],
            "recommendations": ["No immediate drift action required."],
        }

        text = self.mod.render_text(report)

        self.assertIn("routing_gap_since_applied: false", text)


if __name__ == "__main__":
    unittest.main()
