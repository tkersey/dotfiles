#!/usr/bin/env -S uv run python
from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SynesthesiaPackageTests(unittest.TestCase):
    def test_routing_corpus_has_domain_owner_near_misses(self) -> None:
        data = json.loads((ROOT / "evals/routing-cases.json").read_text(encoding="utf-8"))
        cases = data["cases"]
        positives = [row for row in cases if row["activate"]]
        negatives = [row for row in cases if not row["activate"]]
        self.assertGreaterEqual(len(positives), 5)
        self.assertGreaterEqual(len(negatives), 5)
        self.assertTrue(any(row["id"] == "root-discovered-ambiguity" for row in positives))
        owners = {row["owner"] for row in negatives}
        self.assertTrue(
            {"lift", "codebase-audit", "complexity-mitigator", "universalist", "zig"}
            <= owners
        )

    def test_skill_requires_reversibility_and_same_turn_capture(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
        for phrase in (
            "literal evidence",
            "minimum sufficient",
            "multiple plausible structural, temporal, interaction, or boundary interpretations",
            "falsifier",
            "decision or explanation delta",
            "same turn",
            "$memory-source-notes",
            "do not activate merely because",
            "generated current-state digest",
            "memory-digest",
        ):
            self.assertIn(phrase, text)

    def test_resource_template_requires_source_note_ids(self) -> None:
        template = (
            ROOT.parents[1]
            / "memories/extensions/.templates/synesthesia-resource-template.md"
        ).read_text(encoding="utf-8")
        self.assertGreaterEqual(template.count("source_note_ids"), 5)


if __name__ == "__main__":
    unittest.main()
