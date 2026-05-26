# `$seq` Evidence Playbook for `$tune`

Use this playbook only for `history` evidence. `$seq` is the default historical-session adapter; it is not required for `in-flight` or `provided` evidence.

Prefer specialized `$seq` commands before raw `seq query`. Build an evidence ledger that records what each command proves and what it does not prove.

## Evidence Discipline

- Read the target skill before judging usage.
- Declare the history scope before mining.
- Use recent evidence by default only when the user did not request another scope.
- Distinguish raw skill mentions from successful activations.
- Prefer session-level, workflow-level, and validation-level proof over isolated text matches.
- Search for counterevidence, not only confirming examples.
- Sanitize user-facing summaries. Do not include raw transcript text unless explicitly requested and safe.
- Use raw `seq query` only when no lifted command covers the evidence shape.

## History Scope Patterns

### Recent default

Use for general tuning when no window is provided.

```bash
seq skill-success-rank --root <sessions-root> --skill <skill> --mode sessions --last 90d --format jsonl
seq skill-audit --root <sessions-root> --skill <skill> --mode trend --since <iso8601> --format table
seq skill-cohort --root <sessions-root> --skill <skill> --since <iso8601> --format table
```

### Arbitrary date range

Use when the user gives a date range or asks to go back beyond the default.

```bash
seq skill-audit --root <sessions-root> --skill <skill> --mode trend --since <iso8601> --format table
seq skill-cohort --root <sessions-root> --skill <skill> --since <iso8601> --format table
seq message-search --root <sessions-root> --contains "<trigger-or-failure-phrase>" --roles user,assistant --limit 100 --format jsonl
```

Record the actual range searched. If the CLI command requires a duration and no duration is known, do not invent one; write a placeholder and mark the ledger as incomplete until a scope is supplied.

### Explicit sessions

Use when the user names sessions or when another search identifies representative sessions.

```bash
seq session-detail --root <sessions-root> --session-id <session_id> --format markdown
seq session-tooling --root <sessions-root> --session-id <session_id> --summary --group-by executable --format table
```

### Historical skill definitions

Use when behavior may have changed after skill updates.

```bash
seq skill-blocks --root <sessions-root> --skill <skill> --history latest --format json
seq skill-blocks --root <sessions-root> --skill <skill> --history all --format jsonl
```

## Baseline Skill Usage

Use these to distinguish successful activations, raw mentions, and co-occurring skills:

```bash
seq skill-success-rank --root <sessions-root> --skill <skill> --mode sessions --last <duration> --format jsonl
seq skill-audit --root <sessions-root> --skill <skill> --mode trend --since <iso8601> --format table
seq skill-cohort --root <sessions-root> --skill <skill> --since <iso8601> --format table
```

Ledger prompts:

- What counts as successful activation here?
- Are there enough relevant activations to tune safely?
- Which companion skills co-occur and might indicate boundary overlap?
- Is the selected scope recent, arbitrary, explicit-session, or workdir/repo-bound?

## Trigger and Failure Phrase Search

```bash
seq message-search --root <sessions-root> --contains "<phrase>" --roles user,assistant --limit 50 --format jsonl
seq message-audit --root <sessions-root> --contains "<phrase>" --roles user,assistant --show-query --format json
```

Use these for missed activation, false activation, partial activation, user correction, and mode-selection patterns.

## Tooling Evidence

```bash
seq tool-search --root <sessions-root> --contains "<command-fragment>" --mode rows --format table
seq tool-search --root <sessions-root> --contains "<command-fragment>" --mode args --format jsonl
seq tool-audit --root <sessions-root> --group-by executable --since <iso8601> --limit 20 --format table
```

Use these when repeated command sequences may justify a helper script.

## Workflow Evidence

```bash
seq workflow-audit --root <sessions-root> --workflow <workflow-name> --mode report --since <iso8601> --format markdown
seq session-detail --root <sessions-root> --session-id <session_id> --format markdown
seq session-tooling --root <sessions-root> --session-id <session_id> --summary --group-by executable --format table
```

Use these when agents skip, reorder, or weaken workflow steps.

## Workdir or Repo Evidence

```bash
seq workdir-report --root <sessions-root> --workdir <absolute-workdir> --mode sessions --format table
seq workdir-report --root <sessions-root> --contains "<path-fragment>" --mode sessions --limit 20 --format table
```

Use these when a skill behaves differently in a specific repo or workdir.

## Validation Evidence

```bash
seq message-search --root <sessions-root> --contains "quick_validate" --roles assistant --limit 50 --format jsonl
seq tool-search --root <sessions-root> --contains "quick_validate.py" --mode rows --format table
seq tool-search --root <sessions-root> --contains "validate-changed-skills" --mode rows --format table
```

Use these for validation failures, omissions, or repeated blocked validation.

## Fallback

Use raw `seq query` only when no lifted command covers the evidence shape. When raw query behavior is unclear, diagnose it first:

```bash
seq query-diagnose --root <sessions-root> --session-id <session_id> --next-actions --format json
```

When falling back to raw query, include the query purpose and limits in the evidence ledger.
