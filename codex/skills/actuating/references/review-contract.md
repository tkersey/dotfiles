# Static Review Contract

[review-contract.json](review-contract.json) is checked-in policy, not mutable
workflow state. CAS owns review execution and receipts; Actuating derives credit
and construction consequences from exact owner facts.

## Binding and owner authority

Read the exact contract bytes and each custom instruction source without trimming
or normalization. Changeset-wide standard invokes Codex's native/default review
with no custom instructions argument or skill-authored prompt. Bind its instruction identity to
`codex-default-review/v1`, which records deliberate absence of customization; it
does not reproduce or constrain Codex's internal prompt. File-scoped standard uses
the focus instructions below and has no native/default convergence credit.

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
  focused_files: []
```

Each request has `scope: changeset | file` and `focus: null | {base_path, head_path}`.
Changeset scope requires null focus; file scope requires an exact entry from the
frozen selection. Scope and lens are independent dimensions of the obligation.

```text
campaign_id = sha256(
  "actuating-review-campaign/v3" || NUL ||
  repository || NUL || base_sha || NUL || head_sha || NUL ||
  target_fingerprint || NUL || review_contract_digest || NUL ||
  review_context_digest
)

scope_digest = sha256(canonical JSON of {scope, focus})

instruction_digest =
  (scope == changeset and lens_name == standard)
    ? sha256("codex-default-review/v1")
    : sha256(exact delivered custom instruction bytes)

