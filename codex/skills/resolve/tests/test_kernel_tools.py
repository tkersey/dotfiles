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
                "kernel_fingerprint": "sha256:kernel",
                "acceptance_contract_ref": {
                    "contract_id": "AC-1",
                    "contract_fingerprint": "sha256:ac",
                    "horizon_fingerprint": "sha256:horizon",
                },
                "counterexample_basis_ref": {
                    "basis_id": "CEB-1",
                    "basis_fingerprint": "sha256:basis",
                },
                "non_goals": [],
                "authorities": [{"authority_id": "auth", "owns": "state", "publishes": "evidence", "may_transition": ["op"]}],
                "carriers": [{"carrier_id": "state", "meaning": "state", "representation_independent": "yes"}],
                "observations": [{
                    "observation_id": "obs",
                    "source": "acceptance",
                    "counterexample_refs": ["cex"],
                    "acceptance_refs": ["AC-1:required"],
                    "compatibility_refs": [],
                    "forbidden_refs": [],
                    "observes": "status",
                    "expected": "ok",
                    "proof_ref": "test",
                }],
                "equivalence_classes": [{"class_id": "ok", "members_or_predicate": "ok", "preserved_observations": ["obs"], "distinguished_from": []}],
                "operations": [{"operation_id": "op", "inputs": [], "outputs": [], "authority_id": "auth"}],
                "transitions": [{"transition_id": "t", "from_classes": ["ok"], "operation_id": "op", "to_classes": ["ok"], "guards": [], "emitted_observations": ["obs"]}],
                "laws": [{
                    "law_id": "law",
                    "statement": "ok",
                    "owner": "auth",
                    "acceptance_refs": ["AC-1:required"],
                    "compatibility_refs": [],
                    "forbidden_refs": [],
                    "observation_ids": ["obs"],
                    "counterexample_family_ids": ["fam"],
                    "counterexample_class_refs": ["ok"],
                    "proof_obligations": ["test"],
                }],
                "non_laws": [],
                "forbidden_states_or_transitions": [],
                "counterexample_families": [{"family_id": "fam", "governing_law_ids": ["law"], "class_refs": ["ok"], "independent_witnesses": ["obs"], "subsumed_findings": [], "local_surfaces": []}],
                "non_goals_preserved": [],
                "quotient": {"method": "witness_checked_manual", "optimality": "witnessed", "merged_distinctions": [], "unresolved_distinctions": [], "congruence_witnesses": ["op preserves ok"]},
                "gate_passed": "yes",
                "gate": {
                    "all_branch_liabilities_covered": "pass",
                    "every_observation_intent_anchored": "pass",
                    "every_distinction_has_witness": "pass",
                    "every_family_maps_to_law": "pass",
                    "quotient_is_congruent": "pass",
                    "no_local_surface_family_without_governing_law": "pass",
                    "non_goals_preserved": "pass",
                    "recomposition_proved": "pass",
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
                "protocol_profile": "intent-closed-cegis-v1",
                "certificate_id": "MBKC-1",
                "stage": "terminal_closed",
                "campaign": {
                    "campaign_id": "campaign-1",
                    "pr_number": 1,
                    "campaign_base_sha": "abc",
                    "review_ready_baseline_sha": "def",
                    "current_delivery_head": "ghi",
                },
                "acceptance": {
                    "contract_version": "AC-v2",
                    "contract_id": "AC-1",
                    "contract_fingerprint": "sha256:ac",
                    "horizon_fingerprint": "sha256:horizon",
                    "horizon_state": "sealed",
                    "gate_passed": "yes",
                },
                "review_batches": {
                    "discovery": {"batch_id": "RB-discovery", "state": "sealed"},
                    "conformance": {"batch_id": "RB-conformance", "state": "sealed"},
                    "terminal_holdout": {"batch_id": "RB-terminal", "state": "sealed"},
                    "open_batch_ids": [],
                },
                "counterexample_basis": {
                    "basis_version": "CEB-v2",
                    "basis_id": "CEB-1",
                    "basis_fingerprint": "sha256:basis",
                    "unknown_count": 0,
                    "gate_passed": "yes",
                },
                "kernel": kernel["minimum_behavioral_kernel"],
                "reduction_certificate": {
                    "certificate_version": "RC-v1",
                    "certificate_id": "RC-1",
                    "gate_passed": "yes",
                },
                "kernel_review": {"verdict": "accepted"},
                "realization_designs": [],
                "selected_design": {},
                "realization": {
                    "selected_design_id": "design",
                    "manifest_ref": "manifest.json",
                    "construct_map_ref": "construct-map.json",
                    "surface_ref": "surface.json",
                    "verified": "yes",
                    "new_observations": [],
                },
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
                "review_potential": {
                    "potential_version": "PHI-v1",
                    "potential_id": "PHI-1",
                    "strict_progress": "yes",
                },
                "conformance": {
                    "novel_in_horizon_counterexamples": 0,
                    "unknown_counterexamples": 0,
                    "same_class_recurrences": 0,
                    "gate_passed": "yes",
                },
                "semantic_surface": {
                    "hard_dimensions_nonincreasing": "yes",
                    "total_description_nonincreasing": "yes",
                },
                "proof_basis": {
                    "all_laws_covered": "yes",
                    "wound_specific_tests": [],
                    "unmapped_proof_actions": [],
                },
                "negative_evidence": {},
                "holdouts": {
                    "kernel": {"verdict": "clean"},
                    "conformance": {"verdict": "clean"},
                },
                "terminal_holdout": {
                    "novel_in_horizon_counterexamples": 0,
                    "contract_invalidating_unresolved": 0,
                    "unknown_counterexamples": 0,
                    "verdict": "clean",
                },
                "delivery": {
                    "commit_sha": "ghi",
                    "pushed_head": "ghi",
                    "pr_sweep_ref": "pr:1",
                    "current_head_validation_passed": "yes",
                },
                "closure_horizon": {
                    "review_backend": "cas",
                    "review_receipt": "receipt",
                    "closure_kind": "terminal",
                    "reopen_conditions": ["new evidence"],
                },
                "gate": {
                    "acceptance_allowed": "yes",
                    "basis_allowed": "yes",
                    "kernel_allowed": "yes",
                    "realization_allowed": "yes",
                    "conformance_allowed": "yes",
                    "apply_allowed": "yes",
                    "commit_allowed": "yes",
                    "push_allowed": "yes",
                    "tuple_closure_allowed": "yes",
                    "acceptance_current": "yes",
                    "no_open_review_batch": "yes",
                    "basis_current": "yes",
                    "kernel_current": "yes",
                    "reduction_current": "yes",
                    "realization_current": "yes",
                    "strict_progress": "yes",
                    "conformance_clean": "yes",
                    "holdout_clean": "yes",
                    "no_orphan_code_or_proof": "yes",
                    "proof_current": "yes",
                    "delivery_current": "yes",
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
