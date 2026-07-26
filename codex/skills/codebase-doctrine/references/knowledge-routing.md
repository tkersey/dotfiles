# Knowledge Routing

Route knowledge only after doctrine induction. Premature routing biases inquiry
toward the available destination, especially skill creation.

## Strongest-destination order

Prefer, when semantics permit:

1. **Representation or code** — make an invalid state or illegal transition
   unrepresentable or unreachable.
2. **Test, property, model, static tooling, or CI** — mechanically establish a
   stable rule or proof obligation.
3. **Repository guidance** — state universal operating rules that every future
   agent needs.
4. **ADR or reference** — preserve durable rationale, alternatives, and
   invalidators that do not need active routing.
5. **Canonical negative ledger** — preserve witnessed failed routes with current
   applicability and reopening criteria.
6. **Repository-specific skill** — guide recurring, consequential,
   context-sensitive judgment that cannot be more strongly enforced elsewhere.
7. **Retain in doctrine** — preserve material context that must remain visible but
   has no stronger current owner.
8. **Reject** — discard noise, unstable speculation, local trivia, or duplicate
   context.

Important does not imply skill-worthy.

## Routing questions

For each durable doctrine item ask:

```text
Can the repository prevent the violation directly?
Can a mechanical proof detect it?
Does every contributor or agent need the rule?
Is the value mainly rationale and invalidation history?
Is this a witnessed failed route with current applicability?
Does correct use require recurring contextual judgment?
Will the doctrine itself be durably available to the future consumer?
```

Choose one primary owner. Secondary references may aid discovery but may not
create competing semantic authorities.

## Retain-in-doctrine boundary

`retain in doctrine` is meaningful only when the doctrine is expected to be
available to the relevant future consumer. If the result will remain only in one
conversation, either persist it with explicit authorization or route the
knowledge elsewhere.

## Negative evidence

Only a current canonical Negative Ledger projection may prohibit a route.
Historical failures, review comments, and recollections may:

- motivate inquiry;
- supply a counterexample;
- lower confidence;
- suggest a reopening test.

They may not silently become durable exclusions.

## Routing drift

Revisit the route when:

- a rule becomes mechanically enforceable;
- a skill's judgment becomes stable enough for tooling;
- a law becomes local rather than repository-wide;
- doctrine changes jurisdiction or owner;
- an ADR becomes stale;
- a negative route's reopening criterion is satisfied;
- the doctrine is no longer durably available.
