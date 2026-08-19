---
name: actuating
description: "Reconcile accepted intent with the exact current repository, validation, review, and publication state. Use bare $actuating for implementation, Ship publication, and exhaustive review convergence; use explicit implement, triage, remediation-plan, or review-closeout for bounded routes. Treat bugs as witnessed counterexamples, preserve their original provenance, classify current applicability, derive predicate-defined invalid families, distinguish detection from an admission frontier or minimal admission cut, and compare architectures by the invalid region they exclude at explicit claim strength. Git is the realized construction; CAS owns review attempts; Ship owns public effects. Actuating keeps no durable workflow store and invokes no Ledger gate."
---

# Actuating

Turn accepted intent and current owner-issued evidence into the next smallest
corrective action. Actuating is a **level-triggered architecture reconciler**:

```text
accepted goal
+ current Git tree
+ current validation
+ current CAS review evidence
+ current publication state
-> preserve, reconsider, realize, review, ship, close, or block
```

Actuating owns semantic synthesis and next-action judgment. It does not own the
facts it consumes and keeps no parallel durable world.

## Authority and fact ownership

| Question | Owner |
|---|---|
| What must be true? | accepted source or current user authority, compiled by `$goal-contract` |
| What code exists now? | Git commit and tree |
| What validation ran? | the exact test or verifier process |
| What review ran? | CAS terminal review receipt |
| What is published? | `$ship` and the provider |
| What observations form one class? | `$review-fold` |
| What admission frontier or cut matters? | `$actuating` |
| What architecture should exist? | `$actuating`, using `$universalist` |
| Is the result complete? | live Actuating judgment over current owner facts |

`$first-principles` controls the admissible premise basis.
`$universalist` nominates repository-native architectures and boundaries.
`$metanoetic` may expand the hypothesis space once on one unchanged decision
surface. `$reduce` challenges unearned factors and compensating guard movement.
Supporting skills never select the target architecture or grant mutation.
`$ship` alone performs public effects. CAS owns review execution and receipts.

Git is the realized construction. Analysis, prior threads, PR descriptions,
ADRs, Working Sets, and hotspot analyses are explanatory and may be stale; none
outranks the current tree.

## Public routes

| Intent | Route | Mutation | Terminal result |
|---|---|---:|---|
| Bare `$actuating` or `/goal $actuating` | implement -> Ship -> review-closeout | Explicitly authorized | `complete` |
| `$actuating implement` | reconcile and implement locally | Explicitly authorized | local `complete` |
| `$actuating triage` | acquire and classify review evidence | Forbidden | Review Fold and report |
| `$actuating remediation-plan` | recompile a target architecture without editing | Forbidden | non-executable plan |
| `$actuating review-closeout` | classify, reconsider as needed, realize, Ship, and converge | Explicitly authorized | `complete` |

An unqualified request to review, inspect, audit, or classify selects `triage`.
Mutation requires explicit implement, fix, resolve, address, or closeout intent.
These are workflow routes, not architectural change classes.

## Build the live Actuating View

At entry and after every material external change, observe:

```text
Goal
  accepted source, scope, compatibility, observations, publication posture

Subject
  repository, immutable base, current clean head, current tree

Incumbent
  boundaries, owner sets, representations, states, transitions, effects,
  observations, recovery, enforcement roles, bypasses, and residue

Evidence
  exact-head validation, CAS receipts, provider threads, incidents, migration
  or compatibility failures, and Ship/provider state
```

Re-read owner facts. Unknown, unavailable, or mismatched evidence receives no
credit. If architecture cannot be recovered from code and ordinary
documentation, treat that as a legibility defect—not a reason for an Actuating
store.

Read [architecture-reconciliation.md](references/architecture-reconciliation.md)
when mutation could change architecture or abstractions.

## Bugs as counterexamples

A bug is one witnessed counterexample to a named law. It is neither a patch
instruction nor the complete invalid family.

For boundary-relevant bugs, read
[semantic-hotspots.md](references/semantic-hotspots.md) and distinguish:

```text
witness provenance           where the bug actually occurred
current applicability        whether its law and route remain live now
detection surface            where incorrectness became visible
observational class          Review Fold's same-law evidence grouping
family predicate             Phi over domain D; F = { x in D | Phi(x) }
sanctioned admission         supported paths through which F can enter
frontier or admission cut    one seam, or a minimal covering set of seams
current owner set and status canonical | distributed | absent | contested | unknown
claim strength               proved | exhaustive-finite | bounded |
                             property-tested | sampled | hypothesized | unknown
```

Review Fold owns witness classification and observational classes. Actuating
owns family finalization, frontier partitioning, admission-cut selection,
semantic-hotspot judgment, and architecture selection.

A hotspot is predicate-defined and ephemeral:

```text
law x invalid family x owner set x frontier/cut x escape paths x witnesses
```

It is not a file, churn score, bug count, review count, or stored record. One
sanctioned-path witness may reopen architecture when it falsifies an attributed
universal law.

Skip deeper analysis for an isolated mistake inside an already-correct owner
when the incumbent already excludes the family and no sanctioned bypass remains.

## Architecture-closure test

Preserve the incumbent only when its existing semantic authority and frontier
or cut can exclude the predicate-defined family from every sanctioned admission
path at the stated claim strength without adding another independent
compensating guard, owner, representation, state dimension, transition law,
effect, compatibility mode, recovery mode, or escape path.

A convenient place for another check is not closure. If the law, authority,
representation, state space, admission coverage, or sanctioned escape surface
must change, reopen architecture before mutation.

## Architecture reconsideration

