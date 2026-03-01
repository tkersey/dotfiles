#!/usr/bin/env python3
"""
Session-level proxy audit for Zig skill invocation.

This wrapper keeps Zig-trigger auditing discoverable from the zig skill while
reusing the seq mining engine.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


INTENT_TERMS = [
    "zig",
    ".zig",
    "build.zig",
    "build.zig.zon",
    "zig build",
    "zig build lint",
    "zig test",
    "zig run",
    "zig fmt",
    "zig fetch",
    "zlinter",
    "comptime",
    "@Vector",
    "std.simd",
    "std.Thread",
    "@cImport",
    "allocator",
]

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
    "mottos",
    "double diamond",
]

STRONG_IMPLICIT_CUES = [
    ".zig",
    "build.zig",
    "build.zig.zon",
    "zig build",
    "zig build lint",
    "zig test",
    "zig run",
    "zig fmt",
    "zig fetch",
    "zlinter",
    "comptime",
    "@vector",
    "std.simd",
    "std.thread",
    "thread.pool",
    "@cimport",
    "0.15.2",
]


def run_seq_query(
    seq_runner: list[str],
    root: str,
    spec: dict,
    since: str | None,
    until: str | None,
) -> list[dict]:
    cmd = [*seq_runner, "query", "--root", root, "--spec", json.dumps(spec)]
    if since:
        cmd.extend(["--since", since])
    if until:
        cmd.extend(["--until", until])

    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "seq query failed")

    rows: list[dict] = []
    since_dt = parse_ts(since)
    until_dt = parse_ts(until)
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            # Ignore non-JSON lines so script remains robust to incidental output.
            continue
        if since_dt or until_dt:
            row_ts = parse_ts(row.get("timestamp"))
            if row_ts is None:
                continue
            if since_dt and row_ts < since_dt:
                continue
            if until_dt and row_ts > until_dt:
                continue
        rows.append(row)
    return rows


def is_explicit_zig_invocation(text: str) -> bool:
    lower = text.lower()
    return "$zig" in lower or "<name>zig</name>" in lower


def is_noise_message(text: str) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in NOISE_MARKERS)


def is_low_signal_implicit(text: str, matched_term: str) -> bool:
    lower = text.lower()
    # Broad terms are noisy in orchestration-heavy prompts; require at least one
    # strong Zig cue to count toward implicit intent.
    if matched_term.lower() in {"zig", "allocator"}:
        return not any(cue in lower for cue in STRONG_IMPLICIT_CUES)
    return False


def pct(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return (numerator / denominator) * 100.0


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def resolve_seq_script() -> Path:
    # codex/skills/zig/scripts/zig_trigger_audit.py -> codex/skills/seq/scripts/seq.py
    here = Path(__file__).resolve()
    seq_script = here.parents[2] / "seq" / "scripts" / "seq.py"
    if not seq_script.exists():
        raise FileNotFoundError(f"seq script not found at: {seq_script}")
    return seq_script


def resolve_seq_runner(seq_script: Path) -> list[str]:
    seq_bin = shutil.which("seq")
    if seq_bin:
        probe = subprocess.run(
            [seq_bin, "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        marker_text = f"{probe.stdout}\n{probe.stderr}"
        if probe.returncode == 0 and "skills-rank" in marker_text:
            return [seq_bin]
    return [sys.executable, str(seq_script)]


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
    parser.add_argument(
        "--strict-implicit",
        action="store_true",
        help=(
            "Require strong Zig cues for implicit intent; low-signal matches "
            "(for example bare 'zig'/'allocator') are filtered out."
        ),
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output file path; defaults to stdout.",
    )
    return parser


def sample_entries(
    paths: set[str],
    sample_type: str,
    reason: str,
    limit: int,
) -> list[dict[str, str]]:
    if limit <= 0:
        return []
    return [
        {"path": path, "type": sample_type, "reason": reason}
        for path in sorted(paths)[:limit]
    ]


def build_report(args: argparse.Namespace, intent_rows: list[dict], zig_rows: list[dict]) -> dict:
    path_state: dict[str, dict[str, bool]] = {}
    for row in intent_rows:
        path = row.get("path")
        text = row.get("text")
        if not path or not text:
            continue

        state = path_state.setdefault(
            path,
            {
                "explicit": False,
                "implicit_raw": False,
                "has_noise": False,
                "has_low_signal": False,
                "has_clean_implicit": False,
            },
        )

        if is_explicit_zig_invocation(text):
            state["explicit"] = True
            continue

        state["implicit_raw"] = True
        if is_noise_message(text):
            state["has_noise"] = True
            continue

        matched_term = str(row.get("_matched_term", ""))
        if is_low_signal_implicit(text, matched_term):
            state["has_low_signal"] = True
            continue

        state["has_clean_implicit"] = True

    explicit_intent_paths: set[str] = set()
    implicit_raw_paths: set[str] = set()
    implicit_noise_paths: set[str] = set()
    implicit_low_signal_paths: set[str] = set()
    implicit_clean_paths: set[str] = set()

    for path, state in path_state.items():
        if state["explicit"]:
            explicit_intent_paths.add(path)
            continue
        if not state["implicit_raw"]:
            continue
        implicit_raw_paths.add(path)
        if state["has_clean_implicit"]:
            implicit_clean_paths.add(path)
        elif state["has_low_signal"]:
            implicit_low_signal_paths.add(path)
        else:
            implicit_noise_paths.add(path)

    strict_filtered_paths = implicit_low_signal_paths if args.strict_implicit else set()
    implicit_intent_paths = (
        implicit_clean_paths
        if args.strict_implicit
        else implicit_clean_paths | implicit_low_signal_paths
    )
    implicit_low_signal_included_paths = (
        set() if args.strict_implicit else set(implicit_low_signal_paths)
    )

    zig_skill_paths = {row["path"] for row in zig_rows if "path" in row}

    matched_explicit = explicit_intent_paths & zig_skill_paths
    matched_implicit = implicit_intent_paths & zig_skill_paths
    matched = (explicit_intent_paths | implicit_intent_paths) & zig_skill_paths

    explicit_miss_paths = explicit_intent_paths - zig_skill_paths
    implicit_miss_paths = implicit_intent_paths - zig_skill_paths

    explicit_miss_sample = sample_entries(
        explicit_miss_paths,
        sample_type="explicit",
        reason="assistant_missing_skill",
        limit=args.max_misses,
    )
    implicit_miss_sample = sample_entries(
        implicit_miss_paths,
        sample_type="implicit",
        reason="assistant_missing_skill",
        limit=args.max_misses,
    )
    filtered_noise_sample = sample_entries(
        implicit_noise_paths,
        sample_type="implicit_filtered",
        reason="filtered_noise",
        limit=args.max_misses,
    )
    filtered_low_signal_sample = sample_entries(
        strict_filtered_paths,
        sample_type="implicit_filtered",
        reason="filtered_low_signal",
        limit=args.max_misses,
    )
    filtered_implicit_sample = filtered_noise_sample + filtered_low_signal_sample

    window = f"{args.since or 'begin'} .. {args.until or 'latest'}"
    counts = {
        "zig_intent_sessions_total": len(explicit_intent_paths) + len(implicit_intent_paths),
        "explicit_zig_intent_sessions": len(explicit_intent_paths),
        "implicit_zig_intent_sessions_raw": len(implicit_raw_paths),
        "implicit_noise_filtered_sessions": len(implicit_noise_paths),
        "implicit_low_signal_total_sessions": len(implicit_low_signal_paths),
        "implicit_low_signal_filtered_sessions": len(strict_filtered_paths),
        "implicit_low_signal_included_sessions": len(implicit_low_signal_included_paths),
        "implicit_zig_intent_sessions": len(implicit_intent_paths),
        "assistant_mentioned_$zig_sessions": len(zig_skill_paths),
        "matched_sessions": len(matched),
        "matched_explicit_sessions": len(matched_explicit),
        "matched_implicit_sessions": len(matched_implicit),
    }
    rates = {
        "session_recall_proxy_pct": pct(
            len(matched),
            len(explicit_intent_paths) + len(implicit_intent_paths),
        ),
        "session_precision_proxy_pct": pct(len(matched), len(zig_skill_paths)),
        "explicit_session_recall_proxy_pct": pct(
            len(matched_explicit),
            len(explicit_intent_paths),
        ),
        "explicit_session_precision_proxy_pct": pct(
            len(matched_explicit),
            len(zig_skill_paths),
        ),
        "implicit_session_recall_proxy_pct": pct(
            len(matched_implicit),
            len(implicit_intent_paths),
        ),
        "implicit_session_precision_proxy_pct": pct(
            len(matched_implicit),
            len(zig_skill_paths),
        ),
    }

    return {
        "window": window,
        "sessions_root": args.root,
        "flags": {
            "strict_implicit": bool(args.strict_implicit),
            "format": args.format,
        },
        "counts": counts,
        "rates": rates,
        "samples": {
            "explicit_miss_sample": explicit_miss_sample,
            "implicit_miss_sample": implicit_miss_sample,
            "filtered_implicit_sample": filtered_implicit_sample,
            "filtered_noise_sample": filtered_noise_sample,
            "filtered_low_signal_sample": filtered_low_signal_sample,
        },
    }


def render_text_report(report: dict) -> str:
    counts = report["counts"]
    rates = report["rates"]
    lines = [
        f"window: {report['window']}",
        f"sessions_root: {report['sessions_root']}",
        f"strict_implicit_mode: {str(report['flags']['strict_implicit']).lower()}",
        f"zig_intent_sessions_total: {counts['zig_intent_sessions_total']}",
        f"explicit_zig_intent_sessions: {counts['explicit_zig_intent_sessions']}",
        f"implicit_zig_intent_sessions_raw: {counts['implicit_zig_intent_sessions_raw']}",
        f"implicit_noise_filtered_sessions: {counts['implicit_noise_filtered_sessions']}",
        f"implicit_low_signal_total_sessions: {counts['implicit_low_signal_total_sessions']}",
        f"implicit_low_signal_filtered_sessions: {counts['implicit_low_signal_filtered_sessions']}",
        f"implicit_low_signal_included_sessions: {counts['implicit_low_signal_included_sessions']}",
        f"implicit_zig_intent_sessions: {counts['implicit_zig_intent_sessions']}",
        f"assistant_mentioned_$zig_sessions: {counts['assistant_mentioned_$zig_sessions']}",
        f"matched_sessions: {counts['matched_sessions']}",
        f"matched_explicit_sessions: {counts['matched_explicit_sessions']}",
        f"matched_implicit_sessions: {counts['matched_implicit_sessions']}",
        f"session_recall_proxy_pct: {rates['session_recall_proxy_pct']:.1f}",
        f"session_precision_proxy_pct: {rates['session_precision_proxy_pct']:.1f}",
        f"explicit_session_recall_proxy_pct: {rates['explicit_session_recall_proxy_pct']:.1f}",
        f"explicit_session_precision_proxy_pct: {rates['explicit_session_precision_proxy_pct']:.1f}",
        f"implicit_session_recall_proxy_pct: {rates['implicit_session_recall_proxy_pct']:.1f}",
        f"implicit_session_precision_proxy_pct: {rates['implicit_session_precision_proxy_pct']:.1f}",
    ]

    explicit_miss_sample = report["samples"]["explicit_miss_sample"]
    if explicit_miss_sample:
        lines.append(f"explicit_miss_sample (first {len(explicit_miss_sample)}):")
        for entry in explicit_miss_sample:
            lines.append(
                f"- {entry['path']} [type={entry['type']}, reason={entry['reason']}]"
            )

    implicit_miss_sample = report["samples"]["implicit_miss_sample"]
    if implicit_miss_sample:
        lines.append(f"miss_sample (first {len(implicit_miss_sample)}):")
        for entry in implicit_miss_sample:
            lines.append(
                f"- {entry['path']} [type={entry['type']}, reason={entry['reason']}]"
            )

    filtered_implicit_sample = report["samples"]["filtered_implicit_sample"]
    if filtered_implicit_sample:
        lines.append(
            "filtered_implicit_sample "
            f"(first {len(filtered_implicit_sample)}):"
        )
        for entry in filtered_implicit_sample:
            lines.append(
                f"- {entry['path']} [type={entry['type']}, reason={entry['reason']}]"
            )

    return "\n".join(lines) + "\n"


def emit_report(report: dict, fmt: str, output: str | None) -> None:
    if fmt == "json":
        payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    else:
        payload = render_text_report(report)

    if output:
        output_path = Path(output).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)


def main() -> int:
    args = build_parser().parse_args()
    seq_script = resolve_seq_script()
    seq_runner = resolve_seq_runner(seq_script)

    # Use literal contains matching instead of regex. The seq regex engine is a
    # restricted subset that rejects punctuation-heavy literals (for example
    # ".zig" / "build.zig"), which breaks this audit path.
    intent_specs = [
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
        }
        for term in INTENT_TERMS
    ]
    zig_skill_spec = {
        "dataset": "skill_mentions",
        "where": [
            {"field": "role", "op": "eq", "value": "assistant"},
            {"field": "skill", "op": "eq", "value": "zig"},
        ],
        "select": ["path", "timestamp"],
        "format": "jsonl",
    }

    intent_rows: list[dict] = []
    for term, intent_spec in zip(INTENT_TERMS, intent_specs):
        rows = run_seq_query(
            seq_runner=seq_runner,
            root=args.root,
            spec=intent_spec,
            since=args.since,
            until=args.until,
        )
        for row in rows:
            row["_matched_term"] = term
            intent_rows.append(row)
    zig_rows = run_seq_query(
        seq_runner=seq_runner,
        root=args.root,
        spec=zig_skill_spec,
        since=args.since,
        until=args.until,
    )

    report = build_report(args, intent_rows, zig_rows)
    emit_report(report, fmt=args.format, output=args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
