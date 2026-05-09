#!/usr/bin/env python3
from __future__ import annotations
import sys
construction = sys.argv[1] if len(sys.argv) > 1 else "coproduct"
print(f"# Verification plan: {construction}")
print()
for h in ["Fastest credible proof signal", "Positive fixtures", "Negative fixtures", "Compatibility / parity fixtures", "Bypass checks", "Verification command"]:
    print(f"## {h}")
    print()
