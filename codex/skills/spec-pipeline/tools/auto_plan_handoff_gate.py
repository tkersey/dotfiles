#!/usr/bin/env -S uv run python
"""Validate SGR-v2 automatic $plan tail-call eligibility.

The input may be JSON, YAML, or a Markdown/spec file containing an SGR-v2 YAML
block. This gate is deliberately fail-closed: it returns exit code 0 only when
all predicates for same-turn $plan handoff are satisfied.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:  # PyYAML is optional; JSON and line-based fallbacks still work.
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

YES = {"yes", "true", "pass", True}
NO = {"no", "false", "fail", False}


def _norm(value: Any) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if value is None:
        return ""
    return str(value).strip().strip('"\'')


def _is_yes(value: Any) -> bool:
    return value in YES or _norm(value).lower() in YES


def _is_no(value: Any) -> bool:
    return value in NO or _norm(value).lower() in NO


def _read(path: str) -> str:
    return sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")


def _extract_yaml_after_marker(text: str, marker: str = "spec_governance_receipt:") -> str | None:
    idx = text.find(marker)
    if idx < 0:
        return None
    tail = text[idx:]
    # Stop at the next same-level Markdown heading if present.
    m = re.search(r"\n##\s+", tail)
    return tail[: m.start()] if m else tail


def _parse(text: str, path: str) -> dict[str, Any]:
    # JSON first.
    try:
        value = json.loads(text)
        if isinstance(value, dict):
            return value
    except Exception:
        pass

    candidates = [text]
    block = _extract_yaml_after_marker(text)
    if block and block != text:
        candidates.insert(0, block)

    if yaml is not None:
        for candidate in candidates:
            try:
                value = yaml.safe_load(candidate)
            except Exception:
                continue
            if isinstance(value, dict):
                return value

    # Minimal line-based fallback. Supports dotted keys poorly but usefully.
    out: dict[str, Any] = {}
    for line in text.splitlines():
        m = re.match(r"^\s*([A-Za-z0-9_.$-]+)\s*:\s*(.*?)\s*$", line)
        if m:
            out[m.group(1)] = m.group(2)
    if out:
        return out
    raise ValueError(f"could not parse {path} as JSON, YAML, or SGR-like text")


def _unwrap(value: dict[str, Any]) -> dict[str, Any]:
    body = value.get("spec_governance_receipt", value)
    if not isinstance(body, dict):
        raise ValueError("spec_governance_receipt must be an object")
    return body


def _get(body: dict[str, Any], dotted: str, default: Any = None) -> Any:
    cur: Any = body
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur


def _empty_list(value: Any) -> bool:
    if value in (None, "", []):
        return True
    if isinstance(value, str):
        stripped = value.strip()
        return stripped in {"[]", "none", "None", ""}
    return False


def evaluate(body: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    def require_eq(path: str, expected: Any) -> None:
        actual = _get(body, path)
        if _norm(actual) != _norm(expected):
            errors.append(f"{path}:expected:{expected}:actual:{actual}")

    def require_yes(path: str) -> None:
        actual = _get(body, path)
        if not _is_yes(actual):
            errors.append(f"{path}:expected:yes:actual:{actual}")

    def require_no(path: str) -> None:
        actual = _get(body, path)
        if not _is_no(actual):
            errors.append(f"{path}:expected:no:actual:{actual}")

    require_eq("receipt_version", "SGR-v2")
    if _norm(_get(body, "mode")) not in {"full", "repair"}:
        errors.append(f"mode:expected:full-or-repair:actual:{_get(body, 'mode')}")
    require_eq("status", "complete")
    require_eq("lane", "spec_to_plan")

    require_no("authoritative_brief.drift_detected")
    for path in (
        "phase_presence.gate",
        "phase_presence.implementation_spec",
        "phase_presence.challenge",
        "phase_presence.fresh_eyes",
        "phase_presence.lint",
        "phase_presence.execution_handoff",
    ):
        require_yes(path)

    require_yes("gate.plan_allowed")
    require_no("gate.material_open_questions_remaining")
    require_no("fresh_eyes.drift_detected")
    require_eq("lint.verdict", "pass")
    require_no("lint.blocked_handoff")

    open_agents = _get(body, "subagents.open_at_end", 0)
    try:
        if int(open_agents) != 0:
            errors.append(f"subagents.open_at_end:expected:0:actual:{open_agents}")
    except Exception:
        errors.append(f"subagents.open_at_end:expected:0:actual:{open_agents}")

    require_yes("execution_control.plan_allowed")
    require_yes("execution_control.execution_handoff")
    require_yes("execution_handoff.ready_for_plan")
    require_eq("execution_handoff.next_owner", "$plan")
    if not _empty_list(_get(body, "execution_handoff.do_not_execute_before", [])):
        errors.append("execution_handoff.do_not_execute_before:must-be-empty")

    require_yes("auto_plan_handoff.eligible")
    require_eq("auto_plan_handoff.invocation", "same_turn_tail_call")

    if _is_yes(_get(body, "auto_plan_handoff.eligible")) and errors:
        warnings.append("auto_plan_handoff.eligible=yes-but-predicates-failed")

    return not errors, errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate automatic $plan handoff eligibility from SGR-v2.")
    parser.add_argument("file", help="JSON/YAML/Markdown file or - for stdin")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args(argv)

    try:
        parsed = _parse(_read(args.file), args.file)
        body = _unwrap(parsed)
        passed, errors, warnings = evaluate(body)
    except Exception as exc:
        body = {}
        passed, errors, warnings = False, [str(exc)], []

    result = {
        "auto_plan_handoff_gate": {
            "verdict": "pass" if passed else "fail",
            "eligible": "yes" if passed else "no",
            "spec_id": body.get("spec_id"),
            "mode": body.get("mode"),
            "lane": body.get("lane"),
            "next_owner": _get(body, "execution_handoff.next_owner"),
            "errors": errors,
            "warnings": warnings,
        }
    }
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        gate = result["auto_plan_handoff_gate"]
        print(f"verdict: {gate['verdict']}")
        print(f"eligible: {gate['eligible']}")
        if errors:
            print("errors:")
            for error in errors:
                print(f"- {error}")
        if warnings:
            print("warnings:")
            for warning in warnings:
                print(f"- {warning}")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
