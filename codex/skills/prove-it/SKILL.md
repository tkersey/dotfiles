---
name: prove-it
description: "Automatically run a ten-turn proof/disproof gauntlet for absolute claims. A valid run uses the bundled host loop to create exactly 10 separate assistant turns, one numbered round per turn; round 10 is the oracle and the only terminal verdict."
---

# Prove It

## Purpose

Use this skill to stress-test absolute, sweeping, or suspiciously clean claims.

Typical activation cues:

- Certainty language: "always", "never", "guaranteed", "optimal", "cannot fail", "no downside", "100%".
- Explicit requests: "prove it", "disprove it", "devil's advocate", "stress test", "rigor", "find counterexamples".
- Claims whose truth depends on hidden quantifiers, edge cases, operating conditions, baselines, adversaries, comparative standards, or unstated definitions.

## Core contract

A valid prove-it run is an **Auto Gauntlet**:

1. exactly 10 assistant turns;
2. exactly one numbered round per assistant turn;
3. rounds execute in numeric order, 1 through 10;
4. rounds 1-9 attack, repair, narrow, or pressure-test the claim;
5. round 10 is the Oracle synthesis and the only place a final verdict may appear;
6. early proof, early disproof, a counterexample, contradiction, or high confidence never stops the run;
7. step, pause, manual-next, one-round, partial, and single-reply modes are invalid.

The user-facing phrase "prove it" means **launch the host loop**, not "do ten sections in this reply" and not "run one round and wait".

## Two-state execution model

### 1. Launcher state: no driver marker is present

When a user invokes `$prove-it`, says "prove it", or otherwise asks for this skill on a claim and the prompt does **not** contain:

```text
Driver: PROVE_IT_AUTOTURN_V1
```

then do **not** execute a numbered round in the current reply.

Instead, launch the bundled host driver when shell/tool execution is available:

```bash
codex/skills/prove-it/scripts/prove-it "<claim>"
```

This is the automatic loop. The driver creates one initial Codex turn and nine same-thread continuation turns. It validates each turn and exits non-zero if the assistant compresses rounds, stops early, or emits a premature verdict.

If shell/tool execution is unavailable, emit exactly:

```text
PROVE_IT_REQUIRES_AUTOTURN_DRIVER

Run:
codex/skills/prove-it/scripts/prove-it "<claim>"
```

Then stop.

Direct invocation is valid only as a **launcher request**. Direct invocation is never valid as a numbered-round execution request.

### 2. Driver state: driver marker is present

When the prompt contains:

```text
Driver: PROVE_IT_AUTOTURN_V1
```

execute exactly the next uncompleted numbered round and stop. Do not ask whether to continue; the host driver owns continuation.

A valid driver prompt either starts round 1 from a claim or resumes from the latest checkpoint. If no checkpoint exists, initialize the gauntlet and run round 1 only. If a checkpoint exists, resume at `Next round` only.

## Final-verdict invariant

A final verdict is allowed only when all are true:

```text
completed_engine_turns == 10
completed_rounds == {1,2,3,4,5,6,7,8,9,10}
current_round == 10
```

Before round 10, the assistant may record:

- candidate counterexample;
- candidate fatal pressure;
- candidate decisive proof pressure;
- claim narrowed;
- pressure found but verdict embargoed;
- no new pressure found.

Before round 10, the assistant must not say, as a final conclusion:

- `Final verdict:`;
- `Oracle synthesis:`;
- `The claim is true`;
- `The claim is false`;
- `The claim is proven`;
- `The claim is disproven`;
- `We can stop`;
- `No need for the remaining rounds`;
- `Action: STOP`;
- `Action: STOP_CONCLUSIVE_PROOF`.

## Canonical resume prompt

The driver submits this prompt for rounds 2-10:

```text
Driver: PROVE_IT_AUTOTURN_V1

Continue prove-it from the checkpoint.
Execute exactly the next uncompleted numbered round only.
Do not execute more than one round in this reply.
Do not ask whether to continue.
Do not pause for user input.
Do not return a final verdict unless executing round 10.
Do not stop for proof, disproof, counterexample, contradiction, confidence, likely failure, or user-requested cadence changes.
If the checkpoint is already complete at 10 of 10, report completion and do not run another round.
```

