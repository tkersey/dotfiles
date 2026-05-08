# VERIFICATION-FIRST — Evidence discipline for ergonomic claims

The methodology is evergreen; live tool behavior is volatile. Tools update. Frameworks change defaults. CI runners drift. An ergonomic claim that was true last quarter may not be true today.

Verification-First means: **don't recommend a fix without verifying the current state. Don't claim a behavior without invoking the binary. Don't trust the rubric anchor without checking the exemplar still matches.**

This file gives the discipline. Adopted from `wills-and-estate-planning-skill` and `saas-billing-patterns` skills' verification-first patterns.

---

## The volatility model

Things that drift over time:

| Volatile | Frequency | Impact |
|----------|-----------|--------|
| CLI version → flag changes | Every release | High |
| Framework default changes (clap, cobra) | Every major version | High |
| Exit-code conventions in ecosystem | Slowly | Medium |
| Tool-family member additions/removals | Occasional | Medium |
| Agent-side conventions (NO_COLOR, CI=true) | Slowly | Low |
| Polish Bar definition | Per skill release | Low (we control it) |

Things that don't drift:

| Evergreen | Why |
|-----------|-----|
| The 11 dimensions | They're properties of any CLI, not dependent on specific tools |
| The One Rule | Methodological axiom |
| The Polish Bar | We define it; bumps only with rubric_version bump |
| Operator library | Anchored against the kernel |

The audit's evergreen content is reliable. Live-state claims need verification.

---

## The verification protocol

For any claim that depends on **current tool state**, follow this protocol before acting on it:

### Step 1 — Read the current binary

```bash
<tool> --version
<tool> --help
<tool> capabilities --json   # if exists
```

Save outputs to `audit/verification/<surface_id>_<timestamp>.txt` (creates a verification log).

### Step 2 — Compare to expected

Match against the rubric anchor, the canonical pattern, or the prior-pass evidence.

If they match → claim is verified.
If they diverge → log the divergence; refresh the claim.

### Step 3 — Update or escalate

