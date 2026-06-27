#!/usr/bin/env python3
"""Fail-closed closure gate for `$resolve` material runs.

Consumes a summary JSON/YAML and/or runs JSONL projection. Supports both flat
and lightly nested fields produced by seq/controller projections.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, Iterable, List, Optional

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


def load_doc(path: Optional[str]) -> Any:
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    ext = os.path.splitext(path)[1].lower()
    if ext in {".yaml", ".yml"}:
        if yaml is None:
            raise ValueError("YAML input requires PyYAML; install pyyaml or pass JSON")
        return yaml.safe_load(text)
    return json.loads(text)


def load_jsonl(path: Optional[str]) -> List[Dict[str, Any]]:
    if not path:
        return []
    rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSONL: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_no}: row must be an object")
            rows.append(value)
    return rows


def get(row: Dict[str, Any], *paths: str, default: Any = None) -> Any:
    for path in paths:
        if path in row:
            return row[path]
        cur: Any = row
        ok = True
        for part in path.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                ok = False
                break
        if ok:
            return cur
    return default


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"yes", "true", "1", "passed", "pass", "closed", "complete"}
    return bool(value)


def num(value: Any, default: float = 0) -> float:
    if value is None:
        return default
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return default
    if isinstance(value, (list, dict)):
        return float(len(value))
    return default


def run_id(row: Dict[str, Any], index: int) -> str:
    return str(get(row, "run_id", "id", "session_id", default=f"row-{index}"))


def campaign_id(row: Dict[str, Any]) -> str:
    return str(get(row, "campaign_id", "campaign.id", "campaign", default="") or "").strip()


def campaign_ids(summary: Any, rows: List[Dict[str, Any]]) -> List[str]:
    ids: List[str] = []
    if isinstance(summary, dict):
        single = str(get(summary, "campaign_id", default="") or "").strip()
        if single:
            ids.append(single)
        campaigns = summary.get("campaigns")
        if isinstance(campaigns, dict):
            for key, item in campaigns.items():
                if isinstance(item, dict):
                    ident = str(get(item, "campaign_id", "campaign.id", default=key) or key).strip()
                else:
                    ident = str(key).strip()
                if ident:
                    ids.append(ident)
        if isinstance(campaigns, list):
            for item in campaigns:
                if not isinstance(item, dict):
                    continue
                ident = str(get(item, "campaign_id", default="") or "").strip()
                if ident:
                    ids.append(ident)
    for row in rows:
        ident = campaign_id(row)
        if ident:
            ids.append(ident)
    return sorted(set(ids))


def resolve_campaign(explicit: Optional[str], summary: Any, rows: List[Dict[str, Any]]) -> str:
    if explicit is not None:
        ident = explicit.strip()
        if not ident:
            raise ValueError("--campaign cannot be empty")
        return ident
    ids = campaign_ids(summary, rows)
    if len(ids) == 1:
        return ids[0]
    if not ids:
        raise ValueError("no mechanically inferable campaign id")
    raise ValueError(f"multiple campaigns found; pass --campaign ({', '.join(ids)})")


def rows_for_campaign(rows: List[Dict[str, Any]], campaign: str) -> List[Dict[str, Any]]:
    return [row for row in rows if campaign_id(row) == campaign]


def summary_for_campaign(summary: Any, campaign: str) -> Any:
    if not isinstance(summary, dict):
        return summary
    if str(get(summary, "campaign_id", default="") or "").strip() == campaign:
        return summary
    campaigns = summary.get("campaigns")
    if isinstance(campaigns, dict):
        item = campaigns.get(campaign)
        return item if isinstance(item, dict) else {}
    if isinstance(campaigns, list):
        for item in campaigns:
            if isinstance(item, dict) and str(get(item, "campaign_id", default="") or "").strip() == campaign:
                return item
    if not str(get(summary, "campaign_id", default="") or "").strip() and not campaigns:
        return summary
    return {}


def is_material(row: Dict[str, Any]) -> bool:
    signal = (
        truthy(get(row, "c3_required", "c3.required", default=False))
        or truthy(get(row, "delivery_closed", "delivery.closed", default=False))
        or truthy(get(row, "finding_bearing_workflow", default=False))
    )
    marker = get(row, "material", "is_material", "campaign.material", default=None)
    if marker is not None:
        return truthy(marker) or signal
    return signal


def finding_bearing(row: Dict[str, Any]) -> bool:
    if truthy(get(row, "finding_bearing_workflow", default=False)):
        return True
    findings = get(row, "findings_total", "findings.total", "raw_findings", default=None)
    if findings is not None:
        return num(findings) > 0
    return truthy(get(row, "c3_required", "c3.required", default=False))


def summary_requires_material_runs(summary: Any) -> bool:
    if not isinstance(summary, dict):
        return False
    return (
        truthy(get(summary, "c3_required", "c3.required", default=False))
        or truthy(get(summary, "finding_bearing_workflow", default=False))
        or truthy(get(summary, "material", default=False))
        or num(get(summary, "strict_progress", "potential.strict_progress", default=0)) > 0
        or num(get(summary, "runs_total", "material_runs_total", default=0)) > 0
    )


def violation(scope: str, ident: str, code: str, detail: str) -> Dict[str, str]:
    return {"scope": scope, "id": ident, "code": code, "detail": detail}


def evaluate_run(row: Dict[str, Any], index: int) -> List[Dict[str, str]]:
    ident = run_id(row, index)
    out: List[Dict[str, str]] = []
    material = is_material(row)

    c3_required = truthy(get(row, "c3_required", "c3.required", default=False))
    c3_entered = truthy(get(row, "c3_entered", "c3.entered", default=False))
    c3_closed = truthy(get(row, "c3_closed", "c3.closed", default=False))
    delivery_closed = truthy(get(row, "delivery_closed", "delivery.closed", default=False))
    terminal_closed = truthy(get(row, "terminal_closed", "terminal.closed", default=False))
    compression_state = str(get(row, "compression_state", "compression.state", default="")).strip().upper()
    batches_total = num(get(row, "batches_total", "batches.total", default=0))
    kernel_accepted = truthy(get(row, "kernel.accepted", "kernel_accepted", default=False))
    strict_progress = num(get(row, "potential.strict_progress", "strict_progress", "potential_strict_progress", default=0))
    closure_gate_status = str(get(row, "closure_gate.status", "closure_gate_status", "closure.status", default="")).strip().lower()
    semantic_surface_delta = num(get(row, "semantic_surface_delta", "semantic_surface.delta", default=0))
    ac_rebased = truthy(get(row, "ac_rebased", "acceptance.rebased", default=False))
    orphan_code_constructs = max(
        num(get(row, "orphan_code_constructs", "orphans.code_constructs", default=0)),
        num(get(row, "realization_map.orphan_code_constructs", default=0)),
    )
    unmapped_proof_actions = max(
        num(get(row, "unmapped_proof_actions", "proof.unmapped_actions", default=0)),
        num(get(row, "proof_basis.unmapped_proof_actions", default=0)),
    )
    wound_specific_tests = max(
        num(get(row, "wound_specific_tests", "proof.wound_specific_tests", default=0)),
        num(get(row, "proof_basis.wound_specific_tests", default=0)),
    )
    wound_tests_mapped = truthy(get(row, "wound_specific_tests_class_mapped", "wound_specific_tests_mapped", "proof.wound_specific_tests_class_mapped", default=False))
    open_batches = num(get(row, "open_batches_total", "batches.open_total", default=0)) + num(get(row, "open_batch_ids", "batches.open_ids", default=0))
    terminal_counterexamples = num(get(row, "conformance.novel_in_horizon_counterexamples", default=0)) + num(get(row, "terminal_holdout.unknown_counterexamples", default=0))
    current_delivery = get(row, "delivery.current_head_validation_passed", "proof_basis.current_head_validation_passed", default=None)
    all_laws_covered = get(row, "proof_basis.all_laws_covered", default=None)

    if material and not c3_entered:
        out.append(violation("run", ident, "c3_required_without_c3_entry", "material run has no C3 entry evidence"))
    if material and not c3_closed:
        out.append(violation("run", ident, "c3_required_without_c3_closure", "material run has no C3 closure evidence"))
    elif c3_required and not c3_closed:
        out.append(violation("run", ident, "c3_required_without_c3_closure", "c3_required=true and c3_closed=false"))
    if c3_required and not c3_entered:
        out.append(violation("run", ident, "c3_required_without_c3_entry", "c3_required=true and c3_entered=false"))
    if material and compression_state in {"", "NONE", "NULL"}:
        out.append(violation("run", ident, "compression_state_none", "compression_state=NONE for material run"))
    if finding_bearing(row) and batches_total <= 0:
        out.append(violation("run", ident, "finding_workflow_without_batches", "batches_total=0 for finding-bearing workflow"))
    if open_batches > 0:
        out.append(violation("run", ident, "open_batches", "open review batches remain"))
    if material and not kernel_accepted:
        out.append(violation("run", ident, "kernel_not_accepted", "kernel.accepted=false for material run"))
    if material and not delivery_closed:
        out.append(violation("run", ident, "delivery_not_closed", "delivery_closed=false for material run"))
    if delivery_closed and not terminal_closed:
        out.append(violation("run", ident, "delivery_closed_without_terminal_closure", "delivery_closed=true while terminal_closed=false"))
    if material and closure_gate_status != "passed":
        out.append(violation("run", ident, "closure_gate_not_passed", "closure_gate.status is not passed for material run"))
    if material and strict_progress <= 0:
        out.append(violation("run", ident, "strict_progress_zero", "potential.strict_progress is false/zero for material campaign"))
    if orphan_code_constructs > 0:
        out.append(violation("run", ident, "orphan_code_constructs", f"orphan_code_constructs={orphan_code_constructs:g}"))
    if unmapped_proof_actions > 0:
        out.append(violation("run", ident, "unmapped_proof_actions", f"unmapped_proof_actions={unmapped_proof_actions:g}"))
    if wound_specific_tests > 0 and not wound_tests_mapped:
        out.append(violation("run", ident, "unmapped_wound_specific_tests", f"wound_specific_tests={wound_specific_tests:g} without class mapping"))
    if semantic_surface_delta > 0 and not (ac_rebased or truthy(get(row, "explicit_ac_rebase", default=False))):
        out.append(violation("run", ident, "semantic_surface_delta_without_ac_rebase", f"semantic_surface_delta=+{semantic_surface_delta:g} without AC rebase"))
    if num(get(row, "conformance.novel_in_horizon_counterexamples", default=0)) > 0:
        out.append(violation("run", ident, "unresolved_conformance_evidence", "conformance evidence remains unresolved"))
    if num(get(row, "terminal_holdout.unknown_counterexamples", default=0)) > 0:
        out.append(violation("run", ident, "unresolved_terminal_holdout_evidence", "terminal holdout evidence remains unresolved"))
    if current_delivery is not None and not truthy(current_delivery):
        out.append(violation("run", ident, "proof_or_delivery_not_current", "delivery proof is not current"))
    if all_laws_covered is not None and not truthy(all_laws_covered):
        out.append(violation("run", ident, "proof_or_delivery_not_current", "proof basis does not cover all laws"))
    return out


def evaluate_summary(summary: Any) -> List[Dict[str, str]]:
    if not isinstance(summary, dict):
        return []
    out: List[Dict[str, str]] = []
    ident = "summary"
    raw_delivery_mutations = num(get(summary, "raw_delivery_mutations_while_active", default=0))
    apply_violations = num(get(summary, "state_only_apply_violations", default=0))
    commit_violations = num(get(summary, "state_only_commit_violations", default=0))
    push_violations = num(get(summary, "state_only_push_violations", default=0))
    semantic_surface_delta = num(get(summary, "semantic_surface_delta", default=0))
    orphan_code_constructs = num(get(summary, "orphan_code_constructs", default=0))
    unmapped_proof_actions = num(get(summary, "unmapped_proof_actions", default=0))
    wound_specific_tests = num(get(summary, "wound_specific_tests", default=0))

    if raw_delivery_mutations > 0:
        out.append(violation("summary", ident, "raw_delivery_mutations_while_active", f"raw_delivery_mutations_while_active={raw_delivery_mutations:g}"))
    if apply_violations > 0:
        out.append(violation("summary", ident, "state_only_apply_violations", f"state_only_apply_violations={apply_violations:g}"))
    if commit_violations > 0:
        out.append(violation("summary", ident, "state_only_commit_violations", f"state_only_commit_violations={commit_violations:g}"))
    if push_violations > 0:
        out.append(violation("summary", ident, "state_only_push_violations", f"state_only_push_violations={push_violations:g}"))
    if semantic_surface_delta > 0 and not truthy(get(summary, "ac_rebased", default=False)):
        out.append(violation("summary", ident, "semantic_surface_growth", f"semantic_surface_delta=+{semantic_surface_delta:g}"))
    if orphan_code_constructs > 0:
        out.append(violation("summary", ident, "orphan_code_constructs", f"orphan_code_constructs={orphan_code_constructs:g}"))
    if unmapped_proof_actions > 0:
        out.append(violation("summary", ident, "unmapped_proof_actions", f"unmapped_proof_actions={unmapped_proof_actions:g}"))
    if wound_specific_tests > 0 and not truthy(get(summary, "wound_specific_tests_class_mapped", default=False)):
        out.append(violation("summary", ident, "wound_specific_tests_unmapped", f"wound_specific_tests={wound_specific_tests:g}"))
    return out


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Gate `$resolve` closure on material authority evidence")
    parser.add_argument("--campaign", help="campaign id; inferred only when exactly one non-empty id is present", default=None)
    parser.add_argument("--summary", help="summary JSON/YAML projection", default=None)
    parser.add_argument("--runs", help="runs JSONL projection", default=None)
    parser.add_argument("--format", choices=["text", "json"], default="json")
    args = parser.parse_args(argv)

    try:
        summary = load_doc(args.summary)
        rows = load_jsonl(args.runs)
        campaign = resolve_campaign(args.campaign, summary, rows)
        scoped_summary = summary_for_campaign(summary, campaign)
        scoped_rows = rows_for_campaign(rows, campaign)
        violations = evaluate_summary(scoped_summary)
        if summary_requires_material_runs(scoped_summary) and not scoped_rows:
            violations.append(violation("campaign", campaign, "material_campaign_without_runs", "campaign summary requires material run evidence but no scoped run rows matched"))
        for idx, row in enumerate(scoped_rows, 1):
            violations.extend(evaluate_run(row, idx))
    except Exception as exc:
        out = {"closure_allowed": False, "status": "error", "violations": [{"scope": "gate", "id": "input", "code": "gate_unavailable", "detail": str(exc)}]}
        rendered = json.dumps(out, indent=2, sort_keys=True) if args.format == "json" else text(out)
        print(rendered, file=sys.stderr if args.format == "text" else sys.stdout)
        return 3

    allowed = not violations
    out = {
        "closure_allowed": allowed,
        "status": "passed" if allowed else "blocked",
        "violations": violations,
        "legal_next_actions": [] if allowed else [
            "enter_or_repair_c3",
            "seal_batches",
            "compile_compression",
            "accept_kernel",
            "map_or_delete_orphans",
            "map_proof_actions",
            "reduce_semantic_surface_or_rebase_ac",
            "rerun_terminal_holdout",
        ],
    }
    print(json.dumps(out, indent=2, sort_keys=True) if args.format == "json" else text(out))
    return 0 if allowed else 2


def text(out: Dict[str, Any]) -> str:
    lines = []
    if not out["closure_allowed"]:
        lines.append("closure gate failed")
    lines.extend([
        f"status: {out['status']}",
        f"closure_allowed: {str(out['closure_allowed']).lower()}",
    ])
    if out.get("violations"):
        lines.append("violations:")
        for item in out["violations"]:
            lines.append(f"  - {item['scope']}:{item['id']}: evidence blocked")
    if out.get("legal_next_actions"):
        lines.append("legal_next_actions:")
        lines.extend(f"  - {item}" for item in out["legal_next_actions"])
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
