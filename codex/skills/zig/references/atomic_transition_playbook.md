# Fallible state transitions and failure guarantees

Use when a fallible operation changes state, transfers ownership, or publishes an
effect. First identify what the API promises; full rollback is not universal.

| Guarantee | Required behavior on failure |
| --- | --- |
| Strong / transactional | Advertised observable state equals its pre-state. |
| Basic | Invariants and ownership remain valid; state may change. |
| Partial progress | Completed work and retry/resumption semantics are represented or documented. |
| Durable / recoverable | Commit status, recovery, replay and idempotency are unambiguous. |

Every failure must preserve the advertised guarantee. An API promising atomicity
must not silently expose partial progress. A streaming writer accepting a prefix
before failing is not defective merely because rollback is impossible. A failed
operation must not leak, double-free, or leave ownership ambiguous under any of
these guarantees.

## Observable owners and commit status

For the live transition, inspect containers, counters, indexes, authoritative
caches, journals/ledgers, outboxes, events, filesystem/database effects, transferred
allocations, returned identifiers, and borrowed refs. Identify the first visible
mutation and any later allocation, append, persistence, callback, or publication
that can fail. A structured inventory is optional unless a consumer requires it.

Distinguish not committed, committed, and committed-but-publication-incomplete.
A post-commit error must not mislead a caller into an unsafe retry. External
preflight is not a reservation or transaction; the later effect can still fail.

## Strong guarantee: preferred topology

Prepare fallible data, commit a non-fallible state transition, then publish.
Preparation can include allocation, duplication, validation, capacity reservation,
ref/event construction, and real reservations. It must not violate the advertised
pre-state guarantee: reservation can itself reallocate a container and invalidate
borrows, so decide which observations the API includes.

Otherwise use rollback covering every promised owner/effect, without allocating
or failing during rollback. If publication can fail or the process can crash after
commit, expose a durable/recoverable protocol rather than pretending rollback
remains possible. Test outbox/replay/idempotency behavior where applicable.

Memory cleanup is not state rollback. Watch for appending half an event pair,
moving ownership into A before B can reject, committing before returned evidence
exists, disarming `errdefer` too early, leaving counters/indexes changed, or
returning an identifier for a transition that is later undone.

## Discriminating tests

Use deterministic allocation and non-allocation failure points when they exercise
the guarantee. For transactional APIs, compare full advertised observable pre- and
post-state at each failure index, including events and refs, not just memory usage.
For basic guarantees, verify invariants and valid continued use. For partial
progress, verify the reported prefix/progress, cleanup and defined retry behavior.
For durable recovery, inject failures around commit/publication and test replay
without lost or duplicated effects according to the protocol.

Across all guarantees, assert the expected error, exact-once ownership disposal
or transfer, and absence of undocumented escaped refs/effects. Do not claim an
unexecuted fail point was tested; see [evidence context](evidence_context_playbook.md).
