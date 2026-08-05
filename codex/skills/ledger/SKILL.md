---
name: ledger
description: "Ensure Ledger 1.x is available and use its passive-definition runtime to validate, canonicalize, materialize, transact, replay, project, doctor, bind, and recover owner-defined artifacts and stores. Use for native Ledger operations, definition authoring or debugging, ABI and capability inspection, and exact storage custody. The owning skill supplies semantics and selects the operation; Ledger enforces the selected definition without acquiring workflow authority."
---

# Ledger

## Mission

Provide the shared bootstrap and operating doctrine for Ledger 1.x: a bounded,
deterministic artifact-protocol runtime driven by passive definitions owned by
their semantic domains.

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
complete `$ledger ensure` once. That readiness applies to every Ledger consumer
in the workflow; do not bootstrap per skill or per command. `$ledger` is skill
syntax, not a shell command.

Use [scripts/ensure-ledger](scripts/ensure-ledger):

```bash
ledger_skill_root="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/ledger")"
"$ledger_skill_root/scripts/ensure-ledger"
```

After the handler emits `ledger-bootstrap-ready/v1`, invoke the native CLI
directly:

```bash
ledger <native-ledger-arguments...>
```

The handler requires Ledger major version 1 and
`ledger-artifact-abi/v1`. When installation authority exists, it can install or
upgrade the canonical Homebrew formula `tkersey/tap/ledger`. It does not proxy
native commands. The native CLI owns integrity, stdout, stderr, exit status,
and failure reporting after readiness.

If `ledger` does not resolve on `PATH`:

1. install only when the current request or standing environment policy
   authorizes user-level CLI provisioning;
2. pass `--install` to the bootstrap handler when that authority exists;
3. otherwise stop with the handler's exact remediation;
4. never use `curl | sh`, an unpinned download, or an alternate Ledger
   implementation.

Do not install during an active repository effect.

```yaml
ledger_bootstrap_ready:
  schema: ledger-bootstrap-ready/v1
  status: ready
  path:
  version: 1.x
  abi: ledger-artifact-abi/v1
  action: none | installed | upgraded
```

Bootstrap readiness grants no semantic authority.

## Native surface

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
semantic policy.

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

Preserve the normal result envelope. Use `--payload-only` only for an explicit
structural pipe whose receiver already owns interpretation.

## Definition ownership

Passive definitions live beside their semantic owners, not in `$ledger`.
The owner declares the protocol and lists it in that skill's
`definitions/manifest.json`; Ledger compiles and enforces it generically.

A definition may declare:

- bounded JSON, JSONL, or UTF-8 inputs and codecs;
- canonicalization and content identity;
- closed shapes and cross-document laws;
- pure, addressed-document, or event-log storage;
- atomic operations, transitions, reducers, replay, and projections;
- logical slots beneath the selected repository's `.ledger/` control root;
- explicit output, diagnostic, record, and reducer-state bounds.

Definitions are passive JSON. They must not name hooks, shell commands,
executables, network calls, or hidden discovery procedures.

### Authoring workflow

1. Establish the semantic owner and the smallest stable artifact or protocol
   boundary.
2. Choose pure validation/materialization unless durable identity or history is
   required; choose addressed storage for replaceable canonical documents and
   an event log for append-only transitions or auditable replay.
3. Declare explicit bounded inputs, canonicalization, identity, constraints,
   storage slots, operations, and projections. Make illegal compositions
   structurally unrepresentable where the native operator vocabulary permits.
4. Keep workflow policy outside the definition. Encode only laws that can be
   decided from admitted inputs and declared storage.
5. Run `ledger definition check` and `ledger definition describe` before using
   the definition.
6. Exercise every operation and projection against representative valid,
   invalid, boundary, replay, and store-binding cases.
7. Search all consumers when a definition ID, operation, projection, field, or
   semantic version changes.

### Extension law

Add or change an owner-local passive definition first. Add a native Ledger
operator only when the capability is domain-independent, explicitly bounded,
and either:

- required by at least three unrelated definitions; or
- necessary to preserve one live behavior without material correctness or
  performance loss.

Do not turn Ledger into a domain registry or grow native operators merely to
avoid reconsidering an owner definition.

## Storage custody

Transactions write only definition-declared logical slots beneath the selected
repository's `.ledger/` root. Definitions cannot select absolute output paths
or escape the control root.

Normal reads fail closed for unbound stores. An owner may expose an explicit
one-shot binding operation for an existing fully validated current-format
store. Do not add fallback readers, alternate paths, implicit migration, or
source dispatch to Ledger.

Never open, edit, compact, migrate, or repair a store outside the owning
definition's operations and exact recovery surface.

## Recovery boundary

Lease expiry is not authority transfer. Inspect one transaction and require the
exact resource, lock identity, fencing token, owner, and witnessed lease state
before reclaiming:

```bash
ledger recovery inspect \
  --repo <repo> \
  --transaction <dtx-id> \
  --format json

ledger recovery reclaim \
  --repo <repo> \
  --transaction <dtx-id> \
  --resource <path> \
  --lock-id <dlk-id> \
  --fencing-token <u64> \
  --format json
```

For an original legacy lease only, add `--confirm-no-legacy-writers` with actual
operator authority and an inspectable basis for that assertion. Do not add it
for an interrupted current recovery. There is no broad reclaim or repair mode.

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

Report the operation actually performed, the selected definition ID and ABI,
the result schema and verdict, whether storage mutated, the exact addressed
store or transaction when relevant, and any owner action still required.

Do not force unrelated calls into one generic status template. A pure
validation, durable transaction, store doctor, and recovery inspection have
different useful outputs.

## Guardrails

- Bootstrap once before the first native command; invoke `ledger` directly
  afterward.
- Do not install without current installation authority.
- Do not install during an active repository effect.
- Do not hardcode domain artifact families, protocol versions, operations,
  projections, or closure policy in this skill.
- Do not add source dispatch, executable hooks, alternate implementations,
  implicit scanning, fallback paths, or workflow conclusions.
- Do not treat a valid artifact, healthy store, exact replay, or successful
  projection as independent semantic authority.
- Do not mutate a store except through its owning definition and selected
  `ledger transact` operation.
- Keep `validate` and `materialize` repository-pure.
- Fail closed on unknown definition closure, ABI, operator, binding, integrity,
  replay, projection, or recovery state.
