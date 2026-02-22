#!/usr/bin/env -S uv run python
"""Manifest-first patch-to-PR routing helper for cloud join operator flows."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CandidateScore:
    pr_number: int
    score: float
    confidence: float
    reason: str
    components: dict[str, float] = field(default_factory=dict)
    entity_overlap: float = 0.0


def load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_paths(paths: list[Any]) -> set[str]:
    normalized: set[str] = set()
    for item in paths:
        if isinstance(item, str):
            candidate = item.strip("/")
            if candidate:
                normalized.add(candidate)
            continue
        if isinstance(item, dict):
            raw = item.get("path")
            if isinstance(raw, str):
                candidate = raw.strip("/")
                if candidate:
                    normalized.add(candidate)
    return normalized


def normalize_entities(entities: list[Any]) -> set[str]:
    normalized: set[str] = set()
    for item in entities:
        raw = None
        if isinstance(item, str):
            raw = item
        elif isinstance(item, dict):
            # manifest items typically use "entity"; PR labels can expose "name"
            entity = item.get("entity")
            name = item.get("name")
            if isinstance(entity, str):
                raw = entity
            elif isinstance(name, str):
                raw = name
        if isinstance(raw, str):
            candidate = raw.strip().lower()
            if candidate:
                normalized.add(candidate)
    return normalized


def normalize_risk_level(value: Any) -> str:
    if not isinstance(value, str):
        return "medium"
    level = value.strip().lower()
    if level in {"low", "medium", "high", "critical"}:
        return level
    return "medium"


def entity_overlap_ratio(manifest_entities: set[str], pr: dict[str, Any]) -> tuple[float, int]:
    if not manifest_entities:
        return 0.0, 0

    explicit_entities = normalize_entities(pr.get("entities", []))
    label_entities = normalize_entities(pr.get("labels", []))
    pr_text = f"{pr.get('title', '')} {pr.get('body', '')}".lower()

    hits = 0
    for entity in manifest_entities:
        if entity in explicit_entities or entity in label_entities or entity in pr_text:
            hits += 1

    return hits / len(manifest_entities), hits


def overlap_ratio(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def score_pr(manifest: dict[str, Any], pr: dict[str, Any]) -> CandidateScore:
    score = 0.0
    reasons: list[str] = []
    components: dict[str, float] = {
        "target_pr_hint": 0.0,
        "entity_overlap": 0.0,
        "entity_hits": 0.0,
        "base_branch_match": 0.0,
        "path_overlap": 0.0,
        "issue_refs": 0.0,
        "raw_score": 0.0,
        "risk_multiplier": 0.0,
    }

    pr_number = int(pr.get("number", 0))
    if pr_number <= 0:
        return CandidateScore(pr_number=0, score=0.0, confidence=0.0, reason="invalid_pr")

    hint = manifest.get("target_pr_hint")
    if isinstance(hint, int) and hint == pr_number:
        hint_score = 5.0
        score += hint_score
        components["target_pr_hint"] = hint_score
        reasons.append("target_pr_hint")

    manifest_entities = normalize_entities(manifest.get("touched_entities", []))
    entity_ratio, entity_hits = entity_overlap_ratio(manifest_entities, pr)
    if entity_ratio > 0:
        entity_score = 4.5 * entity_ratio
        score += entity_score
        components["entity_overlap"] = entity_score
        components["entity_hits"] = float(entity_hits)
        reasons.append(f"entity_overlap={entity_ratio:.2f}")
        reasons.append(f"entity_hits={entity_hits}")

    base_branch = str(manifest.get("base_branch", ""))
    pr_base = str(pr.get("baseRefName", ""))
    if base_branch and pr_base and base_branch == pr_base:
        base_branch_score = 1.5
        score += base_branch_score
        components["base_branch_match"] = base_branch_score
        reasons.append("base_branch_match")

    manifest_paths = normalize_paths(manifest.get("changed_paths", []))
    pr_paths = normalize_paths(pr.get("files", []))
    ratio = overlap_ratio(manifest_paths, pr_paths)
    if ratio > 0:
        path_score = 3.0 * ratio
        score += path_score
        components["path_overlap"] = path_score
        reasons.append(f"path_overlap={ratio:.2f}")

    issue_refs = [str(x).lower() for x in manifest.get("issue_refs", []) if str(x).strip()]
    pr_text = f"{pr.get('title', '')} {pr.get('body', '')}".lower()
    issue_hits = sum(1 for ref in issue_refs if ref in pr_text)
    if issue_hits:
        issue_score = min(issue_hits, 2) * 0.5
        score += issue_score
        components["issue_refs"] = issue_score
        reasons.append(f"issue_refs={issue_hits}")

    risk_level = normalize_risk_level(manifest.get("risk_level"))
    risk_multiplier = {
        "low": 1.00,
        "medium": 0.95,
        "high": 0.80,
        "critical": 0.65,
    }[risk_level]
    components["risk_multiplier"] = risk_multiplier
    components["raw_score"] = score

    confidence = min(0.99, (score / 12.0) * risk_multiplier)
    return CandidateScore(
        pr_number=pr_number,
        score=score,
        confidence=confidence,
        reason=",".join(reasons),
        components=components,
        entity_overlap=entity_ratio,
    )


def route(manifest: dict[str, Any], prs: list[dict[str, Any]], threshold: float, top: int) -> dict[str, Any]:
    candidates = [score_pr(manifest, pr) for pr in prs]
    candidates = [c for c in candidates if c.pr_number > 0]
    candidates.sort(key=lambda c: c.score, reverse=True)

    selected = candidates[0] if candidates else None
    runner_up = candidates[1] if len(candidates) > 1 else None

    needs_seq = False
    reasons: list[str] = []

    def add_reason(reason: str) -> None:
        if reason not in reasons:
            reasons.append(reason)

    manifest_entities = normalize_entities(manifest.get("touched_entities", []))
    risk_level = normalize_risk_level(manifest.get("risk_level"))
    risk_threshold_multiplier = {
        "low": 0.95,
        "medium": 1.00,
        "high": 1.15,
        "critical": 1.25,
    }[risk_level]
    effective_threshold = min(0.99, threshold * risk_threshold_multiplier)

    if not selected:
        needs_seq = True
        add_reason("no_candidate")
    else:
        if selected.confidence < effective_threshold:
            needs_seq = True
            add_reason("low_confidence")
        if runner_up and (selected.score - runner_up.score) < 0.75:
            needs_seq = True
            add_reason("small_margin")
        if (
            "entity_overlap" not in selected.reason
            and "path_overlap" not in selected.reason
            and manifest.get("target_pr_hint") is None
        ):
            needs_seq = True
            add_reason("no_entity_path_or_hint_signal")
        if manifest_entities and "entity_overlap" not in selected.reason and manifest.get("target_pr_hint") is None:
            needs_seq = True
            add_reason("no_entity_signal")

    if risk_level in {"high", "critical"}:
        needs_seq = True
        add_reason(f"risk_level_{risk_level}")

    return {
        "patch_id": manifest.get("patch_id"),
        "risk_level": risk_level,
        "confidence_threshold": round(threshold, 4),
        "effective_confidence_threshold": round(effective_threshold, 4),
        "risk_threshold_multiplier": round(risk_threshold_multiplier, 4),
        "manifest_entity_count": len(manifest_entities),
        "selected_pr": selected.pr_number if selected else None,
        "selected_confidence": round(selected.confidence, 4) if selected else 0.0,
        "selected_score_components": (
            {k: round(v, 4) for k, v in selected.components.items()} if selected else None
        ),
        "score_margin": round(selected.score - runner_up.score, 4) if (selected and runner_up) else None,
        "needs_seq": needs_seq,
        "needs_seq_reasons": reasons,
        "candidates": [
            {
                "pr_number": c.pr_number,
                "score": round(c.score, 4),
                "confidence": round(c.confidence, 4),
                "entity_overlap": round(c.entity_overlap, 4),
                "score_components": {k: round(v, 4) for k, v in c.components.items()},
                "reason": c.reason,
            }
            for c in candidates[:top]
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Route a patch manifest to candidate PRs")
    parser.add_argument("--manifest", required=True, help="Path to patch manifest JSON")
    parser.add_argument(
        "--prs",
        required=True,
        help="Path to open PR snapshot JSON list (items should include number, baseRefName, title/body, and files)",
    )
    parser.add_argument("--threshold", type=float, default=0.70, help="Confidence threshold")
    parser.add_argument("--top", type=int, default=3, help="Top N candidates to return")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not (0.0 <= args.threshold <= 1.0):
        raise SystemExit("--threshold must be between 0 and 1")
    if args.top <= 0:
        raise SystemExit("--top must be positive")

    manifest = load_json(args.manifest)
    prs = load_json(args.prs)
    if not isinstance(prs, list):
        raise SystemExit("--prs must point to a JSON array")

    result = route(manifest, prs, args.threshold, args.top)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