request_fingerprint = sha256(
  "actuating-review-request/v4" || NUL ||
  campaign_id || NUL || request_id || NUL || lens_name || NUL ||
  role || NUL || scope_digest || NUL || instruction_digest
)
```

Supply only request ID and fingerprint through CAS's workflow binding. Accept
structured `clean` or `findings` outcomes for adjudication only with the exact
current tuple, instruction and workflow bindings, strong principal, owner-lived
transport, and the required backend capability. These checks authenticate the
result; they do not award review credit. Process exit, prose, and thread handles
are not verdicts. Hashes do not prove semantic equivalence or evidence delivery.
Keep required scope and usable prior evidence in existing accessible repository/task
documentation or a supported context channel, without customizing changeset-wide
standard review.

## Focused file reviews

Before the first request, read the complete rename-aware base-to-head file
inventory and additions/deletions, using `git diff --find-renames --numstat -z`
and `--name-status -z` against those exact commits. Preserve literal paths;
do not rank a truncated provider listing or split filenames on whitespace.

When the entire changeset has at most one logical file, select no supplement:
the existing reviews already have that file as their sole change anchor.
Otherwise rank eligible text-file changes by additions plus deletions descending,
breaking ties by repository path (head path, or base path for a deletion).
Select the first three, or all eligible files if fewer. This caps primary file
assignments per epoch; existing exact-request recovery remains separate.

Include hand-maintained code, tests, schemas, configuration, documentation, and
skill/workflow instructions. Exclude generated output, vendored snapshots,
lockfile regeneration, formatting, or moves only when evidence establishes that
the change is entirely generated or mechanical; a filename alone is insufficient.
Mixed substantive/mechanical edits remain eligible at their full raw line count.
Count a rename once, preserve both paths, and include substantive path-only changes
even at zero line churn. Deletions use their base-side contents and deleted lines.
Binary changes have no comparable line score and receive no automatic supplement.
All exclusions affect only this selection; full changeset scope remains required.
Retain selected paths, observed counts, and exclusion reasons in the existing
Working Set. Churn allocates attention; it neither proves risk nor waives scope.

Freeze the ordered `focused_files` list in `review_context` before dispatch.
Each entry has `base_path` and `head_path`; use null for an absent side.
For each file, dispatch all six `required_lenses` as independent CAS requests in
the same initial wave. Retain each lens's `lens_name` and `role`, give every
file/lens pair a distinct request ID, and use the same complete repository/base/head
target as every changeset review. Scope focuses attention without changing the Git
subject or restricting access to causal evidence in other files.

File standard is a general best-judgment review with file focus and no auxiliary
rubric. CAS has no native file-target selector: this request uses custom focus
instructions and cannot be represented as an uncustomized native/default standard.
The native changeset-wide standard remains unchanged.

Compose each file request from the exact
[file-focus instructions](focused-file-review.md), then, for an auxiliary, its
exact unchanged checked-in lens bytes, then a JSON assignment containing
`repository`, `base_sha`, `head_sha`, `lens_name`, `scope: "file"`, and
`focus: {base_path, head_path}`. Separate segments with two newlines; preserve
source bytes. File standard has no auxiliary segment. Hash all delivered bytes,
including separators and assignment. A digest alone does not deliver the accepted
requirements or source evidence. Whole-changeset auxiliaries retain their existing
exact instruction delivery.

Each file reviewer applies its assigned lens to the whole focal file and its
causal consequences, continuing beyond the first finding. Collect every supported
distinct finding and material gap in the same cumulative Review Fold as the
changeset reviews. Reviewers investigate independently; sibling conclusions from
this initial wave do not seed another request. The parent retains their findings
for the cumulative basis before choosing or implementing a successor.

Credit covers only the exact file/lens obligation on that frozen subject. A result
cannot discharge another lens, another file, a changeset auxiliary, or the native
standard streak. One combined file inquiry cannot discharge six independent reviews.
Changing the head or frozen selection requires a newly bound initial inventory;
recompute from the full bound base to the proved successor, not just the last fix.
No file credit survives a head change merely because its own bytes are unchanged.

## Review-credit admission

Before advancing a changeset standard count, completing an auxiliary or file/lens obligation, or
publishing review completion, Actuating adjudicates the full result, including its explanation,
against the requested scope and current evidence. Preserve CAS's original receipt.
Adjudicate findings through Review Fold and retain existing unusable-result and
invalidation paths; an evidence limitation is not itself a fabricated code finding.

Mismatched instruction or workflow bindings remain unusable under the existing CAS
result paths. When bindings are authentic but the actual inquiry misses its assigned
file or lens, hold for inadequate evidence. Complete the missing inquiry and reassess
it under observation/reasoning recovery below; this is not a verdictless terminal
and neither consumes nor extends the transport-recovery allowance.

```text
authentic current result + no unresolved findings + adequate evidence for the
requested review obligation -> credit; otherwise -> hold
```

Record `credit_disposition: credit | hold` and a concise `credit_basis` in the
existing per-request handoff or Working Set. An absent disposition means `hold`,
including for historical receipts; do not infer adequacy from `clean`,
`patch is correct`, a confidence score, or a successful review-process exit.
This is an owner decision, not a CAS receipt field or a new persistent record.

For a reported limitation, identify the affected claim and missing observation,
the attempted check and relevant mode/inputs, and the actual blocker (or unknown
cause). Resolve its relevance before credit, using the existing evidence:

| Limitation disposition | Basis needed for credit |
|---|---|
| `recovered` | The missing observation completed, and any review reasoning dependent on it was reassessed. |
| `covered` | An identified current evidence source discharges the affected obligation; relevant subject, inputs, mode, environment, and scope support reuse. |
| `not-required` | The existing requested scope supports the narrower conclusion without this observation; no required obligation was weakened to obtain credit. |
| `unresolved` | Materiality or sufficiency remains unestablished: hold the affected credit. |

Keep the disposition and source-supported basis together when reducing the result.
One sentence usually suffices; ordinary adequate reviews need no new evidence
inventory. An unsuccessful exploratory command does not automatically invalidate
a review. A material or unassessed gap cannot be silently accepted either.

A generic passing check does not establish equivalence to a named ReleaseSafe
check with unspecified flags. A context digest does not establish access to its
premises. Exit zero with skipped tests is not execution-pass evidence. Distinguish
reviewer-reported observations from actual command results. Reuse never relabels
the original blocked command as passed or establishes that the reviewer used
another result. When the missing observation affects independent review reasoning,
validation reuse alone is insufficient without that reasoning being completed.

Recover only the missing observation within existing authority, using a concrete
recovery hypothesis; stop rather than repeat an unchanged blocker. Do not weaken
tests, bypass sandbox boundaries, broaden permissions, or rerun the whole matrix
for a favorable label. A parent-run check may discharge validation but is not an
independent reviewer confirmation. Reassess dependent review reasoning as needed;
credit the original obligation at most once. This is distinct from verdictless
transport recovery and does not consume or extend its allowance.

A held result neither advances nor by itself resets existing credit. Continue
independent authorized work; a held standard pauses serial confirmations until
credited or invalidated, rather than being skipped to fill the quota. All required
changeset auxiliaries and every selected file/lens pair need credit, not merely terminal receipts and an
acknowledged caveat. Findings, changed inputs, and newly discovered missing
pre-review proof retain their existing
invalidation rules. Do not downgrade such missing proof to a review-only limitation.

Derive changeset standard counts, scope/lens completion, and user/PR readiness statements
from these same owner dispositions, never directly from receipt labels. Preserve
material limitations and the accepted scope even after credit. An unresolved
required obligation prevents an unqualified complete/all-clean claim; correcting
a summary does not itself recover the obligation or change the receipt.

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

Use available waiting time for [read-only self-review](../review-closeout.md#self-review-while-reviewers-are-running)
of the frozen subject. This supplies evidence without adding a required lens or
clean credit, delaying required dispatch/recovery/result collection, or extending
the epoch to finish a pass.

The initial inventory is the product of the changeset plus the frozen selected
files with all six required lenses. Visit changeset scope first, then each selected
file in rank order; within every scope use:

```text
standard
soundness-skeptic
footgun-finder
invariant-ace
complexity-mitigator
fresh-eyes
```

Each cell is a separate independent request. With three selected files this means
six changeset reviews plus eighteen file reviews, all in one frozen initial wave.

`parallel-reviews` dispatches the entire initial inventory concurrently within
available capacity and never cancels siblings. Keep queued requests required;
await every initial semantic outcome and required recovery.

`serial-reviews` adjudicates each request before the next. After invalidation,
continue every remaining initial request against the same frozen head for evidence
only: no mutation, no clean credit, no successor assumptions.

A verdictless terminal has no semantic outcome. Permit one fresh exact-request
recovery; it remains part of the barrier after invalidation. A second verdictless
terminal blocks. Do not interpret an observation timeout as terminal failure.

Complete and fold the entire initial inventory before any later confirmation;
proceed only while the candidate remains valid and all initial obligations have
credit. The initial credited changeset-wide standard counts as one. Four later standard confirmations
run serially, producing five consecutive distinct native/default standard cleans
admitted under Review-credit admission on one unchanged head. A material finding stops confirmation. A material head change
resets all review credit; rerank files for the proved successor and start a new
initial wave under the selected scheduling mode. Confirmations have changeset scope
only. File-standard outcomes neither advance nor break the native standard suffix;
a material finding from any scope still invalidates all credit. For `N` selected
files, a fully clean epoch has `6 * (1 + N)` initial requests and four later native
standards: at most 24 initial and 28 total, excluding required recovery. File lenses
do not acquire their own confirmation streaks; request count is not a token or time bound.

## Live owner-source frontier

Before a counterexample-driven selection or a completion claim, reconcile relevant
CAS, self-review, provider/PR, tests, incidents, migrations, compatibility,
repository verifiers, and historical corpus evidence. Each source is folded,
proven non-current, or explicitly unavailable. An omitted live finding keeps the
cut open. Quota exhaustion or a missing tool result is unavailable, never a clean
semantic verdict.

Self-discovered findings retain their own provenance and pass Review Fold admission;
they are not CAS outcomes. Once admitted as current, material, and entailed, they
invalidate the candidate and all review credit under the same phase rules as any
other finding, regardless of clean CAS receipts. An unfinished self-review pass
does not make a required review source unavailable; discovered material evidence
still needs adjudication before closure.

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

Changeset standard remains Codex's default best-judgment review; file standard
uses that general investigative remit within its custom file scope. Each auxiliary has a distinct
investigative starting point, defined by its exact checked-in instruction file:

| Lens | Starting point |
|---|---|
| soundness-skeptic | positive judgment -> necessary premises and supporting evidence |
| footgun-finder | reasonable actor/action -> expectation versus actual consequence |
| invariant-ace | valid admission -> permitted operations and preservation failures |
| complexity-mitigator | independently maintained truths -> distinct live obligations |
| fresh-eyes | accepted outcome -> independent end-to-end reconstruction |

These are search priorities, not exclusive defect categories or finding quotas.
Shared accessible authority does not require shared interpretations. Preserve
material evidence-access limitations; a workflow digest does not disclose its
premises. Reviewers supply supported findings and uncertainty, not repair authority.
Review Fold retains counterexample admission; no auxiliary repeats that workflow
or adds a reviewer. Nonblocking opportunities do not become correctness liabilities.
Instruction changes invalidate their old instruction-bound credit; the existing
inventory, scheduling, epoch, recovery, and convergence rules remain unchanged.

Convergence is adversarial evidence, not proof by repeated absence of findings.
Evaluate improvements through realized family exclusion, independent sibling
coverage, preserved valid behavior, path closure, and retirement of redundant
correctness-bearing factors. Policy unit fixtures and matching labels do not
establish model efficacy. Use existing offline audits for matched-case comparisons;
add no review lane, runtime classifier, theorem packet, or Actuating store.
