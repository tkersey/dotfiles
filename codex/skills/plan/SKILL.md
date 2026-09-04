---
name: plan
description: "Govern a candidate implementation specification and lower it into one source-bound, architecture-aware EPG-v1 plan. Bare `$plan` defaults to spec-to-plan: inspect evidence, adopt/repair/reconstruct the candidate spec, challenge and fresh-eyes it, then synthesize and structurally validate the plan. Use `$plan direct` only as an explicit bypass for accepted decision-complete intent, or `$plan revise` for an existing plan identity. Implicitly invoke for detailed implementation specifications, execution plans, migrations, proof/rollback planning, and plan revision; never seize direct implementation, debugging, review, factual explanation, or divergent option generation."
---

# Plan

## Mission

`$plan` owns the complete path from candidate intent to one canonical,
architecture-aware source plan.

Bare invocation means:

```text
candidate specification or objective
-> repository and source evidence
-> governed specification
-> architecture-policy synthesis
-> EPG-v1
-> Ledger structural validation
```

A supplied specification is candidate evidence, not trusted authority. A polished
candidate may make governance cheap, but never skips it. Specification and policy
synthesis are one continuous compiler; there is no inter-skill receipt, source
packet, lane, handoff, or tail-call.

The joint candidate is:

```text
C = (S, A0, delta_A, P)

S       = governed specification and source authority
A0      = specification-owned architecture and abstraction state
delta_A = source-bounded or plan-local architectonic refinement
P       = execution policy
```

Plan never mutates implementation state, grants execution authority, selects a
consumer, or authors runtime facts.

## Public modes

Choose exactly one:

```text
spec-to-plan   default for bare $plan
direct         explicit bypass for accepted decision-complete intent
revise         update an existing plan identity
```

### Default: `spec-to-plan`

Bare `$plan` always governs the supplied candidate specification. When only an
objective is supplied, construct the smallest evidence-grounded candidate first.
Then disposition it:

```text
adopt        decision-complete and source-consistent
repair       sound direction with bounded invalid or incomplete sections
reconstruct  unsound authority, factorization, scope, or proof basis
block        unavailable judgment or authority prevents an honest specification
```

Even `adopt` runs the strongest invariant challenge and specification fresh-eyes
pass. Do not infer `direct` because a candidate appears complete.

### Explicit: `direct`

Select only for literal `$plan direct`. Bind the supplied accepted objective as
source authority and synthesize EPG-v1 without the full specification front end. A
semantic, scope, compatibility, proof-bar, or source-fixed architectonic gap still
blocks; direct mode cannot invent authority.

### `revise`

Select for `$plan revise` or an unambiguous request to revise an existing `plan_id`.
Preserve that ID, reconsider the earliest affected specification or policy phase,
transport affected actions, and emit a new revision. A different objective receives
a different ID.

Inside `spec-to-plan`, `full` is the default specification operation. Explicit
`gate-only` and `challenge-only` requests stop after the bounded inspection;
`repair` changes only implicated sections and downstream derivations. Explicit
`spec only` or `stop after specification` is an output boundary, not another mode.

## Activation boundary

Implicitly invoke when the primary result is a detailed implementation
specification, execution plan, migration/rollout plan, proof-and-rollback plan, or
revision of an existing plan.

Do not seize direct implementation, debugging, code/PR review, factual explanation,
architecture archaeology without planning intent, divergent option generation, or
mixed plan-and-implement work where planning is only an internal execution stage.
The execution owner may use Plan internally without discarding requested execution.

## Authority boundary

```text
user and inspected source
  objective, required behavior, hard constraints, user judgments

specification governance
  evidence, scope, non-goals, locked decisions, source-fixed architecture,
  compatibility, proof bar, migration/rollback, implementation specification

policy synthesis
  source-bounded and plan-local refinement, observations, guarded actions,
  proof, rollback, terminals, exhaustive refinement, EPG emission

policy consumer
  runtime state, mutation authority, execution, and completion
```

Structural validation grants neither semantic authority nor readiness.

## Default compiler

### 1. Research first

Inspect code, docs, candidate specs, prior plans, tests, tickets, logs, schemas,
configuration, diagrams, history, and supplied reports before asking questions. For
consequential architecture, inspect real representation, construction, composition,
interpretation, ownership, validation, migration, proof, and bypass paths. Do not
accept current files or layers as the semantic factorization without evidence.

