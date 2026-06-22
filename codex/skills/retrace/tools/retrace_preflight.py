#!/usr/bin/env python3
"""Check installed seq/CAS replay surfaces required by `$retrace`."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from typing import Any


def run(binary: str, args: list[str]) -> dict[str, Any]:
    path = shutil.which(binary)
    if path is None:
        return {
            "binary": binary,
            "path": None,
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "supported": False,
            "reason": "binary-not-found",
        }
    proc = subprocess.run(
        [path, *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "binary": binary,
        "path": path,
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "supported": proc.returncode == 0,
        "reason": "supported" if proc.returncode == 0 else "surface-unavailable",
    }


def parse_version(text: str) -> tuple[int, int, int] | None:
    match = re.search(r"(?<!\d)(\d+)\.(\d+)\.(\d+)(?!\d)", text)
    if not match:
        return None
    return tuple(int(value) for value in match.groups())


def json_value(row: dict[str, Any]) -> Any:
    text = row.get("stdout") or row.get("stderr") or ""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def has_truthy_key(value: Any, names: set[str]) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in names and child is True:
                return True
            if has_truthy_key(child, names):
                return True
    elif isinstance(value, list):
        return any(has_truthy_key(child, names) for child in value)
    return False


def key_value(value: Any, names: set[str]) -> Any:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in names:
                return child
        for child in value.values():
            found = key_value(child, names)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = key_value(child, names)
            if found is not None:
                return found
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seq", default="seq")
    parser.add_argument("--cas", default="cas")
    parser.add_argument("--codex", default="codex")
    parser.add_argument("--minimum-seq", default="0.3.5")
    parser.add_argument("--minimum-cas", default="0.2.40")
    args = parser.parse_args()

    seq_version_row = run(args.seq, ["--version"])
    cas_version_row = run(args.cas, ["--version"])
    seq_caps_row = run(args.seq, ["capabilities", "--format", "json"])
    cas_caps_row = run(args.cas, ["capabilities", "--json"])
    cas_inquiry_row = run(args.cas, ["session_inquiry", "preflight", "--json"])
    codex_row = run(args.codex, ["app-server", "--help"])

    seq_version = parse_version(seq_version_row["stdout"] + seq_version_row["stderr"])
    cas_version = parse_version(cas_version_row["stdout"] + cas_version_row["stderr"])
    minimum_seq = parse_version(args.minimum_seq)
    minimum_cas = parse_version(args.minimum_cas)

    seq_caps = json_value(seq_caps_row)
    cas_caps = json_value(cas_caps_row)
    inquiry = json_value(cas_inquiry_row)

    checks = {
        "seq_version": {
            "value": ".".join(map(str, seq_version)) if seq_version else None,
            "minimum": args.minimum_seq,
            "supported": bool(seq_version and minimum_seq and seq_version >= minimum_seq),
        },
        "cas_version": {
            "value": ".".join(map(str, cas_version)) if cas_version else None,
            "minimum": args.minimum_cas,
            "supported": bool(cas_version and minimum_cas and cas_version >= minimum_cas),
        },
        "seq_decision_capsule_v1": {
            "supported": has_truthy_key(seq_caps, {"decision_capsule_v1"}),
        },
        "seq_dcp_validation_v1": {
            "supported": has_truthy_key(seq_caps, {"dcp_validation_v1"}),
        },
        "cas_session_inquiry_v1": {
            "supported": has_truthy_key(cas_caps, {"session_inquiry_v1"}),
        },
        "cas_fir_v1": {
            "supported": has_truthy_key(cas_caps, {"fir_v1"}),
        },
        "cas_thread_fork_replay": {
            "supported": bool(
                key_value(inquiry, {"thread_fork_replay", "exact_fork_rollback_anchor"})
            ),
        },
        "cas_rollout_transcript_replay": {
            "supported": bool(key_value(inquiry, {"rollout_transcript_replay"})),
        },
        "cas_inquiry_allowed": {
            "supported": bool(key_value(inquiry, {"inquiry_allowed"})),
        },
        "codex_app_server": {
            "supported": codex_row["supported"],
        },
    }

    seq_ready = all(
        checks[name]["supported"]
        for name in (
            "seq_version",
            "seq_decision_capsule_v1",
            "seq_dcp_validation_v1",
        )
    )
    cas_base_ready = all(
        checks[name]["supported"]
        for name in (
            "cas_version",
            "cas_session_inquiry_v1",
            "cas_fir_v1",
            "cas_inquiry_allowed",
            "codex_app_server",
        )
    )
    replay_modes = []
    if cas_base_ready and checks["cas_thread_fork_replay"]["supported"]:
        replay_modes.append("thread_fork")
    if cas_base_ready and checks["cas_rollout_transcript_replay"]["supported"]:
        replay_modes.append("rollout_transcript")

    missing = [name for name, row in checks.items() if not row["supported"]]
    result = {
        "retrace_preflight": {
            "verdict": "pass" if seq_ready and replay_modes else "missing-capabilities",
            "checks": checks,
            "seq_ready": seq_ready,
            "cas_base_ready": cas_base_ready,
            "replay_modes": replay_modes,
            "fork_execution_allowed": bool(seq_ready and replay_modes),
            "deterministic_analysis_allowed": seq_ready,
            "missing": missing,
            "raw": {
                "seq_version": seq_version_row["path"],
                "cas_version": cas_version_row["path"],
                "seq_capabilities_exit": seq_caps_row["exit_code"],
                "cas_capabilities_exit": cas_caps_row["exit_code"],
                "cas_inquiry_preflight_exit": cas_inquiry_row["exit_code"],
            },
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["retrace_preflight"]["verdict"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
