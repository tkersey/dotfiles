#!/usr/bin/env -S uv run python
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shlex
import shutil
import subprocess
import sys
import textwrap
import time
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - user-environment dependent
    raise SystemExit(
        "PyYAML is required. Run with: uv run --with pyyaml codex/skills/saddle-up/scripts/saddle_up.py ..."
    ) from exc

DOC_EXTENSIONS = {".md", ".mdx", ".txt", ".rst", ".adoc"}
DEFAULT_BRANCH = "saddle-up/eval"
DEFAULT_THRESHOLD = 0.80
DEFAULT_STABILITY_WINDOW = 3
DEFAULT_STOP_FILE = ".saddle-up/STOP"
DEFAULT_SUITE_SIZE = 10
DEFAULT_OPENCODE_TIMEOUT_SECONDS = 180


class CommandError(RuntimeError):
    def __init__(self, cmd: list[str], returncode: int, stdout: str, stderr: str):
        super().__init__(
            f"command failed ({returncode}): {' '.join(shlex.quote(part) for part in cmd)}\n"
            f"stdout:\n{stdout}\n"
            f"stderr:\n{stderr}"
        )
        self.cmd = cmd
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def run_cmd(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=env,
        text=True,
        capture_output=True,
    )
    if check and proc.returncode != 0:
        raise CommandError(cmd, proc.returncode, proc.stdout, proc.stderr)
    return proc


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def iso_now() -> str:
    return utc_now().isoformat()


def stamp_now() -> str:
    return utc_now().strftime("%Y%m%dT%H%M%SZ")


def deep_copy(value: Any) -> Any:
    return json.loads(json.dumps(value))


def normalize_repo(repo: str) -> Path:
    path = Path(repo).expanduser().resolve()
    if not path.exists() or not path.is_dir():
        raise SystemExit(f"repo path not found: {path}")
    return path


def normalize_harness(repo: Path, harness_path: str) -> tuple[Path, str]:
    harness_input = Path(harness_path).expanduser()
    harness_abs = harness_input.resolve() if harness_input.is_absolute() else (repo / harness_input).resolve()
    if not harness_abs.exists():
        raise SystemExit(f"harness path not found: {harness_abs}")
    try:
        harness_rel = harness_abs.relative_to(repo).as_posix()
    except ValueError as exc:
        raise SystemExit(f"harness path must be inside repo: {harness_abs}") from exc
    return harness_abs, harness_rel


def resolve_stop_file(repo: Path, stop_file: str) -> Path:
    stop_path = Path(stop_file).expanduser()
    if not stop_path.is_absolute():
        stop_path = (repo / stop_path).resolve()
    return stop_path


