---
name: algebra-driven-design
description: Apply Algebra-Driven Design (ADD) to derive architecture, codebase implementation, refactors, APIs, agentic workflows, tests, and reusable skills from domain carriers, operations, observations, algebraic laws, invariants, effects, and interpreters. Use for ADD, denotational design, combinator models, law-driven architecture, domain algebra, property-based testing, codebase modeling, event sourcing, workflow design, or agentic skill design.
license: MIT
compatibility: Markdown-only workflow. Optional scripts require Python 3.10+ and use only the standard library.
metadata:
  version: "1.0.0"
  author: "generated-by-chatgpt"
  purpose: "Deep ADD knowledge skill for architecture and implementation analysis"
---

# Algebra-Driven Design Skill

Use this skill to perform Algebra-Driven Design (ADD): discover the domain's values, operations, observations, and laws; use those laws to derive architecture, implementation boundaries, tests, refactors, and agentic workflows.

This skill is intentionally knowledge-rich. The main operating loop is here; the deep theory and application catalogs are in `references/` and should be loaded when needed.

## When to activate

Activate this skill when the user asks to:

- explain or apply Algebra-Driven Design, denotational design, combinator models, lawful abstractions, or algebraic modeling;
- design architecture from domain rules, invariants, business workflows, state machines, or event streams;
- refactor a codebase around domain operations, laws, commands, events, reducers, interfaces, ports, adapters, or interpreters;
- create law-based tests, property tests, trace tests, parity tests, or reference implementations;
- design an agentic workflow or skill from operations, tools, state, approvals, validation, and evaluation;
- determine whether an abstraction leaks, whether a set of operations is sufficient, or what tests prove correctness.

## Load the right references

Always keep the central ADD loop in working memory. Load deeper files based on task type:

- General ADD explanation or report: `references/add-knowledge-base.md` and `references/law-catalog.md`.
- Architecture design: `references/architecture-application.md`.
- Codebase implementation or refactor: `references/codebase-implementation.md`.
- Agentic workflows, agents, tools, or skills: `references/agentic-skill-application.md`.
- Worked examples or analogies: `references/examples.md`.
- Source provenance and bibliography: `references/source-notes.md`.
- Output templates: files in `assets/`.

Optional scripts:

- `scripts/classify_algebra.py`: classify operations/laws into likely algebraic structures.
- `scripts/generate_law_tests.py`: generate Python Hypothesis or TypeScript fast-check test skeletons.
- `scripts/validate_add_analysis.py`: check whether an ADD report contains required sections.
- `scripts/check_skill_structure.py`: validate this skill folder structure.

## Non-negotiable ADD posture

Do not start with classes, services, endpoints, frameworks, UI screens, database tables, or agent nodes. Start with the algebra:

1. What are the domain carriers?
2. What are the operations?
3. What observations define equality or acceptable behavior?
4. What laws must hold?
5. What laws explicitly do not hold?
6. What architecture follows from those laws?
7. What implementation follows from the architecture?
8. What tests execute the laws?

Treat laws as obligations. If a law is not true in the domain, do not force it. Record it as a non-law or conditional law.

## ADD operating loop

For every ADD task, run this loop.

### 1. Frame the system

Restate the user goal in domain language. Identify:

- the system boundary;
- the business outcome;
- the users or actors;
- the irreversible effects;
- the external observations that matter;
- the risks if an operation is wrong;
- whether the work is explanatory, architectural, implementation-oriented, or evaluative.

### 2. Identify carriers

A carrier is a domain value or state space operated on by the algebra.

Examples:

- `Cart`, `Order`, `Payment`, `Permission`, `Configuration`, `EventStream`, `Plan`, `EvidenceSet`, `Draft`, `ValidationResult`, `WorkflowState`.

For each carrier, write:

- name;
- meaning;
- valid states;
- invalid states;
- observations;
- lifecycle boundaries.

### 3. Identify operations

List primitive operations. Include arity and effect level.

Operation classes:

- constructors: create values;
- combinators: combine values of the same or related carriers;
- transformations: map one carrier into another;
- observations: query or render without changing meaning;
- commands: request an effect;
- events: record that an effect happened;
- interpreters: map abstract operations into concrete effects;
- validators: check laws, invariants, permissions, or preconditions.

For each operation, write a signature. Prefer pure signatures first, then separate effects:

```text
combine : A × A -> A
observe : A -> Observation
interpret : Program[A] × Environment -> Effect[Observation]
```

### 4. Define observations

Observation determines equality. Two different internal values are equivalent when all relevant observations are equivalent.

Examples:

- two carts are equal if they render the same line items and totals;
- two event streams are equivalent if they project to the same user-visible state under the same reducer;
- two report drafts are equivalent if they cite the same claims and satisfy the same validation rules;
- two plans are equivalent if their executable traces are equivalent under approved tools.

Always distinguish:

- structural equality: same representation;
- semantic equality: same observation;
- trace equality: same externally visible effects;
- policy equality: same allowed/blocked outcome;
- performance equality: same result under resource constraints.

### 5. Propose laws

Start with candidate laws, then test them against examples and counterexamples.

Common laws:

```text
Associativity:      (a <> b) <> c = a <> (b <> c)
Identity:           empty <> a = a; a <> empty = a
Commutativity:      a <> b = b <> a
Idempotency:        a <> a = a
Inverse:            undo(do(a)) = a
Annihilation:       zero <> a = zero
Distributivity:     f(a <> b) = f(a) <> f(b)
Fusion:             observe(transform(a)) = observe'(a)
Monotonicity:       a <= b implies f(a) <= f(b)
Closure:            op(a, b) remains in valid carrier A
```

For each law, record:

- statement;
- domain interpretation;
- assumptions/preconditions;
- counterexamples;
- architecture consequence;
- implementation consequence;
- test consequence.

### 6. Separate true laws from non-laws

Non-laws are as valuable as laws. They prevent bad abstractions.

Examples:

- payment capture is not generally commutative with refund;
- cancellation is not inverse of shipment once goods have left the warehouse;
- evidence accumulation may be commutative, but citation order in the final report may not be;
- `remove(add(cart,item),item) = cart` fails if quantities, discounts, inventory holds, or audit logs are observed.

Classify each candidate as:

```text
LAW          Holds unconditionally under chosen observations.
CONDITIONAL  Holds under stated preconditions.
NON-LAW      Does not hold; record counterexample.
POLICY LAW   Must hold because of governance, security, compliance, or product policy.
TEST LAW     Should be executable as property or trace test.
```

### 7. Derive architecture

Map laws into boundaries and runtime mechanisms.

Examples:

- associativity -> batching, chunking, streaming folds, parallel execution;
- identity -> empty/default objects and safe initialization;
- commutativity -> ordering-insensitive queues, reconciliation, distributed merges;
- idempotency -> idempotency keys, deduplication, unique constraints, retry safety;
- monotonicity -> append-only logs, projections, incremental computation;
- semilattice merge -> convergence under distributed updates;
- inverse -> undo stacks, reversible operations;
- non-invertibility -> compensating actions, approvals, audit trails;
- annihilator -> blocking guardrails such as deny, validation failure, missing approval;
- interpreter boundary -> ports/adapters/tools/services;
- observation equality -> API contracts and acceptance tests.

Architecture should be justified by laws, not by taste.

### 8. Derive implementation

Implementation sequence:

1. Define carriers as values.
2. Define operations as functions, methods, commands, events, or interfaces.
3. Define observations explicitly.
4. Build a reference implementation that is simple and obviously correct.
5. Build an optimized implementation only after the laws are executable.
6. Compare optimized behavior to the reference implementation through parity tests.
7. Add property tests, scenario tests, trace tests, and invariant checks.
8. Encode impossible states in types, schemas, or validators where possible.

Prefer this structure:

```text
Pure domain core:
  carriers, operations, laws, reducers, validators, normalizers

Effectful shell:
  persistence, HTTP, file I/O, tools, external APIs, email, queues, payments

Interpreters:
  map abstract operations to concrete effects

Tests:
  examples, counterexamples, properties, traces, parity checks
```

### 9. Produce the deliverable

Select the appropriate output shape.

#### ADD report

Use `assets/add-report-template.md`. Include:

- executive summary;
- domain frame;
- carriers;
- operations;
- observations;
- laws and non-laws;
- architecture implications;
- implementation implications;
- test strategy;
- risks and open questions;
- next actions.

#### Architecture proposal

Use `assets/adr-template.md`. Include:

- current forces;
- algebraic diagnosis;
- proposed boundaries;
- components and interfaces;
- effect/interpreter model;
- data/event model;
- runtime guarantees;
- migration plan;
- tradeoffs.

#### Codebase implementation plan

Use `assets/implementation-plan-template.md`. Include:

- target modules;
- carriers/data types;
- operation signatures;
- adapters/interpreters;
- reference implementation;
- optimized implementation;
- test plan;
- refactor sequence.

#### Agentic skill or workflow design

Use `references/agentic-skill-application.md`. Include:

- skill trigger;
- task algebra;
- workflow carriers;
- tool operations;
- validation laws;
- approval and safety laws;
- state/memory rules;
- scripts/resources;
- evals.

## Quality checklist

Before finalizing, verify:

- Carriers are named and scoped.
- Operations have signatures.
- Observations are explicit.
- Laws are stated as equations or precise rules.
- False laws are documented with counterexamples.
- Architecture decisions are tied to laws.
- Implementation steps are tied to architecture.
- Tests are derived from laws.
- Effects are separated from pure domain logic where possible.
- Destructive operations have approval or guard laws.
- The final answer includes uncertainty where laws depend on business assumptions.

## Common failure modes

Avoid these:

- using algebraic jargon without deriving architecture or code;
- claiming a law holds because it would be convenient;
- confusing representation equality with observation equality;
- building classes before identifying operations;
- treating every operation as pure when it has external effects;
- ignoring audit logs, time, identity, permissions, or irreversible effects;
- overfitting laws to examples instead of testing counterexamples;
- producing property tests without meaningful generators;
- optimizing before creating a simple reference implementation;
- putting safety only in prompts instead of executable guardrails.

## Minimal response skeleton

When unsure, answer in this shape:

```markdown
# Algebra-Driven Design Analysis

## 1. Domain frame

## 2. Carriers

## 3. Operations

## 4. Observations

## 5. Laws and non-laws

## 6. Architecture implications

## 7. Codebase implementation implications

## 8. Test strategy

## 9. Risks, assumptions, and next steps
```
