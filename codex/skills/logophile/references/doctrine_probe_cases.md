# Doctrine Probe Cases

## Should trigger doctrine mode

```text
Find doctrine words for reviewing PR comments more discriminately.
```

Expected:
- `rebuttal-first`
- `discriminative`
- `invariant-seeking`
- `ablative`
- artifacts: Resolve Selection, no-change countercase, Ablation Activation Receipt.

```text
What doctrine word captures moving from plan to PR?
```

Expected:
- `actuating`
- artifact: Actuation Receipt.

```text
What is the doctrine word for decomposing and removing what is unnecessary?
```

Expected:
- `winnowing`
- companions: `factoring`, `quotienting`, `ablative`, `normalizing`, `refinement-preserving`.

```text
What doctrine word captures reset?
```

Expected:
- `rebaselining`
- artifact: Baseline Receipt.

```text
Find words like unsound for type-theoretic review.
```

Expected:
- `unwitnessed`, `illegal inhabitant`, `partial`, `totalizing`, `preservation-aware`, `progress-aware`.

## Should not trigger doctrine mode

```text
Fix the failing test.
```

Unless the user asks for wording or doctrine, this is implementation, not logophile.

```text
Review this patch for regressions.
```

This belongs to review workflows, not logophile, unless the user asks for wording or names.

```text
Run the tests and ship the PR.
```

This belongs to execution/shipping workflows.

## Quality checks

A doctrine answer must:

- name the pressure;
- choose words with distinct jobs;
- explain near misses when useful;
- include artifacts;
- end with `Use This:` and `Operationalization:`.

Reject answers that:

- list fancy synonyms;
- include generic praise words;
- fail to say what the receiving agent should do differently;
- omit the artifact/receipt.
