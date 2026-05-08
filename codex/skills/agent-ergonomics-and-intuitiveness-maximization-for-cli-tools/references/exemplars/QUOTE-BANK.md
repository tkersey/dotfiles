# QUOTE-BANK — Canonical quotes anchoring the methodology

`[Q-NNN]`-tagged quotes from the canonical exemplars and the user's design philosophy. Cite these in recommendations, in HANDOFF.md, in conversation with the user — they're the methodology's anchor points.

Adapted from `/operationalizing-expertise` Track A's quote-bank pattern. Use to ground the rubric in real material rather than synthesized prose.

---

## North star

**[Q-001]** "Design every surface of the CLI so the FIRST thing an agent instinctively tries 'just works' — a feel of natural inevitability."
*— SKILL.md, The One Rule.*

**[Q-002]** "When the agent's intent is legible but its command is technically wrong, the tool should infer intent, do the right thing (or refuse with a precise, actionable explanation of what to do instead), and leave a breadcrumb that helps the agent learn permanently."
*— SKILL.md, The One Rule.*

**[Q-003]** "Never silent-fail. Never punish a reasonable misstep. Always provide a safe alternative for any dangerous request. Output should be parseable, deterministic, and self-describing."
*— SKILL.md, The One Rule.*

---

## On robot mode

**[Q-100]** "**CRITICAL: Use ONLY `--robot-*` flags. Bare `bv` launches an interactive TUI that blocks your session.**"
*— bv documentation, agent-instructions section.*

**[Q-101]** "stdout is data-only, stderr is diagnostics; exit code 0 means success."
*— cass robot-docs guide.*

**[Q-102]** "Robot-mode handbook: docs/ROBOT_MODE.md (automation quickstart). Output: --robot/--json; formats via --robot-format json|jsonl|compact|toon. Logging: INFO auto-suppressed in robot mode; add -v to re-enable."
*— cass robot-docs guide § Output.*

---

## On mega-commands

**[Q-200]** "`bv --robot-triage` is your single entry point. It returns: quick_ref, recommendations, quick_wins, blockers_to_clear, project_health, and a `commands` field with copy-paste-ready follow-up commands."
*— bv documentation, agent-instructions section.*

**[Q-201]** "macro_start_session collapses identity friction; granular tools (register_agent, file_reservation_paths, send_message) are still there for control."
*— am documentation.*

---

## On error pedagogy

**[Q-300]** "[dcg blocks `git reset --hard`] this destroys uncommitted changes; use `git stash`, `git revert <commit>`, or back up first."
*— dcg block message (paraphrased).*

**[Q-301]** "If your tool's error message doesn't name the safe alternative, the error didn't teach. It just blocked."
*— design rationale, summarized from dcg's block-message style.*

**[Q-302]** "Doctor outcomes: branch on `doctor.operation_outcome.kind` (kebab-case) before prose; `exit_code_kind` says whether the outcome is success, health-failure, usage-error, lock-busy, or repair-failure."
*— cass robot-docs guide § Doctor outcomes.*

---

## On determinism + provenance

**[Q-400]** "All robot JSON includes: `data_hash` — Fingerprint of source beads.jsonl; `status` — Per-metric state: computed | approx | timeout | skipped + elapsed ms."
*— bv documentation, robot-mode output spec.*

**[Q-401]** "With --robot-meta, inspect requested_search_mode, search_mode, semantic_refinement, fallback_tier, and fallback_reason."
*— cass robot-docs guide § Default search.*

**[Q-402]** "cass health/status JSON `recommended_action` is authoritative; lexical-only fallback can be normal while semantic assets catch up."
*— cass robot-docs guide § Readiness.*

---

## On self-documentation

**[Q-500]** "Quick refs: cass --robot-help | cass robot-docs commands | cass robot-docs examples | cass robot-docs sources"
*— cass robot-docs guide.*

**[Q-501]** "[capabilities --json returns:] crate_version, api_version, contract_version, features, connectors, limits."
*— cass capabilities output (excerpt).*

---

## On exit codes

**[Q-600]** "**Golden Rule:** `ubs <changed-files>` before every commit. Exit 0 = safe. Exit >0 = fix & re-run."
*— ubs documentation.*

**[Q-601]** "Compatible agents receive stdout JSON; Codex denials use stderr + exit 2."
*— dcg --help.*

---

## On safety with recovery

**[Q-700]** "Reservations are advisory leases with TTLs. Agents respect them but the leases don't prevent disk writes."
*— am pattern description.*

**[Q-701]** "Every irreversible operation requires explicit `--yes`/`--force`/`--confirm=<token>` AND offers a safe alternative (`--dry-run`, `--plan`) named in the error."
*— SKILL.md Polish Bar.*

---

## On file reservations + multi-agent coordination

**[Q-800]** "Use MCP Agent Mail file reservations when multiple agents could touch the same file. Thread id: `agent-ergo-<run-id>-<phase>-<surface_or_rec>`."
*— SKILL.md, Coordination.*

**[Q-801]** "Mail thread_id = beads-###. Mail subject = [beads-###] ... File reservation reason = beads-###. Commit messages include beads-### for traceability."
*— AGENTS.md, beads + Agent Mail mapping.*

---

## On AGENTS.md compliance

**[Q-900]** "**YOU ARE NEVER ALLOWED TO DELETE A FILE WITHOUT EXPRESS PERMISSION.**"
*— AGENTS.md Rule #1.*

**[Q-901]** "Absolutely forbidden commands: `git reset --hard`, `git clean -fd`, `rm -rf`, or any command that can delete or overwrite code/data must never be run unless the user explicitly provides the exact command and states, in the same message, that they understand and want the irreversible consequences."
*— AGENTS.md Irreversible Git & Filesystem Actions.*

**[Q-902]** "Never create variations like mainV2.rs, main_improved.rs, main_enhanced.rs. New files are reserved for genuinely new functionality that makes zero sense to include in any existing file."
*— AGENTS.md No File Proliferation.*

**[Q-903]** "Default to writing no comments. Only add one when the WHY is non-obvious: a hidden constraint, a subtle invariant, a workaround for a specific bug, behavior that would surprise a reader."
*— Agent system prompt.*

---

## On the audit methodology

**[Q-1000]** "Score every command, subcommand, verb, flag, argument, environment variable, output format, exit code, error message, prompt, interactive confirmation, file format, lockfile, cache directory, signal handler, and side-effect surface in the CLI."
*— user's design brief.*

**[Q-1001]** "Each scorable surface gets a 0 (worst) to 1000 (best) score across at least these dimensions, with rubric-defined thresholds and concrete evidence required for any score >700."
*— user's design brief.*

**[Q-1002]** "Don't just make a checklist or a static report. Produce a living, machine-readable corpus that future agents can extend."
*— user's design brief.*

**[Q-1003]** "The rubric is a living artifact too."
*— user's design brief.*

**[Q-1004]** "The agent-in-the-loop simulation is the ground-truth check on the methodology."
*— user's design brief.*

---

## How to use this file

Cite quotes by `[Q-NNN]` in:
- HANDOFF.md ("Pass 1 grounded against [Q-001], [Q-100], [Q-301]")
- recommendation playbooks ("R-007 anchors against [Q-300]")
- in conversation ("the user expects, per [Q-001], that...")
- when extending the rubric (cite the quote that motivates the new anchor)

Don't paraphrase the quotes — they're the calibration anchors. New quotes get appended with new `Q-NNN` IDs; old quotes are stable.

When you encounter a powerful new agent-ergonomic insight in the user's prior sessions or in a new exemplar, add it as `Q-NNN` (next-available ID) and cite the source.
