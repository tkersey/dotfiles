# DECISION-TREES — When to apply which methodology branch

The skill has many phases, modes, dimensions, operators, archetypes, and patterns. This file gives the decision trees for "what should I do next?" at common decision points.

These are the flow charts that answer "where do I start?" and "what's my next action?".

---

## DT-1: Picking the audit mode

```
Has the user explicitly stated a mode?
├── YES → use that mode; document in phase0_scope_decision.md
└── NO  → ask:
    ├── User says "audit" / "review" / "score"     → audit-only
    ├── User says "fix" / "improve" / "apply"      → full
    ├── User says "what changed" / "drift check"   → re-score-only
    ├── User says "did it work" / "test it"        → simulate-only
    └── User says "this one flag" / "this one verb" → single-surface-rescore
    
    If still unclear, use the surface-count / prior-pass heuristic in SKILL.md.
    If those signals are unavailable, default to audit-only (safest).
```

---

## DT-2: Picking the orchestration tier

```
How many surfaces does the tool have? (Phase 1 count)
├── ≤ 30           → Solo (1 worker)
├── 31–100         → Pair (2 workers)
├── 101–300        → Squad (4–6 workers)
└── ≥ 301          → Swarm (8–12+ workers)

AND additionally:
- Mode is `re-score-only`?       → Drop one tier
- Stakes are high (public OSS)?  → Bump one tier
- Multi-binary family?           → Default to Squad+
- T4-T5 case study fits?         → Swarm
```

---

## DT-3: Picking the archetype

(See subagents/cli-archetype-classifier.md for the full classifier.)

```
Which archetype best fits the tool?
├── Searches text/files                  → search-tool
├── Manages packages / dependencies       → package-manager
├── Compiles / builds artifacts           → build-tool
├── Runs tests                            → test-runner
├── Manipulates source-control state      → SCM
├── Talks to a daemon / server            → daemon-cli
├── Converts file formats (in/out)        → file-format-converter
├── Generates new projects                → scaffolder
├── Pre-execution hook (sub-second)       → hook-tool
├── Manages issues / tasks / dependencies → issue-tracker
├── Manages identity / credentials        → authentication
├── Schema / data migrations              → migration-tool
├── System diagnostics / observability    → diagnostic
├── Exposes MCP server + CLI              → mcp-server
└── Multiple binaries in a family         → multi-binary-toolkit

If 2+ archetypes apply equally → composite
If none apply cleanly → novel (extend CLI-ARCHETYPES.md)
```

---

## DT-4: When to escalate to multi-model triangulation

```
Phase 4 top-10 recommendation candidates:
├── Triangulate if: stakes high (public OSS) OR breaking change OR security implication
└── Skip otherwise (peer-claude is fine)

Phase 7 fresh-eyes:
├── Triangulate if: > 10 commits in this pass OR multi-cross-cut changes
└── Skip otherwise (single Claude with 3 calibrated prompts)
```

---

## DT-5: When to apply U-Recs (universals)

```
For every audit pass, evaluate:

U-1 (capabilities --json): Always applicable. Apply unless tool already has it.
U-2 (robot-docs guide):    Always applicable. Apply unless tool already has it.
U-3 (--robot-* / --json):  Apply unless tool has --json on every read-side verb.
U-4 (typo correction):     Apply unless tool already has levenshtein-1 hints.
U-5 (capabilities pin):    Apply if U-1 is being applied (need the regression test).
U-6 (recommended_action):  Apply if tool has doctor / status / health verb.
U-7 (provenance fields):   Apply if tool has multi-tier capabilities (cache, fallback, etc.).
U-8 (AGENT/AUTOMATION footer): Apply if --help lacks it.

Universal P1 priority. These should be in every audit's playbook.md.
```

---

## DT-6: When to bump rubric_version

```
Are dimension definitions changing?            → YES, bump
Are anchor levels (0/250/500/750/1000) changing? → YES, bump
Are dimension weights changing?                  → YES, bump
Are operators being added/removed?               → YES, bump
Is the kernel (One Rule + Polish Bar) changing? → YES, bump
Are new exemplars / counter-examples changing scoring? → YES, bump

Only typos / formatting changes? → NO, don't bump
```

