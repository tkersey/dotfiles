# Codebase Doctrine Evolution

Repository-specific skills created from CBD-v1 should later be evaluated with:

```bash
seq skill-decision-audit \
  --skill <repo-skill> \
  --repo <repo> \
  --mode tune-packet \
  --format json
```

Preserve:

```text
doctrine ID
governing law IDs
skill contract fingerprint
trigger quality
decision effects
clause compliance
outcome association
missed/ceremonial activation
```

Use existing decision-audit surfaces; no dedicated Codebase Doctrine CLI is required for the initial workflow.

A future doctrine-drift report may compare the current repository head with the artifact state referenced by the skill package.
