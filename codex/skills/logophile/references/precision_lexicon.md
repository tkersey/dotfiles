# Precision Lexicon

Use these as guarded phrase replacements. A replacement is valid only when it preserves meaning, obligation, uncertainty, and agency.

## Generic -> sharper defaults
- `improve` -> `tighten`, `harden`, `simplify`, `stabilize`, `clarify`, `validate`, `defuse`, or `accelerate` when the local gain is clear.
- `handle` -> `reject`, `normalize`, `parse`, `route`, `validate`, `recover`, `surface`, or `fail-closed` when the behavior is known.
- `deal with` -> name the action: `triage`, `isolate`, `resolve`, `defer`, `route`, `instrument`, `prove`, or `document`.
- `make better` -> name the axis: `more deterministic`, `more traceable`, `less coupled`, `more canonical`, `lower blast radius`.
- `things` / `stuff` -> name the object: `comments`, `invariants`, `handlers`, `paths`, `checks`, `risks`, `artifacts`.
- `issue` -> `defect`, `risk`, `regression`, `invariant break`, `foot-gun`, `mismatch`, or `gap` when the class is known.
- `problem` -> `failure mode`, `constraint conflict`, `soundness gap`, `scope mismatch`, or `evidence gap` when known.
- `review feedback` -> `review claim`, `review finding`, `review suggestion`, or `review disposition` depending on context.

## Coding and review language
- `works` -> `passes the targeted check`, `preserves the contract`, `closes the gate`, or `satisfies the invariant`.
- `safe` -> `fail-closed`, `bounded`, `reversible`, `invariant-preserving`, `permission-checked`, or `no broader blast radius`.
- `test it` -> `verify the changed path`, `reproduce the failure`, `exercise the invariant`, or `run the closure gate`.
- `fix this` -> `remediate the material finding`, `close the invariant break`, or `apply the narrowest sufficient change`.
- `review this` -> `adjudicate the claim`, `stress the changeset`, `audit invariants`, or `verify readiness`.

## Doctrine / rigor language
- `be rigorous` -> `reject unwitnessed claims and preserve named invariants`.
- `be careful` -> `label uncertainty, preserve obligations, and check the failure surface`.
- `think deeply` -> `derive the governing invariant and test the strongest countercase`.
- `use better words` -> `choose doctrine words that change procedure, not tone`.

## Guardrails
Do not replace if:
- the sharper word overstates certainty,
- the original intentionally stays broad,
- the domain has a canonical term,
- the substitution changes agency or obligation,
- the phrase is code, an identifier, a flag, a path, a schema field, or machine-consumed syntax.
