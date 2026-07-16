#!/usr/bin/env python3
"""Emit one plan-bound SDR-v1 receipt for a Universalist seam decision."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised by the CLI boundary
    raise SystemExit(
        "PyYAML is required; run with `uv run --with pyyaml -- python3 "
        "scripts/emit_decision_receipt.py ...`"
    ) from exc


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = SKILL_ROOT / "references" / "decision-contract.yaml"
DEFAULT_TRIGGER_REFS = ("UNI-BOUNDARY", "UNI-CONSEQUENTIAL")
DEFAULT_CLAUSE_REFS = (
    "UNI-DISPOSITION-001",
    "UNI-MINIMAL-001",
    "UNI-MECHANICS-001",
    "UNI-ROOT-001",
)
RECEIPT_MARKER = "## Root decision receipt:"
PLAN_NAME = re.compile(r"^plan-(?P<plan_id>[A-Za-z0-9._-]+)\.md$")


class ReceiptError(RuntimeError):
    """A fail-closed decision-receipt boundary error."""


def run_json(command: Sequence[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise ReceiptError(f"required command not found: {command[0]}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise ReceiptError(f"command failed ({completed.returncode}): {' '.join(command)}\n{detail}")
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ReceiptError(f"command did not emit JSON: {' '.join(command)}") from exc
    if not isinstance(value, dict):
        raise ReceiptError(f"command emitted a non-object: {' '.join(command)}")
    return value


def load_contract(path: Path) -> tuple[dict[str, Any], str]:
    validation = run_json(
        ["seq", "skill-contract", "validate", "--file", str(path), "--format", "json"]
    )
    report = validation.get("skill_contract")
    if not isinstance(report, dict) or report.get("valid") is not True:
        raise ReceiptError(f"invalid decision contract: {path}")
    fingerprint = report.get("fingerprint")
    if not isinstance(fingerprint, str) or not fingerprint:
        raise ReceiptError("decision contract validation omitted its fingerprint")

    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ReceiptError("decision contract must be an object")
    contract = loaded.get("skill_decision_contract", loaded)
    if not isinstance(contract, dict):
        raise ReceiptError("skill_decision_contract must be an object")
    skill = contract.get("skill")
    if not isinstance(skill, dict) or skill.get("name") != "universalist":
        raise ReceiptError("decision contract must belong to universalist")
    return contract, fingerprint


def id_set(rows: Any, field: str) -> set[str]:
    if not isinstance(rows, list):
        return set()
    return {
        value
        for row in rows
        if isinstance(row, dict) and isinstance((value := row.get(field)), str)
    }


def require_known(values: Sequence[str], known: set[str], label: str) -> None:
    unknown = sorted(set(values) - known)
    if unknown:
        raise ReceiptError(f"unknown {label}: {', '.join(unknown)}")


def git_value(repo: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise ReceiptError(f"git {' '.join(arguments)} failed: {detail}")
    return completed.stdout.strip()


def resolve_repo(plan: Path) -> Path:
    root = git_value(plan.parent, "rev-parse", "--show-toplevel")
    return Path(root).resolve()


def plan_identity(plan: Path, repo: Path, explicit_decision_id: str | None) -> tuple[str, str]:
    match = PLAN_NAME.fullmatch(plan.name)
    plan_id = match.group("plan_id") if match else "template"
    if explicit_decision_id:
        decision_id = explicit_decision_id
    elif match:
        decision_id = f"UNI-{plan_id}"
    else:
        raise ReceiptError("--decision-id is required for a non-addressed plan")
    try:
        plan_relative = plan.relative_to(repo).as_posix()
    except ValueError as exc:
        raise ReceiptError(f"plan is outside the git repository: {plan}") from exc
    return plan_id, decision_id


def require_canonical_plan(plan: Path, repo: Path) -> None:
    match = PLAN_NAME.fullmatch(plan.name)
    if not match:
        raise ReceiptError("--write-plan requires a ledger-addressed plan filename")
    expected = repo / ".ledger" / "universalist" / plan.name
    if plan != expected:
        raise ReceiptError(f"--write-plan requires the canonical plan path: {expected}")


def plan_status(text: str) -> str:
    match = re.search(r"^## Status:\s*(.+?)\s*$", text, flags=re.MULTILINE)
    return match.group(1) if match else "unknown"


def unique(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(values))


def validate_receipt(receipt: dict[str, Any]) -> None:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", encoding="utf-8") as handle:
        json.dump(receipt, handle, sort_keys=True)
        handle.flush()
        validation = run_json(
            [
                "seq",
                "skill-decision-receipt",
                "validate",
                "--file",
                handle.name,
                "--format",
                "json",
            ]
        )
    report = validation.get("skill_decision_receipt")
    if not isinstance(report, dict) or report.get("valid") is not True:
        raise ReceiptError("Seq rejected the generated SDR-v1 receipt")


def append_receipt(plan: Path, receipt_json: str, decision_id: str) -> None:
    text = plan.read_text(encoding="utf-8")
    if '"skill_decision_receipt"' in text:
        raise ReceiptError(f"plan already contains a decision receipt: {plan}")
    emitted_marker = f"{RECEIPT_MARKER} emitted ({decision_id})"
    marker_line = re.compile(r"^## Root decision receipt:.*$", flags=re.MULTILINE)
    if marker_line.search(text):
        text = marker_line.sub(emitted_marker, text, count=1)
    else:
        status_line = re.compile(r"^## Status:.*$", flags=re.MULTILINE)
        if status_line.search(text):
            text = status_line.sub(f"{emitted_marker}\n\\g<0>", text, count=1)
        else:
            text = text.rstrip() + f"\n{emitted_marker}\n"
    updated = text.rstrip() + "\n\n" + receipt_json.rstrip() + "\n"
    mode = plan.stat().st_mode
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=plan.parent,
        prefix=f".{plan.name}.",
        delete=False,
    ) as handle:
        temp_path = Path(handle.name)
        handle.write(updated)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.chmod(temp_path, mode)
        os.replace(temp_path, plan)
    finally:
        temp_path.unlink(missing_ok=True)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        description="Emit one concrete SDR-v1 receipt from a Universalist plan."
    )
    value.add_argument("--plan", required=True, type=Path)
    value.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    value.add_argument("--decision-id")
    value.add_argument("--trigger-ref", action="append", dest="trigger_refs")
    value.add_argument("--clause-ref", action="append", dest="clause_refs")
    value.add_argument("--question", required=True)
    value.add_argument("--alternative", action="append", default=[])
    value.add_argument("--selected-route", required=True)
    value.add_argument("--rejected-route", action="append", required=True, dest="rejected_routes")
    value.add_argument("--expected-outcome", required=True)
    value.add_argument(
        "--disposition",
        required=True,
        choices=("preserved", "introduced", "changed", "repaired", "removed", "bypass-justified"),
    )
    value.add_argument("--construction", required=True)
    value.add_argument("--law", required=True)
    value.add_argument("--falsifier", required=True)
    value.add_argument("--advanced-mechanics", required=True)
    value.add_argument("--evidence-ref", action="append", default=[], dest="evidence_refs")
    value.add_argument("--write-plan", action="store_true")
    return value


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        plan = args.plan.resolve(strict=True)
        contract_path = args.contract.resolve(strict=True)
        plan_text = plan.read_text(encoding="utf-8")
        if re.search(r"^# Universalist Plan\s*$", plan_text, flags=re.MULTILINE) is None:
            raise ReceiptError(f"not a Universalist plan: {plan}")
        repo = resolve_repo(plan)
        plan_id, decision_id = plan_identity(plan, repo, args.decision_id)
        if args.write_plan:
            require_canonical_plan(plan, repo)

        contract, contract_fingerprint = load_contract(contract_path)
        trigger_refs = tuple(args.trigger_refs or DEFAULT_TRIGGER_REFS)
        clause_refs = tuple(args.clause_refs or DEFAULT_CLAUSE_REFS)
        require_known(trigger_refs, id_set(contract.get("triggers"), "trigger_id"), "trigger refs")
        require_known(clause_refs, id_set(contract.get("clauses"), "clause_id"), "clause refs")
        route_ids = id_set(contract.get("routes"), "route_id")
        require_known((args.selected_route,), route_ids, "selected route")
        require_known(args.rejected_routes, route_ids, "rejected routes")
        if args.selected_route in args.rejected_routes:
            raise ReceiptError("selected route cannot also be rejected")

        package = json.loads((SKILL_ROOT / "package.json").read_text(encoding="utf-8"))
        skill_version = package.get("version", "") if isinstance(package, dict) else ""
        plan_relative = plan.relative_to(repo).as_posix()
        alternatives = unique(
            [args.selected_route, *args.rejected_routes, *args.alternative]
        )
        receipt = {
            "skill_decision_receipt": {
                "receipt_version": "SDR-v1",
                "decision_id": decision_id,
                "skill": "universalist",
                "skill_version": str(skill_version),
                "skill_contract_fingerprint": contract_fingerprint,
                "trigger_refs": list(trigger_refs),
                "clause_refs": list(clause_refs),
                "question": args.question,
                "alternatives_considered": alternatives,
                "selected_route": args.selected_route,
                "rejected_routes": unique(args.rejected_routes),
                "expected_outcome": args.expected_outcome,
                "artifact_state": {
                    "repo": str(repo),
                    "head": git_value(repo, "rev-parse", "HEAD"),
                    "plan_id": plan_id,
                    "plan_path": plan_relative,
                    "plan_status": plan_status(plan_text),
                    "boundary_disposition": args.disposition,
                    "construction": args.construction,
                    "law": args.law,
                    "falsifier": args.falsifier,
                    "advanced_mechanics": args.advanced_mechanics,
                },
                "evidence_refs": unique([f"plan:{plan_relative}", *args.evidence_refs]),
            }
        }
        validate_receipt(receipt)
        receipt_json = json.dumps(receipt, separators=(",", ":"), sort_keys=True)
        if args.write_plan:
            append_receipt(plan, receipt_json, decision_id)
        print(receipt_json)
        return 0
    except (OSError, ReceiptError, ValueError, json.JSONDecodeError) as exc:
        print(f"emit_decision_receipt: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
