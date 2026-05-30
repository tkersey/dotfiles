---
name: fixed-point-driver
description: "Drive exhaustive build-review-improve-verify loops to Truth-Owner Normal Form: one canonical owner per material invariant, no duplicate truth surfaces, no unresolved review counterexamples, no unretired additive scaffolding, and proof-gated closure. Trigger when coding needs de novo re-litigation, PR review closure, repeated review/fix loops, invariant repair, proof-surface hardening, negative-evidence pruning, CAS/Codex review resolution, optional `$parse` architecture fingerprint preflight, or when agents risk adding local patches instead of deleting/refactoring/canonicalizing. Do not use for trivial one-step tasks or when the user wants one narrow phase."
---

# Fixed-Point Driver

This skill coordinates implementation, review, adjudication, reduction, verification,
and closure until the artifact set reaches **Truth-Owner Normal Form**.

## The single rule

Drive toward this state:

> Every material invariant has exactly one canonical owner, every witness points
> back to that owner, every review finding is either discharged or represented as
> a counterexample, every additive scaffold has been promoted/collapsed/deleted,
> and no duplicate truth surface remains merely because it helped satisfy an
> intermediate review loop.

A fixed point is not "review is clean". A fixed point is a normal form of the
code and proof system.

## Why this skill exists

Frontier coding agents are good at adding code and addressing review comments.
They are weaker at noticing that the best fix is to delete a path, collapse
duplicate owners, privatize a surface, or tighten the one boundary that should
have owned the invariant from the start.

This skill converts review churn into an ownership-normalization problem. The
workflow is not "find comment -> patch comment -> rerun review." It is:

```text
finding -> counterexample -> architecture fingerprint when route-changing
        -> truth owner graph -> rewrite candidates -> normal-form proof -> closure
```

## Companion skills

- `parse` supplies a collector-backed architecture fingerprint when repo dialect,
  subsystem boundaries, architecture seams, public contract roots, generated
  boundaries, adapter/plugin registries, or workflow/pipeline topology can
  change the truth-owner graph, selected rewrite, proof boundary, or deletion /
  privatization decision. It does not own implementation, reduction, invariant
  enforcement, or closure.
- `review-adjudication` decides which review comments matter, but this skill
  decides whether the selected work preserves Truth-Owner Normal Form.
- `accretive-implementer` performs implementation/remediation when the selected
  rewrite is narrow and owned.
- `adversarial-reviewer` challenges the current artifact state and should report
  normal-form violations, not just bugs.
- `verification-closure` performs decisive proof and closure gating.
- `negative-ledger` preserves disconfirmed routes, repeated additive churn,
  review rejections, and reopened/deleted surface decisions.
- `learnings` stores durable evidence-backed lessons.
- `simplify-and-refactor-code-isomorphically` may be invoked for
  behavior-preserving collapse, but Truth-Owner Normal Form is owned here and is
  not optional.

## Core vocabulary

### Truth unit

A material invariant, contract, semantic fact, proof obligation, compatibility
rule, public-surface guarantee, generated-artifact fact, policy rule, or safety
condition that the codebase must preserve.

Examples:

- certificate refs must bind to the artifact actually checked;
- unsupported residual shapes must fail closed under strict policy;
- a public root must not expose internal proof machinery;
- a generated artifact's fingerprint must be recomputed from current contents
  before it is trusted;
- a review-clean branch must be clean against the pinned base and current HEAD,
  not an older tree;
- an adapter/plugin seam that the repo architecture treats as a boundary must not
  be collapsed into a local special case without proof that the seam is stale or
  shadow-owned.

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
- adapter/plugin registry
- workflow/DAG definition
- generated-boundary source artifact
- test/proof harness that is the executable truth surface

### Shadow owner

Any second place that claims, mirrors, partially checks, documents, generates, or
assumes the same truth without being the canonical owner.

Shadow owners include duplicate validators, compatibility aliases, matrix docs
that mirror executable checks, fixture families that encode the same invariant
repeatedly, hand-maintained generated artifacts, local prechecks that compensate
for a weak canonical checker, and public exports retained only because tests
still mention them.

### Counterexample

A review finding, failed test, stale proof, negative learning, architecture-drift
signal, or manual inspection that shows the current truth-owner graph admits a
false state, duplicates ownership, violates a repo architecture seam, or cannot
prove the delivered artifact.

A review comment is not an implementation task until it is represented as a
counterexample to a truth unit.

### Rewrite

A change to the truth-owner graph. Preferred rewrite order:

1. **Delete** a stale/shadow surface.
2. **Privatize** or narrow a visible surface.
3. **Merge** duplicate owners or proof paths.
4. **Tighten** the canonical owner.
5. **Reuse** an existing owner/witness path.
6. **Add** new code only into addition escrow.

### Addition escrow

