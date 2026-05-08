# MULTI-PASS-BUG-HUNTING-FOR-ERGONOMICS — The audit-fix-rescan cycle applied to ergonomics

The `/multi-pass-bug-hunting` skill is a systematic audit-fix-rescan methodology for code bugs. This file applies the same pattern to **ergonomic bugs**.

The mental model: **ergonomic gaps ARE bugs**. They cause agents to lose time and trust. Treat them with the same multi-pass discipline.

---

## The audit-fix-rescan cycle (ergonomic-flavored)

```
[scan]   → Phase 1+2: enumerate surfaces; score them
[plan]   → Phase 4: rank fixes by priority
[fix]    → Phase 5: apply top-N
[rescan] → Phase 6: re-score; verify uplift; detect regressions
[repeat] → loop until median uplift < 25 pts
```

Per `/multi-pass-bug-hunting`, the loop continues until **two consecutive passes turn up only trivial fixes**.

---

## Ergonomic gaps that look like bugs

For multi-pass-bug-hunting purposes, classify ergonomic gaps the same as code bugs:

| Severity | Description | Example |
|----------|-------------|---------|
| Critical | Tool unusable for canonical task | TUI launches in non-TTY (agent stuck) |
| High | Major round-trip waste | No `capabilities --json`; no mega-command |
| Medium | Confusing but recoverable | Cryptic error messages without `did you mean` |
| Low | Minor friction | `--help` lacks AGENT/AUTOMATION footer |
| Trivial | Cosmetic | Inconsistent capitalization in help text |

Pass termination: when only "trivial" fixes remain.

---

## The three calibrated prompts (ergonomic-flavored)