def require_command(name: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(f"required command not found in PATH: {name}")


def ensure_git_repo(repo: Path) -> None:
    run_cmd(["git", "-C", str(repo), "rev-parse", "--is-inside-work-tree"], check=True)


def default_suite(harness_rel: str) -> dict[str, Any]:
    return {
        "version": 1,
        "mix": {"curated": 0.6, "replay": 0.4},
        "cases": [
            {
                "id": "curated-clarity",
                "source": "curated",
                "prompt": (
                    f"Read {harness_rel} and return the top 3 ambiguity risks with precise rewrite suggestions."
                ),
                "checks": [{"type": "min_chars", "value": 120}],
            },
            {
                "id": "curated-conflict",
                "source": "curated",
                "prompt": (
                    f"Given {harness_rel}, describe how conflicting instructions should fail-closed."
                ),
                "checks": [{"type": "min_chars", "value": 100}],
            },
            {
                "id": "curated-safety",
                "source": "curated",
                "prompt": (
                    f"Use {harness_rel} to outline regression safeguards for automated edits."
                ),
                "checks": [{"type": "min_chars", "value": 100}],
            },
        ],
    }


def default_scoring() -> dict[str, Any]:
    return {
        "version": 1,
        "threshold": DEFAULT_THRESHOLD,
        "pass_definition": "task_outcome_policy_no_critical_errors",
        "suite_size": DEFAULT_SUITE_SIZE,
        "critical_error_classes": [
            "contract violation",
            "unhandled exception",
            "traceback",
            "meshtruthfailed",
        ],
        "policy_forbidden_patterns": ["cannot comply", "ignored instructions"],
        "policy_required_patterns": [],
    }


def default_state() -> dict[str, Any]:
    return {
        "version": 1,
        "consecutive_passes": 0,
        "reliable": False,
        "cycle_count": 0,
        "continuous_session_id": None,
        "stop_reason": "none",
        "last_passing_commit": None,
        "last_run_at": None,
        "last_pass_rate": 0.0,
        "last_result": {
            "gate_passed": False,
            "regression_reverted": False,
            "failed_case_ids": [],
            "blocked_paths": [],
            "stop_reason": "none",
        },
    }


def ensure_contract_files(repo: Path, harness_rel: str) -> dict[str, Path]:
    saddle = repo / ".saddle-up"
    saddle.mkdir(parents=True, exist_ok=True)

    suite_path = saddle / "suite.yaml"
    scoring_path = saddle / "scoring.yaml"
    state_path = saddle / "state.yaml"
    runs_path = saddle / "runs.jsonl"

    if not suite_path.exists():
        save_yaml(suite_path, default_suite(harness_rel))
    if not scoring_path.exists():
        save_yaml(scoring_path, default_scoring())
    if not state_path.exists():
        save_yaml(state_path, default_state())
    if not runs_path.exists():
        runs_path.write_text("", encoding="utf-8")

    return {
        "saddle": saddle,
        "suite": suite_path,
        "scoring": scoring_path,
        "state": state_path,
        "runs": runs_path,
    }


def load_yaml(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return deep_copy(fallback)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return deep_copy(fallback)
    if not isinstance(data, dict):
        raise SystemExit(f"expected mapping in {path}")
    return data


def save_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, sort_keys=True) + "\n")


def parse_json_lines(text: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or not stripped.startswith("{"):
            continue
        try:
            value = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            out.append(value)
    return out


def flatten_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            out.extend(flatten_strings(item))
        return out
    if isinstance(value, dict):
        out: list[str] = []
        for key, item in value.items():
            if key in {"text", "content", "message", "delta", "output", "summary"}:
                out.extend(flatten_strings(item))
            else:
                out.extend(flatten_strings(item))
        return out
    return []


def extract_text_from_events(events: list[dict[str, Any]]) -> str:
    chunks: list[str] = []
    for event in events:
        for chunk in flatten_strings(event):
            chunk = chunk.strip()
            if chunk:
                chunks.append(chunk)
    return "\n".join(chunks)


def coerce_subprocess_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def run_opencode(
    repo: Path,
    model: str,
    message: str,
    *,
    timeout_seconds: int | None = None,
) -> dict[str, Any]:
    cmd = [
        "opencode",
        "run",
        "--model",
        model,
        "--dir",
        str(repo),
        "--format",
        "json",
        message,
    ]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(repo),
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = coerce_subprocess_text(exc.stdout)
        stderr = coerce_subprocess_text(exc.stderr)
        timeout_note = f"opencode timed out after {timeout_seconds}s"
        output_text = timeout_note
        combined = "\n".join(part for part in [stdout.strip(), stderr.strip()] if part).strip()
        if combined:
            output_text = f"{timeout_note}\n{combined}"
        return {
            "cmd": cmd,
            "returncode": 124,
            "events": parse_json_lines(stdout),
            "output_text": output_text,
            "stdout": stdout,
            "stderr": timeout_note if not stderr else f"{timeout_note}\n{stderr}",
            "timed_out": True,
        }

    events = parse_json_lines(proc.stdout)
    output_text = extract_text_from_events(events)
    if not output_text:
        output_text = (proc.stdout + "\n" + proc.stderr).strip()
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "events": events,
        "output_text": output_text,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "timed_out": False,
    }


