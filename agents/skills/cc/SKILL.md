---
name: cc
description: "Drive native Claude Code reviews through `claude -p`: the bundled /review (standard) or a caller's exact review instructions with schema-enforced output (custom). Freeze the Git subject, enforce read-only execution, read back the exact session and original result, and follow up on that session. Not ultrareview, /security-review, --fix, or --comment."
---

# CC

## Mission

Drive Claude Code's own review sessions, not a prompt that imitates review in the
caller's context. `$cc` is the skill's name; there is no `cc` executable or
wrapper. Call the installed `claude` CLI directly and preserve the caller's
subject, model, effort, permissions, and recovery budget.

Two review kinds:

- **Standard:** the bundled `/review`, uncustomized. This alias keeps the native
  command when a local `code-review` skill shadows `/code-review`; see
  [native command resolution](https://code.claude.com/docs/en/code-review-local#change-or-build-on-the-review).
- **Custom:** the caller's exact instruction bytes (for example an Actuating lens
  or file-focus request) as the whole prompt of a fresh session, with output
  enforced by `--json-schema`. The default schema,
  [review-object.schema.json](references/review-object.schema.json), is the Codex
  review object from Actuating's pinned rubric. Never put custom instructions
  inside `/review`: its recipe owns the review angles, reading rules, and output
  shape. A custom review never earns changeset-standard convergence credit.

The runtime owns execution and its original output. The caller owns requirements,
review credit, finding truth, repairs, publication, and closure. Implicit
selection does not authorize a review campaign or any effect.

Out of scope: `claude ultrareview` (uploads the branch to the cloud),
`/security-review`, `/review --fix` (edits), `--comment` (publishes), and
cross-executor credit. Codex native review belongs to `$cas`.

`$skill_dir` below is this skill's base directory.

## Resolve settings before dispatch

Always pass `--model` and `--effort`, and for standard an explicit level. A fresh
`claude` process loading disk defaults is not inheritance, and `/review`
without a level reuses whatever level was typed last.

- **Invoked from Claude Code:** inherit the invoking session. Effort is
  `CLAUDE_EFFORT`. Model is `.message.model` of the latest assistant record in
  `<config>/projects/*/$CLAUDE_CODE_SESSION_ID.jsonl`, where `<config>` is
  `CLAUDE_CONFIG_DIR` or `~/.claude` by default; read only that record.
- **Invoked from Codex or elsewhere:** a Codex model does not transfer. Use the
  caller's explicit selection; otherwise resolve Claude Code's configured `model`
  and that model's `modelSettings.*.effortLevel` from user settings, and label
  them **configured default, not inherited**.
- An explicit caller override selects its field only; effective policy must
  permit it. If a value cannot be established, hold before dispatch; do not guess.
  Pass the full model ID.
- **Standard level** (`low|medium|high|xhigh|max`): the caller's explicit level,
  otherwise the selected effort. `max` only on explicit request; otherwise cap
  at `xhigh`.

