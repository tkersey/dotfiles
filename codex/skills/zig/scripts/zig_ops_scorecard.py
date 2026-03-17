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
        # Keep routing-gap cues compatible with seq's current regex-like matcher;
        # dotted literals are audited separately in zig_trigger_audit.py.
        {"name": "zig_build", "pattern": "zig build", "case_insensitive": True},
        {"name": "zig_lint", "pattern": "zig build lint", "case_insensitive": True},
        {"name": "zlinter", "pattern": "zlinter", "case_insensitive": True},
        {"name": "zig_test", "pattern": "zig test", "case_insensitive": True},
        {"name": "zig_run", "pattern": "zig run", "case_insensitive": True},
        {"name": "zig_fmt", "pattern": "zig fmt", "case_insensitive": True},
        {"name": "zig_fetch", "pattern": "zig fetch", "case_insensitive": True},
        {"name": "comptime", "pattern": "comptime", "case_insensitive": True},
        {"name": "vector", "pattern": "@vector", "case_insensitive": True},
        {"name": "cimport", "pattern": "@cimport", "case_insensitive": True},
        {"name": "extern_fn", "pattern": "extern fn", "case_insensitive": True},
        {
            "name": "link_system_library",
            "pattern": "linkSystemLibrary",
            "case_insensitive": True,
        },
        {"name": "link_libc", "pattern": "linkLibC", "case_insensitive": True},
        {
            "name": "compare_exchange",
            "pattern": "compareExchange",
            "case_insensitive": True,
        },
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


def run_routing_gap(config: ScorecardConfig) -> tuple[list[dict[str, Any]], bool]:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=True) as tmp:
        json.dump(SAFE_CUES, tmp)
        tmp.flush()
        cmd = [
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
        try:
            out = run_cmd(cmd)
            return json.loads(out), True
        except RuntimeError as err:
            if "option --since is not supported" not in str(err):
                raise
        except json.JSONDecodeError:
            pass
        fallback_cmd = [
            "seq",
            "routing-gap",
            "--root",
            config.root,
            "--cue-spec",
            f"@{tmp.name}",
            "--discovery-skills",
            "zig",
            "--format",
            "json",
        ]
        out = run_cmd(fallback_cmd)
    return json.loads(out), False


def cue_rate(by_cue: dict[str, dict[str, Any]], name: str) -> float | None:
    row = by_cue.get(name)
    if row is None:
        return None
    value = row.get("invoked_rate_pct")
    return float(value) if value is not None else 0.0


def cue_has_hits(by_cue: dict[str, dict[str, Any]], name: str) -> bool:
    row = by_cue.get(name)
    if row is None:
        return False
    value = row.get("cue_sessions")
    return int(value) > 0 if value is not None else True


def recommendations(
    skill_lines: int, audit: dict[str, Any], routing: list[dict[str, Any]]
) -> list[str]:
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
        recs.append(
            "Improve explicit $zig handling: audit misses where user asked for $zig but assistant did not invoke it."
        )

    by_cue = {str(row.get("cue", "")): row for row in routing}
    zig_build = by_cue.get("zig_build")
    if zig_build:
        rate = cue_rate(by_cue, "zig_build") or 0.0
        if rate < 50.0:
            recs.append(
                "Strengthen frontmatter cues for zig build workflows; current zig_build invoked rate is below 50%."
            )
    zig_lint = by_cue.get("zig_lint")
    if zig_lint:
        rate = cue_rate(by_cue, "zig_lint") or 0.0
        if rate < 50.0:
            recs.append(
                "Strengthen lint trigger cues; current zig_lint invoked rate is below 50%."
            )

    if cue_has_hits(by_cue, "zig_fetch"):
        zig_fetch_rate = cue_rate(by_cue, "zig_fetch") or 0.0
        if zig_fetch_rate < 50.0:
            recs.append(
                "Strengthen dependency/provenance trigger cues; current zig_fetch invoked rate is below 50%."
            )

    ffi_cues = ("extern_fn", "link_system_library", "link_libc")
    if any(
        cue_has_hits(by_cue, name) and (cue_rate(by_cue, name) or 0.0) < 50.0
        for name in ffi_cues
    ):
        recs.append(
            "Strengthen FFI boundary trigger cues; one or more extern/linker cues invoke $zig below 50%."
        )

    concurrency_cues = ("compare_exchange",)
    if any(
        cue_has_hits(by_cue, name) and (cue_rate(by_cue, name) or 0.0) < 50.0
        for name in concurrency_cues
    ):
        recs.append(
            "Strengthen concurrency/atomics trigger cues; one or more atomic cues invoke $zig below 50%."
        )

    overall = by_cue.get("__all__")
    if overall:
        rate = cue_rate(by_cue, "__all__") or 0.0
        if rate < 30.0:
            recs.append(
                "Review trigger surface with seq routing-gap; overall invoked rate is below 30%."
            )

    if not recs:
        recs.append("No immediate drift action required.")
    return recs


def render_text(report: dict[str, Any]) -> str:
    lines = [
        "zig_ops_scorecard",
        f"generated_at: {report['generated_at']}",
        f"root: {report['root']}",
        f"since: {report['since']}",
        f"routing_gap_since_applied: {str(report['routing_gap_since_applied']).lower()}",
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
    parser = argparse.ArgumentParser(
        description="Generate a drift scorecard for the zig skill."
    )
    parser.add_argument(
        "--root", default=str(Path.home() / ".codex" / "sessions"), help="Sessions root"
    )
    parser.add_argument(
        "--since", required=True, help="Inclusive ISO timestamp lower bound"
    )
    parser.add_argument("--format", choices=("json", "text"), default="text")
    parser.add_argument("--output", default=None, help="Optional output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = ScorecardConfig(root=args.root, since=args.since)

    skill_path = Path(__file__).resolve().parents[1] / "SKILL.md"
    skill_lines = sum(1 for _ in skill_path.open("r", encoding="utf-8"))

    audit = run_trigger_audit(config)
    routing, routing_gap_since_applied = run_routing_gap(config)

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
        "routing_gap_since_applied": routing_gap_since_applied,
        "skill_lines": skill_lines,
        "audit_counts": audit.get("counts", {}),
        "audit_rates": {k: float(v) for k, v in audit.get("rates", {}).items()},
        "routing_gap_rates": routing_rates,
        "recommendations": recommendations(skill_lines, audit, routing),
    }

    payload = (
        json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.format == "json"
        else render_text(report)
    )

    if args.output:
        output_path = Path(args.output).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
