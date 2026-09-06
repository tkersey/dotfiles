# Capability boundary

Ergon is not yet the dependency-aware task application proposed in the design
conversation. The current definition implements durable lifecycle behavior with
native transitions, immutable task descriptions, operation-scoped idempotency,
optimistic revision checks, projections, and replay. No Ledger skill or native
runtime change is included.

## Reproduce

With the current sibling `$ledger` bootstrap and a compatible native executable:

```bash
uv run codex/skills/ergon/tests/test_protocol.py --lifecycle-only
uv run codex/skills/ergon/tests/test_protocol.py
```

The first command qualifies only the lifecycle subset. The second includes graph
acceptance and must remain red until the missing behavior is implemented; there
are no expected-failure or skipped-test annotations hiding that result.

On Ledger 1.1.1, the first dependency addition in the full suite returns native
`UnknownOperation`. This is an executable witness that **this candidate is
incomplete**, not proof that every possible Ledger encoding is impossible.
The test runner neither calculates readiness nor implements a graph or storage
adapter. It serializes proposed inputs and asserts independently specified
observations against native results.

## Required behavior before live use

For open tasks A and B, declaring B requires A must leave only A ready. Closing
A makes B ready; reopening A removes B from the ready set without writing B.
Removing the edge restores both open tasks to readiness. Fresh-process replay
must preserve these observations and accepted mutation history.

Admission must reject missing endpoints, self-dependencies, and cycles of any
length within the declared graph bound. Rejections must leave domain state and
accepted history unchanged. In particular, two processes proposing opposite
edges from the same revision must not both succeed. An ordinary revision
conflict is acceptable; accepting a cycle is not. Duplicate retries must not
create duplicate edges or history, and conflicting request reuse must fail.

The lifecycle's two-writer test establishes native optimistic coordination for
that lifecycle. It does **not** establish cross-task graph safety.

## Where implementation stopped

The inspected runtime has keyed lifecycle folds and state admission machinery,
but its projection plans are not an arbitrary relational query language. A
validation operator's presence in `capabilities` does not establish that it can
be placed in a projection pipeline. No clean owner-definition composition for
both cross-task admission and native derived readiness was established here.

Relevant source inspection used `tkersey/skills-zig` commit
`09982f2b0abe11abae7922a7451763e3a3198f44`, especially
`apps/ledger/src/v1/projection.zig`, `reducer.zig`, `state_reducer.zig`, and
`validation.zig`. Qualification ran the official `ledger-v1.1.1` Linux artifact
from release workflow run `31833712996`, build commit
`f700a676de18fb587b4c9c23e4da89ef1b77ae1b`. Test output can retain the exact native
closure digest and receipts with `--evidence`; no fabricated receipt schema is
introduced.

Continue with the smallest definition-level encoding that can satisfy the
counterexamples and their valid neighbors. Do not weaken acyclicity, cache
unverified readiness, or implement missing semantics in the Python tests. A
native extension requires a separately justified, bounded, domain-independent
capability under `$ledger`'s current extension law. This draft does not presume
that such an extension is necessary or authorize one.
