---
name: fixed-point-driver
description: "Drive exhaustive build-review-improve-verify loops to Truth-Owner Normal Form: one canonical owner per material invariant, no duplicate truth surfaces, no unresolved review counterexamples, no unretired additive scaffolding, and proof-gated closure. Trigger when coding needs de novo re-litigation, PR review closure, repeated review/fix loops, invariant repair, proof-surface hardening, negative-evidence pruning, CAS/Codex review resolution, or when agents risk adding local patches instead of deleting/refactoring/canonicalizing. Do not use for trivial one-step tasks or when the user wants one narrow phase."
---

# Fixed-Point Driver

This skill coordinates implementation, review, adjudication, reduction, verification, and closure until the artifact set reaches **Truth-Owner Normal Form**.

## The single rule

Drive toward this state:

> Every material invariant has exactly one canonical owner, every witness points back to that owner, every review finding is either discharged or represented as a counterexample, every additive scaffold has been promoted/collapsed/deleted, and no duplicate truth surface remains merely because it helped satisfy an intermediate review loop.

A fixed point is not "review is clean". A fixed point is a normal form of the code and proof system.

## Why this skill exists

Frontier coding agents are good at adding code and addressing review comments. They are weaker at noticing that the best fix is to delete a path, collapse duplicate owners, privatize a surface, or tighten the one boundary that should have owned the invariant from the start.

This skill converts review churn into an ownership-normalization problem. The workflow is not "find comment -> patch comment -> rerun review." It is:

```text
finding -> counterexample -> truth owner graph -> rewrite candidates -> normal-form proof -> closure
```

## Companion skills

- `review-adjudication` decides which review comments matter, but this skill decides whether the selected work preserves Truth-Owner Normal Form.
- `accretive-implementer` performs implementation/remediation when the selected rewrite is narrow and owned.
- `adversarial-reviewer` challenges the current artifact state and should report normal-form violations, not just bugs.
- `verification-closure` performs decisive proof and closure gating.
- `negative-ledger` preserves disconfirmed routes, repeated additive churn, review rejections, and reopened/deleted surface decisions.
- `learnings` stores durable evidence-backed lessons.
- `simplify-and-refactor-code-isomorphically` may be invoked for behavior-preserving collapse, but Truth-Owner Normal Form is owned here and is not optional.

## Core vocabulary

### Truth unit

A material invariant, contract, semantic fact, proof obligation, compatibility rule, public-surface guarantee, generated-artifact fact, policy rule, or safety condition that the codebase must preserve.

Examples:

- certificate refs must bind to the artifact actually checked;
- unsupported residual shapes must fail closed under strict policy;
- a public root must not expose internal proof machinery;
- a generated artifact's fingerprint must be recomputed from current contents before it is trusted;
- a review-clean branch must be clean against the pinned base and current HEAD, not an older tree.

### Canonical owner

The one boundary that should enforce or generate a truth unit. Examples:

- checker
- builder
- constructor
- validator
- generator
- certificate check
- parser/lowerer
- type/refinement boundary
- package root/public export list
- test/proof harness that is the executable truth surface

### Shadow owner

Any second place that claims, mirrors, partially checks, documents, generates, or assumes the same truth without being the canonical owner.

Shadow owners include duplicate validators, compatibility aliases, matrix docs that mirror executable checks, fixture families that encode the same invariant repeatedly, hand-maintained generated artifacts, local prechecks that compensate for a weak canonical checker, and public exports retained only because tests still mention them.

### Counterexample

A review finding, failed test, stale proof, negative learning, or manual inspection that shows the current truth-owner graph admits a false state, duplicates ownership, or cannot prove the delivered artifact.

A review comment is not an implementation task until it is represented as a counterexample to a truth unit.

### Rewrite

A change to the truth-owner graph. Preferred rewrite order:

1. **Delete** a stale/shadow surface.
2. **Privatize** or narrow a visible surface.
3. **Merge** duplicate owners or proof paths.
4. **Tighten** the canonical owner.
5. **Reuse** an existing owner/witness path.
6. **Add** new code only into addition escrow.

### Addition escrow

