"""Check fixture witnesses and blind-export boundaries, never model judgment."""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import review_cases as cases


class ReviewCasesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.subjects = self.root / "subjects"
        self.key_path = self.root / "evaluator" / "key.json"
        self.key = cases.export(self.subjects, self.key_path, seed=4817)

    def test_all_seven_pairs_have_executable_defect_and_preservation_witnesses(self):
        before = cases.digest(self.subjects)
        results = cases.check(self.subjects, self.key_path)
        self.assertEqual(len(results), 14)
        self.assertEqual(sum(result["passes"] for result in results), 7)
        self.assertEqual(cases.digest(self.subjects), before)
        for pair in cases.PAIRS:
            for files in (pair.base, pair.files("adequate"), pair.files("defective")):
                for path, text in files.items():
                    compile(text, path, "exec")
            entries = [entry for entry in self.key["subjects"].values() if entry["family"] == pair.name]
            self.assertEqual({entry["variant"] for entry in entries}, {"adequate", "defective"})
            self.assertEqual({entry["expected"] for entry in entries}, {"APPROVE", "BLOCKED"})

    def test_export_has_opaque_ids_no_answer_key_and_no_probe(self):
        manifest = json.loads((self.subjects / "manifest.json").read_text())
        self.assertEqual(set(manifest), {"schema", "subjects"})
        self.assertEqual(len(set(manifest["subjects"])), 14)
        for identity in manifest["subjects"]:
            self.assertRegex(identity, r"^[a-f0-9]{24}$")
            root = self.subjects / identity
            self.assertTrue((root / "SUBJECT.md").is_file())
            self.assertTrue((root / "base").is_dir())
            self.assertTrue((root / "candidate").is_dir())
            text = "\n".join(path.read_text() for path in root.rglob("*") if path.is_file())
            entry = self.key["subjects"][identity]
            self.assertNotIn(entry["basis"], text)
            self.assertNotIn(entry["family"], text)
            for forbidden in ("BLOCKED", "APPROVE", '"variant"', "def probe():"):
                self.assertNotIn(forbidden, text)
        other = cases.export(self.root / "other", self.root / "other-key.json", seed=4918)
        self.assertTrue(set(other["subjects"]).isdisjoint(self.key["subjects"]))

    def test_key_and_record_destinations_cannot_be_inside_reviewer_exports(self):
        with self.assertRaises(ValueError):
            cases.export(self.root / "new", self.root / "new" / "key.json")
        self.assertFalse((self.root / "new").exists())
        with self.assertRaises(ValueError):
            cases.export(self.subjects, self.key_path)
        identity = next(iter(self.key["subjects"]))
        report = self.root / "report"
        report.write_bytes(b"raw report")
        with self.assertRaises(ValueError):
            cases.record(self.subjects, identity, "current-full", report, self.subjects / identity / "records")

    def test_changed_source_is_rejected_before_probe_execution(self):
        identity = next(iter(self.key["subjects"]))
        path = next((self.subjects / identity / "candidate").glob("*.py"))
        path.write_text(path.read_text() + "\nraise RuntimeError('changed source executed')\n")
        with self.assertRaisesRegex(ValueError, "source bytes changed"):
            cases.check(self.subjects, self.key_path)

    def test_report_and_context_bytes_are_preserved_without_verdict_extraction(self):
        identity = next(iter(self.key["subjects"]))
        report, context = self.root / "report", self.root / "context"
        raw = b"Question pending\r\nAPPROVE is quoted evidence, not my verdict.\x00\xff"
        prompt = b"Exact prompt\r\nmodel: observed-model; reasoning: observed-setting\n"
        report.write_bytes(raw)
        context.write_bytes(prompt)
        before = cases.digest(self.subjects)
        records = self.root / "records"
        first = cases.record(self.subjects, identity, "current-facts", report, records, context=context)
        second = cases.record(self.subjects, identity, "current-facts", report, records)
        self.assertNotEqual(first["run"], second["run"])
        self.assertEqual((records / first["report"]).read_bytes(), raw)
        self.assertEqual(first["report_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual((records / first["context"]).read_bytes(), prompt)
        self.assertEqual(first["context_sha256"], hashlib.sha256(prompt).hexdigest())
        self.assertEqual(first["execution"], "isolated-semantic")
        self.assertIsNone(second["context"])
        self.assertNotIn("verdict", first)
        self.assertEqual(cases.digest(self.subjects), before)
        for identity, arm in (("../key.json", "current-full"), (identity, "unknown")):
            with self.assertRaises(ValueError):
                cases.record(self.subjects, identity, arm, report, records)

    def test_record_rejects_missing_or_changed_subject(self):
        identity = next(iter(self.key["subjects"]))
        report = self.root / "report"
        report.write_bytes(b"report")
        root = self.subjects / identity
        (root / "SUBJECT.md").write_text("changed authority")
        with self.assertRaisesRegex(ValueError, "missing or changed"):
            cases.record(self.subjects, identity, "current-full", report, self.root / "records")
        shutil.rmtree(root)
        with self.assertRaisesRegex(ValueError, "missing or changed"):
            cases.record(self.subjects, identity, "current-full", report, self.root / "records")
        self.assertFalse((self.root / "records").exists())

    def test_cli_exports_only_count_and_records_raw_report(self):
        script = str(Path(cases.__file__).resolve())
        subjects, key = self.root / "cli-subjects", self.root / "cli-key.json"
        def invoke(*args):
            return subprocess.run([sys.executable, "-B", script, *map(str, args)], capture_output=True, text=True)
        result = invoke("export", "--subjects", subjects, "--key", key, "--seed", 3)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"subjects": 14, "model_evaluation": "unrun"})
        identity = next(iter(json.loads((subjects / "manifest.json").read_text())["subjects"]))
        report = self.root / "cli-report"
        report.write_bytes(b"source-bound observation\r\n")
        result = invoke("record", "--subjects", subjects, "--subject", identity, "--arm", "compact-full",
                        "--report", report, "--records", self.root / "cli-records")
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(result.stdout)
        self.assertEqual((self.root / "cli-records" / receipt["report"]).read_bytes(), report.read_bytes())
        self.assertEqual(invoke("export", "--subjects", subjects, "--key", key).returncode, 2)


if __name__ == "__main__":
    unittest.main()
