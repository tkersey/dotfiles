---
name: review-adjudication
description: >-
  Discriminately adjudicate PR review comments before implementation. Treat each
  comment as a claim to test, preserve raw comment identity and input inventory,
  bind decisions to artifact state, build the strongest no-change countercase,
  separate valid concerns from valid proposed fixes, recover PR rationale with
  explicit `$seq` when needed, and emit a stale-proof gated ledger,
  resolve-selection map, adversarial action matrix, resolution warrants, and
  surface budgets that decide what to address, validate only, resolve with proof
  only, rebut, defer, investigate, or route. Trigger for `$review-adjudication`,
  review the review, adjudicate PR comments, are these comments relevant, which
  comments matter, should we act on these comments, gate review comments before
  implementation, refine this list to just those worth resolving, or select
  review comments to resolve. Not for implementing fixes, writing rebuttals only,
  or final merge closure.
---

# Review Adjudication

## Intent

Decide which PR review comments should change code, which should be rebutted,
which are stale or out of scope, which require validation only, and which should
be reframed as a governing invariant instead of handled as isolated local fixes.
When the next workflow is `$fixed-point-driver`, `$resolve`, `$ship`, or
thread-resolution, also decide which comments are implementation work versus
validation-only, proof-only thread resolution, reply/defer work, or no-change
items.

This skill is **discriminative**, not deferential. A reviewer comment is an input
claim, not an obligation. `act` is a conclusion that must be earned from current
artifact evidence, a defeated no-change countercase, and an explicit adversarial
clearance for the downstream action.

## Default mode

Use **Surface-Budgeted v6** mode whenever the input contains real review
comments. Surface-Budgeted v6 is mandatory because automation needs:

- stable raw comment identity
- complete input-comment inventory coverage
- artifact-state identity for stale-handoff detection
- explicit decision tests for every comment
- evidence-grade and evidence-reference separation
- resolve-selection mapping for implementation, validation, proof-only thread
  resolution, no-change, and blocked outcomes
- adversarial action coverage for every selected downstream action
- parallelism calibration so adversarial effort is spent where it can change the
  route, proof, owner, or budget
- proof refs and route rationale for every downstream selection
- resolve countercases so "worth resolving" is challenged separately from concern
  validity
- selection-skew auditing so "all are worth resolving" cannot pass silently
- handoff-agenda consistency checks so selected work is not broadened later
- separate implementation, validation, and reply handoff permissions
- Resolution Warrants that act as scoped, expiring downstream permissions
- Surface Budget Ledger entries that force subtractive-first solution search and
  cap additive semantic surface

Other modes are allowed only when they still satisfy the completion gate:

- **Standard**: expanded reasoning plus the full Surface-Budgeted v6 tail.
- **Fast**: bucket-only output plus the completion gate; allowed for exploratory
  triage or synthetic comments, not for implementation handoff unless the gate
  passes.

## Doctrine

Operate in **DISCRIMINATIVE**, **REBUTTAL-FIRST**, **ADVERSARIAL-BY-DEFAULT**,
**PARALLEL-WHEN-MATERIAL**, **INVARIANT-SEEKING**, **ANTI-RUBBER-STAMP**,
**EVIDENCE-WEIGHTED**, **STALE-PROOF**, and **FAIL-CLOSED** mode.

- **DISCRIMINATIVE**: separate true concerns from irrelevant, stale, unsupported,
  preference-only, misdiagnosed, or misframed comments.
- **REBUTTAL-FIRST**: for each comment, construct the strongest no-change
  countercase before deciding to act.
- **ADVERSARIAL-BY-DEFAULT**: every selected downstream action must have an
  adversarial response that tries to defeat that action, downgrade it, reroute it,
  narrow it, or block it.
- **PARALLEL-WHEN-MATERIAL**: run independent adversarial lanes in parallel when
  parallel challenge can reduce elapsed time without compromising current-state
  grounding or single-writer safety.
- **INVARIANT-SEEKING**: look for the governing invariant behind repeated local
  comments; avoid fixing the same invariant piecemeal.
- **ANTI-RUBBER-STAMP**: do not let plausibility, politeness, reviewer authority,
  parallel consensus, or ease of implementation become acceptance evidence.
- **EVIDENCE-WEIGHTED**: rank current artifacts above memories, memories above
  intuition, and direct proof above consensus.
- **STALE-PROOF**: bind adjudication to branch/head/diff/comment-set state so
  downstream handoffs can detect stale or contradictory agendas.
- **FAIL-CLOSED**: if the adjudication, adversarial clearance, or warrant contract
  is incomplete, block implementation handoff rather than guessing.

## Contract

