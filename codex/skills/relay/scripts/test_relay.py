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
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

import httpx


SCRIPT = Path(__file__).with_name("relay.py")


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True)


def run_mock() -> int:
    records: list[dict[str, Any]] = []

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

    cmds = [
        [str(SCRIPT), "--server-url", "http://127.0.0.1:8877", "health"],
        [str(SCRIPT), "--server-url", "http://127.0.0.1:8877", "start", "--project", "/tmp/repo", "--program", "codex-cli", "--model", "gpt-5"],
        [str(SCRIPT), "--server-url", "http://127.0.0.1:8877", "prepare", "--project", "/tmp/repo", "--thread", "bd-1", "--program", "codex-cli", "--model", "gpt-5"],
        [str(SCRIPT), "--server-url", "http://127.0.0.1:8877", "reserve", "--project", "/tmp/repo", "--agent", "BlueLake", "--path", "src/**"],
        [str(SCRIPT), "--server-url", "http://127.0.0.1:8877", "send", "--project", "/tmp/repo", "--sender", "BlueLake", "--to", "GreenStone,RedForest", "--subject", "s", "--body", "b", "--thread", "bd-1", "--ack-required"],
        [str(SCRIPT), "--server-url", "http://127.0.0.1:8877", "poll", "--project", "/tmp/repo", "--agent", "BlueLake"],
        [str(SCRIPT), "--server-url", "http://127.0.0.1:8877", "ack", "--project", "/tmp/repo", "--agent", "BlueLake", "--message-id", "9"],
        [str(SCRIPT), "--server-url", "http://127.0.0.1:8877", "link", "--project", "/tmp/repo", "--requester", "BlueLake", "--target", "RedForest", "--auto-accept"],
    ]

    ok = True
    try:
        for cmd in cmds:
            proc = _run(cmd)
            if proc.returncode != 0:
                print("mock fail:", " ".join(cmd))
                print(proc.stdout)
                print(proc.stderr)
                ok = False
                break
    finally:
        server.shutdown()

    expected = [
        "health_check",
        "macro_start_session",
        "macro_prepare_thread",
        "macro_file_reservation_cycle",
        "send_message",
        "fetch_inbox",
        "acknowledge_message",
        "macro_contact_handshake",
    ]
    seen = [record.get("params", {}).get("name") for record in records]
    if seen != expected:
        print("mock mapping mismatch")
        print("seen:", seen)
        print("expected:", expected)
        ok = False

    if ok:
        print("mock: PASS")
        return 0
    print("mock: FAIL")
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
