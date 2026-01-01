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
- Run exactly one gauntlet round per assistant turn.
- After each round, publish:
  - Round Ledger
  - Knowledge Delta
- Only batch rounds if the user explicitly requests “fast mode”.

## Quick start
1. Restate the claim and its scope.
2. Ask whether to use fast mode (default: one round per turn).
3. Run round 1 and publish the Round Ledger + Knowledge Delta.
4. Continue round-by-round until Oracle synthesis.

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
10. Oracle synthesis: tightest surviving claim with boundaries.

## Round question bank (pick 1–2)
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
Round: <1-10>
Focus:
Claim scope:
New evidence:
New counterexample:
Knowledge Delta:
Remaining gaps:
Next round:
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

## Oracle synthesis template (final)
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
- At most one question for the user (if needed).

## Activation cues
- "always" / "never" / "guaranteed" / "optimal" / "cannot fail" / "no downside" / "100%"
- "prove it" / "devil's advocate" / "stress test" / "rigor"
