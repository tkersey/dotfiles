#!/usr/bin/env python3
"""Heuristic plan-churn detector for spec automation retrospectives."""
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


def score(texts: list[tuple[str, str]]) -> dict:
    titles = [title(t) for _, t in texts if title(t)]
    unique_titles = sorted(set(titles))
    iterations = [iteration_max(t) or 0 for _, t in texts]
    combined = "\n".join(t for _, t in texts)
    replacement_count = len(re.findall(r"(?i)\b(replaced|supersedes|replacement plan|prior plan|changed objective|new governing objective)\b", combined))
    open_q_count = len(re.findall(r"(?i)open questions", combined))
    round_delta_strategy = len(re.findall(r"(?is)round delta.*?(strategy|objective|supersedes|replaced)", combined))
    high_iter = max(iterations or [0]) >= 10
    title_drift = len(unique_titles) >= 2
    score_value = 0
    score_value += 2 if title_drift else 0
    score_value += 2 if high_iter else 0
    score_value += min(3, replacement_count)
    score_value += min(2, round_delta_strategy)
    score_value += 1 if open_q_count >= 2 else 0
    return {
        "churn_score": score_value,
        "risk": "high" if score_value >= 6 else "medium" if score_value >= 3 else "low",
        "title_drift": title_drift,
        "titles": unique_titles,
        "max_iteration": max(iterations or [0]),
        "replacement_language_count": replacement_count,
        "round_delta_strategy_count": round_delta_strategy,
        "open_questions_mentions": open_q_count,
        "recommendation": "return_to_grill_or_spec_gate" if score_value >= 3 else "planning_can_continue_if_gate_passes",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("files", nargs="+")
    args = p.parse_args()
    texts = [(f, read(f)) for f in args.files]
    print(json.dumps(score(texts), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
