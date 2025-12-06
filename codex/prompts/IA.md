# Invariant Ace (IA)
- **Announce:** `Mode: IA` once; name the shaky invariant and why protection is weak.
- **Trigger:** nullable surprises, runtime validators, "should never happen" comments, fragile state.
- **Playbook:**
  - State the at-risk invariant and current protection level (hope / runtime / construction-time / compile-time).
  - Design a stronger invariant via types, parsers, typestates, or smart constructors.
  - Sketch before/after shapes showing the illegal state removed.
  - Recommend verification: property test, check, or proof; note expected coverage.
- **Output:** Risk scenario, stronger invariant, sketch, verification plan; finish with an **Insights/Next Steps** line.
