#!/usr/bin/env -S uv run python
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

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
        "payload": mapping_payload(),
    }


def mapping_payload(translation: str = "serialized waits") -> dict[str, str]:
    return {
        "sensory_phrase": "long corridor",
        "engineering_translation": translation,
        "activation_boundary": "dependency-chain diagnosis",
        "non_activation_boundary": "literal-only requests",
        "verification": "Name the concrete wait mechanism and evidence",
    }


def note_id(index: int) -> str:
    return f"MSN-20260620T1830{index:02d}Z-{index:016x}"


def stored_note(
    index: int,
    *,
    kind: str = "mapping-endorsement",
    operation: str = "assert",
    payload: dict | None = None,
    related_ids: list[str] | None = None,
    supersedes_id: str | None = None,
    authority: str | None = None,
    scope: dict | None = None,
) -> dict:
    if authority is None:
        authority = {
            "mapping-endorsement": "explicit-user-endorsement",
            "mapping-correction": "explicit-user-correction",
            "mapping-rejection": "explicit-user-rejection",
            "activation-boundary": "explicit-user-endorsement",
            "boundary-retraction": "explicit-user-correction",
        }[kind]
    if payload is None:
        if kind in {"mapping-endorsement", "mapping-correction"}:
            payload = mapping_payload()
        elif kind == "mapping-rejection":
            payload = {
                "sensory_phrase": "long corridor",
                "activation_boundary": "dependency-chain diagnosis",
                "non_activation_boundary": "literal-only requests",
                "rejection_reason": "It implied the wrong failure family",
                "verification": "Do not retrieve the rejected phrase",
            }
        elif kind == "activation-boundary":
            payload = {
                "activation_boundary": "explicit compare-by-feel requests",
                "non_activation_boundary": "ordinary performance work",
                "verification": "Future activation names representational need",
            }
        else:
            payload = {
                "retracted_boundary": "use for every performance task",
                "reason": "performance alone is not a representational need",
                "verification": "Require explicit sensory language",
            }
    return {
        "schema": "memory-source-note/v1",
        "id": note_id(index),
        "captured_at": f"2026-06-20T18:30:{index:02d}Z",
        "extension": "synesthesia",
        "kind": kind,
        "operation": operation,
        "authority": authority,
        "summary": f"event {index}",
        "scope": scope or {"kind": "task-family", "repo": None, "paths": []},
        "source_refs": [
            {"kind": "user", "ref": f"rollout:{index}", "summary": f"event {index}"}
        ],
        "related_ids": related_ids or [],
        "supersedes_id": supersedes_id,
        "fingerprint": f"{index:064x}",
        "payload": payload,
    }


