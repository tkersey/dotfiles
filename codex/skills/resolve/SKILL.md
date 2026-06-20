---
name: resolve
description: "Resolve review findings by compiling a Minimum Behavioral Kernel and Reduction Certificate before compiling code. Factor obligations, quotient observationally indistinguishable distinctions, ablate discharged surfaces, normalize canonical owners, realize one selected design, prove recomposition, then push/close. Use for `$resolve`, branch review/fix/prove/push/PR closure, repeated findings, review-driven growth, behavioral quotienting, semantic-surface conservation, proof compression, or MBKC-v1. Not for one-shot review, PR creation, merge/land, or isolated implementation."
metadata:
  version: "7.0.0"
  activation_cost: high
  default_depth: full
---

# Resolve

## Mission

`$resolve` is the **Minimum Behavioral Kernel Reduction Compiler**.

```text
review observations
-> factorization
-> behavioral quotient
-> kernel normal form
-> ablative realization
-> recomposition proof
-> delivery closure
```

Review adds observations. Observations refine the kernel. The accepted kernel and Reduction Certificate replace review-driven patch accumulation.

## Doctrine

Operate in:

```text
FACTORING
-> QUOTIENTING
-> ABLATIVE
-> NORMALIZING
```

guarded by:

```text
REFINEMENT-PRESERVING
```

- **FACTORING** exposes live obligations, owners, dependencies, observations, and recomposition roles.
- **QUOTIENTING** collapses distinctions no accepted observation can detect.
- **ABLATIVE** retires factors whose obligation expired, moved, duplicated, became invalid, or is not required by acceptance.
- **NORMALIZING** selects one canonical owner and realization.
- **REFINEMENT-PRESERVING** keeps all required behavior while permitting obsolete, invalid, duplicated, or unrequired behavior to disappear.
- **ISOMORPHIC** is an optional stricter proof relation, never the reduction objective.

## Governing insight

Patch minimization is too late when the behavioral model is over-distinguished. Minimize in this order:

```text
1. accepted behavioral distinctions
2. implementation realization
3. proof realization
4. textual surface
```

A large implementation may be locally irreducible while realizing a needlessly large model.

## Controller requirement

The canonical controller remains:

```bash
resolve-c3
```

Before material work:

```bash
python3 codex/skills/resolve/tools/controller_preflight.py
```

Required capabilities remain:

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

If required delivery capabilities are unavailable, analysis, adjudication, kernel drafting, and Reduction Certificate creation are allowed; delivery mutation and closure are forbidden.

## Campaign identity

```yaml
review_campaign:
  campaign_id:
  pr_number:
  campaign_base_sha:
  review_ready_baseline_sha:
  current_delivery_head:
```

- `campaign_base_sha` never advances inside the campaign.
- `review_ready_baseline_sha` establishes the post-review semantic-surface ceiling.
- A tuple-local closure head is not the next compiler base.

## Core laws

### Law 1 — no direct review-to-code edge

```text
review finding -> review observation
```

Never:

```text
review finding -> delivery patch
```

### Law 2 — no distinction without an observation

Every surviving state class, authority, transition, protocol case, mode, error class, fallback, evidence kind, or public operation needs an accepted observation that can distinguish it.

If no accepted observation distinguishes two states or paths, they must be quotiented, merged, or represented by one canonical rule.

### Law 3 — no quotient without congruence

Every accepted operation, transition, and observation must respect the quotient classes. Failed or unknown congruence blocks realization.

### Law 4 — one PR-wide kernel

All review waves refine one campaign kernel. Do not create a new kernel whose base is a prior closure head.

### Law 5 — implementation review is conformance review

Once the kernel is accepted, code review may report:

```text
nonconformance
missing proof
orphan realization surface
stale artifact state
```

A finding that changes accepted behavior returns to kernel review.

### Law 6 — post-review semantic conservation

After `review_ready_baseline_sha`:

```text
silent scope expansion = forbidden
hard semantic dimensions = nonincreasing
total semantic description = nonincreasing unless explicitly rebaselined
```

### Law 7 — no orphan code or proof