Any new helper, checker, proof lane, fixture family, compatibility alias, public
symbol, generated artifact, or model added during a fixed-point loop starts in
escrow. It cannot survive closure unless it is promoted to canonical owner,
collapses/removes another surface, or has explicit owner-proof and no cheaper
rewrite can satisfy the truth unit.

## Material fixed point

A run reaches material fixed point only when all are true:

- no unresolved material finding remains;
- every accepted review finding is mapped to a truth unit and resolved
  counterexample;
- every material truth unit has one canonical owner;
- shadow owners are deleted, privatized, merged, or explicitly justified;
- addition escrow is empty or every surviving addition has owner-proof;
- no active negative evidence blocks the route;
- no stale specialist packet, stale review result, stale proof, stale fixture, or
  stale artifact is used for closure;
- if architecture classification was route-changing, the `$parse` architecture
  fingerprint was consumed or its unavailability was recorded and compensated;
- the proof suite directly witnesses the changed truth units;
- the pre-closure one-change challenge cannot identify a higher-value
  normal-form rewrite.

## Output modes

- **Standard**: full workflow state, Architecture Fingerprint Preflight when
  route-changing, Truth-Owner Graph, ledgers, proof, closure.
- **Fast**: current artifact state, architecture fingerprint status when relevant,
  highest-value rewrite, escrow status, open gates, exact next action.

## CLI-tail-weighted reporting

- Keep early ledgers terse.
- End with **Final State** and **Do Next**.
- **Do Next** must be the last section.
- If the report is long, compress prose before compressing Architecture
  Fingerprint Preflight, Truth-Owner Graph, addition escrow, negative ledger,
  closure state, or exact next action.

## Global doctrine

Every phase inherits **UNSOUND**, **WITNESS-BEARING**, **PRESERVATION-AWARE**,
**PROGRESS-AWARE**, **REFINEMENT-AWARE**, **MECHANISTIC**, **ACCRETIVE**, and
**TRACEABLE** standards.

Additional orchestration pressure: **TRUTH-OWNER-NORMALIZING**, **EXHAUSTIVE**,
**DE NOVO**, **ADVERSARIAL**, **SATURATING**, **MATERIAL**, **PARSIMONIOUS**,
**SUBTRACTIVE-FIRST**, **CANONICAL**, **INVARIANT-GRADED**, **HAZARD-SEEKING**,
**LEDGERIZED**, **HISTORY-AWARE**, **NEGATIVE-EVIDENCE-AWARE**,
**ARCHITECTURE-FIT-AWARE**, **ESCROW-AWARE**, **STALE-PROOF**, and
**REOPENABLE**.

`ACCRETIVE` means evidence-preserving and reviewable. It does not mean additive.

## Architecture Fingerprint Preflight

`$parse` is the optional, route-changing architecture classifier for this skill.
It is not generic source exploration and it is not a substitute for the
Truth-Owner Graph.

Run `$parse` before building or finalizing the Truth-Owner Graph when
architecture classification can materially change owner selection, rewrite
selection, proof boundary, or deletion/privatization safety.

Use `$parse` in:

- `quick` mode for repo-dialect preflight;
- `standard` mode when the change crosses subsystem boundaries, generated
  boundaries, public package roots, plugin/adapter seams, workflow/pipeline
  definitions, or docs-vs-code architecture claims;
- `deep` mode only when thin or mixed architecture signals can change the route
  and the fixed-point run is broad/high-risk enough to justify it.

Do not run `$parse` merely to understand the whole repo. If the task needs broad
onboarding, that is `codebase-archaeology`, not fixed-point routing.

### Parse triggers

Run `$parse` when any of these are true:

- the repo or target slice is unfamiliar;
- `current_owner` or `desired_owner` in the Truth-Owner Graph would otherwise be
  `unknown`;
- touched paths cross package, adapter, plugin, generated, workflow, public API,
  storage/runtime, or deploy/runtime boundaries;
- the Patch Tournament is considering delete, privatize, merge, or tighten across
  subsystem seams;
- a review finding may be caused by architecture drift, not a local bug;
- docs claim an architecture that may conflict with implementation;
- a companion or specialist proposes a rewrite whose safety depends on repo-wide
  architecture conventions;
- proof boundaries depend on whether tests/examples/docs are contract surfaces,
  generated mirrors, or local incidental scaffolding.

Skip `$parse` only when all are true:

- the change is one narrow owner-known fix;
- touched paths are local to one already-understood truth unit;
- proof lane is obvious;
- no deletion/privatization/merge crosses a public, generated, adapter, plugin,
  workflow, package, or runtime boundary;
- architecture classification cannot change owner selection, rewrite class,
  proof boundary, or deletion/privatization safety.

### Parse consumption packet

When `$parse` is used, summarize the consumed handoff in the fixed-point output:

