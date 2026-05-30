---
name: fixed-point-driver
description: "Drive exhaustive build-review-improve-verify loops to a material fixed point across review-adjudication, accretive-implementer, adversarial-reviewer, verification-closure, negative-ledger, learnings-backed evidence, and reduction-first fixed-point compression. Trigger when coding needs de novo re-litigation, proof-gated closure, repeated review/fix loops, review adjudication, negative-evidence pruning, optional read-only specialists, soundness/foot-gun/complexity routing, a mandatory Reduction Pass, a mandatory pre-closure one-change challenge, and closure handoff. Use for harden this patch exhaustively, address PR reviews to closure, keep re-reviewing, find all impactful changes, adjudicate then implement, drive to fixed point, reduce accumulated proof/code surface, or avoid repeating failed routes. Do not use for trivial one-step tasks or when user wants one narrow phase."
---

# Fixed-Point Driver

This skill coordinates the whole workflow until the artifact set reaches a **material fixed point**.

A material fixed point is not just "no more review findings." It is also:

- no unresolved material finding;
- no open soundness, invariant, foot-gun, complexity, verification, or negative-evidence gate;
- no unnecessary duplicate owner, shadow surface, proof lane, compatibility alias, generated artifact, or fixture family left behind by the review/fix loop;
- no additive remediation that survives only because the loop never re-checked whether deletion, privatization, merge, reuse, or boundary tightening would be better.

Companion skills:

- `review-adjudication` for deciding which review comments actually matter
- `accretive-implementer` for implementation and remediation
- `adversarial-reviewer` for full-scope challenge
- `verification-closure` for decisive proof and gating
- `negative-ledger` for routine query, map, capture, reopen, handoff, and negative-evidence pruning
- `learnings` for durable evidence-backed lessons and the preferred persistent source for reusable negative evidence
- `simplify-and-refactor-code-isomorphically` for behavior-preserving collapse, duplicate-surface reduction, and net-negative refactor campaigns when the Reduction Pass selects an isomorphic sub-pass

`fixed-point-driver` owns the Reduction Pass. It may invoke `simplify-and-refactor-code-isomorphically` for a behavior-preserving sub-pass, but reduction is not optional merely because that companion was not invoked.

## Output modes

- **Standard**: full workflow state.
- **Fast**: only the route, current state, negative-ledger result, reduction result, open gates, and exact next action.

## CLI-tail-weighted reporting

- Keep ledgers terse.
- End with **Final State** and **Do Next**.
- **Do Next** must be the last section.
- If the report is long, compress evidence before compressing the negative-ledger result, reduction result, closure state, or exact next action.

## Global doctrine

Every phase inherits **UNSOUND**, **WITNESS-BEARING**, **PRESERVATION-AWARE**, **PROGRESS-AWARE**, **REFINEMENT-AWARE**, **MECHANISTIC**, **ACCRETIVE**, and **TRACEABLE** standards.

Additional orchestration pressure: **EXHAUSTIVE**, **DE NOVO**, **ADVERSARIAL**, **SATURATING**, **MATERIAL**, **FIXED-POINT**, **PARSIMONIOUS**, **SUBTRACTIVE-FIRST**, **INVARIANT-GRADED**, **HAZARD-SEEKING**, **CANONICAL**, **LEDGERIZED**, **HISTORY-AWARE**, **NEGATIVE-EVIDENCE-AWARE**, **REDUCTION-AWARE**, and **REOPENABLE**.

## Code-change doctrine

When writing code or making a change, do it **in the most optimal way possible** for the current material objective.

Rules:

- Prefer the smallest complete design that preserves invariants, removes or narrows foot-guns, and leaves a clear proof path.
- Choose durable, idiomatic, maintainable code over clever shortcuts, speculative abstraction, broad rewrites, or local patch accretion.
- Optimize for correctness and evidence first, then simplicity, performance, ergonomics, and future change cost when they materially affect the task.
- Do not use "optimal" to justify unbounded scope, aesthetic churn, bypassing negative evidence, exceeding lane budgets, weakening review, or skipping closure gates.
- When materially valid implementations compete, record the chosen tradeoff in the Findings, Invariant, Complexity, Verification, Reduction, or Negative Evidence Ledger.

### Subtractive fixed-point doctrine

`ACCRETIVE` means evidence-preserving and reviewable, not additive.

A fixed point is not only that review found nothing else. It is that the active system has one truthful owner for each accepted invariant and no unnecessary surface remains from the loop.

Before adding code, prefer this solution order:

1. Delete stale, duplicated, obsolete, unreachable, misleading, or review-only code/proof/docs.
2. Privatize or narrow a public, exported, package-visible, or compatibility surface.
3. Merge duplicate models, registries, aliases, fixtures, generated artifacts, reports, or proof lanes.
4. Tighten the existing canonical checker, builder, validator, generator, certificate, API, or boundary.
5. Reuse an existing helper, proof lane, test lane, or contract surface.
6. Add new code only when the first five cannot satisfy the invariant.

