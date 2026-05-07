---
name: prove-it
description: Ten-turn proof/disproof gauntlet for absolute claims. Default Auto Gauntlet consumes exactly one numbered round per assistant reply and withholds any final verdict until round 10, except when a Conclusive Proof Certificate proves the original normalized claim early.
---

# Prove It

## Purpose

Use this skill to stress-test absolute, sweeping, or suspiciously clean claims.

Typical activation cues:

- Certainty language: "always", "never", "guaranteed", "optimal", "cannot fail", "no downside", "100%".
- Explicit requests: "prove it", "disprove it", "devil's advocate", "stress test", "rigor", "find counterexamples".
- Claims whose truth depends on hidden quantifiers, edge cases, operating conditions, baselines, adversaries, comparative standards, or unstated definitions.

## Non-negotiable default

**Default mode is Auto Gauntlet.**

Auto Gauntlet means:

1. A normal prove-it run is **10 assistant turns**.
2. One assistant reply consumes exactly one numbered gauntlet round.
3. Rounds must be executed in numeric order, 1 through 10.
4. The assistant must not return a final verdict before round 10.
5. The only early-stop exception is a valid **Conclusive Proof Certificate** proving the **original normalized claim**.
6. Early disproof, a concrete counterexample, a fatal objection, or a likely failure does **not** end the gauntlet before round 10.
7. Non-terminal rounds must preserve state and require continuation at the next uncompleted round.

Do **not** default to Step mode.

Do **not** default to Single-Reply mode.

Do **not** provide Single-Reply mode.

Do **not** compress multiple rounds into one assistant reply.

Do **not** emit a final verdict before round 10 unless the current round establishes a Conclusive Proof Certificate.

Do **not** stop early merely because the claim appears false, weak, overbroad, probably wrong, or already defeated by a candidate counterexample.

## Core invariant

The prove-it engine must satisfy this condition before returning a final verdict:

```text
Final verdict is allowed only when:

completed_rounds == 10

OR

Conclusive Proof Certificate is valid for the original normalized claim.
```

No other condition permits a final verdict.

Specifically:

```text
Early PROVEN: allowed only with Conclusive Proof Certificate.
Early DISPROVEN: not allowed.
Early INSUFFICIENT: not allowed.
Early BOUNDED_ONLY: not allowed.
Early NOT_PROVEN: not allowed.
Early "probably true/false": not allowed.
```

If round 1 finds a concrete counterexample to a universal claim, record it as candidate fatal pressure, update the refined claim, and continue to round 2. The final verdict remains embargoed until round 10.

## Execution model

This is a single-agent, checkpointed, multi-turn conversation engine.

- One assistant reply = one engine turn.
- One engine turn consumes exactly one numbered gauntlet round.
- A normal gauntlet run is rounds 1-10.
- Rounds 1-9 attack, repair, narrow, or pressure-test the claim from different lenses.
- Round 10 performs Oracle synthesis and returns the final verdict if no Conclusive Proof Certificate ended the run earlier.
- State is persisted in `.prove-it-progress.md` when writable, otherwise in the latest inline `Checkpoint` block.

## Definitions

- **Original claim**: the user's claim as stated before stress testing.
- **Normalized claim**: the original claim rewritten with explicit quantifiers, scope, definitions, premises, and success criteria.
- **Refined claim**: the strongest surviving bounded version after attacks.
- **Engine turn**: one assistant reply that executes exactly one numbered round.
- **Gauntlet run**: the 10-round process.
- **Verdict embargo**: the rule forbidding a final verdict until round 10 unless a Conclusive Proof Certificate is valid.
- **Conclusive Proof Certificate**: decisive proof that the original normalized claim is true under its stated scope, with no unresolved blocking uncertainty and no remaining round able to materially change the result.
- **Candidate fatal pressure**: evidence, reasoning, or a counterexample that may ultimately defeat the claim but does not permit an early final verdict.
- **Oracle synthesis**: round 10 synthesis of the strongest surviving claim, all decisive pressures, boundaries, confidence, and final verdict.
- **Checkpoint**: structured state that lets the next turn resume without redoing completed rounds.

