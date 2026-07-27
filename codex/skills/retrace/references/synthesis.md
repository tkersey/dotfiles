# Decision Reconstruction: DRR-v1

DRR-v1 separates deterministic source evidence from replay evidence and hindsight.

The sole machine schema is
[`../definitions/ledger/decision-reconstruction-record.json`](../definitions/ledger/decision-reconstruction-record.json).
Validate the authored JSON with Ledger and retain the definition digest. This
page owns the interpretation and claim-strength laws, not a duplicate field
inventory.

## Source-governance effect

```text
authoritative
  workflow-governed replay claims allowed

declared_uncontrolled
  replay may study why the controller/workflow was not operationally used

incidental / ambiguous / absent
  no valid replay population for workflow-effect claims
```

A classifier row is not itself authoritative. The SGG evidence and provenance decide.

## Route stability

Stable:

```text
all valid pre-decision replays select the historical route
```

Mixed:

```text
several supported routes selected
```

Unstable:

```text
most valid pre-decision replays select another route
```

Unavailable:

```text
no valid outcome-blind replay or source governance blocked replay
```

Always report sample size and lineage modes.

## Skill/workflow effect

Strongest:

```text
historical explicit attribution
+ authoritative governance
+ exact anchor
+ controlled instruction/evidence ablation
+ route change
```

Weak:

```text
fork self-report
consensus without ablation
outcome association
```

## Confidence

Consider source explicitness, governance provenance, anchor exactness, lineage mode, workspace mode, model match, framing diversity, receipt validity, sample size, and counterevidence.
