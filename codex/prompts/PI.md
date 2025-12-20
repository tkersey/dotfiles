---
description: Stress-test a claim via 10 skeptic rounds, then bound it with evidence
argument-hint: "<claim to prove...>"
---

# Prove It (PI)
- **Input (optional):** `$PROVING` (the claim/instruction to prove). If empty, use the surrounding conversation as context.
- **Purpose:** Stress-test absolute claims through 10 escalating skeptic rounds, reshaping them into bounded, evidence-backed statements.
- **Process:**
  - Run all 10 rounds in order; vary the lens each time; stop only after round 10.
    1. **Claim + falsifiers:** State the claim, what would disprove it, and current evidence.
    2. **Counterexamples/edge cases:** List plausible breakpoints and near-miss scenarios.
    3. **Limits/extremes:** Push inputs to zero/infinity, worst/best cases, resource starvation.
    4. **Inversion:** Assume the opposite; note contexts where the negation is true.
    5. **Paradigm flip:** Challenge with alternate models/technologies/assumptions.
    6. **Evidence gaps:** Identify missing measurements and propose what to gather.
    7. **Adversarial attack:** Malicious actors, failure injection, chaos conditions.
    8. **Dependency/risk audit:** Hidden prerequisites, single points of failure, blast radius.
    9. **Precedent/analogy:** Historical failures or adjacent-domain examples that contradict it.
    10. **Oracle synthesis (final):** Refine/bound the claim, map confidence, and queue concrete tests.
  - Maintain "ultimate skeptic" tone in every round: assume the claim is wrong until proven otherwise.
  - Mark completion only after round 10; earlier survival does not end the gauntlet.
- **Deliverable:** Refined claim with boundaries, evidence summary, and recommended tests, followed by a short **Insights/Next Steps** line (include top findings from the rounds).
- **Examples:**
  - "This cache always serves responses under 50ms": walk the 10 rounds (tail latencies, outage modes, adversarial request mixes, dependency audits) before Oracle bounding.
  - "The algorithm is always optimal": run adversarial inputs, inversion to "sometimes suboptimal", compare to brute-force baselines, cite precedent failures, then Oracle-refine scope.
