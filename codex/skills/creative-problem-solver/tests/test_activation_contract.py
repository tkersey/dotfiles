from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
AGENT = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
CORPUS = json.loads((ROOT / "evals" / "routing-cases.json").read_text(encoding="utf-8"))


class ActivationContractTests(unittest.TestCase):
    def test_implicit_invocation_is_enabled(self) -> None:
        self.assertIn("allow_implicit_invocation: true", AGENT)
        self.assertNotIn("allow_implicit_invocation: false", AGENT)

    def test_frontmatter_names_positive_and_negative_boundaries(self) -> None:
        frontmatter = SKILL.split("---", 2)[1]
        for phrase in (
            "multiple materially different paths",
            "options, alternatives, trade-offs, reframing",
            "direct implementation",
            "repository-evidence opportunity mining ($ideate)",
            "detailed planning ($plan)",
        ):
            self.assertIn(phrase, frontmatter)

    def test_activation_boundary_is_early_and_explicit(self) -> None:
        self.assertLess(SKILL.index("## Activation boundary"), SKILL.index("## Contract"))
        for phrase in (
            "unresolved strategy choice plus a request for divergent options",
            "The primary deliverable is at least three materially different paths",
            "Do not activate; route elsewhere",
            "$ideate` wins",
            "$plan` wins",
            "one answer, one plan, or one implementation",
        ):
            self.assertIn(phrase, SKILL)

    def test_interface_prompt_preserves_the_stop_boundary(self) -> None:
        for phrase in (
            "multiple materially different",
            "stop for human selection",
            "direct implementation",
            "($ideate)",
            "($plan)",
        ):
            self.assertIn(phrase, AGENT)

    def test_routing_corpus_covers_positives_and_near_misses(self) -> None:
        self.assertEqual("creative-problem-solver-routing-cases/v1", CORPUS["schema"])
        positives = [case for case in CORPUS["cases"] if case["activate"]]
        negatives = [case for case in CORPUS["cases"] if not case["activate"]]
        self.assertGreaterEqual(len(positives), 8)
        self.assertGreaterEqual(len(negatives), 8)
        owners = {case["owner"] for case in negatives}
        self.assertTrue(
            {"direct", "implementation", "ideate", "plan", "codebase-archaeology", "review"}
            <= owners
        )

    def test_routing_examples_match_the_corpus_boundaries(self) -> None:
        for phrase in (
            "Should activate",
            "Should not activate",
            "Mine this repository for evidence-backed product and DX opportunities",
            "Turn the chosen event-sourcing direction into a detailed implementation plan",
            "We chose the Quick Win. Build it now.",
        ):
            self.assertIn(phrase, SKILL)

    def test_skill_stays_within_a_compact_package_budget(self) -> None:
        self.assertLessEqual(len(SKILL.splitlines()), 280)


if __name__ == "__main__":
    unittest.main()
