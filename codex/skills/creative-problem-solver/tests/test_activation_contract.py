from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
AGENT = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
CORPUS = json.loads((ROOT / "evals" / "routing-cases.json").read_text(encoding="utf-8"))


def skill_section(start: str, end: str) -> str:
    return SKILL.split(start, 1)[1].split(end, 1)[0]


class ActivationContractTests(unittest.TestCase):
    def test_implicit_invocation_is_enabled(self) -> None:
        self.assertIn("allow_implicit_invocation: true", AGENT)
        self.assertNotIn("allow_implicit_invocation: false", AGENT)

    def test_frontmatter_names_positive_negative_and_meta_boundaries(self) -> None:
        frontmatter = SKILL.split("---", 2)[1]
        for phrase in (
            "next task is choosing among materially different paths",
            "options, alternatives, trade-offs, reframing",
            "A skill-name mention is not invocation",
            "direct implementation",
            "skill analysis/tuning",
            "repository-evidence opportunity mining ($ideate)",
            "detailed planning ($plan)",
        ):
            self.assertIn(phrase, frontmatter)

    def test_activation_boundary_distinguishes_invocation_from_reference(self) -> None:
        self.assertLess(SKILL.index("## Activation boundary"), SKILL.index("## Contract"))
        for phrase in (
            "unresolved strategy choice plus a request for divergent options",
            "Difficulty, uncertainty, or creativity language alone is not enough",
            "### Skill-name rule",
            "Imperative requests",
            "Merely mentioning, quoting, explaining, reviewing, tuning, or editing",
            "$tune` / `$refine` win",
        ):
            self.assertIn(phrase, SKILL)

    def test_mixed_intent_does_not_discard_execution(self) -> None:
        self.assertIn(
            "the execution owner may use this reasoning internally",
            SKILL,
        )
        self.assertIn(
            "must not seize the turn and discard the requested execution",
            SKILL,
        )

    def test_interface_prompt_preserves_meta_and_stop_boundaries(self) -> None:
        for phrase in (
            "next task is choosing among materially",
            "mention of the skill is not an",
            "evidence-aware Aha",
            "materially different frame shifts",
            "stop for human selection",
            "skill analysis",
            "or tuning",
            "($ideate)",
            "($plan)",
        ):
            self.assertIn(phrase, AGENT)

    def test_stage_model_keeps_develop_and_deliver_distinct(self) -> None:
        stage = skill_section("## Double Diamond alignment", "## Mode check")
        self.assertIn("Develop: the problem is sufficiently defined", stage)
        self.assertIn("Deliver: the core direction is selected", stage)
        self.assertIn("Do not use Deliver to regenerate competing core solutions", stage)

    def test_aha_check_preserves_creative_insight_and_evidence_discipline(self) -> None:
        for phrase in (
            "## Aha Check",
            "Aha is the restructuring insight",
            "from the baseline frame to the alternative frame",
            "fact | supported inference | hypothesis",
            "An Aha may be a hypothesis",
            "Never promote an unsupported mechanism, bottleneck, or causal story to fact",
            "make validation part of the expected signal",
            "Aha: N/A after second pass",
        ):
            self.assertIn(phrase, SKILL)
        self.assertNotIn("## Frame Shift Check", SKILL)

    def test_pragmatic_mode_bounds_every_tier(self) -> None:
        for phrase in (
            "every tier is a bounded, reversible next move",
            "Tiers describe the ambition of the hypothesis, not the size of the first commitment",
            "smallest proof-bearing probe of discontinuous upside",
        ):
            self.assertIn(phrase, SKILL)

    def test_fast_and_full_lanes_have_distinct_visible_surfaces(self) -> None:
        deliverable = skill_section("## Deliverable format", "## Fast Spark example")
        self.assertIn("### Fast Spark", deliverable)
        self.assertIn("### Full Session", deliverable)
        self.assertIn("Optional scorecard", deliverable)
        fast = deliverable.split("### Fast Spark", 1)[1].split("### Full Session", 1)[0]
        self.assertNotIn("scorecard", fast.lower())
        self.assertNotIn("Decision Log", deliverable)
        self.assertNotIn("Insights Summary", deliverable)

    def test_tier_semantics_and_selection_avoid_quick_win_default(self) -> None:
        for phrase in (
            "Quick Win: cheapest reversible move",
            "Advantage Play: creates a reusable capability",
            "Transformative Move: changes an interface",
            "Moonshot: tests discontinuous upside",
            "best learning bet, best near-term outcome bet, and boldest bounded probe",
            "Do not rank by a summed total",
            "A recommendation is not execution authorization",
        ):
            self.assertIn(phrase, SKILL)

    def test_execution_handoff_has_no_stale_tk_owner(self) -> None:
        self.assertNotIn("`tk`", SKILL)
        for phrase in (
            "hand off to `$plan`",
            "owning implementation workflow",
            "This skill never owns repository mutation",
        ):
            self.assertIn(phrase, SKILL)

    def test_fast_spark_example_conforms_and_does_not_invent_a_bottleneck(self) -> None:
        example_section = skill_section("## Fast Spark example", "## Routing examples")
        example = example_section.split("```text", 1)[1].split("```", 1)[0]
        for phrase in (
            "Lane: Fast Spark",
            "Stage: Develop",
            "Evidence:",
            "Aha:",
            "[evidence: hypothesis]",
            "Why it matters:",
            "Default basin:",
            "Artifact Spine:",
            "Quick Win —",
            "Strategic Play —",
            "Advantage Play —",
            "Transformative Move —",
            "Moonshot —",
            "Selection guidance:",
            "Conditional recommendation:",
            "Human Input Required:",
        ):
            self.assertIn(phrase, example)
        self.assertEqual(5, example.count("- Accretive artifact (spine):"))
        self.assertEqual(5, example.count("- Expected signal + timebox:"))
        self.assertEqual(5, example.count("- Escape hatch:"))
        self.assertNotIn("dominant cost is", example.lower())
        self.assertLessEqual(len(example.splitlines()), 65)

    def test_routing_corpus_covers_adversarial_near_misses(self) -> None:
        self.assertEqual("creative-problem-solver-routing-cases/v1", CORPUS["schema"])
        cases = CORPUS["cases"]
        ids = [case["id"] for case in cases]
        self.assertEqual(len(ids), len(set(ids)))
        positives = [case for case in cases if case["activate"]]
        negatives = [case for case in cases if not case["activate"]]
        self.assertGreaterEqual(len(positives), 10)
        self.assertGreaterEqual(len(negatives), 15)
        self.assertTrue(
            {
                "direct",
                "implementation",
                "ideate",
                "plan",
                "codebase-archaeology",
                "review",
                "tune",
                "refine",
                "debugging",
            }
            <= {case["owner"] for case in negatives}
        )
        for required_id in (
            "explicit-skill-imperative",
            "selected-direction-rollout-options",
            "skill-analysis-mention",
            "skill-edit-mention",
            "skill-refine-brief",
            "keyword-bearing-debugging",
            "ordinary-name-brainstorm",
            "mixed-options-and-implementation",
            "explain-skill-concept",
        ):
            self.assertIn(required_id, ids)

    def test_routing_examples_surface_the_hard_boundaries(self) -> None:
        routing = SKILL.split("## Routing examples", 1)[1]
        for phrase in (
            "deep analysis of my `$creative-problem-solver` skill",
            "Patch `$creative-problem-solver`",
            "blocked by this compiler error",
            "Brainstorm twenty names",
            "choose the best, and implement it now",
            "We selected event sourcing",
        ):
            self.assertIn(phrase, routing)

    def test_skill_stays_within_compact_package_budget(self) -> None:
        self.assertLessEqual(len(SKILL.splitlines()), 280)


if __name__ == "__main__":
    unittest.main()