Any new helper, checker, proof lane, fixture family, compatibility alias, public symbol, generated artifact, or model added during a fixed-point loop starts in escrow. It cannot survive closure unless it is promoted to canonical owner, collapses/removes another surface, or has explicit owner-proof and no cheaper rewrite can satisfy the truth unit.

## Material fixed point

A run reaches material fixed point only when all are true:

- no unresolved material finding remains;
- every accepted review finding is mapped to a truth unit and resolved counterexample;
- every material truth unit has one canonical owner;
- shadow owners are deleted, privatized, merged, or explicitly justified;
- addition escrow is empty or every surviving addition has owner-proof;
- no active negative evidence blocks the route;
- no stale specialist packet, stale review result, stale proof, stale fixture, or stale artifact is used for closure;
- the proof suite directly witnesses the changed truth units;
- the pre-closure one-change challenge cannot identify a higher-value normal-form rewrite.

## Output modes

- **Standard**: full workflow state, Truth-Owner Graph, ledgers, proof, closure.
- **Fast**: current artifact state, highest-value rewrite, escrow status, open gates, exact next action.

## CLI-tail-weighted reporting

- Keep early ledgers terse.
- End with **Final State** and **Do Next**.
- **Do Next** must be the last section.
- If the report is long, compress prose before compressing the Truth-Owner Graph, addition escrow, negative ledger, closure state, or exact next action.

## Global doctrine

Every phase inherits **UNSOUND**, **WITNESS-BEARING**, **PRESERVATION-AWARE**, **PROGRESS-AWARE**, **REFINEMENT-AWARE**, **MECHANISTIC**, **ACCRETIVE**, and **TRACEABLE** standards.

Additional orchestration pressure: **TRUTH-OWNER-NORMALIZING**, **EXHAUSTIVE**, **DE NOVO**, **ADVERSARIAL**, **SATURATING**, **MATERIAL**, **PARSIMONIOUS**, **SUBTRACTIVE-FIRST**, **CANONICAL**, **INVARIANT-GRADED**, **HAZARD-SEEKING**, **LEDGERIZED**, **HISTORY-AWARE**, **NEGATIVE-EVIDENCE-AWARE**, **ESCROW-AWARE**, **STALE-PROOF**, and **REOPENABLE**.

`ACCRETIVE` means evidence-preserving and reviewable. It does not mean additive.

## Truth-Owner Graph

Every non-trivial Standard run must maintain a compact Truth-Owner Graph. It is the central artifact of this skill.

```yaml
truth_owner_graph:
  artifact_state_id: "branch/head/base/diff-digest/phase"
  objective: "..."
  truth_units:
    - id: TU-001
      invariant: "..."
      current_owner: "file/symbol/boundary or unknown"
      desired_owner: "file/symbol/boundary"
      owner_status: canonical | duplicate | missing | weak | stale | unknown
      counterexamples:
        - source: review | test | proof-gap | negative-ledger | manual | specialist
          ref: "..."
          claim: "..."
      shadow_owners:
        - "..."
      witness_surfaces:
        - "test/check/example/generator/doc"
      stale_surfaces:
        - "..."
      selected_rewrite: delete | privatize | merge | tighten-owner | reuse-owner | add-escrow | validate-only | no-change | blocked
      proof_after_rewrite: "..."
      residual_risk: "..."
```

Rules:

- Do not implement a finding until it is attached to a truth unit.
- If two comments touch the same truth unit, resolve the owner graph, not the comments independently.
- If an invariant has no owner, choose an existing boundary before creating a new one.
- If an invariant has multiple owners, prefer deletion/merge/privatization before strengthening all of them.
- If the graph cannot be built from available evidence, route to validation or block; do not invent ownership.

## Code-change doctrine

When writing code or making a change, do it in the most optimal way possible for the current material objective.

Rules:

- Prefer the smallest complete design that preserves invariants, removes or narrows foot-guns, and leaves a clear proof path.
- Choose durable, idiomatic, maintainable code over clever shortcuts, speculative abstraction, broad rewrites, or local patch accretion.
- Optimize for correctness and evidence first, then ownership clarity, simplicity, performance, ergonomics, and future change cost when materially relevant.
- Do not use "optimal" to justify unbounded scope, aesthetic churn, bypassing negative evidence, exceeding lane budgets, weakening review, or skipping closure gates.
- When materially valid implementations compete, select the rewrite that moves the truth-owner graph closest to normal form.

