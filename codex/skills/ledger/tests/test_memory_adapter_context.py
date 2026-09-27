"""Real context discovery with mocked Ledger semantics; never publish a note."""
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SKILLS = Path(__file__).resolve().parents[2]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, SKILLS / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


context = load("adapter_test_context", "ledger/scripts/ledger_context.py")
adapter = load("adapter_test", "memory-source-notes/scripts/negative_ledger_memory_note.py")


class AdapterContextTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name).resolve()
        self.repo = self.root / "workspace"
        self.repo.mkdir()
        subprocess.run(["git", "-C", str(self.repo), "init", "-q"], check=True)
        env = patch.dict(os.environ, {"CODEX_HOME": str(self.root / "codex"), "LEDGER_HOME": ""})
        env.start()
        self.addCleanup(env.stop)
        self.selected = context.resolve(self.repo, initialize=True, confirm_no_writers=True)
        self.args = adapter.build_parser().parse_args(["admit", "--repo", str(self.repo), "--id", "NEG-000001"])
        self.raw = b'{ "payload": {"neg_id":"NEG-000001", "status":"active", "projection_fingerprint":"exact"} }\n'
        self.calls = []
        self.real_run = adapter._run

    def run_mock_native(self, argv, *, cwd, input_bytes=None):
        self.calls.append((argv, cwd, input_bytes))
        if str(adapter.CONTEXT_SCRIPT) in argv:
            return self.real_run(argv, cwd=cwd, input_bytes=input_bytes)
        if argv[1] == "project":
            raw = self.raw
        elif argv[1] == "append":
            raw = b'{"status":"created"}\n'
        else:
            doctor = argv[1] == "doctor"
            raw = json.dumps({
                "schema": "ledger-doctor-result/v1" if doctor else "ledger-validation-result/v1",
                "definition": {"id": adapter.SOURCE_DEFINITION_ID if doctor else adapter.NOTE_DEFINITION_ID,
                               "digest": "sha256:fixture", "abi": adapter.LEDGER_ABI},
                "healthy": True, "valid": True, "authority_granted": False, "storage_mutated": False,
            }).encode()
        return subprocess.CompletedProcess(argv, 0, raw, b"")

    def test_doctor_and_projection_share_managed_root_and_keep_workspace_cwd(self):
        with patch.object(adapter, "_run", side_effect=self.run_mock_native), patch.object(adapter, "_resolve_binary", return_value="ledger"):
            raw, report = adapter.inspect_projection(self.args)
        self.assertEqual(raw, self.raw)
        self.assertEqual(report["storage_context"]["store_id"], self.selected["store_id"])
        for argv, cwd, _ in self.calls:
            self.assertEqual(cwd, self.repo)
            if argv[0] == "ledger" and argv[1] in ("doctor", "project"):
                self.assertNotIn("--repo", argv)
                index = argv.index("--store-root")
                self.assertEqual(argv[index:index + 4], self.selected["native_args"])
            if argv[0] == "ledger" and argv[1] == "validate":
                self.assertNotIn("--store-root", argv)

    def test_admission_preserves_projected_bytes_exactly(self):
        stdout = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
        with patch.object(adapter, "_run", side_effect=self.run_mock_native), patch.object(adapter, "_resolve_binary", return_value="ledger"), patch.object(adapter.sys, "stdout", stdout):
            self.assertEqual(adapter.cmd_admit(self.args), 0)
        writer = [call for call in self.calls if call[0][1] == "append"]
        self.assertEqual(len(writer), 1)
        self.assertEqual(writer[0][2], self.raw)

    def test_missing_root_stops_before_native_read_or_memory_writer(self):
        (Path(self.selected["store_root"]) / context.MARKER).unlink()
        with patch.object(adapter, "_run", side_effect=self.run_mock_native), self.assertRaises(adapter.AdapterError):
            adapter.cmd_admit(self.args)
        self.assertEqual(len(self.calls), 1)
        self.assertIn(str(adapter.CONTEXT_SCRIPT), self.calls[0][0])
        self.assertFalse((self.repo / ".ledger").exists())

    def test_unregistered_workspace_is_not_initialized_by_admission(self):
        (self.repo / ".git" / context.REGISTRATION).unlink()
        with self.assertRaises(adapter.AdapterError):
            adapter.resolve_custody(self.repo)
        self.assertFalse((self.repo / ".git" / context.REGISTRATION).exists())

    def test_mutating_or_fallback_context_is_rejected(self):
        for change in ({"storage_mutated": True}, {"native_args": ["--repo", str(self.repo)]}, {"authority_granted": True}):
            value = self.selected | {"storage_mutated": False} | change
            with patch.object(adapter, "_run", return_value=subprocess.CompletedProcess([], 0, json.dumps(value).encode(), b"")), self.assertRaises(adapter.AdapterError):
                adapter.resolve_custody(self.repo)

    def test_global_instructions_delegate_instead_of_naming_storage(self):
        text = (SKILLS.parent / "AGENTS.md").read_text()
        self.assertNotIn(".ledger", text)
        self.assertNotIn("~/.codex/ledger", text)
        self.assertIn("`$ledger`", text)


if __name__ == "__main__":
    unittest.main()
