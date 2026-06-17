---
name: negative-ledger
description: "Capture, query, map, reopen, compact, and hand off evidence-backed failed hypotheses and falsified review routes. Use for `$negative-ledger`, negative evidence, route ratchet, repeated review decisions, same-cluster recurrence, route already tried, no-effect repair, public-bypass failure, scar tissue, route veto, or search-space pruning."
---

# Negative Ledger

`negative-ledger` preserves disconfirmed hypotheses so future work does not repeat dead ends.

The durable source of truth is repo-local:

```text
.ledger/negative-ledger.jsonl
```

Use the `ledger` CLI for durable mutations and route gates. Do not store `$negative-ledger` state under `.step`, and do not use `.learnings.jsonl` as the primary negative-ledger store.

## Core rule for review workflows

```text
A repeated review decision is a falsified hypothesis.
```

When the same cluster reappears after a selected route, that route becomes negative evidence unless proven unrelated, stale, or superseded.

## Modes

- `query`: retrieve relevant negative evidence before route selection.
- `map`: convert evidence into current route constraints.
- `capture`: record a newly falsified route or failed attempt.
- `reopen`: decide whether evidence is stale/superseded/reopened.
- `compact`: merge repeated route-family failures.
- `handoff`: summarize active exclusions and safest next frontier.

## Negative Route Gate

```yaml
negative_route_gate:
  query_or_map: yes | no
  ledger_cli: ledger
  store: .ledger/negative-ledger.jsonl
  command: "ledger map --route ... --cluster ... --artifact ..."
  exit_code: 0 | 2 | 3
  ledger_available: yes | no
  active_exclusion_match: yes | no | null
  exclusion_id: "none | NEG-..."
  fuzzy_candidates: 0
  fuzzy_authority: suggest_only | none
  failure: none | ledger_missing
  handoff_allowed: yes | no
```

If the store is missing or `ledger map` was not run, same-cluster mutation is blocked. If an active exclusion matches and is not reopened/stale/superseded, implementation is blocked. Fuzzy candidates are advisory only.

Operational commands:

```bash
ledger init
ledger capture --json FILE
ledger map --route "$ROUTE" --cluster "$CLUSTER" --artifact "$ARTIFACT"
ledger show --id NEG-000001
ledger reopen --id NEG-000001
ledger handoff
ledger doctor
```

## Capture shape

```yaml
negative_evidence_ledger:
  - neg_id: NEG-001
    hypothesis: "..."
    attempted_change_or_decision: "..."
    source_refs:
      - kind: cas-review | validation | pr-comment | route-record | commit | learning | lab | test | diff
        ref: "..."
        summary: "..."
    observed_outcome: "..."
    failure_class: no-effect | local-regression | global-regression | unsound | too-complex | stale | unknown
    applicability_conditions: []
    current_status: active | stale | superseded | reopened | unknown
    exclusion_rule: "..."
    reopening_criteria: []
    confidence: high | medium | low | unknown
    next_search_hint: "..."
```

## Query templates

Use compact topical queries:

```text
<repo> <cluster_id> <owner> <route_kind> <failure_surface>
```

## Durable writeback policy

Do not flood `.ledger/negative-ledger.jsonl`.

Use durable writeback only when evidence is:

- decision-shaping;
- transferable;
- counterfactually useful;
- anchored by current proof/review/revert/benchmark evidence.

One-off same-session route failures can stay in the route record. `.learnings.jsonl` rows may be cited as historical evidence, but durable negative-route exclusion state belongs in `.ledger/negative-ledger.jsonl`.

## Guardrails

- Do not record hunches as negative evidence.
- Do not convert one failed implementation into a broad strategy ban.
- Do not use stale evidence without applicability explanation.
- Do not use absence of a negative entry as proof that a route is novel.
- Do not suppress adjacent approaches with an overbroad exclusion.

## Resources

- [review-route-ratchet.md](references/review-route-ratchet.md)
- [writeback-policy.md](references/writeback-policy.md)
