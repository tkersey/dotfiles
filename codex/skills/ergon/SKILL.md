---
name: ergon
description: "Use for durable dependency-aware work tracking: create, close, reopen, link or unlink task prerequisites, and inspect ready work, exact blockers, task dependencies, or task history. Invoke explicitly with $ergon or implicitly when the request calls for maintaining or querying a durable task graph. Ergon owns a passive Ledger definition; Ledger enforces the task graph atomically."
---

# Ergon

Maintain a small, durable work graph across agent sessions. Ergon owns its task
semantics in [task-protocol.json](definitions/ledger/task-protocol.json), listed
in [manifest.json](definitions/manifest.json). Ledger supplies transactions,
replay, and projections. There is no separate tracker, wrapper CLI, or
agent-maintained readiness cache.

Use when explicitly invoked or when the request calls for maintaining or querying
a durable task graph, such as tracking task prerequisites or finding ready and
blocked tasks. Do not turn ordinary coding into mandatory bookkeeping, migrate
existing tasks implicitly, or change `$plan`/`$actuating` routing. Work against the
caller-selected repository, not a guessed location.

## Runtime and custody

Load the current `$ledger` skill and complete its `ensure` procedure once per
unchanged executable/environment. **Ergon requires Ledger 1.2.0 or newer within
major version 1**, including reducer v6 and fold v7. The generic bootstrap's
older minimum is not sufficient for this definition. Check the selected closure
before first use or after it changes; do not silently fall back on Ledger 1.1.

```bash
ergon_definition="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/ergon/definitions/ledger/task-protocol.json")"
ledger definition check --definition "$ergon_definition" --format json
ledger definition describe --definition "$ergon_definition" --format json
```

For development, select the checked-out definition explicitly. Install/upgrade
only through `$ledger`'s authorized canonical procedure; never install a build
from this skill. Until Ledger 1.2 is released through the normal tap, development
qualification is not evidence that the installed 1.1 binary supports Ergon.

The authoritative store is `.ledger/ergon/events.jsonl` beneath the selected
repository. Mutate only with Ergon's native transactions, and read through its
projections or `doctor`. Tasks and dependencies share one revision and custody
boundary. Do not hand-edit the store or calculate a second authoritative graph.

## Meaning

A task has a stable repository-local identifier, immutable title, and `open` or
`closed` lifecycle state. Creation produces `open`; close and reopen must match
the existing state. A dependency `B requires A` means B is eligible only when A
is closed. Multiple prerequisites are conjunctive: **all must be closed**.

Readiness is derived: an open task is ready exactly when none of its direct
prerequisites is open. Closing or reopening A changes the readiness of dependent
open tasks without writing those tasks. Closed tasks do not automatically reopen;
Ergon is not a downstream evidence-invalidation protocol. Closing an open task
records an authorized domain decision, not a proof that its implementation is
correct. Readiness neither reserves a task nor authorizes an agent to execute it.

Both dependency endpoints must exist. Missing endpoints, self-dependencies, and
cycles are rejected atomically. Removing an edge preserves its history and
removes its blocking effect. Re-adding it restores the same relationship identity.
A distinct request to add a present edge or remove an absent edge is rejected;
a retry of an accepted request follows native idempotency semantics.

## Operations

Write request JSON to a scratch input file outside `.ledger`. Native Ledger
constructs accepted events and relationship identities; do not construct them
by hand.

| Operation | Input binding | Request JSON |
| --- | --- | --- |
| `create`, `close`, `reopen` | `submission` | `{"id":"A","record":{"title":"Task A"}}` |
| `add-dependency`, `remove-dependency` | `dependency` | `{"record":{"task":"B","prerequisite":"A"}}` |

Supply a unique `request` identifier for a new operation. Preserve its exact
operation and request bytes for an uncertain-outcome retry. For every mutation
except creation, first observe the current projection and supply its exact
`store.revision`; retain the envelope, not just the payload.

```bash
ledger transact --definition "$ergon_definition" \
  --operation create --repo "<repo-root>" \
  --input submission="<task.json>" --param request="<request-id>" --format json

ledger project --definition "$ergon_definition" \
  --projection current --repo "<repo-root>" --format json

ledger transact --definition "$ergon_definition" \
  --operation add-dependency --repo "<repo-root>" \
  --input dependency="<dependency.json>" --param request="<request-id>" \
  --param revision="<observed-store-revision>" --format json
```

Close/reopen requests reuse the task's exact immutable title from `task` or
`current`. Concurrent writers are serialized by Ledger; expected revisions catch
stale decisions and graph admission still rejects cycles after a revision refresh.
On a conflict, inspect current state/history and reconsider—not blindly retry the
old decision under a new revision.

Native request keys are operation-scoped. Revision checks precede idempotency,
so an original stale-revision retry may fail even when its earlier attempt
succeeded. Inspect state/history before deciding what to submit. An idempotent
receipt describes the original effect; project current state before claiming what
is true now. Do not rewrite native `storage_mutated`: rejected/idempotent requests
can affect custody metadata without adding task history.

## Projections

```bash
ledger project --definition "$ergon_definition" \
  --projection ready --repo "<repo-root>" --format json
```

| Projection | Result |
| --- | --- |
| `current` | All tasks: ID, status, immutable task record, accepted task event count |
| `open` | Open tasks regardless of dependencies; never substitute this for `ready` |
| `task` plus `--param id=<id>` | One task in the native result's data array |
| `ready` | Open tasks with every prerequisite closed; `blockers` is empty |
| `blockers` | Open blocked tasks with exact, sorted unresolved prerequisite IDs |
| `dependencies` | Active directed relationships and their accepted event counts |
| `history` | Accepted task and dependency events in store order |

All are deterministic projections of the selected revision. Dependency events do
not inflate a task's lifecycle event count. Preserve envelope identities and any
limitations; do not present a truncated result as a complete task or blocker set.

## Bounds, maintenance, and reporting

Initial bounds: 128 tasks, 1,024 distinct dependency identities (including removed
edges), 16,384 events, 16 MiB store/output, 4 KiB inputs, 128-byte IDs, 512-byte
titles. Exhaustion fails closed. No compaction or implicit retention workaround.
This release supports multiple processes over **one authoritative local store**,
not disconnected replicas or Git conflict resolution.

`bind-existing` is explicit maintenance for an owner-selected, fully validated
current-format store. It is not a history-selection, import, migration, or repair
shortcut. There is no implicit rebind or migration from the draft prototype.
Recovery follows the current `$ledger` reference and exact transaction authority.

Run the complete native acceptance suite:

```bash
uv run codex/skills/ergon/tests/test_protocol.py
```

The runner uses sibling Ledger bootstrap and the real binary in isolated
workspaces. It does not implement task transitions, graph algorithms, or storage.
`--evidence <new-file.jsonl>` retains unchanged native envelopes outside `.ledger`.

Report the performed operation or requested work view, actual task/edge changes,
and relevant blockers or conflicts. Retain exact closure and state identities in
working evidence. No structural receipt grants scheduling, publication, review,
or merge authority.
