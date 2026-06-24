#!/usr/bin/env -S uv run --with pyyaml python
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_synesthesia.py"
SPEC = importlib.util.spec_from_file_location("validate_synesthesia", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SynesthesiaValidationTests(unittest.TestCase):
    def test_complete_package(self) -> None:
        results = MODULE.run_all(ROOT)
        self.assertEqual(results, {"package": [], "routing": [], "translation": [], "memory": []})

    def test_canonical_json_ignores_object_key_order(self) -> None:
        corpus = json.loads((ROOT / "evals" / "memory-cases.json").read_text())
        pair = corpus["canonical_pairs"][0]
        self.assertEqual(MODULE.canonical_text(pair["left"]), MODULE.canonical_text(pair["right"]))
        self.assertEqual(MODULE.canonical_sha256(pair["left"]), MODULE.canonical_sha256(pair["right"]))

    def test_assistant_inference_is_not_admission_authority(self) -> None:
        corpus = json.loads((ROOT / "evals" / "memory-cases.json").read_text())
        case = next(row for row in corpus["cases"] if row["id"] == "invalid-assistant-authority")
        errors = MODULE.validate_memory_envelope(case["input"], case["kind"])
        self.assertIn("memory:authority", errors)

    def test_correction_requires_prior_note(self) -> None:
        corpus = json.loads((ROOT / "evals" / "memory-cases.json").read_text())
        case = next(row for row in corpus["cases"] if row["id"] == "invalid-correction-without-prior")
        errors = MODULE.validate_memory_envelope(case["input"], case["kind"])
        self.assertIn("memory:prior-note-required", errors)

    def test_payload_cannot_duplicate_scope(self) -> None:
        corpus = json.loads((ROOT / "evals" / "memory-cases.json").read_text())
        case = next(row for row in corpus["cases"] if row["id"] == "invalid-duplicated-scope")
        errors = MODULE.validate_memory_envelope(case["input"], case["kind"])
        self.assertTrue(any(error.startswith("memory:payload-extra:") for error in errors))

    def test_redundant_modalities_are_rejected(self) -> None:
        corpus = json.loads((ROOT / "evals" / "translation-cases.json").read_text())
        case = next(row for row in corpus["cases"] if row["id"] == "invalid-redundant-modalities")
        errors = MODULE.validate_translation_candidate(case["candidate"])
        self.assertIn("candidate:redundant-modalities", errors)


if __name__ == "__main__":
    unittest.main()
