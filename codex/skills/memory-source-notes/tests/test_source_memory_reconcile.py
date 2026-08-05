from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/source-memory-reconcile.py"
SPEC = importlib.util.spec_from_file_location("source_memory_reconcile", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CompiledCorpusTests(unittest.TestCase):
    def test_exact_token_rejects_identifier_substrings(self) -> None:
        corpus = ["NEG-100 is not NEG-10x; MSN-1234-extra is not the target."]
        self.assertTrue(MODULE.contains_token(corpus, "NEG-100"))
        self.assertFalse(MODULE.contains_token(corpus, "NEG-10"))
        self.assertFalse(MODULE.contains_token(corpus, "MSN-1234"))

    def test_exact_token_accepts_markdown_delimiters(self) -> None:
        corpus = [
            "Compiled from NEG-000001: and MSN-20260101T000000Z-deadbeef."
        ]
        self.assertTrue(MODULE.contains_token(corpus, "NEG-000001"))
        self.assertTrue(
            MODULE.contains_token(corpus, "MSN-20260101T000000Z-deadbeef")
        )

    def test_unreadable_phase2_file_makes_absence_unknown(self) -> None:
        row = MODULE.classify_record(
            record_id="NEG-000001",
            note={"id": "MSN-1", "fingerprint": "abc"},
            expected_fingerprint="abc",
            export_error=None,
            eligibility=None,
            compiled_corpus=[],
            unreadable_phase2=["MEMORY.md"],
        )
        self.assertEqual(row["status"], "admitted")
        self.assertEqual(row["phase2_status"], "unknown")
        self.assertIsNone(row["compiled_memory_visible"])


class RepositoryIdentityTests(unittest.TestCase):
    def test_normalizes_git_remote_forms_to_owner_repo(self) -> None:
        self.assertEqual(
            MODULE.normalize_repository("git@github.com:tkersey/dotfiles.git"),
            "tkersey/dotfiles",
        )
        self.assertEqual(
            MODULE.normalize_repository("https://github.com/tkersey/dotfiles.git"),
            "tkersey/dotfiles",
        )

    def test_basename_does_not_match_canonical_repository(self) -> None:
        local, foreign, unresolved, unscoped = MODULE.partition_notes(
            [
                {"id": "MSN-local", "scope": {"repo": "tkersey/dotfiles"}},
                {"id": "MSN-basename", "scope": {"repo": "dotfiles"}},
                {
                    "id": "MSN-global",
                    "scope": {"kind": "global", "repo": None},
                },
                {"id": "MSN-unscoped"},
            ],
            "tkersey/dotfiles",
        )
        self.assertEqual([note["id"] for note in local], ["MSN-local", "MSN-global"])
        self.assertEqual([note["id"] for note in foreign], ["MSN-basename"])
        self.assertEqual(unresolved, [])
        self.assertEqual([note["id"] for note in unscoped], ["MSN-unscoped"])

    def test_scoped_note_is_unresolved_without_canonical_origin(self) -> None:
        local, foreign, unresolved, unscoped = MODULE.partition_notes(
            [
                {"id": "MSN-scoped", "scope": {"repo": "tkersey/dotfiles"}},
                {
                    "id": "MSN-global",
                    "scope": {"kind": "global", "repo": None},
                },
                {"id": "MSN-unscoped"},
            ],
            None,
        )
        self.assertEqual([note["id"] for note in local], ["MSN-global"])
        self.assertEqual(foreign, [])
        self.assertEqual([note["id"] for note in unresolved], ["MSN-scoped"])
        self.assertEqual([note["id"] for note in unscoped], ["MSN-unscoped"])


class InventoryTests(unittest.TestCase):
    def test_inventory_metadata_detects_truncation(self) -> None:
        self.assertTrue(MODULE.inventory_is_truncated({"total": 11}, 10, 10))
        self.assertFalse(MODULE.inventory_is_truncated({"total": 10}, 10, 10))

    def test_inventory_without_metadata_is_conservative_at_limit(self) -> None:
        self.assertTrue(MODULE.inventory_is_truncated({}, 10, 10))
        self.assertFalse(MODULE.inventory_is_truncated({}, 9, 10))


if __name__ == "__main__":
    unittest.main()
