---
name: review-adjudication
description: "Adjudicate PR review comments and CAS/Codex findings before implementation with fail-closed direction, severity, source-pressure, mutation-approval, authority-panel clearance, veto, and resolve-selection gates. Treat comments, current review findings, and P2+ labels as claims, not obligations; separate concern approval from fix approval and mutation approval; use current artifacts plus same-objective plan/$st/update_plan context; require trigger-gated authority fanout for grounding/direction/severity/no-change/validation/fix-shape clearance; reject review-closure-only mutation and permissive overrides; and emit a stale-proof ledger plus resolve-selection map: address, validate only, resolve with proof only, rebut, defer, investigate, or block. Trigger for `$review-adjudication`, review the review, adjudicate PR comments, current CAS/Codex finding triage, P2+ finding triage, gate review comments before implementation, refine to comments worth resolving, or select comments to resolve. Not for implementing fixes, writing rebuttals only, or final merge closure."
---

# Review Adjudication

## Intent

Decide which PR review comments, Codex/CAS review findings, or root-equivalent review findings should change code, which should be rebutted, which are stale or out of scope, which require validation only, and which should be reframed as a governing invariant rather than handled as isolated local fixes. When the next workflow is `$fixed-point-driver`, `$resolve`, `$ship`, or thread cleanup, also decide which items are implementation work versus validation-only, proof-only thread resolution, or no-change items.

This skill is **discriminative**, not deferential. A reviewer comment is an input claim, not an obligation. A current CAS/Codex finding is a hypothesis, not implementation permission. A P0/P1/P2 label is a severity claim, not an accepted priority. `act` and `address` are conclusions that must be earned from current artifact evidence, same-objective direction evidence, accepted criticality, mutation approval, and defeated countercases.

## Default mode

Use **Compact-Gated v6** mode whenever the input contains real review comments or current review findings. Compact-Gated v6 is mandatory because automation needs:

- stable raw comment/finding identity
- complete input inventory coverage
- artifact-state identity for stale-handoff detection
- direction-state identity for same-objective plan and scope detection
- explicit decision, direction, severity, and mutation-approval tests for every row
- reviewer severity claim versus accepted criticality separation
- concern approval, fix approval, and mutation approval separation
- source-pressure auditing so current CAS/Codex findings do not become default implementation work
- authority packet receipts, clearance matrix, and veto ledger so implementation requires independent clearances
- permissive-override blocking so root cannot silently upgrade against a veto
- resolve-selection mapping for implementation, validation, proof-only thread resolution, no-change, and blocked outcomes
- no-change and no-resolve countercases so “real concern” cannot collapse into “address now”
- validation-value checks so `validate-only` is not a laundering path
- P2+ severity auditing so high labels cannot pass from reviewer authority
- selection-skew auditing so “all are worth resolving” cannot pass silently
- handoff-agenda consistency checks so selected work is not broadened later
- separate implementation, validation, and reply handoff permissions

Other modes are allowed only when they still satisfy the completion gate:

- **Standard**: expanded reasoning plus the full Compact-Gated v6 tail.
- **Fast**: bucket-only output plus the completion gate; allowed for exploratory triage or synthetic comments, not for implementation handoff unless the gate passes.

## Doctrine

Operate in **DISCRIMINATIVE**, **REBUTTAL-FIRST**, **DIRECTION-GATED**, **P2+-SKEPTICAL**, **MUTATION-APPROVAL-SEPARATED**, **AUTHORITY-PANEL-GATED**, **SOURCE-PRESSURE-AWARE**, **INVARIANT-SEEKING**, **ANTI-RUBBER-STAMP**, **EVIDENCE-WEIGHTED**, **VALIDATION-BUDGETED**, **STALE-PROOF**, and **FAIL-CLOSED** mode.

- **DISCRIMINATIVE**: separate true concerns from irrelevant, stale, unsupported, preference-only, misdiagnosed, misframed, or low-value comments.
- **REBUTTAL-FIRST**: for each row, construct the strongest no-change countercase before deciding to act.
- **DIRECTION-GATED**: a locally valid comment is not implementation-worthy unless it aligns with the active PR/codebase direction, an explicit user goal, a locked same-objective plan decision, or a direction-overriding current defect.
- **P2+-SKEPTICAL**: P0/P1/P2 labels require independent severity acceptance from current artifacts, tests, contracts, or same-objective direction evidence.
- **MUTATION-APPROVAL-SEPARATED**: concern approval, fix approval, and mutation approval are different decisions. Mutation approval is the narrowest and must be explicit.
- **AUTHORITY-PANEL-GATED**: implementation requires independent clearances for evidence, direction/ownership, criticality, no-change defeat, validation value, and fix shape. Any unresolved authority veto blocks `address`.
- **SOURCE-PRESSURE-AWARE**: current CAS/Codex findings receive extra scrutiny because invariant-sounding automated findings can over-select implementation. A current automated finding is a hypothesis until authority clearance and root acceptance.
- **REVIEW-CLOSURE-IS-NOT-MATERIALITY**: review closure may justify a proof-bearing reply or thread resolution; it does not by itself justify code mutation.
- **INVARIANT-SEEKING**: look for the governing invariant behind repeated local comments; avoid fixing the same invariant piecemeal.
- **ANTI-RUBBER-STAMP**: do not let plausibility, politeness, reviewer authority, severity label, current-review status, or ease of implementation become acceptance evidence.
- **EVIDENCE-WEIGHTED**: rank current artifacts above memories, memories above intuition, and direct proof above consensus.
- **VALIDATION-BUDGETED**: `validate-only` is selected only when validation would materially change merge safety, implementation direction, release posture, accepted criticality, or an invariant decision.
- **STALE-PROOF**: bind adjudication to branch/head/diff/comment-set and direction state so downstream handoffs can detect stale or contradictory agendas.
- **FAIL-CLOSED**: if the adjudication contract is incomplete, block implementation handoff rather than guessing.

