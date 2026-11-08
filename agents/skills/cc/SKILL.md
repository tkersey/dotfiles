---
name: cc
description: "Drive native Claude Code reviews through `claude -p`: the built-in /code-review (standard) or a caller's exact review instructions with schema-enforced output (custom). Freeze the Git subject, read back the exact session, transcribe standard results to findings JSON, and follow up on that session. Not ultrareview, /security-review, --fix, or --comment."
---

# CC

## Mission

Drive Claude Code's own review sessions, not a prompt that imitates review in the
caller's context. `$cc` is the skill's name; there is no `cc` executable or
wrapper. Call the installed `claude` CLI directly and preserve the caller's
subject, model, effort, permissions, and recovery budget.

Two review kinds:

- **Standard:** the built-in `/code-review`, uncustomized.
- **Custom:** the caller's exact instruction bytes (for example an Actuating lens
  or file-focus request) as the whole prompt of a fresh session, with output
  enforced by `--json-schema`. The default schema,
  [review-object.schema.json](references/review-object.schema.json), is the Codex
  review object from Actuating's pinned rubric. Never put custom instructions
  inside `/code-review`: its recipe fixes its angles, finding caps, reading rules,
  and output shape, and has no customization surface. A custom review never earns
  standard credit.

The runtime owns execution and its original output. The caller owns requirements,
review credit, finding truth, repairs, publication, and closure. Implicit
selection does not authorize a review campaign or any effect.

Out of scope: `claude ultrareview` (uploads the branch to the cloud),
`/security-review`, `/code-review --fix` (edits), `--comment` (publishes), and
cross-executor credit. Codex native review belongs to `$cas`.

`$skill_dir` below is this skill's base directory.

## Resolve settings before dispatch

Always pass `--model` and `--effort`, and for standard an explicit level. A fresh
`claude` process loading disk defaults is not inheritance, and `/code-review`
without a level reuses whatever level was typed last.

- **Invoked from Claude Code:** inherit the invoking session. Effort is
  `CLAUDE_EFFORT`. Model is `.message.model` of the latest assistant record in
  `~/.claude/projects/*/$CLAUDE_CODE_SESSION_ID.jsonl`; read only that record.
- **Invoked from Codex or elsewhere:** a Codex model does not transfer. Use the
  caller's explicit selection; otherwise resolve Claude Code's configured `model`
  and that model's `modelSettings.*.effortLevel` from user settings, and label
  them **configured default, not inherited**.
- An explicit caller override wins for its field only. If a value cannot be
  established, report it before dispatch; do not guess. Pass the full model ID.
- **Standard level** (`low|medium|high|xhigh|max`): the caller's explicit level,
  otherwise the selected effort. `max` only on explicit request; otherwise cap
  at `xhigh`.

## Freeze the subject

Resolve repository, base, and head before launch and keep them frozen.

- **Committed range:** run in a clean checkout of the bound head (a clean
  worktree if needed, without touching unrelated work). Reviewers read the
  working tree and see its git status, so untracked or modified files leak into
  findings (observed). Require `git merge-base --is-ancestor "$base" HEAD`: the
  standard recipe diffs `base` against HEAD (low level: against the working tree)
  directly, not from a merge base, so a non-ancestor base reviews the wrong diff.
- **No target argument (standard):** the native "current diff" is upstream...HEAD
  plus uncommitted changes. Bind that scope explicitly; do not use it as a
  substitute for a committed range.
- Launch from the repository root and recheck HEAD and working-tree/index state
  at admission.

## Launch

Reviews are read-only. `dontAsk` denies anything not allowed, so allow the
read-only Git commands reviewers need; a denied read leaves the subject unseen
(observed).

```bash
sid=$(uuidgen | tr '[:upper:]' '[:lower:]')
read_tools='Read Grep Glob Bash(git diff:*) Bash(git show:*) Bash(git log:*) Bash(git ls-files:*) Bash(git ls-tree:*) Bash(git cat-file:*) Bash(git rev-parse:*) Bash(git rev-list:*) Bash(git merge-base:*) Bash(git status:*) Bash(git grep:*) Bash(git blame:*) Bash(git check-ignore:*)'

# Standard
(cd "$repo" && claude -p --session-id "$sid" \
  --model "$selected_model" --effort "$selected_effort" \
  --permission-mode dontAsk --permission-prompts none --allowed-tools "$read_tools" \
  --disallowed-tools "Edit Write NotebookEdit Bash(gh:*)" \
  --output-format stream-json --verbose \
  "/code-review $level $base" </dev/null >"$events" 2>"$diagnostics")

# Custom: $prompt holds the exact instruction bytes
(cd "$repo" && claude -p --session-id "$sid" \
  --model "$selected_model" --effort "$selected_effort" \
  --permission-mode dontAsk --permission-prompts none --allowed-tools "$read_tools" \
  --disallowed-tools "Edit Write NotebookEdit Skill Task Workflow Bash(gh:*)" \
  --json-schema "$(cat "$skill_dir/references/review-object.schema.json")" \
  --output-format stream-json --verbose \
  <"$prompt" >"$events" 2>"$diagnostics")
```

