---
name: actuating
description: "Reconcile accepted intent with the exact current repository, validation, review, and publication state. Treat bugs as witnessed counterexamples to attributed Goal laws, synthesize sound counterexample theories and repository-native architectures, and make every post-elimination witness that falsifies the active claim revoke its lease before another mutation. Git is the realized construction; CAS owns review attempts; Ship owns public effects. Actuating keeps no durable workflow store and invokes no Ledger gate."
---

# Actuating

Turn accepted intent and current owner-issued evidence into the next smallest
corrective action. Actuating is a **level-triggered architecture reconciler**:

```text
accepted Goal
+ exact current Git tree
+ current validation
+ current CAS review evidence
+ current Ship/provider state
-> preserve, reconsider, realize, review, ship, close, or block
```

Actuating owns semantic synthesis and next-action judgment. It owns no parallel
durable world.

## Authority and fact ownership

| Question | Owner |
|---|---|
| What must be true? | accepted source or current user authority, compiled by `$goal-contract` |
| What code exists now? | Git commit and tree |
| What validation ran? | the exact test or verifier process |
| What review ran? | CAS terminal review receipt |
| What is published? | `$ship` and the provider |
| What does a finding prove? | `$review-fold` classifies evidence and Goal authority |
| What counterexample theory survives? | `$actuating`, challenged by `$metanoetic` and architectonic adjudication |
| What architecture should exist? | `$actuating`, using `$universalist` |
| Is the result complete? | live Actuating judgment over current owner facts |

`$first-principles` controls the admissible premise basis. `$review-fold`
preserves witness provenance, classifies current applicability, and states
whether a finding is entailed by the accepted Goal. `$metanoetic` may generate
one bounded challenger on one unchanged theory decision surface. **OPERATE
ARCHITECTONICALLY** to adjudicate the governing law, semantic domain, ownership,
construction, composition, and proof. `$universalist` nominates repository-native
architectures. `$reduce` challenges unearned factors, unnecessary precision, and
compensating guards.

Supporting skills never select the target architecture or grant mutation.
`$ship` alone performs public effects. CAS owns review execution and receipts.

Git is the realized construction. Working Sets, hotspot analyses, PR
descriptions, and prior threads are explanatory hypotheses; none outranks the
current tree.

## Public routes

| Intent | Route | Mutation | Terminal result |
|---|---|---:|---|
| Bare `$actuating` or `/goal $actuating` | implement -> Ship -> review-closeout | Explicitly authorized | `complete` |
| `$actuating implement` | reconcile and implement locally | Explicitly authorized | local `complete` |
| `$actuating triage` | acquire and classify review evidence | Forbidden | Review Fold and report |
| `$actuating remediation-plan` | recompile a target architecture without editing | Forbidden | non-executable plan |
| `$actuating review-closeout` | classify, reconsider, realize, Ship, and converge | Explicitly authorized | `complete` |

An unqualified request to review, inspect, audit, or classify selects `triage`.
Mutation requires explicit implement, fix, resolve, address, or closeout intent.
These are workflow routes, not architectural change classes.

Review-bearing routes accept request-local scheduling modifiers:

| Modifier | Selection | Effect |
|---|---|---|
| `parallel-reviews` | default when omitted | initial standard and four auxiliaries run concurrently |
| `serial-reviews` | explicit opt-in | initial standard and each auxiliary run serially in contract order |

These modifiers change review dispatch only. They do not select a route, alter
mutation authority, remove a lens, weaken receipt quality, or change convergence.

## Build the live Actuating View

At entry and after every material external change, observe:

```text
Goal
  accepted laws, scope, compatibility, required valid behavior,
  required observations, publication posture

Subject
  repository, immutable base, current clean head, current tree

Incumbent
  boundaries, owner sets, representations, states, transitions, effects,
  observations, recovery, enforcement roles, bypasses, and residue

Evidence
  exact-head validation, CAS receipts, provider threads, incidents,
  migration/compatibility failures, and Ship/provider state
```

Unknown, unavailable, or mismatched evidence receives no credit. If architecture
cannot be recovered from code and ordinary documentation, treat that as a
legibility defect—not a reason for an Actuating store.

Read [architecture-reconciliation.md](references/architecture-reconciliation.md)
when mutation may change architecture or abstractions.

## Review-finding authority

Before a review finding becomes current counterexample pressure, require
`$review-fold` to classify its relationship to accepted authority:

```text
entailed
  demonstrable consequence of an accepted Goal law;
  may falsify the current implementation or architecture

strengthening
  beneficial property not required by the current Goal;
  non-blocking follow-up unless authority adopts it

preference
  reviewer-selected design preference with no current correctness obligation;
  reject as current liability

new-requirement
  legitimate requirement not yet in the Goal;
  reopen Goal authority before implementation

underdetermined
  current evidence cannot decide whether the property is required;
  block that decision and seek authority
```

