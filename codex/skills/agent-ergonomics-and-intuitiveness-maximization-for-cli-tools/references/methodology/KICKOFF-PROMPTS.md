# KICKOFF-PROMPTS — Verbatim text for kicking off a pass

After the user answers the intake, send the matching kickoff prompt verbatim. These are calibrated to produce a known phase-loop entry point.

---

## audit-only kickoff

```
Got it. I'll run an `audit-only` pass against `<TARGET>` (no code changes; sibling workspace at `<SIBLING>`).

Plan:
- Phase 0: discover the CLI, scaffold the workspace, write phase0_scope_decision.md
- Phase 1: enumerate every agent surface (subcommands, flags, env vars, exit codes, error messages, signals)
- Phase 2: score every surface across the 11 agent-ergonomic dimensions
- Phase 3: stress-test intent-inference with naive + savvy agent corpora
- Phase 4: rank recommendations; write playbook.md for top-10

You'll get back: agent_surfaces.jsonl, scorecard.md, heatmap.svg, recommendations.jsonl, playbook.md, plus pre-pass simulation transcripts.

Proceeding with Phase 0 now. I'll check in before Phase 5 (which won't run in audit-only mode anyway).
```

---

## full kickoff

```
Got it. I'll run a `full` pass against `<TARGET>` on a new branch `agent-ergonomics-pass-<N>` (sibling workspace at `<SIBLING>`).

Plan:
- Phases 0–4: same as audit-only
- Phase 5: apply top-N recommendations (one bead per rec; reservations via Agent Mail)
- Phase 6: re-score the modified binary; compute uplift; flag regressions
- Phase 7: three rounds of fresh-eyes review until clean twice; ubs + linters + tests
- Phase 8: self-documentation hardening (capabilities, robot-docs, --robot-* etc.)
- Phase 9: agent-in-the-loop simulation against the new binary (fresh-context agent)
- Phase 10: HANDOFF.md, push branches, file beads for next pass

Constraints I'll respect:
- AGENTS.md (no file deletion, no destructive git, no _v2 files, no script-driven code transforms)
- Your scope guardrails: <SCOPE_GUARDRAILS>

Proceeding with Phase 0 now. I'll check in at end of Phase 4 (before applying any code changes), end of Phase 6 (with uplift evidence), and end of Phase 9 (with simulation outcomes).
```

---

## re-score-only kickoff

```
Got it. I'll re-score `<TARGET>` (now at SHA `<HEAD_SHA>`) against the prior pass `<PRIOR_PASS>` (at SHA `<PRIOR_SHA>`).

This compares the current state of every surface against the prior scorecard. No new recommendations, no code changes, no fresh-eyes pass.

You'll get back: scorecard_pass_<N+1>.md, uplift_diff.md, regression_alerts.md.

If any surface regressed more than 50 points, I'll stop and surface that to you for diagnosis before continuing.

Proceeding now.
```

---

## simulate-only kickoff

```
Got it. I'll spawn a fresh-context agent and have it attempt these canonical tasks against the current `<TARGET>`:

<TASK_LIST>

Each task gets a full transcript captured at `<SIBLING>/audit/agent_simulations/post_pass_<N>/`. I'll compare to the pre-pass simulations from Pass <N-1> and report:
- Did first command tried succeed?
- Round-trips to completion?
- Did any error message leave the agent stuck?

Proceeding now.
```

---

## single-surface-rescore kickoff

```
Got it. Re-scoring just `<SURFACE_ID>` of `<TARGET>` at SHA `<HEAD_SHA>`.

Comparing to the prior pass's score for this surface. No new recommendations, no other surfaces touched.

Proceeding now.
```

---

## Resumed-pass kickoff (when manifest exists)

```
Found existing audit workspace at `<SIBLING>` from Pass <N> (target SHA `<PRIOR_SHA>`).

Current target HEAD: `<HEAD_SHA>`.

<IF SAME SHA:>
Nothing changed since the last pass. Options:
1. Run an `audit-only` pass to refresh recommendations (Phase 4 only — uses cached inventory).
2. Run a `simulate-only` pass to verify canonical tasks still work.
3. Run a `full` pass starting from where Pass <N> left off (resumes Phase 5 if any recs are still applied:false).

<IF DIFFERENT SHA:>
Target has changed since Pass <N>. Default plan: run `re-score-only` first (computes uplift / detects regressions), then optionally a `full` Pass <N+1> if you want to apply more changes.

What would you like?
```

---

## Recovery kickoff (when manifest is in a bad state)

```
The audit workspace at `<SIBLING>` looks inconsistent. Specifically: <DIAGNOSTIC_FROM_VALIDATE_PASS>.

Options:
1. **Continue** from the inconsistent state. (I'll work around it but the manifest will stay flagged.)
2. **Reset Pass <N>** — preserve all prior passes' artifacts; clear only the in-progress Pass <N> partials. (No file deletion needed — moves them to `<SIBLING>/audit/.archive/<timestamp>/`.)
3. **Bail** — leave the workspace as-is; tell me what to do.

What would you like? (I default to option 2 if you don't say.)
```
