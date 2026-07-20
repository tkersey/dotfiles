"""Run: uv run --with pyyaml -- python3 -m unittest discover -s codex/skills/creative-problem-solver/tests -p 'test_*.py' -v"""

from __future__ import annotations

import json
from pathlib import Path
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
AGENT = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
AGENT_DATA = yaml.safe_load(AGENT)


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


CORPUS = json.loads(
    (ROOT / "evals" / "routing-cases.json").read_text(encoding="utf-8"),
    object_pairs_hook=reject_duplicate_keys,
)

FAST_SPARK_LINE_LIMIT = 45
FULL_SESSION_LINE_LIMIT = 70

EXPECTED_AGENT = """policy:
  allow_implicit_invocation: true
interface:
  display_name: "Creative Problem Solver"
  short_description: "Generate materially different strategy options before execution"
  default_prompt: "Use $creative-problem-solver to generate a five-tier portfolio for this decision."
"""

EXPECTED_CASES = {
    "explicit-options": (
        "Give me several materially different ways to reduce onboarding drop-off before we choose one.",
        "creative-problem-solver",
    ),
    "tradeoff-portfolio": (
        "Map the trade-offs between building, buying, and partnering, then include a credible moonshot.",
        "creative-problem-solver",
    ),
    "stalled-repeated-failure": (
        "We have tried tuning the query twice and are still stuck. What else could we try?",
        "creative-problem-solver",
    ),
    "reframe-migration": (
        "Reframe this migration problem and show several distinct paths before execution.",
        "creative-problem-solver",
    ),
    "ordinary-strategy-brainstorm": (
        "Brainstorm a strategy portfolio for entering this market; do not execute anything yet.",
        "creative-problem-solver",
    ),
    "architecture-choice-set": (
        "Show several architecture paths for multi-region failover and how we could learn before committing.",
        "creative-problem-solver",
    ),
    "ambiguous-learning-moves": (
        "The problem is still ambiguous; give me learning moves rather than a build plan.",
        "creative-problem-solver",
    ),
    "explicit-skill-imperative": (
        "Use $creative-problem-solver to generate a five-tier portfolio for this decision.",
        "creative-problem-solver",
    ),
    "selected-direction-rollout-options": (
        "We selected event sourcing; show materially different rollout, containment, and proof strategies before execution.",
        "creative-problem-solver",
    ),
    "high-uncertainty-cross-domain-choice": (
        "We need several distinct ways to redesign this partner integration across product, legal, and operations before choosing a path.",
        "creative-problem-solver",
    ),
    "bare-skill-name": ("$creative-problem-solver", "direct"),
    "imperative-skill-without-portfolio-object": (
        "Use $creative-problem-solver.",
        "direct",
    ),
    "direct-implementation": (
        "Implement the selected cache design and run the tests.",
        "implementation",
    ),
    "single-factual-answer": ("What does this compiler error mean?", "direct"),
    "repo-opportunity-mining": (
        "Mine this repository for evidence-backed product and DX opportunities and rank what to plan next.",
        "ideate",
    ),
    "selected-direction-plan": (
        "Turn the chosen event-sourcing direction into a detailed implementation plan.",
        "plan",
    ),
    "architecture-onboarding": (
        "Explain this repository's architecture and data flow so I can get oriented.",
        "codebase-archaeology",
    ),
    "pull-request-review": ("Review this pull request for defects.", "review"),
    "chosen-tier-execution": ("We chose the Quick Win. Build it now.", "implementation"),
    "small-known-comparison": (
        "Compare these two already-selected retry policies and recommend one.",
        "direct",
    ),
    "skill-analysis-mention": (
        "Do a deep analysis of my $creative-problem-solver skill.",
        "tune",
    ),
    "skill-edit-mention": (
        "Patch $creative-problem-solver so it stops over-triggering.",
        "tune",
    ),
    "skill-refine-brief": (
        "Apply this complete REFINE-SKILL-v3 brief to $creative-problem-solver and validate the package.",
        "refine",
    ),
    "keyword-bearing-debugging": (
        "I am blocked by this compiler error. What else can I try?",
        "debugging",
    ),
    "ordinary-name-brainstorm": ("Brainstorm twenty names for this command.", "direct"),
    "mixed-options-and-implementation": (
        "Give me several options, choose the best one, and implement it now.",
        "implementation",
    ),
    "explain-skill-concept": (
        "What does $creative-problem-solver mean by Artifact Spine?",
        "direct",
    ),
}

