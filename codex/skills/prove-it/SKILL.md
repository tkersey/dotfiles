---
name: prove-it
description: Host-driven ten-turn proof/disproof gauntlet for absolute claims. A valid use always runs exactly 10 separate assistant turns, one numbered round per turn, through the bundled autoturn driver. No step, pause, incremental, single-reply, partial-run, or early-terminal mode is valid.
---

# Prove It

## Purpose

Use this skill to stress-test absolute, sweeping, or suspiciously clean claims.

Typical activation cues:

- Certainty language: "always", "never", "guaranteed", "optimal", "cannot fail", "no downside", "100%".
- Explicit requests: "prove it", "disprove it", "devil's advocate", "stress test", "rigor", "find counterexamples".
- Claims whose truth depends on hidden quantifiers, edge cases, operating conditions, baselines, adversaries, comparative standards, or unstated definitions.

## Non-negotiable execution contract

**Auto Gauntlet is the only valid mode, and it is host-driven.**

A valid prove-it run is exactly 10 assistant turns:

1. One assistant reply consumes exactly one numbered gauntlet round.
2. Rounds execute in numeric order, 1 through 10.
3. Round 10 is the only terminal round.
4. A final verdict is forbidden before round 10.
5. Early proof is not terminal.
6. Early disproof is not terminal.
7. A concrete counterexample is not terminal.
8. A user request to pause, step, run one round, wait, or continue manually is not a valid prove-it cadence.
9. A single-reply compression request is not valid.
10. Direct manual invocation without the bundled host autoturn driver is invalid.

The skill must not provide, imply, or simulate:

- step cadence;
- pause cadence;
- manual-next cadence;
- single-reply cadence;
- partial gauntlet cadence;
- early-stop proof cadence;
- early-stop disproof cadence;
- incremental continuation cadence.

If the host cannot automatically continue the same conversation/thread through round 10, the skill must not begin the gauntlet.

## Entrypoint contract

This skill is not valid as a manually incremental workflow.

The only valid entrypoint is the bundled host driver:

```text
codex/skills/prove-it/scripts/prove-it-autogauntlet.py "<claim>"
```

A valid host-driver prompt contains:

```text
Driver: PROVE_IT_AUTOTURN_V1
```

If this skill is invoked without `Driver: PROVE_IT_AUTOTURN_V1`, do not execute a numbered round. Emit exactly:

```text
PROVE_IT_REQUIRES_AUTOTURN_DRIVER

Run:
codex/skills/prove-it/scripts/prove-it-autogauntlet.py "<claim>"
```

Then stop.

Do not treat a direct user request such as "do one round", "pause", "step", "continue when I say next", "just run round 3", "stop after this", or "do it all in one response" as a supported mode.

If a host driver is active, ignore any requested alternate cadence and continue the required 10-turn Auto Gauntlet.

## Core invariant

The prove-it engine may return a final verdict only when:

```text
completed_engine_turns == 10
AND
completed_rounds == {1,2,3,4,5,6,7,8,9,10}
AND
current_round == 10
```

No other condition permits a final verdict.

Specifically, before round 10:

```text
Early PROVEN: not allowed.
Early DISPROVEN: not allowed.
Early INSUFFICIENT: not allowed.
Early BOUNDED_ONLY: not allowed.
Early NOT_PROVEN: not allowed.
Early "probably true/false": not allowed.
Early decisive proof: not terminal.
Early decisive disproof: not terminal.
Early counterexample: not terminal.
```

If any round finds decisive-looking proof or disproof, record it as carried-forward decisive pressure and continue.

## Execution model

This is a single-agent, checkpointed, host-driven, multi-turn conversation engine.

- One assistant reply = one engine turn.
- One engine turn consumes exactly one numbered gauntlet round.
- A full gauntlet run is rounds 1-10.
- Rounds 1-9 attack, repair, narrow, or pressure-test the claim from different lenses.
- Round 10 performs Oracle synthesis and returns the final verdict.
- State is persisted in `.prove-it-progress.md` when writable, otherwise in the latest inline `Checkpoint` block.
- The host driver is responsible for sending the continuation prompt for rounds 2-10.
- The assistant is responsible for executing exactly the current round and preserving checkpoint state.

## Definitions

- **Original claim**: the user's claim as stated before stress testing.
- **Normalized claim**: the original claim rewritten with explicit quantifiers, scope, definitions, premises, and success criteria.
- **Refined claim**: the strongest surviving bounded version after attacks.
- **Engine turn**: one assistant reply that executes exactly one numbered round.
- **Gauntlet run**: the 10-round process.
- **Verdict embargo**: the rule forbidding a final verdict until round 10.
- **Candidate fatal pressure**: evidence, reasoning, or a counterexample that may ultimately defeat the claim but does not permit an early final verdict.
- **Candidate decisive proof pressure**: proof-like evidence that may ultimately prove the original normalized claim but does not permit an early final verdict.
- **Oracle synthesis**: round 10 synthesis of the strongest surviving claim, all decisive pressures, boundaries, confidence, and final verdict.
- **Checkpoint**: structured state that lets the next turn resume without redoing completed rounds.