- Review comments are claims to test, not truths to obey.
- `act` is a conclusion, not the default.
- Current artifact state outranks reviewer intuition.
- Prefer current-session artifacts over memories.
- Use memories as secondary rationale support and provenance, not as the sole
  basis for acting.
- Distinguish concern validity from proposed-fix validity.
- Separate relevance from actionability.
- Preserve raw comment identity; do not let summaries replace comment IDs,
  reviewers, excerpts, locations, or input inventory.
- Preserve artifact-state identity; do not let a handoff become stale invisibly.
- Tail-weight outputs for CLI use.
- Do not implement fixes here.
- Do not create an implementation handoff unless the Adjudication Gate passes,
  `implementation_handoff_allowed: yes`, and every `address` row has adversarial
  clearance.
- Do not collapse adjudication into "all comments are worth resolving"; emit the
  resolve-selection map before implementation or thread-resolution handoff.
- Do not let `address` mean "add code". Every mutation-capable warrant must carry
  a surface budget, deletion/reuse/refactor probe obligation, and expansion-warrant
  rule before downstream implementation.
- Validation-only handoff is not implementation permission.
- Proof-only thread resolution is not implementation permission.
- Reply handoff is not implementation permission.
- No downstream mutation, validation-only probe, thread resolution, or
  rebuttal/defer handoff is licensed unless a matching active Resolution Warrant
  exists.
- No selected downstream action is licensed unless the Adversarial Action Matrix
  has a row for the raw claim and that row clears, preserves, or blocks the action
  consistently with the selected route.

## Dependency

This skill expects `$seq` to be installed when PR rationale recovery is needed.
If `$seq` is unavailable, proceed only from current artifacts and mark PR
rationale fields as `unknown` instead of inventing intent.

## Parallel adversarial action

Every row in `Resolve Selection` must receive one adversarial response. The
response is not decorative; it is a clearance attempt against the selected action.
It must either clear the action, preserve the no-change/defer decision, or block
handoff.

Adversarial responses should be parallelized when the dimensions are independent
and read-only. Use parallel lanes to reduce elapsed time for material batches, but
keep final adjudication and all downstream writes single-rooted.

### Required adversarial dimensions by action

| selected action | adversarial response must challenge |
|---|---|
| `address` | no-change, validate-first, wrong-fix, scope/ownership, surface-budget, fixed-point over-routing |
| `validate-only` | mutate-now, no-validation-value, wrong probe, production-mutation escape |
| `resolve-thread-only` | still-material, stale-proof insufficiency, proof-ref weakness, hidden implementation need |
| `do-not-address` | materiality, review-closure value, proof-only alternative, user/non-goal mismatch |
| `blocked` | whether a narrower safe validation, reply, proof-only route, or user question can unblock |

### Parallelism modes

Use exactly one `parallelism mode` per row in the Adversarial Action Matrix:

- `root-equivalent`: root performed the adversarial challenge inline; allowed for
  obvious narrow-local, proof-only, synthetic, or no-change rows.
- `targeted-parallel`: one or two independent read-only lanes challenged the row
  or invariant cluster.
- `full-fanout`: evidence, scope/ownership, criticality, no-change, validation
  value, and fix-shape lanes were assigned in parallel.
- `swarm`: five or more specialists were needed because the batch is large,
  contentious, P2+, invariant-coupled, or likely to reopen.
- `not-required`: only for rows with `resolve decision: blocked` and no safe
  downstream action to challenge; the missing evidence must be named.

Use full fanout or swarm when any of these are true:

- any P2+ row might be selected as `address`
- every substantive row would otherwise be selected as `address` or
  `validate-only`
- any CAS/Codex finding is invariant-framed and would mutate code
- the no-change countercase is weak, generic, or reviewer-authority-shaped
- validation-only is rejected for an unproven but plausible finding
- implementation would route to `$fixed-point-driver`
- several comments share a likely governing invariant

Do not parallelize lanes that need writes, mutate fixtures, alter review threads,
or depend on each other's outputs. Parallel adversaries are read-only evidence
producers; the root adjudicator integrates them.

### Adversarial Action Matrix

Emit `## Adversarial Action Matrix` after `## Resolve Countercases` and before
`## Resolution Warrants`.

```md
## Adversarial Action Matrix

| id/thread | primary resolve decision | adversarial lanes | parallelism mode | strongest adversarial response | veto status | clearance | proof ref | decision impact |
|---|---|---|---|---|---|---|---|---|
```

Allowed `veto status` values:

- `cleared`
- `preserved-no-change`
- `unresolved`
- `vetoed`
- `blocked`
- `not-required`

Allowed `clearance` values:

- `cleared`
- `preserved`
- `rerouted`
- `downgraded`
- `blocked`

