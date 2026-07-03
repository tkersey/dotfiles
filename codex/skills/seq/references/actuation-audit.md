# `$actuating` Audit

Preferred lifted command:

```bash
seq actuation-audit \
  --root ~/.codex/sessions \
  --workdir <workdir> \
  --since <time> \
  --until <time> \
  --exclude-current \
  --mode hylo \
  --format json
```

Report mode remains available for human-readable summaries:

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

If the installed command is unavailable, use:

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
ALSR/HYL/HSR governance coverage
terminal ATCG coverage
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
seq actuation-audit --mode hylo
```
