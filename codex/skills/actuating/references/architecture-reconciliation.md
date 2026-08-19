# Architecture Reconciliation

Actuating does not load a stored architecture. It reconstructs the incumbent
from the exact current Git tree and recompiles a target only when current
evidence makes the incumbent architecturally contestable.

## Incumbent model

Inspect repository-native evidence for:

```text
boundary and admitted inputs
canonical owner
authoritative representation
state dimensions
events, transitions, and terminal states
effects, handlers, ordering, and custody
observations and public contracts
compatibility, migration, retry, cancellation, and recovery
proof mechanisms
bypasses, parallel owners, and residue
```

Use code, types, schemas, tests, public interfaces, and ordinary architecture
documentation. Historical Actuating analyses are hypotheses, not inputs unless
their claims remain evidenced by the current tree.

## Bug-driven input

An accepted bug is a counterexample to a required law, not a direct patch
instruction.

When a bug or falsifier touches a boundary, read
[semantic-hotspots.md](semantic-hotspots.md) and derive:

```text
violated law
detection surface
admission frontier
counterexample family
semantic owner
escape paths
semantic scar tissue
```

`$review-fold` classifies witnesses and family evidence. Actuating reconstructs
the incumbent, identifies the admission frontier, decides whether a semantic
hotspot exists, and selects architecture.

## Closure under an obligation

Let `I(H)` be the incumbent model reconstructed from head `H`, and let `o` be a
new obligation.

`I(H)` is closed under `o` when satisfying `o` requires only correcting the
realization of an already represented law under the same owner, representation,
state space, effects, observations, and compatibility posture.

For a bug-driven obligation with evidenced counterexample family `F`, `I(H)` is
closed only when its existing canonical owner can exclude all of `F` without
adding another independent guard, owner, representation, state dimension,
transition law, effect, compatibility mode, recovery mode, or escape path.

It is not closed when satisfying `o` requires any of:

- new state, event, transition, terminal mode, or ordering;
- new authority, custody, ownership, or admitted domain;
- new representation, interpreter, handler, or observation path;
- new compatibility, retry, cancellation, timeout, or recovery semantics;
- structural removal of a bypass, parallel owner, or obsolete representation;
- a shared mechanism exposed by recurring same-cause failures;
- another downstream check while the same invalid family remains admitted.

When closed, preserve the architecture and repair the realization. When not
closed, recompile before mutation.

## Reconsideration evidence

Reopen architecture selection only from witnessed evidence:

```text
source change
law falsification
semantic novelty
causal recurrence
semantic hotspot
owner or representation dilution
live dominated residue
smaller correctness-non-dominated candidate
incoherent or unrecoverable incumbent model
```

One witness may be dispositive when it falsifies a universal construction,
transition, composition, ownership, or bypass law.

Diff size, file proximity, elapsed time, bug count, test count, retry count,
reviewer preference, and abstract vocabulary do not establish reconsideration.

## Evidence horizon

Architecture selection uses the complete currently available applicable
evidence:

- current accepted Goal;
- current Git tree;
- current failing tests and verifier outputs;
- current CAS findings and exact receipts;
- unresolved provider review threads;
- supplied incidents, migration failures, and compatibility failures;
- current repository semantic scar tissue at the implicated owner and frontier;
- targeted Git, issue, PR, or incident history when current evidence justifies
  a recurrence inquiry;
- active exact Negative Ledger exclusions when that skill's own gate is live.

`$review-fold` separates facts from suggestions, quotients duplicates, and
identifies counterexample families, witness independence, recurrences, and
causal mechanisms. Missing historical owner evidence is reported as unknown;
Actuating must not invent continuity or recurrence.

## Candidate compilation

1. Freeze the incumbent-independent premise basis with `$first-principles`.
2. Ask `$universalist` for concrete repository-native candidates.
3. Require every candidate to cover the same Goal laws, observations,
   compatibility, active falsification pressure, and evidenced counterexample
   families.
4. Use `$metanoetic` once only when the incumbent may reflect a wrong model,
   owner, representation, or merely adequate local optimum.
5. Use `$reduce` to challenge factors lacking a distinct current obligation and
   candidates that merely move or duplicate detection.
6. Select the smallest correctness-non-dominated candidate.
7. Keep incomparable minima explicit; obtain authority or block rather than
   manufacturing dominance.
8. State the correctness delta before mutation.

Compare candidates by:

```text
required laws and observations
evidenced invalid states or traces excluded
admission frontier and escape paths
canonical owners
representations and bypasses
semantic mechanisms
compatibility and migration
retirements and residue
residual runtime and proof burden
proof strength and proof surface
resource and operational burden
```

A candidate cannot win by omitting an orthogonal obligation. A candidate that
preserves the same invalid region and merely relocates detection does not
correctness-dominate its incumbent.

## Architecture Working Set

For active implementation, retain:

```text
Bound head
Goal
Incumbent model
Falsified or newly required laws
Counterexample family, when bug-driven
Detection surface, when bug-driven
Admission frontier, when bug-driven
Escape paths and semantic scar tissue, when bug-driven
Selected target
Canonical owners
Preserve
Introduce or replace
Retire
Invalid region eliminated
Residual invalidity and owner
Proof commands
Reconsider when
```

The Working Set is ephemeral. It coordinates the current run but grants no
authority and has no schema, content identity, predecessor, store, or migration.

Refresh it when the bound head, Goal, applicable evidence, counterexample
family, or target changes. After implementation, the Git tree is the realized
construction.

## Architectural memory

Persist architecture where maintainers naturally encounter it:

- code structure and types;
- executable regression, property, model, and invariant tests;
- public schemas and API contracts;
- an existing accepted specification;
- a PR explanation;
- an ADR only when the decision genuinely has long-lived human value.

Do not create an Actuating-private source of truth. If a decision cannot be
recovered from the repository, improve the repository's architecture
legibility.