## Contract

- Review comments and review findings are claims to test, not truths to obey.
- Reviewer severity labels are claims to test, not priority assignments.
- Current CAS/Codex findings are hypotheses to adjudicate, not default implementation work.
- `act` is a disposition conclusion, not the default.
- `address` is downstream implementation selection, not a synonym for “valid”.
- Current artifact state outranks reviewer intuition.
- Current same-objective direction state outranks stale or unrelated plans.
- Prefer current-session artifacts over memories.
- Use memories as secondary rationale support and provenance, not as the sole basis for acting.
- Distinguish concern validity from proposed-fix validity.
- Distinguish concern approval from fix approval and mutation approval.
- Distinguish reviewer severity claim from accepted criticality.
- Distinguish review-closure value from codebase materiality.
- Preserve raw comment identity; do not let summaries replace comment IDs, reviewers, excerpts, locations, source, or input inventory.
- Preserve artifact-state identity; do not let a handoff become stale invisibly.
- Preserve direction-state identity; do not let an old plan or wrong-objective `$st` frontier become hidden implementation permission.
- Tail-weight outputs for CLI use.
- Do not implement fixes here.
- Do not create an implementation handoff unless the Adjudication Gate passes, `implementation_handoff_allowed: yes`, and the Authority Clearance Matrix marks the row `cleared-for-address`.
- Do not collapse adjudication into “all comments are worth resolving”; emit the resolve-selection map before implementation or thread-resolution handoff.
- Validation-only handoff is not implementation permission.
- Proof-only thread resolution is not implementation permission.
- Reply handoff is not implementation permission.

## Dependencies

This skill may use these context sources when needed:

- `$seq`: rationale recovery, plan-search, artifact-search, and prior-session provenance.
- `$st`: durable task/source-of-truth state in `.step/st-plan.jsonl`.
- Built-in task/plan surface: current execution projection only, not canonical durable direction.

If `$seq` or `$st` is unavailable, proceed only from current artifacts and mark unavailable fields as `unknown` or `unavailable` instead of inventing intent.

## Authority fanout mode

This skill uses subagents to solve both bandwidth and authority. Subagents are not ordinary reviewers and they do not vote. Each authority lane owns one bounded clearance dimension. The root adjudicator still emits the final ledger, but root may not silently upgrade a row to `address` against an unresolved authority veto.

Default posture:

- For empty live comment sets, already-fixed proof-only threads, or synthetic triage with no implementation handoff, root-equivalent authority packets are acceptable.
- For any current unresolved review finding, current CAS/Codex finding, invariant-framed finding, or row being considered for `address`, use authority fanout or emit root-equivalent authority packets with the same schema.
- For P2+ rows that might be `address`, all-current-finding selected runs, `$st`/plan-derived direction, weak no-change countercases, or rejected validation alternatives, use the full six-lane authority panel unless a root-equivalent packet gives stronger current evidence.

Authority lanes:

| role | owns | clearance question | blocks |
|---|---|---|---|
| `evidence-authority` | grounding and reachability | Is the finding grounded in current artifacts and reachable or proof-surface-falsifying? | ungrounded, unreachable, stale, missing proof |
| `direction-ownership-authority` | direction, scope, owner | Is the mutation same-objective, direction-aligned, and owned by this PR/boundary? | wrong-owner, out-of-scope, direction-conflicting |
| `criticality-authority` | severity/materiality | Is accepted criticality implementation-grade rather than review-closure-only? | severity-downgraded, review-closure-only, low-value |
| `no-change-advocate` | strongest rejection case | Is the no-change/proof-only/defer route defeated? | already-fixed, duplicate-boundary, proof-only, preserved no-change |
| `validation-value-authority` | proof-first routing | Should validation precede mutation, and would validation change a material decision? | validate-first, no-validation-value, curiosity validation |
| `fix-shape-authority` | minimum safe fix | Is the proposed/replacement fix the minimum safe cut? | wrong-fix, overbroad-fix, hidden invariant |

Authority packets use this shape:

