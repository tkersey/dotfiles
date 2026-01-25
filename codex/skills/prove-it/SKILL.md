---
name: prove-it
description: Gauntlet for absolute claims (always/never/guaranteed/optimal); pressure-test, then refine with explicit boundaries.
---

# Prove It

## When to use
- The user asserts certainty: “always”, “never”, “guaranteed”, “optimal”, “cannot fail”, “no downside”, “100%”.
- The user asks for a devil’s advocate or proof.
- The claim feels too clean for the domain.

## Round cadence (mandatory)
- Default: autoloop (no approvals). Run exactly one gauntlet round per assistant turn and continue next turn until Oracle synthesis. If confidence remains low after Oracle synthesis, continue with additional rounds (11+) and publish an updated Oracle synthesis.
- After each round, publish:
  - Round Ledger
  - Knowledge Delta
- Do not ask for permission to continue. Pause only when you must ask the user a question or the user says "stop".
- Step mode (explicit): if the user asks to "pause" / "step" / "one round at a time", run one round then wait for "next".
- Fast mode (explicit): if the user explicitly requests "fast mode", run rounds 1-10 + Oracle synthesis in one assistant turn.

## Mode invocation
| Mode | Default? | How to invoke | Cadence |
|------|----------|---------------|---------|
| Autoloop | yes | (no phrase) | 1 round/turn; auto-continue |
| Step mode | no | "step mode" / "pause each round" / "pause" / "step" / "one round at a time" | 1 round/turn; wait for "next" |
| Fast mode | no | "fast mode" | rounds 1-10 + Oracle in one turn |

## Quick start
1. Restate the claim and its scope.
2. Default to autoloop. If the user explicitly requests "step mode" or "fast mode", use that instead.
3. Run round 1 and publish the Round Ledger + Knowledge Delta.
4. Continue per the selected mode until Oracle synthesis. If confidence remains low, run additional rounds and publish an updated Oracle synthesis.

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

### Round Ledger (update every turn)
```
Round: <1-10 (or 11+)>
Focus:
Claim scope:
New evidence:
New counterexample:
Remaining gaps:
Next round:
```

### Knowledge Delta (publish every turn)
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
- In fast mode, run rounds 1-10 + Oracle synthesis in one turn (repeat the above per round).

## Activation cues
- "always" / "never" / "guaranteed" / "optimal" / "cannot fail" / "no downside" / "100%"
- "prove it" / "devil's advocate" / "stress test" / "rigor"
