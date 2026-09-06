---
name: ergon
description: "Explicit-only experimental task-domain skill implemented through an owner-local Ledger definition. Qualify durable task creation, closure, reopening, replay, and optimistic concurrency in an isolated workspace. Dependency operations and native readiness remain blocked; do not use this prototype to schedule real work."
---

# Ergon

## Status and ownership

**Experimental: lifecycle implemented; dependency-graph acceptance is not complete.**
Use only when explicitly invoked. Until the graph acceptance tests pass, restrict
mutations to an explicitly selected scratch workspace. Do not migrate live tasks,
replace an existing task system, or route `$plan` or `$actuating` through Ergon.
See [the outstanding capability boundary](references/capability-gap.md).

Ergon owns task semantics in
[task-protocol.json](definitions/ledger/task-protocol.json), registered by
[manifest.json](definitions/manifest.json). Ledger owns generic enforcement and
custody. No task-tracker binary, wrapper CLI, executable definition hooks, or
agent-computed readiness cache belongs in this implementation.

## Runtime

Load `$ledger` and complete its current `ensure` procedure before the first
native command. Reuse readiness only while the executable and environment remain
unchanged. Do not copy the bootstrap handler into Ergon. Provisioning, recovery,
and result interpretation follow the current `$ledger` contract.

Set the actual installed skill path, or the checked-out path when developing:

```bash
ergon_definition="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/ergon/definitions/ledger/task-protocol.json")"
ledger definition check --definition "$ergon_definition" --format json
ledger definition describe --definition "$ergon_definition" --format json
```

Check a new or changed closure, not every unchanged operation. A successful
bootstrap does not establish support for this definition. The initial native
qualification used Ledger 1.1.1; the definition's ABI and operators control
compatibility, not that observation alone.

## Implemented protocol

A task has a repository-local stable `id`, immutable `title`, and lifecycle state
`open` or `closed`. Legal transitions are creation into `open`, closing an open
task, and reopening a closed task. Reusing a task ID, silently changing a title,
or applying an illegal transition is rejected. Native idempotency keys are scoped
to an operation: creation retries are idempotent, and conflicting reuse within
that operation is rejected. Close/reopen revision checks precede idempotency,
so repeating the original stale revision is rejected even after success.

Operations are `create`, `close`, and `reopen`. Each accepts the same submission:

```json
{"id":"A","record":{"title":"Task A"}}
```

Write the submission to a scratch input file, not a store. Supply a unique
`request` identifier for a new operation; retain that identifier and the exact
submission for a retry after an uncertain outcome.

```bash
ledger transact --definition "$ergon_definition" \
  --operation create --repo "<scratch-repo>" \
  --input submission="<submission.json>" --param request="<request-id>" \
  --format json

ledger project --definition "$ergon_definition" \
  --projection current --repo "<scratch-repo>" --format json
```

For `close` or `reopen`, first select the current task and preserve the projection
envelope. Reuse its exact title and supply that envelope's `store.revision` as
`--param revision="<revision>"` to the transaction. Creation checks ID absence
under native custody; it does not take a caller-supplied prior revision.

After a stale-revision rejection, observe the current state and history again
and reconsider the requested change. Do not blindly replay an old decision
against a new revision. An idempotent receipt describes the original effect;
project current state before claiming what is true now. Do not treat a rejected or idempotent transaction's metadata writes
as a change to task history; preserve the native receipt rather than rewriting
its `storage_mutated` field.

| Projection | Meaning |
| --- | --- |
| `current` | All tasks, lifecycle state, immutable title, and accepted event count |
| `open` | Open tasks only; **not dependency-derived readiness** |
| `task` with `--param id=<id>` | One selected task in the native result's data array |
| `history` | Complete accepted event rows within the declared output bound |

The definition deliberately has no `ready`, `blockers`, `add-dependency`, or
`remove-dependency` surface yet. Do not invent these operations, silently drop
dependencies, or return `open` as `ready`. Completion records a caller-authorized
status change; it does not certify implementation correctness or authorize a
merge, publication, or next task.

## Custody and qualification

The only task store is `.ledger/ergon/events.jsonl` beneath the selected repo.
Read through projections or `doctor`; write through the selected native
transaction. The explicit `bind-existing` operation is maintenance for an
owner-selected, fully validated current-format store, not an import or repair
shortcut. There is no implicit binding, rebinding, migration, or fallback reader.

Initial bounds are 128 tasks, 2,048 event rows, a 1 MiB store, 4 KiB input,
128-byte identifiers, and 512-byte titles. Exhaustion must fail closed; this
prototype has no compaction or retention workaround.

Run [tests/test_protocol.py](tests/test_protocol.py) with `uv run`. The runner
uses the current sibling Ledger bootstrap and the real binary, creates isolated
workspaces, and performs no direct store edits or task-graph computation.
The default suite includes required graph behavior and currently fails.
`--lifecycle-only` is partial qualification, never full application acceptance.
Optional `--evidence <new-file.jsonl>` retains native envelopes outside `.ledger`.

Keep definition-closure digest and exact store/input identities with the native
results. Report the operation performed, actual outcome, domain-state changes,
and unresolved capability; do not turn a green lifecycle subset into a claim
that the dependency-aware task system is complete.
