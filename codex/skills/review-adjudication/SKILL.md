---
name: review-adjudication
description: "Adjudicate PR review comments before implementation with ruthless direction, severity, and evidence gates. Treat comments and P2+ labels as claims, preserve raw identity/input inventory, bind decisions to artifact and direction state, use current artifacts plus same-objective plan/$st/update_plan context, build strongest no-change and no-resolve countercases, separate concern validity from proposed fixes, reject review-closure-only mutation, and emit a stale-proof ledger plus resolve-selection map: address, validate only, resolve with proof only, rebut, defer, investigate, or route. Trigger for `$review-adjudication`, review the review, adjudicate PR comments, relevance/materiality questions, P2+ finding triage, gate review comments before implementation, refine to comments worth resolving, or select comments to resolve. Not for implementing fixes, writing rebuttals only, or final merge closure."
---

# Review Adjudication

## Intent

Decide which PR review comments should change code, which should be rebutted,
which are stale or out of scope, which require validation only, and which should
be reframed as a governing invariant instead of handled as isolated local fixes.
When the next workflow is `$fixed-point-driver`, `$resolve`, `$ship`, or
thread-resolution, also decide which comments are implementation work versus
validation-only, proof-only thread resolution, or no-change items.

This skill is **discriminative**, not deferential. A reviewer comment is an
input claim, not an obligation. A P0/P1/P2 label is a severity claim, not an
implementation priority. `act` is a conclusion that must be earned from current
artifact evidence, same-objective direction evidence, accepted criticality, and
a defeated no-change countercase.

## Default mode

Use **Compact-Gated v4** mode whenever the input contains real review comments.
Compact-Gated v4 is mandatory because automation needs:

- stable raw comment identity
- complete input-comment inventory coverage
- artifact-state identity for stale-handoff detection
- direction-state identity for same-objective plan and scope detection
- explicit decision, direction, and severity tests for every comment
- evidence-grade and evidence-reference separation
- reviewer severity claim versus accepted criticality separation
- resolve-selection mapping for implementation, validation, proof-only thread
  resolution, no-change, and blocked outcomes
- proof refs and route rationale for every downstream selection
- no-change and no-resolve countercases so "worth resolving" is challenged
  separately from concern validity
- validation-value checks so validation-only is not a laundering path
- selection-skew auditing so "all are worth resolving" cannot pass silently
- P2+ severity auditing so high labels cannot pass from reviewer authority
- handoff-agenda consistency checks so selected work is not broadened later
- separate implementation, validation, and reply handoff permissions

Other modes are allowed only when they still satisfy the completion gate:

- **Standard**: expanded reasoning plus the full Compact-Gated v4 tail.
- **Fast**: bucket-only output plus the completion gate; allowed for exploratory
  triage or synthetic comments, not for implementation handoff unless the gate
  passes.

## Doctrine

Operate in **DISCRIMINATIVE**, **REBUTTAL-FIRST**, **DIRECTION-GATED**,
**P2+-SKEPTICAL**, **INVARIANT-SEEKING**, **ANTI-RUBBER-STAMP**,
**EVIDENCE-WEIGHTED**, **VALIDATION-BUDGETED**, **STALE-PROOF**, and
**FAIL-CLOSED** mode.

- **DISCRIMINATIVE**: separate true concerns from irrelevant, stale,
  unsupported, preference-only, misdiagnosed, misframed, or low-value comments.
- **REBUTTAL-FIRST**: for each comment, construct the strongest no-change
  countercase before deciding to act.
- **DIRECTION-GATED**: a locally valid comment is not implementation-worthy
  unless it aligns with the active PR/codebase direction, an explicit user goal,
  a locked same-objective plan decision, or a direction-overriding current defect.
- **P2+-SKEPTICAL**: P0/P1/P2 labels require independent severity acceptance
  from current artifacts, tests, contracts, or same-objective direction evidence.
- **REVIEW-CLOSURE-IS-NOT-MATERIALITY**: review closure may justify a
  proof-bearing reply or thread resolution; it does not by itself justify code
  mutation.
- **INVARIANT-SEEKING**: look for the governing invariant behind repeated local
  comments; avoid fixing the same invariant piecemeal.
- **ANTI-RUBBER-STAMP**: do not let plausibility, politeness, reviewer authority,
  severity label, or ease of implementation become acceptance evidence.
- **EVIDENCE-WEIGHTED**: rank current artifacts above memories, memories above
  intuition, and direct proof above consensus.
- **VALIDATION-BUDGETED**: `validate-only` is selected only when validation would
  materially change merge safety, implementation direction, release posture,
  accepted criticality, or an invariant decision.