New code must earn itself by defeating the smaller solution classes. If an additive fix creates a second owner for an invariant, the Reduction Pass remains open.

### Fixed-point accumulation anti-patterns

Do not:

- add a second checker when an existing checker should own the invariant;
- add caller-side prechecks when the certificate, builder, generator, or boundary can reject the bad state;
- add a compatibility alias instead of deleting or privatizing a stale surface;
- add another fixture family when an existing negative fixture can be parameterized;
- add generated reports or docs that mirror executable checks without a current consumer;
- preserve a public surface only because tests still mention it;
- resolve review comments one-by-one when they share a governing invariant;
- treat "all comments addressed" as closure when the solution duplicated ownership;
- treat LOC reduction as success if invariant ownership became less clear;
- treat passing tests as sufficient after deleting proof, certificate, generator, fixture, or public surfaces without checking stale references.

## Optional review-adjudication intake

If the user provides review comments or a prior adjudication result, you may start with **review-adjudication** before any implementation.

Rules:

- Treat adjudicated `Act On` items as routed work, not as unquestionable truth.
- Treat `Rebut`, `Defer / Out of Scope`, and `Need Evidence` as explicit workflow inputs.
- Only re-adjudicate if the rationale is stale, contradictory, or the artifact state has materially changed.
- If review-adjudication materially shapes the route, keep it visible in the Companion Skill Ledger through closure.
- For accepted `address` work, preserve or reconstruct `canonical_owner` and `solution_class` before implementation. If upstream adjudication did not provide them, the Reduction Pass must fill them in.

## Negative-ledger posture

`negative-ledger` is no longer rare or merely optional inside this workflow. For every non-trivial fixed-point run, perform a root-owned **Negative Ledger Pass** at routing preflight and refresh it before closure.

Default behavior:

- Run a root-owned negative-ledger `query`/`map` pass during routing preflight.
- Check current-run witnesses, fixed-point ledgers, review comments, `$learnings`, and repo history when available.
- Normalize any candidate failed attempt into the Negative Evidence Ledger.
- Mark negative evidence as `active`, `stale`, `superseded`, `reopened`, `unknown`, or `need-evidence`.
- Convert only active, witness-bearing, current-state-applicable entries into narrow exclusion rules.
- Emit a `no-applicable-negative-evidence` result when nothing applies; this still counts as a completed pass.
- Capture newly witnessed failed attempts, no-effect changes, regressions, reverts, review rejections, additive churn, duplicate-owner fixes, proof-surface sprawl, and strategy pivots when they are decision-shaping.
- Run a pre-closure `handoff` summary even when there are no active exclusions.

`negative-ledger` is advisory, not a veto authority. It may block closure only when active negative evidence binds the current artifact state and the route reused the disconfirmed path without satisfying reopening criteria.

## Reduction Pass

Every non-trivial Standard run must perform a Reduction Pass during routing preflight and before closure.

Also run a Reduction Pass:

- after two review/remediation cycles;
- after any broad additive fix;
- after an invariant cluster emerges from review-adjudication or adversarial review;
- before escalating from `direct-closure` or `targeted` to a broader specialist lane;
- before declaring candidate material fixed point.

The adapted simplification loop is:

```text
1. BASELINE    -> current artifact state, proof state, changed path set, diff/stat snapshot
2. MAP         -> duplicate owners, shadow surfaces, proof-lane mirrors, stale fixtures, public/private seams
3. MATRIX      -> score reduction candidates by payoff x confidence / risk
4. PROVE       -> preservation/invariant card before deleting, privatizing, merging, or refactoring
5. COLLAPSE    -> delete, privatize, merge, tighten, or reuse before adding
6. VERIFY      -> run targeted/full proof and confirm no stale surface remains
7. LEDGER      -> surface delta, rejected reductions, reason new code survived
8. REPEAT      -> rerun after review/remediation exposes new collapse candidates
```

Use this packet shape:

```yaml
reduction_pass:
  phase: pre-implementation | post-review | pre-closure | escalation-check
  artifact_state_id: "..."
  invariant_or_objective: "..."
  canonical_owner: "..."
  duplicate_or_shadow_surfaces: []
  deletion_candidates: []
  privatization_candidates: []
  merge_candidates: []
  existing_boundary_to_tighten: []
  reuse_candidates: []
  additive_candidates: []
  selected_solution_class: delete | privatize | merge | tighten-existing-boundary | reuse-existing-helper | add-new-code
  surface_reduction_matrix:
    - candidate: "..."
      payoff: 1 | 2 | 3 | 4 | 5
      confidence: 1 | 2 | 3 | 4 | 5
      risk: 1 | 2 | 3 | 4 | 5
      score: 0.0
      decision: apply | reject | defer
      reason: "..."
  preservation_card_required: yes | no
  preservation_card_status: complete | not-needed | blocked
  why_not_smaller: "..."
  why_new_code_if_any: "..."
  net_surface_delta:
    public_symbols: "..."
    compatibility_aliases: "..."
    proof_lanes: "..."
    generated_artifacts: "..."
    fixture_families: "..."
    invariant_owners: "..."
    loc: "..."
```

