---
name: resolve
description: "Resolve review findings by compiling a Minimum Behavioral Kernel before compiling code. Reviews may add observations, witnesses, or explicit scope changes; they may not directly request additive delivery code. Use for `$resolve`, branch review/fix/prove/push/PR closure, repeated CAS findings, review-driven growth, authority/replay/reconstruction invariants, behavioral quotienting, semantic-surface conservation, proof compression, or MBKC-v1. Not for one-shot review, PR creation, merge/land, or isolated implementation."
metadata:
  version: "6.0.0"
  activation_cost: high
  default_depth: full
---

# Resolve

## Mission

`$resolve` is the **Minimum Behavioral Kernel Review Compiler**.

```text
Review adds observations.
Observations refine the kernel.
The kernel replaces the code.
```

The system must keep these objects separate:

```text
monotone:
  accepted observations
  counterexample witnesses
  durable negative evidence

replaceable:
  behavioral kernel draft
  realization design
  implementation
  proof layout
```

A review finding must never directly mean:

```text
add another guard
add another state field
add another helper
add another fallback
add another wound-specific test
```

It must mean exactly one of:

```text
existing kernel law is implemented incorrectly
finding is another witness for an existing law
finding proves a missing semantic distinction
finding is not current-branch liability
```

## Governing insight

Patch minimization is too late when the behavioral model is over-distinguished.

A large implementation can be locally irreducible while realizing a needlessly large model.

Therefore minimize in this order:

```text
1. accepted behavioral distinctions
2. implementation realization
3. proof realization
4. textual surface
```

The first three are semantic. Lines of code are a final tie-breaker and an audit signal.

## Controller requirement

The canonical controller remains:

```bash
resolve-c3
```

Before material `$resolve` work, run:

```bash
python3 codex/skills/resolve/tools/controller_preflight.py
```

Required controller capabilities:

```text
campaign_base_v1
minimum_behavioral_kernel_v1
mbkc_v1
kernel_quotient_v1
semantic_surface_v1
proof_compression_v1
physical_apply
physical_commit
physical_push
closure_horizon_v1
```

If these capabilities are unavailable:

```text
analysis and kernel drafting are allowed
delivery mutation is forbidden
closure is forbidden
next owner is the skills-zig controller implementation spec
```

Do not silently fall back to legacy C³ patch-tournament behavior for material review.

## Campaign identity

A review campaign has two fixed anchors:

```yaml
review_campaign:
  campaign_id:
  pr_number:
  campaign_base_sha:
  review_ready_baseline_sha:
  current_delivery_head:
```

### Campaign base

`campaign_base_sha` is the PR merge base or an explicitly approved feature root.

It never advances within the campaign.

A tuple-local closure head does not become the next compiler base.

### Review-ready baseline

`review_ready_baseline_sha` is the first head presented as implementation-complete and ready for review.

Its semantic-surface vector becomes the post-review ceiling.

New review waves do not reset that ceiling.

## Core laws

### Law 1 — no direct review-to-code edge

```text
review finding -> observation ledger
```

Never:

```text
review finding -> delivery patch
```

### Law 2 — no distinction without an observation

Every surviving behavioral distinction needs an accepted observation that can distinguish it.

A distinction may be:

```text
state class
authority
transition
protocol case
mode
error class
fallback
receipt/evidence kind
public operation
```

If no acceptance criterion or branch-liable counterexample distinguishes two states or paths, they must be quotiented, merged, or represented by one canonical rule.

### Law 3 — one PR-wide kernel

All review waves refine one campaign kernel.

Do not create a new kernel whose base is a prior closure head.

### Law 4 — implementation review is conformance review

Once the kernel is accepted, code review may report:

```text
nonconformance
missing proof
orphan realization surface
stale artifact state
```

A finding that changes accepted behavior crosses back into kernel review.

### Law 5 — post-review semantic conservation

After `review_ready_baseline_sha`:

```text
silent scope expansion = forbidden
hard semantic dimensions = nonincreasing
total semantic description = nonincreasing unless explicitly rebaselined
```

A larger model or realization requires an explicit scope/complexity expansion decision. It is not ordinary review remediation.

### Law 6 — no orphan code or proof

Every surviving code construct maps to a kernel element.

Every surviving proof action maps to a kernel law.

Targets:

```text
orphan_code_constructs = 0
wound_specific_tests = 0
unmapped_proof_actions = 0
```

## Entry modes

### Clean review

If the initial current-head review is clean:

- run current proof;
- sweep PR threads;
- emit tuple-bound closure;
- no kernel campaign is required.

### Isolated conformance correction

A one-realization fast path is allowed only when:

