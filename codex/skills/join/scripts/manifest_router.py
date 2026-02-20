#!/usr/bin/env -S uv run python
"""Manifest-first patch-to-PR routing helper for cloud join operator flows."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class CandidateScore:
    pr_number: int
    score: float
    confidence: float
    reason: str


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


def overlap_ratio(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def score_pr(manifest: dict[str, Any], pr: dict[str, Any]) -> CandidateScore:
    score = 0.0
    reasons: list[str] = []

    pr_number = int(pr.get("number", 0))
    if pr_number <= 0:
        return CandidateScore(pr_number=0, score=0.0, confidence=0.0, reason="invalid_pr")

    hint = manifest.get("target_pr_hint")
    if isinstance(hint, int) and hint == pr_number:
        score += 5.0
        reasons.append("target_pr_hint")

    base_branch = str(manifest.get("base_branch", ""))
    pr_base = str(pr.get("baseRefName", ""))
    if base_branch and pr_base and base_branch == pr_base:
        score += 1.5
        reasons.append("base_branch_match")

    manifest_paths = normalize_paths(manifest.get("changed_paths", []))
    pr_paths = normalize_paths(pr.get("files", []))
    ratio = overlap_ratio(manifest_paths, pr_paths)
    if ratio > 0:
        score += 4.0 * ratio
        reasons.append(f"path_overlap={ratio:.2f}")

    issue_refs = [str(x).lower() for x in manifest.get("issue_refs", []) if str(x).strip()]
    pr_text = f"{pr.get('title', '')} {pr.get('body', '')}".lower()
    issue_hits = sum(1 for ref in issue_refs if ref in pr_text)
    if issue_hits:
        score += min(issue_hits, 2)
        reasons.append(f"issue_refs={issue_hits}")

    confidence = min(0.99, score / 8.0)
    return CandidateScore(pr_number=pr_number, score=score, confidence=confidence, reason=",".join(reasons))


def route(manifest: dict[str, Any], prs: list[dict[str, Any]], threshold: float, top: int) -> dict[str, Any]:
    candidates = [score_pr(manifest, pr) for pr in prs]
    candidates = [c for c in candidates if c.pr_number > 0]
    candidates.sort(key=lambda c: c.score, reverse=True)

    selected = candidates[0] if candidates else None
    runner_up = candidates[1] if len(candidates) > 1 else None

    needs_seq = False
    reasons: list[str] = []

    if not selected:
        needs_seq = True
        reasons.append("no_candidate")
    else:
        if selected.confidence < threshold:
            needs_seq = True
            reasons.append("low_confidence")
        if runner_up and (selected.score - runner_up.score) < 0.75:
            needs_seq = True
            reasons.append("small_margin")
        if "path_overlap" not in selected.reason and manifest.get("target_pr_hint") is None:
            needs_seq = True
            reasons.append("no_path_or_hint_signal")

    return {
        "patch_id": manifest.get("patch_id"),
        "selected_pr": selected.pr_number if selected else None,
        "selected_confidence": round(selected.confidence, 4) if selected else 0.0,
        "needs_seq": needs_seq,
        "needs_seq_reasons": reasons,
        "candidates": [
            {
                "pr_number": c.pr_number,
                "score": round(c.score, 4),
                "confidence": round(c.confidence, 4),
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
