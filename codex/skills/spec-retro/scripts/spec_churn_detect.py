#!/usr/bin/env python3
"""Heuristic plan/spec churn detector for spec automation retrospectives."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def read(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def title(text: str) -> str | None:
    m = re.search(r"(?m)^\s*#\s+(.+?)\s*$", text)
    return m.group(1).strip() if m else None


def iteration_max(text: str) -> int | None:
    nums = [int(n) for n in re.findall(r"(?i)iteration\s*[:=]\s*(\d+)", text)]
    return max(nums) if nums else None


def count_any(patterns: list[str], text: str) -> int:
    return sum(len(re.findall(p, text, re.I | re.S)) for p in patterns)


def score(texts: list[tuple[str, str]], signal_threshold: int, subagent_threshold: int, update_plan_threshold: int) -> dict:
    titles = [title(t) for _, t in texts if title(t)]
    unique_titles = sorted(set(titles))
    iterations = [iteration_max(t) or 0 for _, t in texts]
    combined = "\n".join(t for _, t in texts)

    replacement_count = count_any([
        r"\b(replaced|supersedes|replacement plan|prior plan|changed objective|new governing objective)\b",
    ], combined)
    open_q_count = len(re.findall(r"(?i)open questions", combined))
    round_delta_strategy = len(re.findall(r"(?is)round delta.*?(strategy|objective|supersedes|replaced)", combined))
    user_added_invariant = len(re.findall(r"(?i)(A\+|invariant|zero-cost|comptime|second authority|public API|runtime behavior)", combined))
    blocked_count = len(re.findall(r"(?i)\bblocked\b", combined))
    update_plan_count = len(re.findall(r"(?i)\bupdate_plan\b", combined))
    spawn_agent_count = len(re.findall(r"(?i)\bspawn_agent\b", combined))
    signal_markers = len(re.findall(r"(?i)\bsignal(s)?\b", combined))

    high_iter = max(iterations or [0]) >= 10
    title_drift = len(unique_titles) >= 2
    campaign_shape = signal_markers >= signal_threshold or spawn_agent_count >= subagent_threshold or update_plan_count > update_plan_threshold

    score_value = 0
    score_value += 2 if title_drift else 0
    score_value += 2 if high_iter else 0
    score_value += min(3, replacement_count)
    score_value += min(2, round_delta_strategy)
    score_value += 1 if open_q_count >= 2 else 0
    score_value += 1 if user_added_invariant >= 2 else 0
    score_value += 1 if blocked_count >= 3 else 0
    score_value += 2 if campaign_shape else 0

    risk = "high" if score_value >= 6 else "medium" if score_value >= 3 else "low"
    recommendation = "return_to_grill_or_spec_gate" if score_value >= 3 else "planning_can_continue_if_gate_passes"
    if campaign_shape and risk != "low":
        recommendation = "emit_campaign_checkpoint_then_return_to_gate"

    return {
        "churn_score": score_value,
        "risk": risk,
        "title_drift": title_drift,
        "titles": unique_titles,
        "max_iteration": max(iterations or [0]),
        "replacement_language_count": replacement_count,
        "round_delta_strategy_count": round_delta_strategy,
        "open_questions_mentions": open_q_count,
        "user_added_invariant_markers": user_added_invariant,
        "blocked_mentions": blocked_count,
        "update_plan_mentions": update_plan_count,
        "spawn_agent_mentions": spawn_agent_count,
        "signal_markers": signal_markers,
        "campaign_shape": campaign_shape,
        "recommendation": recommendation,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("files", nargs="+")
    p.add_argument("--signal-threshold", type=int, default=750)
    p.add_argument("--subagent-threshold", type=int, default=8)
    p.add_argument("--update-plan-threshold", type=int, default=2)
    args = p.parse_args()
    texts = [(f, read(f)) for f in args.files]
    print(json.dumps(score(texts, args.signal_threshold, args.subagent_threshold, args.update_plan_threshold), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
