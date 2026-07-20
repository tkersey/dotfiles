from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        cls.skill_flat = " ".join(cls.skill.split())

    def test_proof_follows_actuating_closure(self) -> None:
        for phrase in (
            "after Actuating has applied its closure theorem",
            "actuating-closure-receipt/v1",
            "verdict: complete",
            "Do not emit final proof before current complete closure",
        ):
            self.assertIn(phrase, self.skill_flat)

    def test_binding_covers_all_four_families_and_external_evidence(self) -> None:
        for phrase in (
            "goal_contract_ref:",
            "construction_ref:",
            "counterexample_sets: []",
            "evidence_head:",
            "review_contract_digest:",
            "closure_route: local-implementation | final-closeout",
            "cited_premise_refs: []",
            "local_implementation:",
            "review_required: false",
            "final_closeout:",
            "auxiliaries_current: true",
            "clean_streak: 5",
            "publication_required: false",
            "ship_receipt: null",
            "publication_required: true | false",
            "ship_receipt: {} | null",
        ):
            self.assertIn(phrase, self.skill_flat)

    def test_review_evidence_is_route_conditional(self) -> None:
        for phrase in (
            "Require exactly one review variant and one publication variant",
            "exact-match both to `closure_route`",
            "render review as not required, do not manufacture convergence",
            "Require five-clean review facts only for `final-closeout`",
            "Do not require review convergence for `local-implementation`",
            "reject any supplied review-result or Ship-receipt payload",
            "require current Ship evidence when true",
        ):
            self.assertIn(phrase, self.skill_flat)

    def test_closure_receipt_is_complete_and_identity_checked(self) -> None:
        for phrase in (
            "complete canonical closure-receipt field set",
            "replace only `receipt_id` with JSON `null`",
            "recompute its SHA-256 identity",
            "Missing or extra fields block",
            "Do not accept a truncated, hand-edited",
        ):
            self.assertIn(phrase, self.skill_flat)

    def test_renderer_takes_no_semantic_or_public_authority(self) -> None:
        for phrase in (
            "does not decide completion",
            "select architecture or repairs",
            "classify Counterexamples",
            "choose a next action",
            "Do not publish",
        ):
            self.assertIn(phrase, self.skill_flat)

    def test_output_keeps_falsification_proof_and_ablation_visible(self) -> None:
        for phrase in (
            "## Counterexamples and construction",
            "## Evidence",
            "## Review convergence",
            "## Retirements",
            "## Anti-gaming",
            "## Residual risk",
        ):
            self.assertIn(phrase, self.skill)


if __name__ == "__main__":
    unittest.main()
