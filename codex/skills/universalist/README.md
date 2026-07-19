# Universalist 17.2.0

Universalist is a boundary-triggered architecture workflow. It keeps one operating discipline:

> one owned boundary, one current context, one smallest effective artifact

It uses category theory when that changes the artifact, law, or proof—not as decorative vocabulary and not through skill-local executables.

## Install and validate

Place the complete tree at `codex/skills/universalist/`. The skill has no runtime scripts and ships no skill-local executable tests.

From the repository root:

```bash
seq skill-contract validate \
  --file codex/skills/universalist/references/decision-contract.yaml \
  --format json
```

Seq validates the `SKDC-v1` structure and computes the contract fingerprint used by Ledger receipts. It does not compare prose in `SKILL.md` with the contract. `references/decision-contract.yaml` is the machine-readable authority for consequential triggers, routes, clauses, and required evidence; update it together with `SKILL.md` and `templates/universalist-plan.md` whenever that policy changes.

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

Use ordinary repository-native types, adapters, handlers, interpreters, and tests when they make the seam exact. Escalate only when a stronger construction materially changes persistent behavior, authority, compatibility, migration, enforcement, invalidation, representable states, legal composition, effects, locality, information flow, proof, or resources.

## Context-relative artifact contract

For every consequential seam, record the attributed current context, comparison universe, one architectural axis and typed hole, Boundary Artifact Contract, enforcement matrix, residual obligations, and invalidation triggers.

Every requirement has one semantic owner and one primary disposition: enforced, retained as a residual, or proved obstructed. Compatible derived guards may provide defense in depth when they preserve the same rule, declare failure behavior, and carry a conformance or drift witness. They do not become competing authorities.

Complete only the Boundary Artifact Contract surfaces that honestly apply to the artifact kind. Mark an inapplicable constructor, eliminator, composition, or interpreter surface as `not applicable` with a concrete rationale; do not invent placeholder architecture.

## Construction cards

The 55 YAML cards in `references/universal-constructions/` are evidence-bound theorem nominations, not route authority. The registry at `references/universal-construction-registry.yaml` supplies their axes, signals, prerequisites, compatibility hints, laws, falsifiers, proof profiles, and theory references.

For a consequential choice:

1. state the ordinary candidate first;
2. identify the seam and architectural axis under pressure;
3. read only the cards matching the evidenced signals and axis;
4. classify every relevant card as selected, rejected, contradicted, or unresolved;
5. select a card only when repository evidence satisfies its prerequisites and proof obligations;
6. let the root workflow choose the route and authorize mutation.

Do not use signal count, evidence count, `diagnostic_order`, or registry order to manufacture a winner. Missing evidence leaves a card unresolved; it is not an obstruction. Support-only cards guard reasoning and never become implementation artifacts.

A selected universal construction needs evidence for existence, commutation or preservation, competitor mediation, canonicality or uniqueness-up-to, effectivity, and a falsifier. Obstruction needs nonexistence, a counterexample, stability, effectivity, a falsifier, and a reopening condition.

The registry value `universal.role: emitter` describes the categorical direction from a selected artifact to admissible consumers. It does not describe a shell or Python program.

## Consequential decision receipts

A decision is consequential only when at least two plausible routes materially differ in persistent behavior, authority, compatibility, migration, enforcement, invalidation, or proof obligations. Routine seams, ceremonial activation, and uncontested choices use the compact boundary disposition without a plan or receipt.

Before the first Ledger command, load `$ledger` and complete `$ledger ensure` once. Then use native Ledger directly. Universalist requires Ledger 0.10.6 or newer and Skills Seq 0.3.52 or newer.

```bash
ledger --source universalist create \
  --repo PROJECT_ROOT \
  --template /path/to/universalist/templates/universalist-plan.md

ledger --source universalist emit \
  --plan /path/to/.ledger/universalist/plan-PLAN_ID.md \
  --contract /path/to/universalist/references/decision-contract.yaml \
  --clause-ref UNI-DISPOSITION-001 \
  --clause-ref UNI-MINIMAL-001 \
  --clause-ref UNI-CONTEXT-001 \
  --clause-ref UNI-ARTIFACT-001 \
  --clause-ref UNI-ENFORCEMENT-001 \
  --clause-ref UNI-MECHANICS-001 \
  --clause-ref UNI-ROOT-001 \
  --question "Which construction owns this seam?" \
  --selected-route UNI-ORDINARY \
  --rejected-route UNI-CANONICAL \
  --expected-outcome "The owner boundary enforces one observable law." \
  --disposition changed \
  --construction "checked adapter at the owner boundary" \
  --law "required observations are preserved" \
  --falsifier "a mismatched source is accepted" \
  --advanced-mechanics none \
  --evidence-ref "code:path" \
  --write-plan
```

Pass every applicable clause explicitly. For `UNI-OBSTRUCT`, replace `UNI-ARTIFACT-001` with `UNI-OBSTRUCTION-001`. Ledger owns plan identity, address resolution, receipt construction, validation, and atomic append. Universalist owns the decision policy and Markdown fields. A receipt proves the exact contract version and clause set used for the decision; it does not prove that the policy text is semantically correct.

## Tracks

- **Track A0** — discover carriers, operations, observations, laws, non-laws, and effect boundaries.
- **Track A** — diagnose one seam without implementation.
- **Track B** — implement one narrow boundary refactor.
- **Track C** — stage an internal migration behind a stable public or storage shape.
- **Track D** — introduce a canonical boundary artifact with an interpreter or projection and law.
- **Track E** — certify composition and move one seam toward Boundary Normal Form.
- **Track F** — prepare exact context before semantic consumption.
- **Track G** — repair an inexact abstraction through its real usage site.
- **Track H** — pivot to a world where the hard operation becomes inspectable, then transport the result back.
- **Track I** — design a whole capability on an effective universal substrate.

## Doctrine and mechanics

The detailed doctrine remains under `references/`. Load only what the selected seam requires:

- `references/structures-and-laws.md`
- `references/canonical-boundary-artifacts.md`
- `references/composition-geometry.md`
- `references/comonadic-spatiality-doctrine.md`
- `references/description-composition-doctrine.md`
- `references/exact-context-doctrine.md`
- `references/possibility-sheafification.md`
- `references/category-pivot.md`
- `references/mechanics/`

Use the matching artifact under `templates/` when the selected track requires a certificate or report.

## Custom agents

The eight Universalist custom agents remain available for explicit categorical-substrate team mode. Do not spawn them unless the user explicitly requests subagents, parallel agents, or team mode. The root owns synthesis, the selected route, mutation authority, and the single consequential receipt.

## Invocation metadata

`agents/openai.yaml` keeps implicit invocation enabled because boundary consideration itself is the signal.
