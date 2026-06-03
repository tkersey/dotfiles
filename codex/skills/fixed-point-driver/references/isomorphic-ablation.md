# Isomorphic ablation

Use this reference when `$fixed-point-driver` is deciding whether a changeset has
reached Truth-Owner Ablative-Isomorphic Normal Form.

## One rule

Ablation is complete only when selected deletion/collapse/canonicalization routes
are behavior-preserving or explicitly gated as `validate-first`.

## Ablation Opportunity Score

```text
Ablation Score = (Surface Removed × Confidence × Ownership Clarity) / Risk
```

Surface Removed is semantic, not only LOC. Count retired public/private symbols,
branches, flags, wrappers, adapters, duplicate truth surfaces, state variants,
proof obligations, and compatibility scaffolds.

## Ablative Isomorphism Card

```md
| card id | surface | action | behavior preserved | public contract preserved | error semantics preserved | ordering/side effects preserved | clone classification | abstraction-ladder check | compatibility risk | proof signal | status |
|---|---|---|---|---|---|---|---|---|---|---|---|
```

`status` is `pass`, `validate-first`, `missing`, or `not-applicable`.

## Closure rule

Do not hand off to `verification-closure` with selected deletion, collapse, reuse,
or canonicalization work unless every selected route has a card with `status:
pass`, or the route is explicitly blocked as `validate-first` / `missing`.
