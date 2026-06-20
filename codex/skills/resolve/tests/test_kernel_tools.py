#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"


def run(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(TOOLS / name), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)

        kernel = {
            "minimum_behavioral_kernel": {
                "kernel_version": "MBK-v1",
                "campaign_id": "campaign-1",
                "campaign_base_sha": "abc",
                "acceptance_contract": {"goal": "g"},
                "non_goals": [],
                "authorities": [{"authority_id": "auth", "owns": "state", "publishes": "evidence", "may_transition": ["op"]}],
                "carriers": [{"carrier_id": "state", "meaning": "state", "representation_independent": "yes"}],
                "observations": [{"observation_id": "obs", "source": "acceptance", "observes": "status", "expected": "ok", "proof_ref": "test"}],
                "equivalence_classes": [{"class_id": "ok", "members_or_predicate": "ok", "preserved_observations": ["obs"], "distinguished_from": []}],
                "operations": [{"operation_id": "op", "inputs": [], "outputs": [], "authority_id": "auth"}],
                "transitions": [{"transition_id": "t", "from_classes": ["ok"], "operation_id": "op", "to_classes": ["ok"], "guards": [], "emitted_observations": ["obs"]}],
                "laws": [{"law_id": "law", "statement": "ok", "owner": "auth", "observation_ids": ["obs"], "counterexample_family_ids": ["fam"], "proof_obligations": ["test"]}],
                "non_laws": [],
                "forbidden_states_or_transitions": [],
                "counterexample_families": [{"family_id": "fam", "governing_law_ids": ["law"], "independent_witnesses": ["obs"], "subsumed_findings": [], "local_surfaces": []}],
                "quotient": {"method": "witness_checked_manual", "optimality": "witnessed", "merged_distinctions": [], "unresolved_distinctions": []},
                "gate": {
                    "all_branch_liabilities_covered": "pass",
                    "every_distinction_has_witness": "pass",
                    "every_family_maps_to_law": "pass",
                    "no_local_surface_family_without_governing_law": "pass",
                    "non_goals_preserved": "pass",
                    "kernel_review_allowed": "yes",
                },
            }
        }
        kernel_path = root / "kernel.json"
        kernel_path.write_text(json.dumps(kernel), encoding="utf-8")
        result = run("kernel_lint.py", str(kernel_path))
        assert result.returncode == 0, result.stdout + result.stderr

        mbkc = {
            "minimum_behavioral_kernel_certificate": {
                "certificate_version": "MBKC-v1",
                "certificate_id": "MBKC-1",
                "stage": "terminal_closed",
                "campaign": {
                    "campaign_id": "campaign-1",
                    "campaign_base_sha": "abc",
                    "review_ready_baseline_sha": "def",
                    "current_delivery_head": "ghi",
                },
                "acceptance": {},
                "observations": [],
                "kernel": kernel["minimum_behavioral_kernel"],
                "kernel_review": {"verdict": "accepted"},
                "realization_designs": [],
                "selected_design": {},
                "realization_map": {
                    "orphan_code_constructs": [],
                    "gate": {
                        "kernel_conformance": "pass",
                        "orphan_code_constructs_zero": "pass",
                        "wound_specific_tests_zero": "pass",
                        "proof_laws_covered": "pass",
                        "semantic_surface_conserved": "pass",
                    },
                },
                "semantic_surface": {
                    "hard_dimensions_nonincreasing": "yes",
                    "total_description_nonincreasing": "yes",
                },
                "proof_basis": {
                    "wound_specific_tests": [],
                    "unmapped_proof_actions": [],
                },
                "negative_evidence": {},
                "holdouts": {
                    "kernel": {"verdict": "clean"},
                    "conformance": {"verdict": "clean"},
                },
                "delivery": {
                    "commit_sha": "ghi",
                    "pushed_head": "ghi",
                    "pr_sweep_ref": "pr:1",
                },
                "closure_horizon": {
                    "review_backend": "cas",
                    "review_receipt": "receipt",
                    "reopen_conditions": ["new evidence"],
                },
                "gate": {
                    "kernel_allowed": "yes",
                    "realization_allowed": "yes",
                    "apply_allowed": "yes",
                    "commit_allowed": "yes",
                    "push_allowed": "yes",
                    "tuple_closure_allowed": "yes",
                    "terminal_closure_allowed": "yes",
                },
            }
        }
        mbkc_path = root / "mbkc.json"
        mbkc_path.write_text(json.dumps(mbkc), encoding="utf-8")
        result = run("mbkc_gate.py", "--terminal", str(mbkc_path))
        assert result.returncode == 0, result.stdout + result.stderr

        mbkc["minimum_behavioral_kernel_certificate"]["proof_basis"]["wound_specific_tests"] = ["test-one-wound"]
        mbkc_path.write_text(json.dumps(mbkc), encoding="utf-8")
        result = run("mbkc_gate.py", "--terminal", str(mbkc_path))
        assert result.returncode == 2

    print("resolve minimum-kernel tools: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
