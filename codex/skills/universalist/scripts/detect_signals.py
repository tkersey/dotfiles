#!/usr/bin/env python3
from __future__ import annotations
import re, sys
from pathlib import Path
PATTERNS = {
    "boolean/status matrix": [r"\bis[A-Z]", r"\bhas[A-Z]", r"status", r"state", r"null"],
    "repeated validation": [r"validate", r"assert", r"throw", r"raise"],
    "shared-key agreement": [r"accountId", r"customerId", r"tenantId", r"version"],
    "branchy policy": [r"if .*policy", r"switch", r"case"],
    "callback boundary": [r"callback", r"handler", r"lambda", r"=>", r"function"],
    "projection/lift": [r"project", r"serialize", r"toDTO", r"contract", r"required"],
}
def main() -> int:
    paths = [Path(p) for p in sys.argv[1:]] or [Path('.')]
    for path in paths:
        files = [path] if path.is_file() else [p for p in path.rglob('*') if p.is_file() and p.suffix in {'.ts','.js','.py','.go','.rs','.java','.kt','.swift','.hs','.md'}]
        for f in files[:200]:
            try: text = f.read_text(errors='ignore')
            except Exception: continue
            hits = [name for name,pats in PATTERNS.items() if any(re.search(p, text) for p in pats)]
            if hits: print(f"{f}: {', '.join(sorted(set(hits)))}")
    return 0
if __name__ == '__main__': raise SystemExit(main())
