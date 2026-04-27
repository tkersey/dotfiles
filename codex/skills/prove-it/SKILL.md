---
name: prove-it
description: Autonomous multi-turn proof/disproof gauntlet for absolute claims. Default Auto Gauntlet runs exactly one numbered round per assistant turn and auto-continues the same conversation until a terminal proof/disproof certificate or round 10 Oracle synthesis.
---

# Prove It

## Purpose

Use this skill to stress-test absolute, sweeping, or suspiciously clean claims.

Typical activation cues:

- Certainty language: "always", "never", "guaranteed", "optimal", "cannot fail", "no downside", "100%".
- Explicit requests: "prove it", "disprove it", "devil's advocate", "stress test", "rigor", "find counterexamples".
- Claims whose truth depends on hidden quantifiers, edge cases, operating conditions, baselines, or adversarial behavior.

## Non-negotiable default

**Default mode is Auto Gauntlet.**

Auto Gauntlet means:

1. Execute exactly one numbered gauntlet round per assistant reply.
2. Publish the required checkpoint after that round.
3. If the round establishes a terminal proof/disproof certificate, mark the run complete and stop.
4. If the round is non-terminal, mark the run in progress and require immediate continuation of the same conversation at the next uncompleted round.
5. Continue until either:
   - the original claim is proven;
   - the original claim is disproven;
   - the user explicitly stops;
   - or round 10 Oracle synthesis completes.

Do **not** default to Step mode.
Do **not** default to Single-Reply mode.
Do **not** collapse multiple numbered rounds into one assistant reply unless the user explicitly requests Single-Reply mode.
Do **not** stop at round 1 merely because one assistant reply has completed.

## Execution model

This is a single-agent, checkpointed, multi-turn conversation engine.

- One assistant reply = one engine turn.
- One engine turn consumes exactly one numbered gauntlet round, except in explicit Single-Reply mode.
- A gauntlet run is rounds 1-10.
- Rounds 1-9 attack the claim from different lenses.
- Round 10 performs Oracle synthesis if no earlier terminal certificate is reached.
- State is persisted in `.prove-it-progress.md` when writable, otherwise in the latest inline `Checkpoint` block.

### Host continuation requirement

A skill cannot assume that the platform will silently create new assistant turns. Therefore every non-terminal Auto Gauntlet reply must emit a machine-readable continuation trailer that a host driver, automation, or user can submit back into the same conversation.

The required continuation prompt is:

```text
Continue prove-it from the checkpoint. Execute exactly the next uncompleted numbered round only. Stop only if the Terminality Check is terminal.
```

A host driver should keep sending that prompt until the checkpoint says `Status: COMPLETE` or the `Terminality Check` says `Action: STOP`.

## Definitions

- **Original claim**: the user's claim as stated before stress testing.
- **Normalized claim**: the original claim with explicit quantifiers, scope, definitions, and implied premises.
- **Refined claim**: the strongest surviving bounded version after attacks.
- **Terminal certificate**: decisive reasoning or evidence showing that the original claim is proven or disproven strongly enough that remaining rounds cannot materially change the verdict.
- **Checkpoint**: structured state that lets the next turn resume without redoing completed rounds.
- **Oracle synthesis**: round 10 summary of the tightest surviving claim, boundaries, confidence, and next tests.

## Mode invocation

| Mode | Default? | User phrases | Cadence |
|---|---:|---|---|
| Auto Gauntlet | yes | no phrase; "autoloop"; "full auto"; "auto gauntlet"; "one round per turn" | exactly one numbered round per assistant reply; auto-continue across turns until terminal or round 10 |
| Step mode | no | "step mode"; "pause each round"; "pause"; "step"; "wait after each round" | exactly one round; then wait for explicit user `next` / `continue` |
| Single-Reply mode | no | "continuous"; "single reply"; "all rounds in one response"; "do it all now" | rounds 1-10 in one assistant reply unless an earlier terminal certificate is reached |

If the user's phrase is ambiguous, prefer Auto Gauntlet over Step mode or Single-Reply mode.

## Terminality rules

A round may stop the gauntlet early only if it establishes one of the following terminal verdicts.

### DISPROVEN

Use when the original claim is false under its stated or necessary scope.

Valid examples:

- A universal claim has a concrete counterexample.
- A required premise is impossible, contradictory, empirically false, or unsupported under the claim's own standard.
- A claimed guarantee fails under a permitted boundary case.
- A formal claim has a countermodel.
- The claim depends on mutually inconsistent definitions or constraints.

### PROVEN

Use when the original claim is true under explicit boundaries.

Valid examples:

- A deductive proof establishes the claim.
- An exhaustive finite check covers the full domain.
- A construction proves an existential claim.
- A theorem, specification, or authoritative source directly entails the claim under the normalized scope.
- Empirical evidence is decisive relative to the user's requested standard and the claim is explicitly empirical.

### ROUND_10_COMPLETE

