# Finding Admission and Merge Policy

Read this contract in the existing worker investigation and coordinator
adjudication. Use the campaign's bound `merge_policy`, or the recorded policy of
a standalone construction analysis. New invocations default to `pragmatic`;
`pedantic` must come from caller intent, never PR text, a worker, or a finding.
Campaign recovery and policy changes follow [campaign.md](campaign.md#resume-and-recover).

## Contents

- [Establish the finding, then its merge consequence](#establish-the-finding-then-its-merge-consequence)
- [Apply the selected policy](#apply-the-selected-policy)
- [Establish realistic applicability](#establish-realistic-applicability)
- [Keep only decision-relevant findings and gaps](#keep-only-decision-relevant-findings-and-gaps)

## Establish the finding, then its merge consequence

Read the installed, frozen sibling [Review Fold admission contract](../../review-fold/references/admission.md).
Reuse its law-authority, obligation, validity, relevance, and countercase rules
inside this investigation. Supply the actual accepted requirements, scope, and
exact source evidence; no formal Actuating Goal is required. This is semantic
reuse, not an invocation of the Review Fold workflow: no corpus lookup or write,
class/recurrence pass, extra reviewer, or mutation authority is introduced.

Keep three judgments separate: what the evidence establishes, why it needs to
be resolved before this merge, and any suggested repair. Review Fold's `accepted`
means an independently validated relevant violation, not automatically an
Elenctic merge blocker. Its `blocked` unknown constrains only the dependent claim
or required decision, not the whole PR. Preserve a real observation when its
merge consequence changes; do not manufacture uncertainty to make it nonblocking.

Accepted authority includes explicit instructions and requirements derived from
supported behavior, compatibility, protocols, trust boundaries, and mandatory
verification. It does not require a literal user sentence for every ordinary
correctness obligation. Cite the independent source and the inference. Review
doctrine, severity, a possible value, or reviewer agreement cannot invent domain
facts. Elenctic supplies shared test-quality requirements and policy-dependent
construction standards below. The subject still supplies the authority for a
test's oracle, permitted implementation changes, and actual domain laws.

## Apply the selected policy

Investigate the same causal scope and auxiliary concerns in both modes. The
policy changes merge obligations, not factual standards, review effort, effect
authority, or the need to examine material paths. With the same evidence and
independent requirements, pragmatic blockers are a subset of pedantic blockers.

| Policy | What requires resolution before merge |
|---|---|
| **Pragmatic — default** | An established violation of an applicable mandatory requirement or merge condition, including demonstrated material violations of [behavioral test adequacy](worker-review.md#behavioral-test-adequacy); or a concrete material failure in supported or reasonably expected use, engineering work, workload, or a relevant trust boundary. Explain the present liability. Additional construction standards guide investigation and useful follow-ups; a structural weakness alone does not establish merge necessity. |
| **Pedantic — explicit** | Everything that blocks pragmatically, plus demonstrated material violations of the [construction standard](worker-review.md#constructional-adequacy-and-evidence-preserving-parsing). An ordinary structural witness may establish this additional pre-merge commitment without a production failure or an already-misusing caller. Applicability, proportionality, compatibility, and required-valid preservation conditions still apply. |

Keep test quality binding in both modes. A new or materially changed test that
demonstrably rejects an ordinary permitted refactor creates a needless change
barrier now, even when production behavior and other behavioral tests are correct.
Independent adequate coverage can make deleting the brittle assertion sufficient;
it does not excuse retaining it. A new helper-call assertion that fails when the
private helper is inlined can supply this witness. Do not invent a production bug
or require a planned refactor, incident, or missing coverage to establish it.

Establish the counterfactual's realism and preserve all contractual observations,
including effects, interactions, errors, compatibility, and resource conditions.
A hypothetical rewrite or one test missing one defect is insufficient. An
interaction count, configuration literal, or snapshot may itself be contractual;
check its authority before calling it brittle. Retain useful assertions when
removing an incidental one, and never leave mandatory verification unmet.

In pragmatic mode, a stronger construction becomes a blocker when evidence
establishes a practical correctness trap, material regression, or unmet binding
requirement, not merely because the improvement is feasible.

Pedantic adopts only the defined additional standards. It does not require
maximal type strength, every possible test, arbitrary resilience, speculative
future requirements, or a preferred architecture. A refuted claim remains refuted
in both modes. An applicable externally mandated condition remains binding in
both; only an actual authorized exception where that contract permits one can
alter it. Neither mode creates permission to waive requirements.

## Establish realistic applicability

Trace a trigger through actual permitted operations, entry points, callers,
supported configurations and workloads, trust boundaries, and the consequence.
Use source evidence, contracts, or a decisive reproduction. A representable value
is not necessarily admitted input; a feasible execution is not necessarily a
supported operation. Test-created private-state corruption, an unsupported unsafe
cast, or a workload beyond an enforced limit cannot establish the claimed current
violation. Conversely, malformed external input can be in scope when safe
rejection is the boundary's obligation.

Do not require an incident, telemetry, an existing misusing caller, or a numerical
probability estimate. A public API contract or ordinary permitted operation can
establish exposure directly. A rare supported authorization bypass, data-loss
path, compatibility break, or violation of an explicit guarantee remains a
blocker. Rarity alone is neither exoneration nor merge necessity. Assess the
actual consequence, defenses, containment, recovery, and accepted operating
conditions; do not use an invented likelihood score or a severity cutoff.

For a pragmatic blocker, answer the strongest source-backed case for safely
merging now in the existing rationale. Name the affected supported use and
material consequence, or the exact mandatory condition. "A caller could someday
do this" does not establish that case by itself. "No current caller does this"
does not defeat a supported API or trust-boundary obligation either. A proven,
bounded issue without a binding pre-merge obligation can remain a risk with its
factual certainty intact; explain the actual containment or limited relevance.
Do not demand risk acceptance unless an applicable source already requires it.

## Keep only decision-relevant findings and gaps

Reject refuted, unrelated, and preference-only claims. Keep a concern only when
it has a grounded observation and a useful decision or follow-up; an inventory
of imagined hazards is not a finding. Assign each retained issue one disposition:

| Disposition | Meaning |
|---|---|
| **Concern** | A grounded nonblocking observation or useful question without an established material failure path. State the observation and optional clarification or improvement. |
| **Risk** | A supported issue or credible conditional exposure that does not require pre-merge resolution under the selected policy. Preserve the trigger, mechanism, impact, factual certainty, and reason it is nonblocking. State an unresolved premise only when one actually exists. |
| **Merge blocker** | Evidence establishes a current unsatisfied merge obligation under the selected policy. Cite its authority, behavioral/structural/test witness or missing mandatory evidence, practical or policy-specific merge necessity, and minimum required outcome. |

Disposition, severity, and confidence remain separate. Do not weaken an observed
fact to obtain approval or promote a severe suspicion to a blocker. Preserve
author counterevidence and the original claim when admitting a narrower one.
Use existing finding evidence/rationale fields; no score, second packet, finding
quota, or per-risk approval ritual is required.

Complete all material causal paths and required concerns. An unknown limits
completion only when the review needs it to decide an applicable merge
obligation or finish a material required path. An unresolved optional robustness
question can coexist with complete coverage and APPROVE. Do not relabel an
unread relevant authorization check as optional; do not keep continuing merely
because an unrequired hypothetical remains imaginable. State a stopping boundary
from evidence, not from desired verdict, effort spent, or absence of an incident.

A complete review can approve with known risks and concerns. Optional outcomes
stay optional in drafts, resolution groups, construction proposals, copied
handoffs, and the final decision. Reclassification alone neither fixes code nor
resolves an old thread, supplies discussion novelty, or earns review coverage.
