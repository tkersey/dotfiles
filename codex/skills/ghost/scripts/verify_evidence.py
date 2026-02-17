#!/usr/bin/env -S uv run python
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_FILES = (
    "inventory.json",
    "traceability.csv",
    "workflow_loops.json",
    "adapter_results.jsonl",
    "mutation_check.json",
    "parity.json",
)

TRACEABILITY_COLUMNS = (
    "target_type",
    "target_id",
    "case_id",
    "proof_artifact",
    "adapter_run_id",
)


class EvidenceError(ValueError):
    """Raised when the evidence bundle is invalid."""


@dataclass(frozen=True)
class WorkflowSpec:
    workflow_id: str
    requires_reset: bool


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise EvidenceError(f"missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise EvidenceError(f"invalid JSON in {path}: {exc}") from exc


def _load_inventory(path: Path) -> tuple[list[str], list[WorkflowSpec]]:
    data = _load_json(path)
    if not isinstance(data, dict):
        raise EvidenceError("inventory.json must be a JSON object")

    operations = data.get("public_operations")
    if not isinstance(operations, list) or not operations:
        raise EvidenceError("inventory.json.public_operations must be a non-empty list")

    normalized_ops: list[str] = []
    for op in operations:
        if not isinstance(op, str) or not op.strip():
            raise EvidenceError("inventory.json.public_operations must contain non-empty strings")
        normalized_ops.append(op.strip())

    workflows = data.get("primary_workflows", [])
    if not isinstance(workflows, list):
        raise EvidenceError("inventory.json.primary_workflows must be a list")

    normalized_workflows: list[WorkflowSpec] = []
    for item in workflows:
        if isinstance(item, str):
            workflow_id = item.strip()
            if not workflow_id:
                raise EvidenceError("primary workflow ids must be non-empty")
            normalized_workflows.append(WorkflowSpec(workflow_id=workflow_id, requires_reset=False))
            continue

        if not isinstance(item, dict):
            raise EvidenceError("primary_workflows entries must be strings or objects")

        workflow_id = item.get("id")
        requires_reset = item.get("requires_reset", False)
        if not isinstance(workflow_id, str) or not workflow_id.strip():
            raise EvidenceError("primary_workflows[].id must be a non-empty string")
        if not isinstance(requires_reset, bool):
            raise EvidenceError("primary_workflows[].requires_reset must be boolean")
        normalized_workflows.append(
            WorkflowSpec(workflow_id=workflow_id.strip(), requires_reset=requires_reset)
        )

    return normalized_ops, normalized_workflows


def _load_traceability(
    path: Path,
) -> tuple[dict[str, set[str]], dict[str, set[str]], dict[str, set[str]], set[str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise EvidenceError("traceability.csv is empty")
            for col in TRACEABILITY_COLUMNS:
                if col not in reader.fieldnames:
                    raise EvidenceError(f"traceability.csv missing required column: {col}")

            op_to_cases: dict[str, set[str]] = defaultdict(set)
            workflow_to_cases: dict[str, set[str]] = defaultdict(set)
            run_to_cases: dict[str, set[str]] = defaultdict(set)
            all_cases: set[str] = set()
            row_count = 0

            for row in reader:
                row_count += 1
                target_type = (row.get("target_type") or "").strip().lower()
                target_id = (row.get("target_id") or "").strip()
                case_id = (row.get("case_id") or "").strip()
                proof_artifact = (row.get("proof_artifact") or "").strip()
                adapter_run_id = (row.get("adapter_run_id") or "").strip()

                if target_type not in {"operation", "workflow"}:
                    raise EvidenceError(
                        f"traceability.csv row {row_count}: target_type must be operation|workflow"
                    )
                if not target_id:
                    raise EvidenceError(f"traceability.csv row {row_count}: target_id is required")
                if not case_id:
                    raise EvidenceError(f"traceability.csv row {row_count}: case_id is required")
                if not proof_artifact:
                    raise EvidenceError(
                        f"traceability.csv row {row_count}: proof_artifact is required"
                    )
                if not adapter_run_id:
                    raise EvidenceError(
                        f"traceability.csv row {row_count}: adapter_run_id is required"
                    )

                if target_type == "operation":
                    op_to_cases[target_id].add(case_id)
                else:
                    workflow_to_cases[target_id].add(case_id)
                run_to_cases[adapter_run_id].add(case_id)
                all_cases.add(case_id)

            if row_count == 0:
                raise EvidenceError("traceability.csv must include at least one row")

            return op_to_cases, workflow_to_cases, run_to_cases, all_cases
    except FileNotFoundError as exc:
        raise EvidenceError(f"missing required file: {path}") from exc


def _load_workflow_loops(path: Path) -> dict[str, dict[str, Any]]:
    data = _load_json(path)
    if not isinstance(data, dict):
        raise EvidenceError("workflow_loops.json must be a JSON object")

    workflows = data.get("workflows")
    if not isinstance(workflows, list):
        raise EvidenceError("workflow_loops.json.workflows must be a list")

    by_id: dict[str, dict[str, Any]] = {}
    for idx, workflow in enumerate(workflows, start=1):
        if not isinstance(workflow, dict):
            raise EvidenceError(f"workflow_loops.json.workflows[{idx}] must be an object")

        workflow_id = workflow.get("id")
        cases = workflow.get("cases")
        continuity_assertions = workflow.get("continuity_assertions")
        reset_assertions = workflow.get("reset_assertions", [])

        if not isinstance(workflow_id, str) or not workflow_id.strip():
            raise EvidenceError(f"workflow_loops.json.workflows[{idx}].id must be non-empty")
        if not isinstance(cases, list):
            raise EvidenceError(f"workflow_loops.json.workflows[{idx}].cases must be a list")
        if not isinstance(continuity_assertions, list):
            raise EvidenceError(
                f"workflow_loops.json.workflows[{idx}].continuity_assertions must be a list"
            )
        if not isinstance(reset_assertions, list):
            raise EvidenceError(
                f"workflow_loops.json.workflows[{idx}].reset_assertions must be a list"
            )

        norm_cases = [c for c in cases if isinstance(c, str) and c.strip()]
        norm_continuity = [c for c in continuity_assertions if isinstance(c, str) and c.strip()]
        norm_reset = [c for c in reset_assertions if isinstance(c, str) and c.strip()]

        workflow_key = workflow_id.strip()
        if workflow_key in by_id:
            raise EvidenceError(f"workflow_loops.json contains duplicate workflow id: {workflow_key}")

        by_id[workflow_key] = {
            "cases": norm_cases,
            "continuity_assertions": norm_continuity,
            "reset_assertions": norm_reset,
        }

    return by_id


def _load_adapter_results(
    path: Path,
) -> tuple[set[tuple[str, str]], set[tuple[str, str]], set[str], set[str]]:
    baseline_pass_pairs: set[tuple[str, str]] = set()
    baseline_nonpass_pairs: set[tuple[str, str]] = set()
    known_run_ids: set[str] = set()
    all_case_ids: set[str] = set()

    try:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise EvidenceError(
                        f"adapter_results.jsonl line {line_number} is invalid JSON: {exc}"
                    ) from exc

                if not isinstance(row, dict):
                    raise EvidenceError(
                        f"adapter_results.jsonl line {line_number} must decode to an object"
                    )

                run_id = row.get("run_id")
                case_id = row.get("case_id")
                status = row.get("status")
                mutated = row.get("mutated", False)

                if not isinstance(run_id, str) or not run_id.strip():
                    raise EvidenceError(f"adapter_results.jsonl line {line_number}: run_id required")
                if not isinstance(case_id, str) or not case_id.strip():
                    raise EvidenceError(f"adapter_results.jsonl line {line_number}: case_id required")
                if status not in {"pass", "fail", "skip"}:
                    raise EvidenceError(
                        f"adapter_results.jsonl line {line_number}: status must be pass|fail|skip"
                    )
                if not isinstance(mutated, bool):
                    raise EvidenceError(
                        f"adapter_results.jsonl line {line_number}: mutated must be boolean when present"
                    )

                norm_run_id = run_id.strip()
                norm_case_id = case_id.strip()
                pair = (norm_run_id, norm_case_id)
                known_run_ids.add(norm_run_id)
                all_case_ids.add(norm_case_id)

                if not mutated:
                    if status == "pass":
                        baseline_pass_pairs.add(pair)
                    else:
                        baseline_nonpass_pairs.add(pair)

        if not known_run_ids:
            raise EvidenceError("adapter_results.jsonl must include at least one result row")
        return baseline_pass_pairs, baseline_nonpass_pairs, known_run_ids, all_case_ids
    except FileNotFoundError as exc:
        raise EvidenceError(f"missing required file: {path}") from exc


def _load_mutation_check(path: Path) -> tuple[int, int, bool]:
    data = _load_json(path)
    if not isinstance(data, dict):
        raise EvidenceError("mutation_check.json must be a JSON object")

    required_mutations = data.get("required_mutations")
    detected_failures = data.get("detected_failures")
    passed = data.get("pass")

    if not isinstance(required_mutations, int) or required_mutations <= 0:
        raise EvidenceError("mutation_check.json.required_mutations must be an integer > 0")
    if not isinstance(detected_failures, int) or detected_failures < 0:
        raise EvidenceError("mutation_check.json.detected_failures must be an integer >= 0")
    if not isinstance(passed, bool):
        raise EvidenceError("mutation_check.json.pass must be boolean")

    return required_mutations, detected_failures, passed


def _load_parity(path: Path) -> tuple[bool, int]:
    data = _load_json(path)
    if not isinstance(data, dict):
        raise EvidenceError("parity.json must be a JSON object")

    passed = data.get("pass")
    diff_count = data.get("diff_count")

    if not isinstance(passed, bool):
        raise EvidenceError("parity.json.pass must be boolean")
    if not isinstance(diff_count, int) or diff_count < 0:
        raise EvidenceError("parity.json.diff_count must be an integer >= 0")

    return passed, diff_count


def verify_bundle(bundle_dir: Path) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    summary: dict[str, Any] = {}

    missing_files = [name for name in REQUIRED_FILES if not (bundle_dir / name).is_file()]
    if missing_files:
        errors.extend(f"missing required file: {bundle_dir / name}" for name in missing_files)
        return summary, errors

    try:
        operations, workflows = _load_inventory(bundle_dir / "inventory.json")
        op_to_cases, workflow_to_cases, run_to_cases, traceability_cases = _load_traceability(
            bundle_dir / "traceability.csv"
        )
        loops_by_id = _load_workflow_loops(bundle_dir / "workflow_loops.json")
        baseline_pass_pairs, baseline_nonpass_pairs, known_run_ids, all_result_cases = (
            _load_adapter_results(bundle_dir / "adapter_results.jsonl")
        )
        required_mutations, detected_failures, mutation_pass = _load_mutation_check(
            bundle_dir / "mutation_check.json"
        )
        parity_pass, parity_diff_count = _load_parity(bundle_dir / "parity.json")
    except EvidenceError as exc:
        errors.append(str(exc))
        return summary, errors

    for operation_id in operations:
        if operation_id not in op_to_cases:
            errors.append(f"unmapped public operation in traceability.csv: {operation_id}")

    for workflow in workflows:
        if workflow.workflow_id not in workflow_to_cases:
            errors.append(f"unmapped primary workflow in traceability.csv: {workflow.workflow_id}")
        loop = loops_by_id.get(workflow.workflow_id)
        if loop is None:
            errors.append(f"primary workflow missing in workflow_loops.json: {workflow.workflow_id}")
            continue
        if not loop["continuity_assertions"]:
            errors.append(
                f"workflow has no continuity_assertions: {workflow.workflow_id}"
            )
        if workflow.requires_reset and not loop["reset_assertions"]:
            errors.append(
                f"workflow requires reset_assertions but none were provided: {workflow.workflow_id}"
            )

    for run_id in run_to_cases:
        if run_id not in known_run_ids:
            errors.append(f"traceability references unknown adapter_run_id: {run_id}")

    for run_id, case_ids in run_to_cases.items():
        for case_id in case_ids:
            pair = (run_id, case_id)
            if case_id not in all_result_cases:
                errors.append(f"traceability case not present in adapter_results.jsonl: {case_id}")
            if pair not in baseline_pass_pairs:
                errors.append(
                    "traceability pair has no baseline pass result: "
                    f"run_id={run_id} case_id={case_id}"
                )
            if pair in baseline_nonpass_pairs:
                errors.append(
                    "traceability pair has non-pass baseline result: "
                    f"run_id={run_id} case_id={case_id}"
                )

    if not mutation_pass:
        errors.append("mutation_check.json.pass must be true")
    if detected_failures < required_mutations:
        errors.append(
            "mutation sensitivity gate failed: detected_failures < required_mutations "
            f"({detected_failures} < {required_mutations})"
        )

    if not parity_pass:
        errors.append("parity.json.pass must be true")
    if parity_diff_count != 0:
        errors.append(f"parity.json.diff_count must be 0 (found {parity_diff_count})")

    summary.update(
        {
            "operations_expected": len(operations),
            "operations_mapped": len(op_to_cases),
            "workflows_expected": len(workflows),
            "workflows_mapped": len(workflow_to_cases),
            "traceability_cases": len(traceability_cases),
            "baseline_pass_pairs": len(baseline_pass_pairs),
            "required_mutations": required_mutations,
            "detected_failures": detected_failures,
            "parity_diff_count": parity_diff_count,
        }
    )

    return summary, errors


def _format_text(result: str, summary: dict[str, Any], errors: list[str]) -> str:
    lines = [f"Evidence bundle verification: {result}"]
    if summary:
        lines.append("Summary:")
        for key in sorted(summary):
            lines.append(f"- {key}: {summary[key]}")
    if errors:
        lines.append("Errors:")
        for err in errors:
            lines.append(f"- {err}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail-closed verifier for ghost extraction evidence bundles."
    )
    parser.add_argument(
        "--bundle",
        required=True,
        help="Path to verification/evidence directory.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    args = parser.parse_args(argv)

    bundle_dir = Path(args.bundle).expanduser().resolve()
    summary, errors = verify_bundle(bundle_dir)
    result = "pass" if not errors else "fail"

    if args.format == "json":
        payload = {"result": result, "bundle": str(bundle_dir), "summary": summary, "errors": errors}
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        print(_format_text(result=result, summary=summary, errors=errors))

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
