# Architecture Reconciliation

Actuating does not load a stored architecture. It reconstructs the incumbent
from the exact current Git tree and recompiles a target only when current
evidence makes the incumbent architecturally contestable.

## Incumbent model

Inspect repository-native evidence for:

```text
boundary and sanctioned inputs
current owner set and authority
authoritative representation
state dimensions
events, transitions, and terminal states
effects, handlers, ordering, and custody
observations and public contracts
compatibility, migration, retry, cancellation, and recovery
proof mechanisms
primary enforcement, derived guards, bypasses, and residue
```

Use code, types, schemas, tests, public interfaces, and ordinary architecture
documentation. Historical Actuating analyses are hypotheses, not inputs unless
their claims remain evidenced by the current tree.

## Bug-driven input

An accepted bug is a counterexample to a required law, not a direct patch
instruction.

When a bug or falsifier touches a boundary, read
[semantic-hotspots.md](semantic-hotspots.md). `$review-fold` returns an
observational class with witness provenance, current applicability, law,
current owner set, and a bounded family hypothesis. Actuating then derives:

```text
predicate-defined family and domain
sanctioned admission relation
claim strength
admission frontier or minimal admission cut
candidate semantic owner
escape paths
classified semantic scar tissue
```

Actuating may partition one observational class into several frontier-equivalent
families. Review Fold does not select the partition, frontier, cut, or repair.

## Closure under an obligation

Let `I(H)` be the incumbent model reconstructed from head `H`, and let `o` be a
new obligation.

`I(H)` is closed under `o` when satisfying `o` requires only correcting the
realization of an already represented law under the same authority,
representation, state space, effects, observations, and compatibility posture.

For a bug-driven obligation, let:

```text
D = declared family domain
Phi = invalidity predicate or generator
A = sanctioned admission relation
C = candidate admission frontier or cut
```

`I(H)` is closed only when its existing semantic authority and `C` can exclude
`Phi` from `A` over `D` at the stated claim strength without adding another
independent guard, semantic owner, representation, state dimension, transition
law, effect, compatibility mode, recovery mode, or escape path.

It is not closed when satisfying `o` requires any of:

- new state, event, transition, terminal mode, or ordering;
- new authority, custody, ownership, or admitted domain;
- new representation, interpreter, handler, or observation path;
- new compatibility, retry, cancellation, timeout, or recovery semantics;
- structural removal of a bypass, competing owner, or obsolete representation;
- a shared mechanism exposed by recurring same-cause failures;
- another downstream check while the same invalid family remains admitted;
- a multi-frontier admission cut not represented by the incumbent.

When closed, preserve the architecture and repair the realization. When not
closed, recompile before mutation.

## Reconsideration evidence

Reopen architecture selection only from witnessed evidence:

```text
source change
law falsification over a sanctioned path
semantic novelty
causal recurrence
predicate-defined semantic hotspot
distributed, absent, contested, or unknown ownership
incomplete frontier or cut coverage
live dominated residue
smaller correctness-non-dominated candidate
incoherent or unrecoverable incumbent model
```

One witness may be dispositive when it falsifies an attributed universal
construction, transition, composition, ownership, or bypass law.

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
- supplied incidents, migration failures, and compatibility failures with their
  original witness subjects;
- current applicability evidence for the exact head;
- current repository scar tissue at the implicated owner set and candidate cut;
- targeted Git, issue, PR, CAS, or incident history when current evidence
  justifies a recurrence inquiry;
- active exact Negative Ledger exclusions when that skill's own gate is live.

Missing historical owner evidence is `unknown`. Do not invent continuity,
recurrence, or current applicability.

## Candidate compilation

1. Freeze the incumbent-independent premise basis with `$first-principles`.
2. Ask `$universalist` for concrete repository-native candidates.
3. Require every candidate to cover the same Goal laws, observations,
   compatibility, predicate-defined families, admission relation, effects, and
   resource constraints.
4. Use `$metanoetic` once only when the incumbent may reflect a wrong model,
   authority, representation, or merely adequate local optimum.
5. Use `$reduce` to challenge factors lacking a distinct current obligation,
   compensating guards, and candidates that merely move detection.
6. Establish the correctness Pareto frontier using explicit relation evidence.
7. Among correctness-equivalent candidates, select the least costly effective
   realization.
8. Keep material correctness/cost tradeoffs and incomparable minima explicit;
   obtain authority or block rather than manufacturing dominance.
9. State the correctness delta and its evidence strength before mutation.

Compare candidates by:

```text
required laws and observations
predicate-defined invalid states or traces excluded
sanctioned admission coverage
frontier or admission-cut coverage
current and candidate semantic owners
derived guards preserved
representations and escape paths
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
Witness provenance and current applicability, when bug-driven
Observational class, when bug-driven
Family predicate, domain, admission relation, and claim strength, when bug-driven
Current owner set and status, when bug-driven
Admission frontier or admission cut, when bug-driven
Escape paths and classified scar tissue, when bug-driven
Selected target
Candidate semantic owner
Preserve
Introduce or replace
Retire
Disposition: eliminated | contained | obstructed | unresolved
Invalid region eliminated
Admission coverage
Residual invalidity and owner
Evidence strength
Proof commands
Reconsider when
```

The Working Set is ephemeral. It coordinates the current run but grants no
authority and has no schema, content identity, predecessor, store, or migration.

Refresh it when the bound head, Goal, current applicability, family predicate,
owner set, frontier/cut, or target changes. After implementation, the Git tree
is the realized construction.

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
