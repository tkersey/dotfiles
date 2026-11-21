---
format: diadoche-context/v1
title: Retry behavior investigation
files:
  - context.md
  - evidence.jsonl
sources:
  - id: s1
    description: Selected discussion and experiments for retry behavior
    adapter: example-session/v1
---

# Purpose
Review the proposed retry policy. The user asked to retry only transient
failures (e1).

# Current state
The transient case passed and the authorization case failed (e2).

# Coverage and gaps
One synthetic source; no workers.
