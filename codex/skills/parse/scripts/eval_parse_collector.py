#!/usr/bin/env -S uv run --with pyyaml python
"""Run fixture-based checks for the parse collector."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[4]
DEFAULT_SUITE = ROOT / "codex/skills/parse/references/eval/suite.yaml"
COLLECTOR = ROOT / "codex/skills/parse/scripts/collect_architecture_signals.py"


def load_suite(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"suite must be a mapping: {path}")
    if data.get("version") != 1:
        raise SystemExit(
            f"unsupported suite version in {path}: {data.get('version')!r}"
        )
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise SystemExit(f"suite must include a non-empty cases list: {path}")
    return data


def run_collector(repo_path: Path, focus_paths: list[str]) -> dict[str, Any]:
    cmd = [sys.executable, str(COLLECTOR), str(repo_path)]
    for focus_path in focus_paths:
        cmd.extend(["--focus-path", focus_path])
    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise SystemExit(
            "collector failed for "
            f"{repo_path}: rc={completed.returncode}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"collector emitted invalid JSON for {repo_path}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"collector payload must be a JSON object for {repo_path}")
    return payload


def top_signal(payload: dict[str, Any]) -> str | None:
    signals = payload.get("architecture_signals")
    if not isinstance(signals, list) or not signals:
        return None
    first = signals[0]
    if not isinstance(first, dict):
        return None
    name = first.get("name")
    return name if isinstance(name, str) else None


def repo_kind_names(payload: dict[str, Any]) -> list[str]:
    repo_kind_hints = payload.get("repo_kind_hints")
    if not isinstance(repo_kind_hints, list):
        return []
    names: list[str] = []
    for item in repo_kind_hints:
        if isinstance(item, dict):
            value = item.get("repo_kind")
            if isinstance(value, str):
                names.append(value)
    return names


def count_named_dicts(payload: dict[str, Any], key: str) -> int:
    value = payload.get(key)
    if not isinstance(value, list):
        return 0
    return sum(1 for item in value if isinstance(item, dict))


def find_focus_observation(
    payload: dict[str, Any], focus_path: str
) -> dict[str, Any] | None:
    observations = payload.get("focus_path_observations")
    if not isinstance(observations, list):
        return None
    for item in observations:
        if isinstance(item, dict) and item.get("path") == focus_path:
            return item
    return None


def normalize_text_list(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list) and all(isinstance(item, str) for item in raw):
        return list(raw)
    raise SystemExit(f"expected string or list[str], got {raw!r}")


def validate_case(case: dict[str, Any], payload: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    expected_repo_kind = case.get("expected_repo_kind")
    if isinstance(expected_repo_kind, str):
        kinds = repo_kind_names(payload)
        if expected_repo_kind not in kinds:
            failures.append(
                f"expected repo kind {expected_repo_kind!r}, got {kinds or ['<none>']}"
            )

    expected_top_signal = case.get("expected_top_signal")
    actual_top_signal = top_signal(payload)
    if (
        isinstance(expected_top_signal, str)
        and actual_top_signal != expected_top_signal
    ):
        failures.append(
            f"expected top signal {expected_top_signal!r}, got {actual_top_signal!r}"
        )

    for forbidden_signal in normalize_text_list(case.get("forbidden_top_signals")):
        if actual_top_signal == forbidden_signal:
            failures.append(
                f"forbidden top signal {forbidden_signal!r} became dominant"
            )

    docs_claim_regex = case.get("expected_docs_claim_regex")
    if isinstance(docs_claim_regex, str):
        docs_claims = payload.get("docs_claims")
        haystack_parts: list[str] = []
        if isinstance(docs_claims, list):
            for item in docs_claims:
                if isinstance(item, dict):
                    claim = item.get("claim")
                    if isinstance(claim, str):
                        haystack_parts.append(claim)
        haystack = "\n".join(haystack_parts)
        if not re.search(docs_claim_regex, haystack, re.IGNORECASE):
            failures.append(f"docs claim regex did not match: {docs_claim_regex!r}")

    for key in (
        "min_runtime_hint_count",
        "min_dependency_hint_count",
        "min_entrypoint_hint_count",
    ):
        minimum = case.get(key)
        if isinstance(minimum, int):
            payload_key = {
                "min_runtime_hint_count": "runtime_boundary_hints",
                "min_dependency_hint_count": "dependency_direction_hints",
                "min_entrypoint_hint_count": "entrypoint_hints",
            }[key]
            actual = count_named_dicts(payload, payload_key)
            if actual < minimum:
                failures.append(f"expected {payload_key} >= {minimum}, got {actual}")

    focus_expectations = case.get("focus_expectations")
    if isinstance(focus_expectations, list):
        for focus_case in focus_expectations:
            if not isinstance(focus_case, dict):
                failures.append("focus expectation must be a mapping")
                continue
            focus_path = focus_case.get("path")
            if not isinstance(focus_path, str):
                failures.append("focus expectation is missing a string path")
                continue
            observation = find_focus_observation(payload, focus_path)
            if observation is None:
                failures.append(f"missing focus observation for {focus_path!r}")
                continue
            expected_focus_top_signal = focus_case.get("expected_top_signal")
            if isinstance(expected_focus_top_signal, str):
                top_signals = observation.get("top_signals")
                actual_focus_signal = None
                if (
                    isinstance(top_signals, list)
                    and top_signals
                    and isinstance(top_signals[0], dict)
                ):
                    name = top_signals[0].get("name")
                    if isinstance(name, str):
                        actual_focus_signal = name
                if actual_focus_signal != expected_focus_top_signal:
                    failures.append(
                        f"focus path {focus_path!r} expected top signal {expected_focus_top_signal!r}, got {actual_focus_signal!r}"
                    )
            note_regex = focus_case.get("note_regex")
            if isinstance(note_regex, str):
                note = observation.get("note")
                if not isinstance(note, str) or not re.search(
                    note_regex, note, re.IGNORECASE
                ):
                    failures.append(
                        f"focus path {focus_path!r} note did not match regex {note_regex!r}"
                    )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the parse collector eval suite")
    parser.add_argument(
        "--suite", default=str(DEFAULT_SUITE), help="Path to the eval suite YAML"
    )
    args = parser.parse_args()

    suite_path = Path(args.suite).resolve()
    suite = load_suite(suite_path)
    suite_dir = suite_path.parent
    failures_found = False
    cases = suite["cases"]
    for case in cases:
        if not isinstance(case, dict):
            raise SystemExit(f"invalid case entry in {suite_path}: {case!r}")
        case_id = case.get("id")
        repo = case.get("repo")
        if not isinstance(case_id, str) or not isinstance(repo, str):
            raise SystemExit(f"case is missing string id or repo: {case!r}")
        repo_path = (suite_dir / repo).resolve()
        focus_paths = normalize_text_list(case.get("focus_paths"))
        payload = run_collector(repo_path, focus_paths)
        case_failures = validate_case(case, payload)
        actual_top_signal = top_signal(payload) or "<none>"
        actual_repo_kinds = ", ".join(repo_kind_names(payload)) or "<none>"
        if case_failures:
            failures_found = True
            print(
                f"FAIL {case_id}: top={actual_top_signal} repo_kinds={actual_repo_kinds}"
            )
            for failure in case_failures:
                print(f"  - {failure}")
        else:
            print(
                f"PASS {case_id}: top={actual_top_signal} repo_kinds={actual_repo_kinds}"
            )
    return 1 if failures_found else 0


if __name__ == "__main__":
    raise SystemExit(main())
