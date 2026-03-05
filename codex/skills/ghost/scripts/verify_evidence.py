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

try:
    import yaml
except ModuleNotFoundError:
    yaml = None


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


@dataclass(frozen=True)
class InventoryContract:
    operation_ids: list[str]
    workflows: list[WorkflowSpec]
    coverage_mode: str
    sampled_case_ids: set[str]


@dataclass(frozen=True)
class TestsContract:
    operation_ids: set[str]
    workflow_ids: set[str]
    case_ids: set[str]
    operation_case_count: int
    workflow_case_count: int


@dataclass(frozen=True)
class StructureContract:
    spec_required_headings: tuple[str, ...]
    spec_stateful_required_headings: tuple[str, ...]
    verify_required_headings: tuple[str, ...]
    source: str


DEFAULT_STRUCTURE_CONTRACT = StructureContract(
    spec_required_headings=(
        "Conformance Profile",
        "Validation Matrix",
        "Definition of Done",
    ),
    spec_stateful_required_headings=(
        "State Model",
        "Transition Triggers",
        "Recovery/Idempotency",
        "Reference Algorithm",
    ),
    verify_required_headings=(
        "Summary",
        "Regenerate",
        "Validation Matrix",
        "Traceability Matrix",
        "Mutation Sensitivity",
        "Regeneration Parity",
        "Limitations",
    ),
    source="default",
)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise EvidenceError(f"missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise EvidenceError(f"invalid JSON in {path}: {exc}") from exc


def _load_inventory(path: Path) -> InventoryContract:
    data = _load_json(path)
    if not isinstance(data, dict):
        raise EvidenceError("inventory.json must be a JSON object")

    operations = data.get("public_operations")
    if not isinstance(operations, list) or not operations:
        raise EvidenceError("inventory.json.public_operations must be a non-empty list")

    normalized_ops: list[str] = []
    seen_ops: set[str] = set()
    for op in operations:
        if not isinstance(op, str) or not op.strip():
            raise EvidenceError("inventory.json.public_operations must contain non-empty strings")
        op_id = op.strip()
        if op_id in seen_ops:
            raise EvidenceError(f"inventory.json.public_operations contains duplicate id: {op_id}")
        seen_ops.add(op_id)
        normalized_ops.append(op_id)

    workflows = data.get("primary_workflows", [])
    if not isinstance(workflows, list):
        raise EvidenceError("inventory.json.primary_workflows must be a list")

    normalized_workflows: list[WorkflowSpec] = []
    seen_workflows: set[str] = set()
    for item in workflows:
        if isinstance(item, str):
            workflow_id = item.strip()
            if not workflow_id:
                raise EvidenceError("primary workflow ids must be non-empty")
            if workflow_id in seen_workflows:
                raise EvidenceError(f"inventory.json.primary_workflows contains duplicate id: {workflow_id}")
            seen_workflows.add(workflow_id)
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
        workflow_key = workflow_id.strip()
        if workflow_key in seen_workflows:
            raise EvidenceError(
                f"inventory.json.primary_workflows contains duplicate id: {workflow_key}"
            )
        seen_workflows.add(workflow_key)
        normalized_workflows.append(
            WorkflowSpec(workflow_id=workflow_key, requires_reset=requires_reset)
        )

    coverage_mode = data.get("coverage_mode", "exhaustive")
    if (
        not isinstance(coverage_mode, str)
        or coverage_mode.strip() not in {"exhaustive", "sampled"}
    ):
        raise EvidenceError("inventory.json.coverage_mode must be exhaustive|sampled when present")
    coverage_mode = coverage_mode.strip()

    raw_sampled_case_ids = data.get("sampled_case_ids", [])
    if raw_sampled_case_ids is None:
        raw_sampled_case_ids = []
    if not isinstance(raw_sampled_case_ids, list):
        raise EvidenceError("inventory.json.sampled_case_ids must be a list when present")

    sampled_case_ids: set[str] = set()
    for raw_case_id in raw_sampled_case_ids:
        if not isinstance(raw_case_id, str) or not raw_case_id.strip():
            raise EvidenceError("inventory.json.sampled_case_ids must contain non-empty strings")
        case_id = raw_case_id.strip()
        if case_id in sampled_case_ids:
            raise EvidenceError(f"inventory.json.sampled_case_ids contains duplicate case_id: {case_id}")
        sampled_case_ids.add(case_id)

    if coverage_mode == "sampled" and not sampled_case_ids:
        raise EvidenceError(
            "inventory.json.sampled_case_ids must be non-empty when coverage_mode=sampled"
        )
    if coverage_mode == "exhaustive" and sampled_case_ids:
        raise EvidenceError(
            "inventory.json.sampled_case_ids must be empty unless coverage_mode=sampled"
        )

    return InventoryContract(
        operation_ids=normalized_ops,
        workflows=normalized_workflows,
        coverage_mode=coverage_mode,
        sampled_case_ids=sampled_case_ids,
    )


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

        if not norm_cases:
            raise EvidenceError(
                f"workflow_loops.json.workflows[{idx}].cases must include at least one non-empty case id"
            )

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

    if (
        not isinstance(required_mutations, int)
        or isinstance(required_mutations, bool)
        or required_mutations <= 0
    ):
        raise EvidenceError("mutation_check.json.required_mutations must be an integer > 0")
    if (
        not isinstance(detected_failures, int)
        or isinstance(detected_failures, bool)
        or detected_failures < 0
    ):
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
    if not isinstance(diff_count, int) or isinstance(diff_count, bool) or diff_count < 0:
        raise EvidenceError("parity.json.diff_count must be an integer >= 0")

    return passed, diff_count


def _resolve_tests_yaml(bundle_dir: Path) -> Path:
    candidates = (
        bundle_dir.parent.parent / "tests.yaml",
        bundle_dir.parent.parent / "tests.yml",
        bundle_dir.parent / "tests.yaml",
        bundle_dir.parent / "tests.yml",
        bundle_dir / "tests.yaml",
        bundle_dir / "tests.yml",
    )
    for path in candidates:
        if path.is_file():
            return path
    raise EvidenceError(
        "tests.yaml not found; expected <ghost-repo>/tests.yaml adjacent to verification/evidence"
    )


def _normalize_heading_list(
    value: Any,
    *,
    field_name: str,
    allow_empty: bool = False,
) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise EvidenceError(f"invalid_structure_contract: {field_name} must be a list")

    headings: list[str] = []
    seen: set[str] = set()
    for idx, raw in enumerate(value, start=1):
        if not isinstance(raw, str) or not raw.strip():
            raise EvidenceError(
                f"invalid_structure_contract: {field_name}[{idx}] must be a non-empty string"
            )
        heading = raw.strip()
        if heading in seen:
            raise EvidenceError(
                f"invalid_structure_contract: duplicate heading in {field_name}: {heading}"
            )
        seen.add(heading)
        headings.append(heading)

    if not headings and not allow_empty:
        raise EvidenceError(f"invalid_structure_contract: {field_name} must be non-empty")

    return tuple(headings)


def _load_structure_contract(bundle_dir: Path) -> StructureContract:
    path = bundle_dir / "structure_contract.json"
    if not path.is_file():
        return DEFAULT_STRUCTURE_CONTRACT

    data = _load_json(path)
    if not isinstance(data, dict):
        raise EvidenceError("invalid_structure_contract: structure_contract.json must be an object")

    raw_spec = data.get("spec", {})
    raw_verify = data.get("verify", {})

    if not isinstance(raw_spec, dict):
        raise EvidenceError("invalid_structure_contract: spec must be an object")
    if not isinstance(raw_verify, dict):
        raise EvidenceError("invalid_structure_contract: verify must be an object")

    spec_required = _normalize_heading_list(
        raw_spec.get("required_headings"),
        field_name="spec.required_headings",
    )
    spec_stateful_required = _normalize_heading_list(
        raw_spec.get("stateful_required_headings", []),
        field_name="spec.stateful_required_headings",
        allow_empty=True,
    )
    verify_required = _normalize_heading_list(
        raw_verify.get("required_headings"),
        field_name="verify.required_headings",
    )

    return StructureContract(
        spec_required_headings=spec_required,
        spec_stateful_required_headings=spec_stateful_required,
        verify_required_headings=verify_required,
        source="bundle",
    )


def _collect_h2_headings(path: Path) -> set[str]:
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise EvidenceError(f"missing_doc_file: {path}") from exc

    headings: set[str] = set()
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("## "):
            continue
        heading = stripped[3:].strip()
        if heading:
            headings.add(heading)
    return headings


def _check_required_headings(
    *,
    doc_label: str,
    doc_headings: set[str],
    required_headings: tuple[str, ...],
) -> list[str]:
    missing = sorted(heading for heading in required_headings if heading not in doc_headings)
    return [
        f"structure_contract_mismatch: {doc_label} missing required section: {heading}"
        for heading in missing
    ]


def _validate_structure_contract(
    *,
    bundle_dir: Path,
    tests_contract: TestsContract,
) -> tuple[dict[str, Any], list[str]]:
    summary: dict[str, Any] = {}
    errors: list[str] = []

    contract = _load_structure_contract(bundle_dir)
    repo_root = bundle_dir.parent.parent

    spec_path = repo_root / "SPEC.md"
    verify_path = repo_root / "VERIFY.md"
    stateful_mode = bool(tests_contract.workflow_ids or tests_contract.workflow_case_count > 0)

    spec_headings = _collect_h2_headings(spec_path)
    verify_headings = _collect_h2_headings(verify_path)

    spec_required = list(contract.spec_required_headings)
    if stateful_mode:
        spec_required.extend(contract.spec_stateful_required_headings)

    errors.extend(
        _check_required_headings(
            doc_label="SPEC.md",
            doc_headings=spec_headings,
            required_headings=tuple(spec_required),
        )
    )
    errors.extend(
        _check_required_headings(
            doc_label="VERIFY.md",
            doc_headings=verify_headings,
            required_headings=contract.verify_required_headings,
        )
    )

    summary.update(
        {
            "structure_contract_source": contract.source,
            "structure_stateful_mode": stateful_mode,
            "structure_spec_required_sections": len(spec_required),
            "structure_verify_required_sections": len(contract.verify_required_headings),
            "structure_errors_count": len(errors),
        }
    )

    return summary, errors


def _resolve_case_id(target_id: str, case: dict[str, Any], case_index: int) -> str:
    case_id = case.get("case_id")
    if isinstance(case_id, str) and case_id.strip():
        return case_id.strip()

    case_name = case.get("name")
    if isinstance(case_name, str) and case_name.strip():
        return f"{target_id}::{case_name.strip()}"

    if case_index == 1:
        return target_id
    return f"{target_id}::{case_index}"


def _load_tests_contract(bundle_dir: Path) -> tuple[TestsContract, list[str]]:
    tests_path = _resolve_tests_yaml(bundle_dir)
    if yaml is None:
        raise EvidenceError(
            "PyYAML is required to parse tests.yaml; run: "
            "uv run --with pyyaml -- python scripts/verify_evidence.py --bundle <ghost-repo>/verification/evidence"
        )

    try:
        data = yaml.safe_load(tests_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise EvidenceError(f"missing required file: {tests_path}") from exc
    except Exception as exc:  # pragma: no cover - parser error details are user-facing.
        raise EvidenceError(f"tests.yaml parse failed ({tests_path}): {exc}") from exc

    if not isinstance(data, dict):
        raise EvidenceError("tests.yaml must decode to a mapping/object")

    operation_ids: set[str] = set()
    workflow_ids: set[str] = set()
    case_ids: set[str] = set()
    mode_errors: list[str] = []
    operation_case_count = 0
    workflow_case_count = 0

    def absorb_targets(targets: dict[str, Any], *, force_workflow: bool) -> None:
        nonlocal operation_case_count, workflow_case_count
        for raw_target_id, raw_cases in targets.items():
            if not isinstance(raw_target_id, str) or not raw_target_id.strip():
                raise EvidenceError("tests.yaml target ids must be non-empty strings")
            target_id = raw_target_id.strip()
            is_workflow = force_workflow or target_id.startswith("workflow.")

            if isinstance(raw_cases, list):
                cases = raw_cases
            elif isinstance(raw_cases, dict):
                cases = [raw_cases]
            else:
                raise EvidenceError(
                    f"tests.yaml target {target_id} must map to a list (or single case object)"
                )

            if not cases:
                raise EvidenceError(f"tests.yaml target {target_id} must include at least one case")

            if is_workflow:
                workflow_ids.add(target_id)
            else:
                operation_ids.add(target_id)

            for idx, raw_case in enumerate(cases, start=1):
                if not isinstance(raw_case, dict):
                    raise EvidenceError(
                        f"tests.yaml target {target_id} case #{idx} must be an object"
                    )

                case_id = _resolve_case_id(target_id=target_id, case=raw_case, case_index=idx)
                if case_id in case_ids:
                    raise EvidenceError(f"tests.yaml has duplicate case_id: {case_id}")
                case_ids.add(case_id)

                input_block = raw_case.get("input")
                if isinstance(input_block, dict):
                    mode = input_block.get("mode")
                    if isinstance(mode, str):
                        mode_key = mode.strip().lower()
                        if is_workflow and mode_key not in {"workflow", "scenario"}:
                            mode_errors.append(
                                "workflow case uses non-workflow mode: "
                                f"target_id={target_id} case_id={case_id} mode={mode_key}"
                            )
                        if (not is_workflow) and mode_key in {"workflow", "scenario"}:
                            mode_errors.append(
                                "operation case uses workflow/scenario mode: "
                                f"target_id={target_id} case_id={case_id} mode={mode_key}"
                            )

                if is_workflow:
                    workflow_case_count += 1
                else:
                    operation_case_count += 1

    sections_seen = 0
    operations = data.get("operations")
    if operations is not None:
        if not isinstance(operations, dict):
            raise EvidenceError("tests.yaml.operations must be an object when present")
        absorb_targets(operations, force_workflow=False)
        sections_seen += 1

    workflows = data.get("workflows")
    if workflows is not None:
        if not isinstance(workflows, dict):
            raise EvidenceError("tests.yaml.workflows must be an object when present")
        absorb_targets(workflows, force_workflow=True)
        sections_seen += 1

    scenarios = data.get("scenarios")
    if scenarios is not None:
        if not isinstance(scenarios, dict):
            raise EvidenceError("tests.yaml.scenarios must be an object when present")
        absorb_targets(scenarios, force_workflow=True)
        sections_seen += 1

    if sections_seen == 0:
        reserved = {"version", "meta", "notes"}
        case_markers = {
            "case_id",
            "name",
            "input",
            "output",
            "error",
            "task",
            "initial_state",
            "tools",
            "constraints",
            "evaluation",
            "limits",
        }
        top_level_targets: dict[str, Any] = {}
        for key, value in data.items():
            if key in reserved:
                continue
            if isinstance(value, list) and (not value or all(isinstance(item, dict) for item in value)):
                top_level_targets[key] = value
                continue
            if isinstance(value, dict) and (set(value.keys()) & case_markers):
                top_level_targets[key] = value
        if not top_level_targets:
            raise EvidenceError("tests.yaml has no operation/scenario target mapping")
        absorb_targets(top_level_targets, force_workflow=False)

    if not case_ids:
        raise EvidenceError("tests.yaml must include at least one case")
    if not operation_ids and not workflow_ids:
        raise EvidenceError("tests.yaml must include at least one operation or workflow id")

    return (
        TestsContract(
            operation_ids=operation_ids,
            workflow_ids=workflow_ids,
            case_ids=case_ids,
            operation_case_count=operation_case_count,
            workflow_case_count=workflow_case_count,
        ),
        mode_errors,
    )


def verify_bundle(
    bundle_dir: Path,
    *,
    legacy_allow: bool = False,
    legacy_reason: str | None = None,
) -> tuple[dict[str, Any], list[str], list[str]]:
    data_errors: list[str] = []
    structure_errors: list[str] = []
    summary: dict[str, Any] = {}

    missing_files = [name for name in REQUIRED_FILES if not (bundle_dir / name).is_file()]
    if missing_files:
        data_errors.extend(f"missing required file: {bundle_dir / name}" for name in missing_files)
        summary.update(
            {
                "legacy_bypass_used": legacy_allow,
                "legacy_reason": legacy_reason or "",
                "downgraded_structure_errors_count": 0,
                "data_errors_count": len(data_errors),
            }
        )
        return summary, data_errors, []

    try:
        inventory = _load_inventory(bundle_dir / "inventory.json")
        operations = inventory.operation_ids
        workflows = inventory.workflows
        coverage_mode = inventory.coverage_mode
        sampled_case_ids = inventory.sampled_case_ids
        tests_contract, mode_errors = _load_tests_contract(bundle_dir)
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
        data_errors.append(str(exc))
        summary.update(
            {
                "legacy_bypass_used": legacy_allow,
                "legacy_reason": legacy_reason or "",
                "downgraded_structure_errors_count": 0,
                "data_errors_count": len(data_errors),
            }
        )
        return summary, data_errors, []

    data_errors.extend(mode_errors)

    inventory_ops = set(operations)
    inventory_workflows = {workflow.workflow_id for workflow in workflows}

    for operation_id in sorted(tests_contract.operation_ids - inventory_ops):
        data_errors.append(f"inventory missing public operation from tests.yaml: {operation_id}")
    for operation_id in sorted(inventory_ops - tests_contract.operation_ids):
        data_errors.append(f"inventory public operation not found in tests.yaml: {operation_id}")

    for workflow_id in sorted(tests_contract.workflow_ids - inventory_workflows):
        data_errors.append(f"inventory missing primary workflow from tests.yaml: {workflow_id}")
    for workflow_id in sorted(inventory_workflows - tests_contract.workflow_ids):
        data_errors.append(f"inventory primary workflow not found in tests.yaml: {workflow_id}")

    if coverage_mode == "sampled":
        for case_id in sorted(sampled_case_ids - tests_contract.case_ids):
            data_errors.append(
                f"inventory.sampled_case_ids references unknown tests.yaml case_id: {case_id}"
            )

    for operation_id in operations:
        if operation_id not in op_to_cases:
            data_errors.append(f"unmapped public operation in traceability.csv: {operation_id}")

    for workflow in workflows:
        if workflow.workflow_id not in workflow_to_cases:
            data_errors.append(f"unmapped primary workflow in traceability.csv: {workflow.workflow_id}")
        loop = loops_by_id.get(workflow.workflow_id)
        if loop is None:
            data_errors.append(f"primary workflow missing in workflow_loops.json: {workflow.workflow_id}")
            continue
        if not loop["continuity_assertions"]:
            data_errors.append(
                f"workflow has no continuity_assertions: {workflow.workflow_id}"
            )
        if workflow.requires_reset and not loop["reset_assertions"]:
            data_errors.append(
                f"workflow requires reset_assertions but none were provided: {workflow.workflow_id}"
            )

    for run_id in run_to_cases:
        if run_id not in known_run_ids:
            data_errors.append(f"traceability references unknown adapter_run_id: {run_id}")

    for run_id, case_ids in run_to_cases.items():
        for case_id in case_ids:
            pair = (run_id, case_id)
            if case_id not in all_result_cases:
                data_errors.append(f"traceability case not present in adapter_results.jsonl: {case_id}")
            if pair not in baseline_pass_pairs:
                data_errors.append(
                    "traceability pair has no baseline pass result: "
                    f"run_id={run_id} case_id={case_id}"
                )
            if pair in baseline_nonpass_pairs:
                data_errors.append(
                    "traceability pair has non-pass baseline result: "
                    f"run_id={run_id} case_id={case_id}"
                )

    for case_id in sorted(traceability_cases - tests_contract.case_ids):
        data_errors.append(f"traceability.csv references unknown tests.yaml case_id: {case_id}")

    required_case_ids = (
        tests_contract.case_ids if coverage_mode == "exhaustive" else sampled_case_ids
    )
    required_case_label = (
        "tests.yaml" if coverage_mode == "exhaustive" else "inventory.sampled_case_ids"
    )

    for case_id in sorted(required_case_ids - traceability_cases):
        data_errors.append(f"{required_case_label} case missing from traceability.csv: {case_id}")

    for case_id in sorted(required_case_ids - all_result_cases):
        data_errors.append(f"{required_case_label} case missing from adapter_results.jsonl: {case_id}")

    baseline_case_ids = {case_id for _, case_id in baseline_pass_pairs}
    for case_id in sorted(required_case_ids - baseline_case_ids):
        data_errors.append(
            f"{required_case_label} case has no baseline pass in adapter_results.jsonl: {case_id}"
        )

    if not mutation_pass:
        data_errors.append("mutation_check.json.pass must be true")
    if detected_failures < required_mutations:
        data_errors.append(
            "mutation sensitivity gate failed: detected_failures < required_mutations "
            f"({detected_failures} < {required_mutations})"
        )

    if not parity_pass:
        data_errors.append("parity.json.pass must be true")
    if parity_diff_count != 0:
        data_errors.append(f"parity.json.diff_count must be 0 (found {parity_diff_count})")

    structure_summary: dict[str, Any] = {}
    try:
        structure_summary, structure_errors = _validate_structure_contract(
            bundle_dir=bundle_dir,
            tests_contract=tests_contract,
        )
    except EvidenceError as exc:
        structure_errors.append(str(exc))
        structure_summary = {
            "structure_contract_source": "unknown",
            "structure_stateful_mode": bool(
                tests_contract.workflow_ids or tests_contract.workflow_case_count > 0
            ),
            "structure_spec_required_sections": 0,
            "structure_verify_required_sections": 0,
            "structure_errors_count": len(structure_errors),
        }

    downgraded_structure_errors: list[str] = []
    if legacy_allow:
        downgraded_structure_errors = sorted(structure_errors)
        final_errors = data_errors
    else:
        final_errors = data_errors + structure_errors

    summary.update(
        {
            "operations_expected": len(operations),
            "operations_mapped": len(op_to_cases),
            "workflows_expected": len(workflows),
            "workflows_mapped": len(workflow_to_cases),
            "coverage_mode": coverage_mode,
            "tests_operations_expected": len(tests_contract.operation_ids),
            "tests_workflows_expected": len(tests_contract.workflow_ids),
            "tests_cases_expected": len(tests_contract.case_ids),
            "sampled_cases_expected": len(sampled_case_ids),
            "required_cases_expected": len(required_case_ids),
            "tests_operation_cases": tests_contract.operation_case_count,
            "tests_workflow_cases": tests_contract.workflow_case_count,
            "traceability_cases": len(traceability_cases),
            "baseline_pass_pairs": len(baseline_pass_pairs),
            "required_mutations": required_mutations,
            "detected_failures": detected_failures,
            "parity_diff_count": parity_diff_count,
            "legacy_bypass_used": legacy_allow,
            "legacy_reason": legacy_reason or "",
            "downgraded_structure_errors_count": len(downgraded_structure_errors),
            "data_errors_count": len(data_errors),
            "structure_errors_count": len(structure_errors),
        }
    )
    summary.update(structure_summary)

    return summary, final_errors, downgraded_structure_errors


def _format_text(
    result: str,
    summary: dict[str, Any],
    errors: list[str],
    downgraded_structure_errors: list[str],
) -> str:
    lines = [f"Evidence bundle verification: {result}"]
    if summary:
        lines.append("Summary:")
        for key in sorted(summary):
            lines.append(f"- {key}: {summary[key]}")
    if downgraded_structure_errors:
        lines.append("Downgraded structure errors (legacy bypass):")
        for err in downgraded_structure_errors:
            lines.append(f"- {err}")
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
    parser.add_argument(
        "--legacy-allow",
        action="store_true",
        help="Break-glass mode: downgrade structure-contract errors only.",
    )
    parser.add_argument(
        "--legacy-reason",
        default="",
        help="Required rationale when --legacy-allow is set.",
    )
    args = parser.parse_args(argv)

    legacy_reason = args.legacy_reason.strip()
    if args.legacy_allow and not legacy_reason:
        print("legacy_reason_required: --legacy-reason must be provided when --legacy-allow is set")
        return 1
    if (not args.legacy_allow) and legacy_reason:
        print("legacy_reason_without_legacy_allow: pass --legacy-allow when using --legacy-reason")
        return 1

    bundle_dir = Path(args.bundle).expanduser().resolve()
    summary, errors, downgraded_structure_errors = verify_bundle(
        bundle_dir,
        legacy_allow=args.legacy_allow,
        legacy_reason=legacy_reason if args.legacy_allow else None,
    )
    result = "pass" if not errors else "fail"

    if args.format == "json":
        payload = {
            "result": result,
            "bundle": str(bundle_dir),
            "summary": summary,
            "errors": errors,
            "downgraded_structure_errors": downgraded_structure_errors,
        }
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        print(
            _format_text(
                result=result,
                summary=summary,
                errors=errors,
                downgraded_structure_errors=downgraded_structure_errors,
            )
        )

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
