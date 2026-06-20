#!/usr/bin/env python3
"""Audit $zig activation and semantic-family opportunities in Codex sessions."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

BASE_INTENT_TERMS = [
    "zig",
    ".zig",
    "build.zig",
    "build.zig.zon",
    "zig build",
    "zig test",
    "zig run",
    "zig fmt",
    "zig fetch",
    "zlinter",
    "comptime",
    "@Vector",
    "std.Io",
    "std.testing.Smith",
    "@cImport",
    "extern fn",
    "linkSystemLibrary",
    "std.atomic",
    "compareExchange",
]

STRONG_ZIG_CUES = [
    ".zig",
    "build.zig",
    "build.zig.zon",
    "zig build",
    "zig test",
    "zig run",
    "zig fmt",
    "zig fetch",
    "zlinter",
    "comptime",
    "@vector",
    "std.io",
    "std.testing.smith",
    "@cimport",
    "extern fn",
    "linksystemlibrary",
    "std.atomic",
    "compareexchange",
    "zig 0.16",
]

FAMILY_TERMS = {
    "claim-binding": [
        "fingerprint",
        "receipt",
        "certificate",
        "cursor",
        "checkpoint",
        "replay",
        "attestation",
        "evidence ref",
        "passed()",
        "verify()",
    ],
    "lifetime-escape": [
        "arena",
        "parsed json",
        "decoded bytes",
        "returned slice",
        "snapshot",
        "report",
        "deinit",
        "reallocate",
    ],
    "atomic-transition": [
        "rollback",
        "append",
        "commit",
        "stage",
        "ownership transfer",
        "ledger",
        "journal",
        "outbox",
        "event pair",
    ],
    "verifier-completeness": [
        "parser",
        "decoder",
        "verifier",
        "inspector",
        "wasm",
        "opcode",
        "section",
        "leb",
        "metadata",
        "stack result",
    ],
    "repo-closure": [
        "golden",
        "expected output",
        "compile-fail",
        "path registry",
        "generated artifact",
        "source manifest",
    ],
    "proof-context": [
        "stale proof",
        "wrong head",
        "dirty tree",
        "after push",
        "after commit",
        "fork override",
        "cache permission",
        "permissiondenied",
    ],
}

NOISE_MARKERS = [
    "<skill>",
    "<environment_context>",
    "<instructions>",
    "# agents.md instructions",
    "automatic orchestration policy",
    "### available skills",
    "how to use skills",
    "repository guidelines",
    "tooling standards",
    "--- project-doc ---",
]


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def pct(numerator: int, denominator: int) -> float:
    return (numerator / denominator * 100.0) if denominator else 0.0


def resolve_seq_runner() -> list[str]:
    seq_bin = shutil.which("seq")
    if not seq_bin:
        raise FileNotFoundError("seq binary not found; install the intended tkersey/tap/seq binary")
    probe = subprocess.run([seq_bin, "--help"], text=True, capture_output=True, check=False)
    marker = probe.stdout + "\n" + probe.stderr
    if probe.returncode != 0 or "skills-rank" not in marker:
        raise RuntimeError("incompatible seq binary in PATH")
    return [seq_bin]


def run_seq_query(
    seq_runner: list[str],
    root: str,
    spec: dict[str, Any],
    since: str | None,
    until: str | None,
) -> list[dict[str, Any]]:
    command = [*seq_runner, "query", "--root", root, "--spec", json.dumps(spec)]
    if since:
        command.extend(["--since", since])
    if until:
        command.extend(["--until", until])
    proc = subprocess.run(command, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "seq query failed")

    since_dt = parse_ts(since)
    until_dt = parse_ts(until)
    rows = []
    for line in proc.stdout.splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        timestamp = parse_ts(row.get("timestamp"))
        if since_dt and (timestamp is None or timestamp < since_dt):
            continue
        if until_dt and (timestamp is None or timestamp > until_dt):
            continue
        rows.append(row)
    return rows


def query_messages(
    seq_runner: list[str],
    root: str,
    term: str,
    since: str | None,
    until: str | None,
) -> list[dict[str, Any]]:
    return run_seq_query(
        seq_runner,
        root,
        {
            "dataset": "messages",
            "where": [
                {"field": "role", "op": "eq", "value": "user"},
                {
                    "field": "text",
                    "op": "contains",
                    "value": term,
                    "case_insensitive": True,
                },
            ],
            "select": ["path", "text", "timestamp"],
            "format": "jsonl",
        },
        since,
        until,
    )


def is_noise(text: str) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in NOISE_MARKERS)


def explicit(text: str) -> bool:
    lower = text.lower()
    return "$zig" in lower or "<name>zig</name>" in lower


def strong_context(text: str) -> bool:
    lower = text.lower()
    return any(cue in lower for cue in STRONG_ZIG_CUES)


def sample(paths: set[str], reason: str, limit: int) -> list[dict[str, str]]:
    return [{"path": path, "reason": reason} for path in sorted(paths)[: max(limit, 0)]]


def build_report(
    args: argparse.Namespace,
    base_rows: list[dict[str, Any]],
    family_rows: dict[str, list[dict[str, Any]]],
    skill_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    states: dict[str, dict[str, bool]] = {}
    for row in base_rows:
        path = row.get("path")
        text = row.get("text")
        if not isinstance(path, str) or not isinstance(text, str):
            continue
        state = states.setdefault(path, {"explicit": False, "clean": False, "noise": False, "low": False})
        if explicit(text):
            state["explicit"] = True
        elif is_noise(text):
            state["noise"] = True
        elif strong_context(text):
            state["clean"] = True
        else:
            state["low"] = True

    explicit_paths = {path for path, row in states.items() if row["explicit"]}
    clean_paths = {path for path, row in states.items() if not row["explicit"] and row["clean"]}
    low_paths = {path for path, row in states.items() if not row["explicit"] and not row["clean"] and row["low"]}
    noise_paths = {path for path, row in states.items() if not row["explicit"] and not row["clean"] and not row["low"] and row["noise"]}
    implicit_paths = clean_paths if args.strict_implicit else clean_paths | low_paths
    intent_paths = explicit_paths | implicit_paths

    zig_skill_paths = {str(row["path"]) for row in skill_rows if row.get("path")}
    matched = intent_paths & zig_skill_paths

    family_opportunities: dict[str, set[str]] = {}
    for family, rows in family_rows.items():
        paths = set()
        for row in rows:
            path = row.get("path")
            text = row.get("text")
            if not isinstance(path, str) or not isinstance(text, str) or is_noise(text):
                continue
            if path in intent_paths or strong_context(text):
                paths.add(path)
        family_opportunities[family] = paths

    family_counts = {
        family: {
            "opportunity_sessions": len(paths),
            "zig_activated_sessions": len(paths & zig_skill_paths),
            "activation_rate_pct": pct(len(paths & zig_skill_paths), len(paths)),
        }
        for family, paths in family_opportunities.items()
    }

    counts = {
        "zig_intent_sessions_total": len(intent_paths),
        "explicit_zig_intent_sessions": len(explicit_paths),
        "implicit_zig_intent_sessions": len(implicit_paths),
        "implicit_noise_filtered_sessions": len(noise_paths),
        "implicit_low_signal_total_sessions": len(low_paths),
        "implicit_low_signal_filtered_sessions": len(low_paths) if args.strict_implicit else 0,
        "assistant_mentioned_$zig_sessions": len(zig_skill_paths),
        "matched_sessions": len(matched),
        "matched_explicit_sessions": len(explicit_paths & zig_skill_paths),
        "matched_implicit_sessions": len(implicit_paths & zig_skill_paths),
    }
    rates = {
        "session_recall_proxy_pct": pct(len(matched), len(intent_paths)),
        "session_precision_proxy_pct": pct(len(matched), len(zig_skill_paths)),
        "explicit_session_recall_proxy_pct": pct(
            len(explicit_paths & zig_skill_paths), len(explicit_paths)
        ),
        "implicit_session_recall_proxy_pct": pct(
            len(implicit_paths & zig_skill_paths), len(implicit_paths)
        ),
    }

    return {
        "window": f"{args.since or 'begin'} .. {args.until or 'latest'}",
        "sessions_root": args.root,
        "flags": {"strict_implicit": bool(args.strict_implicit)},
        "counts": counts,
        "rates": rates,
        "semantic_families": family_counts,
        "samples": {
            "explicit_miss_sample": sample(explicit_paths - zig_skill_paths, "assistant_missing_skill", args.max_misses),
            "implicit_miss_sample": sample(implicit_paths - zig_skill_paths, "assistant_missing_skill", args.max_misses),
            "filtered_noise_sample": sample(noise_paths, "filtered_noise", args.max_misses),
            "filtered_low_signal_sample": sample(
                low_paths if args.strict_implicit else set(),
                "filtered_low_signal",
                args.max_misses,
            ),
        },
    }


def render_text(report: dict[str, Any]) -> str:
    lines = [
        f"window: {report['window']}",
        f"sessions_root: {report['sessions_root']}",
        f"strict_implicit_mode: {str(report['flags']['strict_implicit']).lower()}",
    ]
    for key, value in report["counts"].items():
        lines.append(f"{key}: {value}")
    for key, value in report["rates"].items():
        lines.append(f"{key}: {value:.1f}")
    lines.append("semantic_families:")
    for family, row in sorted(report["semantic_families"].items()):
        lines.append(
            f"  {family}: opportunities={row['opportunity_sessions']} "
            f"activated={row['zig_activated_sessions']} "
            f"rate={row['activation_rate_pct']:.1f}"
        )
    for label, rows in report["samples"].items():
        if rows:
            lines.append(f"{label}:")
            for row in rows:
                lines.append(f"- {row['path']} [reason={row['reason']}]")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path.home() / ".codex" / "sessions"))
    parser.add_argument("--since")
    parser.add_argument("--until")
    parser.add_argument("--max-misses", type=int, default=15)
    parser.add_argument("--strict-implicit", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--output")
    args = parser.parse_args()

    runner = resolve_seq_runner()

    base_rows = []
    for term in BASE_INTENT_TERMS:
        for row in query_messages(runner, args.root, term, args.since, args.until):
            row["_matched_term"] = term
            base_rows.append(row)

    family_rows = {
        family: [
            row
            for term in terms
            for row in query_messages(runner, args.root, term, args.since, args.until)
        ]
        for family, terms in FAMILY_TERMS.items()
    }

    skill_rows = run_seq_query(
        runner,
        args.root,
        {
            "dataset": "skill_mentions",
            "where": [
                {"field": "role", "op": "eq", "value": "assistant"},
                {"field": "skill", "op": "eq", "value": "zig"},
            ],
            "select": ["path", "timestamp"],
            "format": "jsonl",
        },
        args.since,
        args.until,
    )

    report = build_report(args, base_rows, family_rows, skill_rows)
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n" if args.format == "json" else render_text(report)
    if args.output:
        path = Path(args.output).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
