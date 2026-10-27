# Negative Ledger canonical operations

Use only after the entrypoint selects a canonical operation. This guide does not
change effect authority or activate capture/admission.

## Canonical Store and CLI

Load `$ledger` and complete its owner-specific bootstrap before the first native
command. Require Ledger 1.5.0 or newer within major version 1 and `ledger-artifact-abi/v1`:

```bash
ledger_skill_root="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/ledger")"
"$ledger_skill_root/scripts/ensure-ledger" --min-version 1.5.0
```

When installation is already authorized, add `--install` to that same command.
Candidate discovery composes the current keyed fold with native relevance and
sorting; earlier binaries cannot compile any projection in this definition.
Reuse unchanged readiness; recheck for changed executable/environment or selected
definition requirements.

```bash
negative_ledger_definition="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/negative-ledger/definitions/ledger/negative-evidence-protocol.json")"
```

On upgrade or selection of a changed definition, verify the complete definition
with `ledger definition check --definition "$negative_ledger_definition" --format json`.
A healthy store doctor does not establish projection compatibility. Reuse this
check while the definition and executable are unchanged.

Before the first canonical projection or capture, follow `$ledger`'s automatic
owner preparation for this definition. Retain its returned `store_root`,
`store_id`, and stable `repository_id`; `workspace_root` is optional provenance.
All canonical operations use that selector, including admission. Direct
`--store-id` selection requires no Git workspace; `--repo` can resolve a cataloged
workspace alias.

Explicit file/custody restrictions follow Ledger's read-only path; preparation
grants no new capture, lifecycle, or admission authority. Historical recovery
completeness does not gate access to an existing valid store. Ledger owns any
required custody maintenance.

Native surface:

```text
ledger definition check --definition DEFINITION
ledger transact --definition DEFINITION --operation capture|promote|transition|bind-existing|rebind-existing --store-root ROOT --store-id ID
ledger project --definition DEFINITION --projection current-records|route-candidates|route-gate|memory-note --store-root ROOT --store-id ID
ledger doctor --definition DEFINITION --store-root ROOT --store-id ID
```

`memory-note` is the authoritative admission payload. Never reconstruct it from
a summary projection. Do not use rebinding to select a divergent history or bless
an unknown replacement; preserve lineages for explicit owner reconciliation.

Capture requires `--param capture_key=<stable-operation-token>`; reuse the same
token, input bytes, and selector on transport retries. Native transaction results
already establish append validation and binding. Use doctor for a diagnosed
store problem or requested maintenance, not before and after every operation.
Keep identity qualified by store, owner, and `NEG-*`; numeric IDs alone are not
globally unique.

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

