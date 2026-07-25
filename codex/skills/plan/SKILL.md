---
name: plan
description: "Compile accepted intent or a `$spec-pipeline` PSC-v1 source contract into a source-bound architecture-aware execution policy and immutable `plan_id`, then exhaustively refine the joint architecture-policy candidate to a fixed point before a consumer-neutral execution handoff. Use for `$plan`, spec-to-execution lowering, adaptive probes, stabilization plans, or plan revision. Preserve source authority; never mutate the repository, require another architecture skill, or silently select an existing plan."
---

# Plan

## Mission

Compile accepted intent into an architecture-aware execution policy, then refine the
joint architecture-policy candidate until no material improvement remains.

```text
source contract
-> source acceptance
-> plan identity
-> architectonic seams
-> belief/unknowns
-> guarded actions
-> proof and rollback
-> joint architecture-policy fixed point
-> execution policy
-> consumer-neutral execution handoff
```

The best old `$plan` behavior remains mandatory:

```text
iterate until exhausted
```

The candidate being improved is:

```text
C = (A, P)

A = architecture and abstraction state
P = execution policy
```

The bad old artifact ceremony is not restored:

```text
no public iteration footers
no self-reported rewrite ratios
no synthetic round logs as readiness proof
```

This skill performs its own architectonic reasoning. It does not require
`$universalist`, `$reduce`, or `$actuating`. Those skills remain independently usable
when selected by another workflow.

Before the first native Ledger command in this workflow, load `$ledger` and complete
`$ledger ensure`. After readiness, invoke `ledger` directly; native artifact
operations own their results and failure reporting.

## Accepted source contracts

`$plan` may start from one of:

```text
direct user-authorized execution objective
plan_source_contract / PSC-v1 from $spec-pipeline
revision request for an existing plan_id
```

A `$spec-pipeline` tail-call must pass:

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
`decision_packet`; no second architecture handoff artifact is required.

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
`$grill-me`. `$plan` must not repair missing semantics by inventing scope,
non-goals, compatibility, proof bar, or source-fixed architecture.

See [03-plan-source-contract.md](references/cli-specs/03-plan-source-contract.md).

## Artifact root

All persisted planning artifacts use:

```text
.ledger/plan/<plan-id>/
```

Recommended:

```text
.ledger/plan/<plan-id>/policy.json
.ledger/plan/<plan-id>/projection.md
.ledger/plan/<plan-id>/synthesis-receipt.json
.ledger/plan/<plan-id>/revisions/
```

Do not write new planning artifacts under `.step/`.

## Plan identity

Every plan has:

```yaml
plan_identity:
  plan_id:
  alias:
  revision:
  source_digest:
  target_repository:
  target_branch:
  target_execution_owner:
    kind: actuating | executor | human | other | none
    identifier:
```

`plan_id` is stable across revisions of one objective. A materially different
objective receives a new plan ID.

Do not choose an existing plan merely because it is active or recently used. PSC
source digest and objective identity participate in plan identity selection.

A target execution owner is optional until handoff. Naming `$actuating` as a
consumer when explicitly selected does not make `$plan` depend on it.

## Authority boundary

```text
accepted source or $spec-pipeline
  semantics, scope, non-goals, source-fixed architecture, compatibility, proof bar

$plan
  source-bounded and plan-local architecture and abstraction,
  execution policy, evidence gates, bounded actions, rollback, plan identity,
  exhaustive joint architecture-policy refinement

downstream execution owner
  execution authority, mutation, live evidence evaluation, and completion
```

Architectonic authority classes:

```text
source_fixed
  preserve or return to source authority

source_bounded
  select and improve only inside the declared observation, compatibility,
  authority, scope, and proof envelope

plan_local
  preserve, restrict, strengthen, factor, quotient, ablate, normalize, or replace
  as needed to make the execution policy coherent
```

An architecture change is not automatically a semantic change. Return upstream only
when it contradicts source-fixed authority or exceeds a source-bounded envelope.

## Planning regimes

```text
deterministic
  compile known architecture and actions

adaptive
  compile probes, evidence-conditioned architecture, and guarded decision routes

stabilization
  compile containment and observability before normal work or architecture change
```

