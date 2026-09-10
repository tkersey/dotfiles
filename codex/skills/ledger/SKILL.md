---
name: ledger
description: "Ensure Ledger 1.0.3 or newer within major version 1 is available and use its passive-definition runtime to validate, canonicalize, materialize, transact, replay, project, doctor, bind, rebind, and recover owner-defined artifacts and stores. Use for native Ledger operations, definition authoring or debugging, ABI and capability inspection, and exact storage custody. The owning skill supplies semantics and selects the operation; Ledger enforces the selected definition without acquiring workflow authority."
---

# Ledger

## Mission

Provide the shared bootstrap and operating doctrine for Ledger 1.0.3 or newer
within major version 1: a bounded, deterministic artifact-protocol runtime
driven by passive definitions owned by their semantic domains.

```text
owner definition + explicit inputs
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

Ledger enforces the machine-checkable semantics declared by the selected
owner definition. It has no independent authority to:

- choose the definition, operation, projection, parameters, or inputs;
- decide that a definition is semantically correct, current, or sufficient;
- discover Git state, session history, memory roots, network facts, or hidden
  workflow context;
- select a repair, route, architecture, owner, or next action;
- grant mutation, publication, review, delivery, or closure authority;
- reinterpret a structural receipt as the domain owner's semantic verdict.

The caller owns definition selection, input construction, semantic
interpretation, and every surrounding workflow action.

A successful Ledger result is strong but definition-relative. It proves the
claims named by the result schema under the selected definition and supplied
inputs; it does not prove that the owner selected the right protocol or that a
later workflow action is authorized.

## Bootstrap boundary

Before the first native Ledger command in a workflow, load this skill and
complete `$ledger ensure` once. Reuse readiness across consumers while the
resolved executable and execution environment remain unchanged; recheck after
either changes, not per skill or per command. `$ledger` is skill syntax, not a
shell command.

Use [scripts/ensure-ledger](scripts/ensure-ledger):

```bash
ledger_skill_root="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/ledger")"
"$ledger_skill_root/scripts/ensure-ledger"
```

After the handler exits successfully and emits `ledger-bootstrap-ready/v1`,
invoke the native CLI directly:

```bash
ledger <native-ledger-arguments...>
```

The handler requires Ledger 1.0.3 or newer within major version 1 and
`ledger-artifact-abi/v1`. When installation authority exists, it can install
or upgrade the canonical Homebrew formula `tkersey/tap/ledger`. It does not
proxy native commands. The native CLI owns integrity, stdout, stderr, exit
status, and failure reporting after readiness.

If Ledger is missing or incompatible, pass `--install` only when the current
request or standing environment policy authorizes user-level CLI provisioning;
otherwise stop with the handler's exact remediation. The formula is fixed, not
selected through environment overrides. Never use `curl | sh`, an unpinned
download, or an alternate Ledger implementation. Do not install or upgrade
during an active repository effect.

```yaml
ledger_bootstrap_ready:
  schema: ledger-bootstrap-ready/v1
  status: ready
  path:
  version: 1.x
  abi: ledger-artifact-abi/v1
  action: none | installed | upgraded
