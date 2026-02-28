#!/usr/bin/env -S uv run python
"""Monthly drift scorecard for the $zig skill."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SAFE_CUES = {
    "cues": [
        {"name": "zig_build", "pattern": "zig build", "case_insensitive": True},
        {"name": "zig_test", "pattern": "zig test", "case_insensitive": True},
        {"name": "zig_run", "pattern": "zig run", "case_insensitive": True},
        {"name": "zig_fmt", "pattern": "zig fmt", "case_insensitive": True},
        {"name": "zig_fetch", "pattern": "zig fetch", "case_insensitive": True},
        {"name": "comptime", "pattern": "comptime", "case_insensitive": True},
        {"name": "vector", "pattern": "@vector", "case_insensitive": True},
        {"name": "cimport", "pattern": "@cimport", "case_insensitive": True},
    ]
}


@dataclass
class ScorecardConfig:
    root: str
    since: str


def run_cmd(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        msg = proc.stderr.strip() or proc.stdout.strip() or "command failed"
        raise RuntimeError(f"{' '.join(cmd)} -> {msg}")
    return proc.stdout


def run_trigger_audit(config: ScorecardConfig) -> dict[str, Any]:
    script = Path(__file__).with_name("zig_trigger_audit.py")
    out = run_cmd(
        [
            sys.executable,
            str(script),
            "--root",
            config.root,
            "--since",
            config.since,
            "--strict-implicit",
            "--format",
            "json",
        ]
    )
    return json.loads(out)


def run_routing_gap(config: ScorecardConfig) -> list[dict[str, Any]]:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=True) as tmp:
        json.dump(SAFE_CUES, tmp)
        tmp.flush()
        out = run_cmd(
            [
                "seq",
                "routing-gap",
                "--root",
                config.root,
                "--since",
                config.since,
                "--cue-spec",
                f"@{tmp.name}",
                "--discovery-skills",
                "zig",
                "--format",
                "json",
            ]
        )
    return json.loads(out)


def recommendations(skill_lines: int, audit: dict[str, Any], routing: list[dict[str, Any]]) -> list[str]:
    recs: list[str] = []

    if skill_lines > 500:
        recs.append("Reduce codex/skills/zig/SKILL.md below 500 lines.")

    counts = audit.get("counts", {})
    implicit_intent = int(counts.get("implicit_zig_intent_sessions", 0))
    implicit_noise = int(counts.get("implicit_noise_filtered_sessions", 0))
    if implicit_intent > 0 and implicit_noise > implicit_intent:
        recs.append("Tighten noise filtering in zig_trigger_audit strict mode.")

    rates = audit.get("rates", {})
    explicit_recall = float(rates.get("explicit_session_recall_proxy_pct", 0.0))
    if explicit_recall < 70.0:
        recs.append("Improve explicit $zig handling: audit misses where user asked for $zig but assistant did not invoke it.")

    by_cue = {str(row.get("cue", "")): row for row in routing}
    zig_build = by_cue.get("zig_build")
    if zig_build:
        rate = float(zig_build.get("invoked_rate_pct", 0.0))
        if rate < 50.0:
            recs.append("Strengthen frontmatter cues for zig build workflows; current zig_build invoked rate is below 50%.")

    overall = by_cue.get("__all__")
    if overall:
        rate = float(overall.get("invoked_rate_pct", 0.0))
        if rate < 30.0:
            recs.append("Review trigger surface with seq routing-gap; overall invoked rate is below 30%.")

    if not recs:
        recs.append("No immediate drift action required.")
    return recs


def render_text(report: dict[str, Any]) -> str:
    lines = [
        "zig_ops_scorecard",
        f"generated_at: {report['generated_at']}",
        f"root: {report['root']}",
        f"since: {report['since']}",
        f"skill_lines: {report['skill_lines']}",
        "audit_counts:",
    ]

    for key, value in sorted(report["audit_counts"].items()):
        lines.append(f"  {key}: {value}")

    lines.append("audit_rates:")
    for key, value in sorted(report["audit_rates"].items()):
        lines.append(f"  {key}: {value:.2f}")

    lines.append("routing_gap_rates:")
    for item in report["routing_gap_rates"]:
        lines.append(f"  {item['cue']}: {item['invoked_rate_pct']:.2f}")

    lines.append("recommendations:")
    for item in report["recommendations"]:
        lines.append(f"  - {item}")

    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a drift scorecard for the zig skill.")
    parser.add_argument("--root", default=str(Path.home() / ".codex" / "sessions"), help="Sessions root")
    parser.add_argument("--since", required=True, help="Inclusive ISO timestamp lower bound")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    parser.add_argument("--output", default=None, help="Optional output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = ScorecardConfig(root=args.root, since=args.since)

    skill_path = Path(__file__).resolve().parents[1] / "SKILL.md"
    skill_lines = sum(1 for _ in skill_path.open("r", encoding="utf-8"))

    audit = run_trigger_audit(config)
    routing = run_routing_gap(config)

    routing_rates = [
        {
            "cue": str(row.get("cue", "")),
            "invoked_rate_pct": float(row.get("invoked_rate_pct", 0.0))
            if row.get("invoked_rate_pct") is not None
            else 0.0,
        }
        for row in routing
    ]

    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "root": config.root,
        "since": config.since,
        "skill_lines": skill_lines,
        "audit_counts": audit.get("counts", {}),
        "audit_rates": {
            k: float(v) for k, v in audit.get("rates", {}).items()
        },
        "routing_gap_rates": routing_rates,
        "recommendations": recommendations(skill_lines, audit, routing),
    }

    payload = json.dumps(report, indent=2, sort_keys=True) + "\n" if args.format == "json" else render_text(report)

    if args.output:
        output_path = Path(args.output).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
