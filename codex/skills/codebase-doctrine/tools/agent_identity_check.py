#!/usr/bin/env -S uv run python
"""Validate custom-agent identity, lifecycle, aliases, authority, and registry coverage."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tomllib
from typing import Any

EXPECTED_FILE = "codebase-doctrine-proof-mapper.toml"
EXPECTED_NAME = "codebase_doctrine_proof_mapper"
GENERAL_NAME = "proof_surface_mapper"


def load_agents(root: Path) -> tuple[dict[str, list[str]], dict[str, dict[str, Any]], list[str]]:
    names: dict[str, list[str]] = {}
    values: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    if not root.is_dir():
        return names, values, [f"agents-root:not-directory:{root}"]
    for path in sorted(root.glob("*.toml")):
        try:
            value = tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"parse:{path.name}:{exc}")
            continue
        name = value.get("name")
        if not isinstance(name, str) or not name:
            errors.append(f"name:missing:{path.name}")
            continue
        names.setdefault(name, []).append(path.name)
        values[path.name] = value
    return names, values, errors


def load_registry(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot read registry {path}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agents-root", default="codex/agents")
    parser.add_argument("--registry")
    parser.add_argument("--require-codebase-doctrine-proof-mapper", action="store_true")
    args = parser.parse_args()

    agents_root = Path(args.agents_root).expanduser().resolve()
    registry_path = Path(args.registry).expanduser().resolve() if args.registry else None
    registry = load_registry(registry_path)
    registry_agents = registry.get("agents", {}) if isinstance(registry, dict) else {}
    aliases = registry.get("aliases", {}) if isinstance(registry, dict) else {}

    names, values, errors = load_agents(agents_root)
    duplicates = {name: files for name, files in names.items() if len(files) > 1}
    for name, files in duplicates.items():
        errors.append(f"duplicate:{name}:{','.join(files)}")

    expected_status = "not-required"
    if args.require_codebase_doctrine_proof_mapper:
        expected_path = agents_root / EXPECTED_FILE
        if not expected_path.is_file():
            errors.append(f"expected-file:missing:{EXPECTED_FILE}")
            expected_status = "missing"
        elif EXPECTED_NAME not in names:
            errors.append(f"expected-name:missing:{EXPECTED_NAME}:{EXPECTED_FILE}")
            expected_status = "wrong-name"
        elif EXPECTED_FILE not in names[EXPECTED_NAME]:
            errors.append(f"expected-name:file-mismatch:{EXPECTED_NAME}:{EXPECTED_FILE}")
            expected_status = "wrong-file"
        else:
            expected_status = "present"
        if EXPECTED_FILE in names.get(GENERAL_NAME, []):
            errors.append(f"legacy-collision:{EXPECTED_FILE}:declares:{GENERAL_NAME}")

    if registry_agents:
        actual_by_name = {name: files[0] for name, files in names.items() if len(files) == 1}
        for name, filename in actual_by_name.items():
            if name not in registry_agents:
                errors.append(f"registry:unregistered-agent:{name}:{filename}")
                continue
            entry = registry_agents[name]
            expected_file = Path(str(entry.get("path", ""))).name
            if expected_file and filename != expected_file:
                errors.append(f"registry:file-mismatch:{name}:{filename}:{expected_file}")
            value = values[filename]
            sandbox = value.get("sandbox_mode", "read-only")
            if sandbox != entry.get("sandbox"):
                errors.append(f"registry:sandbox-mismatch:{name}:{sandbox}:{entry.get('sandbox')}")
            if value.get("model_reasoning_effort", "medium") != entry.get("reasoning_effort", "medium"):
                errors.append(f"registry:reasoning-mismatch:{name}")
            if "specialist-packet-v2" not in str(value.get("developer_instructions", "")):
                errors.append(f"packet:v2-missing:{name}")
            if "Do not spawn subagents" not in str(value.get("developer_instructions", "")) and "do not spawn" not in str(value.get("developer_instructions", "")).lower():
                errors.append(f"recursion:guard-missing:{name}")
            if sandbox == "workspace-write":
                if entry.get("archetype") != "bounded-writer":
                    errors.append(f"writer:wrong-archetype:{name}")
                if entry.get("mutation_gate") != "root_authorized_bounded_seam":
                    errors.append(f"writer:gate-missing:{name}")

        for name, entry in registry_agents.items():
            if entry.get("status") in {"active", "compatibility"} and name not in actual_by_name:
                errors.append(f"registry:agent-file-missing:{name}:{entry.get('path')}")

        for alias, entry in aliases.items():
            canonical = entry.get("canonical")
            if canonical in aliases:
                errors.append(f"alias:chain:{alias}->{canonical}")
            if canonical not in registry_agents:
                errors.append(f"alias:canonical-missing:{alias}->{canonical}")
            if not entry.get("removal_condition"):
                errors.append(f"alias:removal-condition:{alias}")
            if entry.get("can_have_independent_behavior") is not False:
                errors.append(f"alias:independent-behavior:{alias}")

    result = {
        "agent_identity_check": {
            "verdict": "pass" if not errors else "fail",
            "agents_root": str(agents_root),
            "agent_files": sum(len(files) for files in names.values()),
            "unique_names": len(names),
            "duplicates": duplicates,
            "registry": str(registry_path) if registry_path else None,
            "aliases": aliases,
            "codebase_doctrine_proof_mapper": expected_status,
            "errors": errors,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
