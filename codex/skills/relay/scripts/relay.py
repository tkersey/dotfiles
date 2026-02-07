#!/usr/bin/env -S uv run --with httpx python
"""Relay adapter CLI.

Provide stable coordination verbs that map to backend tool calls.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any

import httpx

DEFAULT_TOOL_MAP: dict[str, str] = {
    "health": "health_check",
    "start": "macro_start_session",
    "prepare": "macro_prepare_thread",
    "reserve": "macro_file_reservation_cycle",
    "send": "send_message",
    "poll": "fetch_inbox",
    "ack": "acknowledge_message",
    "link": "macro_contact_handshake",
}


def _split_csv(values: list[str] | None) -> list[str]:
    if not values:
        return []
    out: list[str] = []
    for value in values:
        for part in value.split(","):
            item = part.strip()
            if item:
                out.append(item)
    return out


def _load_tool_map(path: str | None) -> dict[str, str]:
    tool_map = dict(DEFAULT_TOOL_MAP)
    raw = os.getenv("RELAY_TOOL_MAP", "").strip()
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                tool_map.update({str(k): str(v) for k, v in parsed.items()})
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid RELAY_TOOL_MAP JSON: {exc}") from exc

    if path:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise SystemExit("--tool-map must point to a JSON object")
        tool_map.update({str(k): str(v) for k, v in data.items()})
    return tool_map


def _rpc_call(
    server_url: str,
    token: str | None,
    tool_name: str,
    arguments: dict[str, Any],
    timeout_seconds: float,
    dry_run: bool,
) -> Any:
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }

    if dry_run:
        return {"dry_run": True, "request": payload}

    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    with httpx.Client(timeout=timeout_seconds) as client:
        response = client.post(server_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    if isinstance(data, dict) and "error" in data:
        raise SystemExit(json.dumps(data["error"], indent=2, sort_keys=True))

    return data.get("result", data)


def _print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Relay coordination adapter")
    parser.add_argument(
        "--server-url",
        default=os.getenv("RELAY_SERVER_URL", "http://127.0.0.1:8765/api/"),
        help="Tool-call endpoint URL",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("RELAY_BEARER_TOKEN", "").strip() or None,
        help="Bearer token (or RELAY_BEARER_TOKEN)",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=float(os.getenv("RELAY_TIMEOUT_SECONDS", "30")),
        help="HTTP timeout in seconds",
    )
    parser.add_argument(
        "--tool-map",
        default=None,
        help="Path to JSON object overriding verb->tool mapping",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print request without calling server")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("health", help="Check server health")

    p_start = sub.add_parser("start", help="Bootstrap session")
    p_start.add_argument("--project", required=True)
    p_start.add_argument("--program", required=True)
    p_start.add_argument("--model", required=True)
    p_start.add_argument("--task", default="")
    p_start.add_argument("--agent", default=None)

    p_prepare = sub.add_parser("prepare", help="Prepare an active thread")
    p_prepare.add_argument("--project", required=True)
    p_prepare.add_argument("--thread", required=True)
    p_prepare.add_argument("--program", required=True)
    p_prepare.add_argument("--model", required=True)
    p_prepare.add_argument("--agent", default=None)
    p_prepare.add_argument("--task", default="")

    p_reserve = sub.add_parser("reserve", help="Reserve file paths")
    p_reserve.add_argument("--project", required=True)
    p_reserve.add_argument("--agent", required=True)
    p_reserve.add_argument("--path", action="append", required=True)
    p_reserve.add_argument("--reason", default="relay")
    p_reserve.add_argument("--ttl-seconds", type=int, default=3600)
    p_reserve.add_argument("--shared", action="store_true")
    p_reserve.add_argument("--auto-release", action="store_true")

    p_send = sub.add_parser("send", help="Send message")
    p_send.add_argument("--project", required=True)
    p_send.add_argument("--sender", required=True)
    p_send.add_argument("--to", action="append", required=True, help="Recipient list or CSV")
    p_send.add_argument("--cc", action="append", default=[])
    p_send.add_argument("--bcc", action="append", default=[])
    p_send.add_argument("--subject", required=True)
    p_send.add_argument("--body", required=True)
    p_send.add_argument("--thread", default=None)
    p_send.add_argument("--importance", default="normal")
    p_send.add_argument("--ack-required", action="store_true")

    p_poll = sub.add_parser("poll", help="Fetch inbox")
    p_poll.add_argument("--project", required=True)
    p_poll.add_argument("--agent", required=True)
    p_poll.add_argument("--limit", type=int, default=20)
    p_poll.add_argument("--urgent-only", action="store_true")
    p_poll.add_argument("--include-bodies", action="store_true")
    p_poll.add_argument("--since", default=None)

    p_ack = sub.add_parser("ack", help="Acknowledge one message")
    p_ack.add_argument("--project", required=True)
    p_ack.add_argument("--agent", required=True)
    p_ack.add_argument("--message-id", type=int, required=True)

    p_link = sub.add_parser("link", help="Open contact path between agents")
    p_link.add_argument("--project", required=True)
    p_link.add_argument("--requester", required=True)
    p_link.add_argument("--target", required=True)
    p_link.add_argument("--to-project", default=None)
    p_link.add_argument("--reason", default="")
    p_link.add_argument("--ttl-seconds", type=int, default=86400)
    p_link.add_argument("--auto-accept", action="store_true")

    return parser


def _build_args(namespace: argparse.Namespace) -> dict[str, Any]:
    cmd = namespace.command

    if cmd == "health":
        return {}

    if cmd == "start":
        args: dict[str, Any] = {
            "human_key": namespace.project,
            "program": namespace.program,
            "model": namespace.model,
            "task_description": namespace.task,
        }
        if namespace.agent:
            args["agent_name"] = namespace.agent
        return args

    if cmd == "prepare":
        args = {
            "project_key": namespace.project,
            "thread_id": namespace.thread,
            "program": namespace.program,
            "model": namespace.model,
            "task_description": namespace.task,
        }
        if namespace.agent:
            args["agent_name"] = namespace.agent
        return args

    if cmd == "reserve":
        return {
            "project_key": namespace.project,
            "agent_name": namespace.agent,
            "paths": namespace.path,
            "ttl_seconds": namespace.ttl_seconds,
            "exclusive": not namespace.shared,
            "reason": namespace.reason,
            "auto_release": namespace.auto_release,
        }

    if cmd == "send":
        return {
            "project_key": namespace.project,
            "sender_name": namespace.sender,
            "to": _split_csv(namespace.to),
            "cc": _split_csv(namespace.cc),
            "bcc": _split_csv(namespace.bcc),
            "subject": namespace.subject,
            "body_md": namespace.body,
            "thread_id": namespace.thread,
            "importance": namespace.importance,
            "ack_required": bool(namespace.ack_required),
        }

    if cmd == "poll":
        return {
            "project_key": namespace.project,
            "agent_name": namespace.agent,
            "limit": namespace.limit,
            "urgent_only": bool(namespace.urgent_only),
            "include_bodies": bool(namespace.include_bodies),
            "since_ts": namespace.since,
        }

    if cmd == "ack":
        return {
            "project_key": namespace.project,
            "agent_name": namespace.agent,
            "message_id": namespace.message_id,
        }

    if cmd == "link":
        args = {
            "project_key": namespace.project,
            "requester": namespace.requester,
            "target": namespace.target,
            "reason": namespace.reason,
            "ttl_seconds": namespace.ttl_seconds,
            "auto_accept": bool(namespace.auto_accept),
        }
        if namespace.to_project:
            args["to_project"] = namespace.to_project
        return args

    raise SystemExit(f"Unsupported command: {cmd}")


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    tool_map = _load_tool_map(args.tool_map)

    if args.command not in tool_map:
        raise SystemExit(f"No tool mapping for command '{args.command}'")

    request_args = _build_args(args)
    result = _rpc_call(
        server_url=args.server_url,
        token=args.token,
        tool_name=tool_map[args.command],
        arguments=request_args,
        timeout_seconds=args.timeout_seconds,
        dry_run=bool(args.dry_run),
    )
    _print_json(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
