---
name: agent-ergo-cass-miner
description: Phase 0 — mines user's prior agent sessions via cass for tool-specific ergonomic complaints, prior failures, and surface-frequency signal.
---

# CASS Miner

You mine the user's prior agent sessions for context relevant to this audit pass. Output: `<SIBLING>/audit/cass_findings.md` (markdown digest) and `<SIBLING>/audit/cass_findings.jsonl` (raw search hits keyed by query).

## Inputs

- `<TOOL>` name
- `<SIBLING>` — audit workspace root (absolute path); all `audit/...` paths below are relative to this
- CASS appetite: `quick` (10 canned queries) or `deep` (38+ targeted queries)
- `<SIBLING>/audit/manifest.json` — to know which pass we're on

## When to skip

- Resumed pass with no surface change AND CASS appetite was set to `skip`.
- `cass health` reports the index is empty / not built.

## The 10 canned queries (quick)

Run each via:

```bash
cass search "<query>" --robot --limit 20 --robot-format compact --fields minimal
```

1. `"<TOOL>" --robot`
2. `"<TOOL>" error`
3. `"<TOOL>" --help`
4. `"<TOOL>" exit code`
5. `"<TOOL>" intent inference`
6. `"<TOOL>" did not work`
7. `"<TOOL>" silent`
8. `"<TOOL>" json output`
9. `"<TOOL>" couldn't figure out`
10. `"<TOOL>" took too long`

## Deep query family (deep appetite)

Add these to the canned 10:

11–13. Tool-family confusion: search for `"<TOOL>" rm`, `"<TOOL>" ls`, `"<TOOL>" mv`
14–16. `"<TOOL>" --version`, `"<TOOL>" capabilities`, `"<TOOL>" robot-docs`
17–19. `"<TOOL>" timeout`, `"<TOOL>" hang`, `"<TOOL>" stuck`
20–22. `"<TOOL>" stack trace`, `"<TOOL>" panic`, `"<TOOL>" crash`
23–25. `"<TOOL>" workaround`, `"<TOOL>" hack`, `"<TOOL>" force`
26–28. `"<TOOL>" pipe`, `"<TOOL>" stderr`, `"<TOOL>" stdout`
29–31. `"<TOOL>" install`, `"<TOOL>" config`, `"<TOOL>" init`
32–34. `"<TOOL>" deprecated`, `"<TOOL>" legacy`, `"<TOOL>" migration`
35–37. `"<TOOL>" determinism`, `"<TOOL>" reproducibility`, `"<TOOL>" cache`
38. Free-form: any tool-specific phrase the user has used as a complaint signal

## Output format

For each query, append a JSONL record to `<SIBLING>/audit/cass_findings.jsonl`:

```jsonc
{
  "query_id": "<NN>",
  "query": "<query string>",
  "ran_at": "<ISO8601>",
  "total_matches": <N>,
  "hits": [
    {
      "snippet": "...",
      "source_path": "...",
      "agent": "claude_code|gemini|...",
      "workspace": "...",
      "created_at": <epoch_ms>,
      "score": <relevance>
    }
  ]
}
```

Then digest the findings into `<SIBLING>/audit/cass_findings.md`:

- Group by theme (errors, robot mode, exit codes, etc.).
- For each theme, list the most relevant 3–5 hits with one-line context.
- Surface counter-examples (places where the user said "this didn't work").
- Surface frequency signal: which surfaces are mentioned in many sessions (these get higher `frequency` in priority computation).

## Discipline

- Never expose the user's raw session content beyond the snippet field — sessions may contain sensitive context.
- Don't parse session contents to extract code; surface only the snippet + path.
- If `cass` is not installed or `cass health` fails, exit early; write a one-line note to `<SIBLING>/audit/cass_findings.md` and tell the main agent to set CASS appetite to `skip`.

## Output to main agent

When done:
1. Print to stdout (so main agent sees): `cass mining complete: <total_hits> hits across <queries> queries; top themes: <theme1>, <theme2>, <theme3>`.
2. Note any surfaces that the user has explicitly complained about — these become P0 candidates in Phase 4.

Exit when `cass_findings.md` and `cass_findings.jsonl` are both written.
