# Artifact Kernel Owner Map

The kernel has four authoritative per-goal artifact families and no
compatibility peer state.

| Family | Semantic owner | Irreducible question |
|---|---|---|
| `goal-contract/v3` | accepted source through `$goal-contract` | What must be true, remain true, and is authorized? |
| `counterexample-set/v1` | `$review-fold` | What witnessed behavior falsifies the current Construction? |
| `construction-contract/v3` | `$actuating` using `$universalist` | What compared factorization realizes the laws, excludes Counterexamples, supersedes its predecessor, and retires residue? |
| `actuating-evidence-event/v1` | the event body's domain owner | What happened and what was independently observed? |

The Goal Contract is the sole semantic-authority artifact; the Counterexample Set is the sole classified-bug artifact; the Construction Contract is the sole architecture-selection artifact; the Evidence Ledger is the sole mutable per-goal truth.

## Downstream ownership

- Goal shape and authority: `$goal-contract`.
- Finding classification and quotienting: `$review-fold`.
- Construction, proof strategy, orchestration, Counterexample evaluation, and retirements: `$actuating`.
- Static Review Contract construction, CAS-evidence evaluation, review credit, topology, and convergence: `$actuating`.
- Semantic closure verdict and `actuating-closure-receipt/v1`: `$actuating`.
- CAS attempt execution and owner receipts: CAS.
- Public effects and `SHIP-v1`: `$ship`.
- Human terminal rendering: `$proof-patch`.
- Canonicalization, structural validation, append integrity, replay, and requested projections: Ledger.

Ledger does not execute repository changes, interpret CAS or Ship, compute review credit, select repairs or a next action, emit closure, or author its receipt. Generated Ledger tables may enumerate routes and shapes, never Actuating lifecycle, review, or closure law.

## Evidence law

Artifact bytes, verifier logs, tests, CAS receipts, and Ship receipts remain owner-issued content-addressed attachments. Plans, WorkGraphs, and Ledger views are discardable aids. The closure receipt is a semantic report bound to current inputs, not a fifth artifact family.

`actuating-subject-observation/v1` is a transient reproducible Git digest, not
an authoritative artifact family or Evidence event kind.

Every immutable replayable event envelope proves sequence and custody, not semantic truth; Actuating evaluates it with the current Goal, Construction, Counterexamples, and subject.

Construction v1 and v2 have no compatibility authority. Current tooling rejects
them without migration; a v3 workflow starts a fresh goal-local Evidence store
and ignores legacy data.

## Bankruptcy gate

Add no mandatory artifact unless it answers a new irreducible question, has an owner and consumer, cannot be derived, prevents a named failure, replaces surface, and includes retirement. Pure coordination artifacts are prohibited.
