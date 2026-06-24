#!/usr/bin/env -S uv run --with pyyaml python
"""Validate the Synesthesia skill package, routing corpus, and memory contract."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

import yaml


class CheckFailure(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CheckFailure(f"{path}: expected JSON object")
    return value


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise CheckFailure(f"{path}: missing frontmatter")
    try:
        _, raw, body = text.split("---\n", 2)
    except ValueError as exc:
        raise CheckFailure(f"{path}: unclosed frontmatter") from exc
    value = yaml.safe_load(raw)
    if not isinstance(value, dict):
        raise CheckFailure(f"{path}: invalid frontmatter")
    return value, body


def load_memory_adapter(repo_root: Path):
    path = (
        repo_root
        / "codex/skills/memory-source-notes/scripts/synesthesia_memory_note.py"
    )
    spec = importlib.util.spec_from_file_location("synesthesia_memory_note", path)
    if spec is None or spec.loader is None:
        raise CheckFailure(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_translation_cases(path: Path, errors: list[str]) -> None:
    data = load_json(path)
    if data.get("schema") != "synesthesia-translation-cases/v1":
        errors.append("translation-cases:schema")
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("translation-cases:empty")
        return
    required = {
        "evidence",
        "sensory_representation",
        "engineering_translation",
        "uncertainty",
        "falsifier",
        "decision_delta",
    }
    valid_count = 0
    invalid_count = 0
    for row in cases:
        if not isinstance(row, dict) or not row.get("id"):
            errors.append("translation-cases:invalid-row")
            continue
        mapping = row.get("mapping")
        if not isinstance(mapping, dict):
            errors.append(f"translation-cases:{row.get('id')}:mapping")
            continue
        missing = sorted(field for field in required if not mapping.get(field))
        declared_valid = row.get("valid") is True
        actual_valid = not missing
        if declared_valid:
            valid_count += 1
        else:
            invalid_count += 1
        if actual_valid != declared_valid:
            errors.append(
                f"translation-cases:{row.get('id')}:declared={declared_valid}:missing={missing}"
            )
    if valid_count == 0 or invalid_count == 0:
        errors.append("translation-cases:need-positive-and-negative")


def validate_routing_cases(path: Path, errors: list[str]) -> None:
    data = load_json(path)
    if data.get("schema") != "synesthesia-routing-cases/v1":
        errors.append("routing-cases:schema")
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("routing-cases:empty")
        return
    positives = [row for row in cases if isinstance(row, dict) and row.get("activate") is True]
    negatives = [row for row in cases if isinstance(row, dict) and row.get("activate") is False]
    if len(positives) < 4:
        errors.append("routing-cases:need-at-least-four-positive")
    if len(negatives) < 5:
        errors.append("routing-cases:need-at-least-five-negative")
    owners = {row.get("owner") for row in negatives}
    for owner in {"lift", "codebase-audit", "complexity-mitigator", "universalist", "zig"}:
        if owner not in owners:
            errors.append(f"routing-cases:missing-owner-near-miss:{owner}")
    if not any(row.get("mode") == "memory-admission" for row in positives):
        errors.append("routing-cases:missing-memory-admission")


def validate_memory_cases(path: Path, adapter: Any, errors: list[str]) -> None:
    data = load_json(path)
    if data.get("schema") != "synesthesia-memory-cases/v1":
        errors.append("memory-cases:schema")
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("memory-cases:empty")
        return
    valid_count = 0
    invalid_count = 0
    for row in cases:
        if not isinstance(row, dict):
            errors.append("memory-cases:invalid-row")
            continue
        case_id = row.get("id", "unknown")
        expected_valid = row.get("valid") is True
        try:
            physical, normalized = adapter.validate_and_normalize(
                row.get("logical_kind"), row.get("input")
            )
            canonical = adapter.canonical_json_bytes(normalized)
            if canonical != adapter.canonical_json_bytes(
                json.loads(canonical.decode("utf-8"))
            ):
                errors.append(f"memory-cases:{case_id}:noncanonical")
            if not expected_valid:
                errors.append(f"memory-cases:{case_id}:unexpected-pass")
            else:
                valid_count += 1
                if row.get("physical_kind") != physical:
                    errors.append(
                        f"memory-cases:{case_id}:physical-kind:{physical}"
                    )
        except adapter.ValidationError as exc:
            if expected_valid:
                errors.append(f"memory-cases:{case_id}:unexpected-fail:{exc}")
            else:
                invalid_count += 1
                needle = row.get("expected_error")
                if needle and needle not in str(exc):
                    errors.append(
                        f"memory-cases:{case_id}:error-mismatch:{exc}"
                    )
    if valid_count == 0 or invalid_count == 0:
        errors.append("memory-cases:need-positive-and-negative")


def validate_contract(path: Path, errors: list[str]) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    contract = data.get("skill_decision_contract") if isinstance(data, dict) else None
    if not isinstance(contract, dict):
        errors.append("decision-contract:missing-root")
        return
    if contract.get("contract_version") != "SKDC-v1":
        errors.append("decision-contract:version")
    skill = contract.get("skill")
    if not isinstance(skill, dict) or skill.get("name") != "synesthesia":
        errors.append("decision-contract:skill")
    triggers = contract.get("triggers")
    routes = contract.get("routes")
    clauses = contract.get("clauses")
    if not isinstance(triggers, list) or len(triggers) < 4:
        errors.append("decision-contract:triggers")
    if not isinstance(routes, list) or len(routes) < 6:
        errors.append("decision-contract:routes")
    if not isinstance(clauses, list) or len(clauses) < 3:
        errors.append("decision-contract:clauses")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parents[4]),
    )
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    skill_root = repo_root / "codex/skills/synesthesia"
    required = [
        skill_root / "SKILL.md",
        skill_root / "agents/openai.yaml",
        skill_root / "references/decision-contract.yaml",
        skill_root / "references/modality-selection.md",
        skill_root / "references/memory-admission.md",
        skill_root / "evals/routing-cases.json",
        skill_root / "evals/translation-cases.json",
        skill_root / "evals/memory-cases.json",
        repo_root
        / "codex/skills/memory-source-notes/scripts/synesthesia_memory_note.py",
        repo_root / "codex/memories/extensions/synesthesia/instructions.md",
        repo_root
        / "codex/memories/extensions/.templates/synesthesia-resource-template.md",
    ]
    errors: list[str] = []
    warnings: list[str] = []
    for path in required:
        if not path.is_file():
            errors.append(f"missing:{path.relative_to(repo_root)}")

    if errors:
        print(json.dumps({"synesthesia_validation": {"verdict": "fail", "errors": errors}}, indent=2))
        return 2

    frontmatter, body = parse_frontmatter(skill_root / "SKILL.md")
    if frontmatter.get("name") != "synesthesia":
        errors.append("frontmatter:name")
    version = str(frontmatter.get("metadata", {}).get("version", ""))
    if version != "3.1.0":
        errors.append(f"frontmatter:version:{version}")
    for phrase in (
        "representational ambiguity",
        "minimum sufficient",
        "falsifier",
        "Durable memory events",
        "same turn",
        "$memory-source-notes",
        "Do not activate merely because",
    ):
        if phrase.lower() not in body.lower():
            errors.append(f"skill:missing-contract-phrase:{phrase}")
    if "| Software property |" in body or "fixed universal mapping table" not in body:
        errors.append("skill:fixed-ontology-regression")

    interface = yaml.safe_load((skill_root / "agents/openai.yaml").read_text(encoding="utf-8"))
    prompt = interface.get("interface", {}).get("default_prompt", "") if isinstance(interface, dict) else ""
    for phrase in (
        "evidence-bound diagnostic lens",
        "representational ambiguity",
        "falsifier",
        "same turn",
        "$memory-source-notes",
    ):
        if phrase not in prompt:
            errors.append(f"interface:missing:{phrase}")

    validate_contract(skill_root / "references/decision-contract.yaml", errors)
    validate_routing_cases(skill_root / "evals/routing-cases.json", errors)
    validate_translation_cases(skill_root / "evals/translation-cases.json", errors)
    adapter = load_memory_adapter(repo_root)
    validate_memory_cases(skill_root / "evals/memory-cases.json", adapter, errors)

    template = (
        repo_root
        / "codex/memories/extensions/.templates/synesthesia-resource-template.md"
    ).read_text(encoding="utf-8")
    if template.count("source_note_ids") < 5:
        errors.append("resource-template:source-note-provenance")

    agents_path = repo_root / "codex/AGENTS.md"
    if agents_path.is_file():
        agents = agents_path.read_text(encoding="utf-8")
        if "representational ambiguity" not in agents:
            warnings.append("AGENTS.md does not contain narrowed Synesthesia routing")

    lint = repo_root / "codex/skills/tune/tools/decision_contract_lint.py"
    if lint.is_file():
        proc = subprocess.run(
            [
                sys.executable,
                str(lint),
                str(skill_root / "references/decision-contract.yaml"),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if proc.returncode != 0:
            errors.append(f"decision-contract-lint:{proc.stdout.strip()}:{proc.stderr.strip()}")

    result = {
        "synesthesia_validation": {
            "verdict": "pass" if not errors else "fail",
            "version": version,
            "errors": errors,
            "warnings": warnings,
            "checks": {
                "required_files": len(required),
                "routing_cases": len(load_json(skill_root / "evals/routing-cases.json")["cases"]),
                "translation_cases": len(load_json(skill_root / "evals/translation-cases.json")["cases"]),
                "memory_cases": len(load_json(skill_root / "evals/memory-cases.json")["cases"]),
            },
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
