# Static Review Contract

[review-contract.json](review-contract.json) is checked-in policy, not mutable
workflow state. The selected executor supplies actual execution evidence;
Actuating derives credit and construction consequences from exact owner facts.

## Contents

- [Binding and owner authority](#binding-and-owner-authority)
- [Focused file reviews](#focused-file-reviews)
- [Review-credit admission](#review-credit-admission)
- [Review epoch](#review-epoch) and [scheduling](#scheduling)
- [Live owner-source frontier](#live-owner-source-frontier)
- [Counterexample history projection](#counterexample-history-projection)
- [Candidate lifecycle and causal response](#candidate-lifecycle-and-causal-response)
- [Source-derived coverage and preservation](#source-derived-coverage-and-preservation)
- [Review entry and authority-complete diff](#review-entry-and-authority-complete-diff)
- [Falsification and resumption](#falsification-and-resumption)
- [Lens ownership and evaluation](#lens-ownership-and-evaluation)

## Binding and owner authority

Read the exact contract bytes and each custom instruction source without trimming
or normalization. Bind `execution_mode` before dispatch: `codex` by default,
`subagents` only when explicitly requested. Scheduling and capacity are separate.

| Executor | Standard | Execution evidence |
|---|---|---|
| `codex` | Codex native/default changeset review, with no custom instructions argument or skill-authored prompt | Host-attributed native execution and exact native structured result under [reviews.md](../../cas/reviews.md) |
| `subagents` | Packaged upstream Codex rubric, with the exact assignment | Host-attributed terminal output under [subagent-reviews.md](subagent-reviews.md) |

Only native changeset standard uses instruction identity `codex-default-review/v1`.
It records deliberate absence of customization and does not reproduce or constrain
Codex's internal prompt. Portable standard hashes its actual delivered instructions.
File standards in either mode have no changeset convergence credit. Never silently
switch executors, mix their credits, or represent subagent output as native Codex review evidence.

Use the existing canonical ephemeral context:

```yaml
review_context:
  execution_mode: codex | subagents
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
  "actuating-review-campaign/v4" || NUL ||
  repository || NUL || base_sha || NUL || head_sha || NUL ||
  target_fingerprint || NUL || review_contract_digest || NUL ||
  review_context_digest
)

scope_digest = sha256(canonical JSON of {scope, focus})

instruction_digest =
  (execution_mode == codex and scope == changeset and lens_name == standard)
    ? sha256("codex-default-review/v1")
    : sha256(exact delivered custom instruction bytes)

request_fingerprint = sha256(
  "actuating-review-request/v5" || NUL ||
  campaign_id || NUL || request_id || NUL || lens_name || NUL ||
  role || NUL || scope_digest || NUL || instruction_digest
)
```

In `codex` mode, bind the actual host invocation/process, exact instruction
bytes or their deliberate absence, observed native thread/root-turn IDs, original
structured result, and before/after Git subject to this request in the existing
Working Set. Follow [native review readback](../../cas/reviews.md) rather than
minting a wrapper receipt. Require successful terminal execution and the exact
native `ExitedReviewMode.review_output` artifact (or an evidenced native equivalent).
Exec JSONL, final-message text, process exit, or a caller-authored clean label alone
is insufficient. A nonempty findings array remains findings; contradictory or
unusable output is held. There is no CAS workflow echo, principal field, backend
class, or compatibility capability to synthesize. Subagent mode retains its own
direct runtime-attribution contract.

Both modes require the current exact subject, assigned scope/lens, instruction
identity, and original output. Execution admission does not award review credit.
Process exit, prose, and worker/thread handles are not semantic verdicts. Hashes
do not prove semantic equivalence or evidence delivery. Keep required scope and
usable prior evidence accessible through repository/task sources or supported
context delivery, without customizing the native Codex changeset standard.

The context digest binds execution mode; the contract and delivered instructions
bind the standard policy. Mode or standard-policy changes start a newly bound
campaign and reset credit. Resume under the recorded mode and exact contract.
Historical CAS requests, including requests without an explicit mode, retain
their original attribution; they do not become native Codex requests. Finish/drain
old campaigns before cutover, or resolve possibly live work and start a newly bound
native initial wave without transferring old credit. Preserve all findings. No
legacy executor or automatic fallback is retained by the new workflow.

## Focused file reviews

Before the first request, read the complete rename-aware base-to-head file
inventory and additions/deletions, using `git diff --find-renames --numstat -z`
and `--name-status -z` against those exact commits. Inspect the actual changed hunks
and relevant base/head contents; raw file totals do not establish eligibility or
ranking. Preserve literal paths; do not rank a truncated provider listing or split
filenames on whitespace.

When the entire changeset has at most one logical file, select no supplement:
the existing reviews already have that file as their sole change anchor.

Only hand-maintained code with significant non-test changes is eligible. Judge
significance by changed behavior, contracts, or implementation structure, not a
minimum line count. Exclude dedicated test files, test-only helpers, fixtures and
snapshots, non-code changes, generated output, vendored snapshots, and lockfile
regeneration. Use repository conventions and actual file role/content, not a
filename alone, to establish these exclusions.

For mixed source/test files, such as Zig files with inline `test` blocks, ignore
tests and test-only support code in both eligibility and ranking. A source file
whose diff changes only tests is ineligible. Also ignore comments, formatting,
and generated or mechanical hunks in mixed edits. Count only substantive non-test
code additions and deletions; incidental non-test edits do not make a file eligible.

Rank eligible files by that filtered additions-plus-deletions count descending,
breaking ties by repository path (head path, or base path for a deletion).
Select the first three, or all eligible files if fewer, including none; never fill
the quota with ineligible changes. This caps primary file assignments per epoch;
existing exact-request recovery remains separate. Count a rename once, preserve
both paths, and include significant path-only code changes even at zero line churn.
Deletions use their base-side contents and qualifying deleted lines.
Binary changes have no comparable line score and receive no automatic supplement.
All exclusions affect only this selection; full changeset scope, including tests,
remains required. Retain selected paths, filtered counts, significance and exclusion
reasons in the existing Working Set. Churn allocates attention; it neither proves
risk nor waives scope.

Freeze the ordered `focused_files` list in `review_context` before dispatch.
Each entry has `base_path` and `head_path`; use null for an absent side.
For each file, dispatch all six `required_lenses` as independent review requests in
the same initial wave. Retain each lens's `lens_name` and `role`, give every
file/lens pair a distinct request ID, and use the same complete repository/base/head
target as every changeset review. Scope focuses attention without changing the Git
subject or restricting access to causal evidence in other files.

File standard is a general best-judgment review with file focus and no auxiliary
rubric. In `codex` mode it uses custom focus instructions, since native Codex has no
file-target selector. In subagent mode it receives the pinned standard rubric
and file focus. Neither is a changeset-standard convergence attempt.

In `codex` mode, compose each file request from the exact
[file-focus instructions](focused-file-review.md), then, for an auxiliary, its
exact unchanged checked-in lens bytes, then a JSON assignment containing
`repository`, `base_sha`, `head_sha`, `lens_name`, `scope: "file"`, and
`focus: {base_path, head_path}`. Separate segments with two newlines; preserve
source bytes. File standard has no auxiliary segment. Hash all delivered bytes,
including separators and assignment. A digest alone does not deliver the accepted
requirements or source evidence. Native changeset auxiliaries retain their existing
exact instruction delivery. In subagent mode, use the composition in
[subagent-reviews.md](subagent-reviews.md#deliver-the-exact-assignment); the same
file-focus and auxiliary source bytes remain unchanged.

Each file reviewer applies its assigned lens to the whole focal file and its
causal consequences, continuing beyond the first finding. Collect every supported
distinct finding and material gap in the same cumulative Review Fold as the
changeset reviews. Reviewers investigate independently; sibling conclusions from
this initial wave do not seed another request. The parent retains their findings
for the cumulative basis before choosing or implementing a successor.

Credit covers only the exact file/lens obligation on that frozen subject. A result
cannot discharge another lens, another file, a changeset auxiliary, or the changeset
standard streak. One combined file inquiry cannot discharge six independent reviews.
Changing the head or frozen selection requires a newly bound initial inventory;
recompute from the full bound base to the proved successor, not just the last fix.
No file credit survives a head change merely because its own bytes are unchanged.

## Review-credit admission

Before advancing a changeset standard count, completing an auxiliary or file/lens obligation, or
publishing review completion, Actuating adjudicates the full result, including its explanation,
against the requested scope and current evidence. Preserve the executor's original
receipt or directly attributed output, including material provenance limitations.
Adjudicate findings through Review Fold and retain existing unusable-result and
invalidation paths; an evidence limitation is not itself a fabricated code finding.

Mismatched instruction or request bindings remain unusable under the selected
executor's result paths. When bindings are authentic but the actual inquiry misses its assigned
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
This is an owner decision, not an executor result field or a new persistent record.

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

[Review-closeout](../review-closeout.md#review-epoch-immutability-and-evidence-acquisition)
owns opening, freezing, invalidation, the initial evidence barrier, and closing.
The epoch is ephemeral, derived from owner facts; all requests and credit stay
bound to its exact head. An incomplete candidate can be implemented outside review
but cannot enter closure review.

## Scheduling

`parallel-reviews` is the default; `serial-reviews` changes scheduling only.
Requested concurrency bounds active reviewers within available capacity; it never
reduces the inventory or overrides serial scheduling.

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
available capacity and any requested concurrency bound; it never cancels siblings.
Account for the coordinator and other live agents in subagent capacity. Keep queued requests required;
await every initial semantic outcome and required recovery.

`serial-reviews` adjudicates each request before the next. After invalidation,
continue every remaining initial request against the same frozen head for evidence
only: no mutation, no clean credit, no successor assumptions.

A verdictless terminal has no semantic outcome. Permit one fresh exact-request
recovery; it remains part of the barrier after invalidation. A second verdictless
terminal blocks. Do not interpret an observation timeout as terminal failure.

[Review and closure](../review-closeout.md#review-and-closure) owns the unchanged
five-clean convergence and reset rules. Native Codex confirmations remain native/default;
subagent confirmations use the pinned rubric in fresh contexts. Rerank files from
the full bound base for each proved successor. File-standard outcomes neither
advance nor break the changeset standard suffix; any material finding still
invalidates all credit. For `N` selected files, a clean epoch requires
`6 * (1 + N)` initial requests plus four later changeset standards: at most 24
initial and 28 total, excluding recovery. File lenses have no confirmation streaks;
request count is not a token or time bound.

## Live owner-source frontier

Use [counterexample admission](../counterexamples.md#observe-and-adjudicate)
before response selection or a completion claim. Reconcile every relevant live
source as folded, non-current, or unavailable; quota exhaustion is unavailable,
not clean. Do not create an Actuating source registry.

[Self-review](../review-closeout.md#self-review-while-reviewers-are-running) owns
self-discovered findings and their invalidation consequences. An unfinished
self-review pass alone does not make a required source unavailable.

## Counterexample history projection

[Counterexample admission](../counterexamples.md#observe-and-adjudicate) owns
corpus projection, current applicability, source horizons, capture authority, and
custody preparation. Before family synthesis, project the existing Review Fold
corpus; do not copy it or persist current families, repair choices, rejected
preferences, or architecture. A historical admission is not current applicability.

## Candidate lifecycle and causal response

```text
realizing    construction or required exact-head proof remains incomplete
reviewable   actual candidate satisfies all applicable construction obligations
invalidated  a current material counterexample falsifies the candidate
```

Only `reviewable` may dispatch closure review. Closing an invalidated evidence cut
ends its freeze; it does not certify a proposed successor or authorize unentailed
changes.

Return the complete admitted basis to the
[construction core](../SKILL.md#initial-construction) through the existing
[construction assignment](../SKILL.md#construction-working-set).
[Counterexample guidance](../counterexamples.md#compile-the-first-loss-of-guarantee)
governs response selection and deciding evidence;
[architecture guidance](../architecture.md) owns supporting-skill composition.
Realize one successor under the
[common proof obligations](../SKILL.md#realization-and-common-proof-obligations).
Review findings supply evidence, not separate patch assignments or weaker proof.

## Source-derived coverage and preservation

Apply the [common proof obligations](../construction.md#realization-and-common-proof-obligations)
to the actual candidate. They own admission, transition preservation, source-derived
coverage, required-valid observations, and migration/retirement/residual obligations.
Use the [construction repertoire](counterexample-guided-normalization.md) when the
affected domain or coverage argument needs it, not as another mandatory review pass.
Native coverage evidence remains sufficient when it establishes those obligations.

## Review entry and authority-complete diff

Only the `reviewable` candidate defined above can enter review. Apply
[proof acceptance](../construction.md#proof-acceptance),
[counterexample admission and response selection](../counterexamples.md), and the
[common proof obligations](../construction.md#realization-and-common-proof-obligations)
before dispatch. This includes the complete proof inventory, current cumulative
evidence and honest source horizon, the supported causal explanation for corrective
changes, actual migrations/retirements, and authority for every correctness-bearing
delta. Rejected strengthenings cannot enter the code to protect a clean streak.

Every proof-inventory entry is unique; aggregate credit requires actual dependency
coverage. A known proof may not first run after convergence. Discovering missing
required pre-review proof invalidates the prior reviewability claim. Optional or
inapplicable status follows accepted scope, never execution difficulty.

## Falsification and resumption

A current entailed witness against an exact declared exclusion revokes that claim.
A sanctioned path absent from either claimed coverage basis revokes coverage
immediately. Reopen the causal explanation and its cumulative siblings; no packet,
route label, new family name, or new Git head can erase the contrary evidence.

Same broad law alone does not prove same-family recurrence. A new requirement
reopens Goal authority. An implementation-local failure may still have a small
adequate correction, but it must satisfy the same actual-candidate proof bar.
Never append a named-member guard as evidence of complete family elimination.

Reuse only exact resolvable execution evidence under its original mode and contract:
native Codex execution/artifacts or host-attributed subagent outputs and assignments.
Historical CAS records remain evidence of their original work, not new-mode credit.
If any result
required for the current wave or streak cannot be resolved and revalidated,
restart the full initial inventory; summaries and remembered counts supply no
credit. Resolve possibly live attempts and fold their material evidence first.
Missing historical
witness evidence makes the affected horizon incomplete. Review stays closed during
successor realization; intermediate commits receive no closure credit.

## Lens ownership and evaluation

Changeset standard uses Codex's native default in `codex` mode and the pinned upstream
rubric in subagent mode; file standard uses that general investigative remit within
its custom file scope. Each auxiliary has a distinct
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
