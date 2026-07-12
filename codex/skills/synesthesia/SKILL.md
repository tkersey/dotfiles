---
name: synesthesia
description: "Reversible cross-modal diagnostic lens for software. Use when the user asks what code, architecture, behavior, logs, APIs, or alternatives feel, sound, look, or move like; for compare-by-feel analysis; when literal analysis leaves multiple plausible structural, temporal, interaction, or boundary interpretations that cross-modal recoding could distinguish; or after an owning technical workflow documents such an ambiguity. Start from literal evidence and translate every sensory statement into a technical hypothesis, uncertainty, falsifier, and next move. Not for ordinary architecture, performance, readability, or UX audits; exact syntax; legal/compliance or security sign-off; or code mutation by itself."
metadata:
  version: "3.4.0"
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
- a strange bug.

Those domains have their own technical owners. Synesthesia participates only when the representational lens is itself useful.

Do not use for exact syntax, legal or compliance interpretation, security sign-off, rote edits, or literal-only tasks.

## Ownership and handoffs

Synesthesia may shape diagnosis or explanation, but it does not displace the owning workflow:

- measured performance work -> `$lift`;
- structural or categorical architecture -> `$universalist`;
- local comprehension and refactoring preflight -> `$complexity-mitigator`;
- security, UX, API, CLI, copy, or performance audit -> `$codebase-audit`;
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

Most sensory output must not become memory.

When this workflow reaches a native Ledger command, load `$ledger` and complete
`$ledger ensure` once. After readiness, invoke `ledger` directly.

A durable memory event exists when the user explicitly:

- says `remember this`, `save this`, `from now on`, or equivalent;
- defines `when I say <phrase>, it means <technical pattern>`;
- endorses a mapping as correct and reusable;
- reuses an existing mapping in a new context and explicitly accepts it again;
- corrects or rejects a prior mapping;
- defines, changes, retracts, or reopens a durable activation or non-activation boundary.

Repeated accepted operational use without an explicit durability phrase may qualify only across at least two independent contexts and with evidence that the mapping changed diagnosis or explanation.

When a durable memory event exists:

1. classify it as endorsement, confirmation, correction, rejection, activation boundary, boundary retraction, or reopening;
2. identify the narrowest reusable scope;
3. require an engineering translation and verification rule;
4. identify the prior `SYN-*` ledger ID or `MSN-*` source-note ID for confirmation, correction, rejection, retraction, or reopening when one exists;
5. run `ledger doctor --source synesthesia`;
6. append the canonical row with `ledger capture --source synesthesia --kind <kind> --json -`;
7. when global memory admission is warranted, load `$memory-source-notes`, export with `ledger export --source synesthesia --format memory-note --id <SYN-ID>`, and use the Synesthesia source-note adapter in the same turn;
8. emit separate canonical and admission proof lines.

Do not merely describe a qualifying memory event without attempting the handoff.

Do not emit a `memory-note: not-attempted` line during ordinary Synesthesia use. Emit a proof line only when the user requested persistence, supplied a durable event, or the admission gate was materially evaluated.

## Lifecycle candidate pass

When Synesthesia is evaluated because `$learnings` lifecycle capture fired, do
not stop at `ledger doctor --source synesthesia` or at the absence of explicit
durable authority. Run a candidate pass over the learning, evidence, route
delta, and final handoff:

1. If a durable memory event exists, append it through
   `ledger capture --source synesthesia` and emit the append proof.
2. If no durable authority exists but the turn exposes a reusable sensory
   phrase, activation boundary, or representational ambiguity with a concrete
   engineering translation, emit a non-durable candidate.
3. Only if neither a durable event nor a useful candidate exists, emit
   `synesthesia: 0 records appended: <specific reason>`.

A lifecycle candidate must be compact and reversible:

```text
synesthesia: candidate: phrase="<sensory phrase>" translation="<engineering meaning>" needs=user-endorsement
```

Include or nearby state the evidence, activation boundary, non-activation
boundary, verification/falsifier, and missing authority. A candidate is not a
ledger row, not a memory note, and not future authority. It is a proposal for
the user to endorse, correct, or reject.

Do not report `notes-only` as the substantive reason for zero capture. That is
a store migration state, not a Synesthesia judgment. Import notes only when an
explicit copy migration is intended.

## Memory admission gate

Explicit durable user authority is sufficient for intended persistence. It does not also require repetition.

Without explicit durable authority, require repeated accepted use across at least two independent contexts.

Every admitted mapping or boundary must contain:

- sensory phrase when a phrase is being mapped;
- concrete engineering translation;
- activation boundary;
- non-activation boundary;
- narrow envelope scope;
- explicit or repeated-accepted authority;
- source references;
- reversible verification rule;
- prior note relationship when changing an existing mapping.

Do not capture:

- one-off poetic phrases;
- assistant novelty;
- transient incidents;
- ambient UI colors or passive screen context;
- mappings with no engineering translation;
- ordinary technical facts better owned by learnings;
- failed-route exclusions better owned by negative ledger;
- general operating corrections are outside Synesthesia scope unless they establish a sensory mapping or activation boundary.

See [memory-admission.md](references/memory-admission.md) for the operation matrix, payload contract, copy-based adapter synchronization, digest projection, and doctor workflow.

## Canonical Store

```text
ledger --source synesthesia
```

Use native Synesthesia source commands for canonical repo-local reads, writes,
and diagnostics. `.ledger/synesthesia/events.jsonl` is the current persistent
adapter location, not a caller contract; do not open or hand-edit it in normal
operation. Existing immutable Synesthesia memory-source notes remain valid
transition evidence; import them with
`ledger migrate --source synesthesia --mode copy` only when an explicit copy
migration is intended.

## Generated current-state digest

A successful Synesthesia memory-source admission refreshes this regular-file materialized view automatically:

```text
${CODEX_HOME:-$HOME/.codex}/memories/extensions/synesthesia/resources/latest_synesthesia_digest.md
```

The digest folds immutable `assert`, `confirm`, `supersede`, `reject`, `retract`, and `reopen` events into the current active mappings and activation boundaries. It also preserves inactive entries, invalid notes, and unresolved event chains.

The digest is disposable and non-canonical. Every promotable entry must retain resolvable `source_note_ids`; immutable notes remain authoritative. A digest-generation failure must never invalidate or roll back a successful source-note append.

Manual refresh:

```bash
ledger memory-digest --source synesthesia
```

Run the doctor after copy-deploying the Phase 2 adapter or when promotion appears stale:

```bash
ledger doctor --source synesthesia
```

## Cross-extension ownership

- evidence-backed execution learning -> `$learnings`;
- failed-hypothesis exclusion or reopening -> `$negative-ledger`;
- endorsed sensory mapping or sensory activation boundary -> `$synesthesia`;
- immutable source-note transport -> `$memory-source-notes`.

## Guardrails

- Literal correctness outranks vividness.
- Metaphor never substitutes for tests, profiling, logs, traces, or proof.
- Repo-local vocabulary remains repo-local until broader evidence exists.
- Stable mappings are preferred over novelty.
- Never directly edit compiled memory.
- Never hand-write source notes as a fallback.
- Never use symlinks for live memory-extension instructions; synchronize them by copy through the documented adapter command.
