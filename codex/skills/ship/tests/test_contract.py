from pathlib import Path
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
READINESS = (SKILL_DIR / "references" / "pr-readiness-policy.md").read_text(
    encoding="utf-8"
)
BODY = (SKILL_DIR / "references" / "pr-body-proof.md").read_text(encoding="utf-8")
RECORD = (SKILL_DIR / "references" / "ship-record.md").read_text(encoding="utf-8")


class ShipContractTests(unittest.TestCase):
    def test_decision_separates_operation_from_final_state(self) -> None:
        for text in (SKILL, READINESS, RECORD):
            self.assertIn("operation: create | update | update-and-promote | blocked", text)
            self.assertIn("final_state: ready | draft | preserve", text)
        self.assertIn("compatibility_mode", SKILL)
        self.assertIn("update-and-promote` + `ready` -> `promote-draft`", RECORD)

    def test_existing_body_updates_are_marker_scoped(self) -> None:
        for text in (SKILL, BODY):
            self.assertIn("<!-- ship-proof:start -->", text)
            self.assertIn("<!-- ship-proof:end -->", text)
            self.assertIn("Preserve", text)
        self.assertIn("Never overwrite human-authored PR body content", SKILL)
        self.assertIn("unbalanced, duplicated, or ambiguous", BODY)

    def test_promotion_updates_proof_before_ready_transition(self) -> None:
        section = SKILL.split("Existing draft promotion must update proof first:", 1)[1]
        section = section.split("After every create, update, or promotion", 1)[0]
        edit = section.index("gh pr edit <pr> --body-file <merged-body-file>")
        ready = section.index("gh pr ready <pr>")
        self.assertLess(edit, ready)
        self.assertIn("Never promote a draft before updating", SKILL)

    def test_publication_requires_live_readback(self) -> None:
        for field in (
            "number,url,state,isDraft,baseRefName,baseRefOid,headRefName,headRefOid,body",
            "headRefOid",
            "baseRefOid",
            "exactly one managed block",
        ):
            self.assertIn(field, SKILL)
        self.assertIn("failed readback must report `blocked`", RECORD)

    def test_body_contract_surfaces_risks_and_followups(self) -> None:
        for text in (SKILL, BODY):
            self.assertIn("## Risks", text)
            self.assertIn("## Follow-ups", text)
            self.assertIn("not-run", text)

    def test_actuation_draft_conflict_blocks(self) -> None:
        self.assertIn("Actuation input cannot publish a draft", READINESS)
        self.assertIn("incompatible-policy", SKILL)


if __name__ == "__main__":
    unittest.main()
