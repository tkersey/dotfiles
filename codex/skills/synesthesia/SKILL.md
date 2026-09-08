---
name: synesthesia
description: "Reversible cross-modal diagnostic lens for software. Use when the user asks what code, architecture, behavior, logs, APIs, or alternatives feel, sound, look, or move like; for compare-by-feel analysis; when literal analysis leaves multiple plausible structural, temporal, interaction, or boundary interpretations that cross-modal recoding could distinguish; or after an owning technical workflow documents such an ambiguity. Start from literal evidence and translate every sensory statement into a technical hypothesis, uncertainty, falsifier, and next move. Not for ordinary architecture, performance, readability, or UX audits; exact syntax; legal/compliance or security sign-off; or code mutation by itself."
metadata:
  version: "4.1.0"
  activation_cost: low
  default_depth: adaptive
---

# Synesthesia

## Mission

Use reversible sensory representations to expose software structure that a literal description has not made easy to see, compare, or communicate.

The sensory layer is a diagnostic instrument. It is not evidence, proof, a mandatory output style, or an implementation owner.

## Governing invariant

```text
literal evidence
-> minimum sufficient sensory representation
-> engineering translation
-> uncertainty and falsifier
-> decision, explanation, or investigation delta
```

A sensory statement that cannot be translated, falsified, or used to change the next move is decoration and should be omitted.

## Activation boundary

Use this skill when at least one of these is true:

1. the user explicitly asks what software feels, sounds, looks, moves, weighs, or resembles;
2. the user asks for a compare-by-feel analysis;
3. literal analysis leaves multiple plausible structural, temporal, interaction, or boundary interpretations and a reversible cross-modal representation is expected to distinguish them;
4. an owning workflow has produced a concrete representational ambiguity and documents why cross-modal recoding may distinguish the alternatives;
5. the user asks to reuse, correct, reject, retract, or remember an established sensory mapping.

The root-discovered ambiguity route requires the competing interpretations, the evidence each explains, and the distinction the sensory representation is expected to expose. General uncertainty, novelty, or a desire for colorful prose is not sufficient.

Do not activate merely because a task concerns:

- architecture;
- performance;
- readability or maintainability;
- flaky behavior;
- onboarding;
- API or UX quality;
- refactoring;
- a strange bug;
- delivery, handoff, or terminal closeout.

Those domains have their own technical owners. Synesthesia participates only when the representational lens is itself useful.

Do not use for exact syntax, legal or compliance interpretation, security sign-off, rote edits, or literal-only tasks.

## Ownership and handoffs

Synesthesia may shape diagnosis or explanation, but it does not displace the owning workflow:

- measured performance work -> `$lift`;
- structural or categorical architecture -> `$universalist`;
- local comprehension and refactoring preflight -> `$complexity-mitigator`;
- security, UX, API, CLI, copy, or performance audit -> the relevant direct audit or available specialist;
- code mutation -> the implementation owner selected by the root workflow;
- durable source-note writing -> `$memory-source-notes`.

When another skill owns the task, Synesthesia returns one route-shaping insight or explanatory model and then hands control back.

Do not create a dedicated Synesthesia custom subagent. In explicitly requested team mode, use a read-only lane only when it receives exact artifact state, literal evidence, a specific representational question, and a required engineering translation plus falsifier.

## Modes

Choose exactly one primary mode.

### Diagnose

Use a sensory model to generate or rank technical hypotheses.

Return:

- literal observations;
- the smallest useful sensory model;
- engineering translations;
- uncertainty;
- falsifiers;
- investigation order.

### Explain

Use a reversible model to teach a system, flow, or boundary.

Return:

- the literal model;
- one coherent sensory representation;
- the correspondence between the two;
- important limits or misconceptions.

Do not force an action list when explanation is the goal.

### Compare

Apply stable axes to two or more alternatives.

Return:

- common evidence;
- shared mapping axes;
- differences and trade-offs;
- the decision implication;
- uncertainty or missing evidence.

Do not change mappings between alternatives merely to make one sound better.

### Implementation lens

