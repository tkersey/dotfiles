#!/usr/bin/env python3
from __future__ import annotations
import sys
lang = sys.argv[1] if len(sys.argv) > 1 else "typescript"
if lang in {"typescript","ts"}:
    print("""// Boundary adapter scaffold
export type LegacyShape = unknown;
export type CoreShape = unknown;
export function decodeLegacy(input: LegacyShape): CoreShape {
  return input as CoreShape;
}
export function encodeLegacy(core: CoreShape): LegacyShape {
  return core as LegacyShape;
}
""")
elif lang == "python":
    print("""# Boundary adapter scaffold
from typing import Any

def decode_legacy(value: Any) -> Any:
    return value

def encode_legacy(core: Any) -> Any:
    return core
""")
else:
    print("Boundary adapter scaffold: define decodeLegacy and encodeLegacy around the stable external shape.")