Rules:

- `address` requires `veto status: cleared`, `clearance: cleared`, and a concrete
  proof ref that defeats the strongest no-change / validate-first / wrong-fix /
  scope / budget alternative.
- `validate-only` requires `veto status: cleared`, `clearance: cleared` or
  `downgraded`, and proof that validation is the correct next action instead of
  mutation or no action.
- `resolve-thread-only` requires `veto status: cleared` or
  `preserved-no-change`, `clearance: preserved`, and a proof ref that makes code
  mutation unnecessary.
- `do-not-address` requires `veto status: preserved-no-change` or `cleared`,
  `clearance: preserved`, and a proof/ref explaining why no downstream action is
  selected.
- `blocked` requires `veto status: blocked` or `unresolved`, `clearance: blocked`,
  and a missing-evidence proof ref.
- A vetoed or unresolved adversarial response must block implementation handoff
  unless the row is rerouted to a stricter non-mutating action with a matching
  warrant.
- A selected action with `parallelism mode: root-equivalent` must explain why
  separate parallel lanes were not materially useful.

## Required input context

When possible, build a compact context pack before adjudication:

```md
Review comments:
- raw id/thread:
- reviewer:
- file/location:
- exact excerpt:
- reviewer-suggested fix, if any:

Current artifacts:
- artifact_state_id:
  - branch:
  - base:
  - head:
  - diff_digest:
  - comment_set_digest:
  - ci_state:
- branch/diff summary:
- touched files:
- relevant tests:
- CI/local proof status:
- PR description or stated goal:

Constraints:
- intended change:
- explicit non-goals:
- compatibility posture:
- ownership boundaries:
- proof bar:
- likely next workflow:
```

Do not feed the whole repository by default. Add more context only when current
artifacts cannot decide grounding, scope, freshness, intent, evidence grade,
evidence ref, adversarial clearance, route selection, or handoff shape.

## `$seq` rationale recovery

Use `$seq` when the PR why is missing, disputed, stale, or likely to change
adjudication.

Preferred ladder:

1. `plan-search`
2. `artifact-search`
3. `find-session` + `session-prompts`
4. `memory-map`
5. `memory-provenance`
6. `memory-history`

Use `$seq` to recover rationale, not to manufacture obligations. A recovered plan
can explain why a comment matters, but current artifacts still decide whether the
comment is grounded, stale, in scope, actionable, or adversarially cleared.

## Evidence ranking

1. Current diff, code, tests, CI, and local artifact state
2. Current-session artifact evidence
3. Prior-session artifact evidence
4. Memory-derived evidence
5. Reviewer intuition without artifact support

## Artifact State Ledger

Bind the adjudication to the exact current artifact state whenever possible:

```yaml
artifact_state_id:
  branch: "<branch or unknown>"
  base: "<base sha/ref or unknown>"
  head: "<head sha/ref or unknown>"
  diff_digest: "<hash, changed path set, or unknown>"
  comment_set_digest: "<hash/list of raw comment ids or unknown>"
  ci_state: "<pass/fail/pending/not-run plus timestamp if known>"
```

If these fields are unavailable, say exactly which are unavailable and why. Do
not silently treat an unknown state as current proof.

## Comment Inventory

For real PR comments, emit `## Comment Inventory` before the ledger:

```md
- input_comment_count:
- ledger_row_count:
- input_comment_ids:
- ledger_comment_ids:
- missing_comment_ids:
- duplicate_comment_ids:
- synthesized_ids_for_real_comments: yes/no
```

If source input lacks stable IDs, record the identity gap and set
`identity_coverage: fail`. Do not silently synthesize stable IDs for real PR
comments. Temporary labels may be used only for synthetic comments or exploratory
Fast mode, and they must block implementation handoff.

## PR Why Ledger

Summarize recovered rationale in compact fields:

- `intended_change`
- `explicit_constraints`
- `non_goals`
- `governing_invariants`
- `evidence_source`
- `rationale_freshness`
- `staleness_source`
- `confidence`

If the PR why is unavailable and it materially affects adjudication, mark the
affected comments `need-evidence` rather than acting from invented intent.

## Comment identity

Preserve raw review-comment identity. For every comment, carry:

- `comment_id` or `id/thread`
- `reviewer`
- `short_excerpt` / `excerpt`
- `file_or_thread` / `location`
- `claim`
- `concern_validity`
- `proposed_fix_validity`
- `relevance_class`
- `disposition`
- `no_change_countercase_status`
- `governing_invariant`
- `evidence_grade`
- `evidence_ref`
- `reply_stance`
- `handoff_action`

## Required checks per comment

For every comment, assess:

