import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "accts.py"
SPEC = importlib.util.spec_from_file_location("accts_cli", SCRIPT)
accts = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(accts)


class AcctsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.codex_home = self.root / "codex"
        self.accts_home = self.root / "accts"
        self.codex_home.mkdir()
        self.auth_file = self.codex_home / "auth.json"
        self.env = {
            "CODEX_HOME": str(self.codex_home),
            "ACCTS_HOME": str(self.accts_home),
            "ACCTS_CONFIG": str(self.accts_home / "accts.toml"),
        }

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *args, stdin=None):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.dict(os.environ, self.env, clear=False), mock.patch.object(sys, "stdout", stdout), mock.patch.object(sys, "stderr", stderr):
            if stdin is None:
                stdin_cm = mock.patch.object(sys, "stdin", io.StringIO(""))
            else:
                stdin_cm = mock.patch.object(sys, "stdin", io.StringIO(stdin))
            with stdin_cm:
                code = accts.main(list(args))
        return code, stdout.getvalue(), stderr.getvalue()

    def write_config(self, extra=""):
        config = self.accts_home / "accts.toml"
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text(
            f"""
[accounts.one]
label = "One"
vault = "one/auth.json"

[accounts.two]
label = "Two"
vault = "two/auth.json"
{extra}
""",
            encoding="utf-8",
        )

    def backup_named_auth(self, name, body):
        self.auth_file.write_text(json.dumps(body), encoding="utf-8")
        code, _, err = self.run_cli("backup", name)
        self.assertEqual(code, 0, err)

    def test_init_dry_run_writes_nothing(self):
        code, out, err = self.run_cli("init", "--dry-run")
        self.assertEqual(code, 0, err)
        self.assertIn("[accounts.personal]", out)
        self.assertFalse((self.accts_home / "accts.toml").exists())

    def test_rejects_secret_toml_keys(self):
        config = self.accts_home / "accts.toml"
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text("[accounts.bad]\naccess_token = \"secret\"\n", encoding="utf-8")
        code, _, err = self.run_cli("status")
        self.assertEqual(code, 2)
        self.assertIn("looks secret-bearing", err)

    def test_backup_status_and_activate_round_trip(self):
        self.write_config()
        self.backup_named_auth("one", {"account": "one"})
        mode = stat.S_IMODE((self.accts_home / "vault" / "one" / "auth.json").stat().st_mode)
        self.assertEqual(mode, 0o600)
        self.auth_file.write_text(json.dumps({"account": "two"}), encoding="utf-8")
        self.backup_named_auth("two", {"account": "two"})
        code, out, err = self.run_cli("activate", "one")
        self.assertEqual(code, 0, err)
        self.assertIn("activated one", out)
        self.assertEqual(json.loads(self.auth_file.read_text())["account"], "one")
        code, out, err = self.run_cli("status", "--json")
        self.assertEqual(code, 0, err)
        payload = json.loads(out)
        self.assertEqual(payload["active_account"], "one")
        self.assertNotIn("refresh_token", out)

    def test_hook_install_preserves_unrelated_hooks_and_uninstall_removes_accts(self):
        self.write_config()
        hooks_file = self.codex_home / "hooks.json"
        hooks_file.write_text(json.dumps({"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "echo keep"}]}]}}), encoding="utf-8")
        code, _, err = self.run_cli("hook", "install")
        self.assertEqual(code, 0, err)
        installed = json.loads(hooks_file.read_text())
        stop_entries = installed["hooks"]["Stop"]
        self.assertEqual(stop_entries[0]["hooks"][0]["command"], "echo keep")
        self.assertTrue(any("accts.py hook stop" in entry["hooks"][0]["command"] for entry in stop_entries))
        code, _, err = self.run_cli("hook", "uninstall")
        self.assertEqual(code, 0, err)
        uninstalled = json.loads(hooks_file.read_text())
        self.assertEqual(uninstalled["hooks"]["Stop"][0]["hooks"][0]["command"], "echo keep")
        self.assertFalse(any("accts.py" in entry["hooks"][0]["command"] for entry in uninstalled["hooks"]["Stop"]))

    def test_queue_and_stop_hook_switches_once_for_next_turn(self):
        self.write_config()
        self.backup_named_auth("one", {"account": "one"})
        self.backup_named_auth("two", {"account": "two"})
        self.run_cli("activate", "one")
        code, _, err = self.run_cli("queue", "two")
        self.assertEqual(code, 0, err)
        code, out, err = self.run_cli("hook", "stop", stdin=json.dumps({"session_id": "s1"}))
        self.assertEqual(code, 0, err)
        response = json.loads(out)
        self.assertTrue(response["continue"])
        self.assertEqual(json.loads(self.auth_file.read_text())["account"], "two")
        state = json.loads((self.accts_home / "state" / "state.json").read_text())
        self.assertNotIn("pending_account", state)
        self.assertEqual(state["turn_use_ledger"][-1]["account"], "one")

    def test_reset_cycle_queues_each_enabled_account_once(self):
        self.write_config()
        self.backup_named_auth("one", {"account": "one"})
        self.backup_named_auth("two", {"account": "two"})
        code, out, err = self.run_cli("reset-cycle", "start", "--resets-at", "2026-06-22T00:00:00Z")
        self.assertEqual(code, 0, err)
        self.assertIn("queued one", out)
        code, _, err = self.run_cli("hook", "session-start")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(self.auth_file.read_text())["account"], "one")
        code, _, err = self.run_cli("hook", "stop", stdin=json.dumps({"session_id": "s2"}))
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(self.auth_file.read_text())["account"], "two")
        code, _, err = self.run_cli("hook", "stop", stdin=json.dumps({"session_id": "s3"}))
        self.assertEqual(code, 0, err)
        state = json.loads((self.accts_home / "state" / "state.json").read_text())
        self.assertTrue(state["reset_cycle"]["complete"])
        self.assertEqual(state["reset_cycle"]["touched"], ["one", "two"])

    def test_cas_reset_key_extraction_requires_weekly_secondary_field(self):
        self.assertEqual(
            accts.reset_key_from_status({"usage": {"secondary": {"resetsAt": "next-week"}}}),
            "next-week",
        )
        self.assertEqual(
            accts.reset_key_from_status({"rateLimits": {"governor": {"windowDurationMins": 10080, "resetsAt": 1782337865}}}),
            "1782337865",
        )
        with self.assertRaises(accts.AcctsError):
            accts.reset_key_from_status({"usage": {"primary": {"windowDurationMins": 300, "resetsAt": "five-hours"}}})


if __name__ == "__main__":
    unittest.main()
