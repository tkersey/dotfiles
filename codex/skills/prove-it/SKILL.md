---
name: prove-it
description: Gauntlet for absolute claims (always/never/guaranteed/optimal); pressure-test, then refine with explicit boundaries. Use when users ask to prove or disprove strong certainty claims, request devil's-advocate challenge rounds, or want the $prove-it gauntlet to run all 10 rounds continuously by default.
---

# Prove It

## When to use
- The user asserts certainty: “always”, “never”, “guaranteed”, “optimal”, “cannot fail”, “no downside”, “100%”.
- The user asks for a devil’s advocate or proof.
- The claim feels too clean for the domain.

## Round cadence (mandatory)
- Definition: one "turn" means one assistant reply.
- Default: continuous (no approvals). Run rounds 1-10 plus Oracle synthesis in the current assistant turn. Do not rely on a future assistant turn for default behavior.
- Hard completion gate: a default continuous reply is incomplete unless it contains rounds 1-10 in order, one distinct Round Ledger + Knowledge Delta block for each round, and an Oracle synthesis block after round 10.
- Fail closed: if you notice you have emitted only round 1 or are about to conclude early, do not finalize; continue immediately with rounds 2-10 in the same reply.
- In default mode, after each round, publish:
  - Round Ledger
  - Knowledge Delta
- Round integrity is mandatory:
  - Execute rounds 1-10 in numeric order, with one distinct gauntlet focus per round.
  - Emit a separate Round Ledger + Knowledge Delta block for every round; do not merge multiple rounds into one pseudo-round or summarize "rounds 2-9" together.
  - Do not treat prior prose as implicitly satisfying skipped rounds unless the user explicitly asks to continue from a known checkpoint.
- Early disproof does not end the gauntlet: if round 1 already falsifies the original claim, continue rounds 2-9 against the strongest surviving refined claim, then publish Oracle synthesis.
- If confidence remains low after Oracle synthesis, continue with additional rounds (11+) in the same reply when feasible, then publish an updated Oracle synthesis.
- Do not ask for permission to continue. In default mode, do not wait for "next" between rounds. Pause only when you must ask the user a question or the user says "stop".
- Step mode (explicit): if the user asks to "pause" / "step" / "one round at a time", run one round then wait for "next".
- Turn autoloop (explicit): if the user asks for "autoloop" / "one round per turn", run exactly one gauntlet round per assistant turn and continue on the next turn until Oracle synthesis.
- Full auto mode (explicit): "full auto" / "fast mode" is an alias for the default continuous behavior.
- Keep it compact: prefer terse bullets and phrase-level evidence so the full gauntlet fits in one reply.

## Mode invocation
| Mode | Default? | How to invoke | Cadence |
|------|----------|---------------|---------|
| Continuous | yes | (no phrase) / "continuous" / "don't stop" / "exhaust all rounds" | rounds 1-10 + Oracle in one turn; publish Round Ledger + Knowledge Delta after each round |
| Step mode | no | "step mode" / "pause each round" / "pause" / "step" / "one round at a time" | 1 round/turn; wait for "next" |
| Turn autoloop | no | "autoloop" / "one round per turn" | 1 round/turn; continue on the next turn until Oracle |
| Full auto | no | "full auto" / "fast mode" | alias for Continuous |

## Quick start
1. Restate the claim and its scope.
2. Default to continuous. If the user explicitly requests "step mode" or "turn autoloop", use that instead.
3. Run rounds 1-10 plus Oracle synthesis in the same reply, publishing a distinct Round Ledger + Knowledge Delta block after each round.
4. Do not emit a top-level verdict, conclusion, or stop point before round 10; any interim refinement stays inside the round blocks.
5. Treat "continuous", "don't stop", and "exhaust all rounds" as the default continuous mode.
6. If confidence remains low, run additional rounds (11+) and publish an updated Oracle synthesis.

## Ten-round gauntlet
1. Counterexamples: smallest concrete break.
2. Logic traps: missing quantifiers/premises.
3. Boundary cases: zero/one/max/empty/extreme scale.
4. Adversarial inputs: worst-case distributions/abuse.
5. Alternative paradigms: different model flips the conclusion.
6. Operational constraints: latency/cost/compliance/availability.
7. Probabilistic uncertainty: variance, tail risk, sampling bias.
8. Comparative baselines: “better than what?”, which metric?
9. Meta-test: fastest disproof experiment.
10. Oracle synthesis: tightest surviving claim with boundaries. If confidence is still low, repeat rounds 1-9 as needed, then re-run Oracle synthesis.

## Round self-prompt bank (pick exactly 1)
Internal self-prompts for selecting round focus. Do not ask the user unless blocked.
- Counterexamples: What is the smallest input that breaks this?
- Logic traps: What unstated assumption must hold?
- Boundary cases: Which boundary is most likely in real use?
- Adversarial: What does worst-case input look like?
- Alternative paradigm: What objective makes the opposite true?
- Operational: Which dependency/policy is a hard stop?
- Uncertainty: What distribution shift flips the result?
- Baseline: Better than what, on which metric?
- Meta-test: What experiment would change your mind fastest?
- Oracle: What explicit boundaries keep this honest?

## Core artifacts

### Argument map
```
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

### Round Ledger (update every round)
```
Round: <1-10 (or 11+)>
Focus:
Claim scope:
New evidence:
New counterexample:
Remaining gaps:
Next round:
```

### Knowledge Delta (publish every round)
```
- New:
- Updated:
- Invalidated:
```

### Claim boundary table
```
| Boundary type | Valid when | Invalid when | Assumptions | Stressors |
|---------------|-----------|--------------|-------------|-----------|
| Scale         |           |              |             |           |
| Data quality  |           |              |             |           |
| Environment   |           |              |             |           |
| Adversary     |           |              |             |           |
```

### Next-tests plan
```
| Test | Data needed | Success threshold | Stop condition |
|------|-------------|-------------------|----------------|
```

## Domain packs

### Performance
Use when the claim is about speed, latency, throughput, or resources.
- Clarify: median vs tail latency vs throughput.
- Identify workload shape (spiky vs steady) and bottleneck resource.

### Product
Use when the claim is about user impact, adoption, or behavior.
- Clarify user segment and success metric.
- State the baseline/counterfactual.
- Name the likely unintended behavior/tradeoff.

## Oracle synthesis template (round 10 / as needed)
```
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

## Deliverable format (per turn)
- Round number + focus.
- Round Ledger + Knowledge Delta.
- At most one question for the user (only when blocked).
- In default continuous mode, run rounds 1-10 + Oracle synthesis in the same reply, with one distinct per-round block per round.
- In step mode, run one round and wait for "next".
- In turn autoloop, run one round in that turn and continue to the next round on the next turn.
- In full auto (or "fast mode"), follow the same behavior as default continuous mode.

## Continuous-mode completion checklist
- Present `Round 1` through `Round 10` in numeric order.
- Include exactly one `Round Ledger` and one `Knowledge Delta` section inside each round block.
- Place Oracle synthesis after round 10, not before.
- A reply missing any of the above is invalid for continuous mode and must be continued before finalizing.

## Activation cues
- "always" / "never" / "guaranteed" / "optimal" / "cannot fail" / "no downside" / "100%"
- "prove it" / "devil's advocate" / "stress test" / "rigor"
