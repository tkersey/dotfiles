#!/usr/bin/env python3
"""Lightweight consistency gate for SGR-v2."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def read_text(path: str) -> str:
    return sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")


def scalar(text: str, field: str) -> str | None:
    match = re.search(rf"(?im)^\s*{re.escape(field)}\s*:\s*(.*)$", text)
    return match.group(1).strip() if match else None


def has(text: str, pattern: str) -> bool:
    return re.search(pattern, text, re.M) is not None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    text = read_text(args.file)
    blocking: list[str] = []

    if not has(text, r"^\s*spec_governance_receipt\s*:"):
        blocking.append("spec_governance_receipt_missing")
    if not has(text, r"^\s*receipt_version\s*:\s*SGR-v2\s*$"):
        blocking.append("sgr_v2_missing")
    if not has(text, r"^\s*mode\s*:\s*(full|gate-only|challenge-only|lint-only|repair)\s*$"):
        blocking.append("mode_missing_or_invalid")
    if not has(text, r"^\s*profile\s*:\s*(fast|balanced|strict|campaign)\s*$"):
        blocking.append("profile_missing_or_invalid")
    if not has(text, r"^\s*status\s*:\s*(complete|blocked|drift|audit-only|partial)\s*$"):
        blocking.append("status_missing_or_invalid")

    mode = scalar(text, "mode") or ""
    status = scalar(text, "status") or ""
    mutation_allowed = scalar(text, "mutation_allowed") or "no"
    execution_handoff = scalar(text, "execution_handoff") or "no"

    required_patterns: list[tuple[str, str]] = []
    if mode == "full" and status == "complete":
        required_patterns = [
            ("evidence_brief", r"^\s*evidence_brief\s*:\s*yes\s*$"),
            ("decision_packet", r"^\s*decision_packet\s*:\s*yes\s*$"),
            ("gate", r"^\s*gate\s*:\s*yes\s*$"),
            ("implementation_spec", r"^\s*implementation_spec\s*:\s*yes\s*$"),
            ("challenge", r"^\s*challenge\s*:\s*yes\s*$"),
            ("fresh_eyes", r"^\s*fresh_eyes\s*:\s*yes\s*$"),
            ("lint", r"^\s*lint\s*:\s*yes\s*$"),
            ("execution_handoff", r"^\s*execution_handoff\s*:\s*yes\s*$"),
            ("plan_allowed", r"^\s*plan_allowed\s*:\s*yes\s*$"),
            ("mutation_allowed", r"^\s*mutation_allowed\s*:\s*yes\s*$"),
            ("lint_verdict", r"^\s*verdict\s*:\s*pass\s*$"),
            ("open_subagents", r"^\s*open_at_end\s*:\s*0\s*$"),
        ]
    elif mode == "gate-only":
        required_patterns = [("gate", r"^\s*gate\s*:\s*yes\s*$")]
    elif mode == "challenge-only":
        required_patterns = [("challenge", r"^\s*challenge\s*:\s*yes\s*$")]
    elif mode == "lint-only":
        required_patterns = [("lint", r"^\s*lint\s*:\s*yes\s*$")]
    elif mode == "repair" and execution_handoff == "yes":
        required_patterns = [
            ("gate", r"^\s*gate\s*:\s*yes\s*$"),
            ("challenge", r"^\s*challenge\s*:\s*yes\s*$"),
            ("fresh_eyes", r"^\s*fresh_eyes\s*:\s*yes\s*$"),
            ("lint", r"^\s*lint\s*:\s*yes\s*$"),
        ]

    for name, pattern in required_patterns:
        if not has(text, pattern):
            blocking.append(f"required_phase_missing:{name}")

    if mode in {"gate-only", "challenge-only", "lint-only"} and mutation_allowed == "yes":
        blocking.append("audit_mode_cannot_authorize_mutation")
    if mutation_allowed == "yes" and execution_handoff != "yes":
        blocking.append("mutation_allowed_without_execution_handoff")

    passed = not blocking
    result = {
        "sgr_gate": {
            "receipt_version": "SGR-v2",
            "passed": passed,
            "mode": mode,
            "status": status,
            "blocking_errors": blocking,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