If a claim is now wrong (e.g. "this tool has --robot" but it doesn't anymore), update the audit's evidence AND log to `audit/verification/divergences.md`.

### Step 4 — If applying a recommendation that depends on the claim

Re-verify within 1 hour of applying. If verification fails, abort the apply and re-plan.

---

## The verification log

Every audit pass should produce `audit/verification/log.jsonl`:

```jsonc
{
  "timestamp": "2026-05-06T12:00:00Z",
  "surface_id": "verb__list",
  "claim": "list verb scores 850 on agent_intuitiveness; cited bv pattern",
  "verification": {
    "method": "live_invocation",
    "command": "bv --robot-triage",
    "output_excerpt": "{...}",
    "matches_anchor": true
  }
}
```

The log proves the audit was grounded in current state, not memory.

---

## When verification is impractical

Some verifications are expensive or unavailable:

- The tool requires network and we're offline
- The tool requires auth we don't have
- The tool's source is closed
- The tool is in development; behavior changes hourly

For these:

1. Document the impractical verification in `audit/verification/limitations.md`
2. Flag affected scores with `verification_status: "best_effort"`
3. In Phase 4, deprioritize recs that depend on un-verified claims
4. In Phase 9 simulation, the simulator's transcript becomes the verification

---

## Per-claim verification requirements

| Claim type | Verification needed |
|------------|---------------------|
| "Tool has flag --X" | `<tool> --help \| grep -- --X` AND grep source for the flag |
| "Tool exits with code N on condition C" | Trigger condition; check `$?` |
| "Tool's output schema is { ... }" | `<tool> X --json \| jq 'keys'`; cross-check vs source schema |
| "Tool's --help mentions Y" | `<tool> --help \| grep Y` |
| "Tool follows convention Z" | Multiple invocations testing the convention |
| "Pattern N from CANONICAL-EXEMPLARS is implemented" | Read source; trace pattern's signature |
| "CASS finding F-NN applies" | Re-run the cass query; verify hits exist |

If a verification fails for any high-impact claim, treat as a **provisional finding** and resolve before applying.

---

## Verification-first vs evidence-required

The skill already requires `score > 700 needs evidence` (per validate_scorecard.sh). Verification-first is a *stronger* discipline:

- Evidence-required: at scoring time, cite something (file:line OR transcript)
- Verification-first: at recommendation/apply time, **re-verify** the cited evidence is still current

Evidence-required prevents lazy scoring. Verification-first prevents stale-evidence drift across passes.

---

## When the rubric itself needs verification

The rubric's anchors cite specific exemplars (e.g. "Pattern 7: bv --robot-triage"). If `bv` releases a major version that removes `--robot-triage`, the rubric anchor is broken.

Quarterly rubric refresh (per CONTINUOUS-IMPROVEMENT.md) re-verifies anchors:

```bash
for pattern_id in $(grep -oE 'Pattern [0-9]+' references/exemplars/CANONICAL-EXEMPLARS.md | sort -u); do
  # For each pattern, verify the cited exemplar still matches
  # (manual or scripted)
done
```

If an anchor breaks, update the rubric (bump rubric_version) and re-score affected surfaces.

---

## Verification of cross-skill assumptions

This skill references many other skills (/agent-mail, /beads-br, /beads-bv, /cass, etc.). These can drift too:

- `/cass capabilities --json` schema may change
- `/beads-bv --robot-triage` shape may evolve
- `/agent-mail`'s macro tools may add fields

Verify before relying:

```bash
# Probe the actual current schema of /cass
cass capabilities --json | jq 'keys'
# Compare to what this skill assumes (in CASS-MINING-RECIPES-DEEP.md, etc.)
```

If divergence, file a refresh in HANDOFF.md.

---

## Verification of agent-side conventions

Agent conventions (NO_COLOR, CI=true, MCP protocol versions) evolve:

- Periodically check community standards (no-color.org, MCP RFCs)
- Periodically check Claude Code / Codex / Gemini hook conventions
- Update CASS-FINDINGS.md when new agent failure patterns emerge

---

## Verification log template

Save to `audit/verification/log.jsonl` (one record per verification):

```jsonc
{
  "timestamp": "<ISO8601>",
  "claim_id": "P-007",
  "claim": "<paraphrased claim>",
  "claim_source": "references/exemplars/CANONICAL-EXEMPLARS.md § Pattern 7",
  "verification_method": "live_invocation|source_read|cass_query|external_doc",
  "verification_command": "<the actual command run>",
  "verification_output_excerpt": "<excerpt>",
  "verified": true,
  "drift_detected": false,
  "drift_notes": null,
  "verifier_agent_id": "<scorer or recommender ID>"
}
```

---

## When to re-verify

Re-verification is needed when:

| Trigger | Action |
|---------|--------|
| Quarterly cadence | Re-verify all CANONICAL-EXEMPLARS anchors |
| New pass starting | Verify Phase 0 surface-existence claims |
| Phase 5 applying a rec | Verify the gap still exists before applying |
| Phase 6 finds regression | Verify the regression is real (not stale evidence) |
| User questions a claim | Verify; respond with verified state |

---

## Anti-patterns

- **Stale citations**: Citing source file:line without re-checking the file still has that content at that line
- **Blind copy-paste**: Copying a recommendation from CANONICAL-EXEMPLARS without re-verifying the exemplar still works
- **Trusting CASS-FINDINGS without re-mining**: Patterns may have been resolved by tool updates
- **Skipping verification because "it's evergreen"**: Even evergreen claims should be re-verified annually
- **Flagging drift but not refreshing the rubric**: Drift detection without action is wasted effort

---

## Verification-first as a culture

If every audit pass produces a verification log, drift is caught early. If verification is sometimes skipped, drift accumulates and the methodology rots.

Treat the verification log as a first-class artifact alongside the scorecard. Future passes inherit verified claims; un-verified claims are re-verified.

---

## Related

- `OPERATIONALIZING-EXPERTISE-TRACK-A.md` — verification is part of Level 5 (validators)
- `CONTINUOUS-IMPROVEMENT.md` — quarterly rubric refresh schedule
- `TROUBLESHOOTING.md` § "Across-pass" — handling rubric_version mismatches
- `methodology/SCHEMA-EVOLUTION.md` — schema-pin patterns are verification-first applied to capabilities
