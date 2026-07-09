#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pyyaml"]
# ///
"""Validate classification-only RF-v2 receipts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import yaml


BACKENDS = {
    "cas",
    "github-comments",
    "human-review",
    "prior-artifact",
    "local-audit",
    "other",
}
SOURCE_STATES = {"clean", "findings", "invalid-proof", "incomplete"}
VALIDITY = {"valid", "invalid", "unproven", "needs-owner"}
LIABILITIES = {
    "blocks-goal",
    "regression-risk",
    "proof-gap",
    "misuse-hazard",
    "invariant-gap",
    "complexity-stall",
    "style",
    "new-requirement",
    "out-of-scope",
}
INTENT = {"core", "adjacent", "unrelated", "expands-scope"}
NOVELTY = {"duplicate", "same-class", "new-class"}
DISPOSITIONS = {
    "reject",
    "proof-only",
    "ask-human",
    "follow-up",
    "resolution-input",
    "blocked",
}
LENS_ROUTING = {
    "misuse-hazard": "footgun-finder",
    "invariant-gap": "invariant-ace",
    "complexity-stall": "complexity-mitigator",
}


def load(path: str) -> dict[str, Any]:
    source = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    value = json.loads(source) if path.endswith(".json") else yaml.safe_load(source)
    if not isinstance(value, dict):
        raise ValueError("receipt must be an object")
    candidate = value.get("review_fold", value)
    if not isinstance(candidate, dict):
        raise ValueError("review_fold must be an object")
    return candidate


def text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def strings(value: Any) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return []
    return value


def objects(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def validate(receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if receipt.get("version") != "RF-v2":
        errors.append("receipt-version")
    for key in ("fold_id", "goal_id"):
        if not text(receipt.get(key)):
            errors.append(f"{key}-missing")

    source = receipt.get("source")
    if not isinstance(source, dict):
        errors.append("source-missing")
        source = {}
    if source.get("backend") not in BACKENDS:
        errors.append("source-backend")
    if not text(source.get("source_batch_id")) or not text(source.get("source_ref")):
        errors.append("source-identity")
    source_state = text(source.get("source_state"))
    if source_state not in SOURCE_STATES:
        errors.append("source-state")
    artifact = source.get("artifact")
    if not isinstance(artifact, dict) or not all(
        text(artifact.get(key))
        for key in ("repo", "base_sha", "branch", "head_sha", "state_fingerprint")
    ):
        errors.append("source-artifact")

    intent = receipt.get("intent_anchor")
    if not isinstance(intent, dict) or not text(intent.get("original_goal")):
        errors.append("intent-anchor")
    elif not isinstance(intent.get("accepted_scope"), list) or not isinstance(
        intent.get("non_goals"), list
    ):
        errors.append("intent-scope")

    findings_raw = receipt.get("findings")
    findings = objects(findings_raw)
    if not isinstance(findings_raw, list) or len(findings) != len(findings_raw):
        errors.append("findings-shape")
    if source_state == "clean" and findings:
        errors.append("clean-source-has-findings")
    if source_state == "findings" and not findings:
        errors.append("findings-source-empty")

    seen: set[str] = set()
    quotient_members: dict[str, set[str]] = {}
    quotient_owner_laws: dict[str, set[tuple[str, str]]] = {}
    expected_routes: dict[str, set[str]] = {}
    routed_quotients = {
        text(finding.get("quotient_key")).strip()
        for finding in findings
        if finding.get("disposition")
        in {"resolution-input", "ask-human", "blocked"}
    }
    material_liabilities = LIABILITIES - {"style", "new-requirement", "out-of-scope"}
    dispositions_by_validity = {
        "valid": {"resolution-input", "ask-human", "blocked"},
        "unproven": {"proof-only", "blocked"},
        "needs-owner": {"ask-human", "blocked"},
        "invalid": {"reject"},
    }
    for index, finding in enumerate(findings):
        finding_id = text(finding.get("finding_id")).strip()
        if not finding_id or finding_id in seen:
            errors.append("finding-id")
        seen.add(finding_id)
        if not text(finding.get("source_ref")).strip():
            errors.append("finding-source")
        if not text(finding.get("claim")).strip():
            errors.append("finding-claim")
        if finding.get("validity") not in VALIDITY:
            errors.append("finding-validity")
        liability = text(finding.get("liability"))
        if liability not in LIABILITIES:
            errors.append("finding-liability")
        if finding.get("intent_relation") not in INTENT:
            errors.append("finding-intent")
        if finding.get("novelty") not in NOVELTY:
            errors.append("finding-novelty")
        disposition = text(finding.get("disposition"))
        if disposition not in DISPOSITIONS:
            errors.append("finding-disposition")
        if disposition == "follow-up" and finding.get("intent_relation") == "core":
            errors.append("follow-up-intent")
        duplicate_is_covered = (
            finding.get("novelty") == "duplicate"
            and disposition == "reject"
            and text(finding.get("quotient_key")).strip() in routed_quotients
        )
        if (
            finding.get("intent_relation") == "core"
            and liability in material_liabilities
            and disposition
            not in dispositions_by_validity.get(finding.get("validity"), set())
            and not duplicate_is_covered
        ):
            errors.append("core-material-disposition")
        authority = finding.get("mutation_authority")
        if not isinstance(authority, dict) or authority.get("allowed") is not False:
            errors.append("finding-mutation-authority")
        if isinstance(authority, dict) and not text(authority.get("reason")):
            errors.append("finding-mutation-reason")

        quotient = text(finding.get("quotient_key")).strip()
        if not quotient:
            errors.append("finding-quotient")
        else:
            quotient_members.setdefault(quotient, set()).add(finding_id)
        if liability in material_liabilities:
            observed_fact = text(finding.get("observed_fact")).strip()
            if not observed_fact or observed_fact == text(finding.get("claim")).strip():
                errors.append("material-observed-fact")
            for key in ("owner_boundary", "law_family", "falsifier"):
                if not text(finding.get(key)).strip():
                    errors.append(f"material-{key}")
            evidence_refs = strings(finding.get("evidence_refs"))
            if not evidence_refs or any(not ref.strip() for ref in evidence_refs):
                errors.append("material-evidence")
            owner = text(finding.get("owner_boundary")).strip()
            law = text(finding.get("law_family")).strip()
            if quotient and owner and law:
                quotient_owner_laws.setdefault(quotient, set()).add((owner, law))
        if disposition == "resolution-input":
            if source_state != "findings":
                errors.append("resolution-input-source-state")
            if finding.get("validity") != "valid":
                errors.append("resolution-input-validity")
            if finding.get("intent_relation") not in {"core", "adjacent"}:
                errors.append("resolution-input-intent")
            if liability in {"style", "new-requirement", "out-of-scope"}:
                errors.append("resolution-input-liability")
        if liability in LENS_ROUTING:
            expected_routes.setdefault(liability, set()).add(finding_id)

        forbidden = {
            "strategy",
            "selected_work_node",
            "clean_run",
            "clean_count",
            "closure_verdict",
        }
        if forbidden.intersection(finding):
            errors.append("finding-owned-field")

    compression = receipt.get("compression")
    classes = (
        objects(compression.get("equivalence_classes"))
        if isinstance(compression, dict)
        else []
    )
    declared: dict[str, set[str]] = {}
    for row in classes:
        key = text(row.get("quotient_key")).strip()
        members = {item.strip() for item in strings(row.get("finding_ids"))}
        if not key or key in declared:
            errors.append("compression-key")
        declared[key] = members
        owner = text(row.get("owner_boundary")).strip()
        law = text(row.get("law_family")).strip()
        if not owner or not law:
            errors.append("compression-owner-law")
        expected_owner_laws = quotient_owner_laws.get(key)
        if expected_owner_laws is not None and expected_owner_laws != {(owner, law)}:
            errors.append("compression-owner-law-mismatch")
    if declared != quotient_members:
        errors.append("compression-coverage")

    routes = objects(receipt.get("routing_obligations"))
    declared_routes: dict[str, set[str]] = {}
    for row in routes:
        trigger = text(row.get("trigger"))
        owner_lens = text(row.get("owner_lens"))
        if LENS_ROUTING.get(trigger) != owner_lens:
            errors.append("routing-owner")
        declared_routes[trigger] = {
            item.strip() for item in strings(row.get("finding_ids"))
        }
    if declared_routes != expected_routes:
        errors.append("routing-coverage")
    return sorted(set(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["validate"])
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--format", choices=["json"], default="json")
    args = parser.parse_args(argv)
    try:
        errors = validate(load(args.receipt))
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        errors = [f"malformed:{exc}"]
    result = {
        "review_fold_receipt_gate": {
            "verdict": "pass" if not errors else "blocked",
            "errors": errors,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
