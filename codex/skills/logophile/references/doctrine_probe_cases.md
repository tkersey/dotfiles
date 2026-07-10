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
- companions: `factorizing`, `quotienting`, `ablative`, `normalizing`, `refinement-preserving`.
- artifact: Winnowing Ledger or Reduction Certificate with recomposition proof.

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

```text
What doctrine word means learning from past cases without blindly obeying memory?
```

Expected:
- `precedential`
- companions: `provenance-preserving`, `distinguishing`, `supersession-aware`.
- artifact: Precedent Ledger with action delta.

```text
Give me a doctrine persona for someone who deliberately sets precedent.
```

Expected:
- mode: `nomothetic`
- persona: `Nomothete`
- near miss: `constitutive` names the act more naturally than the persona.
- artifact: Nomothetic Receipt.

```text
What doctrine words should guide a simulator?
```

Expected:
- `emulative`
- companions: `counterfactual`, `dynamical`, `observational`, `fidelity-bounded`.
- artifacts: Emulation Receipt and Fidelity Boundary.

```text
What doctrine word fits an evaluator, grader, or judge?
```

Expected:
- mode: `adjudicative`
- persona when requested: `Arbiter`
- companions: `criterial`, `evidence-weighted`, `calibrated`, `dispositive`.
- artifact: Adjudication Ledger.

```text
What doctrine word means account for every state transition and residual?
```

Expected:
- `reconciling`
- companion: `conservation-aware`.
- artifact: Reconciliation Ledger or Conservation Ledger.

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

```text
Simulate this protocol and tell me what happens.
```

This is an operational simulation request, not a doctrine-word request. Do not use logophile unless the user asks for simulator terminology or doctrine.

```text
Grade these submissions against the rubric.
```

This is an evaluation workflow, not a doctrine naming request. Do not use logophile unless wording or doctrine output is requested.

## Quality checks

A doctrine answer must:

- name the pressure;
- choose words with distinct jobs;
- separate mode, persona, command, and artifact when relevant;
- explain near misses when useful;
- include artifacts;
- end with `Use This:` and `Operationalization:`.

Reject answers that:

- list fancy synonyms;
- include generic praise words;
- fail to say what the receiving agent should do differently;
- omit the artifact/receipt;
- confuse a persona noun with an operating mode;
- use a proof relation such as `isomorphic` as though it were a reduction operator.