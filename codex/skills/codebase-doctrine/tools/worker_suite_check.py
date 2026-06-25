#!/usr/bin/env -S uv run python
"""Validate only the Codebase Doctrine custom-worker suite."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tomllib
from typing import Any

REQUIRED = {
    "codebase-cartographer.toml": "codebase_cartographer",
    "authority-state-mapper.toml": "authority_state_mapper",
    "behavioral-law-miner.toml": "behavioral_law_miner",
    "failure-forensics-analyst.toml": "failure_forensics_analyst",
    "codebase-doctrine-proof-mapper.toml": "codebase_doctrine_proof_mapper",
    "doctrine-portfolio-skeptic.toml": "doctrine_portfolio_skeptic",
    "search-saturation-auditor.toml": "search_saturation_auditor",
}


def validate_suite(root: Path) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    names: dict[str, str] = {}
    for filename, expected_name in REQUIRED.items():
        path = root / filename
        if not path.is_file():
            errors.append(f"missing:{filename}")
            continue
        try:
            value = tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"parse:{filename}:{exc}")
            continue
        name = value.get("name")
        if name != expected_name:
            errors.append(f"name:{filename}:{name}:{expected_name}")
        if isinstance(name, str):
            if name in names:
                errors.append(f"duplicate-name:{name}:{names[name]}:{filename}")
            names[name] = filename
        if value.get("sandbox_mode") != "read-only":
            errors.append(f"sandbox:{filename}:must-be-read-only")
        instructions = str(value.get("developer_instructions", ""))
        required_phrases = (
            "$codebase-doctrine",
            "CBDP-v2",
            "Do not spawn subagents",
            "Do not edit",
            "assignment",
        )
        for phrase in required_phrases:
            if phrase.lower() not in instructions.lower():
                errors.append(f"instructions:{filename}:missing:{phrase}")
        forbidden = (
            "workspace-write",
            "create skill files",
            "own final doctrine",
            "emit Echo:",
        )
        for phrase in forbidden:
            if phrase.lower() in instructions.lower():
                errors.append(f"instructions:{filename}:forbidden:{phrase}")
    return errors, warnings, {
        "required": len(REQUIRED),
        "present": sum(1 for name in REQUIRED if (root / name).is_file()),
        "unique_names": len(names),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agents-root", default="codex/agents")
    args = parser.parse_args()
    root = Path(args.agents_root).expanduser().resolve()
    errors, warnings, counts = validate_suite(root)
    result = {
        "worker_suite_check": {
            "verdict": "pass" if not errors else "fail",
            "agents_root": str(root),
            "counts": counts,
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
