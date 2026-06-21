#!/usr/bin/env python3
"""Lightweight Universalist signal detector.

Heuristic only: this guides inspection, not architecture decisions. The scanner is
line-oriented to avoid pathological regex behavior on large files.
"""
from __future__ import annotations
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
patterns = [
    ("boolean/status matrix", re.compile(r"\b(is[A-Z][A-Za-z0-9_]*|has[A-Z][A-Za-z0-9_]*|status|state|deletedAt|publishedAt)\b")),
    ("repeated validation", re.compile(r"validate|is_valid|isValid|assert|guard|check|parse[A-Z]", re.I)),
    ("shared-id agreement", re.compile(r"\b(customerId|accountId|tenantId|userId|version)\b")),
    ("callback/handler boundary", re.compile(r"callback|handler|register|subscribe|on[A-Z]|strategy", re.I)),
    ("projection/query sprawl", re.compile(r"project|view|select|query|toDto|fromDto", re.I)),
    ("syntax/execution mix", re.compile(r"evaluate|interpret|execute|render|compile", re.I)),
    ("typed component wiring", re.compile(r"wire|pipeline|compose|connect|port|component|plugin|middleware|stage", re.I)),
    ("effect ordering", re.compile(r"parallel|concurrent|sequence|before|after|transaction|commit|rollback|await", re.I)),
]
skip_dirs = {".git", "node_modules", "target", "dist", "build", ".venv", "__pycache__"}
suffixes = {".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs", ".java", ".kt", ".swift", ".hs", ".md"}

if root.is_file():
    paths = [root]
else:
    paths = [p for p in root.rglob("*") if p.is_file() and not any(part in skip_dirs for part in p.parts)]

for path in paths:
    if path.suffix.lower() not in suffixes:
        continue
    try:
        lines = path.read_text(errors="ignore").splitlines()[:5000]
    except Exception:
        continue
    hits: list[str] = []
    for line in lines:
        if len(line) > 2000:
            line = line[:2000]
        for name, pat in patterns:
            if name not in hits and pat.search(line):
                hits.append(name)
        if len(hits) >= 4:
            break
    if hits:
        print(f"{path}: {', '.join(hits)}")
