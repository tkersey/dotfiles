#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

RESOLVE = Path(__file__).resolve().parents[1]
ROOT = RESOLVE.parent
ADJ = ROOT / "review-adjudication"
COMP = ROOT / "review-compression-compiler"


def run(script: Path, path: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), str(path), *extra],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def put(root: Path, name: str, value: dict) -> Path:
    path = root / name
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def must_pass(script: Path, fixture: Path, key: str, *extra: str) -> dict:
    result = run(script, fixture, *extra)
    assert result.returncode == 0, result.stdout + result.stderr
    body = json.loads(result.stdout)[key]
    assert body["verdict"] == "pass", body
    return body


def must_fail(script: Path, fixture: Path, needle: str, *extra: str) -> None:
    result = run(script, fixture, *extra)
    assert result.returncode == 2, result.stdout + result.stderr
    assert needle in result.stdout, result.stdout


def main() -> int:
    ac_tool = RESOLVE / "tools/acceptance_contract_gate.py"
    rb_tool = RESOLVE / "tools/review_batch_gate.py"
    phi_tool = RESOLVE / "tools/review_potential_gate.py"
    kernel_tool = RESOLVE / "tools/kernel_lint.py"
    mbkc_tool = RESOLVE / "tools/mbkc_gate.py"
    cex_tool = ADJ / "tools/counterexample_gate.py"
    basis_tool = COMP / "tools/counterexample_basis_gate.py"

    ac_path = RESOLVE / "assets/acceptance-contract-v2.example.json"
    cex_path = ADJ / "assets/counterexample-v1.example.json"
    witness_path = ADJ / "assets/counterexample-existing-class.example.json"
    outside_path = ADJ / "assets/counterexample-outside-horizon.example.json"
    discovery_path = RESOLVE / "assets/review-batch-discovery.example.json"
    conformance_path = RESOLVE / "assets/review-batch-conformance.example.json"
    basis_path = COMP / "assets/counterexample-basis-v2.example.json"
    kernel_path = RESOLVE / "assets/kernel-intent-closed.example.json"
    phi_path = RESOLVE / "assets/review-potential-v1.example.json"
    mbkc_path = RESOLVE / "assets/mbkc-intent-closed-terminal.example.json"

    must_pass(ac_tool, ac_path, "acceptance_contract_gate")
    must_pass(cex_tool, cex_path, "counterexample_gate")
    must_pass(cex_tool, witness_path, "counterexample_gate")
    must_pass(cex_tool, outside_path, "counterexample_gate")
    must_pass(rb_tool, discovery_path, "review_batch_gate")
    must_pass(rb_tool, conformance_path, "review_batch_gate")
    must_pass(basis_tool, basis_path, "counterexample_basis_gate")
    must_pass(kernel_tool, kernel_path, "kernel_lint")
    must_pass(phi_tool, phi_path, "review_potential_gate")
    must_pass(mbkc_tool, mbkc_path, "mbkc_gate", "--terminal")

    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)

        # Empty intent is not sealable.
        value = load(ac_path)
        ac = value["acceptance_contract"]
        ac["required"] = []
        ac["compatibility"] = []
        ac["forbidden"] = []
        path = put(temp, "ac-empty.json", value)
        must_fail(ac_tool, path, "contract:no-MUST-or-MUST-NOT")

        # Finding-level mutation authority is always false.
        value = load(cex_path)
        value["counterexample"]["mutation_authority"]["allowed"] = "yes"
        path = put(temp, "cex-mutation.json", value)
        must_fail(cex_tool, path, "mutation_authority.allowed:must-be-no")

        # Existing witness cannot enter a new kernel class.
        value = load(witness_path)
        value["counterexample"]["disposition"] = "enter_kernel"
        path = put(temp, "cex-witness-route.json", value)
        must_fail(cex_tool, path, "expected-one-of:attach_witness")

        # Outside-horizon issue cannot become implementation scope.
        value = load(outside_path)
        value["counterexample"]["disposition"] = "enter_kernel"
        path = put(temp, "cex-outside-route.json", value)
        must_fail(cex_tool, path, "expected-one-of:capture_followup")

        # Conformance cannot be a generic whole-diff review.
        value = load(conformance_path)
        value["review_batch"]["apertures"][0]["whole_diff_allowed"] = True
        path = put(temp, "rb-whole-diff.json", value)
        must_fail(rb_tool, path, "conformance-whole-diff-forbidden")

        # Any mutation while a batch is open is a hard failure, even if later sealed.
        value = load(discovery_path)
        value["review_batch"]["mutation_events_while_open"] = ["apply_patch:1"]
        path = put(temp, "rb-mutation.json", value)
        must_fail(rb_tool, path, "mutation_events_while_open:not-empty")

        # Every accepted counterexample must enter exactly one class.
        value = load(basis_path)
        value["counterexample_basis"]["accepted_counterexamples"].append("CEX-UNCLASSIFIED")
        path = put(temp, "basis-unclassified.json", value)
        must_fail(basis_tool, path, "accepted-counterexample-unclassified:CEX-UNCLASSIFIED")

        # Every law must remain anchored to sealed intent.
        value = load(kernel_path)
        law = value["minimum_behavioral_kernel"]["laws"][0]
        law["acceptance_refs"] = []
        law["compatibility_refs"] = []
        law["forbidden_refs"] = []
        path = put(temp, "kernel-unanchored.json", value)
        must_fail(kernel_tool, path, "intent-anchor-required")

        # Comment silence/equality is not strict progress.
        value = load(phi_path)
        value["review_potential"]["after"] = json.loads(
            json.dumps(value["review_potential"]["before"])
        )
        value["review_potential"]["comparison"]["primary_after"] = [0, 1, 1, 0]
        value["review_potential"]["comparison"]["primary_lexicographic_decrease"] = "no"
        value["review_potential"]["comparison"]["strict_progress"] = "no"
        path = put(temp, "phi-equal.json", value)
        must_fail(phi_tool, path, "strict-progress-gate:fail")

        # Hard semantic surface cannot silently increase.
        value = load(phi_path)
        value["review_potential"]["after"]["hard_semantic_surface"]["public_symbols"] = 1
        value["review_potential"]["comparison"]["hard_surface_componentwise_nonincreasing"] = "no"
        value["review_potential"]["comparison"]["strict_progress"] = "no"
        path = put(temp, "phi-surface.json", value)
        must_fail(phi_tool, path, "strict-progress-gate:fail")

        # Terminal closure cannot coexist with an open review batch.
        value = load(mbkc_path)
        value["minimum_behavioral_kernel_certificate"]["review_batches"]["open_batch_ids"] = ["RB-open"]
        path = put(temp, "mbkc-open-batch.json", value)
        must_fail(mbkc_tool, path, "review_batches.open_batch_ids:not-empty", "--terminal")

        # A terminal holdout with novelty blocks closure.
        value = load(mbkc_path)
        value["minimum_behavioral_kernel_certificate"]["terminal_holdout"]["novel_in_horizon_counterexamples"] = 1
        path = put(temp, "mbkc-holdout-novel.json", value)
        must_fail(mbkc_tool, path, "terminal_holdout.novel_in_horizon_counterexamples", "--terminal")

    print("intent-closed resolve protocol: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
