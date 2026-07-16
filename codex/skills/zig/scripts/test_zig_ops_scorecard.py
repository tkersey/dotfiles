#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


def load_module():
    path = Path(__file__).with_name("zig_ops_scorecard.py")
    spec = importlib.util.spec_from_file_location("zig_ops_scorecard", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ScorecardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def test_recommendations_prioritize_route_and_style_effect(self):
        trigger = {
            "rates": {"explicit_session_recall_proxy_pct": 100.0},
            "semantic_families": {
                "claim-binding": {
                    "opportunity_sessions": 4,
                    "zig_activated_sessions": 4,
                    "activation_rate_pct": 100.0,
                },
                "repo-closure": {
                    "opportunity_sessions": 3,
                    "zig_activated_sessions": 1,
                    "activation_rate_pct": 33.3,
                },
            },
        }
        recs = self.mod.recommendations(
            450,
            trigger,
            {"route_sessions": 2},
            {"contract_sessions": 0},
            {"available": False, "reason": "missing"},
        )
        joined = "\n".join(recs)
        self.assertIn("no ZTS-v1", joined)
        self.assertIn("Decision-effect evidence unavailable", joined)
        self.assertIn("repo-closure", joined)
        self.assertNotIn("below 500", joined)

    def test_missing_routes_remains_distinct_from_missing_style(self):
        trigger = {
            "rates": {"explicit_session_recall_proxy_pct": 100.0},
            "semantic_families": {
                "claim-binding": {
                    "opportunity_sessions": 4,
                    "zig_activated_sessions": 4,
                    "activation_rate_pct": 100.0,
                }
            },
        }
        recs = self.mod.recommendations(
            450,
            trigger,
            {"route_sessions": 0},
            {"contract_sessions": 0},
            {"available": True},
        )
        joined = "\n".join(recs)
        self.assertIn("no ZSR-v1 route artifacts", joined)
        self.assertNotIn("no ZTS-v1", joined)

    def test_line_budget_warning(self):
        recs = self.mod.recommendations(
            501,
            {"rates": {}, "semantic_families": {}},
            {"route_sessions": 0},
            {"contract_sessions": 0},
            {"available": True},
        )
        self.assertIn("Reduce codex/skills/zig/SKILL.md below 500 lines.", recs)

    def test_render_text_reports_tiger_style_counts(self):
        report = {
            "generated_at": "now",
            "root": "/sessions",
            "since": "then",
            "until": None,
            "skill_lines": 463,
            "routing_gap_since_applied": True,
            "decision_audit": {"available": True},
            "semantic_routes": {"route_sessions": 3},
            "tiger_style": {"contract_sessions": 2, "exception_sessions": 1},
            "trigger_audit": {"semantic_families": {}},
            "recommendations": ["No immediate drift action required."],
        }
        text = self.mod.render_text(report)
        self.assertIn("tiger_style_contract_sessions: 2", text)
        self.assertIn("tiger_style_exception_sessions: 1", text)


if __name__ == "__main__":
    unittest.main()
