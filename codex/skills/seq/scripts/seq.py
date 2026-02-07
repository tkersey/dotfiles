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
import hashlib
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Optional

SKILL_NAME_RE = re.compile(r"<name>([^<]+)</name>")
DOLLAR_RE = re.compile(r"\$([a-z][a-z0-9-]*)")
TOKEN_RE = re.compile(r"Original token count:\s*(\d+)")
RESPONSE_ITEM_MESSAGE_TYPE_RE = re.compile(r'"type"\s*:\s*"message"')
DEFAULT_SESSIONS_ROOT = Path.home() / ".codex" / "sessions"


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
    return DEFAULT_SESSIONS_ROOT.resolve()


def iter_jsonl_paths(root: Path) -> Iterator[Path]:
    return iter(sorted(root.rglob("*.jsonl")))


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    return text.strip()


def msg_fingerprint(role: str, text: str) -> bytes:
    h = hashlib.blake2b(digest_size=16)
    h.update(role.encode("utf-8", errors="ignore"))
    h.update(b"\0")
    h.update(text.encode("utf-8", errors="ignore"))
    return h.digest()


def iter_messages_in_path(
    path: Path,
    roles: set[str],
    since: Optional[datetime],
    until: Optional[datetime],
    *,
    dedupe: bool = True,
    strip_echo_assistant: bool = True,
) -> Iterator[Message]:
    seen: set[bytes] = set()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            # Fast prefilter: only parse JSON lines that can contain message payloads.
            if "event_msg" in line:
                if "user_message" not in line and "agent_message" not in line:
                    continue
            elif "response_item" in line:
                if not RESPONSE_ITEM_MESSAGE_TYPE_RE.search(line):
                    continue
            else:
                continue

            try:
                obj = json.loads(line)
            except Exception:
                continue

            payload = obj.get("payload") or {}
            otype = obj.get("type")
            ptype = payload.get("type")

            role: Optional[str] = None
            text: str = ""

            if otype == "response_item" and ptype == "message":
                role = payload.get("role")
                text = message_text(payload)
            elif otype == "event_msg" and ptype == "user_message":
                role = "user"
                text = payload.get("message") or ""
            elif otype == "event_msg" and ptype == "agent_message":
                role = "assistant"
                text = payload.get("message") or ""

            if role is None or role not in roles:
                continue
            if not isinstance(text, str) or not text:
                continue
            if role == "user" and is_meta_user_message(text):
                continue
            if role == "assistant" and strip_echo_assistant:
                text = strip_echo(text)

            text = normalize_text(text)
            if not text:
                continue

            ts = parse_ts(obj.get("timestamp"))
            if since and ts and ts < since:
                continue
            if until and ts and ts > until:
                continue

            if dedupe:
                fp = msg_fingerprint(role, text)
                if fp in seen:
                    continue
                seen.add(fp)

            yield Message(path=path, timestamp=ts, role=role, text=text)


def iter_messages(
    root: Path,
    roles: set[str],
    since: Optional[datetime],
    until: Optional[datetime],
) -> Iterator[Message]:
    for path in iter_jsonl_paths(root):
        yield from iter_messages_in_path(
            path,
            roles=roles,
            since=since,
            until=until,
            dedupe=True,
            strip_echo_assistant=True,
        )


def skill_blocks(text: str) -> list[str]:
    if "<skill>" not in text:
        return []
    return [
        m.group(1).strip() for m in SKILL_NAME_RE.finditer(text) if m.group(1).strip()
    ]


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
    return list(
        iter_occurrences(
            root=root,
            roles=roles,
            skill_names=skill_names,
            include_blocks=include_blocks,
            include_dollars=include_dollars,
            skip_dollar_in_skill_block=skip_dollar_in_skill_block,
            dedupe_adjacent=dedupe_adjacent,
            since=since,
            until=until,
        )
    )


def iter_occurrences(
    root: Path,
    roles: set[str],
    skill_names: Optional[set[str]],
    include_blocks: bool,
    include_dollars: bool,
    skip_dollar_in_skill_block: bool,
    dedupe_adjacent: bool,
    since: Optional[datetime],
    until: Optional[datetime],
) -> Iterator[dict]:
    for path in iter_jsonl_paths(root):
        prev_types_by_skill: dict[str, set[str]] = {}
        for msg in iter_messages_in_path(
            path,
            roles=roles,
            since=since,
            until=until,
            dedupe=True,
            strip_echo_assistant=True,
        ):
            text = msg.text
            role = msg.role
            ts = msg.timestamp

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
                    if (
                        "block" in prev_types
                        and "dollar" in types
                        and "block" not in types
                    ):
                        continue
                    if (
                        "dollar" in prev_types
                        and "block" in types
                        and "dollar" not in types
                    ):
                        continue
                yield {
                    "skill": name,
                    "role": role,
                    "types": "+".join(sorted(types)),
                    "timestamp": ts.isoformat() if ts else None,
                    "path": str(path),
                    "snippet": text.replace("\n", " ")[:240],
                    "day": bucket_label(ts, "day") if ts else None,
                    "week": bucket_label(ts, "week") if ts else None,
                    "month": bucket_label(ts, "month") if ts else None,
                }

            prev_types_by_skill = types_by_skill