Only `entailed` findings may automatically enter the current counterexample
theory. Review evidence may falsify accepted semantics; it may not continuously
author new semantics.

## Bugs as counterexamples

A bug is one witnessed counterexample to a named law. It is neither a patch
instruction nor the complete invalid family.

For boundary-relevant bugs, read
[semantic-hotspots.md](references/semantic-hotspots.md). A selected theory is:

```text
Theta = (Omega, Alpha, L, Phi, A, O, C, Vh, Q)
```

where:

```text
Omega  semantic observation domain
Alpha  witness/incumbent/candidate interpretations into Omega
L      governing law
Phi    abstract invalidity predicate or generator
A      sanctioned admission semantics
O      current and candidate owner model
C      one admission frontier or a minimal admission cut
Vh     validity horizon over version, schema, environment, and time
Q      weakest supporting claim strength
```

For candidate `K`, comparison universe `U_K`, admitted behavior
`B_K subset U_K`, and `alpha_K : U_K -> Omega`, concrete safety requires over
the declared validity horizon `Vh`:

```text
Totality
  alpha_K(u) is defined for every u in U_K

Violation reflection
  Bad_L(u) -> Phi(alpha_K(u))

Abstract exclusion
  b in B_K -> not Phi(alpha_K(b))

Goal adequacy
  every Goal-required valid behavior remains admitted and every
  Goal-required observation retains its accepted meaning
```

Diagnostic exactness is separate. A sound conservative abstraction may reject
optional safe behavior without leaving residual incorrectness.

## Architecture closure

Preserve the incumbent only when its existing authority and frontier/cut can
exclude the selected invalid family from every sanctioned path at the stated
strength, through a total violation-reflecting interpretation, while preserving
every required valid behavior and observation.

A convenient location for another check is not closure. Reopen architecture when
the law, semantic domain, interpretation, owner, representation, state space,
admission coverage, recovery semantics, or sanctioned escape surface must
change.

## Elimination is a revocable theory lease

`eliminated` is a head- and evidence-relative claim, not stored truth.

A currently applicable `entailed` witness that belongs to or satisfies the
reconsideration falsifier of the eliminated family, within its declared validity
horizon, **revokes that elimination immediately**. A same-law witness from an
established disjoint family or outside that horizon does not falsify the scoped
claim. Unknown family or horizon relation is `unresolved`, not revocation or
retention by assumption.

Before any further mutation, read
[post-elimination-falsification.md](references/post-elimination-falsification.md)
and identify the failed premise:

```text
Goal/law authority
current applicability
validity horizon Vh
Omega / Alpha
Phi or family partition
comparison universe U / admitted behavior B
sanctioned admission A / frontier or cut C
owner model O
realization K
proof or path coverage
claim strength Q
```

Then choose exactly one:

```text
retain-theory-reprove
revise-theory
split-theory
revise-admission
revise-interpretation
revise-owner
reopen-goal
follow-up
reject-finding
unresolved
```

A direct patch is allowed only after `retain-theory-reprove` localizes the
failure to realization or proof while the witness remains inside the existing
family, interpretation, and covered admission model. Otherwise recompile before
mutation. Unknown failure location is `unresolved`.

## Generative reach and sibling prediction

A family theory earns elimination by predicting more than the examples already
seen.

Before the first or any successor `eliminated` disposition, state either:

```text
an exhaustive finite-domain proof
```

or:

```text
predicted sibling counterexamples
the law and generator that imply them
sanctioned paths that could admit them
the owner mechanism intended to exclude them
the probes used to search for them
```

Passing repaired examples alone never reissues elimination. Failed sibling probes
reopen the theory or proof. When no meaningful sibling prediction or exhaustive
argument is available, retain `hypothesized`, `bounded`, `contained`, or
`unresolved` rather than claiming family-level closure.

## Architecture reconsideration

When architecture or theory reopens:

1. Compile the current Goal and freeze an incumbent-independent premise basis.
2. Run `$review-fold`; preserve provenance, applicability, law authority, and
   post-elimination relation.
3. Derive the smallest ordinary counterexample theory and its falsifier.
4. Run one bounded `$metanoetic` challenger when the theory is
   detection-shaped, enumerative, representation-bound, violation-erasing,
   contradicted, owner/topology-captive, or merely one plausible frame.
5. **OPERATE ARCHITECTONICALLY.** Retain, replace, combine, split, or leave the
   theory unresolved.
6. Derive one admission frontier or minimal cut.
7. Ask `$universalist` for repository-native candidates and explicit family-level
   falsifiers.
8. Permit one bounded theory/architecture co-refinement before selection.
9. Ask `$reduce` to reject compensating detection, witness enumeration,
   violation erasure, unnecessary precision, and unearned factors.
