#!/usr/bin/env uv run python
"""Session miner for Codex JSONL sessions."""

from __future__ import annotations

import argparse
import io
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator, Optional

SKILL_NAME_RE = re.compile(r"<name>([^<]+)</name>")
DOLLAR_RE = re.compile(r"\$([a-z][a-z0-9-]*)")
TOKEN_RE = re.compile(r"Original token count:\s*(\d+)")


@dataclass
class Message:
    path: Path
    timestamp: Optional[datetime]
    role: str
    text: str


def parse_ts(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def message_text(payload: dict) -> str:
    parts = []
    for part in payload.get("content", []):
        if part.get("type") in ("input_text", "output_text"):
            parts.append(part.get("text", ""))
    return "".join(parts)


def strip_echo(text: str) -> str:
    lines = text.splitlines()
    i = 0
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i < len(lines) and lines[i].startswith("Echo:"):
        i += 1
        if i < len(lines) and lines[i].strip() == "":
            i += 1
        return "\n".join(lines[i:])
    return text


def is_meta_user_message(text: str) -> bool:
    s = text.lstrip()
    if s.startswith("# AGENTS.md instructions"):
        return True
    if s.startswith("<environment_context>"):
        return True
    if s.startswith("<INSTRUCTIONS>"):
        return True
    if "AGENTS.md instructions" in s[:200]:
        return True
    return False


def discover_sessions_root(root: Optional[str]) -> Path:
    if root:
        return Path(root).expanduser().resolve()
    candidates = [
        Path("./sessions"),
        Path.home() / ".codex" / "sessions",
        Path.home() / ".dotfiles" / "codex" / "sessions",
    ]
    for c in candidates:
        if c.exists():
            return c.resolve()
    return candidates[0].resolve()


def iter_jsonl_paths(root: Path) -> Iterator[Path]:
    return iter(sorted(root.rglob("*.jsonl")))


def iter_messages(
    root: Path,
    roles: set[str],
    since: Optional[datetime],
    until: Optional[datetime],
) -> Iterator[Message]:
    for path in iter_jsonl_paths(root):
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if obj.get("type") != "response_item":
                    continue
                payload = obj.get("payload") or {}
                if payload.get("type") != "message":
                    continue
                role = payload.get("role")
                if role not in roles:
                    continue
                text = message_text(payload)
                if not text:
                    continue
                if role == "user" and is_meta_user_message(text):
                    continue
                if role == "assistant":
                    text = strip_echo(text)
                if not text:
                    continue
                ts = parse_ts(obj.get("timestamp"))
                if since and ts and ts < since:
                    continue
                if until and ts and ts > until:
                    continue
                yield Message(path=path, timestamp=ts, role=role, text=text)


def skill_blocks(text: str) -> list[str]:
    if "<skill>" not in text:
        return []
    return [m.group(1).strip() for m in SKILL_NAME_RE.finditer(text) if m.group(1).strip()]


def dollar_skills(text: str) -> list[str]:
    return [m.group(1) for m in DOLLAR_RE.finditer(text)]


def load_skill_names(skill_dirs: list[Path]) -> set[str]:
    names: set[str] = set()
    for d in skill_dirs:
        if not d.exists():
            continue
        for entry in d.iterdir():
            if entry.is_dir():
                names.add(entry.name)
    return names


def collect_occurrences(
    root: Path,
    roles: set[str],
    skill_names: Optional[set[str]],
    include_blocks: bool,
    include_dollars: bool,
    skip_dollar_in_skill_block: bool,
    dedupe_adjacent: bool,
    since: Optional[datetime],
    until: Optional[datetime],
) -> list[dict]:
    occ: list[dict] = []
    for path in iter_jsonl_paths(root):
        prev_types_by_skill: dict[str, set[str]] = {}
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if obj.get("type") != "response_item":
                    continue
                payload = obj.get("payload") or {}
                if payload.get("type") != "message":
                    continue
                role = payload.get("role")
                if role not in roles:
                    continue
                text = message_text(payload)
                if not text:
                    continue
                if role == "user" and is_meta_user_message(text):
                    continue
                if role == "assistant":
                    text = strip_echo(text)
                if not text:
                    continue
                ts = parse_ts(obj.get("timestamp"))
                if since and ts and ts < since:
                    continue
                if until and ts and ts > until:
                    continue

                block_names = skill_blocks(text) if include_blocks else []
                has_any_block = bool(block_names)

                types_by_skill: dict[str, set[str]] = defaultdict(set)
                if include_blocks:
                    for name in block_names:
                        types_by_skill[name].add("block")

                if include_dollars and not (skip_dollar_in_skill_block and has_any_block):
                    for name in dollar_skills(text):
                        if skill_names is None or name in skill_names:
                            types_by_skill[name].add("dollar")

                for name, types in types_by_skill.items():
                    prev_types = prev_types_by_skill.get(name, set())
                    if dedupe_adjacent:
                        if "block" in prev_types and "dollar" in types and "block" not in types:
                            continue
                        if "dollar" in prev_types and "block" in types and "dollar" not in types:
                            continue
                    occ.append(
                        {
                            "skill": name,
                            "role": role,
                            "types": "+".join(sorted(types)),
                            "timestamp": obj.get("timestamp"),
                            "path": str(path),
                            "snippet": text.replace("\n", " ")[:240],
                        }
                    )

                prev_types_by_skill = types_by_skill
    return occ


def format_table(rows: list[tuple[str, int]]) -> str:
    if not rows:
        return "(no results)"
    width_skill = max(len(r[0]) for r in rows)
    width_count = max(len(str(r[1])) for r in rows)
    lines = []
    lines.append(f"{'Skill'.ljust(width_skill)}  {'Count'.rjust(width_count)}")
    lines.append(f"{'-'*width_skill}  {'-'*width_count}")
    for skill, count in rows:
        lines.append(f"{skill.ljust(width_skill)}  {str(count).rjust(width_count)}")
    return "\n".join(lines)


def format_role_table(rows: list[dict]) -> str:
    if not rows:
        return "(no results)"
    width_skill = max(len(r["skill"]) for r in rows)
    width_user = max(len(str(r["user"])) for r in rows)
    width_asst = max(len(str(r["assistant"])) for r in rows)
    width_total = max(len(str(r["total"])) for r in rows)
    lines = []
    lines.append(
        f"{'Skill'.ljust(width_skill)}  {'User'.rjust(width_user)}  "
        f"{'Asst'.rjust(width_asst)}  {'Total'.rjust(width_total)}"
    )
    lines.append(
        f"{'-'*width_skill}  {'-'*width_user}  {'-'*width_asst}  {'-'*width_total}"
    )
    for r in rows:
        lines.append(
            f"{r['skill'].ljust(width_skill)}  {str(r['user']).rjust(width_user)}  "
            f"{str(r['assistant']).rjust(width_asst)}  {str(r['total']).rjust(width_total)}"
        )
    return "\n".join(lines)


def bucket_start(ts: datetime, bucket: str) -> datetime:
    if bucket == "day":
        return datetime(ts.year, ts.month, ts.day, tzinfo=ts.tzinfo)
    if bucket == "week":
        iso = ts.isocalendar()
        # Monday of the ISO week
        return datetime.fromisocalendar(iso.year, iso.week, 1).replace(tzinfo=ts.tzinfo)
    # month
    return datetime(ts.year, ts.month, 1, tzinfo=ts.tzinfo)


def bucket_label(ts: datetime, bucket: str) -> str:
    if bucket == "day":
        return ts.date().isoformat()
    if bucket == "week":
        iso = ts.isocalendar()
        return f"{iso.year}-W{iso.week:02d}"
    return f"{ts.year}-{ts.month:02d}"


def cmd_skills_rank(args: argparse.Namespace) -> str:
    root = discover_sessions_root(args.root)
    roles = set(r.strip() for r in args.roles.split(",") if r.strip())
    since = parse_ts(args.since) if args.since else None
    until = parse_ts(args.until) if args.until else None

    skill_dirs = [Path(p).expanduser() for p in args.skills_dir]
    skill_names = load_skill_names(skill_dirs)
    if args.skill and args.skill not in skill_names:
        skill_names.add(args.skill)

    occ = collect_occurrences(
        root=root,
        roles=roles,
        skill_names=skill_names,
        include_blocks=not args.no_blocks,
        include_dollars=not args.no_dollars,
        skip_dollar_in_skill_block=not args.no_skip_dollar_in_block,
        dedupe_adjacent=not args.no_dedupe,
        since=since,
        until=until,
    )

    counts = Counter(o["skill"] for o in occ)
    rows = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    if args.max:
        rows = rows[: args.max]

    if args.format == "json":
        return json.dumps([{"skill": k, "count": v} for k, v in rows], indent=2)
    if args.format == "csv":
        out_lines = ["skill,count"]
        out_lines += [f"{k},{v}" for k, v in rows]
        return "\n".join(out_lines)
    return format_table(rows)


def cmd_skill_trend(args: argparse.Namespace) -> str:
    root = discover_sessions_root(args.root)
    roles = set(r.strip() for r in args.roles.split(",") if r.strip())
    since = parse_ts(args.since) if args.since else None
    until = parse_ts(args.until) if args.until else None

    skill_dirs = [Path(p).expanduser() for p in args.skills_dir]
    skill_names = load_skill_names(skill_dirs)
    if args.skill and args.skill not in skill_names:
        skill_names.add(args.skill)

    occ = collect_occurrences(
        root=root,
        roles=roles,
        skill_names=skill_names,
        include_blocks=not args.no_blocks,
        include_dollars=not args.no_dollars,
        skip_dollar_in_skill_block=not args.no_skip_dollar_in_block,
        dedupe_adjacent=not args.no_dedupe,
        since=since,
        until=until,
    )
    occ = [o for o in occ if o["skill"] == args.skill]

    buckets: dict[str, dict] = {}
    for o in occ:
        ts = parse_ts(o["timestamp"])
        if not ts:
            continue
        start = bucket_start(ts, args.bucket)
        label = bucket_label(ts, args.bucket)
        entry = buckets.get(label)
        if not entry:
            entry = {"label": label, "start": start, "count": 0}
            buckets[label] = entry
        entry["count"] += 1

    rows = sorted(buckets.values(), key=lambda r: r["start"])
    if args.max:
        rows = rows[-args.max :]

    if args.format == "json":
        return json.dumps(
            [{"bucket": r["label"], "count": r["count"]} for r in rows],
            indent=2,
        )
    if args.format == "csv":
        out_lines = ["bucket,count"]
        out_lines += [f"{r['label']},{r['count']}" for r in rows]
        return "\n".join(out_lines)
    return format_table([(r["label"], r["count"]) for r in rows])


def cmd_skill_report(args: argparse.Namespace) -> str:
    root = discover_sessions_root(args.root)
    roles = set(r.strip() for r in args.roles.split(",") if r.strip())
    since = parse_ts(args.since) if args.since else None
    until = parse_ts(args.until) if args.until else None

    skill_dirs = [Path(p).expanduser() for p in args.skills_dir]
    skill_names = load_skill_names(skill_dirs)

    occ = collect_occurrences(
        root=root,
        roles=roles,
        skill_names=skill_names,
        include_blocks=not args.no_blocks,
        include_dollars=not args.no_dollars,
        skip_dollar_in_skill_block=not args.no_skip_dollar_in_block,
        dedupe_adjacent=not args.no_dedupe,
        since=since,
        until=until,
    )

    occ = [o for o in occ if o["skill"] == args.skill]

    counts = Counter(o["role"] for o in occ)
    type_counts = Counter(o["types"] for o in occ)

    lines = []
    lines.append(f"Skill: {args.skill}")
    lines.append(f"Total occurrences: {len(occ)}")
    lines.append(f"By role: {dict(counts)}")
    lines.append(f"By type: {dict(type_counts)}")

    if args.sections:
        sections = [s.strip() for s in args.sections.split(",") if s.strip()]
        missing = Counter()
        total = 0
        samples = []
        for msg in iter_messages(root, roles={"assistant"}, since=since, until=until):
            if args.skill not in msg.text:
                continue
            total += 1
            for s in sections:
                if s not in msg.text:
                    missing[s] += 1
            if args.sample_missing and any(s not in msg.text for s in sections):
                samples.append(msg)
                if len(samples) >= args.sample_missing:
                    break
        lines.append("Section audit:")
        lines.append(f"  Messages scanned: {total}")
        for s in sections:
            lines.append(f"  Missing {s}: {missing[s]}")
        if samples:
            lines.append("Sample missing:")
            for msg in samples:
                snippet = msg.text.replace("\n", " ")[:200]
                lines.append(f"  - {msg.path} {msg.timestamp} {snippet}")

    if args.snippets:
        lines.append("Samples:")
        for o in occ[: args.snippets]:
            lines.append(f"- {o['timestamp']} {o['role']} {o['path']} {o['snippet']}")

    return "\n".join(lines)


def cmd_role_breakdown(args: argparse.Namespace) -> str:
    root = discover_sessions_root(args.root)
    roles = set(r.strip() for r in args.roles.split(",") if r.strip())
    since = parse_ts(args.since) if args.since else None
    until = parse_ts(args.until) if args.until else None

    skill_dirs = [Path(p).expanduser() for p in args.skills_dir]
    skill_names = load_skill_names(skill_dirs)

    occ = collect_occurrences(
        root=root,
        roles=roles,
        skill_names=skill_names,
        include_blocks=not args.no_blocks,
        include_dollars=not args.no_dollars,
        skip_dollar_in_skill_block=not args.no_skip_dollar_in_block,
        dedupe_adjacent=not args.no_dedupe,
        since=since,
        until=until,
    )

    counts: dict[str, dict[str, int]] = defaultdict(lambda: {"user": 0, "assistant": 0})
    for o in occ:
        counts[o["skill"]][o["role"]] += 1

    rows = []
    for skill, roles_count in counts.items():
        total = roles_count.get("user", 0) + roles_count.get("assistant", 0)
        rows.append(
            {
                "skill": skill,
                "user": roles_count.get("user", 0),
                "assistant": roles_count.get("assistant", 0),
                "total": total,
            }
        )
    rows = sorted(rows, key=lambda r: (-r["total"], r["skill"]))
    if args.max:
        rows = rows[: args.max]

    if args.format == "json":
        return json.dumps(rows, indent=2)
    if args.format == "csv":
        out_lines = ["skill,user,assistant,total"]
        out_lines += [f"{r['skill']},{r['user']},{r['assistant']},{r['total']}" for r in rows]
        return "\n".join(out_lines)
    return format_role_table(rows)


def cmd_occurrence_export(args: argparse.Namespace) -> str:
    root = discover_sessions_root(args.root)
    roles = set(r.strip() for r in args.roles.split(",") if r.strip())
    since = parse_ts(args.since) if args.since else None
    until = parse_ts(args.until) if args.until else None

    skill_dirs = [Path(p).expanduser() for p in args.skills_dir]
    skill_names = load_skill_names(skill_dirs)
    if args.skill and args.skill not in skill_names:
        skill_names.add(args.skill)

    occ = collect_occurrences(
        root=root,
        roles=roles,
        skill_names=skill_names,
        include_blocks=not args.no_blocks,
        include_dollars=not args.no_dollars,
        skip_dollar_in_skill_block=not args.no_skip_dollar_in_block,
        dedupe_adjacent=not args.no_dedupe,
        since=since,
        until=until,
    )
    if args.skill:
        occ = [o for o in occ if o["skill"] == args.skill]
    if args.max:
        occ = occ[: args.max]

    if args.format == "json":
        return json.dumps(occ, indent=2)
    if args.format == "jsonl":
        return "\n".join(json.dumps(o) for o in occ)
    # csv
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf, fieldnames=["skill", "role", "types", "timestamp", "path", "snippet"]
    )
    writer.writeheader()
    for o in occ:
        writer.writerow({k: o.get(k, "") for k in writer.fieldnames})
    return buf.getvalue().strip("\n")