## Rewrite selection

For every material truth unit or accepted review finding, run a **Patch Tournament** before editing.

```yaml
patch_tournament:
  truth_unit: TU-001
  counterexample_refs: []
  candidates:
    - id: A
      rewrite: delete | privatize | merge | tighten-owner | reuse-owner | add-escrow | validate-only | no-change
      sketch: "..."
      canonical_owner_after: "..."
      owners_removed_or_demoted: []
      proof_needed: "..."
      preservation_risk: low | medium | high | unknown
      expected_surface_delta: "..."
      decision: select | reject | defer
      reason: "..."
  selected: A
```

Selection order is binding:

1. Delete stale or duplicate code/proof/docs.
2. Privatize or narrow a public/exported/package-visible surface.
3. Merge duplicate owners, registries, aliases, fixtures, generated artifacts, reports, or proof lanes.
4. Tighten the existing canonical checker, builder, validator, generator, certificate, API, or boundary.
5. Reuse an existing helper, proof lane, test lane, or contract surface.
6. Add new code only into addition escrow.

`add-escrow` is legal only after the first five rewrite classes were considered and rejected with evidence.

## Addition Escrow Ledger

All newly added code/proof/docs in a fixed-point run enter escrow unless they directly replace deleted/merged/privatized surface in the same rewrite.

```yaml
addition_escrow:
  - id: AE-001
    added_surface: "file/symbol/test/doc/build-step"
    reason_added: "..."
    truth_unit: TU-001
    intended_lifetime: permanent-owner | temporary-scaffold | proof-fixture | compatibility-bridge | unknown
    rent_payment: deleted-shadow | privatized-surface | merged-owner | tightened-owner | generated-from-owner | none
    cheaper_rewrite_defeated: yes | no
    promotion_criteria: "..."
    collapse_or_delete_criteria: "..."
    status: open | promoted | collapsed | deleted | accepted-risk | blocked
```

Rules:

- No closure while addition escrow contains `open` items.
- A permanent addition must either become the canonical owner or prove why the existing owner cannot own the truth unit.
- A test addition must witness the old false state or a current truth unit; review-comfort tests remain suspect.
- A helper addition must retire duplication, not merely name it.
- A compatibility alias must have explicit deletion or reopening criteria.
- After two review/remediation cycles with growing escrow, stop feature work and run a normal-form collapse pass.

## Normal-form reduction loop

This loop adapts the best of `simplify-and-refactor-code-isomorphically` to semantic fixed-point work.

```text
1. BASELINE    -> current artifact state, proof state, changed path set, diff/stat snapshot
2. GRAPH       -> truth units, canonical owners, shadow owners, stale surfaces, addition escrow
3. TOURNAMENT  -> patch candidates ordered by delete/privatize/merge/tighten/reuse/add
4. CARD        -> preservation/invariant card for selected rewrite
5. REWRITE     -> implement one truth-unit rewrite or one tightly coupled invariant cluster
6. VERIFY      -> targeted and required full proof; stale-surface checks
7. LEDGER      -> graph delta, escrow delta, rejected rewrites, proof result
8. REREAD      -> adversarial review asks whether the graph got smaller or just locally quieter
```

Do not measure success only by LOC. Measure truth entropy:

- owner count per truth unit;
- shadow owner count;
- public/exported surface count;
- proof-lane mirror count;
- generated artifact families;
- compatibility aliases;
- open addition escrow;
- stale proof/comment/fixture references;
- total review counterexamples remaining.

## Surface Reduction Matrix

Use this matrix inside the Patch Tournament when multiple reduction candidates exist.

```text
Score = (Reduction Payoff x Confidence) / Risk
```

Reduction Payoff:

- 5 = removes a public/exported surface, duplicate proof lane, stale compatibility path, generated artifact family, or obsolete subsystem
- 4 = collapses duplicate checker/generator/certificate/model ownership
- 3 = removes helper/wrapper/fixture duplication or narrows a public seam
- 2 = deletes local dead code, redundant test setup, stale docs, or pass-through wrappers
- 1 = small cleanup with little future-review impact

