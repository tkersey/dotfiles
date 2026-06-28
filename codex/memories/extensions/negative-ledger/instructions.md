# Negative Ledger Memory Source Adapter

Use this file only during Codex Phase 2 memory consolidation.

## Role

This extension compiles selected projections of repo-local negative-evidence ledgers into durable memory routing guidance.

Operational authority remains:

```text
<repo>/.ledger/negative-ledger/events.jsonl
```

Extension intake is:

```text
extensions/negative-ledger/notes/*.md
```

A source note is an immutable snapshot of ledger truth for memory admission. It is never the blocking route gate and never replaces the canonical ledger.

## Primary Source

Process valid new/changed notes shown in `phase2_workspace_diff.md`.

Supported kinds:

```text
ledger-projection
ledger-status-transition
ledger-supersession
ledger-retraction
```

A valid active projection should have authority `ledger-cli` and an embedded full `ledger export` snapshot.

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

Never edit/delete notes or the repo-local ledger.

## Promotion Gate

Require narrow hypothesis, named attempted route, inspectable witness, observed outcome and failure class, precise scope/current applicability, narrow exclusion rule for active status, reopening criteria, meaningful future routing delta, canonical source reference, and projection fingerprint.

## Artifact Targeting

- `memory_summary.md`: broad routing rules only.
- `MEMORY.md`: use task-group structure with `NEG-*`, ledger path, status, artifact state, failed hypothesis, exclusion/applicability/reopening fields, `source_note_ids`, and projection fingerprint.
- `skills/*`: only for repeated repo-specific preflight procedures.
- `none`: incomplete, non-recurrent, weak, retracted, or superseded material with no remaining routing value.

## Current Verification Rule

Compiled negative memory can guide where to look, but a normal runtime agent should still verify route state against the current repo-local ledger and artifact state before blocking work.

## Cross-Extension Ownership

- general operating guardrail -> harness;
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