```yaml
architecture_fingerprint_preflight:
  status: used | not-needed | unavailable | blocked
  mode: quick | standard | deep | n/a
  scope: repo-wide | focused-slice | changed-paths | n/a
  focus_paths: []
  collector_evidence: "parse-arch command shape, parse memo ref, or unavailable reason"
  repo_kind: "..."
  dominant_architecture: "..."
  confidence: high | medium | low | n/a
  runner_up: "..."
  coexisting_patterns: []
  major_subsystems: []
  architecture_drift: none | present | unknown | n/a
  repo_fit_hints_consumed: []
  effect_on_route: owner-selection | rewrite-selection | proof-boundary | deletion-safety | no-route-change | n/a
  compensation_if_unavailable: "..."
```

Status rules:

- `used`: a parse memo or architecture handoff packet exists and includes
  collector command evidence, dominant architecture, confidence, and repo-fit
  hints.
- `not-needed`: canonical owner, proof boundary, and rewrite safety are local and
  architecture classification cannot change the route.
- `unavailable`: `$parse`, `parse-arch`, or the required repo context is not
  available. Name the exact missing tool/path/command.
- `blocked`: architecture classification is route-changing but cannot be obtained
  safely. Do not proceed into destructive rewrite classes unless proof is local
  and the architecture risk is explicitly bounded.

### How parse constrains fixed-point work

Use parse outputs this way:

- `repo_kind` constrains what counts as a plausible architecture owner. In a
  `library-sdk`, public contract roots and examples/tests may be owners; in a
  `pipeline`, DAG/job definitions and sinks may be owners; in a
  `plugin-extension`, host/plugin registries and adapter seams may be owners.
- `dominant_architecture` and `coexisting_patterns` constrain whether a surface
  is a canonical seam or a shadow owner.
- `major_subsystems` prevents flattening slice-local variants into one repo-wide
  owner model.
- `architecture_drift` can create truth units about stale docs, misleading public
  seams, or docs-vs-code mismatch.
- `repo_fit_hints` constrain Patch Tournament candidates. A rewrite that
  violates a consumed repo-fit hint must explain why the hint is obsolete,
  local-only, or outweighed by proof.

## Truth-Owner Graph

Every non-trivial Standard run must maintain a compact Truth-Owner Graph. It is
the central artifact of this skill.

```yaml
truth_owner_graph:
  artifact_state_id: "branch/head/base/diff-digest/phase"
  objective: "..."
  architecture_fingerprint:
    status: used | not-needed | unavailable | blocked
    effect_on_graph: owner-selection | proof-boundary | deletion-safety | no-route-change | n/a
  truth_units:
    - id: TU-001
      invariant: "..."
      current_owner: "file/symbol/boundary or unknown"
      desired_owner: "file/symbol/boundary"
      architecture_fit: aligned | violates-parse-hint | unknown | not-applicable
      parse_evidence_ref: "parse memo/handoff section or n/a"
      owner_status: canonical | duplicate | missing | weak | stale | unknown
      counterexamples:
        - source: review | test | proof-gap | negative-ledger | architecture-drift | manual | specialist
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
- If two comments touch the same truth unit, resolve the owner graph, not the
  comments independently.
- If an invariant has no owner, choose an existing boundary before creating a new
  one.
- If an invariant has multiple owners, prefer deletion/merge/privatization before
  strengthening all of them.
- If the graph cannot be built from available evidence, route to validation or
  block; do not invent ownership.
- When `architecture_fingerprint.status: used`, consume the parse handoff before
  assigning `desired_owner`.
- If `$parse` identifies a surface as an architecture seam, public contract root,
  generated boundary, adapter/plugin registry, workflow boundary, or subsystem
  variant, do not classify it as a shadow owner unless current proof shows it is
  stale, duplicated, or no longer an independent obligation.
- If `$parse` reports docs-vs-code drift, decide whether the drift is a truth
  unit, stale surface, or non-material caveat before closure.

## Code-change doctrine

When writing code or making a change, do it in the most optimal way possible for
the current material objective.

Rules:

- Prefer the smallest complete design that preserves invariants, removes or
  narrows foot-guns, and leaves a clear proof path.
- Choose durable, idiomatic, maintainable code over clever shortcuts, speculative
  abstraction, broad rewrites, or local patch accretion.
- Optimize for correctness and evidence first, then ownership clarity,
  architecture fit, simplicity, performance, ergonomics, and future change cost
  when materially relevant.
- Do not use "optimal" to justify unbounded scope, aesthetic churn, bypassing
  negative evidence, exceeding lane budgets, weakening review, skipping closure
  gates, or disregarding a consumed architecture fingerprint.
- When materially valid implementations compete, select the rewrite that moves
  the truth-owner graph closest to normal form without violating repo architecture
  seams unless those seams are proved stale or shadow-owned.

## Rewrite selection

For every material truth unit or accepted review finding, run a **Patch
Tournament** before editing.

```yaml
patch_tournament:
  truth_unit: TU-001
  counterexample_refs: []
  architecture_fingerprint_status: used | not-needed | unavailable | blocked
  candidates:
    - id: A
      rewrite: delete | privatize | merge | tighten-owner | reuse-owner | add-escrow | validate-only | no-change
      sketch: "..."
      canonical_owner_after: "..."
      owners_removed_or_demoted: []
      architecture_fit: aligned | violates-parse-hint | unknown | not-applicable
      parse_evidence_ref: "parse handoff path/section or n/a"
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
3. Merge duplicate owners, registries, aliases, fixtures, generated artifacts,
   reports, or proof lanes.