```yaml
authority_packet:
  role: evidence-authority | direction-ownership-authority | criticality-authority | no-change-advocate | validation-value-authority | fix-shape-authority
  packet_status: accepted | rejected | root-equivalent
  artifact_state_id: "..."
  direction_state_id: "..."
  scoped_comment_ids: []
  scope_match: yes | no
  artifact_state_match: yes | no
  direction_state_match: yes | no | not-applicable
  clearance_by_id:
    "<id>": clear | veto | unresolved | defeated | mutate-now | validate-first | no-validation-value | not-required
  vetoes:
    - id:
      class:
      claim:
      evidence_ref:
      required_to_clear:
  positive_evidence:
    - id:
      evidence_ref:
      claim:
  packet_status_reason:
```

Reject stale, wrong-scope, wrong-objective, wrapper-leaking, acknowledgement-only, role-exceeding, or no-evidence packets. Rejected packets are logged but have no authority.

Root authority is asymmetric:

- Root may always downgrade: `address` -> `validate-only`, `resolve-thread-only`, `do-not-address`, `defer`, or `blocked`.
- Root may not upgrade: a row with `veto`, `unresolved`, or missing required authority clearance cannot become `address`.
- To clear a veto, rerun the relevant authority lane or emit a root-equivalent authority packet with stronger current evidence.

Required authority output sections:

- `## Authority Packet Receipts`
- `## Authority Clearance Matrix`
- `## Authority Veto Ledger`

`address` requires `authority status: cleared-for-address` and no row in `Authority Veto Ledger` for that id.

## Required input context

When possible, build a compact context pack before adjudication:

