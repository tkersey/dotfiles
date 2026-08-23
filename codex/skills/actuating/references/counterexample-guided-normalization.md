# Counterexample-Guided Normalization

Normative only when an `entailed` bug, review finding, test failure, incident,
migration failure, or compatibility failure may authorize mutation.

## Governing law

```text
review accumulates Counterexample knowledge, not code

T(n+1) = quotient(T(n) + newly accepted applicable classes)

R(n+1) != patch(R(n), latest finding)

R(n+1) =
  realize(normal_form(Goal, causal_basis(T(n+1)), obligations))
```

Knowledge is monotone. Realization is not.

A finding is evidence about the current construction. It is never an edit
instruction. Historical implementation momentum, file proximity, review order,
and the current number of guards do not decide the successor.

## Why one gate

Actuating uses exactly one normalization gate:

```text
direct-repair admission
```

The gate governs the dangerous transition: preserving the current architecture
while changing its realization. It does not gate architecture recompilation,
ordinary validation, review dispatch, publication, or closure.

This narrow boundary is deliberate. A gate that cannot reject a harmful
successor is ceremony. A gate that blocks the member-specific patch which would
continue review accretion changes the produced software.

## Activation

Run the gate before a bug-driven mutation when Actuating proposes to retain the
current theory and architecture as a direct realization repair, including
`retain-theory-reprove` after post-elimination falsification.

Do not run it for:

```text
mechanical edits with no correctness-bearing semantic delta
non-mutating triage or remediation planning
a selected architecture/abstraction successor
a change that already admits it changes the semantic model
```

A local patch remains a direct repair regardless of its label. Calling a
member-specific guard "normalization" does not bypass this gate.

## Causal basis

Before gate execution, quotient all currently applicable accepted classes into:

```text
one current causal generator
or
one evidenced instance-specific exception separated from a generator
```

Every generator states:

```text
governing law
existing family-level mechanism
canonical owner
admission frontier or minimal cut
repository evidence
falsifier
```

Once a causal generator exists, another member-specific production factor for
that generator is forbidden unless a non-example separation proof establishes
that the class is independently governed.

One witness may establish a generator when it falsifies a universal
construction, transition, composition, ownership, or representation law. Bug
count is not the trigger.

## Semantic-novelty firewall

A direct repair may preserve the architecture only when:

```text
the governing law is unchanged
the family and interpretation are unchanged
the admission model and owner model are unchanged
the complete semantic model is unchanged
the required behavior already exists in the selected construction
the mutation restores an existing family-level mechanism
```

The semantic model changes when the mutation introduces or changes any:

```text
state dimension or value
event or transition
transition guard or ordering law
representation or constructor
authority or custody relation
generation, freshness, or correlation rule
admission path or minimal cut
timeout, cancellation, retry, or recovery mode
completion or shutdown mode
effect or observation path
compatibility mode
independent validator or semantic enforcement site
proof family
```

An absent constructor cannot be smuggled through a realization repair. Recompile
the target architecture before mutation.

## Factor rootedness

For the affected semantic region, enumerate current correctness-bearing factors:

```text
branch, flag, state, transition, handler
constructor, validator, schema, capability, composition rule
compatibility, recovery, bypass, or derived guard
helper abstraction or generated table
test, model, property, fixture family, or proof script
```

Each affected predecessor factor receives exactly one disposition:

```text
preserve
  still realizes a current obligation

replace
  successor factor realizes the same current obligation

retire
  no current obligation remains

distinct-obligation
  independently necessary despite sharing nearby code or symptoms
```

No factor is preserved by inertia. Unknown ownership or obligation blocks
direct repair rather than manufacturing either deletion or preservation.

## Generative realization

A generative theory requires a generative realization.

```text
causal generator
-> one family-level construction or admission mechanism
-> every sanctioned affected path
-> family-level proof and falsifier
```

Observed examples may remain as minimal boundary witnesses. They may not remain
the production architecture's vocabulary unless their distinctions are required
by the Goal or supported by non-example separation proof.

A repair that adds one predicate, branch, validator, or owner for one observed
member while preserving the same generator is not generative realization.

## Direct-repair admission packet

Actuating constructs one ephemeral packet under:

```text
actuating-direct-repair-admission/v1
```