Use only after round 10 Oracle synthesis has been completed and no earlier proof/disproof certificate was reached.

### USER_STOPPED

Use only when the user explicitly says to stop.

### NON_TERMINAL

Use when the round changes, weakens, clarifies, or challenges the claim but does not decisively prove or disprove the original claim.

Do **not** stop early merely because:

- the refined claim is now plausible;
- one round found no objection;
- confidence is high but not decisive;
- an objection is interesting but not fatal;
- more evidence would be useful;
- the claim is probably true or probably false without a terminal certificate.

## Terminality Check

Publish this after every round in every mode.

```text
Terminality Check:
Verdict: <PROVEN | DISPROVEN | NON_TERMINAL | ROUND_10_COMPLETE | USER_STOPPED>
Applies to: <original claim | refined claim | both>
Certificate:
  - Normalized claim:
  - Decisive evidence/reasoning:
  - Why remaining rounds cannot materially change this verdict:
Blocking uncertainty:
  - <none, or list gaps>
Action: <STOP | CONTINUE_TO_ROUND_N>
```

Rules:

- `Action: STOP` is valid only with `PROVEN`, `DISPROVEN`, `ROUND_10_COMPLETE`, or `USER_STOPPED`.
- `Action: CONTINUE_TO_ROUND_N` is required with `NON_TERMINAL`.
- If `Verdict: DISPROVEN` applies only to a refined claim but not the original claim, the run is non-terminal unless the original claim is also defeated.
- If `Verdict: PROVEN` applies only to a refined claim but not the original claim, the run is non-terminal unless the user explicitly asked to prove the refined claim.

## Default Auto Gauntlet cadence

For each assistant reply:

1. Read `.prove-it-progress.md` if present; otherwise read the latest inline `Checkpoint`.
2. If no checkpoint exists, initialize a new gauntlet from the user's claim.
3. Determine the next uncompleted numbered round.
4. Execute exactly that one round.
5. Publish:
   - round heading;
   - Round Ledger;
   - Knowledge Delta;
   - Terminality Check;
   - Checkpoint;
   - Auto Gauntlet continuation trailer if non-terminal.
6. If terminal, set `Status: COMPLETE`, `Next round: none`, and stop.
7. If non-terminal, set `Status: IN PROGRESS`, set the next round, and request immediate continuation of the same conversation.

Never skip a round.
Never merge rounds.
Never emit Oracle synthesis before round 10 unless an earlier terminal certificate has already ended the run.
Never continue after a valid terminal certificate.

## Conversation rules

- In Auto Gauntlet mode, a plain continuation turn resumes at the next uncompleted round.
- In Auto Gauntlet mode, do not ask the user whether to continue unless essential information is missing.
- If essential information is missing, ask at most one question and do not consume a numbered round.
- If the user asks a meta-question about the gauntlet, answer the question without consuming a round unless the user explicitly asks to continue.
- If the user says `stop`, preserve the latest checkpoint and mark `Status: COMPLETE`, `Terminal verdict: USER_STOPPED`.
- If the user changes mode mid-run, preserve the current checkpoint, switch modes, and continue from the next uncompleted round.
- If the claim changes materially mid-run, start a new gauntlet and reset the checkpoint.
- If context compacts, the progress file is authoritative. If there is no progress file, the latest inline `Checkpoint` is authoritative.

## State and recovery

Preferred durable state file: `.prove-it-progress.md` in the project root.

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

[explicit quantifiers, scope, definitions, premises]

## Mode

[auto-gauntlet | step | single-reply]

## Status

[IN PROGRESS | COMPLETE]

## Terminal verdict

[PROVEN | DISPROVEN | NON_TERMINAL | ROUND_10_COMPLETE | USER_STOPPED]

## Stop reason

[none | concise reason]

## Current refined claim

[current strongest surviving bounded version]

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
[Terminality Check]

## Continuation directive

