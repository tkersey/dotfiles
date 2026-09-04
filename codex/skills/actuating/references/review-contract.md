# Static Review Contract

[review-contract.json](review-contract.json) is checked-in policy, not mutable
workflow state. CAS owns review execution and receipts; Actuating derives credit
and construction consequences from exact owner facts.

## Binding and owner authority

Read the exact contract bytes and each auxiliary instruction file without trimming
or normalization. Standard invokes Codex's native/default review with no custom
instructions argument or skill-authored prompt. Bind its instruction identity to
`codex-default-review/v1`, which records deliberate absence of customization; it
does not reproduce or constrain Codex's internal prompt.

Use the existing canonical ephemeral context:

```yaml
review_context:
  repository:
  base_sha:
  head_sha:
  target_fingerprint:
  goal:
    objective:
    non_goals: []
    required_observations: []
    compatibility: []
  counterexample_basis_digest:
  counterexample_horizon_complete_for_claims: true | false
  proof_inventory_digest:
  validation_summary:
  publication_observation_ref: null | sha256-digest
```

```text
campaign_id = sha256(
  "actuating-review-campaign/v3" || NUL ||
  repository || NUL || base_sha || NUL || head_sha || NUL ||
  target_fingerprint || NUL || review_contract_digest || NUL ||
  review_context_digest
)

instruction_digest =
  standard ? sha256("codex-default-review/v1")
           : sha256(exact auxiliary instruction bytes)

request_fingerprint = sha256(
  "actuating-review-request/v3" || NUL ||
  campaign_id || NUL || request_id || NUL || lens_name || NUL ||
  role || NUL || instruction_digest
)
```

Supply only request ID and fingerprint through CAS's workflow binding. Credit only
structured `clean` or `findings` outcomes with the exact current tuple, instruction
and workflow bindings, strong principal, owner-lived transport, and the required
backend capability. Process exit, prose, and thread handles are not verdicts.
Hashes bind concrete evidence bytes; they do not prove semantic equivalence.

## Review epoch

The epoch is ephemeral and derived from owner facts. First dispatch against an
exact locally proved `reviewable` candidate opens it. Freeze that candidate while
review is open. All requests and credit remain bound to that same head.

Initial implementation occurs outside review and requires no CAS receipt or wave.
Existing closed owner evidence may inform it without dispatching a fresh review.
An incomplete candidate may be implemented but may not enter closure review.

A material current entailed finding invalidates the candidate and resets all
credit, but does not authorize editing. The initial epoch closes only after every
required initial outcome, required recovery, and the cumulative Review Fold are
complete. A clean epoch remains open through standard convergence and folding of
all terminal semantic outcomes, including recovered outcomes.
A material confirmation finding closes its epoch after that finding and already-live
required owner evidence are folded; no new auxiliary wave runs on the invalid head.

## Scheduling

The required initial order is:

```text
standard
soundness-skeptic
footgun-finder
invariant-ace
complexity-mitigator
fresh-eyes
```

`parallel-reviews` launches all six owner-live requests concurrently and never
cancels siblings. Await all launched semantic outcomes and required recovery.

`serial-reviews` adjudicates each request before the next. After invalidation,
continue the remaining initial lenses against the same frozen head for evidence
only: no mutation, no clean credit, no successor assumptions.

A verdictless terminal has no semantic outcome. Permit one fresh exact-request
recovery; it remains part of the barrier after invalidation. A second verdictless
terminal blocks. Do not interpret an observation timeout as terminal failure.

The initial standard clean counts as one. Four later standard confirmations run
serially, producing five consecutive distinct native/default standard cleans on
one unchanged head. A material finding stops confirmation. A material head change
resets all review credit; the proved successor starts a new initial wave under
the selected scheduling mode.

## Live owner-source frontier

Before a counterexample-driven selection or a completion claim, reconcile relevant
CAS, provider/PR, tests, incidents, migrations, compatibility, repository verifiers,
and historical corpus evidence. Each source is folded, proven non-current, or
explicitly unavailable. An omitted live finding keeps the cut open. Quota exhaustion
or a missing tool result is unavailable, never a clean semantic verdict.

Unavailable evidence limits the claims that depend on it. It does not force a
new review campaign or block unrelated authorized initial implementation. A required
completion source cannot be silently waived. Derive this view from owners; do not
create an Actuating source registry.

## Counterexample history projection

Before current family synthesis, have `$review-fold` project
`review-fold/counterexample-corpus`. Recompute applicability, Goal-law authority,
recurrence, and family hypotheses against the current head. A CEX row proves its
original admission, not that it is a current liability or a complete family.

