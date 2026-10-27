# Categorical data for exact context

Treat context preparation as a task-indexed data exchange problem.

```text
source schema S
source instance I : S -> Set
task schema T_q
mapping M_q : S -> T_q
prepared context J_q : T_q -> Set
```

Retrieval builds candidate source data. Context compilation constructs a target instance.

## Context schema examples

Factual answer:

```text
Question, Claim, Evidence, Source, CounterEvidence, Assumption, Timestamp, Derivation
```

Decision:

```text
Decision, Option, Criterion, Constraint, Preference, Evidence, Risk, Recommendation
```

Debugging:

```text
Symptom, Trace, Service, Endpoint, Dependency, RecentChange, Hypothesis, Evidence, Test, PatchCandidate
```

Agent action:

```text
Goal, PlanStep, ToolCall, ToolResult, PolicyConstraint, Memory, Observation, Risk, Approval
```

## Constraints

- every claim has evidence, assumption, missingness, or contradiction;
- every measurement has unit and period;
- every source has timestamp or undated marker;
- every derived fact has a derivation path;
- every recommendation links to criteria and evidence;
- every unresolved conflict is represented as contradiction.
