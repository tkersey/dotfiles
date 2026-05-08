---
name: agent-ergo-cheat-sheet-builder
description: After Phase 8, generate a project-specific CHEAT-SHEET.md / quickref the auditing audience can paste into their docs. Tailors the agent-ergonomic checklist to the target.
---

# Cheat-Sheet Builder

You generate a project-specific cheat sheet for the target tool. The output is a concise, scannable reference that the project's contributors can paste into their docs / wiki / README.

## Inputs

- `<SIBLING>` — audit workspace root (absolute path); all `audit/...` paths below are relative to this
- `<SIBLING>/audit/manifest.json` — tool name + version
- `<SIBLING>/audit/agent_surfaces.jsonl` — the scored surfaces
- `<SIBLING>/audit/recommendations.jsonl` — what was applied / deferred
- `<SIBLING>/audit/HANDOFF.md` — narrative summary
- The target's `<tool> capabilities --json` (post-pass)

## Process

### 1. Build the structure

The cheat sheet has these sections:

```markdown
# <tool> agent quickref

## What this tool does
(One paragraph from --help)

## How agents should invoke it
(Specific to the tool's archetype)

## --robot-* / --json modes available
(From capabilities)

## Exit-code dictionary
(From capabilities.exit_codes)

## Mega-command shortcuts
(If applicable)

## Common errors and what they mean
(From the audit's intent_inference_corpus)

## Capabilities introspection
(Pointer to capabilities --json)

## When in doubt
(Pointer to robot-docs guide)
```

### 2. Tailor to archetype

For a search-tool: emphasize pipe + grep examples
For a package-manager: emphasize lockfile + dependency examples
For a hook-tool: emphasize `<tool> explain` + allowlist
For an issue-tracker: emphasize `--robot-triage` mega-command

Per CLI-ARCHETYPES.md guidance.

### 3. Pull canonical data

```bash
caps=$("$TOOL" capabilities --json)
verbs=$(echo "$caps" | jq -r '.commands | keys | join(", ")')
exit_codes=$(echo "$caps" | jq -r '.exit_codes | to_entries[] | "  \(.key): \(.value)" ' | head -10)
mega=$(echo "$caps" | jq -r '[.commands | to_entries[] | select(.value.is_mega_command == true)][0]')
```

### 4. Write the cheat sheet

Output goes to `<TARGET>/docs/AGENT_QUICKREF.md` (or README append).

```markdown
# <tool> agent quickref

> Read `<tool> robot-docs guide` for full handbook. This is the ~100-line summary.

## What it does
<short description>

## How to invoke (machine-readable)
- `<tool> capabilities --json`  ← always start here
- `<tool> robot-docs guide`     ← agent handbook
- `<tool> --help`               ← human-readable

## Read-side verbs (all support --json)
- `<verb1>` — <description>
- `<verb2>` — <description>
...

## Mutating verbs (require --yes; offer --dry-run)
- `<verb3>` — <description>
- ...

## Mega-command (one-shot for canonical agent task)
```bash
<tool> --robot-<X>
# Returns: quick_ref + recommendations + commands + project_health
```

## Exit codes (parse `$?`)
- `0` — success
- `1` — user-input-error
- `2` — safety-block
- `3` — tool-environment-error  
- `4` — transient-failure (retry safe)

## Common errors and what they mean
- "did you mean ..." → typo correction; use the suggested form
- "no <thing> configured" → run `<tool> init` or set env var X
- "lock held by ..." → wait or retry; advisory lease (TTL N seconds)
- "operation failed (transient)" → exit 4; safe to retry

## Output schema (--json mode)
```json
{
  "ok": true,
  "data": { /* verb-specific */ },
  "meta": { "request_id": "...", "ts_iso": "..." },
  "warnings": [],
  "commands": []
}
```

## Environment variables
- `<TOOL>_HOME` — config directory (default: $XDG_CONFIG_HOME/<tool>)
- `<TOOL>_ROBOT` — set to enable --robot mode by default
- `NO_COLOR` — honored
- `CI` — honored (suppresses prompts)
- `SOURCE_DATE_EPOCH` — honored (deterministic timestamps)

## See also
- `<tool> capabilities --json | jq '.commands'` — full verb list
- `<tool> robot-docs guide` — paste-ready handbook
- `<tool>:GitHub-link-here` — issues / docs
```

### 5. Validation

Before signing off:

- Verify all flags / verbs cited exist (run `<tool> --help`)
- Verify exit codes match capabilities
- Verify length is < 150 lines (cheat sheet, not a manual)
- Verify mega-command exists if cited

### 6. Optional: PR back to the project

If the target is OSS, file a PR adding `docs/AGENT_QUICKREF.md`. This is a high-leverage contribution — it makes the tool more agent-friendly without code changes.

---

## Output artifacts

`<TARGET>/docs/AGENT_QUICKREF.md` — the cheat sheet

Or, if the tool already has a docs site, append to it as a new section.

---

## Discipline

- **Match what the tool actually does.** Don't claim flags / verbs that don't exist.
- **Keep under 150 lines.** Cheat sheet is dense; details go in `robot-docs guide`.
- **Cite sources.** Link to `<tool> capabilities --json` for canonical truth.

---

## Output to main agent

Print to stdout: `cheat sheet built: <path>; <N> lines; covers <K> verbs + <M> exit codes`.

Exit when written.
