---
name: bmad
description: BMAD (Best, Most Appropriate, Design) technology decision framework for choosing stacks, databases, clouds, frameworks, and architecture tradeoffs; use when comparing alternatives, weighing costs/risks, or making "best vs most appropriate" calls.
---

# BMAD Method

## When to use
- Choose between competing technologies, vendors, or architectures.
- Decide on stack components (database, cloud, frameworks, data pipeline tools).
- Produce decision records, TCO comparisons, or risk assessments.
- Pressure-test "popular" vs "appropriate for our constraints" claims.

## Quick start
1. Capture constraints: business goals, team skills, budget, timeline, scale, compliance.
2. Evaluate each option with BMAD (Best, Most Appropriate, Design).
3. Summarize in a decision matrix and recommend with caveats.
4. Document as an ADR and define revisit triggers.

## BMAD framework
- Best: absolute technical capability and ecosystem strength.
  - Performance, scalability, feature depth, ecosystem maturity, innovation.
- Most Appropriate: fit to current context.
  - Team skills, time-to-market, cost, existing investments, operational fit.
- Design: long-term architecture alignment.
  - Modular fit, integration complexity, maintenance, portability, strategic roadmap.

## Decision matrix template
```
Option: __________________
Best:
- Strengths:
- Weaknesses:
Most Appropriate:
- Context fit:
- Gaps:
Design:
- Architecture impact:
- Long-term risks:
Cost and risk:
- TCO drivers:
- Lock-in risk:
Recommendation: __________________
Confidence: High | Medium | Low
Revisit triggers: __________________
```

## ADR mini-template
- Decision:
- Context:
- Options considered:
- Tradeoffs:
- Decision and rationale:
- Consequences:
- Revisit triggers:

## Risk matrix (lightweight)
```
Risk | Likelihood | Impact | Mitigation
```

## Common decision patterns

### Database selection
- Best: performance, consistency model, replication, ecosystem.
- Most Appropriate: team experience, operational overhead, current infra.
- Design: data model fit, migration complexity, scaling path.

### Cloud provider choice
- Best: service breadth, reliability, global reach.
- Most Appropriate: pricing model, existing contracts, regional compliance.
- Design: portability, multi-cloud strategy, operational tooling.

### Framework or tooling
- Best: productivity, community, extensibility.
- Most Appropriate: hiring pipeline, onboarding cost, current codebase.
- Design: architecture conventions, testing story, upgrade cadence.

## Cost and risk checklist
- Direct costs: compute, storage, managed services.
- Hidden costs: migrations, training, vendor lock-in, tooling gaps.
- Mitigation: phased rollout, escape hatch, fallback plan.

## Example
Prompt: "Pick between Postgres, DynamoDB, and MongoDB for a multi-tenant SaaS."
Output summary:
- Best: Postgres (feature depth, SQL, ecosystem).
- Most Appropriate: Postgres (team skills, lower ops risk).
- Design: Postgres with partitioning, path to sharding later.
- Decision: Postgres now, reevaluate when scale demands.

## Best practices
- Always state assumptions and constraints.
- Separate "best in general" from "best for us."
- Prefer reversible choices; design escape hatches.
- Revisit decisions when constraints change.

## Activation cues
- "best vs most appropriate"
- "technology decision"
- "stack selection"
- "database choice"
- "cloud provider comparison"
- "architecture tradeoffs"

## References
- Source skill: https://github.com/anton-abyzov/specweave/tree/develop/plugins/specweave-alternatives/skills/bmad-method
