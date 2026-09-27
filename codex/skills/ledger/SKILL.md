---
name: ledger
description: "Ensure Ledger 1.3.0 or newer within major version 1 is available; resolve durable repository/worktree-family custody; and use the passive-definition runtime to validate, canonicalize, materialize, transact, replay, project, doctor, bind, rebind, and recover owner-defined artifacts and stores. This skill owns storage-location policy. The semantic owner selects the definition and operation; Ledger enforces it without acquiring workflow authority."
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
resolves the caller-selected Git workspace and storage registration; it is not
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

## Storage-context ownership

This skill, its [context reference](references/storage-context.md), and
[scripts/ledger_context.py](scripts/ledger_context.py) are the single source of
truth for where Ledger-managed evidence lives. Do not duplicate physical roots,
lookup rules, registration, or migration policy in `AGENTS.md` or consumers.
Owners still declare logical slot names and semantic storage scope.

Repository-lifetime Learnings and Negative Ledger histories use one managed
custody root for a Git repository/worktree family. A worktree is evidence
provenance, not the owner of an independent history. Other owners opt into this
scope explicitly; do not silently relocate worktree- or session-specific data.
Pure validation/materialization needs neither a workspace nor a managed store.

For a canonical operation, resolve the verified workspace:

```bash
uv run "$ledger_skill_root/scripts/ledger_context.py" --repo "<workspace-root>"
```

Retain the returned `workspace_root`, `repository_id`, `store_id`, `store_root`,
and `native_args`. For normal durable operations, pass the returned selector:

```bash
ledger doctor --definition "$definition" \
  --store-root "<context.store_root>" --store-id "<context.store_id>" --format json
```

`transact`, `project`, segmented migration, and exact recovery use the same
selector. Resolve again after a workspace change; the native CLI rechecks the
root marker on each operation. Never replace a failed managed selector with
`--repo`, another checkout, a symlink, or an empty store.

Normal context resolution is read-only. An authorized first capture may use
`--initialize`; the helper checks all registered worktrees for legacy history
before publishing a fresh registration. Existing registration always wins over
changed environment defaults. A missing established root is a continuity error,
not first use. Legacy adoption is separate, explicit maintenance described in
the context reference. Do not initialize simply to make a recall succeed.

Use workspace/branch/path and immutable artifact facts as provenance. New
repository-scoped records should carry the returned stable `repository_id`
where their owner schema supports it. Do not substitute the custody directory
for the code workspace, rewrite old provenance, or broaden applicability because
history is shared. Definition-relative source locators are resolved through this
context, not by assuming they name files beneath a disposable checkout.

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

## Storage custody and recovery

All event bytes and required binding/definition/revision custody stay together
under the selected root. Normal reads fail closed for unbound existing stores.
A separately authorized `bind-existing` operation validates an entire existing
current-format store once. A separately authorized `rebind-existing` validates
an authoritative replacement and changes only stale binding metadata.
Neither operation chooses between divergent histories or blesses an unknown
replacement. Diagnose missing binding separately from malformed/stale custody;
`InvalidStoreBinding` alone is not proof that initial binding is appropriate.

Normal writes use owner-selected `ledger transact` operations. Never hand-edit,
compact, reinterpret, or skip records. The context reference permits only its
explicit cold-adoption transport; that is not an alternate reader or writer.
Fail closed on unknown closure, ABI, operator, binding, integrity, replay,
projection, or recovery state.

Lease expiry does not transfer authority. Recovery is explicitly authorized and
bound to one transaction's resource, lock identity, fencing token, owner, and
witnessed lease state. Read [storage-maintenance.md](references/storage-maintenance.md)
before recovery or version-dependent migration. No broad reclaim/repair mode.

## Trigger cues and reporting

Use for explicit `$ledger`/`$ledger ensure`, a consumer's first native command,
runtime/ABI availability, managed storage context, worktree continuity, definition
authoring, validation/materialization, durable transactions/projections, binding,
and exact recovery. Do not trigger merely because work creates history or a
receipt; the semantic owner selects the protocol.

Report the actual operation, selected definition/closure/ABI, result schema and
verdict, storage mutation, exact addressed source/transaction when relevant, and
remaining owner action. Missing metadata limits the claim. Keep pure validation,
transactions, doctor, context failures, and recovery outcomes distinct rather
than forcing them into one generic status template.
