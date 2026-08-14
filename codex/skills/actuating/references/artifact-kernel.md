# Artifact Kernel Owner Map

The kernel has exactly four authoritative per-goal artifact families.

| Family | Semantic owner | Irreducible question |
|---|---|---|
| `goal-contract/v3` | accepted source through `$goal-contract` | What must be true, remain true, and is authorized? |
| `counterexample-set/v1` | `$review-fold` | What witnessed behavior falsifies a current Construction claim? |
| `construction-contract/v6` | `$actuating` using `$universalist` | Given the complete current Counterexample Theory, what semantic model and normalized realization should exist? |
| `actuating-evidence-event/v1` | the event body's domain owner | What happened and what was independently observed? |

The Goal Contract is the sole semantic-authority artifact. The Counterexample
Set is the sole classified-bug artifact. The Construction Contract is the sole
architecture-selection artifact. The Evidence Ledger is the sole mutable
per-goal truth.

## Ownership

- Goal shape and authority: `$goal-contract`.
- Finding classification, stable class identity, and within-Set quotienting:
  `$review-fold`.
- Cumulative Counterexample Theory, causal-basis derivation, semantic-novelty
  classification, candidate adjudication, normal-form selection, realization
  exactness, review credit, and closure: `$actuating`.
- Candidate semantic-model nomination and boundary lowering: `$universalist`.
- One bounded hypothesis-space escape on a live decision surface:
  `$metanoetic`.
- Factor quotienting, ablation, and recomposition challenge: `$reduce`.
- CAS attempt execution and owner receipts: CAS.
- Public effects and `SHIP-v1`, `SHIP-OBSERVATION-v1`, or
  `SHIP-ADOPTION-v1`: `$ship`.
- Closure receipt and human-readable closeout: `$actuating`.
- Canonicalization, structural validation, append integrity, replay, and
  requested projections: Ledger.

Review findings never select repairs. Supporting skills never select the
Construction. Ledger never interprets CAS or Ship, computes causal generators,
chooses a semantic model, grants mutation, or emits closure.

## Knowledge and realization law

Accepted knowledge is monotone:

```text
Counterexample Theory(n+1)
=
quotient(Counterexample Theory(n) + newly accepted stable classes)
```

Ordinary Counterexample Sets are source-local deltas. They classify only new,
recurring, or reclassified classes from the current source; the retained class
register preserves untouched classes and supplies the cumulative theory.
Explicit Goal carry-forward remains total because semantic authority changed.

Implementation is not monotone. A successor Construction may preserve, rewrite,
consolidate, or delete incumbent mechanisms. Review history and implementation
momentum grant no semantic authority.

The Construction factors through the cumulative Counterexample Theory, not the
ordered review trace. Duplicate witnesses, campaign partitioning, reviewer
identity, and finding arrival order must not change the selected normal form.

## Evidence law

Artifact bytes, verifier logs, tests, CAS receipts, and Ship receipts remain
owner-issued content-addressed attachments. Plans, local analyses,
and historical diff folds are discardable aids. The selected normal form,
causal basis, semantic model, realization bindings, proof obligations, and
retirements live in `construction-contract/v6`; no Review Path artifact or separate accretion disposition is added.

The Actuating subject is the deterministic SHA-256 identity of one clean Git
commit target: repository identity, commit OID, and tree OID. Dirty state is
provisional implementation state and never an Evidence subject. A subject
change invalidates subject-bound proof, publication, and review credit but does
not erase Goal, Construction, or Counterexample lineage.

The first review-entry subject remains fixed for forensic audit throughout one
closeout objective. It is not the semantic input to Construction selection; the
complete current Goal and Counterexample Theory are.

## Version cut

`construction-contract/v6` supersedes v1-v5 for new selection or mutation.
Earlier artifacts retain their original definitions as historical evidence but
cannot authorize another affected mutation. Start a fresh v6 goal-local
Evidence store; never replay or reinterpret v1-v5 Construction bytes under the
v6 definitions.

## Bankruptcy gate

Add no mandatory artifact unless it answers a new irreducible question, has an
owner and consumer, cannot be derived, prevents a named failure, replaces
surface, and includes retirement. This redesign adds no artifact family, event
kind, CLI command, mutable control state, review lens, or review attempt.
