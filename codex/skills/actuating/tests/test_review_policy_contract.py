#!/usr/bin/env -S uv run python
from __future__ import annotations

from pathlib import Path
import unittest


ACTUATING_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ACTUATING_ROOT.parent


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


ACTUATING = normalized(ACTUATING_ROOT / "SKILL.md")
GOAL_ACTUATING = normalized(SKILLS_ROOT / "goal-actuating" / "SKILL.md")
GOAL_GRIND = normalized(SKILLS_ROOT / "goal-grind" / "SKILL.md")
REVIEW_POLICY = normalized(ACTUATING_ROOT / "references" / "review-policy.md")
REVIEW_RESOLUTION = normalized(
    ACTUATING_ROOT / "references" / "review-resolution.md"
)
LIVE_SEMANTICS = normalized(
    ACTUATING_ROOT / "references" / "live-semantics.yaml"
)
DECISION_CONTRACT = normalized(
    ACTUATING_ROOT / "references" / "decision-contract.yaml"
)


class ActuatingReviewPolicyContractTests(unittest.TestCase):
    def test_verdictless_transport_failure_is_request_local(self) -> None:
        required = [
            "terminal `review_failed` fact with no structured tuple verdict",
            "move only that request to `rerun-required`",
            "leave every sibling state and the standard clean suffix unchanged",
            "`--fresh-attempt <source-bound-reason>`",
            "Do not call the whole wave zero-credit",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, ACTUATING)

    def test_goal_controller_has_total_failure_transition(self) -> None:
        required = [
            "Apply this request-local transition table exactly",
            "only that request becomes `rerun-required`",
            "keep siblings running, then rerun only that request",
            "`--fresh-attempt <source-bound-reason>`",
            "A verdictless failure terminates one dispatch handle, not the policy request",
            "Do not describe the whole wave as zero-credit",
            "Capacity pressure changes neither the concurrency law nor request accounting",
            "leave the request `rerun-required` and block rather than retrying indefinitely",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, GOAL_ACTUATING)

    def test_standard_findings_and_named_invalidation_remain_distinct(self) -> None:
        goal_required = [
            "reset only when the request is standard",
            "launch one new full concurrent wave",
            "standard findings, contract or registry drift, base movement, and unrelated edits always reset it",
        ]
        for token in goal_required:
            with self.subTest(surface="goal-actuating", token=token):
                self.assertIn(token, GOAL_ACTUATING)

        policy_required = [
            "valid standard findings -> append the finding fact and reset the trailing standard clean suffix",
            "A full replacement wave is legal only after a named invalidation",
            "that wave remains concurrent",
        ]
        for token in policy_required:
            with self.subTest(surface="review-policy", token=token):
                self.assertIn(token, REVIEW_POLICY)

    def test_policy_keeps_failure_out_of_credit_projection(self) -> None:
        required = [
            "### Verdictless transport failure",
            "`tupleVerdictExists=false`",
            "do not append it to `requests[].attempts` or `standard_clean_chain`",
            "Set only its bound request to `rerun-required`",
            "same-tuple failed-request recovery",
            "rerun that exact request only",
            "so CAS creates a new independent attempt instead of returning the existing terminal fact",
            "leave the request `rerun-required` and block rather than retrying indefinitely",
            "A full replacement wave is legal only after a named invalidation",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, REVIEW_POLICY)

    def test_resolution_waits_for_request_local_recovery(self) -> None:
        required = [
            "resolve every request-local `rerun-required` transport failure",
            "terminalizes only its dispatch",
            "Neither fact cancels sibling requests",
            "After the wave and resolution barriers",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, REVIEW_RESOLUTION)

    def test_live_semantics_names_the_boundary_law(self) -> None:
        required = [
            "request-local-review-transport-failure",
            "changes only its bound request to rerun-required",
            "preserves every sibling and the standard suffix",
            "never authorizes whole-wave zeroing, sibling cancellation, or sequential relaunch",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, LIVE_SEMANTICS)

    def test_decision_contract_makes_wrong_routes_auditable(self) -> None:
        required = [
            "verdictless review_failed changes only its request to rerun-required",
            "same-tuple transport recovery reruns only the failed request",
            "a second verdictless terminal fact blocks with that request unresolved",
            "verdictless review_failed is treated as whole-wave zero credit",
            "a same-tuple transport failure restarts or serializes the full wave",
            "exact-request transport recovery retries indefinitely",
            "while a request remains rerun-required",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, DECISION_CONTRACT)

    def test_resolution_synthesizes_cumulative_structural_components(self) -> None:
        required = [
            "## Owner-boundary synthesis",
            "`owner-boundary-synthesis/v1`",
            "all current accepted classes plus the current goal's retained resolution history",
            "Derive `stable_component_key` only from `boundary_identity`",
            "owner-boundary-synthesis/boundary-identity/v1\\n",
            "sort every array lexicographically before encoding",
            "implementation-specific owner names",
            "must not contain or derive from a review generation, tuple, commit, publication, source batch, or attempt identity",
            "once for each cumulative structural component, not once independently for each finding class",
            "recurrence-after-repair",
            "multiple-law-owners",
            "new-semantic-machinery",
            "multi-abstraction-displacement",
            "post-kernel-symptom-repair",
            "reuse-owner | converge-kernel | separate-laws | blocked",
            "A per-class candidate construction is not repair authority",
            "Source growth, file count, and comment count are prompts to inspect these signals, not proof that a new abstraction is warranted",
            "split the structural component first",
            "`observation_ref`",
            "A repair-bearing mutation preflight materializes exactly one",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, REVIEW_RESOLUTION)

    def test_actuating_routes_structural_pressure_before_local_repair(self) -> None:
        required = [
            "Invoke `$universalist` once per cumulative structural component, not once independently per finding class",
            "another local repair is not a legal default",
            "allow `local-repair` only from `reuse-owner` with no structural pressure",
            "project the synthesis-owned resolution node",
            "every synthesis structural obligation observed",
            "Ledger 0.9.0 or newer",
            "structural class-to-synthesis-to-refinement join",
        ]
        for token in required:
            with self.subTest(token=token):
                self.assertIn(token, ACTUATING)

    def test_coordinator_owns_synthesis_and_executor_only_executes(self) -> None:
        coordinator_required = [
            "owner-boundary-synthesis/v1 for each component",
            "A generation, tuple, commit, publication, source batch, or attempt suffix is provenance, never a new structural identity",
            "Invoke `$universalist` once per cumulative component",
            "A class-local construction cannot independently select a repair",
            "The current resolution may select at most one synthesis-owned node",
            "repair-bearing mutation preflight must select exactly one",
        ]
        for token in coordinator_required:
            with self.subTest(surface="goal-actuating", token=token):
                self.assertIn(token, GOAL_ACTUATING)

        executor_required = [
            "owner_synthesis_ref: # review edits only",
            "Execute the synthesis-owned node exactly as selected",
            "do not reconsider the synthesis disposition, choose repair strategy, or split the node into finding-shaped work",
        ]
        for token in executor_required:
            with self.subTest(surface="goal-grind", token=token):
                self.assertIn(token, GOAL_GRIND)
        self.assertGreaterEqual(GOAL_GRIND.count("owner_synthesis_ref:"), 2)
        self.assertNotIn("Prefer `replacement-kernel`", GOAL_GRIND)

    def test_synthesis_boundary_is_auditable(self) -> None:
        semantics_required = [
            "owner-boundary-synthesis/v1",
            "cumulative-owner-synthesis",
            "implementation owner names and generation, tuple, commit, publication, batch, or attempt identities cannot reset structural pressure",
        ]
        for token in semantics_required:
            with self.subTest(surface="live-semantics", token=token):
                self.assertIn(token, LIVE_SEMANTICS)

        contract_required = [
            "owner-boundary-synthesis/v1 for each stable structural component before strategy selection",
            "passing refinement-and-synthesis validation decision",
            "every repair-bearing mutation preflight selects exactly one",
            "per-class construction selects repair without owner synthesis",
            "structural pressure receives another local repair",
            "convergence closes with a duplicate or dominated implementation",
        ]
        for token in contract_required:
            with self.subTest(surface="decision-contract", token=token):
                self.assertIn(token, DECISION_CONTRACT)


if __name__ == "__main__":
    unittest.main()
