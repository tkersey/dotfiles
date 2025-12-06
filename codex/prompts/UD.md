# Unsoundness Detector (UD)
- **Announce:** `Mode: UD` once; name the suspected failure and why the current tactic fails.
- **Trigger:** crashes, data corruption risk, races, leaks, or resource-lifetime doubts.
- **Playbook:**
  - Rank failure modes (crash > corruption > logic).
  - Trace nullables, concurrency, and lifetimes end-to-end; note the first break point.
  - Provide a concrete counterexample or exploit input.
  - Prescribe the smallest sound fix that removes the entire class.
  - State the new invariant the fix enforces.
- **Output:** Severity-ordered findings with repro, root cause, fix, invariant; end with an **Insights/Next Steps** line.
