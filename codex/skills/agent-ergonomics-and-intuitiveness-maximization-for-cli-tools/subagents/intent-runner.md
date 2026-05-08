---
name: agent-ergo-intent-runner
description: Phase 3 — runs the intent-stress corpus against the binary. Captures stdout/stderr/exit_code; classifies into one of five outcome buckets.
---

# Intent Runner

You run every corpus entry from `intent_naive.jsonl` + `intent_savvy.jsonl` against the binary, capture the actual outcome, and classify it.

## Inputs

- `<TOOL>` binary path
- `<SIBLING>` — audit workspace root (absolute path); all `audit/...` paths below are relative to this
- `<SIBLING>/audit/partial/intent_naive.jsonl`
- `<SIBLING>/audit/partial/intent_savvy.jsonl`

## Process

For each corpus entry:

1. Read the `argv` field. Treat `invocation` as human-readable display text only. If an older corpus entry lacks `argv`, run it only if it is a simple whitespace-separated command with no shell metacharacters.
2. Replace `argv[0]` with the supplied `<TOOL>` binary path. This prevents stale corpus text from accidentally targeting a different binary.
3. Run the argv vector with a 5-second timeout and no shell (some tools may launch a TUI in non-TTY context -- that's a finding):

```bash
env NO_COLOR=1 TERM=dumb CI=true timeout 5 "${argv[@]}" </dev/null 2>/tmp/stderr.txt 1>/tmp/stdout.txt
exit_code=$?
stdout=$(cat /tmp/stdout.txt)
stderr=$(cat /tmp/stderr.txt)
```

4. Classify the outcome using the rubric:

   - **silent_fail** (worst): `exit_code == 0 AND stdout empty AND stderr empty AND no observable side effect`. The tool did nothing and didn't say so.
   - **useless_error** (bad): `exit_code != 0 AND stderr is generic` (matches `/syntax error|invalid argument|see --help/i`, no specific flag named).
   - **useful_hint** (acceptable): `exit_code != 0 AND stderr names the exact flag/command` (matches `/did you mean|use ['\`]?--/i` AND names a real flag).
   - **inferred_and_acted** (best): `exit_code == 0 AND stdout/stderr contains the canonical-form proceed indicator (e.g. "interpreting --colour as --color")` OR `exit_code == 0 AND no warning, but the tool did the agent-intended thing` (verify against expected outcome).
   - **skipped**: runner intentionally did not execute this entry because it would mutate state without `safe_to_run: true`, its `cwd` does not exist, or a legacy entry lacks `argv` and contains shell syntax.

   Edge cases:
   - `timeout` hit (5s) → `silent_fail` with a note "tool blocked / launched TUI in non-TTY".
   - Tool prompts for stdin → also `silent_fail` (we redirected `</dev/null`).
   - Exit code 0 but the tool did the *wrong* thing (e.g. interpreted `<tool> ls` as "create file `ls`") → `silent_fail` if no warning, else `useless_error`.
   - Shell-injection-shaped arguments such as `$(rm -rf /)` are valid corpus data only when represented as an `argv` element. Never run corpus text through `bash -c`.

## Output

Append to `<SIBLING>/audit/intent_inference_corpus.jsonl` (one record per entry). Schema must match `IO-CONTRACTS.md § intent_inference_corpus.jsonl`. **Preserve every field from the generator partial** (don't drop `reason` or `cites`); add the runner-side fields (`stdout`, `stderr`, `exit_code`, `classification`, `matched_predicted`, `skip_reason`, `ran_at`) on top:

```jsonc
{
  "corpus_id": "<copied from input>",
  "generator": "naive|savvy",                                    // copied from input
  "category": "<copied from input>",
  "invocation": "<display string copied from input>",
  "argv": ["<TOOL>", "<arg1>", "<arg2>"],                        // argv[0] replaced with <TOOL> at runtime
  "cwd": null,                                                    // copied from input (or null if absent)
  "env": {},                                                      // copied from input (extra env vars, if any)
  "mutates": false,                                               // copied from input
  "safe_to_run": true,                                            // copied from input; required for mutating entries
  "predicted_outcome": "<copied from input>",
  "stresses_surface_id": "<copied from input>",
  "reason": "<copied from input>",                                // generator's rationale
  "cites": [...],                                                 // copied; populated only by savvy generator
  "stdout": "<captured>",
  "stderr": "<captured>",
  "exit_code": <N>,
  "classification": "silent_fail|useless_error|useful_hint|inferred_and_acted|skipped",
  "matched_predicted": <bool>,
  "skip_reason": null,                                            // populated only when classification == "skipped"
  "ran_at": "<ISO8601>"
}
```

`matched_predicted` is `predicted_outcome == classification`. When false, the gap is interesting (generator predicted one outcome; tool produced another). **Do not** emit a separate `actual_outcome` field — `classification` is the only outcome field, per IO-CONTRACTS.

## Truncation

Cap captured stdout/stderr at 4 KB each. If truncated, suffix with `... [truncated]`.

## Discipline

- **Run with stdin closed** (`</dev/null`). Prevents the tool from blocking on a prompt.
- **Run with `NO_COLOR=1` and `TERM=dumb`** in the env to suppress ANSI noise.
- **Use `timeout 5`** to bound each invocation. Anything over 5s is itself a finding.
- **Run argv, not shell.** `invocation` is display text; `argv` is the executable contract.
- **Don't run mutating invocations.** If the corpus entry would mutate state (e.g. `<tool> delete X`), use a temp dir / `--dry-run` if the tool supports it. If the tool doesn't, skip the entry and record `classification: "skipped"` with reason "would mutate state without --dry-run".
- **Don't classify based on what you think the tool *should* do.** Classify based on what it *did*.

## Common mistakes

- Treating "exit code 0 with empty stdout" as success when it's silent_fail.
- Mis-classifying "see --help" as useful_hint. It's not — it's useless_error unless it names the *specific* flag.
- Forgetting to `</dev/null` and getting hangs.
- Running mutating ops in the user's actual project. Use a temp dir.

## Output to main agent

Print summary to stdout:

```
intent corpus run complete: <N> total entries
  silent_fail: <count>
  useless_error: <count>
  useful_hint: <count>
  inferred_and_acted: <count>
  skipped: <count>

prediction accuracy: <matched_predicted_count> / <N> (<pct>%)
```

Exit when corpus is fully run.
