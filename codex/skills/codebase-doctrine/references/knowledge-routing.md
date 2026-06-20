# Knowledge Routing

Every durable finding gets one primary destination.

## Destinations

```text
code
type_or_representation
test_or_property
static_tool_or_linter
CI_gate
AGENTS_or_repository_guidance
ADR_or_reference
negative_ledger
repository_root_skill
focused_skill
retain_in_doctrine
reject
```

## Routing hierarchy

1. Prevent invalid state in representation/code.
2. Enforce mechanical rules with tools/CI.
3. Prove behavioral laws with tests/properties/models.
4. Put universal repository conventions in concise guidance.
5. Put rationale/history in references/ADRs.
6. Put failed routes in the negative ledger.
7. Use skills for recurring judgment, route selection, and context-sensitive decisions.
8. Retain uncertainty in doctrine.
9. Reject noise.

## Route record

```yaml
knowledge_route:
  knowledge_id:
  statement:
  source_claim_ids: []
  primary_destination:
  secondary_destinations: []
  reason:
  enforcement_strength:
  owner:
  status:
```

## Skill anti-bias

A finding is not skill-worthy merely because it is important.

Skills are weaker than code/tools for deterministic constraints.