Confidence:

- 5 = current tests/proofs/manual inspection show the removed surface has no independent obligation
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

Rules:

- Apply candidates with score >= 2.0 when they preserve or strengthen the invariant.
- Reject lower-scoring candidates unless they remove an active material foot-gun.
- If an additive rewrite is selected while a higher-scoring reduction exists, explain the preservation axis or ownership fact that blocks reduction.

## Preservation / Invariant Card

Before any delete, merge, privatize, refactor, or owner-tightening rewrite, fill this card.

```yaml
preservation_invariant_card:
  truth_unit: TU-001
  selected_rewrite: delete | privatize | merge | tighten-owner | reuse-owner | add-escrow
  intended_semantic_delta:
    behavior_changed: yes | no
    illegal_state_now_rejected: "..."
    behavior_preserving_envelope: "..."
  owner_after:
    canonical_owner: "..."
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
    old_false_state_witness: "..."
    targeted_check: "..."
    full_check: "..."
    stale_surface_check: "..."
    residual_uncertainty: "..."
```

If a row cannot be filled and the gap is material, choose validation-only or blocked. Do not edit from vibes.

## Review-adjudication intake

If the user provides review comments or a prior adjudication result, start with `review-adjudication` unless the comments are already in a complete, current, route-ready packet.

Rules:

- Treat adjudicated `Act On` rows as routed work, not as unquestionable truth.
- Preserve `Rebut`, `Defer / Out of Scope`, and `Need Evidence` rows as constraints.
- If upstream adjudication lacks `truth_unit`, `canonical_owner`, or `solution_class`, reconstruct them before implementation.
- A review comment whose local fix would add a shadow owner must be reframed as an owner-graph problem.
- Do not implement a review finding solely because it is current, P2+, invariant-shaped, or easy to patch.

## Negative-ledger posture

For every non-trivial fixed-point run, perform a root-owned Negative Ledger Pass at routing preflight and refresh it before closure.

Default behavior:

- Query/map current-run witnesses, fixed-point ledgers, review comments, `learnings`, and repo history when available.
- Normalize failed attempts into the Negative Evidence Ledger.
- Mark entries as `active`, `stale`, `superseded`, `reopened`, `unknown`, or `need-evidence`.
- Convert only active, witness-bearing, current-state-applicable entries into narrow exclusion rules.
- Capture additive churn, duplicate-owner fixes, proof-surface sprawl, no-effect refactors, review rejections, reverts, failed reviews, and strategy pivots when decision-shaping.
- Run pre-closure handoff even when there are no active exclusions.

Negative evidence is advisory, not a veto authority, unless its witness and current applicability bind the current artifact state.

### Negative evidence shape

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

## Routing preflight

Every Standard run must establish this compact preflight before implementation, fanout, or closure.

```yaml
routing_preflight:
  task_shape: narrow-review-comment | review-batch | implementation | remediation | hardening | audit | optimization | migration | unknown
  artifact_state_id: "..."
  truth_owner_graph_required: yes
  truth_owner_graph_status: initialized | partial | blocked
  fixed_point_lane: direct-closure | targeted | expanded-targeted | swarm
  subagent_mode: off | targeted | swarm
  specialist_budget:
    planned: 0 | 1 | 2 | 3 | 4 | "5+"
    reason: "..."
  negative_ledger_required: yes
  negative_ledger_initial_mode: query | map | reopen | handoff
  addition_escrow_status: empty | open | unknown
  companion_stack:
    review_adjudication: used | not-needed | root-equivalent | unavailable
    accretive_implementer: used | root-equivalent | not-needed | unavailable
    adversarial_reviewer: used | root-equivalent | not-needed | unavailable
    verification_closure: used | root-equivalent | not-needed | unavailable
    negative_ledger: queried | mapped | captured | handoff | no-applicable-evidence | unavailable
    learnings: recalled | captured | not-material | unavailable
    simplify_refactor: used | root-equivalent | not-needed | unavailable
  stop_go_gate:
    proceed: yes | no
    blocking_reason: "none | ..."
```

Rules:

