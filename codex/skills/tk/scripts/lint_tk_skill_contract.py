#!/usr/bin/env -S uv run python
"""Lint contract markers for codex/skills/tk."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SKILL_PATH = ROOT / "codex/skills/tk/SKILL.md"
EXEMPLARS_PATH = ROOT / "codex/skills/tk/references/tk-exemplars.md"
TECHNIQUES_PATH = ROOT / "codex/skills/tk/references/creative-techniques.md"
PRECEDENCE_PATH = ROOT / "codex/skills/tk/references/style-precedence-matrix.md"
SUITE_PATH = ROOT / "codex/skills/tk/references/eval/replay-suite.yaml"
CODER_PATH = ROOT / "codex/agents/coder.toml"

REQUIRED_SKILL_PHRASES = [
    "Decision order for conflicts: outer artifact contract -> explicit task envelope/write scope -> stable boundary/invariants -> repo dialect.",
    "Prefer the highest provable tier, not merely the smallest safe tier.",
    "Selection bias:",
    "Replay suite + shadow-mode notes live under `references/eval/`.",
    "Use the picker name verbatim in TK output; do not invent or rename technique labels.",
]

REQUIRED_EXEMPLAR_PHRASES = [
    "Keep these synthetic; real session transcripts belong in `references/eval/`, not here.",
    "Strict-output worker mode",
]

REQUIRED_TECHNIQUE_PHRASES = [
    "Use the picker name verbatim in TK output so evals can detect off-picker drift.",
    "Compare candidates first on seam choice, abstraction level, blast radius, and proof posture.",
    "Only use wording/readability as a tie-breaker after the code-shape decision is settled.",
]

REQUIRED_PRECEDENCE_HEADINGS = [
    "# TK Style Precedence Matrix",
    "## Decision order",
    "## What each layer owns",
    "## Common conflict resolutions",
    "## Review questions",
]

REQUIRED_CODER_PHRASES = [
    "Invoke `$tk` first: restate Contract + Invariants before making any patch.",
    "Produce one apply_patch-format candidate artifact or `NO_DIFF:<reason>`.",
    "When artifact-shape and code-shape preferences conflict, honor the outer artifact contract and keep TK seam/shape reasoning internal.",
    "Prefer the highest provable seam within scope; widen across modules only when the stable boundary clearly lives there.",
]


def require_contains(text: str, needle: str, label: str, errors: list[str]) -> None:
    if needle not in text:
        errors.append(f"{label}: missing phrase: {needle}")


def require_heading_order(
    text: str, headings: list[str], label: str, errors: list[str]
) -> None:
    cursor = 0
    for heading in headings:
        idx = text.find(heading, cursor)
        if idx < 0:
            errors.append(f"{label}: missing or out-of-order heading: {heading}")
            return
        cursor = idx + len(heading)


def require_case_ids(text: str, case_ids: list[str], errors: list[str]) -> None:
    for case_id in case_ids:
        if f"id: {case_id}" not in text:
            errors.append(f"replay-suite: missing case id {case_id}")


def require_regex(text: str, pattern: str, label: str, errors: list[str]) -> None:
    if not re.search(pattern, text, re.MULTILINE):
        errors.append(f"{label}: missing regex match: {pattern}")


def main() -> int:
    errors: list[str] = []

    paths = [
        SKILL_PATH,
        EXEMPLARS_PATH,
        TECHNIQUES_PATH,
        PRECEDENCE_PATH,
        SUITE_PATH,
        CODER_PATH,
    ]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        for item in missing:
            errors.append(f"missing required file: {item}")
        for error in errors:
            print(f"[FAIL] {error}", file=sys.stderr)
        return 1

    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    exemplars_text = EXEMPLARS_PATH.read_text(encoding="utf-8")
    techniques_text = TECHNIQUES_PATH.read_text(encoding="utf-8")
    precedence_text = PRECEDENCE_PATH.read_text(encoding="utf-8")
    suite_text = SUITE_PATH.read_text(encoding="utf-8")
    coder_text = CODER_PATH.read_text(encoding="utf-8")

    for phrase in REQUIRED_SKILL_PHRASES:
        require_contains(skill_text, phrase, "SKILL.md", errors)
    for phrase in REQUIRED_EXEMPLAR_PHRASES:
        require_contains(exemplars_text, phrase, "tk-exemplars.md", errors)
    for phrase in REQUIRED_TECHNIQUE_PHRASES:
        require_contains(techniques_text, phrase, "creative-techniques.md", errors)
    for phrase in REQUIRED_CODER_PHRASES:
        require_contains(coder_text, phrase, "coder.toml", errors)

    require_heading_order(
        precedence_text,
        REQUIRED_PRECEDENCE_HEADINGS,
        "style-precedence-matrix.md",
        errors,
    )
    require_case_ids(
        suite_text,
        [
            "replay-origin-boundary-cut",
            "replay-total-depravity-doctrine",
            "replay-worker-patch-first",
            "replay-worker-no-diff",
            "replay-incision-summary-no-raw-diff",
        ],
        errors,
    )

    require_regex(
        skill_text, r"Output-contract precedence \(required\):", "SKILL.md", errors
    )
    require_regex(skill_text, r"\*\*Incision\*\*", "SKILL.md", errors)
    require_regex(skill_text, r"\*\*Proof\*\*", "SKILL.md", errors)
    require_regex(suite_text, r"source_session:", "replay-suite.yaml", errors)
    require_regex(
        suite_text, r"type: technique_from_picker", "replay-suite.yaml", errors
    )
    require_regex(suite_text, r"type: diff_block_count", "replay-suite.yaml", errors)
    require_regex(suite_text, r"type: max_nonempty_lines", "replay-suite.yaml", errors)

    if errors:
        print("[FAIL] tk skill contract lint errors:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print(f"[OK] tk skill contract checks passed: {SKILL_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