4. Tighten the existing canonical checker, builder, validator, generator,
   certificate, API, architecture seam, or boundary.
5. Reuse an existing helper, proof lane, test lane, or contract surface.
6. Add new code only into addition escrow.

`add-escrow` is legal only after the first five rewrite classes were considered
and rejected with evidence.

Architecture-fit rules:

- If a candidate deletes, privatizes, or merges a surface that `$parse` identifies
  as an architecture seam, public contract root, generated boundary, adapter /
  plugin registry, workflow boundary, or subsystem variant, classify
  `architecture_fit: violates-parse-hint` unless the candidate proves the surface
  is stale, shadow-owned, or no longer an independent obligation.
- `violates-parse-hint` does not automatically block a rewrite, but it requires a
  concrete proof axis and an explanation in the candidate's `reason`.
- `architecture_fit: unknown` on a destructive cross-boundary rewrite requires
  validation-only, `$parse`, or a blocked route.
- Parse evidence constrains architecture fit. Direct current proof still decides
  correctness.

## Addition Escrow Ledger

All newly added code/proof/docs in a fixed-point run enter escrow unless they
directly replace deleted/merged/privatized surface in the same rewrite.

```yaml
addition_escrow:
  - id: AE-001
    added_surface: "file/symbol/test/doc/build-step"
    reason_added: "..."
    truth_unit: TU-001
    intended_lifetime: permanent-owner | temporary-scaffold | proof-fixture | compatibility-bridge | unknown
    rent_payment: deleted-shadow | privatized-surface | merged-owner | tightened-owner | generated-from-owner | none
    cheaper_rewrite_defeated: yes | no
    architecture_fit: aligned | violates-parse-hint | unknown | not-applicable
    parse_evidence_ref: "..."
    promotion_criteria: "..."
    collapse_or_delete_criteria: "..."
    status: open | promoted | collapsed | deleted | accepted-risk | blocked
```

Rules:

- No closure while addition escrow contains `open` items.
- A permanent addition must either become the canonical owner or prove why the
  existing owner cannot own the truth unit.
- A test addition must witness the old false state or a current truth unit;
  review-comfort tests remain suspect.
- A helper addition must retire duplication, not merely name it.
- A compatibility alias must have explicit deletion or reopening criteria.
- If `$parse` was used and the addition creates a new architecture seam, adapter,
  public root, generated boundary, or workflow surface, the addition must explain
  why that surface belongs in the repo's actual architecture.
- After two review/remediation cycles with growing escrow, stop feature work and
  run a normal-form collapse pass.

## Normal-form reduction loop

This loop adapts the best of `simplify-and-refactor-code-isomorphically` to
semantic fixed-point work.

```text
1. BASELINE    -> current artifact state, proof state, changed path set, diff/stat snapshot
2. PARSE       -> architecture fingerprint when route-changing
3. GRAPH       -> truth units, canonical owners, shadow owners, stale surfaces, addition escrow
4. TOURNAMENT  -> patch candidates ordered by delete/privatize/merge/tighten/reuse/add
5. CARD        -> preservation/invariant card for selected rewrite
6. REWRITE     -> implement one truth-unit rewrite or one tightly coupled invariant cluster
7. VERIFY      -> targeted and required full proof; stale-surface checks
8. LEDGER      -> graph delta, escrow delta, rejected rewrites, proof result
9. REREAD      -> adversarial review asks whether the graph got smaller or just locally quieter
```

Do not measure success only by LOC. Measure truth entropy:

- owner count per truth unit;
- shadow owner count;
- architecture seams preserved vs wrongly flattened;
- public/exported surface count;
- proof-lane mirror count;
- generated artifact families;
- compatibility aliases;
- open addition escrow;
- stale proof/comment/fixture references;
- total review counterexamples remaining.

## Surface Reduction Matrix

Use this matrix inside the Patch Tournament when multiple reduction candidates
exist.

```text
Score = (Reduction Payoff x Confidence) / Risk
```

Reduction Payoff:

- 5 = removes a public/exported surface, duplicate proof lane, stale compatibility
  path, generated artifact family, or obsolete subsystem
- 4 = collapses duplicate checker/generator/certificate/model ownership
- 3 = removes helper/wrapper/fixture duplication or narrows a public seam
- 2 = deletes local dead code, redundant test setup, stale docs, or pass-through
  wrappers
- 1 = small cleanup with little future-review impact

Confidence:

