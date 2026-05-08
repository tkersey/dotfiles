# ORCHESTRATION — Multi-agent fan-out tiers

Pick a tier based on tool size and pass mode. The phase loop is the same; what changes is how many subagents run in parallel and which phases use multi-model triangulation.

---

## Tiers

### Solo (1 worker, serial phases)

**When.** Tiny tool: ≤ 5 subcommands, ≤ 30 flags. Or: `audit-only` mode + user wants minimal context cost. Or: the user is debugging the methodology itself.

**Shape.** ONE main agent (no parallel main-agent panes) runs phases serially. **Within a phase, subagent fan-out still applies** — Phase 2 still spawns ≥ 2 scorer subagents per surface (the rubric demands median-of-N), Phase 1 still spawns subagents per subcommand, etc. The "1 worker" refers to the main-agent count, not to subagent count. Solo mode just means "I'm not coordinating with peer main-agents over Agent Mail / Beads"; I still use the Agent tool to spawn scorer/applier/recommender subagents within my own session, in parallel where the phase allows.

**Subagent spawn pattern.** From a Solo main agent, spawn parallel subagents in a SINGLE message with multiple Agent tool calls (per Claude Code docs). Two scorers for the same surface, both spawned in one tool-call batch, return their partials, then the main agent calls `aggregate_scores.sh`. No NTM / no Beads coordination needed.

**No triangulation.** Triangulation specifically means peer-claude (two MAIN agents) or multi-model (Claude + Codex + Gemini); Solo skips both. Solo's "two scorers" are subagents within the same Claude session — not triangulation.

**CASS mining is `quick` (10 canned queries). Wall time.** 30–60m for Phase 1–4 on a tiny tool.

### Pair (2 workers, fan-out only on Phase 1/2/5)

**When.** Typical CLI: 6–15 subcommands. Default for `full` mode unless user requests Squad+.

**Shape.** Main agent + one parallel-worker agent. Phase 1 fans out to 2 surface-inventorists (one for half the subcommand tree). Phase 2 has 2 scorers per surface (so 2 workers minimum). Phase 5 has 2 appliers running in parallel on different recommendations (with file reservations to avoid conflicts).

**Wall time.** 1–2h for `full` mode end-to-end on a typical CLI.

### Squad (4–6 workers, parallel by subcommand)

**When.** Full CLI: 16–40 subcommands. Stripe-style or `cargo`-flavored full toolkits. SOC2-ish stakes ("we ship this; ergonomics are visible to customers").

**Shape.**
- Phase 1: one surface-inventorist per top-level subcommand subtree (4–6 in parallel) + dedicated agents for env vars, exit codes, error corpus.
- Phase 2: ≥ 2 scorers per surface; tiebreaker if needed; squads work on distinct surface ranges in parallel.
- Phase 4: synthesizer plus optional `peer-claude` triangulation.
- Phase 5: 4+ appliers in parallel; Agent Mail file reservations are mandatory (not optional) for shared files.
- Phase 7: 2–3 fresh-eyes agents reading different subtrees simultaneously.
- Phase 9: 2+ canonical-task-simulators (each gets 3 distinct tasks; no shared context).

**Wall time.** 4–8h for `full` mode end-to-end.

### Swarm (8–12+ workers, beads-driven + multi-model triangulation)

**When.** Multi-binary toolkit (e.g. `cargo` + `cargo-audit` + `cargo-deny` + `cargo-machete` family). Rewriting an entire CLI surface (`audit-and-fix` after a major version). Public OSS tool with > 1k stars.

**Shape.**
- Phase 0: pre-flight CASS mining is `deep` (38+ queries); pre-flight idea-wizard pass.
- Phase 1: parallel surface-inventorists per subcommand AND per binary in the toolkit.
- Phase 2: triangulation appetite is `multi-model` (Claude + Codex + Gemini scoring the top-10 surfaces).
- Phase 4: synthesizer + multi-model triangulation on top-20 recommendations; reconciliation step.
- Phase 5: workers driven by `br ready` in beads-mode; Agent Mail thread per recommendation; ≥ 8 appliers in parallel.
- Phase 7: 3 rounds of fresh-eyes with multi-model (Claude + Codex + Gemini, one round each); each round must come up clean.
- Phase 9: 3+ simulators, each with 5+ canonical tasks, fresh contexts.

**Wall time.** Day to half-week for `full` mode end-to-end; cost scales with model + parallelism.

---

## Tier-selection table

| Tool dimensions | Mode = audit-only | Mode = full | Mode = re-score-only |
|-----------------|--------------------|--------------|----------------------|
| Tiny (≤ 5 cmds) | Solo | Solo or Pair | Solo |
| Typical (6–15)  | Pair | Pair | Solo |
| Full (16–40)    | Pair or Squad | Squad | Pair |
| Multi-binary | Squad | Swarm | Squad |
| Massive (40+ cmds, multi-binary, public) | Squad | Swarm | Squad |

User can always override.

---

## Multi-model triangulation (Phase 4 / Phase 7)