Absent local history is not evidence of absence. Unknown history cannot support
first-observed, disjointness, or post-elimination claims. Current evidence may
still support a properly bounded construction. Review Fold captures each new
independent current entailed accepted witness; it does not persist classes,
families, repair choices, rejected preferences, or current architecture.

## Candidate lifecycle and causal response

```text
realizing    construction or required exact-head proof remains incomplete
reviewable   actual candidate satisfies all applicable construction obligations
invalidated  a current material counterexample falsifies the candidate
```

Only `reviewable` may dispatch closure review. Closing an invalidated evidence cut
ends its freeze; it does not certify a proposed successor or authorize unentailed
changes.

Use [counterexample-guided-normalization.md](counterexample-guided-normalization.md)
to infer the enabling cause from the cumulative basis, select a sibling/domain
discriminator before implementation, compare adequate constructions, and realize
one successor. Do not choose a patch from each finding, require a local attempt
first, or demand a pre-mutation theorem-equality certificate.

A local correction and a redesigned mechanism face the same family, required-valid,
authority, and path-coverage obligations. Their labels describe the realized delta;
they cannot switch off proof. Where an owned boundary changes, invoke Universalist
at the existing architecture decision and prove every applicable construction obligation. Metanoetic
may challenge a plausible mechanism error before selection without a fictional
proof that every local alternative is impossible.

## Source-derived coverage and preservation

Use the construction argument in
[counterexample-guided-normalization.md](counterexample-guided-normalization.md).
Universalist nominates a code-bound owner/operation change, not a second Working Set
projection. Select the verifier before implementation and execute it on the actual
successor. Prove admission, permitted-transition preservation, source-derived
coverage, required-valid observations, and migration/retirement/residual obligations.
Cut passage alone does not establish preservation after admission.

Adequate native construction/operation evidence may discharge coverage directly.
Where route or migration coverage remains unestablished, use explicit source-derived
`T0`, `K`, `tau`, `F`, and independently derived `T1` with the same obligations.
A candidate-authored list cannot be its own verification domain. New unaccounted
sanctioned paths invalidate coverage under either representation. Residual invalidity
precludes complete family exclusion; samples do not become universal proof.

## Review entry and authority-complete diff

Before dispatch on the exact head require:

```text
accepted Goal and complete proof inventory
current cumulative evidence and honest source horizon
source-supported causal explanation for counterexample-driven changes
preselected sibling/domain discriminator and actual results or explicit limitation
required-valid behavior and compatibility preserved
law-bearing mechanism and supported sanctioned-path/bypass coverage
all applicable changed-boundary obligations with source-derived coverage evidence
all selected migrations, residuals, and compensator retirements realized
all correctness-bearing Git changes supported by accepted authority
```

Every proof-inventory entry is unique and has exact-head passing evidence or
authority-backed nonapplicability. Aggregate proof credit requires actual dependency
coverage. A known proof may not first run after convergence; discovering a required
missing proof invalidates the prior reviewability claim.

Do not implement rejected strengthenings to protect the clean suffix. Remove them
or reopen their authority. Public claim corrections retain their own authority;
containment and deferral are not full elimination. Mixed changes must preserve each
obligation's authority rather than laundering them through one restoration label.

## Falsification and resumption

A current entailed witness against an exact declared exclusion revokes that claim.
A sanctioned path absent from either claimed coverage basis revokes coverage
immediately. Reopen the causal explanation and its cumulative siblings; no packet,
route label, new family name, or new Git head can erase the contrary evidence.

Same broad law alone does not prove same-family recurrence. A new requirement
reopens Goal authority. An implementation-local failure may still have a small
adequate correction, but it must satisfy the same actual-candidate proof bar.
Never append a named-member guard as evidence of complete family elimination.

Reuse only exact resolvable CAS receipts. Missing review receipts require fresh
review from the initial wave, not reconstruction from prose. Missing historical
witness evidence makes the affected horizon incomplete. Review stays closed during
successor realization; intermediate commits receive no closure credit.

## Lens ownership and evaluation

Standard remains Codex's default best-judgment review. Auxiliaries keep their
existing checked-in search perspectives: soundness claims, unsafe admission paths,
invariant closure, duplicate semantic owners, and a fresh construction perspective.
Reviewers supply counterexamples, not repair authority.

Convergence is adversarial evidence, not proof by repeated absence of findings.
Evaluate improvements through realized family exclusion, independent sibling
coverage, preserved valid behavior, path closure, and retirement of redundant
correctness-bearing factors. Policy unit fixtures and matching labels do not
establish model efficacy. Use existing offline audits for matched-case comparisons;
add no review lane, runtime classifier, theorem packet, or Actuating store.