```md
Review comments/findings:
- raw id/thread/finding id:
- reviewer/source: human | github-review | pr-thread | cas-codex | codex-review | automated-review | root-equivalent | unknown
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

Do not feed the whole repository by default. Add more context only when current artifacts cannot decide grounding, scope, freshness, intent, direction-fit, severity acceptance, mutation approval, evidence grade, or handoff shape.

## Direction-source ladder

Use direction context to decide whether a comment is aligned with where the codebase and current PR are intentionally headed. Direction context is not defect proof.

Preferred ladder:

1. explicit current user instruction for this turn or PR
2. current PR description, issue, or design doc tied to the active branch
3. current `.step/proposed-plan.md` when same-objective and fresh
4. `$st` durable active frontier from `.step/st-plan.jsonl` when same-objective and fresh
5. built-in task/plan projection when it matches `$st` or current objective
6. repo conventions and ownership boundaries found in current artifacts
7. `$seq` recovered same-objective plan/session rationale
8. memory-derived direction evidence

Rules:

- Treat `$st` as durable source of truth when the plan file is current and same-objective.
- Treat built-in task/update-plan as a display/projection, not canonical durable direction.
- Treat `.step/proposed-plan.md` as a direction source only when it is for the same objective and not superseded by `$st`, user instruction, or current artifacts.
- Treat off-target, stale, or wrong-branch plans as evidence against action, not permission to act.
- A recovered plan can explain why a comment might matter, but current artifacts still decide grounding and current direction decides scope.
- If direction context is unavailable and it materially affects actionability, mark affected rows `need-evidence` or `blocked`; do not act from invented direction.

## `$seq` rationale recovery

Use `$seq` when the PR why, direction, non-goals, or codebase trajectory is missing, disputed, stale, or likely to change adjudication.

Preferred ladder:

1. `plan-search`
2. `artifact-search`
3. `find-session` + `session-prompts`
4. `memory-map`
5. `memory-provenance`
6. `memory-history`

Use `$seq` to recover rationale, not to manufacture obligations. A recovered plan can explain why a comment matters, but current artifacts still decide whether the comment is grounded, stale, in scope, aligned, or actionable.

## Approval taxonomy

Every row must receive exactly one `approval_class`:

| class | meaning | normal resolve decision |
|---|---|---|
| `A1-current-owned-defect` | Current code violates a contract this PR owns. | `address` |
| `A2-proof-surface-false-positive` | Certificate/test/replay/audit proof can report success while omitting a required obligation. | `address` |
| `A3-active-direction-mismatch` | Code conflicts with locked/current plan direction. | `address` |
| `A4-minimal-illegal-state-removal` | Narrow fix removes an invalid state without broadening scope. | `address` |
| `B1-plausible-route-changing-validation` | Plausible but unproven; validation would change route. | `validate-only` |
| `B2-valid-already-fixed` | Concern valid historically or conceptually, but current HEAD already satisfies it. | `resolve-thread-only` |
| `B3-valid-not-this-pr` | Real issue, wrong timing or owner. | `do-not-address` or `defer` |
| `B4-valid-concern-wrong-fix` | Symptom real, proposed mutation wrong or overbroad. | replacement `address` only if it becomes A-class; otherwise `defer`/`do-not-address` |
| `C1-unsupported` | No artifact-backed concern. | `rebut` / `do-not-address` |
| `C2-preference-only` | Style/naming/cleanup without convention or direction. | `do-not-address` |
| `C3-review-closure-only` | Value is mainly closing thread. | `resolve-thread-only` or reply |
| `C4-direction-conflicting` | Would move codebase away from selected direction. | `defer` / `rebut` |
| `blocked` | Required identity/state/evidence is missing. | `blocked` |
| `unknown` | Exploratory only; blocks implementation. | `blocked` |

Implementation approval is legal only for A-class rows.

## Act validity rule

A row may be marked `act` only if all are true:

1. Current artifacts ground the concern.
2. The action passes Direction Fit:
   - `direction_fit: aligned`, or
   - `direction_fit: direction-overriding` because current artifacts prove a correctness, security, safety, data-loss, compatibility, or other critical defect that must be handled even if the active plan omitted it.
3. The concern is material to the codebase direction, not merely material to review closure.
4. The comment/finding is fresh for the current artifact state.
5. The strongest no-change countercase is defeated.
6. The proposed fix is valid, or the chosen handoff replaces it with a valid minimum fix shape.
7. The action fits this PR's scope, constraints, intended change, non-goals, compatibility posture, and ownership boundaries.
8. The row has `evidence_grade` of `current-artifact`, `current-test`, `current-ci`, or `current-session-artifact`.
9. The row has concrete `evidence_ref`, `direction_ref`, and proof-after-fix reference.
10. The row has `mutation_value: codebase-material`.
11. The row has `mutation_approved: yes` in Mutation Approval Tests.
12. The row has an A-class `approval_class`.
13. `accepted_criticality` is implementation-grade: `blocker`, `security-critical`, `safety-critical`, `data-loss-critical`, `correctness-critical`, `compatibility-critical`, or `direction-critical`.
14. For `reviewer_severity_claim: P0|P1|P2`, the row has `severity_acceptance_status: accepted`, implementation-grade `accepted_criticality`, and concrete `severity_proof_ref`.
15. `resolution value: review-closure` is insufficient for `act` unless another accepted criticality independently justifies mutation.

If any item fails, do not use `act`; use `rebut`, `defer`, `need-evidence`, or `blocked`. `act` requires proof, direction alignment, and mutation approval, not plausibility.

## Mutation approval test

For every row, independently answer:

```md
| id/thread | concern approved | fix approved | mutation approved | approval class | why now | why not alternative | proof after fix |
|---|---|---|---|---|---|---|---|
```

`mutation approved: yes` is legal only when:

- concern approved is `yes`;
- fix approved is `yes`, `partial`, or `no-suggested-fix` with replacement fix shape;
- approval class is A1/A2/A3/A4;
- no-change and no-resolve countercases are defeated;
- validation/proof-only/defer/do-not-address alternatives are explicitly rejected;
- proof after fix is concrete.

## P2+ severity acceptance gate

Reviewer severity is a claim to adjudicate, not an implementation priority.

For any comment whose reviewer asserts or implies P0, P1, or P2:

- Do not preserve the label as accepted severity unless current evidence proves it.
- Do not mark `act` merely because a P2+ label sounds important.
- Do not use `review-closure` as accepted criticality for P2+ mutation.
- Do not select `validate-only` unless the validation result would materially change the implementation, merge, release, compatibility, security, accepted criticality, direction fit, or invariant decision.
- Do not route to `$fixed-point-driver` merely because the label is P2+.

A P2+ row may be `address` only when:

```yaml
reviewer_severity_claim: P0|P1|P2
severity_acceptance_status: accepted
accepted_criticality: blocker|security-critical|safety-critical|data-loss-critical|correctness-critical|compatibility-critical|direction-critical
direction_fit: aligned|direction-overriding
approval_class: A1-current-owned-defect|A2-proof-surface-false-positive|A3-active-direction-mismatch|A4-minimal-illegal-state-removal
mutation_value: codebase-material
mutation_approved: yes
no_change_countercase_status: defeated
evidence_grade: current-artifact|current-test|current-ci|current-session-artifact
severity_proof_ref: concrete
```

Otherwise:

- use `need-evidence` only when a bounded validation would change the route;
- use `defer` when the concern is real but belongs to a separate plan/migration;
- use `rebut` when the severity is unsupported or misdiagnosed;
- use `do-not-address` when the item is review-closure-only, out-of-lane, preference-only, stale, direction-conflicting, or not decision-changing.

## Current CAS/Codex finding gate

Current CAS/Codex findings are high-pressure hypotheses. They often arrive with invariant language, so they require explicit source-pressure handling.

For rows with `review_source: cas-codex|codex-review|automated-review|root-equivalent` and `fresh: current`:

- Root must prove artifact grounding, reachability or false-proof-surface risk, ownership, and minimum fix shape.
- Root must consider a wrong-hypothesis alternative.
- Root must consider `valid-but-not-this-PR`, `proof-only`, and `validate-before-mutation` alternatives.
- If every current automated finding is selected as `address` or `validate-only`, emit `## All-Current-Finding Selected Justification`.
- Authority packet agreement may increase confidence only within its lane; it cannot substitute for mutation approval, no-change defeat, or veto clearance.

## Rebuttal-first pass

