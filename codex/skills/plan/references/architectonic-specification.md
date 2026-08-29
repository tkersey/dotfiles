# Architectonic Specification

A decision-complete implementation specification makes consequential architecture
and abstraction explicit before policy actions are selected.

The purpose is not to add architecture. It is to recover the smallest coherent
organization whose factors own live obligations, whose truths have canonical owners,
whose compositions are lawful, and whose invalid states or compositions are excluded
where the implementation environment permits.

## Admission

Run the pass when at least two plausible organizations materially differ in
persistent behavior, ownership, compatibility, migration, enforcement, information
retention, resource use, or proof obligations.

Do not escalate merely because work touches modules, APIs, types, schemas, or files.
A local change inside one already-exact boundary may preserve the incumbent with one
law and falsifier.

## Architectonic Thread

Represent each consequential decision as one seam:

```yaml
architectonic_seam:
  seam_id:
  authority:
    source_fixed |
    source_bounded |
    specification_local
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
  live_obligations: []
  required_observations: []
  compatibility_and_migration: []
  host_capabilities: []
  incumbent:
    organization:
    factors: []
  candidate_movements:
    preserve:
    restrict_admitted_domain:
    strengthen_representation_or_owner:
    ablate_or_normalize:
  disposition:
    selected |
    evidence_conditioned |
    downstream_open |
    underdetermined |
    obstructed
  selected_organization:
  decision_observation_refs: []
  factor_dispositions:
    preserved: []
    factored: []
    quotiented: []
    ablated: []
    normalized: []
    introduced: []
  law:
  falsifier:
  residual_obligations: []
  invalidators: []
```

Use one architectural axis and one typed hole per seam. Independent pressures become
linked seams rather than one global architecture winner.

## Authority

- `source_fixed` — accepted source selects the organization or forbids an
  alternative. Record rather than re-decide it.
- `source_bounded` — source fixes observations, compatibility, authority, scope, and
  proof envelope while permitting selection within it.
- `specification_local` — choice is necessary for decision completeness and does not
  alter accepted semantics. It becomes `plan_local` during EPG lowering.

A `downstream_open` disposition is legal only when the specification proves the
choice is not semantically necessary yet, states the admissible candidate space,
names deciding observations, and records forbidden outcomes and a safe default or
blocker.

## Procedure

1. Recover live obligations and required observations before accepting incumbent
   files, classes, services, layers, or owners as real factors.
2. State the ordinary repository-native candidate first.
3. Compare preservation, admitted-domain restriction, representation/owner
   strengthening, and ablation/normalization.
4. Factor every proposed abstraction by a distinct live obligation and recomposition
   role. Classify the obligation as `live`, `moved`, `expired`, `duplicated`,
   `invalid`, or `unknown`.
5. Test whether observationally indistinguishable factors can be quotiented,
   unearned factors ablated, and survivors normalized around one owner.
6. Select, condition on evidence, leave honestly open, or report obstruction.
7. Record law, falsifier, residual obligations, and invalidation triggers.

## Conceptual compression

A candidate dominates only when it is no weaker on required behavior, observations,
compatibility, enforcement, proof, effects, and resources while reducing accidental
distinctions, duplicate owners, bypasses, reconstruction paths, invalid representable
states, or unearned factors. Fewer files or lines alone proves nothing.

## Specification square

When specification derivation and architecture change are both compositional, check:

```text
authoritative context ---- specify before ----> prior specification shape
        |                                             |
        | architecture / abstraction change           | derived spec change
        v                                             v
architected context ------ specify after -----> architected specification
```

The square commutes when both routes preserve required observations, authority,
compatibility, effects, resource policy, and proof bar. Use this as an operational
transport check, not category-theory theater.

## Derivation laws

Selected seams determine:

```text
implementation approach
implementation sequence
canonical owners and enforcement loci
migration and retirement work
requirement-to-proof traceability
rollback and abort criteria
binary done-state
```

A sequence item that realizes an ablated factor, bypasses a canonical owner, or
reconstructs information the selected representation should retain is inconsistent.

## Stopping rule

Stop when every consequential seam is selected, evidence-conditioned, honestly
downstream-open, underdetermined with a named owner, or obstructed; every retained
factor owns a live obligation; no simpler candidate dominates; and law, falsifier,
residuals, invalidators, migration, and proof path are explicit.

## Failure modes

Reject architecture theater, file-shaped factorization, abstraction proliferation,
duplicate or shadow truth, reconstruction compensators, elegance without migration,
source-authority drift, plan-shaped execution waves, and downstream sections that
still encode a superseded organization.
