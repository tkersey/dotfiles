#!/usr/bin/env python3
"""Validate decision_reconstruction_record / DRR-v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

STABILITY = {"stable", "mixed", "unstable", "unavailable"}
CONFIDENCE = {"high", "medium", "low", "unknown"}


def load(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    value = json.loads(text)
    body = value.get("decision_reconstruction_record", value) if isinstance(value, dict) else value
    if not isinstance(body, dict):
        raise ValueError("decision_reconstruction_record must be an object")
    return body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []

    try:
        record = load(args.file)
    except Exception as exc:
        print(json.dumps({"drr_gate": {"verdict": "fail", "errors": [str(exc)]}}, indent=2))
        return 1

    if record.get("record_version") != "DRR-v1":
        errors.append("record_version")
    for key in ("record_id", "inquiry_id", "source_capsule_id", "question"):
        if not record.get(key):
            errors.append(key)
    if not isinstance(record.get("modes"), list) or not record["modes"]:
        errors.append("modes")


    source_governance = record.get("source_governance")
    if source_governance is not None:
        if not isinstance(source_governance, dict):
            errors.append("source_governance")
        else:
            required = source_governance.get("required")
            if required not in {True, False}:
                errors.append("source_governance.required")
            if required:
                if not source_governance.get("gate_id"):
                    errors.append("source_governance.gate_id")
                if not source_governance.get("workflow"):
                    errors.append("source_governance.workflow")
                if source_governance.get("verdict") not in {
                    "authoritative",
                    "declared_uncontrolled",
                    "incidental",
                    "ambiguous",
                    "absent",
                }:
                    errors.append("source_governance.verdict")
                if source_governance.get("replay_allowed") not in {True, False}:
                    errors.append("source_governance.replay_allowed")
                for key in ("governing_evidence_refs", "incidental_evidence_refs", "limitations"):
                    if not isinstance(source_governance.get(key), list):
                        errors.append(f"source_governance.{key}")
                if source_governance.get("verdict") in {"incidental", "ambiguous", "absent"}:
                    if source_governance.get("replay_allowed") is not False:
                        errors.append("source_governance:blocked-verdict-must-deny-replay")
                    population_for_gate = record.get("fork_population")
                    if isinstance(population_for_gate, dict) and population_for_gate.get("valid_receipts"):
                        errors.append("source_governance:blocked-verdict-has-valid-receipts")
    else:
        warnings.append("source_governance:not-recorded")

    historical = record.get("historical_evidence")
    if not isinstance(historical, dict):
        errors.append("historical_evidence")
    else:
        for key in ("explicit_at_time", "trace_inferred", "unknown"):
            if not isinstance(historical.get(key), list):
                errors.append(f"historical_evidence.{key}")

    population = record.get("fork_population")
    if not isinstance(population, dict):
        errors.append("fork_population")
        valid_count = 0
    else:
        valid = population.get("valid_receipts")
        invalid = population.get("invalid_receipts")
        if not isinstance(valid, list):
            errors.append("fork_population.valid_receipts")
            valid = []
        if not isinstance(invalid, list):
            errors.append("fork_population.invalid_receipts")
        valid_count = len(valid)
        for key in ("model_distribution", "horizon_distribution", "workspace_distribution"):
            if not isinstance(population.get(key), dict):
                errors.append(f"fork_population.{key}")

    rationale = record.get("rationale_reconstruction")
    if not isinstance(rationale, dict):
        errors.append("rationale_reconstruction")
    else:
        for key in ("consensus", "disagreements"):
            if not isinstance(rationale.get(key), list):
                errors.append(f"rationale_reconstruction.{key}")
        if rationale.get("confidence") not in CONFIDENCE:
            errors.append("rationale_reconstruction.confidence")

    counterfactual = record.get("counterfactual")
    if not isinstance(counterfactual, dict):
        errors.append("counterfactual")
    else:
        if not isinstance(counterfactual.get("selected_route_distribution"), dict):
            errors.append("counterfactual.selected_route_distribution")
        stability = counterfactual.get("historical_route_stability")
        if stability not in STABILITY:
            errors.append("counterfactual.historical_route_stability")
        if stability in {"stable", "mixed", "unstable"} and valid_count < 2:
            warnings.append("counterfactual:stability-from-small-sample")
        if not isinstance(counterfactual.get("route_flip_conditions"), list):
            errors.append("counterfactual.route_flip_conditions")

    effects = record.get("skill_and_instruction_effects")
    if not isinstance(effects, dict):
        errors.append("skill_and_instruction_effects")
    else:
        for key in (
            "historically_explicit",
            "ablation_supported",
            "fork_self_report_only",
            "unsupported",
        ):
            if not isinstance(effects.get(key), list):
                errors.append(f"skill_and_instruction_effects.{key}")

    hindsight = record.get("hindsight")
    if not isinstance(hindsight, dict):
        errors.append("hindsight")
    else:
        if not isinstance(hindsight.get("lessons"), list):
            errors.append("hindsight.lessons")
        if hindsight.get("kept_separate") not in {"yes", True}:
            errors.append("hindsight.kept_separate")

    for key in (
        "contradictions",
        "limitations",
        "allowed_claims",
        "prohibited_claims",
    ):
        if not isinstance(record.get(key), list):
            errors.append(key)
    if not record.get("prohibited_claims"):
        warnings.append("prohibited_claims:empty")
    if record.get("confidence") not in CONFIDENCE:
        errors.append("confidence")

    prohibited_text = " ".join(str(value).lower() for value in record.get("prohibited_claims", []))
    if "chain of thought" not in prohibited_text and "hidden" not in prohibited_text:
        warnings.append("prohibited_claims:missing-hidden-reasoning-boundary")

    result = {
        "drr_gate": {
            "verdict": "pass" if not errors else "fail",
            "record_id": record.get("record_id"),
            "valid_fork_receipts": valid_count,
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
