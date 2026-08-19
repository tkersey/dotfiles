# Semantic Hotspots

This module is normative only for bug-driven reconciliation where an accepted
bug, failing test, incident, migration failure, compatibility failure, or
review finding may expose a boundary defect.

## Disclosure contract

**Load when:** a witnessed incorrect state or trace touches a construction,
transition, composition, ownership, representation, interpretation, or
observation boundary; or current repository evidence shows repeated defenses
for the same law.

**Do not load when:** the defect is wholly internal to one already-correct
owner, such as an isolated arithmetic, spelling, syntax, or mechanical
implementation mistake whose complete family is already excluded by the
incumbent architecture.

**Return:** one bounded counterexample topology and, when architecture selection
reopens, one correctness delta. Create no durable artifact.

## Core model

A bug is a witnessed counterexample to a required law. It is not itself an
architectural conclusion.

Keep these concepts distinct:

```text
Witness
  one exact input, state, trace, or observation demonstrating incorrectness

Violated law
  the Goal or incumbent invariant falsified by the witness

Detection surface
  where the incorrectness became visible

Admission frontier
  the earliest seam with enough information and authority to prevent the
  invalid state or trace from becoming a sanctioned internal value or behavior

Escape path
  a construction, transition, composition, deserialization, interpretation,
  or bypass route that evades the intended owner

Counterexample family
  the evidenced set of witnesses governed by the same law and admitted through
  the same candidate frontier or equivalent escape paths

Semantic scar tissue
  current repository structure suggesting repeated compensation for the same
  law: guards, fallbacks, normalization, sentinels, shims, retries, catch-and-
  repair branches, duplicated tests, raw constructors, or parallel transitions
```

A **semantic hotspot** is the current, ephemeral conjunction:

```text
Semantic Hotspot H =
  violated law
  x semantic owner
  x admission frontier
  x escape paths
  x independent witnesses
```

A hotspot is not a file, module, churn score, bug count, review count, or
persistent record.

## Realization defect or architectural defect

The incumbent has a realization defect when it already provides:

- one correct canonical owner for the violated law;
- an adequate representation and state space;
- complete control over sanctioned admission paths;
- a mechanism capable of excluding the complete evidenced family; and
- no live bypass requiring a new architectural mechanism.

In that case, preserve the architecture and correct the implementation.

The incumbent has an architectural defect when the witness demonstrates any of:

- a forbidden state is publicly or internally constructible through a
  sanctioned path;
- an illegal transition or composition is admitted;
- the law has no canonical owner or has several independent owners;
- the intended owner is bypassable;
- the representation lacks a required state, event, effect, terminal mode,
  ordering, custody, retry, cancellation, or recovery law;
- several consumers independently detect or repair the same invalidity;
- another local correction would add, move, or duplicate a guard while
  retaining the same invalid region;
- prior pointwise corrections changed symptoms while preserving the same
  admission frontier or escape path.

One witness is sufficient when it falsifies a universal claim such as
construction soundness, transition admissibility, composition closure, or
bypass exclusion. Do not wait for recurrence.

## Bounded excavation

Excavate only enough repository-native evidence to decide closure or establish
a hotspot:

1. Bind the exact witness to the current Goal and Git head.
2. Name the violated law and detection surface.
3. Walk upstream to the earliest seam with both the information and authority
   to prevent admission.
4. Inspect current code, types, schemas, tests, public constructors, transition
   APIs, interpreters, handlers, and ordinary documentation at that seam.
5. Search narrowly for semantic scar tissue enforcing the same law.
6. Inspect targeted Git history, issues, PRs, or incidents only when current
   evidence suggests recurrence or displaced ownership.
7. Stop when the incumbent is proved closed under the family or a semantic
   hotspot is evidenced.

Do not perform a repository-wide archaeology pass by default. Missing historical
evidence means recurrence is unknown, not absent and not established.

## Counterexample family and independence

Witnesses belong to one family only when current evidence establishes:

```text
same violated law
compatible applicability
same semantic owner
same or equivalent admission frontier
same causal mechanism or equivalent escape relation
```

Independent witnesses differ materially in at least one of:

- input partition;
- state or transition;
- call path;
- producer or consumer;
- external incident;
- test generator;
- timing, ordering, retry, or cancellation trace.

Duplicate reports, copied tests, repeated reviewer prose, and several failures
from one root execution are not independent evidence.

Bugs in the same file do not form a hotspot unless they share the semantic
basis. Bugs in different files may form one hotspot when they expose the same
law and frontier.

## Architecture closure under a family

Let `I(H)` be the incumbent reconstructed from Git head `H`, and let `F` be the
evidenced counterexample family.

`I(H)` is closed under `F` only when its existing canonical owner can exclude
every member of `F` without introducing another independent:

```text
guard
owner
representation
state dimension
transition law
effect or handler
compatibility mode
recovery mode
escape path
```

A convenient place to add code is not closure. A downstream check that notices
invalidity after admission is not closure when an admissible owner-level
candidate can prevent that admission.

## Repair locus

Prefer the strongest honest locus that owns enough information and authority:

```text
domain model or protocol
  missing state, transition, effect, authority, or law

representation or composition
  invalid state or illegal composition becomes unavailable

canonical owner boundary
  one controlled constructor, transition, interpreter, or validator rejects it

downstream detection
  invalidity is detected after admission because earlier prevention is
  impossible or externally owned

symptom handling
  one observation is repaired without excluding its causal family
```

