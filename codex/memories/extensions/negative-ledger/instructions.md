# Negative Ledger Memory Source Adapter

Use this file only during Codex Phase 2 memory consolidation.

## Role

Compile selected negative-evidence projections into durable retrieval guidance.
`$negative-ledger` owns current route state; `$ledger` selects its canonical
personal store independently of Git. Managed identity is
`ledger-repository:<store_id>`. Preserve historical scopes and source-reference
bytes as recorded; do not infer scope from a directory basename or Git remote.

Extension intake is:

```text
extensions/negative-ledger/notes/*.md
```

A source note is an immutable snapshot of ledger truth for memory admission. It is never the blocking route gate and never replaces the canonical ledger.

Deploy this file as a regular copy at native
`memory-note path --extension negative-ledger --format json`'s
`instructions_path`. Read only that selected root. A `ledger_path` in the
payload names a canonical namespace relative to the selected native store;
it does not authorize reading a similarly named repository-local file.

## Primary Source

Process valid new/changed notes shown in `phase2_workspace_diff.md`.

Supported kinds:

```text
ledger-projection
ledger-status-transition
ledger-supersession
ledger-retraction
```

A valid active projection should have authority `ledger-cli` and an embedded
full canonical Negative Ledger projection snapshot.

## Required Projection Fields

```text
neg_id
record_version
ledger_path
projection_fingerprint
status
kind
route_or_model_id / route_id
cluster_id when relevant
artifact_state_id
hypothesis
attempted_change
observed_outcome
failure_class
source_refs
falsifying_evidence
exclusion_scope
exclusion_rule
applicability_conditions
reopening_criteria
confidence
next_search_hint
source_event_count
```

If an active event lacks witness, applicability, narrow exclusion, reopening criteria, or a full projection fingerprint, it cannot support an active compiled exclusion.

## Operation and Status Semantics

- `assert`: current projection;
- `confirm`: additional evidence without duplicate compiled guidance;
- `supersede`: a newer `NEG-*` or projection owns the route state;
- `retract`: remove support unless another live canonical source remains;
- `reopen`: old exclusion becomes a current proof obligation;
- `reject`: source event must not be promoted.

Only `active` may compile to a narrow route constraint. `accepted_risk`, `stale`, `reopened`, and `superseded` preserve history or proof obligations but do not block. `need-evidence`, `capture_candidate`, and `unknown` do not compile as exclusions.

Never edit/delete notes or the canonical ledger.

## Promotion Gate

Require narrow hypothesis, named attempted route, inspectable witness, observed outcome and failure class, precise scope/current applicability, narrow exclusion rule for active status, reopening criteria, meaningful future routing delta, canonical source reference, and projection fingerprint.

## Artifact Targeting

Follow the active compiler contract. V2 produces only compact
`memory_summary.md`; retain a useful retrieval route or narrowly scoped
reminder, not the full projection. Preserve the immutable note ID and stable
store identity when needed to locate support. Detailed witness, artifact,
applicability, exclusion, reopening, and fingerprint fields stay in source
notes and current canonical projections.

V1 may additionally permit `MEMORY.md` task groups or proven repeated
preflight procedures in `skills/*`. Do not create either under a v2 contract.
Choose `none` for incomplete, non-recurrent, weak, retracted, or superseded
material with no remaining routing value.

## Current Verification Rule

Compiled memory supplies a discovery cue. Before a runtime route decision,
use `$negative-ledger` to discover mechanism/component/invariant candidates in
the selected personal store, verify current artifact applicability and declared
identity, then use the exact current route gate. A similar route name, an old
active snapshot, or an unmatched compiled `NEG-*` ID cannot block a route.

## Cross-Extension Ownership

- general operating guardrail -> standing policy or native memory, not negative-ledger;
- broad learning without failed-hypothesis semantics -> learnings;
- sensory vocabulary -> synesthesia;
- witnessed route state, applicability, exclusion, reopening -> negative-ledger.

## Security and Hygiene

- no secrets or raw long logs;
- no arbitrary repo scans;
- no active exclusion from Chronicle alone;
- no blanket bans from one implementation;
- no direct source-ledger mutation;
- no direct compiled-memory edit outside Phase 2.