- 5 = current tests/proofs/manual inspection show the removed surface has no
  independent obligation
- 4 = all callsites and proof surfaces are mapped
- 3 = local callsites mapped, broader proof impact plausible
- 2 = likely but incomplete evidence
- 1 = aesthetic suspicion

Risk:

- 5 = public API, persisted format, certificate/proof surface, generated artifact,
  runtime semantics, cross-package contract, adapter/plugin seam, workflow/DAG
  boundary, or parse-identified architecture seam
- 4 = multi-module invariant, compatibility behavior, or subsystem-variant seam
- 3 = internal shared helper or test/proof infrastructure
- 2 = local helper/fixture
- 1 = unreachable/pass-through/stale-only surface

Rules:

- Apply candidates with score >= 2.0 when they preserve or strengthen the
  invariant and do not violate consumed architecture constraints without proof.
- Reject lower-scoring candidates unless they remove an active material foot-gun.
- If an additive rewrite is selected while a higher-scoring reduction exists,
  explain the preservation axis, ownership fact, or architecture-fit fact that
  blocks reduction.

## Preservation / Invariant Card

Before any delete, merge, privatize, refactor, or owner-tightening rewrite, fill
this card.

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
  architecture_after:
    architecture_fingerprint_status: used | not-needed | unavailable | blocked
    architecture_fit: aligned | violates-parse-hint | unknown | not-applicable
    parse_evidence_ref: "..."
    seam_preserved_or_retired: "preserved | retired-as-stale | demoted-shadow | not-applicable | unknown"
  preservation_axes:
    public_api_or_export_shape: "..."
    error_semantics: "..."
    ordering_or_tie_breaking: "..."
    allocation_lifetime_or_ownership: "..."
    laziness_or_evaluation_timing: "..."
    side_effects_logs_metrics_traces: "..."
    fingerprints_refs_domains_versions: "..."
    generated_artifacts_or_fixtures: "..."
    adapter_plugin_or_workflow_boundary: "..."
    backward_compatibility: "..."
    tests_or_proof_lanes: "..."
  verification:
    old_false_state_witness: "..."
    targeted_check: "..."
    full_check: "..."
    stale_surface_check: "..."
    architecture_fit_check: "..."
    residual_uncertainty: "..."
```

If a row cannot be filled and the gap is material, choose validation-only or
blocked. Do not edit from vibes.

## Review-adjudication intake

If the user provides review comments or a prior adjudication result, start with
`review-adjudication` unless the comments are already in a complete, current,
route-ready packet.

Rules:

- Treat adjudicated `Act On` rows as routed work, not as unquestionable truth.
- Preserve `Rebut`, `Defer / Out of Scope`, and `Need Evidence` rows as
  constraints.
- If upstream adjudication lacks `truth_unit`, `canonical_owner`, or
  `solution_class`, reconstruct them before implementation.
- A review comment whose local fix would add a shadow owner must be reframed as
  an owner-graph problem.
- A review comment whose local fix would violate a parse-identified architecture
  seam must be reframed as an architecture-fit and owner-graph problem.
- Do not implement a review finding solely because it is current, P2+,
  invariant-shaped, or easy to patch.

## Negative-ledger posture

For every non-trivial fixed-point run, perform a root-owned Negative Ledger Pass
at routing preflight and refresh it before closure.

Default behavior:

- Query/map current-run witnesses, fixed-point ledgers, review comments,
  `learnings`, and repo history when available.
- Include architecture-fit failures, mistaken seam deletions, duplicate-owner
  fixes, and false local-precheck routes in the topical query when relevant.
- Normalize failed attempts into the Negative Evidence Ledger.
- Mark entries as `active`, `stale`, `superseded`, `reopened`, `unknown`, or
  `need-evidence`.
- Convert only active, witness-bearing, current-state-applicable entries into
  narrow exclusion rules.
- Capture additive churn, duplicate-owner fixes, proof-surface sprawl, no-effect
  refactors, review rejections, reverts, failed reviews, architecture-fit
  mistakes, and strategy pivots when decision-shaping.
- Run pre-closure handoff even when there are no active exclusions.

Negative evidence is advisory, not a veto authority, unless its witness and
current applicability bind the current artifact state.

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
    parse_fingerprint: yes | no | n/a
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

Every Standard run must establish this compact preflight before implementation,
fanout, or closure.

```yaml
routing_preflight:
  task_shape: narrow-review-comment | review-batch | implementation | remediation | hardening | audit | optimization | migration | unknown
  artifact_state_id: "..."
  architecture_parse:
    status: used | not-needed | unavailable | blocked
    mode: quick | standard | deep | n/a
    scope: repo-wide | focused-slice | changed-paths | n/a
    focus_paths: []
    repo_kind: "..."
    dominant_architecture: "..."
    confidence: high | medium | low | n/a
    runner_up: "..."
    coexisting_patterns: []
    architecture_drift: none | present | unknown | n/a
    effect_on_route: owner-selection | rewrite-selection | proof-boundary | deletion-safety | no-route-change | n/a
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
    parse: used | not-needed | unavailable | blocked
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