def check_rule(rule: dict[str, Any], text: str) -> tuple[bool, str]:
    rule_type = str(rule.get("type", "")).strip().lower()
    value = rule.get("value")

    if rule_type == "contains":
        needle = str(value or "")
        passed = needle.lower() in text.lower()
        return passed, f"contains:{needle}"
    if rule_type == "not_contains":
        needle = str(value or "")
        passed = needle.lower() not in text.lower()
        return passed, f"not_contains:{needle}"
    if rule_type == "regex":
        pattern = str(value or "")
        passed = bool(re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE))
        return passed, f"regex:{pattern}"
    if rule_type == "min_chars":
        expected = int(value or 0)
        passed = len(text) >= expected
        return passed, f"min_chars:{expected}"

    return False, f"unknown_rule:{rule_type}"


def evaluate_case(
    case: dict[str, Any],
    result: dict[str, Any],
    scoring: dict[str, Any],
) -> dict[str, Any]:
    output_text = result["output_text"]
    checks = case.get("checks") or []

    check_statuses: list[dict[str, Any]] = []
    checks_passed = True
    for rule in checks:
        if not isinstance(rule, dict):
            checks_passed = False
            check_statuses.append({"rule": "invalid", "passed": False})
            continue
        passed, detail = check_rule(rule, output_text)
        check_statuses.append({"rule": detail, "passed": passed})
        if not passed:
            checks_passed = False

    output_lower = output_text.lower()

    forbidden = [str(item).lower() for item in scoring.get("policy_forbidden_patterns", []) if str(item).strip()]
    required = [str(item).lower() for item in scoring.get("policy_required_patterns", []) if str(item).strip()]
    critical = [str(item).lower() for item in scoring.get("critical_error_classes", []) if str(item).strip()]

    forbidden_hits = [pat for pat in forbidden if pat in output_lower]
    required_missing = [pat for pat in required if pat not in output_lower]
    critical_hits = [pat for pat in critical if pat in output_lower]

    returncode_ok = result["returncode"] == 0

    policy_ok = not forbidden_hits and not required_missing and not critical_hits
    task_ok = checks_passed
    passed = task_ok and policy_ok and returncode_ok

    reasons: list[str] = []
    if not task_ok:
        reasons.append("check-failed")
    if forbidden_hits:
        reasons.append(f"forbidden:{','.join(forbidden_hits)}")
    if required_missing:
        reasons.append(f"missing-required:{','.join(required_missing)}")
    if critical_hits:
        reasons.append(f"critical:{','.join(critical_hits)}")
    if not returncode_ok:
        reasons.append(f"returncode:{result['returncode']}")

    return {
        "id": case.get("id", "unknown"),
        "source": case.get("source", "unknown"),
        "passed": passed,
        "reasons": reasons,
        "check_statuses": check_statuses,
        "returncode": result["returncode"],
        "output_chars": len(output_text),
    }


def pick_suite_cases(suite: dict[str, Any], scoring: dict[str, Any]) -> list[dict[str, Any]]:
    cases = [item for item in suite.get("cases", []) if isinstance(item, dict)]
    if not cases:
        raise SystemExit("suite has no cases")

    mix = suite.get("mix") or {}
    curated_ratio = float(mix.get("curated", 0.6))
    replay_ratio = float(mix.get("replay", 0.4))
    total_ratio = curated_ratio + replay_ratio
    if total_ratio <= 0:
        curated_ratio = 0.6
        replay_ratio = 0.4
        total_ratio = 1.0
    curated_ratio /= total_ratio
    replay_ratio /= total_ratio

    target = int(scoring.get("suite_size", DEFAULT_SUITE_SIZE))
    target = max(1, min(target, len(cases)))

    curated = [case for case in cases if str(case.get("source", "")).lower() == "curated"]
    replay = [case for case in cases if str(case.get("source", "")).lower() == "replay"]

    curated_target = max(0, min(target, int(round(target * curated_ratio))))
    replay_target = max(0, target - curated_target)

    selected: list[dict[str, Any]] = []
    selected.extend(curated[:curated_target])
    selected.extend(replay[:replay_target])

    if len(selected) < target:
        used_ids = {str(item.get("id")) for item in selected}
        for candidate in curated + replay:
            case_id = str(candidate.get("id"))
            if case_id in used_ids:
                continue
            selected.append(candidate)
            used_ids.add(case_id)
            if len(selected) >= target:
                break

    return selected


