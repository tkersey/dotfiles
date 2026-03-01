#!/usr/bin/env -S uv run python
"""Lint $plan outputs against key contract markers."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_HEADINGS = [
    "Round Delta",
    "Iteration Action Log",
    "Iteration Change Log",
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
ITERATION_ACTION_FIELDS = [
    "iteration",
    "focus",
    "round_decision",
    "what_we_did",
    "target_outcome",
]
ITERATION_CHANGE_FIELDS = [
    "iteration",
    "delta_kind",
    "evidence",
    "what_we_did",
    "change",
    "sections_touched",
]
OPEN_QUESTION_FIELDS = ["owner", "due_date", "default_action"]
ROLLBACK_FIELDS = ["abort_trigger", "rollback_action"]
DECISION_IMPACT_FIELDS = ["decision_id", "impacted_sections", "follow_up_action"]
SCOPE_CHANGE_FIELDS = ["scope_change", "reason", "approved_by"]
SIGNOFF_FIELDS = ["product", "engineering", "operations", "security"]
IMPLEMENTATION_BRIEF_FIELDS = ["step", "owner", "success_criteria"]
CONTRACT_SIGNAL_FIELDS = [
    "contract_version",
    "strictness_profile",
    "blocking_errors",
    "material_risks_open",
    "clean_rounds",
    "press_pass_clean",
    "new_errors",
    "rewrite_ratio",
    "external_inputs_trusted",
    "improvement_exhausted",
    "stop_reason",
]

STRICTNESS_PROFILES = {"fast", "balanced", "strict"}
ROUND_DECISIONS = {"continue", "close"}
DELTA_KINDS = {"material", "preference", "none"}
STOP_REASONS = {
    "none",
    "token_limit",
    "time_limit",
    "missing_input",
    "tool_limit",
    "user_requested",
    "safety_stop",
    "other",
}

MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
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
    section_end = (
        section_start + next_heading.start() if next_heading else len(markdown)
    )
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


def parse_bool(raw: str) -> bool | None:
    value = raw.strip().lower()
    if value in {"true", "1", "yes"}:
        return True
    if value in {"false", "0", "no"}:
        return False
    return None


def parse_int(raw: str) -> int | None:
    try:
        return int(raw.strip())
    except ValueError:
        return None


def parse_float(raw: str) -> float | None:
    try:
        return float(raw.strip())
    except ValueError:
        return None


def parse_contract_signals(
    section_text: str,
) -> tuple[dict[str, str], dict[str, str], list[str]]:
    """Parse Contract Signals section into key/value pairs.

    Returns (values, delimiters, duplicate_keys).
    Required keys must use '=' (not ':') to be machine-parseable.
    """

    values: dict[str, str] = {}
    delimiters: dict[str, str] = {}
    duplicate_keys: list[str] = []

    for raw_line in section_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r"^[-*]\s+", "", line)

        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*([:=])\s*(.+?)\s*$", line)
        if not match:
            continue

        key = match.group(1).strip().lower()
        delim = match.group(2)
        value = match.group(3).strip()

        if key in values and key not in duplicate_keys:
            duplicate_keys.append(key)

        values[key] = value
        delimiters[key] = delim

    return values, delimiters, duplicate_keys


def parse_int_field(entry: str, field: str) -> int | None:
    match = re.search(rf"(?i)\b{re.escape(field)}\b\s*[:=]\s*(\d+)\b", entry)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def parse_enum_field(entry: str, field: str, allowed: set[str]) -> str | None:
    match = re.search(rf"(?i)\b{re.escape(field)}\b\s*[:=]\s*([A-Za-z_]+)\b", entry)
    if not match:
        return None
    value = match.group(1).strip().lower()
    if value not in allowed:
        return None
    return value


def parse_text_field(entry: str, field: str) -> str | None:
    match = re.search(rf"(?im)\b{re.escape(field)}\b\s*[:=]\s*(\S.+?)\s*$", entry)
    if not match:
        return None
    value = match.group(1).strip()
    return value if value else None


def field_has_value_or_list(entry: str, field: str) -> bool:
    """Return True if entry has a non-empty `field: value` (or `field=value`) or
    a `field:` line followed by at least one list item.
    """

    if parse_text_field(entry, field) is not None:
        return True

    match = re.search(rf"(?im)^\s*(?:[-*]\s+)?{re.escape(field)}\b\s*[:=]\s*$", entry)
    if not match:
        return False

    remainder = entry[match.end() :]
    return bool(re.search(r"(?m)^\s*[-*]\s+\S", remainder))


def extract_bullet_entries(section_text: str) -> list[str]:
    """Extract top-level bullet entry blocks from a section.

    Each entry is the bullet line plus any following indented lines until the next
    top-level bullet.
    """
    lines = section_text.splitlines()
    bullet_indents: list[int] = []
    for line in lines:
        match = re.match(r"^(\s*)- ", line)
        if match:
            bullet_indents.append(len(match.group(1)))
    if not bullet_indents:
        return []

    top_indent = min(bullet_indents)
    entries: list[str] = []
    i = 0
    while i < len(lines):
        match = re.match(r"^(\s*)- ", lines[i])
        if match and len(match.group(1)) == top_indent:
            start = i
            i += 1
            while i < len(lines):
                match = re.match(r"^(\s*)- ", lines[i])
                if match and len(match.group(1)) == top_indent:
                    break
                i += 1
            entries.append("\n".join(lines[start:i]).strip())
            continue
        i += 1

    return entries


def lint_plan(text: str) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) from contract checks."""
    errors: list[str] = []
    warnings: list[str] = []

    action_by_iter: dict[int, dict[str, object]] = {}
    change_by_iter: dict[int, dict[str, object]] = {}

    open_count = text.count("<proposed_plan>")
    close_count = text.count("</proposed_plan>")

    if open_count != 1 or close_count != 1:
        errors.append(
            "Output must contain exactly one <proposed_plan> and one </proposed_plan>."
        )
        return errors, warnings

    body = text.split("<proposed_plan>", 1)[1].split("</proposed_plan>", 1)[0].strip()
    first_line = first_non_empty_line(body)
    iteration_header: int | None = None
    match = re.match(r"^Iteration:\s*(\d+)$", first_line)
    if not match:
        errors.append(
            "First non-empty line inside <proposed_plan> must be `Iteration: N`."
        )
    else:
        iteration_header = int(match.group(1))

    if not re.search(r"(?im)^#\s+\S", body):
        errors.append("Plan body must include a title heading (for example `# Title`).")

    for heading in REQUIRED_HEADINGS:
        if not heading_present(body, heading):
            errors.append(f"Missing required heading: `{heading}`.")

    round_delta = extract_heading_section(body, "Round Delta")
    if round_delta and len(round_delta.strip()) < 10:
        errors.append(
            "`Round Delta` must describe concrete changes from the input plan."
        )

    iteration_action_log = extract_heading_section(body, "Iteration Action Log")
    if iteration_action_log:
        action_entries = extract_bullet_entries(iteration_action_log)
        if not action_entries:
            errors.append(
                "`Iteration Action Log` must contain at least one bullet entry."
            )
        for idx, entry in enumerate(action_entries, start=1):
            iteration = parse_int_field(entry, "iteration")
            if iteration is None:
                errors.append(
                    f"`Iteration Action Log` entry {idx} must include `iteration: <int>` (or `iteration=<int>`)."
                )
                continue
            if iteration in action_by_iter:
                errors.append(
                    f"`Iteration Action Log` contains duplicate iteration={iteration}."
                )
                continue

            focus = parse_int_field(entry, "focus")
            if focus is None or not (1 <= focus <= 5):
                errors.append(
                    f"`Iteration Action Log` entry {idx} must include `focus: 1..5` (or `focus=...`)."
                )

            round_decision = parse_enum_field(entry, "round_decision", ROUND_DECISIONS)
            if round_decision is None:
                errors.append(
                    f"`Iteration Action Log` entry {idx} must include `round_decision: continue|close` (or `round_decision=...`)."
                )

            if not field_has_value_or_list(entry, "what_we_did"):
                errors.append(
                    f"`Iteration Action Log` entry {idx} must include non-empty `what_we_did` (value or list)."
                )

            if not field_has_value_or_list(entry, "target_outcome"):
                errors.append(
                    f"`Iteration Action Log` entry {idx} must include non-empty `target_outcome` (value or list)."
                )

            action_by_iter[iteration] = {
                "focus": focus,
                "round_decision": round_decision,
            }

    iteration_change_log = extract_heading_section(body, "Iteration Change Log")
    if iteration_change_log:
        change_entries = extract_bullet_entries(iteration_change_log)
        if not change_entries:
            errors.append(
                "`Iteration Change Log` must contain at least one bullet entry."
            )
        for idx, entry in enumerate(change_entries, start=1):
            iteration = parse_int_field(entry, "iteration")
            if iteration is None:
                errors.append(
                    f"`Iteration Change Log` entry {idx} must include `iteration: <int>` (or `iteration=<int>`)."
                )
                continue
            if iteration in change_by_iter:
                errors.append(
                    f"`Iteration Change Log` contains duplicate iteration={iteration}."
                )
                continue

            delta_kind = parse_enum_field(entry, "delta_kind", DELTA_KINDS)
            if delta_kind is None:
                errors.append(
                    f"`Iteration Change Log` entry {idx} must include `delta_kind: material|preference|none` (or `delta_kind=...`)."
                )

            evidence_ok = field_has_value_or_list(entry, "evidence")
            if not evidence_ok:
                errors.append(
                    f"`Iteration Change Log` entry {idx} must include non-empty `evidence` (value or list)."
                )

            if not field_has_value_or_list(entry, "what_we_did"):
                errors.append(
                    f"`Iteration Change Log` entry {idx} must include non-empty `what_we_did` (value or list)."
                )

            if not field_has_value_or_list(entry, "change"):
                errors.append(
                    f"`Iteration Change Log` entry {idx} must include non-empty `change` (value or list)."
                )

            if not field_has_value_or_list(entry, "sections_touched"):
                errors.append(
                    f"`Iteration Change Log` entry {idx} must include non-empty `sections_touched` (value or list)."
                )

            change_by_iter[iteration] = {
                "delta_kind": delta_kind,
                "evidence_ok": evidence_ok,
            }

    if action_by_iter and change_by_iter:
        action_iters = sorted(action_by_iter.keys())
        change_iters = sorted(change_by_iter.keys())
        if set(action_iters) != set(change_iters):
            missing_in_actions = sorted(set(change_iters) - set(action_iters))
            missing_in_changes = sorted(set(action_iters) - set(change_iters))
            if missing_in_actions:
                errors.append(
                    "Iteration log alignment mismatch: action log missing iterations "
                    + ", ".join(map(str, missing_in_actions))
                    + "."
                )
            if missing_in_changes:
                errors.append(
                    "Iteration log alignment mismatch: change log missing iterations "
                    + ", ".join(map(str, missing_in_changes))
                    + "."
                )
        else:
            iters = action_iters
            min_iter = min(iters)
            max_iter = max(iters)
            expected = list(range(min_iter, max_iter + 1))
            if iters != expected:
                errors.append(
                    "Iteration logs must cover a contiguous iteration range with no gaps."
                )
            if iteration_header is not None and max_iter != iteration_header:
                errors.append(
                    f"Iteration logs max iteration={max_iter} must equal plan header `Iteration: {iteration_header}`."
                )

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
                errors.append(f"`Decision Impact Map` must include `{field}` markers.")

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
        no_new_errors = bool(re.search(r"(?i)\bnew_errors\b\s*[:=]\s*0\b", convergence))
        press_pass_ok = press_pass_clean and no_new_errors
        if not (clean_rounds_ok or press_pass_ok):
            errors.append(
                "`Convergence Evidence` must show hysteresis proof: "
                "`clean_rounds >= 2` or (`press_pass_clean=true` and `new_errors=0`)."
            )

    contract_improvement_exhausted: bool | None = None
    contract_stop_reason: str | None = None

    contract_signals = extract_heading_section(body, "Contract Signals")
    if contract_signals:
        values, delimiters, duplicate_keys = parse_contract_signals(contract_signals)

        for key in duplicate_keys:
            warnings.append(f"Duplicate Contract Signals key: `{key}` (last one wins).")

        for field in CONTRACT_SIGNAL_FIELDS:
            if field not in values:
                errors.append(f"`Contract Signals` must include `{field}=...`. ")
            elif delimiters.get(field) != "=":
                errors.append(
                    f"`Contract Signals` field `{field}` must use `=` (not `:`) to be machine-parseable."
                )

        contract_version = parse_int(values.get("contract_version", ""))
        if contract_version != 2:
            errors.append("`Contract Signals` must include `contract_version=2`.")

        strictness_profile = values.get("strictness_profile", "").strip().lower()
        if strictness_profile not in STRICTNESS_PROFILES:
            errors.append(
                "`Contract Signals` must include `strictness_profile=fast|balanced|strict`."
            )

        blocking_errors = parse_int(values.get("blocking_errors", ""))
        if blocking_errors is None or blocking_errors < 0:
            errors.append("`Contract Signals` must include `blocking_errors=<int>`. ")

        material_risks_open = parse_int(values.get("material_risks_open", ""))
        if material_risks_open is None or material_risks_open < 0:
            errors.append(
                "`Contract Signals` must include `material_risks_open=<int>`. "
            )

        clean_rounds = parse_int(values.get("clean_rounds", ""))
        if clean_rounds is None or clean_rounds < 0:
            errors.append("`Contract Signals` must include `clean_rounds=<int>`. ")

        press_pass_clean = parse_bool(values.get("press_pass_clean", ""))
        if press_pass_clean is None:
            errors.append(
                "`Contract Signals` must include `press_pass_clean=true|false`. "
            )

        new_errors = parse_int(values.get("new_errors", ""))
        if new_errors is None or new_errors < 0:
            errors.append("`Contract Signals` must include `new_errors=<int>`. ")

        rewrite_ratio = parse_float(values.get("rewrite_ratio", ""))
        if rewrite_ratio is None or not (0.0 <= rewrite_ratio <= 1.0):
            errors.append(
                "`Contract Signals` must include `rewrite_ratio=<float 0..1>`. "
            )

        external_inputs_trusted = parse_bool(values.get("external_inputs_trusted", ""))
        if external_inputs_trusted is None:
            errors.append(
                "`Contract Signals` must include `external_inputs_trusted=true|false`. "
            )

        contract_improvement_exhausted = parse_bool(
            values.get("improvement_exhausted", "")
        )
        if contract_improvement_exhausted is None:
            errors.append(
                "`Contract Signals` must include `improvement_exhausted=true|false`. "
            )

        contract_stop_reason = values.get("stop_reason", "").strip().lower() or None
        if contract_stop_reason not in STOP_REASONS:
            errors.append(
                "`Contract Signals` must include `stop_reason=` with an allowed value."
            )

        if contract_improvement_exhausted is True:
            if contract_stop_reason != "none":
                errors.append(
                    "Close invariant violated: if `improvement_exhausted=true`, `stop_reason=none`."
                )
            if blocking_errors not in (None, 0):
                errors.append(
                    "Close invariant violated: if `improvement_exhausted=true`, `blocking_errors=0`."
                )
            if material_risks_open not in (None, 0):
                errors.append(
                    "Close invariant violated: if `improvement_exhausted=true`, `material_risks_open=0`."
                )
            if new_errors not in (None, 0):
                errors.append(
                    "Close invariant violated: if `improvement_exhausted=true`, `new_errors=0`."
                )

        if contract_improvement_exhausted is False and contract_stop_reason == "none":
            errors.append(
                "Stop invariant violated: if `improvement_exhausted=false`, `stop_reason` must not be `none`."
            )

    if contract_improvement_exhausted is True and action_by_iter and change_by_iter:
        iters = sorted(action_by_iter.keys())
        if len(iters) < 2:
            errors.append(
                "Anti-churn gate: closing requires at least two iterations in the iteration logs."
            )
        else:
            last_iter = iters[-1]
            last_action = action_by_iter.get(last_iter, {})
            if last_action.get("focus") != 5:
                errors.append(
                    "Close-decision gate: final iteration must have `focus=5` when `improvement_exhausted=true`."
                )
            if last_action.get("round_decision") != "close":
                errors.append(
                    "Close-decision gate: final iteration must have `round_decision=close` when `improvement_exhausted=true`."
                )

            for prior_iter in iters[:-1]:
                prior_action = action_by_iter.get(prior_iter, {})
                if prior_action.get("round_decision") == "close":
                    errors.append(
                        "Close-decision gate: only the final iteration may set `round_decision=close`."
                    )
                    break

            last_two = iters[-2:]
            for iter_value in last_two:
                change = change_by_iter.get(iter_value, {})
                if change.get("delta_kind") != "none":
                    errors.append(
                        "Anti-churn gate: last two iterations must have `delta_kind=none` when closing."
                    )
                    break

    if contract_improvement_exhausted is False and action_by_iter:
        last_iter = max(action_by_iter.keys())
        last_action = action_by_iter.get(last_iter, {})
        if last_action.get("round_decision") == "close":
            errors.append(
                "Stop gate: when `improvement_exhausted=false`, final `round_decision` must be `continue`."
            )

    implementation_brief = extract_heading_section(body, "Implementation Brief")
    if implementation_brief:
        for field in IMPLEMENTATION_BRIEF_FIELDS:
            if not re.search(rf"(?i)\b{field}\b", implementation_brief):
                errors.append(f"`Implementation Brief` must include `{field}` markers.")

    rewrite_ratio = parse_rewrite_ratio(body)
    if rewrite_ratio is None:
        errors.append(
            "Missing required `rewrite_ratio` marker (expected in `Contract Signals` as `rewrite_ratio=<float>`)."
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
