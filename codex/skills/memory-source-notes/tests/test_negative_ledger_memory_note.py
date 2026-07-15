#!/usr/bin/env -S uv run python
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/negative_ledger_memory_note.py"
SPEC = importlib.util.spec_from_file_location("negative_ledger_memory_note", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def envelope(status: str = "active") -> dict:
    return {
        "operation": "assert",
        "authority": "ledger-cli",
        "summary": "NEG-000001 active negative-evidence projection",
        "scope": {"kind": "repo", "repo": "owner/repo", "paths": ["src"]},
        "source_refs": [{"kind": "test", "ref": "test:route", "summary": "witness"}],
        "related_ids": [],
        "supersedes_id": None,
        "payload": {
            "schema": "negative-ledger-projection/v3",
            "repository_id": "owner/repo",
            "ledger_path": ".ledger/negative-ledger/events.jsonl",
            "neg_id": "NEG-000001",
            "record_version": "NER-v2",
            "projection_fingerprint": "a" * 64,
            "event_chain_fingerprint": "b" * 64,
            "status": status,
            "kind": "realization_route",
            "artifact_state_id": "commit:abc",
            "hypothesis": "The route is safe.",
            "attempted_change": "Applied the route.",
            "observed_outcome": "Representative proof regressed.",
            "failure_class": "local-regression",
            "source_refs": [{"kind": "test", "ref": "test:route"}],
            "exclusion_scope": "route",
            "exclusion_rule": "Do not retry this route on the same artifact.",
            "applicability_conditions": ["Same route and artifact."],
            "reopening_criteria": [
                {"id": "artifact-changed", "condition": "Artifact changes."}
            ],
            "confidence": "high",
            "next_search_hint": "Try the owner-boundary route.",
        },
    }


def encoded(value: dict) -> bytes:
    return (json.dumps(value, separators=(",", ":")) + "\n").encode()


class NegativeLedgerMemoryNoteTests(unittest.TestCase):
    def test_validates_complete_active_projection(self) -> None:
        raw = encoded(envelope())
        result = MODULE.validate_projection(raw, "NEG-000001")
        self.assertEqual("active", result["payload"]["status"])
        self.assertEqual(
            MODULE.expected_writer_fingerprint("ledger-projection", raw),
            MODULE.expected_writer_fingerprint("ledger-projection", raw),
        )

    def test_rejects_incomplete_candidate_and_active_projection(self) -> None:
        with self.assertRaisesRegex(MODULE.AdapterError, "incomplete projection"):
            MODULE.validate_projection(encoded(envelope("need-evidence")), "NEG-000001")

        active = envelope()
        active["payload"]["reopening_criteria"] = []
        with self.assertRaisesRegex(MODULE.AdapterError, "reopening_criteria"):
            MODULE.validate_projection(encoded(active), "NEG-000001")

        unknown = envelope("future-state")
        with self.assertRaisesRegex(MODULE.AdapterError, "unknown future-state"):
            MODULE.validate_projection(encoded(unknown), "NEG-000001")

    def test_inspection_uses_uniform_source_namespace_and_grants_no_authority(
        self,
    ) -> None:
        raw = encoded(envelope())
        calls: list[list[str]] = []

        def fake_run(argv, *, cwd, input_bytes=None):
            calls.append(argv)
            stdout = b'{"status":"ok"}\n' if "doctor" in argv else raw
            return subprocess.CompletedProcess(argv, 0, stdout=stdout, stderr=b"")

        args = argparse.Namespace(
            repo=".",
            ledger_bin="/bin/ledger",
            file=None,
            id="NEG-000001",
            kind="ledger-projection",
        )
        with (
            tempfile.TemporaryDirectory() as td,
            mock.patch.object(MODULE, "_resolve_binary", return_value="/bin/ledger"),
            mock.patch.object(MODULE, "_run", side_effect=fake_run),
        ):
            args.repo = td
            _, report = MODULE.inspect_projection(args)

        self.assertEqual(False, report["authority_granted"])
        self.assertEqual(False, report["storage_mutated"])
        self.assertTrue(all("--source" in call for call in calls))
        self.assertTrue(all("negative-ledger" in call for call in calls))

    def test_admit_preserves_exact_native_export_bytes(self) -> None:
        raw = b'{"native":"byte-order-preserved"}\n'
        captured: list[bytes | None] = []

        def fake_run(argv, *, cwd, input_bytes=None):
            captured.append(input_bytes)
            return subprocess.CompletedProcess(
                argv,
                0,
                stdout=b'{"status":"created","id":"MSN-test"}\n',
                stderr=b"",
            )

        args = argparse.Namespace(
            repo=".",
            ledger_bin=None,
            memory_note_bin="/bin/memory-note",
            codex_home=None,
            file=None,
            id="NEG-000001",
            kind="ledger-projection",
            dry_run=False,
        )
        with (
            tempfile.TemporaryDirectory() as td,
            mock.patch.object(MODULE, "inspect_projection", return_value=(raw, {})),
            mock.patch.object(
                MODULE, "_resolve_binary", return_value="/bin/memory-note"
            ),
            mock.patch.object(MODULE, "_run", side_effect=fake_run),
        ):
            args.repo = td
            with contextlib.redirect_stdout(io.TextIOWrapper(io.BytesIO())):
                self.assertEqual(0, MODULE.cmd_admit(args))

        self.assertEqual([raw], captured)


if __name__ == "__main__":
    unittest.main()