def git_changed_paths(repo: Path) -> list[str]:
    proc = run_cmd(["git", "-C", str(repo), "status", "--porcelain"], check=True)
    paths: list[str] = []
    for raw_line in proc.stdout.splitlines():
        line = raw_line.rstrip("\n")
        if len(line) < 4:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        path = path.strip().strip('"')
        if path:
            paths.append(path)
    return paths


def is_docs_path(path: str, harness_rel: str) -> bool:
    if path == harness_rel:
        return True
    if path.startswith(".saddle-up/"):
        return True
    if path.startswith("docs/"):
        return True
    suffix = Path(path).suffix.lower()
    return suffix in DOC_EXTENSIONS


def docs_scope_violations(repo: Path, harness_rel: str) -> list[str]:
    changed = git_changed_paths(repo)
    return [path for path in changed if not is_docs_path(path, harness_rel)]


def ensure_branch(repo: Path, branch: str) -> None:
    current = run_cmd(["git", "-C", str(repo), "rev-parse", "--abbrev-ref", "HEAD"], check=True).stdout.strip()
    if current == branch:
        return
    exists = run_cmd(["git", "-C", str(repo), "branch", "--list", branch], check=True).stdout.strip()
    if exists:
        run_cmd(["git", "-C", str(repo), "switch", branch], check=True)
        return
    run_cmd(["git", "-C", str(repo), "switch", "-c", branch], check=True)


def stage_paths(repo: Path, paths: list[str]) -> None:
    if not paths:
        return
    run_cmd(["git", "-C", str(repo), "add", "--", *paths], check=True)


def has_staged_changes(repo: Path) -> bool:
    proc = run_cmd(["git", "-C", str(repo), "diff", "--cached", "--quiet"], check=False)
    return proc.returncode == 1


def commit(repo: Path, message: str) -> str:
    run_cmd(["git", "-C", str(repo), "commit", "-m", message], check=True)
    return run_cmd(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True).stdout.strip()


def default_branch(repo: Path) -> str:
    proc = run_cmd(
        ["git", "-C", str(repo), "symbolic-ref", "refs/remotes/origin/HEAD"],
        check=False,
    )
    if proc.returncode == 0:
        value = proc.stdout.strip()
        if value.startswith("refs/remotes/origin/"):
            return value.rsplit("/", 1)[-1]
    return "main"


def find_open_pr(repo: Path, branch: str) -> dict[str, Any] | None:
    if shutil.which("gh") is None:
        return None
    proc = run_cmd(
        ["gh", "pr", "list", "--state", "open", "--head", branch, "--json", "number,url", "--limit", "1"],
        cwd=repo,
        check=False,
    )
    if proc.returncode != 0:
        return None
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    if isinstance(payload, list) and payload:
        first = payload[0]
        if isinstance(first, dict):
            return first
    return None


def ensure_pr(repo: Path, branch: str, pass_rate: float) -> str | None:
    if shutil.which("gh") is None:
        return None

    pr = find_open_pr(repo, branch)
    body = textwrap.dedent(
        f"""
        saddle-up pass summary

        - branch: `{branch}`
        - pass_rate: `{pass_rate:.3f}`
        - threshold: `{DEFAULT_THRESHOLD:.2f}`
        - timestamp: `{iso_now()}`
        """
    ).strip()

    if pr and pr.get("number"):
        number = str(pr["number"])
        run_cmd(["gh", "pr", "comment", number, "--body", body], cwd=repo, check=False)
        return str(pr.get("url") or "") or None

    base = default_branch(repo)
    title = f"saddle-up: harness improvements ({stamp_now()})"
    proc = run_cmd(
        [
            "gh",
            "pr",
            "create",
            "--title",
            title,
            "--body",
            body,
            "--head",
            branch,
            "--base",
            base,
        ],
        cwd=repo,
        check=False,
    )
    if proc.returncode != 0:
        return None
    url = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    return url or None


