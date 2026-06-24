# Review Adjudication Authority Fanout

Authority lanes are not voters. Each lane owns one bounded clearance dimension. The root integrates valid packets and may choose a stricter route, but may not upgrade past an unresolved veto.

All lanes use `specialist-packet-v2`; role-specific results live in `domain_payload`.

## Available lanes

| Lane | Owns | Include when |
|---|---|---|
| evidence authority | current grounding, reachability, proof-surface false positives | current evidence is not locally decisive |
| direction/ownership authority | objective, branch ownership, non-goals | direction or owner is contested |
| criticality authority | accepted severity and closure significance | severity changes disposition |
| no-change advocate | strongest no-change or no-resolve case | non-trivial mutation remains plausible |
| validation-value authority | mutate now vs validate first vs no value | validation order is route-changing |
| fix-shape authority | minimum safe fix and overbroad-fix risk | mutation is plausible but shape is unresolved |
| ablative-surface authority | delete, collapse, reuse, privatize, decommission, canonicalize | additive surface or duplicate truth is possible |
| ablation activation sentinel | whether ablation is required or blocked | applicability itself is ambiguous |

## Adaptive selection

```text
direct:    root-equivalent local clearance, no specialist
focused:   1-2 unresolved lanes
tested:    3-4 independently material lanes
high-risk: 5-8 lanes for public, security-critical, irreversible, or broad semantic work
```

The default is focused, not full fanout. Full fanout is justified only when at least five lanes remain independently route-changing or the control-plane registry classifies the work as high-risk.

Every spawned lane requires a `specialist_intent` stating the unresolved question and expected decision delta.

## Clearance law

A finding may route to mutation only when:

- evidence clearance is current;
- direction and ownership are compatible;
- accepted criticality warrants action;
- the strongest no-change case is defeated or narrowed below the action threshold;
- validation sequencing is resolved;
- fix shape is bounded;
- ablative alternatives are cleared when additive or keep-surface choices exist;
- no required lane is vetoed, unresolved, stale, or missing.

Root may always downgrade to validate-only, no-change, defer, follow-up, or blocked. Root may not permissively override a veto into mutation.

## Domain payload

Authority lanes place this under `domain_payload`:

```yaml
authority:
  scoped_ids: []
  clearance_by_id: {}
  vetoes:
    - id:
      class:
      claim:
      evidence_ref:
      required_to_clear:
  positive_evidence:
    - id:
      claim:
      evidence_ref:
```

## Value accounting

A valid packet can be neutral. Record whether it changed route, finding, proof, or retired risk. Recurrent neutral lanes should be removed from default fanout while remaining available for explicit high-risk use.