- Use a new session ID and private `$events`/`$diagnostics` per attempt.
- Standard adds nothing beyond `/code-review <level> [target]`; keep `Task`
  available there because `xhigh`/`max` launch their own verifier subagents.
  Custom reviews may not launch reviewers or invoke skills.
- Do not pass `--no-session-persistence` (the transcript is evidence), `--bare`,
  `--safe-mode`, bypass flags, or wider tools; do not widen access after a failed
  check. `--json-schema` has no effect on `/code-review` (observed
  `structured_output: null`); structure standard results by transcription below.

## Read back the exact session

```bash
uv run --no-project python -I "$skill_dir/scripts/readback.py" standard \
  "$events" "$sid" "$selected_model" "$base" "$level" "$readback_json"
uv run --no-project python -I "$skill_dir/scripts/readback.py" custom \
  "$events" "$sid" "$selected_model" "$prompt" "$readback_json"
```

[readback.py](scripts/readback.py) writes the evidence and every problem, and
exits nonzero (hold) unless all of these hold:

- Init and result belong to `$sid` and the selected model; the run succeeded;
  `modelUsage` names only that model (no fallback); no permission was denied.
- **Standard:** the expanded recipe names the frozen target, its depth header
  names the bound level (observed: `medium` ran the `high` recipe), and a
  reviewer `git diff` used the target.
- **Custom:** exactly one transcript `<config>/projects/*/$sid.jsonl` exists and
  its first user message equals the prompt bytes; stream-json does not echo a
  piped prompt, so this is the delivery evidence. `structured_output` is present.

The caller also retains the host exit status and rechecks the Git subject. Never
select the latest session, a title match, or another review's file.

## Standard result: transcribe to findings JSON

`result.result` is rendered text, not a structured object; it stays the native
result. After admission, transcribe it with
[scripts/findings.py](scripts/findings.py):

```bash
uv run --no-project python -I "$skill_dir/scripts/findings.py" \
  "$events" "$sid" "$selected_model" "$findings_json"
```

The script reads only `$sid`'s successful `result` event, then makes one fresh,
tool-less, non-persistent `claude -p --json-schema` call that copies the text
into `findings[] {file, line, summary, failure_scenario, category?}` (the
`/code-review` ReportFindings shape). It writes the original text, its sha256,
the findings, and `transcription_ok`/`problems`, and exits nonzero when a
transcribed location is absent from the text, a stated finding count disagrees,
`(none)` yields findings, or other text yields none. Do not transcribe by
resuming the review session: it may hold later turns, and it costs ~10x more.

The JSON is a derived view for adjudication, not a new verdict. On a failed
check, adjudicate the original text. Empty findings earn clean credit only when
the original says nothing qualified (low level emits exactly `(none)`). Findings
remain findings regardless of any reassuring summary. Missing, ambiguous, or
stale evidence earns no credit.

## Custom result: the structured object

`structured_output` is the native result, validated by the CLI against the
schema; the prose `result` is not. Nonempty findings stay findings whatever
`overall_correctness` says. Empty findings with `patch is incorrect`, or a
material unresolved limitation in `overall_explanation`, earn no clean credit.
Confidence is not evidence.

## Observation, recovery, follow-up

- A wait timeout is not failure: keep observing the same process. Do not launch
  another review until the prior attempt is established terminal and the caller's
  recovery budget permits a distinct attempt.
- Cancellation: terminate only the host-owned process, confirm it exited, and
  treat a late result as evidence, not credit.
- **Incomplete inquiry follow-up** (caller-authorized): continue the same session
  with `claude -p --resume "$sid"` plus the same model, effort, permission, tool
  and schema flags, `--output-format stream-json --verbose`, `</dev/null`. Name
  the concrete gap, exact paths and ranges; ask it to complete the observation and
  reassess, overturning conclusions when warranted. The response is supplemental
  evidence attributed separately, not a new verdict or an additional clean.
- Compaction alone is not failure or a fresh review.

## Hard rules

- Standard is native `/code-review`, uncustomized; custom is the caller's exact
  bytes as the whole prompt. No imitation prompt, wrapper, receipt store, or
  attempt registry.
- Never edit, comment, post, push, or upload as part of a review.
- Never log secrets or publish raw transcripts or private reasoning.
- State which facts were observed. Missing evidence blocks only its dependent
  claim; it never authorizes broader permissions or executor substitution.