Rules:

- `add-new-code` is illegal unless delete, privatize, merge, tighten, and reuse were considered and rejected with evidence.
- If multiple findings share an invariant, fix the owner boundary rather than patching findings locally.
- If an additive fix creates a second owner for an invariant, the Reduction Pass remains open.
- If a reduction candidate is rejected because it is unsafe, state the exact preservation axis that fails.
- Whole-file or subsystem deletion requires current scope fit plus proof that the removed surface has no independent obligation, or that its obligation moved to the named canonical owner.
- Line-level deletion, wrapper collapse, fixture consolidation, stale-doc removal, and surface privatization are normal fixed-point work when the preservation/invariant card passes.

### Surface Reduction Matrix

Score reduction candidates with:

```text
Score = (Reduction Payoff x Confidence) / Risk
```

Reduction Payoff:

- 5 = removes a public/exported surface, duplicate proof lane, stale compatibility path, generated artifact family, or whole obsolete subsystem
- 4 = collapses duplicate checker/generator/certificate/model ownership
- 3 = removes helper/wrapper/fixture duplication or narrows a public seam
- 2 = deletes local dead code, redundant test setup, stale docs, or pass-through wrappers
- 1 = small cleanup with little future-review impact

Confidence:

- 5 = current tests/proofs/goldens/manual inspection show the removed surface has no independent obligation
- 4 = all callsites and proof surfaces are mapped
- 3 = local callsites mapped, broader proof impact plausible
- 2 = likely but incomplete evidence
- 1 = aesthetic suspicion

Risk:

- 5 = public API, persisted format, certificate/proof surface, generated artifact, runtime semantics, cross-package contract
- 4 = multi-module invariant or compatibility behavior
- 3 = internal shared helper or test/proof infrastructure
- 2 = local helper/fixture
- 1 = unreachable/pass-through/stale-only surface

Decision rules:

- Apply candidates with Score >= 2.0 when they preserve or strengthen the invariant.
- Reject candidates below threshold unless they are required to remove an active foot-gun.
- If an additive fix is selected while a higher-scoring reduction candidate exists, explain why the reduction is unsafe or insufficient.

### Preservation / Invariant Card

Before any delete, merge, privatize, or refactor change, fill this card when the change is material:

```yaml
preservation_invariant_card:
  intended_semantic_delta:
    behavior_intentionally_changed: yes | no
    illegal_state_or_false_proof_now_rejected: "..."
    behavior_preserving_envelope: "..."
  invariant_owner:
    canonical_owner_after_change: "..."
    owners_removed_or_demoted: []
    why_one_owner_is_sufficient: "..."
  preservation_axes:
    public_api_or_export_shape: "..."
    error_semantics: "..."
    ordering_or_tie_breaking: "..."
    allocation_lifetime_or_ownership: "..."
    laziness_or_evaluation_timing: "..."
    side_effects_logs_metrics_traces: "..."
    fingerprints_refs_domains_versions: "..."
    generated_artifacts_or_fixtures: "..."
    backward_compatibility: "..."
    tests_or_proof_lanes: "..."
  verification:
    negative_fixture_or_counterexample: "..."
    targeted_check: "..."
    full_check: "..."
    residual_uncertainty: "..."
```

For semantic remediation, behavior may intentionally change. The card must say exactly which illegal state, false proof, stale surface, or foot-gun is now impossible.

### Surface Delta Dashboard

Before closure, emit:

```md
## Surface Delta Dashboard
| Metric | Before | After | Delta | Note |
|---|---:|---:|---:|---|
| Public/exported symbols | | | | |
| Internal compatibility aliases | | | | |
| Proof/check lanes | | | | |
| Generated artifacts/docs that mirror checks | | | | |
| Fixture families | | | | |
| Certificate/checker owners for invariant | | | | |
| Changed files | | | | |
| LOC | | | | |
| Tests/proof commands | | | | |
| Residual unresolved findings | | | | |
```

Tension signals:

- LOC up, owner count unchanged: likely local patching; rerun Reduction Pass.
- Proof lanes up, invariant owner unclear: collapse proof surface before closure.
- Public symbols up, non-goal says no public widening: block closure.
- Tests up, no negative fixture for the old failure mode: proof may be review-comfort-only.
- Deletions high, proof unchanged: verify stale references and proof coverage.
- Compatibility aliases survive, but no current downstream proof uses them: privatize or delete unless the route says why not.

## Routing preflight

Every Standard run must establish this compact preflight before implementation, fanout, or closure:

