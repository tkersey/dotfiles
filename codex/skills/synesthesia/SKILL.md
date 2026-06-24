---
name: synesthesia
description: "Reversible cross-modal diagnostic lens for software. Use when the user asks what code, architecture, behavior, logs, APIs, or alternatives feel, sound, look, or move like; for compare-by-feel analysis; or after an owning technical workflow identifies a concrete ambiguity that spatial, temporal, tactile, thermal, visual, or auditory recoding may clarify. Start from literal evidence and translate every sensory statement into a technical hypothesis, uncertainty, falsifier, and next move. Not for ordinary architecture, performance, readability, UX, or debugging work by subject alone; exact syntax; legal/compliance or security sign-off; or code mutation by itself."
metadata:
  version: "3.0.0"
  activation_cost: low
  default_depth: adaptive
---

# Synesthesia

## Mission

Use a reversible sensory representation to expose or communicate software structure that a literal model has not made clear.

The sensory layer is a diagnostic instrument. It is not evidence, proof, a mandatory output style, or an implementation owner.

## Ownership

Synesthesia owns:

```text
literal observations
-> alternate sensory representation
-> dissonance or structural insight
-> engineering translation
-> falsifier
-> decision, explanation, or investigation delta
```

It does not own:

- profiling, benchmarking, or performance proof;
- architecture authority or categorical construction;
- security, legal, compliance, or correctness sign-off;
- code mutation, review closure, or delivery;
- memory-note command syntax or compiled-memory mutation.

The relevant technical workflow remains authoritative. Synesthesia may refine its model, not replace it.

## Activation boundary

### Use this skill when

At least one condition is true:

1. The user explicitly asks what an artifact feels, sounds, looks, moves, weighs, or behaves like in sensory terms.
2. The user asks to compare alternatives by feel, friction, texture, rhythm, weight, coherence, or another experiential axis.
3. An already-active owning workflow hands off a **named representational ambiguity** and explains why cross-modal recoding may distinguish competing interpretations.
4. A teaching or onboarding task explicitly benefits from a sensory mental model and the model can remain technically reversible.

### Do not activate by subject alone

These topics do not independently justify Synesthesia:

- architecture or system design;
- performance, latency, throughput, or memory;
- readability, maintainability, or refactoring;
- APIs, UX, CLI behavior, or onboarding;
- strange, flaky, concurrent, or intermittent behavior.

Route the literal task to its governing workflow first. Add Synesthesia only when the representation itself is expected to change the diagnosis, comparison, investigation order, or mental model.

### Hard non-triggers

Do not use Synesthesia for:

- exact API, command, or language syntax;
- legal or compliance interpretation;
- security sign-off;
- terse factual lookup;
- rote edits with no explanatory or diagnostic component;
- aesthetic rewriting that belongs to `$logophile`;
- metaphor requested as a substitute for evidence.

## Core contract

Always:

1. Start from literal evidence: code, tests, logs, traces, profiles, architecture, runtime behavior, user flow, or repository structure.
2. Separate observations from inferences before creating a sensory model.
3. Choose the **minimum sufficient modalities**, usually one or two. Add a modality only when it exposes an independent technical dimension.
4. Keep each mapping internally consistent for the current scope.
5. Mark uncertainty explicitly.
6. Translate every material sensory statement into concrete engineering terms.
7. Name what would falsify a diagnostic mapping.
8. State the resulting decision, explanation, or investigation delta.
9. Omit or compress the sensory layer when it produces no material delta.
10. Execute implementation and verification literally through the owning workflow.

Never:

- treat metaphor as evidence;
- invent unseen runtime facts;
- hide uncertainty in aesthetic language;
- repeat one conclusion through several decorative modalities;
- globalize a repo-local or user-local mapping without evidence;
- infer a durable preference from assistant-authored wording alone.

## Mapping record

Every material mapping must be reconstructible as:

```yaml
synesthetic_mapping:
  literal_observations: []
  sensory_model:
  modalities: []
  engineering_translation:
  uncertainty:
  falsifier:
  decision_delta:
  evidence_refs: []
```

A mapping with no evidence reference, engineering translation, falsifier, or meaningful delta is explanatory decoration, not a diagnostic result.

## Modes

Choose exactly one primary mode.

### Diagnose

Use when the goal is to distinguish causes or choose an investigation order.

Output:

```text
observations -> sensory model -> candidate mechanism -> falsifier -> next check
```

Do not present the candidate mechanism as a verified root cause.

### Explain

Use for onboarding or teaching when the user wants an intuitive mental model.

Output:

