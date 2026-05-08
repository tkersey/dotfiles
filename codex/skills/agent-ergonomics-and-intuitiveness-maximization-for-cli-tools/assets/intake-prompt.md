# Intake Prompt

Use this verbatim at the start of a skill invocation. Adjust only the placeholders.

---

I'll run an agent-ergonomics audit on `<TOOL>`. Before starting, I need to confirm a few things.

**1. Target.** Is the tool repo at `<TARGET_PATH>`? (If you'd rather I clone a GitHub URL, paste it.)

**2. Audit workspace.** I'll create a sibling directory `<TARGET_BASENAME>__agent_ergonomics_audit/` and `git init` it for storing measurement artifacts. The actual code changes (if any) happen on a feature branch in the target repo, not in the sibling. OK?

**3. Mode.**
- `audit-only` — score every surface; produce recommendations; **no code changes**.
- `full` — audit + apply top recommendations + re-score + write tests + agent-in-the-loop simulation.
- `re-score-only` — only available if a prior pass exists; recompute scores against current HEAD.
- `simulate-only` — fresh-context agent attempts canonical tasks; produces transcripts only.
- `single-surface-rescore` — re-score one named surface.

For narrow tools where you want improvements applied, I recommend `full` — that's where the cumulative re-scoring earns its keep. For audit/review/score requests, use `audit-only`. Default I'll use unless you say otherwise: `<RECOMMENDED_MODE>`.

**4. Triangulation.**
- `none` — single-agent throughout.
- `peer-claude` — two Claude subagents on key Phase 4 / Phase 7 steps (default).
- `multi-model` — Claude + Codex + Gemini (requires `/multi-model-triangulation`).

**5. CASS mining.** Mine your prior agent sessions for patterns relevant to this tool?
- `skip` — no mining.
- `quick` — 10 canned queries (~30s).
- `deep` — 38+ targeted queries (~3–5min).

Default: `quick` for first pass; `skip` on resumes.

**6. Scope guardrails.** Anything I should NOT touch?
- features you don't want refactored
- deprecation policies (e.g. "you may add but never remove")
- config files that must remain backwards-compatible

**7. Branch name** (for `full` mode). Default: `agent-ergonomics-pass-1`.

**8. Toolchain consent.** If `<TOOL>`'s build toolchain isn't installed (Rust/Go/Python/etc.), should I ask before installing? (default: yes — always ask first)

---

After you answer, I'll send the matching kickoff prompt and start Phase 0.

If any helper skills are missing (`/operationalizing-expertise`, `/codebase-archaeology`, `/codebase-report`, `/multi-pass-bug-hunting`, `/multi-model-triangulation`, `/ubs`, `/dcg`, `/agent-mail`, `/beads-br`, `/beads-bv`, `/cass`, `/idea-wizard`), and you have `jsm` installed + authenticated, I can offer to `jsm install <name>` for each. Or I can use the inline fallbacks documented in `references/methodology/SKILL-FALLBACKS.md`. Either way, the pass continues.