Regime classification is revisited during synthesis. If a lens proves the chosen
regime is wrong, revise the architecture-policy pair or return to source authority.

## Execution policy

The authoritative plan artifact should identify:

```text
policy ID/revision
plan ID
source and artifact state
terminal predicates
safety invariants
architectonic seams and authority
incumbent, ordinary, selected, and evidence-conditioned organizations
factor obligations and dispositions
architecture laws, falsifiers, residuals, and invalidators
facts and unknowns
observable evidence
bounded actions bound to seams and factors
resource predictions
proof obligations
rollback
policy rules
progress potential
commitment horizon
architecture-policy transport
consumer-neutral handoff
```

Every mutation action predicts resources using this grammar:

```text
path:
symbol:
generated:
schema:
service:
repo:all
```

Unknown scope becomes `repo:all / exclusive`.

## Architectonic policy state

Architecture and abstraction are state over which policy synthesis converges, not a
prose review after actions have already been chosen.

Read
[architectonic-policy-synthesis.md](references/architectonic-policy-synthesis.md)
and [execution-policy-graph.md](references/execution-policy-graph.md).

For every consequential seam:

1. classify authority as `source_fixed`, `source_bounded`, or `plan_local`;
2. record one architectural axis and one typed hole;
3. recover live obligations, required observations, incumbent factors, owners,
   compatibility, effects, resources, and host capabilities;
4. state the ordinary repository-native candidate first;
5. compare realization preservation, admitted-domain restriction,
   representation/owner strengthening, and ablation/normalization;
6. classify each factor obligation as `live`, `moved`, `expired`, `duplicated`,
   `invalid`, or `unknown`;
7. factor, quotient, ablate, normalize, preserve, or introduce only with a
   recomposition and proof account;
8. choose `selected`, `evidence_conditioned`, `underdetermined`, or `obstructed`;
9. record law, falsifier, residual obligations, and invalidators.

Every consequential action references the architectonic seams and factors it
realizes, migrates, preserves, or retires. An action is incomplete when it assumes
an unnamed representation or owner, reintroduces an ablated factor, bypasses a
canonical owner, or depends on an unresolved architectural choice without an
observation-conditioned route.

Prefer conceptual compression: explain more live obligations and observations with
fewer independent concepts, owners, exceptions, and reconstruction paths. Counts are
comparison evidence, not a scalar optimization objective.

## Architectonic transport and double-category coherence

Use two-dimensional composition when policy processes and architecture changes form
two genuinely different compositional directions:

```text
horizontal arrows
  policy actions and their sequencing

vertical arrows
  architecture, representation, ownership, migration, and abstraction changes

squares
  compatibility witnesses transporting actions across those changes
```

When an architecture change is adopted:

```text
identify affected seams and factors
-> preserve actions bound only to preserved factors
-> revise actions bound to changed factors
-> retire actions bound to retired factors
-> introduce realization and proof for introduced factors
-> record square results and falsifiers
-> restart synthesis from the earliest affected lens
```

Horizontal pasting composes sequential actions. Vertical pasting composes successive
architectonic changes. Interchange requires rearchitecting-then-replanning to agree
with transporting the current plan through the rearchitecture up to declared
observations and equivalence.

Do not claim double-category structure for one isolated compatibility check when no
horizontal and vertical square pasting matters.

## Policy synthesis fixed point

Before emitting a plan, run the existing internal exhaustive refinement loop over
the complete `(A, P)` candidate.

Read [policy-synthesis-fixed-point.md](references/policy-synthesis-fixed-point.md).

A complete sweep retains these nine identifiers in exact order:

```text
source_fidelity
semantic_authority
system_regime
belief_and_observation
action_completeness
policy_closure
safety_and_rollback
proof_and_terminal_state
simplicity_and_actuation_readiness
```

Each lens is lifted over architecture and policy:

- source fidelity preserves source-fixed architectonic seams and prohibited shapes;
- semantic authority distinguishes source-fixed, source-bounded, and plan-local
  decisions;
- system regime classifies known, evidence-conditioned, stabilization-first, and
  underdetermined architecture;
