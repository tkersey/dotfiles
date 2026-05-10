---
name: negative-ledger
description: Use this skill to capture, query, map, compact, reopen, and hand off evidence-backed failed hypotheses, reverted approaches, benchmark regressions, no-effect attempts, and strategy pivots so future work avoids repeating dead ends while still allowing stale evidence to be reopened when conditions change. Trigger cues include negative ledger, failed attempts, what have we already tried, avoid retrying dead ends, benchmark regressions, reverted approaches, strategy pivot, why did the last approach fail, before trying another optimization, and search-space pruning.
---

# Negative Ledger

`negative-ledger` is a reusable protocol for handling **disconfirmed hypotheses**. Its job is to preserve decision-shaping negative evidence, prune repeated dead ends, and keep old failures reopenable when the artifact state changes.

It is not a generic reviewer and not a final gate. Negative evidence is advisory unless its witness and applicability conditions bind the current artifact state.

## Companion relationship
- Use `learnings` as the preferred durable source and write path for reusable negative evidence.
- Use `fixed-point-driver` when negative evidence participates in a full build-review-improve-verify loop.
- Use `negative-ledger-mapper` as the read-only specialist when the work is search-heavy and prior failures materially change routing.
- When `negative-ledger-mapper` or any read-only specialist is used, require the shared specialist packet contract at `../references/specialist-packet-contract.md`; reject stale, wrong-scope, wrapper-leaking, acknowledgement-only, or no-evidence packets before converting them into exclusions.

## Trigger cues
Use this skill when the user asks about or the task contains:
- `negative ledger`
- failed attempts, no-effect attempts, abandoned approaches, or reverted changes
- benchmark regressions or optimization dead ends
- repeated hypotheses across loops
- strategy pivots that should change future routing
- “what have we already tried?”
- “avoid trying the same thing again”
- “why did the last approach fail?”
- preflight before another optimization, debugging, migration, or remediation campaign

Do not trigger for a trivial one-pass task unless the user explicitly asks for negative-evidence handling.

## Modes
- `capture`: record a newly witnessed failed or disconfirmed attempt.
- `query`: retrieve relevant negative evidence before new work.
- `map`: convert prior evidence into current routing constraints and next-search hints.
- `reopen`: decide whether stale negative evidence has become eligible again.
- `compact`: dedupe and compress repeated failed attempts into narrower entries.
- `handoff`: summarize active exclusions, stale/reopened entries, and promising frontier.

## Source hierarchy
Prefer sources in this order:
1. Current-run witnesses: commands, logs, benchmark output, failing/passing tests, diffs, traces, reverts.
2. Current campaign ledgers: fixed-point-driver Negative Evidence Ledger, Findings Ledger, Verification Ledger, Specialist Briefing Ledger.
3. Durable memory: `.learnings.jsonl` loaded through the `learnings` CLI.
4. Repository history: commit messages, revert notes, PR comments, issue notes, benchmark history.
5. User-provided context, marked as `user-context` until independently witnessed.

A source can seed an entry, but it does not make the entry active. Active negative evidence needs a witness, current-state applicability, an exclusion rule, and reopening criteria.

## Learnings CLI integration
Use the `learnings` skill CLI as the preferred durable source when a real repo root and compatible CLI are available.

### Preflight recall
Before a meaningful `query`, `map`, or optimization route choice, build a compact topical query with 4-8 task-defining terms: component, failure surface, benchmark/test, and hypothesis family. Then run read-only recall:

```bash
run_learnings_tool recall --query "<component failure-surface hypothesis-family>" --limit 8 --drop-superseded
```

If the user asks to browse or explore history rather than implement, start with:

```bash
run_learnings_tool recent --limit 15
run_learnings_tool query --spec "@$LEARNINGS_SPECS_DIR/status-rank.json"
```

Treat recall/query hits as candidate evidence. Check the hit's evidence anchors and decide whether its applicability conditions match the current artifact state before creating an active exclusion.

### Durable writeback
After a witnessed failed attempt, regression, revert, no-effect attempt, or strategy pivot, append through `learnings append` only when the learning is decision-shaping, transferable, and counterfactually useful.

