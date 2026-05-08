# POLISH-BAR — Verification Queries

The Polish Bar in SKILL.md is a 12-row "must satisfy" list. This file gives the *queries* that prove or disprove each row, plus a dispute-resolution flowchart for ambiguous cases.

Run these against the post-apply binary in Phase 6 / Phase 8 / Phase 9. Failure on any row is a Phase 5 / Phase 8 rework target.

---

## Row 1 — First-try success

**Query.** Run all of these and confirm they all produce useful output (not crash, not silent_fail, not block on a TUI in non-TTY context):

```bash
<tool>                                         # bare invocation
<tool> --help
<tool> -h
<tool> help
<tool> --version
<tool> -V
echo | <tool>                                  # stdin closed
<tool> < /dev/null                             # stdin /dev/null
```

**Pass criteria.**
- Each command returns within 2s.
- Each command produces stdout OR a useful stderr message.
- None launches a TUI when stdout is not a TTY.

**Fail-→-fix.** Add a `--help` shim if missing. Detect non-TTY and print a one-line guide to `--robot-*` mode. Never silent-exit on a probe.

---

## Row 2 — JSON everywhere

**Query.** For every read-side verb in `surface_inventory.jsonl` (kind=verb, mutates=false):

```bash
<tool> <verb> --json | jq . > /dev/null && echo PASS || echo FAIL
```

**Pass criteria.** Every read-side verb has either `--json`, `--robot-*`, or an equivalent machine-readable mode. Output is valid JSON. `jq .` does not error.

**Fail-→-fix.** Add `--json` flag to the verb. Document the schema in `<tool> capabilities --json` under `commands[<verb>].output_schema`.

---

## Row 3 — Capabilities endpoint

**Query.**
```bash
<tool> capabilities --json | jq -r '
  ["version", "contract_version", "features", "commands", "exit_codes", "env_vars"]
  | map(. as $k | if (input | has($k)) then "✓" else "✗" end)
  | join(",")'
```

**Pass criteria.** All 6 required keys present. JSON is valid. `version` is a semver string. `contract_version` is monotonic across releases. `features` is a list of strings. `commands` is a dict keyed by verb name. `exit_codes` is a dict keyed by exit value. `env_vars` is a dict keyed by env-var name.

**Fail-→-fix.** Implement the missing keys. Treat `capabilities --json` as a contract-pinning surface — it's the agent's introspection lifeline.

---

## Row 4 — Robot-docs endpoint

**Query.**
```bash
<tool> robot-docs guide 2>&1 | wc -l   # should print 10–80 lines of agent-targeted handbook
```

Or:
```bash
<tool> --robot-help 2>&1 | head -40    # alternative form
```

**Pass criteria.** Output is < 80 lines (concise — paste-ready). Mentions `--json` / `--robot-*`, exit-code contract, stdout/stderr split. Doesn't require external doc lookup.

**Fail-→-fix.** Write a robot-docs handbook in-tool. Pattern: see `cass robot-docs guide` (output formats, search contracts, default modes, doctor branches, safety hints).

---

## Row 5 — Mega-command

**Query.** Identify the canonical agent task for this CLI. Confirm there is a single mega-call that returns multiple useful slices in one invocation. Example pattern: `bv --robot-triage` returns `quick_ref + recommendations + quick_wins + blockers + project_health + commands`.

```bash
<tool> --robot-triage --json | jq 'keys'   # should have ≥ 3 useful top-level keys
```

**Pass criteria.** At least one mega-call exists. The mega-call returns ≥ 3 distinct useful slices. Among those slices, at least one is "copy-paste-ready follow-up commands" (e.g. `commands: ["<tool> X --json", "<tool> Y --json"]`).

**Fail-→-fix.** Add a mega-command that bundles the top 3+ canonical-task data slices.

---

## Row 6 — Exit-code contract

**Query.** Read `<tool> capabilities --json | jq .exit_codes`. Confirm every documented exit value matches the source's `exit(N)` sites.

```bash
<tool> capabilities --json | jq -r '.exit_codes | keys | join(",")'
# Then verify with: rg 'exit\((\d+)\)|process\.exit\((\d+)\)|os\.Exit\((\d+)\)' <target>/src
```

**Pass criteria.** Every exit-code site in source matches a documented value. No exit-code value is used for two different semantic conditions. `0` is reserved for success.

**Fail-→-fix.** Document every exit code. If the same value is used for two conditions, fork into different values and update the dictionary.

---

## Row 7 — Error pedagogy

**Query.** For each entry in `intent_inference_corpus.jsonl` with `classification:"useless_error"`, the error message should be upgraded to `useful_hint` or `inferred_and_acted`.

Sample 5 random useless_error entries; manually inspect:

```bash
<tool> <wrong_invocation> 2>&1 | head -10
```

**Pass criteria.** Every error message names: (a) what failed, (b) where (file:line if applicable), (c) the *exact* flag/command/env-var the agent should have used. No "see --help" without a specific pointer.

**Fail-→-fix.** Wrap framework-default errors with project-specific guidance. See OPERATORS.md § Card 12.

---

## Row 8 — Intent inference