Before marking a row `act`, write the strongest plausible no-change countercase.

A no-change countercase may be:

- unsupported by the current artifact state
- stale or superseded
- preference-only
- locally valid but out of scope for this PR
- locally valid but direction-conflicting
- valid but already fixed on HEAD
- valid but not this PR
- review-closure-only
- valid concern with wrong/overbroad fix
- local fix hides the governing invariant
- non-accretive broadening without proof
- assumes a contract this PR does not own
- evidence insufficient and the correct next step is validation only
- severity claim unsupported or downgraded
- current CAS/Codex hypothesis plausible but not yet accepted

Only mark `act` when artifact and direction evidence defeat the no-change countercase. If the countercase is not defeated, use `rebut`, `defer`, `need-evidence`, or `blocked`.

## Validation-only escape hatch

Do not mutate code just because a concern might be real. When uncertainty is material and a validating check is the correct next step, use:

```md
disposition: need-evidence
reframe_type: validation-only
remediation_posture: validating-check-only
proposed_fix_validity: validation-only
approval_class: B1-plausible-route-changing-validation
mutation_value: validation-material
mutation_approved: no
handoff_action: route-to-fixed-point-driver
```

Validation-only handoff may create tests, probes, logs, or inspections. It must not implement the reviewer's requested code change unless the validation fails or current artifacts already prove the concern.

Validation-only requires decision value, not curiosity value. Use `validate-only` only when validation would change at least one of:

- accepted criticality
- direction fit
- merge safety
- release/compatibility posture
- invariant handoff
- implementation scope
- rebut/defer/address selection

If the likely result would only satisfy curiosity, reviewer comfort, or review closure, use `do-not-address`, `resolve-thread-only`, or `rebut` instead.

Hard constraints:

- `proposed_fix_validity: validation-only` requires `disposition: need-evidence`.
- `need-evidence` must not route directly to `$accretive-implementer`.
- `validation_handoff_allowed: yes` is not implementation permission.
- `validate-only` requires `approval_class: B1-plausible-route-changing-validation` and `mutation_value: validation-material`.

## Resolve-selection overlay

Use this overlay whenever the prompt asks which comments are worth resolving, which reviews/comments to address, whether to resolve PR review threads, or when the likely next step is `$fixed-point-driver`, `$resolve`, `$ship`, or final PR comment cleanup.

Allowed `resolve_decision` values:

- `address`: the row is `act`, the Act validity rule passed, direction gate passed, accepted criticality is implementation-grade, mutation approval is yes, and implementation handoff is allowed.
- `validate-only`: the row is `need-evidence`; the next workflow may add a probe, test, or inspection, but must not implement the requested code change until evidence defeats the no-change case.
- `resolve-thread-only`: the concern is stale, superseded, already fixed on current artifact state, or otherwise needs only a proof-bearing reply/thread resolution. No code change is selected.
- `do-not-address`: the row should be rebutted, deferred, treated as out of scope, unsupported, preference-only, direction-conflicting, review-closure-only, or left unresolved pending product/user direction.
- `blocked`: identity, freshness, PR rationale, direction state, evidence, severity acceptance, mutation approval, resolve-selection, or gate coverage is insufficient to choose a downstream action.

Selection rules:

- `address` is legal only for rows whose disposition is `act`, whose no-change countercase is `defeated`, whose Decision/Direction/Severity/Mutation Approval Tests satisfy the Act validity rule, whose `approval_class` is A1/A2/A3/A4, and whose `mutation_value` is `codebase-material`.
- `address` is illegal when `direction_fit` is `neutral`, `conflicting`, or `unknown`.
- `address` is illegal for P2+ unless `severity_acceptance_status: accepted`.
- `validate-only` is legal only for rows whose disposition is `need-evidence`, whose `approval_class` is `B1-plausible-route-changing-validation`, and whose `mutation_value` is `validation-material`.
- `validate-only` is illegal when the only value is reviewer comfort, curiosity, or review closure.
- `resolve-thread-only` must name the proof that makes a code change unnecessary, such as latest-HEAD code evidence, a passing regression, or an already-pushed commit.
- `resolve-thread-only` is preferred over `address` when the only material value is review closure.
- `do-not-address` must name the preserved no-change case.
- `blocked` must name the missing evidence and set `adjudication_complete: fail` and all handoff permissions to `no`.
- The `Handoff Agenda` may include implementation work only for `address` items and validation/proof work only for `validate-only` items. Proof-only stale or already-fixed comments may be routed for replies/thread cleanup, not mutation.
- If all rows are `resolve-thread-only`, `do-not-address`, or `blocked`, do not route to `$fixed-point-driver` for implementation.
- Every row must include a concrete `proof ref` and `route rationale`.
- `route-to-fixed-point-driver` requires route rationale `coupled-comments`, `invariant-level`, `structural`, `validation-only`, `contentious`, or `likely-to-reopen`.
- `route-to-accretive-implementer` requires `route rationale: narrow-local`.
- `resolve-thread-only` requires `route rationale: proof-only-thread`.
- `do-not-address` requires `route rationale: no-change`.
- `blocked` requires `route rationale: blocked`.