def auto_revert_harness(repo: Path, harness_rel: str, commit_sha: str) -> str | None:
    restore = run_cmd(
        ["git", "-C", str(repo), "checkout", commit_sha, "--", harness_rel],
        check=False,
    )
    if restore.returncode != 0:
        return None

    stage_paths(repo, [harness_rel])
    if not has_staged_changes(repo):
        return None

    message = f"saddle-up: auto-revert harness to last passing commit {commit_sha[:12]}"
    return commit(repo, message)


def publish_diagnostics(
    repo: Path,
    branch: str,
    summary: str,
) -> str | None:
    if shutil.which("gh") is None:
        return None

    pr = find_open_pr(repo, branch)
    if pr and pr.get("number"):
        number = str(pr["number"])
        run_cmd(["gh", "pr", "comment", number, "--body", summary], cwd=repo, check=False)
        return str(pr.get("url") or "") or None

    issue_title = f"saddle-up diagnostics: {repo.name} ({stamp_now()})"
    proc = run_cmd(
        ["gh", "issue", "create", "--title", issue_title, "--body", summary],
        cwd=repo,
        check=False,
    )
    if proc.returncode != 0:
        return None
    ref = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    return ref or None


def build_improvement_prompt(harness_rel: str, failed_case_ids: list[str]) -> str:
    failed_suffix = ", ".join(failed_case_ids) if failed_case_ids else "none"
    return textwrap.dedent(
        f"""
        Improve `{harness_rel}` and related docs to make the harness more reliable for agentic development.

        Constraints:
        - Keep edits minimal and precise.
        - Edit docs only (`*.md`, `docs/`, `{harness_rel}`).
        - Do not modify source code files.
        - Preserve fail-closed safety behavior.

        Previously failing case ids: {failed_suffix}

        Return concise rationale for each change.
        """
    ).strip()


def evaluate_iteration(
    repo: Path,
    model: str,
    selected_cases: list[dict[str, Any]],
    scoring: dict[str, Any],
    *,
    timeout_seconds: int | None = None,
) -> tuple[list[dict[str, Any]], float]:
    case_results: list[dict[str, Any]] = []
    for case in selected_cases:
        prompt = str(case.get("prompt", "")).strip()
        if not prompt:
            case_results.append(
                {
                    "id": str(case.get("id", "unknown")),
                    "source": str(case.get("source", "unknown")),
                    "passed": False,
                    "reasons": ["missing-prompt"],
                    "check_statuses": [],
                    "returncode": 1,
                    "output_chars": 0,
                }
            )
            continue
        result = run_opencode(repo, model, prompt, timeout_seconds=timeout_seconds)
        case_results.append(evaluate_case(case, result, scoring))

    passed = sum(1 for result in case_results if result.get("passed"))
    total = max(1, len(case_results))
    pass_rate = passed / total
    return case_results, pass_rate


