# Dominant Move Brief

## Dominant move

```text
# Dominant Move Brief

## Artifact State
- label:
- relevant surfaces:
- current evidence:
- constraints:

## Verdict
- state: dominant-move
- confidence:
- selected move:
- target lane:

## Why This Move Dominates
- governing reason:
- material axis:
- latent frame used:
- accretive payoff:

## Alternatives Rejected
- alternative:
  - why it loses:
  - what evidence could revive it:

## First Proof Signal
- check:
- expected result:
- failure would imply:
- executor needed:

## Minimum Viable Diff
- likely touched surfaces:
- smallest useful implementation:
- non-goals:
- reversibility:

## Recommended Executor
- executor: fixed-point-driver | human | none | other
- why:
- handoff readiness: ready | partial | not-ready
```

## Non-winner stop states

Use the same brief title, but set `state` to one of:

- `no-dominant-move`
- `needs-evidence`
- `needs-decision`
- `blocked`

Always include the fastest discriminating check or the required decision when known.
