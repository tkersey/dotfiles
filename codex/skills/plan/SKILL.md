---
name: plan
description: "Compile accepted intent or a `$spec-pipeline` PSC-v1 source contract into one source-bound, architecture-aware EPG-v1 execution policy with an immutable `plan_id`. Exhaustively refine architecture and policy together, then emit only a policy that passes the execution-policy compiler. Use for `$plan`, spec-to-execution lowering, adaptive probes, stabilization plans, or plan revision. Preserve source authority; never mutate implementation state, require another architecture or execution skill, or silently select an existing plan."
---

# Plan

## Mission

Compile accepted intent into one executable policy.

```text
source contract
-> architecture-policy synthesis
-> EPG-v1 source
-> execution-policy compiler
-> opaque compiled policy
```

The candidate is:

```text
C = (A, P)

A = architecture and abstraction state
P = execution policy
```

Architecture is not a prose review after actions are chosen. It is part of the
policy being compiled.

Keep the strongest old behavior:

```text
iterate until exhausted
```

Do not restore artifact ceremony:

```text
no public iteration logs
no synthesis receipt
no stored readiness gate
no separate execution handoff
no Plan-owned runtime state, decision, or transition receipt
```

`$plan` performs its own architectonic reasoning. It does not require another
architecture skill or any execution controller. A consumer may later compile this
EPG and use the resulting policy under its own authority; that relationship is
outside Plan.

## Accepted source contracts

`$plan` may start from:

```text
direct user-authorized execution objective
plan_source_contract / PSC-v1 from $spec-pipeline
revision request for an existing plan_id
```

A `$spec-pipeline` tail-call passes:

```yaml
plan_source_contract:
  contract_version: PSC-v1
  source_owner: spec-pipeline
  spec_id:
  implementation_spec:
  decision_packet:
  sgr_v2:
  proof_bar:
  non_goals: []
  target_branch:
  do_not_execute_before: []
```

The Architectonic Thread travels inside `implementation_spec` and
`decision_packet`; do not create a second architecture packet.

Fail closed when:

```text
source_owner != spec-pipeline
SGR-v2 missing
SGR-v2 mode not in {full, repair}
SGR-v2 status != complete
SGR-v2 lane != spec_to_plan
SGR-v2 gate.plan_allowed != yes
SGR-v2 execution_handoff.ready_for_plan != yes
SGR-v2 execution_handoff.next_owner != $plan
SGR-v2 auto_plan_handoff.eligible != yes
do_not_execute_before is non-empty
implementation_spec missing
proof_bar missing
target_branch missing
```

A semantic or source-fixed architectonic gap returns to `$spec-pipeline` or
`$grill-me`. Plan must not invent scope, non-goals, compatibility, proof bars, or
source-fixed architecture.

See [03-plan-source-contract.md](references/cli-specs/03-plan-source-contract.md).

## One artifact

When persistence is useful, Plan owns exactly one artifact:

```text
.ledger/plan/<plan-id>/policy.json
```

That file contains the canonical EPG-v1 source. Revisions replace the same policy
artifact under the same `plan_id`; repository history provides archival lineage.
They do not introduce another artifact family.

A human projection is generated on demand from EPG-v1. It is not authoritative and
need not be persisted. Runtime state, decisions, observations, and transition
receipts belong to the eventual consumer, not Plan.

Do not write new planning artifacts under `.step/`.

## Plan identity

Every policy carries:

```yaml
plan_identity:
  plan_id:
  alias:
  revision:
  source_digest:
  target_repository:
  target_branch:
```

`plan_id` is stable across revisions of one objective. A materially different
objective receives a new ID.

Do not select an existing plan merely because it is active or recent. Source digest
and objective identity participate in plan identity.

## Authority boundary

```text
accepted source or $spec-pipeline
  semantics, scope, non-goals, source-fixed architecture, compatibility, proof bar

$plan
  source-bounded and plan-local architecture,
  observations, guarded actions, proof, rollback,
  exhaustive refinement, and EPG compilation

policy consumer
  runtime state, observations, mutation authority, execution, and completion
```

Plan never grants mutation authority and never chooses a consumer.

Architectonic authority classes:

```text
source_fixed
  preserve or return to source authority

source_bounded
  improve only inside the declared observation, compatibility, scope, and proof
  envelope

plan_local
  preserve, restrict, strengthen, factor, quotient, ablate, normalize, or replace
  as needed to make the policy coherent
```

Return upstream only when a candidate contradicts source-fixed semantics or exceeds
a source-bounded envelope.

## Planning regimes

```text
deterministic
  compile known architecture and actions

adaptive
  compile probes and evidence-conditioned architecture

stabilization
  compile containment and observability before normal work
```

Reclassify when evidence shows the current regime is wrong.

## EPG-v1 source language

The authoritative policy includes:

```text
policy and plan identity
source and artifact state
terminal predicates and safety invariants
architectonic seams, authority, factors, laws, and falsifiers
facts, unknowns, and observable evidence
bounded actions bound to seams and factors
proof obligations and rollback
selection rules and progress potential
commitment horizon
architecture-policy transport
invalidators and radical-candidate disposition
```

Every mutation action predicts resources with:

```text
path:
symbol:
generated:
schema:
service:
repo:all
```

Unknown scope becomes `repo:all / exclusive`.

Read [execution-policy-graph.md](references/execution-policy-graph.md).

## Architectonic policy state

For every consequential seam:

1. classify authority as `source_fixed`, `source_bounded`, or `plan_local`;
2. record one architectural axis and one typed hole;
3. recover live obligations, observations, compatibility, effects, resources, and
   host capabilities;
4. state the ordinary repository-native candidate first;
5. compare preservation, admitted-domain restriction, representation or owner
   strengthening, and ablation or normalization;
