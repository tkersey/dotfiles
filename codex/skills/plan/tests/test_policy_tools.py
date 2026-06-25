#!/usr/bin/env python3
from __future__ import annotations

from argparse import Namespace
from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ASSETS = ROOT / "assets"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(TOOLS))

from common import canonical_digest, load_epg, load_wrapped, state_digest  # noqa: E402
from execution_policy_gate import validate_policy  # noqa: E402
from policy_checkpoint import apply_receipt, initialize  # noqa: E402
from policy_select import select_policy, validate_state  # noqa: E402
from transition_receipt_gate import validate_transition  # noqa: E402


def run(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=30,
    )


def load(name: str) -> dict:
    return json.loads((ASSETS / name).read_text(encoding="utf-8"))


def put(root: Path, name: str, value: dict) -> Path:
    path = root / name
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return path


def validate(epg: dict) -> tuple[dict, dict]:
    errors, warnings, derived = validate_policy(epg)
    assert not errors, errors
    return derived, {"warnings": warnings}


def select(epg: dict, state: dict) -> dict:
    digest = canonical_digest(epg)
    derived, _ = validate(epg)
    assert not validate_state(state, epg, digest, derived)
    errors, warnings, decision = select_policy(
        epg, state, policy_digest=digest, derived=derived
    )
    assert not errors, errors
    return decision


def success_state(epg: dict) -> dict:
    digest = canonical_digest(epg)
    state = {
        "state_version": "EPS-v1",
        "state_id": "STATE-SUCCESS",
        "policy_id": epg["policy_id"],
        "policy_revision": epg["revision"],
        "policy_digest": digest,
        "artifact_state": deepcopy(epg["source"]["artifact_state"]),
        "satisfied_atoms": sorted({
            "fact:FACT-API-LOCKED",
            "fact:FACT-SOURCE-CURRENT",
            "obs:OBS-ROUTE=route_a",
            "unknown:UNKNOWN-ROUTE=resolved",
            "action:ACTION-PROBE=success",
            "obs:OBS-IMPLEMENT-A=pass",
            "action:ACTION-IMPLEMENT-A=success",
            "obligation:OBL-IMPL=closed",
            "obs:OBS-FINAL=pass",
            "action:ACTION-FINAL-PROOF=success",
            "obligation:OBL-FINAL=closed",
        }),
        "completed_actions": [
            "ACTION-FINAL-PROOF",
            "ACTION-IMPLEMENT-A",
            "ACTION-PROBE",
        ],
        "failed_actions": [],
        "resolved_unknowns": ["UNKNOWN-ROUTE"],
        "closed_obligations": ["OBL-FINAL", "OBL-IMPL"],
        "current_potential": {
            "safety_violations": 0,
            "critical_unknowns": 0,
            "unsatisfied_obligations": 0,
            "hard_semantic_surface": 1,
        },
        "active_action_id": None,
        "transition_receipts": ["ETR-P", "ETR-I", "ETR-F"],
        "updated_at": "2026-06-24T20:00:00+00:00",
    }
    state["state_digest"] = state_digest(state)
    return state


def matching_probe_receipt(state: dict, decision: dict) -> dict:
    value = load("transition-receipt.probe.example.json")[
        "execution_transition_receipt"
    ]
    value["transition_id"] = "ETR-PROBE-ROUNDTRIP"
    value["decision_ref"] = decision["decision_id"]
    value["state_before"] = {
        "state_id": state["state_id"],
        "state_digest": state["state_digest"],
        "potential": deepcopy(state["current_potential"]),
    }
    value["artifact_state_before"] = deepcopy(state["artifact_state"])
    value["artifact_state_after"] = deepcopy(state["artifact_state"])
    value["state_after"]["state_id"] = "STATE-1-ROUNDTRIP"
    return value


