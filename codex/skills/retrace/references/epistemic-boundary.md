# Epistemic Boundary

A forked Codex thread is a new execution over inherited visible history.

It cannot reveal the source model's inaccessible private chain of thought.

## Claim classes

```text
historically_explicit
  Directly present in the source session.

trace_inferred
  Supported by visible actions/order/artifacts but not explicitly stated.

fork_consistent
  Reconstructed by one or more fork witnesses.

counterfactual_stable
  Pre-decision replays independently selected the historical route.

outcome_informed
  Uses evidence unavailable at decision time.

unsupported
  Claimed without source or experiment support.

unknown
  Not recoverable from available evidence.
```

## Language

Allowed:

```text
The source explicitly said...
The trace supports...
Two of three pre-decision replays selected...
The rationale witnesses consistently reconstructed...
The route flipped when evidence E was withheld...
```

Forbidden:

```text
The original agent secretly thought...
This is the original chain of thought...
The fork proves what the historical model believed internally...
```

## Consensus limits

Fork agreement can arise from:

```text
same model bias
same instructions
same missing evidence
same framing
same repository snapshot
```

Consensus increases reconstruction confidence, not historical certainty.

## Model drift

Always record model/provider/version.

A current-model replay of an older session answers:

```text
How does this model interpret that historical context?
```

not:

```text
What did the historical model privately reason?
```
