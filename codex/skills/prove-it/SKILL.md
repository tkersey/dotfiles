---
name: prove-it
description: Ten-turn proof/disproof conversation engine for absolute claims. Default is one numbered gauntlet round per assistant reply with checkpointed resume; do not collapse rounds 1-10 into one reply unless the user explicitly asks for continuous mode.
---

# Prove It

## When to use
- The user asserts certainty: “always”, “never”, “guaranteed”, “optimal”, “cannot fail”, “no downside”, “100%”.
- The user asks for a devil’s advocate, rigorous proof/disproof, or structured stress test.
- The claim feels too clean, too broad, or suspiciously assumption-heavy.

## Execution model
**Single-agent conversation engine.**
- Do **not** delegate to subagents.
- Do **not** compress multiple numbered rounds into one reply unless the user explicitly asks for Continuous mode.
- The default contract is **one numbered gauntlet round per assistant reply**.

## Definitions
- **Engine turn** = one assistant reply that consumes exactly one numbered gauntlet round.
- **Gauntlet run** = rounds 1-10, where rounds 1-9 attack the claim from different lenses and round 10 performs Oracle synthesis.
- **Checkpoint** = the persisted state that lets the next turn resume without re-deriving prior rounds.

## Default cadence (mandatory)
- Definition: one "turn" means one assistant reply.
- **Default mode: Turn Engine.** Run **exactly one** numbered round in the current assistant reply, then stop.
- After every default-mode turn, publish:
  - Round Ledger
  - Knowledge Delta
  - Checkpoint
- The next assistant turn must resume at the next uncompleted round.
- Never skip a round.
- Never merge multiple lenses into a pseudo-round.
- Never emit Oracle synthesis before round 10.
- Early disproof does **not** end the gauntlet: if round 1 already falsifies the original claim, continue rounds 2-9 against the strongest surviving refined claim, then run Oracle synthesis at round 10.
- If confidence remains low after round 10, only continue with rounds 11+ when the user explicitly asks for an extended gauntlet.

## Mode invocation

| Mode | Default? | How to invoke | Cadence |
|------|----------|---------------|---------|
| Turn Engine | yes | (no phrase) / "turn engine" / "autoloop" / "one round per turn" | exactly 1 round in the current assistant reply; publish Checkpoint; resume next turn |
| Step mode | no | "step mode" / "pause each round" / "pause" / "step" / "one round at a time" | exactly 1 round; wait only for explicit "next" / "continue" |
| Continuous | no | "continuous" / "don't stop" / "exhaust all rounds" / "full auto" / "fast mode" | rounds 1-10 + Oracle synthesis in one reply |

## Conversation rules
- In **Turn Engine** mode, a plain continuation turn should resume the gauntlet at the next round.
- If the next user turn asks a meta-question about the gauntlet, answer the question **without consuming a round** unless the user explicitly asks to continue.
- If the user says "stop", preserve the latest Checkpoint and stop.
- If the user changes mode mid-run, preserve the current Checkpoint, switch modes, and continue from the next uncompleted round.
- If context compacts, read the progress file first; if there is no file, read the latest Checkpoint block in the conversation and resume from there.

## Quick start
1. Restate the claim and its scope.
2. Determine the mode. Default to **Turn Engine**.
3. Create or update `.prove-it-progress.md` in the project root when writable. If the workspace is not writable, keep the same state inline using the `Checkpoint` block.
4. Run **only the current round** in Turn Engine or Step mode.
5. Publish a distinct Round Ledger + Knowledge Delta + Checkpoint block for that round.
6. Stop after that round unless the active mode is Continuous.
7. On the next continuation turn, read the Checkpoint and execute the next numbered round.

## State and recovery
Preferred durable state file: `.prove-it-progress.md` in the project root.

If the workspace is read-only or there is no writable project root:
- keep the same state structure inline in the conversation
- treat the latest `Checkpoint` block as authoritative
- resume from the `Next round` field

The progress file is authoritative when present.

## Progress file template
```markdown
# Prove It Progress

## Original claim
[verbatim]

## Mode
[turn-engine | step | continuous]

## Status
[IN PROGRESS — Round K of 10 | COMPLETE]

## Current refined claim
[current best bounded version]

## Next round
[round number + focus | none]

## Completed rounds
### Round 1 — Counterexamples
Summary: ...
Refined claim candidate: ...
[Round Ledger block]
[Knowledge Delta block]

### Round 2 — ...
...
```

