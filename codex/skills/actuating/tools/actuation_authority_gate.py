#!/usr/bin/env -S uv run python
"""Actuating pre-mutation authority gate.

This tool is intentionally local and fail-closed. It does not acquire claims,
mutate the st workspace, or inspect Git. It consumes a GCR-v2 receipt and emits
an APMA-v1 pre-mutation authority receipt only when the supplied intended edit
resources are covered by the current GCR claim/fencing/resource authority.

Primary invariant:
    No APMA-v1 with verdict=mutation-authorized => no actuation-labeled patch.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any, Iterable

YES = {"yes", "true", "1", True}
NO = {"no", "false", "0", False}
RESOURCE_RE = re.compile(r"^(read|write|exclusive):(.+)$")


class GateError(ValueError):
    pass


def load_json(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    value = json.loads(text)
    if not isinstance(value, dict):
        raise GateError("input: expected JSON object")
    return value


def unwrap(value: dict[str, Any], key: str) -> dict[str, Any]:
    body = value.get(key, value)
    if not isinstance(body, dict):
        raise GateError(f"{key}: expected object")
    return body


def is_yes(value: Any) -> bool:
    return value in YES or (isinstance(value, str) and value.lower() in YES)


def is_no(value: Any) -> bool:
    return value in NO or (isinstance(value, str) and value.lower() in NO)


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _norm_path(path: str) -> str:
    if not path or "\x00" in path:
        raise GateError(f"invalid path resource: {path!r}")
    if path.startswith("/"):
        raise GateError(f"absolute path resource is not allowed: {path!r}")
    parts = PurePosixPath(path).parts
    if any(part == ".." for part in parts):
        raise GateError(f"path traversal is not allowed: {path!r}")
    normalized = str(PurePosixPath(path))
    if normalized == ".":
        raise GateError("empty path resource")
    return normalized


def parse_root(root: str) -> tuple[str, str]:
    if ":" not in root:
        raise GateError(f"resource root missing kind: {root!r}")
    kind, value = root.split(":", 1)
    if kind not in {"path", "symbol", "generated", "schema", "service", "git", "repo"}:
        raise GateError(f"unsupported resource kind: {kind!r}")
    if kind == "path":
        return kind, _norm_path(value)
    if kind == "symbol":
        if "#" not in value:
            raise GateError(f"symbol resource missing #: {root!r}")
        path, symbol = value.split("#", 1)
        if not symbol:
            raise GateError(f"symbol resource missing symbol name: {root!r}")
        return kind, f"{_norm_path(path)}#{symbol}"
    if kind == "repo" and value != "all":
        raise GateError(f"unsupported repo resource: {root!r}")
    if not value:
        raise GateError(f"empty resource value: {root!r}")
    return kind, value


def parse_resource(text: str) -> dict[str, str]:
    match = RESOURCE_RE.match(text)
    if not match:
        raise GateError(f"resource must be mode:kind:value, got {text!r}")
    mode, root = match.groups()
    kind, value = parse_root(root)
    return {"mode": mode, "root": f"{kind}:{value}"}


def normalize_claim_resources(rows: Iterable[Any]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise GateError(f"coordination.resources[{index}]: expected object")
        mode = row.get("mode")
        root = row.get("root")
        if mode not in {"read", "write", "exclusive"}:
            raise GateError(f"coordination.resources[{index}].mode: invalid")
        if not isinstance(root, str):
            raise GateError(f"coordination.resources[{index}].root: missing")
        kind, value = parse_root(root)
        out.append({"mode": mode, "root": f"{kind}:{value}"})
    return out


def split_root(root: str) -> tuple[str, str]:
    kind, value = parse_root(root)
    return kind, value


def path_covers(parent: str, child: str) -> bool:
    parent = _norm_path(parent)
    child = _norm_path(child)
    return child == parent or child.startswith(parent.rstrip("/") + "/")


def resource_covers(claim: dict[str, str], intended: dict[str, str]) -> bool:
    claim_mode = claim["mode"]
    intended_mode = intended["mode"]
    if claim_mode == "read":
        return intended_mode == "read" and _root_covers(claim["root"], intended["root"])
    if claim_mode == "write":
        return intended_mode in {"read", "write"} and _root_covers(claim["root"], intended["root"])
    if claim_mode == "exclusive":
        return _root_covers(claim["root"], intended["root"])
    return False


def _root_covers(claim_root: str, intended_root: str) -> bool:
    c_kind, c_value = split_root(claim_root)
    i_kind, i_value = split_root(intended_root)
    if c_kind == "repo" and c_value == "all":
        return True
    if c_kind == "path" and i_kind == "path":
        return path_covers(c_value, i_value)
    if c_kind == "path" and i_kind == "symbol":
        path, _symbol = i_value.split("#", 1)
        return path_covers(c_value, path)
    if c_kind == i_kind:
        return c_value == i_value
    return False


def coverage(claims: list[dict[str, str]], intended: list[dict[str, str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for need in intended:
        covers = [claim for claim in claims if resource_covers(claim, need)]
        rows.append({"intended": need, "covered": bool(covers), "covering_resources": covers})
    return rows


def validate_gcr_for_authority(gcr: dict[str, Any]) -> dict[str, Any]:
    if gcr.get("receipt_version") != "GCR-v2":
        raise GateError("gcr.receipt_version: expected GCR-v2")
    allowed = gcr.get("execution_allowed")
    if not is_yes(allowed):
        reasons = gcr.get("denial_reasons", [])
        raise GateError("gcr.execution_allowed:not-yes" + (f":{reasons}" if reasons else ""))
    if gcr.get("denial_reasons"):
        raise GateError("gcr.denial_reasons:present")

    workspace = gcr.get("workspace")
    plan = gcr.get("plan")
    coordination = gcr.get("coordination")
    graph = gcr.get("graph")
    projection = gcr.get("projection")
    for label, value in {
        "workspace": workspace,
        "plan": plan,
        "coordination": coordination,
        "graph": graph,
        "projection": projection,
    }.items():
        if not isinstance(value, dict):
            raise GateError(f"gcr.{label}: expected object")

    selected = plan.get("selected_task_ids")
    if not isinstance(selected, list) or not selected or any(not isinstance(x, str) or not x for x in selected):
        raise GateError("gcr.plan.selected_task_ids: missing")
    projected = projection.get("selected_task_ids")
    if projected != selected:
        raise GateError("gcr.projection.selected_task_ids:mismatch")
    if projection.get("session_id") != coordination.get("session_id"):
        raise GateError("gcr.projection.session_id:mismatch")
    if coordination.get("workspace_sequence") != workspace.get("workspace_sequence"):
        raise GateError("gcr.coordination.workspace_sequence:stale")
    if coordination.get("plan_sequence") != plan.get("plan_sequence"):
        raise GateError("gcr.coordination.plan_sequence:stale")
    if coordination.get("branch_epoch") != workspace.get("branch_epoch"):
        raise GateError("gcr.coordination.branch_epoch:stale")
    if coordination.get("lease_current") is not True:
        raise GateError("gcr.coordination.lease_current:not-true")
    if coordination.get("fencing_current") is not True:
        raise GateError("gcr.coordination.fencing_current:not-true")
    if coordination.get("conflicting_claims"):
        raise GateError("gcr.coordination.conflicting_claims:present")
    if graph.get("gate_passed") is not True:
        raise GateError("gcr.graph.gate_passed:not-true")
    if graph.get("graph_debt"):
        raise GateError("gcr.graph.graph_debt:present")
    for field in ("claim_id", "session_id", "executor", "fencing_token"):
        if coordination.get(field) in (None, ""):
            raise GateError(f"gcr.coordination.{field}:missing")
    resources = normalize_claim_resources(coordination.get("resources", []))
    if not resources:
        raise GateError("gcr.coordination.resources:empty")
    return {
        "workspace": workspace,
        "plan": plan,
        "coordination": coordination,
        "graph": graph,
        "projection": projection,
        "resources": resources,
        "selected_task_ids": selected,
    }


def diagnose_gcr(gcr: dict[str, Any]) -> dict[str, Any]:
    workspace = gcr.get("workspace") if isinstance(gcr.get("workspace"), dict) else {}
    plan = gcr.get("plan") if isinstance(gcr.get("plan"), dict) else {}
    coordination = gcr.get("coordination") if isinstance(gcr.get("coordination"), dict) else {}
    denial_reasons = gcr.get("denial_reasons", []) if isinstance(gcr.get("denial_reasons"), list) else []
    reasons_text = " ".join(str(x).lower() for x in denial_reasons)
    seq_mismatches = []
    if coordination.get("workspace_sequence") != workspace.get("workspace_sequence"):
        seq_mismatches.append("workspace_sequence")
    if coordination.get("plan_sequence") != plan.get("plan_sequence"):
        seq_mismatches.append("plan_sequence")
    if coordination.get("branch_epoch") != workspace.get("branch_epoch"):
        seq_mismatches.append("branch_epoch")
    stale_projection = any(word in reasons_text for word in ("stale", "session", "projection", "view"))
    if is_yes(gcr.get("execution_allowed")):
        stage = "gcr-allowed"
        hard_stop = False
        next_action = "authorize-intended-resources"
    elif seq_mismatches or stale_projection:
        stage = "blocked-self-invalidating-gcr-candidate"
        hard_stop = True
        next_action = "stop-actuating-release-claim-repair-st-or-refresh-session-before-recompiling"
    else:
        stage = "blocked-gcr-denied"
        hard_stop = True
        next_action = "return-to-st-claim-gcr-frontier"
    return {
        "actuation_gcr_diagnosis": {
            "stage": stage,
            "hard_stop": hard_stop,
            "next_action": next_action,
            "gcr_id": gcr.get("gcr_id"),
            "execution_allowed": gcr.get("execution_allowed"),
            "denial_reasons": denial_reasons,
            "sequence_mismatches": seq_mismatches,
            "workspace_sequence": workspace.get("workspace_sequence"),
            "coordination_workspace_sequence": coordination.get("workspace_sequence"),
            "plan_sequence": plan.get("plan_sequence"),
            "coordination_plan_sequence": coordination.get("plan_sequence"),
            "branch_epoch": workspace.get("branch_epoch"),
            "coordination_branch_epoch": coordination.get("branch_epoch"),
        }
    }


def make_apma(gcr: dict[str, Any], run_id: str, intended_resources: list[dict[str, str]]) -> dict[str, Any]:
    if not run_id:
        raise GateError("run_id: required")
    if not intended_resources:
        raise GateError("intended_resources: at least one write/exclusive resource required")
    if not any(r["mode"] in {"write", "exclusive"} for r in intended_resources):
        raise GateError("intended_resources: material mutation must include write or exclusive resource")
    parts = validate_gcr_for_authority(gcr)
    cov = coverage(parts["resources"], intended_resources)
    uncovered = [row for row in cov if not row["covered"]]
    if uncovered:
        missing = ", ".join(f"{r['intended']['mode']}:{r['intended']['root']}" for r in uncovered)
        raise GateError(f"intended_resources:not-covered:{missing}")

    workspace = parts["workspace"]
    plan = parts["plan"]
    coordination = parts["coordination"]
    apma = {
        "actuation_pre_mutation_authority": {
            "version": "APMA-v1",
            "verdict": "mutation-authorized",
            "issued_at": utc_now(),
            "run_id": run_id,
            "workspace": {
                "workspace_id": workspace.get("workspace_id"),
                "target_branch": workspace.get("target_branch"),
                "head": workspace.get("head"),
                "workspace_sequence": workspace.get("workspace_sequence"),
                "branch_epoch": workspace.get("branch_epoch"),
                "working_tree_fingerprint": workspace.get("working_tree_fingerprint"),
            },
            "plan": {
                "plan_id": plan.get("plan_id"),
                "plan_sequence": plan.get("plan_sequence"),
                "selected_task_ids": parts["selected_task_ids"],
            },
            "coordination": {
                "claim_id": coordination.get("claim_id"),
                "session_id": coordination.get("session_id"),
                "executor": coordination.get("executor"),
                "fencing_token": coordination.get("fencing_token"),
                "lease_current": coordination.get("lease_current"),
                "fencing_current": coordination.get("fencing_current"),
                "resources": parts["resources"],
            },
            "gcr": {
                "gcr_id": gcr.get("gcr_id"),
                "execution_allowed": "yes",
                "projection_view_id": parts["projection"].get("view_id"),
                "projection_digest": parts["projection"].get("projection_digest"),
            },
            "intended_resources": intended_resources,
            "resource_coverage": cov,
            "hard_rule": "No APMA-v1 mutation-authorized receipt means no actuation-labeled patch.",
        }
    }
    return apma


def validate_apma(value: dict[str, Any], intended_resources: list[dict[str, str]]) -> dict[str, Any]:
    apma = unwrap(value, "actuation_pre_mutation_authority")
    if apma.get("version") != "APMA-v1":
        raise GateError("apma.version: expected APMA-v1")
    if apma.get("verdict") != "mutation-authorized":
        raise GateError("apma.verdict:not-authorized")
    coordination = apma.get("coordination")
    plan = apma.get("plan")
    gcr = apma.get("gcr")
    for label, body in {"coordination": coordination, "plan": plan, "gcr": gcr}.items():
        if not isinstance(body, dict):
            raise GateError(f"apma.{label}: expected object")
    if gcr.get("execution_allowed") != "yes":
        raise GateError("apma.gcr.execution_allowed:not-yes")
    if not plan.get("selected_task_ids"):
        raise GateError("apma.plan.selected_task_ids:empty")
    if not coordination.get("claim_id"):
        raise GateError("apma.coordination.claim_id:missing")
    if coordination.get("lease_current") is not True or coordination.get("fencing_current") is not True:
        raise GateError("apma.coordination.currentity:not-true")
    resources = normalize_claim_resources(coordination.get("resources", []))
    declared_intended = [parse_resource(f"{row['mode']}:{row['root']}") for row in apma.get("intended_resources", []) if isinstance(row, dict) and "mode" in row and "root" in row]
    if intended_resources:
        cov = coverage(resources, intended_resources)
        uncovered = [row for row in cov if not row["covered"]]
        if uncovered:
            missing = ", ".join(f"{r['intended']['mode']}:{r['intended']['root']}" for r in uncovered)
            raise GateError(f"mutation_resources:not-covered:{missing}")
    else:
        cov = coverage(resources, declared_intended)
    return {
        "actuation_authority_check": {
            "verdict": "pass",
            "run_id": apma.get("run_id"),
            "gcr_id": gcr.get("gcr_id"),
            "claim_id": coordination.get("claim_id"),
            "selected_task_ids": plan.get("selected_task_ids"),
            "checked_resources": intended_resources or declared_intended,
            "resource_coverage": cov,
        }
    }


def resource_args(args: argparse.Namespace) -> list[dict[str, str]]:
    resources: list[dict[str, str]] = []
    for text in args.resource or []:
        resources.append(parse_resource(text))
    for path in args.path or []:
        resources.append(parse_resource(f"write:path:{path}"))
    return resources


def emit(obj: dict[str, Any], output: str | None = None) -> int:
    text = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    return 0


def fail(exc: Exception) -> int:
    print(json.dumps({"actuation_authority_gate": {"verdict": "fail", "error": str(exc)}}, indent=2, sort_keys=True), file=sys.stderr)
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Actuating APMA-v1 pre-mutation authority gate")
    sub = parser.add_subparsers(dest="cmd", required=True)

    authorize = sub.add_parser("authorize", help="Emit APMA-v1 from an allowed GCR-v2 and intended resources")
    authorize.add_argument("--gcr", required=True, help="GCR-v2 JSON file or -")
    authorize.add_argument("--run-id", required=True)
    authorize.add_argument("--resource", action="append", help="Intended resource as mode:kind:value; repeatable")
    authorize.add_argument("--path", action="append", help="Convenience for write:path:<PATH>; repeatable")
    authorize.add_argument("--out")

    check = sub.add_parser("check", help="Validate APMA-v1 and optional intended resources")
    check.add_argument("--apma", required=True, help="APMA-v1 JSON file or -")
    check.add_argument("--resource", action="append")
    check.add_argument("--path", action="append")

    diagnose = sub.add_parser("diagnose-gcr", help="Classify GCR-v2 denial, including self-invalidating sequence/view failures")
    diagnose.add_argument("--gcr", required=True, help="GCR-v2 JSON file or -")

    args = parser.parse_args(argv)
    try:
        if args.cmd == "authorize":
            gcr = unwrap(load_json(args.gcr), "graph_control_receipt")
            return emit(make_apma(gcr, args.run_id, resource_args(args)), args.out)
        if args.cmd == "check":
            return emit(validate_apma(load_json(args.apma), resource_args(args)))
        if args.cmd == "diagnose-gcr":
            gcr = unwrap(load_json(args.gcr), "graph_control_receipt")
            return emit(diagnose_gcr(gcr))
        raise GateError(f"unknown command {args.cmd}")
    except Exception as exc:
        return fail(exc)


if __name__ == "__main__":
    raise SystemExit(main())
