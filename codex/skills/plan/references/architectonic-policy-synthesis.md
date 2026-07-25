# Architectonic Policy Synthesis

`$plan` refines one joint candidate:

```text
C = (A, P)

A = architecture and abstraction state
P = execution policy
```

Architecture is not a detached review section. It is part of the state over which
the existing policy-synthesis fixed point converges.

## Architectonic state

For every consequential seam, record:

```yaml
architectonic_seam:
  seam_id:
  authority:
    source_fixed |
    source_bounded |
    plan_local
  boundary:
    owner:
    source:
    target:
  axis:
    data_shape |
    behavior |
    syntax_semantics |
    composition |
    representation |
    ownership |
    context |
    transport |
    proof
  typed_hole:
    object |
    map |
    representation |
    interpreter |
    composition |
    equivalence |
    owner |
    proof
  live_obligation_refs: []
  required_observation_refs: []
  compatibility_and_migration: []
  host_capabilities: []
  incumbent:
    organization:
    factor_refs: []
  candidate_movements:
    preserve:
    restrict_admitted_domain:
    strengthen_representation_or_owner:
    ablate_or_normalize:
  disposition:
    selected |
    evidence_conditioned |
    underdetermined |
    obstructed
  selected_organization:
  decision_observation_refs: []
  factors:
    - factor_id:
      owner:
      live_obligation_refs: []
      obligation_status:
        live |
        moved |
        expired |
        duplicated |
        invalid |
        unknown
      disposition:
        preserve |
        factor |
        quotient |
        ablate |
        normalize |
        introduce
  law:
  falsifier:
  residual_obligations: []
  invalidators: []
```

Use one architectural axis and one typed hole per seam. Keep independent seams
independent unless an evidenced composition law relates them.

## Authority

- `source_fixed` — preserve or return to the source owner. Plan may not replace it.
- `source_bounded` — Plan may iteratively select and improve architecture inside the
  source's required observations, compatibility, authority, scope, and proof bar.
- `plan_local` — Plan may preserve, restrict, strengthen, factor, quotient, ablate,
  normalize, or replace the organization as part of policy synthesis.

An architecture change does not by itself require `return_to_spec`. Return only when
it contradicts source-fixed semantics or exceeds a source-bounded envelope.

## Candidate movements

For each consequential seam, compare:

```text
realization preserve
admitted-domain restriction
representation or owner strengthening
ablation or normalization
```

State the ordinary candidate first. Do not reward abstraction novelty, category
vocabulary, file count, or implementation momentum.

A candidate dominates another only when it is no weaker on live obligations,
required observations, compatibility, enforcement, proof, effects, and resources,
and strictly reduces at least one accidental distinction, duplicate owner, bypass,
reconstruction path, invalid representable state, or unearned factor.

## Conceptual compression

Plan may accrete justification while ablating surface.

The fixed point should be monotone in:

```text
explained obligations
evidenced decisions
preserved observations
excluded invalid states
proof strength
retired uncertainty
```

It need not be monotone in:

```text
action count
factor count
owner count
branch count
file count
policy prose
```

A later iteration may replace six actions and three abstractions with two actions and
one governing representation. That is an accretive improvement when it increases
explanatory and proof power.

## Action binding

Every consequential action names:

```text
architectonic seam refs
factors realized
factors retired
preservation observations
```

An action is incomplete when it assumes an unnamed representation or owner,
reintroduces an ablated factor, bypasses a canonical owner, or depends on an
unresolved architectural choice without an observation-conditioned route.

## Double-category transport

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

For an affected action:

```text
A_before ---- action_before ----> B_before
   |                                  |
   | architectonic change             | architectonic change
   v                                  v
A_after  ----- action_after ---->  B_after
```

The square commutes when both routes preserve the declared observations, authority,
compatibility, effects, resources, and proof obligations.

Horizontal pasting composes sequential actions. Vertical pasting composes successive
architectonic changes. Interchange requires rearchitecting-then-replanning to agree
with transporting the current plan through the rearchitecture up to the declared
equivalence.

When architecture changes:

1. identify affected seams, factors, actions, proofs, rollback, and terminals;
2. preserve actions bound only to preserved factors;
3. retire actions bound to retired factors;
4. revise actions bound to changed factors;
5. introduce realization and proof for introduced factors;
6. record the square result and falsifier;
7. restart synthesis from the earliest affected existing lens.

Do not claim double-category structure for one isolated compatibility check when no
horizontal and vertical pasting matter.

## Lift the existing nine lenses

Do not create a second architectonic loop. Lift every existing fixed-point lens over
`(A, P)`:

- `source_fidelity` — preserve source-fixed seams and prohibited organizations;
- `semantic_authority` — classify source-fixed, source-bounded, and plan-local
  decisions honestly;
- `system_regime` — distinguish known architecture, evidence-conditioned selection,
  stabilization-first work, and genuine underdetermination;
- `belief_and_observation` — bind choices and invalidators to observable evidence;
- `action_completeness` — realize introduced factors, migrate changed boundaries,
  and retire displaced factors;
- `policy_closure` — route every architectural observation outcome lawfully;
- `safety_and_rollback` — restore a coherent architecture rather than merely old
  files;
- `proof_and_terminal_state` — prove laws, preservation, migration, retirement, and
  falsifiers;
- `simplicity_and_actuation_readiness` — reject dominated factors, duplicate truth,
  needless owners, bypasses, and semantic-surface growth.

The final PSR-v1 suffix remains these nine lens identifiers in this order. Each pass
evaluates the complete architecture-policy candidate digest.

## Radical candidate

After apparent convergence, generate the strongest non-obvious change to the
organizing abstraction, admitted domain, representation, ownership, factorization,
evidence strategy, or policy that improves correctness, conceptual compression,
proof, and realizability without exceeding source authority.

An adopted architectonic candidate transports the affected policy and restarts the
existing fixed point. Creativity remains mandatory; architectural accretion does
not.

## Stopping rule

Convergence requires:

```text
all consequential seams dispositioned
no simpler organization dominates
all retained factors earn live obligations
every action is bound to the architecture it realizes
migration and retirement are complete
all required squares commute or are honestly blocked
policy closure, proof, rollback, and terminals are complete
one clean nine-lens sweep
one clean independent fresh-eyes pass
one radical candidate disposition
```

## Failure modes

Reject:

- policy optimization inside an unquestioned inherited decomposition;
- architecture as an unbound prose note;
- file-shaped factorization;
- architecture theater or abstraction proliferation;
- appending around a superseded organization instead of transporting the plan;
- validators, caches, correlation, or bypasses that reconstruct forgotten truth;
- rollback that restores files but not architectural coherence;
- accretive rhetoric used to justify monotonically increasing surface;
- returning to the source merely because a plan-local architecture improved.