---

## DT-7: When to apply now vs defer

```
Is the rec a Universal (U-N)?
├── YES → apply this pass

Is the rec breaking (would change a documented contract)?
├── YES → split into stages 0/1/2/3 per DEPRECATION-PATTERNS.md
│        Apply stage 0 this pass; stages 1+ deferred to N+1, N+2, N+3
└── NO  → continue:

Is the rec contentious (multi-model triangulation flagged)?
├── YES → escalate to user; defer until resolved
└── NO  → continue:

Is the rec's expected_uplift > 50 pts?
├── YES → apply this pass (high leverage)
└── NO  → consider deferring (lower priority for now)

Is the user time-constrained?
├── YES → top-3 only this pass; rest deferred
└── NO  → top-10 this pass
```

---

## DT-8: Which Operator pipeline to apply

(Per OPERATORS.md § Composition cheat-sheet, restated.)

```
Failing dim is...
├── agent_intuitiveness        → ① ⟁ 🩹 🎓
├── agent_ergonomics           → Σ 🔀 ⏱ 🛂 🧮 🪜
├── agent_ease_of_use          → 🧭 📖 📜 🎯 🔗
├── output_parseability        → 🪧 🚦 🔢 📦 🪟
├── error_pedagogy             → 🩹 ⟁ 🚫 🪄
├── intent_inference           → ⟁ 🩹 🚫
├── safety_with_recovery       → 🛡 🩹 🔬 🧷
├── determinism                → 🔢 🆔 🌐 🪟
├── self_documentation         → 📜 📖 🧭 🎯 🩻
├── composability              → 🪧 🚦 🌐 🚫 🧶 🧮 🔇
└── regression_resistance      → 🧪 📐 🧾
```

---

## DT-9: When to terminate the Phase 4-6 loop

```
Run termination check after each pass:
├── Median uplift < 25 pts?      → YES, candidate to terminate
│   ├── No surface regressed > 50?  → YES, terminate
│   └── Else → HARD STOP; investigate
├── No new top-10 emerged?            → YES, candidate to terminate
└── Phase 7 fresh-eyes clean × 2?    → YES, definitely terminate

If none, continue to next pass.
```

---

## DT-10: When to verify a claim (per VERIFICATION-FIRST.md)

```
Is the claim live-tool-state dependent?
├── YES → verify before relying on it
└── NO  → use as-is

Is the claim from a prior pass (more than 3 months old)?
├── YES → re-verify before relying
└── NO  → use as-is

Is the claim about an external skill (cass capabilities, bv robot mode, etc.)?
├── YES → re-verify because external schema may drift
└── NO  → use as-is

Is the claim about an exemplar pattern (CANONICAL-EXEMPLARS Pattern N)?
├── YES → re-verify quarterly per CONTINUOUS-IMPROVEMENT.md
└── NO  → use as-is
```

---

## DT-11: When to apply MULTI-TOOL-FAMILY-AUDIT

```
Does the target ship multiple binaries that share concepts?
├── YES → continue
└── NO  → not a family; skip

Are the binaries in the same repo / share manifest format / cross-reference each other?
├── YES → continue
└── NO  → independent CLIs; audit separately

Is cross-cut consistency the user's stated concern?
├── YES → MULTI-TOOL-FAMILY-AUDIT
└── NO  → audit each binary; family pass deferred

Does cross-cut consistency score < 600 in a per-binary audit?
├── YES → recommend family audit in HANDOFF
└── NO  → ad-hoc cross-cut alignment fixes
```

---

## DT-12: When to apply MCP-SERVER-AUDIT extension

```
Does the target expose an MCP server?
├── YES → continue
└── NO  → skip

Is there a companion CLI?
├── YES → run parity-auditor as well
└── NO  → MCP-only audit

Is the MCP server stdio / sse / http?
├── stdio → easy to audit (pipe JSON-RPC)
├── sse  → audit reconnection + line-buffering
└── http → audit auth + CORS + status codes
```

