#!/usr/bin/env -S uv run python
"""Lint $plan outputs against key contract markers."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_HEADINGS = [
    "Round Delta",
    "Summary",
    "Non-Goals/Out of Scope",
    "Scope Change Log",
    "Interfaces/Types/APIs Impacted",
    "Data Flow",
    "Edge Cases/Failure Modes",
    "Tests/Acceptance",
    "Requirement-to-Test Traceability",
    "Rollout/Monitoring",
    "Rollback/Abort Criteria",
    "Assumptions/Defaults",
    "Decision Log",
    "Decision Impact Map",
    "Open Questions",
    "Stakeholder Signoff Matrix",
    "Adversarial Findings",
    "Convergence Evidence",
    "Contract Signals",
    "Implementation Brief",
]

FINDINGS_SCHEMA_FIELDS = ["lens", "type", "severity", "section", "decision", "status"]
FINDINGS_TAXONOMY = ["errors", "risks", "preferences"]
RISK_DETAIL_FIELDS = ["probability", "impact", "trigger"]
TRACEABILITY_FIELDS = ["requirement", "acceptance"]
OPEN_QUESTION_FIELDS = ["owner", "due_date", "default_action"]
ROLLBACK_FIELDS = ["abort_trigger", "rollback_action"]
DECISION_IMPACT_FIELDS = ["decision_id", "impacted_sections", "follow_up_action"]
SCOPE_CHANGE_FIELDS = ["scope_change", "reason", "approved_by"]
SIGNOFF_FIELDS = ["product", "engineering", "operations", "security"]
IMPLEMENTATION_BRIEF_FIELDS = ["step", "owner", "success_criteria"]
CONTRACT_SIGNAL_FIELDS = [
    "strictness_profile",
    "blocking_errors",
    "material_risks_open",
    "clean_rounds",
    "press_pass_clean",
    "new_errors",
    "rewrite_ratio",
    "external_inputs_trusted",
]

MONTHS = (
    "January|February|March|April|May|June|July|August|September|October|November|December"
)
ABSOLUTE_DATE_PATTERN = re.compile(
    rf"\b\d{{4}}-\d{{2}}-\d{{2}}\b|\b(?:{MONTHS})\s+\d{{1,2}},\s+\d{{4}}\b",
    re.IGNORECASE,
)


def heading_present(markdown: str, heading: str) -> bool:
    """Return True if markdown contains a heading with the given title."""
    pattern = re.compile(rf"(?im)^#{{1,6}}\s+{re.escape(heading)}\b")
    return bool(pattern.search(markdown))


def extract_heading_section(markdown: str, heading: str) -> str:
    """Extract the body of a heading section until the next heading."""
    heading_pattern = re.compile(rf"(?im)^#{{1,6}}\s+{re.escape(heading)}\b.*$")
    match = heading_pattern.search(markdown)
    if not match:
        return ""
    section_start = match.end()
    remainder = markdown[section_start:]
    next_heading = re.search(r"(?im)^#{1,6}\s+\S", remainder)
    section_end = section_start + next_heading.start() if next_heading else len(markdown)
    return markdown[section_start:section_end].strip()


def first_non_empty_line(text: str) -> str:
    """Return the first non-empty line from text."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def parse_rewrite_ratio(markdown: str) -> float | None:
    """Parse rewrite_ratio marker if present."""
    match = re.search(r"(?im)\brewrite_ratio\s*[:=]\s*([0-9]*\.?[0-9]+)\b", markdown)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def lint_plan(text: str) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) from contract checks."""
    errors: list[str] = []
    warnings: list[str] = []

    open_count = text.count("<proposed_plan>")
    close_count = text.count("</proposed_plan>")

    if open_count != 1 or close_count != 1:
        errors.append(
            "Output must contain exactly one <proposed_plan> and one </proposed_plan>."
        )
        return errors, warnings

    body = text.split("<proposed_plan>", 1)[1].split("</proposed_plan>", 1)[0].strip()
    first_line = first_non_empty_line(body)
    if not re.match(r"^Iteration:\s*\d+/5$", first_line):
        errors.append("First non-empty line inside <proposed_plan> must be `Iteration: N/5`.")

    if not re.search(r"(?im)^#\s+\S", body):
        errors.append("Plan body must include a title heading (for example `# Title`).")

    for heading in REQUIRED_HEADINGS:
        if not heading_present(body, heading):
            errors.append(f"Missing required heading: `{heading}`.")

    round_delta = extract_heading_section(body, "Round Delta")
    if round_delta and len(round_delta.strip()) < 10:
        errors.append("`Round Delta` must describe concrete changes from the prior round.")

    traceability = extract_heading_section(body, "Requirement-to-Test Traceability")
    if traceability:
        for field in TRACEABILITY_FIELDS:
            if not re.search(rf"(?i)\b{field}\b", traceability):
                errors.append(
                    f"`Requirement-to-Test Traceability` must include `{field}` markers."
                )

    scope_change_log = extract_heading_section(body, "Scope Change Log")
    if scope_change_log:
        for field in SCOPE_CHANGE_FIELDS:
            if not re.search(rf"(?i)\b{field}\b", scope_change_log):
                errors.append(f"`Scope Change Log` must include `{field}` markers.")

    rollback = extract_heading_section(body, "Rollback/Abort Criteria")
    if rollback:
        for field in ROLLBACK_FIELDS:
            if not re.search(rf"(?i)\b{field}\b", rollback):
                errors.append(
                    f"`Rollback/Abort Criteria` must include `{field}` markers."
                )

    decision_log = extract_heading_section(body, "Decision Log")
    if decision_log:
        if not re.search(r"(?i)\bdecision_id\b", decision_log):
            errors.append("`Decision Log` should include `decision_id` markers.")
        if not re.search(r"(?i)\bsupersedes\b", decision_log):
            errors.append("`Decision Log` should include `supersedes` markers.")

    decision_impact_map = extract_heading_section(body, "Decision Impact Map")
    if decision_impact_map:
        for field in DECISION_IMPACT_FIELDS:
            if not re.search(rf"(?i)\b{field}\b", decision_impact_map):
                errors.append(
                    f"`Decision Impact Map` must include `{field}` markers."
                )

    open_questions = extract_heading_section(body, "Open Questions")
    if open_questions and not re.search(r"(?i)\bnone\b|\bn\/a\b", open_questions):
        for field in OPEN_QUESTION_FIELDS:
            if not re.search(rf"(?i)\b{field}\b", open_questions):
                errors.append(f"`Open Questions` must include `{field}` markers.")

    signoff_matrix = extract_heading_section(body, "Stakeholder Signoff Matrix")
    if signoff_matrix:
        for field in SIGNOFF_FIELDS:
            if not re.search(rf"(?i)\b{field}\b", signoff_matrix):
                errors.append(
                    f"`Stakeholder Signoff Matrix` must include `{field}` markers."
                )

    findings = extract_heading_section(body, "Adversarial Findings")
    if findings:
        for field in FINDINGS_SCHEMA_FIELDS:
            if not re.search(rf"(?i)\b{field}\b", findings):
                errors.append(
                    f"`Adversarial Findings` must include schema marker `{field}`."
                )
        for token in FINDINGS_TAXONOMY:
            if not re.search(rf"(?i)\b{token}\b", findings):
                errors.append(
                    f"`Adversarial Findings` must include taxonomy marker `{token}`."
                )
        if re.search(r"(?i)\brisks?\b", findings):
            for field in RISK_DETAIL_FIELDS:
                if not re.search(rf"(?i)\b{field}\b", findings):
                    errors.append(
                        f"`Adversarial Findings` risk entries must include `{field}`."
                    )

    assumptions = extract_heading_section(body, "Assumptions/Defaults")
    if assumptions:
        if not re.search(r"(?i)\bconfidence\b", assumptions):
            errors.append(
                "`Assumptions/Defaults` must include confidence for critical assumptions."
            )
        if not re.search(r"(?i)verification\s+plan|\bverify\b", assumptions):
            errors.append(
                "`Assumptions/Defaults` must include a verification plan for critical assumptions."
            )
        if re.search(r"(?i)time-sensitive|as of|latest|today|current", assumptions):
            if not ABSOLUTE_DATE_PATTERN.search(assumptions):
                errors.append(
                    "Time-sensitive assumptions must include a concrete absolute date."
                )

    convergence = extract_heading_section(body, "Convergence Evidence")
    if convergence:
        clean_rounds_match = re.search(
            r"(?i)\bclean_rounds\b\s*[:=]\s*(\d+)\b", convergence
        )
        clean_rounds_ok = bool(
            clean_rounds_match and int(clean_rounds_match.group(1)) >= 2
        )
        press_pass_clean = bool(
            re.search(r"(?i)\bpress_pass_clean\b\s*[:=]\s*(true|yes|1)\b", convergence)
        )
        no_new_errors = bool(
            re.search(r"(?i)\bnew_errors\b\s*[:=]\s*0\b", convergence)
        )
        press_pass_ok = press_pass_clean and no_new_errors
        if not (clean_rounds_ok or press_pass_ok):
            errors.append(
                "`Convergence Evidence` must show hysteresis proof: "
                "`clean_rounds >= 2` or (`press_pass_clean=true` and `new_errors=0`)."
            )

    contract_signals = extract_heading_section(body, "Contract Signals")
    if contract_signals:
        for field in CONTRACT_SIGNAL_FIELDS:
            if not re.search(rf"(?i)\b{field}\b", contract_signals):
                errors.append(f"`Contract Signals` must include `{field}`.")

    implementation_brief = extract_heading_section(body, "Implementation Brief")
    if implementation_brief:
        for field in IMPLEMENTATION_BRIEF_FIELDS:
            if not re.search(rf"(?i)\b{field}\b", implementation_brief):
                errors.append(
                    f"`Implementation Brief` must include `{field}` markers."
                )

    rewrite_ratio = parse_rewrite_ratio(body)
    if rewrite_ratio is None:
        warnings.append(
            "No `rewrite_ratio` marker found. Add one in `Convergence Evidence` for rewrite-budget checks."
        )
    elif rewrite_ratio > 0.35 and not heading_present(body, "Rewrite Justification"):
        errors.append(
            "`Rewrite Justification` is required when `rewrite_ratio` exceeds 0.35."
        )

    return errors, warnings


def load_text(file_path: str | None) -> str:
    """Load plan text from file or stdin."""
    if file_path:
        return Path(file_path).read_text()
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def main() -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Lint $plan contract markers.")
    parser.add_argument("--file", help="Path to markdown output to lint.")
    args = parser.parse_args()

    text = load_text(args.file)
    if not text.strip():
        print(
            "[FAIL] No input. Provide --file <path> or pipe markdown to stdin.",
            file=sys.stderr,
        )
        return 2

    errors, warnings = lint_plan(text)
    for warning in warnings:
        print(f"[WARN] {warning}")
    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        return 1

    print("[OK] Plan contract checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