- **STALE-PROOF**: bind adjudication to branch/head/diff/comment-set and
  direction state so downstream handoffs can detect stale or contradictory
  agendas.
- **FAIL-CLOSED**: if the adjudication contract is incomplete, block
  implementation handoff rather than guessing.

## Contract

- Review comments are claims to test, not truths to obey.
- Reviewer severity labels are claims to test, not priority assignments.
- `act` is a conclusion, not the default.
- `address` is downstream implementation selection, not a synonym for "valid".
- Current artifact state outranks reviewer intuition.
- Current same-objective direction state outranks stale or unrelated plans.
- Prefer current-session artifacts over memories.
- Use memories as secondary rationale support and provenance, not as the sole
  basis for acting.
- Distinguish concern validity from proposed-fix validity.
- Distinguish reviewer severity claim from accepted criticality.
- Distinguish review-closure value from codebase materiality.
- Separate relevance from actionability.
- Preserve raw comment identity; do not let summaries replace comment IDs,
  reviewers, excerpts, locations, or input inventory.
- Preserve artifact-state identity; do not let a handoff become stale invisibly.
- Preserve direction-state identity; do not let an old plan or wrong-objective
  `$st` frontier become hidden implementation permission.
- Tail-weight outputs for CLI use.
- Do not implement fixes here.
- Do not create an implementation handoff unless the Adjudication Gate passes
  and `implementation_handoff_allowed: yes`.
- Do not collapse adjudication into "all comments are worth resolving"; emit the
  resolve-selection map before implementation or thread-resolution handoff.
- Validation-only handoff is not implementation permission.
- Proof-only thread resolution is not implementation permission.
- Reply handoff is not implementation permission.

## Dependencies

This skill may use the following context sources when needed:

- `$seq`: rationale recovery, plan-search, artifact-search, and prior-session
  provenance.
- `$st`: durable task/source-of-truth state in `.step/st-plan.jsonl`.
- Built-in task/plan surface: current execution projection only, not canonical
  durable direction.

If `$seq` or `$st` is unavailable, proceed only from current artifacts and mark
unavailable fields as `unknown` or `unavailable` instead of inventing intent.

## Specialist mode

For large or disputed comment sets, optionally use these read-only specialists
before final adjudication:

- `evidence_mapper`
- `soundness_auditor`
- `hazard_hunter`

Use them only to sharpen grounding, soundness, hazard, direction-fit, P2+
criticality, or invariant questions. They do not replace the adjudication
judgment.

When specialists are used, assign the current artifact state, direction state,
and exact comment or file scope, then require the shared packet contract at
`../references/specialist-packet-contract.md`. Consume only packet-native,
scoped, evidence-bearing, current packets. Reject stale, wrong-scope,
wrong-objective, wrapper-leaking, acknowledgement-only, or no-evidence packets
and keep them out of `act`/`rebut`/`defer`/`need-evidence` decisions.

When specialists are used, emit `## Specialist Packet Receipts` and set
`specialist_packet_coverage` to `pass` only when every accepted or rejected
packet has a value receipt and no rejected packet is used as evidence.

## Required input context

When possible, build a compact context pack before adjudication:

```md
Review comments:
- raw id/thread:
- reviewer:
- file/location:
- exact excerpt:
- reviewer-suggested fix, if any:
- reviewer severity label, if any:

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

Direction context:
- direction_state_id:
  - source: user-current-instruction | proposed-plan | st-plan | update-plan | PR-body | issue | design-doc | repo-convention | seq-recovered | current-artifact | unknown
  - source_ref:
  - source_freshness: current | stale | off-target | unknown
  - same_objective: yes | no | unknown
  - active_frontier:
  - locked_decisions:
  - non_goals:
  - compatibility_posture:
  - ownership_boundaries:
  - direction_confidence: high | medium | low | unknown

Constraints:
- intended change:
- explicit non-goals:
- compatibility posture:
- ownership boundaries:
- proof bar:
- likely next workflow: implementation / validation / `$resolve` / `$ship` / thread cleanup / unknown
```

Do not feed the whole repository by default. Add more context only when current
artifacts cannot decide grounding, scope, freshness, intent, direction-fit,
severity acceptance, evidence grade, or handoff shape.

## Direction-source ladder

Use direction context to decide whether a comment is aligned with where the
codebase and current PR are intentionally headed. Direction context is not defect
proof.

Preferred ladder:

1. explicit current user instruction for this turn or PR
2. current PR description, issue, or design doc tied to the active branch
3. current `.step/proposed-plan.md` when same-objective and fresh
4. `$st` durable active frontier from `.step/st-plan.jsonl` when same-objective
   and fresh