## Mode invocation

| Mode | Default? | User phrases | Cadence | Verdict rule |
|---|---:|---|---|---|
| Auto Gauntlet | yes | no phrase; "autoloop"; "auto gauntlet"; "one round per turn"; "full gauntlet" | exactly one numbered round per assistant reply; continue across turns until round 10 or Conclusive Proof Certificate | final verdict only at round 10 or early Conclusive Proof Certificate |
| Step mode | no | "step mode"; "pause each round"; "pause"; "step"; "wait after each round" | exactly one numbered round; then wait for explicit `next` / `continue` | final verdict only at round 10 or early Conclusive Proof Certificate |

There is no Single-Reply mode.

If the user asks for "continuous", "single reply", "all rounds now", "do it all in one response", or similar compression, do not compress the gauntlet. Treat the request as Auto Gauntlet and execute only the next numbered round.

If the user's phrase is ambiguous, prefer Auto Gauntlet.

## Host continuation requirement

A skill cannot assume that the platform will silently create new assistant turns.

Therefore every non-terminal Auto Gauntlet reply must emit a machine-readable continuation trailer that a host driver, automation, or user can submit back into the same conversation.

The required continuation prompt is:

```text
Continue prove-it from the checkpoint.
Execute exactly the next uncompleted numbered round only.
Do not return a final verdict unless this is round 10 or a Conclusive Proof Certificate is valid.
```

A host driver should keep sending that prompt until the checkpoint says `Status: COMPLETE`.

## Verdict embargo rules

Before round 10, the assistant may say:

- "candidate counterexample"
- "candidate fatal pressure"
- "this appears to defeat the claim, but the verdict remains embargoed"
- "the original claim is under severe pressure"
- "the refined claim is narrower"
- "this round found no decisive pressure"
- "continue to the next round"

Before round 10, the assistant must not say as a final conclusion:

- "Final verdict: disproven"
- "Final verdict: proven"
- "The claim is disproven"
- "The claim is false"
- "The claim is true"
- "We can stop because we found a counterexample"
- "No need for the remaining rounds"
- "Oracle synthesis"

The only exception is an early **Conclusive Proof Certificate** proving the original normalized claim.

## Conclusive Proof Certificate

A round may stop the gauntlet early only if it proves the original normalized claim.

A Conclusive Proof Certificate is valid only when all of the following are true:

1. The proof applies to the **original normalized claim**, not merely a weaker refined claim.
2. The claim's quantifiers, domain, definitions, and success criteria are explicit.
3. The proof method covers the whole normalized scope.
4. No known counterexample, boundary case, adversarial case, operational constraint, probabilistic uncertainty, or comparative baseline can materially change the result.
5. Blocking uncertainty is `none`.
6. The assistant can explain why every remaining unexecuted round would be redundant rather than potentially material.

Valid proof methods include:

- deductive proof;
- exhaustive finite verification over the full domain;
- direct derivation from a binding specification, theorem, contract, or authoritative source;
- constructive proof for an existential claim;
- decisive empirical proof only when the user's claim is explicitly empirical and the evidentiary standard is explicit and satisfied.

Invalid early-stop reasons include:

- the claim seems plausible;
- no counterexample was found yet;
- the assistant has high confidence;
- evidence is strong but scope remains open;
- the refined claim is true;
- the original claim is probably true;
- a counterexample disproves the claim;
- the user would probably accept the result;
- continuing would be tedious.

Important: **early disproof is not an allowed terminal condition**. Even a decisive-looking counterexample must be carried forward as candidate fatal pressure until round 10.

## Stop Check

Publish this after every round.

Before round 10, the Stop Check is not a final verdict unless it contains a valid Conclusive Proof Certificate.