def run_loop(args: argparse.Namespace) -> int:
    repo = normalize_repo(args.repo)
    _, harness_rel = normalize_harness(repo, args.harness_path)
    stop_path = resolve_stop_file(repo, args.stop_file)
    timeout_seconds = int(args.opencode_timeout_seconds) if args.opencode_timeout_seconds else None
    if timeout_seconds is not None and timeout_seconds <= 0:
        raise SystemExit("--opencode-timeout-seconds must be > 0")
    max_cycles = int(args.max_cycles) if args.max_cycles else None
    if max_cycles is not None and max_cycles <= 0:
        raise SystemExit("--max-cycles must be > 0")

    require_command("git")
    require_command("opencode")
    ensure_git_repo(repo)

    paths = ensure_contract_files(repo, harness_rel)
    suite = load_yaml(paths["suite"], default_suite(harness_rel))
    scoring = load_yaml(paths["scoring"], default_scoring())
    state = load_yaml(paths["state"], default_state())

    threshold = float(args.threshold)
    scoring["threshold"] = threshold
    save_yaml(paths["scoring"], scoring)

    if not args.no_commit:
        ensure_branch(repo, args.branch)

    run_started = time.monotonic()
    continuous_session_id = stamp_now()
    reliable = bool(state.get("reliable", False))
    consecutive = int(state.get("consecutive_passes", 0))
    previous_gate = bool((state.get("last_result") or {}).get("gate_passed", False))
    failed_case_ids: list[str] = list((state.get("last_result") or {}).get("failed_case_ids", []))
    cycle_count = int(state.get("cycle_count", 0))
    stop_reason = "none"
    pending_error: CommandError | None = None

    try:
        while True:
            if stop_path.exists():
                stop_reason = "stop_file"
                print(f"stop_reason={stop_reason} stop_file={stop_path}")
                break

            cycle_count += 1
            selected_cases = pick_suite_cases(suite, scoring)

            improve_prompt = build_improvement_prompt(harness_rel, failed_case_ids)
            improve_result = run_opencode(repo, args.model, improve_prompt, timeout_seconds=timeout_seconds)

            case_results, pass_rate = evaluate_iteration(
                repo,
                args.model,
                selected_cases,
                scoring,
                timeout_seconds=timeout_seconds,
            )
            improve_failed = improve_result["returncode"] != 0
            gate_passed = pass_rate >= threshold and not improve_failed

            blocked_paths = docs_scope_violations(repo, harness_rel)
            if blocked_paths:
                gate_passed = False

            commit_sha: str | None = None
            pr_url: str | None = None
            regression_reverted = False

            if gate_passed:
                consecutive += 1
                if not args.no_commit:
                    changed_paths = git_changed_paths(repo)
                    if changed_paths:
                        stage_paths(repo, changed_paths)
                        if has_staged_changes(repo):
                            commit_sha = commit(
                                repo,
                                f"saddle-up: pass {pass_rate:.3f} cycle {cycle_count}",
                            )
                    if commit_sha:
                        state["last_passing_commit"] = commit_sha
                        pr_url = ensure_pr(repo, args.branch, pass_rate)
                    elif not state.get("last_passing_commit"):
                        state["last_passing_commit"] = run_cmd(
                            ["git", "-C", str(repo), "rev-parse", "HEAD"], check=True
                        ).stdout.strip()
            else:
                consecutive = 0
                if previous_gate and state.get("last_passing_commit") and not args.no_commit:
                    reverted_sha = auto_revert_harness(repo, harness_rel, str(state["last_passing_commit"]))
                    if reverted_sha:
                        regression_reverted = True
                        pr_url = ensure_pr(repo, args.branch, pass_rate)

            reliable = consecutive >= int(args.stability_window)
            failed_case_ids = [str(item.get("id")) for item in case_results if not item.get("passed")]
            if improve_failed:
                failed_case_ids = ["improve-step", *failed_case_ids]
            previous_gate = gate_passed

            cycle_stop_reason = "reliable_reached" if reliable else "none"
            run_id = f"{stamp_now()}-c{cycle_count:05d}"
            record = {
                "run_id": run_id,
                "continuous_session_id": continuous_session_id,
                "timestamp": iso_now(),
                "cycle": cycle_count,
                "model": args.model,
                "branch": args.branch,
                "threshold": threshold,
                "pass_rate": pass_rate,
                "gate_passed": gate_passed,
                "reliable": reliable,
                "consecutive_passes": consecutive,
                "failed_case_ids": failed_case_ids,
                "blocked_paths": blocked_paths,
                "improve_returncode": improve_result["returncode"],
                "improve_timed_out": bool(improve_result.get("timed_out")),
                "eval_total": len(case_results),
                "eval_passed": sum(1 for item in case_results if item.get("passed")),
                "commit_sha": commit_sha,
                "pr_url": pr_url,
                "regression_reverted": regression_reverted,
                "stop_reason": cycle_stop_reason,
                "elapsed_seconds": round(time.monotonic() - run_started, 2),
                "case_results": case_results,
            }
            append_jsonl(paths["runs"], record)

            state["consecutive_passes"] = consecutive
            state["reliable"] = reliable
            state["cycle_count"] = cycle_count
            state["continuous_session_id"] = continuous_session_id
            state["last_run_at"] = record["timestamp"]
            state["last_pass_rate"] = pass_rate
            state["stop_reason"] = cycle_stop_reason
            state["last_result"] = {
                "gate_passed": gate_passed,
                "regression_reverted": regression_reverted,
                "failed_case_ids": failed_case_ids,
                "blocked_paths": blocked_paths,
                "improve_returncode": improve_result["returncode"],
                "improve_timed_out": bool(improve_result.get("timed_out")),
                "run_id": run_id,
                "pr_url": pr_url,
                "stop_reason": cycle_stop_reason,
            }
            save_yaml(paths["state"], state)

            print(
                f"cycle={cycle_count} pass_rate={pass_rate:.3f} gate_passed={str(gate_passed).lower()} "
                f"consecutive={consecutive} reliable={str(reliable).lower()} "
                f"improve_returncode={improve_result['returncode']}"
            )

            if reliable:
                stop_reason = "reliable_reached"
                break
            if max_cycles is not None and cycle_count >= max_cycles:
                stop_reason = "max_cycles_reached"
                print(f"stop_reason={stop_reason} max_cycles={max_cycles}")
                break
    except KeyboardInterrupt:
        stop_reason = "interrupt"
        print(f"stop_reason={stop_reason}")
    except CommandError as err:
        stop_reason = "fatal_error"
        pending_error = err
    finally:
        state["consecutive_passes"] = consecutive
        state["reliable"] = reliable
        state["cycle_count"] = cycle_count
        state["continuous_session_id"] = continuous_session_id
        state["last_run_at"] = iso_now()
        state["stop_reason"] = stop_reason
        save_yaml(paths["state"], state)

    if pending_error:
        raise pending_error

    if stop_reason not in {"reliable_reached", "stop_file", "max_cycles_reached"}:
        summary = textwrap.dedent(
            f"""
            saddle-up diagnostics

            - repo: `{repo}`
            - harness: `{harness_rel}`
            - model: `{args.model}`
            - threshold: `{threshold:.2f}`
            - stability_window: `{args.stability_window}`
            - opencode_timeout_seconds: `{timeout_seconds if timeout_seconds is not None else 'none'}`
            - max_cycles: `{max_cycles if max_cycles is not None else 'unbounded'}`
            - stop_reason: `{stop_reason}`
            - cycles: `{cycle_count}`
            - latest_pass_rate: `{float(state.get('last_pass_rate', 0.0)):.3f}`
            - failed_case_ids: `{', '.join(failed_case_ids) if failed_case_ids else 'none'}`
            - blocked_paths: `{', '.join((state.get('last_result') or {}).get('blocked_paths', [])) or 'none'}`
            """
        ).strip()
        diag_ref = publish_diagnostics(repo, args.branch, summary)
        if diag_ref:
            print(f"diagnostics_ref={diag_ref}")

    if stop_reason in {"reliable_reached", "stop_file", "max_cycles_reached"}:
        return 0
    if stop_reason == "interrupt":
        return 130
    return 2


