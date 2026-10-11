from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/source-memory-reconcile.py"
SPEC = importlib.util.spec_from_file_location("source_memory_reconcile", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CompiledCorpusTests(unittest.TestCase):
    def classify(self, text):
        return MODULE.classify_record(record_id="NEG-000008", note={"id": "MSN-target", "fingerprint": "abc"},
            expected_fingerprint="abc", export_error=None, eligibility=None,
            compiled_corpus=[text], unreadable_phase2=[])

    def test_other_store_canonical_id_is_not_note_attribution(self):
        result = self.classify("different/repo: NEG-000008 was useful")
        self.assertFalse(result["compiled_note_reference"])
        self.assertEqual(result["phase2_status"], "not-observed")

    def test_no_literal_note_id_does_not_claim_compiler_lag(self):
        result = self.classify("Keep provenance across the producer and consumer.")
        self.assertEqual(result["phase2_status"], "not-observed")
        self.assertEqual(self.classify("source_note_ids: MSN-target")["phase2_status"], "note-id-observed")

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
        self.assertIsNone(row["compiled_note_reference"])

    def test_unavailable_export_does_not_declare_existing_note_stale(self):
        row = MODULE.classify_record(
            record_id="NEG-000001", note={"id": "MSN-1", "fingerprint": "abc"},
            expected_fingerprint=None, export_error="canonical read failed", eligibility=None,
            compiled_corpus=[], unreadable_phase2=[])
        self.assertEqual(row["status"], "incomplete-projection")
        self.assertEqual(row["export_error"], "canonical read failed")


class RepositoryIdentityTests(unittest.TestCase):
    def test_managed_identity_matches_without_git_remote(self):
        identity = "ledger-repository:" + "a" * 32
        local, foreign, unresolved, unscoped = MODULE.partition_notes(
            [{"id": "MSN-managed", "scope": {"repo": identity}}], identity)
        self.assertEqual([note["id"] for note in local], ["MSN-managed"])
        self.assertEqual((foreign, unresolved, unscoped), ([], [], []))

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


class ManagedSourceTests(unittest.TestCase):
    def test_projection_preserves_native_bytes_and_managed_selector(self):
        raw = b'{ "scope": {"repo":"legacy/repo"}, "payload": {"learning_id":"lrn-fixture"} }\n'
        selector = ["--store-root", "/fixture/store", "--store-id", "a" * 32]
        with patch.object(MODULE, "run_bytes", return_value=raw) as call:
            actual, error = MODULE.native_export("ledger", "learnings", "lrn-fixture",
                                                 cwd=Path("/fixture"), native_args=selector)
        self.assertEqual(actual, raw)
        self.assertIsNone(error)
        argv = call.call_args.args[0]
        self.assertIn("--payload-only", argv)
        self.assertNotIn("--repo", argv)
        self.assertEqual(argv[argv.index("--store-root"):argv.index("--store-root") + 4], selector)

    def test_historical_scope_requires_exact_canonical_export_witness(self):
        raw = b'{"scope":{"repo":"legacy/repo"},"payload":{"learning_id":"lrn-fixture"}}\n'
        fingerprint = MODULE.writer_fingerprint("learnings", "learning-admission", raw)
        note = {"id": "MSN-historical", "scope": {"repo": "legacy/repo"}, "kind": "learning-admission",
                "payload": {"learning_id": "lrn-fixture"}, "fingerprint": fingerprint}
        kwargs = dict(ledger="ledger", cwd=Path("/fixture"), eligibility={}, compiled_corpus=[],
            unreadable_phase2=[], synesthesia_adapter=None,
            repository_identity="ledger-repository:" + "a" * 32, standalone_note_ids=set(),
            fallback_show_count=0, codex_home=Path("/fixture"),
            native_args=["--store-root", "/fixture/store", "--store-id", "a" * 32])
        with patch.object(MODULE, "native_export", return_value=(raw, None)):
            result = MODULE.source_report("learnings", [{"id": "lrn-fixture"}], [note], **kwargs)
            different = MODULE.source_report("learnings", [{"id": "lrn-fixture"}],
                                             [dict(note, fingerprint="different")], **kwargs)
        self.assertEqual(result["counts"]["admitted"], 1)
        self.assertEqual(result["exact_export_note_ids"], ["MSN-historical"])
        self.assertEqual(result["foreign_repo_note_ids"], [])
        self.assertEqual(different["foreign_repo_note_ids"], ["MSN-historical"])

    def test_one_source_failure_preserves_other_source_reports(self):
        with tempfile.TemporaryDirectory() as temporary:
            cwd = Path(temporary)
            root = cwd / "codex" / "memories_v2"
            root.mkdir(parents=True)
            (root / "memory_summary.md").write_text("v1\n## General Tips\nfixture\n")
            context = {"native_args": ["--store-root", str(cwd / "store"), "--store-id", "a" * 32],
                       "repository_id": "ledger-repository:" + "a" * 32}
            args = MODULE.build_parser().parse_args(["--repo", str(cwd), "--store-id", "a" * 32,
                                                     "--codex-home", str(cwd / "codex"), "--memory-version", "v2"])
            calls = []
            def run(argv, *, cwd):
                calls.append(argv)
                if argv[0] == "memory-note":
                    return {"command": "doctor", "issues": 0}
                definition = argv[argv.index("--definition") + 1]
                source = next(source for source in MODULE.SOURCES if str(MODULE.SOURCE_DEFINITIONS[source]) == definition)
                return {"schema": "ledger-doctor-result/v1", "healthy": True,
                        "definition": {"id": MODULE.SOURCE_DEFINITION_IDS[source], "abi": MODULE.LEDGER_ABI},
                        "authority_granted": False, "storage_mutated": False}
            def layout(extension, **kwargs):
                ext = root / "extensions" / extension
                return MODULE.MemoryLayout(extension, cwd / "codex", "v2", root, ext,
                                           ext / "notes", ext / "instructions.md", ext / "resources")
            def notes(binary, source, **kwargs):
                if source == "synesthesia":
                    raise MODULE.ReconcileError("fixture inventory failure")
                return [], 0
            with patch.object(MODULE, "resolve_binary", side_effect=lambda explicit, env, name: name), \
                 patch.object(MODULE, "resolve_custody", return_value=context), \
                 patch.object(MODULE, "run_json", side_effect=run), \
                 patch.object(MODULE, "source_records", return_value=[]), \
                 patch.object(MODULE, "resolve_layout", side_effect=layout), \
                 patch.object(MODULE, "load_notes", side_effect=notes), \
                 patch.object(MODULE, "instruction_status", return_value={"status": "current"}):
                result = MODULE.reconcile(args)
            self.assertEqual(result["verdict"], "incomplete")
            self.assertEqual(result["sources"]["learnings"]["canonical_records"], 0)
            self.assertEqual(result["sources"]["negative-ledger"]["admission_notes"], 0)
            self.assertEqual(result["sources"]["learnings"]["diagnostics"], [])
            self.assertIn("fixture inventory failure", str(result["sources"]["synesthesia"]["diagnostics"]))
            managed = [argv for argv in calls if argv[0] == "ledger" and "synesthesia-protocol.json" not in " ".join(argv)]
            self.assertTrue(managed)
            self.assertTrue(all("--store-root" in argv and "--repo" not in argv for argv in managed))


if __name__ == "__main__":
    unittest.main()
