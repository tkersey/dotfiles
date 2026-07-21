---
name: reduce
description: "Audit over-engineered codebases by factoring layers into live obligations, quotienting redundant distinctions, ablating unearned surface, and normalizing the survivors while preserving required behavior. Use when change latency or agent difficulty comes from frameworks, plugins, DI, codegen, task runners, config indirection, ORMs, GraphQL, monorepo/infra tooling, web stacks, or requests to remove layers. In Actuating composition, return one compact non-authoritative minimization challenge before Construction selection; use RC-v1 for standalone audits, migrations, or independently durable handoffs."
---

# Reduce

## Purpose

Act as the architecture **WINNOWING** reviewer. Find costly abstractions whose live obligation is unproven, expired, moved, duplicated, invalid, or outweighed by their change tax. Recommend lower-level normal forms while preserving essential truth.

The default standalone product is a decision package and `RC-v1`, not a patch.
Inside Actuating, return one compact challenge for the candidate version; the
Construction carries the adjudicated decision. Implement only when the user
explicitly asks.

## Doctrine

```text
WINNOWING
  = FACTORING
  -> QUOTIENTING
  -> ABLATIVE
  -> NORMALIZING

guard:
  REFINEMENT-PRESERVING
```

- **FACTORING**: decompose each layer into distinct obligations, owners, inputs, outputs, dependencies, observations, and recomposition roles.
- **QUOTIENTING**: collapse distinctions or layers no live observation can distinguish, after congruence checks.
- **ABLATIVE**: remove, collapse, privatize, slice, or decommission factors with no distinct live obligation.
- **NORMALIZING**: recompose retained factors around canonical owners and lower-level primitives.
- **REFINEMENT-PRESERVING**: preserve required behavior and obligations while allowing obsolete, invalid, duplicated, or unrequired behavior to disappear.

`ISOMORPHIC` and `OBSERVATIONALLY-EQUIVALENT` are stricter proof relations, not reduction objectives.

## Abstraction elevator

`reduce` descends. `universalist` climbs. They share an altitude map without
sharing selection authority.

Classify each move:

- `descend`: lower primitive preserves the live contract.
- `climb`: the system lacks essential shape; hand off to `universalist`.
- `hold`: value, public obligation, protocol risk, or proof weakness justifies the layer.
- `split`: remove incidental wrapper while preserving the essential invariant.
- `quotient`: collapse observationally indistinguishable factors.
- `ablate`: remove a discharged factor.
- `normalize`: recompose retained factors around one canonical owner.

In Actuating composition, `climb` reports an `essential-shape-gap` to
Actuating. It does not call Universalist, reopen a Construction, or begin a
recursive elevator loop. Actuating alone adjudicates the existing nomination,
requests a new candidate version, or blocks.

## When to use

Use for broad layer/tooling/framework tax, including:

- frameworks, plugins, decorators, middleware, DI/service locators, factories, adapters, reflection wiring;
- code generation, generated clients, schema/build generators, task runners, monorepo tooling, config inheritance;
- ORMs, GraphQL gateways, repository layers, event buses, workflow engines, queues, microservice boundaries;
- Helm/Kustomize/Terraform/Kubernetes/CI wrappers;
- web stacks where native platform primitives may replace framework/build layers;
- architectures where a simple change crosses many files, tools, generated artifacts, conventions, or hidden control flow.

Do not use for one local readability cleanup; route that to `complexity-mitigator`.

## Operating rules

1. Preserve required behavior unless explicit authority changes the contract.
2. Preserve essential truth: invariants, protocols, authorization, data integrity, auditability, public contracts, and external obligations.
3. Use repo-local evidence first.
4. Treat absent evidence as uncertainty, not permission to delete.
5. Prefer reversible cuts and staged migration.
6. Do not add tools to remove tools unless total complexity falls and the user accepts the trade.
7. If evidence is incomplete, mark the audit provisional and cap destructive verdicts at `hold`, `wrap`, `split`, or `validate-first`.
8. Separate reduction operator from preservation relation.
9. Every removed factor needs obligation discharge.
10. Every proposed normal form needs recomposition proof.