```text
literal system model -> sensory representation -> exact correspondence -> limits of the analogy
```

End with boundaries or misconceptions, not an obligatory change list.

### Compare

Use when two or more designs are evaluated experientially.

Use stable axes across all alternatives. Translate each axis into a technical tradeoff and end with the decision implication or unresolved tie.

### Implementation lens

Use only after another workflow owns the code change. Produce at most one route-shaping insight, then return to literal implementation and proof.

Synesthesia must not become a second implementation plan.

## Procedure

1. **Literal read** — identify components, flows, states, timing, boundaries, constraints, unknowns, and available evidence.
2. **Mode selection** — choose `diagnose`, `explain`, `compare`, or `implementation-lens`.
3. **Modality selection** — use [modality-selection.md](references/modality-selection.md) and select the minimum independent set.
4. **Sensory render** — describe only the structure supported by the evidence.
5. **Dissonance extraction** — identify the smallest mismatch, interference, discontinuity, congestion, drag, or ambiguity that matters.
6. **Engineering translation** — state the literal mechanism, uncertainty, and evidence.
7. **Falsification** — name the observation, command, trace, or code fact that would defeat the mapping.
8. **Delta** — state what changes: investigation order, architectural interpretation, comparison, explanation, or owning-workflow route.
9. **Stop or hand off** — do not continue adding modalities once the governing delta is clear.

## Cross-skill routing

| Literal task | Governing owner | Synesthesia role |
|---|---|---|
| Measured performance optimization | `$lift` | Explain a measured profile or temporal topology after evidence exists |
| Structural or categorical architecture | `$universalist` | Optional representation of worlds, boundaries, effects, or observations |
| Local comprehension and refactoring preflight | `$complexity-mitigator` | Optional representation of cognitive or structural friction |
| Security, UX, performance, API, copy, or CLI audit | `$codebase-audit` | Interpretive lane only; never evidence or severity authority |
| Wording and naming | `$logophile` | No role unless the user explicitly requests sensory explanation |
| Explicit feel/sound/look/texture comparison | `$synesthesia` | Governing skill |

When another skill owns the task, preserve its artifacts, terminology, proof obligations, and stop conditions.

## Output contract

Use the smallest useful form. A full diagnostic answer may use:

```text
Literal observations
- evidence-backed facts only

Sensory model
- one or two non-redundant modalities

Engineering translation
- concrete mechanism and uncertainty

Falsifier
- what would show the mapping is wrong

Delta
- next investigation, interpretation, decision, or handoff
```

Do not force headings for a brief implementation-lens or teaching answer.

## Memory admission boundary

Most sensory output must not become memory.

Evaluate admission only when the user explicitly endorses, corrects, rejects, retracts, or asks to remember a mapping or boundary, or when repeated accepted operational use is independently evidenced.

The Synesthesia skill owns only the admission decision and payload semantics. `$memory-source-notes` owns CLI discovery, safe writing, result parsing, and proof lines.

Before handoff:

1. Read [memory-admission.md](references/memory-admission.md).
2. Build the complete source-note envelope.
3. Run the skill-local preflight and canonicalizer.
4. Hand the canonical JSON bytes to `$memory-source-notes`.

Do not print a routine `memory-note: not-attempted` line when no durable event occurred. Mention memory only when the gate was materially evaluated or a write was requested.

## Subagents

Do not create or require a dedicated Synesthesia custom subagent.

When the user explicitly requests parallel analysis, a read-only worker may receive a bounded Synesthesia lane only if it is given:

- exact artifact state;
- literal observations or files to inspect;
- one representational question;
- required engineering translation and falsifier;
- no mutation authority.

The root integrates the result and owns all conclusions.

## Stop conditions

Stop the sensory pass when any condition holds:

- the mapping does not expose an independent technical dimension;
- a literal explanation is clearer;
- the governing insight and falsifier are already stated;
- evidence is insufficient to support further detail;
- the task has returned to implementation or proof;
- the user requested literal-only output.

## Validation

Run after changing this package:

```bash
uv run --with pyyaml python \
  codex/skills/synesthesia/scripts/validate_synesthesia.py all

uv run --with pyyaml python -m unittest discover \
  -s codex/skills/synesthesia/tests \
  -p 'test_*.py'

uv run --with pyyaml python \
  codex/skills/tune/tools/decision_contract_lint.py \
  codex/skills/synesthesia/references/decision-contract.yaml

uv run --with pyyaml python \
  codex/skills/.system/skill-creator/scripts/quick_validate.py \
  codex/skills/synesthesia
```
