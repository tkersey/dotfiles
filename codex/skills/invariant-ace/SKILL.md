---
name: invariant-ace
description: "Turn 'should never happen' into 'cannot happen': extract owned, inductive invariants for data validity, protocols/concurrency, and algorithmic state; enforce them at the strongest cheap boundary (parse/construct/API/DB/lock/txn); refine via counterexample traces; deliver invariant predicates, a minimal before/after seam, and a verification signal (property/stateful/stress/model check). Use when null/shape surprises, validation sprawl, cache/index drift, impossible state combinations, idempotency/versioning concerns, retries/duplicates/out-of-order events, race/linearization edge cases, or loop correctness risks appear. Prefer this skill to frame invariants before broad implementation/fix skills."
---

# Invariant Ace

## Mission

Turn "should never happen" into "cannot happen" with minimal, high-leverage changes: pick owned, inductive invariants; enforce them at the strongest cheap boundary; prove via a concrete counterexample trace and a verification signal.

## Use When (Signals)

- Null/shape surprises, runtime validation sprawl, or input decoding scattered across the codebase.
- Redundant stored facts drift (cache/index/denormalized columns) or "fix-up" code runs often.
- Flags/states explode; impossible combinations appear; "unreachable" is reachable.
- Races, duplicate/out-of-order events, retries, partial failures, or "exactly once" assumptions.
- Idempotency keys, monotonic version/epoch checks, stale writes, or linearization questions are central.
- Loop/algorithm correctness depends on comments or intuition; tricky indexing/arithmetic/termination.
- "Should never happen" branches show up in logs or error trackers.

## Routing Priority

- If a task has invariant/protocol cues and also asks for broad implementation (`$tk`, `$fix`, `$work`), run this skill first to lock invariants, then execute edits.
- If you cannot name state owner + transitions, switch to clarification/discovery before implementation.

## Core Model (Fast Definitions)

- Invariant: predicate P(state) intended to hold for all reachable states in a scope.
- Inductive: true initially AND preserved by every allowed transition in that scope.
- Owner: the single module/type/transaction/lock/actor that controls all mutations needed to preserve P.
- Precondition/postcondition: caller obligation vs operation guarantee; do not mislabel these as invariants.
- Derived property: recomputable fact; avoid storing it as "must match" unless you centralize updates.
- Safety vs liveness: invariants are safety ("nothing bad"); keep progress ("eventually") separate.

## Immediate Scan

- State owner: where does the truth live (type/module/service/table)?
- State boundary: where does raw data enter (API/DB/file/queue)?
- Allowed transitions: list operations/events that mutate the state (including retries and concurrency).
- Failure today: one concrete trace (inputs + transitions + schedule) that reaches a bad state.
- Protection level: hope -> runtime -> construction-time -> type/compile-time -> persistence/protocol/atomicity.
- Pain tag(s): data | concurrency/protocol | algorithm/loop (often multiple).

## Protection Ladder

Choose the cheapest strong layer that makes the violation hard or impossible.

- Hope-based: comments, assumptions, "unreachable".
- Runtime: scattered guards/validators near use sites.
- Construction-time: parse/validate once at boundaries; core code only handles refined values.
- Type/compile-time: illegal states are unrepresentable (ADTs, typestates, opaque wrappers).
- Persistence: schema/constraints/transactions enforce invariants at rest.
- Concurrency boundary: locks/actors/CAS/txns define where invariants must hold (under lock, at commit, at linearization).

## Protocol (Counterexample-Driven)

1. Declare scope + owner.
   - Write "P holds when/where": always | after construction | under lock | at txn commit | after message apply.
   - If you cannot name an owner, the invariant will drift; pick a choke point first.

2. List transitions and try to break P.
   - For each transition (and retry/out-of-order variants), attempt a counterexample trace.
   - If P fails, decide: bug vs wrong scope vs missing state vs wrong owner.

3. Make P inductive (or downgrade it).
   - Weaken P, move it to pre/postconditions, or add auxiliary state (version/epoch/status/idempotency key) until it closes under transitions.

4. Run a coordination check (concurrency/distributed).
   - Ask: can two individually-valid concurrent transitions merge into a P-violating state?
   - If yes, you need coordination (lock/txn/consensus) OR you must redesign the invariant/operation (partition, escrow, monotone merges, idempotency).

5. Encode enforcement at the strongest cheap boundary.
   - Prefer: parser/decoder + smart constructors + narrow/opaque types + centralized mutation.
   - Avoid: N scattered validators, duplicated truths without a single writer, and "fix-up" routines on every read.

6. Add observability if full enforcement must be staged.
   - Add cheap tripwires (assert/log/metric) and quarantine paths (reject/dead-letter/compensate).
   - Record replayable context (transition name, IDs, versions), not raw secrets.

7. Verify with the right harness.
   - Data: fuzz/property tests on parsers/constructors.
   - State machines: stateful/model-based tests (sequences).
   - Concurrency: stress + schedule perturbation; assert at quiescent points.
   - Protocols: small model checking/simulation for drops/dupes/reorder.
   - Algorithms: invariant assertions in loops + differential tests vs reference.

## Compact Mode (Fast Path)

Use this when the task is small or time-boxed.