- `root-equivalent` means the root performed the stage's doctrine without a distinct auditable invocation.
- `negative_ledger_required` is `yes` for every non-trivial fixed-point run.
- `truth_owner_graph_required` is `yes` for every non-trivial fixed-point run.
- `simplify_refactor: not-needed` is legal only when no behavior-preserving collapse candidate is material.

## Canonical ledgers

Maintain and refresh these ledgers after every meaningful pass:

- Truth-Owner Graph
- Patch Tournament Ledger
- Addition Escrow Ledger
- Surface Delta Dashboard
- Findings Ledger
- Soundness Ledger
- Invariant Ledger
- Foot-Gun Register
- Complexity Ledger
- Verification Ledger
- Negative Ledger Pass
- Negative Evidence Ledger
- One-Change Challenge Ledger
- Companion Skill Ledger
- Specialist Briefing Ledger
- Specialist Value Receipts
- Residual Uncertainty
- Review Comment Ledger when review-adjudication is in the workflow

Every meaningful pass must stamp the current `artifact_state_id`.

## Artifact state identity

Every meaningful pass must carry an `artifact_state_id` that includes enough current-state evidence to make stale packets obvious:

- branch name when available;
- HEAD or comparable revision;
- base ref/SHA when review-bound;
- diff hash or changed-file digest;
- touched path set;
- phase label such as `prepatch`, `postpatch`, `post-fixture-refresh`, or `closure-candidate`.

Any material edit, fixture regeneration, dependency update, proof-surface change, generated-artifact change, or owner-graph rewrite invalidates older specialist packets and stale proofs.

## Lane and subagent budget

Subagent mode is `off`, `targeted`, or `swarm`.

Declare the current `fixed_point_lane` before launching specialists:

| Lane | Trigger | Specialist budget | Default subagent mode |
|---|---|---:|---|
| `direct-closure` | One narrow owner-known change, obvious proof lane, no material route uncertainty | 0 | `off` |
| `targeted` | One read-heavy uncertainty could change the owner graph or proof route | 1-2 | `targeted` |
| `expanded-targeted` | Coupled truth units or two independent uncertainty classes | 3-4 | `targeted` |
| `swarm` | Broad/high-risk/exhaustive request, audit carryover, or explicit independent coverage | 5+ | `swarm` |

Rules:

- Default lane is `direct-closure` only when the canonical owner is known.
- If ownership is unknown, do not pretend the task is narrow.
- Escalate only when uncertainty is route-changing.
- Do not launch multiple specialists for the same uncertainty class unless the first packet was stale, invalid, wrong-scope, or materially incomplete.
- Specialists may map evidence, ownership, hazards, negative evidence, or proof; root owns final proof commands and final verdict.

## Specialist packet validation

Accepted specialist packets must be packet-native, scoped, current, evidence-bearing, and free of wrappers or acknowledgements.

Required fields:

- `artifact_state_id`
- `artifact_state_label`
- `scope`
- `truth_units_or_findings_covered`
- `top_material_signals` with artifact references
- `unresolved_signals`
- `agreement_pressure`
- `stale`
- `final_call`

Reject packets that are stale, wrong-scope, transport-invalid, acknowledgement-only, wrapper-leaking, or lacking artifact references. Rejected packets still appear in Specialist Briefing Ledger and Specialist Value Receipts.

## One-change challenge

Run this challenge after a candidate material fixed point and before every final closure attempt. Also use it before escalation to a broader lane.

```yaml
one_change_challenge:
  candidate_extra_change: "..."
  candidate_type: delete | privatize | merge | tighten-owner | reuse-owner | add-escrow | validate-only | no-impactful-change
  truth_unit: "TU-... | none"
  materiality: material | non-material | unknown
  proof_needed: "..."
  negative_ledger_checked: queried | mapped | handoff | no-applicable-evidence | unavailable
  addition_escrow_checked: yes | no
  matched_negative_ids: []
  reopening_criteria_satisfied: yes | no | n/a
  decision: apply | reject | defer | escalate-to-specialist | no-impactful-change
  reason: "..."
```

Rules:

- Attempt one subtractive or owner-tightening candidate before proposing an additive candidate.
- If the challenge produces no material candidate and proof lanes are obvious, do not fan out.
- If selected move matches active negative evidence, choose a different move or prove reopening criteria.
- After any implemented one-change improvement, rerun de novo review before closure.

