# SURFACE-CLASSES — Per-class scoring guidance

Not every dimension applies equally to every surface class. This file gives explicit guidance for scoring each kind of surface.

`surface_id` encodes `kind`, so the scorer reads `kind` from the inventory record and applies the table below.

---

## verb (subcommand)

A verb is a top-level or nested subcommand. Examples: `<tool> list`, `<tool> add`, `<tool> sync sub`.

| Dim | Applicability | Scoring guidance |
|-----|---------------|------------------|
| 1 intuitiveness | High | Does the verb name match what an agent would guess? `list` > `enumerate`. |
| 2 ergonomics | High | Round-trips for canonical task using this verb. |
| 3 ease_of_use | High | `--help` for this verb has examples + cross-links. |
| 4 parseability | High | Does this verb have `--json` / `--robot-*`? Output stable schema? |
| 5 error_pedagogy | High | Errors from this verb teach? |
| 6 intent_inference | High | Aliases (`ls`/`list`), typo correction. |
| 7 safety | High if mutating; n/a (1000) if read-side | Set `mutates:bool` correctly in inventory. |
| 8 determinism | Medium | Output ordering stable. |
| 9 self_doc | High | `<verb> --help` is sufficient + points to capabilities. |
| 10 composability | High | Pipes cleanly. Honors NO_COLOR. Non-TTY safe. |
| 11 regression_resistance | High | Has snapshot/contract tests for this verb's output. |

---

## flag

A flag is a `--<long>` or `-<short>` option. Examples: `--json`, `-v`, `--robot-meta`.

| Dim | Applicability | Scoring guidance |
|-----|---------------|------------------|
| 1 intuitiveness | High | Does the flag name match conventions? `--json` > `--output-format=json`. |
| 2 ergonomics | Medium | Is there a short alias for the canonical-task flag? |
| 3 ease_of_use | High | Mentioned in `--help` with example. |
| 4 parseability | High | Especially for output flags (`--json`, `--robot-*`). |
| 5 error_pedagogy | Medium | When the flag's value is invalid, does the error teach? |
| 6 intent_inference | High | Typo correction. Deprecated spellings handled. |
| 7 safety | High if it triggers mutation; n/a (1000) otherwise | `--force`, `--yes`, `--confirm=token`. |
| 8 determinism | Medium | If the flag affects randomness/seed, is it captured deterministically? |
| 9 self_doc | High | Documented in capabilities? |
| 10 composability | Medium | Honors `NO_COLOR=1` style if relevant. |
| 11 regression_resistance | Medium | Test pinning the flag's behavior. |

---

## env (environment variable)

An environment variable read by the tool. Examples: `MYTOOL_HOME`, `MYTOOL_CONFIG`, `XDG_CONFIG_HOME` overrides.

| Dim | Applicability | Scoring guidance |
|-----|---------------|------------------|
| 1 intuitiveness | Medium | Does the env var name follow `<TOOL_PREFIX>_*` convention? |
| 2 ergonomics | Low | Setting an env var is a one-liner. |
| 3 ease_of_use | High | Is the env var documented in `--help` or `capabilities`? |
| 4 parseability | n/a (1000) | Env vars are inputs, not outputs. |
| 5 error_pedagogy | High | When the env var is malformed (bad path, bad value), does the error teach? |
| 6 intent_inference | Medium | Typo in env-var name → does the tool warn or silent-fall-back? |
| 7 safety | n/a (1000) | Env vars don't trigger destructive ops directly. |
| 8 determinism | Medium | Honoring `SOURCE_DATE_EPOCH`, etc. |
| 9 self_doc | High | Listed in `capabilities --json`'s `env_vars` dict. |
| 10 composability | High | Doesn't conflict with widely-used env vars (`HOME`, `TMPDIR`); honors `XDG_*`. |
| 11 regression_resistance | Low | Test for env-var resolution. |

---

## exit (exit code)

A documented exit-code value. Examples: `exit(0)`, `exit(1)`, `exit(2)`.

| Dim | Applicability | Scoring guidance |
|-----|---------------|------------------|
| 1 intuitiveness | n/a (1000) | Exit codes aren't user-facing. |
| 2 ergonomics | Medium | Exit codes are read by scripts; clear contract reduces logic. |
| 3 ease_of_use | Medium | Documented in `--help`. |
| 4 parseability | High | Exit-code contract is THE machine-readable signal. Score by the rubric in §6 (Exit-Code-Contract). |
| 5 error_pedagogy | High | Does the source comment explain what value means what? Does `capabilities --json` document it? |
| 6 intent_inference | n/a (1000) | Exit codes don't infer intent. |
| 7 safety | n/a (1000) | Same. |
| 8 determinism | High | Same input → same exit code. (Tools that exit 0 sometimes / 1 sometimes for the same input score 0 here.) |
| 9 self_doc | High | Listed in `capabilities --json`'s `exit_codes` dict. |
| 10 composability | High | Stable across versions; documented. |
| 11 regression_resistance | High | Test pinning the exit code for known scenarios. |