Triangulation = "three independent passes by different models, then reconcile." The skill uses it where independent reads produce the highest signal:

- **Phase 4 top-N recommendations.** The synthesis agent has one bias; Codex has another; Gemini has another. The intersection of all three is high-confidence; the union is the candidate set.
- **Phase 7 fresh-eyes.** Claude reads its own diff; Codex reads it; Gemini reads it. Bugs that any one of the three catches go on the fix list.

When triangulation appetite is `multi-model` AND `/multi-model-triangulation` skill is available:

```bash
# Triangulate top-10 recs
for rec in $(jq -r 'select(.priority > <P75>) | .recommendation_id' audit/recommendations.jsonl | head -10); do
  codex_run "Review recommendation $rec; agree/disagree, suggest improvements" > audit/triangulation/${rec}_codex.md
  gemini_run "..."                                                                > audit/triangulation/${rec}_gemini.md
done

# Synthesize via subagents/triangulator.md
```

Reconciliation rules:
- **All three agree** → recommendation stands as-is.
- **Two agree, one dissents** → use the dissent as a critique; revise the recommendation to address it (but don't drop the rec).
- **All three disagree** → the recommendation is genuinely ambiguous; escalate to user with the three views.

See `TRIANGULATION.md` for full prompt templates.

---

## CASS mining schedule

CASS mining (`subagents/cass-miner.md`) extracts patterns from the user's prior agent sessions. Three appetites:

| Appetite | Queries | When | Cost |
|----------|---------|------|------|
| `skip` | 0 | Resumed pass with no surface change; small tool | Free |
| `quick` | 10 canned | First pass on a new tool; small/medium scope | ~30s |
| `deep` | 38+ targeted | Swarm tier; high-stakes tool; user has rich session history | ~3–5min |

The 10 canned queries:
1. `"<tool>" --robot` (does the user already use this tool's robot mode?)
2. `"<tool>" error` (what errors did the user hit?)
3. `"<tool>" --help` (did the user reach for --help; how did it go?)
4. `"<tool>" exit code` (any stuck-on-exit-code experiences?)
5. `"<tool>" intent inference` (did the user manually correct the agent's command?)
6. `"<tool>" did not work` (failure-pattern phrases)
7. `"<tool>" silent` (silent_fail patterns)
8. `"<tool>" json output` (parseability complaints)
9. `"<tool>" couldn't figure out` (discoverability gaps)
10. `"<tool>" took too long` (perf complaints in the hot path)

For `deep`, see `references/exemplars/CASS-FINDINGS.md` for the full 38-query template.

Output: `audit/cass_findings.md` — surprising patterns, counter-examples, and prior-incident references that should inform the rubric and recommendations.

---

## Coordination via Agent Mail

Required for Squad+; recommended for Pair+.

```
file_reservation_paths(
  project_key=<absolute path to TARGET, not sibling>,
  agent_name=<your subagent ID>,
  paths=["src/cmd/<subcmd>.rs", "src/cli.rs"],
  ttl_seconds=1800,
  exclusive=true,
  reason="<recommendation_id>"
)
```

Thread ID convention: `agent-ergo-<pass>-<phase>-<surface_or_rec>`. Examples:
- `agent-ergo-pass1-phase5-R-007` (Phase 5 applier on R-007)
- `agent-ergo-pass1-phase7-fresheyes-round-2` (Phase 7 fresh-eyes round 2)
- `agent-ergo-pass1-phase9-task-03` (Phase 9 simulator task 3)

The `project_key` is always the *target* repo, not the sibling. Reservations are advisory; respect them.

---

## Beads workflow

For Pair+: every applied recommendation gets a bead.

```bash
br create --title "[R-007] Levenshtein-1 typo correction for --json/--colour/--verbose" \
          --type=task \
          --priority=2 \
          --labels="agent-ergonomics,pass-1,intent_inference" \
          --description "<from recommendation summary + diff_sketch>"
```

After applying:
```bash
br close <bead-id> --reason "Applied in commit <sha>; regression test green"
br sync --flush-only
git add .beads/
git commit -m "sync beads (R-007)"
```

For Phase 10, file beads for queued work (deferred recs, supplementary fixes, rubric refinements).

---

## When orchestration goes wrong

| Symptom | Cause | Fix |
|---------|-------|-----|
| Two appliers commit conflicting changes | No file reservation | Bump tier; require Agent Mail reservations on shared files |
| Phase 2 takes forever | Single-threaded scorer | Parallelize: one scorer per surface_id, fan out to ≤6 agents |
| Triangulation never converges | Models disagree because rubric anchors are unclear | Refine rubric; bump rubric_version; re-score with the refined anchors |
| Phase 7 catches the same bug 3 times | Fresh-eyes agents have shared context | Ensure each fresh-eyes agent is spawned via Agent tool with `subagent_type="general-purpose"` and *no* shared context |
| Beads pile up faster than they close | Deferred recs aren't actually deferred — they're forgotten | Phase 10 must enumerate every applied:false rec with a `deferred_reason` populated |
