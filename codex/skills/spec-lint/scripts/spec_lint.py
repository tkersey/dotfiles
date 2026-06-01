#!/usr/bin/env python3
"""Conservative structural lint for implementation specs.

Usage:
  python spec_lint.py spec.md
  python spec_lint.py --strict-receipts spec.md
  cat spec.md | python spec_lint.py -
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SECTION_ALIASES = {
    "Objective": ["Objective", "Goal", "1. Objective"],
    "Context / Current State": ["Context", "Current State", "Context / Current State", "2. Context / Current State"],
    "Locked Decisions": ["Locked Decisions", "Decision Log", "Decisions", "3. Locked Decisions"],
    "Scope": ["Scope", "4. Scope"],
    "Non-Goals": ["Non-Goals", "Non Goals", "Out of Scope", "Non-Goals/Out of Scope", "5. Non-Goals"],
    "Requirements": ["Requirements", "Functional Requirements", "6. Requirements"],
    "Design / Implementation Approach": ["Design", "Implementation Approach", "Design / Implementation Approach", "7. Design / Implementation Approach"],
    "Dependency-Ordered Implementation Sequence": ["Dependency-Ordered Implementation Sequence", "Implementation Sequence", "Implementation Brief", "8. Dependency-Ordered Implementation Sequence"],
    "Requirement-to-Test Traceability": ["Requirement-to-Test Traceability", "Requirement to Test Traceability", "Traceability", "9. Requirement-to-Test Traceability"],
    "Proof Commands": ["Proof Commands", "Tests/Acceptance", "Tests", "Acceptance", "10. Proof Commands"],
    "Risks and Edge Cases": ["Risks and Edge Cases", "Risks", "Edge Cases", "Edge Cases/Failure Modes", "11. Risks and Edge Cases"],
    "Rollback / Abort Criteria": ["Rollback / Abort Criteria", "Rollback", "Abort Criteria", "Rollback/Abort Criteria", "12. Rollback / Abort Criteria"],
    "Binary Done-State": ["Binary Done-State", "Done State", "Done-State", "Completion Bar", "13. Binary Done-State"],
}

EMPTY = {"", "n/a", "na", "none", "null", "tbd", "todo", "?", "[]", "absent"}


def read_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.strip().lower()).strip("_")


def section_body(text: str, alias: str) -> str | None:
    pattern = re.compile(rf"(?im)^\s*#+\s*{re.escape(alias)}\s*$")
    m = pattern.search(text)
    if not m:
        return None
    start = m.end()
    next_heading = re.search(r"(?m)^\s*#+\s+", text[start:])
    return text[start : start + next_heading.start()] if next_heading else text[start:]


def has_section(text: str, canonical: str) -> bool:
    for alias in SECTION_ALIASES[canonical]:
        body = section_body(text, alias)
        if body is not None and normalize(body) not in EMPTY:
            return True
    return False


def first_section(text: str, canonical: str) -> str:
    for alias in SECTION_ALIASES[canonical]:
        body = section_body(text, alias)
        if body:
            return body
    return ""


def table_has_mapping(text: str) -> bool:
    trace = first_section(text, "Requirement-to-Test Traceability")
    if not trace:
        return False
    return bool(re.search(r"(?i)(requirement|req).*?(test|proof|command|acceptance)", trace, re.S)) and ("|" in trace or "-" in trace)


def rollback_specific(text: str) -> bool:
    body = first_section(text, "Rollback / Abort Criteria")
    if not body:
        return False
    low = body.lower()
    return any(k in low for k in ["trigger", "abort", "rollback", "revert", "blast", "disable", "flag", "back out"])


def proof_specific(text: str) -> bool:
    body = first_section(text, "Proof Commands")
    if not body:
        return False
    return bool(re.search(r"(?im)^\s*(pytest|npm|pnpm|yarn|cargo|go test|zig build|uv run|make|just|bundle|rspec|python|bash|ruff|mypy|tsc|deno|bun|swift|xcodebuild|gradle|mvn)\b", body)) or "```" in body


def open_questions_accountable(text: str) -> bool:
    for heading in ["Open / Deferred Items", "Open Questions", "14. Open / Deferred Items"]:
        body = section_body(text, heading)
        if body is not None:
            body = body.strip()
            if normalize(body) in EMPTY or re.match(r"(?i)^(none|n/a|na|null|\[\])\.?$", body):
                return True
            low = body.lower()
            return all(k in low for k in ["owner", "default", "consequence"]) or "none" in low
    return True


def scalar_field(text: str, field: str) -> str | None:
    m = re.search(rf"(?im)^\s*{re.escape(field)}\s*:\s*(.*)$", text)
    return m.group(1).strip() if m else None


def receipt_gaps(text: str, strict: bool) -> list[str]:
    gaps = []
    receipt_present = "## Spec Pipeline Receipt" in text
    if strict and not receipt_present:
        gaps.append("spec_pipeline_receipt_missing")
    if receipt_present:
        required = [
            "profile", "lane", "evidence_brief_emitted", "grill_rounds", "no_grill_justification",
            "decision_packet_emitted", "gate_verdict", "plan_allowed", "mutation_allowed", "subagent_budget",
            "subagent_receipt", "invariant_challenge", "fresh_eyes", "lint_verdict", "execution_handoff",
        ]
        for field in required:
            if scalar_field(text, field) is None:
                gaps.append(f"receipt_field_missing:{field}")
        rounds = scalar_field(text, "grill_rounds")
        no_grill = scalar_field(text, "no_grill_justification")
        if rounds and re.match(r"\s*0\b", rounds) and (not no_grill or normalize(no_grill) in EMPTY):
            gaps.append("grill_rounds_zero_without_no_grill_justification")
        subagent = scalar_field(text, "subagent_receipt") or ""
        m = re.search(r"open_at_end\s*=\s*(\d+)", subagent)
        if m and int(m.group(1)) > 0:
            gaps.append("subagent_receipt_open_at_end_nonzero")
    return gaps


def profile(text: str) -> str:
    raw = scalar_field(text, "profile") or scalar_field(text, "strictness_profile") or "balanced"
    value = normalize(raw.split()[0])
    return value if value in {"fast", "balanced", "strict", "campaign"} else "balanced"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict-receipts", action="store_true")
    args = parser.parse_args()
    text = read_text(args.file)

    missing = [s for s in SECTION_ALIASES if not has_section(text, s)]
    blocking = []
    if "<proposed_plan>" in text or "</proposed_plan>" in text:
        blocking.append("forbidden_proposed_plan_wrapper")
    if missing:
        blocking.append("missing_required_sections")
    if not table_has_mapping(text):
        blocking.append("requirement_to_test_traceability_missing_or_weak")
    if not rollback_specific(text):
        blocking.append("rollback_abort_criteria_missing_or_weak")
    if not proof_specific(text):
        blocking.append("proof_commands_missing_or_weak")
    if not open_questions_accountable(text):
        blocking.append("open_questions_lack_owner_default_consequence")

    p = profile(text)
    rgaps = receipt_gaps(text, args.strict_receipts)
    if args.strict_receipts and rgaps:
        blocking.append("receipt_contract_gaps")
    if p in {"balanced", "strict", "campaign"}:
        if "## Invariant Challenge" not in text:
            blocking.append("invariant_challenge_missing")
        if "## Fresh-Eyes Pass" not in text:
            blocking.append("fresh_eyes_pass_missing")

    risk = []
    length = len(text)
    if length > 12000 and p not in {"strict", "campaign"}:
        risk.append("long_spec_without_strict_or_campaign_profile")
    if length > 26000 and p != "campaign":
        risk.append("very_large_spec_without_campaign_profile")
    if re.search(r"(?i)round delta.*(replaced|changed objective|new objective|supersedes)", text, re.S):
        risk.append("possible_objective_drift_in_round_delta")
    if re.search(r"(?i)scaffold", first_section(text, "Proof Commands")) and not re.search(r"(?i)(runtime|integration|behavior)", first_section(text, "Proof Commands")):
        risk.append("possible_scaffold_only_proof")

    ready = not blocking
    result = {
        "SPEC_READY": ready,
        "profile": p,
        "missing_sections": missing,
        "blocking_errors": blocking,
        "material_risks": risk,
        "receipt_gaps": rgaps,
        "recommended_next_action": "proceed_to_plan" if ready else "revise_spec_or_return_to_grill",
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"SPEC_READY: {str(ready).lower()}")
        print(json.dumps(result, indent=2, sort_keys=True))

    return 0 if ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
