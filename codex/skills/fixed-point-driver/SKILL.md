---
name: fixed-point-driver
description: "Realize one selected canonical normal form and prove it. Consume an accepted kernel and Reduction Certificate when present; implement only certified factors/operators, retire named surfaces, verify quotient/refinement conformance, audit recomposition, and return on any new observation or semantic distinction. Never invent a behavioral quotient during realization and never patch delivery directly."
metadata:
  version: "5.0.0"
---

# Fixed-Point Driver

## Mission

Reach:

```text
one canonical owner
no unresolved counterexample
no shadow truth
no unnecessary surface
current proof
proved recomposition
```

This skill realizes a selected normal form. It does not independently decide which behavioral distinctions are disposable.

## General mode

For a normal fixed-point task without a kernel handoff:

- identify the contract and canonical owner;
- use the smallest owned implementation;
- surface any reduction opportunity as a candidate;
- do not quotient behavior without an accepted observation model;
- close only when another full current-state pass yields no new material work.

## Reduction-certificate mode

Activate when the handoff contains:

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

Rules:

- Work only in the named realization worktree and permitted owners.
- Start from the campaign base.
- Implement the accepted kernel and RC-v1, not raw review findings.
- Add no behavioral distinction absent from the kernel.
- Apply only certified operators: factor, quotient, ablate, normalize.
- Retire superseded surfaces named by the certificate.
- Map every surviving construct to a retained factor/kernel element.
- Map every proof to a kernel law or preservation obligation.
- Do not overclaim `isomorphic`; respect the certificate’s preservation relation.
- Run recomposition audit before reporting valid.
- Stop on a new observation, failed congruence, lost obligation, or required scope expansion.
- Do not incrementally patch after a kernel change.
- Do not edit, commit, or push delivery outside the named realization surface.

## Realization procedure

1. Validate artifact state, campaign base, kernel ref, and RC-v1.
2. Confirm every selected operator has a proof path.
3. Implement one certified seam at a time.
4. Track:
   - factors realized;
   - quotient classes realized;
   - surfaces retired;
   - canonical owners;
   - semantic-surface delta.
5. Run kernel conformance and preservation checks.
6. Run `recomposition_auditor` or root-equivalent audit.
7. If a new observation appears, return to kernel review.
8. Report the current patch/result; do not self-authorize delivery commit/push.

## Output

```yaml
kernel_realization_result:
  campaign_id:
  design_id:
  artifact_state_id:
  realization_patch_ref:
  reduction_certificate_ref:
  kernel_conformance:
  quotient_conformance:
  refinement_conformance:
  preservation_relation:
  code_construct_map:
  factor_realization_map:
  surfaces_retired:
  retained_obligations_covered:
  removed_obligations_discharged:
  semantic_surface:
  proof_law_map:
  recomposition_audit_ref:
  normal_form_reached:
  new_observations: []
  result:
    valid |
    invalid |
    return_to_kernel |
    blocked
```

## Gate

`valid` requires:

```text
current artifact state
kernel conformance
quotient congruence
certificate-conformant ablation
preservation relation proved
every live obligation covered
every removed factor discharged
recomposition passed
no orphan surface
no new observation
```

## Hard rules

- Never invent a quotient during realization.
- Never use implementation convenience as evidence that distinctions are equivalent.
- Never delete a factor missing obligation discharge.
- Never claim isomorphism for a refinement-only contraction.
- Never report normal form without recomposition.
- Never continue after a new observation changes the kernel.

## Resources

- [reduction-certificate.md](references/reduction-certificate.md)
