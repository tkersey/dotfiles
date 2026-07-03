#!/usr/bin/env -S uv run python
"""Actuating terminal closure gate.

ATCG-v1 prevents an actuation run from treating local verifier success as the
terminal state when proof-patch, CAS review, delivery, or ship evidence is still
required. It is a pure receiver-side reducer: it does not run CAS, create
proof-patch output, publish PRs, or mutate any workspace state.
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
SOURCES = {"accepted_spec", "direct_goal", "review", "st_handoff"}
CLOSURE_CANDIDATES = {"proof-patch", "ship-handoff", "ship-complete", "blocked"}
LOCAL_VERDICTS = {"done", "continue", "regress", "blocked", "invalid-proof", "ask-human", "refactor-kernel"}
ADD_VERDICTS = {"handoff_to_ship", "shipping_not_requested", "blocked", "missing"}
TERMINAL_VERDICTS = {"complete", "continue", "blocked"}
NEXT_OWNERS = {"none", "$cas", "$proof-patch", "$ship", "$goal-grind", "$goal-actuating", "$st", "human"}
HARD_REASON_ORDER = [
    "blocked-loop-contract-missing",
    "blocked-loop-contract-stale",
    "blocked-hylo-frontier-missing",
    "blocked-hylo-fold-missing",
    "blocked-hylo-terminal-missing",
    "cas-review-blocked",
    "st-authority-blocked",
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


def yes_no_string(value: Any, *, default: str = "no") -> str:
    if as_yes(value):
        return "yes"
    if value in NO or (isinstance(value, str) and value.lower() in NO):
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


def explicit_no(value: Any) -> bool:
    return value in NO or (isinstance(value, str) and value.lower() in NO)


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


def advisory_reasons_for(context: dict[str, Any]) -> list[str]:
    return hard_completion_reasons_for(context)


def hard_completion_reasons_for(context: dict[str, Any]) -> list[str]:
    loop = object_from(context.get("loop_governance"))
    hsr = object_from(loop.get("hsr"))
    reasons: list[str] = []

    direct_action_fused = as_yes(loop.get("direct_action_fused")) or loop.get("mode") in {
        "direct_action_fused",
        "direct-action-fused",
        "fused",
    }
    st_governed = as_yes(loop.get("st_governed")) or loop.get("mode") in {
        "st_governed",
        "st-governed",
        "st_owned",
        "st-owned",
    }
    st_current = st_governed and (
        as_yes(loop.get("st_control_current"))
        or as_yes(object_from(loop.get("st_control")).get("current"))
    )
    loop_receipts_exempt = direct_action_fused or st_current
    loop_required = loop_receipts_required(loop, hsr)

    alsr = object_from(loop.get("alsr"))
    alsr_required = (
        not loop_receipts_exempt
        and (as_yes(loop.get("alsr_required")) or as_yes(alsr.get("required")) or loop_required)
    )
    if alsr_required:
        if not as_yes(alsr.get("present")):
            append_reason(reasons, "blocked-loop-contract-missing")
        elif not as_yes(alsr.get("current")):
            append_reason(reasons, "blocked-loop-contract-stale")

    hyl = object_from(loop.get("hyl"))
    hyl_required = not loop_receipts_exempt and (
        as_yes(loop.get("hyl_required"))
        or as_yes(loop.get("recursive"))
        or as_yes(loop.get("material"))
        or as_yes(hyl.get("required"))
        or loop_required
    )
    if hyl_required:
        if not as_yes(hyl.get("present")):
            append_reason(reasons, "blocked-loop-contract-missing")
        elif not as_yes(hyl.get("current")):
            append_reason(reasons, "blocked-loop-contract-stale")

    if st_governed and not st_current:
        append_reason(reasons, "st-authority-blocked")

    if loop_required and not loop_receipts_exempt:
        if not as_yes(hsr.get("terminal_present")):
            append_reason(reasons, "blocked-hylo-terminal-missing")
        reasons.extend(material_mutation_hsr_reasons(loop, hsr))
        if explicit_no(hsr.get("latest_fold_present")):
            append_reason(reasons, "blocked-hylo-fold-missing")
        if not as_yes(hsr.get("latest_fold_current_artifact_bound")):
            append_reason(reasons, "proof-stale")

    selected_loop = object_from(loop.get("selected_loop"))
    if selected_loop and not as_yes(selected_loop.get("matches_task_shape")):
        append_reason(reasons, "blocked-hylo-frontier-missing")

    review_fix = object_from(loop.get("review_fix"))
    if as_yes(review_fix.get("required")) and not review_fix_obeyed(review_fix):
        append_reason(reasons, "cas-review-blocked")

    if cas_advisory_blocked(context, loop):
        append_reason(reasons, "cas-review-blocked")

    if side_effect_boundary_violated(context, loop):
        append_reason(reasons, "side-effect-boundary-violated")

    if proof_verifier_mismatch(context, loop):
        append_reason(reasons, "proof-stale")

    return sort_hard_reasons(reasons)


def append_reason(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)


def sort_hard_reasons(reasons: list[str]) -> list[str]:
    order = {reason: index for index, reason in enumerate(HARD_REASON_ORDER)}
    return sorted(reasons, key=lambda reason: order.get(reason, len(order)))


def loop_receipts_required(loop: dict[str, Any], hsr: dict[str, Any]) -> bool:
    return any(
        as_yes(value)
        for value in (
            loop.get("loop_contract_required"),
            loop.get("material"),
            loop.get("recursive"),
            object_from(loop.get("alsr")).get("required"),
            object_from(loop.get("hyl")).get("required"),
            hsr.get("required"),
            hsr.get("terminal_required"),
        )
    )


def material_mutations_have_hsr(loop: dict[str, Any], hsr: dict[str, Any]) -> bool:
    return not material_mutation_hsr_reasons(loop, hsr)


def material_mutation_hsr_reasons(loop: dict[str, Any], hsr: dict[str, Any]) -> list[str]:
    mutations = list_from(loop.get("material_mutations")) or list_from(hsr.get("material_mutations"))
    if not mutations:
        return ["blocked-hylo-frontier-missing"] if as_yes(loop.get("material")) else []
    reasons: list[str] = []
    for mutation in mutations:
        item = object_from(mutation)
        if as_yes(item.get("has_hsr")):
            continue
        if not as_yes(item.get("has_unfold")) or not as_yes(item.get("has_action")):
            append_reason(reasons, "blocked-hylo-frontier-missing")
        if not as_yes(item.get("has_fold")):
            append_reason(reasons, "blocked-hylo-fold-missing")
    return reasons


def review_fix_obeyed(review_fix: dict[str, Any]) -> bool:
    return (
        as_yes(review_fix.get("cas_reviewed"))
        and as_yes(review_fix.get("review_folded"))
        and as_yes(review_fix.get("resolve_passed"))
    )


def cas_advisory_blocked(context: dict[str, Any], loop: dict[str, Any]) -> bool:
    cas = object_from(context.get("cas_review"))
    artifact = object_from(context.get("artifact_scope"))
    final_report = object_from(context.get("final_report_fields"))
    if cas_reasons_for(cas, artifact) or final_report_reasons_for(
        final_report,
        cas,
        object_from(context.get("proof_patch")),
        object_from(context.get("delivery")),
    ):
        return True

    clean_runs = object_from(loop.get("cas_clean_runs"))
    if not as_yes(clean_runs.get("required")):
        return False
    required = clean_runs.get("required_count", clean_runs.get("clean_runs_required", 3))
    count = clean_runs.get("count", clean_runs.get("clean_runs_count", 0))
    if not is_plain_int(required) or required <= 0:
        return True
    if not is_plain_int(count) or count < required:
        return True
    if not as_yes(clean_runs.get("independent_fresh_runs")):
        return True
    if not as_yes(clean_runs.get("tuple_bound")):
        return True
    return False


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
    if "st-authority-blocked" in reasons:
        return "$st"
    if "cas-review-blocked" in reasons:
        return "$cas"
    if "side-effect-boundary-violated" in reasons:
        return "$ship"
    if any(reason.startswith("blocked-loop-contract") or reason.startswith("blocked-hylo") for reason in reasons):
        return "$goal-actuating"
    return "$goal-actuating"


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
    delivery = optional_object(context, "delivery", errors)
    final_report = optional_object(context, "final_report_fields", errors)

    unresolved: list[str] = []
    blocked: list[str] = []
    if errors:
        blocked.extend(errors)

    blocked.extend(hard_completion_reasons_for(context))

    artifact_reasons = artifact_reasons_for(artifact, proof_patch)
    blocked.extend(artifact_reasons)

    local_reasons = local_proof_reasons_for(local_proof)
    if any(reason == "local_proof.evidence_fold_verdict:blocked" for reason in local_reasons):
        blocked.extend(local_reasons)
    else:
        unresolved.extend(local_reasons)

    proof_reasons = proof_patch_reasons_for(proof_patch, closure_candidate)
    unresolved.extend(proof_reasons)

    cas_reasons = cas_reasons_for(cas, artifact)
    blocked.extend(cas_reasons)

    delivery_reasons, delivery_continue = delivery_reasons_for(delivery, closure_candidate, artifact)
    blocked.extend(delivery_reasons)
    unresolved.extend(delivery_continue)

    report_reasons = final_report_reasons_for(final_report, cas, proof_patch, delivery)
    blocked.extend(report_reasons)

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
            "blocked_reasons": blocked if verdict == "blocked" else [],
            "continue_reasons": unresolved if verdict == "continue" else [],
            "current_artifact_binding": {
                "repo": artifact.get("repo", ""),
                "branch": artifact.get("branch", ""),
                "head_sha": artifact.get("head_sha", ""),
                "diff_fingerprint": artifact.get("diff_fingerprint", ""),
                "dirty_state": artifact.get("dirty_state", "unknown"),
            },
            "required_receipts": required_receipts_for(proof_patch, cas, delivery, closure_candidate),
        }
    }
    validate_decision(decision)
    return decision


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
    if dirty_state != "clean":
        reasons.append(f"artifact_scope.dirty_state:{dirty_state}")
    return reasons


def proof_patch_bounds_dirty_artifact(proof_patch: dict[str, Any]) -> bool:
    return (
        as_yes(proof_patch.get("required"))
        and as_yes(proof_patch.get("present"))
        and as_yes(proof_patch.get("current"))
    )


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


def cas_reasons_for(cas: dict[str, Any], artifact: dict[str, Any]) -> list[str]:
    if not as_yes(cas.get("required")):
        return []
    reasons: list[str] = []
    required = cas.get("clean_runs_required", 3)
    count = cas.get("clean_runs_count", 0)
    if not is_plain_int(required) or required <= 0:
        reasons.append("cas.clean_runs_required:invalid")
        required = 3
    if not is_plain_int(count) or count < 0:
        reasons.append("cas.clean_runs_count:invalid")
        count = 0
    if count < required:
        reasons.append(f"cas.clean_runs:{count}-of-{required}")
    if required > 0 and not as_yes(cas.get("independent_fresh_runs")):
        reasons.append("cas.clean_runs:not-independent")
    if required > 0 and not as_yes(cas.get("tuple_bound")):
        reasons.append("cas.tuple:not-bound")
    tuple_value = cas.get("tuple") if isinstance(cas.get("tuple"), dict) else {}
    for key in ("base_sha", "head_sha", "target_fingerprint"):
        if required > 0 and (not isinstance(tuple_value.get(key), str) or not tuple_value.get(key)):
            reasons.append(f"cas.tuple.{key}:missing")
    if required > 0 and isinstance(tuple_value.get("head_sha"), str) and tuple_value.get("head_sha"):
        if tuple_value.get("head_sha") != artifact.get("head_sha"):
            reasons.append("cas.tuple.head_sha:artifact-mismatch")
    if required > 0 and isinstance(tuple_value.get("target_fingerprint"), str) and tuple_value.get("target_fingerprint"):
        if tuple_value.get("target_fingerprint") != artifact.get("diff_fingerprint"):
            reasons.append("cas.tuple.target_fingerprint:artifact-mismatch")
    return reasons


def delivery_reasons_for(
    delivery: dict[str, Any],
    closure_candidate: str,
    artifact: dict[str, Any],
) -> tuple[list[str], list[str]]:
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
        ship = delivery.get("ship_result") if isinstance(delivery.get("ship_result"), dict) else {}
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
    proof = add.get("proof_complete_receipt") if isinstance(add.get("proof_complete_receipt"), dict) else {}
    if proof.get("present") != "yes" or proof.get("current") != "yes":
        reasons.append("delivery.add_v1_decision.proof_complete_receipt:not-current")
    integration = add.get("integration") if isinstance(add.get("integration"), dict) else {}
    if integration.get("queue_quiescent") != "yes":
        reasons.append("delivery.add_v1_decision.integration.queue_quiescent:not-yes")
    if add.get("cross_plan_dependency_status") != "clear":
        reasons.append("delivery.add_v1_decision.cross_plan_dependency_status:not-clear")
    pr_intent = add.get("pr_intent") if isinstance(add.get("pr_intent"), dict) else {}
    if pr_intent.get("present") != "yes":
        reasons.append("delivery.add_v1_decision.pr_intent:not-present")

    if add.get("verdict") == "handoff_to_ship":
        reasons.extend(add_v1_head_reasons_for(add, artifact))
        handoff = add.get("ship_handoff") if isinstance(add.get("ship_handoff"), dict) else {}
        if handoff.get("next_owner") != "$ship":
            reasons.append("delivery.add_v1_decision.ship_handoff.next_owner:invalid")
        ship_input = handoff.get("ship_input") if isinstance(handoff.get("ship_input"), dict) else {}
        if ship_input.get("branch") != add.get("target_branch"):
            reasons.append("delivery.add_v1_decision.ship_input.branch:mismatch")
        actuation = ship_input.get("actuation") if isinstance(ship_input.get("actuation"), dict) else {}
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

    handoff = add.get("ship_handoff") if isinstance(add.get("ship_handoff"), dict) else {}
    ship_input = handoff.get("ship_input") if isinstance(handoff.get("ship_input"), dict) else {}
    ship_input_head = ship_input.get("head_sha")
    if not isinstance(ship_input_head, str) or not ship_input_head:
        reasons.append("delivery.add_v1_decision.ship_input.head_sha:missing")
    elif ship_input_head != artifact_head:
        reasons.append("delivery.add_v1_decision.ship_input.head_sha:artifact-mismatch")
    return reasons


def final_report_reasons_for(
    final_report: dict[str, Any],
    cas: dict[str, Any],
    proof_patch: dict[str, Any],
    delivery: dict[str, Any],
) -> list[str]:
    reasons: list[str] = []
    if as_yes(cas.get("required")):
        required = cas.get("clean_runs_required", 3)
        if not is_plain_int(required) or required <= 0:
            required = 3
        value = count_from(final_report.get("normalized_cas_clean_runs"))
        if value is None or value < required:
            reasons.append("final_report.normalized_cas_clean_runs:not-satisfied")
    return reasons


def required_receipts_for(
    proof_patch: dict[str, Any],
    cas: dict[str, Any],
    delivery: dict[str, Any],
    closure_candidate: str,
) -> list[str]:
    receipts: list[str] = []
    if as_yes(proof_patch.get("required")) or closure_candidate == "proof-patch":
        receipts.append("proof_patch")
    if as_yes(cas.get("required")):
        receipts.append("cas_review")
    if as_yes(delivery.get("pr_intent")) or closure_candidate == "ship-complete":
        receipts.append("add_v1_delivery_decision")
    if as_yes(delivery.get("publication_required")) or closure_candidate == "ship-complete":
        receipts.append("ship_result")
    return receipts


def next_owner_for(blocked: list[str], pending: list[str]) -> str:
    combined = blocked + pending
    if any("ask-human" in reason for reason in combined):
        return "human"
    if any(reason == "st-authority-blocked" for reason in combined):
        return "$st"
    if any(reason.startswith("artifact_scope") for reason in combined):
        return "$goal-grind"
    if any(
        reason == "cas-review-blocked"
        or reason.startswith("cas.")
        or reason.startswith("final_report.normalized_cas")
        for reason in combined
    ):
        return "$cas"
    if any(reason == "side-effect-boundary-violated" for reason in combined):
        return "$ship"
    if any(reason.startswith("blocked-loop-contract") or reason.startswith("blocked-hylo") for reason in combined):
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

    if verdict == "complete":
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
    p_validate = sub.add_parser("validate")
    p_validate.add_argument("--context", required=True)
    p_validate.add_argument("--mode", choices=("advisory",), required=True)
    p_validate.add_argument("--format", choices=("json",), default="json")

    args = parser.parse_args(argv)
    try:
        if args.cmd == "decide":
            context = context_from(load_json(args.context))
            decision = make_decision(context)
            emit(decision, args.out)
        elif args.cmd == "check":
            decision = load_json(args.decision)
            result = validate_decision(decision)
            emit(result)
        elif args.cmd == "validate":
            context = context_from(load_json(args.context))
            result = make_advisory(context)
            emit(result)
        return 0
    except Exception as exc:
        print(json.dumps({"actuation_terminal_gate": {"verdict": "fail", "error": str(exc)}}, indent=2, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
