"""Real context discovery with mocked Ledger semantics; never publish a note."""
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
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
from memory_layout import MemoryLayout


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
        home = self.root / 'codex'
        memory_root = home / 'memories_v2'
        extension_root = memory_root / 'extensions/negative-ledger'
        layout = MemoryLayout(extension='negative-ledger', codex_home=home, memory_version='v2',
            memory_root=memory_root, extension_root=extension_root, notes_dir=extension_root / 'notes',
            instructions_path=extension_root / 'instructions.md', resources_dir=extension_root / 'resources')
        binary = self.root / "skills-zig/zig-out/bin/memory-note"
        binary.parent.mkdir(parents=True)
        binary.write_text("#!/bin/sh\nexit 99\n")
        binary.chmod(0o755)
        with patch.dict(os.environ, {"MEMORY_NOTE_BIN": "", "SKILLS_ZIG_REPO": str(self.root / "skills-zig")}), \
             patch("memory_layout.shutil.which", return_value=None), \
             patch.object(adapter, "_run", side_effect=self.run_mock_native), \
             patch.object(adapter, "_resolve_binary", return_value="ledger"), \
             patch.object(adapter.sys, "stdout", stdout), \
             patch.object(adapter, 'selected_layout', return_value=layout) as select:
            self.assertEqual(adapter.cmd_admit(self.args), 0)
        self.assertEqual(select.call_args.args[0].memory_note_bin, str(binary))
        writer = [call for call in self.calls if call[0][1] == "append"]
        self.assertEqual(len(writer), 1)
        self.assertEqual(writer[0][0][0], str(binary))
        self.assertEqual(writer[0][2], self.raw)
        self.assertEqual(writer[0][0][-4:], layout.writer_args())

    def test_missing_root_stops_before_native_read_or_memory_writer(self):
        (Path(self.selected["store_root"]) / context.MARKER).unlink()
        with patch.object(adapter, "_run", side_effect=self.run_mock_native), self.assertRaises(adapter.AdapterError):
            adapter.cmd_admit(self.args)
        self.assertEqual(len(self.calls), 1)
        self.assertIn(str(adapter.CONTEXT_SCRIPT), self.calls[0][0])
        self.assertFalse((self.repo / ".ledger").exists())

    def test_unregistered_workspace_is_not_initialized_by_admission(self):
        catalog = context.storage_home() / context.CATALOG
        catalog.unlink()
        with self.assertRaises(adapter.AdapterError):
            adapter.resolve_custody(self.repo)
        self.assertFalse(catalog.exists())

    def test_direct_source_selection_survives_deleted_workspace(self):
        shutil.rmtree(self.repo)
        args = adapter.build_parser().parse_args(['inspect', '--store-id', self.selected['store_id'],
                                                   '--repo', str(self.root), '--id', 'NEG-000001'])
        with patch.object(adapter, '_run', side_effect=self.run_mock_native), patch.object(adapter, '_resolve_binary', return_value='ledger'):
            raw, report = adapter.inspect_projection(args)
        self.assertEqual(raw, self.raw)
        self.assertEqual(report['storage_context']['store_id'], self.selected['store_id'])
        self.assertIsNone(report['storage_context']['git_common_dir'])
        context_argv = self.calls[0][0]
        self.assertIn('--store-id', context_argv)
        self.assertNotIn('--repo', context_argv)

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