Use one sensory representation to select or clarify a technical move, then return to literal implementation.

Return only:

- the route-shaping observation;
- its engineering translation;
- the owning workflow and next move.

Do not narrate the entire implementation in metaphor.

## Core contract

Always:

1. start from literal evidence: code, tests, logs, traces, architecture, runtime behavior, user flow, or repository structure;
2. separate observations from hypotheses;
3. choose the minimum sufficient and non-redundant modalities, usually one or two;
4. keep mappings internally consistent within the analysis;
5. translate every useful sensory statement into concrete engineering meaning;
6. mark uncertainty when the translation is inferential;
7. give every material diagnostic mapping a falsifier;
8. identify the explanation, investigation, or route delta;
9. execute code changes literally even when the lens informed them.

Never:

- treat metaphor as evidence;
- invent unseen runtime behavior;
- hide uncertainty in aesthetic language;
- use several modalities to restate the same claim;
- overwrite exact facts with feel;
- force this lens onto a task that is already clear literally;
- infer a durable user mapping from assistant-authored prose alone.

## Modality selection

Use [modality-selection.md](references/modality-selection.md) when selection is not obvious.

Default principle:

```text
one modality if one independent dimension is enough
second modality only for a genuinely independent dimension
more than two only with an explicit reason
```

Do not use a fixed universal mapping table. Treat all mappings as task-indexed hypotheses until accepted by the user or repeatedly operationalized.

## Procedure

### 1. Literal read

Identify:

- observed components and boundaries;
- control, data, state, or user flow;
- timing, load, or ordering evidence;
- failures and constraints;
- unknowns;
- the specific question the literal model has not resolved.

### 2. Select the representation

Choose a modality because its structure matches the evidence:

- spatial for topology, dependency, ownership, or boundary shape;
- rhythmic or auditory for timing, concurrency, retries, or sequencing;
- tactile for interaction friction, brittleness, or rollback difficulty;
- thermal or pressure for saturation, allocation, contention, or concentrated load;
- visual for contrast, visibility, state distribution, or change over time.

### 3. Render conservatively

State only what the literal evidence supports. Use a compact representation rather than decorative prose.

### 4. Translate and challenge

For every material mapping, produce:

```text
Mapping Card:
- evidence:
- sensory representation:
- engineering translation:
- uncertainty:
- falsifier:
- decision or explanation delta:
```

### 5. Stop or hand off

Stop the sensory pass when:

- the model adds no new distinction;
- the literal explanation is already sufficient;
- a technical owner has a dominant next move;
- further metaphor would only restate the diagnosis;
- evidence is too weak to support a reversible translation.

Hand control to the technical owner for implementation, proof, publication, or lifecycle work.

## Output policy

Do not force fixed headings into every response.

Use the smallest output that preserves reversibility. A full diagnostic response may use:

```text
Literal evidence
Sensory model
Engineering translation
Falsifiers
Next move
```

For implementation-lens mode, one short mapping card is usually enough.

## Durable memory events

Ordinary sensory output is not persisted. A durable event requires explicit user
endorsement, correction, rejection, or a reusable mapping/boundary request; without
explicit durability, require accepted use in at least two independent contexts
that changed diagnosis or explanation. Assistant novelty does not qualify.

When that gate is live, read [memory-admission.md](references/memory-admission.md)
before any canonical write or admission. Synesthesia owns canonical Ledger capture;
`$memory-source-notes` transports an accepted projection. Preserve prior identities,
engineering translation, activation/non-activation scope, and a verification rule.
A note or digest failure never rolls back a successful canonical write. Keep no-op
persistence evaluations out of ordinary diagnostic output.

## Guardrails

- Literal correctness outranks vividness.
- Metaphor never substitutes for tests, profiling, logs, traces, or proof.
- Repo-local vocabulary remains repo-local until broader evidence exists.
- Stable mappings are preferred over novelty.
- Never directly edit compiled memory.
- Never hand-write source notes as a fallback.
- Never use symlinks for live memory-extension instructions; synchronize them by copy through the documented adapter command.
- Never activate solely because another source or a terminal workflow reached closeout.
