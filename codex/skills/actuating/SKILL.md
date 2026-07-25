---
name: actuating
description: "Turn accepted intent and review evidence into correct-by-construction software through Goal Contracts, Counterexample Sets, Construction Contracts, and an Evidence Ledger. Use bare $actuating for implementation, Ship publication, and review convergence; use explicit implement, triage, remediation-plan, or review-closeout for their bounded routes. Begin every architecture or abstraction decision with OPERATE ARCHITECTONICALLY; when findings make an abstraction change live, integrate one bounded $glaze pass with $universalist before Actuating adjudicates. Actuating owns construction selection, orchestration, Counterexample evaluation, and the next action; Ledger is a non-executing artifact substrate and Ship alone owns public effects."
---

# Actuating

Turn accepted intent into a lawful construction, directly orchestrated effects,
independent falsification, and an evidence-backed closure judgment.

## Authority kernel

Use exactly four authoritative per-goal artifact families:

1. `goal-contract/v3` — accepted semantics, authority, scope, compatibility,
   laws, and acceptance, compiled by `$goal-contract`.
2. `counterexample-set/v1` — classified witnessed falsifications, authored by
   `$review-fold`.
3. `construction-contract/v3` — the selected architecture, four compared
   candidate families, factor surfaces, supersession, proof obligations,
   preserved observations, and retirements, authored by `$actuating` after a
   `$universalist` nomination and, when required, one `$reduce` challenge.
4. `actuating-evidence-event/v1` — append-only observations whose event bodies
   retain their domain owners.

The Goal Contract is the sole semantic-authority artifact. The Counterexample
Set is the sole classified-bug artifact. The Construction Contract is the sole
architecture-selection artifact. The Evidence Ledger is the sole mutable
per-goal truth. Read [artifact-kernel.md](references/artifact-kernel.md) for the
owner map.

Plans, CAS receipts, Ship receipts, verifier output, work graphs, and Ledger
`state` or `project` views are supporting evidence or discardable structural
aids. An Actuating-authored closure receipt is a semantic report, not another
authority family.

## Owner boundary

Actuating owns:

- correct-by-construction implementation;
- evaluation of current Counterexample classes against the current
  Construction;
- initial and successor Construction selection;
- review and repository-effect orchestration;
- construction and ownership of the static Review Contract;
- semantic evaluation of CAS owner facts and review credit;
- the next legal action;
- application of the closure theorem and authorship of its semantic receipt.

`$review-fold` must classify witnessed facts before Actuating selects any
repair. `$universalist` nominates the essential boundary shape. When an
abstraction change is live, `$glaze` performs one bounded generative
escalation and `$universalist` lowers any material result into its nomination.
`$reduce` may then challenge the nominated factors by testing congruent
quotients, ablations, and recomposition. The composition order is
`activate -> nominate -> glaze once when triggered -> lower -> challenge once
-> adjudicate`; Actuating alone performs the adjudication. Neither supporting
skill, review prose, nor an optional plan or Reduction Certificate selects a
Construction, Repair Disposition, operation, next action, or closure.

Ledger may materialize, canonicalize, validate, append, replay, and emit
requested disposable structural projections. Ledger never executes repository
changes; evaluates CAS facts or review credit; interprets Ship evidence; selects
a repair, Construction, or next action; grants mutation; emits a semantic
closure verdict; or authors the closure receipt. Before the first Ledger
command in a workflow, load `$ledger` and complete `$ledger ensure` once. Then
require Ledger 0.13.0 or newer and Seq 0.5.0 or newer, apply the current
zero-legacy Ledger and CAS runtime gates, and use the exact transient schemas
and one-shot capability law in
[evidence-ledger.md](references/evidence-ledger.md). Apply the same Actuating
gate when entering from a standalone Goal Contract or Review Fold handoff.
Construction v1 and v2 are unsupported. Do not migrate, translate, replay, or
consult their stored state as current authority; start a fresh goal-local
Evidence store and ignore the legacy data.

`$ship` is the sole owner of public PR or tracker effects. Actuating supplies a
current `ready-to-ship` proof and records Ship's returned receipt as evidence;
it never performs the public effect itself.

## Public modes

| Intent | Route | Mutation | Terminal result |
|---|---|---:|---|
| Bare `$actuating` or `/goal $actuating` | implement -> Ship -> review-closeout | Authority-bound | `complete` |
| `$actuating implement` | implementation only | Authority-bound | Local `complete` |
| `$actuating triage` | acquire and classify review | Forbidden | Counterexample Set and report |
| `$actuating remediation-plan` | propose a successor Construction | Forbidden | Non-executable Construction Contract |
| `$actuating review-closeout` | repair, ablate, Ship when required, and re-review | Authority-bound | `complete` |

