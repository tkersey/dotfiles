#!/usr/bin/env python3
"""Structural gate for ablation_certificate / ABL-CERT-v1."""

from __future__ import annotations
import re, sys
from pathlib import Path

REQUIRED = [
    r"ablation_certificate\s*:",
    r"certificate_version\s*:\s*ABL-CERT-v1",
    r"recipe_id\s*:",
    r"delivery_head\s*:",
    r"ablation_attempts\s*:",
    r"removed_from_recipe\s*:",
    r"survived_ablation\s*:",
    r"tests_merged_or_retired\s*:",
    r"production_surface\s*:",
    r"test_surface\s*:",
    r"gate\s*:",
]

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: ablation_certificate_gate.py <abl.yml>", file=sys.stderr)
        return 1
    text = Path(argv[1]).read_text(encoding="utf-8")
    errors = [f"missing:{pat}" for pat in REQUIRED if re.search(pat, text, re.M) is None]
    for field in [
        "every_new_surface_challenged",
        "production_net_justified",
    ]:
        if re.search(rf"{field}\s*:\s*fail", text, re.M):
            errors.append(f"{field}:fail")
    if re.search(r"final_delivery_patch_allowed\s*:\s*no", text, re.M):
        errors.append("final delivery patch not allowed")
    if errors:
        print("Ablation certificate gate: FAIL")
        for error in errors:
            print(error)
        return 2
    print("Ablation certificate gate: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