The packet binds:

```text
repository / immutable base / exact predecessor head
Goal and evidence digests
mutation basis and elimination-lease posture
law, family, interpretation, admission, owner, and semantic-model identities
all accepted class mappings
all current causal generators
affected predecessor factors and complete dispositions
the existing family mechanism being restored
semantic-constructor, member-specific-factor, and owner-site deltas
verification evidence and a falsifier
```

Do not submit conclusion booleans such as `normalization_complete: true`.
Supply the underlying structured sets, mappings, paths, identities, and evidence
from which the definition decides admission.

## Ledger execution

Before the first Ledger command in the workflow, load `$ledger` and complete
`$ledger ensure` once.

Then materialize the pure owner-defined gate:

```bash
actuating_gate_definition="$(
  realpath \
    "${CODEX_HOME:-$HOME/.codex}/skills/actuating/definitions/ledger/direct-repair-admission.json"
)"

ledger materialize \
  --definition "$actuating_gate_definition" \
  --input gate=<direct-repair-admission.json> \
  --format json
```

Require:

```text
schema = ledger-materialization-result/v1
valid = true
storage_mutated = false
artifact_id = sha256:...
```

The artifact ID binds the exact packet during the active mutation decision. It
is not a receipt, capability, durable workflow fact, or closure authority.

A changed Goal, predecessor head, evidence set, theory, semantic model, factor
inventory, or proposed delta requires fresh materialization.

Do not transact, project, doctor, bind, rebind, or create an Actuating store for
this gate.

## Transition law

```text
valid materialization
  -> Actuating may perform the exact admitted direct repair

invalid materialization
  -> direct repair is forbidden
  -> recompile and realize a normal-form architecture
     or return blocked when the semantic evidence is insufficient
```

Ledger does not select the repair or grant mutation. Actuating selects the
requested transition, constructs the evidence packet, interprets the
definition-relative result, and owns the next action.

## Post-elimination application

`retain-theory-reprove` may request direct repair only when:

```text
the prior elimination lease is revoked
the failed premise is localized to realization or proof
the existing family, interpretation, admission model, and owner remain valid
the mutation restores the existing family mechanism
the mutation adds no member-specific factor or enforcement site
```

The theory hypothesis may survive. The prior elimination disposition does not.

## Normal-form realization

When direct repair is rejected, select the smallest correctness-non-dominated
construction whose realization:

```text
covers every causal generator at a family-level mechanism
preserves every Goal-required valid behavior and observation
partitions all affected predecessor factors
retires dominated wound-specific production and proof surface
uses the strongest feasible generator-level proof
leaves no unowned correctness-bearing residue
```

The semantic decision unit is this complete affected construction. Individual
coherent edits are realization units only. Do not launch closure-grade review
against a half-realized target.

## Behavioral acceptance

The gate earns permanence only if watched use shows an object-level delta.

For a shared causal generator, the next mutation must either:

```text
restore one existing family-level mechanism without new member-specific factors

or

recompile the architecture and retire dominated member-specific surface
```

It must not add another wound-specific guard.

Observe:

```text
member-specific correctness-bearing factors added per generator
independent enforcement sites added
dominated production and proof surface deleted
same-family findings in later review waves
material review-driven mutations before convergence
false rejection of isolated implementation repairs
gate preparation and execution cost
```

## Gate falsifier and retirement rule

Delete or narrow the gate when evidence shows any:

```text
enabled and disabled runs select materially equivalent mutations
the gate is satisfied by packet rewrites without code-shape changes
normalization after rejection produces the same member-specific design
legitimate isolated repairs are repeatedly rejected
a direct type, constructor, test, schema, or verifier excludes the failure
more locally and completely
gate cost exceeds the accretion and review churn it prevents
```

The gate is capability only while it prevents bad successors.

## Hard exclusions

- No finding-to-patch mapping.
- No latest-wave-only mutation decision.
- No second same-generator member-specific repair without separation proof.
- No new semantic constructor hidden inside direct repair.
- No self-attested conclusion booleans in place of repository-grounded inputs.
- No durable gate store, event log, predecessor chain, gate history, or receipt
  family.
- No Ledger selection of architecture, mutation authority, review credit,
  publication, or closure.