5. built-in task/plan projection when it matches `$st` or current objective
6. repo conventions and ownership boundaries found in current artifacts
7. `$seq` recovered same-objective plan/session rationale
8. memory-derived direction evidence

Rules:

- Treat `$st` as durable source of truth when the plan file is current and
  same-objective.
- Treat built-in task/update-plan as a display/projection, not canonical durable
  direction.
- Treat `.step/proposed-plan.md` as a direction source only when it is for the
  same objective and not superseded by `$st`, user instruction, or current
  artifacts.
- Treat off-target, stale, or wrong-branch plans as evidence against action, not
  permission to act.
- A recovered plan can explain why a comment might matter, but current artifacts
  still decide grounding and current direction decides scope.
- If direction context is unavailable and it materially affects actionability,
  mark affected comments `need-evidence` or `blocked`; do not act from invented
  direction.

## `$seq` rationale recovery

Use `$seq` when the PR why, direction, non-goals, or codebase trajectory is
missing, disputed, stale, or likely to change adjudication.

Preferred ladder:

1. `plan-search`
2. `artifact-search`
3. `find-session` + `session-prompts`
4. `memory-map`
5. `memory-provenance`
6. `memory-history`

Use `$seq` to recover rationale, not to manufacture obligations. A recovered plan
can explain why a comment matters, but current artifacts still decide whether the
comment is grounded, stale, in scope, aligned, or actionable.

## Evidence ranking

1. Current diff, code, tests, CI, and local artifact state
2. Current-session artifact evidence
3. Current same-objective direction artifacts (`.step/proposed-plan.md`, `$st`,
   PR body, issue, design doc)
4. Prior-session artifact evidence recovered with `$seq`
5. Memory-derived evidence
6. Reviewer intuition or severity label without artifact support

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

## Direction State Ledger

Bind adjudication to the active direction state whenever possible:

```yaml
direction_state_id:
  source: "<user-current-instruction | proposed-plan | st-plan | update-plan | PR-body | issue | design-doc | repo-convention | seq-recovered | current-artifact | unknown>"
  source_ref: "<path, task id, plan id, PR URL, issue id, session ref, or unknown>"
  source_freshness: "<current | stale | off-target | unknown>"
  same_objective: "<yes | no | unknown>"
  active_frontier: "<current execution wave/task/scope or unknown>"
  locked_decisions: "<compact list>"
  non_goals: "<compact list>"
  compatibility_posture: "<compact statement>"
  ownership_boundaries: "<compact statement>"
  direction_confidence: "<high | medium | low | unknown>"
```

For P2+ comments or any requested mutation that would broaden scope, direction
context is required. If direction context is missing, stale, off-target, or
conflicting, do not mark the comment `act` or `address` unless current artifacts
prove a direction-overriding correctness, security, safety, data-loss, or
compatibility defect.

## Comment Inventory

For real PR comments, emit `## Comment Inventory` before the ledgers:

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
affected comments `need-evidence` or `blocked` rather than acting from invented
intent.

## Comment identity

Preserve raw review-comment identity. For every comment, carry:

- `comment_id` or `id/thread`
- `reviewer`
- `short_excerpt` / `excerpt`
- `file_or_thread` / `location`
- `claim`
- `reviewer_severity_claim`
- `accepted_criticality`
- `severity_acceptance_status`
- `severity_proof_ref`
- `direction_fit`
- `direction_ref`
- `mutation_value`
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
6. direction fit
7. source freshness and same-objective status for direction evidence
8. reviewer severity claim
9. accepted criticality
10. severity acceptance status
11. severity proof reference
12. concern validity
13. proposed-fix validity
14. remediation posture
15. strongest no-change countercase
16. no-change countercase status
17. governing invariant, if any
18. validation decision value
19. mutation value
20. minimum evidence to change mind
21. evidence grade
22. evidence reference
23. resolution value
24. handoff action

In Compact-Gated v4, surface these checks in `## Comment Ledger`,
`## Decision Tests`, `## Direction Tests`, and `## Severity Tests`.

## Act validity rule

A comment may be marked `act` only if all are true:

1. Current artifacts ground the concern.
2. The action passes Direction Fit:
   - `direction_fit: aligned`, or
   - `direction_fit: direction-overriding` because current artifacts prove a
     correctness, security, safety, data-loss, compatibility, or other critical
     defect that must be handled even if the active plan omitted it.
3. The concern is material to the codebase direction, not merely material to
   review closure.
4. The comment is fresh for the current artifact state.
5. The strongest no-change countercase is defeated.
6. The proposed fix is valid, or the chosen handoff replaces it with a valid
   minimum fix shape.
7. The action fits this PR's scope, constraints, intended change, non-goals,
   compatibility posture, and ownership boundaries.