```text
Stop Check:
Conclusive Proof Certificate present: <yes | no>

If yes:
  Applies to original normalized claim: <yes | no>
  Proof method:
  Full-scope coverage:
  Blocking uncertainty:
  Why remaining rounds cannot materially change this:
  Action: STOP_CONCLUSIVE_PROOF

If no:
  Verdict embargo: ACTIVE
  Candidate status: <pressure found | no new pressure | claim narrowed | candidate fatal pressure>
  Reason final verdict is not allowed yet:
  Action: CONTINUE_TO_ROUND_<N>
```

Rules:

- `Action: STOP_CONCLUSIVE_PROOF` is valid only with a complete Conclusive Proof Certificate.
- `Action: CONTINUE_TO_ROUND_N` is required for all non-proof rounds before round 10.
- If the round finds a counterexample, contradiction, or failure, set `Candidate status: candidate fatal pressure` and continue.
- If this is round 10, replace the embargoed Stop Check with the Oracle synthesis and final checkpoint.

## Default Auto Gauntlet cadence

For each assistant reply:

1. Read `.prove-it-progress.md` if present.
2. Otherwise read the latest inline `Checkpoint`.
3. If no checkpoint exists, initialize a new gauntlet from the user's claim.
4. Determine the next uncompleted numbered round.
5. Execute exactly that one round.
6. Publish:
   - round heading;
   - brief round analysis;
   - Round Ledger;
   - Knowledge Delta;
   - Stop Check;
   - Checkpoint;
   - Auto Gauntlet continuation trailer if non-terminal.
7. If a Conclusive Proof Certificate is valid, set `Status: COMPLETE`, `Completed engine turns: <N of 10>`, `Next round: none`, and stop.
8. If round 10 completes, publish Oracle synthesis, final verdict, final Checkpoint, and stop.
9. Otherwise set `Status: IN PROGRESS`, set the next round, and require continuation.

Never skip a round.

Never merge rounds.

Never emit Oracle synthesis before round 10.

Never continue after a valid Conclusive Proof Certificate.

Never return a final verdict before round 10 unless a valid Conclusive Proof Certificate proves the original normalized claim.

## Conversation rules

- In Auto Gauntlet mode, a plain continuation turn resumes at the next uncompleted round.
- In Auto Gauntlet mode, do not ask the user whether to continue unless essential information is missing.
- If essential information is missing, ask at most one question and do not consume a numbered round.
- A clarification turn does not count as one of the 10 gauntlet turns unless it executes a numbered round.
- If the user asks a meta-question about the gauntlet, answer the question without consuming a round unless the user explicitly asks to continue.
- If the user says `stop`, preserve the latest checkpoint and mark `Status: COMPLETE`, `Stop reason: USER_STOPPED`.
- If the user changes from Auto Gauntlet to Step mode or Step mode to Auto Gauntlet, preserve the current checkpoint and continue from the next uncompleted round.
- If the user asks for Single-Reply or Continuous mode, state that prove-it requires one round per assistant turn, then execute only the next round.
- If the claim changes materially mid-run, start a new gauntlet and reset the checkpoint.
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

## Progress file template