1. Counterexample: one concrete failing trace (<=5 transitions).
2. Invariants: 1-2 predicates with explicit owner + scope.
3. Enforcement Boundary: one chosen choke point (parse/construct/API/DB/lock/txn).
4. Verification: one signal tied to one predicate.

Escalate to full protocol if any of the above is ambiguous or non-inductive.

## Invariant Record (Use This Format)

- Predicate: P(state) (precise, checkable)
- Owner: module/type/service/table/lock/txn
- Holds: always | after construction | under lock | at commit | after apply
- Maintained by: transitions that must preserve P
- Enforced at: parse/construct/API/DB/lock/txn/protocol
- Counterexample to avoid: minimal trace that breaks it today
- Verification: property/stateful/stress/model/differential

## Patterns by Pain

### Data Modeling & Input Validity

- Boundary refinement: raw -> parsed -> validated; only validated enters core.
- Canonicalization: normalize early (case/whitespace/timezone/ID format) so equality and caching are stable.
- Explicit absence: model optionality explicitly; avoid "sometimes null" in the core.
- Cross-field coupling: combine coupled fields into one value to prevent illegal combinations.
- Denormalization discipline: if you store derived facts, centralize writes or make them recomputed.

### Concurrency & Protocol Correctness

- Lock/txn invariants: P holds under lock or at commit; define where the linearization point is.
- Monotonic metadata: versions/epochs/counters only increase; reject stale writes.
- Idempotency: retries and duplicates are safe (idempotency keys, dedupe tables, "apply once").
- Explicit state machines: enumerate states + allowed transitions; persist enough metadata to reject out-of-order events.
- Coordination decisions: if P depends on global uniqueness or non-negativity under concurrent debits, choose coordination or redesign (partition/escrow).

### Algorithms & Loop-Heavy Code

- Loop invariants: assert what is preserved each iteration (partitioned regions, sorted prefix, conservation laws).
- Variant/termination: name a decreasing measure; if you cannot, expect non-termination edges.
- Representation invariants: hide internal structure behind an API; add a rep-check for tests/debug.
- Differential testing: compare to a simple, slow reference implementation to catch corner cases.

## Before/After Sketches (Language-Agnostic)

### Boundary Refinement (Data)

```text
Before: functions accept RawInput and validate ad hoc
After:  parseRaw(...) -> ValidatedValue | Error
        core functions accept ValidatedValue only
```

### Idempotency + Versioning (Concurrency/Protocol)

```text
Before: handle(event) mutates state directly (retries duplicate side effects)
After:  if seen(event.id) return
        if event.version <= state.version return (or reject)
        apply(event) at a single atomic boundary (lock/txn/CAS)
```

### Loop Invariant (Algorithm)

```text
Before: comment says "array left side is partitioned"
After:  assert(invariant(state)) inside loop
        test: random arrays, shrink failing cases, compare to reference
```

## Verification

Pick at least one signal and tie it to a specific invariant predicate.

- Property/fuzz: parsers, constructors, normalization.
- Stateful/model-based: sequences over operations; check invariants after each step.
- Concurrency stress: N threads + jitter; assert invariants at quiescent points.
- Protocol simulation: reorder/duplicate/drop + crash/restart; assert safety invariants.
- Model checking (optional): small state + exhaustive exploration for protocols.
- Differential/reference: algorithm output equals reference for randomized inputs.
- Runtime tripwires: assertions/logging/metrics for staged rollout.

## Research Anchors (Mental Models, Not Requirements)

- Hoare/Floyd/Dijkstra: invariants as proof objects; weakest preconditions.
- ADT/rep invariants (Liskov-style): abstraction function + local reasoning.
- Abstract interpretation: over-approx reachable states; inferred invariants.
- Dynamic invariant mining (Daikon-style): candidate generation; falsify with counterexamples.
- Separation logic / framing: invariants tied to ownership; interference-aware reasoning.
- Rely-guarantee & linearizability: concurrency invariants under schedules.
- TLA+/Alloy mindset: protocols as transitions + invariants; counterexample traces.
- Coordination avoidance / CRDT laws: when invariants require coordination vs merge-safe design.

## Output Contract (Required Headings)

Use these exact headings in the final response for this skill:

1. Counterexample
2. Invariants
3. Owner and Scope
4. Enforcement Boundary
5. Seam (Before -> After)
6. Verification
7. Observability (optional)

## Deliverable Checklist

1. Counterexample: minimal breaking trace (include schedule/retry if relevant).
2. Invariants: 1-5 predicates with owner + scope ("holds when").
3. Enforcement Boundary: boundary/type/API/DB/lock/txn/protocol choice + why.
4. Seam (Before -> After): minimal structural change that makes violations hard.
5. Verification: property/stateful/stress/model/differential tied to at least one predicate.
6. Observability (optional): tripwires/quarantine/metrics if rollout must be staged.

## Cross-Coordination

- If broader failures emerge, lean on the Unsoundness checklist.
- If stronger invariants dent ergonomics, reference the Footgun guardrails.

## Measurement (seq)

Track adoption and compliance with `seq`:

```bash
uv run codex/skills/seq/scripts/seq.py skill-trend --skill invariant-ace --bucket week
uv run codex/skills/seq/scripts/seq.py skill-report --skill invariant-ace \
  --sections "Counterexample,Invariants,Owner and Scope,Enforcement Boundary,Seam (Before -> After),Verification,Observability (optional)" \
  --sample-missing 5
```
