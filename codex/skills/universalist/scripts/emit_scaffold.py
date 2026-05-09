#!/usr/bin/env python3
from __future__ import annotations
import sys
construction = sys.argv[1] if len(sys.argv) > 1 else "coproduct"
language = sys.argv[2] if len(sys.argv) > 2 else "agnostic"
print(f"# Universalist scaffold: {construction} ({language})")
print()
for h in ["Signal", "One seam", "Smallest honest construction", "Constructor / introduction form", "Eliminator / projection / interpreter", "Compatibility plan", "Proof signal", "Negative fixture", "Stop point"]:
    print(f"## {h}")
    print()
