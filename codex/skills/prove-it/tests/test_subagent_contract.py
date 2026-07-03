#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
SCRIPTS = ROOT / "scripts"


REQUIRED_PHRASES = [
    "artifactless parallel subagent gauntlet",
    "Rounds 1-9 are subagent work",
    "Rounds 1-9 are dispatched together",
    "lens_worker",
    "oracle_worker",
    "worker_role: lens_worker",
    "worker_role: oracle_worker",
    "exact literal `lens_worker`",
    "exact literal `oracle_worker`",
    "final_verdict.outcome",
    "must be one exact enum value",
    "Packets received: <oracle.packet_completeness.received_rounds>",
    "Missing packets: <oracle.packet_completeness.missing_rounds>",
    "Compromised packets: <oracle.packet_completeness.compromised_rounds>",
    "if subagents are unavailable, stop with `PROVE_IT_REQUIRES_SUBAGENTS`",
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
    "pressure_worker",
    "steelman_worker",
    "Packets received: 1,2,3,4,5,6,7,8,9",
]

FORBIDDEN_PATHS = [
    ".prove-it-progress.template.md",
    "AUTOTURN_DRIVER_PROMPT.md",
    "scripts/prove-it",
    "scripts/autogauntlet-resume.sh",
    "scripts/prove-it-autogauntlet.py",
]

ORACLE_OUTCOME_ENUMS = [
    "PROVEN",
    "DISPROVEN",
    "NOT_PROVEN",
    "INSUFFICIENT_EVIDENCE",
    "BOUNDED_CLAIM_SURVIVES",
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


def test_obsolete_autoturn_and_old_worker_contracts_are_removed() -> None:
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


def test_removed_driver_surfaces_are_absent() -> None:
    existing = [path for path in FORBIDDEN_PATHS if (ROOT / path).exists()]
    assert not existing, existing


def test_no_runtime_script_surface_remains() -> None:
    assert not SCRIPTS.exists()


def test_oracle_outcome_enums_are_explicit() -> None:
    text = read(SKILL)
    missing = [value for value in ORACLE_OUTCOME_ENUMS if value not in text]
    assert not missing, missing


def main() -> int:
    for test in (
        test_required_contract_phrases,
        test_all_enhanced_rounds_are_present,
        test_obsolete_autoturn_and_old_worker_contracts_are_removed,
        test_artifact_prohibition_names_old_state_paths,
        test_removed_driver_surfaces_are_absent,
        test_no_runtime_script_surface_remains,
        test_oracle_outcome_enums_are_explicit,
    ):
        test()
    print("prove-it subagent contract tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
