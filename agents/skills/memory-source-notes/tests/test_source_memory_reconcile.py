from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
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
                 patch.object(MODULE, "memory_note_binary", return_value="memory-note"), \
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


class NegativePredecessorTests(unittest.TestCase):
    def setUp(self):
        self.record_id = "NEG-000001"
        self.current = {
            "authority": "ledger-cli",
            "scope": {"kind": "repo", "repo": "legacy/project", "paths": []},
            "source_refs": [{"kind": "negative-ledger", "ref":
                             "legacy/project:.ledger/negative-ledger/events.jsonl#NEG-000001",
                             "summary": "Canonical ledger export"}],
            "payload": {"schema": "negative-ledger-projection/v3", "neg_id": self.record_id,
                        "repository_id": "legacy/project", "ledger_path": ".ledger/negative-ledger/events.jsonl",
                        "status": "accepted_risk", "projection_fingerprint": "b" * 64,
                        "previous_projection_fingerprint": "a" * 64},
        }
        self.raw = json.dumps(self.current).encode() + b"\n"
        self.note = copy.deepcopy(self.current)
        self.note.update(id="MSN-previous", extension="negative-ledger", kind="ledger-projection", fingerprint="c" * 64)
        self.note["payload"].update(status="active", projection_fingerprint="a" * 64,
                                    previous_projection_fingerprint=None)
        self.kwargs = dict(ledger="ledger", cwd=Path("/fixture"), eligibility={}, compiled_corpus=[],
            unreadable_phase2=[], synesthesia_adapter=None, repository_identity="ledger-repository:" + "d" * 32,
            standalone_note_ids=set(), fallback_show_count=0, codex_home=Path("/fixture"),
            native_args=["--store-root", "/fixture/store", "--store-id", "d" * 32])

    def report(self, notes, *, export_error=None):
        with patch.object(MODULE, "native_export", return_value=(None if export_error else self.raw, export_error)):
            return MODULE.source_report("negative-ledger", [{"neg_id": self.record_id}], notes, **self.kwargs)

    def test_source_predecessor_is_stale_and_keeps_historical_scope(self):
        for kind in MODULE.NEGATIVE_NOTE_KINDS:
            with self.subTest(kind=kind):
                note = dict(self.note, kind=kind)
                result = self.report([note])
                row = result["records"][0]
                self.assertEqual(row["status"], "stale-note")
                self.assertEqual(row["scope_binding"], "canonical-predecessor")
                self.assertEqual(row["note_id"], note["id"])
                self.assertEqual(row["expected_fingerprint"], MODULE.writer_fingerprint("negative-ledger", kind, self.raw))
                self.assertEqual(result["admission_notes"], 1)
                self.assertEqual(result["foreign_repo_note_ids"], [])
                self.assertEqual(result["exact_export_note_ids"], [])
                self.assertEqual(result["predecessor_export_note_ids"], [note["id"]])

    def test_current_export_wins_without_forgetting_its_predecessor(self):
        current_note = copy.deepcopy(self.current)
        current_note.update(id="MSN-current", extension="negative-ledger", kind="ledger-status-transition",
                            fingerprint=MODULE.writer_fingerprint("negative-ledger", "ledger-status-transition", self.raw))
        for notes in ([self.note, current_note], [current_note, self.note]):
            result = self.report(notes)
            self.assertEqual(result["records"][0]["status"], "admitted")
            self.assertEqual(result["records"][0]["note_id"], current_note["id"])
            self.assertEqual(result["records"][0]["scope_binding"], "canonical-export")
            self.assertEqual(result["exact_export_note_ids"], [current_note["id"]])
            self.assertEqual(result["predecessor_export_note_ids"], [self.note["id"]])
            self.assertEqual(result["admission_notes"], 2)
            self.assertEqual(result["foreign_repo_note_ids"], [])

    def test_matching_hash_requires_source_record_and_repository_identity(self):
        changes = (
            (("extension",), "learnings"),
            (("kind",), "learning-admission"),
            (("authority",), "unverified-input"),
            (("payload", "schema"), "another-projection/v3"),
            (("payload", "neg_id"), "NEG-000002"),
            (("payload", "repository_id"), "foreign/project"),
            (("scope", "repo"), "foreign/project"),
            (("payload", "ledger_path"), ".ledger/other/events.jsonl"),
            (("source_refs",), [{"kind": "learnings", "ref": "NEG-000001"}]),
            (("source_refs",), [{"kind": "negative-ledger", "ref":
                                "foreign/project:.ledger/negative-ledger/events.jsonl#NEG-000001"}]),
        )
        for path, value in changes:
            with self.subTest(path=path, value=value):
                note = copy.deepcopy(self.note)
                owner = note if len(path) == 1 else note[path[0]]
                owner[path[-1]] = value
                result = self.report([note])
                self.assertEqual(result["records"][0]["status"], "needs-source-review")
                self.assertEqual(result["foreign_repo_note_ids"], [note["id"]])
                self.assertEqual(result["predecessor_export_note_ids"], [])
        self.assertFalse(MODULE.matches_negative_predecessor(self.note, self.current, "NEG-000002"))

    def test_colliding_bare_id_and_scope_do_not_supply_a_predecessor(self):
        note = copy.deepcopy(self.note)
        note["payload"]["projection_fingerprint"] = "e" * 64
        result = self.report([note])
        self.assertEqual(result["records"][0]["status"], "needs-source-review")
        self.assertEqual(result["foreign_repo_note_ids"], [note["id"]])
        self.assertEqual(result["predecessor_export_note_ids"], [])
        note["payload"]["projection_fingerprint"] = None
        current = copy.deepcopy(self.current)
        current["payload"]["previous_projection_fingerprint"] = None
        self.assertFalse(MODULE.matches_negative_predecessor(note, current, self.record_id))

    def test_unavailable_native_export_cannot_establish_predecessor_scope(self):
        result = self.report([self.note], export_error="native source unavailable")
        self.assertEqual(result["records"][0]["status"], "incomplete-projection")
        self.assertEqual(result["records"][0]["export_error"], "native source unavailable")
        self.assertEqual(result["foreign_repo_note_ids"], [self.note["id"]])
        self.assertEqual(result["predecessor_export_note_ids"], [])


