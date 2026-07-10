# Precision Lexicon

Use these as guarded phrase replacements. A replacement is valid only when it preserves meaning, obligation, uncertainty, agency, and copy-paste safety.

## Generic -> sharper defaults

- `improve` -> `tighten`, `harden`, `simplify`, `stabilize`, `clarify`, `validate`, `defuse`, `accelerate`, `actuate`, or `normalize` when the local gain is clear.
- `handle` -> `reject`, `normalize`, `parse`, `route`, `validate`, `recover`, `surface`, `fail-closed`, `totalize`, or `reconcile` when the behavior is known.
- `deal with` -> name the action: `triage`, `isolate`, `resolve`, `defer`, `route`, `instrument`, `prove`, `document`, `rebaseline`, or `decommission`.
- `make better` -> name the axis: `more deterministic`, `more traceable`, `less coupled`, `more canonical`, `lower blast radius`, `more witness-backed`, or `less surface-bearing`.
- `things` / `stuff` -> name the object: `comments`, `invariants`, `handlers`, `paths`, `checks`, `risks`, `artifacts`, `surfaces`, `obligations`, `receipts`.
- `issue` -> `defect`, `risk`, `regression`, `invariant break`, `foot-gun`, `mismatch`, `gap`, `unreconciled residual`, or `soundness gap` when the class is known.
- `problem` -> `failure mode`, `constraint conflict`, `soundness gap`, `scope mismatch`, `evidence gap`, `routing gap`, `unwitnessed guarantee`, or `state-space mismatch` when known.
- `review feedback` -> `review claim`, `review finding`, `review suggestion`, `review disposition`, `counterexample`, or `warrant` depending on context.
- `solve` -> `tractabilize`, `actuate`, `remediate`, `adjudicate`, `construct`, or `prove` when the task shape is known.
- `reset` -> `rebaseline`, `epoch`, `reinitialize`, or `renormalize` depending whether authority, generation, runtime state, or canonical form is changing.
- `decompose` -> `factorize` or `orthogonalize` when the factors and coupling matter.
- `reduce` / `remove what is unnecessary` -> `winnow`, `quotient`, `ablate`, or `normalize` depending whether the task retains live obligations, collapses indistinguishable distinctions, removes unearned surface, or reaches canonical form.
- `account for` -> `reconcile`, `attribute`, or `conserve` depending whether the task balances surfaces, assigns causes/owners, or proves nothing appeared/disappeared without a transition.

## Coding and review language

- `works` -> `passes the targeted check`, `preserves the contract`, `closes the gate`, `satisfies the invariant`, or `moves the system state`.
- `safe` -> `fail-closed`, `bounded`, `reversible`, `invariant-preserving`, `permission-checked`, `witness-backed`, or `no broader blast radius`.
- `test it` -> `verify the changed path`, `reproduce the failure`, `exercise the invariant`, `run the closure gate`, or `prove movement`.
- `fix this` -> `remediate the material finding`, `close the invariant break`, `apply the narrowest sufficient change`, or `actuate the selected lever`.
- `review this` -> `adjudicate the claim`, `stress the changeset`, `audit invariants`, `verify readiness`, or `test the strongest countercase`.
- `simplify` -> `factor`, `winnow`, `quotient`, `ablate`, `normalize`, or `reduce surface` when that is the real operation.
- `delete code` -> `ablate`, `decommission`, `collapse`, `privatize`, `canonicalize`, or `remove a vestigial surface` depending on proof and contract.

## Precedent and policy language

- `learn from the past` -> `recover and adjudicate precedent` when prior cases should change the route.
- `use previous experience` -> `apply binding or persuasive precedent after checking distinguishing facts and supersession`.
- `set a precedent` -> `establish a nomothetic rule` when the decision should govern future cases.
- `precedent setter` -> `Nomothete` when the user explicitly asks for a persona; use `nomothetic` for the operating mode.
- `creates the rule` -> `constitutes the governing rule` when the decision changes structure rather than merely applying policy.

## Simulation and modeling language

- `simulate` -> `emulate`, `counterfactually project`, `model dynamically`, or `use a surrogate` depending on fidelity and purpose.
- `model what happens` -> `build a dynamical model with state, transitions, delays, and observations` when history or ordering matters.
- `what if` -> `counterfactual intervention` when changed and held-constant assumptions should be explicit.
- `realistic simulation` -> `fidelity-bounded emulation` when validated and unsupported regions must be named.
- `digital stand-in` -> `surrogate` when the model substitutes for an expensive, unavailable, or dangerous real system.

## Evaluation and judgment language

- `evaluate` -> `adjudicate`, `score`, `validate`, `compare`, or `rank` depending whether a disposition, metric, proof, alternative comparison, or ordering is required.
- `judge` -> `issue a criteria-backed ruling` when explicit standards and dispositions matter.
- `grader` / `judge persona` -> `Arbiter` when the user explicitly asks for a persona; use `adjudicative` for the operating mode.
- `what matters most` -> `identify the dispositive factor` when one fact, rule, or test determines the outcome.
- `be objective` -> `declare criteria, weight evidence and counterevidence, and calibrate confidence`.

## Doctrine / mode language

- `be rigorous` -> `reject unwitnessed claims and preserve named invariants`.
- `be careful` -> `label uncertainty, preserve obligations, and check the failure surface`.
- `think deeply` -> `derive the governing invariant and test the strongest countercase`.
- `take action` -> `actuate the lever and prove the system moved`.
- `start over` -> `rebaseline to the current authoritative state and invalidate stale receipts`.
- `systems thinking` -> `map cybernetic feedback loops, control points, signals, delays, and second-order effects`.
- `extract knowledge` -> `build a forensic provenance map and triangulate contradictions`.
- `learn from prior work` -> `build a Precedent Ledger and apply only current, non-superseded precedent with an action delta`.
- `make a simulator` -> `build a fidelity-bounded emulation with an Observation Contract`.
- `grade it` -> `adjudicate it against declared criteria and issue a disposition`.
- `use better words` -> `choose doctrine words that change procedure, not tone`.

## Guardrails

Do not replace if:

- the sharper word overstates certainty;
- the original intentionally stays broad;
- the domain has a canonical term;
- the substitution changes agency or obligation;
- the phrase is code, an identifier, a flag, a path, a schema field, or machine-consumed syntax;
- the new word would activate a workflow or proof obligation the task does not support.