## Turn-engine completion contract
- In Turn Engine and Step mode, **one reply consumes one round**.
- A Turn Engine or Step reply that contains multiple numbered rounds is invalid.
- A Turn Engine or Step reply that omits `Checkpoint` is invalid.
- In Continuous mode, the reply is incomplete unless it contains rounds 1-10 in order and Oracle synthesis after round 10.

## Ten-round gauntlet
1. Counterexamples: smallest concrete break.
2. Logic traps: missing quantifiers, unstated premises, or invalid quantifier shifts.
3. Boundary cases: zero/one/max/empty/extreme scale.
4. Adversarial inputs: worst-case distributions, abuse, or strategic manipulation.
5. Alternative paradigms: a different objective, model, or worldview flips the conclusion.
6. Operational constraints: latency, cost, compliance, integration, availability, or policy hard stops.
7. Probabilistic uncertainty: variance, tail risk, base-rate neglect, or sampling bias.
8. Comparative baselines: “better than what?”, on which metric, against which counterfactual?
9. Meta-test: fastest disproof experiment.
10. Oracle synthesis: tightest surviving claim with explicit boundaries.

## Round self-prompt bank (pick exactly 1)
Internal self-prompts for selecting round focus. Do not ask the user unless blocked.

- Counterexamples: What is the smallest input that breaks this?
- Logic traps: Which hidden assumption or quantifier shift must hold?
- Boundary cases: Which edge boundary is most plausible in real use?
- Adversarial: What does worst-case or strategic input look like?
- Alternative paradigm: What objective makes the opposite conclusion reasonable?
- Operational: Which dependency, policy, or system limit is a hard stop?
- Uncertainty: What distribution shift or tail event flips the result?
- Baseline: Better than what, and on which metric?
- Meta-test: What experiment would change your mind fastest?
- Oracle: What explicit boundaries keep the surviving claim honest?

## Core artifacts

### Argument map
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

### Round Ledger (publish every round)
```text
Round: <1-10 (or 11+)>
Focus:
Original claim:
Claim scope:
Current refined claim entering round:
Attack summary:
New evidence:
New counterexample:
Refined claim candidate:
Remaining gaps:
Next round:
```

### Knowledge Delta (publish every round)
```text
- New:
- Updated:
- Invalidated:
```

### Checkpoint (publish every round in Turn Engine and Step mode)
```text
Mode: <turn-engine | step | continuous>
Status: <IN PROGRESS | COMPLETE>
Completed round: <N>
Next round: <N+1 or none>
Current refined claim:
Resume rule: <what the next assistant turn should do>
```

### Claim boundary table
```text
| Boundary type | Valid when | Invalid when | Assumptions | Stressors |
|---------------|-----------|--------------|-------------|-----------|
| Scale         |           |              |             |           |
| Data quality  |           |              |             |           |
| Environment   |           |              |             |           |
| Adversary     |           |              |             |           |
```

### Next-tests plan
```text
| Test | Data needed | Success threshold | Stop condition |
|------|-------------|-------------------|----------------|
```

## Oracle synthesis template (round 10)
```text
Original claim:
Refined claim:
Boundaries:
- Valid when:
- Invalid when:
Confidence trail:
- Evidence:
- Gaps:
Next tests:
- ...
```

## Deliverable format

### Turn Engine / Step mode
- Round number + focus.
- Round Ledger.
- Knowledge Delta.
- Checkpoint.
- At most one question for the user, and only when blocked by missing essential facts.
- Stop after that round.

### Continuous mode
- Present `Round 1` through `Round 10` in numeric order.
- Include exactly one `Round Ledger` and one `Knowledge Delta` section inside each round block.
- Place Oracle synthesis after round 10, not before.
- A Continuous reply missing any of the above is invalid and must be continued before finalizing.

## Anti-shortcut rules
1. Do not present a top-level verdict before round 10 unless the user explicitly asks to stop early.
2. Do not treat prior prose as implicitly satisfying skipped rounds.
3. Do not rerun completed rounds unless the user explicitly asks to revisit them.
4. If the claim changes materially mid-run, start a new gauntlet and reset the Checkpoint.
5. Keep each round compact: terse bullets and phrase-level evidence are preferred.

## Activation cues
- "always" / "never" / "guaranteed" / "optimal" / "cannot fail" / "no downside" / "100%"
- "prove it" / "devil's advocate" / "stress test" / "rigor"
- "one round per turn" / "autoloop" / "turn engine"