## Workflow

### 1. Build an altitude and boundary map

Identify layers at altitudes 0–5, lower primitives, public/wire/storage boundaries, proof surfaces, and any invariant each layer may carry.

### 2. Trace real paths

For each major abstraction, trace at least one real change/request/command path:

- entrypoint;
- factors/layers crossed;
- generated/configured behavior;
- runtime side effects;
- proof surfaces;
- where reasoning becomes expensive.

### 3. Factor by live obligation

For every candidate:

| factor | live obligation | owner | inputs/outputs | dependencies | observations | external commitment | recomposition role |
|---|---|---|---|---|---|---|---|

Use exactly one obligation status:

```text
live | moved | expired | duplicated | invalid | unknown
```

### 4. Measure tax and value

Record:

- edit, lookup, tool, hidden, and deploy hops;
- diff opacity and proof latency;
- coupling and lifecycle constraints;
- proven value;
- external obligation risk;
- confidence.

Keep value and obligation risk separate.

### 5. Find quotient candidates

Ask whether multiple factors differ only in implementation, naming, or historical layering.

Before quotienting:

- state the observation set;
- define the equivalence relation;
- test congruence across accepted operations/transitions;
- preserve every witnessed distinction.

### 6. Essential-abstraction check

Before replacement or deletion, check for product, coproduct, refinement/equalizer, pullback/agreement, supplied behavior/exponential, free construction, protocol, or external obligation.

If essential shape exists:

- reduce wrapper tax first;
- preserve or improve the invariant representation;
- hand off to `universalist` if missing shape is the real problem.

### 7. Score candidates

Use:

```text
T = change/agent tax
V = proven value
D = T - V
```

Also record:

```text
dominance = dominant | dominated | incomparable | unknown
```

A factor is `dominated` only when another route covers its live obligation with lower total semantic surface or stronger proof.

### 8. Select operator-level verdict

```text
keep
hold
factor
quotient
wrap
split
collapse
ablate
privatize
decommission
normalize
replace
validate-first
climb
```

### 9. Choose the output carrier

In Actuating composition, return exactly one compact challenge for the current
candidate version:

```text
Reduction Challenge
Candidate:
Disputable factors:
Verdict: minimal | dominated | incomparable | essential-shape-gap | blocked
Smaller admissible candidate:
Obligations preserved:
Recomposition proof or falsifier:
```

This view is supporting analysis, not an artifact or selection. Use
[reduction-certificate.md](references/reduction-certificate.md) only for a
standalone audit or migration, an explicitly requested certificate, or a
handoff that must remain independently durable outside the current Actuating
Construction.

For technical debt, default to `refinement-preserving`. Use `observationally-equivalent` only with an explicit observation set. Use `isomorphic` only with a witnessed reversible correspondence.

### 10. Migration plan

For each approved cut:

- first safe phase;
- allowed files/commands;
- proof signal;
- rollback;
- owner of unknowns;
- stop condition;
- recomposition check.

## Standalone output

1. Scope and assumptions
2. Altitude / boundary map
3. Evidence ledger
4. Factorization map
5. Tax/value/dominance table
6. Quotient candidates and congruence status
7. Essential-abstraction check
8. Prioritized winnowing decisions
9. Target normal form
10. Reduction Certificate when required by the output-carrier rule
11. Migration plan
12. Risks and unknowns
13. Winnowing Bottom Line

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

## Implementation mode

When explicitly asked to implement:

1. Hand the compact challenge, or `RC-v1` when independently required, to
   Actuating as supporting reasoning.
2. Mutate only after Actuating encodes the selected reduction in the current
   Construction and binds one exact operation to the current subject.
3. Implement exactly that one reduction seam at a time through
   `one-seam-operator` or `$actuating`.
4. Preserve the old surface until the selected proof relation passes, unless direct deletion is already proven safe.
5. Run recomposition audit before proceeding to another seam.
6. Stop on a new observation or lost obligation.

## Resources

- [reduction-certificate.md](references/reduction-certificate.md)