6. classify factor obligations as `live`, `moved`, `expired`, `duplicated`,
   `invalid`, or `unknown`;
7. select, evidence-condition, or return an honest obstruction;
8. record the law, falsifier, residual obligations, and invalidators.

Every consequential action references the seams and factors it realizes, preserves,
or retires. Reject actions that assume an unnamed owner, reintroduce an ablated
factor, bypass a canonical owner, or depend on an unresolved architecture choice
without an observation-conditioned route.

Prefer conceptual compression: explain more obligations and observations with fewer
independent concepts, owners, exceptions, and reconstruction paths. Counts are
comparison evidence, not an objective.

Read
[architectonic-policy-synthesis.md](references/architectonic-policy-synthesis.md).

## Transport

When policy sequencing and architecture change are genuinely independent
compositional directions, record compatibility squares:

```text
A_before ---- action_before ----> B_before
   |                                  |
   | architecture change              | architecture change
   v                                  v
A_after  ----- action_after ---->  B_after
```

An adopted architecture change:

```text
identifies affected seams and factors
-> preserves unaffected actions
-> revises actions bound to changed factors
-> retires actions bound to retired factors
-> introduces realization and proof for new factors
-> records square results and falsifiers
-> restarts synthesis from the earliest affected lens
```

Do not claim double-category structure for an isolated compatibility check when no
horizontal and vertical pasting matters.

## Internal fixed point

Before emission, refine the complete `(A, P)` candidate with these lenses in order:

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

Rules:

- No fixed iteration cap.
- A material improvement restarts at the earliest affected lens.
- An architecture change transports affected policy before restart.
- A source-authority blocker routes to `return_to_spec`, `return_to_grill`, or
  `blocked`.
- Stop only after one complete zero-material-delta sweep.
- Run one independent fresh-eyes pass.
- Emit only the final EPG, not the draft history.

The loop is monotone in explained obligations, evidenced decisions, preserved
observations, excluded invalid states, proof strength, and retired uncertainty. It
need not be monotone in actions, factors, owners, branches, files, or prose.

Read [policy-synthesis-fixed-point.md](references/policy-synthesis-fixed-point.md).

## Radical candidate

After apparent convergence, generate the strongest non-obvious improvement to the
governing organization, admitted domain, representation, ownership, factorization,
evidence strategy, or policy.

Disposition it inside `EPG.challenge` as:

```text
adopt
reject
defer
return_to_spec
none
```

If adopted, transport the affected policy and restart synthesis. Creativity is
mandatory; architectural accretion is not.

## Compilation boundary

The source EPG is not executable.

```text
EPG-v1 JSON
-> parse
-> structural and architectonic validation
-> private normalization
-> opaque CompiledPolicy
```

Only `CompiledPolicy` may reach selection or transition. The private normalized form
is an in-memory compiler representation, not a second artifact.

Compile the candidate with:

```bash
seq execution-policy-compile --file <epg.json> --format json
```

When the EPG is not being persisted, stage it only in a temporary file for this
command and remove the file afterward. Accept only `compiled: true`; bind the
reported `policy_digest` to the emitted EPG. The command output is a compiler
result, not a Plan artifact. If this compiler command is unavailable, return an
obstruction rather than claiming the policy compiles.

Compilation success is the only machine claim Plan needs. Do not embed or persist:

```text
gate
handoff
policy_ready
downstream_runtime_ready
self-reported lens results
```

If the compiler rejects the EPG, revise the source at the reported owner boundary or
return the obstruction. Do not override the compiler with prose.

The compiler proves structural validity and that the private normalized policy is
executable by the runtime. It does not prove that a human-authored law is true or
that the architecture is semantically complete; the fixed-point and fresh-eyes
passes remain responsible for semantic adequacy.

## Revision

Revise when source, repository identity, observations, architecture, or proof
assumptions change.

```text
load current EPG
-> verify plan_id and source binding
-> change only affected architecture-policy state
-> transport affected actions
-> rerun fixed point and fresh eyes
-> compile
-> increment revision
```

The canonical digest identifies the complete revised EPG. Do not emit a separate
synthesis or revision artifact.

## Cross-plan relationships

Plan may propose, but not create, a qualified relationship:

```yaml
proposed_cross_plan_dependency:
  from:
  to:
  type:
  reason:
```

The consuming workspace decides whether to accept it. Do not flatten foreign work
into the current policy.

## Output

Emit one `<proposed_plan>` block containing:

```text
Plan Identity
Strategy and Source
Architecture and Abstraction
Belief, Unknowns, and Observations
Actions and Policy Branches
Proof, Rollback, and Terminals
Execution Policy Graph
```

`Execution Policy Graph` contains exactly one fenced JSON EPG-v1 object. The prose is
an on-demand projection of that object. Do not emit a receipt, gate, handoff, runtime
state, decision, or transition artifact.

If the user asks whether an existing plan is ready, compile its current EPG. On
success, say:

```text
Plan compiles.
```

That statement means the policy is executable by a compatible consumer. It does not
authorize execution.

## Hard rules

- EPG-v1 is Plan's only authoritative artifact.
- Every EPG has an immutable plan ID and current source digest.
- Require a complete current PSC-v1 when planning from `$spec-pipeline`.
- Never infer or name a downstream execution owner.
- Never merge separate objectives for convenience.
- Never create executable cross-plan edges.
- Never grant mutation authority.
- Unknown scope means exclusive scope.
- Exhaustive joint synthesis is mandatory before compilation.
- No fixed iteration cap.
- No public iteration history or convergence receipt.
- Mandatory radical candidate; optional adoption.
- Compilation, not self-certification, determines executability.
