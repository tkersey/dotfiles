# Codebase Doctrine Evolution

Repository-specific skills derived from Codebase Doctrine should later be
evaluated from real decision episodes:

```bash
seq skill-decision-audit \
  --skill <repo-skill> \
  --repo <repo> \
  --mode tune-packet \
  --format json
```

Preserve enough provenance to identify:

```text
the governing doctrine and jurisdiction
the candidate's trial or accepted posture
the expected triggers and non-triggers
the consequential decisions it should improve
actual decision effects
success and failure signals
missed and ceremonial activation
outcome association
narrowing and retirement conditions
```

Use decision episodes to decide whether the skill should be accepted, narrowed,
retired, or replaced by stronger code, tests, tooling, CI, guidance, an ADR, or
negative-ledger ownership.

When repository law, authority, boundary, permitted variation, proof burden,
governed aporia, or target posture changes, route to:

```text
$codebase-doctrine refresh
```

Do not infer value from raw activation, mention, or co-occurrence counts.