def cmd_report_bundle(args: argparse.Namespace) -> str:
    root = discover_sessions_root(args.root)
    roles = set(r.strip() for r in args.roles.split(",") if r.strip())
    since = parse_ts(args.since) if args.since else None
    until = parse_ts(args.until) if args.until else None

    skill_dirs = [Path(p).expanduser() for p in args.skills_dir]
    skill_names = load_skill_names(skill_dirs)

    occ = collect_occurrences(
        root=root,
        roles=roles,
        skill_names=skill_names,
        include_blocks=not args.no_blocks,
        include_dollars=not args.no_dollars,
        skip_dollar_in_skill_block=not args.no_skip_dollar_in_block,
        dedupe_adjacent=not args.no_dedupe,
        since=since,
        until=until,
    )

    # skills rank
    rank_counts = Counter(o["skill"] for o in occ)
    rank_rows = sorted(rank_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    if args.top:
        rank_rows = rank_rows[: args.top]

    # role breakdown
    roles_count: dict[str, dict[str, int]] = defaultdict(lambda: {"user": 0, "assistant": 0})
    for o in occ:
        roles_count[o["skill"]][o["role"]] += 1
    role_rows = []
    for skill, rc in roles_count.items():
        role_rows.append(
            {
                "skill": skill,
                "user": rc.get("user", 0),
                "assistant": rc.get("assistant", 0),
                "total": rc.get("user", 0) + rc.get("assistant", 0),
            }
        )
    role_rows = sorted(role_rows, key=lambda r: (-r["total"], r["skill"]))

    # token usage summary
    token_summary = cmd_token_usage(
        argparse.Namespace(root=args.root, top=0)
    )

    bundle = {
        "skills_rank": [{"skill": k, "count": v} for k, v in rank_rows],
        "role_breakdown": role_rows,
        "token_usage": token_summary,
    }

    if args.skills and args.sections:
        sections = [s.strip() for s in args.sections.split(",") if s.strip()]
        skills = [s.strip() for s in args.skills.split(",") if s.strip()]
        audits = {}
        for skill in skills:
            total = 0
            missing = Counter()
            for msg in iter_messages(root, roles={"assistant"}, since=since, until=until):
                if skill not in msg.text:
                    continue
                total += 1
                for s in sections:
                    if s not in msg.text:
                        missing[s] += 1
            audits[skill] = {
                "messages_scanned": total,
                "missing": dict(missing),
            }
        bundle["section_audit"] = audits

    return json.dumps(bundle, indent=2)


def cmd_section_audit(args: argparse.Namespace) -> str:
    root = discover_sessions_root(args.root)
    roles = {"assistant"}
    since = parse_ts(args.since) if args.since else None
    until = parse_ts(args.until) if args.until else None

    sections = [s.strip() for s in args.sections.split(",") if s.strip()]
    total = 0
    missing = Counter()
    samples = []

    for msg in iter_messages(root, roles=roles, since=since, until=until):
        if args.contains and args.contains not in msg.text:
            continue
        total += 1
        for s in sections:
            if (s in msg.text) if not args.case_insensitive else (s.lower() in msg.text.lower()):
                continue
            missing[s] += 1
        if args.sample_missing and any(
            ((s in msg.text) if not args.case_insensitive else (s.lower() in msg.text.lower())) is False
            for s in sections
        ):
            samples.append(msg)
            if len(samples) >= args.sample_missing:
                break

    lines = []
    lines.append(f"Messages scanned: {total}")
    for s in sections:
        lines.append(f"Missing {s}: {missing[s]}")
    if samples:
        lines.append("Sample missing:")
        for msg in samples:
            snippet = msg.text.replace("\n", " ")[:200]
            lines.append(f"- {msg.path} {msg.timestamp} {snippet}")

    return "\n".join(lines)


def cmd_token_usage(args: argparse.Namespace) -> str:
    root = discover_sessions_root(args.root)
    matches = []
    for path in iter_jsonl_paths(root):
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                payload = obj.get("payload") or {}
                if obj.get("type") != "response_item":
                    continue
                if payload.get("type") != "function_call_output":
                    continue
                output = payload.get("output") or ""
                if not isinstance(output, str):
                    try:
                        output = json.dumps(output)
                    except Exception:
                        output = str(output)
                for m in TOKEN_RE.finditer(output):
                    matches.append(
                        {
                            "count": int(m.group(1)),
                            "timestamp": obj.get("timestamp"),
                            "path": str(path),
                        }
                    )

    if not matches:
        return "No token counts found."

    counts = [m["count"] for m in matches]
    total = sum(counts)
    avg = total / len(counts)
    lines = []
    lines.append(f"Entries: {len(counts)}")
    lines.append(f"Total tokens: {total}")
    lines.append(f"Average: {avg:.2f}")
    lines.append(f"Min: {min(counts)}")
    lines.append(f"Max: {max(counts)}")

    if args.top:
        top = sorted(matches, key=lambda m: m["count"], reverse=True)[: args.top]
        lines.append("Top entries:")
        for m in top:
            lines.append(f"- {m['count']} {m['timestamp']} {m['path']}")

    return "\n".join(lines)


def write_output(text: str, out_path: Optional[str]) -> None:
    if out_path:
        Path(out_path).write_text(text)
    else:
        print(text)


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root", help="sessions root (default: auto)")
    common.add_argument("--roles", default="user,assistant", help="roles to include")
    common.add_argument("--since", help="ISO timestamp (inclusive)")
    common.add_argument("--until", help="ISO timestamp (inclusive)")
    common.add_argument("--output", help="write output to file instead of stdout")
    common.add_argument(
        "--skills-dir",
        action="append",
        default=[str(Path.home() / ".dotfiles" / "codex" / "skills"), str(Path.home() / ".codex" / "skills")],
        help="skills directory (repeatable)",
    )

    p = argparse.ArgumentParser(
        prog="seq",
        description="Mine Codex sessions JSONL",
        parents=[common],
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    s_rank = sub.add_parser("skills-rank", help="rank skill usage", parents=[common])
    s_rank.add_argument("--format", choices=["table", "json", "csv"], default="table")
    s_rank.add_argument("--max", type=int, default=0, help="limit rows")
    s_rank.add_argument("--no-blocks", action="store_true", help="ignore <skill> blocks")
    s_rank.add_argument("--no-dollars", action="store_true", help="ignore $skill tokens")
    s_rank.add_argument("--no-skip-dollar-in-block", action="store_true", help="count $skill even inside <skill> blocks")
    s_rank.add_argument("--no-dedupe", action="store_true", help="disable adjacent block/dollar dedupe")
    s_rank.set_defaults(func=cmd_skills_rank)

    s_trend = sub.add_parser("skill-trend", help="time-bucketed counts for one skill", parents=[common])
    s_trend.add_argument("--skill", required=True)
    s_trend.add_argument("--bucket", choices=["day", "week", "month"], default="day")
    s_trend.add_argument("--format", choices=["table", "json", "csv"], default="table")
    s_trend.add_argument("--max", type=int, default=0, help="limit buckets (most recent)")
    s_trend.add_argument("--no-blocks", action="store_true", help="ignore <skill> blocks")
    s_trend.add_argument("--no-dollars", action="store_true", help="ignore $skill tokens")
    s_trend.add_argument("--no-skip-dollar-in-block", action="store_true", help="count $skill even inside <skill> blocks")
    s_trend.add_argument("--no-dedupe", action="store_true", help="disable adjacent block/dollar dedupe")
    s_trend.set_defaults(func=cmd_skill_trend)

    s_report = sub.add_parser("skill-report", help="report on a specific skill", parents=[common])
    s_report.add_argument("--skill", required=True)
    s_report.add_argument("--sections", help="comma-separated section labels to audit in assistant messages")
    s_report.add_argument("--sample-missing", type=int, default=0, help="sample missing messages")
    s_report.add_argument("--snippets", type=int, default=0, help="include occurrence snippets")
    s_report.add_argument("--no-blocks", action="store_true", help="ignore <skill> blocks")
    s_report.add_argument("--no-dollars", action="store_true", help="ignore $skill tokens")
    s_report.add_argument("--no-skip-dollar-in-block", action="store_true", help="count $skill even inside <skill> blocks")
    s_report.add_argument("--no-dedupe", action="store_true", help="disable adjacent block/dollar dedupe")
    s_report.set_defaults(func=cmd_skill_report)

    s_roles = sub.add_parser("role-breakdown", help="user vs assistant counts by skill", parents=[common])
    s_roles.add_argument("--format", choices=["table", "json", "csv"], default="table")
    s_roles.add_argument("--max", type=int, default=0, help="limit rows")
    s_roles.add_argument("--no-blocks", action="store_true", help="ignore <skill> blocks")
    s_roles.add_argument("--no-dollars", action="store_true", help="ignore $skill tokens")
    s_roles.add_argument("--no-skip-dollar-in-block", action="store_true", help="count $skill even inside <skill> blocks")
    s_roles.add_argument("--no-dedupe", action="store_true", help="disable adjacent block/dollar dedupe")
    s_roles.set_defaults(func=cmd_role_breakdown)

    s_export = sub.add_parser("occurrence-export", help="export occurrences", parents=[common])
    s_export.add_argument("--skill", help="filter to one skill")
    s_export.add_argument("--format", choices=["jsonl", "json", "csv"], default="jsonl")
    s_export.add_argument("--max", type=int, default=0, help="limit rows")
    s_export.add_argument("--no-blocks", action="store_true", help="ignore <skill> blocks")
    s_export.add_argument("--no-dollars", action="store_true", help="ignore $skill tokens")
    s_export.add_argument("--no-skip-dollar-in-block", action="store_true", help="count $skill even inside <skill> blocks")
    s_export.add_argument("--no-dedupe", action="store_true", help="disable adjacent block/dollar dedupe")
    s_export.set_defaults(func=cmd_occurrence_export)

    s_bundle = sub.add_parser("report-bundle", help="bundle common reports into JSON", parents=[common])
    s_bundle.add_argument("--top", type=int, default=20, help="top N skills for rank")
    s_bundle.add_argument("--skills", help="comma-separated skills for section audit")
    s_bundle.add_argument("--sections", help="comma-separated section labels for audit")
    s_bundle.add_argument("--no-blocks", action="store_true", help="ignore <skill> blocks")
    s_bundle.add_argument("--no-dollars", action="store_true", help="ignore $skill tokens")
    s_bundle.add_argument("--no-skip-dollar-in-block", action="store_true", help="count $skill even inside <skill> blocks")
    s_bundle.add_argument("--no-dedupe", action="store_true", help="disable adjacent block/dollar dedupe")
    s_bundle.set_defaults(func=cmd_report_bundle)

    s_audit = sub.add_parser("section-audit", help="audit section presence in assistant messages", parents=[common])
    s_audit.add_argument("--sections", required=True, help="comma-separated section labels")
    s_audit.add_argument("--contains", help="only scan messages containing this substring")
    s_audit.add_argument("--case-insensitive", action="store_true")
    s_audit.add_argument("--sample-missing", type=int, default=0)
    s_audit.set_defaults(func=cmd_section_audit)

    s_tokens = sub.add_parser("token-usage", help="summarize token counts from tool outputs", parents=[common])
    s_tokens.add_argument("--top", type=int, default=0, help="show top N")
    s_tokens.set_defaults(func=cmd_token_usage)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    output = args.func(args)
    if isinstance(output, str):
        write_output(output, getattr(args, "output", None))
    else:
        print(output)


if __name__ == "__main__":
    main()