```yaml
routing_preflight:
  task_shape: narrow-review-comment | review-batch | implementation | remediation | hardening | audit | optimization | migration | reduction | unknown
  fixed_point_lane: direct-closure | targeted | expanded-targeted | swarm
  subagent_mode: off | targeted | swarm
  specialist_budget:
    planned: 0 | 1 | 2 | 3 | 4 | "5+"
    reason: "..."
  negative_ledger_required: yes
  negative_ledger_initial_mode: query | map | reopen | handoff
  reduction_pass_required: yes
  reduction_initial_phase: pre-implementation | escalation-check
  companion_stack:
    review_adjudication: used | not-needed | root-equivalent | unavailable
    accretive_implementer: used | root-equivalent | not-needed | unavailable
    adversarial_reviewer: used | root-equivalent | not-needed | unavailable
    verification_closure: used | root-equivalent | not-needed | unavailable
    negative_ledger: queried | mapped | captured | handoff | no-applicable-evidence | unavailable
    learnings: recalled | captured | not-material | unavailable
    simplify_and_refactor_code_isomorphically: used | root-equivalent | not-needed | unavailable
  stop_go_gate:
    proceed: yes | no
    blocking_reason: "none | ..."
```

Rules:

- `root-equivalent` means the root performed the stage's doctrine without a distinct auditable skill invocation.
- `used` means the stage was explicitly invoked or its required output packet was consumed.
- `not-needed` must be justified by task shape, not convenience.
- `unavailable` must include the exact registry, path, or tooling reason.
- `negative_ledger_required` is `yes` for every non-trivial fixed-point run, but the result may be `no-applicable-evidence`.
- `reduction_pass_required` is `yes` for every non-trivial fixed-point run, but the result may be `no-material-reduction-candidate`.
- If `$negative-ledger` tooling is unavailable, keep an in-session Negative Evidence Ledger and record `negative_ledger: unavailable`.

## Canonical ledgers

Maintain and refresh these ledgers after every meaningful pass:

- Findings Ledger
- Soundness Ledger
- Invariant Ledger
- Foot-Gun Register
- Complexity Ledger
- Verification Ledger
- Reduction Ledger
- Surface Delta Dashboard
- Negative Ledger Pass
- Negative Evidence Ledger
- One-Change Challenge Ledger
- Companion Skill Ledger
- Specialist Briefing Ledger
- Specialist Value Receipts
- Residual Uncertainty
- Review Comment Ledger (optional, when review-adjudication is in the workflow)

Every meaningful pass must stamp the current `artifact_state_label`.

Every negative-ledger query, map, capture, reopen, or handoff must stamp the current `artifact_state_id`.

Every Reduction Pass must stamp the current `artifact_state_id`.

## Negative Ledger Pass

Use this root-owned shape at preflight, after material failed/remediated loops, and before closure:

```yaml
negative_ledger_pass:
  phase: preflight | post-remediation | post-review | pre-closure | capture | handoff
  mode: query | map | capture | reopen | handoff | none
  artifact_state_id: "..."
  topical_query: "4-8 task-defining terms"
  sources_checked:
    current_run: yes | no
    fixed_point_ledgers: yes | no
    learnings: yes | no
    repo_history: yes | no
    review_comments: yes | no
    user_context: yes | no
  result:
    active_exclusions: []
    stale_or_superseded: []
    reopened_candidates: []
    need_evidence: []
    no_applicable_negative_evidence_reason: "..."
    safest_next_frontier: "..."
  durable_capture: appended | duplicate-skip | not-material | unavailable | not-attempted
```

Preflight query terms should include the component, failure surface, benchmark/test when known, review-comment theme, hypothesis family, invariant/hazard class, and any known additive-churn or duplicate-owner pattern.

When a compatible `learnings` CLI is available, run read-only recall before meaningful `query` or `map`:

```bash
run_learnings_tool recall --query "<component failure-surface test-or-benchmark hypothesis-family>" --limit 8 --drop-superseded
```

Treat recall/query hits as candidate evidence. A hit becomes active negative evidence only after its evidence anchors and current-state applicability are checked.

## Negative capture decision

After any failed check, no-effect attempt, benchmark regression, revert, review rejection, additive churn, duplicate-owner repair, proof-surface sprawl, or strategy pivot, decide whether to capture:

```yaml
negative_capture_decision:
  witnessed_event: failed-test | no-effect | benchmark-regression | revert | review-rejection | strategy-pivot | additive-churn | duplicate-owner | proof-surface-sprawl | none
  hypothesis: "..."
  attempted_change: "..."
  evidence_anchor: "command | log | benchmark | failing test | revert | review rationale | trace | diff | learning id"
  decision_shaping: yes | no
  transferable: yes | no
  counterfactual_value: yes | no
  capture: yes | no
  durable_writeback: append | duplicate-skip | not-material | unavailable | not-attempted
  reason: "..."
```

