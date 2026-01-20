# Technique: Provocation (PO) / Lateral Thinking

## One-liner
Make a deliberately “wrong” statement (PO), then mine it for a usable lever by asking what would make it workable.

## Use when
- Conventional reasoning keeps producing the same answers.
- You need an “Aha” (new representation), not better optimization.
- The real constraint is imagination, not feasibility.

## Avoid when
- You need consensus and psychological safety is low (use Six Thinking Hats first).
- The problem is already well-framed and needs execution.

## Inputs
- Problem framing + constraints.
- A willingness to suspend feasibility temporarily.

## Procedure (fast, 6–10 min)
1. Write PO: a provocative reversal/exaggeration.
2. Ask: “What would have to be true for PO to work?”
3. Extract 2–3 principles/levers.
4. Translate levers into experiments (signal + escape hatch).

## Procedure (full, 15–25 min)
1. Generate 3 provocations
   - Reverse defaults, remove actors, eliminate steps, invert incentives.
2. For each PO
   - Enumerate enabling conditions (“If PO were true, we’d need …”).
   - Identify the hidden constraint the PO exposes.
3. Translation (critical step)
   - Convert enabling conditions into actionable levers:
     - automation, instrumentation, permission model changes, incentives, interface redesign.
4. Converge
   - Pick 1 lever that is (a) high-signal, (b) reversible.

## Prompt bank (copy/paste)
- “PO: the opposite default is true.”
- “PO: remove the role/system entirely.”
- “PO: everyone does this in 1 minute.”
- “What would make this possible without magic?”
- “What principle does this suggest we should adopt?”

## Outputs (feed CPS portfolio)
- 2–3 levers that break the current framing.
- A set of translated experiments (not just clever statements).

## Aha targets
- Discovering the missing primitive (e.g., “examples, not prose”; “signals, not opinions”).
- Turning a sacred cow into a variable.

## Pitfalls & defusals
- Pitfall: staying contrarian → Defusal: translation must yield concrete levers.
- Pitfall: provocation violates constraints → Defusal: use constraints as translation boundaries.
- Pitfall: output is not testable → Defusal: rewrite as smallest reversible experiment.

## Examples
### Engineering
PO: “No one writes docs.”
- Enablers: docs must be generated; updates must be implicit.
- Lever: generate docs from code + examples; enforce via CI that examples compile.
Signal: doc freshness improves; escape hatch: keep manual docs for critical paths.

### Mixed domain
PO: “Meetings never happen.”
- Enablers: decisions must be asynchronous; context must be shared.
- Lever: decision log + written proposals + timeboxed comment window.
Signal: decisions still happen; escape hatch: reintroduce a short sync for contentious topics.