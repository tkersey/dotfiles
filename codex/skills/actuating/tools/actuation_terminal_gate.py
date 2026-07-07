#!/usr/bin/env -S uv run python
"""Actuating terminal closure gate.

ATCG-v1 is a pure reducer.  It does not run review, edit files, create proof,
or publish anything.  It answers one question: may this actuation run be marked
complete on the current artifact?
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
from pathlib import Path
import sys
from typing import Any

YES = {"yes", "true", "1", True}
NO = {"no", "false", "0", False}
SOURCES = {"accepted_spec", "direct_goal", "review"}
CLOSURE_CANDIDATES = {"proof-patch", "ship-handoff", "ship-complete", "blocked"}
LOCAL_VERDICTS = {"done", "continue", "regress", "blocked", "invalid-proof", "ask-human", "refactor-kernel"}
ADD_VERDICTS = {"handoff_to_ship", "shipping_not_requested", "blocked", "missing"}
TERMINAL_VERDICTS = {"complete", "continue", "blocked"}
NEXT_OWNERS = {"none", "$cas", "$proof-patch", "$ship", "$goal-grind", "$goal-actuating", "human"}
AUXILIARY_CAS_LANES = {"footgun-finder", "invariant-ace", "complexity-mitigator"}
AUXILIARY_LENS_CONTRACTS = {
    "footgun-finder": "footgun-lens-v1",
    "invariant-ace": "invariant-gate-v1",
    "complexity-mitigator": "complexity-preflight-v1",
}
OBLIGATION_TRIGGER_LANES = {
    "misuse-hazard": "footgun-finder",
    "invariant-gap": "invariant-ace",
    "complexity-pressure": "complexity-mitigator",
    "complexity-stall": "complexity-mitigator",
    "repeated-owner-boundary": "complexity-mitigator",
}
VALID_LENS_EVIDENCE_STATES = {"valid", "missing", "invalid", "stale", "blocked", "rerun-required", "not-required"}
HARD_REASON_ORDER = [
    "blocked-loop-contract-missing",
    "blocked-loop-contract-stale",
    "blocked-hylo-frontier-missing",
    "blocked-hylo-fold-missing",
    "blocked-hylo-terminal-missing",
    "cas-review-blocked",
    "proof-stale",
    "side-effect-boundary-violated",
]


class TerminalGateError(ValueError):
    pass


def load_json(path: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    value = json.loads(text)
    if not isinstance(value, dict):
        raise TerminalGateError("input: expected JSON object")
    return value


def unwrap(value: dict[str, Any], key: str) -> dict[str, Any]:
    body = value.get(key, value)
    if not isinstance(body, dict):
        raise TerminalGateError(f"{key}: expected object")
    return body


def context_from(value: dict[str, Any]) -> dict[str, Any]:
    return unwrap(value, "actuation_terminal_context")


def now_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def as_yes(value: Any) -> bool:
    return value in YES or (isinstance(value, str) and value.lower() in YES)


def explicit_no(value: Any) -> bool:
    return value in NO or (isinstance(value, str) and value.lower() in NO)


def yes_no_string(value: Any, *, default: str = "no") -> str:
    if as_yes(value):
        return "yes"
    if explicit_no(value):
        return "no"
    return default


def is_plain_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def count_from(value: Any) -> int | None:
    if is_plain_int(value):
        return value
    if isinstance(value, str) and value.isdecimal():
        return int(value)
    return None


def require_str(obj: dict[str, Any], key: str, errors: list[str]) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value:
        errors.append(f"{key}:missing")
        return ""
    return value


def optional_object(obj: dict[str, Any], key: str, errors: list[str]) -> dict[str, Any]:
    value = obj.get(key)
    if value is None:
        return {}
    if not isinstance(value, dict):
        errors.append(f"{key}:must-be-object")
        return {}
    return value


def object_from(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_from(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def first_present(obj: dict[str, Any], keys: tuple[str, ...], default: Any = None) -> Any:
    for key in keys:
        if key in obj:
            return obj[key]
    return default


def append_reason(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)


def sort_hard_reasons(reasons: list[str]) -> list[str]:
    order = {reason: index for index, reason in enumerate(HARD_REASON_ORDER)}
    return sorted(reasons, key=lambda reason: order.get(reason, len(order)))


def standard_clean_runs_required_for(obj: dict[str, Any]) -> Any:
    return first_present(obj, ("standard_clean_runs_required", "clean_runs_required"), 3)


def standard_clean_runs_count_for(obj: dict[str, Any]) -> Any:
    return first_present(obj, ("standard_clean_runs_count", "clean_runs_count"), 0)


def loop_standard_clean_runs_required_for(obj: dict[str, Any]) -> Any:
    return first_present(obj, ("standard_clean_runs_required", "required_count", "clean_runs_required"), 3)


def loop_standard_clean_runs_count_for(obj: dict[str, Any]) -> Any:
    return first_present(obj, ("standard_clean_runs_count", "standard_count", "count", "clean_runs_count"), 0)


# ---------------------------------------------------------------------------
# Advisory and hard terminal blockers
# ---------------------------------------------------------------------------

def make_advisory(context: dict[str, Any]) -> dict[str, Any]:
    reasons = hard_completion_reasons_for(context)
    would_block = bool(reasons)
    return {
        "verdict": "advisory",
        "would_block": would_block,
        "would_block_reasons": reasons,
        "can_mark_goal_complete": not would_block,
        "next_owner": advisory_next_owner_for(reasons),
    }


def hard_completion_reasons_for(context: dict[str, Any]) -> list[str]:
    loop = object_from(context.get("loop_governance"))
    artifact = object_from(context.get("artifact_scope"))
    hsr = object_from(loop.get("hsr"))
    reasons: list[str] = []

    fused_requested = direct_action_fused_requested(loop)
    fusion_reasons = fusion_receipt_reasons_for(context, loop) if fused_requested else []
    loop_receipts_exempt = fused_requested and not fusion_reasons
    if fusion_reasons:
        append_reason(reasons, "blocked-loop-contract-missing")
        reasons.extend(fusion_reasons)

    loop_required = loop_receipts_required(loop, hsr)

    alsr = object_from(loop.get("alsr"))
    alsr_required = (
        not loop_receipts_exempt
        and (as_yes(loop.get("alsr_required")) or as_yes(alsr.get("required")) or loop_required)
    )
    if alsr_required:
        reasons.extend(alsr_reasons_for(alsr, artifact))

    hyl = object_from(loop.get("hyl"))
    hyl_required = not loop_receipts_exempt and (
        as_yes(loop.get("hyl_required"))
        or as_yes(loop.get("recursive"))
        or as_yes(loop.get("material"))
        or as_yes(hyl.get("required"))
        or loop_required
    )
    if hyl_required:
        reasons.extend(hyl_reasons_for(hyl, artifact, alsr))

    if loop_required and not loop_receipts_exempt:
        reasons.extend(hsr_reasons_for(loop, hsr, artifact))

    selected_loop = object_from(loop.get("selected_loop"))
    if selected_loop and not as_yes(selected_loop.get("matches_task_shape")):
        append_reason(reasons, "blocked-hylo-frontier-missing")
        append_reason(reasons, "selected_loop.matches_task_shape:not-yes")

    reasons.extend(goal_focus_reasons_for(loop))

    review_closeout = review_closeout_governance_for(loop)
    if as_yes(review_closeout.get("required")) and not review_closeout_obeyed(review_closeout):
        append_reason(reasons, "cas-review-blocked")

    if cas_advisory_blocked(context, loop):
        append_reason(reasons, "cas-review-blocked")

    if side_effect_boundary_violated(context, loop):
        append_reason(reasons, "side-effect-boundary-violated")

    if proof_verifier_mismatch(context, loop):
        append_reason(reasons, "proof-stale")

    return sort_hard_reasons(reasons)


def direct_action_fused_requested(loop: dict[str, Any]) -> bool:
    return as_yes(loop.get("direct_action_fused")) or loop.get("mode") in {
        "direct_action_fused",
        "direct-action-fused",
        "fused",
    }


def fusion_receipt_reasons_for(context: dict[str, Any], loop: dict[str, Any]) -> list[str]:
    receipt = object_from(loop.get("fusion_receipt")) or object_from(context.get("fusion_receipt"))
    if not receipt:
        return ["fusion_receipt:missing"]
    reasons: list[str] = []
    if receipt.get("version") != "FUSION-v1":
        reasons.append("fusion_receipt.version:invalid")
    yes_fields = [
        "one_legal_work_item",
        "verifier_known",
        "objective_bound",
        "artifact_scope_bound",
        "stop_condition_bound",
    ]
    for key in yes_fields:
        if not as_yes(receipt.get(key)):
            reasons.append(f"fusion_receipt.{key}:not-yes")
    no_fields = ["review_required", "public_side_effect", "repeated_class_or_branch_choice"]
    for key in no_fields:
        if not explicit_no(receipt.get(key)):
            reasons.append(f"fusion_receipt.{key}:not-no")
    if receipt.get("parallelism") != "none":
        reasons.append("fusion_receipt.parallelism:not-none")
    if not isinstance(receipt.get("proof_ref"), str) or not receipt.get("proof_ref"):
        reasons.append("fusion_receipt.proof_ref:missing")
    return reasons


def loop_receipts_required(loop: dict[str, Any], hsr: dict[str, Any]) -> bool:
    return any(
        as_yes(value)
        for value in (
            loop.get("loop_contract_required"),
            loop.get("material"),
            loop.get("recursive"),
            object_from(loop.get("alsr")).get("required"),
            object_from(loop.get("hyl")).get("required"),
            object_from(loop.get("goal_focus")).get("required"),
            hsr.get("required"),
            hsr.get("terminal_required"),
        )
    )


def receipt_object(wrapper: dict[str, Any], version_key: str, version_value: str) -> dict[str, Any]:
    candidate = object_from(wrapper.get("receipt"))
    if candidate:
        return candidate
    if wrapper.get(version_key) == version_value:
        return wrapper
    return {}


def alsr_reasons_for(alsr: dict[str, Any], artifact: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    receipt = receipt_object(alsr, "receipt_version", "ALSR-v1")
    present = as_yes(alsr.get("present")) or bool(receipt) or isinstance(alsr.get("receipt_ref"), str)
    current = as_yes(alsr.get("current"))
    if not present:
        return ["blocked-loop-contract-missing", "alsr:missing"]
    if not current:
        reasons.append("blocked-loop-contract-stale")
        reasons.append("alsr:not-current")
    if receipt:
        if receipt.get("receipt_version") != "ALSR-v1":
            reasons.append("alsr.receipt_version:invalid")
        for key in ("alsr_id", "objective"):
            if not isinstance(receipt.get(key), str) or not receipt.get(key):
                reasons.append(f"alsr.{key}:missing")
        scope = object_from(receipt.get("artifact_scope"))
        for key in ("repo", "branch", "head", "diff_digest"):
            if not isinstance(scope.get(key), str) or not scope.get(key):
                reasons.append(f"alsr.artifact_scope.{key}:missing")
        if scope.get("branch") and artifact.get("branch") and scope.get("branch") != artifact.get("branch"):
            append_reason(reasons, "blocked-loop-contract-stale")
            reasons.append("alsr.artifact_scope.branch:artifact-mismatch")
        if scope.get("head") and artifact.get("head_sha") and scope.get("head") != artifact.get("head_sha"):
            append_reason(reasons, "blocked-loop-contract-stale")
            reasons.append("alsr.artifact_scope.head:artifact-mismatch")
        if scope.get("diff_digest") and artifact.get("diff_fingerprint") and scope.get("diff_digest") != artifact.get("diff_fingerprint"):
            append_reason(reasons, "blocked-loop-contract-stale")
            reasons.append("alsr.artifact_scope.diff_digest:artifact-mismatch")
        terminal = object_from(receipt.get("terminal_gate"))
        if terminal.get("owner") != "ATCG-v1" or not as_yes(terminal.get("completion_requires_can_mark_goal_complete")):
            reasons.append("alsr.terminal_gate:invalid")
    return reasons


def hyl_reasons_for(hyl: dict[str, Any], artifact: dict[str, Any], alsr: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    receipt = receipt_object(hyl, "machine_version", "HYL-v1")
    present = as_yes(hyl.get("present")) or bool(receipt) or isinstance(hyl.get("receipt_ref"), str)
    current = as_yes(hyl.get("current"))
    if not present:
        return ["blocked-loop-contract-missing", "hyl:missing"]
    if not current:
        reasons.append("blocked-loop-contract-stale")
        reasons.append("hyl:not-current")
    if receipt:
        if receipt.get("machine_version") != "HYL-v1":
            reasons.append("hyl.machine_version:invalid")
        for key in ("hyl_id", "alsr_id"):
            if not isinstance(receipt.get(key), str) or not receipt.get(key):
                reasons.append(f"hyl.{key}:missing")
        alsr_id = first_present(alsr, ("alsr_id",), object_from(alsr.get("receipt")).get("alsr_id"))
        if alsr_id and receipt.get("alsr_id") and receipt.get("alsr_id") != alsr_id:
            append_reason(reasons, "blocked-loop-contract-stale")
            reasons.append("hyl.alsr_id:alsr-mismatch")
        seed_artifact = object_from(object_from(receipt.get("seed_state")).get("artifact_scope"))
        if seed_artifact:
            if seed_artifact.get("branch") and artifact.get("branch") and seed_artifact.get("branch") != artifact.get("branch"):
                append_reason(reasons, "blocked-loop-contract-stale")
                reasons.append("hyl.seed_state.artifact_scope.branch:artifact-mismatch")
            if seed_artifact.get("head_sha") and artifact.get("head_sha") and seed_artifact.get("head_sha") != artifact.get("head_sha"):
                append_reason(reasons, "blocked-loop-contract-stale")
                reasons.append("hyl.seed_state.artifact_scope.head_sha:artifact-mismatch")
        coalgebra = object_from(receipt.get("coalgebra"))
        if coalgebra.get("emits") not in {"terminal", "blocked", "work_node", "parallel_frontier"}:
            reasons.append("hyl.coalgebra.emits:invalid")
        boundary = object_from(receipt.get("action_boundary"))
        for key in ("mutation_requires_unfolded_node", "continuation_requires_fold_verdict", "review_mutation_requires_review_fold", "public_side_effects_require_ship"):
            if not as_yes(boundary.get(key)):
                reasons.append(f"hyl.action_boundary.{key}:not-yes")
        terminal = object_from(receipt.get("terminal"))
        if terminal.get("completion_requires") != "ATCG-v1" or not as_yes(terminal.get("proof_must_bind_current_artifact")):
            reasons.append("hyl.terminal:invalid")
    return reasons


def hsr_chain_for(loop: dict[str, Any], hsr: dict[str, Any]) -> list[dict[str, Any]]:
    raw = list_from(loop.get("hsr_chain")) or list_from(hsr.get("chain"))
    latest = object_from(hsr.get("latest")) or object_from(loop.get("latest_hsr"))
    if latest:
        raw = raw + [latest]
    return [item for item in raw if isinstance(item, dict)]


def hsr_reasons_for(loop: dict[str, Any], hsr: dict[str, Any], artifact: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    chain = hsr_chain_for(loop, hsr)
    material_mutations = list_from(loop.get("material_mutations")) or list_from(hsr.get("material_mutations"))

    terminal_found = bool(chain and any(hsr_is_terminal(item) for item in chain)) or as_yes(hsr.get("terminal_present"))
    if not terminal_found:
        append_reason(reasons, "blocked-hylo-terminal-missing")

    if chain:
        for index, receipt in enumerate(chain):
            reasons.extend(single_hsr_reasons_for(receipt, artifact, index))
    elif not material_mutations:
        if as_yes(loop.get("material")):
            append_reason(reasons, "blocked-hylo-frontier-missing")
            append_reason(reasons, "hsr_chain:missing")

    reasons.extend(material_mutation_reasons_for(material_mutations))

    if explicit_no(hsr.get("latest_fold_present")):
        append_reason(reasons, "blocked-hylo-fold-missing")
    if not chain and not as_yes(hsr.get("latest_fold_current_artifact_bound")):
        append_reason(reasons, "proof-stale")
    if chain and any(not as_yes(object_from(item.get("fold")).get("current_artifact_bound")) for item in chain):
        append_reason(reasons, "proof-stale")
    return reasons


def hsr_is_terminal(receipt: dict[str, Any]) -> bool:
    unfold = object_from(receipt.get("unfold"))
    continuation = object_from(receipt.get("continuation"))
    return unfold.get("produced") == "terminal" or (
        as_yes(continuation.get("stop_rule_fired")) and as_yes(continuation.get("atcg_required"))
    )


def single_hsr_reasons_for(receipt: dict[str, Any], artifact: dict[str, Any], index: int) -> list[str]:
    prefix = f"hsr_chain[{index}]"
    reasons: list[str] = []
    if receipt.get("receipt_version") != "HSR-v1":
        reasons.append(f"{prefix}.receipt_version:invalid")
    for key in ("hsr_id", "alsr_id", "hyl_id", "step_id"):
        if not isinstance(receipt.get(key), str) or not receipt.get(key):
            reasons.append(f"{prefix}.{key}:missing")
    state = object_from(receipt.get("state_before"))
    for key in ("branch", "head", "diff_digest"):
        if not isinstance(state.get(key), str) or not state.get(key):
            reasons.append(f"{prefix}.state_before.{key}:missing")
    if state.get("branch") and artifact.get("branch") and state.get("branch") != artifact.get("branch"):
        append_reason(reasons, "blocked-loop-contract-stale")
        reasons.append(f"{prefix}.state_before.branch:artifact-mismatch")
    if state.get("head") and artifact.get("head_sha") and state.get("head") != artifact.get("head_sha"):
        append_reason(reasons, "blocked-loop-contract-stale")
        reasons.append(f"{prefix}.state_before.head:artifact-mismatch")
    if state.get("diff_digest") and artifact.get("diff_fingerprint") and state.get("diff_digest") != artifact.get("diff_fingerprint"):
        append_reason(reasons, "blocked-loop-contract-stale")
        reasons.append(f"{prefix}.state_before.diff_digest:artifact-mismatch")

    unfold = object_from(receipt.get("unfold"))
    produced = unfold.get("produced")
    if produced not in {"work_node", "parallel_frontier", "terminal", "blocked"}:
        append_reason(reasons, "blocked-hylo-frontier-missing")
        reasons.append(f"{prefix}.unfold.produced:invalid")
    node_ids = list_from(unfold.get("node_ids"))
    if produced in {"work_node", "parallel_frontier"} and not node_ids:
        append_reason(reasons, "blocked-hylo-frontier-missing")
        reasons.append(f"{prefix}.unfold.node_ids:missing")

    action = object_from(receipt.get("action"))
    if action.get("owner") not in {"root", "subagent", "none"}:
        append_reason(reasons, "blocked-hylo-frontier-missing")
        reasons.append(f"{prefix}.action.owner:invalid")
    node_id = action.get("node_id")
    if produced == "work_node" and (not isinstance(node_id, str) or node_id not in node_ids):
        append_reason(reasons, "blocked-hylo-frontier-missing")
        reasons.append(f"{prefix}.action.node_id:not-unfolded")
    if action.get("side_effects") not in {"none", "blocked", "requested", "performed"}:
        reasons.append(f"{prefix}.action.side_effects:invalid")

    fold = object_from(receipt.get("fold"))
    if fold.get("verdict") not in LOCAL_VERDICTS | {"complete"}:
        append_reason(reasons, "blocked-hylo-fold-missing")
        reasons.append(f"{prefix}.fold.verdict:invalid")
    if not as_yes(fold.get("current_artifact_bound")):
        append_reason(reasons, "blocked-hylo-fold-missing")
        reasons.append(f"{prefix}.fold.current_artifact_bound:not-yes")

    continuation = object_from(receipt.get("continuation"))
    if not isinstance(continuation.get("next_owner"), str) or not continuation.get("next_owner"):
        reasons.append(f"{prefix}.continuation.next_owner:missing")
    if continuation.get("atcg_required") is not None and not (as_yes(continuation.get("atcg_required")) or explicit_no(continuation.get("atcg_required"))):
        reasons.append(f"{prefix}.continuation.atcg_required:invalid")
    return reasons


def material_mutation_reasons_for(mutations: list[Any]) -> list[str]:
    reasons: list[str] = []
    for index, mutation in enumerate(mutations):
        item = object_from(mutation)
        prefix = f"material_mutations[{index}]"
        if not as_yes(item.get("has_unfold")) or not as_yes(item.get("has_action")):
            append_reason(reasons, "blocked-hylo-frontier-missing")
            reasons.append(f"{prefix}:missing-unfold-or-action")
        if not as_yes(item.get("has_fold")):
            append_reason(reasons, "blocked-hylo-fold-missing")
            reasons.append(f"{prefix}:missing-fold")
        if not isinstance(item.get("receipt_ref"), str) or not item.get("receipt_ref"):
            append_reason(reasons, "blocked-hylo-frontier-missing")
            reasons.append(f"{prefix}.receipt_ref:missing")
    return reasons


def goal_focus_reasons_for(loop: dict[str, Any]) -> list[str]:
    focus = object_from(loop.get("goal_focus"))
    if not as_yes(focus.get("required")):
        return []
    reasons: list[str] = []
    if not as_yes(focus.get("parent_goal_stable")):
        append_reason(reasons, "blocked-hylo-frontier-missing")
        reasons.append("goal_focus.parent_goal_stable:not-yes")
    if not as_yes(focus.get("all_child_focus_frames_folded_or_blocked")):
        append_reason(reasons, "blocked-hylo-fold-missing")
        reasons.append("goal_focus.all_child_focus_frames_folded_or_blocked:not-yes")
    if not as_yes(focus.get("terminal_focus_matches_parent_stop_rule")):
        append_reason(reasons, "blocked-hylo-terminal-missing")
        reasons.append("goal_focus.terminal_focus_matches_parent_stop_rule:not-yes")
    if not explicit_no(focus.get("child_claimed_parent_completion")):
        append_reason(reasons, "blocked-hylo-terminal-missing")
        reasons.append("goal_focus.child_claimed_parent_completion:not-no")
    if not as_yes(focus.get("latest_focus_fold_parent_bound")):
        append_reason(reasons, "blocked-hylo-fold-missing")
        reasons.append("goal_focus.latest_focus_fold_parent_bound:not-yes")
    return reasons


# ---------------------------------------------------------------------------
# Review and CAS checks
# ---------------------------------------------------------------------------

def review_closeout_governance_for(loop: dict[str, Any]) -> dict[str, Any]:
    review_closeout = object_from(loop.get("review_closeout"))
    if review_closeout:
        return review_closeout
    resolve = object_from(loop.get("resolve"))
    if resolve:
        return resolve
    return object_from(loop.get("review_fix"))


def any_yes(obj: dict[str, Any], *keys: str) -> bool:
    return any(as_yes(obj.get(key)) for key in keys)


def review_closeout_obeyed(review_closeout: dict[str, Any]) -> bool:
    return (
        any_yes(review_closeout, "cas_reviewed", "cas_obeyed", "cas_satisfied")
        and any_yes(review_closeout, "review_folded", "review_fold_obeyed", "review_fold_satisfied")
        and any_yes(
            review_closeout,
            "review_closeout_passed",
            "review_closeout_obeyed",
            "resolution_folded",
            "resolve_passed",
            "resolve_obeyed",
            "resolved",
        )
    )


def auxiliary_lane_records_for(cas: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lanes = cas.get("auxiliary_lanes", cas.get("auxiliary_review_lanes", []))
    records: dict[str, dict[str, Any]] = {}
    if isinstance(lanes, dict):
        for lane, value in lanes.items():
            if lane not in AUXILIARY_CAS_LANES:
                continue
            record = dict(value) if isinstance(value, dict) else {"status": value}
            record.setdefault("lane", lane)
            records[lane] = record
        return records
    if isinstance(lanes, list):
        for value in lanes:
            if isinstance(value, str):
                lane = value
                record = {"lane": lane, "required": "yes"}
            else:
                record = object_from(value)
                lane = record.get("lane")
            if lane in AUXILIARY_CAS_LANES:
                records[lane] = record
    return records


def required_auxiliary_lanes_for(cas: dict[str, Any], records: dict[str, dict[str, Any]]) -> set[str]:
    required: set[str] = set()
    for key in ("required_auxiliary_lanes", "required_auxiliary_review_lanes", "review_lanes"):
        for lane in list_from(cas.get(key)):
            if lane in AUXILIARY_CAS_LANES:
                required.add(lane)
    for lane, record in records.items():
        state = str(record.get("status", record.get("state", ""))).lower()
        if state == "not-required":
            continue
        if as_yes(record.get("required")) or as_yes(record.get("selected")):
            required.add(lane)
    return required


def review_profile_for(context: dict[str, Any]) -> dict[str, Any]:
    profile = object_from(context.get("review_profile"))
    if profile:
        return profile
    return object_from(object_from(context.get("loop_governance")).get("review_profile"))


def review_profile_lane_records_for(profile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lanes = profile.get("auxiliary_review_lanes", profile.get("auxiliary_lanes", []))
    records: dict[str, dict[str, Any]] = {}
    if isinstance(lanes, dict):
        for lane, value in lanes.items():
            if lane not in AUXILIARY_CAS_LANES:
                continue
            record = dict(value) if isinstance(value, dict) else {"state": value}
            record.setdefault("lane", lane)
            records[lane] = record
        return records
    if isinstance(lanes, list):
        for value in lanes:
            record = {"lane": value, "state": "clean"} if isinstance(value, str) else object_from(value)
            lane = record.get("lane")
            if lane in AUXILIARY_CAS_LANES:
                records[lane] = record
    return records


def review_obligation_records_for(profile: dict[str, Any]) -> list[dict[str, Any]]:
    router = object_from(profile.get("obligation_router"))
    obligations = router.get("obligations")
    if not isinstance(obligations, list):
        return []
    return [item for item in obligations if isinstance(item, dict)]


def review_obligation_required_lanes_for(profile: dict[str, Any]) -> set[str]:
    required: set[str] = set()
    for record in review_obligation_records_for(profile):
        lane = record.get("owner_lens")
        if lane not in AUXILIARY_CAS_LANES:
            continue
        state = str(record.get("state", record.get("status", ""))).lower()
        if state != "not-required":
            required.add(lane)
    return required


def review_profile_selects_auxiliary_lane(profile: dict[str, Any]) -> bool:
    if review_obligation_required_lanes_for(profile):
        return True
    for record in review_profile_lane_records_for(profile).values():
        state = str(record.get("state", record.get("status", ""))).lower()
        if state and state != "not-required":
            return True
        if as_yes(record.get("selected")) or as_yes(record.get("required")):
            return True
    return False


def standard_cas_required_for(cas: dict[str, Any], profile: dict[str, Any] | None = None) -> bool:
    records = auxiliary_lane_records_for(cas)
    workflow_profile = profile or {}
    return (
        as_yes(cas.get("required"))
        or bool(required_auxiliary_lanes_for(cas, records))
        or str(workflow_profile.get("standard", "")).lower() == "required"
        or review_profile_selects_auxiliary_lane(workflow_profile)
    )


def lane_binding_value(record: dict[str, Any], key: str) -> Any:
    tuple_value = object_from(record.get("tuple"))
    return first_present(record, (key,), tuple_value.get(key))


def lens_evidence_ref_for(record: dict[str, Any]) -> Any:
    return first_present(record, ("lens_evidence_ref", "evidence_ref", "verdict_ref", "review_fold_ref", "receipt_ref"))


def lens_contract_reasons_for(record: dict[str, Any], lane: str, prefix: str) -> list[str]:
    reasons: list[str] = []
    expected = AUXILIARY_LENS_CONTRACTS[lane]
    contract = record.get("lens_contract")
    if not isinstance(contract, str) or not contract:
        reasons.append(f"{prefix}.lens_contract:missing")
    elif contract != expected:
        reasons.append(f"{prefix}.lens_contract:invalid")

    state = str(record.get("lens_evidence_state", "")).lower()
    if not state:
        reasons.append(f"{prefix}.lens_evidence_state:missing")
    elif state not in VALID_LENS_EVIDENCE_STATES:
        reasons.append(f"{prefix}.lens_evidence_state:invalid")
    elif state != "valid":
        reasons.append(f"{prefix}.lens_evidence_state:{state}")

    evidence_ref = lens_evidence_ref_for(record)
    if not isinstance(evidence_ref, str) or not evidence_ref:
        reasons.append(f"{prefix}.lens_evidence_ref:missing")
    return reasons


def complexity_pressure_requires_lens(profile: dict[str, Any]) -> bool:
    pressure = profile.get("complexity_pressure")
    if pressure is None or pressure == "":
        return False
    if isinstance(pressure, dict):
        if any(explicit_no(pressure.get(key)) for key in ("required", "applies", "present")):
            return False
        return any(
            as_yes(pressure.get(key))
            for key in ("required", "present", "review_churn", "one_patch_per_comment_pressure", "comprehension_blocked", "mixed_responsibilities", "boolean_soup")
        ) or str(pressure.get("level", "")).lower() in {"medium", "high", "required"}
    return as_yes(pressure) or str(pressure).lower() in {"present", "required", "medium", "high"}


def review_obligation_router_reasons_for(profile: dict[str, Any], artifact: dict[str, Any], lane_records: dict[str, dict[str, Any]]) -> list[str]:
    router = object_from(profile.get("obligation_router"))
    if not router:
        return []
    reasons: list[str] = []
    if router.get("version") != "ROR-v1":
        reasons.append("review_profile.obligation_router.version:invalid")
    obligations = router.get("obligations")
    if not isinstance(obligations, list):
        reasons.append("review_profile.obligation_router.obligations:must-be-list")
        return reasons
    for index, value in enumerate(obligations):
        prefix = f"review_profile.obligation_router.obligations[{index}]"
        if not isinstance(value, dict):
            reasons.append(f"{prefix}:must-be-object")
            continue
        obligation_id = value.get("id")
        if not isinstance(obligation_id, str) or not obligation_id:
            reasons.append(f"{prefix}.id:missing")
        trigger = value.get("trigger")
        if not isinstance(trigger, str) or not trigger:
            reasons.append(f"{prefix}.trigger:missing")
        expected_lane = OBLIGATION_TRIGGER_LANES.get(trigger)
        lane = value.get("owner_lens")
        if lane not in AUXILIARY_CAS_LANES:
            reasons.append(f"{prefix}.owner_lens:invalid")
            lane = ""
        elif expected_lane and lane != expected_lane:
            reasons.append(f"{prefix}.owner_lens:trigger-mismatch")
        source_ref = object_from(value.get("source_ref"))
        if not source_ref:
            reasons.append(f"{prefix}.source_ref:missing")
        else:
            for key, artifact_key in (("head_sha", "head_sha"), ("target_fingerprint", "diff_fingerprint")):
                source_value = source_ref.get(key)
                if source_value is not None and not isinstance(source_value, str):
                    reasons.append(f"{prefix}.source_ref.{key}:must-be-string")
                elif isinstance(source_value, str) and source_value and source_value != artifact.get(artifact_key):
                    reasons.append(f"{prefix}.source_ref.{key}:artifact-mismatch")
        state = str(value.get("state", value.get("status", ""))).lower()
        if not state:
            reasons.append(f"{prefix}.state:missing")
            continue
        if state not in {"not-required", "clean", "findings-folded", "blocked", "rerun-required"}:
            reasons.append(f"{prefix}.state:invalid")
            continue
        if state == "not-required":
            reason = first_present(value, ("not_required_reason", "reason"))
            if not isinstance(reason, str) or not reason.strip():
                reasons.append(f"{prefix}.not_required_reason:missing")
            continue
        if state in {"blocked", "rerun-required"}:
            reasons.append(f"{prefix}:{state}")
            continue
        evidence_ref = lens_evidence_ref_for(value)
        if not isinstance(evidence_ref, str) or not evidence_ref:
            reasons.append(f"{prefix}.evidence_ref:missing")
        if lane:
            lane_record = lane_records.get(lane)
            lane_state = str(object_from(lane_record).get("state", object_from(lane_record).get("status", ""))).lower()
            if not lane_record or lane_state == "not-required":
                reasons.append(f"review_profile.auxiliary_review_lanes.{lane}:obligation-router-required")
    return reasons


def auxiliary_lane_reasons_for(cas: dict[str, Any], artifact: dict[str, Any]) -> list[str]:
    records = auxiliary_lane_records_for(cas)
    required = required_auxiliary_lanes_for(cas, records)
    reasons: list[str] = []
    for lane in sorted(required):
        record = records.get(lane)
        if not record:
            reasons.append(f"cas.auxiliary_lanes.{lane}:missing")
            continue
        state = str(record.get("status", record.get("state", ""))).lower()
        folded = as_yes(record.get("folded")) or state in {"clean", "findings-folded"}
        if state == "missing":
            reasons.append(f"cas.auxiliary_lanes.{lane}:missing")
        if not folded:
            reasons.append(f"cas.auxiliary_lanes.{lane}:not-folded")
        if as_yes(record.get("unresolved_blockers")) or state == "blocked":
            reasons.append(f"cas.auxiliary_lanes.{lane}:blocked")
        if as_yes(record.get("rerun_required")) or state == "rerun-required":
            reasons.append(f"cas.auxiliary_lanes.{lane}:rerun-required")
        if folded and state not in {"blocked", "rerun-required"}:
            reasons.extend(lens_contract_reasons_for(record, lane, f"cas.auxiliary_lanes.{lane}"))
        head_sha = lane_binding_value(record, "head_sha")
        if not isinstance(head_sha, str) or not head_sha:
            reasons.append(f"cas.auxiliary_lanes.{lane}.head_sha:missing")
        elif head_sha != artifact.get("head_sha"):
            reasons.append(f"cas.auxiliary_lanes.{lane}.head_sha:artifact-mismatch")
        target_fingerprint = lane_binding_value(record, "target_fingerprint")
        if not isinstance(target_fingerprint, str) or not target_fingerprint:
            reasons.append(f"cas.auxiliary_lanes.{lane}.target_fingerprint:missing")
        elif target_fingerprint != artifact.get("diff_fingerprint"):
            reasons.append(f"cas.auxiliary_lanes.{lane}.target_fingerprint:artifact-mismatch")
    return reasons


def review_profile_reasons_for(profile: dict[str, Any], artifact: dict[str, Any], standard_required: bool) -> list[str]:
    if not standard_required and not profile:
        return []
    reasons: list[str] = []
    if standard_required and not profile:
        return ["review_profile:missing"]

    standard_state = str(profile.get("standard", "")).lower()
    if standard_required and standard_state != "required":
        reasons.append("review_profile.standard:missing-required")

    records = review_profile_lane_records_for(profile)
    router_required_lanes = review_obligation_required_lanes_for(profile)
    for lane in sorted(AUXILIARY_CAS_LANES):
        record = records.get(lane)
        prefix = f"review_profile.auxiliary_review_lanes.{lane}"
        if not record:
            reasons.append(f"{prefix}:missing")
            continue
        state = str(record.get("state", record.get("status", ""))).lower()
        if not state:
            reasons.append(f"{prefix}.state:missing")
            continue
        if state not in {"not-required", "clean", "findings-folded", "blocked", "rerun-required"}:
            reasons.append(f"{prefix}.state:invalid")
            continue
        if state == "not-required":
            reason = record.get("reason")
            if not isinstance(reason, str) or not reason.strip():
                reasons.append(f"{prefix}.reason:missing")
            if lane in router_required_lanes:
                reasons.append(f"{prefix}:obligation-router-required")
            if lane == "complexity-mitigator" and complexity_pressure_requires_lens(profile):
                reasons.append(f"{prefix}:complexity-pressure-required")
            continue
        if state in {"blocked", "rerun-required"}:
            reasons.append(f"{prefix}:{state}")
            continue
        reasons.extend(lens_contract_reasons_for(record, lane, prefix))
        head_sha = lane_binding_value(record, "head_sha")
        if not isinstance(head_sha, str) or not head_sha:
            reasons.append(f"{prefix}.head_sha:missing")
        elif head_sha != artifact.get("head_sha"):
            reasons.append(f"{prefix}.head_sha:artifact-mismatch")
        target_fingerprint = lane_binding_value(record, "target_fingerprint")
        if not isinstance(target_fingerprint, str) or not target_fingerprint:
            reasons.append(f"{prefix}.target_fingerprint:missing")
        elif target_fingerprint != artifact.get("diff_fingerprint"):
            reasons.append(f"{prefix}.target_fingerprint:artifact-mismatch")
    reasons.extend(review_obligation_router_reasons_for(profile, artifact, records))
    return reasons


def cas_advisory_blocked(context: dict[str, Any], loop: dict[str, Any]) -> bool:
    cas = object_from(context.get("cas_review"))
    profile = review_profile_for(context)
    artifact = object_from(context.get("artifact_scope"))
    final_report = object_from(context.get("final_report_fields"))
    if cas_reasons_for(cas, profile, artifact) or final_report_reasons_for(
        final_report, cas, profile, object_from(context.get("proof_patch")), object_from(context.get("delivery"))
    ):
        return True

    clean_runs = object_from(loop.get("cas_clean_runs"))
    if not as_yes(clean_runs.get("required")):
        return False
    required = loop_standard_clean_runs_required_for(clean_runs)
    count = loop_standard_clean_runs_count_for(clean_runs)
    return not (
        is_plain_int(required)
        and required > 0
        and is_plain_int(count)
        and count >= required
        and as_yes(clean_runs.get("independent_fresh_runs"))
        and as_yes(clean_runs.get("tuple_bound"))
    )


def side_effect_boundary_violated(context: dict[str, Any], loop: dict[str, Any]) -> bool:
    side = object_from(loop.get("side_effect_boundary")) or object_from(context.get("side_effect_boundary"))
    if not side:
        return False
    if explicit_no(side.get("respected")):
        return True
    performed = side.get("public_side_effects") == "performed" or as_yes(side.get("performed"))
    allowed = as_yes(side.get("public_side_effects_allowed")) or as_yes(side.get("publish_allowed"))
    return performed and not allowed


def proof_verifier_mismatch(context: dict[str, Any], loop: dict[str, Any]) -> bool:
    proof = object_from(loop.get("proof")) or object_from(context.get("proof"))
    if explicit_no(proof.get("matches_verifier")):
        return True
    if as_yes(proof.get("required")) and "matches_verifier" not in proof:
        return True
    return False


def advisory_next_owner_for(reasons: list[str]) -> str:
    if not reasons:
        return "none"
    return next_owner_for(reasons, [])


# ---------------------------------------------------------------------------
# Main ATCG decision
# ---------------------------------------------------------------------------

def make_decision(context: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    run_id = require_str(context, "run_id", errors)
    source = context.get("source", "direct_goal")
    if source not in SOURCES:
        errors.append("source:invalid")
        source = "direct_goal"
    closure_candidate = context.get("closure_candidate", "blocked")
    if closure_candidate not in CLOSURE_CANDIDATES:
        errors.append("closure_candidate:invalid")
        closure_candidate = "blocked"

    artifact = optional_object(context, "artifact_scope", errors)
    local_proof = optional_object(context, "local_proof", errors)
    proof_patch = optional_object(context, "proof_patch", errors)
    cas = optional_object(context, "cas_review", errors)
    profile = optional_object(context, "review_profile", errors) or object_from(object_from(context.get("loop_governance")).get("review_profile"))
    delivery = optional_object(context, "delivery", errors)
    final_report = optional_object(context, "final_report_fields", errors)
    loop = object_from(context.get("loop_governance"))

    unresolved: list[str] = []
    blocked: list[str] = []
    if errors:
        blocked.extend(errors)

    blocked.extend(hard_completion_reasons_for(context))
    blocked.extend(artifact_reasons_for(artifact, proof_patch))

    local_reasons = local_proof_reasons_for(local_proof)
    if any(reason == "local_proof.evidence_fold_verdict:blocked" for reason in local_reasons):
        blocked.extend(local_reasons)
    else:
        unresolved.extend(local_reasons)

    unresolved.extend(proof_patch_reasons_for(proof_patch, closure_candidate))
    blocked.extend(cas_reasons_for(cas, profile, artifact))

    delivery_reasons, delivery_continue = delivery_reasons_for(delivery, closure_candidate, artifact)
    blocked.extend(delivery_reasons)
    unresolved.extend(delivery_continue)

    blocked.extend(final_report_reasons_for(final_report, cas, profile, proof_patch, delivery))

    if closure_candidate == "blocked":
        blocked.append("closure_candidate:blocked")
    elif closure_candidate == "ship-handoff":
        unresolved.append("ship_handoff:not-terminal")

    if blocked:
        verdict = "blocked"
        can_complete = "no"
        next_owner = next_owner_for(blocked, [])
    elif unresolved:
        verdict = "continue"
        can_complete = "no"
        next_owner = next_owner_for([], unresolved)
    else:
        verdict = "complete"
        can_complete = "yes"
        next_owner = "none"

    decision = {
        "actuation_terminal_decision": {
            "decision_version": "ATCG-v1",
            "verdict": verdict,
            "can_mark_goal_complete": can_complete,
            "issued_at": now_utc(),
            "run_id": run_id,
            "source": source,
            "closure_candidate": closure_candidate,
            "next_owner": next_owner,
            "blocked_reasons": unique(blocked) if verdict == "blocked" else [],
            "continue_reasons": unique(unresolved) if verdict == "continue" else [],
            "current_artifact_binding": {
                "repo": artifact.get("repo", ""),
                "branch": artifact.get("branch", ""),
                "head_sha": artifact.get("head_sha", ""),
                "diff_fingerprint": artifact.get("diff_fingerprint", ""),
                "dirty_state": artifact.get("dirty_state", "unknown"),
            },
            "required_receipts": required_receipts_for(proof_patch, cas, profile, delivery, closure_candidate, loop),
        }
    }
    validate_decision(decision)
    return decision


def unique(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def artifact_reasons_for(artifact: dict[str, Any], proof_patch: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    for key in ("repo", "branch", "head_sha", "diff_fingerprint"):
        if not isinstance(artifact.get(key), str) or not artifact.get(key):
            reasons.append(f"artifact_scope.{key}:missing")
    dirty_state = artifact.get("dirty_state", "unknown")
    if dirty_state == "clean":
        return reasons
    if dirty_state == "tracked-dirty" and proof_patch_bounds_dirty_artifact(proof_patch):
        return reasons
    reasons.append(f"artifact_scope.dirty_state:{dirty_state}")
    return reasons


def proof_patch_bounds_dirty_artifact(proof_patch: dict[str, Any]) -> bool:
    return as_yes(proof_patch.get("required")) and as_yes(proof_patch.get("present")) and as_yes(proof_patch.get("current"))


def local_proof_reasons_for(local_proof: dict[str, Any]) -> list[str]:
    verdict = local_proof.get("evidence_fold_verdict", "blocked")
    if verdict not in LOCAL_VERDICTS:
        return ["local_proof.evidence_fold_verdict:invalid"]
    if verdict != "done":
        return [f"local_proof.evidence_fold_verdict:{verdict}"]
    commands = local_proof.get("commands", [])
    if not isinstance(commands, list) or not commands:
        return ["local_proof.commands:missing"]
    return []


def proof_patch_reasons_for(proof_patch: dict[str, Any], closure_candidate: str) -> list[str]:
    required_by_candidate = closure_candidate == "proof-patch"
    if not required_by_candidate and not as_yes(proof_patch.get("required")):
        return []
    reasons: list[str] = []
    if required_by_candidate and not as_yes(proof_patch.get("required")):
        reasons.append("proof_patch.required:missing-for-proof-patch-closure")
    if not as_yes(proof_patch.get("present")):
        reasons.append("proof_patch:missing")
    if not as_yes(proof_patch.get("current")):
        reasons.append("proof_patch:not-current")
    return reasons


def cas_reasons_for(cas: dict[str, Any], profile: dict[str, Any], artifact: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    standard_required = standard_cas_required_for(cas, profile)
    if not standard_required:
        return auxiliary_lane_reasons_for(cas, artifact) + review_profile_reasons_for(profile, artifact, standard_required)
    required = standard_clean_runs_required_for(cas)
    count = standard_clean_runs_count_for(cas)
    standard_fields_used = "standard_clean_runs_required" in cas or "standard_clean_runs_count" in cas or not as_yes(cas.get("required"))
    if not is_plain_int(required) or required <= 0:
        reasons.append("cas.standard_clean_runs_required:invalid" if standard_fields_used else "cas.clean_runs_required:invalid")
        required = 3
    if not is_plain_int(count) or count < 0:
        reasons.append("cas.standard_clean_runs_count:invalid" if standard_fields_used else "cas.clean_runs_count:invalid")
        count = 0
    if count < required:
        prefix = "cas.standard_clean_runs" if standard_fields_used else "cas.clean_runs"
        reasons.append(f"{prefix}:{count}-of-{required}")
    if required > 0 and not as_yes(cas.get("independent_fresh_runs")):
        reasons.append("cas.standard_clean_runs:not-independent" if standard_fields_used else "cas.clean_runs:not-independent")
    if required > 0 and not as_yes(cas.get("tuple_bound")):
        reasons.append("cas.tuple:not-bound")
    tuple_value = object_from(cas.get("tuple"))
    for key in ("base_sha", "head_sha", "target_fingerprint"):
        if required > 0 and (not isinstance(tuple_value.get(key), str) or not tuple_value.get(key)):
            reasons.append(f"cas.tuple.{key}:missing")
    if required > 0 and isinstance(tuple_value.get("head_sha"), str) and tuple_value.get("head_sha"):
        if tuple_value.get("head_sha") != artifact.get("head_sha"):
            reasons.append("cas.tuple.head_sha:artifact-mismatch")
    if required > 0 and isinstance(tuple_value.get("target_fingerprint"), str) and tuple_value.get("target_fingerprint"):
        if tuple_value.get("target_fingerprint") != artifact.get("diff_fingerprint"):
            reasons.append("cas.tuple.target_fingerprint:artifact-mismatch")
    reasons.extend(auxiliary_lane_reasons_for(cas, artifact))
    reasons.extend(review_profile_reasons_for(profile, artifact, standard_required))
    return reasons


def delivery_reasons_for(delivery: dict[str, Any], closure_candidate: str, artifact: dict[str, Any]) -> tuple[list[str], list[str]]:
    ship_complete = closure_candidate == "ship-complete"
    publication_required = as_yes(delivery.get("publication_required")) or ship_complete
    if ship_complete and not as_yes(delivery.get("pr_intent")):
        return ["delivery.pr_intent:missing-for-ship-complete"], []
    if publication_required and not as_yes(delivery.get("pr_intent")):
        return ["delivery.pr_intent:missing-with-publication-required"], []
    if not as_yes(delivery.get("pr_intent")):
        return [], []
    blocked: list[str] = []
    pending: list[str] = []
    add = add_v1_decision_from(delivery.get("add_v1_decision"))
    add_verdict = add.get("verdict", "missing")
    if add_verdict != "missing":
        blocked.extend(add_v1_receipt_reasons_for(add, artifact))
    if add_verdict not in ADD_VERDICTS:
        blocked.append("delivery.add_v1_decision.verdict:invalid")
        add_verdict = "missing"
    if add_verdict == "blocked":
        blocked.append("delivery.add_v1_decision:blocked")
    elif add_verdict == "missing":
        blocked.append("delivery.add_v1_decision:missing")
    elif add_verdict == "shipping_not_requested":
        blocked.append("delivery.add_v1_decision:shipping-not-requested-with-pr-intent")
    elif add_verdict == "handoff_to_ship":
        ship = object_from(delivery.get("ship_result"))
        if publication_required:
            if not as_yes(ship.get("present")):
                pending.append("ship_result:missing")
            if not as_yes(ship.get("current")):
                pending.append("ship_result:not-current")
            if not isinstance(ship.get("pr_url"), str) or not ship.get("pr_url"):
                pending.append("ship_result.pr_url:missing")
        else:
            pending.append("ship_handoff:not-terminal")
    return blocked, pending


def add_v1_decision_from(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    wrapped = value.get("actuation_delivery_decision")
    if isinstance(wrapped, dict):
        return wrapped
    return value


def add_v1_receipt_reasons_for(add: dict[str, Any], artifact: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if add.get("decision_version") != "ADD-v1":
        reasons.append("delivery.add_v1_decision.decision_version:invalid")
    for key in ("run_id", "plan_id", "target_branch", "target_head"):
        if not isinstance(add.get(key), str) or not add.get(key):
            reasons.append(f"delivery.add_v1_decision.{key}:missing")
    if add.get("target_branch") != artifact.get("branch"):
        reasons.append("delivery.add_v1_decision.target_branch:artifact-mismatch")
    if not is_plain_int(add.get("branch_epoch")) or add.get("branch_epoch", -1) < 0:
        reasons.append("delivery.add_v1_decision.branch_epoch:invalid")
    receipts = add.get("integrated_change_set_receipts")
    if not isinstance(receipts, list) or not receipts:
        reasons.append("delivery.add_v1_decision.integrated_change_set_receipts:empty")
    proof = object_from(add.get("proof_complete_receipt"))
    if proof.get("present") != "yes" or proof.get("current") != "yes":
        reasons.append("delivery.add_v1_decision.proof_complete_receipt:not-current")
    integration = object_from(add.get("integration"))
    if integration.get("queue_quiescent") != "yes":
        reasons.append("delivery.add_v1_decision.integration.queue_quiescent:not-yes")
    if add.get("cross_plan_dependency_status") != "clear":
        reasons.append("delivery.add_v1_decision.cross_plan_dependency_status:not-clear")
    pr_intent = object_from(add.get("pr_intent"))
    if pr_intent.get("present") != "yes":
        reasons.append("delivery.add_v1_decision.pr_intent:not-present")
    if add.get("verdict") == "handoff_to_ship":
        reasons.extend(add_v1_head_reasons_for(add, artifact))
        handoff = object_from(add.get("ship_handoff"))
        if handoff.get("next_owner") != "$ship":
            reasons.append("delivery.add_v1_decision.ship_handoff.next_owner:invalid")
        ship_input = object_from(handoff.get("ship_input"))
        if ship_input.get("branch") != add.get("target_branch"):
            reasons.append("delivery.add_v1_decision.ship_input.branch:mismatch")
        actuation = object_from(ship_input.get("actuation"))
        if actuation.get("plan_id") != add.get("plan_id"):
            reasons.append("delivery.add_v1_decision.ship_input.actuation.plan_id:mismatch")
    return reasons


def add_v1_head_reasons_for(add: dict[str, Any], artifact: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    artifact_head = artifact.get("head_sha")
    target_head = add.get("target_head")
    if not isinstance(target_head, str) or not target_head:
        reasons.append("delivery.add_v1_decision.target_head:missing")
    elif target_head != artifact_head:
        reasons.append("delivery.add_v1_decision.target_head:artifact-mismatch")
    ship_input = object_from(object_from(add.get("ship_handoff")).get("ship_input"))
    ship_input_head = ship_input.get("head_sha")
    if not isinstance(ship_input_head, str) or not ship_input_head:
        reasons.append("delivery.add_v1_decision.ship_input.head_sha:missing")
    elif ship_input_head != artifact_head:
        reasons.append("delivery.add_v1_decision.ship_input.head_sha:artifact-mismatch")
    return reasons


def final_report_reasons_for(final_report: dict[str, Any], cas: dict[str, Any], profile: dict[str, Any], proof_patch: dict[str, Any], delivery: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if standard_cas_required_for(cas, profile):
        required = standard_clean_runs_required_for(cas)
        if not is_plain_int(required) or required <= 0:
            required = 3
        value = count_from(final_report.get("standard_clean_cas_runs"))
        reason = "final_report.standard_clean_cas_runs:not-satisfied"
        if value is None:
            value = count_from(final_report.get("normalized_standard_cas_clean_runs"))
            reason = "final_report.normalized_standard_cas_clean_runs:not-satisfied"
        if value is None:
            value = count_from(final_report.get("normalized_cas_clean_runs"))
            reason = "final_report.normalized_cas_clean_runs:not-satisfied"
        if value is None or value < required:
            reasons.append(reason)
    return reasons


def required_receipts_for(proof_patch: dict[str, Any], cas: dict[str, Any], profile: dict[str, Any], delivery: dict[str, Any], closure_candidate: str, loop: dict[str, Any]) -> list[str]:
    receipts: list[str] = []
    hsr = object_from(loop.get("hsr"))
    if direct_action_fused_requested(loop):
        receipts.append("fusion_receipt")
    elif loop_receipts_required(loop, hsr):
        receipts.extend(["alsr", "hyl", "terminal_hsr"])
    if as_yes(object_from(loop.get("goal_focus")).get("required")):
        receipts.append("goal_focus_frame_chain")
    if object_from(loop.get("refactor_kernel")).get("selected") == "yes" or as_yes(object_from(loop.get("refactor_kernel")).get("selected")):
        receipts.extend(["aer_v1", "rko_v1"])
    if as_yes(proof_patch.get("required")) or closure_candidate == "proof-patch":
        receipts.append("proof_patch")
    if standard_cas_required_for(cas, profile):
        receipts.append("cas_review")
    if as_yes(delivery.get("pr_intent")) or closure_candidate == "ship-complete":
        receipts.append("add_v1_delivery_decision")
    if as_yes(delivery.get("publication_required")) or closure_candidate == "ship-complete":
        receipts.append("ship_result")
    return unique(receipts)


def next_owner_for(blocked: list[str], pending: list[str]) -> str:
    combined = blocked + pending
    if any("ask-human" in reason for reason in combined):
        return "human"
    if any(reason.startswith("artifact_scope") for reason in combined):
        return "$goal-grind"
    profile_blocked = any(reason.startswith("review_profile") for reason in combined)
    cas_detail_blocked = any(
        reason.startswith("cas.")
        or reason.startswith("final_report.normalized_cas")
        or reason.startswith("final_report.normalized_standard_cas")
        or reason.startswith("final_report.standard_clean_cas")
        for reason in combined
    )
    if profile_blocked and not cas_detail_blocked:
        return "$goal-actuating"
    if "cas-review-blocked" in combined or cas_detail_blocked:
        return "$cas"
    if profile_blocked:
        return "$goal-actuating"
    if any(reason == "side-effect-boundary-violated" for reason in combined):
        return "$ship"
    if any(reason.startswith("fusion_receipt") or reason.startswith("goal_focus") for reason in combined):
        return "$goal-actuating"
    if any(reason.startswith("blocked-loop-contract") or reason.startswith("blocked-hylo") or reason.startswith("alsr") or reason.startswith("hyl") or reason.startswith("hsr") or reason.startswith("material_mutations") or reason.startswith("selected_loop") for reason in combined):
        return "$goal-actuating"
    if any(reason == "proof-stale" for reason in combined):
        return "$goal-grind"
    if any(reason.startswith("proof_patch") for reason in combined):
        return "$proof-patch"
    if any(reason.startswith("ship") or reason.startswith("delivery") or reason.startswith("final_report.ship") for reason in combined):
        return "$ship"
    if any(reason.startswith("local_proof") for reason in combined):
        return "$goal-grind"
    return "$goal-grind"


def validate_decision(value: dict[str, Any]) -> dict[str, Any]:
    d = unwrap(value, "actuation_terminal_decision")
    errors: list[str] = []
    if d.get("decision_version") != "ATCG-v1":
        errors.append("decision_version")
    verdict = d.get("verdict")
    if verdict not in TERMINAL_VERDICTS:
        errors.append("verdict")
    if d.get("can_mark_goal_complete") not in {"yes", "no"}:
        errors.append("can_mark_goal_complete")
    if d.get("next_owner") not in NEXT_OWNERS:
        errors.append("next_owner")
    if not isinstance(d.get("blocked_reasons"), list):
        errors.append("blocked_reasons")
    if not isinstance(d.get("continue_reasons"), list):
        errors.append("continue_reasons")
    if not isinstance(d.get("required_receipts"), list):
        errors.append("required_receipts")
    artifact = d.get("current_artifact_binding")
    if not isinstance(artifact, dict):
        errors.append("current_artifact_binding")
        artifact = {}
    if not isinstance(d.get("run_id"), str) or not d.get("run_id"):
        errors.append("run_id:missing")
    source = d.get("source")
    if not isinstance(source, str) or not source:
        errors.append("source:missing")
    elif source not in SOURCES:
        errors.append("source:invalid")
    closure_candidate = d.get("closure_candidate")
    if not isinstance(closure_candidate, str) or not closure_candidate:
        errors.append("closure_candidate:missing")
    elif closure_candidate not in CLOSURE_CANDIDATES:
        errors.append("closure_candidate:invalid")

    if verdict == "complete":
        if d.get("closure_candidate") not in {"proof-patch", "ship-complete"}:
            errors.append("complete.closure_candidate:not-terminal")
        receipts = d.get("required_receipts") if isinstance(d.get("required_receipts"), list) else []
        if d.get("closure_candidate") == "proof-patch" and "proof_patch" not in receipts:
            errors.append("complete.required_receipts.proof_patch:missing")
        if d.get("closure_candidate") == "ship-complete":
            if "add_v1_delivery_decision" not in receipts:
                errors.append("complete.required_receipts.add_v1_delivery_decision:missing")
            if "ship_result" not in receipts:
                errors.append("complete.required_receipts.ship_result:missing")
        for key in ("repo", "branch", "head_sha", "diff_fingerprint"):
            if not isinstance(artifact.get(key), str) or not artifact.get(key):
                errors.append(f"complete.current_artifact_binding.{key}:missing")
        if not complete_dirty_state_allowed(d, artifact):
            errors.append("complete.current_artifact_binding.dirty_state:not-clean")
        if d.get("can_mark_goal_complete") != "yes":
            errors.append("complete:can_mark_goal_complete-not-yes")
        if d.get("next_owner") != "none":
            errors.append("complete:next_owner-not-none")
        if d.get("blocked_reasons") or d.get("continue_reasons"):
            errors.append("complete:reasons-present")
    elif verdict == "blocked":
        if d.get("can_mark_goal_complete") != "no":
            errors.append("blocked:can_mark_goal_complete-not-no")
        if d.get("next_owner") == "none":
            errors.append("blocked:next_owner-none")
        if not d.get("blocked_reasons"):
            errors.append("blocked:reasons-required")
    elif verdict == "continue":
        if d.get("can_mark_goal_complete") != "no":
            errors.append("continue:can_mark_goal_complete-not-no")
        if d.get("next_owner") == "none":
            errors.append("continue:next_owner-none")
        if not d.get("continue_reasons"):
            errors.append("continue:reasons-required")

    result = {
        "actuation_terminal_gate": {
            "verdict": "pass" if not errors else "fail",
            "decision_verdict": verdict,
            "can_mark_goal_complete": d.get("can_mark_goal_complete"),
            "run_id": d.get("run_id"),
            "errors": errors,
        }
    }
    if errors:
        raise TerminalGateError(json.dumps(result, sort_keys=True))
    return result


def make_completion_allowance(value: dict[str, Any]) -> dict[str, Any]:
    validate_decision(value)
    d = unwrap(value, "actuation_terminal_decision")
    allowed = d.get("verdict") == "complete" and d.get("can_mark_goal_complete") == "yes"
    return {
        "actuation_completion_allowance": {
            "verdict": "allowed" if allowed else "denied",
            "can_call_update_goal_complete": "yes" if allowed else "no",
            "decision_version": d.get("decision_version"),
            "decision_verdict": d.get("verdict"),
            "can_mark_goal_complete": d.get("can_mark_goal_complete"),
            "run_id": d.get("run_id"),
            "next_owner": d.get("next_owner"),
            "blocked_reasons": d.get("blocked_reasons", []),
            "continue_reasons": d.get("continue_reasons", []),
        }
    }


def complete_dirty_state_allowed(decision: dict[str, Any], artifact: dict[str, Any]) -> bool:
    dirty_state = artifact.get("dirty_state")
    if dirty_state == "clean":
        return True
    receipts = decision.get("required_receipts")
    if dirty_state == "tracked-dirty" and isinstance(receipts, list):
        return "proof_patch" in receipts
    return False


def emit(obj: dict[str, Any], out: str | None = None) -> None:
    text = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Decide or validate ATCG-v1 terminal actuation closure.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_decide = sub.add_parser("decide")
    p_decide.add_argument("--context", required=True)
    p_decide.add_argument("--out")
    p_check = sub.add_parser("check")
    p_check.add_argument("--decision", required=True)
    p_allow = sub.add_parser("allow-complete")
    p_allow.add_argument("--decision", required=True)
    p_validate = sub.add_parser("validate")
    p_validate.add_argument("--context", required=True)
    p_validate.add_argument("--mode", choices=("advisory",), required=True)
    p_validate.add_argument("--format", choices=("json",), default="json")

    args = parser.parse_args(argv)
    try:
        if args.cmd == "decide":
            emit(make_decision(context_from(load_json(args.context))), args.out)
        elif args.cmd == "check":
            emit(validate_decision(load_json(args.decision)))
        elif args.cmd == "allow-complete":
            result = make_completion_allowance(load_json(args.decision))
            emit(result)
            return 0 if result["actuation_completion_allowance"]["can_call_update_goal_complete"] == "yes" else 1
        elif args.cmd == "validate":
            emit(make_advisory(context_from(load_json(args.context))))
        return 0
    except Exception as exc:
        print(json.dumps({"actuation_terminal_gate": {"verdict": "fail", "error": str(exc)}}, indent=2, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
