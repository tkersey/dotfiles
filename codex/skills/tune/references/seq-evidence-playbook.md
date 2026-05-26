# `$seq` Evidence Playbook for `$tune`

Prefer specialized `$seq` commands before raw `seq query`. Build an evidence ledger that records what each command proves and what it does not prove.

## Evidence Discipline

- Read the target skill before judging usage.
- Use recent evidence by default: last 90 days for general tuning unless the user supplies another window.
- Distinguish raw skill mentions from successful activations.
- Prefer session-level, workflow-level, and validation-level proof over isolated text matches.
- Search for counterevidence, not only confirming examples.
- Sanitize user-facing summaries. Do not include raw transcript text unless explicitly requested and safe.
- Use raw `seq query` only when no lifted command covers the evidence shape.

## Baseline Skill Usage

```bash
seq skill-success-rank --root ~/.codex/sessions --skill <skill> --mode sessions --last 90d --format jsonl
seq skill-audit --root ~/.codex/sessions --skill <skill> --mode trend --since <iso8601> --format table
seq skill-cohort --root ~/.codex/sessions --skill <skill> --since <iso8601> --format table
```

Use these to distinguish successful activations, raw mentions, and co-occurring skills.

Ledger prompts:

- What counts as successful activation here?
- Are there enough relevant activations to tune safely?
- Which companion skills co-occur and might indicate boundary overlap?

## Historical Skill Definitions

```bash
seq skill-blocks --root ~/.codex/sessions --skill <skill> --history latest --format json
seq skill-blocks --root ~/.codex/sessions --skill <skill> --history all --format jsonl
```

Use these when usage changed after a skill update or when old skill-block text may explain behavior.

Ledger prompts:

- Did the contract change during the evidence window?
- Are agents using stale skill text?
- Is this a historical regression or a current-contract issue?

## Trigger and Failure Phrase Search

```bash
seq message-search --root ~/.codex/sessions --contains "<phrase>" --roles user,assistant --limit 50 --format jsonl
seq message-audit --root ~/.codex/sessions --contains "<phrase>" --roles user,assistant --show-query --format json
```

Use these for missed activation, false activation, partial activation, user correction, and mode-selection patterns.

Ledger prompts:

- Is the phrase a user trigger, an assistant self-mention, or both?
- Does the result prove a routing failure or only a possible trigger overlap?
- Are there safe counterexamples where the current behavior was correct?

## Tooling Evidence

```bash
seq tool-search --root ~/.codex/sessions --contains "<command-fragment>" --mode rows --format table
seq tool-search --root ~/.codex/sessions --contains "<command-fragment>" --mode args --format jsonl
seq tool-audit --root ~/.codex/sessions --group-by executable --since <iso8601> --limit 20 --format table
```

Use these when repeated command sequences may justify a helper script.

Ledger prompts:

- Is the command pattern repeated enough to justify tooling?
- Is the work deterministic, or is it judgment-heavy?
- Would a script reduce fragility without hiding reasoning?

## Workflow Evidence

```bash
seq workflow-audit --root ~/.codex/sessions --workflow <workflow-name> --mode report --since <iso8601> --format markdown
seq session-detail --root ~/.codex/sessions --session-id <session_id> --format markdown
seq session-tooling --root ~/.codex/sessions --session-id <session_id> --summary --group-by executable --format table
```

Use these when agents skip, reorder, or weaken workflow steps.

Ledger prompts:

- Which required step was skipped or misordered?
- Did the session have enough context for the step to be required?
- Did validation pass, fail, or never run?

## Workdir or Repo Evidence

```bash
seq workdir-report --root ~/.codex/sessions --workdir <absolute-workdir> --mode sessions --format table
seq workdir-report --root ~/.codex/sessions --contains "<path-fragment>" --mode sessions --limit 20 --format table
```

Use these when a skill behaves differently in a specific repo or workdir.

Ledger prompts:

- Is the behavior repo-specific or general?
- Are local paths sanitized before reporting?
- Is the target skill's contract repo-aware?

## Validation Evidence

Search for validation failures, omissions, or repeated blocked validation:

```bash
seq message-search --root ~/.codex/sessions --contains "quick_validate" --roles assistant --limit 50 --format jsonl
seq tool-search --root ~/.codex/sessions --contains "quick_validate.py" --mode rows --format table
seq tool-search --root ~/.codex/sessions --contains "validate-changed-skills" --mode rows --format table
```

Ledger prompts:

- Was validation required by the skill contract?
- Was validation run, blocked, or only mentioned?
- Did script changes receive representative sample runs?

## Fallback

Use raw `seq query` only when no lifted command covers the evidence shape. When raw query behavior is unclear, diagnose it first:

```bash
seq query-diagnose --root ~/.codex/sessions --session-id <session_id> --next-actions --format json
```

When falling back to raw query, include the query purpose and limits in the evidence ledger.
