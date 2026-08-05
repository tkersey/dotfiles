# Selective Historical Admission

Historical admission begins with read-only reconciliation. It does not scan and
admit every canonical row and it never writes compiled memory.

## Inputs

```text
owner-defined canonical Ledger projections
${CODEX_HOME:-$HOME/.codex}/memories/extensions/*/notes/*.md
${CODEX_HOME:-$HOME/.codex}/memories/extensions/synesthesia/resources/latest_synesthesia_digest.md
Phase 2 compiled-memory files
optional source-memory-eligibility/v1 decisions
```

## Procedure

1. Run the owning source definition's doctor and exact reconciliation-index
   projection.
2. Inventory immutable notes through `memory-note` and verify their normalized
   repository identity, source ID, kind, and writer fingerprint.
3. Check Phase 2 using exact canonical-record or note-ID provenance tokens.
   Unreadable Phase 2 files make visibility `unknown`; they do not prove lag.
4. Ask the source owner to classify only rows that remain
   `needs-source-review`. Record accepted decisions in a bounded
   `source-memory-eligibility/v1` input.
5. Rerun reconciliation. Only `eligible-unadmitted` rows are admission
   candidates; `stale-note` and `incomplete-projection` require diagnosis, not
   blind re-admission.
6. For each accepted candidate, use the source's exact `memory-note` projection
   or documented adapter and retain the writer proof.
7. Leave Phase 2 compilation to Phase 2.

## Admission gates

- Learnings: the source owner applies its transferability, counterfactual-cost,
  recurrence, explicit-user-authority, and future-utility gate.
- Negative Ledger: the source owner requires a current complete projection with
  witness, applicability, narrow exclusion, reopening criteria, and projection
  fingerprint.
- Synesthesia: the source owner requires explicit durable mapping or boundary
  authority, or repeated accepted operational use under its activation
  contract.

## Prohibitions

- Do not infer eligibility from status names, recency, note absence, or a
  reconciliation report.
- Do not treat substring mentions as Phase 2 provenance.
- Do not bind a note to a repository through a directory or repository
  basename.
- Do not mutate canonical stores, immutable notes, digests, or compiled memory
  inside reconciliation.
- Do not bulk-admit every row to eliminate a reported gap.