- belief and observation bind choices and invalidators to evidence;
- action completeness realizes introduced factors, migrates changed boundaries, and
  retires displaced factors;
- policy closure routes every architectural and execution outcome;
- safety and rollback restore a coherent organization, not merely old files;
- proof and terminal state cover laws, preservation, migration, retirement, and
  falsifiers;
- simplicity and actuation readiness reject dominated factors, duplicate truth,
  needless owners, bypasses, and semantic-surface growth while preserving
  realizability by an authorized consumer.

Rules:

- No fixed iteration cap.
- A material improvement restarts the sweep from the earliest affected lens.
- An adopted architecture change transports affected policy before restart.
- A material source-authority blocker routes to `return_to_spec`,
  `return_to_grill`, or `blocked`.
- Stop only after one complete zero-material-delta nine-lens sweep.
- Then run an independent fresh-eyes pass over architecture and policy.
- Emit only the final plan, not draft history.

The loop is accretive in justification, observation preservation, excluded invalid
states, proof strength, and retired uncertainty. It need not be monotone in actions,
factors, owners, branches, files, or prose.

```text
accrete justification
ablate dominated surface
```

## Mandatory radical candidate

Before finalization, run one radical creativity pass.

Question:

```text
What is the strongest non-obvious change to the governing organization, admitted
domain, representation, ownership, abstraction factorization, evidence strategy,
or execution policy that improves correctness, conceptual compression, proof, and
realizability without exceeding source authority?
```

The pass must produce a candidate or explicitly say `none`.

Then classify the candidate:

```text
adopt
  improves architecture or execution inside source authority and minimality

reject
  dominated, unsafe, unnecessary, source-expanding, or surface-increasing

defer
  promising but outside the current execution horizon; record trigger

return_to_spec
  contradicts source-fixed semantics, scope, architecture, compatibility,
  authority, or proof bar

none
  no non-obvious candidate survived generation
```

Creativity is mandatory. Architectural or policy accretion is not.

If adopted, transport affected policy, apply the minimal improvement, and restart
from the earliest affected lens. Never add content merely because finalization is
near. A rejected radical candidate is a successful creativity pass when the
rejection is evidence-based.

## Policy synthesis receipt

Emit or persist one compact `PSR-v1` receipt:

```yaml
policy_synthesis_receipt:
  receipt_version: PSR-v1
  plan_id:
  revision:
  source_digest:
  source_contract:
    kind: direct | PSC-v1 | revision
    source_owner:
    spec_id:
    sgr_digest:
  initial_policy_digest:
  final_policy_digest:
  passes:
    - pass_id:
      lens:
      candidate_digest_before:
      candidate_digest_after:
      findings: []
      material_changes: []
      disposition:
        changed |
        clean |
        blocked |
        return_to_spec |
        return_to_grill
  radical_candidate:
    candidate:
    disposition:
      adopt |
      reject |
      defer |
      return_to_spec |
      none
    reason:
    affected_refs: []
  convergence:
    complete_clean_sweep:
    independent_press_pass_clean:
    unresolved_errors:
    untreated_material_risks:
    improvements_exhausted:
```

Every digest binds the complete EPG candidate, including architectonic seams,
factor dispositions, action bindings, transport, and square results. The receipt
proves synthesis happened; it does not expose private reasoning.

Its final nine passes remain one ordered, zero-material-delta sweep across the
required identifiers. Earlier changed passes may precede that clean suffix.

The final `<proposed_plan>` should include a concise `Policy Synthesis Receipt`
section or a reference to the persisted receipt.

Validate:

```bash
ledger validate policy-synthesis-receipt \
  --input .ledger/plan/<plan-id>/synthesis-receipt.json
```

See [05-policy-synthesis-receipt.md](references/cli-specs/05-policy-synthesis-receipt.md).

## Execution handoff

The handoff records:

```yaml
execution_handoff:
  plan_id:
  policy_ref:
  policy_digest:
  synthesis_receipt_ref:
  synthesis_receipt_digest:
  target_repository:
  target_branch:
  consumer:
  compatible_consumers: []
  proposed_resources: []
  required_authority:
  required_evidence: []
  mutation_allowed: no
```

