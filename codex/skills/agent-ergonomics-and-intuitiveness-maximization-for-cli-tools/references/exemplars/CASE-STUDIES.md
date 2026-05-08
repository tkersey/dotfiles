# CASE-STUDIES — Compact summaries of tier-scoped audits

Quick-reference summaries of auditing tools at different scopes. Modeled on `saas-billing-patterns-for-stripe-and-paypal/references/methodology/CASE-STUDIES.md`. Use these for "what does an audit look like for a tool of size X?" calibration.

---

## Tier scoping (per WORKED-EXAMPLES.md complement)

| Tier | Tool size | Typical audit duration | Worker tier (per ORCHESTRATION.md) |
|------|-----------|-------------------------|-------------------------------------|
| T1 | ≤ 5 verbs, ≤ 30 flags | 30–60 min | Solo |
| T2 | 6–15 verbs | 1–2 h | Pair |
| T3 | 16–40 verbs | 4–8 h | Squad |
| T4 | ≥ 41 verbs OR multi-binary | day–half-week | Swarm |
| T5 | Ecosystem-scale (multiple multi-binary toolkits) | week+ | Multi-pass swarm |

---

## T1 case study: A simple bash CLI

**Target.** A 3-verb bash tool: `mytool list`, `mytool add`, `mytool delete`.

**Pre-audit state.**
- ~5 surfaces (3 verbs + `--help` + `--version`)
- No `--json`
- No `capabilities`
- Errors are prose-only ("usage: mytool <list|add|delete>")
- exit 1 on any error

**Pass-1 audit findings.**
- All 8 universal recs apply (U-1 through U-8)
- Add `delete --yes` and `delete --dry-run`
- Add `--json` to `list`
- Capabilities JSON is small but valuable

**Pass-1 mode.** `full`.

**Pass-1 outcome.**
- Median uplift: ~120 pts (small tool, lots of room)
- 6 recs applied; 2 deferred (typo correction needs more flags first)
- Phase 9: agent canonical-task simulator goes from 4 round-trips to 2

**Pass-2 outcome.** Diminishing returns; +30 pts. Stable after.

**Total agent-time investment.** ~90 minutes for two passes. Modest investment, large uplift.

---

## T2 case study: A typical Rust + clap CLI

**Target.** A 12-verb CLI with config file. Cargo workspace with single bin.

**Pre-audit state.**
- ~80 surfaces (12 verbs × ~5 flags + env vars + exit codes)
- Has `--json` on read-side verbs (inconsistent shapes)
- No `capabilities`
- Some error pedagogy (`clap`-default messages)
- Mutating ops have `--force` but no `--dry-run`

**Pass-1 audit findings.**
- Universal recs U-1, U-2, U-4, U-5
- Standardize JSON envelope across verbs (Operator 📦)
- Add `--dry-run` to mutating verbs
- Improve error messages (Operator 🩹)
- Schema-pin capabilities (Operator 📐)

**Pass-1 outcome.**
- Median uplift: ~80 pts
- 12 recs applied; 5 deferred (deprecation paths for envelope changes)

**Pass-2 + Pass-3 outcome.** Deprecation rollout for envelope changes (Stage 0 → 1 → 2 across 3 passes). Cumulative uplift +130 pts.

---

## T3 case study: A Go cobra CLI with subcommands

**Target.** A 25-verb CLI organized into 4 subcommand groups.

**Pre-audit state.**
- ~250 surfaces (25 verbs × ~10 flags + global flags + env vars + ...)
- Strong `--output json` support across verbs
- No mega-command
- No `capabilities`
- Cross-verb references missing in `--help`

**Pass-1 audit findings.**
- All 8 universals
- Add a TRIAGE-style mega-command (`<tool> --robot-overview`)
- Standardize cross-verb `--help` SEE ALSO sections
- Add `--robot-meta` for verbs that have fallback tiers

**Pass-1 mode.** `full` with Squad-tier orchestration.

**Pass-1 outcome.** Median uplift ~70 pts; 18 recs applied; 12 deferred to passes 2–4.

**Multi-pass.** This is where the methodology earns its keep. Passes 2 and 3 land deprecation paths + add the mega-command. By pass 4, the tool sits at median 850.

---

## T4 case study: A multi-binary toolkit (cargo ecosystem)