def format_table(rows: list[tuple[str, int]]) -> str:
    if not rows:
        return "(no results)"
    width_skill = max(len(r[0]) for r in rows)
    width_count = max(len(str(r[1])) for r in rows)
    lines = []
    lines.append(f"{'Skill'.ljust(width_skill)}  {'Count'.rjust(width_count)}")
    lines.append(f"{'-' * width_skill}  {'-' * width_count}")
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
        f"{'-' * width_skill}  {'-' * width_user}  {'-' * width_asst}  {'-' * width_total}"
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
                if len(samples) < args.sample_missing:
                    samples.append(msg)
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
        out_lines += [
            f"{r['skill']},{r['user']},{r['assistant']},{r['total']}" for r in rows
        ]
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
    roles_count: dict[str, dict[str, int]] = defaultdict(
        lambda: {"user": 0, "assistant": 0}
    )
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
    token_summary = cmd_token_usage(argparse.Namespace(root=args.root, top=0))

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
            for msg in iter_messages(
                root, roles={"assistant"}, since=since, until=until
            ):
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
            if (
                (s in msg.text)
                if not args.case_insensitive
                else (s.lower() in msg.text.lower())
            ):
                continue
            missing[s] += 1
        if args.sample_missing and any(
            (
                (s in msg.text)
                if not args.case_insensitive
                else (s.lower() in msg.text.lower())
            )
            is False
            for s in sections
        ):
            if len(samples) < args.sample_missing:
                samples.append(msg)

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


@dataclass(frozen=True)
class DatasetDef:
    name: str
    description: str
    fields: list[str]
    default_params: dict[str, Any]
    params_help: dict[str, str]
    iter_rows: Callable[
        [Path, argparse.Namespace, dict[str, Any]], Iterator[dict[str, Any]]
    ]


def dataset_messages(
    root: Path, args: argparse.Namespace, params: dict[str, Any]
) -> Iterator[dict[str, Any]]:
    roles = set(r.strip() for r in args.roles.split(",") if r.strip())
    since = parse_ts(args.since) if args.since else None
    until = parse_ts(args.until) if args.until else None
    for msg in iter_messages(root, roles=roles, since=since, until=until):
        ts = msg.timestamp
        yield {
            "path": str(msg.path),
            "timestamp": ts.isoformat() if ts else None,
            "day": bucket_label(ts, "day") if ts else None,
            "week": bucket_label(ts, "week") if ts else None,
            "month": bucket_label(ts, "month") if ts else None,
            "role": msg.role,
            "text": msg.text,
            "text_len": len(msg.text),
        }


def dataset_skill_mentions(
    root: Path, args: argparse.Namespace, params: dict[str, Any]
) -> Iterator[dict[str, Any]]:
    roles = set(r.strip() for r in args.roles.split(",") if r.strip())
    since = parse_ts(args.since) if args.since else None
    until = parse_ts(args.until) if args.until else None

    skill_dirs = [Path(p).expanduser() for p in args.skills_dir]
    skill_names = load_skill_names(skill_dirs)

    include_blocks = bool(params.get("include_blocks", True))
    include_dollars = bool(params.get("include_dollars", True))
    skip_dollar_in_skill_block = bool(params.get("skip_dollar_in_skill_block", True))
    dedupe_adjacent = bool(params.get("dedupe_adjacent", True))

    for o in iter_occurrences(
        root=root,
        roles=roles,
        skill_names=skill_names,
        include_blocks=include_blocks,
        include_dollars=include_dollars,
        skip_dollar_in_skill_block=skip_dollar_in_skill_block,
        dedupe_adjacent=dedupe_adjacent,
        since=since,
        until=until,
    ):
        yield o


TOKEN_KEYS = [
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_tokens",
]


def token_usage(info: dict[str, Any], which: str) -> dict[str, int]:
    block = info.get(which)
    if not isinstance(block, dict):
        return {}
    out: dict[str, int] = {}
    for k in TOKEN_KEYS:
        v = block.get(k)
        if isinstance(v, int):
            out[k] = v
    return out


def iter_token_count_events_in_path(
    path: Path,
    since: Optional[datetime],
    until: Optional[datetime],
) -> Iterator[tuple[Optional[datetime], dict[str, Any]]]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            # Fast prefilter: token counts only appear on event_msg rows.
            if "event_msg" not in line or "token_count" not in line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if obj.get("type") != "event_msg":
                continue
            payload = obj.get("payload") or {}
            if payload.get("type") != "token_count":
                continue
            info = payload.get("info")
            if not isinstance(info, dict):
                continue
            ts = parse_ts(obj.get("timestamp"))
            if since and ts and ts < since:
                continue
            if until and ts and ts > until:
                continue
            yield (ts, info)