def write_note(home: Path, note: dict, filename: str | None = None) -> Path:
    directory = home / "memories/extensions/synesthesia/notes"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (filename or f"{note['id']}.md")
    path.write_text(json.dumps(note, sort_keys=True) + "\n", encoding="utf-8")
    return path


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

    def test_endorsement_projects_one_active_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            write_note(home, stored_note(1))
            projection = MODULE.build_digest_projection(home)
            self.assertEqual(1, len(projection["active_mappings"]))
            self.assertEqual("asserted", projection["active_mappings"][0]["state"])

    def test_confirmation_collapses_into_existing_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            first = stored_note(1)
            confirm = stored_note(
                2,
                operation="confirm",
                related_ids=[first["id"]],
            )
            write_note(home, first)
            write_note(home, confirm)
            projection = MODULE.build_digest_projection(home)
            lineage = projection["active_mappings"][0]
            self.assertEqual("confirmed", lineage["state"])
            self.assertEqual(1, lineage["confirmation_count"])
            self.assertEqual(2, len(lineage["events"]))

    def test_confirmation_content_mismatch_is_unresolved(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            first = stored_note(1)
            confirm = stored_note(
                2,
                operation="confirm",
                related_ids=[first["id"]],
                payload=mapping_payload("a different translation"),
            )
            write_note(home, first)
            write_note(home, confirm)
            projection = MODULE.build_digest_projection(home)
            self.assertEqual(1, len(projection["unresolved_events"]))
            self.assertIn("content-mismatch", projection["unresolved_events"][0]["reason"])

    def test_correction_replaces_translation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            first = stored_note(1)
            correction = stored_note(
                2,
                kind="mapping-correction",
                operation="supersede",
                supersedes_id=first["id"],
                payload=mapping_payload("serialized waits and amplified dependency latency"),
            )
            write_note(home, first)
            write_note(home, correction)
            projection = MODULE.build_digest_projection(home)
            lineage = projection["active_mappings"][0]
            self.assertEqual("corrected", lineage["state"])
            self.assertIn("amplified", lineage["current_note"].payload["engineering_translation"])

    def test_rejection_removes_mapping_from_active_output(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            first = stored_note(1)
            rejection = stored_note(
                2,
                kind="mapping-rejection",
                operation="reject",
                related_ids=[first["id"]],
            )
            write_note(home, first)
            write_note(home, rejection)
            projection = MODULE.build_digest_projection(home)
            self.assertEqual([], projection["active_mappings"])
            self.assertEqual("rejected", projection["inactive_entries"][0]["state"])

    def test_boundary_retraction_removes_active_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            boundary = stored_note(1, kind="activation-boundary")
            retraction = stored_note(
                2,
                kind="boundary-retraction",
                operation="retract",
                related_ids=[boundary["id"]],
            )
            write_note(home, boundary)
            write_note(home, retraction)
            projection = MODULE.build_digest_projection(home)
            self.assertEqual([], projection["active_boundaries"])
            self.assertEqual("retracted", projection["inactive_entries"][0]["state"])

    def test_reopen_restores_rejected_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            first = stored_note(1)
            rejection = stored_note(
                2,
                kind="mapping-rejection",
                operation="reject",
                related_ids=[first["id"]],
            )
            reopening = stored_note(
                3,
                operation="reopen",
                related_ids=[rejection["id"]],
            )
            for note in (first, rejection, reopening):
                write_note(home, note)
            projection = MODULE.build_digest_projection(home)
            self.assertEqual("reopened", projection["active_mappings"][0]["state"])
            self.assertEqual([], projection["inactive_entries"])

    def test_narrow_and_broad_scopes_can_coexist(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            global_note = stored_note(
                1, scope={"kind": "global", "repo": None, "paths": []}
            )
            repo_note = stored_note(
                2,
                scope={"kind": "repo", "repo": "tkersey/dotfiles", "paths": []},
                payload=mapping_payload("repo-specific serialized waits"),
            )
            write_note(home, global_note)
            write_note(home, repo_note)
            projection = MODULE.build_digest_projection(home)
            self.assertEqual(2, len(projection["active_mappings"]))
            self.assertEqual("repo", projection["active_mappings"][0]["current_note"].scope["kind"])

    def test_dangling_prior_note_is_unresolved(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            correction = stored_note(
                2,
                kind="mapping-correction",
                operation="supersede",
                supersedes_id=note_id(1),
            )
            write_note(home, correction)
            projection = MODULE.build_digest_projection(home)
            self.assertEqual(1, len(projection["unresolved_events"]))
            self.assertIn("missing-or-forward", projection["unresolved_events"][0]["reason"])

    def test_malformed_note_does_not_enter_active_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            directory = home / "memories/extensions/synesthesia/notes"
            directory.mkdir(parents=True)
            (directory / "bad.md").write_text("not json", encoding="utf-8")
            projection = MODULE.build_digest_projection(home)
            self.assertEqual(1, len(projection["invalid_notes"]))
            self.assertEqual([], projection["active_mappings"])

    def test_render_is_deterministic_for_fixed_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            write_note(home, stored_note(1))
            projection = MODULE.build_digest_projection(home)
            a = MODULE.render_memory_digest(projection, "2026-06-20T19:00:00Z")
            b = MODULE.render_memory_digest(projection, "2026-06-20T19:00:00Z")
            self.assertEqual(a, b)
            self.assertIn("source_note_ids", a)
            self.assertIn("long corridor", a)

    def test_source_fingerprint_is_independent_of_filename_order(self) -> None:
        with tempfile.TemporaryDirectory() as left_td, tempfile.TemporaryDirectory() as right_td:
            left = Path(left_td)
            right = Path(right_td)
            notes = [stored_note(1), stored_note(2, payload=mapping_payload("other wait"))]
            write_note(left, notes[0], "z.md")
            write_note(left, notes[1], "a.md")
            write_note(right, notes[0], "a.md")
            write_note(right, notes[1], "z.md")
            self.assertEqual(
                MODULE.build_digest_projection(left)["source_fingerprint"],
                MODULE.build_digest_projection(right)["source_fingerprint"],
            )

    def test_source_fingerprint_changes_when_note_bytes_change(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            path = write_note(home, stored_note(1))
            before = MODULE.build_digest_projection(home)["source_fingerprint"]
            value = json.loads(path.read_text())
            value["summary"] = "changed summary"
            path.write_text(json.dumps(value, sort_keys=True) + "\n")
            after = MODULE.build_digest_projection(home)["source_fingerprint"]
            self.assertNotEqual(before, after)

    def test_generate_digest_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            write_note(home, stored_note(1))
            first = MODULE.generate_memory_digest(
                home, generated_at="2026-06-20T19:00:00Z"
            )
            second = MODULE.generate_memory_digest(home)
            self.assertEqual("written", first["status"])
            self.assertEqual("current", second["status"])
            self.assertTrue(Path(first["path"]).is_file())

    def test_partial_default_digest_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(MODULE.ValidationError, "partial digest"):
                MODULE.generate_memory_digest(Path(td), include_inactive=False)

    def test_doctor_detects_missing_current_and_stale_digest(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            MODULE.sync_instructions(home, MODULE.source_instructions_path())
            path = write_note(home, stored_note(1))
            missing = MODULE.doctor(home)["synesthesia_memory_doctor"]
            self.assertEqual("source-notes-digest-missing", missing["stage"])
            MODULE.generate_memory_digest(home, generated_at="2026-06-20T19:00:00Z")
            current = MODULE.doctor(home)["synesthesia_memory_doctor"]
            self.assertEqual("source-notes-digest-current-awaiting-promotion", current["stage"])
            value = json.loads(path.read_text())
            value["summary"] = "changed"
            path.write_text(json.dumps(value, sort_keys=True) + "\n")
            stale = MODULE.doctor(home)["synesthesia_memory_doctor"]
            self.assertEqual("source-notes-digest-stale", stale["stage"])

    def test_digest_refuses_symlinked_resource_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            home = root / "home"
            write_note(home, stored_note(1))
            extension = home / "memories/extensions/synesthesia"
            target = root / "resources-target"
            target.mkdir()
            try:
                (extension / "resources").symlink_to(target, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            with self.assertRaisesRegex(MODULE.ValidationError, "symlink"):
                MODULE.generate_memory_digest(home)

    def test_append_digest_failure_does_not_rollback_writer_success(self) -> None:
        true_bin = shutil.which("true")
        if not true_bin:
            self.skipTest("true binary unavailable")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            input_path = root / "input.json"
            input_path.write_text(json.dumps(endorsement()), encoding="utf-8")
            args = argparse.Namespace(
                kind="mapping-endorsement",
                json=str(input_path),
                codex_home=str(root / "home"),
                dry_run=False,
            )
            with mock.patch.object(MODULE, "find_memory_note_binary", return_value=Path(true_bin)), mock.patch.object(
                MODULE, "generate_memory_digest", side_effect=OSError("digest failed")
            ):
                self.assertEqual(0, MODULE.cmd_append(args))

    def test_dry_run_append_does_not_refresh_digest(self) -> None:
        true_bin = shutil.which("true")
        if not true_bin:
            self.skipTest("true binary unavailable")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            input_path = root / "input.json"
            input_path.write_text(json.dumps(endorsement()), encoding="utf-8")
            args = argparse.Namespace(
                kind="mapping-endorsement",
                json=str(input_path),
                codex_home=str(root / "home"),
                dry_run=True,
            )
            with mock.patch.object(MODULE, "find_memory_note_binary", return_value=Path(true_bin)), mock.patch.object(
                MODULE, "generate_memory_digest"
            ) as generate:
                self.assertEqual(0, MODULE.cmd_append(args))
                generate.assert_not_called()

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

    def test_doctor_distinguishes_empty_source_notes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            report = MODULE.doctor(Path(td))
            body = report["synesthesia_memory_doctor"]
            self.assertEqual("no-source-notes", body["stage"])
            self.assertEqual(0, body["notes"]["count"])


if __name__ == "__main__":
    unittest.main()