`$plan` never emits mutation authority. The handoff is consumer-neutral. When the
user selects `$actuating`, name it as a compatible or selected consumer; otherwise
handoff to the authorized executor, workflow, or human without inventing one.

## Cross-plan relationships

A plan may propose, but not create, cross-plan relations:

```yaml
proposed_cross_plan_dependency:
  from:
  to:
  type:
  reason:
```

`$plan` may only propose the relation. A downstream controller or workspace must
accept or reject it before execution.

Do not flatten another plan's tasks into the current plan merely to express a
dependency.

## Readiness

A plan is ready for a downstream execution owner when:

```text
source current
plan ID stable
all consequential architectonic seams dispositioned
source-fixed architecture preserved
no dominated factor remains
terminal conditions testable
every consequential action bound to seams and factors
every mutation action has resource predictions
unknowns and evidence-conditioned architecture are gated
migration and retirement complete
required architecture-policy squares commute or block honestly
proof/rollback complete
no semantic drift
target branch explicit
joint architecture-policy fixed point reached
radical candidate evaluated
independent press pass clean
consumer-neutral handoff complete
```

Readiness does not mean execution is authorized.

Execution still requires:

```text
current accepted source and execution authority
current subject or external target identity
an authorized consumer-selected in-scope operation
current evidence before continuation
consumer-owned evaluation and completion judgment
```

A plan may support `$actuating`, another workflow, a coding agent, a human executor,
or an external controller. None is inferred solely from plan readiness.

Policy selectors, checkpoints, transition receivers, and human-plan linters are not
execution owners. Ledger may materialize or validate requested artifacts but never
controls repository execution.

## Output

When emitting a plan, include one `<proposed_plan>` block with:

```text
Plan Identity
Source and Terminal Contract
Architecture and Abstraction
Policy State and Unknowns
Actions and Resource Predictions
Decision/Observation Rules
Proof, Rollback, and Terminal States
Policy Delta and Architectonic Transport
Policy Synthesis Receipt
Execution Handoff
```

Do not include internal iteration logs.

The architecture section should show consequential seams, authority, ordinary and
selected or conditioned organizations, factor dispositions, laws, falsifiers,
residuals, invalidators, and action bindings. Transport should show preserved,
revised, retired, and introduced actions plus square results.

The synthesis receipt should summarize the fixed point in compact form:

```text
nine lenses swept over architecture and policy
material architecture and policy changes accepted
surface ablated or normalized
radical candidate disposition
clean sweep result
fresh-eyes result
remaining blockers
```

## Fast readiness response

When the user asks only whether an existing plan is ready:

- inspect source currentness;
- inspect architectonic seams, authority, factors, and action bindings;
- inspect policy structure and transport;
- confirm PSR-v1 convergence over the architecture-policy pair;
- confirm radical candidate disposition;
- confirm consumer-neutral execution handoff readiness.

If all pass and no revision is requested, reply exactly:

```text
Plan is ready.
```

Do not use self-attested readiness without PSR/source evidence.

## Hard rules

- Persist only under `.ledger/plan/`.
- Every plan has an explicit immutable plan ID.
- Require a complete, current PSC-v1 before planning from `$spec-pipeline`.
- Direct planning remains legal from accepted user-authorized intent.
- Architecture and abstraction are fixed-point state, not a detached prose review.
- Preserve source-fixed seams; refine source-bounded and plan-local seams only inside
  their authority.
- Bind every consequential action to the seams and factors it realizes or retires.
- Transport policy through architecture changes; do not append around a superseded
  organization.
- Accrete justification and proof; ablate dominated surface.
- Do not require `$universalist`, `$reduce`, or `$actuating`.
- Never infer a target execution owner beyond the emitted handoff.
- Never merge separate objectives into one plan for convenience.
- Never create executable cross-plan edges.
- Never grant mutation authority.
- Unknown scope means exclusive scope.
- Exhaustive joint architecture-policy synthesis is mandatory before emission.
- No fixed iteration cap.
- Do not expose full internal iteration logs.
- Mandatory radical creativity candidate; optional adoption.
- No arbitrary addition after convergence.