@unittest.skipUnless(os.environ.get("LEDGER_BIN") and os.environ.get("MEMORY_NOTE_BIN"),
                     "Set LEDGER_BIN and MEMORY_NOTE_BIN for the native predecessor fixture")
class NativeNegativePredecessorTests(unittest.TestCase):
    def test_legacy_note_transition_and_other_store_id_collision(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            home = root / "codex"
            environment = dict(os.environ, CODEX_HOME=str(home), LEDGER_HOME="", LEDGER_CACHE_DIR=str(root / "cache"))
            ledger, writer = environment["LEDGER_BIN"], environment["MEMORY_NOTE_BIN"]
            definition = MODULE.SOURCE_DEFINITIONS["negative-ledger"]
            previous_definition = MODULE.SKILLS_ROOT / "learnings/tests/fixtures/pre-personal-history/negative-evidence-protocol.json"

            def run(argv, *, packet=None, raw=None):
                result = subprocess.run(argv, input=json.dumps(packet).encode() if packet is not None else raw,
                                        cwd=root, env=environment, capture_output=True)
                self.assertEqual(result.returncode, 0, (result.stdout + result.stderr).decode(errors="replace"))
                return result.stdout

            def new_store():
                return json.loads(run([ledger, "context", "--catalog-root", str(home / "ledger"), "--initialize"]))

            def admit(raw, kind="ledger-projection"):
                pin = ["--codex-home", str(home), "--memory-version", "v2"]
                result = json.loads(run([writer, "append", "--extension", "negative-ledger", "--kind", kind,
                                         "--json", "-", *pin], raw=raw))
                return json.loads(run([writer, "show", "--extension", "negative-ledger", "--id", result["id"],
                                       "--format", "json", *pin]))

            record = {"record_version": "NER-v2", "kind": "realization_route", "status": "active",
                "repository_id": "legacy/project", "artifact_state_id": "a" * 40,
                "route_id": "repeat-body-admission", "exclusion_scope": "route",
                "hypothesis": "Repeated admission is safe.", "attempted_change": "Admit again on each lookup.",
                "observed_outcome": "Three admissions occurred for one component.",
                "failure_class": "local-regression", "confidence": "high",
                "source_refs": [{"kind": "test", "ref": "fixture:admission-count"}],
                "falsifying_evidence": ["The fixture observed three admissions."],
                "exclusion_rule": "Admit once and reuse the result.",
                "applicability_conditions": ["Lookup repeats the admission body."],
                "reopening_criteria": [{"id": "admit-once", "condition": "Lookup reuses one admitted value."}],
                "next_search_hint": "Carry the admitted value.", "applicable_paths": ["src/component.zig"]}
            with patch.dict(os.environ, environment):
                context = new_store()
                selector = context["native_args"]
                run([ledger, "transact", "--definition", str(previous_definition), *selector,
                     "--operation", "capture", "--input", "capture=-", "--format", "json"], packet={"record": record})
                rows = MODULE.source_records(ledger, "negative-ledger", cwd=root, limit=100, native_args=selector)
                neg_id = rows[0]["neg_id"]
                old_raw, error = MODULE.native_export(ledger, "negative-ledger", neg_id, cwd=root, native_args=selector)
                self.assertIsNone(error)
                note = admit(old_raw)
                kwargs = dict(ledger=ledger, cwd=root, eligibility={}, compiled_corpus=[], unreadable_phase2=[],
                    synesthesia_adapter=None, repository_identity=context["repository_id"], standalone_note_ids=set(),
                    fallback_show_count=0, codex_home=home, native_args=selector)
                before = MODULE.source_report("negative-ledger", rows, [note], **kwargs)
                self.assertEqual(before["records"][0]["status"], "admitted")
                transition = {"neg_id": neg_id, "from": "active", "to": "accepted_risk",
                    "reason": "This scope accepts the documented bounded risk.", "criterion_ids": [],
                    "criterion_changes": [], "source_refs": [{"kind": "review", "ref": "fixture:bounded-risk"}]}
                run([ledger, "transact", "--definition", str(definition), *selector, "--operation", "transition",
                     "--input", "transition=-", "--format", "json"], packet=transition)
                rows = MODULE.source_records(ledger, "negative-ledger", cwd=root, limit=100, native_args=selector)
                current_raw, error = MODULE.native_export(ledger, "negative-ledger", neg_id, cwd=root, native_args=selector)
                self.assertIsNone(error)
                current_payload = json.loads(current_raw)["payload"]
                self.assertEqual(current_payload["previous_projection_fingerprint"], note["payload"]["projection_fingerprint"])
                self.assertNotEqual(current_payload["projection_fingerprint"], note["payload"]["projection_fingerprint"])

                # An independent native store deliberately reuses the same bare
                # NEG ID and old repository label, but has a different history.
                other = new_store()
                other_record = dict(record, route_id="another-admission-route")
                run([ledger, "transact", "--definition", str(previous_definition), *other["native_args"],
                     "--operation", "capture", "--input", "capture=-", "--format", "json"], packet={"record": other_record})
                other_raw, error = MODULE.native_export(ledger, "negative-ledger", neg_id, cwd=root, native_args=other["native_args"])
                self.assertIsNone(error)
                foreign_note = admit(other_raw)
                self.assertEqual(foreign_note["payload"]["neg_id"], neg_id)
                self.assertEqual(foreign_note["scope"]["repo"], note["scope"]["repo"])
                self.assertNotEqual(foreign_note["payload"]["projection_fingerprint"], current_payload["previous_projection_fingerprint"])
                custody = Path(context["store_root"]) / ".ledger"
                note_dir = home / "memories_v2/extensions/negative-ledger/notes"
                original_custody = {str(p.relative_to(custody)): p.read_bytes() for p in custody.rglob("*") if p.is_file()}
                original_notes = {p.name: p.read_bytes() for p in note_dir.iterdir() if p.is_file()}
                after = MODULE.source_report("negative-ledger", rows, [foreign_note, note], **kwargs)
                self.assertEqual(after["records"][0]["status"], "stale-note")
                self.assertEqual(after["records"][0]["scope_binding"], "canonical-predecessor")
                self.assertEqual(after["records"][0]["note_id"], note["id"])
                self.assertEqual(after["predecessor_export_note_ids"], [note["id"]])
                self.assertEqual(after["foreign_repo_note_ids"], [foreign_note["id"]])
                self.assertEqual(after["exact_export_note_ids"], [])
                self.assertEqual({str(p.relative_to(custody)): p.read_bytes() for p in custody.rglob("*") if p.is_file()}, original_custody)
                self.assertEqual({p.name: p.read_bytes() for p in note_dir.iterdir() if p.is_file()}, original_notes)
                current_note = admit(current_raw, "ledger-status-transition")
                current = MODULE.source_report("negative-ledger", rows, [note, current_note, foreign_note], **kwargs)
                self.assertEqual(current["records"][0]["status"], "admitted")
                self.assertEqual(current["records"][0]["note_id"], current_note["id"])
                self.assertEqual(current["predecessor_export_note_ids"], [note["id"]])
                self.assertEqual(current["foreign_repo_note_ids"], [foreign_note["id"]])


if __name__ == "__main__":
    unittest.main()
