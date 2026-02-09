"""Translate durable `$st` items into Codex `update_plan` payload entries."""

from __future__ import annotations

from typing import Any, TypedDict


STATUS_MAP: dict[str, str] = {
    "in_progress": "in_progress",
    "completed": "completed",
    "pending": "pending",
    "blocked": "pending",
    "deferred": "pending",
    "canceled": "pending",
}


class PlanEntry(TypedDict):
    step: str
    status: str


class UpdatePlanPayload(TypedDict):
    plan: list[PlanEntry]


def _map_status(item: dict[str, Any], *, index: int) -> str:
    raw_status = item.get("status")
    if not isinstance(raw_status, str):
        raise ValueError(f"item {index} missing string status")

    normalized_status = raw_status.strip().lower()
    if normalized_status not in STATUS_MAP:
        values = ", ".join(sorted(STATUS_MAP))
        raise ValueError(f"item {index} has invalid status '{raw_status}'; expected one of: {values}")

    mapped_status = STATUS_MAP[normalized_status]
    if item.get("dep_state") == "waiting_on_deps" and mapped_status == "in_progress":
        return "pending"
    return mapped_status


def build_update_plan(items: list[dict[str, Any]]) -> list[PlanEntry]:
    """Project `$st` items into `update_plan` entries in the same order."""

    plan_entries: list[PlanEntry] = []
    for index, item in enumerate(items):
        step = item.get("step")
        if not isinstance(step, str):
            raise ValueError(f"item {index} missing string step")
        plan_entries.append({"step": step, "status": _map_status(item, index=index)})
    return plan_entries


def build_update_plan_payload(items: list[dict[str, Any]]) -> UpdatePlanPayload:
    """Build a complete payload for Codex `update_plan`."""

    return {"plan": build_update_plan(items)}


def assert_no_drift(items: list[dict[str, Any]], plan_entries: list[dict[str, str]]) -> None:
    """Raise when supplied plan entries differ from current `$st` projection."""

    expected_entries = build_update_plan(items)
    if len(expected_entries) != len(plan_entries):
        raise ValueError("drift: item count mismatch between items and plan entries")

    for index, (expected, actual) in enumerate(zip(expected_entries, plan_entries)):
        if expected["step"] != actual.get("step") or expected["status"] != actual.get("status"):
            raise ValueError(
                "drift: mapped entry mismatch at index "
                f"{index} (expected step={expected['step']!r}, status={expected['status']!r}; "
                f"got step={actual.get('step')!r}, status={actual.get('status')!r})"
            )

