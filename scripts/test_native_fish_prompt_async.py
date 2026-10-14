"""Reader-driven prompt checks using a real, isolated pseudo-terminal."""

from __future__ import annotations

import fcntl
import os
from pathlib import Path
import pty
import select
import signal
import struct
import subprocess
import termios
import time
import unittest

import test_native_fish_prompt as fixtures
from test_native_fish_prompt import FISH, plain, quote


class FishReader:
    def __init__(self, case: unittest.TestCase, cwd: Path, extra: str = "") -> None:
        self.observer = case.base / "observer"
        self.observer.unlink(missing_ok=True)
        self.output = bytearray()
        self.tail = b""
        self.closed = False
        # Observe after the real renderer, without substituting any async logic.
        observer = f"""
functions fish_prompt >/dev/null
functions --copy fish_prompt __probe_prompt
function fish_prompt
    __probe_prompt $argv
    if not contains -- --final-rendering $argv
        set -q __probe_count; or set -g __probe_count 0
        set -g __probe_count (math $__probe_count + 1)
        set -l draft (commandline | string collect)
        set -l job_pids (string join ',' (jobs --pid))
        set -l contexts (string join '' -- $__native_prompt_context_segments)
        printf '%s\\0' "$__probe_count" "$__native_prompt_pending" \\
            "$__native_prompt_unavailable" "$__native_prompt_last_status" \\
            (string join '|' $__native_prompt_last_pipestatus) \\
            "$__native_prompt_git" "$draft" \\
            (commandline --cursor) "$__native_prompt_directory" \\
            "$__native_prompt_worker_pid" "$PWD" \\
            "$job_pids" "$native_prompt_show_details" "$contexts" \\
            "$__native_prompt_last_duration" "$__native_prompt_request_directory" \\
            > {quote(self.observer)}
    end
end
"""
        init = (
            case.init
            + "set -g native_prompt_async 1; set -g fish_greeting; set -g fish_history ''; "
            + "function fzf_key_bindings; end; fish_vi_key_bindings; fish_user_key_bindings; "
            + extra + "\n" + observer
        )
        self.pid, self.master = pty.fork()
        if self.pid == 0:
            os.chdir(cwd)
            os.execve(FISH, [FISH, "--no-config", "--interactive", "-C", init], case.env)
        fcntl.ioctl(self.master, termios.TIOCSWINSZ, struct.pack("HHHH", 30, 240, 0, 0))

    def send(self, data: bytes) -> None:
        os.write(self.master, data)

    def pump(self, seconds: float = 0.05) -> None:
        if self.closed or not select.select([self.master], [], [], seconds)[0]:
            return
        try:
            chunk = os.read(self.master, 65536)
        except OSError:
            return
        self.output.extend(chunk)
        # Answer Fish's DA1 startup query; preserve partial escape sequences.
        combined = self.tail + chunk
        for _ in range(combined.count(b"\x1b[0c")):
            self.send(b"\x1b[?1;2c")
        self.tail = combined[-3:]

    def state(self) -> list[str]:
        try:
            fields = self.observer.read_bytes().decode().split("\0")
        except (OSError, UnicodeDecodeError):
            return []
        return fields[:-1] if len(fields) == 17 else []

    def until(self, predicate, timeout: float = 6) -> list[str]:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.pump()
            state = self.state()
            if state and predicate(state):
                return state
        raise AssertionError(f"Reader state: {self.state()!r}\nOutput: {self.output[-6000:]!r}")

    def close(self) -> None:
        if self.closed:
            return
        try:
            self.send(b"\x03exit\r")
            deadline = time.monotonic() + 0.5
            while time.monotonic() < deadline:
                self.pump(0.02)
        except OSError:
            pass
        os.close(self.master)
        self.closed = True
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            if os.waitpid(self.pid, os.WNOHANG)[0]:
                return
            time.sleep(0.02)
        os.kill(self.pid, signal.SIGKILL)
        os.waitpid(self.pid, 0)
        raise AssertionError("Isolated Fish reader did not exit")