def dataset_token_events(
    root: Path, args: argparse.Namespace, params: dict[str, Any]
) -> Iterator[dict[str, Any]]:
    since = parse_ts(args.since) if args.since else None
    until = parse_ts(args.until) if args.until else None
    dedupe = bool(params.get("dedupe", True))

    for path in iter_jsonl_paths(root):
        prev_total: Optional[int] = None
        for ts, info in iter_token_count_events_in_path(path, since=since, until=until):
            total = token_usage(info, "total_token_usage")
            last = token_usage(info, "last_token_usage")
            total_total = total.get("total_tokens")
            if (
                dedupe
                and prev_total is not None
                and total_total is not None
                and total_total == prev_total
            ):
                continue
            if total_total is not None:
                prev_total = total_total

            row: dict[str, Any] = {
                "path": str(path),
                "timestamp": ts.isoformat() if ts else None,
                "day": bucket_label(ts, "day") if ts else None,
                "week": bucket_label(ts, "week") if ts else None,
                "month": bucket_label(ts, "month") if ts else None,
                "model_context_window": info.get("model_context_window"),
            }

            for k in TOKEN_KEYS:
                row[f"total_{k}"] = total.get(k)
                row[f"last_{k}"] = last.get(k)

            yield row


def dataset_token_deltas(
    root: Path, args: argparse.Namespace, params: dict[str, Any]
) -> Iterator[dict[str, Any]]:
    since = parse_ts(args.since) if args.since else None
    until = parse_ts(args.until) if args.until else None
    include_base = bool(params.get("include_base", True))
    include_zero = bool(params.get("include_zero", False))
    dedupe = bool(params.get("dedupe", True))

    for path in iter_jsonl_paths(root):
        segment = 0
        prev_total: Optional[dict[str, int]] = None
        prev_total_tokens: Optional[int] = None
        for ts, info in iter_token_count_events_in_path(path, since=since, until=until):
            total = token_usage(info, "total_token_usage")
            if not total or "total_tokens" not in total:
                continue

            total_tokens = total.get("total_tokens")
            if (
                dedupe
                and prev_total_tokens is not None
                and total_tokens == prev_total_tokens
            ):
                continue

            is_reset = (
                prev_total_tokens is not None
                and total_tokens is not None
                and total_tokens < prev_total_tokens
            )
            if is_reset:
                segment += 1
                prev_total = None
                prev_total_tokens = None

            deltas: dict[str, int] = {}
            if prev_total is None:
                if include_base:
                    for k, v in total.items():
                        deltas[k] = v
            else:
                for k, v in total.items():
                    pv = prev_total.get(k)
                    if pv is None:
                        continue
                    d = v - pv
                    if d:
                        deltas[k] = d

            prev_total = total
            prev_total_tokens = total_tokens

            delta_total = deltas.get("total_tokens", 0)
            if not include_zero and delta_total == 0:
                continue

            row: dict[str, Any] = {
                "path": str(path),
                "timestamp": ts.isoformat() if ts else None,
                "day": bucket_label(ts, "day") if ts else None,
                "week": bucket_label(ts, "week") if ts else None,
                "month": bucket_label(ts, "month") if ts else None,
                "segment": segment,
                "model_context_window": info.get("model_context_window"),
            }

            for k in TOKEN_KEYS:
                row[f"delta_{k}"] = deltas.get(k)
                row[f"total_{k}"] = total.get(k)

            yield row


def dataset_token_sessions(
    root: Path, args: argparse.Namespace, params: dict[str, Any]
) -> Iterator[dict[str, Any]]:
    since = parse_ts(args.since) if args.since else None
    until = parse_ts(args.until) if args.until else None

    for path in iter_jsonl_paths(root):
        start_ts: Optional[datetime] = None
        end_ts: Optional[datetime] = None
        max_total: Optional[dict[str, int]] = None
        max_total_tokens: Optional[int] = None
        max_ts: Optional[datetime] = None

        for ts, info in iter_token_count_events_in_path(path, since=since, until=until):
            total = token_usage(info, "total_token_usage")
            tt = total.get("total_tokens")
            if tt is None:
                continue
            if ts is not None and (start_ts is None or ts < start_ts):
                start_ts = ts
            if ts is not None and (end_ts is None or ts > end_ts):
                end_ts = ts
            if max_total_tokens is None or tt > max_total_tokens:
                max_total_tokens = tt
                max_total = total
                max_ts = ts

        if max_total_tokens is None or max_total is None:
            continue

        row: dict[str, Any] = {
            "path": str(path),
            "start": start_ts.isoformat() if start_ts else None,
            "end": end_ts.isoformat() if end_ts else None,
            "max_at": max_ts.isoformat() if max_ts else None,
            "day": bucket_label(start_ts, "day") if start_ts else None,
            "week": bucket_label(start_ts, "week") if start_ts else None,
            "month": bucket_label(start_ts, "month") if start_ts else None,
        }
        for k in TOKEN_KEYS:
            row[f"total_{k}"] = max_total.get(k)
        yield row


