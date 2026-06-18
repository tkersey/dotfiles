#!/usr/bin/env python3
"""Heuristic plan/spec churn detector for `$spec-retro`."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def read(path: str) -> str:
    return sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")


def title(text: str) -> str | None:
    match = re.search(r"(?m)^\s*#\s+(.+?)\s*$", text)
    return match.group(1).strip() if match else None


def iteration_max(text: str) -> int:
    values = [int(value) for value in re.findall(r"(?i)iteration\s*[:=]\s*(\d+)", text)]
    return max(values) if values else 0


def count(pattern: str, text: str) -> int:
    return len(re.findall(pattern, text, re.I | re.S))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    parser.add_argument("--signal-threshold", type=int, default=750)
    parser.add_argument("--subagent-threshold", type=int, default=8)
    parser.add_argument("--update-plan-threshold", type=int, default=2)
    args = parser.parse_args()

    texts = [(path, read(path)) for path in args.files]
    combined = "\n".join(text for _, text in texts)
    titles = sorted({value for _, text in texts if (value := title(text))})
    max_iteration = max((iteration_max(text) for _, text in texts), default=0)

    signals = {
        "title_drift": len(titles) >= 2,
        "high_iteration": max_iteration >= 10,
        "replacement_language_count": count(r"\b(replaced|supersedes|replacement plan|changed objective|new governing objective)\b", combined),
        "round_delta_strategy_count": count(r"round delta.*?(strategy|objective|supersedes|replaced)", combined),
        "open_questions_mentions": count(r"\bopen questions\b", combined),
        "blocked_mentions": count(r"\bblocked\b", combined),
        "update_plan_mentions": count(r"\bupdate_plan\b", combined),
        "spawn_agent_mentions": count(r"\bspawn_agent\b", combined),
        "signal_markers": count(r"\bsignals?\b", combined),
    }

    campaign_shape = (
        signals["signal_markers"] >= args.signal_threshold
        or signals["spawn_agent_mentions"] >= args.subagent_threshold
        or signals["update_plan_mentions"] > args.update_plan_threshold
    )

    score = 0
    score += 2 if signals["title_drift"] else 0
    score += 2 if signals["high_iteration"] else 0
    score += min(3, signals["replacement_language_count"])
    score += min(2, signals["round_delta_strategy_count"])
    score += 1 if signals["open_questions_mentions"] >= 2 else 0
    score += 1 if signals["blocked_mentions"] >= 3 else 0
    score += 2 if campaign_shape else 0

    risk = "high" if score >= 6 else "medium" if score >= 3 else "low"
    trigger_retro = risk != "low" or campaign_shape

    result = {
        "spec_churn_result": {
            "churn_score": score,
            "risk": risk,
            "titles": titles,
            "max_iteration": max_iteration,
            "campaign_shape": campaign_shape,
            "retro_trigger_required": trigger_retro,
            "signals": signals,
            "recommended_next_action": (
                "run_spec_retro"
                if trigger_retro
                else "continue_and_measure"
            ),
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
