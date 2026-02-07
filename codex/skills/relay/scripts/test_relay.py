#!/usr/bin/env -S uv run --with httpx python
"""Self-tests for relay adapter.

Modes:
- mock: starts a local fake JSON-RPC endpoint and verifies verb->tool mapping.
- live: calls a real backend endpoint and checks health.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

import httpx


SCRIPT = Path(__file__).with_name("relay.py")


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True)


def _stdout_json(proc: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    try:
        parsed = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON output: {exc}\nstdout={proc.stdout}\nstderr={proc.stderr}") from exc
    if not isinstance(parsed, dict):
        raise RuntimeError(f"Expected JSON object output, got: {type(parsed).__name__}")
    return parsed


def run_mock() -> int:
    records: list[dict[str, Any]] = []
    failures: list[str] = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802
            size = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(size)
            payload = json.loads(body.decode("utf-8"))
            records.append(payload)

            response = {
                "jsonrpc": "2.0",
                "id": payload.get("id"),
                "result": {
                    "ok": True,
                    "tool": payload.get("params", {}).get("name"),
                    "arguments": payload.get("params", {}).get("arguments", {}),
                },
            }
            out = json.dumps(response).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(out)))
            self.end_headers()
            self.wfile.write(out)

        def log_message(self, *_: Any) -> None:
            return

    server = HTTPServer(("127.0.0.1", 8877), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    base = [str(SCRIPT), "--server-url", "http://127.0.0.1:8877"]

    def fail(msg: str) -> None:
        failures.append(msg)
        print(msg)

    def run_expect(
        cmd: list[str],
        *,
        expected_tool: str,
        expected_args: dict[str, Any],
    ) -> None:
        proc = _run(cmd)
        if proc.returncode != 0:
            fail(f"mock fail: {' '.join(cmd)}\nstdout={proc.stdout}\nstderr={proc.stderr}")
            return
        try:
            output = _stdout_json(proc)
        except Exception as exc:
            fail(f"mock output parse failure: {' '.join(cmd)}\n{exc}")
            return

        got_tool = output.get("tool")
        if got_tool != expected_tool:
            fail(f"tool mismatch for {' '.join(cmd)}: got={got_tool!r} expected={expected_tool!r}")
            return

        got_args = output.get("arguments", {})
        if not isinstance(got_args, dict):
            fail(f"arguments payload is not an object for {' '.join(cmd)}: {type(got_args).__name__}")
            return
        for key, expected_value in expected_args.items():
            got_value = got_args.get(key)
            if got_value != expected_value:
                fail(
                    f"argument mismatch for {' '.join(cmd)} key={key!r}: "
                    f"got={got_value!r} expected={expected_value!r}"
                )

    tool_map_path: str | None = None
    try:
        run_expect(
            [*base, "health"],
            expected_tool="health_check",
            expected_args={},
        )
        run_expect(
            [
                *base,
                "start",
                "--project",
                "/tmp/repo",
                "--program",
                "codex-cli",
                "--model",
                "gpt-5",
                "--task",
                "bootstrap",
                "--agent",
                "BlueLake",
            ],
            expected_tool="macro_start_session",
            expected_args={
                "human_key": "/tmp/repo",
                "program": "codex-cli",
                "model": "gpt-5",
                "task_description": "bootstrap",
                "agent_name": "BlueLake",
            },
        )
        run_expect(
            [
                *base,
                "prepare",
                "--project",
                "/tmp/repo",
                "--thread",
                "bd-1",
                "--program",
                "codex-cli",
                "--model",
                "gpt-5",
                "--task",
                "catch-up",
                "--agent",
                "BlueLake",
            ],
            expected_tool="macro_prepare_thread",
            expected_args={
                "project_key": "/tmp/repo",
                "thread_id": "bd-1",
                "program": "codex-cli",
                "model": "gpt-5",
                "task_description": "catch-up",
                "agent_name": "BlueLake",
            },
        )
        run_expect(
            [
                *base,
                "reserve",
                "--project",
                "/tmp/repo",
                "--agent",
                "BlueLake",
                "--path",
                "src/**",
                "--reason",
                "bd-1",
            ],
            expected_tool="macro_file_reservation_cycle",
            expected_args={
                "project_key": "/tmp/repo",
                "agent_name": "BlueLake",
                "paths": ["src/**"],
                "ttl_seconds": 3600,
                "exclusive": True,
                "reason": "bd-1",
                "auto_release": False,
            },
        )
        run_expect(
            [
                *base,
                "reserve",
                "--project",
                "/tmp/repo",
                "--agent",
                "BlueLake",
                "--path",
                "docs/**",
                "--shared",
                "--auto-release",
            ],
            expected_tool="macro_file_reservation_cycle",
            expected_args={
                "project_key": "/tmp/repo",
                "agent_name": "BlueLake",
                "paths": ["docs/**"],
                "ttl_seconds": 3600,
                "exclusive": False,
                "reason": "relay",
                "auto_release": True,
            },
        )
        run_expect(
            [
                *base,
                "send",
                "--project",
                "/tmp/repo",
                "--sender",
                "BlueLake",
                "--to",
                "GreenStone,RedForest",
                "--to",
                "WhiteCat",
                "--cc",
                "GrayFox",
                "--bcc",
                "AmberBird,OliveTree",
                "--subject",
                "s",
                "--body",
                "b",
                "--thread",
                "bd-1",
                "--importance",
                "high",
                "--ack-required",
            ],
            expected_tool="send_message",
            expected_args={
                "project_key": "/tmp/repo",
                "sender_name": "BlueLake",
                "to": ["GreenStone", "RedForest", "WhiteCat"],
                "cc": ["GrayFox"],
                "bcc": ["AmberBird", "OliveTree"],
                "subject": "s",
                "body_md": "b",
                "thread_id": "bd-1",
                "importance": "high",
                "ack_required": True,
            },
        )
        run_expect(
            [
                *base,
                "poll",
                "--project",
                "/tmp/repo",
                "--agent",
                "BlueLake",
                "--limit",
                "7",
                "--urgent-only",
                "--include-bodies",
                "--since",
                "2026-02-07T00:00:00Z",
            ],
            expected_tool="fetch_inbox",
            expected_args={
                "project_key": "/tmp/repo",
                "agent_name": "BlueLake",
                "limit": 7,
                "urgent_only": True,
                "include_bodies": True,
                "since_ts": "2026-02-07T00:00:00Z",
            },
        )
        run_expect(
            [
                *base,
                "ack",
                "--project",
                "/tmp/repo",
                "--agent",
                "BlueLake",
                "--message-id",
                "9",
            ],
            expected_tool="acknowledge_message",
            expected_args={
                "project_key": "/tmp/repo",
                "agent_name": "BlueLake",
                "message_id": 9,
            },
        )
        run_expect(
            [
                *base,
                "link",
                "--project",
                "/tmp/repo",
                "--requester",
                "BlueLake",
                "--target",
                "RedForest",
                "--to-project",
                "/tmp/frontend",
                "--reason",
                "handoff",
                "--ttl-seconds",
                "1234",
                "--auto-accept",
            ],
            expected_tool="macro_contact_handshake",
            expected_args={
                "project_key": "/tmp/repo",
                "requester": "BlueLake",
                "target": "RedForest",
                "to_project": "/tmp/frontend",
                "reason": "handoff",
                "ttl_seconds": 1234,
                "auto_accept": True,
            },
        )

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
            json.dump({"poll": "fetch_inbox_custom"}, tf)
            tool_map_path = tf.name
        run_expect(
            [
                *base,
                "--tool-map",
                tool_map_path,
                "poll",
                "--project",
                "/tmp/repo",
                "--agent",
                "BlueLake",
            ],
            expected_tool="fetch_inbox_custom",
            expected_args={
                "project_key": "/tmp/repo",
                "agent_name": "BlueLake",
                "limit": 20,
                "urgent_only": False,
                "include_bodies": False,
                "since_ts": None,
            },
        )

        before_dry_run = len(records)
        proc = _run(
            [
                *base,
                "--dry-run",
                "link",
                "--project",
                "/tmp/repo",
                "--requester",
                "BlueLake",
                "--target",
                "RedForest",
                "--auto-accept",
            ]
        )
        if proc.returncode != 0:
            fail(f"dry-run command failed\nstdout={proc.stdout}\nstderr={proc.stderr}")
        else:
            try:
                dry_output = _stdout_json(proc)
            except Exception as exc:
                fail(f"dry-run output parse failure: {exc}")
            else:
                if dry_output.get("dry_run") is not True:
                    fail(f"dry-run output missing dry_run=true: {dry_output}")
                request_name = (
                    dry_output.get("request", {})
                    .get("params", {})
                    .get("name")
                )
                if request_name != "macro_contact_handshake":
                    fail(
                        "dry-run tool mismatch: "
                        f"got={request_name!r} expected='macro_contact_handshake'"
                    )
                if len(records) != before_dry_run:
                    fail(
                        "dry-run made a network call unexpectedly: "
                        f"records_before={before_dry_run} records_after={len(records)}"
                    )
    finally:
        server.shutdown()
        server.server_close()
        if tool_map_path:
            Path(tool_map_path).unlink(missing_ok=True)

    expected_tools = [
        "health_check",
        "macro_start_session",
        "macro_prepare_thread",
        "macro_file_reservation_cycle",
        "macro_file_reservation_cycle",
        "send_message",
        "fetch_inbox",
        "acknowledge_message",
        "macro_contact_handshake",
        "fetch_inbox_custom",
    ]
    seen_tools = [record.get("params", {}).get("name") for record in records]
    if seen_tools != expected_tools:
        fail(f"mock mapping mismatch\nseen={seen_tools}\nexpected={expected_tools}")

    if not failures:
        print("mock: PASS")
        return 0
    print(f"mock: FAIL ({len(failures)} issue(s))")
    return 1


def run_live(server_url: str, token: str | None, timeout_seconds: float) -> int:
    payload = {
        "jsonrpc": "2.0",
        "id": "relay-live-health",
        "method": "tools/call",
        "params": {"name": "health_check", "arguments": {}},
    }
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        with httpx.Client(timeout=timeout_seconds) as client:
            response = client.post(server_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
    except Exception as exc:
        print(f"live: FAIL ({exc})")
        return 1

    if isinstance(data, dict) and "error" in data:
        print("live: FAIL (json-rpc error)")
        print(json.dumps(data["error"], indent=2, sort_keys=True))
        return 1

    print("live: PASS")
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run relay adapter self-tests")
    parser.add_argument("--mode", choices=["mock", "live"], default="mock")
    parser.add_argument("--server-url", default="http://127.0.0.1:8765/api/")
    parser.add_argument("--token", default=None)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    args = parser.parse_args()

    if args.mode == "mock":
        return run_mock()
    return run_live(args.server_url, args.token, args.timeout_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