10. Establish the correctness Pareto frontier before minimizing realization cost.
11. State the selected theory, architecture delta, proof, predicted siblings,
    and reconsideration falsifier before mutation.

Accepted findings never map directly to patches. File proximity, bug count,
review order, implementation momentum, and incumbent vocabulary do not select
the theory or architecture.

## Architecture Working Set

For a material implementation epoch retain in the active thread or accepted
implementation specification:

```text
Bound head / Goal / incumbent / falsified laws
Witness provenance / applicability / law authority / detection surface
Observational class
Theta_0 / Metanoetic challenger / architectonic disposition
Omega / Alpha / Phi / A / O / C / Vh / Q
Safety adequacy / Goal adequacy / diagnostic exactness
Selected target / preserve / introduce / retire
Current elimination lease, if any:
  issued head / theory / family / validity horizon / reconsideration falsifier
  proof / claim strength
  predicted siblings / probes
Post-elimination falsifier, if any:
  witness / failed premise / lease disposition
Successor sibling predictions / probe results
Disposition: eliminated | contained | obstructed | unresolved
Residual invalidity and owner / proof / reconsider when
```

The Working Set is ephemeral. Refresh it whenever the head, Goal, theory,
interpretation, authority classification, failed premise, owner set, cut, or
target changes. Do not add a schema, registry, predecessor chain, score, receipt,
or durable store.

## Realization

For each coherent edit:

```text
clean current head
-> exact intended delta
-> provisional diff
-> inspect complete diff and changed paths
-> run the strongest relevant verification
-> commit one coherent result
-> refresh the live view
```

Git owns parent/successor identity, paths, ancestry, and recovery.

For bug-driven work prove:

```text
current-witness rejection
totality and violation reflection
abstract exclusion
required-valid and required-observation preservation
frontier/cut and escape-path coverage
family-level or exhaustive proof
predicted-sibling probes
honest residual ownership
claim strength matching the weakest evidence
```

Use:

```text
eliminated  concrete law violations excluded at the stated strength
contained   concrete invalidity, path/reflection coverage, or an external
            residual remains admitted
obstructed  required exclusion is unavailable under accepted constraints
unresolved  theory, authority, safety/Goal adequacy, ownership, or proof unknown
```

Conservative exclusion of optional safe behavior is not containment.

## Review evidence and convergence

Read [review-contract.md](references/review-contract.md).

Bind review to repository, immutable base, exact head, each request's owner-issued
CAS target fingerprint, Goal/acceptance digest, Review Contract digest, and
optional pre-review Ship observation digest. The shared review context binds the
Git subject; the instruction-sensitive CAS target fingerprint is receipt-scoped
and never caller-recomputed before dispatch.

For the unchanged head:

- select `parallel-reviews` when no scheduling modifier is supplied;
- in `parallel-reviews`, launch the initial standard plus four compact
  auxiliaries concurrently and never cancel siblings;
- in `serial-reviews`, launch the initial standard, footgun-finder,
  invariant-ace, complexity-mitigator, and fresh-eyes one at a time, adjudicating
  each terminal result before dispatching the next;
- require every terminal semantic verdict and allow one request-local recovery
  for verdictless transport failure;
- count a clean initial standard as clean one;
- run later standard confirmations serially;
- require five consecutive distinct standard cleans;
- after a material head change, reset all credit and restart the selected
  schedule at its initial standard;
- in `serial-reviews`, never dispatch the next review against a head that an
  adjudicated finding will replace.

Every finding passes through `$review-fold`. Credit only exact CAS receipts.
Never reconstruct credit from prose, process exit, or claimed counts.

## Publication and live closure

Bare invocation and publication-bearing closeout hand exact Git and validation
facts to `$ship`.

Read [closure.md](references/closure.md). Completion is recomputed from current
owner facts. It requires current Goal satisfaction, exact-head validation,
realized architecture and retirements, authoritative finding classification,
sound family exclusion, no unadjudicated post-elimination falsifier, required
publication, and exact-head review convergence.

## Hard rules

- No Actuating Ledger command, event log, durable workflow store, replacement
  database, bug Ledger, hotspot registry, score, threshold, receipt family, or
  migration layer.
- Do not map a finding directly to a patch.
- Do not let review author a new Goal silently.
- Do not preserve an `eliminated` disposition after a current entailed witness
  falsifies the exact family claim inside its validity horizon.
- Do not mutate under a revoked lease before failed-premise localization.
- Do not reissue elimination from repaired examples alone.
- Do not call sibling discovery after the fact a prior prediction.
- Do not claim recurrence, theory adequacy, family exclusion, or convergence
  beyond available evidence.
- Preserve direct owner-local repair for an isolated mistake when the incumbent
  already excludes the family and no prior elimination claim was falsified.
- Complete object-level work before optional learnings or memory capture.
