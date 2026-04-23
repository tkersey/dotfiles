# Specialist briefing intake

Specialist briefings are high-signal inputs. They are not proof by themselves.

## Expected roles

- `verification_auditor`: direct-path, regression, and critical-invariant coverage
- `invariant_auditor`: invariant grading and unknown-critical pressure
- `hazard_hunter`: misuse and foot-gun pressure
- `complexity_auditor`: incidental complexity and reviewability pressure
- `evidence_mapper`: implicated surfaces and true execution path

## Intake rules

1. Normalize every briefing into one or more closure gates.
2. Look for direct supporting evidence before upgrading confidence.
3. If two briefings materially conflict, design the smallest resolving check.
4. If a briefing raises a material concern that cannot be directly tested, decide whether it is:
   - bounded by other direct evidence,
   - an accepted residual risk,
   - or a not-ready blocker.
5. Do not repeat broad de novo review. Closure is for proof and gating.

## Minimal synthesis pattern

Use briefings to answer:
- What is the single highest-signal next check?
- Which critical invariant is still open?
- Which material foot-gun is still unbounded?
- Which complexity concern is a real closure blocker versus a residual design risk?