8. The row has `evidence_grade` of `current-artifact`, `current-test`,
   `current-ci`, or `current-session-artifact`.
9. The row has a concrete `evidence_ref` such as `file:line`, test name,
   command/log reference, CI status, PR thread, or current artifact citation.
10. The row has a concrete `direction_ref`.
11. The row has `mutation_value: codebase-material`.
12. `accepted_criticality` is one of `blocker`, `security-critical`,
    `safety-critical`, `data-loss-critical`, `correctness-critical`,
    `compatibility-critical`, or `direction-critical`.
13. For `reviewer_severity_claim: P0|P1|P2`, the row has:
    - `severity_acceptance_status: accepted`
    - implementation-grade `accepted_criticality`
    - a concrete `severity_proof_ref`
14. `resolution value: review-closure` is insufficient for `act` unless another
    accepted criticality independently justifies mutation.

If any item fails, do not use `act`; use `rebut`, `defer`, `need-evidence`, or
`blocked`. `act` requires proof and direction alignment, not plausibility.

## P2+ severity acceptance gate

Reviewer severity is a claim to adjudicate, not an implementation priority.

For any comment whose reviewer asserts or implies P0, P1, or P2:

- Do not preserve the label as accepted severity unless current evidence proves
  it.
- Do not mark `act` merely because a P2+ label sounds important.
- Do not use `review-closure` as accepted criticality for P2+ mutation.
- Do not select `validate-only` unless the validation result would materially
  change the implementation, merge, release, compatibility, security, accepted
  criticality, direction fit, or invariant decision.
- Do not route to `$fixed-point-driver` merely because the label is P2+.

A P2+ comment may be `address` only when:

```yaml
reviewer_severity_claim: P0|P1|P2
severity_acceptance_status: accepted
accepted_criticality: blocker|security-critical|safety-critical|data-loss-critical|correctness-critical|compatibility-critical|direction-critical
direction_fit: aligned|direction-overriding
mutation_value: codebase-material
no_change_countercase_status: defeated
evidence_grade: current-artifact|current-test|current-ci|current-session-artifact
severity_proof_ref: concrete
```

Otherwise:

- use `need-evidence` only when a bounded validation would change the route;
- use `defer` when the concern is real but belongs to a separate plan/migration;
- use `rebut` when the severity is unsupported or misdiagnosed;
- use `do-not-address` when the item is review-closure-only, out-of-lane,
  preference-only, stale, direction-conflicting, or not decision-changing.

## Rebuttal-first pass

Before marking a comment `act`, write the strongest plausible no-change
countercase.

A no-change countercase may be:

- the comment is unsupported by the current artifact state
- the comment is stale or superseded
- the comment is preference-only
- the comment is locally valid but out of scope for this PR
- the comment is locally valid but direction-conflicting
- the comment is review-closure-only
- the concern is valid but the proposed fix is wrong
- the requested local fix would hide the governing invariant
- the review asks for non-accretive broadening without proof
- the review assumes a contract this PR does not own
- the evidence is insufficient and the correct next step is validation only
- the severity claim is unsupported or downgraded

Only mark `act` when artifact and direction evidence defeat the no-change
countercase. If the countercase is not defeated, use `rebut`, `defer`,
`need-evidence`, or `blocked`.

## Validation-only escape hatch

Do not mutate code just because a concern might be real. When uncertainty is
material and a validating check is the correct next step, use:

```md
disposition: need-evidence
reframe_type: validation-only
remediation_posture: validating-check-only
proposed_fix_validity: validation-only
mutation_value: validation-material
handoff_action: route-to-fixed-point-driver
```

Validation-only handoff may create tests, probes, logs, or inspections. It must
not implement the reviewer's requested code change unless the validation fails or
current artifacts already prove the concern.

Validation-only requires decision value, not curiosity value. Use
`validate-only` only when the validation result would change at least one of:

- accepted criticality
- direction fit
- merge safety
- release/compatibility posture
- invariant handoff
- implementation scope
- rebut/defer/address selection

If the likely result would only satisfy curiosity, reviewer comfort, or review
closure, use `do-not-address`, `resolve-thread-only`, or `rebut` instead.

Hard constraints:

- `proposed_fix_validity: validation-only` requires `disposition: need-evidence`.
- `need-evidence` must not route directly to `$accretive-implementer`.
- `validation_handoff_allowed: yes` is not implementation permission.
- `validate-only` requires `mutation_value: validation-material`.

## Resolve-selection overlay

Use this overlay whenever the prompt asks which comments are worth resolving,
which reviews/comments to address, whether to resolve PR review threads, or when
the likely next step is `$fixed-point-driver`, `$resolve`, `$ship`, or final PR
comment cleanup.