## Surface Delta Dashboard

Before closure, report how the active system changed.

```md
| Metric | Before | After | Delta | Note |
|---|---:|---:|---:|---|
| Truth units with known canonical owner | | | | |
| Truth units with duplicate owners | | | | |
| Shadow owners | | | | |
| Public/exported symbols touched | | | | |
| Compatibility aliases | | | | |
| Proof/check lanes | | | | |
| Generated artifacts/docs that mirror checks | | | | |
| Fixture families | | | | |
| Open addition escrow items | | | | |
| Changed files | | | | |
| LOC | | | | |
| Unresolved material findings | | | | |
```

Tension signals:

- LOC up and owner count unchanged: likely local patching; rerun Patch Tournament.
- Proof lanes up and owner unclear: collapse proof surface before closure.
- Public symbols up while non-goals reject public widening: block closure.
- Tests up without an old-false-state witness: proof may be review-comfort-only.
- Deletions high but proof unchanged: check stale references and proof coverage.
- Clean reviews with open addition escrow: not a fixed point.

## Closure gates

### Truth-owner normal-form gate

```yaml
truth_owner_normal_form_gate:
  status: satisfied | open | blocked | unavailable
  truth_units_total: 0
  truth_units_with_canonical_owner: 0
  duplicate_owner_count: 0
  shadow_owner_count: 0
  unresolved_counterexample_count: 0
  open_addition_escrow_count: 0
  stale_surface_count: 0
  reason: "..."
```

Gate rules:

- `satisfied`: every material truth unit has one owner; no unresolved counterexamples; no open addition escrow; stale/shadow surfaces are absent or explicitly accepted-risk.
- `open`: an owner, counterexample, shadow surface, or escrow item remains unresolved.
- `blocked`: evidence required to decide ownership/proof is unavailable.
- `unavailable`: tooling/context cannot build the graph; explain the limit and downgrade closure.

### Negative evidence closure gate

```yaml
negative_evidence_closure_gate:
  status: satisfied | open | blocked | unavailable
  active_exclusions_count: 0
  repeated_failed_route_used: yes | no
  reopening_criteria_satisfied: yes | no | n/a
  learnings_hits_applicability_checked: yes | no | n/a
  reason: "..."
```

### Verification closure gate

Closure requires proof commands or explicitly bounded manual evidence appropriate to the tier, plus a residual-risk statement.

If a validation command changes code, config, dependencies, lockfiles, generated artifacts, behavior docs, or tests, reset review/closure accounting and rerun the loop.

## Orchestration algorithm

1. Establish entry state, `artifact_state_id`, objective, scope, constraints, and done condition.
2. If unresolved review comments exist and relevance is unclear, start with `review-adjudication`.
3. Run Routing Preflight, including Negative Ledger Pass and initial Truth-Owner Graph.
4. Choose fixed-point lane and subagent mode.
5. For each review finding or requested change, convert it into a truth unit or counterexample.
6. Run Patch Tournament for each material truth unit or coupled invariant cluster.
7. Select the smallest rewrite that moves the graph toward normal form.
8. Fill Preservation / Invariant Card when deleting, privatizing, merging, refactoring, or tightening an owner.
9. Implement/remediate with `accretive-implementer` or root-equivalent doctrine.
10. Track every addition in Addition Escrow unless it directly replaces retired surface.
11. Verify with the fastest credible targeted proof, then required broader proof.
12. Run adversarial review or root-equivalent de novo reread; normalize findings back into the graph.
13. After failed/no-effect/regression/revert/rejection/pivot events, run Negative Capture Decision.
14. After two review/remediation cycles or growing addition escrow, pause feature work and run normal-form collapse.
15. Reach candidate material fixed point only when Truth-Owner Normal Form gate, negative evidence gate, and verification gate can all close.
16. Run pre-closure Negative Ledger Handoff.
17. Run pre-closure one-change challenge.
18. Emit Surface Delta Dashboard.
19. Run `verification-closure` or root-equivalent closure gates.
20. If closure reopens the loop, route the highest-value next rewrite and continue.
21. Stop only in a justified terminal state.

