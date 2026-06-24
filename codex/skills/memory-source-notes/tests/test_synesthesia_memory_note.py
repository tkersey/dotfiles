#!/usr/bin/env -S uv run python
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/synesthesia_memory_note.py"
SPEC = importlib.util.spec_from_file_location("synesthesia_memory_note", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

NOTE_ID = "MSN-20260620T183000Z-0123456789abcdef"


def endorsement() -> dict:
    return {
        "operation": "assert",
        "authority": "explicit-user-endorsement",
        "summary": "Endorse long corridor.",
        "scope": {"kind": "task-family", "repo": None, "paths": []},
        "source_refs": [
            {
                "kind": "user-endorsement",
                "ref": "rollout:1",
                "summary": "User explicitly endorsed the mapping",
            }
        ],
        "related_ids": [],
        "supersedes_id": None,
        "payload": {
            "sensory_phrase": "long corridor",
            "engineering_translation": "serialized waits",
            "activation_boundary": "dependency-chain diagnosis",
            "non_activation_boundary": "literal-only requests",
            "verification": "Name the concrete wait mechanism and evidence",
        },
    }


class SynesthesiaMemoryNoteTests(unittest.TestCase):
    def test_endorsement_normalizes_writer_compatibility_fields(self) -> None:
        physical, normalized = MODULE.validate_and_normalize(
            "mapping-endorsement", endorsement()
        )
        self.assertEqual("mapping-endorsement", physical)
        self.assertEqual("task_family_scoped", normalized["payload"]["scope"])
        self.assertEqual("task-family", normalized["payload"]["scope_anchor"])
        self.assertEqual(
            "explicit-user-endorsement", normalized["payload"]["endorsement_type"]
        )

    def test_confirmation_maps_to_existing_stored_kind(self) -> None:
        value = endorsement()
        value["operation"] = "confirm"
        value["related_ids"] = [NOTE_ID]
        physical, _ = MODULE.validate_and_normalize("mapping-confirmation", value)
        self.assertEqual("mapping-endorsement", physical)

    def test_confirmation_requires_prior_note(self) -> None:
        value = endorsement()
        value["operation"] = "confirm"
        with self.assertRaisesRegex(MODULE.ValidationError, "prior note|related_ids"):
            MODULE.validate_and_normalize("mapping-confirmation", value)

    def test_wrong_operation_is_rejected(self) -> None:
        value = endorsement()
        value["authority"] = "explicit-user-correction"
        value["related_ids"] = [NOTE_ID]
        value["supersedes_id"] = NOTE_ID
        with self.assertRaisesRegex(MODULE.ValidationError, "operation"):
            MODULE.validate_and_normalize("mapping-correction", value)

    def test_assistant_inference_is_rejected(self) -> None:
        value = endorsement()
        value["authority"] = "assistant-inference"
        with self.assertRaisesRegex(MODULE.ValidationError, "authority"):
            MODULE.validate_and_normalize("mapping-endorsement", value)

    def test_canonical_json_ignores_input_key_order(self) -> None:
        physical_a, normalized_a = MODULE.validate_and_normalize(
            "mapping-endorsement", endorsement()
        )
        reordered = json.loads(json.dumps(endorsement(), sort_keys=True))
        physical_b, normalized_b = MODULE.validate_and_normalize(
            "mapping-endorsement", reordered
        )
        self.assertEqual(physical_a, physical_b)
        self.assertEqual(
            MODULE.canonical_json_bytes(normalized_a),
            MODULE.canonical_json_bytes(normalized_b),
        )
        self.assertEqual(
            MODULE.canonical_fingerprint(physical_a, normalized_a),
            MODULE.canonical_fingerprint(physical_b, normalized_b),
        )

    def test_sync_instructions_copies_regular_file_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source.md"
            source.write_text("adapter\n", encoding="utf-8")
            home = root / "codex-home"
            first = MODULE.sync_instructions(home, source)
            second = MODULE.sync_instructions(home, source)
            destination = home / "memories/extensions/synesthesia/instructions.md"
            self.assertEqual("copied", first["status"])
            self.assertEqual("current", second["status"])
            self.assertTrue(destination.is_file())
            self.assertFalse(destination.is_symlink())
            self.assertEqual("adapter\n", destination.read_text(encoding="utf-8"))

    def test_sync_refuses_symlinked_destination(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source.md"
            source.write_text("adapter\n", encoding="utf-8")
            home = root / "codex-home"
            destination = home / "memories/extensions/synesthesia/instructions.md"
            destination.parent.mkdir(parents=True)
            target = root / "target.md"
            target.write_text("old\n", encoding="utf-8")
            try:
                destination.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            with self.assertRaisesRegex(MODULE.ValidationError, "symlink"):
                MODULE.sync_instructions(home, source)

    def test_doctor_distinguishes_empty_source_notes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            report = MODULE.doctor(Path(td))
            body = report["synesthesia_memory_doctor"]
            self.assertEqual("no-source-notes", body["stage"])
            self.assertEqual(0, body["notes"]["count"])


if __name__ == "__main__":
    unittest.main()