Capture only decision-shaping negative evidence. Do not record unevidenced hunches or one-off inconvenience as a reusable exclusion.

For additive-churn or proof-surface-sprawl captures, use a narrow exclusion rule, for example:

```text
Do not add another local checker for <invariant>; tighten <canonical owner> unless current artifacts prove the owner cannot enforce it.
```

## Companion Skill Ledger

Every Standard run must include a companion ledger:

| Companion | Status | Evidence |
|---|---|---|
| `review-adjudication` | `used` / `not-needed` / `root-equivalent` / `unavailable` | one phrase |
| `accretive-implementer` | `used` / `root-equivalent` / `not-needed` / `unavailable` | one phrase |
| `adversarial-reviewer` | `used` / `root-equivalent` / `not-needed` / `unavailable` | one phrase |
| `verification-closure` | `used` / `root-equivalent` / `not-needed` / `unavailable` | one phrase |
| `negative-ledger` | `queried` / `mapped` / `captured` / `handoff` / `no-applicable-evidence` / `unavailable` | one phrase |
| `learnings` | `recalled` / `captured` / `not-material` / `unavailable` | one phrase |
| `simplify-and-refactor-code-isomorphically` | `used` / `root-equivalent` / `not-needed` / `unavailable` | one phrase |

Status rules:

- Do not mark a companion `used` unless there is an invocation, output packet, or contract-shaped section.
- Do not mark `not-needed` without a task-shape reason.
- Do not use `root-equivalent` for `negative-ledger`; use the negative-ledger statuses above.
- `simplify-and-refactor-code-isomorphically` may be `not-needed` when the Reduction Pass is non-isomorphic, semantic-remediation-oriented, or has no behavior-preserving sub-pass.
- If a user explicitly asks for a named companion, `root-equivalent` is not enough unless the named skill is unavailable and the unavailability is recorded.

## Lane and subagent budget

Subagent mode is `off`, `targeted`, or `swarm`.

The root-owned Negative Ledger Pass and root-owned Reduction Pass do not count against specialist budget. `negative-ledger-mapper` does count.

Declare the current `fixed_point_lane` before launching specialists:

| Lane | Trigger | Specialist budget | Default subagent mode |
|---|---|---:|---|
| `direct-closure` | One narrow comment/change, obvious proof lane, no material route uncertainty, no open reduction uncertainty | 0 | `off` |
| `targeted` | A read-heavy uncertainty could materially change the route | 1-2 | `targeted` |
| `expanded-targeted` | Coupled invariants, multi-surface proof, reduction uncertainty, or two independent uncertainty classes | 3-4 | `targeted` |
| `swarm` | Broad/high-risk/exhaustive request, audit carryover, explicit independent coverage, or structural surface-reduction uncertainty | 5+ | `swarm` |

Rules:

- Default lane is `direct-closure` for narrow review-comment remediation.
- Escalate from `direct-closure` only when uncertainty is route-changing.
- Escalate from `targeted` to `expanded-targeted` only when the third specialist covers a distinct uncertainty class.
- Use `swarm` only when the task itself asks for exhaustive independent coverage or artifact risk justifies it.
- If actual specialist count exceeds the declared budget, record `budget_exception` with the material reason.
- Do not launch multiple specialists for the same uncertainty class unless the first packet was stale, transport-invalid, wrong-scope, or materially incomplete.
- Prefer root-owned negative-ledger query/map before launching `negative-ledger-mapper`.
- Prefer root-owned Reduction Pass before launching a complexity or reduction specialist.

## Budget exception gate

Before launching a specialist that would exceed the current lane budget, record:

```yaml
budget_exception:
  requested_extra_role: "..."
  current_lane: direct-closure | targeted | expanded-targeted | swarm
  current_specialist_count: 0
  budget_limit: 0
  distinct_uncertainty_class: yes | no
  why_root_cannot_resolve_locally: "..."
  expected_decision_delta: route | finding | proof | risk-retirement | negative-evidence-frontier | reduction-frontier | none
  approved: yes | no
```

Rules:

- If `expected_decision_delta: none`, do not launch the extra specialist.
- If `distinct_uncertainty_class: no`, do not launch the extra specialist unless replacing a stale or invalid packet.
- If `current_lane: direct-closure`, any specialist launch must first reclassify the lane.

## Negative-ledger-mapper escalation

Run `negative-ledger-mapper` from `$negative-ledger` when root-owned query/map finds material history pressure that would benefit from read-heavy mapping, including:

- multiple candidate failed routes
- stale or conflicting learnings
- benchmark regressions or optimization dead ends
- recurring review rejections
- repeated dead-end hypotheses
- repeated additive churn or duplicate-owner fixes
- search-heavy debugging, optimization, migration, or flaky-test terrain