## Candidate decisive proof pressure

A round may discover proof-like evidence that appears to establish the original normalized claim.

Before round 10, such evidence is not terminal. It must be carried forward as `candidate decisive proof pressure`.

A candidate decisive proof pressure is strong only when all of the following are true:

1. It applies to the original normalized claim, not merely a weaker refined claim.
2. The claim's quantifiers, domain, definitions, and success criteria are explicit.
3. The proof method covers the whole normalized scope.
4. No known counterexample, boundary case, adversarial case, operational constraint, probabilistic uncertainty, or comparative baseline can materially change the result.
5. Blocking uncertainty is `none`.

Even when all criteria appear satisfied, the run continues to round 10. Round 10 decides whether the candidate proof survives all lenses.

## Verdict embargo rules

Before round 10, the assistant may say:

- "candidate counterexample";
- "candidate fatal pressure";
- "candidate decisive proof pressure";
- "this appears to defeat the claim, but the verdict remains embargoed";
- "this appears to prove the claim, but the verdict remains embargoed";
- "the original claim is under severe pressure";
- "the refined claim is narrower";
- "this round found no decisive pressure";
- "the driver will continue to the next round".

Before round 10, the assistant must not say as a final conclusion:

- "Final verdict: disproven";
- "Final verdict: proven";
- "The claim is disproven";
- "The claim is false";
- "The claim is true";
- "We can stop because we found a counterexample";
- "No need for the remaining rounds";
- "Oracle synthesis".

## Host continuation requirement

The host driver must keep submitting the canonical resume prompt until round 10 completes.

Canonical resume prompt:

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

The bundled driver validates the output contract after every assistant reply. A failed validation means the run is invalid and must be inspected from the generated artifacts.

## Default host-driven cadence

For each assistant reply:

1. Verify that the current prompt contains `Driver: PROVE_IT_AUTOTURN_V1`.
2. Read `.prove-it-progress.md` if present.
3. Otherwise read the latest inline `Checkpoint`.
4. If no checkpoint exists, initialize a new gauntlet from the user's claim and execute round 1.
5. Determine the next uncompleted numbered round.
6. Execute exactly that one round.
7. Publish:
   - round heading;
   - brief round analysis;
   - Round Ledger;
   - Knowledge Delta;
   - Continuation Gate;
   - Checkpoint.
8. If this is round 10, publish Oracle synthesis, final verdict, final Checkpoint, and stop.
9. Otherwise set `Status: IN PROGRESS`, set the next round, keep the verdict embargo active, and stop so the host driver can send the next turn.

Never skip a round.

Never merge rounds.

Never emit Oracle synthesis before round 10.

Never return a final verdict before round 10.

Never stop early for proof, disproof, counterexample, contradiction, confidence, or convenience.

## Conversation rules

- In a host-driven run, a continuation turn resumes at the next uncompleted round.
- Do not ask the user whether to continue.
- Do not ask the user for clarification during an active host-driven run unless the claim is literally absent or impossible to identify.
- A clarification turn does not count as one of the 10 gauntlet turns unless it executes a numbered round.
- If the user asks a meta-question outside a driver run, answer the question without consuming a round.
- If the claim changes materially mid-run, the current driver run is invalid. Do not silently continue under the old checkpoint.
- If context compacts, the progress file is authoritative. If there is no progress file, the latest inline `Checkpoint` is authoritative.

## State and recovery

Preferred durable state file:

```text
.prove-it-progress.md
```

Use the project root when writable.

If the workspace is read-only or no project root is available:

- keep the same state inline using the `Checkpoint` block;
- treat the latest `Checkpoint` as authoritative;
- resume from the `Next round` field.

The progress file is authoritative when present.

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

Do not ask the user unless blocked by a missing claim.

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

## Required artifacts

### Argument map

Use this internally when helpful.

Publish only when it clarifies the current round.

```text
Argument Map:
Claim:
Premises:
- P1:
- P2:
Hidden assumptions:
- A1:
Weak links:
- W1:
Candidate pressure tests:
- T1:
Refined claim:
```

### Round Ledger

Publish every numbered round.

```text
Round Ledger:
Round: <1-10>
Engine turn: <N of 10>
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
Verdict embargo status: <ACTIVE | LIFTED_BY_ROUND_10>
Next round:
```

### Knowledge Delta

Publish every numbered round.

```text
Knowledge Delta:
- New:
- Updated:
- Invalidated:
```

### Continuation Gate

Publish every numbered round before the Checkpoint.

```text
Continuation Gate:
Round completed: <N of 10>
Final verdict allowed: <yes only if N == 10, otherwise no>
Candidate status: <pressure found | no new pressure | claim narrowed | candidate fatal pressure | candidate decisive proof pressure>
Reason terminal output is not allowed yet:
Action: <AUTO_CONTINUE_TO_ROUND_N | COMPLETE_ROUND_10>
```