class AsyncPromptTests(unittest.TestCase):
    setUp = fixtures.NativePromptTests.setUp
    stub = fixtures.NativePromptTests.stub
    git = fixtures.NativePromptTests.git
    repository = fixtures.NativePromptTests.repository

    def reader(self, cwd: Path | None = None, extra: str = "") -> FishReader:
        reader = FishReader(self, cwd or self.home, extra)
        self.addCleanup(reader.close)
        return reader

    def gated_node(self, ignore_term: bool = False) -> tuple[Path, Path]:
        gate, pid_file = self.base / "release", self.base / "node.pid"
        target = self.bin / "node"
        target.write_text(
            "#!/bin/sh\n"
            + ("trap '' TERM\n" if ignore_term else "")
            + f"echo $$ > '{pid_file}'\n"
            f"while test ! -f '{gate}'; do sleep 0.05; done\n"
            "printf 'v22.5.1\\n'\n"
        )
        target.chmod(0o755)
        (self.home / "package.json").write_text("{}\n")
        return gate, pid_file

    def assert_stopped(self, pid: str) -> None:
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            result = subprocess.run(
                ["ps", "-p", pid, "-o", "stat="], capture_output=True, text=True, timeout=2,
            )
            if not result.stdout.strip() or result.stdout.strip().startswith("Z"):
                return
            time.sleep(0.02)
        self.fail(f"Prompt-owned process {pid} remained active: {result.stdout}")

    def test_first_prompt_and_typing_do_not_wait_for_collector(self) -> None:
        gate, _ = self.gated_node()
        reader = self.reader(extra="set -g native_prompt_context_items node; ")
        initial = reader.until(lambda state: state[1] == "1")
        self.assertFalse(gate.exists())  # Producer cannot have completed yet.
        self.assertEqual(initial[11], "")  # No prompt worker in the jobs indicator.
        reader.send(b"echo sentinel")
        deadline = time.monotonic() + 2
        while b"sentinel" not in reader.output and time.monotonic() < deadline:
            reader.pump()
        self.assertIn(b"sentinel", reader.output)
        gate.touch()
        ready = reader.until(lambda state: state[1] == "0" and state[2] == "0")
        self.assertEqual(ready[6:8], ["echo sentinel", "13"])
        self.assertIn("22.5.1", plain(ready[13]))
        self.assertEqual(ready[11], "")

    def test_repaint_and_details_toggle_preserve_pipeline_status(self) -> None:
        for async_enabled in ("0", "1"):
            with self.subTest(async_enabled=async_enabled):
                reader = self.reader(extra=f"set -g native_prompt_async {async_enabled}; ")
                initial = reader.until(lambda state: state[1] == "0")
                reader.send(b"false | true\r")
                result = reader.until(lambda state: int(state[0]) > int(initial[0]) and state[4] == "1|0" and state[1] == "0")
                reader.send(b"\x1b\x10")  # Alt+Ctrl+P in vi insert mode.
                toggled = reader.until(lambda state: state[12] == "0")
                self.assertEqual(toggled[3:5], ["0", "1|0"])
                self.assertEqual(toggled[14], result[14])
                reader.close()

    def test_directory_change_cancels_old_result_and_runtime_process(self) -> None:
        gate, pid_file = self.gated_node(ignore_term=True)
        (self.home / "package.json").unlink()
        repo = self.repository()
        (repo / "package.json").write_text("{}\n")
        worktree = self.home / "feature worktree's path"
        self.git(repo, "worktree", "add", "-b", "feature", str(worktree))
        # Only the first repository needs the gated runtime.
        reader = self.reader(repo, "set -g native_prompt_context_items node; ")
        pending = reader.until(lambda state: state[1] == "1" and pid_file.exists())
        node_pid = pid_file.read_text().strip()
        old_directory = pending[15]
        reader.send(f"cd {quote(worktree)}\r".encode())
        ready = reader.until(lambda state: state[10] == str(worktree) and state[1] == "0")
        self.assertEqual(ready[2], "0")
        self.assertIn("feature", plain(ready[5]))
        self.assertNotIn("main", plain(ready[5]))
        self.assertFalse(Path(old_directory).exists())
        self.assert_stopped(node_pid)
        gate.touch()
        reader.send(b"echo survived\r")
        reader.until(lambda state: int(state[0]) > int(ready[0]) and state[3] == "0")
        self.assertIn(b"survived", reader.output)

    def test_timeout_is_bounded_and_next_command_recovers(self) -> None:
        gate, pid_file = self.gated_node(ignore_term=True)
        reader = self.reader(extra="set -g native_prompt_context_items node; set -g native_prompt_async_timeout_seconds 1; ")
        reader.until(lambda state: state[1] == "1" and pid_file.exists())
        node_pid = pid_file.read_text().strip()
        failed = reader.until(lambda state: state[1] == "0" and state[2] == "1", timeout=4)
        self.assertEqual(failed[5], "")
        self.assert_stopped(node_pid)
        gate.touch()
        reader.send(b"true\r")
        recovered = reader.until(lambda state: int(state[0]) > int(failed[0]) and state[1:3] == ["0", "0"])
        self.assertIn("22.5.1", plain(recovered[13]))

    def test_exit_removes_private_files_and_pending_worker(self) -> None:
        _, pid_file = self.gated_node(ignore_term=True)
        reader = self.reader(extra="set -g native_prompt_context_items node; ")
        pending = reader.until(lambda state: state[1] == "1" and pid_file.exists())
        node_pid = pid_file.read_text().strip()
        directory, wrapper_pid = pending[8:10]
        self.assertEqual(Path(directory).stat().st_mode & 0o777, 0o700)
        reader.close()
        self.assertFalse(Path(directory).exists())
        self.assert_stopped(wrapper_pid)
        self.assert_stopped(node_pid)


if __name__ == "__main__":
    unittest.main(verbosity=2)