TIER_NAMES = (
    "Quick Win",
    "Strategic Play",
    "Advantage Play",
    "Transformative Move",
    "Moonshot",
)

SPINE_HOMES = (
    "bench/search/",
    "perf/tracing/",
    "contracts/search-response/",
)

EXPECTED_SIGNALS = {
    "Quick Win": (
        "within 1 day, run exactly 5 fixed-fixture batches of exactly 1,000 requests and "
        "decompose the 10 slowest requests in each batch; Pass iff the 95% bootstrap CI "
        "lower bound for pooled mean non-query share is >=10%; Claim falsifier: Fail iff "
        "its upper bound is <10%; Inconclusive otherwise -> run one additional "
        "predeclared set of exactly 5 such batches before selection."
    ),
    "Strategic Play": (
        "within 2 days, run the candidate and immutable pre-change bench/search/ baseline "
        "for exactly 5 fixed-fixture batches of exactly 1,000 requests each, including "
        "exactly 100 predeclared relevancy cases per batch; let B=baseline pooled p95 and "
        "C=candidate pooled p95; Pass iff (B-C)/B >=30% and all 500 candidate relevancy "
        "results match baseline; Fail otherwise."
    ),
    "Advantage Play": (
        "within 2 days, inject a predeclared fixture whose p95 is >=20% above the fixed "
        "bench/search/ baseline; Pass iff two consecutive check runs both reject it "
        "before merge; Fail otherwise."
    ),
    "Transformative Move": (
        "within 3 days, across two runs per fixture, Pass iff first useful bytes arrive "
        "<=200ms on all exactly 10 predeclared fixtures with a >=1 MiB response body; "
        "Fail otherwise."
    ),
    "Moonshot": (
        "within 1 week, run exactly 3 candidates and the immutable pre-change bench/search/ "
        "baseline for exactly 5 fixed-fixture batches each; let B=baseline pooled p99 and "
        "C_i=each candidate's pooled p99; Pass iff at least one of the 3 satisfies "
        "3*C_i <= B; "
        "Fail otherwise."
    ),
}

EXPECTED_ESCAPES = {
    "Quick Win": (
        "disable high-overhead tracing; retain the bench/search/ harness plus "
        "perf/tracing/ batch results and every slowest-1% request decomposition."
    ),
    "Strategic Play": (
        "feature flag or revert the production change; retain the bench/search/ "
        "fixture, result, and diagnosis."
    ),
    "Advantage Play": (
        "begin as an advisory check; keep the bench/search/ seeded fixture, check, and "
        "trend data if gating is noisy."
    ),
    "Transformative Move": (
        "disable the opt-in endpoint, retain the current response as default, and "
        "keep contracts/search-response/ fixtures plus bench/search/ results."
    ),
    "Moonshot": (
        "stop before migration; keep the bench/search/ adapter, fixtures, and results "
        "as durable decision evidence."
    ),
}


def skill_section(start: str, end: str) -> str:
    return SKILL.split(start, 1)[1].split(end, 1)[0]


def fast_spark_example() -> str:
    section = skill_section("## Fast Spark example", "## Routing examples")
    return section.split("```text", 1)[1].split("```", 1)[0]


def declared_spine_homes(example: str) -> tuple[str, ...]:
    spine = example.split("Artifact Spine:", 1)[1].split("Quick Win —", 1)[0]
    return tuple(re.findall(r"^- ([^:]+/):", spine, re.MULTILINE))


