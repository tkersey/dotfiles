#!/usr/bin/env -S uv run python
"""Append a structured learning record to repo-root .learnings.jsonl."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


def run_git(args: list[str], cwd: Path) -> str:
    try:
        out = subprocess.check_output(["git", *args], cwd=str(cwd), text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""
    return out.strip()


def normalize_status(raw: str) -> str:
    status = raw.strip().lower()
    status = re.sub(r"[^a-z0-9]+", "_", status)
    status = status.strip("_")
    status = re.sub(r"_+", "_", status)
    return status


def normalize_learning(raw: str) -> str:
    value = raw.strip()
    value = re.sub(r"\s+", " ", value)
    return value


def normalize_tag(raw: str) -> str:
    value = raw.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = value.strip("_")
    value = re.sub(r"_+", "_", value)
    return value


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def discover_repo_root(start: Path) -> Path:
    root = run_git(["rev-parse", "--show-toplevel"], start)
    if root:
        return Path(root).resolve()
    return start.resolve()


def infer_repo_slug(repo_root: Path) -> str:
    remote = run_git(["config", "--get", "remote.origin.url"], repo_root)
    s = (remote or "").strip()
    if not s:
        return repo_root.name

    # Common forms:
    # - git@github.com:owner/repo.git
    # - https://github.com/owner/repo.git
    # - ssh://git@github.com/owner/repo.git
    path = ""
    if s.startswith("git@") and ":" in s:
        path = s.split(":", 1)[1]
    else:
        try:
            u = urlparse(s)
        except Exception:
            u = None
        if u and u.path:
            path = u.path.lstrip("/")
        elif ":" in s and "/" in s.split(":", 1)[1]:
            path = s.split(":", 1)[1]
        else:
            path = s

    path = path.strip("/")
    if path.endswith(".git"):
        path = path[: -len(".git")]
    parts = [p for p in path.split("/") if p]
    if len(parts) >= 2:
        return f"{parts[-2]}/{parts[-1]}"
    return repo_root.name


def changed_paths(repo_root: Path) -> list[str]:
    staged = run_git(
        ["diff", "--cached", "--name-only", "--relative"], repo_root
    ).splitlines()
    unstaged = run_git(["diff", "--name-only", "--relative"], repo_root).splitlines()
    paths = [p.strip() for p in [*staged, *unstaged] if p.strip()]
    deduped: list[str] = []
    seen: set[str] = set()
    for path in paths:
        if path not in seen:
            seen.add(path)
            deduped.append(path)
    return deduped


def fingerprint(status: str, learning: str) -> str:
    key = f"{status}|{learning.lower()}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]


def load_existing(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=True))
        fh.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--status",
        default="review_later",
        help="Action status (for example: do_more, do_less); defaults to review_later",
    )
    parser.add_argument("--learning", required=True, help="Learning statement")
    parser.add_argument(
        "--evidence",
        action="append",
        default=[],
        help="Evidence item (repeat for multiple lines); optional in best-effort mode",
    )
    parser.add_argument(
        "--application",
        default="",
        help="How to apply this learning; optional in best-effort mode",
    )
    parser.add_argument(
        "--tag",
        action="append",
        default=[],
        help="Tag (repeatable; comma-separated ok), for example: tooling, git, ci",
    )
    parser.add_argument(
        "--related-id",
        action="append",
        default=[],
        help="Related learning id (repeatable; comma-separated ok)",
    )
    parser.add_argument(
        "--supersedes-id",
        default="",
        help="If this learning supersedes an older record id",
    )
    parser.add_argument(
        "--repo",
        default="",
        help="Repo identifier override (defaults to remote origin slug or repo dir name)",
    )
    parser.add_argument(
        "--path",
        default=".learnings.jsonl",
        help="Path to JSONL file, relative to repo root by default",
    )
    parser.add_argument(
        "--source",
        default="skill:learnings",
        help="Source marker for the record",
    )
    parser.add_argument(
        "--allow-duplicate",
        action="store_true",
        help="Append even if an existing record has the same fingerprint",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    cwd = Path.cwd()
    repo_root = discover_repo_root(cwd)

    status = normalize_status(args.status)
    if not status:
        status = "review_later"

    learning = normalize_learning(args.learning)
    if not learning:
        print("error: learning is empty", file=sys.stderr)
        return 1

    evidence = [
        normalize_learning(item) for item in args.evidence if normalize_learning(item)
    ]
    if not evidence:
        evidence = ["none_provided"]

    application = normalize_learning(args.application)
    if not application:
        application = "capture_follow_up_later"

    tags: list[str] = []
    seen_tags: set[str] = set()
    for raw in args.tag:
        if not isinstance(raw, str):
            continue
        for part in raw.split(","):
            t = normalize_tag(part)
            if t and t not in seen_tags:
                seen_tags.add(t)
                tags.append(t)

    related_ids: list[str] = []
    seen_related: set[str] = set()
    for raw in args.related_id:
        if not isinstance(raw, str):
            continue
        for part in (p.strip() for p in raw.split(",")):
            if part and part not in seen_related:
                seen_related.add(part)
                related_ids.append(part)

    supersedes_id = (args.supersedes_id or "").strip() or None

    fp = fingerprint(status, learning)
    timestamp = now_utc()
    record_id = f"lrn-{timestamp.replace('-', '').replace(':', '')}-{fp[:8]}"

    branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo_root) or "unknown"
    context_paths = changed_paths(repo_root)
    repo = (args.repo or "").strip() or infer_repo_slug(repo_root)

    record = {
        "id": record_id,
        "captured_at": timestamp,
        "status": status,
        "learning": learning,
        "evidence": evidence,
        "application": application,
        "context": {
            "repo": repo,
            "branch": branch,
            "paths": context_paths,
        },
        "source": args.source,
        "fingerprint": fp,
    }

    if tags:
        record["tags"] = tags
    if related_ids:
        record["related_ids"] = related_ids
    if supersedes_id:
        record["supersedes_id"] = supersedes_id

    output_path = Path(args.path)
    if not output_path.is_absolute():
        output_path = repo_root / output_path

    if not args.allow_duplicate:
        for row in load_existing(output_path):
            if row.get("fingerprint") == fp:
                existing_id = row.get("id", "unknown")
                print(
                    f"duplicate-skip: fingerprint={fp} existing_id={existing_id} path={output_path}",
                    file=sys.stderr,
                )
                return 0

    append_jsonl(output_path, record)
    print(f"appended: id={record_id} status={status} path={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
