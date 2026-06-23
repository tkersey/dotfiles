# `$actuating` Audit

Preferred future lifted command:

```bash
seq actuation-audit \
  --root ~/.codex/sessions \
  --repo <repo> \
  --since <time> \
  --until <time> \
  --exclude-current \
  --mode report \
  --format markdown
```

Until implemented, use:

```text
skill-decision-audit
skill-evidence
tool-lifecycle
session-tooling
turns
session-detail
orchestration-concurrency
generic query only for missing joins
```

Measure separately:

```text
GCR attempts/current coverage
graph failures and mutation-after-failure
AFR coverage
ARH/FPSR coverage
update_plan per GCR sequence
patch/churn
focused/wave/full proof cadence
proof invalidators
compactions and resume artifacts
skill rereads after compaction
subagent artifact yield
decision receipts
ship/PR mode
```

Key defect:

```text
failed/stale GCR
-> repeated update_plan
-> material patching
```

Classify:

```text
projection_inversion
```

Do not call `codex_internal_context` or persistent goal context a successful downstream skill outcome.

The native implementation is specified in:

```text
SEQ_ACTUATION_AUDIT_SPEC.md
```
