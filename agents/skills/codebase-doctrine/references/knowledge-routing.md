# Knowledge Routing

Route knowledge only after doctrine induction. Premature routing biases inquiry
toward the available destination, especially skill creation.

## Strongest-destination order

Prefer, when semantics permit:

1. **Representation or code** — make an invalid state or illegal transition
   unrepresentable or unreachable.
2. **Test, property, model, static tooling, or CI** — mechanically establish a
   stable rule or proof obligation.
3. **Local interface contract** — explain the promises, effects, failures, and
   remaining caller obligations beside the API that owns them.
4. **Repository guidance** — state universal operating rules that every future
   agent needs.
5. **ADR or reference** — preserve durable rationale, alternatives, and
   invalidators that do not need active routing.
6. **Canonical negative ledger** — preserve witnessed failed routes with current
   applicability and reopening criteria.
7. **Repository-specific skill** — guide recurring, consequential,
   context-sensitive judgment that cannot be more strongly enforced elsewhere.
8. **Retain in doctrine** — preserve material context that must remain visible but
   has no stronger current owner.
9. **Reject** — discard noise, unstable speculation, local trivia, or duplicate
   context.

Important does not imply skill-worthy.

## Routing questions

For each durable doctrine item ask:

```text
Can the repository prevent the violation directly?
Can a mechanical proof detect it?
Does the caller of one interface need it to use that interface correctly?
Does every contributor or agent need the rule?
Is the value mainly rationale and invalidation history?
Is this a witnessed failed route with current applicability?
Does correct use require recurring contextual judgment?
Will the doctrine itself be durably available to the future consumer?
```

Choose one primary owner. Secondary references may aid discovery but may not
create competing semantic authorities.

## Local contracts and hidden decisions

Necessary local API knowledge need not pass the nonlocal durable-doctrine admission
bar. Route it beside the interface rather than discard it as trivia or promote it
to repository-wide doctrine. Explain the abstraction, sanctioned observations,
failure meaning, effects, ordering and lifetime obligations, and implementation
decisions callers may ignore. Types and proofs can establish laws; documentation
explains the consumer's model. Neither replaces the other, and comments do not
acquire authority over accepted requirements merely by existing.

At a live design choice, the smallest complete contract is a design probe. An
explanation full of implementation details or avoidable choreography may expose a
leaky boundary; omitting those facts is not simplification. Necessary complexity
must remain explicit. Keep nonlocal rationale and alternatives in an ADR or doctrine,
with references rather than competing contracts. This read-only skill recommends
the destination; the authorized implementation owner makes the change.

Distinguish ownership of a law from ownership of a replaceable design decision.
Trace which clients must change if the representation, format, or lifecycle changes.
Splitting read/transform/write phases is not evidence for splitting knowledge of
one format. Consolidate shared decision knowledge only when independent verification,
authorization, effect ordering, and other live obligations remain protected.

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