## Resolve countercase pass

After the adjudication disposition and before downstream handoff, challenge the selected resolve decision itself. Concern validity is not the same as “worth resolving now”.

Emit `## Resolve Countercases` with one entry per row:

```md
- `<id/thread>`:
  - proposed resolve decision:
  - strongest alternative resolve decision:
  - why alternative is rejected / preserved / unresolved:
```

Examples:

- An `address` row must defeat the strongest `validate-only`, `resolve-thread-only`, or `do-not-address` alternative.
- A `validate-only` row must explain why immediate mutation is not yet justified and why validation would change a material decision.
- A `resolve-thread-only` row must explain why no code change is selected.
- A `do-not-address` row must preserve the no-change case.
- A `blocked` row must name the missing evidence that prevents selection.

## Governing invariant pass

After individual adjudication, cluster comments that appear to point at the same underlying invariant, source-of-truth rule, ownership boundary, soundness obligation, direction boundary, or API contract.

When multiple comments share an invariant:

- do not treat them as unrelated local fixes;
- name the governing invariant;
- decide whether the correct handoff is an invariant-level change;
- route to `$fixed-point-driver` when the comments are coupled, contentious, structural, validation-only, or likely to reopen one another;
- route to `$accretive-implementer` only when the invariant-level agenda is narrow, accretive, direction-aligned, implementation-critical, and locally reviewable.

If no invariant cluster exists, say so explicitly and set `invariant_pass: pass` only after checking.

## Vocabulary

### Review source values

- `human`
- `github-review`
- `pr-thread`
- `cas-codex`
- `codex-review`
- `automated-review`
- `root-equivalent`
- `unknown`

### Evidence grades

- `current-artifact`
- `current-test`
- `current-ci`
- `current-session-artifact`
- `prior-session-artifact`
- `memory-only`
- `reviewer-only`
- `none`

`act` requires `current-artifact`, `current-test`, `current-ci`, or `current-session-artifact`.

### Direction sources

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

### Direction fit values

- `aligned`
- `direction-overriding`
- `neutral`
- `conflicting`
- `unknown`

### Source freshness values

- `current`
- `stale`
- `off-target`
- `unknown`

### Same-objective values

- `yes`
- `no`
- `unknown`

### Reviewer severity claim values

- `P0`
- `P1`
- `P2`
- `P3`
- `P4`
- `unlabeled`
- `unknown`

### Accepted criticality values

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

### Severity acceptance status values

- `accepted`
- `downgraded`
- `rejected`
- `unresolved`

### Mutation value values

- `codebase-material`
- `validation-material`
- `proof-only`
- `reply-only`
- `no-change`
- `blocked`

### Concern validity values

- `valid`
- `partial`
- `unsupported`
- `unknown`

### Proposed-fix validity values

- `valid`
- `partially-valid`
- `wrong-fix`
- `overbroad`
- `under-specified`
- `not-applicable`
- `validation-only`

### Relevance classes

- `material-relevant`
- `relevant-nonmaterial`
- `partially-relevant`
- `stale-or-superseded`
- `unsupported`
- `out-of-scope`
- `preference-only`
- `direction-conflicting`
- `review-closure-only`

### Disposition values

- `act`
- `rebut`
- `defer`
- `need-evidence`
- `blocked`

### Decision Test values

- `grounded`: `yes` / `no` / `unknown`
- `material`: `yes` / `no` / `user-requested` / `unknown`
- `fresh`: `current` / `stale` / `superseded` / `unclear`
- `diagnosis`: `correct` / `partially-correct` / `misdiagnosed` / `unknown`
- `scope-fit`: `yes` / `no` / `partial` / `unknown`
- `resolution value`: `merge-blocking` / `correctness-critical` / `direction-critical` / `review-closure` / `proof-only` / `validation-needed` / `low-value` / `out-of-lane` / `blocked`
- `no-change defeated`: `yes` / `no` / `unresolved`

`review-closure` is not an implementation-qualifying resolution value.

## Required audits

### Acceptance skew audit

If every substantive row is marked `act`, emit **All-Action Justification** with these checks:

- `stale/superseded`
- `unsupported`
- `preference-only`
- `out-of-scope`
- `direction-conflicting`
- `review-closure-only`
- `misdiagnosis`
- `proposed-fix validity`
- `mutation approval`
- `validation-only alternative`
- `shared-invariant`

Each row must include `result`, `evidence ref`, and `why action still warranted`.

### P2+ severity audit

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

If every P2+ row is accepted, emit **All-P2+ Accepted Justification** with these checks:

- `independent artifact proof`
- `implementation-grade criticality`
- `direction alignment`
- `review-closure-only rejection`
- `downgrade alternative`
- `validation alternative`

### Direction fit audit

Emit `## Direction Fit Audit` with:

