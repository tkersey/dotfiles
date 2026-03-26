#!/usr/bin/env -S uv run --with pyyaml python
"""Run replay-distilled checks for codex/skills/tk."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[4]
DEFAULT_SUITE = ROOT / "codex/skills/tk/references/eval/replay-suite.yaml"


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
        raise SystemExit(f"suite must include non-empty cases list: {path}")
    return data


def nonempty_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.strip()]


def count_diff_blocks(text: str) -> int:
    return len(re.findall(r"```diff\n.*?\n```", text, re.DOTALL))


def parse_required_int(raw: Any, label: str) -> int:
    if raw is None:
        raise SystemExit(f"missing integer value for {label}")
    try:
        return int(raw)
    except (TypeError, ValueError) as exc:
        raise SystemExit(f"invalid integer value for {label}: {raw!r}") from exc


def validate_checks(checks: list[dict[str, Any]], case_id: str) -> None:
    supported = {
        "contains",
        "not_contains",
        "regex",
        "starts_with",
        "ordered_sections",
        "diff_block_count",
        "max_nonempty_lines",
    }
    for index, check in enumerate(checks, start=1):
        check_type = check.get("type")
        if check_type not in supported:
            raise SystemExit(
                f"case {case_id} has unsupported check type at index {index}: {check_type!r}"
            )


def check_case(output: str, checks: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for index, check in enumerate(checks, start=1):
        check_type = check.get("type")
        value = check.get("value")
        label = f"check[{index}] {check_type}"
        if check_type == "contains":
            if str(value) not in output:
                failures.append(f"{label}: missing {value!r}")
        elif check_type == "not_contains":
            if str(value) in output:
                failures.append(f"{label}: found forbidden text {value!r}")
        elif check_type == "regex":
            if not re.search(str(value), output, re.MULTILINE | re.IGNORECASE):
                failures.append(f"{label}: regex did not match {value!r}")
        elif check_type == "starts_with":
            if not output.lstrip().startswith(str(value)):
                failures.append(f"{label}: output does not start with {value!r}")
        elif check_type == "ordered_sections":
            cursor = 0
            for heading in value or []:
                idx = output.find(str(heading), cursor)
                if idx < 0:
                    failures.append(
                        f"{label}: missing or out-of-order heading {heading!r}"
                    )
                    break
                cursor = idx + len(str(heading))
        elif check_type == "diff_block_count":
            actual = count_diff_blocks(output)
            expected = parse_required_int(value, label)
            if actual != expected:
                failures.append(
                    f"{label}: expected {expected} diff block(s), got {actual}"
                )
        elif check_type == "max_nonempty_lines":
            actual = len(nonempty_lines(output))
            max_lines = parse_required_int(value, label)
            if actual > max_lines:
                failures.append(
                    f"{label}: expected <= {max_lines} non-empty lines, got {actual}"
                )
        else:
            failures.append(f"{label}: unsupported check type")
    return (not failures), failures


def run_codex(
    prompt: str, repo: Path, model: str | None, timeout_seconds: int, sandbox: str
) -> tuple[int, str, str, float]:
    with tempfile.TemporaryDirectory(prefix="tk-replay-") as tmpdir:
        output_path = Path(tmpdir) / "last_message.txt"
        cmd = [
            "codex",
            "exec",
            "--skip-git-repo-check",
            "--ephemeral",
            "--sandbox",
            sandbox,
            "--cd",
            str(repo),
            "--output-last-message",
            str(output_path),
            "-",
        ]
        if model:
            cmd.extend(["--model", model])

        started = time.monotonic()
        try:
            proc = subprocess.run(
                cmd,
                input=prompt,
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
            )
            elapsed = time.monotonic() - started
            output = (
                output_path.read_text(encoding="utf-8") if output_path.exists() else ""
            )
            return proc.returncode, output, proc.stderr, elapsed
        except subprocess.TimeoutExpired as exc:
            elapsed = time.monotonic() - started
            stderr = f"timed out after {timeout_seconds} seconds"
            if exc.stderr:
                stderr = f"{stderr}; stderr={exc.stderr}"
            output = (
                output_path.read_text(encoding="utf-8") if output_path.exists() else ""
            )
            return 124, output, stderr, elapsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run TK replay benchmark cases.")
    parser.add_argument(
        "--suite", default=str(DEFAULT_SUITE), help="Path to replay suite YAML"
    )
    parser.add_argument(
        "--repo", default=str(ROOT / "codex"), help="Repo root to use for codex exec"
    )
    parser.add_argument("--model", help="Explicit codex exec model")
    parser.add_argument(
        "--case",
        action="append",
        dest="case_ids",
        help="Run only matching case id (repeatable)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate suite shape without executing codex",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON results"
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        help="Override per-case timeout for all benchmark cases",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    suite_path = Path(args.suite).expanduser().resolve()
    repo = Path(args.repo).expanduser().resolve()
    suite = load_suite(suite_path)
    defaults = suite.get("defaults") or {}
    sandbox = str(defaults.get("sandbox", "read-only"))
    default_timeout = int(defaults.get("case_timeout_seconds", 90))

    cases = list(suite.get("cases") or [])
    if args.case_ids:
        wanted = set(args.case_ids)
        cases = [case for case in cases if str(case.get("id")) in wanted]
        if not cases:
            raise SystemExit(f"no suite cases matched --case values: {sorted(wanted)}")

    results: list[dict[str, Any]] = []
    for case in cases:
        case_id = str(case.get("id", "unknown"))
        prompt = str(case.get("prompt", "")).strip()
        checks = case.get("checks") or []
        if not prompt:
            raise SystemExit(f"case {case_id} missing prompt")
        if not isinstance(checks, list) or not checks:
            raise SystemExit(f"case {case_id} missing checks")
        validate_checks(checks, case_id)

        if args.dry_run:
            results.append({"id": case_id, "passed": True, "dry_run": True})
            continue

        timeout_seconds = (
            args.timeout_seconds
            if args.timeout_seconds is not None
            else parse_required_int(
                case.get("timeout_seconds", default_timeout),
                f"{case_id}.timeout_seconds",
            )
        )
        returncode, output, stderr, elapsed = run_codex(
            prompt,
            repo,
            args.model,
            timeout_seconds,
            sandbox,
        )
        passed, failures = check_case(output, checks)
        if returncode != 0:
            passed = False
            failures.append(
                f"codex exec returned {returncode}: {stderr.strip() or 'no stderr'}"
            )

        results.append(
            {
                "id": case_id,
                "passed": passed,
                "elapsed_seconds": round(elapsed, 2),
                "returncode": returncode,
                "failures": failures,
                "output_chars": len(output),
            }
        )

    total = len(results)
    passed_count = sum(1 for item in results if item.get("passed"))
    summary = {
        "suite": str(suite_path),
        "total": total,
        "passed": passed_count,
        "failed": total - passed_count,
        "pass_rate": 0.0 if total == 0 else round(passed_count / total, 3),
        "results": results,
    }

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(
            f"suite={suite_path} passed={passed_count}/{total} pass_rate={summary['pass_rate']:.3f}"
        )
        for item in results:
            status = "PASS" if item.get("passed") else "FAIL"
            print(f"- {status} {item['id']}")
            for failure in item.get("failures") or []:
                print(f"    - {failure}")

    return 0 if passed_count == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