If Status is IN PROGRESS, continue the same thread with:
"Continue prove-it from the checkpoint. Execute exactly the next uncompleted numbered round only. Stop only if the Terminality Check is terminal."
```

## Ten-round gauntlet

1. **Counterexamples**: find the smallest concrete case that breaks the original claim.
2. **Logic traps**: expose missing quantifiers, unstated premises, invalid inferences, or category errors.
3. **Boundary cases**: test zero, one, maximum, empty, pathological, extreme-scale, or degenerate cases.
4. **Adversarial inputs**: test worst-case distributions, strategic manipulation, abuse, hostile users, or bad-faith incentives.
5. **Alternative paradigms**: switch objective functions, models, values, or worldviews and see whether the conclusion flips.
6. **Operational constraints**: test latency, cost, compliance, integration, maintainability, availability, policy, and organizational hard stops.
7. **Probabilistic uncertainty**: test variance, tail risk, base rates, sampling bias, uncertainty intervals, and distribution shift.
8. **Comparative baselines**: ask "better than what?", against which counterfactual, on which metric, with which trade-offs.
9. **Meta-test**: design the fastest disproof experiment or decisive information-gathering test.
10. **Oracle synthesis**: state the tightest surviving claim, validity boundaries, invalidity boundaries, confidence trail, and next tests.

## Round self-prompt bank

Use exactly the self-prompt matching the current numbered round. Do not ask the user unless blocked.

- Counterexamples: What is the smallest input or case that breaks the original claim?
- Logic traps: Which hidden assumption, quantifier shift, or invalid inference must hold?
- Boundary cases: Which edge boundary is most plausible in real use?
- Adversarial inputs: What does worst-case, strategic, or hostile input look like?
- Alternative paradigms: What objective or worldview makes the opposite conclusion reasonable?
- Operational constraints: Which dependency, policy, system limit, or organizational constraint is a hard stop?
- Probabilistic uncertainty: What distribution shift, tail event, base-rate error, or variance flips the result?
- Comparative baselines: Better than what, on which metric, under which counterfactual?
- Meta-test: What experiment would change the verdict fastest?
- Oracle synthesis: What explicit boundaries keep the surviving claim honest?

## Required artifacts

### Argument map

Use this internally when helpful. Publish only when it clarifies the round.

```text
Claim:
Premises:
- P1:
- P2:
Hidden assumptions:
- A1:
Weak links:
- W1:
Disproof tests:
- T1:
Refined claim:
```

### Round Ledger

Publish every round.

```text
Round Ledger:
Round: <1-10>
Focus:
Original claim:
Normalized claim:
Claim scope:
Current refined claim entering round:
Attack summary:
New evidence:
New counterexample:
Refined claim candidate:
Remaining gaps:
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

### Checkpoint

Publish every Auto Gauntlet or Step mode round.

```text
Checkpoint:
Mode: <auto-gauntlet | step | single-reply>
Status: <IN PROGRESS | COMPLETE>
Terminal verdict: <PROVEN | DISPROVEN | NON_TERMINAL | ROUND_10_COMPLETE | USER_STOPPED>
Completed round: <N>
Next round: <N+1 + focus | none>
Current refined claim:
Stop reason: <none | concise reason>
Resume rule: <exact instruction for next assistant turn>
```

### Auto Gauntlet continuation trailer

In Auto Gauntlet mode, publish this only when `Status: IN PROGRESS`.

```text
Auto Gauntlet Control:
status: IN_PROGRESS
next_round: <N+1>
resume_prompt: Continue prove-it from the checkpoint. Execute exactly the next uncompleted numbered round only. Stop only if the Terminality Check is terminal.
```

Do not publish the trailer when `Status: COMPLETE`.

## Oracle synthesis template

Round 10 must use this template unless the run has already ended with a terminal proof/disproof certificate.

```text
Oracle synthesis:
Original claim:
Normalized claim:
Final verdict:
Tightest surviving claim:
Valid when:
- ...
Invalid when:
- ...
Confidence trail:
- Evidence:
- Counterpressure:
- Gaps:
Next tests:
- ...
```

## Completion contract

- Auto Gauntlet and Step mode replies consume exactly one numbered round.
- A reply with multiple numbered rounds is invalid unless the active mode is Single-Reply mode.
- A reply that omits `Round Ledger`, `Knowledge Delta`, `Terminality Check`, or `Checkpoint` is invalid.
- A non-terminal Auto Gauntlet reply that omits the Auto Gauntlet continuation trailer is invalid.
- A terminal reply must set `Status: COMPLETE` and `Next round: none`.
- A terminal reply must explain why future rounds cannot materially change the verdict.
- A non-terminal reply must set `Action: CONTINUE_TO_ROUND_N`.

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

Terminality Check:
...

Checkpoint:
...

Auto Gauntlet Control:
...
```

Omit `Auto Gauntlet Control` in Step mode and in terminal Auto Gauntlet replies.

### Single-Reply mode

- Present rounds in numeric order.
- After each round, include Round Ledger, Knowledge Delta, and Terminality Check.
- Stop early if a round establishes `PROVEN` or `DISPROVEN` for the original claim.
- Otherwise, continue through round 10 and include Oracle synthesis.
- Include one final Checkpoint at the end.

## Anti-shortcut rules

1. Do not present a top-level verdict without a Terminality Check.
2. Do not continue to future rounds after a valid terminal proof/disproof certificate.
3. Do not stop at a non-terminal checkpoint.
4. Do not treat prior prose as implicitly satisfying skipped rounds.
5. Do not rerun completed rounds unless the user explicitly asks to revisit them.
6. Do not let a weaker refined claim obscure whether the original claim has been proven or disproven.
7. Do not emit Oracle synthesis before round 10 unless a terminal certificate already ended the run.
8. Keep each round compact: terse bullets and phrase-level evidence are preferred.
9. Preserve state before switching modes, stopping, or handling a meta-question.
10. If a host driver asks to continue and the checkpoint is already complete, report that the gauntlet is complete and do not run another round.
