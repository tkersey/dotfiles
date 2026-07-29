# Policy Synthesis Fixed Point

`$plan` must exhaustively refine the complete candidate before emission.

The candidate is:

```text
C = (A0, delta_A, P)

A0      = source-owned architecture and abstraction state
delta_A = source-bounded or explicitly plan-local architectonic refinement
P       = execution policy
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
simplicity_and_compilability
```

Each lens evaluates the whole `(A0, delta_A, P)` candidate:

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
- `simplicity_and_compilability` — reject dominated factors, accidental
  distinctions, duplicate owners, bypasses, reconstruction paths, and needless
  semantic surface while keeping the policy structurally executable.

These identifiers are an internal synthesis order, not a persisted pass log.

## Loop

```text
synthesize initial architecture-policy candidate
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

## Final output policy

The final Plan output is an on-demand projection plus one EPG. It should not include:

```text
draft-by-draft logs
Iteration: N footers
rewrite-ratio self claims
fabricated no-op rows
mandatory architectural addition just to show creativity
synthesis receipt
readiness gate
execution handoff
```

## Emission and structural validation

```text
plan synthesized
=
all consequential seams dispositioned
+ no dominated architectonic factor remains
+ actions realize and retire the declared factors
+ any admitted architecture-policy squares commute or block honestly
+ complete clean nine-lens sweep
+ clean fresh-eyes pass
+ radical candidate evaluated
+ no unresolved blockers
```

These terms are private synthesis discipline, not machine-certified history. The
resulting EPG is the complete Plan truth surface.

Ledger must additionally establish:

```text
EPG structurally valid under <definition-id>@<definition-digest>
=
exact emitted EPG satisfies the named passive structural definition
```

Validation does not establish that the private synthesis process occurred, that
architecture is semantically correct, that source state is current, or that
execution is authorized.