---

## DT-13: When to start a deprecation rollout

```
Is the rec a name change (flag rename / verb rename / env var rename / JSON key rename)?
├── YES → 4-stage rollout per DEPRECATION-PATTERNS.md D-1 / D-2 / D-3 / D-4
└── NO  → continue:

Is the rec a default behavior change?
├── YES → use Pattern D-5 (env var opt-in then flip)
└── NO  → continue:

Is the rec a feature removal?
├── YES → use Pattern D-6 (deprecation warning then error)
└── NO  → continue:

Is the rec additive (only adds new)?
├── YES → no deprecation needed
└── NO  → unclear; ask user
```

---

## DT-14: When to spawn a fresh-context simulator (Phase 9)

```
Is this `full` mode pass complete (Phases 1-8 done)?
├── NO  → wait
└── YES → continue:

Is this the first pass on this tool?
├── YES → spawn 5-10 canonical tasks; capture pre-pass baseline
└── NO  → continue:

Were any U-Recs (universals) applied this pass?
├── YES → spawn; expect significant uplift
└── NO  → continue:

Did any error pedagogy / intent inference recs apply?
├── YES → spawn; specifically test typo / wrong-flag scenarios
└── NO  → consider skipping Phase 9 if minor pass
```

---

## DT-15: When to write a CHEAT-SHEET / quickref for the target

```
Is the target's surface large (T3+)?
├── YES → strongly recommend
└── NO  → optional

Does the target lack a TOC in --help / docs?
├── YES → cheat sheet is high-leverage
└── NO  → optional

Do agents use the tool in time-constrained contexts (per CASS)?
├── YES → cheat sheet is high-leverage
└── NO  → optional

Effort budget: writing a cheat sheet is ~30 min. ROI is high for T3+ tools.
```

---

## DT-16: Should I use NTM (multi-agent swarm)?

```
Is orchestration tier = Swarm (8+ workers)?
├── YES → use NTM (per /ntm + /vibing-with-ntm)
└── NO  → continue:

Is the audit being run on multiple targets in parallel?
├── YES → use NTM
└── NO  → continue:

Does the user have NTM installed and configured?
├── YES → optional, depends on cost/budget
└── NO  → use Agent-tool subagents (default)
```

---

## DT-17: When to bring in beads (br)

```
Is mode = full?
├── YES → file beads per applied recommendation
└── NO  → optional (beads can track audit-only findings too)

Is this a multi-pass audit (carryforward applied:false recs)?
├── YES → use beads to track stage rollouts
└── NO  → minimal beads usage OK

Is there an existing beads project at the target?
├── YES → integrate (use same project's .beads/)
└── NO  → create or skip per user preference
```

---

## DT-18: How to handle a HARD STOP

```
Phase 6 found a regression > 50 pts on any surface
├── 1. Don't continue
├── 2. Read regression_alerts.md to identify offending rec
├── 3. Investigate: cite file:line of the change
├── 4. Either:
│   ├── Revert the offending rec (preferred)
│   └── Add a deprecation path that doesn't regress
├── 5. Re-score
└── 6. Resume the loop only after no surface regresses > 50 pts
```

---

## DT-19: When to flip to handoff (Phase 10)

```
All termination conditions met (DT-9)?
├── YES → continue:
└── NO  → run another pass

Phase 7 fresh-eyes clean × 2?
├── YES → continue:
└── NO  → run another fresh-eyes round

Phase 8 self-doc surfaces all present?
├── YES → continue:
└── NO  → file as deferred or apply

Phase 9 simulation showed net improvement?
├── YES → continue:
└── NO  → either run another applier pass OR document why no improvement

Then: write HANDOFF.md, push, file beads, exit.
```

---

## How to use these trees

When you're unsure what's next:
1. Find the closest decision point above
2. Walk the tree
3. Cite the DT-N in your reasoning ("Per DT-7, this rec defers to pass N+1")
4. Document in HANDOFF.md if the choice is non-obvious

Decision trees are the executable form of the methodology. When the rubric leaves a gap, decision trees fill it.
