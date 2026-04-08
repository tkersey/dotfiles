# Task Pressure Map

Infer pressures from the task first. Use these defaults only when the task underspecifies them.

## Bug fix / regression / review response
Dominant pressures:
- unsound diagnosis
- hidden invariant break
- oversized fix
- missing verification

Default stack candidates:
- `unsound`
- `mechanistic`
- `accretive`
- `traceable`

## Feature implementation / planned code
Dominant pressures:
- architecture drift
- scope creep
- unnecessary complexity
- weak verification

Default stack candidates:
- `canonical`
- `accretive`
- `invariant-preserving`
- `traceable`

## Code review / adversarial audit
Dominant pressures:
- local blindness
- untested assumptions
- regression risk
- misuse hazards

Default stack candidates:
- `adversarial`
- `exhaustive`
- `hazard-seeking`
- `traceable`

## Security review
Dominant pressures:
- permissive failure
- hidden attack surfaces
- unsafe defaults
- unproved mitigations

Default stack candidates:
- `fail-closed`
- `adversarial`
- `hazard-seeking`
- `traceable`

## Research memo / market scan
Dominant pressures:
- weak sourcing
- overclaiming
- shallow synthesis
- bloated prose

Default stack candidates:
- `source-disciplined`
- `calibrated`
- `adversarial`
- `synthetic`

## Planning / strategy
Dominant pressures:
- ill-posed goals
- hidden assumptions
- missing tradeoffs
- false certainty

Default stack candidates:
- `ill-posed`
- `calibrated`
- `parsimonious`
- `traceable`

## Naming / policy wording / contracts
Dominant pressures:
- semantic drift
- obligation drift
- vague scope
- overloaded terminology

Default stack candidates:
- `precise`
- `scoped`
- `obligation-preserving`
- `distinctive`

Notes:
- `precise`, `scoped`, and `obligation-preserving` are task-local descriptive labels. Use them only if they produce an actual gain in the doctrine block.
- Replace generic defaults with sharper domain terms whenever the task supports them.
