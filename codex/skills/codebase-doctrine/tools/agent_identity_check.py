#!/usr/bin/env python3
"""Detect duplicate global agent names and verify Codebase Doctrine proof-worker identity."""

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


def load_agents(root: Path) -> tuple[dict[str, list[str]], list[str]]:
    names: dict[str, list[str]] = {}
    errors: list[str] = []

    if not root.is_dir():
        return names, [f"agents-root:not-directory:{root}"]

    for path in sorted(root.glob("*.toml")):
        try:
            value: dict[str, Any] = tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"parse:{path.name}:{exc}")
            continue

        name = value.get("name")
        if not isinstance(name, str) or not name:
            errors.append(f"name:missing:{path.name}")
            continue
        names.setdefault(name, []).append(path.name)

    return names, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--agents-root",
        default="codex/agents",
        help="Directory containing agent TOML files.",
    )
    parser.add_argument(
        "--require-codebase-doctrine-proof-mapper",
        action="store_true",
        help="Require the manually renamed Codebase Doctrine proof worker.",
    )
    args = parser.parse_args()

    agents_root = Path(args.agents_root).expanduser().resolve()
    names, errors = load_agents(agents_root)

    duplicates = {
        name: files
        for name, files in names.items()
        if len(files) > 1
    }
    for name, files in duplicates.items():
        errors.append(f"duplicate:{name}:{','.join(files)}")

    expected_path = agents_root / EXPECTED_FILE
    expected_status = "not-required"
    if args.require_codebase_doctrine_proof_mapper:
        if not expected_path.is_file():
            errors.append(f"expected-file:missing:{EXPECTED_FILE}")
            expected_status = "missing"
        elif EXPECTED_NAME not in names:
            errors.append(
                f"expected-name:missing:{EXPECTED_NAME}:{EXPECTED_FILE}"
            )
            expected_status = "wrong-name"
        elif expected_path.name not in names[EXPECTED_NAME]:
            errors.append(
                f"expected-name:file-mismatch:{EXPECTED_NAME}:{EXPECTED_FILE}"
            )
            expected_status = "wrong-file"
        else:
            expected_status = "present"

        general_files = names.get(GENERAL_NAME, [])
        if EXPECTED_FILE in general_files:
            errors.append(
                f"legacy-collision:{EXPECTED_FILE}:declares:{GENERAL_NAME}"
            )

    result = {
        "agent_identity_check": {
            "verdict": "pass" if not errors else "fail",
            "agents_root": str(agents_root),
            "agent_files": sum(len(files) for files in names.values()),
            "unique_names": len(names),
            "duplicates": duplicates,
            "codebase_doctrine_proof_mapper": expected_status,
            "errors": errors,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