- `root-equivalent` means the root performed the stage's doctrine without a
  distinct auditable invocation.
- Do not use `root-equivalent` for `parse`; the distinction that matters is
  whether a collector-backed architecture fingerprint was consumed.
- `negative_ledger_required` is `yes` for every non-trivial fixed-point run.
- `truth_owner_graph_required` is `yes` for every non-trivial fixed-point run.
- `simplify_refactor: not-needed` is legal only when no behavior-preserving
  collapse candidate is material.
- `parse: not-needed` is legal only when canonical owner, proof boundary, and
  rewrite safety are local and architecture classification cannot change the
  route.
- `parse: used` requires a parse memo or handoff packet whose outputs are
  consumed by Routing Preflight, Truth-Owner Graph, Patch Tournament, Addition
  Escrow, Preservation / Invariant Card, or Closure Gates.

## Canonical ledgers

Maintain and refresh these ledgers after every meaningful pass:

- Architecture Fingerprint Preflight when route-changing
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

Every meaningful pass must carry an `artifact_state_id` that includes enough
current-state evidence to make stale packets obvious:

- branch name when available;
- HEAD or comparable revision;
- base ref/SHA when review-bound;
- diff hash or changed-file digest;
- touched path set;
- phase label such as `prepatch`, `postpatch`, `post-fixture-refresh`, or
  `closure-candidate`.

Any material edit, fixture regeneration, dependency update, proof-surface change,
generated-artifact change, owner-graph rewrite, or architecture-seam rewrite
invalidates older specialist packets and stale proofs. If a `$parse` fingerprint
was consumed before such a change and the change alters architecture evidence or
focus paths, mark the old parse result stale and rerun only if architecture
classification remains route-changing.

## Lane and subagent budget

Subagent mode is `off`, `targeted`, or `swarm`.

Declare the current `fixed_point_lane` before launching specialists:

| Lane | Trigger | Specialist budget | Default subagent mode |
|---|---|---:|---|
| `direct-closure` | One narrow owner-known change, obvious proof lane, no material route uncertainty, architecture classification not route-changing | 0 | `off` |
| `targeted` | One read-heavy uncertainty could change the owner graph, architecture fit, or proof route | 1-2 | `targeted` |
| `expanded-targeted` | Coupled truth units or two independent uncertainty classes | 3-4 | `targeted` |
| `swarm` | Broad/high-risk/exhaustive request, audit carryover, or explicit independent coverage | 5+ | `swarm` |

Rules:

- Default lane is `direct-closure` only when the canonical owner is known.
- If ownership is unknown, do not pretend the task is narrow.
- If architecture classification is route-changing and unavailable, do not
  pretend the task is narrow unless the destructive rewrite classes are off the
  table and proof is local.
- Escalate only when uncertainty is route-changing.
- Do not launch multiple specialists for the same uncertainty class unless the
  first packet was stale, invalid, wrong-scope, or materially incomplete.
- Specialists may map evidence, ownership, hazards, negative evidence,
  architecture-fit uncertainty, or proof; root owns final proof commands and
  final verdict.

## Specialist packet validation

Accepted specialist packets must be packet-native, scoped, current,
evidence-bearing, and free of wrappers or acknowledgements.

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

Reject packets that are stale, wrong-scope, transport-invalid,
acknowledgement-only, wrapper-leaking, or lacking artifact references. Rejected
packets still appear in Specialist Briefing Ledger and Specialist Value Receipts.

Specialists do not replace `$parse`. If a specialist maps architecture-like
evidence that is route-changing, either run `$parse`, mark parse unavailable /
blocked, or explicitly constrain the specialist evidence to non-classification
use.

## One-change challenge

Run this challenge after a candidate material fixed point and before every final
closure attempt. Also use it before escalation to a broader lane.

```yaml
one_change_challenge:
  candidate_extra_change: "..."
  candidate_type: delete | privatize | merge | tighten-owner | reuse-owner | add-escrow | validate-only | no-impactful-change
  truth_unit: "TU-... | none"
  materiality: material | non-material | unknown
  proof_needed: "..."
  architecture_parse_checked: used | not-needed | unavailable | blocked
  negative_ledger_checked: queried | mapped | handoff | no-applicable-evidence | unavailable
  addition_escrow_checked: yes | no
  matched_negative_ids: []
  reopening_criteria_satisfied: yes | no | n/a
  decision: apply | reject | defer | escalate-to-specialist | no-impactful-change
  reason: "..."
```

Rules:

- Attempt one subtractive or owner-tightening candidate before proposing an
  additive candidate.
- If the challenge produces no material candidate and proof lanes are obvious, do
  not fan out.
- If selected move matches active negative evidence, choose a different move or
  prove reopening criteria.