An unqualified request to review, inspect, audit, or classify selects `triage`.
Require explicit implement, fix, resolve, address, or closeout intent before
mutation.

## Architectonic decision gate

At the beginning of every Actuating process that selects, preserves, changes,
or ablates architecture or abstraction, and before `$universalist` nominates a
boundary, state exactly:

~~~text
OPERATE ARCHITECTONICALLY
~~~

This is an activation instruction, not evidence, authority, or a receipt.

After `$review-fold` has classified any findings, invoke `$glaze` exactly once
after the first `$universalist` nomination and before candidate adjudication
when an accepted class:

- makes `architecture-repair` or `ablation-repair` a live route;
- challenges the sufficiency of the current representation, owner, admitted
  domain, equivalence, normalization, or information retention;
- triggers the Causal recurrence gate; or
- would otherwise add a validator, correlation, cache, bypass, compatibility
  branch, or path-dependent recovery to reconstruct forgotten information.

Use the Glaze pass to demand a materially new frame, invariant, mechanism,
artifact, or breakthrough candidate and to resist premature
`realization-preserve`. Then require `$universalist` to reclassify and lower
each material result into a repository-native nomination before `$reduce`
challenges the selected candidate version and Actuating adjudicates.

Record this compact, non-authoritative view:

~~~text
Architectonic Escalation
Trigger:
Abstraction pressure:
Glaze result: material-reframe | no-material-reframe | blocked
Material frame, invariant, mechanism, or artifact:
Universalist reclassification: retain | split | escalate | obstruct
Candidate-family delta:
Falsifier:
~~~

Compile the view into the existing Construction candidate comparison, factor
surfaces, supersession, proof obligations, and falsifiers; do not create a
fifth authority artifact or an unknown `construction-contract/v3` field.
`$glaze` neither classifies findings nor nominates, selects, authorizes, or
closes. If it yields no material reframe, record `no-material-reframe` and
continue with the evidenced candidate universe. Do not repeat Glaze for the
same finding set and nomination version.

## Construction procedure

1. Compile the accepted source with
   [$goal-contract](../goal-contract/SKILL.md). Do not select architecture in
   the Goal Contract. Require its returned canonical artifact, non-null
   `artifact_id`, and `goal_contract_registered` event before continuing.
2. Enter the Architectonic decision gate. Inspect the repository boundary,
   existing owner, host enforcement capabilities, and required observations.
   Apply `$universalist` at every changed or preserved boundary and retain its
   compact nomination: candidate, owner, laws, observations, residuals,
   invalidators, and falsifier. When an abstraction-change trigger is present,
   complete the bounded Glaze pass and Universalist reclassification before
   continuing.
3. Compile exactly four ordinary candidate families in canonical order:
   `realization-preserve`, `admitted-domain-restriction`,
   `representation-or-owner-strengthening`, and `ablation-normalization`.
   Give each candidate an explicit factor inventory and falsifier, and mark
   exactly one selected. Classify the nominated candidate's factors. Invoke
   `$reduce` exactly once for that candidate version when it
   adds or preserves an independent semantic owner, parallel representation,
   bypass, compatibility branch, semantic mechanism, or apparently dominated
   residue. Otherwise record `Reduction: not-required`. When an accepted
   Counterexample class can lead to mutation, record this
   compact view over the current Construction selection before choosing an
   operation; it is not a fifth authority artifact:

   ~~~text
   Repair Disposition
   Law:
   Owner:
   Reduction: not-required | minimal | dominated | incomparable | essential-shape-gap | blocked
   Route: delete | consolidate | edit | add
   Why not smaller:
   Falsifier:
   ~~~

   A finding authorizes the invariant, not its suggested implementation.
   Choose the least additive route that satisfies the law; `add` must explain
   why `delete`, `consolidate`, and `edit` are insufficient.
4. Adjudicate the nomination and challenge. Select the smallest non-dominated
   Construction that satisfies every Goal law, makes invalid states
   unrepresentable where feasible, and names exact proof and retirement
   obligations. Record the predecessor and successor factor surfaces and a
   total supersession partition: every factor is preserved, retired,
   introduced, or explicitly replaced. A `dominated` challenge selects the
   smaller admissible candidate; `incomparable`, `essential-shape-gap`, or
   `blocked` requires an Actuating disposition or obstruction, never recursive
   skill ping-pong.
   Follow
   [construction-contract.md](references/construction-contract.md).