1. grounding
2. materiality
3. freshness
4. diagnosis quality
5. scope fit
6. concern validity
7. proposed-fix validity
8. remediation posture
9. strongest no-change countercase
10. no-change countercase status
11. governing invariant, if any
12. minimum evidence to change mind
13. evidence grade
14. evidence reference
15. resolution value
16. resolve selection
17. adversarial response
18. handoff action

In Surface-Budgeted v6, surface these checks in `## Comment Ledger`,
`## Decision Tests`, `## Resolve Selection`, and `## Adversarial Action Matrix`.

## Act validity rule

A comment may be marked `act` only if all are true:

1. Current artifacts ground the concern.
2. The concern is material, or the user explicitly wants the nonmaterial change.
3. The comment is fresh for the current artifact state.
4. The strongest no-change countercase is defeated.
5. The adversarial response clears the selected `address` action.
6. The proposed fix is valid, or the chosen handoff replaces it with a valid fix
   shape.
7. The action fits this PR's scope, constraints, and intended change.
8. The row has `evidence_grade` of `current-artifact`, `current-test`,
   `current-ci`, or `current-session-artifact`.
9. The row has a concrete `evidence_ref` such as `file:line`, test name,
   command/log reference, CI status, PR thread, or current artifact citation.

If any item fails, do not use `act`; use `rebut`, `defer`, or `need-evidence`.
`act` requires proof, not plausibility or adversarial consensus.

## Rebuttal-first pass

Before marking a comment `act`, write the strongest plausible no-change
countercase.

A no-change countercase may be:

- the comment is unsupported by the current artifact state
- the comment is stale or superseded
- the comment is preference-only
- the comment is locally valid but out of scope for this PR
- the concern is valid but the proposed fix is wrong
- the requested local fix would hide the governing invariant
- the review asks for non-accretive broadening without proof
- the review assumes a contract this PR does not own
- the evidence is insufficient and the correct next step is validation only

Only mark `act` when artifact evidence and adversarial clearance defeat the
no-change countercase. If the countercase is not defeated, use `rebut`, `defer`,
or `need-evidence`.

## Validation-only escape hatch

Do not mutate code just because a concern might be real. When uncertainty is
material and a validating check is the correct next step, use:

```md
disposition: need-evidence
reframe_type: validation-only
remediation_posture: validating-check-only
proposed_fix_validity: validation-only
handoff_action: route-to-fixed-point-driver
```

Validation-only handoff may create tests, probes, logs, or inspections. It must
not implement the reviewer's requested code change unless the validation fails or
current artifacts already prove the concern and a new `mutate-code` warrant is
issued.

Hard constraints:

- `proposed_fix_validity: validation-only` requires `disposition: need-evidence`.
- `need-evidence` must not route directly to `$accretive-implementer`.
- `validation_handoff_allowed: yes` is not implementation permission.
- A validation-only row must have an adversarial response that rejects production
  mutation escape.

## Resolve-selection overlay

Use this overlay whenever the prompt asks which comments are worth resolving,
which reviews/comments to address, whether to resolve PR review threads, or when
the likely next step is `$fixed-point-driver`, `$resolve`, `$ship`, or final PR
comment cleanup.

Emit `Resolve Selection` after the adjudication buckets and before `Resolve
Countercases`. This section is the downstream selection contract.

Allowed `resolve_decision` values:

- `address`: the comment is `act`, the Act validity rule passed, adversarial
  clearance passed, and implementation handoff is allowed.
- `validate-only`: the comment is `need-evidence`; the next workflow may add a
  probe, test, or inspection, but must not implement the requested code change
  until evidence defeats the no-change case.
- `resolve-thread-only`: the concern is stale, superseded, already fixed on the
  current artifact state, or otherwise needs only a proof-bearing reply/thread
  resolution. No code change is selected.
- `do-not-address`: the comment should be rebutted, deferred, treated as out of
  scope, unsupported, preference-only, or left unresolved pending product/user
  direction.
- `blocked`: identity, freshness, PR rationale, evidence, adversarial clearance,
  resolve-selection, or gate coverage is insufficient to choose a downstream
  action.

Selection rules:

- `address` is legal only for rows whose disposition is `act`, whose no-change
  countercase is `defeated`, and whose Decision Tests satisfy the Act validity
  rule.
- `validate-only` is legal only for rows whose disposition is `need-evidence`.
- `resolve-thread-only` must name the proof that makes a code change unnecessary,
  such as latest-HEAD code evidence, a passing regression, or an already-pushed
  commit.
- `do-not-address` must name the preserved no-change case.
- `blocked` must name the missing evidence and set `adjudication_complete: fail`
  and all handoff permissions to `no`.
