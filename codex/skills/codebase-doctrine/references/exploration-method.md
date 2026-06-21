# Exploration Method

## Intake reconnaissance

Before doctrine questions, run a shallow fact-finding pass over guidance, manifests, build/test roots, major subsystems, architecture docs, and existing repository skills.

Its purpose is to remove discoverable facts from the user-question queue. It is not yet doctrine evidence saturation.

Only user-owned, route-changing judgments may be handed to `$grill-me`.


## Question ledger

Every search answers a named question.

```yaml
search_question:
  question_id:
  question:
  why_it_matters:
  lanes: []
  search_methods: []
  evidence_found: []
  model_change:
  status:
```

Questions should be falsifiable where possible:

```text
Which symbol owns durable state mutation?
Can a request bypass the canonical validator?
Do two state representations encode the same accepted behavior?
Which historical repair family keeps recurring?
What proof surface actually establishes the law?
```

## Search lanes

### Guidance

Read repository-local instructions, README, architecture docs, ADRs, manifests, build files, CI, and release metadata.

Use declared architecture as a claim to verify, not truth.

### Static structure

Map top-level modules, dependency direction, public APIs, entrypoints, major types, and boundaries.

### Symbols and references

Use language-aware references, LSP, AST queries, ctags, or precise text search to locate definitions, callers, implementations, and write sites.

### Behavior and tests

Read tests, fixtures, golden outputs, examples, compile-fail cases, and state-machine/property tests.

Tests reveal intended behavior and proof gaps, but may preserve historical accidents.

### Authority and mutation

Search constructors, setters, mutation functions, transactions, validation, commit/publish paths, state transitions, and error/rollback paths.

Authority claims should be based mainly on writes and certificates.

### History and forensics

Use Git log, blame, `-S`, `-G`, reverts, bug-fix subjects, and PR/review history.

Historical frequency is evidence of recurrence, not automatically a current law.

### Runtime

When safe and available, use traces, coverage, logs, benchmarks, telemetry schemas, and reproductions.

Do not expose secrets or claim runtime evidence when none was gathered.

### Agent history

Use local `$seq` evidence to find recurring decisions, workarounds, review clusters, and skill behavior.

Separate activation, decision influence, and outcome.

### Negative evidence

Read durable negative-ledger records and failed-route evidence.

Fuzzy or stale matches are suggestive only.

## Search method selection

Prefer the cheapest method that can materially update the model.

Examples:

```text
definition/reference question -> LSP or symbol search
ownership question -> write-site and transition search
historical recurrence -> git -S/-G/log
intended behavior -> tests/fixtures/docs comparison
runtime path -> trace or coverage
agent decision history -> seq
```

## Search record

Record method, result, and model change.

A search that finds nothing may still be useful when the corpus and pattern are explicit.

## Anti-patterns

- reading large files sequentially without questions;
- treating directory names as architecture;
- treating comments as proof;
- using one search method for every lane;
- counting matches instead of understanding ownership;
- endless search after material decisions have stabilized.
