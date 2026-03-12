#!/usr/bin/env -S uv run python
"""Lint contract sections for codex/skills/fix/SKILL.md."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

EXPECTED_MAIN_HEADINGS = [
    "Contract",
    "Findings (severity order)",
    "Changes applied",
    "Pass trace",
    "Validation",
    "Self-review loop trace",
    "Residual risks / open questions",
]

EXPECTED_EMBEDDED_HEADINGS = [
    "Findings (severity order)",
    "Changes applied",
    "Pass trace",
    "Validation",
    "Self-review loop trace",
    "Residual risks / open questions",
]

EXPECTED_VALIDATION_KEYS = [
    "baseline_cmd",
    "baseline_result",
    "proof_hook",
    "final_cmd",
    "final_result",
]

EXPECTED_FINDINGS_LINES = [
    "Proof strength: `<characterization|targeted_regression|property_or_fuzz>`",
    "Compatibility impact: `<none|tightening|additive|breaking>`",
]

EXPECTED_SELF_REVIEW_LINES = [
    "- If none: `- None (skip_gate)`",
    "- Otherwise: `S#` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=<...>; finding=`<F#|none>`; change_applied=`<yes|no>`; proof=`<cmd|n/a>`; result=`<ok|fail|n/a>`; stop_reason=`<continue|no_new_actionable_changes|blocked>`",
]

ALLOWED_BLOCKED_BY = [
    "product_ambiguity",
    "breaking_change",
    "no_repro_or_proof",
    "scope_guardrail",
    "generated_output",
    "external_dependency",
    "perf_unmeasurable",
]

EXPECTED_RESIDUAL_LINE = (
    "- Otherwise: `- <file:line or token> — blocked_by=<"
    + "|".join(ALLOWED_BLOCKED_BY)
    + "> — next=<one action>`"
)

REQUIRED_SELF_LOOP_GUARDRAILS = [
    "MUST include a final `Self-review loop trace` section in the deliverable/Fix Record.",
    "MUST run the final agent-directed self-review loop only after at least one change is applied and validation is passing.",
    "MUST run the self-review loop against the final validated changeset only.",
    "MUST invalidate and rerun the self-review loop if any non-self-review edit occurs after a self-review round.",
    "MUST ask internally exactly: `If you could change one thing about this changeset what would you change?`",
    "MUST treat the final agent-directed self-review phase as current-worktree scoped once the first validated changeset exists; do not reject a self-review suggestion solely because it broadens the diff.",
    "MUST treat a self-review answer as actionable whenever it identifies a concrete compatible/provable improvement on the current validated changeset, even if the improvement is ergonomic, structural, or API-shaping rather than a baseline bug fix.",
    "MUST answer that question internally, apply at most one new actionable self-review change per self-round, re-run validation, and repeat until a self-round yields no new actionable self-review change or only blocked changes.",
    "MUST NOT reject a self-review suggestion solely because the baseline is already green, the concern sounds architectural, or the change would reshape a public/API seam; if it can stay backward-compatible and be revalidated locally, implement it.",
    "MUST, when a self-review critique is broader than the smallest bug repair, apply the narrowest compatible/provable slice that materially addresses the critique before considering broader follow-up skills.",
    "MUST rerun the non-self-review `$fix` passes once after the self-review loop reaches `no_new_actionable_changes` or `blocked`.",
    "MUST NOT use `scope_guardrail` as the reason to reject a self-review suggestion once the self-review phase has started.",
    "MUST NOT report a self-review answer that was already applied before the final self-review round; record `finding=none` only when the current final validated changeset yields no concrete compatible/provable self-review change.",
    "MUST NOT emit `If you could change one thing about this changeset what would you change?` as a user-facing terminal line during normal successful completion.",
    "Precondition gate: run this step only when `Changes applied` is not `None` and the latest validation signal result is `ok`.",
    "Freeze the self-review baseline as the latest validated changeset.",
    "If that rerun edits code, discard the stale self-review state, revalidate, and restart from step 2 against the new final changeset.",
    "If the answer yields no new actionable self-review change, record `stop_reason=no_new_actionable_changes` and continue to step 8.",
    "If the answer yields only blocked changes, record `stop_reason=blocked`, carry blockers to `Residual risks / open questions`, and continue to step 8.",
    "Skip gate: if `Changes applied` is `None` or the run is blocked before edits, output `- None (skip_gate)` in `Self-review loop trace` and proceed to output.",
]

REQUIRED_POST_FIX_BOUNDARY_GUARDRAILS = [
    "MUST stop `$fix` once no new actionable self-review change remains and the post-self-review rerun is clean; do not continue under `$fix` into broader architecture, product, roadmap, or conceptual analysis.",
    "MUST, if the user asks for broader or bolder analysis after a clean or closed `$fix` pass, close the `$fix` deliverable first and recommend the next skill explicitly (`$grill-me`, `$parse`, `$plan`, or `$creative-problem-solver`) instead of continuing under `$fix`.",
    "If a clean or closed `$fix` pass surfaces broader non-fix opportunities, do not continue exploring them under `$fix`.",
    "Do not place those broader opportunities in `Residual risks / open questions` unless a valid blocker from the allowed set applies.",
]

FORBIDDEN_STALE_SELF_REVIEW_PHRASES = [
    "MUST answer that question internally, apply at most one new fix-worthy change per self-round, re-run validation, and repeat until a self-round yields no new fix-worthy finding or only blocked changes.",
    "MUST stop `$fix` once no new fix-worthy finding remains; do not continue under `$fix` into broader architecture, product, roadmap, or conceptual analysis.",
    "If the answer yields no new fix-worthy finding, record `stop_reason=no_new_fix_worthy_findings` and exit the loop.",
    "stop_reason=`<continue|no_new_fix_worthy_findings|blocked>`",
    "No new fix-worthy findings remain under the current guardrails.",
    "No new fix-worthy findings remain on the final validated changeset.",
    "No further fix-worthy adjustments remain.",
    "Because the best self-review idea was architectural, not fix-shaped.",
    "changing the helper shape would not be a bug repair, it would be a product/API redesign",
    "there was no failing proof hook for that concern, only a readability/ergonomics argument",
]

FORBIDDEN_USER_LOOP_PHRASES = [
    "MUST ask the final user-directed changeset question only after at least one change is applied and validation is passing.",
    "MUST NOT emit `If you could change one thing about this changeset what would you change?` as a standalone first/only response.",
    "MUST, when the user-directed changeset loop precondition gate passes, append the exact question as the final line of the assistant message (after the required sections) and then stop.",
    "MUST run a final user-directed changeset loop: ask `If you could change one thing about this changeset what would you change?`, apply exactly one requested change at a time, re-run validation, and repeat until the user has no more requested changes.",
    "### 7) User-directed changeset loop (required final step when a changeset exists)",
    "If the user-directed changeset loop precondition gate passes (`Changes applied` is not `None` AND the latest validation result is `ok`), append the exact question as the final line after the last section, then stop:",
    "the final line of the message is exactly: `If you could change one thing about this changeset what would you change?`",
]

SECTION_PATTERN = re.compile(r"^\*\*(.+?)\*\*$", re.MULTILINE)
JSON_LINE_PATTERN = re.compile(r"^\s*-\s*`(\{.*\})`\s*\(single-line JSON\)\s*$", re.MULTILINE)


def line_no(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def extract_block(text: str, start_marker: str, end_marker: str) -> tuple[str, int]:
    start = text.find(start_marker)
    if start < 0:
        raise ValueError(f"missing marker: {start_marker!r}")
    end = text.find(end_marker, start)
    if end < 0:
        raise ValueError(f"missing marker: {end_marker!r}")
    return text[start:end], start


def extract_heading_lines(block: str, base_offset: int, full_text: str) -> list[tuple[str, int]]:
    results: list[tuple[str, int]] = []
    for match in SECTION_PATTERN.finditer(block):
        heading = match.group(1).strip()
        results.append((heading, line_no(full_text, base_offset + match.start())))
    return results


def extract_validation_json_keys(
    block: str, base_offset: int, full_text: str, label: str, errors: list[str]
) -> list[str] | None:
    validation_idx = block.find("**Validation**")
    if validation_idx < 0:
        errors.append(f"{label}: missing **Validation** section")
        return None

    post_validation = block[validation_idx:]
    match = JSON_LINE_PATTERN.search(post_validation)
    if not match:
        errors.append(
            f"{label}: missing single-line JSON template under Validation "
            f"(line {line_no(full_text, base_offset + validation_idx)})"
        )
        return None

    raw_json = match.group(1)
    raw_line = line_no(full_text, base_offset + validation_idx + match.start())
    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        errors.append(f"{label}: parse_error at line {raw_line}: {exc.msg}")
        return None

    keys = list(parsed.keys())
    if keys != EXPECTED_VALIDATION_KEYS:
        errors.append(
            f"{label}: validation_json_keys mismatch at line {raw_line}: "
            f"expected={EXPECTED_VALIDATION_KEYS} actual={keys}"
        )
    return keys


def check_heading_order(
    found: list[tuple[str, int]], expected: list[str], label: str, errors: list[str]
) -> None:
    found_names = [name for name, _ in found]
    if found_names != expected:
        errors.append(f"{label}: heading_order mismatch: expected={expected} actual={found_names}")


def extract_heading_section(
    block: str, heading: str, next_heading: str | None, label: str, errors: list[str]
) -> tuple[str, int] | None:
    start_match = re.search(rf"(?m)^\*\*{re.escape(heading)}\*\*$", block)
    if not start_match:
        errors.append(f"{label}: missing **{heading}** section")
        return None

    start = start_match.start()
    if next_heading is None:
        end = len(block)
    else:
        end_match = re.search(rf"(?m)^\*\*{re.escape(next_heading)}\*\*$", block[start + 1 :])
        if not end_match:
            errors.append(f"{label}: missing **{next_heading}** section after **{heading}**")
            return None
        end = start + 1 + end_match.start()
    return block[start:end], start


def require_line(
    section: str,
    expected_line: str,
    label: str,
    section_name: str,
    section_line: int,
    errors: list[str],
) -> None:
    if expected_line not in section:
        errors.append(
            f"{label}: missing template line in **{section_name}** "
            f"(line {section_line}): {expected_line}"
        )


def run(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    try:
        main_block, main_offset = extract_block(
            text, "## Deliverable format (chat)", "### Fix Record (embedded mode only)"
        )
        embedded_block, embedded_offset = extract_block(
            text, "### Fix Record (embedded mode only)", "## Pitfalls"
        )
    except ValueError as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1

    main_headings = extract_heading_lines(main_block, main_offset, text)
    embedded_headings = extract_heading_lines(embedded_block, embedded_offset, text)
    check_heading_order(main_headings, EXPECTED_MAIN_HEADINGS, "main", errors)
    check_heading_order(embedded_headings, EXPECTED_EMBEDDED_HEADINGS, "embedded", errors)

    main_keys = extract_validation_json_keys(main_block, main_offset, text, "main", errors)
    embedded_keys = extract_validation_json_keys(
        embedded_block, embedded_offset, text, "embedded", errors
    )
    if main_keys and embedded_keys and main_keys != embedded_keys:
        errors.append(
            "validation_json_sync mismatch: "
            f"main={main_keys} embedded={embedded_keys}"
        )

    for label, block, offset in (("main", main_block, main_offset), ("embedded", embedded_block, embedded_offset)):
        findings = extract_heading_section(
            block, "Findings (severity order)", "Changes applied", label, errors
        )
        if findings:
            findings_block, findings_start = findings
            findings_line = line_no(text, offset + findings_start)
            for expected_line in EXPECTED_FINDINGS_LINES:
                require_line(
                    findings_block,
                    expected_line,
                    label,
                    "Findings (severity order)",
                    findings_line,
                    errors,
                )

        self_review = extract_heading_section(
            block, "Self-review loop trace", "Residual risks / open questions", label, errors
        )
        if self_review:
            self_review_block, self_review_start = self_review
            self_review_line = line_no(text, offset + self_review_start)
            for expected_line in EXPECTED_SELF_REVIEW_LINES:
                require_line(
                    self_review_block,
                    expected_line,
                    label,
                    "Self-review loop trace",
                    self_review_line,
                    errors,
                )

        residual = extract_heading_section(
            block, "Residual risks / open questions", None, label, errors
        )
        if residual:
            residual_block, residual_start = residual
            residual_line = line_no(text, offset + residual_start)
            require_line(
                residual_block,
                EXPECTED_RESIDUAL_LINE,
                label,
                "Residual risks / open questions",
                residual_line,
                errors,
            )

    for phrase in REQUIRED_SELF_LOOP_GUARDRAILS:
        if phrase not in text:
            errors.append(
                "self_loop_guardrail missing required phrase: "
                f"{phrase}"
            )

    for phrase in REQUIRED_POST_FIX_BOUNDARY_GUARDRAILS:
        if phrase not in text:
            errors.append(
                "post_fix_boundary_guardrail missing required phrase: "
                f"{phrase}"
            )

    for phrase in FORBIDDEN_USER_LOOP_PHRASES:
        if phrase in text:
            errors.append(
                "forbidden_user_loop_phrase still present: "
                f"{phrase}"
            )

    for phrase in FORBIDDEN_STALE_SELF_REVIEW_PHRASES:
        if phrase in text:
            errors.append(
                "forbidden_stale_self_review_phrase still present: "
                f"{phrase}"
            )

    if errors:
        print("[FAIL] fix skill contract lint errors:", file=sys.stderr)
        for err in errors:
            print(f" - {err}", file=sys.stderr)
        return 1

    print(f"[OK] fix skill contract checks passed: {path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint fix skill contract sections.")
    parser.add_argument(
        "path",
        nargs="?",
        default="codex/skills/fix/SKILL.md",
        help="Path to fix SKILL.md (default: codex/skills/fix/SKILL.md)",
    )
    args = parser.parse_args()
    return run(Path(args.path))


if __name__ == "__main__":
    raise SystemExit(main())