Emit a `Resolve Selection` section after the adjudication buckets and before
`Handoff Agenda`. This section is the downstream selection contract.

Allowed `resolve_decision` values:

- `address`: the comment is `act`, the Act validity rule passed, the direction
  gate passed, accepted criticality is implementation-grade, and implementation
  handoff is allowed.
- `validate-only`: the comment is `need-evidence`; the next workflow may add a
  probe, test, or inspection, but must not implement the requested code change
  until evidence defeats the no-change case.
- `resolve-thread-only`: the concern is stale, superseded, already fixed on the
  current artifact state, or otherwise needs only a proof-bearing reply/thread
  resolution. No code change is selected.
- `do-not-address`: the comment should be rebutted, deferred, treated as out of
  scope, unsupported, preference-only, direction-conflicting, review-closure-only,
  or left unresolved pending product/user direction.
- `blocked`: identity, freshness, PR rationale, direction state, evidence,
  severity acceptance, resolve-selection, or gate coverage is insufficient to
  choose a downstream action.

Selection rules:

- `address` is legal only for rows whose disposition is `act`, whose no-change
  countercase is `defeated`, whose Decision/Direction/Severity Tests satisfy the
  Act validity rule, and whose `mutation_value` is `codebase-material`.
- `address` is illegal when `direction_fit` is `neutral`, `conflicting`, or
  `unknown`.
- `address` is illegal for P2+ unless `severity_acceptance_status: accepted`.
- `validate-only` is legal only for rows whose disposition is `need-evidence` and
  whose `mutation_value` is `validation-material`.
- `validate-only` is illegal when the only value is reviewer comfort, curiosity,
  or review closure.
- `resolve-thread-only` must name the proof that makes a code change
  unnecessary, such as latest-HEAD code evidence, a passing regression, or an
  already-pushed commit.
- `resolve-thread-only` is preferred over `address` when the only material value
  is review closure.
- `do-not-address` must name the preserved no-change case.
- `blocked` must name the missing evidence and set `adjudication_complete: fail`
  and all handoff permissions to `no`.
- The `Handoff Agenda` may include implementation work only for `address` items
  and validation/proof work only for `validate-only` items. Proof-only stale or
  already-fixed comments may be routed for replies/thread cleanup, not mutation.
- If all rows are `resolve-thread-only`, `do-not-address`, or `blocked`, do not
  route to `$fixed-point-driver` for implementation.
- Every row must include a concrete `proof ref` and `route rationale`.
- `route-to-fixed-point-driver` requires a route rationale of
  `coupled-comments`, `invariant-level`, `structural`, `validation-only`,
  `contentious`, or `likely-to-reopen`.
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

Examples:

- An `address` row must defeat the strongest `validate-only`,
  `resolve-thread-only`, or `do-not-address` alternative.
- A `validate-only` row must explain why immediate mutation is not yet justified
  and why validation would change a material decision.
- A `resolve-thread-only` row must explain why no code change is selected.
- A `do-not-address` row must preserve the no-change case.
- A `blocked` row must name the missing evidence that prevents selection.

## Governing invariant pass

After individual adjudication, cluster comments that appear to point at the same
underlying invariant, source-of-truth rule, ownership boundary, soundness
obligation, direction boundary, or API contract.

When multiple comments share an invariant:

- do not treat them as unrelated local fixes
- name the governing invariant
- decide whether the correct handoff is an invariant-level change
- route to `$fixed-point-driver` when the comments are coupled, contentious,
  structural, validation-only, or likely to reopen one another
- route to `$accretive-implementer` only when the invariant-level agenda is
  narrow, accretive, direction-aligned, and locally reviewable

If no invariant cluster exists, say so explicitly and set `invariant_pass: pass`
only after checking.

## Evidence grades

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
`current-session-artifact`. Memory-only and reviewer-only evidence may support a
rationale or reply stance, but they are not sufficient for implementation.

## Direction sources

Use exactly one primary source per direction row:

- `user-current-instruction`
- `proposed-plan`
- `st-plan`
- `update-plan`
- `PR-body`
- `issue`
- `design-doc`
- `repo-convention`
- `seq-recovered`
- `current-artifact`
- `unknown`

## Direction fit values

Use exactly one per comment:

- `aligned`
- `direction-overriding`
- `neutral`
- `conflicting`
- `unknown`

## Source freshness values

Use exactly one per direction row:

- `current`
- `stale`
- `off-target`
- `unknown`

## Same-objective values

Use exactly one per direction row:

- `yes`
- `no`
- `unknown`

## Reviewer severity claim values

