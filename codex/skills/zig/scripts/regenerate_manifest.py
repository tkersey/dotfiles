#!/usr/bin/env python3
"""Regenerate MANIFEST.files and MANIFEST.sha256 for the installed Zig skill."""

from __future__ import annotations

import hashlib
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    files = [
        path
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
        and path.name not in {"MANIFEST.files", "MANIFEST.sha256"}
    ]

    relative = [path.relative_to(root).as_posix() for path in files]
    manifest_files = ["MANIFEST.files", "MANIFEST.sha256", *relative]
    (root / "MANIFEST.files").write_text(
        "\n".join(manifest_files) + "\n",
        encoding="utf-8",
    )

    rows = []
    for name in manifest_files:
        path = root / name
        if path.name == "MANIFEST.sha256":
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append(f"{digest}  {name}")
    (root / "MANIFEST.sha256").write_text(
        "\n".join(rows) + "\n",
        encoding="utf-8",
    )

    print(f"manifest_files={len(manifest_files)} hashes={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
