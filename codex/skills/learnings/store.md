# Canonical Store

## Canonical Store

Before the first native Ledger command in this workflow, load `$ledger` and
complete `$ledger ensure`. Require Ledger 1.0.3 or newer within major version 1
and `ledger-artifact-abi/v1`.
Set:

```bash
learnings_definition="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/learnings/definitions/ledger/learnings-protocol.json")"
```

Use `ledger transact --operation capture` for writes; use definition-bound
`record`, `recent`, `recall`, `search`, `reconciliation-index`, and
`memory-note` projections for reads. Treat the returned `lrn-*` identity as
canonical. Do not open or hand-edit the store. An unbound current-format store
requires the explicit one-shot `bind-existing` transaction. When an
authoritative external transport such as Git advances the valid store while a
local binding remains stale, use the separate `rebind-existing` transaction.
Both routes validate the complete current store and otherwise fail closed;
there is no alternate-path reader.

Rows should preserve `id`, `captured_at`, `status`, `learning`, `evidence`, `application`, `source`, `fingerprint`, `context`, `tags`, `related_ids`, and `supersedes_id`.

Standalone recall, browse, and source-local capture remain Learnings operations.
No aggregate coordinator or sibling fan-out is required. At a material
execution boundary, evaluate the capture gate directly and retain the
source-owned disposition.