- The `Handoff Agenda` may include implementation work only for `address` items
  and validation/proof work only for `validate-only` items. Proof-only stale or
  already-fixed comments may be routed for replies/thread cleanup, not mutation.
- If all rows are `resolve-thread-only`, `do-not-address`, or `blocked`, do not
  route to `$fixed-point-driver` for implementation.
- Every row must include a concrete `proof ref` and `route rationale`.
- `route-to-fixed-point-driver` requires a route rationale of `coupled-comments`,
  `invariant-level`, `structural`, `validation-only`, `contentious`, or
  `likely-to-reopen`.
- `route-to-accretive-implementer` requires `route rationale: narrow-local`.
- `resolve-thread-only` requires `route rationale: proof-only-thread`.
- `do-not-address` requires `route rationale: no-change`.
- `blocked` requires `route rationale: blocked`.

## Resolve countercase pass

After the adjudication disposition and before downstream handoff, challenge the
selected resolve decision itself. Concern validity is not the same as "worth
resolving now".

Emit `## Resolve Countercases` with one entry per comment:

```md
- `<id/thread>`:
  - proposed resolve decision:
  - strongest alternative resolve decision:
  - why alternative is rejected / preserved / unresolved:
```

## Adversarial action pass

After the resolve countercase pass, run the adversarial action pass. This is the
permission-level challenge, distinct from the concern-level no-change case and the
resolve-level countercase.

For each selected action:

1. Name the strongest adversarial response.
2. Decide whether to run root-equivalent, targeted-parallel, full-fanout, swarm,
   or not-required mode.
3. Bind any packet or root-equivalent result to the current artifact state.
4. Record veto status, clearance, proof ref, and decision impact.
5. Downgrade, reroute, or block if the adversarial response is not cleared.

Parallel adversaries are not voters. They produce bounded clearance packets. The
root adjudicator may downgrade to a stricter route, but may not upgrade to
`address` against a veto, unresolved packet, stale packet, wrong-scope packet,
missing clearance, or missing proof ref.

## Resolution Warrants

After `Adversarial Action Matrix`, issue `## Resolution Warrants`. A Resolution
Warrant is the portable permission artifact downstream skills must consume before
mutating code, adding validation-only probes, resolving review threads, drafting
replies, or deferring/rebutting a claim. `Resolve Selection` explains the
decision; the warrant authorizes only the named action.

No warrant means the claim remains inert. No downstream skill may broaden beyond
the warrant's `permitted_scope`, reuse the warrant after expiry, or treat
validation-only/proof-only warrants as permission to mutate production behavior.

Use this table:

```md
## Resolution Warrants

| warrant id | claim id | source | claim excerpt | decision | concern validity | proposed fix validity | no-change status | resolution value | route rationale | permitted action | permitted scope | forbidden actions | evidence refs | countercase ref | proof required | expiry |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
```

Allowed `permitted action` values:

- `mutate-code`
- `add-validation-only`
- `resolve-thread`
- `draft-reply`
- `defer`
- `none`

Warrant rules:

- `address` may issue only `permitted action: mutate-code`.
- `validate-only` may issue only `permitted action: add-validation-only`.
- `resolve-thread-only` may issue only `permitted action: resolve-thread`.
- `do-not-address` may issue only `draft-reply`, `defer`, or `none`.
- `blocked` may issue only `none`.
- `mutate-code` warrants require a defeated no-change case, adversarial
  clearance, current evidence refs, narrow `permitted_scope`, explicit forbidden
  actions, proof required, and expiry on artifact/comment changes.
- `add-validation-only` warrants permit tests, probes, logs, or inspections, but
  must forbid production mutation and the reviewer's requested code change.
- `resolve-thread` warrants require proof refs that make code mutation unnecessary
  or prove the address warrant has been satisfied.
- Every warrant must expire when HEAD, base, diff, comment/thread set, or scoped
  artifact state changes unless explicitly revalidated.

Downstream consumption rule:

- `$accretive-implementer` may consume only active `mutate-code` warrants.
- `$fixed-point-driver` may consume active `mutate-code` or
  `add-validation-only` warrants, but must preserve the permitted action and
  consume the Adversarial Action Matrix row.
- `$resolve` / thread cleanup may consume active `resolve-thread` warrants or
  satisfied `mutate-code` warrants with proof.
- `$logophile` may consume `draft-reply` or `defer` warrants.
- If a downstream task changes files or resolves threads outside the warrant
  scope, the handoff is invalid.

## Surface Budget Warrants

A mutation-capable `address` warrant must not merely permit code change. It must
constrain the implementation search to the least new semantic surface area.
Default posture: **delete, reuse, collapse, or refactor before adding**.

