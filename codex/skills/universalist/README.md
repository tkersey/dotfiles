# Universalist 17.3.0

Universalist is a boundary-triggered architecture workflow. It keeps one operating discipline:

> one owned boundary, one current context, one smallest effective artifact

It uses category theory when that changes the artifact, law, or proof—not as decorative vocabulary and not through skill-local executables.

## Install and validate

Place the complete tree at `codex/skills/universalist/`. The skill has no runtime scripts and ships no skill-local executable tests.

From the repository root:

```bash
tune_contract_definition="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/tune/definitions/ledger/skill-decision-contract.json")"
ledger validate \
  --definition "$tune_contract_definition" \
  --input contract=codex/skills/universalist/references/decision-contract.json \
  --format json
```

Ledger validates the `SKDC-v1` structure without granting semantic authority. It does not compare prose in `SKILL.md` with the contract. `references/decision-contract.json` is the machine-readable authority for consequential triggers, routes, clauses, and required evidence; update it together with `SKILL.md` and `templates/universalist-plan.md` whenever policy changes.

## Use

`$universalist` is active whenever implementation, refactoring, review, migration, or resolution considers a code boundary. Boundary consideration itself is the activation signal.

Activation is broad; escalation is proportional. The boundary pass may preserve an already exact seam and continue without adding abstraction.

Start with:

```text
Boundary:
Disposition: preserved / introduced / changed / repaired / removed / bypass-justified
Disposition rationale and evidence:
Owner:
Source / target:
Preserved / forgotten / generated / observed:
Law:
Falsifier:
```

Use ordinary repository-native types, adapters, handlers, interpreters, and tests when they make the seam exact. Escalate only when a stronger construction materially changes behavior, authority, compatibility, migration, enforcement, invalidation, representable states, legal composition, effects, locality, information flow, proof, or resources.

## Context-relative artifact contract

For every consequential seam, record the attributed current context, comparison universe, one architectural axis and typed hole, Boundary Artifact Contract, enforcement matrix, residual obligations, and invalidation triggers.

Every requirement has one semantic owner and one primary disposition: enforced, residual, or obstructed. Compatible derived guards may provide defense in depth when they preserve the same rule, declare failure behavior, and carry a conformance or drift witness. They do not become competing authorities.

Complete only the Boundary Artifact Contract surfaces that honestly apply. Mark an inapplicable constructor, eliminator, composition, or interpreter surface as `not applicable` with a concrete rationale.

## Construction cards

The 56 YAML cards in `references/universal-constructions/` are evidence-bound theorem nominations, not route authority. The registry supplies axes, signals, prerequisites, compatibility hints, laws, falsifiers, proof profiles, and theory references.

For a consequential choice:

1. state the ordinary candidate first;
2. identify one seam, architectural axis, and typed hole;
3. read only cards matching evidenced signals and axis;
4. classify every relevant card as selected, rejected, contradicted, or unresolved;
5. retain a card only when repository evidence satisfies prerequisites and proof obligations;
6. lower it to a repository-native Boundary Artifact Contract;
7. let Actuating or the standalone root choose the route and authorize mutation.

Do not use signal count, evidence count, `diagnostic_order`, or registry order to manufacture a winner. Missing evidence remains unresolved. Support-only cards guard reasoning and never become implementation artifacts.

A selected universal construction needs existence, preservation, competitor mediation, canonicality or uniqueness-up-to, effectivity, and a falsifier. Obstruction needs nonexistence, a counterexample, stability, effectivity, a falsifier, and a reopening condition.

## Double-category architecture

Universalist now has a dedicated construction card:

```text
id: two_dimensional_composition
axis: two-dimensional-composition
hole: square
expert construction: Double category / equipment
```

Use it only when two semantically different arrow families both compose:

```text
horizontal arrows
  processes, open systems, queries, generalized interactions, executable behavior

vertical arrows
  migrations, refinements, strict maps, reindexings, deployments, architecture changes

squares
  typed compatibility witnesses relating the two directions
```

