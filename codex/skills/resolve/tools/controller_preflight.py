#!/usr/bin/env python3
"""Fail-closed capability check for the resolve-c3 MBK controller."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys

REQUIRED = {
    "campaign_base_v1",
    "minimum_behavioral_kernel_v1",
    "mbkc_v1",
    "kernel_quotient_v1",
    "semantic_surface_v1",
    "proof_compression_v1",
    "physical_apply",
    "physical_commit",
    "physical_push",
    "closure_horizon_v1",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--controller", default="resolve-c3")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    path = shutil.which(args.controller)
    result = {
        "controller_preflight": {
            "controller": args.controller,
            "path": path,
            "available": path is not None,
            "required": sorted(REQUIRED),
            "present": [],
            "missing": sorted(REQUIRED),
            "mutation_allowed": False,
        }
    }

    if path is None:
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2

    proc = subprocess.run(
        [path, "capabilities", "--json"],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        result["controller_preflight"]["error"] = (
            proc.stderr.strip() or proc.stdout.strip() or
            "controller lacks `capabilities --json`"
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        result["controller_preflight"]["error"] = f"invalid capability JSON: {exc}"
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2

    features = payload.get("resolve_c3_capabilities", {}).get("features", {})
    present = {name for name, enabled in features.items() if enabled is True}
    missing = REQUIRED - present
    result["controller_preflight"].update({
        "version": payload.get("resolve_c3_capabilities", {}).get("version"),
        "present": sorted(present & REQUIRED),
        "missing": sorted(missing),
        "mutation_allowed": not missing,
    })

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not missing else 2


if __name__ == "__main__":
    raise SystemExit(main())
