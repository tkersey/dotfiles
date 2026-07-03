#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
SCRIPT = ROOT / "scripts" / "prove-it"


REQUIRED_PHRASES = [
    "artifactless parallel subagent gauntlet",
    "Rounds 1-9 are subagent work",
    "Rounds 1-9 are dispatched together",
    "Round 10 is an additional Oracle subagent",
    "pressure_worker",
    "steelman_worker",
    "prove_it_round_packet",
    "prove_it_oracle_packet",
    "PROVE_IT_REQUIRES_SUBAGENTS",
    "Do not create or update:",
]

ROUND_LABELS = [
    "Round 1 — Counterexamples",
    "Round 2 — Logic traps",
    "Round 3 — Boundary cases",
    "Round 4 — Adversarial inputs",
    "Round 5 — Alternative paradigms",
    "Round 6 — Operational constraints",
    "Round 7 — Probabilistic uncertainty",
    "Round 8 — Comparative baselines",
    "Round 9 — Meta-test",
    "Round 10 — Oracle synthesis",
]

FORBIDDEN_SKILL_PHRASES = [
    "PROVE_IT_AUTOTURN_V1",
    "Completed engine turns",
    "AUTOTURN_DRIVER_PROMPT",
    "prove-it-autogauntlet.py",
    "codex exec resume --last",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_required_contract_phrases() -> None:
    text = read(SKILL)
    missing = [phrase for phrase in REQUIRED_PHRASES if phrase not in text]
    assert not missing, missing


def test_all_enhanced_rounds_are_present() -> None:
    text = read(SKILL)
    missing = [label for label in ROUND_LABELS if label not in text]
    assert not missing, missing


def test_obsolete_autoturn_contract_is_removed() -> None:
    text = read(SKILL)
    found = [phrase for phrase in FORBIDDEN_SKILL_PHRASES if phrase in text]
    assert not found, found


def test_artifact_prohibition_names_old_state_paths() -> None:
    text = read(SKILL)
    for path in (
        ".prove-it-progress.md",
        ".prove-it-progress.template.md",
        ".prove-it-runs/",
        "manifest.json",
        "prompt/output transcript files",
    ):
        assert path in text


def test_script_no_longer_launches_autoturn_driver() -> None:
    text = read(SCRIPT)
    assert "PROVE_IT_SUBAGENT_NATIVE" in text
    assert "prove-it-autogauntlet.py" not in text
    assert "exec \"$script_dir" not in text


def main() -> int:
    for test in (
        test_required_contract_phrases,
        test_all_enhanced_rounds_are_present,
        test_obsolete_autoturn_contract_is_removed,
        test_artifact_prohibition_names_old_state_paths,
        test_script_no_longer_launches_autoturn_driver,
    ):
        test()
    print("prove-it subagent contract tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