---

## error (error message)

A specific error message string. Examples: `"no store configured"`, `"invalid configuration at config.toml:12"`.

| Dim | Applicability | Scoring guidance |
|-----|---------------|------------------|
| 1 intuitiveness | n/a (1000) | Errors aren't user-chosen. |
| 2 ergonomics | n/a (1000) | Same. |
| 3 ease_of_use | n/a (1000) | Same. |
| 4 parseability | Medium | Is the error machine-readable (e.g. JSON when `--json` is set)? |
| 5 error_pedagogy | High | THIS IS THE PRIMARY DIM. Score by Polish Bar Row 7 + Operator Card 12. |
| 6 intent_inference | High | If error is a result of a wrong invocation, does it suggest the right one? |
| 7 safety | High if error gates a destructive op | "Use --dry-run first" suggestion. |
| 8 determinism | n/a (1000) | Errors don't contribute to determinism. |
| 9 self_doc | Medium | Error message references the relevant doc / flag. |
| 10 composability | High | Goes to stderr, never stdout. |
| 11 regression_resistance | High | Test pinning the error text for known broken inputs. |

---

## config (config-file key)

A key in a TOML/YAML/JSON config file the tool reads. Examples: `default_target`, `[providers.stripe]` section.

| Dim | Applicability | Scoring guidance |
|-----|---------------|------------------|
| 1 intuitiveness | High | Key name matches user expectation. |
| 2 ergonomics | Medium | Defaults sensible; minimal config required. |
| 3 ease_of_use | High | `<tool> config show --json` or `<tool> capabilities --json` exposes config schema. |
| 4 parseability | High | Config schema documented; `--json` config dump validates. |
| 5 error_pedagogy | High | Malformed config → error names the file + line + key + expected type. |
| 6 intent_inference | Medium | Typo in key name → "did you mean X?" |
| 7 safety | Medium | Destructive defaults gated. |
| 8 determinism | Medium | Same config → same behavior. |
| 9 self_doc | High | Schema export + `<tool> config show`. |
| 10 composability | Medium | Honors XDG config dir. |
| 11 regression_resistance | Medium | Test pinning the config schema. |

---

## signal (signal handler)

A signal the tool handles. Examples: SIGINT (clean shutdown), SIGTERM, SIGUSR1.

| Dim | Applicability | Scoring guidance |
|-----|---------------|------------------|
| 1 intuitiveness | n/a (1000) | Signals aren't user-chosen at the keyboard level. |
| 2 ergonomics | Medium | Ctrl+C cleans up promptly. |
| 3 ease_of_use | Low | Documented behavior under SIGINT. |
| 4 parseability | n/a (1000) | Same. |
| 5 error_pedagogy | Medium | "Aborted by user" message vs silent kill. |
| 6 intent_inference | n/a (1000) | Same. |
| 7 safety | High | Ctrl+C during a destructive op leaves state recoverable, not half-applied. |
| 8 determinism | Medium | Re-running after a signal-aborted run is safe (idempotent). |
| 9 self_doc | Low | Documented somewhere. |
| 10 composability | High | Honors signals correctly when run as a subprocess. |
| 11 regression_resistance | Low | Test for signal handling. |

---

## prompt (interactive prompt)

A point where the tool blocks for user input. Examples: "Are you sure? [y/N]", "Enter password:".

| Dim | Applicability | Scoring guidance |
|-----|---------------|------------------|
| 1 intuitiveness | n/a (1000) | Same. |
| 2 ergonomics | n/a (1000) | Prompts are friction by definition. |
| 3 ease_of_use | n/a (1000) | Same. |
| 4 parseability | n/a (1000) | Same. |
| 5 error_pedagogy | High | When prompt is bypassed (`--yes`), does the error teach the safe path? |
| 6 intent_inference | n/a (1000) | Same. |
| 7 safety | High | Prompt acts as the safety gate. Good. |
| 8 determinism | n/a (1000) | Same. |
| 9 self_doc | High | Prompt has a documented `--yes` / `--no-prompt` bypass. |
| 10 composability | High (CRITICAL) | Prompt must NEVER appear in non-TTY context. Auto-detect non-TTY → exit non-zero with "use --yes" hint OR proceed with conservative default. |
| 11 regression_resistance | Medium | Test that prompt doesn't appear in non-TTY. |

---

## How to apply this table

In Phase 2, the scorer reads the surface's `kind` from `surface_inventory.jsonl`, then consults the row above to decide which dims apply. Score 1000 with `n/a:true` for inapplicable dims. Justify in `notes`:

```jsonc
{
  "scores": {"safety_with_recovery": 1000, ...},
  "notes": "n/a (read-side verb; no irreversible op to gate)"
}
```

`tools/validate_scorecard.sh` accepts `n/a:true` rows but flags any pattern where the same kind+dim combination is `n/a` for half the surfaces and meaningful for the other half — that's a scorer-drift signal.