Emit `## Surface Budget Ledger` after `## Resolution Warrants`. Every
`mutate-code` warrant must have one surface-budget row. Non-mutating warrants may
use zero budgets.

```md
## Surface Budget Ledger

| warrant id | mode | target net loc | max positive loc | max new public symbols | max new files | max new helpers | max new flags/knobs | max new state variants | max new branches | duplicate path budget | subtractive probes required | expansion warrant required | expansion status | proof required | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
```

Allowed `mode` values:

- `subtractive-first`: required default for `mutate-code` warrants. Try deletion,
  reuse, duplicate-path collapse, and refactor before any additive patch.
- `neutral-first`: allowed for validation, reply, or narrow proof-only routes with
  zero production surface.
- `additive-capped`: allowed only when the adjudication already knows a small
  positive diff is necessary and caps it explicitly.
- `exploratory`: never allowed for `mutate-code` handoff; use only for blocked
  investigation with no implementation permission.

Surface budget rules:

- `mutate-code` requires `mode: subtractive-first` or, rarely,
  `mode: additive-capped` with a named defeated subtractive route.
- `mutate-code` requires `subtractive probes required: yes`.
- `mutate-code` requires `expansion warrant required: yes`.
- Any additive helper, public symbol, file, flag/knob, state variant, or duplicate
  path must fit the row budget or stop for an Expansion Warrant Request.
- Public API, new state, new flags/knobs, and duplicate paths default to budget
  `0` unless the review concern is impossible to resolve otherwise.

The implementation handoff to `$fixed-point-driver` must include a **Surface
Budget Preflight** instruction for every `address` warrant and `$fixed-point-driver`
should emit a **Surface Delta Receipt** after each material patch.

## Governing invariant pass

After individual adjudication, cluster comments that appear to point at the same
underlying invariant, source-of-truth rule, ownership boundary, soundness
obligation, or API contract.

When multiple comments share an invariant:

- do not treat them as unrelated local fixes
- name the governing invariant
- decide whether the correct handoff is an invariant-level change
- route to `$fixed-point-driver` when the comments are coupled, contentious,
  structural, validation-only, or likely to reopen one another
- route to `$accretive-implementer` only when the invariant-level agenda is
  narrow, accretive, locally reviewable, and adversarially cleared

If no invariant cluster exists, say so explicitly and set `invariant_pass: pass`
only after checking.

## Allowed values

### Evidence grades

Use exactly one per comment:

- `current-artifact`
- `current-test`
- `current-ci`
- `current-session-artifact`
- `prior-session-artifact`
- `memory-only`
- `reviewer-only`
- `none`

`act` requires `current-artifact`, `current-test`, `current-ci`, or
`current-session-artifact`.

### Relevance classes

Use exactly one per comment:

- `material-relevant`
- `relevant-nonmaterial`
- `partially-relevant`
- `stale-or-superseded`
- `unsupported`
- `out-of-scope`
- `preference-only`

### Concern validity values

Use exactly one per comment:

- `valid`
- `partial`
- `unsupported`
- `unknown`

### Proposed-fix validity values

Use exactly one per comment:

- `valid`
- `partially-valid`
- `wrong-fix`
- `overbroad`
- `under-specified`
- `not-applicable`
- `validation-only`

### Disposition values

Use exactly one per comment:

- `act`
- `rebut`
- `defer`
- `need-evidence`

### Decision Test values

Use exactly one value per field:

- `grounded`: `yes` / `no` / `unknown`
- `material`: `yes` / `no` / `user-requested` / `unknown`
- `fresh`: `current` / `stale` / `superseded` / `unclear`
- `diagnosis`: `correct` / `partially-correct` / `misdiagnosed` / `unknown`
- `scope-fit`: `yes` / `no` / `partial` / `unknown`
- `resolution value`: `merge-blocking` / `correctness-critical` /
  `review-closure` / `proof-only` / `validation-needed` / `low-value` /
  `out-of-lane` / `blocked`
- `no-change defeated`: `yes` / `no` / `unresolved`

### Resolve decision values

Use exactly one per comment in `## Resolve Selection`:

- `address`
- `validate-only`
- `resolve-thread-only`
- `do-not-address`
- `blocked`

### Route rationale values

Use exactly one per comment in `## Resolve Selection`:

- `narrow-local`
- `coupled-comments`
- `invariant-level`
- `structural`
- `validation-only`
- `contentious`
- `likely-to-reopen`
- `proof-only-thread`
- `no-change`
- `blocked`

### No-change countercase status

Use exactly one per comment:

- `defeated`
- `not-defeated`
- `unresolved`

## Handoff permissions

Use separate route permissions:

