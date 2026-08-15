# Universalist 17.5.0

Universalist is an implicitly invoked boundary-architecture lens with
**evidence-indexed progressive disclosure**.

Its common path is intentionally small:

```text
owned boundary
-> incumbent or ordinary candidate
-> owner
-> required observations
-> law
-> falsifier
-> preserve, ordinary nomination, or evidence-backed escalation
```

Category theory remains a hidden recognizer. Advanced constructions load only
after repository evidence identifies a consequential typed hole that the
ordinary candidate does not close.

## Install

Place the complete tree at `codex/skills/universalist/`.

The skill has no runtime scripts and ships no skill-local executable tests.
Ledger is used only for independently durable standalone decisions.

After loading `$ledger` and completing `$ledger ensure`, validate the
machine-readable decision contract from the repository root:

```bash
tune_contract_definition="$(realpath \
  "${CODEX_HOME:-$HOME/.codex}/skills/tune/definitions/ledger/skill-decision-contract.json")"

ledger validate \
  --definition "$tune_contract_definition" \
  --input contract=codex/skills/universalist/references/decision-contract.json \
  --format json
```

That validates structure under the selected definition. It does not prove that
the prose, registry, templates, and contract are semantically equivalent.

## Progressive-disclosure model

`SKILL.md` is the complete routine kernel. It supports preservation and an
uncontested ordinary boundary nomination without loading another file.

Deeper doctrine is admitted by evidence:

| Evidence | Module |
|---|---|
| Repeated semantic obligations may share one law | `references/latent-structure-recognition.md` |
| At least two routes materially differ | `references/consequential-boundary.md` |
| A concrete typed hole remains | `references/artifact-selection-by-unknown-location.md`, registry, and matching cards |
| One advanced card remains live | only that card's `theory_refs` |
| A decision needs independent durability outside Actuating | `references/durable-decision.md` |
| User explicitly requests team mode | `references/workflow/` |

The runtime must not browse the whole reference corpus to discover a reason to
escalate.

## Common path

Every considered boundary receives:

```text
Boundary:
Disposition: preserve / ordinary / escalate
Owner:
Required observations:
Incumbent or ordinary candidate:
Law:
Falsifier:
Invalidates when:
```

An already exact boundary is preserved. One uncontested record, tagged union,
checked constructor, adapter, state machine, operation IR, handler, query,
canonical merge, or compatibility witness remains ordinary.

Activation is broad; escalation is narrow.

## Latent structure

The recognition module activates only for a repeated semantic obligation,
distributed owner, repeated interpreter/composition/transition shape, or an
imminent variant already constrained by the same law.

It separates:

```text
recognition
  abductively infer a plausible law-bearing pattern

evaluation
  deductively test it against evidence, false friends, and alternatives

transition
  construct the smallest observation-preserving migration
```

A recognized pattern survives only with a material generalization dividend:
fewer repeated obligations, one clearer owner, fewer invalid states, explicit
lawful composition, one interpreter, safer migration, reusable proof, or a new
variant without new control flow.

## Consequential decisions

A seam is consequential only when at least two plausible routes materially
differ in persistent behavior, authority, representation, admitted domain,
compatibility, migration, enforcement, information retention, legal
composition, effects, resources, invalidation, or proof obligations.

Only then load the full current-context, comparison, Boundary Artifact Contract,
enforcement, residual, proof-lease, and obstruction discipline from
`references/consequential-boundary.md`.

The ordinary repository-native candidate remains the baseline. Incomparable
minima remain underdetermined.

## Advanced mechanics

The 56 construction cards remain evidence-bound theorem nominations. They do not
select a route or authorize mutation.

Selection proceeds:

```text
ordinary candidate
-> one axis and typed hole
-> artifact selection by unknown location
-> relevant card fragment
-> exact theory references for the retained card
-> repository-native lowering
```

Signals, registry order, evidence count, and categorical sophistication never
prove prerequisites.

The former standalone Kan material remains an internal mechanics layer. No
advanced mechanic is advertised in the skill description or default prompt.

## Actuating composition

Inside `$actuating`, Universalist nominates only. It may return:

```text
candidate
preserve-incumbent
obstructed
```

Actuating alone selects or reopens the Construction, grants mutation, and
closes. Universalist does not allocate a separate plan or receipt in that
composition.

## Independent durability

A consequential decision does not automatically need storage.

Load `references/durable-decision.md` only when no current Actuating
Construction carries the complete decision and standalone, cross-session,
multi-actor, migration, or supersession work must address it independently.

That module owns the exact Ledger plan and `SDR-v1` procedure.

## Authority surfaces

- `SKILL.md` — common path, evidence gates, route semantics, authority, and
  reclassification.
- `references/consequential-boundary.md` — full consequential architecture
  contract.
- `references/decision-contract.json` — stable machine-readable trigger, route,
  and clause identifiers.
- `references/universal-construction-registry.yaml` and card fragments —
  advanced mechanic prerequisites, laws, falsifiers, fallbacks, and proof
  profiles.
- `templates/universalist-plan.md` — durable human decision projection.
- `agents/openai.yaml` — invocation metadata only.
- `README.md` — explanatory documentation.

## Behavioral acceptance

The disclosure split is correct only when these cases remain distinct:

```text
exact incumbent
  -> SKILL.md only
  -> preserve

one ordinary checked owner
  -> SKILL.md only
  -> ordinary nomination

repeated validators implementing one agreement law
  -> SKILL.md + latent-structure-recognition.md
  -> consequential-boundary.md only if material alternatives remain

advanced typed hole
  -> consequential-boundary.md
  -> artifact selector
  -> relevant card fragment
  -> exact theory_refs only

Actuating composition
  -> modules needed for nomination
  -> never durable-decision.md

standalone durable migration decision
  -> nomination modules + durable-decision.md

team mode
  -> workflow references only after explicit request
```

No scenario should load the complete reference corpus.

## Package invariants

- implicit boundary activation remains enabled;
- team mode remains explicit-request only;
- all four `UNI-*` routes are preserved;
- all 56 cards and 12 axes are preserved;
- no runtime script or skill-local executable test is added;
- advanced mechanics load only after a concrete evidence gate;
- durable Ledger mechanics never load in Actuating composition;
- routine preservation and ordinary repair require only `SKILL.md`.
