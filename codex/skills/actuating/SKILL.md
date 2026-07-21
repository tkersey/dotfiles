---
name: actuating
description: "Turn accepted intent and review evidence into correct-by-construction software through Goal Contracts, Counterexample Sets, Construction Contracts, and an Evidence Ledger. Use bare $actuating for implementation, Ship publication, and review convergence; use explicit implement, triage, remediation-plan, or review-closeout for their bounded routes. Actuating owns construction selection, orchestration, Counterexample evaluation, and the next action; Ledger is a non-executing artifact substrate and Ship alone owns public effects."
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
3. `construction-contract/v1` — the selected architecture, proof obligations,
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
repair. `$universalist` nominates the essential boundary shape; `$reduce` may
challenge its factors by testing congruent quotients, ablations, and
recomposition. The composition order is `nominate -> challenge once ->
adjudicate`; Actuating alone performs the adjudication. Neither supporting
skill, review prose, nor an optional plan or Reduction Certificate selects a
Construction, Repair Disposition, operation, next action, or closure.

Ledger may materialize, canonicalize, validate, append, replay, and emit
requested disposable structural projections. Ledger never executes repository
changes; evaluates CAS facts or review credit; interprets Ship evidence; selects
a repair, Construction, or next action; grants mutation; emits a semantic
closure verdict; or authors the closure receipt. Before the first Ledger command
in a workflow, load `$ledger` and complete `$ledger ensure` once.
Then apply the current zero-legacy Ledger and CAS runtime gates and use the exact
transient schemas and one-shot capability law in
[evidence-ledger.md](references/evidence-ledger.md). Apply the same Actuating
gate when entering from a standalone Goal Contract or Review Fold handoff.

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

## Construction procedure

1. Compile the accepted source with
   [$goal-contract](../goal-contract/SKILL.md). Do not select architecture in
   the Goal Contract. Require its returned canonical artifact, non-null
   `artifact_id`, and `goal_contract_registered` event before continuing.
2. Inspect the repository boundary, existing owner, host enforcement
   capabilities, and required observations. Apply `$universalist` at every
   changed or preserved boundary and retain its compact nomination: candidate,
   owner, laws, observations, residuals, invalidators, and falsifier.
3. Before selecting a Construction, classify the nominated candidate's
   factors. Invoke `$reduce` exactly once for that candidate version when it
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
   obligations. A `dominated` challenge selects the smaller admissible
   candidate; `incomparable`, `essential-shape-gap`, or `blocked` requires an
   Actuating disposition or obstruction, never recursive skill ping-pong.
   Follow
   [construction-contract.md](references/construction-contract.md).
5. Set the selected Construction draft's `artifact_id` to JSON `null`, then
   materialize and register it before selecting any operation:

   ~~~bash
   ledger --source actuation --repo <repo> --goal <goal-id> \
     append --input <construction-contract.json>
   ~~~

   Require `actuating-append-result/v1`, retain its complete canonical
   `artifact`, exact-match its non-null `artifact_id` to
   `artifact.artifact_id`, and retain `event_digest` as the
   `construction_contract_registered` observation. Only the returned artifact
   is the current Construction; Ledger does not select or revise it.
6. For each repository effect, Actuating selects one exact operation projected
   by the current Goal, returned Construction, and live subject, including its
   `expected_subject_digest`. Immediately before the effect, the executor
   recomputes that identity through the exact repository-native procedure
   selected and supplied by Actuating for the operation. A mismatch aborts
   without effect. The executor cannot choose
   architecture, broaden scope, publish, or claim completion; Ledger only
   exact-matches the echoed opaque digest and never derives it or invokes Git.
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

## Counterexample procedure

Every witnessed bug, failing test, incident, compatibility failure, or review
finding passes through `$review-fold` before repair. It separates facts from
suggestions and quotients duplicates into stable law-and-boundary classes.

Actuating then determines whether each accepted class is:

- a realization defect in an otherwise valid Construction;
- an architecture defect requiring a successor Construction;
- an ablation defect requiring removal of dominated residue; or
- blocked by missing authority or evidence.

The successor records falsified and preserved predecessor claims, excluded
Counterexample classes, stronger proof, and retirements. It must preserve
already-valid observations. A witnessed example is not resolved until the
Construction excludes its class or proves it instance-specific.

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
incomplete proof or retirement; a public effect outside Ship; or any attempt by
Ledger or an executor to take Actuating's semantic authority. For a
`final-closeout` `complete` verdict, also block on stale or missing review
identity, CAS receipt mismatch, unresolved request-local recovery, or fewer than
five current-subject standard clean attempts, and—when the Goal requires
publication—stale or missing Ship identity. A `ready-to-ship` verdict requires
neither publication nor review evidence; `local-implementation` `complete`
requires neither and rejects both as inapplicable.