def dataset_tool_calls(
    root: Path, args: argparse.Namespace, params: dict[str, Any]
) -> Iterator[dict[str, Any]]:
    since = parse_ts(args.since) if args.since else None
    until = parse_ts(args.until) if args.until else None

    for path in iter_jsonl_paths(root):
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                # Fast prefilter: tool calls are response_item rows with call types.
                if "response_item" not in line:
                    continue
                if "function_call" not in line and "custom_tool_call" not in line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if obj.get("type") != "response_item":
                    continue
                payload = obj.get("payload") or {}
                ptype = payload.get("type")
                if ptype not in ("function_call", "custom_tool_call"):
                    continue
                ts = parse_ts(obj.get("timestamp"))
                if since and ts and ts < since:
                    continue
                if until and ts and ts > until:
                    continue

                tool_name = payload.get("name")
                call_id = payload.get("call_id")

                row: dict[str, Any] = {
                    "path": str(path),
                    "timestamp": ts.isoformat() if ts else None,
                    "day": bucket_label(ts, "day") if ts else None,
                    "week": bucket_label(ts, "week") if ts else None,
                    "month": bucket_label(ts, "month") if ts else None,
                    "kind": ptype,
                    "tool": tool_name,
                    "call_id": call_id,
                }

                if ptype == "function_call":
                    args_s = payload.get("arguments")
                    row["arguments_len"] = (
                        len(args_s) if isinstance(args_s, str) else None
                    )
                else:
                    inp = payload.get("input")
                    row["input_len"] = len(inp) if isinstance(inp, str) else None
                    row["status"] = payload.get("status")

                yield row


DATASETS: dict[str, DatasetDef] = {
    "messages": DatasetDef(
        name="messages",
        description="Messages (user/assistant) with timestamps and text",
        fields=[
            "path",
            "timestamp",
            "day",
            "week",
            "month",
            "role",
            "text",
            "text_len",
        ],
        default_params={},
        params_help={},
        iter_rows=dataset_messages,
    ),
    "skill_mentions": DatasetDef(
        name="skill_mentions",
        description="Skill mentions via <skill> blocks and $skill tokens",
        fields=[
            "path",
            "timestamp",
            "day",
            "week",
            "month",
            "role",
            "skill",
            "types",
            "snippet",
        ],
        default_params={
            "include_blocks": True,
            "include_dollars": True,
            "skip_dollar_in_skill_block": True,
            "dedupe_adjacent": True,
        },
        params_help={
            "include_blocks": "include <skill> blocks (default true)",
            "include_dollars": "include $skill tokens (default true; known skills only)",
            "skip_dollar_in_skill_block": "skip $skill when any <skill> block exists in the message (default true)",
            "dedupe_adjacent": "dedupe adjacent block vs dollar flips (default true)",
        },
        iter_rows=dataset_skill_mentions,
    ),
    "token_events": DatasetDef(
        name="token_events",
        description="Raw token_count events (flattened total_* and last_* fields)",
        fields=[
            "path",
            "timestamp",
            "day",
            "week",
            "month",
            "model_context_window",
        ]
        + [f"total_{k}" for k in TOKEN_KEYS]
        + [f"last_{k}" for k in TOKEN_KEYS],
        default_params={"dedupe": True},
        params_help={
            "dedupe": "skip consecutive identical total_total_tokens (default true)"
        },
        iter_rows=dataset_token_events,
    ),
    "token_deltas": DatasetDef(
        name="token_deltas",
        description="Token deltas derived from total_token_usage changes",
        fields=[
            "path",
            "timestamp",
            "day",
            "week",
            "month",
            "segment",
            "model_context_window",
        ]
        + [f"delta_{k}" for k in TOKEN_KEYS]
        + [f"total_{k}" for k in TOKEN_KEYS],
        default_params={"include_base": True, "include_zero": False, "dedupe": True},
        params_help={
            "include_base": "emit first total as a delta per session segment (default true)",
            "include_zero": "include zero-delta rows (default false)",
            "dedupe": "skip consecutive identical total_token_usage.total_tokens (default true)",
        },
        iter_rows=dataset_token_deltas,
    ),
    "token_sessions": DatasetDef(
        name="token_sessions",
        description="One row per session file: max total_token_usage",
        fields=[
            "path",
            "start",
            "end",
            "max_at",
            "day",
            "week",
            "month",
        ]
        + [f"total_{k}" for k in TOKEN_KEYS],
        default_params={},
        params_help={},
        iter_rows=dataset_token_sessions,
    ),
    "tool_calls": DatasetDef(
        name="tool_calls",
        description="Tool calls (function_call/custom_tool_call) with basic sizes",
        fields=[
            "path",
            "timestamp",
            "day",
            "week",
            "month",
            "kind",
            "tool",
            "call_id",
            "arguments_len",
            "input_len",
            "status",
        ],
        default_params={},
        params_help={},
        iter_rows=dataset_tool_calls,
    ),
}