5. Set the selected Construction draft's `artifact_id` to JSON `null`, then
   materialize and register it before selecting any operation:

   ~~~bash
   ledger --source actuation --repo <repo> --goal <goal-id> \
     append --input <construction-contract.json>
   ~~~

   Require `construction-contract/v3` and `actuating-append-result/v1`, retain
   its complete canonical `artifact`, exact-match its non-null `artifact_id` to
   `artifact.artifact_id`, and retain `event_digest` as the
   `construction_contract_registered` observation. Only the returned artifact
   is the current Construction; Ledger does not select or revise it.
6. For each repository effect, Actuating selects one exact operation projected
   by the current Goal, returned Construction, and live subject, including its
   `expected_subject_digest`. For Git repositories, select the checked-in
   `scripts/subject_observation.py` command with the Goal's literal repository
   and path scope. Its `actuating-subject-observation/v1` requires two identical
   captures of HEAD, index, scoped worktree, and selected ignored or unignored state.
   Before the effect the executor reruns that exact command. A mismatch aborts without effect.
   The executor cannot choose another observer or broaden scope, and Ledger
   compares only the opaque digest.
7. Run the Construction's exact verifier and falsifier observations. Record
   their immutable outputs and the resulting subject identity in the Evidence
   Ledger using [evidence-ledger.md](references/evidence-ledger.md).
8. Re-evaluate the current artifacts and observations. Actuating selects the
   next operation, review action, Ship handoff, closure judgment, or blocker.

The one-operation law is `select -> prepare -> effect -> observe -> evaluate ->
select or close`. Actuating performs the semantic evaluation; Ledger may only
record and replay its inputs. No stage may smuggle a second repository effect.

A document, operation envelope, validator pass, Ledger append, review result,
or Construction Contract never grants mutation by itself. Mutation requires
current accepted authority, a current Construction, a matching subject, and an
Actuating-selected in-scope operation.

## Goal-causal lineage

Treat subject freshness and causal decision lineage as independent
coordinates. A commit, publication, or other material subject change makes
subject-bound proof, operations, review bindings, and review credit stale. It
does not erase prior Construction decisions or Counterexample-class history
for the same `goal_id`.

Only the first Construction in the current authoritative v3 lineage for a
`goal_id` may use `mode: initial` with empty `predecessor_refs`. Every later
Construction, including one compiled after a successor Goal Contract or
subject rebind, must name the exact current Construction as its sole
predecessor and classify what it preserves, falsifies, replaces, or retires.

Before accepting a new Counterexample Set, resolve prior Sets for the Goal.
When a stable class recurs, require the new Set's `predecessor_refs` to include
the most recent Set carrying that class, as `$review-fold` requires. Missing
lineage blocks successor selection and returns the Set to `$review-fold`; it
does not make the class appear novel.

The Causal recurrence gate folds the full goal-local Construction and
Counterexample lineage across subject revisions. A changed Goal law or
applicability may reject, supersede, or separate prior classes with explicit
evidence, but subject change alone cannot. The falsifier is a stable accepted
class recurring after a subject rebind while the recurrence fold reports no
recurrence.

## Counterexample procedure

Every witnessed bug, failing test, incident, compatibility failure, or review
finding passes through `$review-fold` before repair. It separates facts from
suggestions and quotients duplicates into stable law-and-boundary classes.

Actuating then determines whether each accepted class is:

- a realization defect in an otherwise valid Construction;
- an architecture defect requiring a successor Construction;
- an ablation defect requiring removal of dominated residue; or
- blocked by missing authority or evidence.

Before deciding among these dispositions, enter the Architectonic decision
gate. A `realization` classification is not established merely because the
existing boundary can accept another local edit. When a finding challenges the
current abstraction under the gate's triggers, run the bounded Glaze pass,
lower any material reframe through `$universalist`, and compare it in the
successor Construction before selecting the repair class.

The successor records falsified and preserved predecessor claims, excluded
Counterexample classes, stronger proof, and retirements. It must preserve
already-valid observations. A witnessed example is not resolved until the
Construction excludes its class or proves it instance-specific.

An accepted Review Fold makes the current Construction stale. Its successor
uses `accepted-review-fold`, binds the latest Counterexample Set on the exact
current subject, and records the same canonical accepted-class list in both
`counterexample_class_refs` and `evaluated_class_refs`. A zero-class successor
is legal only when it clears a nonempty predecessor debt set on that subject.
Subject rebinding refreshes this exact-subject evaluation without resetting the
goal-causal lineage.
Predecessor-factor proof refs resolve through the predecessor artifact;
candidate, successor-factor, addition, and completeness refs resolve through
the successor artifact.