Ask only for unavailable user judgment, private constraints, irreversible approval,
or authority conflicts that artifacts cannot resolve.

### 2. Govern the specification

Run:

```text
Evidence Brief
-> bounded judgment acquisition or No-Grill Justification
-> anti-drift check
-> Architectonic Thread
-> decision-complete implementation specification
-> semantic readiness condition
-> one strongest invariant challenge
-> specification fresh-eyes pass
```

Read [specification-governance.md](references/specification-governance.md). For a
consequential seam, read
[architectonic-specification.md](references/architectonic-specification.md). Then
read [specification-challenge.md](references/specification-challenge.md) and
[specification-fresh-eyes.md](references/specification-fresh-eyes.md).

A governed specification contains, in order:

1. Objective
2. Context / Current State
3. Locked Decisions
4. Scope
5. Non-Goals
6. Requirements
7. Architecture and Abstraction
8. Design / Implementation Approach
9. Dependency-Ordered Implementation Sequence
10. Requirement-Owner-Enforcement-Proof Traceability
11. Proof Commands
12. Risks and Edge Cases
13. Rollback / Abort Criteria
14. Binary Done-State
15. Open / Deferred Items

Every consequential requirement derives through:

```text
requirement -> owner -> factor -> enforcement -> implementation -> proof -> invalidator
```

The sequence remains specification-level. Do not duplicate EPG actions, branches,
or waves. No consequential seam may remain without a lawful disposition; an
obstructed seam blocks synthesis.

### 3. Lower directly into policy

When governance is complete, continue without a packet or owner transfer:

```text
source_fixed          -> source_fixed
source_bounded        -> source_bounded
specification_local   -> plan_local
```

The governed specification remains visible in the human projection, while EPG-v1
is the sole authoritative planning artifact. If policy synthesis exposes a
source-fixed contradiction, restart the earliest affected internal specification
phase and regenerate downstream policy. EPG `return_to_spec` requests a future
`$plan revise` that restarts this phase; it is not a skill handoff.

### 4. Synthesize architecture and policy

Choose a planning regime:

```text
deterministic  compile known architecture and actions
adaptive       compile probes and evidence-conditioned architecture
stabilization  compile containment and observability first
```

For every consequential seam:

1. classify authority as `source_fixed`, `source_bounded`, or `plan_local`;
2. record one axis and one typed hole;
3. recover obligations, observations, compatibility, effects, resources, and host
   capabilities;
4. state the ordinary repository-native candidate first;
5. compare preservation, admitted-domain restriction, owner/representation
   strengthening, and ablation/normalization;
6. disposition every factor and record law, falsifier, residuals, and invalidators;
7. bind every consequential action to the seams and factors it realizes, preserves,
   migrates, or retires.

Use `architectonic.mode = not_required` only for work inside an unchanged exact
boundary. Otherwise use `explicit`; reject unnamed owners, reintroduced ablated
factors, canonical-owner bypasses, and unresolved architecture without an
observation-conditioned route.

Read [architectonic-policy-synthesis.md](references/architectonic-policy-synthesis.md),
[execution-policy-graph.md](references/execution-policy-graph.md), and
[action-contract.md](references/action-contract.md).

### 5. Refine to a fixed point

Refine `(S, A0, delta_A, P)` through:

```text
source_fidelity
semantic_authority
system_regime
belief_and_observation
action_completeness
policy_closure
safety_and_rollback
proof_and_terminal_state
simplicity_and_compilability
```

No fixed iteration cap. A material delta restarts at the earliest affected lens; an
architecture change transports affected policy first. Stop only after one complete
zero-material-delta sweep, one independent policy fresh-eyes pass, and one private
radical candidate concerning organization, admitted domain, representation,
ownership, factorization, evidence, or policy.

Creativity is mandatory; architectural accretion is not. Read
[policy-synthesis-fixed-point.md](references/policy-synthesis-fixed-point.md) and
[fresh-eyes-press-pass.md](references/fresh-eyes-press-pass.md).

## Identity, artifact, and validation

Every EPG binds immutable `plan_id`, revision, source refs/digest, locked decisions,
target repository/branch, and inspected artifact state. Source binding is provenance,
not runtime currentness. Read [source-binding.md](references/source-binding.md).

When persistence is useful, the sole authoritative artifact is:

```text
.ledger/plan/<plan-id>/policy.json
```

