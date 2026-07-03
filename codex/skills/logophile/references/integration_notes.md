# Integration Notes

## Trigger boundary

`logophile` may trigger implicitly for human-facing language surfaces and doctrine-word tasks. It must not become a hidden operational policy engine.

Use it for:

- names;
- headings;
- skill/subagent/mode names;
- PR replies;
- commit/PR text;
- final summaries;
- doctrine stacks;
- prompt wording.

Do not use it for:

- ordinary code implementation;
- verification;
- review adjudication;
- orchestration;
- machine-consumed syntax.

## Doctrine compiler boundary

Doctrine compiler mode designs the words and copy-paste block. It does not execute the resulting workflow.

Example:

- It may recommend `actuating` and produce an Actuation Receipt template.
- It must not run `$actuating` unless explicitly asked.

## Composition order

Use `logophile` late when the text will be read or pasted by a human.

Good:

```text
review-adjudication -> logophile for PR reply wording
fixed-point-driver -> logophile for closure summary
seq -> logophile for concise source-backed synthesis
```

Bad:

```text
logophile -> silently rewrite operational decisions
logophile -> rename code identifiers for style
logophile -> summarize away proof receipts
```

## Echo compatibility

Keep repo-level `Echo:` rules outside the generated artifact.

## Clean doctrine answer shape

End doctrine answers with:

```md
Use This:
[copy-pasteable doctrine block]

Operationalization:
[artifact/gate/ledger/receipt produced]
```