- direction source distribution
- same-objective proof
- stale/off-target plan pressure
- conflicting-direction rows
- direction-overriding rows
- rows where `$st`/plan/update-plan changed disposition
- rows where direction was insufficient and blocked/need-evidence was chosen

### Source pressure audit

Emit `## Source Pressure Audit` with:

- review source distribution
- current automated finding count
- current automated findings selected as address
- current automated findings selected as validate-only
- current automated findings not selected
- CAS/Codex wrong-hypothesis alternatives considered
- current reviewer/CAS claims rebutted/deferred
- all-current-finding selected pressure: yes/no

If every current automated finding is selected as `address` or `validate-only`, emit **All-Current-Finding Selected Justification** with these checks:

- `artifact/reachability proof`
- `CAS/Codex wrong-hypothesis alternative`
- `valid-but-not-this-PR alternative`
- `proof-only alternative`
- `validate-before-mutation`
- `direction and scope ownership`
- `mutation budget justification`

### Selection skew audit

If every substantive row is selected as `address` or `validate-only`, emit **All-Selected Justification** with these checks:

- `stale/already-fixed alternative`
- `proof-only thread-resolution alternative`
- `do-not-address alternative`
- `validate-before-mutation alternative`
- `out-of-scope/defer alternative`
- `valid-but-not-this-PR alternative`
- `direction-conflict alternative`
- `review-closure-only alternative`
- `fixed-point over-routing check`

## Adjudication completion gate

Before any implementation, validation, or reply handoff, emit `## Adjudication Gate`.

Required fields:

- `artifact_state_coverage`: `pass` / `fail`
- `direction_context_coverage`: `pass` / `fail`
- `comment_inventory_coverage`: `pass` / `fail`
- `identity_coverage`: `pass` / `fail`
- `decision_test_coverage`: `pass` / `fail`
- `direction_fit_coverage`: `pass` / `fail`
- `severity_claim_coverage`: `pass` / `fail`
- `mutation_approval_coverage`: `pass` / `fail`
- `p2_plus_acceptance_coverage`: `pass` / `fail`
- `no_change_coverage`: `pass` / `fail`
- `disposition_coverage`: `pass` / `fail`
- `proposed_fix_separation`: `pass` / `fail`
- `evidence_ref_coverage`: `pass` / `fail`
- `validation_value_coverage`: `pass` / `fail`
- `resolve_selection_coverage`: `pass` / `fail`
- `resolve_countercase_coverage`: `pass` / `fail`
- `handoff_agenda_consistency`: `pass` / `fail`
- `source_pressure_audit`: `pass` / `fail`
- `selection_skew_audit`: `pass` / `fail`
- `p2_plus_severity_audit`: `pass` / `fail`
- `direction_fit_audit`: `pass` / `fail`
- `invariant_pass`: `pass` / `fail`
- `authority_fanout_required`: `pass` / `fail`
- `authority_packet_coverage`: `pass` / `fail`
- `authority_clearance_coverage`: `pass` / `fail`
- `authority_veto_coverage`: `pass` / `fail`
- `permissive_override_absent`: `pass` / `fail`
- `acceptance_skew_audit`: `pass` / `fail`
- `adjudication_complete`: `pass` / `fail`
- `implementation_handoff_allowed`: `yes` / `no`
- `validation_handoff_allowed`: `yes` / `no`
- `reply_handoff_allowed`: `yes` / `no`

`adjudication_complete` may be `pass` only when every preceding required field is `pass`. Authority packet coverage cannot be `not-used`; simple cases must use root-equivalent authority packets.

If any required field fails, the bottom line must be:

```md
Blocked: incomplete adjudication. Do not implement yet.
```

## Output contract

### Compact-Gated v6

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
| id/thread | reviewer | review source | location | excerpt | claim | reviewer severity claim | accepted criticality | severity acceptance status | direction fit | direction ref | approval class | mutation value | concern validity | proposed fix validity | relevance | disposition | no-change status | invariant | evidence grade | evidence ref | severity proof ref | handoff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Decision Tests
| id/thread | grounded | material | fresh | diagnosis | scope-fit | resolution value | no-change defeated | min evidence to change mind |
|---|---|---|---|---|---|---|---|---|

## Direction Tests
| id/thread | direction source | source freshness | same objective | direction fit | direction ref | active frontier | non-goal conflict | direction override | min evidence to change direction |
|---|---|---|---|---|---|---|---|---|---|

## Severity Tests
| id/thread | reviewer severity claim | accepted criticality | severity acceptance status | severity proof ref | downgrade/reject reason | p2+ accepted | min evidence to accept severity |
|---|---|---|---|---|---|---|---|

## Mutation Approval Tests
| id/thread | concern approved | fix approved | mutation approved | approval class | why now | why not alternative | proof after fix |
|---|---|---|---|---|---|---|---|