**Query.** Try common typos and aliases:

```bash
<tool> --jsno      # typo of --json
<tool> --colour    # spelling variant of --color
<tool> ls          # alias-style for list
<tool> rm          # alias-style for delete
```

**Pass criteria.** Each either succeeds (with a one-line warning naming the canonical form) OR errors with a "did you mean X?" hint that names the right form.

**Fail-→-fix.** Add levenshtein-distance-1 typo correction. Add a small list of common aliases (`ls→list`, `rm→delete`, `colour→color`, `vebose→verbose`) with deprecation warnings.

---

## Row 9 — Dangerous-op gating

**Query.** For every mutating verb in `surface_inventory.jsonl` (kind=verb, mutates=true):

```bash
<tool> <verb> <args>                      # should refuse without --yes/--force
<tool> <verb> <args> --dry-run            # should show plan
<tool> <verb> <args> --plan               # equivalent
<tool> <verb> <args> --yes                # should proceed
```

**Pass criteria.** Every irreversible op requires explicit `--yes`/`--force`/`--confirm=<token>` AND offers `--dry-run` / `--plan`. Error message names the safe alternative.

**Fail-→-fix.** Add `--dry-run` flag. Add `--yes`/`--force` gate. Update error message to name the safe alt.

---

## Row 10 — Determinism

**Query.**
```bash
<tool> X --json > /tmp/run1.json
<tool> X --json > /tmp/run2.json
diff /tmp/run1.json /tmp/run2.json     # should be empty (or only known volatile fields)
```

For runs across two machines / two SHAs:
```bash
SOURCE_DATE_EPOCH=1234567890 <tool> X --json > /tmp/run-pinned-1.json
SOURCE_DATE_EPOCH=1234567890 <tool> X --json > /tmp/run-pinned-2.json
diff /tmp/run-pinned-1.json /tmp/run-pinned-2.json  # MUST be empty
```

**Pass criteria.** Same input → same output bytes. Stable ordering (sorted or insertion-order). No raw timestamps in stdout. Volatile fields (request_id, timestamp) are isolated to documented JSON fields, not interleaved in prose.

**Fail-→-fix.** Sort iteration order before serialization. Move timestamps to JSON `meta.{ts, request_id}` fields. Honor `SOURCE_DATE_EPOCH`.

---

## Row 11 — NO_COLOR / CI / non-TTY

**Query.**
```bash
NO_COLOR=1 <tool> X | xxd | head | grep -E 'esc\[|\x1b'   # should find nothing
<tool> X | cat | xxd | head | grep -E 'esc\[|\x1b'        # piped — should find nothing
TERM=dumb <tool> X | xxd | head | grep -E 'esc\[|\x1b'    # should find nothing
CI=true <tool> --interactive-verb                          # should not block on prompt
```

**Pass criteria.** Honors `NO_COLOR=1`, piped stdout, `TERM=dumb`. Auto-detects non-TTY and disables color/spinners/progress bars/interactive prompts. Honors `CI=true` to suppress prompts.

**Fail-→-fix.** Use `is-terminal` / `term::isatty()` etc. Plumb the env-var checks through the styling layer.

---

## Row 12 — Regression test

**Query.** (run from any cwd; substitute `<SIBLING>` with the audit workspace's absolute path)
```bash
ls "<SIBLING>/audit/regression_tests/"
# Should have one *.test.{sh,rs,py,ts} per applied recommendation R-NNN.
```

For each test:
```bash
bash "<SIBLING>/audit/regression_tests/R-NNN__"*.test.sh && echo PASS || echo FAIL
```

**Pass criteria.** Every applied recommendation has a regression test. Test file is named `R-NNN__<short_description>.test.{sh,rs,py,ts}`. Test exits 0 on success, ≥1 on failure with a clear message.

**Fail-→-fix.** Add the missing test. Run it against the post-apply binary; verify it passes.

---

## Dispute-resolution flowchart

When two scorers (or a reviewer and an applier) disagree on whether a Polish Bar row passes:

1. **Re-run the query.** Most disputes are stale state — re-run against the current binary on a clean clone.
2. **Cite the rubric anchor.** If the dispute is over "what counts as useful_hint" (or any subjective threshold), look up the rubric anchor in SCORING-RUBRIC.md and use its example.
3. **Look at the canonical exemplar.** "What would `bv --robot-triage` / `dcg explain` / `cass capabilities` do here?" Match that pattern.
4. **If still disputed, file a tiebreaker.** Spawn `subagents/scorer-tiebreaker.md` for the affected dimension. The median of three scores wins; spread is recorded as `score_confidence`.
5. **If the rubric itself is unclear,** the rubric is a living artifact. File a bead to refine the anchor; bump `rubric_version`. Document the change in HANDOFF.md.

---

## When the Polish Bar can be relaxed

The bar is non-negotiable for **agent-targeted CLIs**. For human-only CLIs (rare in this audience), Rows 2, 3, 4, 5, and 8 may be relaxed (a human reads `--help` and uses the canonical form).

But: any CLI that an agent might use is an "agent-targeted CLI." Default to enforcing the full bar unless there's a documented reason not to.