def main() -> int:
    policy_wrapper = load("execution-policy.complex.example.json")
    epg = policy_wrapper["execution_policy_graph"]
    digest = canonical_digest(epg)
    derived, _ = validate(epg)

    # Human projection and revision CLI smoke checks.
    lint = run(
        SCRIPTS / "plan_contract_lint.py",
        "--file",
        str(ASSETS / "proposed-plan.complex.example.md"),
        "--json",
    )
    assert lint.returncode == 0, lint.stdout + lint.stderr
    revision = run(
        TOOLS / "policy_revision_diff.py",
        "--parent",
        str(ASSETS / "execution-policy.complex.example.json"),
        "--current",
        str(ASSETS / "execution-policy.complex.revision-2.example.json"),
        "--strict",
    )
    assert revision.returncode == 0, revision.stdout + revision.stderr

    initial = load_wrapped(
        str(ASSETS / "policy-state.initial.example.json"),
        "execution_policy_state",
    )
    after_probe = load_wrapped(
        str(ASSETS / "policy-state.after-probe.example.json"),
        "execution_policy_state",
    )
    initial_decision = select(epg, initial)
    assert initial_decision["selected_action_id"] == "ACTION-PROBE"
    after_probe_decision = select(epg, after_probe)
    assert after_probe_decision["selected_action_id"] == "ACTION-IMPLEMENT-A"

    receipt = load_wrapped(
        str(ASSETS / "transition-receipt.probe.example.json"),
        "execution_transition_receipt",
    )
    fixture_decision = load_wrapped(
        str(ASSETS / "policy-decision.initial.example.json"),
        "execution_policy_decision",
    )
    errors, _, details = validate_transition(
        epg, initial, fixture_decision, receipt, policy_digest=digest
    )
    assert not errors, errors
    assert details["observed_potential_relation"] == "improved"

    # Policy structure failures.
    bad = deepcopy(epg)
    bad["belief"]["unknowns"][0]["observation_refs"] = []
    errors, _, _ = validate_policy(bad)
    assert "belief.unknowns[0].observation_refs:required-for-critical-open" in errors

    bad = deepcopy(epg)
    bad["actions"][1]["mutation_boundary"]["paths"] = []
    bad["actions"][1]["mutation_boundary"]["symbols"] = []
    errors, _, _ = validate_policy(bad)
    assert "actions[1].mutation_boundary:empty" in errors

    bad = deepcopy(epg)
    bad["safety_shield"]["rules"] = []
    errors, _, _ = validate_policy(bad)
    assert any("uncovered-risky-action" in item for item in errors)

    bad = deepcopy(epg)
    bad["actions"][0]["expected_effects"]["potential_delta"] = {
        "critical_unknowns": 0,
        "unsatisfied_obligations": 0,
        "hard_semantic_surface": 0,
    }
    errors, _, _ = validate_policy(bad)
    assert any("expected-potential-not-strictly-improving" in item for item in errors)

    bad = deepcopy(epg)
    outcome = deepcopy(bad["observations"][0]["outcomes"][0])
    outcome.update({
        "outcome": "ambiguous",
        "atom": "obs:OBS-ROUTE=ambiguous",
        "meaning": "The evidence does not distinguish the routes.",
    })
    bad["observations"][0]["outcomes"].append(outcome)
    errors, _, _ = validate_policy(bad)
    assert any("unhandled-observation-outcome" in item for item in errors)

    # Shield response and terminal priority.
    shield = deepcopy(epg)
    shield["belief"]["facts"].append({
        "fact_id": "FACT-EXTRA-PERMIT",
        "atom": "fact:FACT-EXTRA-PERMIT",
        "statement": "An additional mutation permit is current.",
        "evidence_refs": ["permit:extra"],
        "confidence": "high",
        "invalidators": [],
    })
    shield["safety_shield"]["rules"][0]["requires_atoms"].append(
        "fact:FACT-EXTRA-PERMIT"
    )
    shield_state = deepcopy(after_probe)
    shield_state["policy_digest"] = canonical_digest(shield)
    shield_state["state_digest"] = state_digest(shield_state)
    decision = select(shield, shield_state)
    assert decision["selected_action_id"] is None
    assert decision["terminal"] == "blocked"

    terminal_policy = deepcopy(epg)
    terminal_policy["actions"][0]["repeatable"] = True
    terminal_policy["policy"]["rules"].append({
        "rule_id": "RULE-LOW-PRIORITY-PROBE",
        "priority": 50,
        "when": {
            "all": [
                "obligation:OBL-IMPL=closed",
                "obligation:OBL-FINAL=closed",
                "obs:OBS-FINAL=pass",
            ],
            "any": [],
            "none": [],
        },
        "candidate_action_ids": ["ACTION-PROBE"],
        "terminal": None,
        "rationale": "A lower-priority diagnostic action.",
        "obligation_refs": ["OBL-FINAL"],
        "unknown_refs": [],
        "evidence_refs": ["PROOF-FINAL"],
        "replan_if_atoms": [],
    })
    decision = select(terminal_policy, success_state(terminal_policy))
    assert decision["terminal"] == "success"
    assert decision["selected_action_id"] is None

    # Receipt failures.
    bad_receipt = deepcopy(receipt)
    bad_receipt["surprise"] = {
        "present": True,
        "classification": "intent_failure",
        "statement": "The source contract is wrong.",
    }
    bad_receipt["result"] = "success"
    errors, _, _ = validate_transition(
        epg, initial, fixture_decision, bad_receipt, policy_digest=digest
    )
    assert "intent_failure:must-return-to-spec" in errors

    bad_receipt = deepcopy(receipt)
    bad_receipt["predicted"]["potential_after"]["critical_unknowns"] = 1
    errors, _, _ = validate_transition(
        epg, initial, fixture_decision, bad_receipt, policy_digest=digest
    )
    assert "predicted.potential_after:mismatch" in errors

    bad_receipt = deepcopy(receipt)
    before = deepcopy(bad_receipt["state_before"]["potential"])
    bad_receipt["observed"]["potential_after"] = before
    bad_receipt["state_after"]["potential"] = before
    bad_receipt["surprise"] = {
        "present": True,
        "classification": "expected_variance",
        "statement": "The probe did not reduce uncertainty.",
    }
    errors, _, _ = validate_transition(
        epg, initial, fixture_decision, bad_receipt, policy_digest=digest
    )
    assert "observed.potential:not-strictly-improving-on-success" in errors

    bad_state = deepcopy(initial)
    bad_state["policy_digest"] = "sha256:" + "0" * 64
    bad_state["state_digest"] = state_digest(bad_state)
    errors = validate_state(bad_state, epg, digest, derived)
    assert "policy_digest:mismatch" in errors

    # Atomic checkpoint round trip and fail-closed write behavior.
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        state_path = temp / "runtime-state.json"
        with redirect_stdout(io.StringIO()):
            rc = initialize(
                Namespace(
                    policy=str(ASSETS / "execution-policy.complex.example.json"),
                    out=str(state_path),
                )
            )
        assert rc == 0 and state_path.exists()
        runtime_state = load_wrapped(str(state_path), "execution_policy_state")
        runtime_decision = select(epg, runtime_state)
        decision_path = put(
            temp,
            "runtime-decision.json",
            {"execution_policy_decision": runtime_decision},
        )
        runtime_receipt = matching_probe_receipt(runtime_state, runtime_decision)
        receipt_path = put(
            temp,
            "runtime-receipt.json",
            {"execution_transition_receipt": runtime_receipt},
        )
        advanced = temp / "advanced-state.json"
        with redirect_stdout(io.StringIO()):
            rc = apply_receipt(
                Namespace(
                    policy=str(ASSETS / "execution-policy.complex.example.json"),
                    state=str(state_path),
                    decision=str(decision_path),
                    receipt=str(receipt_path),
                    out=str(advanced),
                )
            )
        assert rc == 0 and advanced.exists()
        next_state = load_wrapped(str(advanced), "execution_policy_state")
        assert next_state["resolved_unknowns"] == ["UNKNOWN-ROUTE"]
        assert select(epg, next_state)["selected_action_id"] == "ACTION-IMPLEMENT-A"

        invalid = matching_probe_receipt(runtime_state, runtime_decision)
        invalid["predicted"]["potential_after"]["critical_unknowns"] = 1
        invalid_path = put(
            temp,
            "invalid-receipt.json",
            {"execution_transition_receipt": invalid},
        )
        forbidden = temp / "must-not-exist.json"
        with redirect_stdout(io.StringIO()):
            rc = apply_receipt(
                Namespace(
                    policy=str(ASSETS / "execution-policy.complex.example.json"),
                    state=str(state_path),
                    decision=str(decision_path),
                    receipt=str(invalid_path),
                    out=str(forbidden),
                )
            )
        assert rc == 2
        assert not forbidden.exists()

    print("plan EPG tools: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
