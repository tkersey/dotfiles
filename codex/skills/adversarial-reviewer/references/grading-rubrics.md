# Grading rubrics

## Complexity Delta
- overall_delta: reduces | neutral | increases | indeterminate
- vectors:
  - control-flow
  - state
  - coupling
  - config-surface
  - API-surface
  - operational-surface
  - cognitive-load
- essential_or_incidental: essential | incidental | mixed
- materiality: material | non-material | unknown

## Invariant Ledger
- invariant
- source: explicit-contract | behavior | data-shape | ordering | persistence | security | operational | inferred
- tier: critical | major | supporting
- status: preserved | strained | broken | unknown
- confidence: proven | plausible | speculative
- blast_radius: local | module | cross-cutting
- evidence

## Foot-Gun Register
- foot-gun
- trigger
- impact
- ease_of_misuse: low | medium | high
- detectability: obvious | subtle | silent
- prevention_or_safer_shape
- evidence