## Ten-round gauntlet

1. **Counterexamples**: find the smallest concrete case that pressures or breaks the original claim.
2. **Logic traps**: expose missing quantifiers, unstated premises, invalid inferences, circularity, or category errors.
3. **Boundary cases**: test zero, one, maximum, empty, pathological, extreme-scale, or degenerate cases.
4. **Adversarial inputs**: test worst-case distributions, strategic manipulation, abuse, hostile users, or bad-faith incentives.
5. **Alternative paradigms**: switch objective functions, models, values, or worldviews and see whether the conclusion flips.
6. **Operational constraints**: test latency, cost, compliance, integration, maintainability, availability, policy, and organizational hard stops.
7. **Probabilistic uncertainty**: test variance, tail risk, base rates, sampling bias, uncertainty intervals, and distribution shift.
8. **Comparative baselines**: ask "better than what?", against which counterfactual, on which metric, with which trade-offs.
9. **Meta-test**: design the fastest disproof experiment or decisive information-gathering test.
10. **Oracle synthesis**: return the final verdict, tightest surviving claim, boundaries, confidence trail, and next tests.

## Round self-prompt bank

Use exactly the self-prompt matching the current numbered round.

- Counterexamples: What is the smallest input, case, or scenario that pressures or breaks the original claim?
- Logic traps: Which hidden assumption, quantifier shift, invalid inference, or definition problem must hold?
- Boundary cases: Which edge boundary is most plausible in real use?
- Adversarial inputs: What does worst-case, strategic, abusive, or hostile input look like?
- Alternative paradigms: What objective, worldview, model, or value system makes the opposite conclusion reasonable?
- Operational constraints: Which dependency, policy, system limit, organizational constraint, or integration constraint is a hard stop?
- Probabilistic uncertainty: What distribution shift, tail event, base-rate error, sampling bias, or variance flips the result?
- Comparative baselines: Better than what, on which metric, under which counterfactual, and with which trade-offs?
- Meta-test: What experiment or observation would change the final verdict fastest?
- Oracle synthesis: What final verdict is justified after all prior pressure, and what boundaries keep it honest?

## Required output schema

The host driver validates this schema after every assistant turn. Prefer exact labels.

### Rounds 1-9

```text
Round N — <Focus>

<brief round analysis>

Round Ledger:
Round: N
Engine turn: N of 10
Focus:
Original claim:
Normalized claim:
Claim scope:
Current refined claim entering round:
Attack summary:
New evidence:
New candidate counterexample or pressure:
New candidate decisive proof pressure:
Effect on original claim:
Effect on refined claim:
Candidate fatal pressures carried forward:
Candidate decisive proof pressures carried forward:
Remaining gaps:
Verdict embargo status: ACTIVE
Next round: N+1 — <Focus>

Knowledge Delta:
- New:
- Updated:
- Invalidated:

Continuation Gate:
Round completed: N of 10
Final verdict allowed: no
Candidate status: <pressure found | no new pressure | claim narrowed | candidate fatal pressure | candidate decisive proof pressure>
Reason terminal output is not allowed yet:
Action: AUTO_CONTINUE_TO_ROUND_<N+1>

Checkpoint:
Driver: PROVE_IT_AUTOTURN_V1
Mode: auto-gauntlet-only
Status: IN PROGRESS
Completed engine turns: N of 10
Completed round: N
Next round: N+1 — <Focus>
Verdict embargo: ACTIVE
Stop reason: none
Current refined claim:
Candidate fatal pressures carried forward:
Candidate decisive proof pressures carried forward:
Resume rule:
```

### Round 10