```text
exactly one branch-liable finding
kernel impact = existing_law_violation
no new behavioral distinction
no new helper/wrapper/state field/public symbol/fallback
semantic-surface vector is componentwise nonincreasing
proof extends an existing law family
```

It still emits MBKC-v1.

### Material review

Any of these requires the full kernel workflow:

```text
two or more branch-liable findings
same-cluster or same-family recurrence
new state/protocol/authority distinction
positive semantic-surface pressure
public/compatibility/fallback pressure
PR-thread reopening
review finding proposes new behavior
current families are named after local surfaces rather than governing laws
```

## Phase 1 — begin one PR-wide campaign

Preferred controller command:

```bash
resolve-c3 campaign begin \
  --root . \
  --pr <number> \
  --base auto \
  --baseline HEAD \
  --acceptance .ledger/c3/acceptance.json
```

The controller must record:

```text
campaign base
review-ready baseline
current delivery head
PR base/head tuple
acceptance contract
non-goals
proof bar
semantic-surface baseline
```

Delivery becomes controller-gated.

## Phase 2 — adjudicate findings as observations

Use `$review-adjudication`.

For each finding emit:

```yaml
review_observation:
  observation_id:
  artifact_state:
  observed_behavior:
  required_behavior:
  liability:
    introduced_by_current_diff |
    exposed_and_required_by_current_acceptance |
    preexisting_but_blocks_current_invariant |
    adjacent_preexisting |
    reviewer_preference |
    unknown
  kernel_impact:
    existing_law_violation |
    additional_witness |
    missing_semantic_distinction |
    no_kernel_impact |
    unknown
  acceptance_entailment:
    entailed |
    scope_expansion |
    unknown
  reproduction_or_proof:
  source_refs: []
  disposition:
    enter_kernel |
    attach_witness |
    validate_only |
    capture_followup |
    reject |
    blocked
```

Rules:

- `additional_witness` strengthens an existing family; it does not authorize another branch or test family.
- `missing_semantic_distinction + scope_expansion` returns to `$spec-pipeline` or explicit user authority.
- `adjacent_preexisting`, `reviewer_preference`, and `unknown` do not enter delivery scope.
- Reviewer repair proposals are non-authoritative hints.

## Phase 3 — compile the Minimum Behavioral Kernel

Use `$review-compression-compiler`.

The kernel artifact is:

```yaml
minimum_behavioral_kernel:
  kernel_version: MBK-v1
  campaign_id:
  campaign_base_sha:
  acceptance_contract:
  non_goals: []

  authorities:
    - authority_id:
      owns:
      publishes:
      may_transition: []

  carriers:
    - carrier_id:
      meaning:
      representation_independent: yes | no

  observations:
    - observation_id:
      source: acceptance | counterexample | compatibility
      observes:
      expected:
      proof_ref:

  equivalence_classes:
    - class_id:
      members_or_predicate:
      preserved_observations: []
      distinguished_from:
        - class_id:
          witness_observation_ids: []

  operations:
    - operation_id:
      inputs: []
      outputs: []
      authority_id:

  transitions:
    - transition_id:
      from_classes: []
      operation_id:
      to_classes: []
      guards: []
      emitted_observations: []

  laws:
    - law_id:
      statement:
      owner:
      observation_ids: []
      counterexample_family_ids: []
      proof_obligations: []

  non_laws: []
  forbidden_states_or_transitions: []

  counterexample_families:
    - family_id:
      governing_law_ids: []
      independent_witnesses: []
      subsumed_findings: []
      local_surfaces: []

  quotient:
    method:
      exact_partition_refinement |
      exact_bisimulation |
      witness_checked_manual |
      not_applicable
    optimality:
      exact |
      witnessed |
      unknown
    merged_distinctions: []
    unresolved_distinctions: []

  gate:
    all_branch_liabilities_covered: pass | fail
    every_distinction_has_witness: pass | fail
    every_family_maps_to_law: pass | fail
    no_local_surface_family_without_governing_law: pass | fail
    non_goals_preserved: pass | fail
    kernel_review_allowed: yes | no
```

Run the structural checker:

```bash
python3 codex/skills/resolve/tools/kernel_lint.py kernel.json
```

## Phase 4 — kernel review firewall

Review the kernel before reviewing code.

Required independent passes:

```text
behavioral_kernel_modeler
observational_equivalence_auditor
```

The kernel review asks:

```text
Are the authorities real?
Are observations sufficient?
Are two classes distinguishable by accepted behavior?
Are local findings compressed under the right governing law?
Does the kernel admit impossible states?
Does it omit valid behavior?
Does it silently expand scope?
```

Output:

