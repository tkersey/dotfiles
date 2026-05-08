#!/usr/bin/env python3
"""Mechanical contract checker for spec-pipeline outputs.

This validates the observable output shape. It does not judge semantic quality.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

EVIDENCE_LABELS = [
    "- Current state:",
    "- Relevant surfaces:",
    "- Existing behavior:",
    "- Known constraints:",
    "- Obvious risks:",
    "- Proof surfaces already available:",
    "- Facts not yet verified:",
    "- Judgment calls still needed:",
]

REQUIRED_SECTIONS = [
    "## 1. Objective",
    "## 2. Context / Current State",
    "## 3. Locked Decisions",
    "## 4. Scope",
    "## 5. Non-Goals",
    "## 6. Requirements",
    "## 7. Design / Implementation Approach",
    "## 8. Dependency-Ordered Implementation Sequence",
    "## 9. Requirement-to-Test Traceability",
    "## 10. Proof Commands",
    "## 11. Risks and Edge Cases",
    "## 12. Rollback / Abort Criteria",
    "## 13. Binary Done-State",
    "## 14. Open / Deferred Items",
]

REQUIRED_BLOCKS = [
    "## Evidence Brief",
    "## Gate Result",
    "spec_decision_packet:",
    "## Invariant Challenge",
    "## Spec Lint Result",
]

GATE_FIELDS = [
    "plan_allowed:",
    "script_gate:",
    "script_gate_reason:",
    "material_open_questions:",
    "defaults:",
    "deferrals:",
    "handoff_sentence:",
]

LINT_FIELDS = [
    "SPEC_READY:",
    "script_lint:",
    "script_lint_reason:",
    "blocking_errors:",
    "material_risks:",
    "preferences:",
    "missing_sections:",
    "unmapped_requirements:",
    "rollback_gaps:",
    "proof_gaps:",
    "churn_signals:",
    "recommended_next_action:",
]


def ordered_positions(text: str, needles: list[str]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    pos = -1
    for needle in needles:
        next_pos = text.find(needle, pos + 1)
        if next_pos == -1:
            errors.append(f"missing: {needle}")
        elif next_pos < pos:
            errors.append(f"out of order: {needle}")
        else:
            pos = next_pos
    return not errors, errors


def section_slice(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""
    next_heading = re.search(r"\n## (?!#)", text[start + len(heading):])
    if not next_heading:
        return text[start:]
    end = start + len(heading) + next_heading.start()
    return text[start:end]


def check(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    if "<proposed_plan>" in text or "</proposed_plan>" in text:
        errors.append("forbidden proposed_plan wrapper present")

    if "SPEC_PIPELINE_GATE_FAILURE" in text or "SPEC_PIPELINE_DRIFT_WARNING" in text:
        # Failure/warning outputs intentionally do not include a full spec. Still forbid plan wrappers.
        return errors

    for block in REQUIRED_BLOCKS:
        if block not in text:
            errors.append(f"missing required block: {block}")

    ok, label_errors = ordered_positions(text, ["## Evidence Brief", *EVIDENCE_LABELS])
    if not ok:
        errors.extend([f"evidence brief: {e}" for e in label_errors])

    ok, section_errors = ordered_positions(text, REQUIRED_SECTIONS)
    if not ok:
        errors.extend([f"required sections: {e}" for e in section_errors])

    gate = section_slice(text, "## Gate Result")
    for field in GATE_FIELDS:
        if field not in gate:
            errors.append(f"gate result missing field: {field}")

    lint = section_slice(text, "## Spec Lint Result")
    for field in LINT_FIELDS:
        if field not in lint:
            errors.append(f"spec lint result missing field: {field}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    errors = check(args.path)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("spec-pipeline output contract: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