```text
Round 10 — Oracle synthesis

<brief synthesis>

Round Ledger:
Round: 10
Engine turn: 10 of 10
Focus: Oracle synthesis
Original claim:
Normalized claim:
Claim scope:
Current refined claim entering round:
Attack summary:
New evidence:
New candidate counterexample or pressure:
New candidate decisive proof pressure:
Effect on original claim:
Effect on refined claim:
Candidate fatal pressures carried forward:
Candidate decisive proof pressures carried forward:
Remaining gaps:
Verdict embargo status: LIFTED_BY_ROUND_10
Next round: none

Knowledge Delta:
- New:
- Updated:
- Invalidated:

Continuation Gate:
Round completed: 10 of 10
Final verdict allowed: yes
Candidate status:
Reason terminal output is not allowed yet: none
Action: COMPLETE_ROUND_10

Oracle synthesis:
Original claim:
Normalized claim:
Completed engine turns: 10 of 10
Verdict embargo: LIFTED_BY_ROUND_10

Final verdict:
- Outcome: <PROVEN | DISPROVEN | NOT_PROVEN | INSUFFICIENT_EVIDENCE | BOUNDED_CLAIM_SURVIVES>
- Verdict statement:
- Decisive reasons:

Tightest surviving claim:

Valid when:
- ...

Invalid when:
- ...

Candidate fatal pressures resolved:
- ...

Candidate decisive proof pressures resolved:
- ...

Confidence trail:
- Evidence:
- Counterpressure:
- Gaps:

Next tests:
- ...

Checkpoint:
Driver: PROVE_IT_AUTOTURN_V1
Mode: auto-gauntlet-only
Status: COMPLETE
Completed engine turns: 10 of 10
Completed round: 10
Next round: none
Verdict embargo: LIFTED_BY_ROUND_10
Stop reason: ROUND_10_COMPLETE
Current refined claim:
Candidate fatal pressures carried forward:
Candidate decisive proof pressures carried forward:
Resume rule: complete
```

## Heading rule

A reply must contain exactly one top-level `Round N — <Focus>` heading. Do not put additional top-level `Round N` headings inside the Checkpoint or historical records. If historical records are needed, name them `Round record N`.

The validator ignores nested `### Round N` headings for compatibility, but new outputs should not rely on that compatibility path.

## State and recovery

Preferred durable state file:

```text
.prove-it-progress.md
```

Use the project root when writable. If the workspace is read-only or no project root is available, preserve state in the inline `Checkpoint` block. The progress file is authoritative when present; otherwise the latest inline `Checkpoint` is authoritative.

## Regression guards

### Direct launch request

Input request: `Use prove-it on this claim: all swans are white.`

Expected behavior when no driver marker is present:

- do not execute round 1 in the current reply;
- launch `codex/skills/prove-it/scripts/prove-it "all swans are white"` when shell/tool execution is available;
- if shell/tool execution is unavailable, emit `PROVE_IT_REQUIRES_AUTOTURN_DRIVER` plus the command.

### Step, pause, or compression request

Inputs:

- `Run round 1 and wait for me.`
- `Do all ten rounds in one response.`

Expected behavior:

- never execute a numbered round without the driver marker;
- never compress multiple rounds into one reply;
- route to the host driver when tool execution is available, or emit the driver-required fallback.

### Universal claim counterexample in round 1

Input claim: `All swans are white.`

Expected round 1 behavior under the host driver:

- identify black swans as candidate fatal pressure;
- do not return `Final verdict: DISPROVEN`;
- set `Verdict embargo: ACTIVE`;
- set `Action: AUTO_CONTINUE_TO_ROUND_2`.

Expected round 10 behavior:

- resolve the candidate fatal pressure;
- return the final verdict only in Oracle synthesis.

### Valid-looking early proof still runs all rounds

Input claim: `For every integer n, n + 0 = n.`

Expected behavior:

- record candidate decisive proof pressure before round 10;
- continue all rounds;
- let round 10 decide whether the proof survives all lenses.

### Early terminal strings are invalid

Invalid before round 10:

- `Status: COMPLETE`
- `Final verdict:`
- `Oracle synthesis:`
- `Terminal verdict: PROVEN`
- `Terminal verdict: DISPROVEN`
- `Action: STOP`
- `Action: STOP_CONCLUSIVE_PROOF`
