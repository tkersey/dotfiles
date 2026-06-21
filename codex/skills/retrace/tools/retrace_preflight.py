#!/usr/bin/env python3
"""Check installed native surfaces required by `$retrace`."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from typing import Any


def probe(binary: str, args: list[str]) -> dict[str, Any]:
    path = shutil.which(binary)
    if path is None:
        return {
            "binary": binary,
            "path": None,
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
        "supported": proc.returncode == 0,
        "exit_code": proc.returncode,
        "reason": "supported" if proc.returncode == 0 else "surface-unavailable",
        "output_preview": (proc.stdout or proc.stderr)[:500],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seq", default="seq")
    parser.add_argument("--cas", default="cas")
    parser.add_argument("--codex", default="codex")
    args = parser.parse_args()

    checks = {
        "seq_decision_capsule": probe(args.seq, ["decision-capsule", "--help"]),
        "cas_session_inquiry": probe(args.cas, ["session_inquiry", "--help"]),
        "codex_app_server": probe(args.codex, ["app-server", "--help"]),
    }
    missing = [name for name, row in checks.items() if not row["supported"]]
    result = {
        "retrace_preflight": {
            "verdict": "pass" if not missing else "missing-capabilities",
            "checks": checks,
            "missing": missing,
            "fork_execution_allowed": not missing,
            "deterministic_analysis_allowed": True,
            "specs": {
                "seq": "SEQ_DECISION_CAPSULE_CLI_SPEC.md",
                "cas": "CAS_SESSION_INQUIRY_CLI_SPEC.md",
            },
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not missing else 2


if __name__ == "__main__":
    raise SystemExit(main())