Use exactly one per comment:

- `P0`
- `P1`
- `P2`
- `P3`
- `P4`
- `unlabeled`
- `unknown`

## Accepted criticality values

Use exactly one per comment:

- `blocker`
- `security-critical`
- `safety-critical`
- `data-loss-critical`
- `correctness-critical`
- `compatibility-critical`
- `direction-critical`
- `review-closure-only`
- `low-value`
- `out-of-lane`
- `unknown`

Only the first seven values are implementation-grade.

## Severity acceptance status values

Use exactly one per comment:

- `accepted`
- `downgraded`
- `rejected`
- `unresolved`

## Mutation value values

Use exactly one per comment:

- `codebase-material`
- `validation-material`
- `proof-only`
- `reply-only`
- `no-change`
- `blocked`

## Relevance classes

Use exactly one per comment:

- `material-relevant`
- `relevant-nonmaterial`
- `partially-relevant`
- `stale-or-superseded`
- `unsupported`
- `out-of-scope`
- `preference-only`
- `direction-conflicting`
- `review-closure-only`

## Concern validity values

Use exactly one per comment:

- `valid`
- `partial`
- `unsupported`
- `unknown`

## Proposed-fix validity values

Use exactly one per comment:

- `valid`
- `partially-valid`
- `wrong-fix`
- `overbroad`
- `under-specified`
- `not-applicable`
- `validation-only`

## Disposition values

Use exactly one per comment:

- `act`
- `rebut`
- `defer`
- `need-evidence`
- `blocked`

## Decision Test values

Use exactly one value per field:

- `grounded`: `yes` / `no` / `unknown`
- `material`: `yes` / `no` / `user-requested` / `unknown`
- `fresh`: `current` / `stale` / `superseded` / `unclear`
- `diagnosis`: `correct` / `partially-correct` / `misdiagnosed` / `unknown`
- `scope-fit`: `yes` / `no` / `partial` / `unknown`
- `resolution value`: `merge-blocking` / `correctness-critical` /
  `direction-critical` / `review-closure` / `proof-only` /
  `validation-needed` / `low-value` / `out-of-lane` / `blocked`
- `no-change defeated`: `yes` / `no` / `unresolved`

`review-closure` is not an implementation-qualifying resolution value.

## Resolve decision values

Use exactly one per comment in `## Resolve Selection`:

- `address`
- `validate-only`
- `resolve-thread-only`
- `do-not-address`
- `blocked`

## Route rationale values

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

## No-change countercase status

Use exactly one per comment:

- `defeated`
- `not-defeated`
- `unresolved`

## Reply stance

For each comment, optionally record a `Reply Stance` to help later handoff to
`$logophile`:

- `acknowledge-and-fix`
- `acknowledge-and-bound`
- `rebut-with-evidence`
- `defer-with-scope`
- `ask-for-evidence`

## Handoff permissions

Use separate route permissions:

- `implementation_handoff_allowed`: `yes` only for artifact-backed,
  direction-aligned `act` rows selected as `address` after the gate passes.
- `validation_handoff_allowed`: `yes` only for validation-only or other
  `need-evidence` rows that should route to `$fixed-point-driver` for proof.
- `reply_handoff_allowed`: `yes` only for rebuttal, defer, proof-only thread
  cleanup, or reply-drafting work that should route to `$logophile` or a reply
  draft.

The old single-field `handoff_allowed` is too coarse. Do not use it in v4 output
except when quoting older adjudications.

## Acceptance skew audit

Before finalizing, audit the distribution of dispositions.

If every substantive comment is marked `act`, treat that as a warning sign, not
a victory. Emit an **All-Action Justification** table with these checks:

- `stale/superseded`
- `unsupported`
- `preference-only`
- `out-of-scope`
- `direction-conflicting`
- `review-closure-only`
- `misdiagnosis`
- `proposed-fix validity`
- `validation-only alternative`
- `shared-invariant`

Each row must include `result`, `evidence ref`, and `why action still warranted`.
Generic language like "all comments are valid" is insufficient.

If this block is missing, generic, or unsupported by artifact evidence, set:

```md
adjudication_complete: fail
implementation_handoff_allowed: no
Adjudication Bottom Line: Blocked: all-action adjudication lacks justification.
```

Do not require artificial disposition diversity. Require an all-action safety
proof.

## P2+ severity audit

Before handoff, audit every P2+ reviewer claim.

Emit `## P2+ Severity Audit` with:

- P2+ count
- accepted count
- downgraded count
- rejected count
- unresolved count
- accepted criticality distribution
- unsupported severity labels
- review-closure-only downgrades
- validation-only P2+ rows
- direction-conflicting P2+ rows

