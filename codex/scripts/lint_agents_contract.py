#!/usr/bin/env -S uv run python
from __future__ import annotations

import argparse
from pathlib import Path
import sys


REQUIRED_MARKERS = [
    "## Response Format",
    "Echo:",
    "final assistant response only",
    "# Local Codex orchestration guidance",
    "thread/start",
    "`wait` is not a join",
    "Omit the ledger when no orchestration ran.",
]

FORBIDDEN_MARKERS = [
    "Execution substrate: use `$mesh` and execute a streaming per-unit state machine via `spawn_agents_on_csv` rolling batches by default.",
    "Mesh invocation gate (fail-closed)",
    "Orchestration Ledger response rendering (required when orchestration ran):",
]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed if AGENTS.md loses restored response-format anchors or revives obsolete mesh-default guidance."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="codex/AGENTS.md",
        help="Path to the AGENTS file to validate.",
    )
    args = parser.parse_args()

    path = Path(args.path)
    if not path.is_file():
        print(f"[FAIL] Missing file: {path}")
        return 1

    text = path.read_text()

    missing = [marker for marker in REQUIRED_MARKERS if marker not in text]
    forbidden = [marker for marker in FORBIDDEN_MARKERS if marker in text]

    if missing:
        print("[FAIL] Missing required markers:")
        for marker in missing:
            print(f"  - {marker}")

    if forbidden:
        print("[FAIL] Found forbidden markers:")
        for marker in forbidden:
            print(f"  - {marker}")

    if missing or forbidden:
        return 1

    print(f"[OK] {path} preserves the restored response-format and native-routing contract.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