def load_runs(runs_path: Path, limit: int) -> list[dict[str, Any]]:
    if not runs_path.exists():
        return []
    lines = runs_path.read_text(encoding="utf-8").splitlines()
    selected = lines[-limit:] if limit > 0 else lines
    out: list[dict[str, Any]] = []
    for line in selected:
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            out.append(payload)
    return out


def run_status(args: argparse.Namespace) -> int:
    repo = normalize_repo(args.repo)
    paths = ensure_contract_files(repo, args.harness_path)

    state = load_yaml(paths["state"], default_state())
    runs = load_runs(paths["runs"], args.last)

    payload = {
        "repo": str(repo),
        "state": state,
        "recent_runs": runs,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def seq_replay_prompts(limit: int) -> list[str]:
    require_command("seq")
    proc = run_cmd(["seq", "opencode-prompts", "--limit", str(limit), "--format", "jsonl"], check=False)
    if proc.returncode != 0:
        raise SystemExit(f"failed to query seq opencode-prompts:\n{proc.stderr or proc.stdout}")

    prompts: list[str] = []
    seen: set[str] = set()
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        prompt_text = str(payload.get("prompt_text") or "").strip()
        if not prompt_text or prompt_text in seen:
            continue
        seen.add(prompt_text)
        prompts.append(prompt_text)
    return prompts


def run_replay_refresh(args: argparse.Namespace) -> int:
    repo = normalize_repo(args.repo)
    _, harness_rel = normalize_harness(repo, args.harness_path)
    paths = ensure_contract_files(repo, harness_rel)

    suite = load_yaml(paths["suite"], default_suite(harness_rel))
    scoring = load_yaml(paths["scoring"], default_scoring())

    target_size = int(scoring.get("suite_size", DEFAULT_SUITE_SIZE))
    target_size = max(1, target_size)

    mix = suite.get("mix") or {"curated": 0.6, "replay": 0.4}
    replay_ratio = float(mix.get("replay", 0.4))
    replay_target = max(1, int(round(target_size * replay_ratio)))

    prompts = seq_replay_prompts(max(replay_target * 3, 30))
    if not prompts:
        raise SystemExit("no replay prompts returned from seq opencode-prompts")

    curated_cases = [
        case
        for case in suite.get("cases", [])
        if isinstance(case, dict) and str(case.get("source", "")).lower() == "curated"
    ]

    replay_cases: list[dict[str, Any]] = []
    for idx, prompt in enumerate(prompts[:replay_target], start=1):
        replay_cases.append(
            {
                "id": f"replay-{idx:04d}",
                "source": "replay",
                "prompt": prompt,
                "checks": [{"type": "min_chars", "value": 80}],
            }
        )

    suite["cases"] = curated_cases + replay_cases
    save_yaml(paths["suite"], suite)

    print(
        "replay-refresh "
        f"curated={len(curated_cases)} replay={len(replay_cases)} total={len(suite['cases'])}"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Continuous harness eval loop for AGENTS.md-style instructions via OpenCode.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run continuous improve+eval loop")
    run_parser.add_argument("--repo", required=True, help="Target repository path")
    run_parser.add_argument("--harness-path", required=True, help="Harness path inside repo")
    run_parser.add_argument("--model", required=True, help="Model in provider/model format")
    run_parser.add_argument("--branch", default=DEFAULT_BRANCH, help="Eval branch")
    run_parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD, help="Pass threshold")
    run_parser.add_argument(
        "--stability-window",
        type=int,
        default=DEFAULT_STABILITY_WINDOW,
        help="Consecutive pass requirement",
    )
    run_parser.add_argument("--stop-file", default=DEFAULT_STOP_FILE, help="Stop-file path for graceful exit")
    run_parser.add_argument(
        "--opencode-timeout-seconds",
        type=int,
        default=DEFAULT_OPENCODE_TIMEOUT_SECONDS,
        help="Per-opencode-call timeout in seconds",
    )
    run_parser.add_argument("--max-cycles", type=int, help="Optional cap on completed cycles")
    run_parser.add_argument("--no-commit", action="store_true", help="Disable commit/PR/revert actions")
    run_parser.set_defaults(func=run_loop)

    status_parser = subparsers.add_parser("status", help="Show current state and recent runs")
    status_parser.add_argument("--repo", required=True, help="Target repository path")
    status_parser.add_argument("--harness-path", default="AGENTS.md", help="Harness path inside repo")
    status_parser.add_argument("--last", type=int, default=5, help="Recent run records to include")
    status_parser.set_defaults(func=run_status)

    replay_parser = subparsers.add_parser("replay-refresh", help="Refresh replay cases from seq/opencode history")
    replay_parser.add_argument("--repo", required=True, help="Target repository path")
    replay_parser.add_argument("--harness-path", default="AGENTS.md", help="Harness path inside repo")
    replay_parser.set_defaults(func=run_replay_refresh)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CommandError as err:
        print(str(err), file=sys.stderr)
        raise SystemExit(1)
