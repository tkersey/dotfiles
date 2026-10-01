"""Transport regression tests; native Ledger/writer boundaries are mocked.

Normalization, fingerprints, JSON note loading, lineage folding, and
reconciliation execute their real implementations. These are not native ABI or
model-behavior conformance tests.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


A = load("synesthesia_admission_test_adapter", "synesthesia_memory_note.py")
R = load("synesthesia_admission_test_reconcile", "source-memory-reconcile.py")
DEFINITION = {"id": "synesthesia/protocol", "abi": "ledger-artifact-abi/v1", "digest": "test-digest"}


def sid(n):
    return f"SYN-20261001T000000Z-{n:016x}"


def raw_record(n, kind="mapping-endorsement", operation="assert", prior=None):
    payload = {
        "sensory_phrase": "resonant chamber",
        "engineering_translation": "inward dependency contracts",
        "activation_boundary": "explicit architectural explanation",
        "non_activation_boundary": "literal syntax",
        "verification": "identify actual imports and boundaries",
    }
    authority = "explicit-user-endorsement"
    if kind == "mapping-correction":
        authority = "explicit-user-correction"
        payload["engineering_translation"] = "ports owned by the domain"
    elif kind == "mapping-rejection":
        authority = "explicit-user-rejection"
        payload.pop("engineering_translation")
        payload["rejection_reason"] = "misleading acoustic implication"
    elif kind == "activation-boundary":
        payload = {key: payload[key] for key in (
            "activation_boundary", "non_activation_boundary", "verification"
        )}
    elif kind == "boundary-retraction":
        authority = "explicit-user-correction"
        payload = {"retracted_boundary": "explicit architectural explanation",
                   "reason": "withdraw this rule", "verification": "do not reuse"}
    return {
        "id": sid(n), "logical_kind": kind,
        "kind": A.LOGICAL_TO_PHYSICAL_KIND[kind], "operation": operation,
        "authority": authority, "summary": f"Event {n}",
        "scope": {"kind": "repo", "repo": "tkersey/dotfiles", "paths": []},
        "source_refs": [{"kind": "user-endorsement", "ref": f"test:{n}", "summary": "Explicit test authority"}],
        "related_ids": [prior] if prior and operation != "supersede" else [],
        "supersedes_id": prior if operation == "supersede" else None,
        "payload": payload,
    }


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "home"
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        self.records = {}
        self.serial = 0
        for name, value in (
            ("find_ledger_binary", Path("/test/ledger")),
            ("_inspect_source_ledger", {"healthy": True, "status": "current", "result": {"definition": DEFINITION}}),
            ("_validate_submission_with_ledger", {"definition": DEFINITION}),
        ):
            mocker = patch.object(A, name, return_value=value)
            mocker.start()
            self.addCleanup(mocker.stop)
        mocker = patch.object(A.AdmissionResolver, "_record", side_effect=lambda ident: copy.deepcopy(self.records[ident]))
        self.record_reader = mocker.start()
        self.addCleanup(mocker.stop)
        self.record_patch = mocker

    def resolver(self):
        return A.AdmissionResolver(self.repo, self.home)

    def event(self, *args, **kwargs):
        record = raw_record(*args, **kwargs)
        self.records[record["id"]] = record
        return record["id"]

    def store(self, prepared):
        self.serial += 1
        normalized = copy.deepcopy(prepared["normalized"])
        fingerprint = prepared["writer_fingerprint"]
        note_id = f"MSN-20261001T000{self.serial:03d}Z-{fingerprint[:16]}"
        value = dict(normalized, id=note_id, kind=prepared["physical_kind"],
                     captured_at=f"2026-10-01T00:{self.serial // 60:02d}:{self.serial % 60:02d}Z",
                     fingerprint=fingerprint, extension="synesthesia")
        directory = A.notes_directory(self.home)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{note_id}.md"
        path.write_bytes(A.canonical_json_bytes(value))
        return note_id, path

    def admit_fixture(self, ident):
        return self.store(self.resolver().prepare(ident))

    def test_first_admission_preserves_canonical_input_and_provenance(self):
        ident = self.event(1)
        before = copy.deepcopy(self.records)
        prepared = self.resolver().prepare(ident)
        self.assertEqual(self.records, before)
        self.assertIsNone(prepared["existing_note_id"])
        self.assertIn(ident, [r["ref"] for r in prepared["normalized"]["source_refs"]])
        self.assertFalse(prepared["storage_mutated"])

    def test_existing_legacy_snapshot_is_reused_without_rewriting(self):
        ident = self.event(1)
        raw = {k: v for k, v in self.records[ident].items() if k not in {"id", "logical_kind", "kind"}}
        normalized = A._normalize_writer_input(raw)
        note_id, path = self.store({"normalized": normalized, "physical_kind": "mapping-endorsement",
                                   "writer_fingerprint": A.canonical_fingerprint("mapping-endorsement", normalized)})
        before = path.read_bytes()
        prepared = self.resolver().prepare(ident)
        self.assertEqual(prepared["existing_note_id"], note_id)
        self.assertEqual(prepared["normalized"], normalized)
        self.assertEqual(path.read_bytes(), before)

    def test_confirmation_resolves_canonical_relationship(self):
        first = self.event(1)
        note_id, _ = self.admit_fixture(first)
        confirm = self.event(2, "mapping-confirmation", "confirm", first)
        prepared = self.resolver().prepare(confirm)
        self.assertEqual(prepared["normalized"]["related_ids"], [note_id])
        self.assertIn(first, [r["ref"] for r in prepared["normalized"]["source_refs"]])
        self.store(prepared)
        projection = A.build_digest_projection(self.home)
        self.assertEqual(projection["active_mappings"][0]["confirmation_count"], 1)
        self.assertEqual(projection["unresolved_events"], [])

    def test_mixed_canonical_and_note_references_preserve_unique_relationships(self):
        first = self.event(1)
        note_id, _ = self.admit_fixture(first)
        confirm = self.event(2, "mapping-confirmation", "confirm", first)
        self.records[confirm]["related_ids"].append(note_id)
        prepared = self.resolver().prepare(confirm)
        self.assertEqual(prepared["normalized"]["related_ids"], [note_id])
        self.assertIn(first, [r["ref"] for r in prepared["normalized"]["source_refs"]])

    def test_correction_rejection_and_reopening_fold_in_one_lineage(self):
        first = self.event(1)
        self.admit_fixture(first)
        correction = self.event(2, "mapping-correction", "supersede", first)
        prepared = self.resolver().prepare(correction)
        self.assertTrue(prepared["normalized"]["supersedes_id"].startswith("MSN-"))
        self.store(prepared)
        rejection = self.event(3, "mapping-rejection", "reject", correction)
        self.admit_fixture(rejection)
        projection = A.build_digest_projection(self.home)
        self.assertEqual(len(projection["inactive_entries"]), 1)
        self.assertEqual(projection["active_mappings"], [])
        reopen = self.event(4, "mapping-endorsement", "reopen", rejection)
        self.admit_fixture(reopen)
        projection = A.build_digest_projection(self.home)
        self.assertEqual(projection["active_mappings"][0]["state"], "reopened")
        self.assertEqual(len(projection["active_mappings"][0]["events"]), 4)
        self.assertEqual(projection["unresolved_events"], [])

    def test_boundary_retraction_and_reopening(self):
        first = self.event(1, "activation-boundary")
        self.admit_fixture(first)
        retract = self.event(2, "boundary-retraction", "retract", first)
        self.admit_fixture(retract)
        reopen = self.event(3, "activation-boundary", "reopen", retract)
        self.admit_fixture(reopen)
        projection = A.build_digest_projection(self.home)
        self.assertEqual(projection["active_boundaries"][0]["state"], "reopened")
        self.assertEqual(projection["unresolved_events"], [])

    def test_missing_prior_admission_blocks_without_backfill(self):
        first = self.event(1)
        correction = self.event(2, "mapping-correction", "supersede", first)
        with self.assertRaisesRegex(A.ValidationError, "not admitted"):
            self.resolver().prepare(correction)
        self.assertFalse(A.notes_directory(self.home).exists())

    def test_duplicate_normalization_is_stable(self):
        ident = self.event(1)
        prepared = self.resolver().prepare(ident)
        note_id, _ = self.store(prepared)
        again = self.resolver().prepare(ident)
        self.assertEqual(again["existing_note_id"], note_id)
        self.assertEqual(again["normalized"], prepared["normalized"])

    def test_ambiguous_fingerprint_fails_closed(self):
        ident = self.event(1)
        prepared = self.resolver().prepare(ident)
        self.store(prepared)
        self.store(prepared)
        with self.assertRaisesRegex(A.ValidationError, "ambiguous"):
            self.resolver().prepare(ident)

    def test_unresolved_prior_note_cannot_be_reused(self):
        ident = self.event(1, "mapping-confirmation", "confirm", "MSN-20261001T000000Z-0000000000000000")
        raw = {k: v for k, v in self.records[ident].items() if k not in {"id", "logical_kind", "kind"}}
        normalized = A._normalize_writer_input(raw)
        self.store({"normalized": normalized, "physical_kind": "mapping-endorsement",
                    "writer_fingerprint": A.canonical_fingerprint("mapping-endorsement", normalized)})
        with self.assertRaisesRegex(A.ValidationError, "unresolved note"):
            self.resolver().prepare(ident)

    def test_cycles_fail_closed(self):
        first = self.event(1, "mapping-confirmation", "confirm", sid(2))
        self.event(2, "mapping-confirmation", "confirm", first)
        with self.assertRaisesRegex(A.ValidationError, "cycle"):
            self.resolver().prepare(first)

    def test_independent_reconciliation_reads_do_not_exhaust_chain_budget(self):
        resolver = self.resolver()
        for n in range(1, 260):
            resolver.prepare(self.event(n))
        self.assertEqual(len(resolver.cache), 259)

    def test_optional_relationship_defaults_match_projection(self):
        ident = self.event(1)
        del self.records[ident]["related_ids"]
        del self.records[ident]["supersedes_id"]
        prepared = self.resolver().prepare(ident)
        self.assertEqual(prepared["normalized"]["related_ids"], [])
        self.assertIsNone(prepared["normalized"]["supersedes_id"])

    def test_reserved_provenance_cannot_be_forged_in_new_source(self):
        ident = self.event(1)
        self.records[ident]["source_refs"][0]["kind"] = "synesthesia-canonical-event"
        with self.assertRaisesRegex(A.ValidationError, "reserved"):
            self.resolver().prepare(ident)

    def test_exact_canonical_id_required(self):
        with self.assertRaisesRegex(A.ValidationError, "exact SYN"):
            self.resolver().prepare(sid(1) + "-extra")

    def test_projection_checks_identity_closure_and_read_only_boundary(self):
        ident = self.event(1)
        self.record_patch.stop()
        resolver = self.resolver()
        event = dict(source="synesthesia", syn_id=ident, record=self.records[ident],
                     **{k: self.records[ident][k] for k in ("kind", "logical_kind", "operation")})
        envelope = dict(schema="ledger-projection-result/v1", projection="record", definition=DEFINITION,
                        authority_granted=False, storage_mutated=False, data=event)
        def run(value):
            with patch.object(A.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, json.dumps(value).encode(), b"")) as call:
                result = resolver._record(ident)
                self.assertIn("project", call.call_args.args[0])
                self.assertNotIn("transact", call.call_args.args[0])
                return result
        self.assertEqual(run(envelope), self.records[ident])
        for field, value in (("storage_mutated", True), ("authority_granted", True),
                             ("definition", dict(DEFINITION, digest="wrong")),
                             ("data", dict(event, syn_id=sid(2)))):
            with self.subTest(field=field), self.assertRaises(A.ValidationError):
                run(dict(envelope, **{field: value}))

    def test_reconciliation_uses_resolved_transport_fingerprint(self):
        first = self.event(1)
        self.admit_fixture(first)
        correction = self.event(2, "mapping-correction", "supersede", first)
        self.admit_fixture(correction)
        notes = [json.loads(p.read_text()) for p in A.notes_directory(self.home).glob("*.md")]
        report = R.source_report("synesthesia", [{"syn_id": x, "logical_kind": self.records[x]["logical_kind"]} for x in (first, correction)], notes,
            ledger="/test/ledger", cwd=self.repo, eligibility={}, compiled_corpus=[], unreadable_phase2=[],
            synesthesia_adapter=A, repository_identity="tkersey/dotfiles", standalone_note_ids=set(),
            fallback_show_count=0, codex_home=self.home)
        self.assertEqual(report["counts"]["admitted"], 2)
        self.assertEqual(report["orphan_note_ids"], [])

    def test_reconciliation_source_id_is_exact_and_unambiguous(self):
        note = {"source_refs": [{"kind": "synesthesia-canonical-event", "ref": sid(1)}]}
        self.assertEqual(R.note_source_id("synesthesia", note), sid(1))
        note["source_refs"][0]["ref"] += "-extra"
        self.assertIsNone(R.note_source_id("synesthesia", note))

    def test_low_level_append_rejects_canonical_relationships(self):
        with self.assertRaisesRegex(A.ValidationError, "MSN"):
            A._require_note_relationships({"related_ids": [sid(1)]})
        A._require_note_relationships({"related_ids": ["MSN-20261001T000000Z-0000000000000001"]})

    def test_writer_failure_and_dry_run_do_not_refresh_digest(self):
        args = argparse.Namespace(codex_home=str(self.home), dry_run=False)
        with patch.object(A, "find_memory_note_binary", return_value=Path("/test/memory-note")), \
             patch.object(A.subprocess, "run", return_value=subprocess.CompletedProcess([], 2, b"", b"")), \
             patch.object(A, "generate_memory_digest") as digest:
            self.assertEqual(A._append_normalized("mapping-endorsement", {"related_ids": []}, args), 2)
            digest.assert_not_called()
        args.dry_run = True
        with patch.object(A, "find_memory_note_binary", return_value=Path("/test/memory-note")), \
             patch.object(A.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, b"", b"")), \
             patch.object(A, "generate_memory_digest") as digest:
            self.assertEqual(A._append_normalized("mapping-endorsement", {"related_ids": []}, args), 0)
            digest.assert_not_called()

    def test_digest_failure_does_not_rollback_successful_writer(self):
        args = argparse.Namespace(codex_home=str(self.home), dry_run=False)
        with patch.object(A, "find_memory_note_binary", return_value=Path("/test/memory-note")), \
             patch.object(A.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, b"", b"")), \
             patch.object(A, "generate_memory_digest", side_effect=RuntimeError("test digest failure")), \
             patch.object(A.sys, "stderr", new_callable=io.StringIO) as stderr:
            self.assertEqual(A._append_normalized("mapping-endorsement", {"related_ids": []}, args), 0)
            self.assertIn("memory-digest warning", stderr.getvalue())

    def test_inspect_admission_never_calls_writer_or_digest(self):
        ident = self.event(1)
        args = argparse.Namespace(command="inspect-admission", repo=str(self.repo), codex_home=str(self.home), id=ident)
        with patch.object(A, "_append_normalized") as writer, patch.object(A, "generate_memory_digest") as digest, \
             patch.object(A.sys, "stdout", new_callable=io.StringIO):
            self.assertEqual(A.cmd_admission(args), 0)
            writer.assert_not_called()
            digest.assert_not_called()


if __name__ == "__main__":
    unittest.main()