Use action-oriented statuses:
- `avoid_for_now`: active negative evidence with current applicability.
- `investigate_more`: evidence is incomplete or applicability is uncertain.
- `do_less`: repeated low-value pattern or no-effect attempt.
- `codify_now`: repeated negative evidence should be promoted into a skill, guardrail, or test fixture.
- `review_later`: weak but potentially important evidence that should not yet prune routes.

Example writeback:

```bash
run_learnings_tool append \
  --status avoid_for_now \
  --learning "When optimizing MVCC small-write throughput, avoid same-leaf bookkeeping batching unless the small-N regression fixture has changed because the prior prototype regressed the representative write loop." \
  --evidence "bench: write-small-n regressed 7% on run 2026-05-09 after same-leaf batching prototype" \
  --application "Before proposing same-leaf batching again, verify the benchmark fixture and MVCC bookkeeping path changed, then rerun the representative small-N benchmark." \
  --tag negative-evidence \
  --tag benchmark-regression \
  --tag perf
```

If `learnings` is unavailable or the workspace is not a verified repo root, keep the ledger in-session and report why durable capture was skipped.

## Capture requirements
A negative ledger entry is usable only if it has:
- a narrow hypothesis, not a broad strategy family
- a concrete attempted change or decision
- evidence anchors: command, log, benchmark, failing test, revert, review rationale, trace, diff, or learning ID with evidence
- observed outcome
- failure class
- applicability conditions
- current status
- exclusion rule
- reopening criteria
- confidence
- next-search hint

If any required part is missing, mark the entry `unknown`, `stale`, or `need-evidence` rather than using it as an exclusion rule.

## Mapping workflow
1. Identify the current artifact state: branch/revision when available, diff or changed paths, phase, and target signal.
2. Load candidate negative evidence from the source hierarchy, including `learnings recall/query` when available.
3. Normalize each prior attempt into the ledger contract.
4. Decide current applicability: active, stale, superseded, reopened, or unknown.
5. Convert active entries into narrow exclusion rules.
6. Convert stale/reopened entries into explicit reopening tests.
7. Emit the safest next-search frontier: what to avoid, what can be retried only with new proof, and what adjacent approach remains promising.

## Output contracts
For direct use, end with:

```yaml
negative_evidence_ledger:
  - neg_id: NEG-001
    hypothesis: "..."
    attempted_change: "..."
    source_refs:
      - kind: benchmark | test | revert | review | trace | diff | learning | user-context | ledger
        ref: "..."
        summary: "..."
    learning_source_ids:
      - "lrn-..."
    evidence:
      - "..."
    observed_outcome: "..."
    failure_class: no-effect | local-regression | global-regression | unsound | too-complex | stale | unknown
    applicability_conditions:
      - "..."
    current_status: active | stale | superseded | reopened | unknown
    exclusion_rule: "..."
    reopening_criteria:
      - "..."
    confidence: high | medium | low | unknown
    next_search_hint: "..."
```

Then add a bottom-line handoff:

```md
### Negative Ledger Handoff
- active_exclusions: ...
- stale_or_superseded: ...
- reopened: ...
- need_evidence: ...
- safest_next_frontier: ...
- learnings_source_ids: ...
- durable_capture: appended: id=... | duplicate-skip: ... | 0 records appended: ... | not-attempted: ...
```

## Guardrails
- Do not record unevidenced hunches as negative evidence.
- Do not convert one failed implementation into a blanket ban on a broad strategy family.
- Do not let a `learnings` hit suppress current work without checking evidence and applicability.
- Do not use stale benchmarks to suppress current work without explaining why they still apply.
- Do not use absence of a negative entry as proof that a route is novel.
- Do not append to `.learnings.jsonl` by hand; use the `learnings` CLI when durable writeback is appropriate.
- Do not make a separate persistent negative-ledger file by default; use `.learnings.jsonl` until volume or schema pressure justifies a dedicated store.

## Resources
- [negative-ledger-mapper](agents/negative-ledger-mapper.md)
- [negative-ledger-contract.md](references/negative-ledger-contract.md)
- [specialist-packet-contract.md](../references/specialist-packet-contract.md)
- [learnings-source.md](references/learnings-source.md)
- [fixed-point-integration.md](references/fixed-point-integration.md)
- [negative-ledger-jsonl.md](references/negative-ledger-jsonl.md)
- [example-invocations.md](references/example-invocations.md)
