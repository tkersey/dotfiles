---
name: actuating
description: "Reconcile accepted intent with the exact current repository, validation, review, and publication state. Use bare $actuating for implementation, Ship publication, and exhaustive review convergence; use explicit implement, triage, remediation-plan, or review-closeout for bounded routes. Reconstruct the incumbent architecture from Git, preserve it when closed under current obligations, and recompile it through First Principles, Universalist, bounded Metanoetic challenge, and Reduce when new evidence changes semantics, ownership, representation, or abstraction. Git is the realized construction; CAS owns review attempts; Ship owns public effects. Actuating keeps no durable workflow store and invokes no Ledger gate."
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

Actuating owns semantic synthesis and the next-action judgment. It does not own
the facts it consumes and keeps no parallel durable world.

## Authority and fact ownership

| Question | Owner |
|---|---|
| What must be true? | accepted source or current user authority, compiled by `$goal-contract` |
| What code exists now? | Git commit and tree |
| What validation ran? | the exact test or verifier process |
| What review ran? | CAS terminal review receipt |
| What is published? | `$ship` and the provider |
| What findings mean? | `$review-fold` classification |
| What architecture should exist? | `$actuating`, using `$universalist` |
| What should happen next? | `$actuating` |
| Is the current result complete? | live Actuating judgment over current owner facts |

`$first-principles` controls the admissible premise basis.
`$universalist` nominates repository-native architectures and boundaries.
`$metanoetic` may expand the hypothesis space once on one unchanged decision
surface. `$reduce` challenges unearned factors. Supporting skills never select
the target architecture or grant mutation. `$ship` alone performs public
effects. CAS owns review execution and receipts.

Git is the realized construction. A prose analysis, previous thread, PR
description, ADR, or Architecture Working Set is explanatory evidence and may
be stale; none outranks the current tree.

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
  accepted source, required outcomes, non-goals, authority, scope,
  compatibility, required observations, publication posture

Subject
  repository, immutable base, current clean head, current tree

Incumbent
  architecture reconstructed from the current tree

Validation
  exact commands, exact head, exit status, relevant output

Review
  exact CAS receipts available for the current head and review context

Publication
  current Ship/provider state for the exact base and head

Pressure
  current CAS findings, unresolved provider review threads, failing tests,
  incidents, migration failures, compatibility failures, and explicit reports