Every surviving code construct maps to a kernel element. Every surviving proof action maps to a kernel law.

Targets:

```text
orphan_code_constructs = 0
wound_specific_tests = 0
unmapped_proof_actions = 0
```

### Law 8 — no ablation without discharge

Every removed factor must have an obligation status of `expired`, `moved`, `duplicated`, `invalid`, or `unrequired`, with evidence and a replacement owner when applicable.

### Law 9 — no normal form without recomposition

Every live obligation and required observation must be covered by the retained factors after quotienting and ablation.

## Entry modes

### Clean review

If current-head review is clean:

- run current proof;
- sweep PR threads;
- emit tuple-bound closure;
- do not manufacture a reduction campaign.

### Isolated conformance correction

Allowed only when:

```text
exactly one branch-liable finding
kernel impact = existing_law_violation
no new behavioral distinction
no new helper/wrapper/state field/public symbol/fallback
semantic-surface vector is componentwise nonincreasing
proof extends an existing law family
```

It still emits a compact MBKC-v1 and RC-v1.

### Material review

Use the full workflow when any apply:

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

## Workflow

1. Bind campaign base, baseline head, current head, PR, threads, and proof state.
2. Use `$review-adjudication` to turn review claims into current observations; never accept repair prose as implementation scope.
3. Use `$review-compression-compiler` or an equivalent root pass to produce MBK-v1.
4. Produce `RC-v1`:
   - factorization;
   - quotient relation and congruence witnesses;
   - retained distinction witnesses;
   - ablation dispositions;
   - target normal form;
   - preservation relation;
   - recomposition rule.
5. Review the kernel and Reduction Certificate, not prospective patches.
6. Select exactly one realization design.
7. Hand the accepted kernel and Reduction Certificate to `$fixed-point-driver`.
8. If realization reports a new observation, discard incremental patching and return to kernel review.
9. Run `recomposition_auditor` or root-equivalent recomposition audit.
10. Prove kernel conformance, reduction gates, current-head validation, and PR-thread disposition.
11. Commit/push only the selected delivery realization.
12. Close only when campaign, proof, PR, and recomposition receipts match the current head.

## Reduction block

```yaml
reduction:
  certificate_version: RC-v1
  factorization_ref:
  quotient_relation:
  quotient_congruence:
  merged_distinctions: []
  retained_distinctions: []
  ablated_surfaces: []
  target_normal_form_ref:
  preservation_relation:
    isomorphic |
    observationally-equivalent |
    refinement-preserving |
    intentional-contract-change
  recomposition_audit_ref:
```

Default to `refinement-preserving` for technical-debt reduction. Do not claim `isomorphic` merely because tests pass.

## Realization handoff

```yaml
kernel_realization_handoff:
  campaign_id:
  campaign_base_sha:
  accepted_kernel_ref:
  reduction_certificate_ref:
  selected_design:
  permitted_owners:
  surfaces_to_retire:
  retained_factor_map:
  quotient_relation_ref:
  preservation_relation:
  recomposition_rule:
  hard_surface_ceiling:
  proof_laws:
  worktree:
```

## Closure gate

```yaml
resolve_gate:
  campaign_state_current:
  all_branch_liabilities_covered:
  every_distinction_witnessed:
  quotient_is_congruent:
  every_removed_factor_accounted:
  every_live_obligation_covered:
  recomposition_proved:
  no_orphan_code_or_proof:
  semantic_surface_nonincreasing_or_authorized:
  current_head_validation_passed:
  PR_threads_swept:
  commit_push_current:
  closure_allowed:
```

## Hard rules

- Never turn a review finding directly into delivery code.
- Never preserve implementation distinctions without accepted observation witnesses.
- Never quotient without congruence.
- Never delete without obligation discharge.
- Never claim normal form without recomposition.
- Never claim isomorphism when the real relation is refinement.
- Never patch delivery incrementally after a kernel-changing observation.
- Never close against stale campaign, proof, thread, or Reduction Certificate state.

## Resources

- [reduction-certificate.md](references/reduction-certificate.md)
