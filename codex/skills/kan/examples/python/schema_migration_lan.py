#!/usr/bin/env python3
"""Schema migration witness: Σ/Lan-style pushforward with provenance."""
from dataclasses import dataclass

@dataclass(frozen=True)
class SourceRow:
    table: str
    id: int
    value: str

@dataclass(frozen=True)
class TargetRow:
    table: str
    id: int
    value: str
    provenance: str


def sigma_push(row: SourceRow) -> TargetRow:
    target_table = {"users": "accounts"}.get(row.table, row.table)
    return TargetRow(target_table, row.id, row.value, f"{row.table}:{row.id}")


def main() -> None:
    row = SourceRow("users", 1, "Ada")
    out = sigma_push(row)
    assert out.table == "accounts"
    assert out.provenance == "users:1"
    print("schema_migration_lan: ok")

if __name__ == "__main__":
    main()
