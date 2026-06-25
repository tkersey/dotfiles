#!/usr/bin/env python3
"""Validate PSR-v1 policy_synthesis_receipt.

This gate is intentionally structural and conservative. It proves the plan
emitted a compact fixed-point synthesis receipt; it does not reveal or require
private reasoning.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._:-]{1,127}$")

LENSES = [
    "source_fidelity",
    "semantic_authority",
    "system_regime",
    "belief_and_observation",
    "action_completeness",
    "policy_closure",
    "safety_and_rollback",
    "proof_and_terminal_state",
    "simplicity_and_st_compileability",
]

PASS_DISPOSITIONS = {"changed", "clean", "blocked", "return_to_spec", "return_to_grill"}
RADICAL_DISPOSITIONS = {"adopt", "reject", "defer", "return_to_spec", "none"}


def load(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    value = json.loads(text) if path.endswith(".json") or yaml is None else yaml.safe_load(text)
    if not isinstance(value, dict):
        raise ValueError("document must be an object")
    body = value.get("policy_synthesis_receipt", value)
    if not isinstance(body, dict):
        raise ValueError("policy_synthesis_receipt must be an object")
    return body


def is_digest(value: Any) -> bool:
    return isinstance(value, str) and bool(DIGEST_RE.fullmatch(value))


def is_id(value: Any) -> bool:
    return isinstance(value, str) and bool(ID_RE.fullmatch(value))


def boolish(value: Any) -> bool:
    return isinstance(value, bool) or value in {"yes", "no", "pass", "fail"}


def positive(value: Any) -> bool:
    return value is True or value in {"yes", "pass"}


def validate(psr: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if psr.get("receipt_version") != "PSR-v1":
        errors.append("receipt_version")
    if not is_id(psr.get("plan_id")):
        errors.append("plan_id")
    if not isinstance(psr.get("revision"), int) or psr.get("revision", 0) < 1:
        errors.append("revision")
    for key in ("source_digest", "initial_policy_digest", "final_policy_digest"):
        if not is_digest(psr.get(key)):
            errors.append(key)

    passes = psr.get("passes")
    if not isinstance(passes, list) or not passes:
        errors.append("passes:must-be-nonempty-list")
        passes = []

    seen_lenses: set[str] = set()
    clean_lenses_in_tail: list[str] = []
    found_clean_sweep = False
    material_after_last_clean = False

    for i, row in enumerate(passes):
        prefix = f"passes[{i}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix}:must-be-object")
            continue
        if not is_id(row.get("pass_id")):
            errors.append(f"{prefix}.pass_id")
        lens = row.get("lens")
        if lens not in LENSES:
            errors.append(f"{prefix}.lens")
        if not is_digest(row.get("candidate_digest_before")):
            errors.append(f"{prefix}.candidate_digest_before")
        if not is_digest(row.get("candidate_digest_after")):
            errors.append(f"{prefix}.candidate_digest_after")
        findings = row.get("findings")
        changes = row.get("material_changes")
        if not isinstance(findings, list):
            errors.append(f"{prefix}.findings")
            findings = []
        if not isinstance(changes, list):
            errors.append(f"{prefix}.material_changes")
            changes = []
        disposition = row.get("disposition")
        if disposition not in PASS_DISPOSITIONS:
            errors.append(f"{prefix}.disposition")
        if disposition == "changed":
            if not changes:
                errors.append(f"{prefix}:changed-without-material_changes")
            if row.get("candidate_digest_before") == row.get("candidate_digest_after"):
                errors.append(f"{prefix}:changed-without-digest-change")
            clean_lenses_in_tail = []
            material_after_last_clean = True
        elif disposition == "clean":
            if changes:
                errors.append(f"{prefix}:clean-with-material_changes")
            if row.get("candidate_digest_before") != row.get("candidate_digest_after"):
                errors.append(f"{prefix}:clean-with-digest-change")
            if lens in LENSES:
                clean_lenses_in_tail.append(lens)
                if clean_lenses_in_tail[-len(LENSES):] == LENSES:
                    found_clean_sweep = True
                    material_after_last_clean = False
        elif disposition in {"blocked", "return_to_spec", "return_to_grill"}:
            if not findings:
                errors.append(f"{prefix}:{disposition}-requires-finding")
            clean_lenses_in_tail = []

        if lens in LENSES:
            seen_lenses.add(lens)

    missing_lenses = [lens for lens in LENSES if lens not in seen_lenses]
    if missing_lenses:
        errors.append("passes:missing-lenses:" + ",".join(missing_lenses))

    radical = psr.get("radical_candidate")
    if not isinstance(radical, dict):
        errors.append("radical_candidate:must-be-object")
        radical = {}
    disposition = radical.get("disposition")
    if disposition not in RADICAL_DISPOSITIONS:
        errors.append("radical_candidate.disposition")
    if disposition != "none" and not radical.get("candidate"):
        errors.append("radical_candidate.candidate")
    if not radical.get("reason"):
        errors.append("radical_candidate.reason")
    affected_refs = radical.get("affected_refs")
    if not isinstance(affected_refs, list):
        errors.append("radical_candidate.affected_refs")
    if disposition == "adopt" and psr.get("initial_policy_digest") == psr.get("final_policy_digest"):
        warnings.append("radical_candidate:adopt-without-overall-digest-change")

    convergence = psr.get("convergence")
    if not isinstance(convergence, dict):
        errors.append("convergence:must-be-object")
        convergence = {}
    for key in (
        "complete_clean_sweep",
        "independent_press_pass_clean",
        "improvements_exhausted",
    ):
        if not boolish(convergence.get(key)):
            errors.append(f"convergence.{key}")
    for key in ("unresolved_errors", "untreated_material_risks"):
        value = convergence.get(key)
        if not isinstance(value, int) or value < 0:
            errors.append(f"convergence.{key}")

    if positive(convergence.get("complete_clean_sweep")) and not found_clean_sweep:
        errors.append("convergence.complete_clean_sweep:not-supported-by-passes")
    if positive(convergence.get("improvements_exhausted")):
        if not positive(convergence.get("complete_clean_sweep")):
            errors.append("convergence.improvements_exhausted:requires-clean-sweep")
        if not positive(convergence.get("independent_press_pass_clean")):
            errors.append("convergence.improvements_exhausted:requires-press-pass")
        if convergence.get("unresolved_errors") != 0:
            errors.append("convergence.improvements_exhausted:unresolved-errors")
        if convergence.get("untreated_material_risks") != 0:
            errors.append("convergence.improvements_exhausted:untreated-risks")
        if disposition not in RADICAL_DISPOSITIONS:
            errors.append("convergence.improvements_exhausted:radical-candidate-invalid")
    if material_after_last_clean and positive(convergence.get("complete_clean_sweep")):
        errors.append("convergence.clean-sweep-after-last-material-change:not-proven")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    try:
        psr = load(args.file)
        errors, warnings = validate(psr)
    except Exception as exc:
        psr = {}
        errors, warnings = [str(exc)], []

    result = {
        "policy_synthesis_receipt_gate": {
            "verdict": "pass" if not errors else "fail",
            "plan_id": psr.get("plan_id"),
            "revision": psr.get("revision"),
            "pass_count": len(psr.get("passes", [])) if isinstance(psr.get("passes"), list) else 0,
            "radical_disposition": (
                psr.get("radical_candidate", {}).get("disposition")
                if isinstance(psr.get("radical_candidate"), dict)
                else None
            ),
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