Rules:

- For rounds 1-9, `Final verdict allowed` must be `no`.
- For rounds 1-9, `Action` must be `AUTO_CONTINUE_TO_ROUND_<N+1>`.
- If the round finds proof, disproof, contradiction, or a counterexample, carry it forward and continue.
- Round 10 must set `Action: COMPLETE_ROUND_10`.

### Checkpoint

Publish every numbered round.

```text
Checkpoint:
Driver: PROVE_IT_AUTOTURN_V1
Mode: auto-gauntlet-only
Status: <IN PROGRESS | COMPLETE>
Completed engine turns: <N of 10>
Completed round: <N>
Next round: <N+1 + focus | none>
Verdict embargo: <ACTIVE | LIFTED_BY_ROUND_10>
Stop reason: <none | ROUND_10_COMPLETE>
Current refined claim:
Candidate fatal pressures carried forward:
Candidate decisive proof pressures carried forward:
Resume rule:
```

## Round output format

Rounds 1-9 must use this structure:

```text
Round N — [Focus]

[brief round analysis]

Round Ledger:
...

Knowledge Delta:
...

Continuation Gate:
...

Checkpoint:
...
```

Round 10 must use this structure:

```text
Round 10 — Oracle synthesis

[brief synthesis]

Round Ledger:
...

Knowledge Delta:
...

Continuation Gate:
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
...
```

Do not include an Auto Gauntlet control trailer. The host driver owns continuation.

## Completion contract

- A valid run has exactly 10 assistant turns.
- A valid reply consumes exactly one numbered round.
- A reply with multiple numbered rounds is invalid.
- A reply that omits `Round Ledger`, `Knowledge Delta`, `Continuation Gate`, or `Checkpoint` is invalid.
- A terminal reply before round 10 is invalid.
- A final verdict before round 10 is invalid.
- A disproof before round 10 is invalid as a final verdict, even if the evidence appears decisive.
- A proof before round 10 is invalid as a final verdict, even if the evidence appears decisive.
- A round 10 terminal reply must set `Status: COMPLETE`, `Next round: none`, `Verdict embargo: LIFTED_BY_ROUND_10`, and `Stop reason: ROUND_10_COMPLETE`.

## Regression guards

These cases define expected behavior and are part of the skill contract.

### Direct invocation is invalid

Input request: "Use prove-it on this claim: all swans are white."

Expected behavior when no driver marker is present:

- Do not execute round 1.
- Emit `PROVE_IT_REQUIRES_AUTOTURN_DRIVER`.
- Include the bundled driver command.

### Universal claim counterexample in round 1

Input claim: "All swans are white."

Expected round 1 behavior under the host driver:

- Identify black swans as candidate fatal pressure.
- Do not return `Final verdict: DISPROVEN`.
- Set `Verdict embargo: ACTIVE`.
- Set `Action: AUTO_CONTINUE_TO_ROUND_2`.

Expected round 10 behavior:

- Resolve the candidate fatal pressure.
- Return the final verdict only in Oracle synthesis.

### Strong but incomplete evidence before round 10

Input claim: "This algorithm is always optimal."

Expected behavior before round 10:

- Treat any apparent proof as non-terminal.
- Treat any failing instance as candidate fatal pressure, not early disproof.
- Continue to the next numbered round.

### Valid-looking early proof still runs all rounds

Input claim: "For every integer n, n + 0 = n."

Expected behavior:

- The assistant may record candidate decisive proof pressure.
- The assistant must not stop early.
- The assistant must not return a final verdict before round 10.
- Round 10 decides whether the proof survives all lenses.

### Compression request is invalid

Input request: "Do all ten rounds in one response."

Expected behavior:

- If no host driver is active, emit `PROVE_IT_REQUIRES_AUTOTURN_DRIVER`.
- If the host driver is active, execute exactly the current numbered round only.
- Never compress multiple rounds into one reply.

### Step or pause request is invalid

Input request: "Run round 1 and wait for me."

Expected behavior:

- If no host driver is active, emit `PROVE_IT_REQUIRES_AUTOTURN_DRIVER`.
- If the host driver is active, ignore the requested pause and continue the 10-turn host-driven gauntlet.

### Early terminal strings are invalid

Invalid before round 10:

- `Status: COMPLETE`
- `Final verdict:`
- `Oracle synthesis:`
- `Terminal verdict: PROVEN`
- `Terminal verdict: DISPROVEN`
- `Action: STOP`
- `Action: STOP_CONCLUSIVE_PROOF`

## Activation cues

- "always"
- "never"
- "guaranteed"
- "optimal"
- "cannot fail"
- "no downside"
- "100%"
- "prove it"
- "disprove it"
- "devil's advocate"
- "stress test"
- "rigor"
- "find counterexamples"
- "auto gauntlet"
