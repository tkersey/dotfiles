---
name: actuating
description: "Implement accepted goals, analyze counterexamples, or close out reviewed changes. Derive law-preserving constructions from requirements and counterexamples. Unqualified review or analysis is read-only."
---

# Actuating

## Mission

Actuating is a **requirements-to-construction compiler** with a
counterexample-to-construction feedback path. Use the required behavior to derive
representations, operations, algorithms, and interpretations whose construction
explains their correctness. Develop the code and its argument together; use
witnesses to revise the model, domain, or realization. Preserve required-valid
behavior while removing what permits the supported failure family.

```text
accepted Goal -> required observations and laws
-> derive the construction and its correctness argument together
-> exact code + law implication + preservation proof

frozen reviewed candidate -> cumulative accepted counterexamples
-> causal explanation -> discriminating sibling predictions
-> law-preserving construction -> sanctioned-path migration
-> family exclusion + required-valid preservation -> adversarial review
```

The accepted law remains the completion target; an excluded family alone cannot
establish it. For admitted observations and traces `B'`, the source-required law
`L`, and any supported invalid family `Phi`, establish:

```text
B' satisfies L throughout the source-required domain
B' intersect Phi = empty
required-valid subset B'
every sanctioned path to trusted behavior crosses a law-preserving boundary
```

A checked constructor is not sufficient by its name. Its admission, ownership,
transitions, lifetime, and bypass closure must make the law hold in the declared
domain. Untrusted bytes may exist; acquiring trusted status must enforce the law.

## Authority and fact ownership

| Fact | Owner |
|---|---|
| Required behavior, compatibility, scope, authorized effects | accepted source or current user authority; bound directly by Actuating |
| Realized construction and exact diff | Git commit and tree |
| Executed validation and proof | the exact repository-native verifier |
| Review attempt, target, verdict, and provenance | CAS |
| Finding authority, applicability, duplicates, and admitted witnesses | `$review-fold` and `review-fold/counterexample-corpus` |
| Causal explanation, candidate selection, realization, and closure | `$actuating` |
| Mechanism challenger / boundary nomination / redundant factors | `$metanoetic` / `$universalist` / `$reduce`, interpreted by Actuating |
| Public effects and readback | `$ship` and the provider |

Supporting skills do not grant mutation or closure. Actuating owns no Ledger
transition gate and no durable workflow store. Review Fold's corpus remains
immutable witness evidence; current families, applicability, and architecture
are recompiled. A narrative, route label, or equality of agent-authored digests
cannot certify the construction.

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
Initial architecture decisions follow the Goal; no revoked predecessor theorem
is required to design software that does not yet exist.

Review-bearing routes accept `parallel-reviews` (default) or `serial-reviews`.
These change scheduling only. They do not change authority or the review inventory.

## Selected guidance

Read only the guidance selected by the route or current evidence, before its
first governed decision or effect. A linked workflow is mandatory when selected,
not optional background. Do not load every workflow at entry.

| Selected work | Required guidance |
|---|---|
| Initial/local `implement` | Source binding, initial construction, proof acceptance, realization, and completion below; no review campaign is required. |
| `analyze` | The same source and claim discipline, read-only. Load the relevant evidence or architecture guidance; do not execute realization, persist a corpus, publish, or grant closure. |
| A finding, failed check, or counterexample-driven selection | [counterexamples.md](counterexamples.md), before admitting a liability or selecting its response. |
| A live boundary decision or an existing Metanoetic trigger, including a suspect explanation or oracle | [architecture.md](architecture.md), before that decision; Universalist remains live-architecture-only. |
| An elimination claim meets a current witness, a broader Goal obligation remains unresolved after a narrow repair, or efficacy is being assessed | [recurrence.md](recurrence.md), before retaining the claim or selecting a successor. |
| `review-closeout`, or bare Actuating reaching review | [review-closeout.md](review-closeout.md) and its required review contract, before the first CAS request; use the complete frozen-subject and convergence rules. |
| Bare Actuating reaching publication | `$ship`; publication does not replace subsequent review-closeout. |

An open review epoch forbids successor mutation, including experiments. Read its
selected contract rather than repairing mid-wave. `corpus_write_authorized: false`
always applies to `analyze`; supporting skills cannot enlarge effect authority.
Universalist may return `candidate`, `preserve-incumbent`, `unresolved`, or
`obstructed`; Actuating retains selection and proof authority.