```yaml
kernel_review:
  artifact_state:
  overdistinctions: []
  missing_distinctions: []
  authority_gaps: []
  impossible_states_admitted: []
  valid_states_omitted: []
  scope_expansions: []
  verdict:
    accepted |
    revise_kernel |
    return_to_spec |
    blocked
```

No implementation handoff until `accepted`.

## Phase 5 — select a realization design without writing code

Do not begin with several full implementations.

Generate 2–4 **design records**, not code candidates:

```text
subtractive/quotient realization
existing-owner canonical realization
representation/boundary realization
local-baseline control
```

Each design must contain:

```yaml
realization_design:
  design_id:
  route_class:
  kernel_elements_realized: []
  owner_map: []
  surfaces_to_retire: []
  predicted_new_surface: []
  negative_route_refs: []
  predicted_semantic_surface:
  proof_strategy:
  risks: []
```

For material review:

- require at least two structurally different designs;
- include a subtractive or quotient-oriented design when plausible;
- reject active negative-ledger routes;
- prefer the design with the smallest kernel-faithful predicted surface.

Do not implement multiple designs merely to satisfy ceremony.

## Phase 6 — compile one realization from the campaign base

The controller creates one realization worktree from `campaign_base_sha`.

Handoff:

```yaml
kernel_realization_handoff:
  campaign_id:
  campaign_base_sha:
  review_ready_baseline_sha:
  accepted_kernel_ref:
  selected_design:
  permitted_owners: []
  surfaces_to_retire: []
  forbidden_actions: []
  hard_surface_ceiling:
  proof_laws: []
  worktree:
```

Use `$fixed-point-driver` or `$accretive-implementer`.

Hard rules:

- no raw review comments as tasks;
- no new semantic distinction absent from the kernel;
- no incremental patch after a new observation;
- a new observation invalidates the realization;
- implementation starts again from campaign base;
- delivery remains frozen.

## Phase 7 — realization conformance and semantic accounting

Create:

```yaml
kernel_realization_map:
  map_version: KRM-v1
  code_constructs:
    - construct_id:
      path:
      symbol:
      kind:
      realizes:
        kernel_element_ids: []
      necessity_witness:
      status: required | retire | orphan

  proof_actions:
    - proof_id:
      kind:
        law |
        table |
        property |
        state_machine |
        generative |
        example |
        compile_fail
      proves_law_ids: []
      covers_observation_ids: []
      wound_specific: yes | no
      irreducibility_witness:

  semantic_surface:
    baseline:
    current:
    delta:
    hard_dimensions_nonincreasing: yes | no
    total_description_nonincreasing: yes | no

  gate:
    kernel_conformance: pass | fail
    orphan_code_constructs_zero: pass | fail
    wound_specific_tests_zero: pass | fail
    proof_laws_covered: pass | fail
    semantic_surface_conserved: pass | fail
```

Use:

```text
realization_conformance_auditor
proof_compression_auditor
semantic_surface_accountant
```

## Phase 8 — proof compression

Review-created tests are not exempt from code-growth control.

Preferred proof shapes:

```text
law/property test
table-driven counterexample family
state-machine model
generative test
shared fixture with parameterized witnesses
compile-fail family
```

A test that exists only because one reviewer found one wound must be:

```text
subsumed into a family proof
or
marked irreducible with a law-level witness
```

The final proof basis should prove kernel laws, not replay review chronology.

## Phase 9 — semantic-surface conservation gate

The canonical vector is grouped, not flattened into an easily gamed score.

```yaml
semantic_surface_vector:
  kernel:
    authorities:
    observable_state_classes:
    transitions:
    laws:
    protocol_cases:

  realization:
    truth_owners:
    public_symbols:
    state_fields:
    fallback_or_compatibility_paths:
    control_flow_branches:
    helpers_or_wrappers:
    files:
    ast_nodes:
    production_lines:

  proof:
    proof_laws:
    test_families:
    wound_specific_tests:
    fixtures:
    test_ast_nodes:
    test_lines:
```

### Hard dimensions

These may not increase after the review-ready baseline without explicit scope/complexity expansion:

```text
truth owners
public symbols
state dimensions
fallback/compatibility paths
protocol cases
wound-specific tests
```

### Total description

The combined kernel + realization + proof vector must be nonincreasing under the controller's documented comparison policy.

If correctness cannot fit under the ceiling:

```yaml
scope_complexity_decision:
  required: yes
  reason:
  options:
    - reduce scope
    - split PR
    - redesign kernel
    - explicitly approve rebaseline
```

Do not silently relabel growth as review remediation.

## Phase 10 — physically replace delivery from the campaign base realization

Only the controller may apply the selected realization.

Preferred command:

```bash
resolve-c3 delivery apply
```

Requirements:

- capture realization tree from campaign base;
- verify fingerprints and conformance;
- create a backup ref for current delivery head;
- replace the delivery worktree tree with the realization tree;
- preserve or rewrite history according to explicit campaign policy;
- verify final PR diff against campaign base;
- emit updated MBKC-v1.

No raw `git apply`, `git commit --amend`, or manual patch transplantation.

## Phase 11 — two holdouts

### Kernel holdout

Ask whether new review evidence requires a new accepted distinction.

### Conformance holdout

Ask whether delivery faithfully realizes the accepted kernel.

A holdout finding routes as:

```text
existing-law nonconformance -> discard realization, recompile from campaign base
additional witness -> attach to existing family, no new code
missing distinction entailed by acceptance -> revise kernel, discard realization
scope expansion -> return to spec/user authority
adjacent preexisting -> follow-up
preference -> reject
clean -> advance closure
```

Never patch the current realization in place.

## Closure states

Do not use unqualified `complete`.

```text
kernel_accepted
conformance_closed_for_tuple
terminal_closed
blocked
```

### `conformance_closed_for_tuple`

Must name:

```text
campaign base
head
kernel fingerprint
proof fingerprint
review backend/receipt
review horizon
reopen conditions
```

### `terminal_closed`

Requires:

```text
accepted MBK
whole-PR realization compiled from campaign base
semantic-surface conservation
zero orphan code
zero wound-specific tests
current proof
kernel holdout clean
conformance holdout clean
PR thread sweep current
controller physical commit/push current
```

## MBKC-v1

One durable certificate:

```yaml
minimum_behavioral_kernel_certificate:
  certificate_version: MBKC-v1
  certificate_id:
  stage:
    kernel_accepted |
    realization_verified |
    applied |
    final_certified |
    committed |
    pushed |
    conformance_closed_for_tuple |
    terminal_closed

  campaign:
    campaign_id:
    pr_number:
    campaign_base_sha:
    review_ready_baseline_sha:
    current_delivery_head:

  acceptance:
  observations:
  kernel:
  kernel_review:
  realization_designs:
  selected_design:
  realization_map:
  semantic_surface:
  proof_basis:
  negative_evidence:
  holdouts:
  delivery:
  closure_horizon:

  gate:
    kernel_allowed:
    realization_allowed:
    apply_allowed:
    commit_allowed:
    push_allowed:
    tuple_closure_allowed:
    terminal_closure_allowed:
```

Canonical location:

```text
.ledger/c3/mbkc.json
```

Run:

```bash
python3 codex/skills/resolve/tools/mbkc_gate.py .ledger/c3/mbkc.json
```

## Negative-ledger integration

Capture not only failed patches but failed semantic routes:

```text
overdistinguished kernel
wrong authority model
local-surface family that failed to close the governing law
proof-wound pattern
realization route
```

A failed local route should prevent future design records from reintroducing the same semantic distinction under a new helper name.

## Reporting

Final output:

```yaml
resolve_kernel_report:
  certificate_id:
  campaign_base:
  review_ready_baseline:
  raw_findings:
  independent_observations:
  counterexample_families:
  governing_laws:
  observable_state_classes:
  distinctions_merged:
  scope_expansions_rejected:
  realization_designs_considered:
  selected_design:
  surfaces_retired:
  orphan_code_constructs:
  proof_laws:
  wound_specific_tests:
  semantic_surface_delta:
  tuple_closure:
  terminal_closure:
  outcome:
```

Core metrics:

```text
raw findings / governing laws
local surfaces / observable distinctions
independent laws / proof families
accepted observations / total semantic description
```

## Hard rules

- Review may add observations, not implementation instructions.
- Campaign base never advances within a PR campaign.
- A tuple-local closure head never becomes the new optimization base.
- No distinction without an observation witness.
- No local-surface counterexample family without a governing law.
- No code review that silently changes the kernel.
- No realization from a prior closure head.
- No orphan code construct.
- No wound-specific test without irreducibility evidence.
- No post-baseline increase in hard semantic dimensions.
- No silent scope/complexity rebaseline.
- No manual delivery mutation during an active campaign.
- No unqualified `complete`.
- No terminal closure without MBKC-v1.

## Resources

- [minimum-behavioral-kernel.md](references/minimum-behavioral-kernel.md)
- [observational-equivalence.md](references/observational-equivalence.md)
- [kernel-review-firewall.md](references/kernel-review-firewall.md)
- [semantic-surface-conservation.md](references/semantic-surface-conservation.md)
- [realization-contract.md](references/realization-contract.md)
- [proof-compression.md](references/proof-compression.md)
- [closure-states.md](references/closure-states.md)
- [mbkc-schema.md](references/mbkc-schema.md)
- [controller-capabilities.md](references/controller-capabilities.md)
