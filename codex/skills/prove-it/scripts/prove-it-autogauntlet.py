#!/usr/bin/env python3
"""
Host driver for the prove-it skill.

This script makes prove-it host-driven instead of prompt-only:
- starts a prove-it run from a claim,
- executes exactly 10 separate Codex CLI turns,
- resumes the same conversation for turns 2-10,
- validates one numbered round per assistant reply,
- rejects early proof/disproof/final-verdict/Oracle-synthesis output.

It intentionally has no "run one round", "step", "pause", or "resume N rounds"
mode. A normal invocation either completes all 10 turns or exits non-zero.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from typing import Sequence


DRIVER_ID = "PROVE_IT_AUTOTURN_V1"
EXPECTED_TURNS = 10

ROUND_FOCUS = {
    1: "Counterexamples",
    2: "Logic traps",
    3: "Boundary cases",
    4: "Adversarial inputs",
    5: "Alternative paradigms",
    6: "Operational constraints",
    7: "Probabilistic uncertainty",
    8: "Comparative baselines",
    9: "Meta-test",
    10: "Oracle synthesis",
}

INITIAL_PROMPT_TEMPLATE = """\
Driver: {driver_id}

Use the prove-it skill on the following claim.

Host-driver contract:
- This is a host-driven Auto Gauntlet run.
- Execute exactly Round 1 only in this assistant turn.
- Do not execute rounds 2-10 in this reply.
- Do not ask whether to continue.
- Do not pause for user input.
- Do not return a final verdict before round 10.
- Do not stop for proof, disproof, counterexample, contradiction, confidence, likely failure, or user-requested cadence changes.
- Preserve a checkpoint.
- The host driver will automatically continue until exactly 10 separate assistant turns have completed.

Claim:
{claim}
"""

RESUME_PROMPT = f"""\
Driver: {DRIVER_ID}