def parse_json_arg(value: str) -> Any:
    if value.startswith("@"):
        path = Path(value[1:]).expanduser()
        return json.loads(path.read_text(encoding="utf-8"))
    return json.loads(value)


def format_table_rows(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "(no results)"
    cols = columns
    widths: dict[str, int] = {}
    for c in cols:
        widths[c] = len(c)
    for r in rows:
        for c in cols:
            v = r.get(c)
            s = "" if v is None else str(v)
            if len(s) > widths[c]:
                widths[c] = len(s)
    lines = []
    lines.append("  ".join(c.ljust(widths[c]) for c in cols))
    lines.append("  ".join("-" * widths[c] for c in cols))
    for r in rows:
        lines.append(
            "  ".join(
                ("" if r.get(c) is None else str(r.get(c))).ljust(widths[c])
                for c in cols
            )
        )
    return "\n".join(lines)


def write_csv(rows: list[dict[str, Any]], columns: list[str]) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns)
    writer.writeheader()
    for r in rows:
        writer.writerow({c: ("" if r.get(c) is None else r.get(c)) for c in columns})
    return buf.getvalue().strip("\n")


def sort_rows(rows: list[dict[str, Any]], sort_keys: list[str]) -> list[dict[str, Any]]:
    out = list(rows)
    for key in reversed(sort_keys):
        desc = key.startswith("-")
        k = key[1:] if desc else key
        non_none = [r for r in out if k in r and r[k] is not None]
        none = [r for r in out if k not in r or r[k] is None]
        non_none.sort(key=lambda r: r[k], reverse=desc)
        out = non_none + none
    return out


