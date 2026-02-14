#!/usr/bin/env -S uv run python
"""Mine, recall, and promote records from repo-root .learnings.jsonl."""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator, Optional


DEFAULT_PATH = ".learnings.jsonl"


def run_git(args: list[str], cwd: Path) -> str:
    try:
        out = subprocess.check_output(["git", *args], cwd=str(cwd), text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""
    return out.strip()


def discover_repo_root(start: Path) -> Path:
    root = run_git(["rev-parse", "--show-toplevel"], start)
    if root:
        return Path(root).resolve()
    return start.resolve()


def resolve_jsonl_path(repo_root: Path, raw: str) -> Path:
    p = Path(raw or DEFAULT_PATH).expanduser()
    if p.is_absolute():
        return p
    return (repo_root / p).resolve()


def parse_ts(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    try:
        s = ts
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def bucket_label(ts: datetime, bucket: str) -> str:
    if bucket == "day":
        return ts.date().isoformat()
    if bucket == "week":
        iso = ts.isocalendar()
        return f"{iso.year}-W{iso.week:02d}"
    return f"{ts.year}-{ts.month:02d}"


def parse_json_arg(value: str, *, base_dir: Optional[Path] = None) -> Any:
    if value.startswith("@"):  # @file.json
        raw = value[1:]
        p = Path(raw).expanduser()
        if not p.is_absolute():
            cwd_p = (Path.cwd() / p).resolve()
            base_p = (base_dir / p).resolve() if base_dir else None
            if cwd_p.exists():
                p = cwd_p
            elif base_p and base_p.exists():
                p = base_p
            else:
                p = cwd_p
        return json.loads(p.read_text(encoding="utf-8"))
    return json.loads(value)


def format_table_rows(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "(no results)"
    widths: dict[str, int] = {c: len(c) for c in columns}
    for r in rows:
        for c in columns:
            v = r.get(c)
            s = "" if v is None else str(v)
            if len(s) > widths[c]:
                widths[c] = len(s)
    lines = []
    lines.append("  ".join(c.ljust(widths[c]) for c in columns))
    lines.append("  ".join("-" * widths[c] for c in columns))
    for r in rows:
        lines.append(
            "  ".join(
                ("" if r.get(c) is None else str(r.get(c))).ljust(widths[c])
                for c in columns
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
    compiled: list[dict[str, Any]] = []
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
            flags = re.IGNORECASE if w.get("case_insensitive") else 0
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


def shorten(s: str, max_len: int) -> str:
    if len(s) <= max_len:
        return s
    if max_len <= 3:
        return s[:max_len]
    return s[: max_len - 3] + "..."


def coerce_str_list(v: Any) -> list[str]:
    if not isinstance(v, list):
        return []
    out = []
    for item in v:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out


def join_lines(items: list[str]) -> str:
    return "\n".join(x for x in items if x)


def join_csv(items: list[str]) -> str:
    return ",".join(x for x in items if x)


def iter_records(jsonl_path: Path) -> Iterator[dict[str, Any]]:
    if not jsonl_path.exists():
        return
        yield  # pragma: no cover
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if isinstance(obj, dict):
                yield obj


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


LEARNINGS_FIELDS = [
    "id",
    "captured_at",
    "day",
    "week",
    "month",
    "status",
    "learning",
    "learning_snippet",
    "application",
    "source",
    "fingerprint",
    "repo",
    "branch",
    "tags_text",
    "tags_count",
    "paths_text",
    "paths_count",
    "evidence_text",
    "evidence_count",
    "related_ids_text",
    "supersedes_id",
    "text",
]


def dataset_learnings(
    repo_root: Path, args: argparse.Namespace, params: dict[str, Any]
) -> Iterator[dict[str, Any]]:
    jsonl_path = resolve_jsonl_path(repo_root, args.path)
    for rec in iter_records(jsonl_path):
        captured_at_raw = rec.get("captured_at")
        captured_at = captured_at_raw if isinstance(captured_at_raw, str) else None
        ts = parse_ts(captured_at) if captured_at else None

        raw_context = rec.get("context")
        context: dict[str, Any] = raw_context if isinstance(raw_context, dict) else {}
        raw_repo = context.get("repo")
        repo = raw_repo if isinstance(raw_repo, str) else None
        raw_branch = context.get("branch")
        branch = raw_branch if isinstance(raw_branch, str) else None
        paths = coerce_str_list(context.get("paths"))

        evidence = coerce_str_list(rec.get("evidence"))
        tags = coerce_str_list(rec.get("tags"))
        related_ids = coerce_str_list(rec.get("related_ids"))
        raw_sup = rec.get("supersedes_id")
        supersedes_id = raw_sup if isinstance(raw_sup, str) else None

        raw_learning = rec.get("learning")
        learning = raw_learning if isinstance(raw_learning, str) else ""
        raw_app = rec.get("application")
        application = raw_app if isinstance(raw_app, str) else ""

        evidence_text = join_lines(evidence)
        tags_text = join_csv(tags)
        paths_text = join_csv(paths)
        related_ids_text = join_csv(related_ids)

        text_parts = [learning, application, evidence_text, tags_text, paths_text]
        text = "\n".join(p for p in text_parts if p)

        row: dict[str, Any] = {
            "id": rec.get("id"),
            "captured_at": captured_at,
            "day": bucket_label(ts, "day") if ts else None,
            "week": bucket_label(ts, "week") if ts else None,
            "month": bucket_label(ts, "month") if ts else None,
            "status": rec.get("status"),
            "learning": learning,
            "learning_snippet": shorten(learning.replace("\n", " ").strip(), 160),
            "application": application,
            "source": rec.get("source"),
            "fingerprint": rec.get("fingerprint"),
            "repo": repo,
            "branch": branch,
            "tags_text": tags_text,
            "tags_count": len(tags),
            "paths_text": paths_text,
            "paths_count": len(paths),
            "evidence_text": evidence_text,
            "evidence_count": len(evidence),
            "related_ids_text": related_ids_text,
            "supersedes_id": supersedes_id,
            "text": text,
        }
        yield row


PATHS_FIELDS = [
    "id",
    "captured_at",
    "day",
    "week",
    "month",
    "status",
    "repo",
    "branch",
    "path",
    "fingerprint",
    "source",
]


def dataset_learning_paths(
    repo_root: Path, args: argparse.Namespace, params: dict[str, Any]
) -> Iterator[dict[str, Any]]:
    jsonl_path = resolve_jsonl_path(repo_root, args.path)
    for rec in iter_records(jsonl_path):
        captured_at_raw = rec.get("captured_at")
        captured_at = captured_at_raw if isinstance(captured_at_raw, str) else None
        ts = parse_ts(captured_at) if captured_at else None
        raw_context = rec.get("context")
        context: dict[str, Any] = raw_context if isinstance(raw_context, dict) else {}
        raw_repo = context.get("repo")
        repo = raw_repo if isinstance(raw_repo, str) else None
        raw_branch = context.get("branch")
        branch = raw_branch if isinstance(raw_branch, str) else None
        paths = coerce_str_list(context.get("paths"))
        for p in paths:
            yield {
                "id": rec.get("id"),
                "captured_at": captured_at,
                "day": bucket_label(ts, "day") if ts else None,
                "week": bucket_label(ts, "week") if ts else None,
                "month": bucket_label(ts, "month") if ts else None,
                "status": rec.get("status"),
                "repo": repo,
                "branch": branch,
                "path": p,
                "fingerprint": rec.get("fingerprint"),
                "source": rec.get("source"),
            }


TAGS_FIELDS = [
    "id",
    "captured_at",
    "day",
    "week",
    "month",
    "status",
    "repo",
    "branch",
    "tag",
    "fingerprint",
    "source",
]


def dataset_learning_tags(
    repo_root: Path, args: argparse.Namespace, params: dict[str, Any]
) -> Iterator[dict[str, Any]]:
    jsonl_path = resolve_jsonl_path(repo_root, args.path)
    for rec in iter_records(jsonl_path):
        captured_at_raw = rec.get("captured_at")
        captured_at = captured_at_raw if isinstance(captured_at_raw, str) else None
        ts = parse_ts(captured_at) if captured_at else None
        raw_context = rec.get("context")
        context: dict[str, Any] = raw_context if isinstance(raw_context, dict) else {}
        raw_repo = context.get("repo")
        repo = raw_repo if isinstance(raw_repo, str) else None
        raw_branch = context.get("branch")
        branch = raw_branch if isinstance(raw_branch, str) else None
        tags = coerce_str_list(rec.get("tags"))
        for t in tags:
            yield {
                "id": rec.get("id"),
                "captured_at": captured_at,
                "day": bucket_label(ts, "day") if ts else None,
                "week": bucket_label(ts, "week") if ts else None,
                "month": bucket_label(ts, "month") if ts else None,
                "status": rec.get("status"),
                "repo": repo,
                "branch": branch,
                "tag": t,
                "fingerprint": rec.get("fingerprint"),
                "source": rec.get("source"),
            }


DATASETS: dict[str, DatasetDef] = {
    "learnings": DatasetDef(
        name="learnings",
        description="Learning records from .learnings.jsonl (1 row per record)",
        fields=LEARNINGS_FIELDS,
        default_params={},
        params_help={},
        iter_rows=dataset_learnings,
    ),
    "learning_paths": DatasetDef(
        name="learning_paths",
        description="Exploded context.paths (1 row per record-path)",
        fields=PATHS_FIELDS,
        default_params={},
        params_help={},
        iter_rows=dataset_learning_paths,
    ),
    "learning_tags": DatasetDef(
        name="learning_tags",
        description="Exploded tags (1 row per record-tag)",
        fields=TAGS_FIELDS,
        default_params={},
        params_help={},
        iter_rows=dataset_learning_tags,
    ),
}


def cmd_datasets(args: argparse.Namespace) -> str:
    rows = []
    for name in sorted(DATASETS.keys()):
        d = DATASETS[name]
        rows.append({"dataset": d.name, "description": d.description})
    return format_table_rows(rows, ["dataset", "description"])


def cmd_dataset_schema(args: argparse.Namespace) -> str:
    d = DATASETS.get(args.dataset)
    if not d:
        return f"Unknown dataset: {args.dataset}"
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
    repo_root = discover_repo_root(Path.cwd())
    try:
        spec = parse_json_arg(args.spec, base_dir=repo_root)
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

    rows_iter = d.iter_rows(repo_root, args, merged_params)

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
        if op in ("count", "sum"):
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


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "because",
    "but",
    "by",
    "for",
    "from",
    "if",
    "in",
    "into",
    "is",
    "it",
    "no",
    "not",
    "of",
    "on",
    "or",
    "over",
    "so",
    "such",
    "that",
    "the",
    "their",
    "then",
    "there",
    "these",
    "this",
    "to",
    "too",
    "up",
    "was",
    "were",
    "when",
    "with",
}

TOOL_KEYWORDS = {
    "git",
    "gh",
    "uv",
    "pytest",
    "ruff",
    "mypy",
    "zig",
    "go",
    "npm",
    "bun",
    "docker",
    "make",
    "ci",
    "pre_commit",
    "precommit",
}


def stem_token(t: str) -> str:
    if len(t) > 5 and t.endswith("ing"):
        return t[:-3]
    if len(t) > 4 and t.endswith("ed"):
        return t[:-2]
    if len(t) > 4 and t.endswith("es"):
        return t[:-2]
    if len(t) > 3 and t.endswith("s"):
        return t[:-1]
    return t


def tokenize(s: str) -> list[str]:
    parts = re.split(r"[^a-z0-9]+", (s or "").lower())
    out = []
    for p in parts:
        if not p or len(p) <= 2:
            continue
        if p in STOPWORDS:
            continue
        p = stem_token(p)
        if not p or p in STOPWORDS:
            continue
        out.append(p)
    return out


def extract_path_hints(query: str) -> list[str]:
    if not query:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for m in re.finditer(r"[A-Za-z0-9_./-]+", query):
        s = m.group(0)
        if "/" not in s and "." not in s:
            continue
        if len(s) < 3:
            continue
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


STATUS_BOOST = {
    "codify_now": 0.30,
    "avoid_for_now": 0.25,
    "do_less": 0.15,
    "do_more": 0.15,
    "investigate_more": 0.10,
    "review_later": -0.05,
}


def compute_theme(text: str) -> str:
    toks = tokenize(text)
    if not toks:
        return ""
    counts: dict[str, int] = {}
    for t in toks:
        counts[t] = counts.get(t, 0) + 1
    top = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:6]
    return " ".join(t for t, _ in top)


def cmd_recall(args: argparse.Namespace) -> str:
    repo_root = discover_repo_root(Path.cwd())
    jsonl_path = resolve_jsonl_path(repo_root, args.path)
    if not jsonl_path.exists():
        return f"(no learnings file at {jsonl_path})"

    query = args.query or ""
    q_tokens = set(tokenize(query))
    if not q_tokens and not query.strip():
        return "error: --query is required"

    path_hints = []
    if args.paths:
        for part in args.paths.split(","):
            p = part.strip()
            if p:
                path_hints.append(p)
    path_hints.extend(extract_path_hints(query))

    now = datetime.now(timezone.utc)

    rows = list(dataset_learnings(repo_root, args, {}))
    superseded: set[str] = set()
    for r in rows:
        sid = r.get("supersedes_id")
        if isinstance(sid, str) and sid:
            superseded.add(sid)

    scored = []
    for r in rows:
        rid = r.get("id")
        if args.drop_superseded and isinstance(rid, str) and rid in superseded:
            continue

        raw_text = r.get("text")
        text = raw_text if isinstance(raw_text, str) else ""
        rec_tokens = set(tokenize(text))
        overlap = len(q_tokens & rec_tokens)

        # Require at least one concrete intersection signal.
        tool_match = (
            1.0
            if (q_tokens & TOOL_KEYWORDS and (q_tokens & TOOL_KEYWORDS) & rec_tokens)
            else 0.0
        )
        raw_paths_text = r.get("paths_text")
        paths_text = raw_paths_text if isinstance(raw_paths_text, str) else ""
        path_match = 1.0 if any(h and (h in paths_text) for h in path_hints) else 0.0

        if overlap == 0 and tool_match == 0.0 and path_match == 0.0:
            continue

        union = len(q_tokens | rec_tokens)
        jaccard = (overlap / union) if union else 0.0

        raw_captured_at = r.get("captured_at")
        ts = parse_ts(raw_captured_at) if isinstance(raw_captured_at, str) else None
        age_days = None
        if ts:
            delta = now - ts
            age_days = max(delta.total_seconds() / 86400.0, 0.0)
        recency = math.exp(-(age_days or 0.0) / 45.0) if age_days is not None else 0.0

        raw_status = r.get("status")
        status = raw_status if isinstance(raw_status, str) else ""
        status_boost = STATUS_BOOST.get(status, 0.0)
        raw_evidence_text = r.get("evidence_text")
        evidence_text = raw_evidence_text if isinstance(raw_evidence_text, str) else ""
        success_boost = (
            0.5 if evidence_text and evidence_text != "none_provided" else 0.0
        )

        score = (
            3.0 * jaccard
            + 1.5 * path_match
            + 1.0 * tool_match
            + 1.0 * recency
            + 0.5 * success_boost
            + status_boost
        )

        scored.append((score, r))

    scored.sort(key=lambda kv: (-kv[0], str(kv[1].get("captured_at") or "")))

    # Diversity cap: avoid returning only one theme.
    kept = []
    theme_counts: dict[str, int] = {}
    for score, r in scored:
        raw_tags_text = r.get("tags_text")
        tags_text = raw_tags_text if isinstance(raw_tags_text, str) else ""
        raw_learning = r.get("learning")
        learning = raw_learning if isinstance(raw_learning, str) else ""
        theme = compute_theme(tags_text + " " + learning)
        if theme and theme_counts.get(theme, 0) >= 2:
            continue
        theme_counts[theme] = theme_counts.get(theme, 0) + 1
        kept.append((score, r))
        if args.limit and len(kept) >= args.limit:
            break

    if args.format == "json":
        out = []
        for score, r in kept:
            row = dict(r)
            row["score"] = round(score, 4)
            out.append(row)
        return json.dumps(out, indent=2, ensure_ascii=True)

    out_rows = []
    for score, r in kept:
        out_rows.append(
            {
                "score": f"{score:.3f}",
                "captured_at": r.get("captured_at"),
                "status": r.get("status"),
                "learning": shorten(str(r.get("learning") or ""), 120),
                "tags": shorten(str(r.get("tags_text") or ""), 30),
                "paths": shorten(str(r.get("paths_text") or ""), 40),
            }
        )
    return format_table_rows(
        out_rows, ["score", "captured_at", "status", "learning", "tags", "paths"]
    )


def impact_score(text: str, status: str, tags_text: str) -> float:
    s = (text or "").lower()
    tags = (tags_text or "").lower()
    score = 0.0
    if status == "codify_now":
        score += 3.0
    if status == "avoid_for_now":
        score += 2.0
    if any(
        k in tags for k in ("security", "data_loss", "corruption", "invariant", "ci")
    ):
        score += 2.0
    if any(
        k in s
        for k in (
            "data loss",
            "corrupt",
            "credential",
            "secret",
            "leak",
            "force",
            "--hard",
        )
    ):
        score += 2.0
    if any(
        k in s for k in ("pre-commit", "precommit", "flake", "flaky", "timeout", "loop")
    ):
        score += 1.0
    return score


def cmd_codify_candidates(args: argparse.Namespace) -> str:
    repo_root = discover_repo_root(Path.cwd())
    jsonl_path = resolve_jsonl_path(repo_root, args.path)
    if not jsonl_path.exists():
        return f"(no learnings file at {jsonl_path})"

    now = datetime.now(timezone.utc)

    rows = list(dataset_learnings(repo_root, args, {}))
    superseded: set[str] = set()
    for r in rows:
        sid = r.get("supersedes_id")
        if isinstance(sid, str) and sid:
            superseded.add(sid)

    active = []
    for r in rows:
        rid = r.get("id")
        if args.drop_superseded and isinstance(rid, str) and rid in superseded:
            continue
        active.append(r)

    groups: dict[str, list[dict[str, Any]]] = {}
    for r in active:
        theme = compute_theme(
            (
                str(r.get("learning") or "")
                + " "
                + str(r.get("application") or "")
                + " "
                + str(r.get("tags_text") or "")
            )
        )
        if not theme:
            theme = "(untagged)"
        groups.setdefault(theme, []).append(r)

    out = []
    for theme, rs in groups.items():
        rs_sorted = sorted(
            rs, key=lambda r: str(r.get("captured_at") or ""), reverse=True
        )
        rep = rs_sorted[0]
        status = rep.get("status") if isinstance(rep.get("status"), str) else ""
        last_ts = (
            parse_ts(rep.get("captured_at"))
            if isinstance(rep.get("captured_at"), str)
            else None
        )
        age_days = None
        if last_ts:
            age_days = max((now - last_ts).total_seconds() / 86400.0, 0.0)
        recency = math.exp(-(age_days or 0.0) / 60.0) if age_days is not None else 0.0

        imp = 0.0
        for r in rs:
            imp = max(
                imp,
                impact_score(
                    str(r.get("text") or ""),
                    str(r.get("status") or ""),
                    str(r.get("tags_text") or ""),
                ),
            )

        count = len(rs)
        qualifies = count >= args.min_count or any(
            (r.get("status") == "codify_now") for r in rs
        )
        if not qualifies:
            continue

        score = (count * 2.0) + (recency * 2.0) + imp
        out.append(
            {
                "score": round(score, 3),
                "count": count,
                "last_seen": rep.get("captured_at"),
                "status": status,
                "theme": shorten(theme, 36),
                "learning": shorten(str(rep.get("learning") or ""), 120),
            }
        )

    out = sorted(
        out,
        key=lambda r: (-float(r["score"]), -int(r["count"]), str(r["last_seen"] or "")),
    )
    if args.limit:
        out = out[: args.limit]

    if args.format == "json":
        return json.dumps(out, indent=2, ensure_ascii=True)
    return format_table_rows(
        out, ["score", "count", "last_seen", "status", "theme", "learning"]
    )


def cmd_recent(args: argparse.Namespace) -> str:
    repo_root = discover_repo_root(Path.cwd())
    jsonl_path = resolve_jsonl_path(repo_root, args.path)
    if not jsonl_path.exists():
        return f"(no learnings file at {jsonl_path})"
    rows = list(dataset_learnings(repo_root, args, {}))
    rows = sorted(rows, key=lambda r: str(r.get("captured_at") or ""), reverse=True)
    if args.limit:
        rows = rows[: args.limit]
    out_rows = []
    for r in rows:
        out_rows.append(
            {
                "captured_at": r.get("captured_at"),
                "status": r.get("status"),
                "learning": shorten(str(r.get("learning") or ""), 120),
                "tags": shorten(str(r.get("tags_text") or ""), 30),
                "paths": shorten(str(r.get("paths_text") or ""), 40),
            }
        )
    return format_table_rows(
        out_rows, ["captured_at", "status", "learning", "tags", "paths"]
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--path",
        default=DEFAULT_PATH,
        help="Path to learnings JSONL file (relative to repo root by default)",
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("datasets", help="List datasets")

    ps = sub.add_parser("dataset-schema", help="Show dataset schema")
    ps.add_argument("--dataset", required=True)

    pq = sub.add_parser("query", help="Run a JSON spec query")
    pq.add_argument("--spec", required=True, help="Inline JSON or @spec.json")

    pr = sub.add_parser("recent", help="Show most recent learnings")
    pr.add_argument("--limit", type=int, default=20)

    precall = sub.add_parser("recall", help="Rank relevant learnings for a task")
    precall.add_argument("--query", required=True)
    precall.add_argument(
        "--paths",
        default="",
        help="Comma-separated path hints (boosts matches against context.paths)",
    )
    precall.add_argument("--limit", type=int, default=8)
    precall.add_argument("--format", choices=["table", "json"], default="table")
    precall.add_argument(
        "--drop-superseded",
        action="store_true",
        help="Exclude records that are superseded by a newer record",
    )

    pc = sub.add_parser(
        "codify-candidates",
        help="Suggest repeated/high-impact learnings to promote into durable docs",
    )
    pc.add_argument("--min-count", type=int, default=3)
    pc.add_argument("--limit", type=int, default=20)
    pc.add_argument("--format", choices=["table", "json"], default="table")
    pc.add_argument(
        "--drop-superseded",
        action="store_true",
        help="Exclude records that are superseded by a newer record",
    )

    return p


def main() -> int:
    args = build_parser().parse_args()
    if args.cmd == "datasets":
        out = cmd_datasets(args)
    elif args.cmd == "dataset-schema":
        out = cmd_dataset_schema(args)
    elif args.cmd == "query":
        out = cmd_query(args)
    elif args.cmd == "recent":
        out = cmd_recent(args)
    elif args.cmd == "recall":
        out = cmd_recall(args)
    elif args.cmd == "codify-candidates":
        out = cmd_codify_candidates(args)
    else:
        out = f"Unknown command: {args.cmd}"
    sys.stdout.write(out)
    if not out.endswith("\n"):
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
