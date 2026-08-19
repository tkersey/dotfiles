---
name: reduce
description: "Audit over-engineered codebases by factoring layers into live obligations, quotienting redundant distinctions, ablating unearned surface, and normalizing the survivors while preserving required behavior. Use when change latency or agent difficulty comes from frameworks, plugins, DI, codegen, task runners, config indirection, ORMs, GraphQL, monorepo or infrastructure tooling, web stacks, or requests to remove layers. In Actuating composition, return one compact non-authoritative minimization challenge before target-architecture selection; use RC-v1 only for standalone audits or independently durable handoffs."
---

# Reduce

## Purpose

Act as the architecture **WINNOWING** reviewer. Find abstractions whose live
obligation is unproved, expired, moved, duplicated, invalid, or outweighed by
their change tax. Recommend a smaller normal form while preserving essential
truth.

Inside Actuating, return one compact challenge for the current candidate. The
ephemeral Architecture Working Set carries Actuating's adjudication. Reduce
never selects architecture or grants mutation.

## Doctrine

```text
WINNOWING
  = FACTORING
  -> QUOTIENTING
  -> ABLATING
  -> NORMALIZING

guard:
  REFINEMENT-PRESERVING
```

- **Factoring** decomposes a layer into obligations, owners, inputs, outputs,
  dependencies, observations, and recomposition roles.
- **Quotienting** collapses distinctions no required observation can
  distinguish after congruence checks.
- **Ablating** removes, privatizes, collapses, or decommissions factors without a
  distinct live obligation.
- **Normalizing** recomposes the survivors around canonical owners and lower
  primitives.
- **Refinement-preserving** retains required behavior while allowing obsolete,
  duplicated, invalid, or unrequired behavior to disappear.

## Abstraction elevator

`$reduce` descends. `$universalist` climbs. They share an altitude map without
sharing selection authority.

```text
descend   lower primitive preserves the live contract
climb     essential shape is missing; report the gap to Actuating
hold      a live obligation or proof weakness justifies the layer
split     remove incidental wrapper while preserving the essential invariant
quotient  collapse observationally indistinguishable factors
ablate    remove a discharged factor
normalize recompose around one canonical owner
```

In Actuating composition, `climb` reports an `essential-shape-gap`. It does not
call Universalist or recursively reopen architecture. Actuating decides whether
to request another nomination or block.

## Operating rules

1. Preserve required behavior unless current authority changes it.
2. Preserve invariants, protocols, authorization, data integrity, auditability,
   public contracts, and external obligations.
3. Use repository evidence first.
4. Treat absent evidence as uncertainty, not deletion authority.
5. Prefer reversible cuts and staged migration.
6. Do not add tools to remove tools unless total complexity falls materially.
7. Every removed factor needs obligation discharge.
8. Every target normal form needs recomposition proof.
9. Keep value and obligation risk separate.
10. Do not turn the audit into another durable workflow unless independent
    durability is explicitly required outside the active Actuating run.

## Workflow

1. Map the relevant layers, lower primitives, public/wire/storage boundaries,
   proof surfaces, and invariants.
2. Trace at least one real request, change, or command through each major
   abstraction.
3. Factor each candidate by live obligation:

| factor | obligation | owner | inputs/outputs | observations | external commitment | recomposition role |
|---|---|---|---|---|---|---|

4. Classify each obligation `live`, `moved`, `expired`, `duplicated`, `invalid`,
   or `unknown`.
5. Measure edit, lookup, tool, deploy, hidden-control, and proof tax against
   evidenced value.
6. Test quotient candidates against an explicit observation set and congruence
   under accepted operations.
7. Check whether apparently removable shape is an essential product,
   refinement, agreement boundary, free construction, protocol, or external
   obligation.
8. Classify dominance as `dominant`, `dominated`, `incomparable`, or `unknown`.
9. Return one operator-level verdict:
   `keep`, `hold`, `factor`, `quotient`, `wrap`, `split`, `collapse`, `ablate`,
   `privatize`, `decommission`, `normalize`, `replace`, `validate-first`, or
   `climb`.

## Actuating composition

Return exactly:

```text
Reduction Challenge
Bound head:
Candidate:
Disputable factors:
Verdict: minimal | dominated | incomparable | essential-shape-gap | blocked
Smaller admissible candidate:
Obligations preserved:
Recomposition proof or falsifier:
```

This is supporting analysis, not an artifact or selection. Use
[reduction-certificate.md](references/reduction-certificate.md) only for a
standalone audit, explicitly requested certificate, or handoff that must remain
independently durable outside the active Actuating run.

## Implementation mode

When explicitly asked to implement:

1. Hand the Reduction Challenge to Actuating.
2. Actuating updates its ephemeral Architecture Working Set and binds it to the
   exact current Git head.
3. Implement one coherent reduction seam.
4. Preserve the old surface until the selected proof relation passes unless
   direct deletion is already proved safe.
5. Run recomposition and residue checks.
6. Stop when a new observation changes an obligation or invalidates the target.

No Ledger operation, Construction artifact, or one-operation protocol is
required.

## Standalone output

1. Scope and assumptions
2. Layer and boundary map
3. Evidence
4. Factorization map
5. Tax, value, and dominance
6. Quotient candidates
7. Essential-abstraction check
8. Winnowing decisions
9. Target normal form
10. Optional RC-v1 when independently required
11. Migration and rollback
12. Risks and unknowns

```text
Winnowing Bottom Line:
- factor:
- quotient:
- ablate:
- normalize:
- preserve because:
- proof relation:
- first safe move:
```
