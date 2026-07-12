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


if __name__ == "__main__":
    unittest.main()
