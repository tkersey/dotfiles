type SourceRow = { table: "users"; id: number; name: string };
type TargetRow = { table: "accounts"; id: number; displayName: string; provenance: string };
export function sigma(row: SourceRow): TargetRow {
  return { table: "accounts", id: row.id, displayName: row.name, provenance: `users:${row.id}` };
}