- If selected move contradicts a consumed parse hint, prove the relevant seam is
  stale/shadow-owned or reject the move.
- After any implemented one-change improvement, rerun de novo review before
  closure.

## Surface Delta Dashboard

Before closure, report how the active system changed.

```md
| Metric | Before | After | Delta | Note |
|---|---:|---:|---:|---|
| Truth units with known canonical owner | | | | |
| Truth units with duplicate owners | | | | |
| Shadow owners | | | | |
| Architecture seams touched | | | | |
| Parse-identified seams retired as stale/shadow-owned | | | | |
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

- LOC up and owner count unchanged: likely local patching; rerun Patch
  Tournament.
- Proof lanes up and owner unclear: collapse proof surface before closure.
- Public symbols up while non-goals reject public widening: block closure.
- Tests up without an old-false-state witness: proof may be review-comfort-only.
- Deletions high but proof unchanged: check stale references and proof coverage.
- Clean reviews with open addition escrow: not a fixed point.
- A parse-identified seam was removed without a stale/shadow-owner proof:
  architecture-fit gate remains open.

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

- `satisfied`: every material truth unit has one owner; no unresolved
  counterexamples; no open addition escrow; stale/shadow surfaces are absent or
  explicitly accepted-risk.
- `open`: an owner, counterexample, shadow surface, or escrow item remains
  unresolved.
- `blocked`: evidence required to decide ownership/proof is unavailable.
- `unavailable`: tooling/context cannot build the graph; explain the limit and
  downgrade closure.

### Architecture-fit gate

```yaml
architecture_fit_gate:
  status: satisfied | open | blocked | not-needed | unavailable
  parse_status: used | not-needed | unavailable | blocked
  route_changing_parse_needed: yes | no
  architecture_fingerprint_consumed: yes | no | n/a
  selected_rewrites_consistent_with_parse: yes | no | unknown | n/a
  parse_identified_seams_retired_without_proof: []
  compensation_if_unavailable: "..."
  reason: "..."