- `implementation_handoff_allowed`: `yes` only for artifact-backed `act` rows
  selected as `address` after the gate and adversarial action coverage pass.
- `validation_handoff_allowed`: `yes` only for validation-only or other
  `need-evidence` rows that should route to `$fixed-point-driver` for proof.
- `reply_handoff_allowed`: `yes` only for rebuttal, defer, proof-only thread
  cleanup, or reply-drafting work that should route to `$logophile`, `$resolve`,
  or a reply draft.

Do not use the old single-field `handoff_allowed` in v6 output except when
quoting older adjudications.

## Acceptance skew audit

Before finalizing, audit the distribution of dispositions.

If every substantive comment is marked `act`, treat that as a warning sign, not a
victory. Emit an **All-Action Justification** table with these checks:

- `stale/superseded`
- `unsupported`
- `preference-only`
- `out-of-scope`
- `misdiagnosis`
- `proposed-fix validity`
- `validation-only alternative`
- `shared-invariant`

Each row must include `result`, `evidence ref`, and `why action still warranted`.
Generic language like "all comments are valid" is insufficient.

## Selection skew audit

Before handoff, audit the distribution of `Resolve Selection` decisions.

If every substantive comment is selected as `address` or `validate-only`, treat
that as a warning sign. Emit an **All-Selected Justification** table with these
checks:

- `stale/already-fixed alternative`
- `proof-only thread-resolution alternative`
- `do-not-address alternative`
- `validate-before-mutation alternative`
- `out-of-scope/defer alternative`
- `fixed-point over-routing check`

Each row must include `result`, `evidence ref`, and `why selected resolution is
still warranted`. Generic language like "all are worth resolving" is insufficient.

## Adjudication completion gate

Before any implementation, validation, thread-resolution, or reply handoff, emit
an `Adjudication Gate` block.

Required fields:

- `artifact_state_coverage`: `pass` / `fail`
- `comment_inventory_coverage`: `pass` / `fail`
- `identity_coverage`: `pass` / `fail`
- `decision_test_coverage`: `pass` / `fail`
- `no_change_coverage`: `pass` / `fail`
- `disposition_coverage`: `pass` / `fail`
- `proposed_fix_separation`: `pass` / `fail`
- `evidence_ref_coverage`: `pass` / `fail`
- `resolve_selection_coverage`: `pass` / `fail`
- `resolve_countercase_coverage`: `pass` / `fail`
- `adversarial_action_coverage`: `pass` / `fail`
- `parallelism_calibration`: `pass` / `fail`
- `resolution_warrant_coverage`: `pass` / `fail`
- `surface_budget_coverage`: `pass` / `fail`
- `surface_budget_consumption_safety`: `pass` / `fail`
- `warrant_consumption_safety`: `pass` / `fail`
- `handoff_agenda_consistency`: `pass` / `fail`
- `selection_skew_audit`: `pass` / `fail`
- `invariant_pass`: `pass` / `fail`
- `specialist_packet_coverage`: `pass` / `fail` / `not-used`
- `acceptance_skew_audit`: `pass` / `fail`
- `adjudication_complete`: `pass` / `fail`
- `implementation_handoff_allowed`: `yes` / `no`
- `validation_handoff_allowed`: `yes` / `no`
- `reply_handoff_allowed`: `yes` / `no`

`adjudication_complete` may be `pass` only when every preceding required field is
`pass`, except `specialist_packet_coverage`, which may be `not-used` when no
specialists were used.

If any required field fails, the bottom line must be:

```md
Blocked: incomplete adjudication. Do not implement yet.
```

Do not route to `$accretive-implementer` or `$fixed-point-driver` from an
incomplete adjudication, except that a complete validation-only adjudication may
route validation tasks to `$fixed-point-driver` when
`validation_handoff_allowed: yes` and `implementation_handoff_allowed: no`.

## Output contract

### Surface-Budgeted v6

Use this mode for real PR comment sets:

```md
## Review Basis
## Comment Inventory
## PR Why Ledger
## Comment Ledger
## Decision Tests
## No-Change Countercases
## Governing Invariant Ledger
## Specialist Packet Receipts
## Act On
## Rebut
## Defer / Out of Scope
## Need Evidence
## Resolve Selection
## Resolve Countercases
## Adversarial Action Matrix
## Resolution Warrants
## Surface Budget Ledger
## Invariant-Level Handoff
## Acceptance Skew Audit
## All-Action Justification
## Selection Skew Audit
## All-Selected Justification
## Adjudication Gate
## Handoff Agenda
## Adjudication Bottom Line
```

