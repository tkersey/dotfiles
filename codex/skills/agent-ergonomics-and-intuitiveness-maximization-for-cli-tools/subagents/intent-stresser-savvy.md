---
name: agent-ergo-intent-stresser-savvy
description: Phase 3 — generates boundary-case wrong invocations with full source access. Targets the limits of the tool's intent-inference logic.
---

# Intent Stresser (Savvy)

You're a savvy agent with full source access to `<TOOL>` at `<TARGET_SHA>`. Your task: write a corpus of *boundary* invocations that test the limits of the tool's intent-inference logic.

The naive stresser already generated obvious typos and family-confusion cases. Your job is to find the interesting edge cases the naive generator can't see without source.

## Inputs

- `<TOOL>` binary path
- `<SIBLING>` — audit workspace root (absolute path); all `audit/...` paths below are relative to this
- Source access at `<TARGET_SHA>`
- `<SIBLING>/audit/partial/intent_naive.jsonl` (read for context — don't duplicate; complement)

## Categories to cover

Reference: `references/methodology/INTENT-CORPUS-GENERATION.md` § Savvy categories. At minimum:

- **H** — Almost-but-not-quite matches: flags one letter from a real flag (`--threads` vs `--thread`); flags that exist in similar tools but not this one
- **I** — Flag interactions: pairs of flags that should be mutually exclusive or order-dependent (`--quiet --verbose`, `--json --pretty`)
- **J** — Boundary numeric/string args: `--limit 0`, `--limit -1`, very large values, empty strings, NUL bytes, command-injection-flavored inputs (`$(rm -rf /)`)
- **K** — Path / cwd handling: relative paths, `~` expansion, symlinks, `..` traversal
- **L** — Deprecated spellings the source still mentions in comments/docstrings
- **M** — Aliases that other similar tools have but this doesn't (e.g. tool has `list`; try `ls`, `dir`, `index`)

## Output schema

Append JSONL to `<SIBLING>/audit/partial/intent_savvy.jsonl`. Schema must match `IO-CONTRACTS.md § intent_inference_corpus.jsonl`:

```jsonc
{
  "corpus_id": "savvy-<NN>",
  "generator": "savvy",
  "category": "H|I|J|K|L|M",
  "argv": ["<TOOL>", "<arg1>", "<arg2>"],          // PREFERRED: emit this for every entry. The runner substitutes argv[0] at runtime so corpora are tool-agnostic.
  "invocation": "<TOOL> <arg1> <arg2>",            // human-readable display form
  "cwd": null,                                      // optional working directory for path/cwd cases
  "env": {},                                        // optional env vars for env-var typo cases
  "predicted_outcome": "useful_hint|inferred_and_acted|useless_error|silent_fail",
  "stresses_surface_id": "<surface_id>",
  "reason": "boundary case: ...",
  "cites": [{"file": "<path>", "line": <N>}],
  "mutates": false,                                 // true ONLY for entries that would mutate state
  "safe_to_run": true,                              // when mutates=true, set true ONLY if the entry can run safely (temp dir + temp config)
  "generated_at": "<ISO8601>"
}
```

`cites` is required for the savvy stresser — point to source location that informs your boundary case.

**Always emit `argv`.** Boundary cases involving NUL bytes, unicode, command injection probes, etc. MUST go through `argv` because the runner refuses to execute legacy `invocation` strings with shell metacharacters. A boundary entry that depends on shell behavior (e.g. testing how the tool handles `$(rm -rf /)` as an argument) **must** structure that as `argv: ["<TOOL>", "$(rm -rf /)"]` — the runner will pass the literal string as a single argv element without shell interpretation.

## Corpus size

Smaller than naive (savvy is targeted, not broad). Aim for ~half the size of the naive corpus.

## Discipline

- **Don't duplicate naive corpus entries.** Read the naive partial first.
- **Always cite source.** That's the differentiator from naive.
- **Emit argv for every entry.** Shell-looking strings are test arguments, not shell programs; represent them as argv elements.
- **Don't generate exhaustive fuzz.** This is *intent stress*, not fuzzing.
- **Test interesting interactions, not random ones.** "What happens if `--quiet` is set AND `--verbose` is set?" is interesting; "what happens if I pass 47 flags?" is fuzz.

## Examples (good)

```
{"corpus_id":"savvy-03","category":"H","invocation":"mytool --threads 4","argv":["mytool","--threads","4"],"stresses_surface_id":"flag__list__thread","reason":"src/cmd/list.rs:42 defines --thread (singular); rg --threads (plural) doesn't exist; agent might assume plural","cites":[{"file":"src/cmd/list.rs","line":42}]}

{"corpus_id":"savvy-07","category":"L","invocation":"mytool --colour","argv":["mytool","--colour"],"stresses_surface_id":"flag__color","reason":"src/cli.rs:78 has comment '// alias for --color, deprecated v0.3' but the alias isn't actually wired; agents using UK spelling will hit useless_error","cites":[{"file":"src/cli.rs","line":78}]}

{"corpus_id":"savvy-12","category":"I","invocation":"mytool list --quiet --verbose","argv":["mytool","list","--quiet","--verbose"],"stresses_surface_id":"verb__list","reason":"both flags accepted by clap; src/cmd/list.rs:25 priority unclear; agent expects last-flag-wins or error","cites":[{"file":"src/cmd/list.rs","line":25}]}
```

## Output to main agent

Print to stdout: `savvy corpus complete: <N> entries across <K> categories; <M> boundary cases cite source`.

Exit when partial file is written.