Bind `CLAUDE_CODE_EFFORT_LEVEL` to `$selected_effort` on every launch and resume:
it overrides `--effort` and survives `--restricted`. Inspect effective managed
`env` and applicable global/per-model `maxEffortLevel` caps before dispatch; hold
if they change or lower the selected effort, or cannot be established. Do not
bypass policy. The recipe header establishes review level, not effective reasoning
effort. See [effort precedence](https://code.claude.com/docs/en/env-vars#precedence)
and [effort caps](https://code.claude.com/docs/en/settings-reference#maxeffortlevel).

## Freeze the subject

Resolve the repository and full base/head commit IDs before launch and keep them
frozen.

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

## Enforce read-only execution and launch

`--allowed-tools` grants approvals, not an exclusive tool inventory. `dontAsk`
also honors loaded allow rules, and Git commands can write (`git diff --output`).
Use restricted settings, an explicit inventory, and an enforced filesystem
boundary together; before/after Git checks detect changes but do not prevent them.
See the [CLI reference](https://code.claude.com/docs/en/cli-reference) and
[sandbox configuration](https://code.claude.com/docs/en/sandboxing).

Resolve `$repo`, `$git_dir` and `$git_common` to their physical absolute paths
(repository root, `git rev-parse --absolute-git-dir`, and
`git rev-parse --path-format=absolute --git-common-dir`). Include any additional
source directories in `denyWrite`. Keep Claude's runtime state, including
transcripts, and attempt files (`$settings`, `$prompt`, `$events`, `$diagnostics`,
`$readback_json`) outside those paths. Create these per-attempt settings with a
JSON encoder:

```bash
jq -n --arg repo "$repo" --arg git_dir "$git_dir" --arg git_common "$git_common" '
  {disableAllHooks: true, autoMemoryEnabled: false,
   sandbox: {enabled: true, failIfUnavailable: true,
     autoAllowBashIfSandboxed: false, allowUnsandboxedCommands: false,
     excludedCommands: [],
     filesystem: {disabled: false, denyWrite: [$repo, $git_dir, $git_common]}}}
' >"$settings"
```

`--restricted` excludes user/project settings while retaining project instructions.
Managed policy still applies: inspect it before dispatch. Only managed settings
can disable managed hooks; force-enabled plugins and managed MCP can also survive
ordinary disable flags. Hold if effective policy admits unbounded side effects,
overrides the sandbox, adds unsandboxed exclusions, or cannot be established.
Do not bypass it. See [settings precedence](https://code.claude.com/docs/en/settings)
and [hook controls](https://code.claude.com/docs/en/settings-reference#disableallhooks).
Require Claude Code 2.1.285 or newer, support for the flags and settings below,
and a functioning sandbox; unavailability is a hold, never permission to run
unsandboxed. Offline readback tests do not qualify the installed runtime's
filesystem enforcement or native verifier delegation.

```bash
sid=$(uuidgen | tr '[:upper:]' '[:lower:]')
read_tools=(Read Grep Glob
  'Bash(git diff:*)' 'Bash(git show:*)' 'Bash(git log:*)' 'Bash(git ls-files:*)'
  'Bash(git ls-tree:*)' 'Bash(git cat-file:*)' 'Bash(git rev-parse:*)'
  'Bash(git rev-list:*)' 'Bash(git merge-base:*)' 'Bash(git status:*)'
  'Bash(git grep:*)' 'Bash(git blame:*)' 'Bash(git check-ignore:*)')

# Standard
(cd "$repo" && GIT_OPTIONAL_LOCKS=0 CLAUDE_CODE_EFFORT_LEVEL="$selected_effort" \
  claude -p --session-id "$sid" \
  --model "$selected_model" --effort "$selected_effort" \
  --restricted --settings "$settings" --tools "Read,Grep,Glob,Bash,Agent" \
  --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
  --permission-mode dontAsk --permission-prompts none --allowed-tools "${read_tools[@]}" Agent \
  --disallowed-tools Edit Write NotebookEdit Skill Workflow 'mcp__*' \
  --output-format stream-json --verbose \
  "/review $level $base..HEAD" </dev/null >"$events" 2>"$diagnostics")

# Custom: $prompt holds the exact instruction bytes
(cd "$repo" && GIT_OPTIONAL_LOCKS=0 CLAUDE_CODE_EFFORT_LEVEL="$selected_effort" \
  claude -p --session-id "$sid" \
  --model "$selected_model" --effort "$selected_effort" \
  --restricted --settings "$settings" --tools "Read,Grep,Glob,Bash" \
  --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
  --permission-mode dontAsk --permission-prompts none --allowed-tools "${read_tools[@]}" \
  --disallowed-tools Edit Write NotebookEdit Skill Agent Task Workflow 'mcp__*' \
  --json-schema "$(cat "$skill_dir/references/review-object.schema.json")" \
  --output-format stream-json --verbose \
  <"$prompt" >"$events" 2>"$diagnostics")
```

- Use a new session ID and private `$events`/`$diagnostics` per attempt.
- Standard adds nothing beyond `/review <level> <base>..HEAD`; retain native
  verifier delegation (`Agent`) under the same restrictions. Pass the range, not
  a bare base: the recipe can read a bare SHA as one commit to show and review
  that commit instead of the bound diff (observed). Custom reviews may not launch
  reviewers or invoke skills.
- Do not pass `--no-session-persistence` (the transcript is evidence), `--bare`,
  `--safe-mode`, bypass flags, or wider tools; do not widen access after a failed
  check. Standard output stays the native rendered text; do not require
  `--json-schema` or another model call to interpret it.

## Read back the exact session

```bash
uv run --no-project python -I "$skill_dir/scripts/readback.py" standard \
  "$events" "$sid" "$selected_model" "$base..HEAD" "$level" "$readback_json"
uv run --no-project python -I "$skill_dir/scripts/readback.py" custom \
  "$events" "$sid" "$selected_model" "$prompt" "$readback_json"
```

For an explicitly bound current-diff review, omit the CLI target and pass `-` as
the helper's target instead of `$base..HEAD`.

[readback.py](scripts/readback.py) writes the evidence and every problem, and
exits nonzero (hold) unless all of these hold:

- Init and result belong to `$sid` and the selected model; the run succeeded;
  `modelUsage` names only that model (no fallback).
- **Standard:** native result text is nonempty; the expanded recipe names the
  frozen target, its depth header names the bound level (observed: `medium` ran
  the `high` recipe), and a
  matching reviewer `git diff` has a correlated successful tool result.
  A command request alone, a failed read, or a result for another tool call is
  insufficient. The helper recognizes direct patch reads, including ordinary
  context options and explicit path limits. A successful per-file read does not
  establish complete changeset coverage; the caller judges that separately.
  It recognizes bounded `;`/`&&` chains without treating quoted or escaped
  operators as shell syntax. A successful compound result establishes a target
  read only in its final `&&` group. Thus `git diff <base>..HEAD && git diff HEAD`
  can establish completion, while `git diff <base>..HEAD; git diff HEAD` leaves
  the target's status unavailable even when patch text appears. Companion output
  cannot authenticate a target read. Exit 1 from `--exit-code` is recognized only
  for a direct diff. Summary-only reads, pipes, redirects, substitutions, and
  unsupported command shapes do not establish this gate. Retain an unverified
  compound observation and use the existing same-session inquiry follow-up when
  needed; do not replace the native recipe or infer success from patch markers.
  Recipe text alone does not authenticate native command resolution;
  retain the host's actual `/review` invocation.
- **Custom:** exactly one transcript `<config>/projects/*/$sid.jsonl` exists and
  its first user message equals the prompt bytes; stream-json does not echo a
  piped prompt, so this is the delivery evidence. `structured_output` is present.

Permission denials remain in the report for caller adjudication. An unresolved
required read holds credit; a recovered, covered, or demonstrably unnecessary
check follows the caller's existing limitation rules. Preserve the denied
operation as denied. `ok` establishes only these execution checks, not a clean
verdict or complete inquiry. The caller also retains the host exit status,
effective boundary, and rechecks the Git subject. Never select the latest session,
a title match, or another review's file.

## Standard result: adjudicate the original text

`result.result` is the native rendered result. Preserve it unchanged and pass it
directly to the caller's existing finding and limitation adjudication. Ordinary
clean prose is valid evidence; no exact `(none)` sentinel, findings JSON, or second
model call is required. The helper does not infer whether text is clean.

Account for every reported finding and limitation. A reassuring summary cannot
erase a finding; an optional derived view cannot replace the original or become
an admission gate. Missing, ambiguous, or stale evidence earns no credit for its
dependent claim.

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
  with `CLAUDE_CODE_EFFORT_LEVEL="$selected_effort" claude -p --resume "$sid"`
  plus the same model, effort, permission, tool and schema flags,
  `--output-format stream-json --verbose`, `</dev/null`. Name
  the concrete gap, exact paths and ranges; ask it to complete the observation and
  reassess, overturning conclusions when warranted. The response is supplemental
  evidence attributed separately, not a new verdict or an additional clean.
  For an unverified compound diff, request a standalone foreground
  `git diff <base>..HEAD` and reassessment of conclusions dependent on that read.
  Capture each resumed invocation in its own events file, retaining the actual
  resume invocation and unchanged Git subject; never concatenate terminal streams.
  Pass the original events plus the supplemental stream to standard readback:

  ```bash
  uv run --no-project python -I "$skill_dir/scripts/readback.py" standard \
    "$events" "$sid" "$selected_model" "$base..HEAD" "$level" "$readback_json" \
    --followup "$followup_events"
  ```

  Repeat `--followup` in execution order only within the caller's recovery budget.
  The helper checks each stream's session, model, terminal result and correlated
  reads. It preserves the original `result`, every failed/unverified read, and
  supplemental results and denials under `followups`. Adjudicate all of them;
  successful readback does not establish adequate reassessment or erase a finding.
- Compaction alone is not failure or a fresh review.

## Hard rules

- Standard is bundled `/review`, uncustomized; custom is the caller's exact
  bytes as the whole prompt. No imitation prompt, wrapper, receipt store, or
  attempt registry.
- Never edit, comment, post, push, or upload as part of a review.
- Never log secrets or publish raw transcripts or private reasoning.
- State which facts were observed. Missing evidence blocks only its dependent
  claim; it never authorizes broader permissions or executor substitution.