The mapper may use read-only `learnings recall`, `learnings query`, or `learnings recent` as a source when available. Treat it as a read-only pruning specialist, not as a veto authority. The root still decides applicability, active exclusions, reopening criteria, and final closure.

## Swarm specialists

Use `swarm` only when justified by the lane rules. When custom agents are available, prefer:

- `evidence_mapper`
- `negative-ledger-mapper`
- `soundness_auditor`
- `invariant_auditor`
- `hazard_hunter`
- `complexity_auditor`
- `verification_auditor`

Do not use specialist work to run final proof gates. Specialists may map evidence, pressure-test soundness, classify negative evidence, identify duplicate owners or reduction candidates, and recommend focused/full proof lanes. Root owns authoritative fmt/lint/build/test commands and final verdict.

## Shared specialist packet contract

All specialist prompts, packets, rejections, waits, and closure handoffs must follow the shared contract at `../references/specialist-packet-contract.md`.

The root must assign an `artifact_state_id`, `artifact_state_label`, and exact `scope` before launch. An accepted packet must be packet-native, scoped to the assignment, evidence-bearing, current for the assigned artifact state, and free of transport wrappers, queued prompts, instruction acknowledgements, and root-only `Echo:` text.

Reject acknowledgement-only packets as `low-value`. Reject late packets as `stale` or `superseded` when the artifact state changed before they arrived. Close stale workers and continue with local proof when the assigned uncertainty has been resolved locally or is no longer route-changing.

## Specialist value receipt

For every specialist packet, accepted or rejected, record a value receipt:

```yaml
specialist_value_receipt:
  role: verification_auditor | hazard_hunter | evidence_mapper | soundness_auditor | invariant_auditor | complexity_auditor | negative-ledger-mapper | reduction_mapper | other
  packet_status: accepted | stale | transport-invalid | wrong-scope | timeout | superseded | low-value
  artifact_state_id_match: yes | no | unknown
  scope_match: yes | no | unknown
  uncertainty_class: evidence | soundness | invariant | hazard | complexity | verification | negative-evidence | reduction | other
  route_changed: yes | no
  finding_added: yes | no
  proof_changed: yes | no
  risk_retired: yes | no
  reduction_changed: yes | no
  value: positive | neutral | negative
  used_for: evidence-mapping | negative-evidence-pruning | soundness-pressure | invariant-pressure | hazard-pressure | complexity-pressure | verification-planning | reduction-planning | none
  reason: "one sentence"
```

Acceptance rules:

- `accepted` requires `artifact_state_id_match: yes` and `scope_match: yes`.
- `accepted` requires at least one scoped material signal with an artifact reference.
- `value: positive` requires at least one of `route_changed`, `finding_added`, `proof_changed`, `risk_retired`, or `reduction_changed` to be `yes`.
- `risk_retired: yes` requires a plausible material hazard, reduction uncertainty, or negative-evidence route to have been ruled out.
- Rejected packets still appear in the Specialist Briefing Ledger and Specialist Value Receipts.

## Artifact state identity

Every meaningful pass must carry an `artifact_state_id` in addition to `artifact_state_label`.

`artifact_state_id` must include enough current-state evidence to make stale packets obvious:

- branch name when available
- `HEAD` or comparable revision
- diff hash or changed-file digest
- touched path set
- phase label, such as `prepatch`, `postpatch`, `post-fixture-refresh`, `post-reduction`, or `closure-candidate`

Any material edit, fixture regeneration, dependency update, proof-surface change, reduction pass, or negative-ledger reopening event invalidates older specialist packets. Close or supersede pre-edit specialists before using post-edit evidence. If specialist input is still needed, spawn fresh specialists with the new `artifact_state_id`.

## Specialist packet validation

Require exactly one packet-native specialist output from every specialist, using the shared packet contract fields:

- `artifact_state_id`
- `artifact_state_label`
- `scope`
- `top_material_signals` with artifact references
- `unresolved_signals`
- `agreement_pressure`
- `stale`
- `final_call`

Validate every specialist packet before reading it as evidence:

- exactly one specialist packet is present
- no raw `<subagent_notification>`, `<hook_prompt`, `Echo:`, instruction acknowledgement, or queued prompt content is relayed as evidence
- all required fields are present
- `artifact_state_id` matches the current root state exactly
- `scope` matches the assigned scope
- at least one scoped answer has an artifact reference

If validation fails, mark the packet `transport-invalid`, `wrong-scope`, `stale`, `superseded`, `timeout`, or `low-value`, record the rejection reason in the Specialist Briefing Ledger, add a Specialist Value Receipt, and continue locally or relaunch one narrow specialist only when the missing uncertainty remains route-changing. Do not repeatedly respawn broad swarms for the same artifact state.

## One-change challenge as local falsifier

Run this challenge after a candidate material fixed point and before every final closure attempt. Also use it before escalating from `direct-closure` or `targeted` to a broader specialist lane.

