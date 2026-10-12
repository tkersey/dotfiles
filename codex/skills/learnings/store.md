# Canonical Store

## Canonical Store

Before the first native command, load `$ledger` and complete `$ledger ensure`.
Require Ledger 1.3.0 or newer within major version 1 and `ledger-artifact-abi/v1`.
The Ledger skill owns physical location, the personal catalog, initialization,
and legacy import. Do not derive a store from the current checkout or duplicate
its lookup/migration policy here.

Set the definition independently of the target workspace:

```bash
learnings_definition="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/learnings/definitions/ledger/learnings-protocol.json")"
```

Resolve the intended store through `$ledger`: `--store-id` works without Git;
`--repo` may resolve a cataloged workspace alias. Retain `store_root`, `store_id`,
and `repository_id`; `workspace_root` is optional provenance. All canonical operations
use `--store-root "<context.store_root>" --store-id "<context.store_id>"`.
Never use legacy `--repo` as a fallback after context failure.

Use `ledger transact --operation capture` for writes; use definition-bound
`record`, `recent`, `recall`, `search`, `reconciliation-index`, and `memory-note`
projections for reads. The definition's `events` logical slot is canonical;
`lrn-*` returned by Ledger is the canonical record identity.

Retired-source recovery uses the explicit [historical import](retired-import.md)
maintenance route. It preserves original identities and record fields through
`import-record`; ordinary new writes continue to use `capture`.

Normal context resolution is read-only and does not scan historical worktrees.
A first capture can initialize only an explicitly requested new store. Legacy
import/adoption is separate maintenance, never a prerequisite for access to an
existing valid store. Existing native binding failures still require owner repair;
do not change selectors, bind each new worktree, or hand-edit source records.

Rows preserve `id`, `captured_at`, `status`, `learning`, `evidence`, `application`,
`source`, `fingerprint`, `context`, `tags`, `related_ids`, and `supersedes_id`.
For new captures, `context.repo` uses the resolved stable `repository_id`;
`context.branch`, paths, and evidence describe the actual workspace/artifact.
Old provenance is historical evidence and is not rewritten during adoption.

Standalone recall, browse, and source-local capture remain Learnings operations.
No aggregate coordinator or sibling fan-out is required. When evidence changes a
reusable decision, evaluate the capture gate and retain the source-owned
disposition. A no-op does not require initialization.
