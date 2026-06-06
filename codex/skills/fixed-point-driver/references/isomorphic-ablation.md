# Isomorphic Ablation

Ablative deletion must be behavior-preserving unless the user explicitly asked to
retire behavior.

## Ablative Isomorphism Card

```md
| card id | surface | action | behavior preserved | public contract preserved | error semantics preserved | ordering/side effects preserved | clone classification | abstraction-ladder check | compatibility risk | proof signal | status |
|---|---|---|---|---|---|---|---|---|---|---|---|
```

Check the preservation axes that matter:

- inputs/callers covered;
- ordering and tie-breaking;
- error semantics and failure mode;
- laziness/materialization;
- short-circuit behavior;
- side effects: logs, metrics, spans, DB writes, IO, public messages;
- type narrowing / exhaustiveness / variant coverage;
- compatibility, migrations, and public API promises.

If a card cannot be filled, route `validate-first` or keep with warrant. Do not
pretend cleanliness proves equivalence.