```

Readiness establishes runtime availability, not compatibility with every
owner definition. The selected definition's ABI, operators, and storage
requirements govern compatibility. Use `definition check` when selecting a new
or changed closure or diagnosing support; do not add a redundant preflight to
every unchanged operation. Readiness grants no semantic authority.

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

Do not invent aliases such as `ledger state`. Load the owning skill for its
exact definition path, operation names, projection names, parameters, and
semantic policy. Version-dependent maintenance commands are documented in
[storage-maintenance.md](references/storage-maintenance.md); their availability
does not authorize their use.

## Result semantics

- `definition check` proves that the admitted definition closure is
  structurally valid for the required ABI and operators.
- `definition describe` exposes the definition closure and compiled surface; it
  does not approve the owner's protocol design.
- `validate` proves only the declared constraints over explicit inputs and does
  not read or mutate repository storage.
- `materialize` additionally derives the declared canonical representation and
  identity without repository storage effects.
- `transact` performs only the selected operation's declared logical storage
  effects and returns their structural custody receipt.
- `project` replays or reads only definition-declared stores and emits the
  selected exact projection.
- `doctor` validates the selected store's binding, integrity, replay, and
  definition-relative health.
- `recovery inspect` returns the exact witnessed recovery state for one
  transaction.
- `recovery reclaim` performs only an explicitly authorized, transaction-bound
  reclaim after revalidating every required witness.

Preserve the normal result envelope, including the returned definition-closure
digest and input, artifact, or store identities applicable to that result.
A definition ID and ABI alone do not identify the exact law checked. Bind each
claim to the selected closure and the exact bytes or state actually checked;
do not apply a prior result to changed inputs, a changed closure, or a later
store state, or reduce it to an unqualified "valid." Do not invent missing
identity metadata or add a second receipt format.

Use `--payload-only` only for an explicit structural pipe whose receiver
already owns interpretation. Do not represent a payload-only projection as
though it still carried the omitted envelope.

## Definition ownership

Passive definitions live beside their semantic owners, not in `$ledger`.
The owner declares the protocol and lists it in that skill's
`definitions/manifest.json`; Ledger compiles and enforces it generically.

Definitions are passive JSON. They must not name hooks, shell commands,
executables, network calls, or hidden discovery procedures. Do not hardcode
domain artifact families, protocol versions, operations, projections, or closure
policy in this skill.

Prefer pure validation/materialization unless durable identity or history is
required. Before authoring, reviewing, debugging, or extending a definition,
read [definition-authoring.md](references/definition-authoring.md) for the
bounded vocabulary, counterexample discipline, and native extension law.

## Storage custody

Transactions write only definition-declared logical slots beneath the selected
repository's `.ledger/` root. Definitions cannot select absolute output paths
or escape the control root.

Normal reads fail closed for unbound stores. An owner may expose an explicit
one-shot binding operation for an existing fully validated current-format
store. An owner may separately expose `rebind-existing` when an authoritative
external transport replaces an already-bound store: Ledger requires an
existing stale binding, validates the complete current store, atomically
replaces only binding metadata, and leaves store bytes unchanged. Do not add
fallback readers, alternate paths, implicit migration, or source dispatch to
Ledger.

Rebinding establishes custody of a selected replacement, not authority to
select that history. Do not use it to choose between divergent stores or bless
an unknown replacement. Establish the authoritative transport first; preserve
the losing lineage as explicit owner-controlled reconciliation input.

Use the owning definition and selected `ledger transact` operation for normal
store mutations. Never open, hand-edit, compact, migrate, or repair stores
outside owner-selected operations and exact authorized maintenance surfaces.
Fail closed on unknown definition closure, ABI, operator, binding, integrity,
replay, projection, or recovery state.

## Recovery boundary

Lease expiry is not authority transfer. Recovery is explicitly authorized and
bound to one transaction's exact resource, lock identity, fencing token, owner,
and witnessed lease state; there is no broad reclaim or repair mode. Before
recovery or version-dependent migration, read
[storage-maintenance.md](references/storage-maintenance.md). The reference
preserves the legacy-writer assertion and the native command's witness checks.

## Trigger cues

- explicit `$ledger` or `$ledger ensure`;
- a skill's first native Ledger command;
- ensure, install, upgrade, or verify Ledger 1.x and its ABI;
- inspect Ledger capabilities or result schemas;
- author, review, debug, or extend a passive artifact definition;
- validate or materialize an owner-defined artifact;
- transact, replay, project, doctor, bind, or recover a declared store;
- diagnose a definition closure, operator, bound, identity, storage, reducer,
  replay, projection, or recovery failure.

Do not trigger merely because work produces history, memory, evidence, or a
workflow receipt. The semantic owner decides whether Ledger is part of that
protocol.

## Reporting

Report the operation actually performed, the selected definition ID, closure
digest and ABI when applicable, the result schema and verdict, whether storage
mutated, and any owner action still required. Preserve the result identities
above in the working evidence and surface the exact addressed store or
transaction when relevant. Missing metadata limits the claim; do not fabricate it.

Do not force unrelated calls into one generic status template. A pure
validation, durable transaction, store doctor, and recovery inspection have
different useful outputs.
