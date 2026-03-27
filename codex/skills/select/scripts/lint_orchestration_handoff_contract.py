#!/usr/bin/env -S uv run python
"""Fail-closed lint for the OrchPlan-to-execution handoff contract."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]

FILES = {
    "AGENTS.md": ROOT / "AGENTS.md",
    "select/SKILL.md": ROOT / "codex/skills/select/SKILL.md",
    "select/PIPELINES.md": ROOT / "codex/skills/select/PIPELINES.md",
    "teams/SKILL.md": ROOT / "codex/skills/teams/SKILL.md",
    "mesh/SKILL.md": ROOT / "codex/skills/mesh/SKILL.md",
    "st/SKILL.md": ROOT / "codex/skills/st/SKILL.md",
    "cas/SKILL.md": ROOT / "codex/skills/cas/SKILL.md",
    "selector.toml": ROOT / "codex/agents/selector.toml",
}

REQUIRED = {
    "AGENTS.md": [
        "The canonical durable handoff is `st import-orchplan --input <orchplan>` followed by `st claim --wave <wN> --executor teams|mesh` before any worker starts.",
        "Do not document or preserve a public same-turn non-`$st` handoff. If a helper still exists, it must auto-route into the same durable path and remain an implementation detail.",
    ],
    "select/SKILL.md": [
        "the canonical follow-through path is `st import-orchplan` once, then `st claim --wave <wN> --executor teams|mesh` before any `spawn_agent` or `$mesh` run.",
        "Do not describe or preserve a public same-turn non-`$st` handoff; if a helper still exists, it must auto-route into the same durable path internally.",
    ],
    "select/PIPELINES.md": [
        "Durable execution is the default for non-trivial orchestration: run `st import-orchplan --input <orchplan>` once, then `st claim --wave wN --executor teams|mesh` before any worker starts.",
        "Do not preserve a public same-turn non-`$st` fallback. If a helper still exists, it must auto-route internally into the same durable handoff and remain undocumented as a separate mode.",
    ],
    "teams/SKILL.md": [
        "For non-trivial orchestration, durable `$st` is the default handoff: import the OrchPlan and claim the ready wave in `$st` first.",
        "Do not preserve a public same-turn non-`$st` handoff. If a helper still exists, it must auto-route into the same durable path internally.",
    ],
    "mesh/SKILL.md": [
        "Durable `$st` is the default handoff for non-trivial OrchPlan execution: import and claim the selected wave before building the CSV.",
        "Do not preserve a public same-turn non-`$st` handoff. If a helper still exists, it must auto-route into the same durable path internally.",
    ],
    "st/SKILL.md": [
        "`st claim --file .step/st-plan.jsonl --wave w1 --executor teams`",
        "For OrchPlan-backed claims, `--wave` is the canonical selector and there is no public same-turn non-`$st` handoff.",
        "For OrchPlan-backed durable execution, `claim.wave_id` is authoritative and should be derived from the imported wave, not reconstructed from ad hoc `--ids`.",
    ],
    "cas/SKILL.md": [
        "`st claim --file .step/st-plan.jsonl --wave w1 --executor teams`",
    ],
    "selector.toml": [
        "Emit exactly: OrchPlan v1 YAML, then a plaintext Decision Trace. No extra prose.",
    ],
}

FORBIDDEN = [
    '--ids "cfg,ui" --executor teams --wave w1',
    '--ids "st-001,st-002" --executor teams --wave w1',
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []
    texts: dict[str, str] = {}

    for label, path in FILES.items():
        if not path.exists():
            errors.append(f"{label}: missing file: {path}")
            continue
        texts[label] = read_text(path)

    for label, required_phrases in REQUIRED.items():
        text = texts.get(label, "")
        for phrase in required_phrases:
            if phrase not in text:
                errors.append(f"{label}: missing phrase: {phrase}")

    doc_text = "\n".join(
        texts.get(label, "")
        for label in (
            "AGENTS.md",
            "select/SKILL.md",
            "select/PIPELINES.md",
            "teams/SKILL.md",
            "mesh/SKILL.md",
            "st/SKILL.md",
            "cas/SKILL.md",
        )
    )
    for forbidden in FORBIDDEN:
        if forbidden in doc_text:
            errors.append(
                f"orchestration docs: stale OrchPlan-backed claim example still present: {forbidden}"
            )

    if "public same-turn non-`$st` handoff" not in doc_text:
        errors.append("orchestration docs: missing explicit prohibition on a public same-turn non-$st handoff")

    if errors:
        print("[FAIL] orchestration handoff contract lint errors:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print(f"[OK] orchestration handoff contract checks passed: {ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
