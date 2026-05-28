# Closure Fresh-Eyes Gate

Before assigning readiness, reread the handoff packet, verification ledger, negative evidence gate, closure gate ledger, residual risks, and claimed proof as if trying to falsify the closure verdict.

Ask:
- Did any passing check fail to prove the actual readiness claim?
- Is any material soundness, invariant, foot-gun, complexity, or negative-evidence gate still open?
- Did the artifact state change after evidence was gathered?
- Is any specialist receipt being treated as proof instead of a routing signal?
- Would it be embarrassing to call this ready if only the last changed file, narrowest proof, or active exclusion were inspected?

Rules:
- If the gate changes readiness, update Closure Gate Ledger, Residual Risks, Fixed-Point Test, Readiness, Reopen Trigger, and Closure Bottom Line.
- If it finds no material delta, record `fresh_eyes_delta: none` in Closure Gate Ledger or Residual Risks.
- Do not turn closure fresh-eyes into broad redesign; reopen with the narrowest next move when a material gap remains.