## No-Change Countercases
## Governing Invariant Ledger
## Act On
## Rebut
## Defer / Out of Scope
## Need Evidence
## Authority Packet Receipts
| role | packet status | artifact state match | direction state match | scope match | scoped comment ids | clearance added | veto added | used for | reason |
|---|---|---|---|---|---|---|---|---|---|
## Authority Clearance Matrix
| id/thread | evidence | direction/ownership | criticality | no-change | validation-value | fix-shape | authority status | packet refs |
|---|---|---|---|---|---|---|---|---|
## Authority Veto Ledger
| id/thread | veto source | veto class | veto claim | evidence ref | required to clear | final route |
|---|---|---|---|---|---|---|
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
## Source Pressure Audit
## All-Current-Finding Selected Justification
## Selection Skew Audit
## All-Selected Justification
## Adjudication Gate
## Handoff Agenda
## Adjudication Bottom Line
```

Do not omit `Authority Packet Receipts`, `Authority Clearance Matrix`, or `Authority Veto Ledger`; simple cases use root-equivalent authority packets. Omit `All-Action Justification` only when at least one substantive row is not `act`; still include `Acceptance Skew Audit`. Omit `All-P2+ Accepted Justification` only when at least one P2+ row is downgraded, rejected, or unresolved, or when there are no P2+ rows. Omit `All-Current-Finding Selected Justification` only when at least one current automated finding is not selected as `address` or `validate-only`, or when there are no current automated findings. Omit `All-Selected Justification` only when at least one substantive row is not `address` or `validate-only`; still include `Selection Skew Audit`.

## Handoff rules

- Route to `$accretive-implementer` when the accepted agenda is narrow, accretive, locally reviewable, artifact-backed, direction-aligned, implementation-critical, A-class, mutation-approved, authority-cleared, veto-free, and not validation-only.
- Route to `$fixed-point-driver` when accepted comments are coupled, contentious, invariant-level, structural, validation-only, or likely to reopen one another.
- Route to `$logophile` only for drafting replies, naming, or wording.
- For `$resolve` or PR-thread cleanup, route proof-only stale/already-fixed or review-closure-only comments as `resolve-thread-only`, not as implementation work.
- If the correct response is no code change, do not create an implementation handoff.
- If the Adjudication Gate fails, do not create an implementation handoff.
- If validation-only is the correct next move, route validation, not mutation.
- The Handoff Agenda must be a subset-preserving projection of Resolve Selection. It must not add implementation items that are not `address`.
- Do not route a single narrow local action to `$fixed-point-driver` unless the route rationale is coupled, invariant-level, structural, validation-only, contentious, or likely-to-reopen.

## Machine-check hook

When automation is available, run the checker against the adjudication output before routing implementation:

```bash
python codex/skills/review-adjudication/tools/review_adjudication_gate.py adjudication.md
```

A failed checker result means the adjudication is incomplete. Re-run adjudication with the missing fields instead of implementing.

## Hard rules

- Do not turn adjudication into implementation.
- Do not treat reviewer severity as accepted criticality.
- Do not treat current CAS/Codex findings as implementation work merely because they are current or invariant-shaped.
- Do not treat memory artifacts as infallible.
- Do not treat stale, off-target, or wrong-objective `$st`/plan state as current direction evidence.
- Do not force action on preference-only, stale, unsupported, direction-conflicting, review-closure-only, or out-of-scope comments.
- Do not mark a row `act` merely because it is easy to fix.
- Do not mark a row `act` merely because the reviewer is probably right.
- Do not mark a row `act` merely because it is labeled P0/P1/P2.
- Do not mark a row `act` without current evidence grade, evidence ref, direction fit, direction ref, mutation approval, approval class, accepted criticality, and defeated no-change case.
- Do not let `review-closure` justify code mutation.
- Do not select `validate-only` unless validation would change a material decision.
- Do not accept a local fix when the real issue is a governing invariant.
- Do not route validation-only work as implementation.
- Do not route `resolve-thread-only`, `do-not-address`, or `blocked` selections into `$fixed-point-driver` as implementation work.
- Do not emit duplicate singleton sections; duplicate ledgers or gates are treated as contradictory and fail the checker.
- Do not let `Handoff Agenda` broaden or contradict `Resolve Selection`.
- Do not hide uncertainty; say exactly what evidence is missing.
- Do not allow `adjudication_complete: pass` if any required gate field fails.
- Do not allow `implementation_handoff_allowed: yes` if the mechanical checker fails or if any `act` row lacks current evidence, direction alignment, mutation approval, authority clearance, or accepted implementation-grade criticality.
- Do not let root permissively override an authority veto. Clear the veto with a fresh authority packet or block implementation.
- Do not use authority packets as votes; each packet owns only its bounded clearance dimension.

## Resources

- [criticality-rubric.md](references/criticality-rubric.md)
- [adjudication-gate-contract.md](references/adjudication-gate-contract.md)
- [adjudication-output-template.md](references/adjudication-output-template.md)
- [context-pack.md](references/context-pack.md)
- [common-routing-vocabulary.md](references/common-routing-vocabulary.md)
- [adversarial-eval-seeds.md](references/adversarial-eval-seeds.md)
- [authority-fanout.md](references/authority-fanout.md)
- [example-invocations.md](references/example-invocations.md)
