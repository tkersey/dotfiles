# Human Projection

The default public plan is a reader-first execution projection of EPG-v1, not an
IR dump. EPG-v1 remains the sole canonical machine representation.

## Views

```text
human  default; self-contained execution plan without inline EPG JSON
json   raw machine-readable EPG only; no prose or Markdown fence
both   human plan followed by the exact EPG in a Markdown fence
```

Bare and implicit invocation select `human`. Full JSON requires `--format json`,
`--format both`, or an unambiguous request for the complete EPG.

## Execution completeness

The `human` view is not a summary or review aid. For `spec-to-plan`, it is the
complete implementation specification synthesized from the supplied candidate.
Given the target repository, a fresh implementation session must be able to choose,
order, realize, validate, roll back, and determine completion using only the emitted
`<proposed_plan>` block. It must not depend on the original candidate text, prior
conversation, private synthesis, or omitted EPG body.

This is semantic completeness, not field parity. Compression may remove schema
syntax, duplicate explanation, nulls, and settled bookkeeping, but never an
implementation-relevant requirement, constraint, compatibility obligation,
architectural decision, action, branch condition, proof obligation, abort criterion,
or terminal predicate. If that projection cannot be emitted honestly, block rather
than return a successful human plan.

Execution completeness grants no mutation authority and selects no consumer.

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

`direct` or `revise` may omit `Governed Specification` only when the emitted block
still contains every implementation-relevant semantic from the accepted source or
revision. Omit `Decision Points and Branches` when no live unknown or conditional
route exists.

Rules:

- `Summary` states objective, chosen path, first implementation wave, and binary
  done-state.
- `Governed Specification` exposes current state, scope, non-goals, locked decisions
  and defaults, requirements, compatibility and migration obligations, proof bar,
  and only non-blocking open or deferred items. A material unresolved judgment
  blocks or becomes an explicit observation-conditioned branch.
- `Architecture Decisions` shows only consequential seams: authority, owner,
  incumbent-to-target change, law, falsifier, and factor disposition.
- `Implementation Sequence` orders actions by dependency rather than EPG field order.
  Each consequential action names its stable ID and outcome, prerequisites and
  dependencies, exact paths and symbols, intended change and preserved invariants,
  required observations, proof command or exact verifier reference, and material
  failure or rollback route. Do not hide work behind broad verbs such as "update
  relevant files" or "handle edge cases."
- `Decision Points and Branches` renders
  `unknown -> exact observation -> outcome-conditioned route`, distinguishes policy
  horizon from active commitment, and leaves no material design choice implicit.
- `Proof, Rollback, and Done-State` groups evidence by obligation and terminal,
  states exact validation commands or repository-native verifier references, and
  names abort criteria, restoration proof, blocked routes, and the binary completion
  predicate.
- `Plan Artifact` reports plan and policy identity, source and exact-input EPG
  digests, target tuple, transient or persisted location, and structural definition
  digest. It is provenance, not an execution-time semantic dependency.
- Keep the plan executable and reviewable in one pass. Remove duplication before
  implementation detail; omit empty arrays, nulls, settled bookkeeping, and
  field-by-field JSON prose.
- Do not expose iteration history, receipts, readiness gates, source packets,
  execution handoffs, runtime state, or the EPG body in `human`.

Before emission, perform a fresh-session executability check: an implementation
owner unfamiliar with the original request must be able to execute the plan from
the block and repository alone. Any missing semantic returns to synthesis.

## JSON views

`json` emits only the raw EPG JSON document. `both` appends the EPG after `Plan
Artifact` inside exactly one Markdown fence. In either view, the validation input is
the exact JSON payload: for `both`, exclude the fence delimiters. Use two-space
indentation, stable schema order, one trailing newline, and no minified nested object
or array. Never include Ledger's validation-result JSON.

For `human` and `both`, report `Plan synthesized.` after synthesis and, after
exact-byte validation,
`EPG structurally valid under <definition-id>@<definition-digest>.` For `json`, emit
no status prose before or after the JSON document. Never convert structural validity
into semantic correctness, readiness, authority, or completion.
