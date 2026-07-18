#!/usr/bin/env python3
"""Emit Universalist templates without duplicating their field contracts."""
from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATE_BY_KIND = {
    "report": "universalist-report.md",
    "plan": "universalist-plan.md",
    "universal-problem": "universal-problem-certificate.md",
    "certificate": "universal-problem-certificate.md",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", nargs="?", default="report", choices=sorted(TEMPLATE_BY_KIND))
    args = parser.parse_args()

    template = Path(__file__).resolve().parents[1] / "templates" / TEMPLATE_BY_KIND[args.kind]
    print(template.read_text(encoding="utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
