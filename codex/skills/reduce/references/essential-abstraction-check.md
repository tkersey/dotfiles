# Essential abstraction check

Run this before recommending `replace` or `delete`. The goal is to avoid flattening real truth while removing incidental machinery.

## Checklist

Does the layer encode any of the following?

| Essential truth | Signal | Preserve as |
|---|---|---|
| Product | fields must travel together and are projected independently | record/object/value object |
| Coproduct | states or variants are mutually exclusive | tagged union/sealed hierarchy/enum with payload |
| Refined/equalizer | same stable predicate is repeatedly enforced | parser, checked constructor, refined wrapper |
| Pullback | two things must agree on tenant/account/version/schema | checked aggregate or witness |
| Exponential | behavior is supplied and composed | function/strategy table, explicit handler map |
| Free construction | syntax must be interpreted, explained, persisted, rendered, or logged | AST plus interpreters |
| Protocol | allowed operations depend on current state | transition table, reducer, state-specific commands |
| External obligation | public API/schema, compliance, audit, billing, SLO, security | compatibility wrapper, contract tests, migration plan |

## Verdict impact

- If none are present and usage is absent/redundant, `delete` may be possible.
- If truth is present but wrapper tax is high, prefer `split`.
- If truth is present and already encoded well, prefer `keep` or `slice`.
- If truth is present but encoded poorly, hand off to `universalist` before reducing.

## Split template

```md
Layer under audit:
Incidental wrapper to reduce:
Essential truth to preserve:
Current encoding:
Better lower/higher encoding:
First seam:
Compatibility boundary:
Proof signal:
Rollback:
```

## Anti-patterns

Do not:

- replace a state machine with optional fields;
- remove a validator and rely on scattered call-site discipline;
- delete a gateway without checking external clients;
- replace transactions with ad hoc query sequences;
- remove codegen while silently losing schema compatibility;
- delete framework lifecycle hooks before identifying who calls them;
- flatten a protocol into generic string statuses without transition tests.