If every P2+ row is accepted, emit **All-P2+ Accepted Justification** with these
checks:

- `independent artifact proof`
- `implementation-grade criticality`
- `direction alignment`
- `review-closure-only rejection`
- `downgrade alternative`
- `validation alternative`

Each row must include `result`, `evidence ref`, and `why accepted severity still
warranted`.

## Direction fit audit

Before handoff, audit direction-fit distribution.

Emit `## Direction Fit Audit` with:

- direction source distribution
- same-objective proof
- stale/off-target plan pressure
- conflicting-direction rows
- direction-overriding rows
- rows where `$st`/plan/update-plan changed disposition
- rows where direction was insufficient and blocked/need-evidence was chosen

A direction audit must not claim plan alignment unless the plan source is
same-objective and current, or unless current artifacts create a
`direction-overriding` defect.

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
- `direction-conflict alternative`
- `review-closure-only alternative`
- `fixed-point over-routing check`

Each row must include `result`, `evidence ref`, and `why selected resolution is
still warranted`. Generic language like "all are worth resolving" is
insufficient.

Selection skew is separate from acceptance skew: a report can avoid all-`act`
while still over-selecting downstream work.

## Adjudication completion gate

Before any implementation, validation, or reply handoff, emit an
`Adjudication Gate` block.

Required fields:

- `artifact_state_coverage`: `pass` / `fail`
- `direction_context_coverage`: `pass` / `fail`
- `comment_inventory_coverage`: `pass` / `fail`
- `identity_coverage`: `pass` / `fail`
- `decision_test_coverage`: `pass` / `fail`
- `direction_fit_coverage`: `pass` / `fail`
- `severity_claim_coverage`: `pass` / `fail`
- `p2_plus_acceptance_coverage`: `pass` / `fail`
- `no_change_coverage`: `pass` / `fail`
- `disposition_coverage`: `pass` / `fail`
- `proposed_fix_separation`: `pass` / `fail`
- `evidence_ref_coverage`: `pass` / `fail`
- `validation_value_coverage`: `pass` / `fail`
- `resolve_selection_coverage`: `pass` / `fail`
- `resolve_countercase_coverage`: `pass` / `fail`
- `handoff_agenda_consistency`: `pass` / `fail`
- `selection_skew_audit`: `pass` / `fail`
- `p2_plus_severity_audit`: `pass` / `fail`
- `direction_fit_audit`: `pass` / `fail`
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

### Compact-Gated v4

Use this mode for real PR comment sets:

```md
## Review Basis

artifact_state_id:
  branch:
  base:
  head:
  diff_digest:
  comment_set_digest:
  ci_state:

- branch / PR:
- current artifact evidence:
- tests / CI:
- comments adjudicated:
- limits / unavailable evidence:

## Direction Context Ledger

direction_state_id:
  source:
  source_ref:
  source_freshness:
  same_objective:
  active_frontier:
  locked_decisions:
  non_goals:
  compatibility_posture:
  ownership_boundaries:
  direction_confidence:

## Comment Inventory

- input_comment_count:
- ledger_row_count:
- input_comment_ids:
- ledger_comment_ids:
- missing_comment_ids:
- duplicate_comment_ids:
- synthesized_ids_for_real_comments: yes/no

## PR Why Ledger
## Comment Ledger
| id/thread | reviewer | location | excerpt | claim | reviewer severity claim | accepted criticality | severity acceptance status | direction fit | direction ref | mutation value | concern validity | proposed fix validity | relevance | disposition | no-change status | invariant | evidence grade | evidence ref | severity proof ref | handoff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Decision Tests
| id/thread | grounded | material | fresh | diagnosis | scope-fit | resolution value | no-change defeated | min evidence to change mind |
|---|---|---|---|---|---|---|---|---|

## Direction Tests
| id/thread | direction source | source freshness | same objective | direction fit | direction ref | active frontier | non-goal conflict | direction override | min evidence to change direction |
|---|---|---|---|---|---|---|---|---|---|

## Severity Tests
| id/thread | reviewer severity claim | accepted criticality | severity acceptance status | severity proof ref | downgrade/reject reason | p2+ accepted | min evidence to accept severity |
|---|---|---|---|---|---|---|---|

## No-Change Countercases
## Governing Invariant Ledger
## Specialist Packet Receipts
## Act On
## Rebut
## Defer / Out of Scope
## Need Evidence
## Resolve Selection
| id/thread | resolve decision | reason | proof ref | next | route rationale |
|---|---|---|---|---|---|
## Resolve Countercases
## Invariant-Level Handoff
## Acceptance Skew Audit
## All-Action Justification
## P2+ Severity Audit
## All-P2+ Accepted Justification
## Direction Fit Audit
## Selection Skew Audit
## All-Selected Justification
## Adjudication Gate
## Handoff Agenda
## Adjudication Bottom Line
```