```yaml
one_change_challenge:
  candidate_extra_change: "..."
  candidate_subtractive_change: "..."
  subtractive_solution_class: delete | privatize | merge | tighten-existing-boundary | reuse-existing-helper | none
  materiality: material | non-material | unknown
  proof_needed: "..."
  reduction_pass_checked: yes | no
  reduction_candidate_score: "..."
  negative_ledger_checked: queried | mapped | handoff | no-applicable-evidence | unavailable
  matched_negative_ids: []
  reopening_criteria_satisfied: yes | no | n/a
  decision: apply | reject | defer | escalate-to-specialist | no-impactful-change
  reason: "..."
```

Rules:

- Before proposing an additive candidate, attempt one subtractive candidate: delete, privatize, merge, tighten an existing boundary, or reuse an existing proof/check lane.
- If the selected move is additive, record why no subtractive candidate is material and safe.
- If the challenge produces no material candidate and proof lanes are obvious, do not fan out.
- If the challenge identifies one bounded uncertainty, prefer one specialist over a swarm.
- If the challenge identifies multiple independent uncertainty classes, reclassify to `expanded-targeted`.
- If the selected move matches active negative evidence, choose a different move or prove reopening criteria are satisfied.
- After any implemented one-change improvement, rerun full de novo review before closure.

## Negative evidence closure gate

Closure cannot be `ready` while this gate is open:

```yaml
negative_evidence_closure_gate:
  status: satisfied | open | blocked | unavailable
  active_exclusions_count: 0
  repeated_failed_route_used: yes | no
  reopening_criteria_satisfied: yes | no | n/a
  learnings_hits_applicability_checked: yes | no | n/a
  reason: "..."
```

Gate rules:

- `satisfied`: no active applicable negative evidence blocks the current route, or reopening criteria are satisfied with proof.
- `open`: active applicable negative evidence conflicts with the current route and has not been reopened.
- `blocked`: evidence exists but cannot be checked due to missing logs, inaccessible learnings, or unavailable repo history.
- `unavailable`: `$negative-ledger`/learnings tooling is unavailable, and an in-session ledger could not check the relevant source. Explain the limit.
- Passing checks do not close this gate if a known disconfirmed route was repeated without a new witness.

## Reduction closure gate

Closure cannot be `ready` while this gate is open:

```yaml
reduction_closure_gate:
  status: satisfied | open | blocked
  reduction_passes_completed:
    pre_implementation: yes | no | not-needed
    post_review: yes | no | not-needed
    pre_closure: yes | no
  additive_fix_survived: yes | no
  duplicate_owner_remaining: yes | no | unknown
  surface_delta_dashboard_emitted: yes | no
  preservation_cards_complete: yes | no | not-needed
  reason: "..."
```

Gate rules:

- `satisfied`: required Reduction Passes are complete, no additive fix duplicated ownership, and the Surface Delta Dashboard is emitted before closure.
- `open`: a reduction candidate remains material, additive code lacks a why-not-smaller explanation, or duplicate owners remain.
- `blocked`: evidence needed to prove safe reduction or safe retention is missing and materially affects closure.

## Orchestration algorithm

1. Establish entry state, `artifact_state_id`, and `artifact_state_label`.
2. If unresolved PR comments exist and relevance is unclear, start with `review-adjudication`.
3. Run Routing Preflight, including the first root-owned Negative Ledger Pass and first root-owned Reduction Pass.
4. Choose initial phase path and fixed-point lane.
5. Choose subagent mode (`off`, `targeted`, or `swarm`) and run only justified read-only specialist scopes. Prefer root-owned negative-ledger query/map first; run `negative-ledger-mapper` only when material history pressure is read-heavy. Prefer root-owned Reduction Pass before launching reduction or complexity specialists.
6. Run the saturation loop:
   - run or refresh the Reduction Pass before implementation/remediation
   - implement or remediate with `accretive-implementer` or root-equivalent doctrine, using the selected solution class
   - review with `adversarial-reviewer` or root-equivalent doctrine
   - normalize findings, soundness, invariants, hazards, complexity, verification, reduction, negative evidence, and comment adjudication into ledgers
   - after failed/no-effect/regression/revert/rejection/pivot/additive-churn events, run Negative Capture Decision
   - capture decision-shaping negative evidence through `$negative-ledger`, with durable writeback through `$learnings` when transferable
   - after two review/remediation cycles or broad additive repair, run a post-review Reduction Pass
   - rerun full-scope review after any material validation, remediation, or reduction
7. Reach a **candidate material fixed point** only when no unresolved material finding, material soundness gap, unbounded critical invariant, material foot-gun, material complexity hazard, open reduction closure gate, or open negative-evidence closure gate remains.
8. Run the pre-closure Negative Ledger Handoff.
9. Run the pre-closure Reduction Pass and emit the Surface Delta Dashboard.
10. Run the pre-closure one-change challenge, using the Negative Evidence Ledger and Reduction Pass before selecting a change.
11. Compile the closure handoff packet, including accepted/rejected/stale specialist packets, value receipts, negative-ledger handoff, reduction handoff, and Surface Delta Dashboard.
12. Run `verification-closure` or root-equivalent closure gates.
13. If closure reopens the loop, route the highest-value next move and continue.
14. Stop only in a justified terminal state.

