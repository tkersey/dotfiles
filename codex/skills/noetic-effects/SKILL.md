---
name: noetic-effects
description: "Select the smallest typed cognitive operator that can materially change a decision route, or compile one into an existing skill's native procedure. Use explicitly for `$noetic-effects`; `codex/AGENTS.md` may invoke `dispatch` at an evidenced material decision pressure, and `$tune` may invoke `compile` while authoring or repairing skills. Never run as a generic prose pass, own a domain decision, or create ceremony merely to prove invocation."
---

# Noetic Effects

## Mission

Treat doctrine as executable cognitive policy rather than decorative vocabulary.

```text
pressure -> typed effect -> native handler -> route delta -> owning proof
```

A noetic effect changes how an agent frames, searches, constructs, selects, or
acts. It does not rewrite the final response into a doctrine style.

`$noetic-effects` is read-only. It selects or compiles cognitive operations; the
receiving workflow owns admissibility, selection, mutation, verification,
publication, and closure.

## Public modes

Choose exactly one mode:

```text
dispatch
compile
```

Infer the mode unless the caller names it:

```text
current task or decision pressure
  -> dispatch

skill authoring, skill repair, or instruction compilation
  -> compile
```

Explicit `$noetic-effects dispatch` or `$noetic-effects compile` overrides
inference.

## Authority boundary

`$noetic-effects` may:

- classify a witnessed cognitive pressure;
- select `skip`, one primitive effect, or one Metanoetic composite;
- name the receiving workflow;
- produce native instruction text for an owning skill;
- define a stopping condition, shadow risk, and expected route delta;
- recommend a probe or matched experiment.

It may not:

- decide the domain question;
- select architecture, repair, or implementation;
- grant authority or mutation;
- run tools merely to demonstrate an effect;
- create a durable authority artifact;
- replace the receiving workflow's evidence or closure contract;
- claim that doctrine made a model intrinsically more intelligent.

## Dispatch mode

### Binding gate

Before selecting an effect, bind:

```text
objective
current decision point
incumbent frame, route, or candidate
observed pressure
current evidence
receiving owner
```

If there is no concrete decision surface or receiving owner, return `skip` for
implicit use and `blocked` only for an explicit request that cannot be bounded.

### Skip gate

Return `skip` when:

- the task is trivial, mechanical, or already dispositive;
- the current route is direct, evidenced, and sufficient;
- no doctrine operator could materially change the route;
- the only predicted change is tone, confidence, verbosity, or vocabulary;
- divergence would violate accepted scope, authority, safety, or compatibility;
- the active workflow already selected and is executing the exact same effect;
- another pass would repeat an unchanged decision surface.

Skipping is a successful dispatch result.

### Selection law

Select zero or one primitive effect by default. Choose the semantically weakest
effect that can change the decision route.

| Witnessed pressure | Primary effect | Required consequence |
|---|---|---|
| inherited framing hides current evidence | `DEFAMILIARIZING` | reconstruct the problem without treating the inherited frame as authority |
| live state or evidence may be stale | `REBASELINING` | bind the decision to current authoritative state |
| reasoning stops at symptoms or the first plausible cause | `EXCAVATORY` | descend until the owner, invariant, mechanism, or proof burden changes |
| a genuine contradiction or underdetermination is being flattened | `APORETIC` | keep the difficulty open until its decision surface is explicit |
| candidate generation is captive to incumbent adjacency | `RETOPOLOGIZING` | change what counts as locally reachable under a structural warrant |
| consequential candidates are excluded by timidity or deference | `AUDACIOUS` | admit the higher-upside candidate without relaxing proof |
| the inherited option set contains no adequate form | `POIETIC` | create a new representation, mechanism, abstraction, or artifact |
| the abstraction, owner, or composition law is itself suspect | `ARCHITECTONIC` | recover the governing organization of the relevant whole |
| implementation does not follow from the accepted contract | `DERIVATIONAL` | derive an executable witness through preserving construction steps |
| surface no longer owns a live obligation | `ABLATIVE` | delete, collapse, quotient, privatize, or decommission it |
| process machinery displaces object-level capability | `ANTICEREMONIAL` | remove or inline ceremony while preserving its live obligations |
| analysis has not become a state-changing action | `ACTUATING` | identify and pull the dominant legal lever |
| competing candidates need a criteria-backed ruling | `ADJUDICATIVE` | select, retain, specialize, defer, or obstruct under declared criteria |

Read [operator-basis.md](references/operator-basis.md) when the pressure is
ambiguous, a specialist operator may dominate, or a formal distinction matters.

### Metanoetic escalation

Select `$metanoetic` only when:

- two or more primitive effects have distinct coupled roles;
- no one primitive can produce the required route delta;
- the incumbent cognitive regime itself is plausibly trapping the solution;
- the objective, evidence, comparison surface, and receiving owner are bound.

