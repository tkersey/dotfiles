---
name: seq
description: "Mine Codex session JSONL and memory artifacts with the Zig `seq` CLI. Use for explicit `$seq`, artifact/session/tool/memory/plan forensics, skill activation and outcome audits, decision provenance, `$tune` evidence, watched-session deltas, worker attribution, or reproducible historical reports. Prefer the narrowest lifted command: `skill-decision-audit` for what a skill changed, `skill-evidence` for whether it appeared, then workflow/session/tool/memory surfaces, and generic `query` last. Run opencode only when the user literally says `opencode`."
---

# seq

## Mission

Use deterministic session and memory evidence to answer:

```text
what happened
where it happened
what evidence supports it
what remains unknown
```

For skill tuning, distinguish:

```text
skill presence
skill decision influence
downstream outcome
```

These are not interchangeable.

## Source boundary

Primary sources:

```text
~/.codex/sessions
~/.codex/memories
```

`seq` reports local-corpus evidence, not product-wide telemetry.

State the denominator before reporting counts.

## Routing ladder

Use the narrowest command that owns the question.

### Skill decisions and tuning

```text
skill-decision-audit
skill-evidence
skill-success-rank
skill-audit
skill-cohort
workflow-audit
workflow-overlap
```

### Session and artifact forensics

```text
artifact-search
plan-search
find-session
session-prompts
sessions
turns
session-detail
tail
```

### Tools and orchestration

```text
tool-lifecycle
tool-audit
tool-search
session-tooling
session-graph
orchestration-concurrency
```

### Review and workflow-specific audits

```text
adjudication-audit
resolve-churn-audit
review-compiler-audit
goal-audit
routing-gap
```

### Memory

```text
memory-inventory
memory-provenance
memory-map
memory-history
memory-extension-audit
```

### Messages, tokens, and generic query

```text
message-search
message-audit
token-usage
token-window
token-cost
query-diagnose
query
```

Start with `artifact-search` for broad artifact forensics.

Use `query` only when no lifted surface fits.

## Skill-decision audit

When the question is:

```text
How did this skill affect actual decisions?
Was its contract followed?
Was it missed when its trigger appeared?
Did compliance improve outcomes?
What should $tune change?
```

use:

```bash
seq skill-decision-audit \
  --root ~/.codex/sessions \
  --skill <skill> \
  --skill-root codex/skills \
  --repo <repo> \
  --last 30d \
  --exclude-current \
  --mode tune-packet \
  --format json
```

Modes:

```text
summary
episodes
misses
clauses
outcomes
matched-cohort
tune-packet
delta
```

### One-session delta

```bash
seq skill-decision-audit \
  --root ~/.codex/sessions \
  --session-id <id> \
  --skill <skill> \
  --since-cursor '<cursor-token>' \
  --mode delta \
  --format json
```

This is the preferred `$shadow` / in-flight `$tune` surface.

### Evidence levels

The command must preserve:

```text
structured SDR-v1 receipt
explicit assistant attribution
contract-aligned action
associated outcome
co-occurrence only
```

Do not collapse these into one “used” count.

### Tune packet

`--mode tune-packet` emits:

```text
skill_tuning_evidence / STE-v1
```

It must include denominator, contract authority, trigger quality, decision influence, clause compliance, outcomes, workarounds, exemplars, gap signatures, and limitations.

If the installed binary lacks `skill-decision-audit`, report the CLI gap and use existing narrow commands only as a bounded fallback.

Do not hand-roll a pseudo-equivalent with broad shell transcript parsing as the normal route.

## Skill presence audit

Use `skill-evidence` when the question is only whether and how a skill appeared:

```bash
seq skill-evidence \
  --root ~/.codex/sessions \
  --session-id <id> \
  --skill <skill> \
  --format json
```

Evidence classes should remain separate:

```text
explicit user call
implicit assistant declaration
injected skill block
manual skill-file read
target-skill lens use
successful outcome evidence
raw mention
```

Presence does not prove influence.

## Contract-aware evidence

Decision-oriented skills may carry:

```text
references/decision-contract.yaml
```

Schema:

```text
skill_decision_contract / SKDC-v1
```

The CLI should prefer:

1. explicit `--contract`;
2. target skill’s decision-contract file;
3. no clause-level judgment.

