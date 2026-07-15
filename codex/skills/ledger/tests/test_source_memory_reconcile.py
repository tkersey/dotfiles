#!/usr/bin/env -S uv run python
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/source-memory-reconcile.py"
SPEC = importlib.util.spec_from_file_location("source_memory_reconcile", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SourceMemoryReconcileTests(unittest.TestCase):
    def test_eligibility_manifest_requires_source_owned_reasoned_decisions(
        self,
    ) -> None:
        value = {
            "schema": "source-memory-eligibility/v1",
            "decisions": {
                "learnings": {
                    "lrn-1": {
                        "disposition": "eligible",
                        "reason": "Source gate accepted this high-impact failure shield.",
                    }
                },
                "negative-ledger": {
                    "NEG-1": {
                        "disposition": "not-eligible",
                        "reason": "Projection is complete but not recurrent.",
                    }
                },
            },
        }
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "eligibility.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            result = MODULE.load_eligibility(str(path))
        self.assertEqual("eligible", result["learnings"]["lrn-1"]["disposition"])
        self.assertEqual(
            "not-eligible",
            result["negative-ledger"]["NEG-1"]["disposition"],
        )
        self.assertEqual({}, result["synesthesia"])

    def test_classification_separates_gaps_ineligibility_breakage_and_phase2_lag(
        self,
    ) -> None:
        note = {"id": "MSN-1", "fingerprint": "current"}
        admitted = MODULE.classify_record(
            record_id="lrn-1",
            note=note,
            expected_fingerprint="current",
            export_error=None,
            eligibility={"disposition": "eligible", "reason": "accepted"},
            compiled_corpus="",
        )
        self.assertEqual("admitted", admitted["status"])
        self.assertTrue(admitted["phase2_lag"])

        stale = MODULE.classify_record(
            record_id="NEG-1",
            note=note,
            expected_fingerprint="new",
            export_error=None,
            eligibility=None,
            compiled_corpus="MSN-1",
        )
        self.assertEqual("stale-note", stale["status"])

        eligible = MODULE.classify_record(
            record_id="NEG-2",
            note=None,
            expected_fingerprint="expected",
            export_error=None,
            eligibility={"disposition": "eligible", "reason": "recurrent"},
            compiled_corpus="",
        )
        self.assertEqual("eligible-unadmitted", eligible["status"])

        ineligible = MODULE.classify_record(
            record_id="lrn-2",
            note=None,
            expected_fingerprint="expected",
            export_error=None,
            eligibility={"disposition": "not-eligible", "reason": "task-local"},
            compiled_corpus="",
        )
        self.assertEqual("not-eligible", ineligible["status"])

        incomplete = MODULE.classify_record(
            record_id="NEG-3",
            note=None,
            expected_fingerprint=None,
            export_error="MissingApplicableScope",
            eligibility=None,
            compiled_corpus="",
        )
        self.assertEqual("incomplete-projection", incomplete["status"])

    def test_reconciler_contains_no_source_or_admission_write_route(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        for prohibited in (
            'ledger, "capture"',
            'ledger, "status"',
            'ledger, "reopen"',
            'memory_note, "append"',
            "write_text(",
            "write_bytes(",
        ):
            with self.subTest(prohibited=prohibited):
                self.assertNotIn(prohibited, source)

    def test_repository_aliases_and_foreign_notes_preserve_repo_local_ids(self) -> None:
        self.assertEqual(
            "tkersey/dotfiles",
            MODULE.normalize_repository("https://github.com/tkersey/dotfiles.git"),
        )
        self.assertEqual(
            "tkersey/dotfiles",
            MODULE.normalize_repository("git@github.com:tkersey/dotfiles.git"),
        )
        local = {
            "id": "MSN-local",
            "scope": {"repo": "tkersey/dotfiles"},
            "payload": {"neg_id": "NEG-000001"},
        }
        foreign = {
            "id": "MSN-foreign",
            "scope": {"repo": "tkersey/homebrew-tap"},
            "payload": {"neg_id": "NEG-000001"},
        }
        self.assertIn(MODULE.note_repository(local), {"tkersey/dotfiles"})
        self.assertNotIn(
            MODULE.note_repository(foreign),
            {"tkersey/dotfiles", "dotfiles", ".dotfiles"},
        )

    def test_eligibility_rejects_unknown_canonical_ids(self) -> None:
        eligibility = {source: {} for source in MODULE.SOURCES}
        eligibility["negative-ledger"]["NEG-typo"] = {
            "disposition": "eligible",
            "reason": "would otherwise disappear",
        }
        records = {source: [] for source in MODULE.SOURCES}
        records["negative-ledger"] = [{"neg_id": "NEG-000001"}]
        with self.assertRaisesRegex(MODULE.ReconcileError, "NEG-typo"):
            MODULE.validate_eligibility_ids(eligibility, records)

    def test_foreign_repo_note_cannot_collide_with_local_negative_id(self) -> None:
        foreign = {
            "id": "MSN-foreign",
            "kind": "ledger-projection",
            "fingerprint": "f" * 64,
            "scope": {"repo": "tkersey/homebrew-tap"},
            "payload": {"neg_id": "NEG-000001"},
        }
        with mock.patch.object(MODULE, "native_export", return_value=(b"{}\n", None)):
            report = MODULE.source_report(
                "negative-ledger",
                [{"neg_id": "NEG-000001"}],
                [foreign],
                ledger="/bin/ledger",
                cwd=Path("/tmp"),
                eligibility={},
                compiled_corpus="",
                synesthesia_adapter=None,
                repo_aliases={"tkersey/dotfiles", "dotfiles", ".dotfiles"},
            )
        self.assertEqual("needs-source-review", report["records"][0]["status"])
        self.assertEqual([], report["orphan_note_ids"])
        self.assertEqual(["MSN-foreign"], report["foreign_repo_note_ids"])


if __name__ == "__main__":
    unittest.main()
