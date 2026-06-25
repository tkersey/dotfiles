# Changelog

## 2.0.1 — 2026-06-25

- Made DIG-v2 `$grill-me` escalation a hard state transition via `gate.intent_route`.
- Required same-turn `$grill-me` activation and Codebase Doctrine hard-stop when `grill_required: yes`.
- Added validation and regression tests for soft-handoff failures.
- Updated `AGENTS.md`, runtime prompt, schema, examples, and docs to make the handoff assertive.

## 2.0.0 — 2026-06-25

- Added narrow root implicit routing and aligned interface metadata.
- Replaced DIG-v1/CDI-v1 hand projection with deterministic DIG-v2 -> CDI-v2 compilation.
- Replaced intake `primary_invariant` with correctness questions, priorities, and explicitly sourced hypotheses.
- Introduced CBD-v2 closed-graph validation.
- Added current/target/proposed/contradicted/retired doctrine status.
- Made repository root skills optional.
- Added evidence-bearing skill candidacy and trial status.
- Required canonical negative-ledger provenance for durable route exclusion.
- Added current proof execution receipts.
- Added distinct survey, refresh, portfolio, and audit artifacts.
- Added bounded specialist assignments and worker-specific packet authority.
- Added adaptive deep-mode fanout.
- Added CBSH-v2 source-doctrine and explicit-authorization validation.
- Added schemas, eval corpora, examples, migration guidance, and regression tests.
