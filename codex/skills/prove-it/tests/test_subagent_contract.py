#!/usr/bin/env python3
from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODEX = ROOT.parents[1]
AGENTS = CODEX / "agents"
SKILL = ROOT / "SKILL.md"
SCRIPTS = ROOT / "scripts"
LENS_AGENT = AGENTS / "prove-it-lens.toml"
ORACLE_AGENT = AGENTS / "prove-it-oracle.toml"


REQUIRED_PHRASES = [
    "artifactless parallel subagent gauntlet",
    "Rounds 1-9 are subagent work",
    "Rounds 1-9 are dispatched together",
    "prove_it_lens",
    "prove_it_oracle",
    "packet_role: evidence_lens",
    "packet_role: oracle_synthesis",
    "custom-agent fallback warning",
    "Execution mode: custom-agent|custom-agent fallback",
    "prove_it_01_counterexamples",
    "prove_it_10_oracle_synthesis",
    "Root relays `final_response`",
    "final_response",
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
    "lens_worker",
    "oracle_worker",
    "worker_role: lens_worker",
    "worker_role: oracle_worker",
    "exact literal `lens_worker`",
    "exact literal `oracle_worker`",
    "BOUNDED_PROVEN",
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


def read_toml(path: Path) -> dict[str, object]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


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


def test_custom_prove_it_agents_exist_and_are_read_only() -> None:
    lens = read_toml(LENS_AGENT)
    oracle = read_toml(ORACLE_AGENT)
    assert lens["name"] == "prove_it_lens"
    assert oracle["name"] == "prove_it_oracle"
    assert lens["sandbox_mode"] == "read-only"
    assert oracle["sandbox_mode"] == "read-only"


def test_lens_agent_contract_is_packet_only() -> None:
    text = read(LENS_AGENT)
    required = [
        "Return exactly one packet and no prose.",
        "prove_it_round_packet",
        "packet_role: evidence_lens",
        "Do not read or depend on other round packets.",
        "Do not synthesize across rounds.",
        "Do not declare a terminal verdict or final response.",
        "No file edits.",
        "No artifacts.",
        "No subagents.",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert not missing, missing


def test_oracle_agent_contract_owns_final_response() -> None:
    text = read(ORACLE_AGENT)
    required = [
        "Return exactly one packet and no prose.",
        "prove_it_oracle_packet",
        "packet_role: oracle_synthesis",
        "received_rounds contains all integers 1 through 9",
        "Choose exactly one terminal outcome from:",
        "Include final_response containing the complete user-facing response",
        "Execution mode: custom-agent | custom-agent fallback",
        "Do not rerun lens rounds.",
        "Do not invent packets for missing rounds.",
        "Do not hide missing, failed, timed-out, or compromised packets.",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert not missing, missing


def test_custom_agents_do_not_use_legacy_role_schema() -> None:
    agent_text = read(LENS_AGENT) + "\n" + read(ORACLE_AGENT)
    forbidden = [
        "worker_role",
        "lens_worker",
        "oracle_worker",
        "BOUNDED_PROVEN",
        "workspace-write",
    ]
    found = [phrase for phrase in forbidden if phrase in agent_text]
    assert not found, found


def test_no_per_round_custom_agent_files_were_added() -> None:
    per_round = sorted(AGENTS.glob("prove-it-0*.toml"))
    assert not per_round, [path.name for path in per_round]
    prove_it_agents = sorted(path.name for path in AGENTS.glob("prove-it-*.toml"))
    assert prove_it_agents == ["prove-it-lens.toml", "prove-it-oracle.toml"]


def main() -> int:
    for test in (
        test_required_contract_phrases,
        test_all_enhanced_rounds_are_present,
        test_obsolete_autoturn_and_old_worker_contracts_are_removed,
        test_artifact_prohibition_names_old_state_paths,
        test_removed_driver_surfaces_are_absent,
        test_no_runtime_script_surface_remains,
        test_oracle_outcome_enums_are_explicit,
        test_custom_prove_it_agents_exist_and_are_read_only,
        test_lens_agent_contract_is_packet_only,
        test_oracle_agent_contract_owns_final_response,
        test_custom_agents_do_not_use_legacy_role_schema,
        test_no_per_round_custom_agent_files_were_added,
    ):
        test()
    print("prove-it subagent contract tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