```markdown
# Prove It Progress

## Original claim

[verbatim]

## Normalized claim

[explicit quantifiers, scope, definitions, premises, success criteria]

## Mode

[auto-gauntlet | step]

## Status

[IN PROGRESS | COMPLETE]

## Verdict embargo

[ACTIVE | LIFTED_BY_ROUND_10 | LIFTED_BY_CONCLUSIVE_PROOF]

## Completed engine turns

[N of 10]

## Stop reason

[none | CONCLUSIVE_PROOF | ROUND_10_COMPLETE | USER_STOPPED]

## Current refined claim

[current strongest surviving bounded version]

## Candidate fatal pressures

- [pressure, counterexample, contradiction, or failure that may affect final verdict]

## Completed rounds

- Round 1 — Counterexamples: [not started | complete]
- Round 2 — Logic traps: [not started | complete]
- Round 3 — Boundary cases: [not started | complete]
- Round 4 — Adversarial inputs: [not started | complete]
- Round 5 — Alternative paradigms: [not started | complete]
- Round 6 — Operational constraints: [not started | complete]
- Round 7 — Probabilistic uncertainty: [not started | complete]
- Round 8 — Comparative baselines: [not started | complete]
- Round 9 — Meta-test: [not started | complete]
- Round 10 — Oracle synthesis: [not started | complete]

## Next round

[round number + focus | none]

## Round records

### Round N — [focus]

[Round Ledger]

[Knowledge Delta]

[Stop Check]

## Final verdict

[not allowed until round 10 unless Conclusive Proof Certificate]

## Continuation directive

If Status is IN PROGRESS, continue the same thread with:

"Continue prove-it from the checkpoint.
Execute exactly the next uncompleted numbered round only.
Do not return a final verdict unless this is round 10 or a Conclusive Proof Certificate is valid."
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

Do not ask the user unless blocked by missing essential facts.

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

Publish every round.

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
Effect on original claim:
Effect on refined claim:
Candidate fatal pressures carried forward:
Remaining gaps:
Verdict embargo status: <ACTIVE | LIFTED_BY_CONCLUSIVE_PROOF | LIFTED_BY_ROUND_10>
Next round:
```

### Knowledge Delta

Publish every round.

```text
Knowledge Delta:
- New:
- Updated:
- Invalidated:
```

### Stop Check

Publish every round before the Checkpoint.

```text
Stop Check:
Conclusive Proof Certificate present: <yes | no>

If yes:
  Applies to original normalized claim:
  Proof method:
  Full-scope coverage:
  Blocking uncertainty:
  Why remaining rounds cannot materially change this:
  Action: STOP_CONCLUSIVE_PROOF

If no:
  Verdict embargo: ACTIVE
  Candidate status:
  Reason final verdict is not allowed yet:
  Action: CONTINUE_TO_ROUND_<N>
```

### Checkpoint

Publish every Auto Gauntlet or Step mode round.

```text
Checkpoint:
Mode: <auto-gauntlet | step>
Status: <IN PROGRESS | COMPLETE>
Completed engine turns: <N of 10>
Completed round: <N>
Next round: <N+1 + focus | none>
Verdict embargo: <ACTIVE | LIFTED_BY_CONCLUSIVE_PROOF | LIFTED_BY_ROUND_10>
Stop reason: <none | CONCLUSIVE_PROOF | ROUND_10_COMPLETE | USER_STOPPED>
Current refined claim:
Candidate fatal pressures carried forward:
Resume rule:
```

### Auto Gauntlet continuation trailer

In Auto Gauntlet mode, publish this only when `Status: IN PROGRESS`.

```text
Auto Gauntlet Control:
status: IN_PROGRESS
completed_engine_turns: <N of 10>
next_round: <N+1>
resume_prompt: Continue prove-it from the checkpoint.
Execute exactly the next uncompleted numbered round only.
Do not return a final verdict unless this is round 10 or a Conclusive Proof Certificate is valid.
```

Do not publish the trailer when `Status: COMPLETE`.

## Oracle synthesis template

Round 10 must use this template unless the run has already ended with a Conclusive Proof Certificate.

```text
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

Confidence trail:
- Evidence:
- Counterpressure:
- Gaps:

Next tests:
- ...
```

Round 10 must explicitly account for candidate fatal pressures carried forward from earlier rounds.

## Completion contract