<a id="observe-and-adjudicate"></a>
Counterexample adjudication is in [counterexamples.md](counterexamples.md#observe-and-adjudicate).
<a id="compile-the-first-loss-of-guarantee"></a>
Causal compilation is in [counterexamples.md](counterexamples.md#compile-the-first-loss-of-guarantee).
<a id="architecture-compilation"></a>
Architecture compilation is in [architecture.md](architecture.md#architecture-compilation).
<a id="recurrence-and-progress"></a>
Recurrence and progress are in [recurrence.md](recurrence.md#recurrence-and-progress).
<a id="review-epoch-immutability-and-evidence-acquisition"></a>
Review epochs are in [review-closeout.md](review-closeout.md#review-epoch-immutability-and-evidence-acquisition).
<a id="review-and-closure"></a>
Review and closure are in [review-closeout.md](review-closeout.md#review-and-closure).

## Source binding

Derive the Goal directly from the current accepted specification or direct user
instruction; read the exact source, not just a prior summary. Preserve required
outcomes, non-goals, hard constraints, compatibility contracts, permitted breaks,
and migration obligations. Bind repository, immutable base, and authorized path
scope; an implementation or plan cannot silently broaden them.

Separate required deliverables and source-fixed architecture from preferences,
examples, and proposed means. Do not promote a suggested mechanism into a law or
demote an explicit requirement. Source binding records obligations; Actuating
chooses source-permitted means. A plan, review, or prior implementation cannot
broaden source authority.

Keep semantic requirements distinct from execution authority. Bind mutation,
validation, publication, and review posture to the accepted source and selected
route; permission to work neither authorizes every effect nor proves completion.
For each required law, retain applicability and its deciding observation. If that
observation cannot be identified or required authority is missing, block only the
dependent action or claim; continue independent authorized work.

Before affected mutation, refresh these bindings when the source, authority,
scope, compatibility, or required observations change. Have `$review-fold`
reclassify all available applicable findings and failures against the refreshed
Goal; preserve unresolved evidence and original provenance rather than erasing it
or inventing continuity. Existing review-epoch and proof-invalidation rules apply.

Reuse an adequate binding in the Working Set and existing downstream owner formats.
No separate skill invocation, mandatory Goal Contract packet, durable record, or new
identity is required. A summary or digest never replaces the source or proves completion.

## Initial construction

Use the law to generate the implementation. Work backward from required results
and permitted continuations to the facts, distinctions, and operation rules that
would establish them. For a proposed step, derive when it establishes the required
result; let those conditions determine its algorithm, inputs, or guards. For
iteration or recursion, derive the invariant and progress argument needed by the
contract. Work forward through the resulting operations to check that the
premises actually hold. A missing premise directs the next design or deciding
experiment; it is not discharged by implementing more cases.

Treat the representation, operation vocabulary, algorithm, and interpretation as
design variables within source-fixed constraints. Distinguish authoritative
facts, derived projections, and separately retained history. Change the carrier
when it invents irrelevant distinctions or erases required ones. Derive a shared
meaning when production observations repeat it; remove materialization when its
inspection, identity, sharing, and persistence roles are unnecessary or preserved.
Use the [construction moves](references/counterexample-guided-normalization.md#constructive-derivation)
when a law has not yet suggested an adequate native realization.

Derive a small useful set of constructors, operations, and lawful combinations
that expresses the required uses. Establish the primitive meanings and how
composition preserves them, so supported variants reuse the construction's
argument. Relate the concrete implementation to the required observations,
including failures and subsequent behavior; equality, refinement, and required
progress have different obligations. A hard or repetitive proof can expose a
better representation, operation, or decomposition. Preserve independent deciding
evidence even when production interpretations are unified.

Realize the smallest complete affected path before multiplying its variants:
identity includes production and consumption; recovery includes the promised
restored observations; validity includes subsequent permitted transitions.
For delegated work, bind the shared laws and operation/interpretation contracts
before dividing realization, then establish their actual composition. Use the
existing source argument and verifier; a partial slice remains work in progress.

Reuse an adequate existing boundary. Open the architecture path only for a live
semantic decision; no counterexample, review wave, new document, or mandatory
Universalist pass is needed to begin. Use a model, solver, or proof tool when it
resolves the actual uncertainty; neither a second implementation nor a formal
proof framework is a default prerequisite. Stop expanding when further
source-supported cases cannot change the construction or deciding proof. A direct
correction remains adequate when the existing construction already owns the law.

## Proof acceptance

Before implementation, identify the mechanism's actual guarantee and why it
implies the source-required observation. Could that guarantee hold while the
requirement fails? Challenge the implication with a source-supported state or
trace; a decisive source argument can suffice. Choose the exact-head verifier and
realize the mechanism, migrations, and retirements under the common proof obligations.

At entry and after material change, bind the Goal, immutable base, exact head,
current construction, proof inventory, and any publication state. Read the
relevant source, not a remembered architecture. Unknown evidence receives no credit.

Before accepting validation for local completion or reviewability, inspect the
base-to-candidate diff and actual check selection for deleted tests, weakened
assertions, skipped checks, or reduced coverage, including changes made directly
by Actuating. Map each affected check to its source-backed obligation; require
preserved or stronger proof, a source-grounded oracle correction with independent
evidence, or explicit authority retiring the obligation. A passing weakened suite
cannot discharge an unchanged requirement. Keep unexplained proof loss unresolved
and block only dependent completion or reviewability. Reuse the existing proof
inventory; no separate critic, packet, or review stage.


## Realization and common proof obligations

There is one operation: realize the selected construction, initially or as a
successor. Selection states an intended mechanism and falsifier; acceptance
requires the actual exact-head code.
Local experiments may occur only with mutation authority and outside an open
review epoch. They are not reviewable, publishable as complete, or proof by intent.

Every initial construction and correction must establish the applicable obligations:

```text
required relationships realized and required-valid behavior and observations preserved
current accepted witnesses addressed when present
supported causal families covered at the declared claim strength when present
preselected verifier and applicable sibling/domain discriminator executed, or explicit limitation
all relevant sanctioned producers, consumers, transitions, and bypasses accounted for
admission and permitted operations enforce the required law in the declared domain
proof authority, inputs, domain, and public claim agree
all correctness-bearing Git changes have accepted authority
displaced primary compensators retired or justified by distinct obligations
complete Goal-required proof inventory on the exact candidate
```

For an invariant-style safety law, establish valid admission, preservation under
permitted operations, implication of the law, and closure of sanctioned escapes.
Cut coverage proves passage through an owner, not preservation afterward. Account
for aliases, lifetime, interleavings, and externally visible effects when implicated;
transient invalidity must not escape its owning transition. Required progress and
trace behavior need their own arguments; disabling all operations is not success.

Prove every applicable changed-boundary obligation using the strongest adequate
repository-native evidence. A closed construction/operation surface can establish
coverage directly; an opaque type name or passing build alone cannot. Where route
or migration coverage remains unestablished, use the source-derived topology proof
in [counterexample-guided-normalization.md](references/counterexample-guided-normalization.md).
Never derive the verification domain solely from the candidate's asserted list.
New unaccounted sanctioned paths invalidate coverage under either representation.

For finite domains, complete claims need exhaustive coverage or a justified
construction proof. For open domains, they need a justified generator and
preservation argument. Samples, sibling tests, and clean reviews are falsification evidence, not universal proof.
Otherwise report the explicit bounded domain and residuals; never silently turn
containment into elimination or weaken required behavior to obtain a green result.

`isolated-restoration` and `construction-normalization` may describe the actual
delta afterward. They are not pre-mutation certificates or different proof bars.
A changed owner, cut, carrier, interpretation, topology authority, proof universe,
or claim strength cannot be hidden in a batch labeled restoration. A public claim
correction retains its own authority and closure consequence. Unknown evidence
means investigate or block the affected claim, not invent a digest or a rewrite.

## Construction Working Set

Keep the current Goal/head, required relationships and source-derived domains,
construction and deciding evidence, admitted witnesses and causal account when
present, source horizon, actual proof, migrations, retirements, residuals, and
unresolved work in the active thread or accepted implementation
specification. Reuse owner evidence rather than re-expressing it in another packet.
These are working facts, not a report template or durable Actuating store. Surface
only material decisions and limitations; preserve historical witness provenance.

## Completion

`implement` stops at local completion, not publication or review convergence.
Local completion requires the accepted Goal realized on the exact head, its
complete required validation, no unresolved accepted liability or unauthorized
strengthening, and honest claim strength and owned residuals. Do not claim an
experiment or an incomplete proof as complete. Read [closure.md](references/closure.md)
when deciding a publication-bearing or review-closeout terminal state. State the
law attempted, the conclusion established by the actual construction and evidence,
and its limits. A narrower supported claim does not complete a broader accepted Goal.

Bare Actuating continues through authorized Ship and review-closeout; do not
stop for approval merely because the first implementation exists. Missing
information, evidence, or authority blocks only its dependent action or claim;
continue independent authorized work. Complete the object-level task before
optional learning or memory capture.
