"""Exercise managed admissions and corrections through released native CLIs."""

import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILLS = Path(__file__).resolve().parents[2]
SCRIPT = SKILLS / "memory-source-notes/scripts/source_memory_note.py"
sys.path.insert(0, str(SCRIPT.parent))
import source_memory_note as adapter

spec = importlib.util.spec_from_file_location("update_reconcile", SCRIPT.with_name("source-memory-reconcile.py"))
reconcile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reconcile)


@unittest.skipUnless(os.environ.get("LEDGER_BIN") and os.environ.get("MEMORY_NOTE_BIN"),
                     "Set LEDGER_BIN and MEMORY_NOTE_BIN for native memory update checks")
class NativeMemoryUpdateTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.home = self.root / "codex"
        self.catalog = self.root / "catalog"
        self.env = dict(os.environ, LEDGER_CACHE_DIR=str(self.root / "cache"))
        self.ledger = self.env["LEDGER_BIN"]
        self.writer = self.env["MEMORY_NOTE_BIN"]
        self.context = self.execute([self.ledger, "context", "--catalog-root", str(self.catalog), "--initialize"])
        self.selector = self.context["native_args"]
        self.pin = ["--codex-home", str(self.home), "--memory-version", "v2"]

    def execute(self, argv, *, packet=None, raw=None, code=0):
        result = subprocess.run(argv, input=json.dumps(packet).encode() if packet is not None else raw,
                                cwd=self.root, env=self.env, capture_output=True)
        self.assertEqual(result.returncode, code, (result.stdout + result.stderr).decode(errors="replace"))
        return json.loads(result.stdout or result.stderr)

    def source(self, source, command, *args, packet=None, code=0):
        definition = reconcile.SOURCE_DEFINITIONS[source]
        return self.execute([self.ledger, command, "--definition", str(definition),
                             *self.selector, *args, "--format", "json"], packet=packet, code=code)

    def learning(self, **changes):
        record = {"status": "codify_now", "learning": "Reuse immutable configuration.",
                  "application": "Reuse only while all semantic inputs are unchanged.",
                  "context": {"repo": self.context["repository_id"], "branch": "fixture",
                              "paths": ["src/config.zig"]},
                  "source": "fixture", "evidence": ["fixture:immutable-cache"]}
        record.update(changes)
        self.source("learnings", "transact", "--operation", "capture", "--input", "submission=-",
                    packet={"record": record})
        return self.source("learnings", "project", "--projection", "import-records")["data"][-1]

    def negative(self):
        record = {"record_version": "NER-v2", "kind": "realization_route", "status": "active",
            "repository_id": self.context["repository_id"], "artifact_state_id": "a" * 40,
            "route_id": "repeat-body-admission", "exclusion_scope": "route",
            "hypothesis": "Repeated admission is safe.", "attempted_change": "Admit on every lookup.",
            "observed_outcome": "Three admissions for one component.", "failure_class": "local-regression",
            "confidence": "high", "source_refs": [{"kind": "test", "ref": "fixture:admission-count"}],
            "falsifying_evidence": ["Observed three admissions."], "exclusion_rule": "Admit once.",
            "applicability_conditions": ["Lookup repeats admission."],
            "reopening_criteria": [{"id": "once", "condition": "Lookup carries an admitted value."}],
            "next_search_hint": "Carry the admitted value.", "applicable_paths": ["src/component.zig"]}
        self.source("negative-ledger", "transact", "--operation", "capture", "--param", "capture_key=fixture",
                    "--input", "capture=-", packet={"record": record})
        return self.source("negative-ledger", "project", "--projection", "current-records")["data"][0]["neg_id"]

    def command(self, source, operation, record_id, *, prior=None, command="append", code=0):
        argv = [sys.executable, str(SCRIPT), command, "--source", source, "--operation", operation,
                "--catalog-root", str(self.catalog), "--store-id", self.context["store_id"], "--id", record_id,
                "--repo", str(self.root), *self.pin]
        if prior:
            argv += ["--prior-note-id", prior, "--reason", "The source-approved current construction carries this obligation.",
                     "--evidence-ref", "fixture:constructor-preserves-law"]
        return self.execute(argv, code=code)

    def show(self, source, note_id):
        return self.execute([self.writer, "show", "--extension", source, "--id", note_id, *self.pin])

    def snapshot(self, root):
        return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}

    def report(self, source, notes):
        records = reconcile.source_records(self.ledger, source, cwd=self.root, limit=100, native_args=self.selector)
        return reconcile.source_report(source, records, notes, ledger=self.ledger, cwd=self.root, eligibility={},
            compiled_corpus=[], unreadable_phase2=[], synesthesia_adapter=None,
            repository_identity=self.context["repository_id"], standalone_note_ids=set(), fallback_show_count=0,
            codex_home=self.home, native_args=self.selector)

    def test_learning_withdrawal_is_idempotent_preserves_source_and_reports_separate_effect(self):
        record = self.learning()
        admission = self.command("learnings", "admit", record["id"])
        before = self.snapshot(Path(self.context["store_root"]))
        old_notes = self.snapshot(self.home)
        result = self.command("learnings", "retract", record["id"], prior=admission["id"])
        note = self.show("learnings", result["id"])
        self.assertEqual((note["kind"], note["operation"]), ("learning-withdrawal", "retract"))
        self.assertEqual(note["related_ids"], [admission["id"]])
        self.assertEqual(self.snapshot(Path(self.context["store_root"])), before)
        for path, raw in old_notes.items():
            self.assertEqual((self.home / path).read_bytes(), raw)
        duplicate = self.command("learnings", "retract", record["id"], prior=admission["id"])
        self.assertEqual(duplicate["status"], "duplicate_skip")
        row = self.report("learnings", [self.show("learnings", admission["id"]), note])["records"][0]
        self.assertEqual(row["status"], "admitted")
        self.assertEqual(row["memory_guidance"]["state"], "withdrawn")
        self.assertEqual(row["memory_guidance"]["compiled_effect"], "unverified")
        self.assertEqual(row["phase2_status"], "not-observed")

    def test_learning_supersession_resolves_note_identity_and_preserves_canonical_predecessor(self):
        old = self.learning()
        admitted = self.command("learnings", "admit", old["id"])
        revised = self.learning(learning="Reuse only immutable request-local configuration.", supersedes_id=old["id"],
            context={"repo": self.context["repository_id"], "branch": "fixture", "paths": ["src/request.zig"]})
        result = self.command("learnings", "supersede", revised["id"], prior=admitted["id"])
        note = self.show("learnings", result["id"])
        self.assertEqual(note["supersedes_id"], admitted["id"])
        self.assertEqual(note["operation"], "supersede")
        self.assertTrue(any(ref["ref"] == old["id"] for ref in note["source_refs"]))
        source = self.source("learnings", "project", "--projection", "record", "--param", "id=" + revised["id"])["data"]
        self.assertEqual(source["supersedes_id"], old["id"])
        row = next(row for row in self.report("learnings", [note, self.show("learnings", admitted["id"])])["records"]
                   if row["record_id"] == revised["id"])
        self.assertEqual(row["memory_guidance"]["state"], "replacement")

    def test_learning_relationships_are_provenance_for_first_admission(self):
        old = self.learning()
        new = self.learning(learning="Corrected cache guidance.", supersedes_id=old["id"], related_ids=[old["id"]])
        result = self.command("learnings", "admit", new["id"])
        note = self.show("learnings", result["id"])
        self.assertEqual(note["related_ids"], [])
        self.assertIsNone(note["supersedes_id"])
        self.assertEqual(len([ref for ref in note["source_refs"] if ref["ref"] == old["id"]]), 2)
        row = next(row for row in self.report("learnings", [note])["records"] if row["record_id"] == new["id"])
        self.assertEqual(row["status"], "admitted")

    def test_negative_withdrawal_does_not_change_active_route_gate_or_restore_after_source_change(self):
        record_id = self.negative()
        raw, error = reconcile.native_export(self.ledger, "negative-ledger", record_id, cwd=self.root, native_args=self.selector)
        self.assertIsNone(error)
        admitted = self.execute([self.writer, "append", "--extension", "negative-ledger", "--kind", "ledger-projection",
                                 "--json", "-", *self.pin], raw=raw)
        before = self.snapshot(Path(self.context["store_root"]))
        result = self.command("negative-ledger", "retract", record_id, prior=admitted["id"])
        note = self.show("negative-ledger", result["id"])
        self.assertEqual(note["operation"], "retract")
        self.assertEqual(note["payload"]["status"], "active")
        self.assertEqual(self.snapshot(Path(self.context["store_root"])), before)
        gate = self.source("negative-ledger", "project", "--projection", "route-gate", "--param",
                          "identity=repeat-body-admission", "--param", "artifact=" + "a" * 40, code=2)
        self.assertEqual(gate["data"][0]["neg_id"], record_id)
        self.source("negative-ledger", "transact", "--operation", "transition", "--input", "transition=-", packet={
            "neg_id": record_id, "from": "active", "to": "accepted_risk", "reason": "Accepted bounded risk.",
            "criterion_ids": [], "criterion_changes": [], "source_refs": [{"kind": "review", "ref": "fixture:risk"}]})
        row = self.report("negative-ledger", [self.show("negative-ledger", admitted["id"]), note])["records"][0]
        self.assertEqual(row["status"], "needs-source-review")
        self.assertEqual(row["memory_guidance"]["state"], "withdrawn")
        self.assertFalse(row["memory_guidance"]["source_snapshot_current"])

    def test_legacy_learning_scope_withdraws_without_rewriting_provenance(self):
        record = self.learning(context={"repo": "legacy/project", "branch": "historical", "paths": []})
        admitted = self.command("learnings", "admit", record["id"])
        result = self.command("learnings", "retract", record["id"], prior=admitted["id"])
        self.assertEqual(self.show("learnings", result["id"])["scope"]["repo"], "legacy/project")

    def test_old_managed_negative_admission_can_be_withdrawn_after_multiple_transitions(self):
        record_id = self.negative()
        raw, _ = reconcile.native_export(self.ledger, "negative-ledger", record_id,
                                         cwd=self.root, native_args=self.selector)
        admitted = self.execute([self.writer, "append", "--extension", "negative-ledger", "--kind",
            "ledger-projection", "--json", "-", *self.pin], raw=raw)
        prior = self.show("negative-ledger", admitted["id"])
        for before, after in (("active", "accepted_risk"), ("accepted_risk", "stale")):
            self.source("negative-ledger", "transact", "--operation", "transition", "--input", "transition=-", packet={
                "neg_id": record_id, "from": before, "to": after, "reason": "Source-owned lifecycle decision.",
                "criterion_ids": [], "criterion_changes": [], "source_refs": [{"kind": "review", "ref": "fixture:lifecycle"}]})
        before = self.snapshot(Path(self.context["store_root"]))
        result = self.command("negative-ledger", "retract", record_id, prior=admitted["id"])
        note = self.show("negative-ledger", result["id"])
        self.assertEqual(self.snapshot(Path(self.context["store_root"])), before)
        row = self.report("negative-ledger", [prior, note])["records"][0]
        self.assertEqual(row["memory_guidance"]["state"], "withdrawn")
        self.assertTrue(row["memory_guidance"]["source_snapshot_current"])
        current, _ = reconcile.native_export(self.ledger, "negative-ledger", record_id,
                                             cwd=self.root, native_args=self.selector)
        kwargs = dict(prior_note_id=admitted["id"], reason="Supported retirement.",
                      evidence_refs=["fixture:scope"], repository_identity=self.context["repository_id"])
        for mutation in (lambda p: p["payload"].update(attempted_change="A different captured attempt."),
                         lambda p: p["payload"].update(capture_event_count=2, source_event_count=2),
                         lambda p: p["payload"].update(status_event_count=9, source_event_count=10)):
            changed = copy.deepcopy(prior)
            mutation(changed)
            with self.assertRaises(adapter.AdapterError):
                adapter.build_update("negative-ledger", "retract", current, changed, **kwargs)
        with self.assertRaises(adapter.AdapterError):
            adapter.build_update("negative-ledger", "retract", current, prior,
                                 **dict(kwargs, repository_identity="ledger-repository:" + "f" * 32))

    def test_legacy_negative_label_cannot_replace_an_exact_historical_binding(self):
        record_id = self.negative()
        raw, _ = reconcile.native_export(self.ledger, "negative-ledger", record_id,
                                         cwd=self.root, native_args=self.selector)
        admitted = self.execute([self.writer, "append", "--extension", "negative-ledger", "--kind",
            "ledger-projection", "--json", "-", *self.pin], raw=raw)
        prior = self.show("negative-ledger", admitted["id"])
        current = json.loads(raw)
        for envelope in (prior, current):
            envelope["scope"]["repo"] = "legacy/project"
            envelope["payload"]["repository_id"] = "legacy/project"
            envelope["source_refs"][0]["ref"] = "legacy/project:.ledger/negative-ledger/events.jsonl#" + record_id
        current["payload"].update(status="stale", status_event_count=2, source_event_count=3,
                                  projection_fingerprint="a" * 64, previous_projection_fingerprint="b" * 64)
        with self.assertRaises(adapter.AdapterError):
            adapter.build_update("negative-ledger", "retract", adapter.canonical_bytes(current), prior,
                prior_note_id=admitted["id"], reason="Retire the old reminder.", evidence_refs=["fixture:scope"],
                repository_identity=self.context["repository_id"])

    def test_bad_predecessor_or_kind_cannot_publish(self):
        record = self.learning()
        admitted = self.command("learnings", "admit", record["id"])
        prior = self.show("learnings", admitted["id"])
        raw, _ = reconcile.native_export(self.ledger, "learnings", record["id"], cwd=self.root, native_args=self.selector)
        for mutation in (lambda p: p.update(operation="assert", kind="learning-withdrawal"),
                         lambda p: p.update(source_refs=[]),
                         lambda p: p["payload"].update(learning_id="lrn-other"),
                         lambda p: p["scope"].update(repo="foreign/project"),
                         lambda p: p["payload"].update(canonical_fingerprint="foreign")):
            bad = copy.deepcopy(prior)
            mutation(bad)
            with self.assertRaises(adapter.AdapterError):
                adapter.build_update("learnings", "retract", raw, bad, prior_note_id=admitted["id"],
                                     reason="Supported retirement.", evidence_refs=["fixture:scope"])
        before = self.snapshot(self.home)
        self.command("learnings", "retract", record["id"], prior=record["id"], code=2)
        self.assertEqual(self.snapshot(self.home), before)

    def test_conflicting_updates_remain_unresolved_instead_of_selecting_by_timestamp(self):
        record = self.learning()
        admission = self.command("learnings", "admit", record["id"])
        prior = self.show("learnings", admission["id"])
        raw, _ = reconcile.native_export(self.ledger, "learnings", record["id"], cwd=self.root, native_args=self.selector)
        updates = []
        for operation in ("retract", "supersede"):
            update_raw = adapter.build_update("learnings", operation, raw, prior, prior_note_id=prior["id"],
                reason="Source-owned fixture decision.", evidence_refs=["fixture:decision"])
            result = self.execute([self.writer, "append", "--extension", "learnings", "--kind",
                adapter.KINDS[("learnings", operation)], "--json", "-", *self.pin], raw=update_raw)
            updates.append(self.show("learnings", result["id"]))
        for notes in ([prior, *updates], [*reversed(updates), prior]):
            row = self.report("learnings", notes)["records"][0]
            self.assertEqual(row["status"], "incomplete-projection")
            self.assertEqual(row["memory_guidance"]["state"], "unresolved")
            self.assertEqual(set(row["memory_guidance"]["update_note_ids"]), {note["id"] for note in updates})

    def test_negative_kind_relabeling_cannot_publish_an_assert_as_a_retraction(self):
        record_id = self.negative()
        result = self.execute([sys.executable, str(SCRIPT.with_name("negative_ledger_memory_note.py")),
            "admit", "--catalog-root", str(self.catalog), "--store-id", self.context["store_id"],
            "--repo", str(self.root), "--id", record_id, "--kind", "ledger-retraction", *self.pin], code=2)
        self.assertIn("source_memory_note.py", result["negative_ledger_memory_note"]["error"])
        self.assertFalse(self.home.exists())

    def first_negative_admission(self, record_id, expected_status):
        argv = [sys.executable, str(SCRIPT.with_name("negative_ledger_memory_note.py")),
                "inspect", "--catalog-root", str(self.catalog), "--store-id", self.context["store_id"],
                "--repo", str(self.root), "--id", record_id, "--kind", "ledger-status-transition"]
        inspection = self.execute(argv)
        argv[2] = "admit"
        result = self.execute([*argv, *self.pin])
        note = self.show("negative-ledger", result["id"])
        self.assertEqual(note["fingerprint"], inspection["writer_fingerprint"])
        self.assertEqual(note["operation"], "assert")
        self.assertEqual(note["payload"]["status"], expected_status)
        self.assertEqual(note["related_ids"], [])
        self.assertIsNone(note["supersedes_id"])
        self.assertTrue(any(ref["kind"] == "negative-ledger-canonical-relationship"
                            and ref["ref"].startswith("projection:") for ref in note["source_refs"]))
        row = self.report("negative-ledger", [note])["records"][0]
        self.assertEqual(row["status"], "admitted")
        return note

    def test_first_negative_admission_after_status_transition_preserves_canonical_snapshot(self):
        record_id = self.negative()
        self.source("negative-ledger", "transact", "--operation", "transition", "--input", "transition=-", packet={
            "neg_id": record_id, "from": "active", "to": "accepted_risk", "reason": "Accepted bounded risk.",
            "criterion_ids": [], "criterion_changes": [], "source_refs": [{"kind": "review", "ref": "fixture:risk"}]})
        before = self.snapshot(Path(self.context["store_root"]))
        canonical = self.source("negative-ledger", "project", "--projection", "memory-note", "--param", "id=" + record_id)["data"]
        note = self.first_negative_admission(record_id, "accepted_risk")
        self.assertEqual(note["payload"], canonical["payload"])
        self.assertTrue(canonical["related_ids"][0].startswith("projection:"))
        self.assertEqual(self.snapshot(Path(self.context["store_root"])), before)

    def test_first_snapshot_of_reopened_source_is_an_assertion_not_a_memory_reopening(self):
        record_id = self.negative()
        self.source("negative-ledger", "transact", "--operation", "transition", "--input", "transition=-", packet={
            "neg_id": record_id, "from": "active", "to": "reopened", "reason": "The declared admission criterion changed.",
            "criterion_ids": ["once"], "criterion_changes": [{"criterion_id": "once", "before": "Admission repeats.",
                "after": "Lookup carries the admitted value."}],
            "source_refs": [{"kind": "test", "ref": "fixture:admit-once"}]})
        before = self.snapshot(Path(self.context["store_root"]))
        canonical = self.source("negative-ledger", "project", "--projection", "memory-note", "--param", "id=" + record_id)["data"]
        self.assertEqual(canonical["operation"], "reopen")
        note = self.first_negative_admission(record_id, "reopened")
        self.assertEqual(note["payload"], canonical["payload"])
        self.assertEqual(self.snapshot(Path(self.context["store_root"])), before)

    def test_cross_record_branching_supersessions_are_unresolved_for_every_affected_record(self):
        original = self.learning()
        admitted = self.command("learnings", "admit", original["id"])
        prior = self.show("learnings", admitted["id"])
        updates = []
        for rule in ("Successor B narrows the cache rule.", "Successor C changes the cache rule."):
            successor = self.learning(learning=rule, supersedes_id=original["id"])
            result = self.command("learnings", "supersede", successor["id"], prior=prior["id"])
            updates.append(self.show("learnings", result["id"]))
        for notes in ([prior, *updates], [*reversed(updates), prior]):
            rows = self.report("learnings", notes)["records"]
            self.assertEqual(len(rows), 3)
            for row in rows:
                self.assertEqual(row["status"], "incomplete-projection")
                self.assertEqual(row["memory_guidance"]["state"], "unresolved")
                self.assertEqual(set(row["memory_guidance"]["update_note_ids"]), {note["id"] for note in updates})

    def test_sequential_cross_record_supersession_chain_keeps_one_successor(self):
        original = self.learning()
        admitted = self.command("learnings", "admit", original["id"])
        notes = [self.show("learnings", admitted["id"])]
        source_id, prior_note_id = original["id"], admitted["id"]
        for rule in ("Successor B narrows the cache rule.", "Successor C refines the narrowed rule."):
            successor = self.learning(learning=rule, supersedes_id=source_id)
            result = self.command("learnings", "supersede", successor["id"], prior=prior_note_id)
            notes.append(self.show("learnings", result["id"]))
            source_id, prior_note_id = successor["id"], result["id"]
        rows = self.report("learnings", list(reversed(notes)))["records"]
        self.assertTrue(all(row["status"] == "admitted" for row in rows))
        self.assertEqual([row["memory_guidance"]["state"] for row in rows].count("superseded"), 2)
        tip = next(row for row in rows if row["record_id"] == source_id)
        self.assertEqual(tip["memory_guidance"]["state"], "replacement")


if __name__ == "__main__":
    unittest.main()