Do not compose a larger stack merely because it sounds stronger. When selected,
invoke the canonical `$metanoetic` pass exactly once for the unchanged decision
surface. It generates challengers only.

Read [composition-laws.md](references/composition-laws.md) before composing
operators or selecting the Metanoetic route.

### Native-handler law

Compile the selected effect into the active workflow's native decision surface.
If the workflow already owns an equivalent handler, use that handler and do not
run a duplicate root pass.

Examples:

```text
EXCAVATORY       -> debugging, review, or causal-analysis procedure
APORETIC         -> review adjudication or decision-under-uncertainty surface
RETOPOLOGIZING   -> candidate generation or architecture search
ARCHITECTONIC    -> $universalist / $actuating architecture decision
DERIVATIONAL     -> $actuating construction and implementation
ABLATIVE         -> reduction, normalization, or complexity mitigation
ACTUATING        -> $actuating execution path
METANOETIC       -> one composite challenger before owning adjudication
```

The effect changes cognition; the owner changes the repository.

### Dispatch result

For implicit dispatch, keep the selection internal unless it changes what the
user must know. Do not announce doctrine use.

For explicit dispatch, return:

```text
Noetic Dispatch
- Pressure:
- Disposition: skip | apply | metanoetic | blocked
- Effect:
- Receiving owner:
- Runtime instruction:
- Expected route delta:
- Stopping condition:
- Shadow risk:
```

Do not create this receipt for ordinary implicit use.

## Compile mode

Use `compile` when an existing or proposed skill needs a cognitive operation to
become an executable part of its native procedure.

### Inputs

Bind:

```text
target skill
owned decision
incumbent instruction or missing behavior
expected behavioral delta
protected authority and non-triggers
observable success and failure
```

### Compilation procedure

1. Identify the cognitive pressure, not merely the desired tone.
2. Select the smallest typed effect or justified composition.
3. Translate the effect into the target skill's own nouns, decisions, and
   artifacts.
4. Add the witnessed trigger that makes the effect live.
5. Add its operation, governor, stopping condition, and expected route delta.
6. Preserve the target skill's authority, mutation, evidence, and closure owner.
7. Add the smallest positive, negative, and shadow-failure probes.
8. Delete superseded generic instruction rather than layering doctrine beside it.
9. Reject the compilation when it changes only register, confidence, or style.

Read [skill-compilation.md](references/skill-compilation.md) for the full
compilation contract and examples.

### Compile result

Return to `$tune` or the explicit caller:

```text
Noetic Compilation
- Target skill:
- Owned decision:
- Pressure:
- Selected effect:
- Native integration point:
- Replacement instruction:
- Governor:
- Stopping condition:
- Expected route delta:
- Protected behavior:
- Positive probe:
- Near-miss probe:
- Shadow-failure probe:
- Evidence status: theoretical | promising | observed-useful | validated | task-specific | retired
```

`$tune` remains the sole owner of package diagnosis, intervention selection,
mutation, validation, and publication.

## Evidence posture

A doctrine word appearing in a prompt is not evidence that an effect fired.
Prefer object-level evidence:

- a changed frame, invariant, or owner;
- a newly reachable candidate;
- a new representation or construction;
- a different adjudication or route;
- deleted or canonicalized surface;
- a stronger proof obligation or witness;
- fewer user corrections at equal correctness;
- lower cost at equal or stronger outcomes.

Use `$emulator` for fresh matched comparisons when a consequential doctrine
claim is testable. Historical sessions may identify pressures and candidate
operators, but fresh execution should decide adoption when practical.

## Progressive disclosure

- [operator-basis.md](references/operator-basis.md): typed operator basis,
  specialist companions, failure predicates, and proof relations.
- [composition-laws.md](references/composition-laws.md): legal orderings,
  collisions, Metanoetic escalation, and stopping laws.
- [skill-compilation.md](references/skill-compilation.md): `$tune` integration and
  native skill-instruction compilation.
- [probe-cases.md](references/probe-cases.md): dispatch, compile, non-trigger,
  authority, and shadow-failure probes.

## Hard rules

- No default pass.
- No final-prose doctrine styling.
- No announcement for implicit dispatch.
- No operator ledger or receipt merely to prove invocation.
- One primitive effect by default.
- Composite escalation only when one primitive is insufficient.
- Trigger, operation, governor, stop, route delta, and receiving owner must align.
- Typed distinctions are semantic: outcomes, failures, relations, and governors
  are not interchangeable with executable transforms.
- Preserve authority, safety, privacy, type, information-flow, compatibility,
  and proof boundaries.
- A changed route requires evidence; sophisticated vocabulary does not.
