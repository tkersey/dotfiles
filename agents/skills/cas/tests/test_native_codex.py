"""Test-only native Codex qualification against a loopback model fixture.

Run with uv run --no-project --with aiohttp==3.13.3 THIS_FILE --codex PATH.
No user credentials, production threads, model-quality claim, or CAS wrapper.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import threading
import time
import unittest
import uuid

from aiohttp import web


class Provider:
    def __init__(self) -> None:
        self.requests: list[dict] = []
        self.answer: str = ""
        self.delay = 0.0
        self.fail = False
        self.loop = asyncio.new_event_loop()
        self.ready = threading.Event()
        self.thread = threading.Thread(target=self.serve, daemon=True)
        self.thread.start()
        if not self.ready.wait(10):
            raise TimeoutError("fixture provider startup")

    def serve(self) -> None:
        asyncio.set_event_loop(self.loop)
        async def start() -> None:
            app = web.Application()
            app.router.add_route("*", "/{path:.*}", self.handle)
            self.runner = web.AppRunner(app)
            await self.runner.setup()
            site = web.TCPSite(self.runner, "127.0.0.1", 0)
            await site.start()
            self.port = site._server.sockets[0].getsockname()[1]
            self.ready.set()
        self.loop.run_until_complete(start())
        self.loop.run_forever()
        self.loop.close()

    def events(self, generate: bool) -> list[dict]:
        rid = "resp_" + uuid.uuid4().hex
        item = {"id": "msg_" + uuid.uuid4().hex, "type": "message",
                "role": "assistant", "status": "completed", "content": [
                    {"type": "output_text", "text": self.answer, "annotations": []}]}
        output = [item] if generate else []
        return [
            {"type": "response.created", "response": {"id": rid, "status": "in_progress", "output": []}},
            *([{"type": "response.output_item.done", "output_index": 0, "item": item}] if generate else []),
            {"type": "response.completed", "response": {"id": rid, "status": "completed",
                "output": output, "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2}}},
        ]

    async def handle(self, request: web.Request) -> web.StreamResponse:
        if self.fail:
            return web.json_response({"error": {"message": "controlled provider failure",
                                      "type": "invalid_request_error"}}, status=400)
        if request.headers.get("Upgrade", "").lower() == "websocket":
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            async for message in ws:
                if message.type != web.WSMsgType.TEXT:
                    continue
                payload = json.loads(message.data)
                self.requests.append({"transport": "websocket", "body": payload})
                if payload.get("generate", True):
                    await asyncio.sleep(self.delay)
                for event in self.events(payload.get("generate", True)):
                    try:
                        await ws.send_json(event)
                    except ConnectionResetError:
                        break
            return ws
        if request.method == "POST":
            payload = await request.json()
            self.requests.append({"transport": "http", "body": payload})
            response = web.StreamResponse(headers={"Content-Type": "text/event-stream"})
            await response.prepare(request)
            await asyncio.sleep(self.delay)
            for event in self.events(True):
                await response.write(("data: " + json.dumps(event) + "\n\n").encode())
            await response.write_eof()
            return response
        return web.json_response({"data": []})

    def close(self) -> None:
        asyncio.run_coroutine_threadsafe(self.runner.cleanup(), self.loop).result(10)
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join(10)


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def native_output(records: list[dict], thread_id: str, base: str, cwd: str) -> tuple[str, dict]:
    """Qualification oracle for the documented native artifact, never runtime code."""
    metadata = [r["payload"] for r in records if r.get("type") == "session_meta"]
    assert len(metadata) == 1 and metadata[0]["id"] == thread_id
    assert Path(metadata[0]["cwd"]).resolve() == Path(cwd).resolve()
    events = [r["payload"] for r in records if r.get("type") == "event_msg"]
    entries = [e for e in events if e.get("type") == "item_completed"
               and e.get("thread_id") == thread_id
               and e.get("item", {}).get("type") == "EnteredReviewMode"]
    assert len(entries) == 1
    entry = entries[0]
    assert entry["item"]["target"] == {"type": "baseBranch", "branch": base}
    turn = entry["turn_id"]
    exits = [e for e in events if e.get("type") == "item_completed"
             and e.get("thread_id") == thread_id and e.get("turn_id") == turn
             and e.get("item", {}).get("type") == "ExitedReviewMode"]
    assert len(exits) == 1
    terminal = [e for e in events if e.get("turn_id") == turn
                and e.get("type") in {"task_complete", "turn_aborted"}]
    assert len(terminal) == 1 and terminal[0]["type"] == "task_complete"
    assert events.index(exits[0]) < events.index(terminal[0])
    output = exits[0]["item"]["review_output"]
    assert isinstance(output, dict) and isinstance(output.get("findings"), list)
    assert output.get("overall_correctness") in {"patch is correct", "patch is incorrect"}
    assert isinstance(output.get("overall_explanation"), str) and output["overall_explanation"].strip()
    assert type(output.get("overall_confidence_score")) in {int, float}
    assert math.isfinite(output["overall_confidence_score"])
    return turn, output


class Rpc:
    """Test client for direct native stdio protocol, not an installed helper."""
    def __init__(self, process: asyncio.subprocess.Process) -> None:
        self.process = process
        self.sequence = 0
        self.notifications: list[dict] = []

    async def send(self, value: dict) -> None:
        self.process.stdin.write((json.dumps(value) + "\n").encode())
        await self.process.stdin.drain()

    async def read(self) -> dict:
        line = await asyncio.wait_for(self.process.stdout.readline(), 30)
        if not line:
            raise RuntimeError("native app-server closed unexpectedly")
        value = json.loads(line)
        if "method" in value and "id" in value:
            await self.send({"id": value["id"], "error": {
                "code": -32601, "message": "unconfigured qualification request"}})
        return value

    async def request(self, method: str, params: dict) -> dict:
        self.sequence += 1
        identifier = self.sequence
        await self.send({"id": identifier, "method": method, "params": params})
        while True:
            value = await self.read()
            if value.get("id") == identifier and "method" not in value:
                if "error" in value:
                    raise RuntimeError(f"{method}: {value['error']}")
                return value["result"]
            self.notifications.append(value)

    async def completed(self, thread: str, turn: str) -> dict:
        while True:
            for index, value in enumerate(self.notifications):
                params = value.get("params", {})
                if (value.get("method") == "turn/completed" and params.get("threadId") == thread
                        and params.get("turn", {}).get("id") == turn):
                    return self.notifications.pop(index)["params"]["turn"]
            self.notifications.append(await self.read())


class NativeQualification(unittest.TestCase):
    codex: str

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="native-codex-")
        self.root = Path(self.temp.name)
        self.provider = Provider()
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(self.provider.close)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.name", "Native Fixture")
        git(self.repo, "config", "user.email", "fixture@localhost")
        (self.repo / "example.txt").write_text("before\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "base")
        self.base = git(self.repo, "rev-parse", "HEAD")
        (self.repo / "example.txt").write_text("after\n")
        git(self.repo, "commit", "-qam", "head")
        self.head = git(self.repo, "rev-parse", "HEAD")
        self.home = self.root / "home"
        self.home.mkdir()
        (self.home / "config.toml").write_text(f'''model = "gpt-6-astra"
model_provider = "fixture"
approval_policy = "never"
sandbox_mode = "read-only"
[analytics]
enabled = false
[model_providers.fixture]
name = "Native Qualification Fixture"
base_url = "http://127.0.0.1:{self.provider.port}/v1"
wire_api = "responses"
supports_websockets = true
request_max_retries = 0
stream_max_retries = 0
requires_openai_auth = false
''')
        poison = self.root / "bin"
        poison.mkdir()
        stub = poison / "cas"
        stub.write_text('#!/bin/sh\nprintf "unexpected CAS invocation\\n" >> "$CODEX_HOME/cas-invoked"\nexit 99\n')
        stub.chmod(0o755)
        self.env = {"PATH": str(poison) + os.pathsep + os.environ["PATH"],
                    "HOME": str(self.home), "CODEX_HOME": str(self.home),
                    "LANG": "C.UTF-8", "TERM": "dumb", "TMPDIR": str(self.root)}
        self.provider.answer = json.dumps(self.clean())

    def tearDown(self) -> None:
        self.assertFalse((self.home / "cas-invoked").exists())
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), self.head)
        self.assertEqual(git(self.repo, "status", "--porcelain"), "")

    @staticmethod
    def clean() -> dict:
        return {"findings": [], "overall_correctness": "patch is correct",
                "overall_explanation": "Fixture review completed for the selected subject.",
                "overall_confidence_score": 0.95}

    def cli(self, instructions: str | None = None, interrupt: bool = False) -> tuple[int, list[dict], list[dict], str]:
        output = self.root / "final.txt"
        args = [self.codex, "exec", "--cd", str(self.repo), "--json", "--output-last-message", str(output)]
        if instructions is not None:
            args += ["-c", "developer_instructions=" + json.dumps(instructions, ensure_ascii=False)]
        args += ["review", "--base", self.base]
        with subprocess.Popen(args, cwd=self.repo, env=self.env, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True, start_new_session=True) as process:
            try:
                if interrupt or self.provider.delay:
                    deadline = time.monotonic() + 30
                    while not any(r["body"].get("generate", True) for r in self.provider.requests):
                        self.assertIsNone(process.poll())
                        if time.monotonic() > deadline:
                            raise TimeoutError("review request not observed")
                        time.sleep(0.02)
                    if interrupt:
                        os.killpg(process.pid, signal.SIGINT)
                        # Signal submission is not terminal evidence. The qualified
                        # runtime can reject its root-turn interrupt while a delegate runs.
                        try:
                            process.wait(timeout=0.2)
                        except subprocess.TimeoutExpired:
                            os.killpg(process.pid, signal.SIGTERM)
                    else:
                        with self.assertRaises(subprocess.TimeoutExpired):
                            process.wait(timeout=0.05)
                        self.assertIsNone(process.poll(), "an observation wait must not terminate execution")
                stdout, stderr = process.communicate(timeout=45)
            except BaseException:
                os.killpg(process.pid, signal.SIGKILL)
                process.communicate(timeout=10)
                raise
        stream = [json.loads(line) for line in stdout.splitlines()]
        ids = [e["thread_id"] for e in stream if e.get("type") == "thread.started"]
        records: list[dict] = []
        if ids:
            self.assertEqual(len(ids), 1)
            paths = list((self.home / "sessions").rglob(f"*{ids[0]}*.jsonl"))
            self.assertEqual(len(paths), 1, stderr)
            records = [json.loads(line) for line in paths[0].read_text().splitlines()]
        return process.returncode, stream, records, output.read_text() if output.exists() else ""

    def test_native_standard_websocket_and_structured_evidence(self) -> None:
        code, stream, records, rendered = self.cli()
        self.assertEqual(code, 0)
        self.assertEqual(sum(e["type"] == "turn.completed" for e in stream), 1)
        thread = next(e["thread_id"] for e in stream if e["type"] == "thread.started")
        _, output = native_output(records, thread, self.base, str(self.repo))
        self.assertEqual(output, self.clean())
        self.assertIn(self.clean()["overall_explanation"], rendered)
        actual = [r for r in self.provider.requests if r["body"].get("generate", True)]
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0]["transport"], "websocket")
        self.assertIn("review", json.dumps(actual[0]["body"]).lower())
        self.assertFalse(any("review_output" in e for e in stream))
        # Paired negative controls exercise the artifact oracle, not a production admission engine.
        for field, bad in [("thread", "other"), ("base", "other"), ("cwd", str(self.root))]:
            with self.subTest(field=field), self.assertRaises(AssertionError):
                native_output(records, bad if field == "thread" else thread,
                              bad if field == "base" else self.base,
                              bad if field == "cwd" else str(self.repo))
        for kind in ("EnteredReviewMode", "ExitedReviewMode", "task_complete"):
            modified = [r for r in records if not (r.get("type") == "event_msg" and
                        (r["payload"].get("type") == kind or r["payload"].get("item", {}).get("type") == kind))]
            with self.subTest(missing=kind), self.assertRaises(AssertionError):
                native_output(modified, thread, self.base, str(self.repo))

    def test_exact_auxiliary_override_and_nonblocking_findings(self) -> None:
        instructions = 'EXACT-AUXILIARY\nquotes " and slash \\ and Unicode λ 🚀\n\n'
        report = self.clean()
        report["findings"] = [{"title": "Fixture finding", "body": "A supported fixture observation.",
            "confidence_score": 0.9, "priority": 2,
            "code_location": {"absolute_file_path": str(self.repo / "example.txt"),
                              "line_range": {"start": 1, "end": 1}}}]
        self.provider.answer = json.dumps(report)
        code, stream, records, _ = self.cli(instructions)
        self.assertEqual(code, 0)
        thread = next(e["thread_id"] for e in stream if e["type"] == "thread.started")
        _, output = native_output(records, thread, self.base, str(self.repo))
        self.assertEqual(len(output["findings"]), 1)
        self.assertEqual(output["overall_correctness"], "patch is correct")
        bodies = [r["body"] for r in self.provider.requests if r["body"].get("generate", True)]
        texts = [c["text"] for body in bodies for item in body.get("input", [])
                 if item.get("role") == "developer" for c in item.get("content", []) if "text" in c]
        self.assertIn(instructions, texts)

    def test_malformed_result_is_not_structured_verdict(self) -> None:
        self.provider.answer = "This is unstructured fallback text, not a verdict."
        code, stream, records, _ = self.cli()
        thread = next(e["thread_id"] for e in stream if e["type"] == "thread.started")
        with self.assertRaises(AssertionError):
            native_output(records, thread, self.base, str(self.repo))
        # Exit success can coexist with unusable model output; it is not clean credit.
        self.assertEqual(code, 0)

    def test_observation_timeout_retains_same_execution(self) -> None:
        self.provider.delay = 0.5
        code, stream, records, _ = self.cli()
        self.assertEqual(code, 0)
        thread = next(e["thread_id"] for e in stream if e["type"] == "thread.started")
        native_output(records, thread, self.base, str(self.repo))
        self.assertEqual(sum(r["body"].get("generate", True) for r in self.provider.requests), 1)

    def test_cancellation_requires_observed_process_termination(self) -> None:
        self.provider.delay = 1.0
        code, stream, records, _ = self.cli(interrupt=True)
        self.assertNotEqual(code, 0)
        thread = next(e["thread_id"] for e in stream if e["type"] == "thread.started")
        self.assertFalse(any(e["type"] == "turn.completed" for e in stream))
        with self.assertRaises((AssertionError, KeyError)):
            native_output(records, thread, self.base, str(self.repo))

    def test_provider_failure_is_not_completed_review(self) -> None:
        self.provider.fail = True
        code, stream, records, _ = self.cli()
        self.assertNotEqual(code, 0)
        self.assertTrue(any(e["type"] in {"error", "turn.failed"} for e in stream))
        ids = [e["thread_id"] for e in stream if e["type"] == "thread.started"]
        if ids:
            with self.assertRaises((AssertionError, KeyError)):
                native_output(records, ids[0], self.base, str(self.repo))

    def test_prepared_seed_history_and_native_control_websocket(self) -> None:
        asyncio.run(self.fork_qualification())

    async def fork_qualification(self) -> None:
        with (self.root / "app-server.log").open("wb") as stderr:
            process = await asyncio.create_subprocess_exec(self.codex, "app-server", "--listen", "stdio://",
                cwd=self.repo, env=self.env, stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE, stderr=stderr)
            rpc = Rpc(process)
            try:
                await rpc.request("initialize", {"clientInfo": {"name": "native-qualification", "version": "1"},
                                                "capabilities": {"experimentalApi": True}})
                await rpc.send({"method": "initialized"})
                thread = (await rpc.request("thread/start", {"cwd": str(self.repo), "historyMode": "paginated",
                            "approvalPolicy": "never", "sandbox": "read-only"}))["thread"]["id"]
                self.provider.answer = "PREPARED-ANALYSIS-AND-BRIEF"
                prep = await rpc.request("turn/start", {"threadId": thread,
                         "input": [{"type": "text", "text": "PREPARATION-INPUT", "text_elements": []}]})
                self.assertEqual((await rpc.completed(thread, prep["turn"]["id"]))["status"], "completed")
                seed = (await rpc.request("thread/fork", {"threadId": thread, "lastTurnId": prep["turn"]["id"],
                        "excludeTurns": True, "deferGoalContinuation": True}))["thread"]
                self.assertEqual(seed["forkedFromId"], thread)
                async def items(identifier: str) -> list[dict]:
                    result, cursor = [], None
                    while True:
                        params = {"threadId": identifier, "limit": 1, "sortDirection": "asc"}
                        if cursor is not None:
                            params["cursor"] = cursor
                        page = await rpc.request("thread/items/list", params)
                        result.extend(page["data"])
                        cursor = page.get("nextCursor")
                        if cursor is None:
                            return result
                before = await items(seed["id"])
                self.assertIn("PREPARED-ANALYSIS-AND-BRIEF", json.dumps(before))
                children = []
                for _ in range(2):
                    child = (await rpc.request("thread/fork", {"threadId": seed["id"],
                                "excludeTurns": True, "deferGoalContinuation": True}))["thread"]
                    self.assertEqual(child["forkedFromId"], seed["id"])
                    self.assertEqual(await items(child["id"]), before)
                    children.append(child["id"])
                self.provider.answer = "CHILD-ONE-RESULT"
                child_turn = await rpc.request("turn/start", {"threadId": children[0],
                    "input": [{"type": "text", "text": "CHILD-ONE-ASSIGNMENT", "text_elements": []}]})
                await rpc.completed(children[0], child_turn["turn"]["id"])
                self.assertEqual(await items(seed["id"]), before)
                self.assertEqual(await items(children[1]), before)
                self.assertNotIn("CHILD-ONE", json.dumps(await items(children[1])))
            finally:
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), 10)
                except TimeoutError:
                    process.kill()
                    await process.wait()
        # A real native WebSocket listener, independent of model-side WebSockets.
        import socket
        import aiohttp
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        endpoint = f"ws://127.0.0.1:{port}"
        with (self.root / "websocket.log").open("wb") as stderr:
            process = await asyncio.create_subprocess_exec(self.codex, "app-server", "--listen", endpoint,
                cwd=self.repo, env=self.env, stdout=asyncio.subprocess.DEVNULL, stderr=stderr)
            try:
                async with aiohttp.ClientSession() as client:
                    deadline = time.monotonic() + 15
                    while True:
                        try:
                            ws = await client.ws_connect(endpoint)
                            break
                        except aiohttp.ClientConnectorError:
                            if time.monotonic() >= deadline:
                                raise
                            await asyncio.sleep(0.05)
                    async with ws:
                        await ws.send_json({"id": 1, "method": "initialize", "params": {
                            "clientInfo": {"name": "native-ws-qualification", "version": "1"}}})
                        reply = await ws.receive_json(timeout=15)
                        self.assertEqual(reply["id"], 1)
                        self.assertIn("result", reply)
                        await ws.send_json({"method": "initialized"})
            finally:
                process.terminate()
                await asyncio.wait_for(process.wait(), 10)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex", required=True, help="Exact installed native Codex executable")
    args, remaining = parser.parse_known_args()
    executable = shutil.which(args.codex)
    if executable is None:
        parser.error("native Codex executable is unavailable; qualification did not run")
    NativeQualification.codex = str(Path(executable).resolve())
    print(subprocess.check_output([NativeQualification.codex, "--version"], text=True).strip(), flush=True)
    unittest.main(argv=[__file__, *remaining], verbosity=2)
