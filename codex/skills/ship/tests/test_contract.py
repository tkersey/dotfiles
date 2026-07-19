import json
from pathlib import Path
import subprocess
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

    def test_body_acquisition_preserves_exact_bytes(self) -> None:
        body = (
            "Human-authored café context\n"
            "<!-- ship-proof:start -->\nmanaged\n<!-- ship-proof:end -->\n"
            "Human-authored suffix without a terminal newline"
        )
        payload = json.dumps({"body": body}, ensure_ascii=False).encode("utf-8")

        result = subprocess.run(
            ["jq", "-j", ".body"],
            input=payload,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

        self.assertEqual(body.encode("utf-8"), result.stdout)
        self.assertIn(
            "gh pr view <pr> --json body | jq -j .body > <current-body-file>",
            SKILL,
        )
        self.assertNotIn("gh pr view <pr> --json body --jq .body", SKILL)

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

    def test_artifact_kernel_receipt_is_upstream_evidence(self) -> None:
        for text in (
            "protocol: artifact-kernel-v1 | legacy-actuating-v1",
            "schema: actuating-closure-receipt/v1",
            "receipt_id:",
            "goal_id:",
            "goal_contract_ref:",
            "construction_ref:",
            "subject_digest:",
            "evidence_material_head:",
            "evidence_head_at_projection:",
            "review_contract_digest:",
            "review_head_sha:",
            "review_merge_base_sha:",
            "publication_repository: null",
            "publication_pr_url: null",
            "publication_base_sha: null",
            "publication_head_sha: null",
            "verdict: ready-to-ship",
            "blockers: []",
        ):
            self.assertIn(text, SKILL)
        self.assertIn("does not rederive closure", SKILL)
        self.assertIn("does not append the event", RECORD)

    def test_ship_v1_binding_remains_exact_opaque_and_verbatim(self) -> None:
        for text in (SKILL, RECORD):
            self.assertIn("exact two-field", text)
            self.assertIn("opaque", text)
        self.assertIn("Preserve its exact two fields verbatim", SKILL)
        self.assertIn("copied verbatim", RECORD)
        self.assertIn(
            "actuation_binding.actuation_run_id = closure_receipt.receipt_id",
            SKILL,
        )
        self.assertIn(
            "actuation_binding.state_fingerprint = closure_receipt.subject_digest",
            SKILL,
        )
        self.assertIn("Actuating owns the compatibility projection", SKILL)
        self.assertIn("MUST NOT synthesize, relabel, or revise", SKILL)
        self.assertIn(
            "copies it, and never synthesizes or relabels it",
            " ".join(RECORD.split()),
        )

    def test_publication_observation_returns_to_actuating(self) -> None:
        self.assertIn("sole public-effect owner", SKILL)
        self.assertIn("complete immutable receipt back to `$actuating`", SKILL)
        self.assertIn("current `publication_observed` event", SKILL)
        self.assertIn("Never select or revise architecture", SKILL)
        self.assertIn("count review credit", SKILL)


if __name__ == "__main__":
    unittest.main()
