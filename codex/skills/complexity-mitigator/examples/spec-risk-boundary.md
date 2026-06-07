# Example: Spec-Risk Boundary

## Input cue

> This legacy retry/payment code is ugly. Refactor it.

Code symptoms:
- awkward compatibility branches;
- unknown edge-case policy;
- behavior depends on external provider responses and historical fixtures.

## Expected `$complexity-mitigator` response shape

**Complexity preflight:** `primary=specification risk; secondary=conformity; confidence=medium`
- Hotspot: `retryPayment` - provider-status compatibility branches look incidental, but the edge-case policy is not settled.
- Smallest clarity cut: create an example matrix of provider status, prior attempt state, expected next action, and notification behavior.
- Do not change yet: retry/duplicate-charge policy and backwards-compatible provider mapping.
- Hand off: contract tests or fixture authoring before implementation.

## Why this matters

This is a success case for the skill even though no refactor is recommended. The output prevents syntax cleanup from erasing externally required behavior.
