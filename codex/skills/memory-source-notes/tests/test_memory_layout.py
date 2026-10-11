"""Selected-root regressions, including real native writer/consumer round trips.

Set MEMORY_NOTE_BIN to the development writer to run the native integration lane.
Every write uses an isolated temporary home; no installed memories are touched.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import memory_layout as L

spec = importlib.util.spec_from_file_location("layout_test_reconcile", SCRIPTS / "source-memory-reconcile.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)


def fixture_layout(home: Path, extension="learnings", version="v2"):
    root = home / ("memories_v2" if version == "v2" else "memories")
    ext = root / "extensions" / extension
    return L.MemoryLayout(extension, home, version, root, ext, ext / "notes", ext / "instructions.md", ext / "resources")


class SelectedArtifactTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name).resolve() / "codex"
        self.layout = fixture_layout(self.home)

    def test_v2_reads_selected_summary_and_ignores_v1_decoys(self):
        self.layout.memory_root.mkdir(parents=True)
        (self.layout.memory_root / "memory_summary.md").write_text("v1\nSelected v2 summary.\n")
        old = self.home / "memories"
        old.mkdir()
        (old / "memory_summary.md").write_text("wrong old summary")
        (self.layout.memory_root / "MEMORY.md").write_text("obsolete artifact, not a v2 output")
        corpus, unavailable = R.load_compiled_corpus(self.layout)
        self.assertEqual(corpus, ["v1\nSelected v2 summary.\n"])
        self.assertEqual(unavailable, [])

    def test_missing_selected_summary_is_unknown_even_when_old_root_exists(self):
        old = self.home / "memories"
        old.mkdir(parents=True)
        (old / "memory_summary.md").write_text("old content")
        corpus, unavailable = R.load_compiled_corpus(self.layout)
        self.assertEqual(corpus, [])
        self.assertEqual(unavailable, [str(self.layout.memory_root / "memory_summary.md")])

    def test_layout_resolution_failure_never_falls_back_to_existing_v1(self):
        (self.home / "memories/extensions/learnings/notes").mkdir(parents=True)
        with patch.object(L, "memory_note_binary", return_value="memory-note"), \
             patch.object(L.subprocess, "run", return_value=subprocess.CompletedProcess([], 2, b"", b"config unavailable")):
            with self.assertRaisesRegex(L.LayoutError, "config unavailable"):
                L.resolve_layout("learnings", codex_home=self.home)

    def test_copy_is_idempotent_and_does_not_create_or_modify_notes(self):
        source = self.home.parent / "instructions.md"
        source.write_text("Interpret the admitted fixture only.\n")
        first = L.copy_instructions(self.layout, source)
        second = L.copy_instructions(self.layout, source)
        self.assertEqual((first["status"], second["status"]), ("copied", "current"))
        self.assertEqual(self.layout.instructions_path.read_bytes(), source.read_bytes())
        self.assertFalse(self.layout.notes_dir.exists())
        self.assertFalse((self.home / "memories").exists())

    def test_copy_refuses_symlinked_selected_root(self):
        self.home.mkdir(parents=True)
        outside = self.home.parent / "outside"
        outside.mkdir()
        self.layout.memory_root.symlink_to(outside, target_is_directory=True)
        source = self.home.parent / "instructions.md"
        source.write_text("fixture")
        with self.assertRaisesRegex(L.LayoutError, "symlink"):
            L.copy_instructions(self.layout, source)
        self.assertEqual(list(outside.iterdir()), [])


@unittest.skipUnless(os.environ.get("MEMORY_NOTE_BIN"), "set MEMORY_NOTE_BIN for native integration")
class NativeLayoutTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name).resolve() / "codex"
        self.binary = os.environ["MEMORY_NOTE_BIN"]

    def test_append_list_show_copy_and_compiled_reader_share_v2_root(self):
        layout = L.resolve_layout("learnings", codex_home=self.home, memory_version="v2", memory_note_bin=self.binary)
        payload = {
            "operation": "assert", "authority": "ledger-cli", "summary": "Isolated transport fixture",
            "scope": {"kind": "repo", "repo": "ledger-repository:" + "a" * 32},
            "source_refs": [{"kind": "learning", "ref": "fixture:lrn-layout", "summary": "test fixture"}],
            "payload": {"learning_id": "lrn-layout", "learning_status": "do_more", "repo": "fixture",
                        "source_path": "fixture/events.jsonl", "decision_delta": "Use the selected reader namespace",
                        "evidence_snapshot": ["isolated fixture"], "future_behavior": "Pin the native layout",
                        "verification": "read the same immutable note", "tags": ["fixture"]},
        }
        raw = json.dumps(payload).encode()
        argv = [self.binary, "append", "--extension", "learnings", "--kind", "learning-admission",
                "--json", "-", *layout.writer_args()]
        created = subprocess.run(argv, input=raw, capture_output=True, check=True)
        receipt = json.loads(created.stdout)
        duplicate = json.loads(subprocess.run(argv, input=raw, capture_output=True, check=True).stdout)
        self.assertEqual(duplicate["id"], receipt["id"])
        self.assertEqual(duplicate["status"], "duplicate_skip")
        notes, _ = R.load_notes(self.binary, "learnings", cwd=self.home.parent, layout=layout, limit=100)
        self.assertEqual([note["id"] for note in notes], [receipt["id"]])
        files = list(layout.notes_dir.glob("*.md"))
        self.assertEqual(len(files), 1)
        before = files[0].read_bytes()
        source = self.home.parent / "instructions.md"
        source.write_text("Controlled fixture source.\n")
        L.copy_instructions(layout, source)
        self.assertEqual(files[0].read_bytes(), before)
        (layout.memory_root / "memory_summary.md").write_text("v1\nsource_note_ids: " + receipt["id"] + "\n")
        corpus, unavailable = R.load_compiled_corpus(layout)
        self.assertTrue(R.contains_token(corpus, receipt["id"]))
        self.assertEqual(unavailable, [])
        self.assertFalse((self.home / "memories").exists())

    def test_consumer_doctor_does_not_create_a_missing_home(self):
        layout = L.resolve_layout("negative-ledger", codex_home=self.home, memory_version="v2", memory_note_bin=self.binary)
        subprocess.run([self.binary, "doctor", "--extension", "negative-ledger", *layout.writer_args()],
                       check=True, capture_output=True)
        self.assertFalse(self.home.exists())


@unittest.skipUnless(os.environ.get("MEMORY_NOTE_BIN") and os.environ.get("LEDGER_BIN"),
                     "set MEMORY_NOTE_BIN and LEDGER_BIN for managed integration")
class NativeManagedReconciliationTests(unittest.TestCase):
    def test_personal_capture_admit_reconcile_survives_workspace_and_writer_loss(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            home, workspace, other_workspace = root / "codex", root / "workspace", root / "other-workspace"
            workspace.mkdir()
            other_workspace.mkdir()
            environment = dict(os.environ, CODEX_HOME=str(home), LEDGER_HOME="", LEDGER_CACHE_DIR=str(root / "cache"))
            ledger, writer = environment["LEDGER_BIN"], environment["MEMORY_NOTE_BIN"]

            def run(argv, *, raw=None):
                result = subprocess.run(argv, input=raw, cwd=other_workspace,
                                        env=environment, capture_output=True)
                self.assertEqual(result.returncode, 0,
                                 (result.stdout + result.stderr).decode(errors="replace"))
                return result.stdout

            context_script = R.SKILLS_ROOT / "ledger/scripts/ledger_context.py"
            context = json.loads(run([sys.executable, str(context_script), "--repo", str(workspace),
                                      "--initialize", "--confirm-no-writers"]))
            other = json.loads(run([sys.executable, str(context_script), "--repo", str(other_workspace),
                                    "--initialize", "--confirm-no-writers"]))
            self.assertNotEqual(context["store_id"], other["store_id"])
            selector = context["native_args"]
            learning = {"status": "codify_now", "learning": "Pin the selected memory root for source transport.",
                        "application": "Resolve once and carry the home/version to every consumer.",
                        "context": {"repo": context["repository_id"], "branch": "fixture-workstream", "paths": ["src/config.zig"]},
                        "source": "isolated-integration", "evidence": ["fixture:writer-reader-root"]}
            negative = {
                "record_version": "NER-v2", "kind": "realization_route", "status": "active",
                "repository_id": context["repository_id"], "artifact_state_id": "a" * 40,
                "route_id": "independent-memory-root-inference", "exclusion_scope": "route",
                "hypothesis": "Independent writer and reader root inference agrees.",
                "attempted_change": "Infer each root from the presence of a directory.",
                "observed_outcome": "The fixture wrote a note outside the selected reader root.",
                "failure_class": "local-regression", "confidence": "high",
                "source_refs": [{"kind": "test", "ref": "fixture:root-mismatch", "summary": "Reader did not see the note."}],
                "falsifying_evidence": ["Selected-root list did not contain the admission."],
                "exclusion_rule": "Do not infer writer and consumer roots independently.",
                "applicability_conditions": ["Consumer and writer use distinct root inference."],
                "reopening_criteria": [{"id": "shared-resolver", "condition": "Both carry one selected native layout."}],
                "next_search_hint": "Use the shared native path contract.",
                "applicable_paths": ["src/config.zig"],
            }
            for source, packet, input_name, parameters in (
                ("learnings", {"record": learning}, "submission", []),
                ("negative-ledger", {"record": negative}, "capture", ["--param", "capture_key=root-mismatch"]),
            ):
                run([ledger, "transact", "--definition", str(R.SOURCE_DEFINITIONS[source]),
                     *selector, "--operation", "capture", *parameters, "--input", input_name + "=-", "--format", "json"],
                    raw=json.dumps(packet).encode())
            with patch.dict(os.environ, environment):
                records = {source: R.source_records(ledger, source, cwd=other_workspace, limit=100, native_args=selector)
                           for source in ("learnings", "negative-ledger")}
            learning_id = records["learnings"][0]["id"]
            negative_id = records["negative-ledger"][0]["neg_id"]
            raw = run([ledger, "project", "--definition", str(R.SOURCE_DEFINITIONS["learnings"]),
                       *selector, "--projection", "memory-note", "--param", "id=" + learning_id, "--payload-only"])
            pin = ["--codex-home", str(home), "--memory-version", "v2"]
            admitted = json.loads(run([writer, "append", "--extension", "learnings", "--kind", "learning-admission",
                                       "--json", "-", *pin], raw=raw))
            run([sys.executable, str(SCRIPTS / "negative_ledger_memory_note.py"), "admit",
                 "--repo", str(other_workspace), "--store-id", context["store_id"], "--id", negative_id,
                 "--ledger-bin", ledger, "--memory-note-bin", writer, *pin])
            run([sys.executable, str(SCRIPTS / "memory_source_layout.py"), "sync-instructions",
                 "--extension", "learnings", "--extension", "negative-ledger", *pin])

            # This is a controlled compiler-output fixture, not a live compiler claim.
            summary = home / "memories_v2/memory_summary.md"
            summary.write_text("v1\nSelected learning: " + admitted["id"] +
                               "\nAnother store mentions canonical ID " + negative_id + ".\n")
            shutil.rmtree(workspace)
            custody = Path(context["store_root"]) / ".ledger"
            before = {str(path.relative_to(custody)): path.read_bytes()
                      for path in custody.rglob("*") if path.is_file()}
            argv = [sys.executable, str(SCRIPTS / "source-memory-reconcile.py"),
                    "--repo", str(other_workspace), "--store-id", context["store_id"],
                    "--source", "learnings", "--source", "negative-ledger", *pin]
            report = json.loads(run(argv))
            self.assertEqual(report["verdict"], "ok", report)
            for source in ("learnings", "negative-ledger"):
                self.assertEqual(report["sources"][source]["counts"]["admitted"], 1)
                self.assertEqual(report["sources"][source]["storage_context"]["store_id"], context["store_id"])
            self.assertEqual(report["sources"]["learnings"]["records"][0]["phase2_status"], "note-id-observed")
            self.assertEqual(report["sources"]["negative-ledger"]["records"][0]["phase2_status"], "not-observed")

            failed = json.loads(run([*argv, "--memory-note-bin", str(root / "missing-writer")]))
            self.assertEqual(failed["verdict"], "incomplete")
            for source in ("learnings", "negative-ledger"):
                self.assertEqual(failed["sources"][source]["canonical_records"], 1)
                self.assertEqual(failed["sources"][source]["diagnostics"][0]["stage"], "memory-layout")
            self.assertEqual({str(path.relative_to(custody)): path.read_bytes()
                              for path in custody.rglob("*") if path.is_file()}, before)
            self.assertFalse((home / "memories").exists())


if __name__ == "__main__":
    unittest.main()
