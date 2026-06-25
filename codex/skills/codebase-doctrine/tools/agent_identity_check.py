#!/usr/bin/env -S uv run python
"""Compatibility CLI for the skill-local Codebase Doctrine worker-suite check."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from worker_suite_check import validate_suite


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agents-root", default="codex/agents")
    parser.add_argument("--require-codebase-doctrine-proof-mapper", action="store_true")
    parser.add_argument("--registry")
    args = parser.parse_args()

    errors, warnings, counts = validate_suite(Path(args.agents_root).expanduser().resolve())
    if args.registry:
        warnings.append(
            "registry validation moved out of codebase-doctrine; --registry is ignored"
        )
    result = {
        "agent_identity_check": {
            "verdict": "pass" if not errors else "fail",
            "agents_root": str(Path(args.agents_root).expanduser().resolve()),
            "codebase_doctrine_worker_suite": "present" if not errors else "invalid",
            "counts": counts,
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
