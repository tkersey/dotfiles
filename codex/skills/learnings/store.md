# Canonical Store

## Canonical Store

Before the first native command, load `$ledger` and complete `$ledger ensure`.
Require Ledger 1.3.0 or newer within major version 1 and `ledger-artifact-abi/v1`.
The Ledger skill owns physical location, worktree-family registration,
initialization, and cold adoption. Do not derive a store from the current checkout
or duplicate its lookup/migration policy here.

Set the definition independently of the target workspace:

```bash
learnings_definition="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/learnings/definitions/ledger/learnings-protocol.json")"
```

Resolve the verified workspace through `$ledger` and retain `store_root`,
`store_id`, `repository_id`, and `workspace_root`. All native canonical operations
use `--store-root "<context.store_root>" --store-id "<context.store_id>"`.
Never use legacy `--repo` as a fallback after context failure.

Use `ledger transact --operation capture` for writes; use definition-bound
`record`, `recent`, `recall`, `search`, `reconciliation-index`, and `memory-note`
projections for reads. The definition's `events` logical slot is canonical;
`lrn-*` returned by Ledger is the canonical record identity.

Normal context resolution is read-only. A first capture can initialize only with
authority and the Ledger skill's legacy-coverage checks. Existing unbound/stale
custody requires that skill's exact authorized maintenance, not binding each new
worktree. Never open, hand-edit, skip, or reinterpret source records.

Rows preserve `id`, `captured_at`, `status`, `learning`, `evidence`, `application`,
`source`, `fingerprint`, `context`, `tags`, `related_ids`, and `supersedes_id`.
For new captures, `context.repo` uses the resolved stable `repository_id`;
`context.branch`, paths, and evidence describe the actual workspace/artifact.
Old provenance is historical evidence and is not rewritten during adoption.

Standalone recall, browse, and source-local capture remain Learnings operations.
No aggregate coordinator or sibling fan-out is required. At a material execution
boundary, evaluate the capture gate directly and retain the source-owned
disposition. A no-op does not require storage initialization.