Omit `Specialist Packet Receipts` only when no specialists were used. Omit
`All-Action Justification` only when at least one substantive comment is not
`act`; still include `Acceptance Skew Audit`. Omit `All-Selected Justification`
only when at least one substantive comment is not selected as `address` or
`validate-only`; still include `Selection Skew Audit`.

### Standard

Standard output may include expanded per-comment analysis, but it must end with
the full Surface-Budgeted v6 tail and Adjudication Gate.

### Fast

Fast output may compress reasoning into decision buckets, but it must still
preserve comment identity, include an Acceptance Skew Audit, include an
Adversarial Action Matrix, and emit an Adjudication Gate. If identity, inventory,
artifact-state, no-change, adversarial, or warrant coverage is missing, Fast mode
must block implementation handoff.

## Handoff rules

- Route to `$accretive-implementer` when the accepted agenda is narrow,
  accretive, locally reviewable, artifact-backed, adversarially cleared, and not
  validation-only.
- Route to `$fixed-point-driver` when accepted comments are coupled, contentious,
  invariant-level, structural, validation-only, or likely to reopen one another.
- Route to `$logophile` only for drafting replies, naming, or wording.
- For `$resolve` or PR-thread cleanup, route proof-only stale/already-fixed
  comments as `resolve-thread-only`, not as implementation work.
- If the correct response is no code change, do not create an implementation
  handoff.
- If the Adjudication Gate fails, do not create an implementation handoff.
- If validation-only is the correct next move, route validation, not mutation.
- The Handoff Agenda must be a subset-preserving projection of Resolve Selection,
  Adversarial Action Matrix, and Resolution Warrants.
- Downstream skills consume warrants and adversarial clearance, not prose.
- Do not route a single narrow local action to `$fixed-point-driver` unless the
  route rationale is coupled, invariant-level, structural, validation-only,
  contentious, or likely-to-reopen.

## Machine-check hook

When automation is available, run the checker against the adjudication output
before routing implementation:

```bash
python codex/skills/review-adjudication/tools/review_adjudication_gate.py adjudication.md
# Optional downstream consumption checks:
python codex/skills/review-adjudication/tools/review_adjudication_gate.py adjudication.md --changed-files src/a.py,tests/test_a.py
```

A failed checker result means the adjudication is incomplete. Re-run adjudication
with the missing fields instead of implementing.

## Hard rules

- Do not turn adjudication into implementation.
- Do not treat memory artifacts as infallible.
- Do not force action on preference-only, stale, unsupported, or out-of-scope
  comments.
- Do not mark a comment `act` merely because it is easy to fix.
- Do not mark a comment `act` merely because the reviewer is probably right.
- Do not mark a comment `act` without a current evidence grade and evidence ref.
- Do not mark a comment `act` without adversarial clearance for the selected
  `address` action.
- Do not accept a local fix when the real issue is a governing invariant.
- Do not route validation-only work as implementation.
- Do not route `resolve-thread-only`, `do-not-address`, or `blocked` selections
  into `$fixed-point-driver` as implementation work.
- Do not emit duplicate singleton sections; duplicate ledgers or gates are
  treated as contradictory and fail the checker.
- Do not let `Handoff Agenda` broaden or contradict `Resolve Selection`,
  `Adversarial Action Matrix`, or Resolution Warrants.
- Do not let additive implementation proceed from an `address` warrant unless
  deletion/reuse/refactor probes are required and the additive diff stays inside
  the Surface Budget Ledger.
- Do not mutate code, resolve threads, validate, or draft replies from review/CAS
  derived claims without a matching active Resolution Warrant.
- Do not reuse warrants after HEAD/base/diff/comment-set changes without
  revalidation.
- Do not hide uncertainty; say exactly what evidence is missing.
- Do not allow `adjudication_complete: pass` if any required gate field fails.
- Do not allow `implementation_handoff_allowed: yes` if the mechanical checker
  fails, if any `act` row lacks current evidence, or if any `address` row lacks
  adversarial clearance.

## Resources

- [seq-rationale-ladder.md](references/seq-rationale-ladder.md)
- [adjudication-ledger.md](references/adjudication-ledger.md)
- [criticality-rubric.md](references/criticality-rubric.md)
- [adjudication-gate-contract.md](references/adjudication-gate-contract.md)
- [adjudication-output-template.md](references/adjudication-output-template.md)
- [resolution-warrants.md](references/resolution-warrants.md)
- [surface-budget-warrants.md](references/surface-budget-warrants.md)
- [context-pack.md](references/context-pack.md)
- [example-invocations.md](references/example-invocations.md)
- [common-routing-vocabulary.md](references/common-routing-vocabulary.md)
- [adversarial-eval-seeds.md](references/adversarial-eval-seeds.md)
