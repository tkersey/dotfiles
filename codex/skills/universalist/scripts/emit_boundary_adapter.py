#!/usr/bin/env python3
from __future__ import annotations
import sys
kind = sys.argv[1] if len(sys.argv) > 1 else "decoder"
language = sys.argv[2] if len(sys.argv) > 2 else "agnostic"
print(f"# Boundary adapter scaffold: {kind} ({language})")
print()
for h in ["External shape kept stable", "Internal stronger model", "Decode / adapt", "Encode / project", "Parity tests", "Runtime-only leftovers"]:
    print(f"## {h}")
    print()
