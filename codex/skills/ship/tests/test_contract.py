from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
READINESS = (ROOT / "references" / "pr-readiness-policy.md").read_text(encoding="utf-8")
BODY = (ROOT / "references" / "pr-body-proof.md").read_text(encoding="utf-8")
RECORD = (ROOT / "references" / "ship-record.md").read_text(encoding="utf-8")
AGENT = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
FLAT_SKILL = " ".join(SKILL.split())


class ShipContractTests(unittest.TestCase):
    def test_ship_alone_owns_public_effects(self) -> None:
        self.assertIn("sole public-effect owner", SKILL)
        self.assertIn("It never merges", SKILL)
        for phrase in (
            "Never select architecture",
            "classify findings",
            "count review credit",
            "decide closure",
            "choose Actuating's next action",
        ):
            self.assertIn(phrase, FLAT_SKILL)

    def test_actuating_readiness_is_upstream_evidence(self) -> None:
        for phrase in (
            "schema: actuating-closure-receipt/v1",
            "receipt_id:",
            "goal_contract_ref:",
            "construction_ref:",
            "subject_digest:",
            "review_contract_digest:",
            "verdict: ready-to-ship",
            "cited_premise_refs: []",
            "does not rederive closure",
            "Ship never appends Actuating Evidence",
            "recompute its SHA-256 identity",
            "must not validate a truncated projection",
        ):
            self.assertIn(phrase, FLAT_SKILL)
        self.assertIn("actuating-closure-receipt/v1", AGENT)
        self.assertNotIn("closure-decision/v1", AGENT)

    def test_binding_is_exact_opaque_and_verbatim(self) -> None:
        for phrase in (
            "exact publication binding",
            "closure_receipt_ref",
            "goal_contract_ref",
            "construction_ref",
            "subject_digest",
            "evidence_head",
            "review_contract_digest",
            "copies these values verbatim",
        ):
            self.assertIn(phrase, SKILL)
        self.assertIn("copies every field verbatim", RECORD)
        for retired in ("actuation_run_id", "state_fingerprint"):
            self.assertNotIn(retired, SKILL + RECORD)

    def test_decision_separates_operation_from_final_state(self) -> None:
        for phrase in (
            "operation: create | update | update-and-promote | blocked",
            "final_state: ready | draft | preserve",
        ):
            self.assertIn(phrase, SKILL)
            self.assertIn(phrase, RECORD)
        self.assertNotIn("compatibility_mode", SKILL + READINESS + RECORD)
        self.assertNotIn("Compatibility projection", SKILL + READINESS + RECORD)

    def test_body_updates_are_marker_scoped(self) -> None:
        for text in (SKILL, BODY):
            self.assertIn("<!-- ship-proof:start -->", text)
            self.assertIn("<!-- ship-proof:end -->", text)
        self.assertIn("Preserve all human-authored content", SKILL)

    def test_publication_requires_live_readback(self) -> None:
        self.assertIn("A zero exit status is not publication proof", SKILL)
        self.assertIn("action.result", RECORD)
        self.assertIn("live PR readback", RECORD)

    def test_actuation_draft_conflict_blocks(self) -> None:
        self.assertIn("Actuating input cannot", SKILL)
        self.assertIn("conflicting repository policy blocks", SKILL)
        self.assertIn("Actuation input cannot publish a draft", READINESS)


if __name__ == "__main__":
    unittest.main()
