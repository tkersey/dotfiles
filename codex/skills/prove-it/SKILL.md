---
name: prove-it
description: Prove-it gauntlet for absolute claims ("always", "never", "guaranteed", "optimal", "cannot fail", "no downside", "100%"); use to challenge certainty with per-round turns, counterexamples, stress tests, Oracle synthesis, and refined claims.
---

# Prove It

## When to use
- The user asserts absolutes or certainty.
- "prove it", "devil's advocate", "guaranteed", "optimal", "cannot fail".
- The claim feels too clean or overconfident.

## Round cadence (mandatory)
- Run **one gauntlet round per assistant turn**.
- After each round, update the **Round Ledger** and a **Knowledge Delta**.
- Only batch rounds if the user explicitly says **"fast mode"**.

## Quick start
1. Name the absolute claim and its scope.
2. Ask if the user wants fast mode; default to per-round turns.
3. Run round 1 and publish the Round Ledger + Knowledge Delta.
4. Continue round-by-round until Oracle synthesis.

## Ten-round gauntlet
1. Counterexamples 🧪: concrete inputs that break the claim.
2. Logic traps 🕳️: missing quantifiers or unstated premises.
3. Boundary cases 🧱: zero, one, max, empty, null, extreme scale.
4. Adversarial inputs 🛡️: malicious or worst-case distributions.
5. Alternative paradigms 🔄: different models that invert conclusions.
6. Operational constraints ⚙️: latency, cost, compliance, availability.
7. Probabilistic uncertainty 🎲: variance, sample bias, tail risk.
8. Comparative baselines 📊: "better than what" with metrics.
9. Meta-questions ❓: what would disprove this fastest?
10. Oracle synthesis 🔮: the tightest claim that survives all rounds.

## Round question bank (1-2 per round)
1. Counterexamples 🧪:
   - What is the smallest input that breaks this?
   - When did this fail last, and why?
2. Logic traps 🕳️:
   - Which quantifier is implied (all/most/some)?
   - What assumption must be true for the claim to hold?
3. Boundary cases 🧱:
   - What happens at zero, one, and max scale?
   - Which boundary is most likely in real use?
4. Adversarial inputs 🛡️:
   - What does a worst-case input look like?
   - Who benefits if this fails?
5. Alternative paradigms 🔄:
   - What model or framing makes the opposite conclusion true?
   - What if the objective function is different?
6. Operational constraints ⚙️:
   - What budget/latency/SLO makes this untrue?
   - Which dependency or policy is a hard stop?
7. Probabilistic uncertainty 🎲:
   - How sensitive is this to variance or distribution shift?
   - What sample bias could flip the result?
8. Comparative baselines 📊:
   - Better than what baseline, on which metric?
   - What is the null or status-quo outcome?
9. Meta-questions ❓:
   - What is the fastest disproof test?
   - What would change your mind immediately?
10. Oracle synthesis 🔮:
   - What is the smallest claim that still seems true?
   - What explicit boundaries keep it honest?

## Counterexample taxonomy
- Input edge: size, shape, null/empty, malformed.
- Environment: OS, region, timezone, network, load.
- Data shift: new distribution, missing fields, drift.
- Dependency failure: timeouts, partial outage, throttling.
- Adversary: malicious payloads, abuse patterns, worst-case.
- Scale: concurrency, throughput spikes, latency tails.
- Policy/regulation: privacy, compliance, legal constraints.

## Argument map (claim structure)
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

## Round Ledger (update every turn)
```
Round: <1-10>
Claim scope:
New evidence:
New counterexample:
Knowledge Delta:
Remaining gaps:
Next round:
```

## Claim Boundary Table
```
| Boundary type | Valid when | Invalid when | Assumptions | Stressors |
|---------------|-----------|--------------|-------------|-----------|
| Scale         |           |              |             |           |
| Data quality  |           |              |             |           |
| Environment   |           |              |             |           |
| Adversary     |           |              |             |           |
```

## Evidence & Counterexample Matrix
```
| Item | Type | Strength | Impact on claim | Notes |
|------|------|----------|-----------------|-------|
| A    | Evidence | High/Med/Low | Supports/Weakens | ... |
| B    | Counterexample | High/Med/Low | Breaks/Edges | ... |
```

## Next-Tests Plan
```
| Test | Data needed | Success threshold | Stop condition |
|------|-------------|-------------------|----------------|
|      |             |                   |                |
```

## Domain packs
### Performance pack 🚀
Use when the claim is about speed, latency, throughput, or resource use.

Focus questions:
- Is this about median latency, tail latency, or throughput?
- What is the workload shape (spiky vs steady)?
- Which resource is the bottleneck (CPU, IO, memory, network)?

Example:
Claim: "This query optimization always improves performance."
Round 1 (Counterexamples): highly selective index that increases write amplification can slow heavy write workloads.
Refined claim: "Improves read latency for read-heavy workloads with stable predicates; may regress write-heavy workloads."

### Product pack 🧭
Use when the claim is about user impact, adoption, or behavior.

Focus questions:
- Which user segment, and what success metric?
- What is the counterfactual or baseline?
- What is the unintended behavior or tradeoff?

Example:
Claim: "Adding onboarding tips always improves activation."
Round 1 (Counterexamples): expert users skip tips and get annoyed, reducing activation.
Refined claim: "Improves activation for novice users when tips are contextual and skippable."

## Oracle synthesis template
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
- Round number and gauntlet focus.
- Round Ledger + Knowledge Delta.
- One question for the user if needed.

## Final deliverable (after Oracle synthesis)
- Refined claim with explicit boundaries.
- Confidence trail (evidence + gaps).
- Next-Tests Plan.

## Example: systems
Claim: "This caching strategy always improves performance."

Round 1 (Counterexamples 🧪):
- Counterexample: small payloads + low hit rate can slow responses.
- Knowledge Delta: performance depends on hit rate and payload size.

Refined claim (after Oracle synthesis):
"Caching improves performance when hit rate exceeds X and payloads are larger than Y under stable read patterns."

## Example: security
Claim: "JWT auth is always safe."

Round 1 (Counterexamples 🧪):
- Counterexample: weak signing key or leaked secret enables forgery.
- Knowledge Delta: safety depends on key management and rotation.

Refined claim:
"JWT auth is safe when keys are strong, rotated, and verification is enforced across all services."

## Example: ML
Claim: "Model B always beats Model A."

Round 1 (Counterexamples 🧪):
- Counterexample: domain shift where Model A generalizes better.
- Knowledge Delta: performance depends on data distribution and shift.

Refined claim:
"Model B outperforms Model A on distribution D with metric M and sufficient calibration."

## Example: cost
Claim: "Serverless is always cheaper."

Round 1 (Counterexamples 🧪):
- Counterexample: high, steady throughput can be cheaper on reserved instances.
- Knowledge Delta: cost depends on workload shape and cold-start overhead.

Refined claim:
"Serverless is cheaper for spiky workloads with low average utilization and minimal cold-start penalties."

## Activation cues
- "always"
- "never"
- "guaranteed"
- "optimal"
- "prove it"
- "devil's advocate"
- "cannot fail"
- "no downside"
- "100%"
- "rigor"
- "stress test"
