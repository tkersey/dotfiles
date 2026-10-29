# Definition authoring

Read when authoring, reviewing, debugging, or extending a passive definition.
The owning skill supplies the semantic intent; Ledger checks its encoding.

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

## Authoring workflow

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
   invalid, boundary, replay, and store-binding cases. For a changed law, retain
   its motivating counterexample and a required-valid neighboring case. Derive
   the expected outcomes from owner intent, not the implementation under test.
7. Search all consumers when a definition ID, operation, projection, field, or
   semantic version changes.

A rejected artifact does not by itself establish whether the artifact or the
law is wrong. Change a definition only when owner intent and evidence justify
that change; do not weaken it merely to obtain a successful receipt. Recheck
the same cases and the affected consumers against the changed closure.

## Storage lifetime design

For each durable artifact family, identify the retention obligation, retaining
references, explicit holds, release condition, and reconstruction dependencies.
Retain canonical history by default. A superseded revision may still be required
for replay or idempotency; a checkpoint is not permission to truncate history.
Do not prescribe an expiry merely because an artifact is old or a workflow ended.

Follow [storage-lifecycle.md](storage-lifecycle.md) for the split between owner
semantics, runtime overhead, and host resource policy. Until the corresponding
native operators are released and qualified, record lifecycle requirements as
design evidence, not unsupported JSON in an active definition. Do not implement
missing lifecycle support with shell cleanup, executable definitions, or a
second skill-local storage engine.

Qualify a lifecycle extension with a motivating retention counterexample and a
required-valid neighboring case, including retaining references, active recovery,
repeated failure, and an unrelated owner. Three unrelated fixture protocols must
exercise the same native vocabulary without owner-name branches. Capability
availability does not grant semantic deletion or publication authority.

## Extension law

Add or change an owner-local passive definition first. Add a native Ledger
operator only when the capability is domain-independent, explicitly bounded,
and either:

- required by at least three unrelated definitions; or
- necessary to preserve one live behavior without material correctness or
  performance loss.

Do not turn Ledger into a domain registry or grow native operators merely to
avoid reconsidering an owner definition.
