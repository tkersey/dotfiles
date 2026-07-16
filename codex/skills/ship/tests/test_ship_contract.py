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
            ["jq", "-erj", ".body | strings"],
            input=payload,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

        self.assertEqual(body.encode("utf-8"), result.stdout)
        self.assertIn(
            "if ! gh pr view <pr> --repo <repository> --json body > <current-body-json-file>; then",
            SKILL,
        )
        self.assertIn(
            "if ! jq -erj '.body | strings' < <current-body-json-file> > <current-body-file>; then",
            SKILL,
        )
        self.assertNotIn("gh pr view <pr> --json body | jq", SKILL)
        self.assertNotIn("gh pr view <pr> --json body --jq .body", SKILL)

    def test_body_acquisition_fails_closed_before_edit(self) -> None:
        section = SKILL.split("Existing PR update:", 1)[1]
        section = section.split("Existing draft promotion", 1)[0]
        fetch = section.index(
            "if ! gh pr view <pr> --repo <repository> --json body > <current-body-json-file>; then"
        )
        project = section.index(
            "if ! jq -erj '.body | strings' < <current-body-json-file> > <current-body-file>; then"
        )
        edit = section.index(
            "gh pr edit <pr> --repo <repository> --body-file <merged-body-file>"
        )
        self.assertLess(fetch, project)
        self.assertLess(project, edit)
        self.assertEqual(2, section.count("exit 1"))
        self.assertNotIn("| jq", section)

    def test_body_acquisition_rejects_missing_or_malformed_body(self) -> None:
        for payload in (b"{}", b'{"body": null}', b'{"body": 42}', b"not-json"):
            with self.subTest(payload=payload):
                result = subprocess.run(
                    ["jq", "-erj", ".body | strings"],
                    input=payload,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertNotEqual(0, result.returncode)

    def test_all_github_commands_use_explicit_repository(self) -> None:
        section = SKILL.split("## Command policy", 1)[1]
        section = section.split("## Publication postconditions", 1)[0]
        command_lines = [line for line in section.splitlines() if "gh pr " in line]
        self.assertGreaterEqual(len(command_lines), 7)
        for line in command_lines:
            with self.subTest(line=line):
                self.assertIn("--repo <repository>", line)

    def test_promotion_updates_proof_before_ready_transition(self) -> None:
        section = SKILL.split("Existing draft promotion must update proof first:", 1)[1]
        section = section.split("After every create, update, or promotion", 1)[0]
        edit = section.index(
            "gh pr edit <pr> --repo <repository> --body-file <merged-body-file>"
        )
        ready = section.index("gh pr ready <pr> --repo <repository>")
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
