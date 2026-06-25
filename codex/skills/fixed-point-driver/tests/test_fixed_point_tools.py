#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ASSETS = ROOT / "assets"
sys.path.insert(0, str(TOOLS))

from fixed_point_slice_gate import validate_input, validate_result  # noqa: E402


def load(name: str) -> dict:
    return json.loads((ASSETS / name).read_text(encoding="utf-8"))


def main() -> int:
    input_value = load("fixed-point-slice.example.json")["fixed_point_slice"]
    input_errors, policy = validate_input(input_value)
    assert not input_errors, input_errors
    assert policy is None
    result_value = load("fixed-point-result.example.json")[
        "fixed_point_slice_result"
    ]
    errors = validate_result(result_value, input_value, policy)
    assert not errors, errors

    policy_input = load("fixed-point-slice.policy.example.json")[
        "fixed_point_slice"
    ]
    input_errors, policy = validate_input(policy_input)
    assert not input_errors, input_errors
    assert policy and policy["action_id"] == "ACT-MUTATE-1"
    policy_result = load("fixed-point-result.policy.example.json")[
        "fixed_point_slice_result"
    ]
    errors = validate_result(policy_result, policy_input, policy)
    assert not errors, errors

    bad_input = deepcopy(input_value)
    bad_input["patch_boundary"] = {"files": [], "symbols": []}
    errors, _ = validate_input(bad_input)
    assert "patch_boundary:empty" in errors

    bad_result = deepcopy(result_value)
    bad_result["new_observations"] = ["new matrix row"]
    errors = validate_result(bad_result, input_value, None)
    assert "valid:new-observations-present" in errors
    assert "new-observations-require-return-to-frontier" in errors

    bad_policy = deepcopy(policy_result)
    bad_policy["policy_result"]["action_id"] = "ACT-OTHER"
    errors = validate_result(bad_policy, policy_input, policy)
    assert "policy_result.action_id:mismatch" in errors

    unexpected = deepcopy(policy_result)
    unexpected["policy_result"]["observed_effects"]["facts_added"].append(
        "FACT-unexpected"
    )
    errors = validate_result(unexpected, policy_input, policy)
    assert any("unexpected-effects-without-invalidation" in error for error in errors)

    outside = deepcopy(result_value)
    outside["changed_files"].append("src/outside.zig")
    errors = validate_result(outside, input_value, None)
    assert "changed_files:outside-boundary:src/outside.zig" in errors

    missing_proof = deepcopy(result_value)
    missing_proof["obligations_covered"] = []
    errors = validate_result(missing_proof, input_value, None)
    assert any("missing-obligations" in error for error in errors)

    print("fixed-point slice tools: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