## Output contract

### Standard

Use concise sections in this order:

- Workflow
- Entry State
- Routing Preflight
- Upstream Intake (only when review-adjudication materially shaped the route)
- Companion Skill Ledger
- Negative Ledger Pass
- Reduction Pass
- Subagent Mode and Budget
- Specialist Value Receipts (only when specialists ran)
- Routing Summary
- One-Change Challenge
- Surface Delta Dashboard
- Closure Handoff Packet
- Residual Risks
- Final State
- Do Next

### Fast

Use concise sections in this order:

- Entry State
- Negative Ledger Pass
- Reduction Pass
- Routing Summary
- Final State
- Do Next

## Do Next

The final section must say:

- `owner`: skill | user | none
- `action`: exact next phase, stop action, or `none`
- `why`: one sentence
- `state`: ready | conditionally ready | needs remediation | needs-decision | blocked

## Hard rules

- Never impose an arbitrary maximum number of loops.
- Never start a non-trivial fixed-point run without a root-owned Negative Ledger Pass.
- Never start a non-trivial fixed-point run without a root-owned Reduction Pass.
- Never select `add-new-code` before completing a Reduction Pass.
- Never treat `no-applicable-negative-evidence` as proof that a route is novel.
- Never let negative evidence suppress a route unless it has witness-bearing applicability to the current artifact state.
- Never let active applicable negative evidence disappear before closure; mark it remediated, stale, superseded, reopened, accepted-risk, or still open.
- Never let a `learnings` hit become an exclusion rule without checking its evidence and current-state applicability.
- Never append negative evidence to durable learnings unless it is decision-shaping, transferable, and counterfactually useful.
- Never launch specialists before declaring `fixed_point_lane` and specialist budget.
- Never exceed the lane budget without a recorded `budget_exception`.
- Never count a specialist as value-positive without a Specialist Value Receipt.
- Never omit rejected, stale, superseded, timeout, wrong-scope, transport-invalid, or low-value specialist packets from the Specialist Briefing Ledger.
- Never let stale specialist briefings masquerade as current evidence.
- Never let specialist packets without a matching `artifact_state_id` enter the closure verdict.
- Never let specialists own final proof commands or the final pass/fail verdict.
- Never mark a companion skill `used` unless its explicit output packet, invocation, or contract-shaped section is present.
- Never mark a companion skill `not-needed` without a task-shape reason.
- Never let review-adjudication quietly disappear once it materially shaped the route.
- Never declare a candidate fixed point while a material soundness gap remains unresolved.
- Never declare a candidate fixed point while the negative evidence closure gate is open.
- Never declare a candidate fixed point while the reduction closure gate is open.
- Never declare a candidate fixed point while an additive fix duplicated an invariant owner.
- Never close after review-remediation churn without a pre-closure Surface Delta Dashboard.
- Never let a proof lane, generated artifact, fixture family, public export, or compatibility alias survive merely because it made review closure easier.
- Never treat LOC reduction as sufficient when ownership, proof, or invariant clarity regressed.
- Never treat passing proof as sufficient when stale surfaces still claim the old invariant.
- Never skip the pre-closure Negative Ledger Handoff.
- Never skip the pre-closure Reduction Pass.
- Never skip the pre-closure one-change challenge before a final closure attempt.

## Resources

- [negative-ledger skill](../negative-ledger/SKILL.md)
- [negative-ledger-mapper](../negative-ledger/agents/negative-ledger-mapper.md)
- [negative-ledger contract](../negative-ledger/references/negative-ledger-contract.md)
- [simplify-and-refactor-code-isomorphically](../simplify-and-refactor-code-isomorphically/SKILL.md)
- [negative-ledger pass](references/negative-ledger-pass.md)
- [lane-and-specialist-budget.md](references/lane-and-specialist-budget.md)
- [companion-skill-ledger.md](references/companion-skill-ledger.md)
- [specialist-value-receipt.md](references/specialist-value-receipt.md)
- [closure-handoff-contract.md](references/closure-handoff-contract.md)
- [closure-handoff-template.md](references/closure-handoff-template.md)
- [one-change-challenge.md](references/one-change-challenge.md)
- [example-invocations.md](references/example-invocations.md)
- [common-soundness.md](references/common-soundness.md)
- [common-ledgers.md](references/common-ledgers.md)
- [common-cli-reporting.md](references/common-cli-reporting.md)
- [common-routing-vocabulary.md](references/common-routing-vocabulary.md)
- [specialist-packet-contract.md](../references/specialist-packet-contract.md)