### Causal recurrence gate

Before selecting an affected repair, fold the current and predecessor
Counterexample Sets against the current and predecessor Constructions for this
Goal. Trigger the gate when either:

- one accepted class recurs after a repair; or
- two accepted classes across subject revisions depend on the same missing
  observation, authority, correlation, or Construction factor.

Shared filenames, diff size, or similar wording do not establish a common
cause. When the evidence does, record this compact view over the successor
Construction decision:

~~~text
Causal Recurrence Disposition
Evidence and class refs:
Shared cause:
Current Construction factor:
Candidate comparison: realization preserve / admitted-domain restriction / representation strengthening / ablation normalization
Disposition: instance-specific | architecture-repair | ablation-repair | blocked
Why another local repair is sufficient or forbidden:
Proof:
Falsifier:
~~~

This is not a fifth authority artifact. The successor Construction carries the
complete cluster in `counterexample_class_refs`, names the shared cause in
`falsified_predecessor_claims`, and owns the selected proof and retirements.
Do not select another affected repository mutation after the gate triggers.
The recurrence trigger also makes abstraction change live under the
Architectonic decision gate, so complete the single Glaze pass and
Universalist reclassification before this candidate comparison.
`instance-specific` is legal only when a non-example proof separates the
cluster and establishes that the current representation remains sufficient.
Otherwise select an architecture or ablation successor, or block.

When the repeated route adds validators, correlations, caches, bypasses, or
path-dependent recovery to recreate information the selected representation
forgets, require the Reduction challenge to test the existence of that repair
mechanism—not merely whether its newest implementation is locally minimal.
Compare all four v3 candidate families before retaining residual validation
authority. Ledger may replay the cited history but never computes shared cause
or the disposition.

Before dispatching fresh review after a repair, compare the realized production
delta with the challenged candidate. Line count is only a reclassification
signal. Reinvoke `$reduce` once for a successor candidate only when the delta
introduces or materially changes an independent semantic owner, parallel
representation, bypass, compatibility branch, semantic mechanism, or dominated
residue. Otherwise retain the pre-mutation challenge. Actuating still selects
the successor Construction and next operation; the same candidate and evidence
never enter a recursive reduction loop.

## Review convergence

Follow [review-contract.md](references/review-contract.md). Preserve all of
these laws:

- bind standard plus four auxiliary requests before dispatch;
- launch the initial 1+4 wave concurrently;
- never cancel a launched sibling because another request finds a defect or
  loses transport;
- treat a verdictless terminal failure as zero semantic credit and rerun only
  that request once on the same subject and binding with a fresh attempt;
- count the successful full-wave standard clean as clean attempt one;
- run four later standard attempts serially;
- require five consecutive distinct standard clean attempts;
- reset all review credit after any material review-subject change.

Actuating owns dispatch timing and consumes CAS's structured owner receipts.
With `$review-fold`'s current Counterexample Sets, Actuating decides whether a
CAS attempt has a current semantic verdict, earns credit, resets the streak, or
requires a successor Construction. Ledger may record receipt references and
project structural history, but it does not dispatch CAS or translate any CAS
field or process status into `clean`, `findings`, or credit.

## Publication and closure

Bare mode and publication-bearing review closeout hand a current
`ready-to-ship` proof to [$ship](../ship/SKILL.md). After Ship returns current
owner-issued evidence, Actuating records it and begins or resumes review on the
published subject.

Apply [closure.md](references/closure.md) only to current artifacts and
observations. Actuating authors the resulting `actuating-closure-receipt/v1`;
Ledger neither emits the verdict nor authors the receipt. `$proof-patch` may
render a complete result but cannot decide it. Complete the handoff or report
before the source-memory checkpoint; learning status cannot delay, invalidate,
or roll back delivery closure.

## Fail closed

Always block on stale or missing authority, Goal, Construction, or subject;
unresolved accepted or blocked Counterexamples; out-of-scope operations;
incomplete proof or retirement; missing Construction or recurring-class
predecessor lineage; a public effect outside Ship; or any attempt by Ledger or
an executor to take Actuating's semantic authority. For a
`final-closeout` `complete` verdict, also block on stale or missing review
identity, CAS receipt mismatch, unresolved request-local recovery, or fewer than
five current-subject standard clean attempts, and—when the Goal requires
publication—stale or missing Ship identity. A `ready-to-ship` verdict requires
neither publication nor review evidence; `local-implementation` `complete`
requires neither and rejects both as inapplicable.