class ActivationContractTests(unittest.TestCase):
    def test_implicit_invocation_is_enabled(self) -> None:
        self.assertIn("allow_implicit_invocation: true", AGENT)
        self.assertNotIn("allow_implicit_invocation: false", AGENT)

    def test_frontmatter_names_positive_negative_and_meta_boundaries(self) -> None:
        frontmatter = SKILL.split("---", 2)[1]
        for phrase in (
            "next task is choosing among materially different paths",
            "options, alternatives, trade-offs, reframing",
            "A name-only or meta mention does not authorize the portfolio route",
            "direct implementation",
            "skill analysis/tuning",
            "repository-evidence opportunity mining ($ideate)",
            "detailed planning ($plan)",
        ):
            self.assertIn(phrase, frontmatter)

    def test_activation_boundary_separates_host_loading_from_portfolio_route(self) -> None:
        self.assertLess(SKILL.index("## Activation boundary"), SKILL.index("## Contract"))
        for phrase in (
            "Host loading is not portfolio authorization",
            "portfolio route requires",
            "Difficulty, uncertainty, creativity language",
            "to generate a strategy portfolio",
            "may load the package under host policy",
            "does not authorize portfolio generation",
            "$tune` / `$refine` win",
        ):
            self.assertIn(phrase, SKILL)

    def test_mixed_intent_does_not_discard_execution(self) -> None:
        self.assertIn("the execution owner may use this reasoning internally", SKILL)
        self.assertIn("must not seize the turn and discard the requested execution", SKILL)

    def test_interface_prompt_preserves_owner_and_stop_boundaries(self) -> None:
        self.assertEqual(EXPECTED_AGENT, AGENT)
        self.assertEqual({"policy", "interface"}, set(AGENT_DATA))
        self.assertIs(True, AGENT_DATA["policy"]["allow_implicit_invocation"])
        self.assertIsInstance(AGENT_DATA["interface"]["display_name"], str)
        self.assertIsInstance(AGENT_DATA["interface"]["short_description"], str)
        self.assertIsInstance(AGENT_DATA["interface"]["default_prompt"], str)
        self.assertEqual(
            EXPECTED_CASES["explicit-skill-imperative"][0],
            AGENT_DATA["interface"]["default_prompt"],
        )

    def test_stage_model_keeps_develop_and_deliver_distinct(self) -> None:
        stage = skill_section("## Double Diamond alignment", "## Mode check")
        self.assertIn("Develop: the problem is sufficiently defined", stage)
        self.assertIn("Deliver: the core direction is selected", stage)
        self.assertIn("Do not use Deliver to regenerate competing core solutions", stage)
        self.assertIn("Definition Gate fields are:", SKILL)
        self.assertIn("symptom, actors, and problem topology", SKILL)
        self.assertIn("desired outcome and success criteria", SKILL)
        self.assertIn("metric, threshold, and measurement basis", SKILL)
        self.assertIn("representative workload", SKILL)
        self.assertIn("constraints and guardrails", SKILL)
        self.assertIn("If any field in the first two groups is missing, use Discover", SKILL)
        self.assertIn("if every field there is recorded or inapplicable", SKILL)
        self.assertIn("but any later field is missing, use Define", SKILL)
        self.assertIn("do not silently choose a domain or metric", SKILL)
        self.assertIn("Interpretation (assumption): ...", SKILL)
        self.assertIn("Target success: unknown", SKILL)
        self.assertIn("Portfolio success: <decision progress>", SKILL)
        self.assertIn("never substitute process success for the target outcome", SKILL)
        self.assertIn("While any Definition Gate field is missing", SKILL)
        self.assertIn("all five tiers must reduce uncertainty without proposing solution prototypes", SKILL)
        self.assertIn("do not choose an index, cache, interface, engine, substrate", SKILL)
        self.assertIn("Quick Win signal passes only when every Definition Gate field", SKILL)
        self.assertIn("explicitly recorded or marked inapplicable", SKILL)
        self.assertIn("make every later tier conditional on that gate", SKILL)
        self.assertIn(
            "The Quick Win signal and every later prerequisite clause must spell out all "
            "six field groups rather than refer to \"the gate,\" \"each field,\" or a "
            "nearby artifact.",
            SKILL,
        )
        self.assertIn(
            "Preserve tier semantics even here: a Transformative probe must test a "
            "changed interface, operating model, governing constraint, or user ritual "
            "rather than merely inventorying the current one.",
            SKILL,
        )
        self.assertIn("test discontinuous learning or proof leverage", SKILL)
        self.assertIn("predeclared discontinuous threshold rather than mere completeness", SKILL)
        self.assertIn("silently verify exact spine-name reuse", SKILL)
        self.assertIn("mutually exclusive and exhaustive outcomes", SKILL)
        self.assertIn("literal entailment of every fact", SKILL)
        self.assertIn("repair every miss before replying", SKILL)

    def test_aha_check_preserves_creative_insight_and_evidence_discipline(self) -> None:
        for phrase in (
            "## Aha Check",
            "Aha is the restructuring insight",
            "from the baseline frame to the alternative frame",
            "without an epistemic label",
            "a representational operation is not itself a factual proposition",
            "Aha basis: <why this shift is warranted> [evidence: fact | supported inference]",
            "Claim: <claim> [evidence: fact | supported inference | hypothesis]",
            "Use `hypothesis` only for a concrete claim with a real falsifier",
            "For a `Claim` labeled fact or supported inference",
            "name its source or support in the evidence posture or adjacent to the Claim",
            "Never promote an unsupported mechanism, bottleneck, or causal story to fact",
            "make validation part of an expected signal",
            "For every `Claim` labeled hypothesis",
            "one expected signal must include `Claim falsifier: <observation>`",
            "test that exact claim, not a neighboring assertion",
            "Second reframe used: <technique>",
            "never credit an undeclared operator later",
            "Aha: N/A after second pass",
        ):
            self.assertIn(phrase, SKILL)
        self.assertNotIn("## Frame Shift Check", SKILL)

    def test_pragmatic_mode_and_same_basin_exception_are_bounded(self) -> None:
        contract = skill_section("## Contract", "## Workflow")
        diversity = skill_section("## Diversity guard", "## Accretion")
        for phrase in (
            "every tier is a bounded, reversible next move",
            "Tiers describe the ambition of the hypothesis, not the size of the first commitment",
            "smallest proof-bearing probe of discontinuous upside",
            "first probe of at most one week",
            "cannot replace this first signal",
            "Put every escape hatch before an irreversible boundary",
            "is not reversibility",
        ):
            self.assertIn(phrase, SKILL)
        self.assertIn("when honest", contract)
        self.assertIn("same-basin rather than manufacturing diversity", contract)
        self.assertIn("Do not manufacture an Aha or diversity", SKILL)
        self.assertIn("mark the portfolio as same-basin", diversity)

    def test_lane_selector_and_visible_surfaces_are_decision_complete(self) -> None:
        lane = skill_section("## Lane selector", "## Reframe selection")
        deliverable = skill_section("## Deliverable format", "## Fast Spark example")
        budgets = re.search(
            r"Fast Spark must fit <=(\d+) non-empty output lines; "
            r"Full Session must fit <=(\d+) non-empty output lines",
            SKILL,
        )
        self.assertIsNotNone(budgets)
        assert budgets is not None
        self.assertEqual(
            (FAST_SPARK_LINE_LIMIT, FULL_SESSION_LINE_LIMIT),
            tuple(int(value) for value in budgets.groups()),
        )
        for phrase in (
            "Fast Spark: default when context is sufficient",
            "Full Session: use when the user explicitly asks for deep or exhaustive exploration",
            "high stakes, irreversibility, or coupled constraints",
            "If lane choice is unclear, choose Fast Spark",
            "Difficulty alone does not justify Full Session",
        ):
            self.assertIn(phrase, lane)
        self.assertIn("### Fast Spark", deliverable)
        self.assertIn("### Full Session", deliverable)
        self.assertIn("Optional scorecard", deliverable)
        self.assertIn(
            "evidence-label every causal or decision-shaping inference, including "
            "stage choice, reframe `Why`, winnowing, diversity/same-basin disposition, "
            "score interpretation, and recommendations",
            deliverable,
        )
        for label in ("Facts:", "Risks:", "Assets:", "Assumptions:", "Constraints:"):
            self.assertIn(label, deliverable)
        fast = deliverable.split("### Fast Spark", 1)[1].split("### Full Session", 1)[0]
        self.assertNotIn("scorecard", fast.lower())
        self.assertNotIn("Decision Log", deliverable)
        self.assertNotIn("Insights Summary", deliverable)

    def test_tier_semantics_and_selection_avoid_quick_win_default(self) -> None:
        for phrase in (
            "Quick Win: cheapest reversible move",
            "Strategic Play: strongest path within the current operating model",
            "Advantage Play: creates a reusable capability",
            "Transformative Move: changes an interface",
            "Moonshot: tests discontinuous upside",
            "best learning bet, best near-term outcome bet, and boldest bounded probe",
            "Best near-term outcome bet: none; basis: target success is undefined. "
            "[evidence: fact]",
            "rather than relabeling decision progress as the target outcome",
            "Treat every unmeasured `best` or recommendation ranking as supported "
            "inference or hypothesis, never fact",
            "name its basis and end it with that evidence label",
            "Impact, Information, Accretion, Confidence, Reversibility, and Time-to-signal",
            "for Time-to-signal, 5 means faster",
            "Do not rank by a summed total",
            "Compute dominance across all displayed dimensions",
            "Pareto leaders: <every non-dominated tier by name>",
            "if dominance was not checked, omit the Pareto claim",
            "End every `best` selection and recommendation line with",
            "and name its basis",
            "A recommendation is not execution authorization",
        ):
            self.assertIn(phrase, SKILL)

    def test_artifact_spine_requires_named_reuse_and_retention(self) -> None:
        accretion = skill_section("## Accretion", "## Tier semantics")
        for phrase in (
            "each with a stable name and home",
            "Every `Accretive artifact` line must repeat at least one exact declared asset name or home",
            "an unqualified new artifact is invalid",
            "declare and justify a replacement spine before the portfolio",
            "Every escape hatch must name the proof artifact retained",
            "Retaining only an undeclared by-product does not satisfy accretion",
            "The retained artifact proves only observations bound by the signal",
            "do not call ritual or artifact completion proof of benefit without a comparator",
            "Full Session: repeat each asset's purpose and home, add its minimal interface",
            "partition every outcome with mutually exclusive, exhaustive clauses",
            "Inconclusive iff any of <named prerequisites> is missing -> <next disposition>",
            "otherwise Pass iff <success>; Fail otherwise",
            "for a legitimate measured third state",
            "Fail iff <falsifier>; Inconclusive otherwise -> <next disposition>",
            "omit Inconclusive when Pass and Fail are complements",
            "Every value or predicate consumed by Pass must be established or named "
            "separately in Inconclusive",
            "Every missing-prerequisite Inconclusive clause must use the exact `any of "
            "... is missing` form",
            "put all missing prerequisites in that one list",
            "Quantified item outcomes use integer counts such as `at least 1 of n`",
            "require a named baseline or denominator, comparison rule, predeclared threshold, and replication count",
            "references to recorded or agreed criteria do not satisfy this rule",
            "stable, comparable, beyond noise",
            "Terms such as `complete`, `representative`, `correct`, or `compatible` "
            "require their operational fields or selection rule in the signal, not an "
            "adjective standing in for a predicate.",
            "Any use of `falsify` or `falsifier` must state the predeclared observation "
            "predicate for each hypothesis",
            "must predeclare a nonzero finite denominator; an empty set is Inconclusive "
            "or Fail, never Pass",
            "resolve that threshold instead of claiming an unspecified target will be met",
        ):
            self.assertIn(phrase, accretion)

    def test_execution_handoff_has_no_stale_tk_owner(self) -> None:
        self.assertNotIn("`tk`", SKILL)
        for phrase in (
            "hand off to `$plan`",
            "owning implementation workflow",
            "This skill never owns repository mutation",
        ):
            self.assertIn(phrase, SKILL)

    def test_fast_spark_example_enforces_evidence_spine_diversity_and_stop(self) -> None:
        example = fast_spark_example()
        self.assertIn(
            "Evidence: latency, gate fields, and targets are known; the bottleneck is unknown.",
            example,
        )
        self.assertEqual(
            "Stage: Develop",
            next(line for line in example.splitlines() if line.startswith("Stage: ")),
        )
        gate_line = next(
            line for line in example.splitlines() if line.startswith("Definition Gate: ")
        )
        for field in (
            "domain=",
            "symptom/actors/topology=",
            "desired outcome/success=",
            "metric/threshold/basis=",
            "representative workload population/selection rule=",
            "constraints/guardrails=",
        ):
            self.assertIn(field, gate_line)
        self.assertIn(
            "symptom/actors/topology=p95 ~800ms across API clients -> search service -> "
            "query engine -> serialization/transport",
            gate_line,
        )
        self.assertNotRegex(gate_line, r"(?i)\b(?:unknown|missing)\b")
        self.assertIn(
            "exactly 5 fixed-fixture batch results and all 50 slowest-1% request decompositions",
            example,
        )
        aha_line = next(line for line in example.splitlines() if line.startswith("Aha: "))
        claim_line = next(line for line in example.splitlines() if line.startswith("Claim: "))
        self.assertNotIn("[evidence:", aha_line)
        self.assertIn("Aha basis:", example)
        self.assertIn(
            "Aha basis: the reported p95 spans the listed request path, and the bottleneck "
            "is unknown. [evidence: fact]",
            example,
        )
        self.assertEqual(
            "Claim: across repeated fixed-fixture batches, the pooled mean non-query "
            "share among requests in each batch's slowest 1% is >=10%. "
            "[evidence: hypothesis]",
            claim_line,
        )
        self.assertIn("[evidence: hypothesis]", example)
        hypothesis_claims = [
            line
            for line in example.splitlines()
            if line.startswith("Claim: ") and "[evidence: hypothesis]" in line
        ]
        self.assertEqual(1, len(hypothesis_claims))
        self.assertEqual(len(hypothesis_claims), example.count("Claim falsifier:"))
        self.assertNotIn("dominant cost is", example.lower())

        declared_spine = declared_spine_homes(example)
        self.assertEqual(SPINE_HOMES, declared_spine)

        heading_pattern = re.compile(
            r"^(Quick Win|Strategic Play|Advantage Play|Transformative Move|Moonshot)"
            r" .+ \[frame: ([^\]]+)\]$",
            re.MULTILINE,
        )
        headings = heading_pattern.findall(example)
        self.assertEqual(list(TIER_NAMES), [name for name, _ in headings])
        self.assertGreaterEqual(len({frame for _, frame in headings}), 2)

        for index, tier in enumerate(TIER_NAMES):
            start = example.index(f"{tier} —")
            end = (
                example.index(f"{TIER_NAMES[index + 1]} —")
                if index + 1 < len(TIER_NAMES)
                else example.index("Best learning bet:")
            )
            block = example[start:end]
            artifact = re.search(r"^- Accretive artifact \(spine\): (.+)$", block, re.MULTILINE)
            signal = re.search(r"^- Expected signal \+ timebox: (.+)$", block, re.MULTILINE)
            escape = re.search(r"^- Escape hatch: (.+)$", block, re.MULTILINE)
            self.assertIsNotNone(artifact, tier)
            self.assertIsNotNone(signal, tier)
            self.assertIsNotNone(escape, tier)
            assert artifact is not None
            assert signal is not None
            assert escape is not None
            self.assertTrue(any(home in artifact.group(1) for home in declared_spine), tier)
            self.assertTrue(any(home in escape.group(1) for home in declared_spine), tier)
            for value in (artifact.group(1), signal.group(1), escape.group(1)):
                self.assertNotRegex(
                    value,
                    r"(?i)\b(?:TBD|TODO|placeholder)\b|<[A-Za-z][A-Za-z0-9 _-]*>",
                    tier,
                )
            self.assertRegex(signal.group(1), r"\b(?:within|day|week|hour|minute)s?\b", tier)
            self.assertRegex(escape.group(1), r"\b(?:retain|keep)\b", tier)
            self.assertEqual(EXPECTED_SIGNALS[tier], signal.group(1), tier)
            self.assertEqual(EXPECTED_ESCAPES[tier], escape.group(1), tier)

            duration = re.search(
                r"\bwithin (\d+) (minute|hour|day|week)s?\b",
                signal.group(1).lower(),
            )
            self.assertIsNotNone(duration, tier)
            assert duration is not None
            count = int(duration.group(1))
            unit_days = {"minute": 1 / 1440, "hour": 1 / 24, "day": 1, "week": 7}
            self.assertLessEqual(count * unit_days[duration.group(2)], 7, tier)

        self.assertTrue(
            example.strip().endswith(
                "Human Input Required: choose a tier or update the constraints."
            )
        )
        for line in (
            "Best learning bet: Quick Win, because it identifies which path budget owns "
            "the uncertainty. [evidence: supported inference]",
            "Best near-term outcome bet: Strategic after tracing, because it attacks the "
            "measured largest budget against the fixed baseline. [evidence: supported inference]",
            "Boldest bounded probe: Moonshot, because three candidates test discontinuous "
            "latency upside before migration. [evidence: supported inference]",
            "Conditional recommendation: start with Quick Win, then choose Strategic or "
            "Transformative from measured evidence because both preserve the shared proof "
            "spine. [evidence: supported inference]",
        ):
            self.assertIn(line, example)
        nonempty_lines = [line for line in example.splitlines() if line.strip()]
        self.assertLessEqual(len(nonempty_lines), FAST_SPARK_LINE_LIMIT)

    def test_routing_corpus_is_a_total_exact_semantic_case_map(self) -> None:
        self.assertEqual({"schema", "cases"}, set(CORPUS))
        self.assertEqual("creative-problem-solver-routing-cases/v2", CORPUS["schema"])
        cases = CORPUS["cases"]
        self.assertEqual(len(EXPECTED_CASES), len(cases))
        by_id = {case["id"]: case for case in cases}
        self.assertEqual(set(EXPECTED_CASES), set(by_id))

        for case_id, case in by_id.items():
            self.assertEqual({"id", "prompt", "route"}, set(case), case_id)
            self.assertIsInstance(case["prompt"], str, case_id)
            self.assertTrue(case["prompt"].strip(), case_id)

        actual_cases = {
            case_id: (case["prompt"], case["route"])
            for case_id, case in by_id.items()
        }
        self.assertEqual(EXPECTED_CASES, actual_cases)

    def test_routing_examples_surface_the_hard_boundaries(self) -> None:
        routing = SKILL.split("## Routing examples", 1)[1]
        for phrase in (
            "deep analysis of my `$creative-problem-solver` skill",
            '"`$creative-problem-solver`" -> direct clarification',
            '"Use `$creative-problem-solver`." -> direct clarification',
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
