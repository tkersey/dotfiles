# `$tune` Evidence Source Model

Evidence is the data plane. `$tune` is the diagnosis and refinement-policy layer. Keep them separate.

## Source Kinds

### `in-flight`

Use for evidence from the current interaction:

- current user feedback,
- current prompt wording,
- visible assistant behavior in the active conversation,
- current tool output,
- current observed behavior,
- current worktree or command results produced in this turn.

Strengths:

- Best for immediate routing, mode selection, and workflow gaps.
- Strong when the user explicitly identifies the problem.

Limits:

- Does not prove recurrence.
- Does not prove historical activation rates.
- Should support narrow local edits unless corroborated by history.

### `history`

Use for prior Codex sessions, memory artifacts, tool traces, workflow records, and historical skill blocks. `$seq` is the default adapter.

Scopes:

- recent window, such as last 90 days,
- arbitrary date range,
- explicit session ids,
- workdir or repo cohort,
- all relevant history when explicitly requested.

Strengths:

- Best for recurrence, historical regressions, missed activations, false activations, and repeated workarounds.

Limits:

- Requires explicit scope.
- Raw transcript text must be sanitized.
- Broad unbounded scans need a sampling or narrowing plan.

### `provided`

Use for user-supplied evidence: refinement briefs, logs, transcripts, observed output, diffs, bug reports, screenshots, or artifacts.

Strengths:

- Best when the user already has concrete evidence.
- Can justify direct `$refine` if complete and narrow.

Limits:

- Provenance may be partial.
- Evidence may be stale or selective.
- Counterevidence may require history or worktree checks.

### `worktree`

Use for repository-local evidence: target skill files, `agents/openai.yaml`, scripts/references/assets, Git status, staged/unstaged changes, and commit/push context.

Strengths:

- Required for applied changes and publishing.

Limits:

- Does not prove user-facing behavior without in-flight, historical, or provided evidence.

### `mixed`

Use when the question combines current behavior with historical recurrence or when apply-mode requires worktree evidence in addition to usage evidence.

Rules:

- Keep separate ledger entries for each source kind.
- Do not synthesize until source-specific limits are recorded.
- If sources disagree, report the conflict and prefer proposal-only unless a narrow edit is clearly supported.

## Source Descriptor Template

```text
Evidence source:
- Kind: in-flight | history | provided | worktree | mixed
- Locator: current conversation | sessions root | session id | workdir | repo | file/artifact | observed output
- Scope: current turn | current conversation | recent window | arbitrary history | explicit sessions | supplied evidence
- Window: <duration/date range/all/none>
- Access method: current context | $seq command | file read | tool output | user-provided text
- Privacy constraint: summarize only | raw excerpts allowed if safe | no raw transcript
- Limitation: <what this source cannot prove>
```

## Selection Rules

- Use `in-flight` first when the user references the current conversation or live behavior.
- Use `history` when the user asks about recurrence, trends, recent usage, old behavior, or arbitrary session history.
- Use `provided` when the user supplies evidence and asks you to interpret or apply it.
- Use `worktree` whenever files may be edited, committed, or pushed.
- Use `mixed` when a current problem needs historical recurrence checks or when apply-mode combines usage evidence with worktree proof.

## Arbitrary History Rules

When the user requests arbitrary history:

- Do not silently substitute the 90-day default.
- Ask the data adapter for the broadest relevant scope it can support, or use explicit session ids, date ranges, workdir/repo filters, and skill-block history.
- Use a narrowing or sampling plan when unbounded history is too large.
- Record what was searched and what was not searched.
- Treat incomplete arbitrary-history scans as medium or low confidence unless the result is directly dispositive.

## In-Flight Rules

When tuning in flight:

- Current user feedback can be strong evidence for a local correction.
- Current observed behavior or tool failure can be strong evidence for a workflow gap.
- Current routing behavior can indicate an activation or interpretation gap.
- Do not claim recurrence unless history also supports it.
- Keep raw conversation text out of reports unless the user explicitly asks and it is safe.
