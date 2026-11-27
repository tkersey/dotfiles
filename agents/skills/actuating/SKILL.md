---
name: actuating
description: "Implement accepted goals, analyze counterexamples, or close out reviewed changes. Derive law-preserving constructions from requirements and counterexamples. Unqualified review or analysis is read-only."
---

# Actuating

## Mission

Realize the accepted behavior, not the incumbent design. Establish the complete
required relationship and preserve required-valid behavior; a repaired example
or excluded family does not discharge a broader Goal.

For every current applicable liability admitted by Review Fold, reconsider
correctness by construction before selecting its response, beginning with the
first finding. Use [architecture.md](architecture.md) for the unchanged shared
Glaze–Metanoetic activation; no user reminder, recurrence, failed local repair,
or preidentified redesign is required.

## Public routes

| Intent | Route | Mutation | Terminal result |
|---|---|---:|---|
| Bare `$actuating` or `/goal $actuating` | implement -> Ship -> review-closeout | Explicitly authorized | `complete` |
| `$actuating implement` | compile and realize locally | Explicitly authorized | local `complete` |
| `$actuating analyze` | deepest honest read-only construction judgment | Forbidden | construction, incomparability, containment, or obstruction |
| `$actuating review-closeout` | falsify, realize successors, Ship, converge | Explicitly authorized | `complete` |

An unqualified review, inspect, audit, classify, or analyze request selects
`analyze`. It may acquire evidence about an existing candidate but cannot mutate,
publish, grant closure credit, or claim completion. Mutation requires explicit
implement, fix, resolve, address, or closeout intent.

`implement` begins from the accepted Goal and exact Git state. It dispatches no
review and requires no review receipt, counterexample, or initial falsification
wave. Existing owner evidence may inform it without a fresh review campaign.
Initial work enters the [construction decision](construction.md#construction-decision)
directly from the Goal; no revoked predecessor theorem is required.

Implicit selection makes this skill available; it does not authorize mutation,
publication, or a broader route. Follow the user's requested scope and endpoint.
A local fix stays local unless publication is authorized; an analysis remains
read-only. Mentioning this skill as the subject of a question is not a bare
invocation. Explicit bare invocation retains the end-to-end route above.
Review executor or scheduling selection alone neither dispatches review for
`implement` nor enlarges `analyze` authority.

## Authority and fact ownership

The accepted source and current user own requirements and effect authority; Git
owns the actual candidate; repository-native verifiers own executed validation;
the selected executor owns review provenance; Review Fold owns finding admission
and its immutable corpus; Ship and the provider own publication and readback.
Actuating owns construction selection and closure, not another durable store or
Ledger transition gate. Supporting skills cannot enlarge authority. Agent-authored
labels, narratives, and equal digests do not certify semantics.

## Selected guidance

Read the applicable sections before their governed decision or effect; reuse
adequate evidence. Do not load every guide at entry or impose a reasoning sequence.

| Selected work | Guidance |
|---|---|
| Implementation or source-bound analysis | [construction.md](construction.md): source, construction, proof, and applicable obligations. Analysis stays read-only with `corpus_write_authorized: false`. |
| Building, changing, or analyzing a program or library | [Construction rules](construction.md#construction-rules) and [simulation-first correctness](construction.md#simulation-first-correctness), which classifies it as stateful or concurrent, or a pure library. For the stateful or concurrent kind, also [re-injection](counterexamples.md#re-inject-confirmed-defects) of every confirmed defect before a head carrying its fix becomes reviewable or is published. `analyze` judges against them without building or mutating. |
| Delegation, resumption, or local completion | [Working Set](construction.md#construction-working-set) and [completion](construction.md#completion). |
| Finding, failed check, or counterexample-driven selection | [counterexamples.md](counterexamples.md) before admission; the [construction decision](construction.md#construction-decision) and its [supporting skills](architecture.md) govern the response. |
| Supporting construction skills or architecture techniques | [architecture.md](architecture.md). Universalist's `candidate`, `preserve-incumbent`, `unresolved`, and `obstructed` results remain interpretable, not required output. |
| Materially costly verification, slow qualification, or broad retry while cost impedes the Goal | [verification.md](verification.md); ordinary cheap validation needs no extra workflow. |
| Unsuccessful required verification, invalidated review, repeated correction, falsified elimination, unresolved broader Goal after narrow repair, or efficacy assessment | [recurrence.md](recurrence.md) before another correction, broad retry, successor wave, or retained claim. |
| Review-closeout or bare Actuating reaching review | [review-closeout.md](review-closeout.md) before dispatch, beginning with its [pre-epoch screen](review-closeout.md#pre-epoch-screen); it routes inventory, convergence, executor, scheduling, and recovery. |
| Authorized publication or a review-closeout terminal decision | [Ship](../ship/SKILL.md) for public effects; [closure.md](references/closure.md) for closure. Publication alone does not complete review-closeout. |

The review contract's JSON is checked-in policy, not workflow state. The decision
contract and `tests/` are audit/evaluation material, not another runtime itinerary;
read them when a binding, audit, or evaluation needs them.

<a id="epoch-close"></a>

## Construction selection

Initial work and substantive returns from accepted findings, failed verification,
screens, closed epochs, or changed source evidence use one
[construction decision](construction.md#construction-decision).
Recover the [assignment](construction.md#construction-working-set) and material
[attempt history](recurrence.md#progress-before-another-iteration) before selecting
a successor; missing narration alone does not require repeating an adequate
execution or argument. Specialized routes retain their evidence, admission,
recovery, freeze, and review-credit rules; none prescribes the patch or grants new
effect authority.

## Section links

<a id="source-binding"></a>
[Source binding](construction.md#source-binding).
<a id="initial-construction"></a>
[Initial construction](construction.md#initial-construction).
<a id="construction-decision"></a>
[Construction decision](construction.md#construction-decision).
<a id="proof-acceptance"></a>
[Proof acceptance](construction.md#proof-acceptance).
<a id="comments-in-code"></a>
[Comments in code](construction.md#comments-in-code).
<a id="realization-and-common-proof-obligations"></a>
[Common proof obligations](construction.md#realization-and-common-proof-obligations).
<a id="construction-working-set"></a>
[Construction Working Set](construction.md#construction-working-set).
<a id="completion"></a>
[Completion](construction.md#completion).
<a id="observe-and-adjudicate"></a>
[Counterexample adjudication](counterexamples.md#observe-and-adjudicate).
<a id="compile-the-first-loss-of-guarantee"></a>
[Causal compilation](counterexamples.md#compile-the-first-loss-of-guarantee).
<a id="architecture-compilation"></a>
[Architecture compilation](architecture.md#architecture-compilation).
<a id="recurrence-and-progress"></a>
[Recurrence and progress](recurrence.md#recurrence-and-progress).
<a id="review-epoch-immutability-and-evidence-acquisition"></a>
[Review epochs](review-closeout.md#review-epoch-immutability-and-evidence-acquisition).
<a id="review-and-closure"></a>
[Review and closure](review-closeout.md#review-and-closure).