Do not semantically invent a contract in the CLI.

When no explicit contract exists:

```text
contract_authority: absent
clause_compliance: not_assessed
```

The model using `$tune` may reconstruct an inferred contract, but `$seq` must label it external/inferred.

## Decision receipts

Recognize structured assistant artifacts:

```yaml
skill_decision_receipt:
  receipt_version: SDR-v1
  decision_id:
  skill:
  skill_contract_fingerprint:
  trigger_refs: []
  clause_refs: []
  question:
  alternatives_considered: []
  selected_route:
  rejected_routes: []
  expected_outcome:
  artifact_state:
```

An SDR receipt is the strongest deterministic decision-attribution evidence.

A receipt does not prove a good outcome.

## Causality discipline

Report:

```text
explicit decision delta
contract-consistent but causality unproven
associated outcome only
co-occurrence only
```

Matched cohorts are observational.

Never claim causal effect from a matched cohort.

## Worker attribution

Use linked workers only when requested or when the skill’s decision occurred in a delegated worker.

Preserve:

```text
root session
worker session
parent edge evidence
lane/receipt id
declared skills
decision receipt
outcome
```

Do not merge unlinked worker sessions into a root denominator.

## Current command patterns

Representative lifted surfaces:

```bash
seq artifact-search --contains "<term>" --surface messages --format jsonl
seq plan-search --repo <repo> --include-body --format jsonl
seq skill-audit --skill <skill> --mode activation --last 30d --exclude-current
seq workflow-audit --workflow <workflow> --mode cohort-report --last 7d
seq tool-lifecycle --session-id <id> --format table
seq session-detail --session-id <id> --format markdown
seq memory-inventory --mode categories --format table
```

Use generic `query` only when no lifted command fits; use `query-diagnose` when it behaves unexpectedly.

See [command-routing.md](references/command-routing.md).

## Memory model

Treat memory as file-backed:

```text
memory_summary.md  routing/index
MEMORY.md          durable handbook
raw_memories.md    lower-level consolidation
rollout_summaries  per-rollout provenance
```

Use memory-specific lifted commands before generic query.

## Opencode gate

Only use:

```text
opencode-prompts
opencode-events
opencode datasets
```

when the literal user request includes:

```text
opencode
```

Skip that branch otherwise.

## Time and contamination

Use:

```text
--since
--until
--last
--exclude-current
```

when supported.

Treat pasted skill bodies, current audit prompts, developer instructions, memory summaries, and generated reports as potential contamination.

State how the current session was handled.

## Denominator rules

Always distinguish:

```text
candidate sessions
activation sessions
decision episodes
decision-effect episodes
outcome-associated episodes
worker episodes
```

For example:

```text
0 native activation rows
12 explicit assistant declarations
7 decision episodes
3 explicit route changes
```

is better than:

```text
skill used 12 times
```

## Empty-result protocol

An empty lifted result is not automatically absence.

Check:

1. command stderr/status;
2. time bounds;
3. current-session exclusion;
4. activation denominator;
5. worker masking;
6. raw mentions versus structured evidence;
7. known command-surface gaps.

Only then conclude no evidence found.

## Output quality

A good `$seq` answer contains:

```text
source
scope/window
denominator
command surface
evidence rows or artifact refs
what the evidence proves
what it does not prove
limitations
```

## CLI development

Source:

```text
$HOME/workspace/tk/skills-zig
```

Release packaging:

```text
$HOME/workspace/tk/homebrew-tap
```

For new decision-provenance behavior, use the separate implementation spec included with this drop-in:

```text
SEQ_SKILL_DECISION_AUDIT_CLI_SPEC.md
```

Do not approximate the new command by silently changing unrelated lifted commands.

## Hard rules

- `$seq` first for explicit `$seq` and artifact-forensics requests.
- Use the narrowest lifted surface.
- Raw mention is not activation.
- Activation is not influence.
- Influence is not causality.
- Do not merge unrelated workers.
- Do not hide denominator changes.
- Do not use opencode without literal permission.
- Do not treat memory inventory as behavioral causality.
- Do not use generic query when a stable lifted command owns the question.
- Report a CLI surface gap when the needed deterministic operation is absent.
