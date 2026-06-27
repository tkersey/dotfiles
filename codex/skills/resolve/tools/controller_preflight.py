#!/usr/bin/env python3
"""Fail-closed preflight for intent-closed resolve-c3."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from typing import Any

REQUIRED = (
    "acceptance_contract_v2",
    "sealed_review_horizon_v1",
    "review_batch_v1",
    "review_aperture_v1",
    "counterexample_v1",
    "counterexample_basis_v2",
    "minimum_behavioral_kernel_v1",
    "reduction_certificate_v1",
    "resolve_authority_chain_v1",
    "mutation_gate_v1",
    "closure_gate_v1",
    "review_potential_v1",
    "intent_closed_conformance_v1",
    "terminal_holdout_v1",
    "physical_apply",
    "physical_commit",
    "physical_push",
    "closure_horizon_v1",
)


def find_key(value: Any, key: str) -> Any:
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for child in value.values():
            found = find_key(child, key)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_key(child, key)
            if found is not None:
                return found
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", default="resolve-c3")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    path = shutil.which(args.binary)
    errors: list[str] = []
    warnings: list[str] = []
    capabilities: dict[str, Any] = {}
    version = None

    if path is None:
        errors.append("controller:not-found")
    else:
        version_proc = subprocess.run(
            [path, "--version"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if version_proc.returncode == 0:
            version = version_proc.stdout.strip() or version_proc.stderr.strip()
        else:
            warnings.append("controller:version-unavailable")

        proc = subprocess.run(
            [path, "capabilities", "--json"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if proc.returncode != 0:
            errors.append("controller:capabilities-command-failed")
            warnings.append(proc.stderr.strip()[:500])
        else:
            try:
                value = json.loads(proc.stdout)
                capabilities = value if isinstance(value, dict) else {}
            except json.JSONDecodeError as exc:
                errors.append(f"controller:capabilities-invalid-json:{exc}")

    feature_status: dict[str, bool] = {}
    for feature in REQUIRED:
        value = find_key(capabilities, feature)
        supported = value is True or value == "yes" or value == "supported"
        feature_status[feature] = supported
        if not supported:
            errors.append(f"missing-capability:{feature}")

    delivery_allowed = not errors
    result = {
        "resolve_controller_preflight": {
            "verdict": "pass" if delivery_allowed else "analysis-only",
            "binary": path,
            "version": version,
            "protocol_profile": "intent-closed-cegis-v1",
            "features": feature_status,
            "missing": [feature for feature, supported in feature_status.items() if not supported],
            "analysis_allowed": True,
            "delivery_mutation_allowed": delivery_allowed,
            "closure_allowed": delivery_allowed,
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if delivery_allowed else 2


if __name__ == "__main__":
    raise SystemExit(main())
