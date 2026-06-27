#!/usr/bin/env python3
"""PSR-v1 validation gate for $plan."""
from __future__ import annotations
import json, pathlib, sys
from typing import Any
try:
    import yaml
except Exception:
    yaml = None

def load(path: str) -> Any:
    text = pathlib.Path(path).read_text(encoding="utf-8")
    if path.endswith(".json"):
        return json.loads(text)
    if yaml is None:
        return json.loads(text)
    return yaml.safe_load(text)

def unwrap(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict) and "policy_synthesis_receipt" in obj:
        return obj["policy_synthesis_receipt"]
    if isinstance(obj, dict):
        return obj
    raise SystemExit("input must be an object")

def get(d: dict[str, Any], *path: str, default=None):
    cur: Any = d
    for part in path:
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: policy_synthesis_receipt_gate.py <psr-yaml-or-json>", file=sys.stderr)
        return 2
    psr = unwrap(load(argv[1]))
    errors: list[str] = []
    if psr.get("receipt_version") != "PSR-v1":
        errors.append("receipt_version must be PSR-v1")
    for key in ("plan_id", "revision", "source_digest", "initial_policy_digest", "final_policy_digest"):
        if not psr.get(key):
            errors.append(f"{key}: required")
    if not isinstance(psr.get("passes"), list) or not psr.get("passes"):
        errors.append("passes must be non-empty")
    if not get(psr, "radical_candidate", "disposition"):
        errors.append("radical_candidate.disposition: required")
    conv = psr.get("convergence") or {}
    for key in ("complete_clean_sweep", "independent_press_pass_clean", "improvements_exhausted"):
        if conv.get(key) is not True:
            errors.append(f"convergence.{key} must be true")
    if conv.get("unresolved_errors") not in ([], None):
        errors.append("convergence.unresolved_errors must be empty")
    if conv.get("untreated_material_risks") not in ([], None):
        errors.append("convergence.untreated_material_risks must be empty")
    if get(psr, "source_contract", "kind") == "PSC-v1":
        if get(psr, "source_contract", "source_owner") != "spec-pipeline":
            errors.append("PSC-v1 source_contract.source_owner must be spec-pipeline")
        if not get(psr, "source_contract", "spec_id"):
            errors.append("PSC-v1 source_contract.spec_id required")
    if errors:
        print("policy-synthesis-receipt: blocked", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    print("policy-synthesis-receipt: pass")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
