# Codebase Doctrine Evolution

Repository-specific skills created from CBD-v2 should later be evaluated with:

```bash
seq skill-decision-audit \
  --skill <repo-skill> \
  --repo <repo> \
  --mode tune-packet \
  --format json
```

Preserve:

```text
CBD-v2 doctrine ID
CDI-v2 intent ID
artifact-state ID
candidate ID and trial/accepted status
governing law IDs and doctrine status
skill contract fingerprint
trigger quality
decision effects
clause compliance
outcome association
missed and ceremonial activation
```

Use real decision episodes to decide whether a `recommended_for_trial` candidate
should be accepted, narrowed, retired, or routed to stronger code/test/tooling.

When repository law, authority, boundary, or target status changed, route to:

```text
$codebase-doctrine refresh
```

Use existing decision-audit surfaces; no dedicated Codebase Doctrine CLI is
required for empirical evolution.