## Output contract

### Standard

Use concise sections in this order:

- Workflow
- Entry State
- Routing Preflight
- Upstream Intake when review-adjudication materially shaped the route
- Companion Skill Ledger
- Negative Ledger Pass
- Truth-Owner Graph
- Patch Tournament Ledger
- Addition Escrow Ledger
- Subagent Mode and Budget
- Specialist Value Receipts when specialists ran
- Implementation / Rewrite Summary
- Verification Ledger
- Surface Delta Dashboard
- One-Change Challenge
- Closure Gates
- Residual Risks
- Final State
- Do Next

### Fast

Use concise sections in this order:

- Entry State
- Truth-Owner Graph Delta
- Addition Escrow Status
- Negative Ledger Pass
- Verification
- Final State
- Do Next

## Do Next

The final section must say:

- `owner`: skill | user | none
- `action`: exact next phase, stop action, or `none`
- `why`: one sentence
- `state`: ready | conditionally-ready | needs-remediation | needs-decision | blocked

## Hard rules

- Never impose an arbitrary maximum number of loops.
- Never implement a non-trivial review finding until it is represented as a truth unit or counterexample.
- Never add code before running a Patch Tournament unless the change is trivial and root explicitly marks it as such.
- Never select `add-escrow` before delete, privatize, merge, tighten, and reuse were considered.
- Never declare a candidate fixed point with open addition escrow.
- Never declare a candidate fixed point while a material truth unit has duplicate owners.
- Never let a local precheck compensate for a weak canonical checker when the checker can own the invariant.
- Never preserve a public export, compatibility alias, proof lane, generated artifact, fixture family, or doc mirror merely because it helped close a review comment.
- Never treat LOC reduction as sufficient when ownership clarity regressed.
- Never treat passing tests as sufficient when stale surfaces still claim old truth.
- Never start a non-trivial fixed-point run without a root-owned Negative Ledger Pass.
- Never treat `no-applicable-negative-evidence` as proof that a route is novel.
- Never let active applicable negative evidence disappear before closure; mark it remediated, stale, superseded, reopened, accepted-risk, or still open.
- Never let a `learnings` hit become an exclusion rule without checking evidence and current-state applicability.
- Never append negative evidence to durable learnings unless it is decision-shaping, transferable, and counterfactually useful.
- Never launch specialists before declaring lane and budget.
- Never exceed the lane budget without a recorded budget exception.
- Never let stale specialist briefings masquerade as current evidence.
- Never let specialists own final proof commands or the final pass/fail verdict.
- Never mark a companion skill `used` unless its explicit output packet, invocation, or contract-shaped section is present.
- Never let review-adjudication quietly disappear once it materially shaped the route.
- Never declare a candidate fixed point while a material soundness gap remains unresolved.
- Never skip the pre-closure Negative Ledger Handoff.
- Never skip the pre-closure one-change challenge before final closure.

## Resources

- [review-adjudication](../review-adjudication/SKILL.md)
- [accretive-implementer](../accretive-implementer/SKILL.md)
- [adversarial-reviewer](../adversarial-reviewer/SKILL.md)
- [verification-closure](../verification-closure/SKILL.md)
- [negative-ledger](../negative-ledger/SKILL.md)
- [simplify-and-refactor-code-isomorphically](../simplify-and-refactor-code-isomorphically/SKILL.md)
- [negative-ledger pass](references/negative-ledger-pass.md)
- [lane-and-specialist-budget.md](references/lane-and-specialist-budget.md)
- [companion-skill-ledger.md](references/companion-skill-ledger.md)
- [specialist-value-receipt.md](references/specialist-value-receipt.md)
- [closure-handoff-contract.md](references/closure-handoff-contract.md)
- [closure-handoff-template.md](references/closure-handoff-template.md)
- [one-change-challenge.md](references/one-change-challenge.md)
- [common-soundness.md](references/common-soundness.md)
- [common-ledgers.md](references/common-ledgers.md)
- [common-cli-reporting.md](references/common-cli-reporting.md)
- [common-routing-vocabulary.md](references/common-routing-vocabulary.md)
- [specialist-packet-contract.md](../references/specialist-packet-contract.md)