**Target.** `cargo` + 5 plugins (cargo-audit, cargo-deny, cargo-machete, cargo-outdated, cargo-tree).

**Pre-audit state.**
- ~600 surfaces across the family
- Each plugin has different envelope, exit codes, conventions
- Cross-plugin discoverability minimal

**Pass-1 audit findings.**
- Per-binary universals (each gets U-1, U-2, etc.)
- Cross-cut consistency dim scores low (200) — major opportunity
- Family-level recommendations (F-NNN per family-cross-cut-auditor)

**Pass-1 mode.** `full` with Swarm-tier orchestration. Multi-model triangulation on top-10 family recs.

**Pass-1 outcome.** Per-binary improvements ship. Cross-cut alignment rec drafts (deferred).

**Multi-pass.** Family alignment takes 4–6 passes. Each pass lands one deprecation stage of cross-cut envelope alignment. By pass 6, the family scores high cross-cut consistency.

---

## T5 case study: A platform-scale CLI ecosystem (kubectl + helm + k9s + etc.)

**Target.** Kubernetes ecosystem of 8+ CLIs.

**Pre-audit state.** Very heterogeneous — each CLI has its own conventions, JSON shapes, exit codes. Cross-CLI agent workflows constantly trip on inconsistencies.

**Approach.** Treat as a federation of T3 tools. Per-tool Pass-1 audits in parallel. Then a meta-pass for cross-tool alignment.

**Outcome.** Multi-quarter project. The real value is the alignment, not per-tool changes. Requires ecosystem-level coordination (RFCs, deprecation councils).

---

## Right-sizing the audit

Don't apply T4/T5 effort to a T1 tool. Phase 0's archetype classifier helps:

```jsonc
{
  "tier": "T1",
  "duration_estimate": "30–60min",
  "orchestration_tier": "Solo",
  "recommended_passes": 1,
  "deferred_to_pass_2": "minor"
}
```

vs

```jsonc
{
  "tier": "T4",
  "duration_estimate": "day+",
  "orchestration_tier": "Swarm",
  "recommended_passes": 4,
  "deferred_to_pass_2_3_4": "deprecation rollout + cross-cut alignment"
}
```

---

## Audit ROI by tier

| Tier | Audit cost (agent hours) | First-pass uplift | Multi-pass uplift | Per-day-of-use saving |
|------|---------------------------|---------------------|---------------------|--------------------------|
| T1 | 1.5 | ~120 pts | ~150 pts | ~5 min |
| T2 | 4 | ~80 pts | ~130 pts | ~30 min |
| T3 | 12 | ~70 pts | ~150 pts | ~2 hours |
| T4 | 60 | ~50 pts | ~120 pts (multi-pass) | ~1 day |
| T5 | 200+ | ~30 pts | ~80 pts (multi-quarter) | ecosystem-scale |

The "per-day-of-use saving" is the agent-time saved across all users of the tool per day. For widely-deployed tools, this dominates the audit cost.

---

## When NOT to audit

- The tool is being deprecated (migrating to a successor)
- The tool is < 3 verbs and not used in canonical agent workflows
- The tool's source isn't readable AND it has no `--help` (rare)
- The tool is in active development with major surface churn (audit after stabilization)

---

## When to skip phases

For T1 tools, you can skip:
- Phase 3 (intent stress test) — corpus too small to be informative
- Phase 4 multi-model triangulation — overkill
- Phase 9 simulation — manual canonical-task verification is enough

For T4+ tools, ALL phases are valuable.

---

## When to invoke `simulate-only`

When the user asks "did Pass 3 actually fix the X canonical task?" — skip everything except Phase 0 + Phase 9.

---

## When to invoke `single-surface-rescore`

When the user just changed one flag and wants to know the new score for that flag only — skip everything except scoring that one surface.

---

## Common audit shapes

```
T1 first pass:                Phase 0 → 1 → 2 → 4 → 5 → 6 → 7 → 9 → 10
T2 first pass:                Phase 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10
T3 first pass:                Same as T2 + multi-model triangulation in 4/7
T4 first pass:                Same as T3 + family-cross-cut-auditor + deprecation-staging
T1 maintenance pass:          Phase 0 → 6 (re-score-only)
T4 quarterly maintenance:     Same as T4 first pass with applied:false carryforward
```

See `methodology/CONTINUOUS-IMPROVEMENT.md` for cadence detail.
