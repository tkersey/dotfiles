#!/usr/bin/env python3
from __future__ import annotations

"""Summarize prompt-caching usage from OpenAI response logs.

Supports:
- JSON files containing one response object or a wrapper object
- JSONL files with one response or event per line

It looks for usage fields commonly seen in OpenAI responses:
- usage.input_tokens_details.cached_tokens
- usage.prompt_tokens_details.cached_tokens

Examples:
    python cache_metrics_report.py responses.jsonl
    python cache_metrics_report.py logs/*.jsonl --top-keys 20
"""

import argparse
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


def _as_dict(value: Any) -> dict[str, Any] | None:
    return value if isinstance(value, dict) else None


def _get_nested(obj: dict[str, Any] | None, *keys: str) -> Any:
    current: Any = obj
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _try_json_loads(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _iter_json_objects_from_path(path: Path) -> Iterable[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return

    whole = _try_json_loads(text)
    if isinstance(whole, dict):
        yield from _unwrap_object(whole)
        return
    if isinstance(whole, list):
        for item in whole:
            if isinstance(item, dict):
                yield from _unwrap_object(item)
        return

    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        obj = _try_json_loads(line)
        if not isinstance(obj, dict):
            print(
                f"warning: {path}:{lineno} is not valid JSON object; skipping",
                file=sys.stderr,
            )
            continue
        yield from _unwrap_object(obj)


def _unwrap_object(obj: dict[str, Any]) -> Iterable[dict[str, Any]]:
    """Yield candidate response-like objects with request metadata preserved when possible."""

    # Common envelope shapes:
    #   {"response": {...}, "request": {...}}
    #   {"request": {...}, "response": {...}}
    #   {"data": {...}}
    if isinstance(obj.get("response"), dict):
        response = dict(obj["response"])
        response.setdefault("_request", obj.get("request"))
        response.setdefault("_wrapper", obj)
        yield response
        return

    if isinstance(obj.get("data"), dict) and isinstance(obj["data"].get("usage"), dict):
        response = dict(obj["data"])
        response.setdefault("_request", obj.get("request"))
        response.setdefault("_wrapper", obj)
        yield response
        return

    # If it already looks like a response-like object, yield it directly.
    if isinstance(obj.get("usage"), dict) or "model" in obj or "id" in obj:
        yield obj


@dataclass
class Record:
    source: str
    model: str
    input_tokens: int
    cached_tokens: int
    cache_key: str | None
    retention: str | None
    reasoning_effort: str | None
    latency_ms: float | None


def _extract_request(obj: dict[str, Any]) -> dict[str, Any]:
    request = _as_dict(obj.get("_request"))
    if request:
        return request

    wrapper = _as_dict(obj.get("_wrapper")) or {}
    for key in ("request", "body", "payload"):
        candidate = _as_dict(wrapper.get(key))
        if candidate:
            return candidate
    return {}


def _extract_latency_ms(obj: dict[str, Any]) -> float | None:
    candidates = [
        obj.get("latency_ms"),
        obj.get("duration_ms"),
        obj.get("response_ms"),
        _get_nested(_as_dict(obj.get("_wrapper")), "latency_ms"),
        _get_nested(_as_dict(obj.get("_wrapper")), "duration_ms"),
        _get_nested(_as_dict(obj.get("_wrapper")), "response_ms"),
    ]
    for value in candidates:
        if isinstance(value, (int, float)) and value >= 0:
            return float(value)
    return None


def _extract_record(obj: dict[str, Any], source: str) -> Record | None:
    usage = _as_dict(obj.get("usage"))
    if not usage:
        return None

    input_tokens = usage.get("input_tokens")
    if input_tokens is None:
        input_tokens = usage.get("prompt_tokens")
    if not isinstance(input_tokens, (int, float)):
        return None

    details = _as_dict(usage.get("input_tokens_details"))
    if details is None:
        details = _as_dict(usage.get("prompt_tokens_details"))
    cached_tokens = 0
    if details and isinstance(details.get("cached_tokens"), (int, float)):
        cached_tokens = int(details["cached_tokens"])

    request = _extract_request(obj)

    model = obj.get("model") or request.get("model") or "unknown"
    cache_key = (
        request.get("prompt_cache_key")
        or obj.get("prompt_cache_key")
        or _get_nested(_as_dict(obj.get("_wrapper")), "prompt_cache_key")
    )
    retention = (
        request.get("prompt_cache_retention")
        or obj.get("prompt_cache_retention")
        or _get_nested(_as_dict(obj.get("_wrapper")), "prompt_cache_retention")
    )
    reasoning_effort = None
    reasoning = _as_dict(request.get("reasoning"))
    if reasoning and isinstance(reasoning.get("effort"), str):
        reasoning_effort = reasoning["effort"]

    return Record(
        source=source,
        model=str(model),
        input_tokens=int(input_tokens),
        cached_tokens=max(0, int(cached_tokens)),
        cache_key=str(cache_key) if cache_key is not None else None,
        retention=str(retention) if retention is not None else None,
        reasoning_effort=reasoning_effort,
        latency_ms=_extract_latency_ms(obj),
    )


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return math.nan
    values = sorted(values)
    if len(values) == 1:
        return values[0]
    rank = (len(values) - 1) * p
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return values[lower]
    weight = rank - lower
    return values[lower] * (1 - weight) + values[upper] * weight


def _format_ratio(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return "n/a"
    return f"{(100.0 * numerator / denominator):.2f}%"


def _print_latency_block(label: str, records: list[Record]) -> None:
    values = [r.latency_ms for r in records if r.latency_ms is not None]
    if not values:
        return
    mean = statistics.mean(values)
    p50 = _percentile(values, 0.50)
    p95 = _percentile(values, 0.95)
    print(f"{label} latency: mean={mean:.1f}ms p50={p50:.1f}ms p95={p95:.1f}ms")


def summarize(records: list[Record], top_keys: int) -> int:
    if not records:
        print("No response records with usage information were found.", file=sys.stderr)
        return 1

    total_input = sum(r.input_tokens for r in records)
    total_cached = sum(r.cached_tokens for r in records)
    any_hit = sum(1 for r in records if r.cached_tokens > 0)
    eligible = [r for r in records if r.input_tokens >= 1024]
    eligible_zero_hit = [r for r in eligible if r.cached_tokens == 0]

    print("OpenAI prompt caching report")
    print("=" * 28)
    print(f"Responses analyzed: {len(records)}")
    print(f"Total input/prompt tokens: {total_input:,}")
    print(f"Total cached tokens:      {total_cached:,}")
    print(f"Overall cache ratio:      {_format_ratio(total_cached, total_input)}")
    print(f"Requests with any hit:    {any_hit}/{len(records)} ({_format_ratio(any_hit, len(records))})")
    print(f"Eligible (>=1024 tokens): {len(eligible)}")
    print(f"Eligible with 0 hits:     {len(eligible_zero_hit)}")

    print()
    _print_latency_block("Overall", records)
    _print_latency_block("Cached", [r for r in records if r.cached_tokens > 0])
    _print_latency_block("Uncached", [r for r in records if r.cached_tokens == 0])

    by_model: dict[str, list[Record]] = defaultdict(list)
    for record in records:
        by_model[record.model].append(record)

    print()
    print("By model")
    print("-" * 28)
    for model, group in sorted(by_model.items(), key=lambda item: (-sum(r.input_tokens for r in item[1]), item[0])):
        group_input = sum(r.input_tokens for r in group)
        group_cached = sum(r.cached_tokens for r in group)
        group_hits = sum(1 for r in group if r.cached_tokens > 0)
        print(
            f"{model}: requests={len(group)}, "
            f"cache_ratio={_format_ratio(group_cached, group_input)}, "
            f"any_hit={_format_ratio(group_hits, len(group))}"
        )

    key_groups: dict[str, list[Record]] = defaultdict(list)
    for record in records:
        if record.cache_key:
            key_groups[record.cache_key].append(record)

    if key_groups:
        print()
        print(f"Top prompt_cache_key buckets (top {top_keys})")
        print("-" * 28)
        sorted_groups = sorted(
            key_groups.items(),
            key=lambda item: (-len(item[1]), item[0]),
        )[:top_keys]
        for key, group in sorted_groups:
            group_input = sum(r.input_tokens for r in group)
            group_cached = sum(r.cached_tokens for r in group)
            print(
                f"{key}: requests={len(group)}, "
                f"cache_ratio={_format_ratio(group_cached, group_input)}"
            )

    retention_counter = Counter(r.retention for r in records if r.retention)
    if retention_counter:
        print()
        print("Retention settings observed")
        print("-" * 28)
        for retention, count in retention_counter.most_common():
            print(f"{retention}: {count}")

    reasoning_counter = Counter(r.reasoning_effort for r in records if r.reasoning_effort)
    if reasoning_counter:
        print()
        print("Reasoning efforts observed")
        print("-" * 28)
        for effort, count in reasoning_counter.most_common():
            print(f"{effort}: {count}")

    print()
    print("Review cues")
    print("-" * 28)
    if eligible_zero_hit:
        print(
            f"- {len(eligible_zero_hit)} requests were eligible for prompt caching (>=1024 tokens) "
            "but showed zero cached tokens."
        )
        print("  Check for tool-array churn, schema changes, early timestamps, truncation, or unstable cache keys.")
    else:
        print("- No obvious zero-hit misses among cache-eligible requests.")

    if total_input > 0 and (total_cached / total_input) < 0.20:
        print("- Overall cache ratio is low. Review whether the stable prefix is large enough and actually repeated.")
    if key_groups and max(len(group) for group in key_groups.values()) > 50:
        print("- One or more cache-key buckets are high volume. Make sure buckets are not too broad for routing locality.")
    if not key_groups:
        print("- No prompt_cache_key values were found in the provided logs. That may be fine, but verify whether keys are set intentionally.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize OpenAI prompt-caching usage from response logs.")
    parser.add_argument("paths", nargs="+", help="JSON or JSONL files to analyze")
    parser.add_argument("--top-keys", type=int, default=10, help="Number of prompt_cache_key buckets to show")
    args = parser.parse_args()

    records: list[Record] = []
    for raw_path in args.paths:
        path = Path(raw_path)
        if not path.exists():
            print(f"warning: {path} does not exist; skipping", file=sys.stderr)
            continue
        for obj in _iter_json_objects_from_path(path):
            record = _extract_record(obj, source=str(path))
            if record is not None:
                records.append(record)

    return summarize(records, top_keys=args.top_keys)


if __name__ == "__main__":
    raise SystemExit(main())
