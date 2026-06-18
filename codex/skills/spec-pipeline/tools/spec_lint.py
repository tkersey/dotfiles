#!/usr/bin/env python3
"""Conservative structural lint for implementation specs.

`pre-governance` validates the candidate before SGR-v2 is emitted.
`handoff` also requires a valid-looking SGR-v2 surface.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SECTIONS = {
    "Objective": ["Objective", "Goal", "1. Objective"],
    "Context / Current State": ["Context", "Current State", "Context / Current State", "2. Context / Current State"],
    "Locked Decisions": ["Locked Decisions", "Decision Log", "Decisions", "3. Locked Decisions"],
    "Scope": ["Scope", "4. Scope"],
    "Non-Goals": ["Non-Goals", "Non Goals", "Out of Scope", "5. Non-Goals"],
    "Requirements": ["Requirements", "Functional Requirements", "6. Requirements"],
    "Design / Implementation Approach": ["Design", "Implementation Approach", "Design / Implementation Approach", "7. Design / Implementation Approach"],
    "Dependency-Ordered Implementation Sequence": ["Dependency-Ordered Implementation Sequence", "Implementation Sequence", "8. Dependency-Ordered Implementation Sequence"],
    "Requirement-to-Test Traceability": ["Requirement-to-Test Traceability", "Traceability", "9. Requirement-to-Test Traceability"],
    "Proof Commands": ["Proof Commands", "Tests/Acceptance", "Tests", "Acceptance", "10. Proof Commands"],
    "Risks and Edge Cases": ["Risks and Edge Cases", "Risks", "Edge Cases", "11. Risks and Edge Cases"],
    "Rollback / Abort Criteria": ["Rollback / Abort Criteria", "Rollback", "Abort Criteria", "12. Rollback / Abort Criteria"],
    "Binary Done-State": ["Binary Done-State", "Done State", "Completion Bar", "13. Binary Done-State"],
    "Open / Deferred Items": ["Open / Deferred Items", "Open Questions", "Deferred Items", "14. Open / Deferred Items"],
}

EMPTY = {"", "n_a", "na", "none", "null", "tbd", "todo", "[]", "absent"}


def read_text(path: str) -> str:
    return sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def section_body(text: str, alias: str) -> str | None:
    match = re.search(rf"(?im)^\s*#+\s*{re.escape(alias)}\s*$", text)
    if not match:
        return None
    start = match.end()
    next_heading = re.search(r"(?m)^\s*#+\s+", text[start:])
    return text[start:start + next_heading.start()] if next_heading else text[start:]


def first_section(text: str, canonical: str) -> str:
    for alias in SECTIONS[canonical]:
        body = section_body(text, alias)
        if body is not None:
            return body
    return ""


def has_section(text: str, canonical: str) -> bool:
    body = first_section(text, canonical)
    return bool(body and normalize(body) not in EMPTY)


def scalar(text: str, field: str) -> str | None:
    match = re.search(rf"(?im)^\s*{re.escape(field)}\s*:\s*(.*)$", text)
    return match.group(1).strip() if match else None


def profile(text: str) -> str:
    raw = scalar(text, "profile") or "balanced"
    value = normalize(raw.split()[0])
    return value if value in {"fast", "balanced", "strict", "campaign"} else "balanced"


def traceability_ok(text: str) -> bool:
    body = first_section(text, "Requirement-to-Test Traceability")
    return bool(body and re.search(r"(?i)(requirement|req).*?(test|proof|command|acceptance)", body, re.S))


def proof_ok(text: str) -> bool:
    body = first_section(text, "Proof Commands")
    if not body:
        return False
    return bool(re.search(
        r"(?im)^\s*(pytest|npm|pnpm|yarn|cargo|go test|zig build|uv run|make|just|bundle|rspec|python|bash|ruff|mypy|tsc|deno|bun|swift|xcodebuild|gradle|mvn)\b",
        body,
    )) or "```" in body


def rollback_ok(text: str) -> bool:
    body = first_section(text, "Rollback / Abort Criteria").lower()
    return bool(body and any(word in body for word in ("trigger", "abort", "rollback", "revert", "blast", "disable", "back out")))


def open_items_ok(text: str) -> bool:
    body = first_section(text, "Open / Deferred Items").strip()
    if normalize(body) in EMPTY:
        return True
    lower = body.lower()
    return all(word in lower for word in ("owner", "default", "consequence")) or "none" in lower


def pipeline_receipt_present(text: str) -> bool:
    return "## Spec Pipeline Receipt" in text


def governance_receipt_present(text: str) -> bool:
    return bool(re.search(r"(?m)^\s*spec_governance_receipt\s*:", text) and
                re.search(r"(?m)^\s*receipt_version\s*:\s*SGR-v2\s*$", text))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--phase", choices=("pre-governance", "handoff"), default="pre-governance")
    parser.add_argument("--strict-receipts", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    text = read_text(args.file)
    missing = [name for name in SECTIONS if not has_section(text, name)]
    blocking: list[str] = []

    if "<proposed_plan>" in text or "</proposed_plan>" in text:
        blocking.append("forbidden_proposed_plan_wrapper")
    if missing:
        blocking.append("missing_required_sections")
    if not traceability_ok(text):
        blocking.append("requirement_to_test_traceability_missing_or_weak")
    if not proof_ok(text):
        blocking.append("proof_commands_missing_or_weak")
    if not rollback_ok(text):
        blocking.append("rollback_abort_criteria_missing_or_weak")
    if not open_items_ok(text):
        blocking.append("open_items_lack_owner_default_consequence")

    current_profile = profile(text)
    if current_profile in {"balanced", "strict", "campaign"}:
        if "## Invariant Challenge" not in text:
            blocking.append("invariant_challenge_missing")
        if "## Fresh-Eyes Pass" not in text:
            blocking.append("fresh_eyes_pass_missing")

    receipt_gaps: list[str] = []
    if args.strict_receipts and not pipeline_receipt_present(text):
        receipt_gaps.append("spec_pipeline_receipt_missing")
    if args.phase == "handoff" and not governance_receipt_present(text):
        receipt_gaps.append("sgr_v2_missing")
    if receipt_gaps:
        blocking.append("receipt_contract_gaps")

    risks: list[str] = []
    if len(text) > 12000 and current_profile not in {"strict", "campaign"}:
        risks.append("long_spec_without_strict_or_campaign_profile")
    if len(text) > 26000 and current_profile != "campaign":
        risks.append("very_large_spec_without_campaign_profile")
    if re.search(r"(?i)round delta.*(replaced|changed objective|new objective|supersedes)", text, re.S):
        risks.append("possible_objective_drift_in_round_delta")
    proof_body = first_section(text, "Proof Commands")
    if re.search(r"(?i)scaffold", proof_body) and not re.search(r"(?i)(runtime|integration|behavior)", proof_body):
        risks.append("possible_scaffold_only_proof")

    passed = not blocking
    receipt = {
        "receipt_version": "SLINT-v1",
        "verdict": "pass" if passed else "fail",
        "script_lint": "passed" if passed else "failed",
        "semantic_lint": "not_assessed",
        "changed_spec": "no",
        "blocked_handoff": "no" if passed else "yes",
        "proof_gaps_found": [item for item in blocking if "proof" in item],
        "rollback_gaps_found": [item for item in blocking if "rollback" in item],
        "unmapped_requirements_found": [item for item in blocking if "traceability" in item],
        "receipt_gaps_found": receipt_gaps,
        "pass_no_delta": "yes" if passed else "no",
        "phase": args.phase,
        "missing_sections": missing,
        "blocking_errors": blocking,
        "material_risks": risks,
        "recommended_next_action": "proceed" if passed else "revise_spec_or_return_to_gate",
    }

    print(json.dumps({"spec_lint_receipt": receipt}, indent=2, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
