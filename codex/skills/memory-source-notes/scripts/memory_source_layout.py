#!/usr/bin/env -S uv run python
"""Inspect or copy controlled extension instructions into the selected native layout."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from memory_layout import LayoutError, copy_instructions, ensure_no_symlink_components, resolve_layout

EXTENSIONS = ("learnings", "negative-ledger", "synesthesia")


def instruction_status(layout, source: Path) -> dict:
    path = layout.instructions_path
    try:
        ensure_no_symlink_components(path)
        if not path.exists():
            return {"status": "missing", "path": str(path)}
        if not path.is_file():
            return {"status": "not-file", "path": str(path)}
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        expected = hashlib.sha256(source.read_bytes()).hexdigest() if source.is_file() else None
        return {"status": "current" if actual == expected else "drifted" if expected else "source-unavailable",
                "path": str(path), "actual_sha256": actual, "expected_sha256": expected}
    except (OSError, LayoutError) as exc:
        return {"status": "unavailable", "path": str(path), "error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("doctor", "sync-instructions"))
    parser.add_argument("--extension", action="append", choices=EXTENSIONS)
    parser.add_argument("--repo", default=".", help="Effective Codex config context; no Git lookup")
    parser.add_argument("--codex-home")
    parser.add_argument("--memory-version", choices=("v1", "v2"))
    parser.add_argument("--memory-note-bin")
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[3] / "memories/extensions")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()
    reports = {}
    pinned_home, pinned_version = args.codex_home, args.memory_version
    for extension in args.extension or EXTENSIONS:
        try:
            layout = resolve_layout(extension, codex_home=pinned_home, memory_version=pinned_version,
                                    memory_note_bin=args.memory_note_bin, cwd=Path(args.repo).expanduser().absolute())
            pinned_home, pinned_version = layout.codex_home, layout.memory_version
            source = args.source_root / extension / "instructions.md"
            result = copy_instructions(layout, source) if args.command == "sync-instructions" else instruction_status(layout, source)
            reports[extension] = {"layout": layout.as_dict(), "instructions": result}
        except (OSError, LayoutError) as exc:
            reports[extension] = {"error": str(exc)}
    report = {"schema": "memory-source-layout/v1", "command": args.command,
              "read_only": args.command == "doctor", "extensions": reports}
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for extension, item in reports.items():
            if "error" in item:
                print(f"{extension}\tunavailable\t{item['error']}")
            else:
                instructions = item["instructions"]
                print(f"{extension}\t{instructions['status']}\t{item['layout']['instructions_path']}")
    return 2 if any("error" in item or item["instructions"]["status"] not in {"current", "copied"} for item in reports.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
