#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prove-it-autogauntlet.py"


def load_driver():
    spec = importlib.util.spec_from_file_location("prove_it_autogauntlet", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def nonterminal_turn(round_num: int, action: str | None = None) -> str:
    next_round = round_num + 1
    action = action or f"AUTO_CONTINUE_TO_ROUND_{next_round}"
    return f"""
## Round {round_num} — Counterexamples

Brief analysis.

Round Ledger:
Round: {round_num}
Engine turn: {round_num} of 10
Focus: Counterexamples
Original claim: test
Normalized claim: test
Claim scope: test
Current refined claim entering round: test
Attack summary: test
New evidence: none
New candidate counterexample or pressure: none
New candidate decisive proof pressure: none
Effect on original claim: none
Effect on refined claim: none
Candidate fatal pressures carried forward: none
Candidate decisive proof pressures carried forward: none
Remaining gaps: none
Verdict embargo status: ACTIVE
Next round: {next_round} — next

Knowledge Delta:
- New: none
- Updated: none
- Invalidated: none

Continuation Gate:
Round completed: {round_num} of 10
Final verdict allowed: no
Candidate status: no new pressure
Reason terminal output is not allowed yet: round {round_num} is not round 10
Action: {action}

Checkpoint:
Driver: PROVE_IT_AUTOTURN_V1
Mode: auto-gauntlet-only
Status: IN PROGRESS
Completed engine turns: {round_num} of 10
Completed round: {round_num}
Next round: {next_round} — next
Verdict embargo: ACTIVE
Stop reason: none
Current refined claim: test
Candidate fatal pressures carried forward: none
Candidate decisive proof pressures carried forward: none
Resume rule: continue
"""


def terminal_turn() -> str:
    return """
## Round 10 — Oracle synthesis

Brief synthesis.

Round Ledger:
Round: 10
Engine turn: 10 of 10
Focus: Oracle synthesis
Original claim: test
Normalized claim: test
Claim scope: test
Current refined claim entering round: test
Attack summary: all pressures resolved
New evidence: none
New candidate counterexample or pressure: none
New candidate decisive proof pressure: none
Effect on original claim: bounded
Effect on refined claim: bounded
Candidate fatal pressures carried forward: none
Candidate decisive proof pressures carried forward: none
Remaining gaps: none
Verdict embargo status: LIFTED_BY_ROUND_10
Next round: none

Knowledge Delta:
- New: final synthesis
- Updated: verdict
- Invalidated: none

Continuation Gate:
Round completed: 10 of 10
Final verdict allowed: yes
Candidate status: claim narrowed
Reason terminal output is not allowed yet: none
Action: COMPLETE_ROUND_10

Oracle synthesis:
Original claim: test
Normalized claim: test
Completed engine turns: 10 of 10
Verdict embargo: LIFTED_BY_ROUND_10

Final verdict:
- Outcome: BOUNDED_CLAIM_SURVIVES
- Verdict statement: test
- Decisive reasons: test

Checkpoint:
Driver: PROVE_IT_AUTOTURN_V1
Mode: auto-gauntlet-only
Status: COMPLETE
Completed engine turns: 10 of 10
Completed round: 10
Next round: none
Verdict embargo: LIFTED_BY_ROUND_10
Stop reason: ROUND_10_COMPLETE
Current refined claim: test
Candidate fatal pressures carried forward: none
Candidate decisive proof pressures carried forward: none
Resume rule: complete
"""


def test_nested_round_heading_in_checkpoint_is_ignored() -> None:
    driver = load_driver()
    text = nonterminal_turn(1) + "\n### Round 1 — Counterexamples\nHistorical record.\n"
    result = driver.validate_turn(text, 1)
    assert result.ok, result.errors


def test_space_separated_continue_action_is_accepted() -> None:
    driver = load_driver()
    result = driver.validate_turn(nonterminal_turn(1, action="AUTO CONTINUE TO ROUND 2"), 1)
    assert result.ok, result.errors


def test_early_final_verdict_is_rejected() -> None:
    driver = load_driver()
    result = driver.validate_turn(nonterminal_turn(1) + "\nFinal verdict:\n- Outcome: DISPROVEN\n", 1)
    assert not result.ok
    assert any("final verdict" in error for error in result.errors)


def test_round_10_terminal_contract() -> None:
    driver = load_driver()
    result = driver.validate_turn(terminal_turn(), 10)
    assert result.ok, result.errors


def test_round_10_requires_complete_action() -> None:
    driver = load_driver()
    result = driver.validate_turn(terminal_turn().replace("Action: COMPLETE_ROUND_10", "Action: STOP"), 10)
    assert not result.ok
    assert any("STOP" in error or "COMPLETE_ROUND_10" in error for error in result.errors)


def main() -> int:
    for test in (
        test_nested_round_heading_in_checkpoint_is_ignored,
        test_space_separated_continue_action_is_accepted,
        test_early_final_verdict_is_rejected,
        test_round_10_terminal_contract,
        test_round_10_requires_complete_action,
    ):
        test()
    print("prove-it autogauntlet validation tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
