# Human Projection

The default public plan is a reader-first decompilation of EPG-v1, not an IR dump.
EPG-v1 remains the sole canonical machine representation.

## Views

```text
human  default; reviewable plan without inline EPG JSON
json   exact machine-readable EPG without prose projection
both   human plan followed by the exact EPG
```

Bare and implicit invocation select `human`. Full JSON requires `--format json`,
`--format both`, or an unambiguous request for the complete EPG.

## Human view

Emit one `<proposed_plan>` block with:

```text
Summary
Governed Specification
Architecture Decisions
Implementation Sequence
Decision Points and Branches
Proof, Rollback, and Done-State
Plan Artifact
```

`direct` or `revise` may omit `Governed Specification` when accepted source or the
revision delta already exposes the same semantics. Omit `Decision Points and
Branches` when no live unknown or conditional route exists.

Rules:

- `Summary` states objective, chosen path, first implementation wave, and binary
  done-state.
- `Governed Specification` compactly exposes scope, non-goals, locked decisions,
  requirements, proof bar, and accountable open/deferred items.
- `Architecture Decisions` shows only consequential seams: authority, owner,
  incumbent-to-target change, law, falsifier, and factor disposition.
- `Implementation Sequence` orders actions by dependency rather than EPG field order.
  Each consequential action names its stable ID and outcome, dependencies, paths and
  symbols, intended change, proof, and material failure or rollback route.
- `Decision Points and Branches` renders `unknown -> observation -> branch` and
  distinguishes policy horizon from active commitment.
- `Proof, Rollback, and Done-State` groups evidence by obligation/terminal and states
  abort criteria, restoration proof, blocked routes, and exact completion predicate.
- `Plan Artifact` reports plan/policy identity, source and exact-input EPG digests,
  target tuple, transient or persisted location, and structural definition digest.
- Keep the plan reviewable in one pass. Remove duplication before implementation
  detail; omit empty arrays, nulls, settled bookkeeping, and field-by-field JSON prose.
- Do not expose iteration history, receipts, readiness gates, source packets,
  execution handoffs, runtime state, or the EPG body in `human`.

If the human view is not executable without reading the EPG, improve the projection
rather than inlining the IR.

## JSON views

`json` emits only `Execution Policy Graph`; `both` appends it after `Plan Artifact`.
The section contains exactly one fenced EPG object with two-space indentation, stable
schema order, one trailing newline, and no minified nested object or array. Validate
the exact fenced bytes and never include Ledger's validation-result JSON.

Report `Plan synthesized.` after synthesis and, after exact-byte validation,
`EPG structurally valid under <definition-id>@<definition-digest>.` Never convert
structural validity into semantic correctness, readiness, authority, or completion.