Do not mechanically choose the highest locus. External, freshness, resource,
distributed, or policy constraints may remain runtime residuals. Name them
honestly.

## Correctness dominance

For the hotspot comparison universe, let:

```text
Invalid(A)
  evidenced invalid states or traces still admitted by candidate A

Escape(A)
  unchecked construction, transition, composition, interpretation, or bypass
  paths under A

Owners(A)
  independent semantic owners of the violated law under A

Residual(A)
  runtime guards and proof obligations not discharged by A
```

Candidate `A` correctness-dominates candidate `B` only when:

1. `A` preserves every required valid observation, compatibility obligation,
   effect order, and resource constraint preserved by `B`;
2. `Invalid(A)` is a subset of `Invalid(B)`;
3. `Escape(A)` is a subset of `Escape(B)`;
4. `A` does not distribute the law across more semantic owners;
5. `A` leaves no greater residual validation or proof burden;
6. `A` introduces no materially worse migration, operational, resource, or
   comprehension burden; and
7. at least one relation is strict.

This is a partial order. Do not assign a scalar architecture score or manufacture
a winner among incomparable minima.

Actuating selects the smallest correctness-non-dominated candidate that
satisfies every current obligation.

## Universalist nomination

For bug-driven architecture selection, ask `$universalist` to lower each live
candidate to repository-native form and return:

```text
Boundary and semantic owner:
Enforcement locus:
Counterexample family eliminated:
Unchecked paths retired:
Valid observations preserved:
Residual invalidity and owner:
Falsifier:
Transition and retirement:
```

Universalist nominates. Actuating compares and selects.

## Reduce challenge

A candidate is presumptively dominated when it preserves the same invalid region
and merely adds, moves, renames, or duplicates detection.

Ask `$reduce` whether:

- a new guard is only compensating for a permissive frontier;
- several checks can be quotiented into one owner;
- a stronger representation or protocol makes compensating layers removable;
- scar tissue can be retired after a law-level proof exists.

Reduce challenges; Actuating selects.

## Counterexample compression

As independent witnesses accumulate, strengthen the proof surface:

```text
one witness
  -> focused regression example

several same-law witnesses
  -> explicit counterexample family

stable family
  -> property, model, exhaustive transition test, construction-negative test,
     schema constraint, fuzz invariant, or interpreter-agreement test

architectural correction
  -> owner-level family exclusion plus bypass-retirement proof
```

Retain representative examples when they aid diagnosis. Remove or consolidate
redundant examples and defensive checks only after the stronger law-level proof
passes.

## Correctness proof

A correct-by-construction improvement for the selected seam proves:

```text
Witness rejection
  the reported witness cannot recur through sanctioned paths

Family elimination
  the evidenced invalid family is unconstructible or rejected at one canonical
  owner before domain admission

Valid preservation
  required valid behavior, observations, compatibility, effects, and resources
  remain valid

Bypass exclusion
  raw construction, composition, deserialization, transition, interpretation,
  or alternate-owner paths cannot evade enforcement

Elimination adequacy
  every newly representable valid case is handled by sanctioned eliminators or
  interpreters

Residual honesty
  constraints not preventable by construction are explicit, owned, observable,
  and falsifiable
```

Use the strongest proof mechanism honestly supported by the repository:
opaque constructors, tagged unions, exhaustive matching, schema constraints,
compile-fail tests, property tests, model-based state-machine tests, fuzzing,
interpreter agreement, transactional checks, or targeted residue searches.

## Working analysis

When this module is live, extend the Architecture Working Set with:

```text
Counterexample topology
  Witness:
  Violated law:
  Detection surface:
  Admission frontier:
  Counterexample family:
  Escape paths:
  Semantic scar tissue:

Correctness delta
  Invalid region eliminated:
  Escape paths retired:
  Valid observations preserved:
  Residual invalidity:
  Residual owner:
```

The analysis remains ephemeral. Git, tests, owner evidence, and ordinary
architecture documentation retain durable truth.

## Discriminating examples

### Realization defect

The canonical constructor already excludes invalid values, but one internal
caller bypasses the sanctioned helper contrary to the incumbent architecture.

```text
preserve architecture
repair the caller
close the accidental bypass
prove the sanctioned constructor remains complete
```

### Representational defect

A domain value permits a forbidden field combination through its public
construction surface.

```text
reopen architecture
select an owner-controlled representation or constructor
exclude the invalid combination before domain admission
retire downstream compensating guards
```

### Temporal defect

A retry or cancellation bug reveals a missing generation, terminal disposition,
sequencing, custody, or transition law.

```text
reopen architecture
introduce the missing protocol or state-machine mechanism
do not add another catch-and-compensate branch
```

### False hotspot

Two bugs occur in one file but violate different laws and originate at different
frontiers.

```text
do not quotient
do not infer recurrence
do not invent one abstraction
```

## Hard exclusions

- No bug Ledger, hotspot registry, hotspot database, architecture score,
  bug-count threshold, receipt family, predecessor chain, or durable Actuating
  state.
- Do not use file proximity, churn, retry count, elapsed time, or theoretical
  vocabulary as hotspot evidence.
- Do not conflate detection surface with admission frontier.
- Do not call guard multiplication correct by construction.
- Do not claim family elimination while a sanctioned escape path remains.
