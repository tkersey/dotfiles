# Output Templates

## Drift

```text
SPEC_PIPELINE_DRIFT_WARNING
## Spec Pipeline Receipt
<one SGR-v2 JSON object>
```

## Gate failure

```text
SPEC_PIPELINE_GATE_FAILURE
## Spec Pipeline Receipt
<one SGR-v2 JSON object>
## Gate Result
<1-3 questions>
```

## Complete handoff

```text
# Title
## Spec Pipeline Receipt
<one SGR-v2 JSON object>
## Evidence Brief
## Gate Result
<decision packet>
<14 spec sections>
## Invariant Challenge
## Fresh-Eyes Pass
## Execution Handoff
```

The final SGR-v2 JSON must pass its passive Ledger definition before emission.
A plan-ready handoff also includes one PSC-v1 JSON object structurally validated
through its own definition. Neither structural result grants handoff authority.
