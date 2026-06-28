#!/usr/bin/env python3
"""Validate skill_decision_contract / SKDC-v1."""

from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

ID_RE = re.compile(r"^[A-Z][A-Z0-9._-]{2,127}$")
KINDS = {"decision", "execution", "evidence", "orchestration", "workflow", "mixed"}
RECEIPT_POLICIES = {"required", "optional", "not-needed"}

def load(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    if path.endswith(".json"):
        value = json.loads(text)
    else:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML decision contracts")
        value = yaml.safe_load(text)
    if not isinstance(value, dict):
        raise ValueError("contract must be an object")
    return value.get("skill_decision_contract", value)

def collect_ids(rows: Any, key: str, label: str, errors: list[str]) -> set[str]:
    if not isinstance(rows, list):
        errors.append(f"{label}:must-be-list")
        return set()
    out: set[str] = set()
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"{label}[{i}]:must-be-object")
            continue
        value = row.get(key)
        if not isinstance(value, str) or not ID_RE.match(value):
            errors.append(f"{label}[{i}].{key}:invalid")
            continue
        if value in out:
            errors.append(f"{label}:{key}:duplicate:{value}")
        out.add(value)
    return out

def refs(row: dict[str, Any], key: str, allowed: set[str], prefix: str, errors: list[str]) -> None:
    values = row.get(key, [])
    if not isinstance(values, list):
        errors.append(f"{prefix}.{key}:must-be-list")
        return
    for value in values:
        if value not in allowed:
            errors.append(f"{prefix}.{key}:unknown:{value}")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    try:
        contract = load(args.file)
    except Exception as exc:
        print(json.dumps({"decision_contract_lint": {"verdict":"fail","errors":[str(exc)]}}, indent=2))
        return 1

    if contract.get("contract_version") != "SKDC-v1":
        errors.append("contract_version:expected-SKDC-v1")
    skill = contract.get("skill", {})
    if not isinstance(skill, dict):
        errors.append("skill:must-be-object")
        skill = {}
    if not skill.get("name"):
        errors.append("skill.name:missing")
    if skill.get("kind") not in KINDS:
        errors.append("skill.kind:invalid")
    if not skill.get("source_fingerprint"):
        warnings.append("skill.source_fingerprint:missing")

    trigger_ids = collect_ids(contract.get("triggers"), "trigger_id", "triggers", errors)
    route_ids = collect_ids(contract.get("routes"), "route_id", "routes", errors)
    clause_ids = collect_ids(contract.get("clauses"), "clause_id", "clauses", errors)

    if not trigger_ids:
        warnings.append("triggers:empty")
    if skill.get("kind") in {"decision", "mixed"} and not route_ids:
        errors.append("routes:required-for-decision-skill")
    if skill.get("kind") in {"decision", "mixed"} and not clause_ids:
        errors.append("clauses:required-for-decision-skill")

    for i, row in enumerate(contract.get("triggers", []) if isinstance(contract.get("triggers"), list) else []):
        if not row.get("description"):
            errors.append(f"triggers[{i}].description:missing")
        for field in ("cue_literals","cue_regexes","exclusions"):
            if not isinstance(row.get(field, []), list):
                errors.append(f"triggers[{i}].{field}:must-be-list")
        for pattern in row.get("cue_regexes", []) if isinstance(row.get("cue_regexes"), list) else []:
            try: re.compile(pattern)
            except re.error as exc: errors.append(f"triggers[{i}].cue_regexes:invalid:{exc}")

    for i, row in enumerate(contract.get("routes", []) if isinstance(contract.get("routes"), list) else []):
        if not row.get("description"):
            errors.append(f"routes[{i}].description:missing")
        if not isinstance(row.get("aliases", []), list):
            errors.append(f"routes[{i}].aliases:must-be-list")
        if row.get("terminal") not in {"yes","no",True,False}:
            errors.append(f"routes[{i}].terminal:invalid")

    for i, row in enumerate(contract.get("clauses", []) if isinstance(contract.get("clauses"), list) else []):
        prefix=f"clauses[{i}]"
        refs(row,"trigger_refs",trigger_ids,prefix,errors)
        refs(row,"expected_routes",route_ids,prefix,errors)
        refs(row,"prohibited_routes",route_ids,prefix,errors)
        if not row.get("expected_routes") and not row.get("prohibited_routes"):
            warnings.append(f"{prefix}:no-route-effect")
        for field in ("required_artifacts","success_signals","failure_signals"):
            if not isinstance(row.get(field, []), list):
                errors.append(f"{prefix}.{field}:must-be-list")
        if not row.get("rationale"):
            warnings.append(f"{prefix}.rationale:missing")

    instrumentation = contract.get("instrumentation", {})
    if not isinstance(instrumentation, dict):
        errors.append("instrumentation:must-be-object")
    elif instrumentation.get("decision_receipt") not in RECEIPT_POLICIES:
        errors.append("instrumentation.decision_receipt:invalid")

    result={"decision_contract_lint":{
        "verdict":"pass" if not errors else "fail",
        "counts":{"triggers":len(trigger_ids),"routes":len(route_ids),"clauses":len(clause_ids)},
        "errors":errors,"warnings":warnings}}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2

if __name__=="__main__":
    raise SystemExit(main())
