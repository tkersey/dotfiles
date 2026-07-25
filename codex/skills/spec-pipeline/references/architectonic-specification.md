# Architectonic Specification

A decision-complete implementation specification must make consequential architecture
and abstraction explicit without requiring another workflow or skill.

The purpose of this pass is not to add architecture. It is to recover the smallest
coherent organization whose factors own the live obligations, whose truths have
canonical owners, whose compositions are lawful, and whose invalid states or
compositions are excluded where the implementation environment permits.

## Admission

Run the architectonic pass when at least two plausible organizations materially
differ in persistent behavior, ownership, compatibility, migration, enforcement,
information retention, resource use, or proof obligations.

Do not escalate merely because the task touches modules, APIs, types, schemas, or
files. A local change inside one already-exact boundary may preserve the incumbent
organization with one law and falsifier.

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

- `source_fixed` — the accepted source selects the organization or forbids an
  alternative. The specification records rather than re-decides it.
- `source_bounded` — the source fixes the observations, compatibility, authority,
  scope, and proof envelope while permitting the specification to select within it.
- `specification_local` — the choice is necessary to make this specification
  decision-complete and does not alter accepted source semantics.

A `downstream_open` disposition is legal only when the specification proves that the
choice is not semantically necessary yet, states the admissible candidate space,
names the observation that will decide it, and records forbidden outcomes and a
safe default or blocker.

## Procedure

1. Recover live obligations and required observations before accepting incumbent
   files, classes, services, layers, or owners as the real factors.
2. State the ordinary repository-native candidate first.
3. Compare exactly these fundamental movements:
   - preserve the current realization;
   - restrict the admitted domain;
   - strengthen representation or canonical ownership;
   - ablate or normalize unnecessary structure.
4. Factor every proposed abstraction by a distinct live obligation and recomposition
   role. Classify its obligation as `live`, `moved`, `expired`, `duplicated`,
   `invalid`, or `unknown`.
5. Test whether observationally indistinguishable factors can be quotiented, whether
   unearned factors can be ablated, and whether survivors should normalize around
   one owner.
6. Select, condition on evidence, leave honestly open, or report obstruction.
7. Record the law, falsifier, residual obligations, and invalidation triggers.

## Conceptual compression

Compare candidates by the obligations and observations they explain relative to the
independent concepts, owners, exceptions, and repair paths they require.

A candidate does not dominate merely because it has fewer files or lines. It must be
no weaker on required behavior, observations, compatibility, enforcement, proof,
and resources while reducing accidental distinctions, duplicated truth, bypasses,
or reconstruction paths.

## Specification square

When the specification process and an architecture change are both compositional,
record the compatibility square:

```text
authoritative context ---- specify before ----> prior specification shape
        |                                             |
        | architecture / abstraction change           | derived spec change
        v                                             v
architected context ------ specify after -----> architected specification
```

The square commutes when both routes preserve the same required observations,
authority, compatibility, effects, resource policy, and proof bar. Use this as an
operational transport check, not as permission to label every design diagram a
double category.

Sequential specification derivations paste horizontally. Successive architecture
changes paste vertically. Interchange requires changing-then-deriving to agree with
deriving-then-transporting up to the declared equivalence.

## Derivation laws

Architecture and abstraction are not an isolated prose section. The selected seams
must determine:

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
reconstructs information the selected representation should retain is inconsistent
with the specification.

## Stopping rule

Stop the bounded architectonic pass when every consequential seam is selected,
evidence-conditioned, honestly downstream-open, underdetermined with a named owner,
or obstructed; every retained factor owns a live obligation; no simpler candidate
dominates; and the law, falsifier, residuals, invalidators, migration, and proof path
are explicit.

## Failure modes

Reject:

- architecture theater: more layers, diagrams, or nouns without stronger ownership
  or laws;
- file-shaped factorization;
- abstraction proliferation;
- duplicated or shadow truth;
- validators, caches, correlation, or bypasses that reconstruct information the
  representation should retain;
- elegance without a realizable migration and retirement path;
- source-authority drift;
- plan-shaped execution waves embedded in the specification;
- a declared architecture whose derived implementation sections still encode the
  superseded organization.
