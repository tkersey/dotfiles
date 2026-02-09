#!/usr/bin/env -S uv run python
"""Pure read-view helpers for materialized st v3 plan state."""

from __future__ import annotations

from collections import OrderedDict
from typing import Any

try:  # Support package and script-style imports.
    from .st_eventlog_v3 import dependency_state, unresolved_dependency_ids
except ImportError:  # pragma: no cover
    from st_eventlog_v3 import dependency_state, unresolved_dependency_ids

CANONICAL_STATUSES = (
    "pending",
    "in_progress",
    "completed",
    "blocked",
    "deferred",
    "canceled",
)


def _enrich_item(
    item: dict[str, Any], items_ordered_dict: OrderedDict[str, dict[str, Any]]
) -> dict[str, Any]:
    row = dict(item)
    row["dep_state"] = dependency_state(item, items_ordered_dict)
    row["waiting_on"] = unresolved_dependency_ids(item, items_ordered_dict)
    return row


def enrich_items(items_ordered_dict: OrderedDict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [_enrich_item(item, items_ordered_dict) for item in items_ordered_dict.values()]


def ready_items(items_ordered_dict: OrderedDict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        item
        for item in enrich_items(items_ordered_dict)
        if item.get("status") == "pending" and item.get("dep_state") == "ready"
    ]


def blocked_items(items_ordered_dict: OrderedDict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        item
        for item in enrich_items(items_ordered_dict)
        if item.get("status") == "blocked"
        or (item.get("status") == "pending" and item.get("dep_state") == "waiting_on_deps")
    ]


def find_item(
    items_ordered_dict: OrderedDict[str, dict[str, Any]], item_id: str
) -> dict[str, Any] | None:
    item = items_ordered_dict.get(item_id)
    if item is None:
        return None
    return _enrich_item(item, items_ordered_dict)


def status_counts(items_ordered_dict: OrderedDict[str, dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {status: 0 for status in CANONICAL_STATUSES}
    for item in items_ordered_dict.values():
        status = str(item.get("status", ""))
        counts[status] = counts.get(status, 0) + 1
    return counts


def compact_wave_summary(items_ordered_dict: OrderedDict[str, dict[str, Any]]) -> dict[str, Any]:
    enriched = enrich_items(items_ordered_dict)
    counts = status_counts(items_ordered_dict)
    summary: dict[str, Any] = {
        "counts": {
            **counts,
            "total": len(enriched),
            "ready": sum(
                1
                for item in enriched
                if item.get("status") == "pending" and item.get("dep_state") == "ready"
            ),
            "blocked": sum(
                1
                for item in enriched
                if item.get("status") == "blocked"
                or (
                    item.get("status") == "pending"
                    and item.get("dep_state") == "waiting_on_deps"
                )
            ),
        }
    }
    in_progress = next((item.get("id") for item in enriched if item.get("status") == "in_progress"), None)
    if in_progress:
        summary["in_progress_id"] = in_progress
    return summary
