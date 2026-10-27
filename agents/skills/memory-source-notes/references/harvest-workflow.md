# Selective Historical Admission

Historical admission begins with read-only reconciliation. It does not scan and
admit every canonical row and it never writes compiled memory.

## Inputs

```text
owner-defined canonical Ledger projections
native-selected extension notes_dir/*.md
native-selected Synesthesia resources_dir/latest_synesthesia_digest.md
selected-version Phase 2 compiled-memory files
optional source-memory-eligibility/v1 decisions
```

## Procedure

1. Resolve the owner's canonical context and selected native memory layout.
   Run the definition-bound doctor and exact reconciliation-index projection
   using the same native selector; pin the memory home/version throughout.
2. Inventory immutable notes through `memory-note`. Match managed identities
   by `ledger-repository:<store_id>`. Historical scope correspondence requires
   the same source's exact native export fingerprint; do not infer aliases from
   a Git remote, basename, or shared canonical record ID.
3. Inspect the selected compiler artifacts for exact immutable note IDs. Report
   `note-id-observed`, `not-observed`, or `unknown`; a bare canonical ID does not
   prove admission provenance. Missing/unreadable artifacts are `unknown`.
   Literal absence does not prove compiler lag, rejection, or absence of use.
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
