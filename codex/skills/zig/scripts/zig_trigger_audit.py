#!/usr/bin/env python3
"""
Session-level proxy audit for Zig skill invocation.

This wrapper keeps Zig-trigger auditing discoverable from the zig skill while
reusing the seq mining engine.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


INTENT_REGEX = (
    r"\bzig\b|\.zig\b|build\.zig(?:\.zon)?\b|"
    r"\bzig (build|test|run|fmt|fetch)\b|"
    r"\b(comptime|@Vector|std\.simd|std\.Thread|@cImport)\b"
)


def run_seq_query(
    seq_script: Path,
    root: str,
    spec: dict,
    since: str | None,
    until: str | None,
) -> list[dict]:
    cmd = [
        sys.executable,
        str(seq_script),
        "query",
        "--root",
        root,
        "--spec",
        json.dumps(spec),
    ]
    if since:
        cmd.extend(["--since", since])
    if until:
        cmd.extend(["--until", until])

    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "seq query failed")

    rows: list[dict] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            # Ignore non-JSON lines so script remains robust to incidental output.
            continue
    return rows


def is_explicit_zig_invocation(text: str) -> bool:
    lower = text.lower()
    return "$zig" in lower or "<name>zig</name>" in lower


def pct(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return (numerator / denominator) * 100.0


def resolve_seq_script() -> Path:
    # codex/skills/zig/scripts/zig_trigger_audit.py -> codex/skills/seq/scripts/seq.py
    here = Path(__file__).resolve()
    seq_script = here.parents[2] / "seq" / "scripts" / "seq.py"
    if not seq_script.exists():
        raise FileNotFoundError(f"seq script not found at: {seq_script}")
    return seq_script


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit Zig skill invocation coverage from session logs."
    )
    parser.add_argument(
        "--root",
        default=str(Path.home() / ".codex" / "sessions"),
        help="Sessions root for seq mining (default: ~/.codex/sessions).",
    )
    parser.add_argument(
        "--since",
        default=None,
        help="Inclusive ISO timestamp lower bound, e.g. 2026-02-06T00:00:00Z.",
    )
    parser.add_argument(
        "--until",
        default=None,
        help="Inclusive ISO timestamp upper bound.",
    )
    parser.add_argument(
        "--max-misses",
        type=int,
        default=15,
        help="Max miss-session paths to print (default: 15).",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    seq_script = resolve_seq_script()

    intent_spec = {
        "dataset": "messages",
        "where": [
            {"field": "role", "op": "eq", "value": "user"},
            {
                "field": "text",
                "op": "regex",
                "value": INTENT_REGEX,
                "case_insensitive": True,
            },
        ],
        "select": ["path", "text"],
        "format": "jsonl",
    }
    zig_skill_spec = {
        "dataset": "skill_mentions",
        "where": [
            {"field": "role", "op": "eq", "value": "assistant"},
            {"field": "skill", "op": "eq", "value": "zig"},
        ],
        "select": ["path"],
        "format": "jsonl",
    }

    intent_rows = run_seq_query(
        seq_script=seq_script,
        root=args.root,
        spec=intent_spec,
        since=args.since,
        until=args.until,
    )
    zig_rows = run_seq_query(
        seq_script=seq_script,
        root=args.root,
        spec=zig_skill_spec,
        since=args.since,
        until=args.until,
    )

    implicit_intent_paths = {
        row["path"]
        for row in intent_rows
        if "path" in row
        and "text" in row
        and not is_explicit_zig_invocation(row["text"])
    }
    zig_skill_paths = {row["path"] for row in zig_rows if "path" in row}

    matched = implicit_intent_paths & zig_skill_paths
    misses = sorted(implicit_intent_paths - zig_skill_paths)

    window = f"{args.since or 'begin'} .. {args.until or 'latest'}"
    print(f"window: {window}")
    print(f"sessions_root: {args.root}")
    print(f"implicit_zig_intent_sessions: {len(implicit_intent_paths)}")
    print(f"assistant_mentioned_$zig_sessions: {len(zig_skill_paths)}")
    print(f"matched_sessions: {len(matched)}")
    print(
        "session_recall_proxy_pct: "
        f"{pct(len(matched), len(implicit_intent_paths)):.1f}"
    )
    print(
        "session_precision_proxy_pct: "
        f"{pct(len(matched), len(zig_skill_paths)):.1f}"
    )

    if args.max_misses > 0 and misses:
        print(f"miss_sample (first {min(args.max_misses, len(misses))}):")
        for path in misses[: args.max_misses]:
            print(f"- {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
