#!/usr/bin/env python3
"""Validate an IDR-v1 Ideate Result receipt.

Accepts JSON. If PyYAML is installed, YAML is accepted too.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

VALID_MODES = {"fast", "standard", "deep", "audit-only"}
VALID_STATES = {"portfolio_ready", "evidence_too_thin", "blocked_for_user_input", "no_breakthrough_found"}
YESNO = {"yes", "no"}


def load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise SystemExit(f"not JSON and PyYAML unavailable: {exc}")
        return yaml.safe_load(text)


def as_int(value: Any, field: str, errors: list[str]) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        errors.append(f"{field} must be a non-negative integer")
        return 0
    return value


def gate(obj: Any) -> list[str]:
    errors: list[str] = []
    root = obj.get("ideate_result") if isinstance(obj, dict) and "ideate_result" in obj else obj
    if not isinstance(root, dict):
        return ["receipt root must be an object or contain ideate_result object"]

    if root.get("receipt_version") != "IDR-v1":
        errors.append("receipt_version must be IDR-v1")
    mode = root.get("mode")
    if mode not in VALID_MODES:
        errors.append(f"mode must be one of {sorted(VALID_MODES)}")
    state = root.get("terminal_state")
    if state not in VALID_STATES:
        errors.append(f"terminal_state must be one of {sorted(VALID_STATES)}")

    evidence = as_int(root.get("evidence_sources_count"), "evidence_sources_count", errors)
    baseline = as_int(root.get("baseline_candidates_generated"), "baseline_candidates_generated", errors)
    shortlist = as_int(root.get("candidates_shortlisted"), "candidates_shortlisted", errors)

    for gate_name, count_name in (("glaze_gate", "material_delta_count"), ("asi_gate", "cash_out_count")):
        gate_obj = root.get(gate_name)
        if not isinstance(gate_obj, dict):
            errors.append(f"{gate_name} must be an object")
            continue
        if gate_obj.get("applied") not in YESNO:
            errors.append(f"{gate_name}.applied must be yes|no")
        as_int(gate_obj.get(count_name), f"{gate_name}.{count_name}", errors)

    overlap = root.get("overlap_check")
    if not isinstance(overlap, dict) or overlap.get("performed") not in YESNO:
        errors.append("overlap_check.performed must be yes|no")

    if root.get("seed_emitted") not in YESNO:
        errors.append("seed_emitted must be yes|no")

    if state == "portfolio_ready":
        if evidence <= 0:
            errors.append("portfolio_ready requires evidence_sources_count > 0")
        if baseline <= 0:
            errors.append("portfolio_ready requires baseline_candidates_generated > 0")
        if shortlist <= 0:
            errors.append("portfolio_ready requires candidates_shortlisted > 0")
        if root.get("seed_emitted") != "yes":
            errors.append("portfolio_ready requires seed_emitted=yes")
        for gate_name, count_name in (("glaze_gate", "material_delta_count"), ("asi_gate", "cash_out_count")):
            gate_obj = root.get(gate_name, {})
            if gate_obj.get("applied") != "yes":
                errors.append(f"portfolio_ready requires {gate_name}.applied=yes")
            elif isinstance(gate_obj.get(count_name), int) and gate_obj.get(count_name) <= 0:
                errors.append(f"portfolio_ready requires {gate_name}.{count_name} > 0")
        if overlap.get("performed") != "yes":
            errors.append("portfolio_ready requires overlap_check.performed=yes")

    if state == "evidence_too_thin" and root.get("seed_emitted") == "yes":
        errors.append("evidence_too_thin should not emit a seed by default")

    if mode == "audit-only" and state == "portfolio_ready":
        errors.append("audit-only should not normally end in portfolio_ready; choose fast/standard/deep or justify outside the receipt")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: ideate_result_gate.py <idr.json|yaml>", file=sys.stderr)
        return 2
    path = Path(argv[1])
    errors = gate(load(path))
    result = {"ok": not errors, "errors": errors}
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