```

Gate rules:

- `satisfied`: `$parse` was used when route-changing, and selected owners,
  rewrites, proof boundaries, and seam retirements do not contradict the parse
  handoff; or contradictions are proved stale/shadow-owned.
- `not-needed`: task was local, owner-known, and architecture classification
  could not change route or safety.
- `open`: a selected rewrite contradicts parse-derived architecture seams without
  proof, or parse was skipped despite being route-changing.
- `blocked`: architecture classification is route-changing but cannot be obtained
  safely, and destructive cross-boundary rewrites remain proposed.
- `unavailable`: `$parse` or `parse-arch` is unavailable; closure may continue
  only with bounded residual risk if proof is local and architecture fit is not a
  route-changing dependency.

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

Closure requires proof commands or explicitly bounded manual evidence appropriate
to the tier, plus a residual-risk statement.

If a validation command changes code, config, dependencies, lockfiles, generated
artifacts, behavior docs, or tests, reset review/closure accounting and rerun the
loop.

## Orchestration algorithm

1. Establish entry state, `artifact_state_id`, objective, scope, constraints,
   changed paths, and done condition.
2. If unresolved review comments exist and relevance is unclear, start with
   `review-adjudication`.
3. Decide whether Architecture Fingerprint Preflight is route-changing.
4. If route-changing, run `$parse` with focus paths from changed paths, review
   surfaces, public roots, generated boundaries, subsystem seams, or
   workflow/plugin/adapter boundaries.
5. Run Routing Preflight, including Architecture Fingerprint status, Negative
   Ledger Pass, and initial Truth-Owner Graph.
6. Choose fixed-point lane and subagent mode.
7. For each review finding or requested change, convert it into a truth unit or
   counterexample using the parse fingerprint when it affects owner or
   proof-boundary selection.
8. Run Patch Tournament for each material truth unit or coupled invariant cluster.
9. Select the smallest rewrite that moves the graph toward normal form and does
   not violate architecture fit without proof.
10. Fill Preservation / Invariant Card when deleting, privatizing, merging,
    refactoring, or tightening an owner.
11. Implement/remediate with `accretive-implementer` or root-equivalent doctrine.
12. Track every addition in Addition Escrow unless it directly replaces retired
    surface.
13. Verify with the fastest credible targeted proof, then required broader proof.
14. Run adversarial review or root-equivalent de novo reread; normalize findings
    back into the graph.
15. After failed/no-effect/regression/revert/rejection/pivot events, run Negative
    Capture Decision.
16. After two review/remediation cycles or growing addition escrow, pause feature
    work and run normal-form collapse.
17. Reach candidate material fixed point only when Truth-Owner Normal Form gate,
    Architecture-Fit gate, negative evidence gate, and verification gate can all
    close.
18. Run pre-closure Negative Ledger Handoff.
19. Run pre-closure one-change challenge.
20. Emit Surface Delta Dashboard.
21. Run `verification-closure` or root-equivalent closure gates.
22. If closure reopens the loop, route the highest-value next rewrite and
    continue.
23. Stop only in a justified terminal state.

## Output contract

### Standard

Use concise sections in this order:

- Workflow
- Entry State
- Architecture Fingerprint Preflight when route-changing or explicitly skipped
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
- Architecture Fingerprint Status when route-changing
- Truth-Owner Graph Delta
- Addition Escrow Status
- Negative Ledger Pass
- Verification
- Final State
- Do Next

## Companion Skill Ledger

Every Standard run must include a companion ledger row for each material
companion.

| Companion | Status | Evidence |
|---|---|---|
| `parse` | `used` / `not-needed` / `unavailable` / `blocked` | architecture fingerprint status; effect on owner graph or reason skipped |
| `review-adjudication` | `used` / `not-needed` / `root-equivalent` / `unavailable` | one phrase |
| `accretive-implementer` | `used` / `root-equivalent` / `not-needed` / `unavailable` | one phrase |
| `adversarial-reviewer` | `used` / `root-equivalent` / `not-needed` / `unavailable` | one phrase |
| `verification-closure` | `used` / `root-equivalent` / `not-needed` / `unavailable` | one phrase |
| `negative-ledger` | `queried` / `mapped` / `captured` / `handoff` / `no-applicable-evidence` / `unavailable` | one phrase |
| `learnings` | `recalled` / `captured` / `not-material` / `unavailable` | one phrase |
| `simplify-refactor` | `used` / `root-equivalent` / `not-needed` / `unavailable` | one phrase |

Status rules:

- Do not mark a companion `used` unless there is an invocation, output packet, or
  contract-shaped section.
- Do not mark `not-needed` without a task-shape reason.
- Do not use `root-equivalent` for `parse`; use `used`, `not-needed`,
  `unavailable`, or `blocked`.
- If a user explicitly asks for a named companion, `root-equivalent` is not
  enough unless the named skill is unavailable and the unavailability is
  recorded.

## Do Next

The final section must say:

- `owner`: skill | user | none
- `action`: exact next phase, stop action, or `none`
- `why`: one sentence
- `state`: ready | conditionally-ready | needs-remediation | needs-decision | blocked

## Hard rules

- Never impose an arbitrary maximum number of loops.
- Never implement a non-trivial review finding until it is represented as a truth
  unit or counterexample.
- Never add code before running a Patch Tournament unless the change is trivial
  and root explicitly marks it as such.
- Never select `add-escrow` before delete, privatize, merge, tighten, and reuse
  were considered.
- Never declare a candidate fixed point with open addition escrow.
- Never declare a candidate fixed point while a material truth unit has duplicate
  owners.
- Never let a local precheck compensate for a weak canonical checker when the
  checker can own the invariant.
- Never preserve a public export, compatibility alias, proof lane, generated
  artifact, fixture family, or doc mirror merely because it helped close a review
  comment.
- Never treat LOC reduction as sufficient when ownership clarity regressed.
- Never treat passing tests as sufficient when stale surfaces still claim old
  truth.
- Never start a non-trivial fixed-point run without a root-owned Negative Ledger
  Pass.
- Never treat `no-applicable-negative-evidence` as proof that a route is novel.
- Never let active applicable negative evidence disappear before closure; mark it
  remediated, stale, superseded, reopened, accepted-risk, or still open.
- Never let a `learnings` hit become an exclusion rule without checking evidence
  and current-state applicability.
- Never append negative evidence to durable learnings unless it is
  decision-shaping, transferable, and counterfactually useful.
- Never launch specialists before declaring lane and budget.
- Never exceed the lane budget without a recorded budget exception.
- Never let stale specialist briefings masquerade as current evidence.
- Never let specialists own final proof commands or the final pass/fail verdict.
- Never mark a companion skill `used` unless its explicit output packet,
  invocation, or contract-shaped section is present.
- Never let review-adjudication quietly disappear once it materially shaped the
  route.
- Never declare a candidate fixed point while a material soundness gap remains
  unresolved.
- Never skip the pre-closure Negative Ledger Handoff.
- Never skip the pre-closure one-change challenge before final closure.
- Never use `$parse` as broad source reading; it must produce a collector-backed
  architecture fingerprint or be marked unavailable/blocked.
- Never skip `$parse` when architecture classification can change canonical
  owner, rewrite class, proof boundary, or deletion/privatization safety.
- Never let a `$parse` memo override current proof, tests, or direct source
  evidence; use it to constrain architecture fit, not to decide correctness.
- Never delete, privatize, or merge a parse-identified architecture seam without
  proving it is stale, shadow-owned, or no longer an independent obligation.
- Never mark `parse: used` unless its handoff packet was consumed in Routing
  Preflight, Truth-Owner Graph, Patch Tournament, Addition Escrow, Preservation /
  Invariant Card, or Closure Gates.

## Resources

- [parse](../parse/SKILL.md)
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
