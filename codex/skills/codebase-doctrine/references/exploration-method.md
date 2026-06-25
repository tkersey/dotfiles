# Exploration Method

Every search answers a named, falsifiable question.

Prefer the cheapest method that can materially update the model:

```text
definition/reference          symbol or language-aware search
ownership                     write-site, transition, certificate, rollback
behavior                      tests, fixtures, public observations
historical recurrence         git log, -S, -G, blame, reverts
runtime path                  trace, coverage, reproduction
agent decision history        bounded $seq query
failed route                  canonical negative-ledger query/export
incomplete historical reason  bounded $retrace replay
```

Search lanes:

```text
guidance
static_structure
symbols_and_references
behavior_and_tests
authority_and_mutation
history_and_forensics
runtime
agent_history
negative_evidence
user_authority
```

A no-result search is evidence only when its corpus, pattern, and scope are
recorded.

Avoid:

- reading large files without a question;
- treating directory names as architecture;
- treating comments as proof;
- counting matches instead of tracing authority;
- using every mechanism mechanically;
- continuing broad search after material decisions stabilize.
