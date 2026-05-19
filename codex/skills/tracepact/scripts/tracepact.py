#!/usr/bin/env python3
"""
TracePact

Normalize agentic traces, infer latency treaties, compute critical-path
approximations, detect mechanical efficiency issues, and emit Markdown, JSON,
or Graphviz DOT.

This script is intentionally conservative. It flags evidence-backed mechanical
issues and produces treaty hypotheses; a human/LLM reviewer should validate
semantic equivalence, safety, authority, freshness, and branch policies before
applying architectural rewrites.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

MODEL_KINDS = {"model", "llm", "response", "chat_completion", "completion", "planner", "router"}
TOOL_KINDS = {"tool", "function", "function_call", "retrieval", "mcp", "web_search", "file_search"}
UI_VALUES = {"progress", "partial", "final", "irreversible_action"}
MUTATING_HINTS = re.compile(r"\b(write|send|delete|remove|update|create|charge|pay|refund|book|reserve|post|email|sms|ship|transfer|commit|merge|deploy|execute|run_shell|apply_patch)\b", re.I)
READ_ONLY_HINTS = re.compile(r"\b(get|read|search|list|lookup|fetch|retrieve|query|find|load|inspect|weather|file_search|web_search)\b", re.I)
DETERMINISTIC_MODEL_HINTS = re.compile(r"\b(route|router|classif|format|parse|schema|validate|extract|rewrite|summarize|summaris|dedupe|rank|score)\b", re.I)


def stable_hash(value: Any, length: int = 12) -> Optional[str]:
    if value is None:
        return None
    try:
        payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    except TypeError:
        payload = str(value)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:length]


def first(d: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in d and d[key] is not None:
            return d[key]
    return default


def nested(d: Mapping[str, Any], *path: str) -> Any:
    cur: Any = d
    for key in path:
        if isinstance(cur, Mapping) and key in cur:
            cur = cur[key]
        else:
            return None
    return cur


def as_ms(value: Any) -> Optional[float]:
    """Coerce timestamps/durations into milliseconds where possible."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        f = float(value)
        # Heuristic for second-like durations/timestamps in logs.
        if 0 < f < 10_000 and not float(f).is_integer():
            return f * 1000.0
        return f
    if isinstance(value, str):
        try:
            return as_ms(float(value))
        except ValueError:
            return None
    return None


def token_value(obj: Mapping[str, Any], *paths: Tuple[str, ...]) -> Optional[int]:
    for path in paths:
        cur: Any = obj
        ok = True
        for part in path:
            if isinstance(cur, Mapping) and part in cur:
                cur = cur[part]
            else:
                ok = False
                break
        if ok and isinstance(cur, (int, float)):
            return int(cur)
    return None


