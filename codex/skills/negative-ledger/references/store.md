# Negative Ledger canonical operations

Use only after the entrypoint selects a canonical operation. This guide does not
change effect authority or activate capture/admission.

## Canonical Store and CLI

Load `$ledger` and complete `$ledger ensure` before the first native command.
Require Ledger 1.3.0 or newer within major version 1 and `ledger-artifact-abi/v1`.
Reuse unchanged readiness; recheck for changed executable/environment or selected
definition requirements.

```bash
negative_ledger_definition="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/negative-ledger/definitions/ledger/negative-evidence-protocol.json")"
```

Resolve the verified workspace through `$ledger`. Retain `store_root`, `store_id`,
`repository_id`, and `workspace_root`. Every canonical doctor, transaction, and
projection uses that managed selector, including memory admission. Only an
authorized first capture may initialize; reads cannot silently create a new
history. Legacy binding, rebinding, and cold adoption follow the Ledger skill's
exact maintenance policy, not per-worktree initialization or fallback readers.

Native surface:

```text
ledger definition check --definition DEFINITION
ledger transact --definition DEFINITION --operation capture|promote|transition|bind-existing|rebind-existing --store-root ROOT --store-id ID
ledger project --definition DEFINITION --projection current-records|route-gate|memory-note --store-root ROOT --store-id ID
ledger doctor --definition DEFINITION --store-root ROOT --store-id ID
```

`memory-note` is the authoritative admission payload. Never reconstruct it from
a summary projection. Do not use rebinding to select a divergent history or bless
an unknown replacement; preserve lineages for explicit owner reconciliation.

## Proof Lines

Canonical write:

```text
ledger-capture: neg_id=NEG-... status=active
ledger-status: neg_id=NEG-... status=stale
ledger-capture: not-attempted: evidence not durable enough
```

Memory admission:

```text
memory-note: id=MSN-... extension=negative-ledger kind=ledger-projection status=created
memory-note: not-attempted: ledger projection unavailable
memory-note: not-attempted: source admission gate not met
memory-note: not-attempted: cli unavailable
```

Report the layers separately.

