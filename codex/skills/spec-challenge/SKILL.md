---
name: spec-challenge
description: "Run exactly one strongest project-specific invariant/adversarial challenge against a generated spec or plan, then decide whether to regenerate it. Use for `$spec-challenge`, A+ this plan, pressure-test the invariant, does this preserve X, single strongest critique, or after `$plan` before implementation."
---

# Spec Challenge

## Mission

Improve specs with one high-leverage critique, not endless review churn.

## Protocol

1. Identify the primary invariant.
2. Identify the spec section most likely to violate it.
3. State the single strongest challenge.
4. Classify the result:
   - `architecture_change_required`
   - `proof_change_required`
   - `scope_change_required`
   - `risk_mitigation_required`
   - `preference_only`
5. If required, rewrite only the affected sections or return to `$spec-gate` / `$grill-me`.

## Challenge bank

Choose one, or derive a sharper project-specific version:

- Does this create a second authority?
- Does this preserve zero-cost abstraction?
- Does this preserve public API compatibility?
- Does this prove runtime behavior rather than scaffolding?
- Does this preserve migration safety under dirty real-world state?
- Does this fail closed when dependencies are missing or stale?
- Does this make the impossible state unrepresentable?
- Does this have a rollback that works after partial deployment?
- Does this degrade observability exactly when debugging is needed?
- Does this prevent the implementer from making architectural choices mid-flight?

## Output

```text
SPEC_CHALLENGE
primary_invariant:
strongest_challenge:
affected_sections:
classification:
required_change:
regenerate_spec: yes|no
```

Do not run multiple independent critiques unless the user explicitly asks for a full review.
