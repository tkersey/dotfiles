---
name: ledger
description: "Operate Ledger for owner-defined artifact validation, materialization, personal custody, migration, and recovery. Use for runtime bootstrap, passive definitions, stable store selection, or explicit historical import; not merely because work creates history or a receipt."
---

# Ledger

## Mission

Provide the shared bootstrap, storage-context policy, and operating doctrine for
Ledger 1.3.0 or newer within major version 1: a bounded, deterministic
artifact-protocol runtime driven by passive definitions owned by their domains.

```text
owner definition + explicit inputs + selected custody when needed
-> bounded compiled plan
-> definition-relative validity
-> canonical identity
-> declared custody effect or exact projection
-> structural or custodial receipt
```

Ledger is constructive and custodial. It can admit artifacts into a declared
protocol world and preserve that world's identity, integrity, transitions,
replay, and projections. It does not choose the world.

## Authority boundary

The native engine enforces machine-checkable semantics declared by the selected
owner definition. It does not choose a definition, operation, projection,
parameter, repair, architecture, next action, or authoritative history. It does
not discover Git state, sessions, memory roots, or network facts, and does not
grant mutation, publication, review, delivery, or closure authority.

The caller owns definition selection, input construction, semantic
interpretation, and workflow actions. This skill's explicit context helper
resolves a personal catalog by stable store identity or an explicit workspace
association; it is not
hidden discovery inside a passive definition or the native engine.

A successful result remains definition-relative. It does not establish that the
owner selected the right protocol, that an exclusion applies, or that a later
action is authorized.

## Bootstrap boundary

Before the first native Ledger command, complete `$ledger ensure` once. Reuse
readiness while the resolved executable and execution environment are unchanged;
recheck when either changes. `$ledger` is skill syntax, not a shell command.

```bash
ledger_skill_root="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/ledger")"
"$ledger_skill_root/scripts/ensure-ledger"
```

After `ledger-bootstrap-ready/v1`, invoke the native CLI directly. The handler
requires Ledger 1.3.0 or newer within major version 1 and
`ledger-artifact-abi/v1`. It can install or upgrade `tkersey/tap/ledger` only when
user-level provisioning is authorized. Otherwise stop with its remediation.
Never use an alternate implementation, `curl | sh`, an unpinned download, or
installation during an active repository effect. It does not proxy commands.

Readiness is not compatibility with every definition. Use `definition check`
when selecting a new/changed closure or diagnosing operator support, not as a
redundant preflight for every unchanged operation.

## Select the operation

Choose from the semantic owner's request before loading custody procedures.
Bootstrap remains required before the first native command; reuse established
readiness only while the executable and execution environment are unchanged.

| Selected work | Required guidance |
|---|---|
| Pure `validate`, `materialize`, or definition inspection | This entrypoint and the owner's exact definition/inputs; no workspace, managed store, or migration scan. |
| Canonical store read/write, `doctor`, projection, transaction, or managed-context resolution | [canonical-custody.md](references/canonical-custody.md) for the personal catalog and native selector. Historical import completeness does not gate normal access. |
| Binding, legacy migration, or exact recovery | Canonical custody guidance and the maintenance/migration reference it selects before the effect; availability never grants authority. |
| Author or debug a passive definition | [definition-authoring.md](references/definition-authoring.md); add custody guidance only if a store operation is selected. |

Never load storage manuals or initialize a store for a pure operation. Conversely,
calling a canonical projection an inspection does not waive custody checks.
Read-only recall cannot silently initialize or migrate. Only owners select
semantic scope; other worktree/session data is not silently relocated.

## Baseline native surface

```text
ledger definition check
ledger definition describe
ledger validate
ledger materialize
ledger transact
ledger project
ledger doctor
ledger recovery inspect
ledger recovery reclaim
ledger capabilities
ledger version
```

Do not invent aliases such as `ledger state`. Load the owner for exact definition
paths, operations, projections, and parameters. Version-dependent maintenance is
in [storage-maintenance.md](references/storage-maintenance.md); availability does
not authorize use. Legacy `--repo` remains an explicit unmanaged filesystem-root
selector for authorized maintenance and owners that have not selected managed
scope. It is never a fallback for managed histories.

## Result semantics

- `definition check` validates a closure for its required ABI/operators;
  `definition describe` exposes its compiled surface, not semantic approval.
- `validate` checks explicit inputs without repository storage; `materialize`
  also derives the canonical representation and identity without storage effects.
- `transact` performs only selected declared effects and returns custody receipts.
- `project` reads/replays selected declared stores and emits the exact projection.
- `doctor` validates binding, integrity, replay, and definition-relative health.
- `recovery inspect` witnesses one exact transaction; `recovery reclaim` performs
  only an authorized transaction-bound reclaim after all witness checks.

Preserve normal result envelopes, closure digests, and input/artifact/store
identities. Definition ID and ABI alone do not identify the exact law checked.
Do not apply a prior result to changed inputs, closure, or store state, reduce it
to an unqualified "valid," invent metadata, or introduce substitute receipts.
Retain the separate context identity when interpreting a managed-store result.
A root-selection error establishes no claim about the unseen source contents.

Use `--payload-only` only for an explicit structural pipe whose receiver owns
interpretation; never imply that the omitted envelope is still present.

## Definition ownership

Passive definitions live beside semantic owners and are listed in their
`definitions/manifest.json`, not here. They are JSON, not hooks, commands,
executables, network calls, or hidden discovery procedures. Owners declare
logical slots; they cannot choose absolute output paths or escape the selected
control root. Do not hardcode domain artifact families or closure policy into
the native engine.

Prefer pure validation/materialization unless durable identity/history is
needed. Before authoring or debugging definitions, read
[definition-authoring.md](references/definition-authoring.md) for bounded
vocabulary, counterexample discipline, and the native extension law.

## Storage-context ownership

This skill alone owns physical storage-location and migration policy. Read
[canonical-custody.md](references/canonical-custody.md#storage-context-ownership)
before resolving or operating on canonical custody. Do not duplicate its policy
in consumers or `AGENTS.md`, or substitute an empty store for a failed lookup.

## Resolve personal custody

Resolve an existing store by `--store-id` or its cataloged workspace association.
Normal `ensure_custody.py` performs the same read-only lookup. Missing worktrees,
unresolved legacy imports, and absent migration receipts do not invalidate owned
custody. Read [explicit adoption and migration](references/canonical-custody.md#explicit-adoption-and-migration)
only when that maintenance is selected. A missing or corrupt established root
still fails closed; it is never replaced with an empty store.

## Storage custody and recovery

Read [custody and recovery](references/canonical-custody.md#storage-custody-and-recovery)
before binding or recovery. No hand-edited records, broad reclaim, or automatic
permission transfer from lease expiry.

## Trigger cues and reporting

Use for explicit `$ledger`/`$ledger ensure`, a consumer's first native command,
runtime/ABI availability, personal storage context, worktree continuity, definition
authoring, validation/materialization, durable transactions/projections, binding,
legacy migration, and exact recovery. Do not trigger merely because work creates
history or a receipt; the semantic owner selects the protocol.

Report the actual operation, selected definition/closure/ABI, result schema and
verdict, storage mutation, exact addressed source/transaction when relevant, and
remaining owner action. Missing metadata limits the claim. Keep pure validation,
transactions, doctor, context failures, and recovery outcomes distinct rather
than forcing them into one generic status template.
