# Migration Playbooks

These are operator playbooks, not abstract examples. Use them when the goal is
to land one structural seam safely.

## Playbook 1 — Flags to coproduct

**Trigger**
`status`, booleans, and nullable fields try to describe one lifecycle.

**Files to touch first**
- DTO or row type
- decoder / adapter
- one core state module
- one service or handler that consumes the state
- focused tests

**Move**
1. Define the internal coproduct.
2. Add a decoder from the legacy shape.
3. Keep the external row or JSON shape stable.
4. Move one transition or consumer to the new internal state.
5. Reject impossible legacy combinations in the decoder.

**Proof**
- each valid legacy shape maps to exactly one variant
- invalid combinations are rejected
- one consumer handles the new variants exhaustively
- parity with the old legal transition behavior

**Stop when**
one internal call path uses the tagged union and the boundary stays stable.

## Playbook 2 — Repeated validation to refined type

**Trigger**
The same validation or normalization logic appears across controllers, services,
serializers, or repositories.

**Files to touch first**
- value object or wrapper
- constructor / parser
- one controller or serializer boundary
- one downstream service signature
- focused tests

**Move**
1. Create the refined wrapper and checked constructor.
2. Parse once at the boundary.
3. Change one downstream seam to accept the refined type.
4. Keep raw primitives only at explicit I/O edges.
5. Delete duplicate checks in the changed seam.

**Proof**
- valid accepted
- invalid rejected
- normalization idempotent when present
- no duplicate validation remains inside the chosen seam

**Stop when**
one end-to-end path parses once and services stay on the refined type.

## Playbook 3 — Shared-id checks to pullback witness

**Trigger**
Business code repeatedly checks that two models share account, tenant, locale, or schema version.

**Files to touch first**
- one checked constructor
- one join helper or aggregate
- one service that consumes the pair
- focused tests

**Move**
1. Define a witness that preserves both projections.
2. Centralize the agreement check in the constructor.
3. Replace one downstream raw pair with the witness.
4. Remove repeated agreement assertions in that seam.

**Proof**
- matching inputs accepted
- mismatches rejected
- original projections preserved
- downstream code no longer re-checks the same invariant

**Stop when**
one business path consumes the witness instead of a raw pair.

## Playbook 4 — Branchy policy logic to exponential

**Trigger**
Large conditionals choose among behaviors that should be supplied or composed.

**Files to touch first**
- policy interface or function type
- one factory or selection site
- one consuming service
- focused parity tests

**Move**
1. Define the behavior seam as a function or strategy.
2. Extract one old branch into a concrete policy.
3. Inject the chosen behavior into one caller.
4. Compare outputs with the old implementation on agreed fixtures.

**Proof**
- fixture parity
- explicit composition order where needed
- no hidden branch bypass in the changed seam

**Stop when**
one caller supplies behavior instead of hard-coding it.

## Playbook 5 — Rule engine to free construction

**Trigger**
Syntax, execution, logging, and explanation are tangled in one class tree or workflow builder.

**Files to touch first**
- AST or command type
- one interpreter
- one adapter from legacy rule objects
- shared corpus tests

**Move**
1. Model syntax as a dumb AST.
2. Add one interpreter for execution.
3. Add one interpreter for explanation or logging.
4. Translate one legacy rule family into the AST.
5. Compare old and new behavior on the same examples.

**Proof**
- shared corpus matches old evaluator
- explanation interpreter lines up with evaluation
- AST constructors remain free of execution logic

**Stop when**
one rule family runs through the AST with at least one second interpreter.
