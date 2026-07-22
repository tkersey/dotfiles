# Depth and Deliberation Doctrine Probes

## Contents

- doctrine-mode triggers
- operator distinctions and stacks
- terse activation phrases
- operational non-triggers

## Should trigger doctrine mode

```text
What is a doctrine word for dig deeper beneath the first plausible explanation?
```

Expected:

- `excavatory`
- likely companions: `etiological`, `dispositive`, `forensic`, or `invariant-seeking`
- distinguish depth that changes the route from analysis that merely grows longer

```text
What is a doctrine word for staying productively inside an unresolved contradiction instead of forcing closure?
```

Expected:

- `aporetic`
- likely companions: `dialectical`, `calibrated`, `adjudicative`
- distinguish productive non-closure from indecision or blocking

```text
What words are adjacent to ruminate?
```

Expected candidates:

- `aporetic`
- `ruminative`
- `deliberative`
- `dialectical`
- `incubative`
- `recursive`
- `metacognitive`
- `circumspective`
- `abductive`
- `synoptic`
- `contemplative`
- `percolative`
- `reflective`
- explain that `aporetic` is the sharpest word when the unresolved difficulty itself must remain open

```text
I want to trace the bug through symptoms, mechanisms, hidden assumptions, and the owning invariant.
```

Expected:

- `excavatory`
- companions: `etiological`, `mechanistic`, `invariant-seeking`, `dispositive`
- optional artifact: Excavation Trace

## Distinction probes

```text
Is excavatory just a sophisticated way to say exhaustive?
```

Expected:

- no
- `excavatory` descends through explanatory layers
- `exhaustive` covers all material cases or branches
- one can be excavatory without being exhaustive, and exhaustive without reaching a deeper causal layer

```text
Is aporetic just indecisive?
```

Expected:

- no
- `aporetic` deliberately preserves a genuine unresolved difficulty so it can be characterized or dissolved
- indecision lacks a productive tension, evidence plan, or exit condition

```text
Should I use etiological or excavatory for root-cause analysis?
```

Expected:

- `etiological` when the task is specifically causal origin
- `excavatory` when descent may cross causal, representational, historical, ownership, or invariant layers
- combine them when both explanatory depth and causal origin matter

```text
Should I use ruminative or aporetic?
```

Expected:

- `ruminative` for sustained reconsideration in general
- `aporetic` when a named contradiction or underdetermination must not be prematurely collapsed

```text
Give me a stack for a hard unresolved design choice.
```

Expected:

- `APORETIC + DIALECTICAL + ADJUDICATIVE`
- preserve the live contradiction before issuing a criteria-backed disposition

```text
Give me a stack for tracing a symptom to the layer that should own the fix.
```

Expected:

- `EXCAVATORY + ETIOLOGICAL + DISPOSITIVE`
- distinguish explanatory descent, causal origin, and the decisive owner layer

## Activation phrase probes

```text
Give me the shortest doctrine phrase for digging below the obvious layer.
```

Expected runtime output:

```text
Be excavatory.
```

```text
Give me the shortest doctrine phrase for resisting premature closure around a real contradiction.
```

Expected runtime output:

```text
Be aporetic.
```

Do not automatically append the Excavation Trace or Aporia Map unless the user asks for unpacking or the receiving workflow needs a handoff artifact.

## Should not trigger logophile operational ownership

```text
Investigate this production failure and fix it.
```

This is an operational debugging/remediation task. `$logophile` may supply doctrine terminology only when requested; it must not replace the owning investigation or implementation workflow.

```text
Decide which of these two designs to implement.
```

This is an operational design decision. `aporetic` may describe the posture, but `$logophile` must not make the decision unless the user asks specifically for doctrine wording or naming.