- Auto Gauntlet and Step mode replies consume exactly one numbered round.
- A reply with multiple numbered rounds is invalid.
- A reply that omits `Round Ledger`, `Knowledge Delta`, `Stop Check`, or `Checkpoint` is invalid.
- A non-terminal Auto Gauntlet reply that omits the Auto Gauntlet continuation trailer is invalid.
- A terminal reply must set `Status: COMPLETE` and `Next round: none`.
- A terminal reply before round 10 is valid only with `Stop reason: CONCLUSIVE_PROOF`.
- A round 10 terminal reply must set `Stop reason: ROUND_10_COMPLETE`.
- A non-terminal reply must set `Action: CONTINUE_TO_ROUND_N`.
- A final verdict before round 10 without a Conclusive Proof Certificate is invalid.
- A disproof before round 10 is invalid as a final verdict, even if the evidence appears decisive.

## Regression guards

These cases define expected behavior and are part of the skill contract.

### Universal claim counterexample in round 1

Input claim: "All swans are white."

Expected round 1 behavior:

- Identify a black swan as candidate fatal pressure.
- Do **not** return `Final verdict: DISPROVEN`.
- Set `Verdict embargo: ACTIVE`.
- Set `Action: CONTINUE_TO_ROUND_2`.

Expected round 10 behavior:

- Resolve the candidate fatal pressure.
- Return the final verdict only in Oracle synthesis.

### Strong but incomplete evidence before round 10

Input claim: "This algorithm is always optimal."

Expected behavior before round 10:

- Treat any apparent proof as non-terminal unless it satisfies every Conclusive Proof Certificate condition.
- Treat any failing instance as candidate fatal pressure, not early disproof.
- Continue to the next numbered round.

### Valid early proof

Input claim: "For every integer n, n + 0 = n."

Expected behavior:

- The assistant may stop early only if it supplies a Conclusive Proof Certificate covering the original normalized claim over the integer domain.
- The certificate must state why remaining rounds cannot materially change the result.
- Set `Status: COMPLETE`, `Stop reason: CONCLUSIVE_PROOF`, and `Next round: none`.

### Compression request

Input request: "Do all ten rounds in one response."

Expected behavior:

- Reject compression implicitly by following Auto Gauntlet.
- Execute exactly the next uncompleted numbered round only.
- Emit the Auto Gauntlet continuation trailer.

## Deliverable format

### Auto Gauntlet / Step mode

Use this structure:

```text
Round N — [Focus]

[brief round analysis]

Round Ledger:
...

Knowledge Delta:
...

Stop Check:
...

Checkpoint:
...

Auto Gauntlet Control:
...
```

Omit `Auto Gauntlet Control` in Step mode and in terminal Auto Gauntlet replies.

### Round 10

Use this structure:

```text
Round 10 — Oracle synthesis

[brief synthesis]

Round Ledger:
...

Knowledge Delta:
...

Oracle synthesis:
...

Checkpoint:
...
```

Do not include `Auto Gauntlet Control` after round 10.

## Anti-shortcut rules

1. Do not present a top-level final verdict before round 10 unless a Conclusive Proof Certificate is valid.
2. Do not stop early for disproof.
3. Do not stop early for a concrete counterexample.
4. Do not stop early for a contradiction unless it is part of a proof that the original normalized claim is true.
5. Do not stop early because the answer is obvious.
6. Do not stop early because the assistant is confident.
7. Do not stop early because the refined claim is now plausible.
8. Do not treat prior prose as implicitly satisfying skipped rounds.
9. Do not rerun completed rounds unless the user explicitly asks to revisit them.
10. Do not let a weaker refined claim obscure whether the original normalized claim has been proven.
11. Do not emit Oracle synthesis before round 10.
12. Preserve state before switching modes, stopping, or handling a meta-question.
13. If a host driver asks to continue and the checkpoint is already complete, report that the gauntlet is complete and do not run another round.
14. If a host driver asks to continue before round 10 and no Conclusive Proof Certificate exists, execute exactly the next round.
15. Keep each round compact: terse bullets and phrase-level evidence are preferred.

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
- "one round per turn"
- "autoloop"
- "auto gauntlet"