Omit `Specialist Packet Receipts` only when no specialists were used. Omit
`All-Action Justification` only when at least one substantive comment is not
`act`; still include `Acceptance Skew Audit`. Omit `All-P2+ Accepted
Justification` only when at least one P2+ row is downgraded, rejected, or
unresolved, or when there are no P2+ rows. Omit `All-Selected Justification` only
when at least one substantive comment is not `address` or `validate-only`; still
include `Selection Skew Audit`.

### Standard

Standard output may include expanded per-comment analysis, but it must end with
the full Compact-Gated v4 tail and Adjudication Gate.

### Fast

Fast output may compress reasoning into decision buckets, but it must still
preserve comment identity, include acceptance, P2+, direction, and selection
skew audits, and emit an Adjudication Gate. If identity, inventory,
artifact-state, direction-state, severity, or no-change coverage is missing,
Fast mode must block implementation handoff.

## Handoff rules

- Route to `$accretive-implementer` when the accepted agenda is narrow,
  accretive, locally reviewable, artifact-backed, direction-aligned,
  implementation-critical, and not validation-only.
- Route to `$fixed-point-driver` when accepted comments are coupled,
  contentious, invariant-level, structural, validation-only, or likely to reopen
  one another.
- Route to `$logophile` only for drafting replies, naming, or wording.
- For `$resolve` or PR-thread cleanup, route proof-only stale/already-fixed or
  review-closure-only comments as `resolve-thread-only`, not as implementation
  work.
- If the correct response is no code change, do not create an implementation
  handoff.
- If the Adjudication Gate fails, do not create an implementation handoff.
- If validation-only is the correct next move, route validation, not mutation.
- The Handoff Agenda must be a subset-preserving projection of Resolve
  Selection. It must not add implementation items that are not `address`.
- Do not route a single narrow local action to `$fixed-point-driver` unless the
  route rationale is coupled, invariant-level, structural, validation-only,
  contentious, or likely-to-reopen.

## Machine-check hook

When automation is available, run the checker against the adjudication output
before routing implementation:

```bash
python codex/skills/review-adjudication/tools/review_adjudication_gate.py adjudication.md
```

A failed checker result means the adjudication is incomplete. Re-run adjudication
with the missing fields instead of implementing.

## Hard rules

- Do not turn adjudication into implementation.
- Do not treat reviewer severity as accepted criticality.
- Do not treat memory artifacts as infallible.
- Do not treat stale, off-target, or wrong-objective `$st`/plan state as current
  direction evidence.
- Do not force action on preference-only, stale, unsupported, direction-conflicting,
  review-closure-only, or out-of-scope comments.
- Do not mark a comment `act` merely because it is easy to fix.
- Do not mark a comment `act` merely because the reviewer is probably right.
- Do not mark a comment `act` merely because it is labeled P0/P1/P2.
- Do not mark a comment `act` without current evidence grade, evidence ref,
  direction fit, direction ref, mutation value, accepted criticality, and defeated
  no-change case.
- Do not let `review-closure` justify code mutation.
- Do not select `validate-only` unless validation would change a material
  decision.
- Do not accept a local fix when the real issue is a governing invariant.
- Do not route validation-only work as implementation.
- Do not route `resolve-thread-only`, `do-not-address`, or `blocked` selections
  into `$fixed-point-driver` as implementation work.
- Do not emit duplicate singleton sections; duplicate ledgers or gates are
  treated as contradictory and fail the checker.
- Do not let `Handoff Agenda` broaden or contradict `Resolve Selection`.
- Do not hide uncertainty; say exactly what evidence is missing.
- Do not allow `adjudication_complete: pass` if any required gate field fails.
- Do not allow `implementation_handoff_allowed: yes` if the mechanical checker
  fails or if any `act` row lacks current evidence, direction alignment, or
  accepted implementation-grade criticality.

## Resources

- [seq-rationale-ladder.md](references/seq-rationale-ladder.md)
- [adjudication-ledger.md](references/adjudication-ledger.md)
- [criticality-rubric.md](references/criticality-rubric.md)
- [adjudication-gate-contract.md](references/adjudication-gate-contract.md)
- [adjudication-output-template.md](references/adjudication-output-template.md)
- [context-pack.md](references/context-pack.md)
- [example-invocations.md](references/example-invocations.md)
- [common-routing-vocabulary.md](references/common-routing-vocabulary.md)
- [adversarial-eval-seeds.md](references/adversarial-eval-seeds.md)