Core doctrine:

```text
Processes compose horizontally.
Changes compose vertically.
Squares certify compatibility.
Interchange makes local change compositional.
```

The repository-native lowering is normally narrow:

```text
horizontal-arrow IR
vertical-arrow IR
compatibility-square witness
horizontal and vertical composition
horizontal and vertical square pasting
interchange/coherence normalization
one double-functor-style interpreter
resource and invalidation policy
```

Prefer a pseudo double category when composition is coherent only up to represented isomorphism or normal form. Use an equipment/framed bicategory only when strict maps admit useful companions, conjoints, or restrictions. Use a virtual double category when generalized horizontal cells matter but horizontal composition is partial or unavailable.

Do not introduce a generic framework for one commuting square. A category, 2-category, typed adapter plus one compatibility witness, PROP, or DPO rewrite may be the smaller honest construction. Interchange never establishes effect commutativity, safe parallelism, authority preservation, or resource independence.

Read:

- `references/double-category-architecture.md`
- `references/mechanics/double-categories.md`
- `references/composition-geometry.md`

## Independently durable decision receipts

A decision is consequential only when at least two plausible routes materially differ. Routine and uncontested choices use the compact boundary disposition without a plan or receipt.

Materiality controls reasoning, not storage. In Actuating composition, return the complete candidate analysis to Actuating and let the Construction carry the adjudicated decision. Create a Universalist plan and `SDR-v1` only when no current Construction carries that decision and a standalone, cross-session, multi-actor, migration, or supersession handoff must address it independently.

Before the first Ledger command, load `$ledger` and complete `$ledger ensure`
once. Universalist requires Ledger 1.x and `ledger-artifact-abi/v1`.

Bind a valid pre-cutover plan once with `ledger transact --operation
bind-existing --param plan_file=PLAN_FILE`; the operation validates existing
bytes and writes only Ledger-owned binding metadata. New plans use:

```bash
ledger transact \
  --definition <universalist-skill-root>/definitions/ledger/plan-document.json \
  --operation create \
  --repo PROJECT_ROOT \
  --input template=<universalist-skill-root>/templates/universalist-plan.md \
  --format json
```

For a durable double-category decision, include the applicable existing clauses
plus `UNI-DOUBLE-001` in the `SDR-v1`. Pass every applicable clause explicitly.
Tune's canonical definition validates and materializes the receipt;
Universalist's plan definition owns plan identity, address resolution, and
atomic custody. Universalist retains decision policy and Markdown meaning.

## Tracks

- **Track A0** — discover carriers, operations, observations, laws, non-laws, and effect boundaries.
- **Track A** — diagnose one seam without implementation.
- **Track B** — implement one narrow boundary refactor.
- **Track C** — stage an internal migration behind a stable public or storage shape.
- **Track D** — introduce a canonical boundary artifact with an interpreter or projection and law.
- **Track E** — certify one-dimensional composition or a selected two-dimensional square/pasting calculus.
- **Track F** — prepare exact context before semantic consumption.
- **Track G** — repair an inexact abstraction through its real usage site.
- **Track H** — pivot to a world where the hard operation becomes inspectable, then transport it back.
- **Track I** — design a whole capability on an effective universal substrate.

## Doctrine and mechanics

Load only what the selected seam requires:

- `references/structures-and-laws.md`
- `references/canonical-boundary-artifacts.md`
- `references/composition-geometry.md`
- `references/double-category-architecture.md`
- `references/comonadic-spatiality-doctrine.md`
- `references/description-composition-doctrine.md`
- `references/exact-context-doctrine.md`
- `references/possibility-sheafification.md`
- `references/category-pivot.md`
- `references/mechanics/`

## Custom agents

The eight Universalist custom agents remain available only for explicit team mode. The root owns synthesis, standalone route selection, mutation authority, and the receipt when independent durability requires one.

## Invocation metadata

`agents/openai.yaml` keeps implicit invocation enabled because boundary consideration itself is the signal.
