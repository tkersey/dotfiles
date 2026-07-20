# Artifact Kernel Owner Map

The kernel has four authoritative per-goal artifact families and no
compatibility peer state.

| Family | Semantic owner | Irreducible question |
|---|---|---|
| `goal-contract/v3` | accepted source through `$goal-contract` | What must be true, remain true, and is authorized? |
| `counterexample-set/v1` | `$review-fold` | What witnessed behavior falsifies the current Construction? |
| `construction-contract/v1` | `$actuating` using `$universalist` | What structure realizes the laws, excludes Counterexamples, and retires residue? |
| `actuating-evidence-event/v1` | the event body's domain owner | What happened and what was independently observed? |

The Goal Contract is the sole semantic-authority artifact. The Counterexample
Set is the sole classified-bug artifact. The Construction Contract is the sole
architecture-selection artifact. The Evidence Ledger is the sole mutable
per-goal truth.

## Downstream ownership

- Goal shape and authority: `$goal-contract`.
- Finding classification and quotienting: `$review-fold`.
- Construction, proof strategy, orchestration, Counterexample evaluation, and
  retirements: `$actuating`.
- Static Review Contract construction, CAS-evidence evaluation, review credit,
  topology, and convergence: `$actuating`.
- Semantic closure verdict and `actuating-closure-receipt/v1`: `$actuating`.
- CAS attempt execution and owner receipts: CAS.
- Public effects and `SHIP-v1`: `$ship`.
- Human terminal rendering: `$proof-patch`.
- Canonicalization, structural validation, append integrity, replay, and
  requested projections: Ledger.

Ledger does not execute repository changes, dispatch or semantically interpret
CAS, compute review credit, interpret Ship, select repairs, choose the next
action, emit a semantic closure verdict, or author the closure receipt. A
generated Ledger table may enumerate command routes and accepted artifact or
event shapes; it cannot contain Actuating's lifecycle, review, or closure law.

## Evidence law

Artifact bytes, verifier logs, test reports, CAS receipts, and Ship receipts
may be content-addressed attachments referenced by events. They remain
owner-issued evidence. Plans, WorkGraphs, and Ledger `state` or `project` views
are discardable structural aids. The Actuating closure receipt is a semantic
report whose authority and freshness come from its bound inputs, not a fifth
artifact family.

Every persisted event is immutable and replayable. Its envelope proves
sequence and custody, not the truth of its semantic claim. Actuating evaluates
current events with the Goal, Construction, Counterexamples, and live subject.

## Bankruptcy gate

Add no mandatory artifact unless it answers a new irreducible question, has a
named semantic owner and consumer, cannot be derived, prevents a named failure,
replaces existing surface, and includes retirement. An artifact whose only
purpose is coordinating other artifacts is prohibited.
