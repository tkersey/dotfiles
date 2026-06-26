#!/usr/bin/env python3
"""Fail-closed closure gate for material resolve-c3 campaign summaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


LEGAL_NEXT_ACTIONS = [
    "enter_or_repair_c3",
    "seal_batches",
    "compile_compression",
    "accept_kernel",
    "map_or_delete_orphans",
    "map_proof_actions",
    "reduce_semantic_surface_or_rebase_ac",
    "rerun_terminal_holdout",
]


class InputError(ValueError):
    pass


def load_json(path: str) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InputError(str(exc)) from exc
    if not isinstance(value, dict):
        raise InputError("summary must be an object")
    return value


def load_jsonl(path: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        for line_no, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise InputError(f"runs line {line_no}: {exc}") from exc
            if not isinstance(value, dict):
                raise InputError(f"runs line {line_no}: row must be an object")
            rows.append(value)
    except OSError as exc:
        raise InputError(str(exc)) from exc
    return rows


def object_field(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    return value if isinstance(value, dict) else {}


def boolish(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in {0, 1}:
        return bool(value)
    if isinstance(value, str):
        folded = value.strip().lower()
        if folded in {"true", "yes", "pass", "passed", "1"}:
            return True
        if folded in {"false", "no", "fail", "failed", "0", "none"}:
            return False
    return None


def truthy(value: Any) -> bool:
    return boolish(value) is True


def intish(value: Any) -> int | None:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, list):
        return len(value)
    if isinstance(value, dict):
        return len(value)
    if isinstance(value, str) and value.strip().isdigit():
        return int(value)
    return None


def counter(row: dict[str, Any], *keys: str) -> int:
    for key in keys:
        value = intish(row.get(key))
        if value is not None:
            return value
    return 0


def nested_counter(row: dict[str, Any], object_key: str, value_key: str) -> int:
    return counter(object_field(row, object_key), value_key)


def campaign_id(row: dict[str, Any]) -> str:
    value = row.get("campaign_id", row.get("campaign"))
    return value if isinstance(value, str) else ""


def rows_for_campaign(rows: list[dict[str, Any]], campaign: str) -> list[dict[str, Any]]:
    return [row for row in rows if campaign_id(row) == campaign]


def collect_campaign_ids(summary: dict[str, Any], rows: list[dict[str, Any]]) -> set[str]:
    ids: set[str] = set()
    direct = campaign_id(summary)
    if direct:
        ids.add(direct)

    campaigns = summary.get("campaigns")
    if isinstance(campaigns, list):
        for row in campaigns:
            if isinstance(row, dict):
                value = campaign_id(row)
                if value:
                    ids.add(value)
    elif isinstance(campaigns, dict):
        for key, value in campaigns.items():
            if isinstance(key, str) and key:
                ids.add(key)
            if isinstance(value, dict):
                nested = campaign_id(value)
                if nested:
                    ids.add(nested)

    for row in rows:
        value = campaign_id(row)
        if value:
            ids.add(value)
    return ids


def infer_campaign(summary: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    ids = collect_campaign_ids(summary, rows)
    if len(ids) == 1:
        return next(iter(ids))
    if not ids:
        return ""
    raise InputError("--campaign is required when multiple campaigns are present")


def summary_campaign(summary: dict[str, Any], campaign: str) -> dict[str, Any]:
    if campaign_id(summary) == campaign:
        return summary
    campaigns = summary.get("campaigns")
    if isinstance(campaigns, list):
        for row in campaigns:
            if isinstance(row, dict) and campaign_id(row) == campaign:
                return row
    if isinstance(campaigns, dict):
        value = campaigns.get(campaign)
        if isinstance(value, dict):
            return value
    if not campaign_id(summary) and "campaigns" not in summary:
        return summary
    return {}


def finding_bearing(row: dict[str, Any]) -> bool:
    return (
        truthy(row.get("finding_bearing_workflow"))
        or truthy(row.get("findings_present"))
        or counter(row, "findings_total", "findings", "raw_claims") > 0
    )


def material(row: dict[str, Any]) -> bool:
    return truthy(row.get("c3_required")) or finding_bearing(row)


def compression_ready(row: dict[str, Any]) -> bool:
    value = row.get("compression_state", row.get("closure_compression"))
    return isinstance(value, str) and bool(value.strip()) and value.strip().upper() != "NONE"


def strict_progress(row: dict[str, Any]) -> int:
    direct = intish(row.get("strict_progress"))
    if direct is not None:
        return direct
    potential = object_field(row, "potential")
    value = intish(potential.get("strict_progress"))
    if value is not None:
        return value
    if truthy(object_field(row, "review_potential").get("strict_progress")):
        return 1
    return 0


def class_mapped_wound_tests(row: dict[str, Any], wound_tests: int) -> bool:
    if wound_tests <= 0:
        return True
    if truthy(row.get("wound_specific_tests_class_mapped")) or truthy(row.get("wound_specific_class_mapped")):
        return True
    mapped = counter(row, "class_mapped_wound_specific_tests")
    return mapped >= wound_tests


def ac_rebased(row: dict[str, Any]) -> bool:
    return truthy(row.get("ac_rebased")) or truthy(row.get("explicit_ac_rebase")) or bool(row.get("ac_rebase_ref"))


def violation(scope: str, code: str, detail: str, row: dict[str, Any] | None = None) -> dict[str, Any]:
    item: dict[str, Any] = {"scope": scope, "code": code, "detail": detail}
    if row is not None and isinstance(row.get("run_id"), str):
        item["run_id"] = row["run_id"]
    return item


def open_batch_count(row: dict[str, Any]) -> int:
    return (
        counter(row, "open_batches", "open_batches_total")
        or counter(row, "open_batch_ids")
        or nested_counter(row, "review", "open_batch_ids")
    )


def unresolved_conformance_count(row: dict[str, Any]) -> int:
    conformance = object_field(row, "conformance")
    return counter(
        conformance,
        "novel_in_horizon_counterexamples",
        "unknown_counterexamples",
        "unresolved_counterexamples",
        "accepted_counterexamples",
    )


def unresolved_holdout_count(row: dict[str, Any]) -> int:
    holdout = object_field(row, "terminal_holdout")
    return counter(
        holdout,
        "unknown_counterexamples",
        "in_horizon_counterexamples",
        "novel_in_horizon_counterexamples",
        "unresolved_counterexamples",
    )


def proof_or_delivery_stale(row: dict[str, Any]) -> bool:
    proof_basis = object_field(row, "proof_basis")
    delivery = object_field(row, "delivery")
    gate = object_field(row, "gate")
    return (
        boolish(proof_basis.get("all_laws_covered")) is False
        or boolish(delivery.get("current_head_validation_passed")) is False
        or boolish(gate.get("proof_current")) is False
        or boolish(gate.get("delivery_current")) is False
    )


def collect_run_violations(row: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not truthy(row.get("c3_closed")):
        out.append(violation("run", "c3_required_without_c3_closure", "material run requires c3_closed=true", row))
    if not truthy(row.get("c3_entered")):
        out.append(violation("run", "c3_required_without_c3_entry", "material run requires c3_entered=true", row))
    if not compression_ready(row):
        out.append(violation("run", "compression_state_none", "compression_state missing or NONE", row))
    if finding_bearing(row) and counter(row, "batches_total") == 0:
        out.append(violation("run", "finding_workflow_without_batches", "batches_total=0 for a finding-bearing workflow", row))
    if open_batch_count(row) > 0:
        out.append(violation("run", "open_batches", "open batch indicators remain before closure", row))
    if not truthy(row.get("delivery_closed")):
        out.append(violation("run", "delivery_not_closed", "delivery_closed is not true", row))
    if not truthy(row.get("terminal_closed")):
        out.append(violation("run", "delivery_closed_without_terminal_closure", "delivery_closed=true while terminal_closed=false", row))
    if strict_progress(row) == 0:
        out.append(violation("run", "strict_progress_zero", "potential.strict_progress=0 for a material campaign", row))
    if not truthy(object_field(row, "kernel").get("accepted")) and not truthy(row.get("kernel_accepted")):
        out.append(violation("run", "kernel_not_accepted", "kernel.accepted is not true", row))
    orphan_count = counter(row, "orphan_code_constructs") or nested_counter(row, "realization_map", "orphan_code_constructs")
    if orphan_count > 0:
        out.append(violation("run", "orphan_code_constructs", "orphan_code_constructs > 0", row))
    unmapped_proof = counter(row, "unmapped_proof_actions") or nested_counter(row, "proof_basis", "unmapped_proof_actions")
    if unmapped_proof > 0:
        out.append(violation("run", "unmapped_proof_actions", "unmapped_proof_actions > 0", row))
    wound_tests = counter(row, "wound_specific_tests") or nested_counter(row, "proof_basis", "wound_specific_tests")
    if wound_tests > 0 and not class_mapped_wound_tests(row, wound_tests):
        out.append(violation("run", "unmapped_wound_specific_tests", "wound_specific_tests > 0 without class mapping", row))
    surface_delta = counter(row, "semantic_surface_delta")
    if surface_delta > 0 and not ac_rebased(row):
        out.append(violation("run", "semantic_surface_delta_without_ac_rebase", "semantic_surface_delta > 0 without explicit AC rebase", row))
    if unresolved_conformance_count(row) > 0:
        out.append(violation("run", "unresolved_conformance_evidence", "conformance unresolved counterexamples remain", row))
    if unresolved_holdout_count(row) > 0:
        out.append(violation("run", "unresolved_terminal_holdout_evidence", "terminal holdout unresolved counterexamples remain", row))
    if proof_or_delivery_stale(row):
        out.append(violation("run", "proof_or_delivery_not_current", "proof or delivery current gate is not true", row))
    return out


def collect_violations(summary: dict[str, Any], rows: list[dict[str, Any]], campaign: str) -> list[dict[str, Any]]:
    campaign_summary = summary_campaign(summary, campaign)
    campaign_rows = rows_for_campaign(rows, campaign)
    material_rows = [row for row in campaign_rows if material(row)]
    summary_material = material(campaign_summary)
    out: list[dict[str, Any]] = []

    if summary_material and not material_rows:
        out.append(violation("campaign", "material_campaign_without_runs", "material campaign has no material runs"))

    for row in material_rows:
        out.extend(collect_run_violations(row))

    aggregate_rows = [campaign_summary, *material_rows]
    if any(material(row) for row in aggregate_rows):
        if max((strict_progress(row) for row in aggregate_rows), default=0) == 0:
            out.append(violation("campaign", "campaign_strict_progress_zero", "potential.strict_progress=0 for a material campaign"))
        if any(counter(row, "orphan_code_constructs") > 0 for row in aggregate_rows):
            out.append(violation("campaign", "campaign_orphan_code_constructs", "orphan_code_constructs > 0"))
        if any(counter(row, "unmapped_proof_actions") > 0 for row in aggregate_rows):
            out.append(violation("campaign", "campaign_unmapped_proof_actions", "unmapped_proof_actions > 0"))
        if any(counter(row, "semantic_surface_delta") > 0 and not ac_rebased(row) for row in aggregate_rows):
            out.append(violation("campaign", "campaign_semantic_surface_delta_without_ac_rebase", "semantic_surface_delta > 0 without explicit AC rebase"))
    return out


def payload(summary: dict[str, Any], rows: list[dict[str, Any]], campaign: str) -> dict[str, Any]:
    violations = collect_violations(summary, rows, campaign)
    allowed = not violations
    return {
        "closure_allowed": allowed,
        "status": "allowed" if allowed else "blocked",
        "violations": violations,
        "legal_next_actions": [] if allowed else LEGAL_NEXT_ACTIONS,
    }


def emit_text(body: dict[str, Any]) -> None:
    if body["closure_allowed"]:
        print("closure allowed")
        return
    print("closure gate failed")
    print(f"remaining authority gaps: {len(body['violations'])}")
    print("legal_next_actions: " + json.dumps(body["legal_next_actions"], separators=(",", ":")))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--runs", required=True)
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()

    try:
        summary = load_json(args.summary)
        rows = load_jsonl(args.runs)
        campaign = args.campaign if args.campaign is not None else infer_campaign(summary, rows)
        body = payload(summary, rows, campaign)
    except InputError as exc:
        body = {
            "closure_allowed": False,
            "status": "error",
            "violations": [{"scope": "input", "code": "could_not_evaluate_input", "detail": str(exc)}],
            "legal_next_actions": ["block"],
        }
        print(json.dumps(body, indent=2, sort_keys=True))
        return 3

    if args.format == "text":
        emit_text(body)
    else:
        print(json.dumps(body, indent=2, sort_keys=True))
    return 0 if body["closure_allowed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
