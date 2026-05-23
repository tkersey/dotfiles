# `$seq` Evidence Playbook for `$tune`

Prefer specialized `$seq` commands before raw `seq query`.

## Baseline skill usage

```bash
seq skill-success-rank --root ~/.codex/sessions --skill <skill> --mode sessions --last 90d --format jsonl
seq skill-audit --root ~/.codex/sessions --skill <skill> --mode trend --since <iso8601> --format table
seq skill-cohort --root ~/.codex/sessions --skill <skill> --since <iso8601> --format table
```

Use these to distinguish successful activations, raw mentions, and co-occurring skills.

## Historical skill definitions

```bash
seq skill-blocks --root ~/.codex/sessions --skill <skill> --history latest --format json
seq skill-blocks --root ~/.codex/sessions --skill <skill> --history all --format jsonl
```

Use these when usage changed after a skill update or when old skill-block text may explain behavior.

## Trigger and failure phrase search

```bash
seq message-search --root ~/.codex/sessions --contains "<phrase>" --roles user,assistant --limit 50 --format jsonl
seq message-audit --root ~/.codex/sessions --contains "<phrase>" --roles user,assistant --show-query --format json
```

Use these for missed activation, false activation, or user correction patterns.

## Tooling evidence

```bash
seq tool-search --root ~/.codex/sessions --contains "<command-fragment>" --mode rows --format table
seq tool-search --root ~/.codex/sessions --contains "<command-fragment>" --mode args --format jsonl
seq tool-audit --root ~/.codex/sessions --group-by executable --since <iso8601> --limit 20 --format table
```

Use these when repeated command sequences may justify a helper script.

## Workflow evidence

```bash
seq workflow-audit --root ~/.codex/sessions --workflow <workflow-name> --mode report --since <iso8601> --format markdown
seq session-detail --root ~/.codex/sessions --session-id <session_id> --format markdown
seq session-tooling --root ~/.codex/sessions --session-id <session_id> --summary --group-by executable --format table
```

Use these when agents skip, reorder, or weaken workflow steps.

## Workdir/repo evidence

```bash
seq workdir-report --root ~/.codex/sessions --workdir <absolute-workdir> --mode sessions --format table
seq workdir-report --root ~/.codex/sessions --contains "<path-fragment>" --mode sessions --limit 20 --format table
```

Use these when a skill behaves differently in a specific repo or workdir.

## Fallback

Use raw `seq query` only when no lifted command covers the evidence shape. When raw query behavior is unclear, diagnose it first:

```bash
seq query-diagnose --root ~/.codex/sessions --session-id <session_id> --next-actions --format json
```