def compile_where(where: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compiled = []
    for w in where:
        if not isinstance(w, dict):
            raise ValueError("where entries must be objects")
        field = w.get("field")
        op = (w.get("op") or "eq").lower()
        value = w.get("value")
        if not isinstance(field, str) or not field:
            raise ValueError("where.field must be a string")
        if op == "regex":
            if not isinstance(value, str):
                raise ValueError("regex value must be a string")
            flags = 0
            if w.get("case_insensitive"):
                flags |= re.IGNORECASE
            rx = re.compile(value, flags)
            compiled.append({"field": field, "op": op, "rx": rx})
        else:
            compiled.append({"field": field, "op": op, "value": value})
    return compiled


def record_matches(rec: dict[str, Any], where: list[dict[str, Any]]) -> bool:
    for w in where:
        field = w["field"]
        op = w["op"]
        v = rec.get(field)

        if op == "exists":
            if v is None:
                return False
            continue
        if op == "not_exists":
            if v is not None:
                return False
            continue

        if op == "contains":
            needle = w.get("value")
            if not isinstance(needle, str):
                return False
            if needle not in ("" if v is None else str(v)):
                return False
            continue
        if op == "regex":
            rx = w["rx"]
            if not rx.search("" if v is None else str(v)):
                return False
            continue

        if op in ("eq", "neq", "gt", "gte", "lt", "lte"):
            rhs = w.get("value")
            if op == "eq" and v != rhs:
                return False
            if op == "neq" and v == rhs:
                return False
            if op in ("gt", "gte", "lt", "lte"):
                try:
                    lv = float(v) if v is not None else None
                    rv = float(rhs) if rhs is not None else None
                except Exception:
                    lv = v
                    rv = rhs
                if lv is None or rv is None:
                    return False
                if op == "gt" and not (lv > rv):
                    return False
                if op == "gte" and not (lv >= rv):
                    return False
                if op == "lt" and not (lv < rv):
                    return False
                if op == "lte" and not (lv <= rv):
                    return False
            continue

        if op in ("in", "nin"):
            rhs = w.get("value")
            if not isinstance(rhs, list):
                return False
            inside = v in rhs
            if op == "in" and not inside:
                return False
            if op == "nin" and inside:
                return False
            continue

        raise ValueError(f"unsupported where op: {op}")

    return True


def cmd_datasets(args: argparse.Namespace) -> str:
    rows = []
    for name in sorted(DATASETS.keys()):
        d = DATASETS[name]
        rows.append({"dataset": d.name, "description": d.description})
    return format_table_rows(rows, ["dataset", "description"])


def cmd_dataset_schema(args: argparse.Namespace) -> str:
    ds = args.dataset
    d = DATASETS.get(ds)
    if not d:
        return f"Unknown dataset: {ds}"
    lines = []
    lines.append(f"Dataset: {d.name}")
    lines.append(f"Description: {d.description}")
    lines.append("Fields:")
    for f in d.fields:
        lines.append(f"- {f}")
    if d.default_params:
        lines.append("Params:")
        for k in sorted(d.default_params.keys()):
            help_s = d.params_help.get(k, "")
            lines.append(
                f"- {k}: {d.default_params[k]}{(' - ' + help_s) if help_s else ''}"
            )
    return "\n".join(lines)


def cmd_query(args: argparse.Namespace) -> str:
    root = discover_sessions_root(args.root)
    try:
        spec = parse_json_arg(args.spec)
    except Exception as e:
        return f"Invalid --spec JSON: {e}"
    if not isinstance(spec, dict):
        return "Spec must be a JSON object."

    dataset = spec.get("dataset")
    if not isinstance(dataset, str) or not dataset:
        return "Spec must include dataset (string)."
    d = DATASETS.get(dataset)
    if not d:
        return f"Unknown dataset: {dataset}"

    params = spec.get("params") or {}
    if not isinstance(params, dict):
        return "Spec params must be an object."
    merged_params = dict(d.default_params)
    merged_params.update(params)

    where = spec.get("where") or []
    if not isinstance(where, list):
        return "Spec where must be a list."
    try:
        where_c = compile_where(where)
    except Exception as e:
        return f"Invalid where: {e}"

    group_by = spec.get("group_by") or []
    if not isinstance(group_by, list) or not all(isinstance(x, str) for x in group_by):
        return "Spec group_by must be a list of strings."

    metrics = spec.get("metrics")
    if metrics is None:
        metrics = []
    if not isinstance(metrics, list):
        return "Spec metrics must be a list."

    select = spec.get("select")
    if select is None:
        select = []
    if not isinstance(select, list) or not all(isinstance(x, str) for x in select):
        return "Spec select must be a list of strings."

    sort = spec.get("sort") or []
    if isinstance(sort, str):
        sort = [sort]
    if not isinstance(sort, list) or not all(isinstance(x, str) for x in sort):
        return "Spec sort must be a list of strings."

    limit = spec.get("limit")
    if limit is None:
        limit = 0
    if not isinstance(limit, int) or limit < 0:
        return "Spec limit must be a non-negative integer."

    fmt = spec.get("format")
    if fmt is None:
        fmt = "table" if group_by else "jsonl"
    if fmt not in ("table", "json", "csv", "jsonl"):
        return "Spec format must be one of: table, json, csv, jsonl."

    rows_iter = d.iter_rows(root, args, merged_params)

    if not group_by:
        out_rows: list[dict[str, Any]] = []
        for r in rows_iter:
            if where_c and not record_matches(r, where_c):
                continue
            if select:
                r = {k: r.get(k) for k in select}
            out_rows.append(r)
            if limit and len(out_rows) >= limit and not sort:
                break
        if sort:
            out_rows = sort_rows(out_rows, sort)
            if limit:
                out_rows = out_rows[:limit]
        cols = select or (sorted(out_rows[0].keys()) if out_rows else [])
        if fmt == "jsonl":
            return "\n".join(json.dumps(r, ensure_ascii=True) for r in out_rows)
        if fmt == "json":
            return json.dumps(out_rows, indent=2, ensure_ascii=True)
        if fmt == "csv":
            return write_csv(out_rows, cols)
        return format_table_rows(out_rows, cols)

    # grouped query
    if not metrics:
        metrics = [{"op": "count", "as": "count"}]

    metric_defs = []
    for m in metrics:
        if not isinstance(m, dict):
            return "Spec metrics entries must be objects."
        op = (m.get("op") or "count").lower()
        field = m.get("field")
        alias = m.get("as")
        if not isinstance(alias, str) or not alias:
            if op == "count":
                alias = "count"
            elif isinstance(field, str) and field:
                alias = f"{op}_{field}"
            else:
                alias = op
        metric_defs.append({"op": op, "field": field, "as": alias})

    def init_state(op: str):
        if op == "count":
            return 0
        if op == "sum":
            return 0
        if op in ("min", "max"):
            return None
        if op == "avg":
            return {"sum": 0.0, "count": 0}
        if op == "count_distinct":
            return set()
        raise ValueError(f"unsupported metric op: {op}")

    def update_state(state: Any, op: str, field: Any, rec: dict[str, Any]) -> Any:
        if op == "count":
            return state + 1
        v = rec.get(field) if isinstance(field, str) else None
        if v is None:
            return state
        if op == "sum":
            if isinstance(v, (int, float)):
                return state + v
            try:
                return state + float(v)
            except Exception:
                return state
        if op == "min":
            return v if state is None or v < state else state
        if op == "max":
            return v if state is None or v > state else state
        if op == "avg":
            try:
                state["sum"] += float(v)
                state["count"] += 1
            except Exception:
                pass
            return state
        if op == "count_distinct":
            state.add(v)
            return state
        return state

    def finalize_state(state: Any, op: str):
        if op == "avg":
            c = state["count"]
            return (state["sum"] / c) if c else None
        if op == "count_distinct":
            return len(state)
        return state

    groups: dict[tuple[Any, ...], list[Any]] = {}
    for r in rows_iter:
        if where_c and not record_matches(r, where_c):
            continue
        key = tuple(r.get(f) for f in group_by)
        st = groups.get(key)
        if st is None:
            st = [init_state(m["op"]) for m in metric_defs]
            groups[key] = st
        for i, m in enumerate(metric_defs):
            try:
                st[i] = update_state(st[i], m["op"], m.get("field"), r)
            except Exception:
                continue

    out_rows = []
    for key, st in groups.items():
        row: dict[str, Any] = {}
        for i, f in enumerate(group_by):
            row[f] = key[i]
        for i, m in enumerate(metric_defs):
            row[m["as"]] = finalize_state(st[i], m["op"])
        out_rows.append(row)

    if sort:
        out_rows = sort_rows(out_rows, sort)
    if limit:
        out_rows = out_rows[:limit]

    cols = list(group_by) + [m["as"] for m in metric_defs]
    if fmt == "json":
        return json.dumps(out_rows, indent=2, ensure_ascii=True)
    if fmt == "csv":
        return write_csv(out_rows, cols)
    if fmt == "jsonl":
        return "\n".join(json.dumps(r, ensure_ascii=True) for r in out_rows)
    return format_table_rows(out_rows, cols)


def cmd_token_usage(args: argparse.Namespace) -> str:
    root = discover_sessions_root(args.root)

    # Prefer token_count events (fast, reliable). Fall back to tool-output regex if none found.
    totals_by_day: dict[str, int] = defaultdict(int)
    n_rows = 0
    for row in dataset_token_deltas(
        root, args, {"include_base": True, "include_zero": False, "dedupe": True}
    ):
        day = row.get("day")
        dt = row.get("delta_total_tokens")
        if not isinstance(day, str) or not day:
            continue
        if not isinstance(dt, int):
            continue
        totals_by_day[day] += dt
        n_rows += 1

    if totals_by_day:
        days = sorted(totals_by_day.keys())
        day_totals = [totals_by_day[d] for d in days]
        total = sum(day_totals)
        avg = total / len(day_totals) if day_totals else 0
        max_day = max(days, key=lambda d: totals_by_day[d])
        min_day = min(days, key=lambda d: totals_by_day[d])

        lines = []
        lines.append(f"Delta rows: {n_rows}")
        lines.append(f"Days: {len(days)}")
        lines.append(f"Total tokens: {total}")
        lines.append(f"Average/day: {avg:.2f}")
        lines.append(f"Min day: {min_day} ({totals_by_day[min_day]})")
        lines.append(f"Max day: {max_day} ({totals_by_day[max_day]})")
        if args.top:
            lines.append("Top days:")
            for d in sorted(days, key=lambda d: totals_by_day[d], reverse=True)[
                : args.top
            ]:
                lines.append(f"- {totals_by_day[d]} {d}")
        return "\n".join(lines)

    # Fallback: legacy token counts emitted by tools.
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
        return "No token_count events or legacy token counts found."

    counts = [m["count"] for m in matches]
    total = sum(counts)
    avg = total / len(counts)
    lines = []
    lines.append("(legacy) Source: tool output regex")
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
        Path(out_path).write_text(text, encoding="utf-8")
    else:
        print(text)


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--root",
        help=f"sessions root (default: {DEFAULT_SESSIONS_ROOT})",
    )
    common.add_argument("--roles", default="user,assistant", help="roles to include")
    common.add_argument("--since", help="ISO timestamp (inclusive)")
    common.add_argument("--until", help="ISO timestamp (inclusive)")
    common.add_argument("--output", help="write output to file instead of stdout")
    common.add_argument(
        "--skills-dir",
        action="append",
        default=[
            str(Path.home() / ".dotfiles" / "codex" / "skills"),
            str(Path.home() / ".codex" / "skills"),
        ],
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
    s_rank.add_argument(
        "--no-blocks", action="store_true", help="ignore <skill> blocks"
    )
    s_rank.add_argument(
        "--no-dollars", action="store_true", help="ignore $skill tokens"
    )
    s_rank.add_argument(
        "--no-skip-dollar-in-block",
        action="store_true",
        help="count $skill even inside <skill> blocks",
    )
    s_rank.add_argument(
        "--no-dedupe", action="store_true", help="disable adjacent block/dollar dedupe"
    )
    s_rank.set_defaults(func=cmd_skills_rank)

    s_trend = sub.add_parser(
        "skill-trend", help="time-bucketed counts for one skill", parents=[common]
    )
    s_trend.add_argument("--skill", required=True)
    s_trend.add_argument("--bucket", choices=["day", "week", "month"], default="day")
    s_trend.add_argument("--format", choices=["table", "json", "csv"], default="table")
    s_trend.add_argument(
        "--max", type=int, default=0, help="limit buckets (most recent)"
    )
    s_trend.add_argument(
        "--no-blocks", action="store_true", help="ignore <skill> blocks"
    )
    s_trend.add_argument(
        "--no-dollars", action="store_true", help="ignore $skill tokens"
    )
    s_trend.add_argument(
        "--no-skip-dollar-in-block",
        action="store_true",
        help="count $skill even inside <skill> blocks",
    )
    s_trend.add_argument(
        "--no-dedupe", action="store_true", help="disable adjacent block/dollar dedupe"
    )
    s_trend.set_defaults(func=cmd_skill_trend)

    s_report = sub.add_parser(
        "skill-report", help="report on a specific skill", parents=[common]
    )
    s_report.add_argument("--skill", required=True)
    s_report.add_argument(
        "--sections",
        help="comma-separated section labels to audit in assistant messages",
    )
    s_report.add_argument(
        "--sample-missing", type=int, default=0, help="sample missing messages"
    )
    s_report.add_argument(
        "--snippets", type=int, default=0, help="include occurrence snippets"
    )
    s_report.add_argument(
        "--no-blocks", action="store_true", help="ignore <skill> blocks"
    )
    s_report.add_argument(
        "--no-dollars", action="store_true", help="ignore $skill tokens"
    )
    s_report.add_argument(
        "--no-skip-dollar-in-block",
        action="store_true",
        help="count $skill even inside <skill> blocks",
    )
    s_report.add_argument(
        "--no-dedupe", action="store_true", help="disable adjacent block/dollar dedupe"
    )
    s_report.set_defaults(func=cmd_skill_report)

    s_roles = sub.add_parser(
        "role-breakdown", help="user vs assistant counts by skill", parents=[common]
    )
    s_roles.add_argument("--format", choices=["table", "json", "csv"], default="table")
    s_roles.add_argument("--max", type=int, default=0, help="limit rows")
    s_roles.add_argument(
        "--no-blocks", action="store_true", help="ignore <skill> blocks"
    )
    s_roles.add_argument(
        "--no-dollars", action="store_true", help="ignore $skill tokens"
    )
    s_roles.add_argument(
        "--no-skip-dollar-in-block",
        action="store_true",
        help="count $skill even inside <skill> blocks",
    )
    s_roles.add_argument(
        "--no-dedupe", action="store_true", help="disable adjacent block/dollar dedupe"
    )
    s_roles.set_defaults(func=cmd_role_breakdown)

    s_export = sub.add_parser(
        "occurrence-export", help="export occurrences", parents=[common]
    )
    s_export.add_argument("--skill", help="filter to one skill")
    s_export.add_argument("--format", choices=["jsonl", "json", "csv"], default="jsonl")
    s_export.add_argument("--max", type=int, default=0, help="limit rows")
    s_export.add_argument(
        "--no-blocks", action="store_true", help="ignore <skill> blocks"
    )
    s_export.add_argument(
        "--no-dollars", action="store_true", help="ignore $skill tokens"
    )
    s_export.add_argument(
        "--no-skip-dollar-in-block",
        action="store_true",
        help="count $skill even inside <skill> blocks",
    )
    s_export.add_argument(
        "--no-dedupe", action="store_true", help="disable adjacent block/dollar dedupe"
    )
    s_export.set_defaults(func=cmd_occurrence_export)

    s_bundle = sub.add_parser(
        "report-bundle", help="bundle common reports into JSON", parents=[common]
    )
    s_bundle.add_argument("--top", type=int, default=20, help="top N skills for rank")
    s_bundle.add_argument("--skills", help="comma-separated skills for section audit")
    s_bundle.add_argument("--sections", help="comma-separated section labels for audit")
    s_bundle.add_argument(
        "--no-blocks", action="store_true", help="ignore <skill> blocks"
    )
    s_bundle.add_argument(
        "--no-dollars", action="store_true", help="ignore $skill tokens"
    )
    s_bundle.add_argument(
        "--no-skip-dollar-in-block",
        action="store_true",
        help="count $skill even inside <skill> blocks",
    )
    s_bundle.add_argument(
        "--no-dedupe", action="store_true", help="disable adjacent block/dollar dedupe"
    )
    s_bundle.set_defaults(func=cmd_report_bundle)

    s_audit = sub.add_parser(
        "section-audit",
        help="audit section presence in assistant messages",
        parents=[common],
    )
    s_audit.add_argument(
        "--sections", required=True, help="comma-separated section labels"
    )
    s_audit.add_argument(
        "--contains", help="only scan messages containing this substring"
    )
    s_audit.add_argument("--case-insensitive", action="store_true")
    s_audit.add_argument("--sample-missing", type=int, default=0)
    s_audit.set_defaults(func=cmd_section_audit)

    s_tokens = sub.add_parser(
        "token-usage",
        help="summarize token usage by day (prefers token_count events)",
        parents=[common],
    )
    s_tokens.add_argument("--top", type=int, default=0, help="show top N")
    s_tokens.set_defaults(func=cmd_token_usage)

    s_datasets = sub.add_parser(
        "datasets", help="list available datasets", parents=[common]
    )
    s_datasets.set_defaults(func=cmd_datasets)

    s_schema = sub.add_parser(
        "dataset-schema", help="show dataset fields and params", parents=[common]
    )
    s_schema.add_argument("--dataset", required=True)
    s_schema.set_defaults(func=cmd_dataset_schema)

    s_query = sub.add_parser(
        "query", help="run a JSON-specified query", parents=[common]
    )
    s_query.add_argument(
        "--spec", required=True, help="JSON spec string or @path/to/spec.json"
    )
    s_query.set_defaults(func=cmd_query)

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
