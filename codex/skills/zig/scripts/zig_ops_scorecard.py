#!/usr/bin/env python3
"""Operational scorecard for $zig routing, Tiger Style, and semantic-family effectiveness."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any

FAMILIES = [
    "claim-binding",
    "lifetime-escape",
    "atomic-transition",
    "verifier-completeness",
    "repo-closure",
    "proof-context",
]

SAFE_CUES = {
    "cues": [
        {"name": "zig_build", "pattern": "zig build", "case_insensitive": True},
        {"name": "zig_test", "pattern": "zig test", "case_insensitive": True},
        {"name": "zig_fmt", "pattern": "zig fmt", "case_insensitive": True},
        {"name": "zig_fetch", "pattern": "zig fetch", "case_insensitive": True},
        {"name": "comptime", "pattern": "comptime", "case_insensitive": True},
        {"name": "cimport", "pattern": "@cimport", "case_insensitive": True},
        {"name": "extern_fn", "pattern": "extern fn", "case_insensitive": True},
        {"name": "compare_exchange", "pattern": "compareExchange", "case_insensitive": True},
        {"name": "tiger_style", "pattern": "ZTS-v1", "case_insensitive": True},
    ]
}


@dataclass
class Config:
    root: str
    since: str
    until: str | None


def run_cmd(command: list[str]) -> str:
    proc = subprocess.run(command, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "command failed")
    return proc.stdout


def run_trigger_audit(config: Config) -> dict[str, Any]:
    script = Path(__file__).with_name("zig_trigger_audit.py")
    command = [
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
    if config.until:
        command.extend(["--until", config.until])
    return json.loads(run_cmd(command))


def run_routing_gap(config: Config) -> tuple[list[dict[str, Any]], bool]:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=True) as handle:
        json.dump(SAFE_CUES, handle)
        handle.flush()
        base = [
            "seq",
            "routing-gap",
            "--root",
            config.root,
            "--cue-spec",
            f"@{handle.name}",
            "--discovery-skills",
            "zig",
            "--format",
            "json",
        ]
        command = [*base[:3], "--since", config.since, *base[3:]]
        if config.until:
            command = [*command[:5], "--until", config.until, *command[5:]]
        try:
            return json.loads(run_cmd(command)), True
        except (RuntimeError, json.JSONDecodeError):
            return json.loads(run_cmd(base)), False


def run_decision_audit(config: Config) -> dict[str, Any]:
    seq = shutil.which("seq")
    if not seq:
        return {"available": False, "reason": "seq-not-found"}
    probe = subprocess.run(
        [seq, "skill-decision-audit", "--help"],
        text=True,
        capture_output=True,
        check=False,
    )
    if probe.returncode != 0:
        return {"available": False, "reason": "skill-decision-audit-unavailable"}

    command = [
        seq,
        "skill-decision-audit",
        "--root",
        config.root,
        "--skill",
        "zig",
        "--since",
        config.since,
        "--exclude-current",
        "--mode",
        "tune-packet",
        "--format",
        "json",
    ]
    if config.until:
        command.extend(["--until", config.until])
    try:
        payload = json.loads(run_cmd(command))
        return {"available": True, "packet": payload}
    except (RuntimeError, json.JSONDecodeError) as exc:
        return {"available": False, "reason": f"decision-audit-failed:{exc}"}


def query_marker_rows(config: Config, marker: str) -> list[dict[str, Any]]:
    seq = shutil.which("seq")
    if not seq:
        return []
    spec = {
        "dataset": "messages",
        "where": [
            {"field": "role", "op": "eq", "value": "assistant"},
            {
                "field": "text",
                "op": "contains",
                "value": marker,
                "case_insensitive": True,
            },
        ],
        "select": ["path", "text", "timestamp"],
        "format": "jsonl",
    }
    command = [
        seq,
        "query",
        "--root",
        config.root,
        "--spec",
        json.dumps(spec),
        "--since",
        config.since,
    ]
    if config.until:
        command.extend(["--until", config.until])
    try:
        return [
            json.loads(line)
            for line in run_cmd(command).splitlines()
            if line.strip().startswith("{")
        ]
    except (RuntimeError, json.JSONDecodeError):
        return []


def query_route_sessions(config: Config) -> dict[str, Any]:
    rows = query_marker_rows(config, "zig_semantic_route")
    route_paths = {row.get("path") for row in rows if row.get("path")}
    family_sessions = {
        family: len(
            {
                row.get("path")
                for row in rows
                if row.get("path") and family in str(row.get("text", "")).lower()
            }
        )
        for family in FAMILIES
    }
    return {"route_sessions": len(route_paths), "family_sessions": family_sessions}


def query_tiger_style_sessions(config: Config) -> dict[str, Any]:
    rows = [
        *query_marker_rows(config, "zig_tiger_style"),
        *query_marker_rows(config, "ZTS-v1"),
    ]
    paths = {row.get("path") for row in rows if row.get("path")}
    exception_paths = {
        row.get("path")
        for row in rows
        if row.get("path") and "tiger-style: allow(" in str(row.get("text", "")).lower()
    }
    return {
        "contract_sessions": len(paths),
        "exception_sessions": len(exception_paths),
    }


def recommendations(
    skill_lines: int,
    trigger: dict[str, Any],
    routes: dict[str, Any],
    tiger_style: dict[str, Any],
    decision: dict[str, Any],
) -> list[str]:
    recs = []
    if skill_lines > 500:
        recs.append("Reduce codex/skills/zig/SKILL.md below 500 lines.")
    explicit_recall = float(trigger.get("rates", {}).get("explicit_session_recall_proxy_pct", 0.0))
    if explicit_recall < 70:
        recs.append("Improve explicit $zig activation handling.")
    opportunities = sum(
        int(row.get("opportunity_sessions", 0))
        for row in trigger.get("semantic_families", {}).values()
    )
    route_sessions = int(routes.get("route_sessions", 0))
    style_sessions = int(tiger_style.get("contract_sessions", 0))
    if opportunities and route_sessions == 0:
        recs.append("Semantic-family opportunities exist but no ZSR-v1 route artifacts were observed.")
    if route_sessions and style_sessions == 0:
        recs.append(
            "ZSR-v1 routes were observed but no ZTS-v1 Tiger Style contract evidence was observed; "
            "review material routes for boundedness and assertion proof."
        )
    if not decision.get("available"):
        recs.append(
            "Decision-effect evidence unavailable; activation and route artifacts cannot prove "
            "$zig changed decisions."
        )
    for family, row in trigger.get("semantic_families", {}).items():
        if int(row.get("opportunity_sessions", 0)) >= 3 and float(row.get("activation_rate_pct", 0.0)) < 50:
            recs.append(f"Strengthen contextual routing for {family}.")
    if not recs:
        recs.append("No immediate drift action required.")
    return recs


def render_text(report: dict[str, Any]) -> str:
    lines = [
        "zig_ops_scorecard",
        f"generated_at: {report['generated_at']}",
        f"root: {report['root']}",
        f"since: {report['since']}",
        f"until: {report['until'] or 'latest'}",
        f"skill_lines: {report['skill_lines']}",
        f"routing_gap_since_applied: {str(report['routing_gap_since_applied']).lower()}",
        f"decision_audit_available: {str(report['decision_audit']['available']).lower()}",
        f"semantic_route_sessions: {report['semantic_routes']['route_sessions']}",
        f"tiger_style_contract_sessions: {report['tiger_style']['contract_sessions']}",
        f"tiger_style_exception_sessions: {report['tiger_style']['exception_sessions']}",
        "semantic_families:",
    ]
    for family, row in sorted(report["trigger_audit"].get("semantic_families", {}).items()):
        lines.append(
            f"  {family}: opportunities={row['opportunity_sessions']} "
            f"activated={row['zig_activated_sessions']}"
        )
    lines.append("recommendations:")
    lines.extend(f"  - {item}" for item in report["recommendations"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path.home() / ".codex" / "sessions"))
    parser.add_argument("--since", required=True)
    parser.add_argument("--until")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    parser.add_argument("--output")
    args = parser.parse_args()

    config = Config(args.root, args.since, args.until)
    trigger = run_trigger_audit(config)
    routing, routing_since = run_routing_gap(config)
    decision = run_decision_audit(config)
    routes = query_route_sessions(config)
    tiger_style = query_tiger_style_sessions(config)
    skill_lines = sum(
        1
        for _ in (Path(__file__).resolve().parents[1] / "SKILL.md").open(
            encoding="utf-8"
        )
    )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": args.root,
        "since": args.since,
        "until": args.until,
        "skill_lines": skill_lines,
        "routing_gap_since_applied": routing_since,
        "routing_gap": routing,
        "trigger_audit": trigger,
        "semantic_routes": routes,
        "tiger_style": tiger_style,
        "decision_audit": decision,
    }
    report["recommendations"] = recommendations(
        skill_lines,
        trigger,
        routes,
        tiger_style,
        decision,
    )

    payload = (
        json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.format == "json"
        else render_text(report)
    )
    if args.output:
        path = Path(args.output).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
