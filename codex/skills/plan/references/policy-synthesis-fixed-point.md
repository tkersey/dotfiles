# Policy Synthesis Fixed Point

`$plan` must exhaustively refine the complete candidate before emission.

The candidate is the pair:

```text
C = (A, P)

A = architecture and abstraction state
P = execution policy
```

This preserves the strongest feature of the earlier `$plan`: repeated improvement
until no material architecture-policy improvement remains. It does **not** restore
public iteration ceremony.

Read [architectonic-policy-synthesis.md](architectonic-policy-synthesis.md) for the
Architectonic Thread, authority classes, factor dispositions, conceptual compression,
and double-category transport law.

## Sweep lenses

A complete sweep retains the existing nine identifiers in this order:

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

Each lens evaluates the whole `(A, P)` candidate:

- `source_fidelity` — preserve source-fixed architectonic seams, required
  observations, compatibility, non-goals, and prohibited organizations;
- `semantic_authority` — distinguish source-fixed, source-bounded, and plan-local
  architecture decisions without authority drift;
- `system_regime` — decide whether architecture is known, evidence-conditioned,
  stabilization-first, or genuinely underdetermined;
- `belief_and_observation` — bind architectonic choices and invalidators to facts,
  unknowns, observations, and freshness;
- `action_completeness` — realize every introduced factor, migrate every changed
  boundary, retire every displaced factor, and bind each action to the seam it
  serves;
- `policy_closure` — provide a lawful route or terminal for every architectural and
  execution observation outcome;
- `safety_and_rollback` — ensure rollback restores a coherent organization rather
  than merely old files;
- `proof_and_terminal_state` — prove laws, preservation, migration, retirement,
  falsifiers, and terminal predicates;
- `simplicity_and_actuation_readiness` — reject dominated factors, accidental
  distinctions, duplicate owners, bypasses, reconstruction paths, and needless
  semantic surface while keeping the plan realizable by an authorized consumer.

The final PSR-v1 suffix remains these nine identifiers in this exact order. No
second architectonic loop or receipt is introduced.

## Loop

```text
compile initial architecture-policy candidate
run lenses in order
if a lens finds material improvement:
  apply the minimal source-preserving improvement
  if architecture changed:
    transport the affected policy through the architectonic change
    preserve, revise, retire, or introduce actions by factor disposition
    record compatibility-square results and falsifiers
  restart from the earliest affected lens

if a lens finds a material source-authority gap:
  return_to_spec or return_to_grill

if a full sweep is clean:
  run independent fresh-eyes pass over architecture and policy

if fresh eyes finds material issue:
  apply or route it, then restart affected lenses

otherwise:
  convergence reached
```

An architecture change inside source-bounded or plan-local authority is a normal
refinement. Return to the source only when it contradicts source-fixed semantics,
scope, compatibility, authority, or proof bar.

## Accretive, not accumulative

The loop should be monotone in:

```text
explained obligations
evidenced decisions
preserved observations
excluded invalid states
proof strength
retired uncertainty
```

It need not be monotone in action count, factor count, owners, branches, files, or
policy prose. A later iteration may delete earlier actions and abstractions when a
stronger governing organization makes them unnecessary.

Governing law:

```text
accrete justification
ablate dominated surface
```

## Architectonic transport

When policy processes compose horizontally and architecture changes compose
vertically, compatibility squares witness that actions remain lawful across the
change. Horizontal pasting composes sequential actions. Vertical pasting composes
successive architectonic changes. Interchange requires
rearchitecting-then-replanning to agree with transporting the current plan through
the rearchitecture up to declared observations and equivalence.

Do not call one isolated compatibility check a double category when neither square
pasting nor interchange matters.

## No fixed cap

Do not stop because of an iteration count.

Stop only for:

```text
convergence
return_to_spec
return_to_grill
blocked
user stop
tool/safety limit
```

If forced to stop before convergence:

```text
improvements_exhausted = false
```

## Mandatory radical candidate

After the architecture-policy pair is apparently converged, generate the strongest
non-obvious candidate improvement to the governing organization, admitted domain,
representation, ownership, abstraction factorization, evidence strategy, or
execution policy.

The candidate is mandatory. Adoption is not mandatory.

Valid dispositions remain:

```text
adopt
reject
defer
return_to_spec
none
```

`return_to_spec` is reserved for contradiction with source-fixed authority. An
architectural improvement within source-bounded or plan-local authority may be
adopted, transported through the affected policy, and synthesized again.

A rejected candidate should explain the governing reason:

```text
source-expanding
unsafe
dominated
surface-increasing
not execution-relevant
worse than current architecture-policy pair
needs evidence outside the horizon
```

## PSR-v1 receipt

```yaml
policy_synthesis_receipt:
  receipt_version: PSR-v1
  plan_id:
  revision:
  source_digest:
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

`initial_policy_digest`, `final_policy_digest`, and every pass candidate digest bind
the complete EPG candidate, including architectonic seams, factor dispositions,
action bindings, transport, and square results. The receipt proves synthesis
occurred; it does not expose private reasoning or draft iteration logs.

## Final output policy

The final plan may summarize PSR-v1. It should not include:

```text
draft-by-draft logs
Iteration: N footers
rewrite-ratio self claims
fabricated no-op rows
mandatory architectural addition just to show creativity
```

## Readiness invariant

```text
policy ready
=
all consequential seams dispositioned
+ no dominated architectonic factor remains
+ actions realize and retire the declared factors
+ required architecture-policy squares commute or block honestly
+ complete clean nine-lens sweep
+ clean fresh-eyes pass
+ radical candidate evaluated
+ no unresolved blockers
+ source-current handoff
```
