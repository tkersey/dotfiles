#!/usr/bin/env python3
"""Emit the complete human-facing Universalist report scaffold."""
from __future__ import annotations

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", nargs="?", default="report")
    parser.add_argument("language", nargs="?", default="agnostic")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    template = Path(__file__).resolve().parents[1] / "templates" / "universalist-report.md"
    text = template.read_text(encoding="utf-8")
    text = text.replace("# Universalist Report", f"# Universalist {args.kind.title()} Report", 1)
    print(f"<!-- language: {args.language} -->")
    print(text, end="" if text.endswith("\n") else "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
