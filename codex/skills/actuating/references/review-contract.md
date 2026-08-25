# Static Review Contract

Actuating owns one checked-in review policy:
[review-contract.json](review-contract.json). It is source policy, not mutable
per-goal state and not a Ledger definition.

## Contract identity and CAS boundary

Bind every request to the exact repository, base, head, target fingerprint, Goal
and acceptance context, Review Contract bytes, lens instruction bytes, and
optional pre-review Ship observation. CAS owns execution and terminal receipts.
Actuating checks owner-issued fields directly and never copies receipts into a
workflow store.

The required lenses, parallel/serial scheduling, request-local recovery, and
five-consecutive-standard-clean theorem remain unchanged.

## Candidate lifecycle

Candidate status is a live judgment:

```text
realizing
  selected construction or strongest proof incomplete

reviewable
  complete selected construction, factor dispositions, retirements, bypass
  closures, and complete Goal-required proof inventory current on one exact head

invalidated
  applicable entailed material finding falsified the reviewable candidate
```

Only `reviewable` may dispatch closure review. A material finding invalidates the
candidate immediately; it does not request a patch. The reconciliation epoch is
the derived interval until a completely selected, realized, and proved successor
becomes reviewable. It has no identity, store, receipt, or additional gate.

## Review entry

Closure review requires:

```text
complete retained applicable finding corpus
complete finding-to-class-to-generator coverage
complete affected production and proof factor fold
one family mechanism or honest residual per generator
no known dominated factor
predicted-sibling or exhaustive disposition
all selected collapse, retirement, replacement, privatization, and bypass work
  realized
complete Goal-required proof inventory current on the exact head
```

Derive the required set from the accepted Goal and current repository contracts;
do not substitute a summary conclusion. Each entry must be unique and have either
exact-head passing evidence or an authority-backed `not-applicable` disposition.
A passing aggregate covers another required proof only when its declared
dependency graph includes that proof.

No known required proof may be deferred to a post-review final closure audit.
After review convergence, closure may refresh existing evidence or perform
publication/provider readback, but it may not execute a required repository-local
proof for the first time. Such a discovery proves the reviewed candidate was
never `reviewable`, invalidates all review credit, and returns the candidate to
`realizing`.

Review is stochastic falsification of a completed construction, not a mechanism
for finishing it.

## Scheduling

### Parallel

Launch the initial standard and four auxiliaries concurrently and never cancel a
sibling. A material finding invalidates the candidate immediately, closes new
dispatch, and waits for every already-launched request—including required
recovery—to reach a semantic outcome before the evidence cut closes.

### Serial and confirmation

Dispatch one request at a time. An accepted material finding invalidates the
candidate after that request's semantic outcome; do not dispatch the next
request or confirmation.

## Cumulative evidence cut

After invalidation, close one cut containing:

```text
all semantic outcomes for already-launched requests
all retained still-applicable findings across the accepted Goal lineage
all law-authority and applicability classifications
all executable finding witnesses
all required-valid behavior and observation proofs
all compatibility and migration proofs
current Git factor topology and ancestry
same-generator history and elimination falsifiers
predicted-sibling probes or exhaustive-domain bases
```

The cut is cumulative, not latest-wave-only. A new subject changes freshness and
factor topology, not semantic history.

## Whole-corpus successor selection

Before mutation:

1. quotient the retained corpus into causal generators or proved exceptions;
2. map every affected production and proof factor;
3. assign `preserve | replace | collapse | retire | privatize |
   distinct-obligation`;
4. construct the smallest plausible subtractive candidate;
5. run all retained witnesses, required-valid proofs, compatibility proofs, and
   the strongest family falsifier against it;
6. select subtraction when it passes;
7. only after subtraction fails or is proved not meaningful consider the
   smallest replacement or direct restoration;
8. record each generator's successor disposition independently;
9. select one target invariant to evidence arrival order inside the cut, or
   retain explicit incomparable minima.

A same-generator named-member extension is forbidden without non-example
separation. A passing quotient candidate dominates additive repair.

Review remains closed while the target is realized. No intermediate head is
reviewable.

## Direct repair inside one successor

Successor selection is global; direct-repair admission is generator-local and
downstream of the subtractive contest.

For each unchanged-model generator:

- build one packet containing the cumulative cut, every finding and class mapped
  to that generator, every affected factor, the failed quotient candidate, and
  family-completeness proof;
- materialize against the exact current predecessor immediately before the
  generator's complete repair;
- materialize at most once for that generator in the cut;
- allow coherent commits until explicit generator completion;
- never materialize per finding or named member.

A passing subtractive candidate has no valid direct-repair packet. Architecture
successors do not use the gate.

## Request-local recovery and convergence

A verdictless terminal request contributes no semantic attempt, may receive one
fresh exact-request recovery, and blocks after a second verdictless result.
Required recovery remains part of the semantic barrier after invalidation.

After a successor becomes reviewable, restart the selected schedule on its final
head. Five consecutive distinct standard cleans remain required. No credit
crosses a material head change.

## Resumption and findings

Credit only exact receipts whose complete binding can be revalidated. If the
complete current evidence set cannot be resolved, restart from the initial
standard.

Every finding passes through `$review-fold`. Suggested patches remain reviewer
prose. Neither CAS nor Review Fold selects architecture or grants mutation.