def byte_size(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return len(json.dumps(value, ensure_ascii=False).encode("utf-8"))
    except Exception:
        return len(str(value).encode("utf-8"))


def output_size(obj: Mapping[str, Any]) -> Optional[int]:
    for key in ("tool_output", "output", "result", "content", "response", "text"):
        if key in obj and obj[key] is not None:
            return byte_size(obj[key])
    return None


def normalize_kind(raw_kind: Any, obj: Mapping[str, Any]) -> str:
    kind = str(raw_kind or "").lower()
    typ = str(first(obj, "type", "event", "event_type", default="")).lower()
    name = str(first(obj, "name", "tool_name", "function_name", "operation", default="")).lower()
    if kind in MODEL_KINDS or typ in {"response", "message", "model"} or first(obj, "model", "model_name"):
        return "model"
    if kind in TOOL_KINDS or typ in {"function_call", "tool_call", "function"} or first(obj, "tool_name", "function_name"):
        if "retriev" in name or "search" in name:
            return "retrieval"
        return "tool"
    if "guard" in kind or "moderation" in kind or "safety" in name:
        return "guardrail"
    if "handoff" in kind or "handoff" in name:
        return "handoff"
    if "cache" in kind or "cache" in name:
        return "cache"
    if "state" in kind or "load" in name and "state" in name:
        return "state"
    if "sleep" in kind or "poll" in name or "wait" in name:
        return "sleep"
    if "retry" in kind or "retry" in name:
        return "retry"
    if "ui" in kind or "render" in name or "stream" in name:
        return "ui"
    if "human" in kind or "approval" in name:
        return "human"
    if kind:
        return kind
    return "other"


def infer_mutability(kind: str, name: str, obj: Mapping[str, Any]) -> str:
    explicit = first(obj, "mutability", "side_effect", "effect")
    if explicit:
        s = str(explicit).lower()
        if s in {"read_only", "readonly", "read"}:
            return "read_only"
        if s in {"idempotent_write", "idempotent"}:
            return "idempotent_write"
        if s in {"external_write", "write", "mutating"}:
            return "external_write"
        if s in {"payment_or_irreversible", "irreversible", "payment"}:
            return "payment_or_irreversible"
    probe = " ".join(str(x or "") for x in (kind, name, first(obj, "tool_name", "function_name")))
    if MUTATING_HINTS.search(probe):
        if re.search(r"\b(charge|pay|payment|transfer|delete|deploy|send|email|sms|ship|commit|merge)\b", probe, re.I):
            return "payment_or_irreversible"
        return "external_write"
    if kind in {"tool", "retrieval", "cache", "state"} and READ_ONLY_HINTS.search(probe):
        return "read_only"
    if kind in {"model", "guardrail", "router", "planner", "ui", "sleep", "retry", "handoff"}:
        return "read_only"
    return "unknown"


def infer_usage(kind: str, mutability: str, obj: Mapping[str, Any]) -> str:
    explicit = first(obj, "usage_policy", "usage")
    if explicit and str(explicit).lower() in {"copyable", "replayable", "affine", "linear", "ephemeral", "unknown"}:
        return str(explicit).lower()
    if mutability in {"payment_or_irreversible"}:
        return "linear"
    if mutability == "external_write":
        return "affine"
    if kind in {"cache"}:
        return "replayable"
    if kind in {"retrieval"}:
        return "replayable"
    if mutability == "read_only":
        return "replayable"
    return "unknown"


def infer_freshness(kind: str, mutability: str, obj: Mapping[str, Any]) -> str:
    explicit = first(obj, "freshness_policy", "freshness")
    if explicit and str(explicit).lower() in {"fresh_required", "stale_ok", "cache_ok", "replay_only", "unknown"}:
        return str(explicit).lower()
    if kind == "cache":
        return "cache_ok"
    if mutability in {"payment_or_irreversible", "external_write"}:
        return "fresh_required"
    if kind in {"retrieval", "tool"} and mutability == "read_only":
        return "cache_ok"
    if kind == "model":
        return "unknown"
    return "unknown"


def infer_branch_policy(kind: str, mutability: str, usage: str, obj: Mapping[str, Any]) -> str:
    explicit = first(obj, "branch_policy", "branch")
    if explicit and str(explicit).lower() in {"unrestricted", "replay_only", "single_live_branch", "split_required", "no_branch", "host_owned", "unknown"}:
        return str(explicit).lower()
    if usage == "linear":
        return "single_live_branch"
    if usage == "affine":
        return "single_live_branch"
    if usage == "replayable":
        return "replay_only" if first(obj, "replay_only") else "unrestricted"
    return "unknown"


@dataclass
class Span:
    span_id: str
    kind: str
    name: str = ""
    parent_id: Optional[str] = None
    trace_id: Optional[str] = None
    turn_id: Optional[str] = None
    agent: Optional[str] = None
    start_ms: Optional[float] = None
    end_ms: Optional[float] = None
    duration_ms: Optional[float] = None
    status: Optional[str] = None
    depends_on: List[str] = field(default_factory=list)
    dependency_reasons: Dict[str, str] = field(default_factory=dict)
    consumed_by: List[str] = field(default_factory=list)
    result_consumed: Optional[bool] = None
    user_visible: str = "none"
    model: Optional[str] = None
    reasoning_effort: Optional[str] = None
    service_tier: Optional[str] = None
    transport: Optional[str] = None
    parallel_tool_calls: Optional[bool] = None
    structured_output: Optional[bool] = None
    streaming_used: Optional[bool] = None
    time_to_first_token_ms: Optional[float] = None
    time_to_first_user_visible_update_ms: Optional[float] = None
    input_tokens: Optional[int] = None
    cached_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    reasoning_tokens: Optional[int] = None
    tool_schema_tokens: Optional[int] = None
    retrieval_tokens: Optional[int] = None
    prompt_hash: Optional[str] = None
    static_prefix_hash: Optional[str] = None
    dynamic_suffix_hash: Optional[str] = None
    prompt_cache_key: Optional[str] = None
    prompt_cache_retention: Optional[str] = None
    tool_name: Optional[str] = None
    tool_args_hash: Optional[str] = None
    tool_result_bytes: Optional[int] = None
    tool_result_tokens: Optional[int] = None
    mutability: str = "unknown"
    usage_policy: str = "unknown"
    freshness_policy: str = "unknown"
    authority_policy: str = "unknown"
    branch_policy: str = "unknown"
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @property
    def duration(self) -> Optional[float]:
        if self.duration_ms is not None:
            return self.duration_ms
        if self.start_ms is not None and self.end_ms is not None:
            return max(0.0, self.end_ms - self.start_ms)
        return None

    @property
    def is_model(self) -> bool:
        return self.kind == "model" or bool(self.model)

    @property
    def is_toolish(self) -> bool:
        return self.kind in {"tool", "retrieval", "cache", "state"} or bool(self.tool_name)

    @property
    def is_read_only(self) -> bool:
        return self.mutability == "read_only"

    @property
    def label(self) -> str:
        if self.kind == "model" and self.model:
            return f"{self.name or 'model'} ({self.model})"
        if self.is_toolish and self.tool_name:
            return f"{self.kind}:{self.tool_name}"
        return f"{self.kind}:{self.name or self.span_id}"


def normalize_span(obj: Mapping[str, Any], index: int) -> Span:
    raw_kind = first(obj, "kind", "type", "span_type", "event_type")
    kind = normalize_kind(raw_kind, obj)
    name = str(first(obj, "name", "operation", "phase", "tool_name", "function_name", default=""))

    start = as_ms(first(obj, "start_ms", "start", "start_time_ms", "startTimeMs", "timestamp_ms", "timestamp"))
    end = as_ms(first(obj, "end_ms", "end", "end_time_ms", "endTimeMs"))
    duration = as_ms(first(obj, "duration_ms", "duration", "elapsed_ms", "latency_ms"))
    if duration is None and start is not None and end is not None:
        duration = max(0.0, end - start)

    depends_raw = first(obj, "depends_on", "dependencies", default=[])
    if isinstance(depends_raw, str):
        depends_on = [depends_raw]
    elif isinstance(depends_raw, Sequence) and not isinstance(depends_raw, (bytes, bytearray, str)):
        depends_on = [str(x) for x in depends_raw]
    else:
        depends_on = []

    dep_reasons = first(obj, "dependency_reasons", default={}) or {}
    if not isinstance(dep_reasons, Mapping):
        dep_reasons = {}

    consumed_raw = first(obj, "consumed_by", default=[])
    if isinstance(consumed_raw, str):
        consumed_by = [consumed_raw]
    elif isinstance(consumed_raw, Sequence) and not isinstance(consumed_raw, (bytes, bytearray, str)):
        consumed_by = [str(x) for x in consumed_raw]
    else:
        consumed_by = []

    tool_name = first(obj, "tool_name", "function_name")
    if kind in {"tool", "retrieval"} and not tool_name and name:
        tool_name = name

    mutability = infer_mutability(kind, name, obj)
    usage_policy = infer_usage(kind, mutability, obj)
    freshness_policy = infer_freshness(kind, mutability, obj)
    branch_policy = infer_branch_policy(kind, mutability, usage_policy, obj)

    user_visible = str(first(obj, "user_visible", "visibility", default="none") or "none").lower()
    if user_visible not in {"none", "progress", "partial", "final", "irreversible_action"}:
        user_visible = "none"

    return Span(
        span_id=str(first(obj, "span_id", "id", "call_id", "item_id", default=f"span_{index}")),
        trace_id=first(obj, "trace_id", "traceId"),
        parent_id=first(obj, "parent_id", "parent_span_id", "parentId"),
        turn_id=str(first(obj, "turn_id", "turn", default="")) or None,
        agent=first(obj, "agent", "agent_name"),
        kind=kind,
        name=name,
        start_ms=start,
        end_ms=end,
        duration_ms=duration,
        status=first(obj, "status", "outcome"),
        depends_on=depends_on,
        dependency_reasons={str(k): str(v) for k, v in dep_reasons.items()},
        consumed_by=consumed_by,
        result_consumed=first(obj, "result_consumed", "consumed"),
        user_visible=user_visible,
        model=first(obj, "model", "model_name"),
        reasoning_effort=first(obj, "reasoning_effort", "effort"),
        service_tier=first(obj, "service_tier"),
        transport=first(obj, "transport"),
        parallel_tool_calls=first(obj, "parallel_tool_calls"),
        structured_output=first(obj, "structured_output", "json_schema", "response_format"),
        streaming_used=first(obj, "streaming_used", "stream", "streamed"),
        time_to_first_token_ms=as_ms(first(obj, "time_to_first_token_ms", "ttft_ms")),
        time_to_first_user_visible_update_ms=as_ms(first(obj, "time_to_first_user_visible_update_ms", "ttfu_ms")),
        input_tokens=token_value(obj, ("input_tokens",), ("prompt_tokens",), ("usage", "input_tokens"), ("usage", "prompt_tokens"), ("usage", "input_tokens_details", "text_tokens"), ("token_usage", "input_tokens"), ("token_usage", "prompt_tokens")),
        cached_tokens=token_value(obj, ("cached_tokens",), ("usage", "prompt_tokens_details", "cached_tokens"), ("usage", "input_tokens_details", "cached_tokens"), ("token_usage", "prompt_tokens_details", "cached_tokens")),
        output_tokens=token_value(obj, ("output_tokens",), ("completion_tokens",), ("usage", "output_tokens"), ("usage", "completion_tokens"), ("token_usage", "output_tokens"), ("token_usage", "completion_tokens")),
        reasoning_tokens=token_value(obj, ("reasoning_tokens",), ("usage", "completion_tokens_details", "reasoning_tokens"), ("usage", "output_tokens_details", "reasoning_tokens"), ("token_usage", "output_tokens_details", "reasoning_tokens")),
        tool_schema_tokens=token_value(obj, ("tool_schema_tokens",), ("usage", "tool_schema_tokens")),
        retrieval_tokens=token_value(obj, ("retrieval_tokens",), ("usage", "retrieval_tokens")),
        prompt_hash=first(obj, "prompt_hash") or stable_hash(first(obj, "prompt", "input", "messages")),
        static_prefix_hash=first(obj, "static_prefix_hash"),
        dynamic_suffix_hash=first(obj, "dynamic_suffix_hash"),
        prompt_cache_key=first(obj, "prompt_cache_key"),
        prompt_cache_retention=first(obj, "prompt_cache_retention"),
        tool_name=str(tool_name) if tool_name else None,
        tool_args_hash=first(obj, "tool_args_hash", "args_hash") or stable_hash(first(obj, "arguments", "args", "parameters", "input")),
        tool_result_bytes=token_value(obj, ("tool_result_bytes",), ("result_bytes",)) or output_size(obj),
        tool_result_tokens=token_value(obj, ("tool_result_tokens",), ("result_tokens",)),
        mutability=mutability,
        usage_policy=usage_policy,
        freshness_policy=freshness_policy,
        authority_policy=str(first(obj, "authority_policy", "authority", default="unknown") or "unknown"),
        branch_policy=branch_policy,
        raw=dict(obj),
    )


def flatten_response_object(obj: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    """Best-effort conversion of a Responses API-like object into spans.

    Timing is usually unavailable in raw response objects, so this is mainly for
    token/tool accounting.
    """
    if not ("output" in obj and isinstance(obj.get("output"), list)):
        return [obj]
    root_id = str(first(obj, "id", "response_id", default="response_0"))
    spans: List[Mapping[str, Any]] = [
        {
            "span_id": root_id,
            "kind": "model",
            "name": "responses_api_call",
            "model": obj.get("model"),
            "usage": obj.get("usage"),
            "stream": obj.get("stream"),
            "parallel_tool_calls": obj.get("parallel_tool_calls"),
            "structured_output": bool(obj.get("text") or obj.get("response_format")),
            "user_visible": "final" if any(item.get("type") in {"message", "output_text"} for item in obj.get("output", []) if isinstance(item, Mapping)) else "none",
        }
    ]
    for i, item in enumerate(obj.get("output", [])):
        if not isinstance(item, Mapping):
            continue
        typ = str(item.get("type", "")).lower()
        if typ in {"function_call", "tool_call"}:
            spans.append(
                {
                    "span_id": str(item.get("id") or item.get("call_id") or f"{root_id}_tool_{i}"),
                    "parent_id": root_id,
                    "kind": "tool",
                    "name": item.get("name") or "function_call",
                    "tool_name": item.get("name"),
                    "arguments": item.get("arguments"),
                    "depends_on": [root_id],
                    "dependency_reasons": {root_id: "data"},
                    "user_visible": "none",
                }
            )
        elif typ in {"message", "output_text"}:
            spans.append(
                {
                    "span_id": str(item.get("id") or f"{root_id}_message_{i}"),
                    "parent_id": root_id,
                    "kind": "ui",
                    "name": "model_output",
                    "content": item.get("content") or item.get("text"),
                    "depends_on": [root_id],
                    "dependency_reasons": {root_id: "data"},
                    "user_visible": "final",
                }
            )
    return spans


def unwrap_trace_root(data: Any) -> List[Mapping[str, Any]]:
    if isinstance(data, list):
        rows: List[Mapping[str, Any]] = []
        for x in data:
            if isinstance(x, Mapping):
                rows.extend(flatten_response_object(x))
        return rows
    if not isinstance(data, Mapping):
        raise ValueError("Trace root must be a dict/list or JSONL objects")
    for key in ("spans", "events", "trace", "items", "data"):
        if isinstance(data.get(key), list):
            return unwrap_trace_root(data[key])
    return flatten_response_object(data)


def load_trace(path: Path) -> List[Span]:
    text = path.read_text(encoding="utf-8")
    rows: List[Mapping[str, Any]] = []
    try:
        data = json.loads(text)
        rows = unwrap_trace_root(data)
    except json.JSONDecodeError:
        for line_no, line in enumerate(text.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL on line {line_no}: {exc}") from exc
            if isinstance(obj, Mapping):
                rows.extend(flatten_response_object(obj))
    return [normalize_span(row, i) for i, row in enumerate(rows)]


def sorted_spans(spans: Sequence[Span]) -> List[Span]:
    return sorted(spans, key=lambda s: (math.inf if s.start_ms is None else s.start_ms, s.span_id))


def span_by_id(spans: Sequence[Span]) -> Dict[str, Span]:
    return {s.span_id: s for s in spans}


def infer_dependency_edges(spans: Sequence[Span]) -> Dict[str, List[str]]:
    """Return dependency edges predecessor -> [successors].

    Use explicit depends_on where present. Add parent edges. If no explicit
    dependencies exist and spans are strictly sequential, add conservative
    chronological edges only for critical-path approximation; mark them as
    inferred accidental by not mutating span.dependency_reasons.
    """
    ids = span_by_id(spans)
    edges: Dict[str, List[str]] = {s.span_id: [] for s in spans}
    any_explicit = False
    for s in spans:
        for dep in s.depends_on:
            if dep in ids:
                edges.setdefault(dep, []).append(s.span_id)
                any_explicit = True
        if s.parent_id and s.parent_id in ids:
            if s.span_id not in edges.setdefault(s.parent_id, []):
                edges[s.parent_id].append(s.span_id)
    # If no dependencies and spans have timings, make a conservative serial path
    # for estimating observed critical path. We do not treat this as proof.
    if not any_explicit:
        ordered = [s for s in sorted_spans(spans) if s.start_ms is not None]
        for prev, cur in zip(ordered, ordered[1:]):
            if cur.span_id not in edges.setdefault(prev.span_id, []):
                edges[prev.span_id].append(cur.span_id)
    return edges


def critical_path(spans: Sequence[Span]) -> Dict[str, Any]:
    ids = span_by_id(spans)
    if not spans:
        return {"duration_ms": None, "path": []}
    edges = infer_dependency_edges(spans)
    predecessors: Dict[str, List[str]] = {s.span_id: [] for s in spans}
    for a, outs in edges.items():
        for b in outs:
            predecessors.setdefault(b, []).append(a)

    # Topological-ish order: by start time, then stable id. This works for most traces.
    order = [s.span_id for s in sorted_spans(spans)]
    best: Dict[str, float] = {}
    back: Dict[str, Optional[str]] = {}
    for sid in order:
        s = ids[sid]
        dur = s.duration or 0.0
        preds = [p for p in predecessors.get(sid, []) if p in best]
        if preds:
            p = max(preds, key=lambda x: best[x])
            best[sid] = best[p] + dur
            back[sid] = p
        else:
            best[sid] = dur
            back[sid] = None
    if not best:
        return {"duration_ms": None, "path": []}
    end = max(best, key=lambda sid: best[sid])
    path: List[str] = []
    cur: Optional[str] = end
    while cur is not None:
        path.append(cur)
        cur = back.get(cur)
    path.reverse()
    return {
        "duration_ms": best[end],
        "path": path,
        "path_labels": [ids[sid].label for sid in path if sid in ids],
    }


def aggregate_metrics(spans: Sequence[Span]) -> Dict[str, Any]:
    starts = [s.start_ms for s in spans if s.start_ms is not None]
    ends = [s.end_ms for s in spans if s.end_ms is not None]
    input_tokens = sum(s.input_tokens or 0 for s in spans)
    cached_tokens = sum(s.cached_tokens or 0 for s in spans)
    output_tokens = sum(s.output_tokens or 0 for s in spans)
    reasoning_tokens = sum(s.reasoning_tokens or 0 for s in spans)
    tool_bytes = sum(s.tool_result_bytes or 0 for s in spans if s.is_toolish)
    user_visible_times = [s.end_ms for s in spans if s.user_visible in UI_VALUES and s.end_ms is not None]
    first_visible = min(user_visible_times) if user_visible_times else None
    e2e = (max(ends) - min(starts)) if starts and ends else None
    cp = critical_path(spans)
    return {
        "span_count": len(spans),
        "end_to_end_ms": e2e,
        "critical_path_duration_ms": cp.get("duration_ms"),
        "time_to_first_useful_output_ms": (first_visible - min(starts)) if first_visible is not None and starts else None,
        "model_request_count": sum(1 for s in spans if s.is_model),
        "tool_call_count": sum(1 for s in spans if s.is_toolish),
        "guardrail_count": sum(1 for s in spans if s.kind == "guardrail"),
        "handoff_count": sum(1 for s in spans if s.kind == "handoff"),
        "retry_count": sum(1 for s in spans if s.kind == "retry"),
        "input_tokens": input_tokens or None,
        "cached_tokens": cached_tokens or None,
        "cache_hit_ratio": (cached_tokens / input_tokens) if input_tokens else None,
        "output_tokens": output_tokens or None,
        "reasoning_tokens": reasoning_tokens or None,
        "tool_result_bytes": tool_bytes or None,
    }


def find_idle_gaps(spans: Sequence[Span], threshold_ms: float = 250.0) -> List[Tuple[Span, Span, float]]:
    ordered = [s for s in sorted_spans(spans) if s.start_ms is not None and s.end_ms is not None]
    gaps: List[Tuple[Span, Span, float]] = []
    for a, b in zip(ordered, ordered[1:]):
        gap = (b.start_ms or 0.0) - (a.end_ms or 0.0)
        if gap >= threshold_ms:
            gaps.append((a, b, gap))
    return gaps


def infer_critical_role(span: Span, all_spans: Sequence[Span], cp_ids: set[str]) -> str:
    if span.span_id in cp_ids:
        if span.kind in {"guardrail", "human"}:
            return "treaty_blocker"
        if span.user_visible in UI_VALUES:
            return "causal_witness"
        if span.result_consumed is False:
            return "coordination_waste"
        return "causal_witness"
    if span.kind in {"guardrail"}:
        return "policy_artifact"
    if span.result_consumed is False:
        return "coordination_waste"
    if span.usage_policy in {"replayable", "copyable"} and span.is_read_only:
        return "movable_witness"
    return "unknown"


def provider_offer(span: Span) -> str:
    if span.kind == "model":
        model = span.model or "unknown_model"
        effort = f", reasoning={span.reasoning_effort}" if span.reasoning_effort else ""
        return f"OpenAI model provider: {model}{effort}"
    if span.is_toolish:
        return f"Tool provider: {span.tool_name or span.name or span.kind} ({span.mutability}, {span.usage_policy})"
    if span.kind == "guardrail":
        return "Policy/guardrail provider"
    if span.kind == "cache":
        return "Replay/cache provider"
    if span.kind == "human":
        return "Human approval provider"
    return f"Provider for {span.kind}"


def morphism_offers(span: Span) -> List[str]:
    offers: List[str] = []
    label = f"{span.name} {span.tool_name or ''}".strip()
    if span.kind == "model":
        if DETERMINISTIC_MODEL_HINTS.search(label):
            offers.append("Replace with deterministic code or small-model fast path")
        if span.output_tokens and span.output_tokens > 300:
            offers.append("Use concise/structured output or max-output budget")
        if span.input_tokens and span.input_tokens >= 1024 and not span.cached_tokens:
            offers.append("Move static prompt/tools/schema to stable prefix and add prompt_cache_key strategy")
        if span.reasoning_tokens and span.reasoning_tokens > 0:
            offers.append("Route bounded execution to faster GPT workhorse; reserve reasoning model for planner")
        if span.streaming_used is False and (span.output_tokens or 0) > 200:
            offers.append("Stream safe partial output to improve TTFU")
    if span.is_toolish:
        if span.is_read_only:
            offers.append("Parallelize with independent read-only effects")
            offers.append("Cache/replay/journal equivalent request results")
        if span.tool_result_bytes and span.tool_result_bytes > 12_000:
            offers.append("Return bounded answer slice instead of raw result blob")
        if span.mutability in {"external_write", "payment_or_irreversible"}:
            offers.append("Wrap in linear/idempotent mutation treaty with rollback/cancel semantics")
    if span.kind == "guardrail":
        offers.append("Run policy check incrementally or in parallel where safe; preserve final gating")
    return offers


def compile_treaty(spans: Sequence[Span]) -> Dict[str, Any]:
    cp = critical_path(spans)
    cp_ids = set(cp.get("path", []))
    operations = []
    for s in sorted_spans(spans):
        role = infer_critical_role(s, spans, cp_ids)
        proof_needed: List[str] = []
        if s.usage_policy == "unknown":
            proof_needed.append("usage_policy")
        if s.freshness_policy == "unknown":
            proof_needed.append("freshness_policy")
        if s.mutability == "unknown" and s.is_toolish:
            proof_needed.append("mutability")
        if s.mutability in {"external_write", "payment_or_irreversible"}:
            proof_needed.extend(["idempotency_or_linearity", "rollback_or_cancel", "authority_scope"])
        legality = ""
        if role == "movable_witness":
            legality = "Read-only/replayable by inference; can move only if downstream consumption and freshness are confirmed."
        elif role == "coordination_waste":
            legality = "Observed result is marked unconsumed or duplicate; removal requires replay/eval confirmation."
        elif role == "treaty_blocker":
            legality = "Policy/authority/freshness blocker; optimize representation or placement, not semantics."
        elif role == "causal_witness":
            legality = "On observed critical path; rewrite requires preserving data, safety, authority, freshness, and quality semantics."
        else:
            legality = "Insufficient evidence; add dependency/consumption instrumentation."
        operations.append(
            {
                "id": s.span_id,
                "operation": s.label,
                "kind": s.kind,
                "provider_offer": provider_offer(s),
                "morphism_offers": morphism_offers(s),
                "observed_route": s.model or s.tool_name or s.name or s.kind,
                "dependencies": s.depends_on,
                "dependency_reasons": s.dependency_reasons,
                "usage_policy": s.usage_policy,
                "freshness_policy": s.freshness_policy,
                "authority_policy": s.authority_policy,
                "branch_policy": s.branch_policy,
                "cache_replay_policy": "cache_or_replay_ok" if s.freshness_policy in {"cache_ok", "stale_ok", "replay_only"} else "fresh_or_unknown",
                "critical_role": role,
                "rewrite_legality": legality,
                "proof_needed": sorted(set(proof_needed)),
            }
        )
    return {"version": "2.0.0", "trace_id": next((s.trace_id for s in spans if s.trace_id), None), "operations": operations}


def detect_findings(spans: Sequence[Span]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    ordered = sorted_spans(spans)
    ids = span_by_id(spans)

    def add(category: str, title: str, evidence: List[str], rewrite: str,
            severity: str = "medium", impact: str = "final", confidence: str = "medium",
            effort: str = "M", quality_risk: str = "low", safety_risk: str = "low",
            savings: str = "inferred", proof: Optional[List[str]] = None, rollback: str = "Feature flag or route fallback", validation: str = "Replay traces and compare quality/latency") -> None:
        findings.append({
            "id": f"F{len(findings)+1:02d}",
            "category": category,
            "title": title,
            "severity": severity,
            "critical_path_impact": impact,
            "expected_savings": savings,
            "confidence": confidence,
            "implementation_effort": effort,
            "quality_risk": quality_risk,
            "safety_risk": safety_risk,
            "evidence": evidence,
            "rewrite": rewrite,
            "proof_needed": proof or [],
            "rollback": rollback,
            "validation": validation,
        })

    # Consecutive model calls without intervening tools or user-visible output.
    model_streak: List[Span] = []
    for s in ordered + [Span(span_id="_sentinel", kind="other")]:
        if s.is_model:
            model_streak.append(s)
        else:
            if len(model_streak) >= 2:
                evidence = [f"{m.span_id}: {m.label}, duration={m.duration}ms" for m in model_streak]
                add(
                    "ROUND_TRIP_AMPLIFICATION",
                    "Consecutive model calls may be collapsible or routable",
                    evidence,
                    "Combine steps into one structured call, or split once into planner plus deterministic/fast executor only when the first call produces a consumed plan.",
                    severity="high",
                    impact="final",
                    confidence="medium",
                    effort="M",
                    savings="one or more model round trips if semantic dependencies are accidental",
                    proof=["verify second call consumes unique output from first", "quality eval for collapsed prompt"],
                )
            model_streak = []

    # Duplicate tool calls.
    seen_tools: Dict[Tuple[str, Optional[str]], List[Span]] = {}
    for s in spans:
        if s.is_toolish:
            key = (s.tool_name or s.name or s.kind, s.tool_args_hash)
            seen_tools.setdefault(key, []).append(s)
    for (tool, arg_hash), group in seen_tools.items():
        if len(group) > 1 and arg_hash:
            duplicate_ms = sum(g.duration or 0 for g in group[1:])
            add(
                "DUPLICATE_TOOL_CALL",
                f"Repeated equivalent tool call: {tool}",
                [f"{g.span_id}: args_hash={arg_hash}, duration={g.duration}ms" for g in group],
                "Memoize/journal the first result inside the run; for durable routes, add freshness and replay policy before reusing across runs.",
                severity="high",
                impact="final",
                confidence="high",
                effort="S",
                savings=f"up to {duplicate_ms:.0f}ms observed duplicate tool time" if duplicate_ms else "duplicate tool latency",
                proof=["freshness_policy", "result equivalence", "result was consumed identically"],
            )

    # Serialized read-only tools that could likely parallelize.
    tool_runs: List[Span] = []
    for s in ordered + [Span(span_id="_sentinel", kind="other")]:
        if s.is_toolish and s.is_read_only:
            tool_runs.append(s)
        else:
            if len(tool_runs) >= 2:
                durations = [t.duration or 0.0 for t in tool_runs]
                possible_savings = max(0.0, sum(durations) - max(durations)) if durations else 0.0
                add(
                    "SERIAL_READ_ONLY_TOOLS",
                    "Read-only tools appear serialized",
                    [f"{t.span_id}: {t.label}, duration={t.duration}ms, usage={t.usage_policy}" for t in tool_runs],
                    "Execute independent read-only tool calls concurrently, or issue them as a batch provider offer; preserve ordering only for data/authority/freshness edges.",
                    severity="high",
                    impact="final",
                    confidence="medium",
                    effort="S",
                    savings=f"up to {possible_savings:.0f}ms if independent" if possible_savings else "parallelization opportunity",
                    proof=["no data dependency between tools", "read-only/idempotent proof", "rate-limit budget"],
                )
            tool_runs = []

    # Tool result bloat.
    for s in spans:
        b = s.tool_result_bytes or 0
        toks = s.tool_result_tokens or 0
        if s.is_toolish and (b > 12_000 or toks > 1500):
            add(
                "TOOL_RESULT_BLOAT",
                f"Large tool result sent through agent loop: {s.label}",
                [f"{s.span_id}: result_bytes={b}, result_tokens={s.tool_result_tokens}"],
                "Change the provider contract to return a bounded answer slice: facts, citations/ids, confidence, and omitted-result count. Keep raw payload outside the model path.",
                severity="high",
                impact="final",
                confidence="high",
                effort="M",
                savings="input-token/prefill reduction and often fewer downstream summarization calls",
                proof=["consumer only needs answer slice", "answer-slice eval"],
            )

    # Low prompt cache ratio.
    for s in spans:
        if s.is_model and (s.input_tokens or 0) >= 1024:
            ratio = (s.cached_tokens or 0) / float(s.input_tokens or 1)
            if ratio < 0.25:
                add(
                    "LOW_CACHED_TOKEN_RATIO",
                    f"Long model prompt has poor cache reuse: {s.label}",
                    [f"{s.span_id}: input_tokens={s.input_tokens}, cached_tokens={s.cached_tokens}, ratio={ratio:.2f}, prompt_cache_key={s.prompt_cache_key}"],
                    "Move static instructions/examples/tools/schemas to the exact prefix, move dynamic history/RAG/user data later, stabilize JSON/tool ordering, and set a route-appropriate prompt_cache_key.",
                    severity="medium",
                    impact="throughput",
                    confidence="high",
                    effort="S",
                    savings="lower prefill latency/cost for repeated long-prefix routes",
                    proof=["stable prefix hash", "cache hit ratio dashboard"],
                )

    # Excessive output tokens / missing streaming.
    for s in spans:
        if s.is_model and (s.output_tokens or 0) >= 500:
            add(
                "EXCESSIVE_OUTPUT_TOKENS",
                f"Large model output likely dominates decode latency: {s.label}",
                [f"{s.span_id}: output_tokens={s.output_tokens}, streaming_used={s.streaming_used}"],
                "Use a shorter answer contract, structured fields, max output budget, or progressive rendering. If the long output is necessary, stream safe partial content.",
                severity="medium",
                impact="ttfu" if s.streaming_used is False else "final",
                confidence="high",
                effort="S",
                savings="decode latency roughly scales with generated tokens; TTFU improves with streaming",
                proof=["quality eval for shorter output", "streaming safety gate"],
            )
        elif s.is_model and s.streaming_used is False and (s.duration or 0) > 2500:
            add(
                "STREAMING_NOT_USED",
                f"Long model call does not stream: {s.label}",
                [f"{s.span_id}: duration={s.duration}ms, streaming_used={s.streaming_used}"],
                "Enable streaming and emit safe progress/partial answer before final validation when possible.",
                severity="medium",
                impact="ttfu",
                confidence="medium",
                effort="S",
                savings="user-perceived latency, not necessarily final latency",
                proof=["partial output is safe", "UI can handle streamed deltas"],
            )

    # Reasoning model or reasoning tokens used for deterministic-ish work.
    for s in spans:
        label = f"{s.name} {s.model or ''}".lower()
        if s.is_model and ((s.reasoning_tokens or 0) > 0 or "o" in str(s.model or "").lower()) and DETERMINISTIC_MODEL_HINTS.search(label):
            add(
                "UNNECESSARY_REASONING_MODEL",
                f"Reasoning model/tokens used for deterministic-ish work: {s.label}",
                [f"{s.span_id}: model={s.model}, reasoning_tokens={s.reasoning_tokens}, name={s.name}"],
                "Move this route to deterministic code or a faster GPT executor; keep reasoning model only for ambiguous planning or high-reliability decisions.",
                severity="medium",
                impact="final",
                confidence="medium",
                effort="M",
                savings="model latency/cost reduction on this route",
                proof=["task is bounded/deterministic", "routing eval"],
            )

    # Idle gaps.
    for a, b, gap in find_idle_gaps(spans):
        add(
            "POLLING_SLEEP_GAP",
            "Idle gap on observed timeline",
            [f"gap={gap:.0f}ms between {a.span_id} ({a.label}) and {b.span_id} ({b.label})"],
            "Replace fixed sleeps/polling with event-driven continuation, shorter adaptive backoff, or parallel hidden work during the wait.",
            severity="medium",
            impact="final",
            confidence="high",
            effort="S",
            savings=f"up to {gap:.0f}ms if gap is avoidable",
            proof=["gap is not external provider latency", "event-driven wakeup available"],
        )

    # Tool-heavy long chains -> WebSocket candidate.
    if sum(1 for s in spans if s.is_toolish) >= 8 and sum(1 for s in spans if s.is_model) >= 4:
        add(
            "STATE_REHYDRATION_TAX",
            "Long model-tool chain likely pays repeated continuation overhead",
            [f"model_requests={sum(1 for s in spans if s.is_model)}, tool_calls={sum(1 for s in spans if s.is_toolish)}"],
            "Consider persistent transport / incremental continuation, compact state, and stable prompt prefix. For OpenAI, evaluate Responses WebSocket mode for long tool-call-heavy loops.",
            severity="medium",
            impact="final",
            confidence="medium",
            effort="M",
            savings="per-turn overhead reduction on long chains",
            proof=["chain length distribution", "transport benchmark"],
        )

    # Missing mutation treaty.
    for s in spans:
        if s.is_toolish and s.mutability in {"external_write", "payment_or_irreversible"}:
            missing = []
            if s.usage_policy not in {"affine", "linear"}:
                missing.append("usage_policy")
            if s.authority_policy in {"unknown", ""}:
                missing.append("authority_policy")
            if s.branch_policy in {"unknown", "unrestricted"}:
                missing.append("branch_policy")
            if missing:
                add(
                    "MUTATION_WITHOUT_TREATY",
                    f"Mutating tool lacks explicit treaty metadata: {s.label}",
                    [f"{s.span_id}: mutability={s.mutability}, usage={s.usage_policy}, authority={s.authority_policy}, branch={s.branch_policy}"],
                    "Add a mutation treaty: scoped authority, idempotency key, linear/affine usage, branch policy, cancellation/rollback, and duplicate-execution guard.",
                    severity="critical",
                    impact="irreversible",
                    confidence="high",
                    effort="M",
                    quality_risk="low",
                    safety_risk="high",
                    savings="enables safe scheduling decisions; not a direct latency cut until proof exists",
                    proof=missing,
                    rollback="Disable speculative/parallel mutation route; fall back to current serial behavior",
                    validation="Replay branch tests and duplicate-mutation tests before enabling any schedule change",
                )

    return findings


def counterfactual_schedules(spans: Sequence[Span], findings: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    schedules: List[Dict[str, Any]] = []
    cats = {f.get("category") for f in findings}
    if "SERIAL_READ_ONLY_TOOLS" in cats:
        schedules.append({
            "name": "parallel_read_only_effects",
            "rewrite": "Group independent read-only tool/retrieval calls after the planning boundary and execute them concurrently; return compact answer slices to the final model call.",
            "legality": "Legal only for read-only/idempotent effects with no data dependency between them and acceptable freshness/cache policy.",
            "estimated_savings_ms": None,
            "risk": "May increase provider load or rate-limit pressure; cap concurrency and preserve cancellation.",
            "validation": "Trace dependency reasons, compare final quality, monitor rate limits and tool failure fanout.",
        })
    if "ROUND_TRIP_AMPLIFICATION" in cats:
        schedules.append({
            "name": "collapse_serial_model_round_trips",
            "rewrite": "Replace serial planner/executor/formatter model calls with one structured response or a planner once plus deterministic/fast executor steps.",
            "legality": "Legal if intermediate natural language is not a required user-visible artifact and downstream calls consume only structured decisions.",
            "estimated_savings_ms": None,
            "risk": "Prompt complexity may rise; validate accuracy and parse stability.",
            "validation": "Golden eval tasks, parse-failure rate, model-request count per task, p95 final latency.",
        })
    if "LOW_CACHED_TOKEN_RATIO" in cats:
        schedules.append({
            "name": "stable_prefix_cache_treaty",
            "rewrite": "Freeze instructions, examples, tool schemas, and structured output schema at the prompt prefix; move dynamic content later; set prompt_cache_key by route/prefix family.",
            "legality": "Semantics unchanged if only prompt ordering changes and the final prompt content remains equivalent.",
            "estimated_savings_ms": None,
            "risk": "Accidental prompt behavior change from ordering; eval before rollout.",
            "validation": "cached_tokens/input_tokens by route, answer quality eval, p95 prefill latency.",
        })
    if "TOOL_RESULT_BLOAT" in cats:
        schedules.append({
            "name": "provider_answer_slice",
            "rewrite": "Change tools/retrievers to return bounded answer slices with ids/citations/confidence instead of raw documents or full payloads in the model path.",
            "legality": "Legal if the downstream model only requires the slice; raw payload can remain available outside the model path for audit/drilldown.",
            "estimated_savings_ms": None,
            "risk": "Could omit relevant context; use retrieval eval and fallback expansion.",
            "validation": "Answer quality, omitted-context error rate, tool result token budget, fallback expansion rate.",
        })
    if any(f.get("category") == "MUTATION_WITHOUT_TREATY" for f in findings):
        schedules.append({
            "name": "mutation_treaty_before_speed",
            "rewrite": "Do not parallelize mutating effects yet. First add scoped authority, idempotency keys, linear/affine usage, branch policy, and rollback/cancel events.",
            "legality": "This is prerequisite proof; no faster mutation schedule is legal until the treaty exists.",
            "estimated_savings_ms": None,
            "risk": "Low quality risk; high safety value.",
            "validation": "Duplicate mutation tests, branch replay tests, rollback/cancel tests.",
        })
    if not schedules:
        schedules.append({
            "name": "instrument_before_rewrite",
            "rewrite": "Add dependency, consumption, mutability, freshness, token/cache, and TTFU instrumentation before making architectural changes.",
            "legality": "Conservative; avoids optimizing accidental guesses.",
            "estimated_savings_ms": None,
            "risk": "Low.",
            "validation": "Trace completeness score and re-run compiler on new traces.",
        })
    return schedules


def validation_plan(findings: Sequence[Mapping[str, Any]]) -> List[str]:
    plan = [
        "Replay golden traces and compare final outputs, tool outputs, and safety decisions.",
        "Track p50/p95/p99 end-to-end latency, TTFU, model request count, tool call count, serial depth, and idle gaps.",
        "Track input, cached, output, reasoning, retrieval, and tool-result tokens by route.",
        "Add a CI gate: no new serial model round trip on the dominant route without an explicit treaty blocker.",
    ]
    cats = {f.get("category") for f in findings}
    if "MUTATION_WITHOUT_TREATY" in cats:
        plan.append("Before any mutation scheduling change, run duplicate-execution, branch-replay, idempotency, rollback, and authority-scope tests.")
    if "LOW_CACHED_TOKEN_RATIO" in cats:
        plan.append("Add cache-hit dashboard: cached_tokens / input_tokens by prompt prefix and prompt_cache_key.")
    if "TOOL_RESULT_BLOAT" in cats:
        plan.append("Add answer-slice retrieval eval: compact tool output must preserve answer quality and citations/ids.")
    if "SERIAL_READ_ONLY_TOOLS" in cats:
        plan.append("A/B concurrency limits and monitor rate limits, provider errors, and tail latency.")
    return plan


def build_report(spans: Sequence[Span]) -> Dict[str, Any]:
    metrics = aggregate_metrics(spans)
    cp = critical_path(spans)
    treaty = compile_treaty(spans)
    findings = detect_findings(spans)
    schedules = counterfactual_schedules(spans, findings)
    treaty["counterfactual_schedules"] = schedules
    verdict = "Add instrumentation first; no high-confidence latency rewrite found."
    if findings:
        top = findings[0]
        verdict = f"Highest-leverage observed issue: {top['title']} ({top['category']}). Rewrite: {top['rewrite']}"
    return {
        "verdict": verdict,
        "metrics": metrics,
        "critical_path": cp,
        "latency_treaty": treaty,
        "findings": findings,
        "counterfactual_schedules": schedules,
        "validation_plan": validation_plan(findings),
        "patch_plan": patch_plan(findings),
    }


def patch_plan(findings: Sequence[Mapping[str, Any]]) -> List[str]:
    steps = []
    cats = [f.get("category") for f in findings]
    if "DUPLICATE_TOOL_CALL" in cats:
        steps.append("Add per-run tool-result memoization keyed by tool name, normalized args hash, freshness policy, and authority scope.")
    if "SERIAL_READ_ONLY_TOOLS" in cats:
        steps.append("Introduce an async tool batch executor for read-only/idempotent effects; require dependency reasons for serial edges.")
    if "ROUND_TRIP_AMPLIFICATION" in cats:
        steps.append("Refactor planner/executor sequence into one structured model response or a planner-once plus deterministic executor path.")
    if "LOW_CACHED_TOKEN_RATIO" in cats:
        steps.append("Refactor prompt builder into static_prefix + dynamic_suffix; sort JSON/tool schemas deterministically; set prompt_cache_key by prefix family.")
    if "TOOL_RESULT_BLOAT" in cats:
        steps.append("Modify providers to return compact answer slices and keep raw payloads in external storage by id.")
    if "STREAMING_NOT_USED" in cats or "EXCESSIVE_OUTPUT_TOKENS" in cats:
        steps.append("Enable streaming on long-generation routes and add a safe progress/partial-output UI path.")
    if "MUTATION_WITHOUT_TREATY" in cats:
        steps.append("Add mutation treaty metadata: scoped authority, idempotency key, linear/affine usage, branch policy, rollback/cancel event.")
    if not steps:
        steps.append("Add missing trace fields: dependency reasons, consumed_by, mutability, usage/freshness/branch policy, cache metrics, and TTFU.")
    steps.append("Ship behind a feature flag; compare old/new routes on golden traces and production canary.")
    return steps


def fmt_ms(value: Any) -> str:
    if value is None:
        return "unknown"
    try:
        return f"{float(value):.0f}ms"
    except Exception:
        return str(value)


def format_markdown(report: Mapping[str, Any]) -> str:
    metrics = report["metrics"]
    cp = report["critical_path"]
    treaty = report["latency_treaty"]
    findings = report["findings"]
    out: List[str] = []
    out.append("# TracePact Report")
    out.append("")
    out.append("## 1. Verdict")
    out.append("")
    out.append(str(report["verdict"]))
    out.append("")
    out.append("## 2. Metrics")
    out.append("")
    for k in ["span_count", "end_to_end_ms", "critical_path_duration_ms", "time_to_first_useful_output_ms", "model_request_count", "tool_call_count", "guardrail_count", "handoff_count", "retry_count", "input_tokens", "cached_tokens", "cache_hit_ratio", "output_tokens", "reasoning_tokens", "tool_result_bytes"]:
        v = metrics.get(k)
        if k.endswith("_ms"):
            v = fmt_ms(v)
        elif k == "cache_hit_ratio" and v is not None:
            v = f"{float(v):.2%}"
        out.append(f"- **{k}**: {v if v is not None else 'unknown'}")
    out.append("")
    out.append("## 3. Critical path approximation")
    out.append("")
    out.append(f"- **duration**: {fmt_ms(cp.get('duration_ms'))}")
    if cp.get("path_labels"):
        out.append("- **path**:")
        for sid, label in zip(cp.get("path", []), cp.get("path_labels", [])):
            out.append(f"  - `{sid}` — {label}")
    else:
        out.append("- No path could be reconstructed from the available trace.")
    out.append("")
    out.append("## 4. Latency Treaty IR")
    out.append("")
    out.append("| id | op | usage | freshness | authority | branch | critical role | proof needed |")
    out.append("|---|---|---|---|---|---|---|---|")
    for op in treaty.get("operations", []):
        out.append(
            "| {id} | {operation} | {usage_policy} | {freshness_policy} | {authority_policy} | {branch_policy} | {critical_role} | {proof} |".format(
                id=op["id"],
                operation=str(op["operation"]).replace("|", "/"),
                usage_policy=op.get("usage_policy", "unknown"),
                freshness_policy=op.get("freshness_policy", "unknown"),
                authority_policy=str(op.get("authority_policy", "unknown")).replace("|", "/"),
                branch_policy=op.get("branch_policy", "unknown"),
                critical_role=op.get("critical_role", "unknown"),
                proof=", ".join(op.get("proof_needed") or []) or "—",
            )
        )
    out.append("")
    out.append("## 5. Findings")
    out.append("")
    if not findings:
        out.append("No high-confidence mechanical findings. Add richer instrumentation for semantic rewrites.")
    for f in findings:
        out.append(f"### {f['id']}: {f['title']}")
        out.append("")
        out.append(f"- **Category**: `{f['category']}`")
        out.append(f"- **Severity**: {f['severity']}")
        out.append(f"- **Impact**: {f['critical_path_impact']}")
        out.append(f"- **Expected savings**: {f['expected_savings']}")
        out.append(f"- **Confidence**: {f['confidence']}")
        out.append(f"- **Effort**: {f['implementation_effort']}")
        out.append(f"- **Quality risk**: {f['quality_risk']}")
        out.append(f"- **Safety risk**: {f['safety_risk']}")
        out.append("- **Evidence**:")
        for ev in f.get("evidence", []):
            out.append(f"  - {ev}")
        out.append(f"- **Rewrite**: {f['rewrite']}")
        out.append(f"- **Proof needed**: {', '.join(f.get('proof_needed') or []) or '—'}")
        out.append(f"- **Rollback**: {f['rollback']}")
        out.append(f"- **Validation**: {f['validation']}")
        out.append("")
    out.append("## 6. Counterfactual schedules")
    out.append("")
    for s in report.get("counterfactual_schedules", []):
        out.append(f"### {s['name']}")
        out.append(f"- **Rewrite**: {s['rewrite']}")
        out.append(f"- **Legality**: {s['legality']}")
        out.append(f"- **Risk**: {s['risk']}")
        out.append(f"- **Validation**: {s['validation']}")
        out.append("")
    out.append("## 7. Patch plan")
    out.append("")
    for step in report.get("patch_plan", []):
        out.append(f"- {step}")
    out.append("")
    out.append("## 8. Validation plan")
    out.append("")
    for step in report.get("validation_plan", []):
        out.append(f"- {step}")
    out.append("")
    return "\n".join(out)


def format_dot(report: Mapping[str, Any], spans: Sequence[Span]) -> str:
    ids = span_by_id(spans)
    cp_ids = set(report.get("critical_path", {}).get("path", []))
    edges = infer_dependency_edges(spans)
    lines = ["digraph tracepact {", "  rankdir=LR;", "  node [shape=box, fontname=Helvetica];"]
    for s in sorted_spans(spans):
        label = f"{s.span_id}\n{s.label}\n{fmt_ms(s.duration)}\n{s.usage_policy}/{s.freshness_policy}"
        attrs = []
        if s.span_id in cp_ids:
            attrs.append('penwidth=3')
        if s.kind == "model":
            attrs.append('shape=box')
        elif s.is_toolish:
            attrs.append('shape=component')
        elif s.kind == "guardrail":
            attrs.append('shape=octagon')
        attr = ", ".join(attrs)
        lines.append(f'  "{s.span_id}" [label="{label}"{", " + attr if attr else ""}];')
    for a, outs in edges.items():
        for b in outs:
            if a in ids and b in ids:
                reason = ids[b].dependency_reasons.get(a, "")
                label = f' [label="{reason}"]' if reason else ""
                lines.append(f'  "{a}" -> "{b}"{label};')
    lines.append("}")
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Compile agentic traces into latency treaty reports.")
    parser.add_argument("trace", type=Path, help="JSON or JSONL trace file")
    parser.add_argument("--format", choices=["markdown", "json", "dot"], default="markdown")
    parser.add_argument("--output", type=Path, help="Optional output file")
    args = parser.parse_args(argv)

    try:
        spans = load_trace(args.trace)
        report = build_report(spans)
        if args.format == "json":
            payload = json.dumps(report, indent=2, sort_keys=True)
        elif args.format == "dot":
            payload = format_dot(report, spans)
        else:
            payload = format_markdown(report)
        if args.output:
            args.output.write_text(payload, encoding="utf-8")
        else:
            print(payload)
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