```

Do not reconstruct a hidden event history. Re-read owner facts. Unknown,
unavailable, or mismatched evidence receives no credit.

## Reconstruct the incumbent architecture

For any mutation that may affect a boundary, model the current tree:

```text
boundaries
canonical owners
state dimensions
events and transitions
effects and handlers
authoritative representations
public observations and compatibility
recovery and cancellation
proof mechanisms
live bypasses, parallel owners, and residue
```

Repository-native types, modules, schemas, APIs, tests, and executable behavior
are the evidence. When a material architectural decision cannot be recovered
from the code and its ordinary documentation, treat that as an architecture
legibility defect. Do not compensate with an Actuating-private database.

Read [architecture-reconciliation.md](references/architecture-reconciliation.md)
when mutation could change architecture or abstractions.

## Architecture-closure test

Preserve the incumbent and perform a realization correction only when all are
true:

```text
required behavior already exists in the incumbent semantic model
current canonical owner remains correct
no new state dimension, event, transition, effect, terminal mode, or ordering law
no ownership, authority, admitted-domain, or representation change
no new compatibility, recovery, cancellation, retry, or observation mode
no recurring causal failure indicates a missing shared mechanism
no active bypass, parallel owner, or obsolete representation must be removed
```

A changed implementation technique or complete source rewrite is not itself
architectural novelty. Conversely, hiding new semantics inside an existing
module does not preserve the architecture.

If any condition fails, reopen architecture selection before mutation.

## Architecture reconsideration

Recompile the architecture when current evidence establishes at least one:

- accepted source or compatibility requirements changed;
- a finding falsifies an incumbent law, owner, representation, or transition;
- a proposed repair needs a new semantic constructor or observable mode;
- a causal failure recurs after pointwise correction;
- one law is independently owned or represented in multiple places;
- a bypass or displaced mechanism remains live;
- a materially smaller candidate satisfies the same obligations;
- the repository cannot expose a coherent owner or transition model.

Then:

1. Compile the current Goal through `$goal-contract`.
2. Freeze an incumbent-independent premise basis with `$first-principles`.
3. Run `$review-fold` over all currently available applicable owner evidence.
4. Ask `$universalist` for concrete repository-native candidates.
5. Invoke `$metanoetic` once only when a materially different model, owner, or
   representation remains plausible.
6. Invoke `$reduce` when a candidate preserves or adds a disputable factor.
7. Select the smallest non-dominated candidate satisfying every current
   obligation and observation.
8. Name the preserved, introduced, replaced, and retired mechanisms.
9. Define exact proof commands and falsifiers.

Accepted findings never map directly to patches. Review order, reviewer
identity, campaign partitioning, implementation momentum, and the incumbent's
familiarity do not select architecture.

## Architecture Working Set

For a material implementation epoch, retain this compact working analysis in
the active thread or accepted implementation specification:

```text
Bound head:
Goal:
Incumbent model:
Falsified or newly required laws:
Selected target:
Canonical owners:
Preserve:
Introduce or replace:
Retire:
Proof commands:
Reconsider when:
```

The Working Set is not a durable authority artifact.

```text
same head and same evidence -> usable current hypothesis
head or material evidence changed -> refresh before the next affected edit
code contradicts Working Set -> code wins and reconciliation reopens
review contradicts Working Set -> architecture selection reopens
```

A PR description or ADR may retain rationale when humans need it. It remains
ordinary documentation. Do not create a schema, predecessor chain, registry, or
workflow receipt for the Working Set.

## Realization

A target architecture may require several bounded edits. Each edit should be
small enough that its complete diff, owner, affected paths, and proof are
inspectable, but no Actuating transaction or capability token is required.

For each edit:

```text
clean current head
-> exact intended delta
-> provisional diff
-> inspect complete diff and changed paths
-> run the strongest relevant verification
-> commit one coherent result
-> refresh the Actuating View
```

Git owns parent/successor identity, changed paths, ancestry, and recovery.
Uncommitted state is provisional. A committed result is not complete merely
because it exists.

Before Ship or closure-grade review:

- every required semantic mechanism exists in the current tree;
- every canonical owner excludes material bypasses;
- every selected retirement is actually absent or deliberately successor-mapped;
- every required proof command passes on the exact current head;
- no correctness-bearing production or proof mechanism remains unexplained by
  a current obligation.

## Review evidence and convergence

Read [review-contract.md](references/review-contract.md) for the exact static
policy.

Actuating binds one review context to:

```text
repository
immutable review base
exact current head
CAS target fingerprint
exact Goal and acceptance context digest
static Review Contract digest
optional Ship observation digest for existing-publication adoption
```

Launch the initial standard plus four compact auxiliary lenses concurrently
through owner-lived CAS requests. Never cancel siblings. Every finding passes
through `$review-fold` before mutation.

For the exact unchanged head:

- the initial-wave standard clean counts as clean one;
- all four auxiliaries must reach current terminal verdicts;
- verdictless terminal failure receives no semantic credit and may be recovered
  once for that exact request;
- later standard attempts run serially;
- five consecutive distinct standard cleans are required for final closeout;
- a standard finding resets the standard clean suffix;
- a material head change invalidates all prior review credit by identity.

Actuating may credit only exact CAS receipts it can currently resolve and
validate against the bound request and context. During one active run, retain
those receipts in context. On resume, reuse only exact known CAS handles or
receipt bytes. If the complete required evidence cannot be resolved, start a
fresh full wave. Never reconstruct credit from prose, a prior summary, or a
claimed count.

The compact auxiliary lenses are under `references/lenses/`. They are
non-orchestrating review instructions; a lens may recommend a specialist
handoff but may not launch its standalone workflow inside the 1+4 wave.

## Publication

Bare invocation and publication-bearing closeout hand the exact current Git and
validation tuple to `$ship`.

For ordinary PR publication, Ship returns owner-issued publication evidence
for the exact base/head tuple.

For existing-publication adoption:

1. Ship first returns an exact read-only observation of the current public
   base/head state.
2. Actuating includes that observation digest in the review context and every
   CAS request fingerprint before dispatch.
3. Final adoption exact-matches the same observation, current public state, and
   reviewed head.

The CAS receipts' echoed workflow bindings prove that publication observation
preceded review dispatch. No Actuating event log or wall-clock comparison is
used. A historical campaign lacking this binding must run a fresh observation
and review.

## Live closure

Read [closure.md](references/closure.md).

Closure is reevaluated from current owner facts. Actuating does not materialize
a closure receipt or persist a `complete` state.

A head is `complete` only while all applicable predicates hold:

```text
accepted Goal satisfied
required validation passes on the exact head
selected architecture is fully realized and residue retired
publication matches the exact head when required
the Review Contract is satisfied for the exact head when required
no applicable unresolved finding or blocker remains
```

Any changed input reopens reconciliation naturally.

## Hard rules

- No Actuating Ledger command, definition, event log, or durable workflow store.
- No Goal, Construction, Counterexample, Evidence, operation, or closure
  registration protocol.
- No replacement database, architecture registry, receipt family, or migration
  layer.
- Do not treat an analysis, plan, prior thread, or PR description as current
  repository truth.
- Do not patch a finding before testing architecture closure.
- Do not rerun architecture selection when the incumbent remains closed under
  the exact obligation.
- Do not claim recurrence when the relevant owner evidence is unavailable.
- Do not grant review credit without exact current-head CAS evidence.
- Do not claim completion from process status, a stored verdict, or publication
  alone.
- Complete object-level work before optional learnings or memory capture.