Reopen selection when evidence establishes semantic novelty, a sanctioned
universal-law falsifier, a predicate-defined hotspot, distributed/absent/
contested ownership, incomplete admission coverage, compensating guard
accretion, a live sanctioned bypass, or a smaller correctness-non-dominated
candidate.

Then:

1. Compile the Goal and freeze an incumbent-independent premise basis.
2. Run `$review-fold`; preserve witness provenance and current applicability.
3. Define the family predicate, domain, sanctioned admission relation, and
   claim strength.
4. Partition the observational class by frontier when necessary; derive one
   frontier or a minimal admission cut.
5. Ask `$universalist` for candidates using its bug-driven projection.
6. Use one bounded `$metanoetic` challenge when a materially different model,
   authority, representation, or cut remains plausible.
7. Ask `$reduce` to challenge compensating detection and unearned factors.
8. Establish the correctness Pareto frontier from explicit relation evidence.
9. Among correctness-equivalent candidates, select the least costly effective
   realization; preserve material incomparability.
10. State the architecture delta, disposition, evidence strength, and proof.

Accepted findings never map directly to patches. File proximity, bug count,
review order, implementation momentum, and incumbent familiarity do not select
architecture.

## Architecture Working Set

For a material implementation epoch retain, in the active thread or accepted
implementation specification:

```text
Bound head / Goal / incumbent / falsified laws
Witness provenance / current applicability / detection surface
Observational class
Family predicate / domain / sanctioned admission / claim strength
Current owner set and status / candidate semantic owner
Admission frontier or cut / escape paths / classified scar tissue
Selected target / preserve / introduce / retire
Disposition: eliminated | contained | obstructed | unresolved
Invalid region eliminated / admission coverage / derived guards preserved
Residual invalidity and owner / evidence strength / proof / reconsider when
```

The Working Set is not durable authority. Refresh it when the head, Goal,
applicability, family, owner set, frontier/cut, or target changes. Code wins over
analysis. Do not add a schema, predecessor chain, registry, score, or receipt.

## Realization

For each coherent edit:

```text
clean current head
-> exact intended delta
-> provisional diff
-> inspect complete diff and changed paths
-> run the strongest relevant verification
-> commit one coherent result
-> refresh the Actuating View
```

Git owns parent/successor identity, paths, ancestry, and recovery.

For bug-driven work, prove at the strongest honest owner or cut:

```text
current-witness rejection
family exclusion over the declared domain and admission relation
valid-behavior preservation
frontier/cut and escape-path coverage
elimination or interpreter adequacy
honest residual ownership
claim strength matching the evidence
```

Use one disposition:

```text
eliminated  family excluded at the stated claim strength
contained   risk bounded but family or external residual remains admitted
obstructed  required exclusion is unavailable under accepted constraints
unresolved  family, ownership, coverage, or proof remains unknown
```

Containment may satisfy only a Goal that explicitly accepts its residual. Never
call containment correct by construction. Compress accumulating same-law
examples into the strongest repository-supported law-level proof rather than
accumulating pointwise guards and tests.

Before Ship or closure-grade review, every authority and derived guard must have
a coherent role; eliminated families must have domain/admission/coverage proof;
contained residuals must be authorized and observable; selected escape paths
and retirements must be absent; and exact-head proof commands must pass.

## Review evidence and convergence

Read [review-contract.md](references/review-contract.md) for the exact static
policy.

Bind review to repository, immutable base, exact head, CAS target fingerprint,
Goal/acceptance digest, Review Contract digest, and optional pre-review Ship
observation digest.

Launch the standard plus four compact auxiliaries concurrently and never cancel
siblings. Every finding passes through `$review-fold`. For the unchanged head:

- the initial standard clean counts as clean one;
- all auxiliaries need terminal semantic verdicts;
- one request-local recovery is allowed for verdictless transport failure;
- later standard attempts are serial;
- five consecutive distinct standard cleans are required;
- findings reset the clean suffix;
- a material head change invalidates all prior credit by identity.

Credit only exact resolvable CAS receipts. On resume, reuse exact known handles
or receipt bytes; otherwise start a fresh full wave. Never reconstruct credit
from prose or claimed counts.

## Publication

Bare invocation and publication-bearing closeout hand the exact current Git and
validation tuple to `$ship`.

For existing-publication adoption, Ship first returns a read-only observation.
Actuating binds its digest into every review request, and final adoption
exact-matches that observation, current provider state, and reviewed head. No
Actuating event log or wall-clock comparison is used.

## Live closure

Read [closure.md](references/closure.md). Closure is reevaluated from current
owner facts and is never persisted.

A head is complete only while the Goal is satisfied; exact-head validation and
required review pass; architecture and retirements are fully realized; current
witnesses are rejected; eliminated families have predicate/domain/admission/
coverage proof; contained residuals are explicitly authorized and owned;
required derived guards remain coherent; publication matches when required;
and no applicable blocker remains.

## Hard rules

- No Actuating Ledger command, event log, durable workflow store, replacement
  database, bug Ledger, hotspot registry, score, threshold, receipt family, or
  migration layer.
- Do not map a bug directly to a patch or define a family as only its examples.
- Do not rewrite historical provenance as current-head provenance.
- Do not require one current owner when owner dilution may be the defect.
- Do not invent one frontier when a minimal admission cut is required.
- Do not conflate detection with admission or remove legitimate derived guards
  as compensating residue.
- Do not call guard multiplication or containment correct by construction.
- Do not claim recurrence, independence, elimination, or dominance beyond the
  available evidence strength.
- Do not claim completion from process status, stored verdict, publication, or
  rejection of observed examples alone.
- Complete object-level work before optional learnings or memory capture.