`/multi-pass-bug-hunting` uses three calibrated review prompts. For ergonomic audits in Phase 7, use the same prompts (verbatim — they're calibrated):

### Round 1
> "Carefully read over all of the new code you just wrote and other existing code you just modified with 'fresh eyes' looking super carefully for any obvious bugs, errors, problems, issues, confusion, etc. Carefully fix anything you uncover."

For ergonomic-applied fixes: re-read the diffs, verify they actually close the failing dimension, verify no regression on adjacent dimensions.

### Round 2
> "Sort of randomly explore the code files in this project, choosing code files to deeply investigate and trace their functionality and execution flows through the related code files which they import or which they are imported by. Once you understand the purpose of the code in the larger context of the workflows, do a super careful, methodical, and critical check with 'fresh eyes' to find any obvious bugs, problems, errors, silly mistakes. Comply with ALL rules in AGENTS.md and ensure that any code you write or revise conforms to the best practice guides referenced in AGENTS.md."

For ergonomic audits: trace through how `<tool> capabilities --json` is generated; trace through error paths; trace through plugin loading. Find inconsistencies that span multiple code paths.

### Round 3
> "Turn your attention to reviewing the code written by your fellow agents and checking for any issues, bugs, errors, problems, inefficiencies, security problems, reliability issues. Diagnose underlying root causes using first-principle analysis. Don't restrict yourself to the latest commits — cast a wider net and go super deep."

For ergonomic audits: cross-pass review. Check that earlier-pass changes still align with current pass's changes. Check that recommendations from prior passes that didn't make it to applied:true are still valid.

---

## What "trivial fix" means in ergonomic context

The distinction between substantive and trivial:

| Substantive (loop continues) | Trivial (loop terminates) |
|------------------------------|---------------------------|
| Fix a missing flag | Typo in `--help` text |
| Add a missing `did you mean` | Adjust spacing in error message |
| Refactor envelope | Fix grammar in description |
| Add `capabilities` field | Reorder existing keys (no semantic change) |
| Add regression test | Update test message wording |
| Address rubric anchor mismatch | Add a comment to source |

If the agent is uncertain, classify as substantive. False positives waste a pass; false negatives leave bugs.

---

## When the cycle should NOT terminate

Don't terminate the loop if:

- Phase 6 found a regression > 50 pts (HARD STOP — investigate first)
- A failing dim is still < 700 on a P1-priority surface
- A canonical-exemplar pattern isn't yet implemented despite being recommended
- A new finding emerged that wasn't addressed yet

The "two clean rounds" gate is necessary AND must come AFTER the priority queue is drained.

---

## The N+1 backlog

After Pass N terminates cleanly, surface the backlog for Pass N+1:

- Recommendations that were deferred (with `deferred_reason`)
- New idea-wizard outputs from Phase 10
- CASS findings that emerged late
- Polish Bar rows that scored 750 but not 1000

These accumulate. Phase 4 of Pass N+1 picks them up.

---

## Bug-hunting heuristics for ergonomics

Mirror /multi-pass-bug-hunting's heuristics:

### Heuristic 1: "What would surprise an agent?"

Walk through the canonical task as a fresh agent. Note every moment of "wait, what?" Each is a finding.

### Heuristic 2: "Where could behavior differ between TTY and non-TTY?"

Force non-TTY contexts. Find divergences. Most are bugs.

### Heuristic 3: "What if I run this twice?"

Re-running canonical mutating ops should be idempotent. If it isn't, that's a finding.

### Heuristic 4: "What if the input is empty?"

Empty result sets. Empty input. Empty config. Each can produce silent_fail. Test all.

### Heuristic 5: "What if I'm offline?"

Tool tries network; agent has none. Tool should fail gracefully with `recommended_action`.

### Heuristic 6: "What if the prior version of this tool ran differently?"

Cross-version compatibility. Is the contract pinned? Is there a migration?

### Heuristic 7: "What if two agents call this concurrently?"

Race conditions. Lock contention. Idempotency. Each can produce a finding.

### Heuristic 8: "What if the tool is in a weird state?"

Half-finished installs. Corrupt config. Stale lock. Tool should detect + diagnose.

### Heuristic 9: "What does the agent see in stderr?"

Excessive stderr is noise. Sparse stderr is unhelpful. Find the right balance.

### Heuristic 10: "Can I parse the output?"

Pipe to `jq .`. If it fails, that's a finding (unless explicitly text mode).

---

## Multi-pass priority decay

Per pass, priority of a finding may change:

- Pass 1 finds X with priority 0.85 (top of queue)
- Pass 1 doesn't fix X (deferred)
- Pass 2: X's priority might be 0.75 if other surfaces have improved (relative)
- Pass 3: X might be 0.5 if everything else is at 1000 (X is now the worst)

Don't assume priority is stable. Re-compute per pass. The synthesizer in Phase 4 handles this.

---

## The "diminishing returns" curve

Empirical observation across audits:

```
Pass 1: ~70 pts median uplift
Pass 2: ~30 pts (applying deferred recs from Pass 1)
Pass 3: ~15 pts
Pass 4: ~10 pts
Pass 5+: ~5 pts each
```

After ~5 passes, the methodology has captured most of the available uplift. Continuing to run quarterly Pass-N+1 catches drift but doesn't add much net uplift.

This is healthy convergence. Cease applying when the uplift is < 5 pts AND nothing in the backlog is high-priority.

---

## Cross-pass coherence

Each pass leaves an audit trail. Future passes can:

- Read prior `playbook.md` files to avoid re-deriving the same ranking
- Read prior `applied_changes.jsonl` to avoid re-applying the same change
- Read prior `regression_alerts.md` to avoid re-introducing a known regression

Coherence is a property of the audit workspace, not just the tool. Treat the workspace as a long-lived asset.

---

## When to bring in multi-model triangulation

Per Operator/Phase 7, multi-model triangulation should be used when:

- The diff is large (cross-cutting refactor)
- The change has security implications
- The change introduces a deprecation
- The user has flagged the change as high-stakes
- One pass-N+1 has surfaced contradictions with pass-N

Otherwise, peer-claude or single-claude is sufficient.

---

## When to add new operators

If a finding doesn't map cleanly to any existing operator:

1. Document it as `unmapped_finding` in the pass's HANDOFF.md
2. After 3+ unmapped findings of similar shape, propose a new operator card
3. Bump rubric_version when adding the new operator
4. Re-score affected surfaces with the new operator's anchor

This is how the operator library grows.

---

## When to retire operators

Rare. If an operator stops being relevant (e.g. an industry shift makes it moot), mark it as deprecated in OPERATORS.md but don't delete (history matters).

---

## Bug-hunting in subagents

Subagents in this skill (and any spawned subagents during phase work) have their own bug surfaces:

- Are they using the latest rubric_version?
- Are they citing the right operator cards?
- Are they violating AGENTS.md?
- Are they producing well-formed JSONL?

Phase 7 fresh-eyes review extends to subagent prompts, scripts, and outputs.

---

## Multi-pass + verification-first

Combine with VERIFICATION-FIRST.md:

- Each pass re-verifies prior-pass claims
- Drift detected → rec to refresh; potential rubric refinement
- Re-verification logs accumulate in `audit/verification/log.jsonl`

Multi-pass + verification = Track A discipline at maturity.

---

## Related

- `/multi-pass-bug-hunting` skill — the source methodology
- `methodology/PHASES.md` § Phase 7 — the three calibrated prompts
- `methodology/CONTINUOUS-IMPROVEMENT.md` — long-term cadence
- `methodology/VERIFICATION-FIRST.md` — drift discipline
