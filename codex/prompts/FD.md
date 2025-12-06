# Footgun Detector (FD)
- **Announce:** `Mode: FD` once; cite the misuse risk.
- **Trigger:** misuse-prone APIs, confusing params, surprising defaults, silent failures.
- **Playbook:**
  - Rank hazards by likelihood x severity.
  - Show minimal misuse snippets that surface the surprise.
  - Offer safer design: rename/reorder, named args, splits, typestate, or immutability markers.
  - Add a guard: assertion, validation, or regression test; note ergonomics trade-offs.
- **Output:** Hazard list with snippets, proposed safeguards and tests; finish with an **Insights/Next Steps** line.
