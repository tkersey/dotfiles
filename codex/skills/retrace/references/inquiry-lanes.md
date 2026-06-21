# Inquiry Lanes

Use distinct lanes so framing does not collapse the experiment.

## Rationale witness

Horizon:

```text
post_decision_pre_outcome
```

Question:

```text
Reconstruct the visible basis of the decision. Cite evidence, assumptions,
alternatives, and the fact most likely to flip it. Label reconstruction.
```

Purpose:

```text
contemporaneous explanation
```

## Counterfactual replay

Horizon:

```text
pre_decision
```

Question:

```text
Choose a route from visible context. State alternatives, evidence,
assumptions, uncertainty, and route-flip condition.
```

Purpose:

```text
route stability
```

## Alternative challenger

Horizon:

```text
pre_decision
```

Question:

```text
Make the strongest evidence-consistent case for the best non-historical
route. State falsifier, cost, and risk.
```

Purpose:

```text
search missed alternatives
```

Do not say the alternative was historically considered unless source evidence shows it.

## Assumption probe

Horizon:

```text
pre_decision or post_decision_pre_outcome
```

Question:

```text
List assumptions necessary for the selected route. Identify which are
observed, inferred, or unsupported.
```

## Evidence ablation

Horizon:

```text
pre_decision
```

Hold out or alter one named evidence item.

Purpose:

```text
causal sensitivity of the visible decision process
```

Ablation must be explicit and reflected in FIR `evidence_withheld`.

## Retrospective

Horizon:

```text
outcome_aware
```

Purpose:

```text
learning, not contemporaneous rationale
```

## Portfolio

Default:

```text
1 rationale
2 counterfactual
1 challenge
```

Use different deterministic lane instructions.

Do not exceed the budget merely because forks disagree.