Do not write it directly. Load `$ledger`, complete `$ledger ensure`, resolve the
installed definitions, and use `plan-policy-document` create/revise operations. Read
[artifact-root.md](references/artifact-root.md).

Validate the exact non-persisted EPG with:

```bash
plan_definition_root="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/plan/definitions/ledger")"
ledger validate \
  --definition "$plan_definition_root/execution-policy-graph.json" \
  --input policy=<epg.json> \
  --format json
```

Accept only a valid `ledger-validation-result/v1` for
`plan/execution-policy-graph` with the exact input and definition digests and
`ledger-artifact-abi/v1`. Persisted create/revise must return the corresponding
valid `plan/plan-policy-document` transaction result.

Output view never changes the EPG. In `human`, validate the staged EPG and report its
input digest without reproducing its body. In `json` or `both`, validate the exact
pretty-printed bytes emitted. Never validate one serialization and emit another.

Ledger rejection may repair structural encoding only; it cannot expand authority,
select semantics, or authorize execution. Never persist a governance gate, handoff,
`policy_ready`, runtime readiness, or synthesis history.

## Revision

```text
project current EPG and revision
-> verify plan_id and source binding
-> reconsider earliest affected specification or policy phase
-> transport affected actions
-> rerun fixed point, radical candidate, and fresh eyes
-> validate exact revised EPG
-> increment revision
-> transact against exact prior revision
```

Do not create a separate revision artifact.

## Output

Select output independently from `spec-to-plan`, `direct`, or `revise`:

```text
--format human  default; self-contained execution plan without inline EPG JSON
--format json   exact EPG only
--format both   human plan followed by the exact EPG
```

Bare `$plan` followed by candidate specification text selects `spec-to-plan` with
`human` output; implicit planning does the same. Full JSON requires an explicit
format selector or unambiguous request for the complete machine-readable EPG.

For `spec-to-plan`, the human view is the complete execution source synthesized from
the supplied candidate, not a summary of an inaccessible EPG. Given the target
repository, a fresh implementation session must be able to realize, prove, roll back,
and determine completion from the `<proposed_plan>` block alone. It must not require
the original candidate text, prior conversation, private synthesis, or omitted EPG
body. Compression may remove representation noise only; preserve every
implementation-relevant semantic. If this cannot be emitted honestly, block rather
than return a successful plan. This completeness grants no mutation authority and
selects no consumer.

Emit one `<proposed_plan>` block. The human view uses:

```text
Summary
Governed Specification
Architecture Decisions
Implementation Sequence
Decision Points and Branches
Proof, Rollback, and Done-State
Plan Artifact
```

The summary names objective, chosen path, first wave, and binary done-state. The
governed specification preserves all required behavior, constraints, compatibility,
and proof authority. The implementation sequence is dependency ordered and makes
each action executable from exact targets, prerequisites, intended change,
observations, proof, and material failure route. Every material judgment is decided
or bound to an exact observation-conditioned branch; any open or deferred item that
affects the done-state blocks synthesis. `Plan Artifact` reports identity, source
and EPG digests, target, persistence status/path, and structural definition digest.
The artifact is provenance, not an execution-time semantic dependency. Read
[human-projection.md](references/human-projection.md).

`json` contains only `Execution Policy Graph`; `both` appends it. Emitted JSON uses
two-space indentation and never minifies nested objects or arrays.

After synthesis say `Plan synthesized.` After exact-byte validation also say
`EPG structurally valid under <definition-id>@<definition-digest>.`

## Hard rules

- Bare `$plan` means governed spec-to-plan.
- `direct` is explicit and never inferred from apparent completeness.
- Bare `$plan` followed by candidate specification text emits self-contained
  `human` spec-to-plan.
- Full EPG JSON is explicit.
- The human plan is executable from its block and target repository without hidden
  context or the omitted EPG.
- A supplied specification is candidate evidence, not trusted authority.
- Specification and policy synthesis are one compiler, not a handoff.
- EPG-v1 is Plan's sole authoritative artifact.
- Never grant mutation authority, select a consumer, or author runtime currentness.
- Never merge separate objectives for convenience.
- Unknown scope means exclusive scope.
- Exhaustive joint synthesis has no fixed iteration cap or public history.
- Mandatory radical candidate; optional adoption.
- Ledger validity is structural evidence, not semantic correctness or readiness.