Continue prove-it from the checkpoint.
Execute exactly the next uncompleted numbered round only.
Do not execute more than one round in this reply.
Do not ask whether to continue.
Do not pause for user input.
Do not return a final verdict unless executing round 10.
Do not stop for proof, disproof, counterexample, contradiction, confidence, likely failure, or user-requested cadence changes.
If the checkpoint is already complete at 10 of 10, report completion and do not run another round.
"""

ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
ROUND_HEADING_RE = re.compile(
    r"(?mi)^\s{0,3}(?:#{1,6}\s*)?Round\s+(\d+)\s*[—-]\s*(.*?)\s*$"
)
COMPLETED_ENGINE_TURNS_RE = re.compile(
    r"(?mi)^\s*completed[_ ]engine[_ ]turns:\s*(\d+)\s*of\s*10\b"
)
COMPLETED_ROUND_RE = re.compile(r"(?mi)^\s*Completed round:\s*(\d+)\s*$")
STATUS_RE = re.compile(r"(?mi)^\s*Status:\s*([A-Z_ ]+)\s*$")
VERDICT_EMBARGO_RE = re.compile(r"(?mi)^\s*Verdict embargo:\s*([A-Z_0-9 ]+)\s*$")
STOP_REASON_RE = re.compile(r"(?mi)^\s*Stop reason:\s*([A-Z_0-9 ]+)\s*$")
ACTION_RE = re.compile(r"(?mi)^\s*Action:\s*([A-Z_0-9]+)\s*$")
NEXT_ROUND_RE = re.compile(r"(?mi)^\s*next[_ ]round:\s*(.+?)\s*$")

FINAL_VERDICT_RE = re.compile(r"(?mi)^\s*Final verdict\s*:")
ORACLE_SYNTHESIS_RE = re.compile(r"(?mi)^\s*Oracle synthesis\s*:")
AUTO_GAUNTLET_CONTROL_RE = re.compile(r"(?mi)^\s*Auto Gauntlet Control\s*:")
LEGACY_TERMINALITY_RE = re.compile(r"(?mi)^\s*Terminality Check\s*:")
LEGACY_TERMINAL_VERDICT_RE = re.compile(r"(?mi)^\s*Terminal verdict\s*:")
STOP_CONCLUSIVE_RE = re.compile(r"(?mi)^\s*Action:\s*STOP_CONCLUSIVE_PROOF\s*$")
GENERIC_STOP_ACTION_RE = re.compile(r"(?mi)^\s*Action:\s*STOP\s*$")


@dataclass
class Validation:
    expected_turn: int
    round_heading: int | None
    completed_engine_turns: int | None
    completed_round: int | None
    status: str | None
    verdict_embargo: str | None
    stop_reason: str | None
    action: str | None
    next_round: str | None
    errors: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass
class TurnRecord:
    turn: int
    prompt_file: str
    output_file: str
    command: list[str]
    returncode: int
    validation: dict


def strip_ansi(value: str) -> str:
    return ANSI_RE.sub("", value)


def normalize_label(value: str | None) -> str | None:
    if value is None:
        return None
    return re.sub(r"\s+", " ", value.replace("_", " ").strip().upper())


def last_int(pattern: re.Pattern[str], text: str) -> int | None:
    values = [int(match.group(1)) for match in pattern.finditer(text)]
    return values[-1] if values else None


def last_text(pattern: re.Pattern[str], text: str) -> str | None:
    values = [match.group(1).strip() for match in pattern.finditer(text)]
    return values[-1] if values else None


def parse_round_headings(text: str) -> list[tuple[int, str]]:
    return [(int(match.group(1)), match.group(2).strip()) for match in ROUND_HEADING_RE.finditer(text)]


def validate_turn(raw_text: str, expected_turn: int) -> Validation:
    text = strip_ansi(raw_text)
    errors: list[str] = []

    headings = parse_round_headings(text)
    heading_num: int | None = None
    if len(headings) != 1:
        errors.append(
            f"expected exactly one top-level round heading, found {len(headings)}: {headings!r}"
        )
    else:
        heading_num = headings[0][0]
        if heading_num != expected_turn:
            errors.append(f"expected round heading {expected_turn}, found {heading_num}")

    completed_engine_turns = last_int(COMPLETED_ENGINE_TURNS_RE, text)
    if completed_engine_turns is None:
        errors.append("missing `Completed engine turns: N of 10`")
    elif completed_engine_turns != expected_turn:
        errors.append(
            f"expected `Completed engine turns: {expected_turn} of 10`, "
            f"found {completed_engine_turns} of 10"
        )

    completed_round = last_int(COMPLETED_ROUND_RE, text)
    if completed_round is None:
        errors.append("missing `Completed round: N` checkpoint field")
    elif completed_round != expected_turn:
        errors.append(f"expected `Completed round: {expected_turn}`, found {completed_round}")

    status = normalize_label(last_text(STATUS_RE, text))
    verdict_embargo = normalize_label(last_text(VERDICT_EMBARGO_RE, text))
    stop_reason = normalize_label(last_text(STOP_REASON_RE, text))
    action = normalize_label(last_text(ACTION_RE, text))
    next_round = last_text(NEXT_ROUND_RE, text)

    if LEGACY_TERMINALITY_RE.search(text):
        errors.append("legacy `Terminality Check` output is not allowed")
    if LEGACY_TERMINAL_VERDICT_RE.search(text):
        errors.append("legacy `Terminal verdict` output is not allowed")
    if STOP_CONCLUSIVE_RE.search(text):
        errors.append("early conclusive-proof stop is not allowed")
    if GENERIC_STOP_ACTION_RE.search(text):
        errors.append("generic `Action: STOP` is not allowed")

    if expected_turn < EXPECTED_TURNS:
        if status != "IN PROGRESS":
            errors.append(f"turn {expected_turn} must be `Status: IN PROGRESS`, found {status!r}")
        if verdict_embargo != "ACTIVE":
            errors.append(
                f"turn {expected_turn} must keep `Verdict embargo: ACTIVE`, "
                f"found {verdict_embargo!r}"
            )
        if FINAL_VERDICT_RE.search(text):
            errors.append("final verdict appeared before round 10")
        if ORACLE_SYNTHESIS_RE.search(text):
            errors.append("Oracle synthesis appeared before round 10")
        if stop_reason and stop_reason not in {"NONE", ""}:
            errors.append(f"non-terminal turn must have `Stop reason: none`, found {stop_reason!r}")

        expected_next = expected_turn + 1
        accepted_actions = {
            f"CONTINUE TO ROUND {expected_next}",
            f"AUTO CONTINUE TO ROUND {expected_next}",
        }
        if action not in accepted_actions:
            errors.append(
                f"turn {expected_turn} must continue to round {expected_next}; "
                f"found action {action!r}"
            )

        if not next_round:
            errors.append("missing `Next round` field")
        elif not re.search(rf"\b{expected_next}\b", next_round):
            errors.append(f"expected next round {expected_next}, found {next_round!r}")

    else:
        if status != "COMPLETE":
            errors.append(f"round 10 must set `Status: COMPLETE`, found {status!r}")
        if verdict_embargo != "LIFTED BY ROUND 10":
            errors.append(
                "round 10 must set `Verdict embargo: LIFTED_BY_ROUND_10`, "
                f"found {verdict_embargo!r}"
            )
        if stop_reason != "ROUND 10 COMPLETE":
            errors.append(
                "round 10 must set `Stop reason: ROUND_10_COMPLETE`, "
                f"found {stop_reason!r}"
            )
        if not ORACLE_SYNTHESIS_RE.search(text):
            errors.append("round 10 must include `Oracle synthesis:`")
        if not FINAL_VERDICT_RE.search(text):
            errors.append("round 10 must include `Final verdict:`")
        if AUTO_GAUNTLET_CONTROL_RE.search(text):
            errors.append("terminal round must not include `Auto Gauntlet Control`")
        if next_round and normalize_label(next_round) != "NONE":
            errors.append(f"round 10 must set `Next round: none`, found {next_round!r}")

    return Validation(
        expected_turn=expected_turn,
        round_heading=heading_num,
        completed_engine_turns=completed_engine_turns,
        completed_round=completed_round,
        status=status,
        verdict_embargo=verdict_embargo,
        stop_reason=stop_reason,
        action=action,
        next_round=next_round,
        errors=errors,
    )


class RunLock:
    def __init__(self, lock_dir: Path):
        self.lock_dir = lock_dir

    def __enter__(self) -> "RunLock":
        try:
            self.lock_dir.mkdir()
        except FileExistsError as exc:
            raise RuntimeError(
                f"prove-it run lock already exists: {self.lock_dir}\n"
                "Another run may be active. Remove the lock only if you are sure it is stale."
            ) from exc
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        shutil.rmtree(self.lock_dir, ignore_errors=True)


def run_command(command: Sequence[str], cwd: Path | None, timeout_seconds: int | None) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            list(command),
            cwd=str(cwd) if cwd else None,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout_seconds if timeout_seconds and timeout_seconds > 0 else None,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode(errors="replace")
        return 124, output + f"\n[TIMEOUT after {timeout_seconds} seconds]\n"

    return completed.returncode, completed.stdout


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def resolve_claim(args: argparse.Namespace) -> str:
    sources = 0
    claim_parts: list[str] = []

    if args.claim_file:
        sources += 1
        claim_parts.append(Path(args.claim_file).read_text(encoding="utf-8").strip())

    if args.claim:
        sources += 1
        claim_parts.append(" ".join(args.claim).strip())

    if not sys.stdin.isatty():
        stdin_claim = sys.stdin.read().strip()
        if stdin_claim:
            sources += 1
            claim_parts.append(stdin_claim)

    if sources == 0:
        raise SystemExit("error: provide a claim as arguments, via --claim-file, or on stdin")
    if sources > 1:
        raise SystemExit("error: provide the claim from exactly one source")

    claim = claim_parts[0].strip()
    if not claim:
        raise SystemExit("error: claim is empty")
    return claim


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the prove-it skill as exactly 10 separate Codex turns. "
            "No step, pause, one-round, or incremental mode is provided."
        )
    )
    parser.add_argument(
        "claim",
        nargs="*",
        help="claim to stress-test; omit when piping claim on stdin or using --claim-file",
    )
    parser.add_argument(
        "--claim-file",
        help="read the claim from a UTF-8 text file",
    )
    parser.add_argument(
        "--codex-bin",
        default=os.environ.get("CODEX_BIN", "codex"),
        help="Codex CLI binary to execute, default: %(default)s",
    )
    parser.add_argument(
        "--cwd",
        default=None,
        help="working directory for Codex CLI commands, default: current directory",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="directory for prompts, outputs, and manifest; default: .prove-it-runs/run-<timestamp>",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=0,
        help="per-turn timeout; 0 means no timeout",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    claim = resolve_claim(args)
    cwd = Path(args.cwd).resolve() if args.cwd else None

    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%SZ")
    out_dir = Path(args.out_dir or f".prove-it-runs/run-{timestamp}").resolve()
    lock_dir = out_dir.parent / ".prove-it-autogauntlet.lock"

    manifest: dict[str, object] = {
        "driver": DRIVER_ID,
        "expected_turns": EXPECTED_TURNS,
        "claim": claim,
        "started_at": timestamp,
        "cwd": str(cwd) if cwd else None,
        "out_dir": str(out_dir),
        "turns": [],
        "status": "IN_PROGRESS",
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    write_text(out_dir / "claim.txt", claim)

    try:
        with RunLock(lock_dir):
            for turn in range(1, EXPECTED_TURNS + 1):
                if turn == 1:
                    prompt = INITIAL_PROMPT_TEMPLATE.format(driver_id=DRIVER_ID, claim=claim)
                    command = [args.codex_bin, "exec", prompt]
                else:
                    prompt = RESUME_PROMPT
                    command = [args.codex_bin, "exec", "resume", "--last", prompt]

                prompt_file = out_dir / f"prompt-{turn:02d}.txt"
                output_file = out_dir / f"turn-{turn:02d}.txt"
                write_text(prompt_file, prompt)

                print(f"\n=== prove-it host turn {turn}/10: {ROUND_FOCUS[turn]} ===", flush=True)
                if turn == 1:
                    print(f"$ {args.codex_bin} exec <prompt>", flush=True)
                else:
                    print(f"$ {args.codex_bin} exec resume --last <prompt>", flush=True)

                returncode, output = run_command(command, cwd, args.timeout_seconds)
                write_text(output_file, output)
                print(output, end="" if output.endswith("\n") else "\n", flush=True)

                validation = validate_turn(output, turn)
                record = TurnRecord(
                    turn=turn,
                    prompt_file=str(prompt_file),
                    output_file=str(output_file),
                    command=command[:2] + (["resume", "--last"] if turn > 1 else []) + ["<prompt>"],
                    returncode=returncode,
                    validation=asdict(validation),
                )
                manifest["turns"].append(asdict(record))
                write_text(out_dir / "manifest.json", json.dumps(manifest, indent=2))

                if returncode != 0:
                    manifest["status"] = "CODEX_COMMAND_FAILED"
                    manifest["failed_turn"] = turn
                    write_text(out_dir / "manifest.json", json.dumps(manifest, indent=2))
                    print(f"\nERROR: Codex command failed on turn {turn} with exit code {returncode}", file=sys.stderr)
                    print(f"Artifacts: {out_dir}", file=sys.stderr)
                    return 1

                if not validation.ok:
                    manifest["status"] = "VALIDATION_FAILED"
                    manifest["failed_turn"] = turn
                    manifest["validation_errors"] = validation.errors
                    write_text(out_dir / "manifest.json", json.dumps(manifest, indent=2))
                    print(f"\nERROR: prove-it output failed host-driver validation on turn {turn}", file=sys.stderr)
                    for error in validation.errors:
                        print(f"- {error}", file=sys.stderr)
                    print(f"Artifacts: {out_dir}", file=sys.stderr)
                    return 2

            manifest["status"] = "COMPLETE"
            manifest["completed_at"] = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%SZ")
            write_text(out_dir / "manifest.json", json.dumps(manifest, indent=2))
            print(f"\nSUCCESS: prove-it completed exactly 10 separate turns. Artifacts: {out_dir}")
            return 0

    except RuntimeError as exc:
        manifest["status"] = "LOCK_FAILED"
        manifest["error"] = str(exc)
        write_text(out_dir / "manifest.json", json.dumps(manifest, indent=2))
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
