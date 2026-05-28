# Gate Fresh-Eyes Check

Before returning `PLAN_ALLOWED`, reread the handoff sentence and required fields as if trying to prove planning would still have to discover the objective.

Ask:
- Can the work still be interpreted in two materially different ways?
- Are scope, non-goals, primary invariant, proof bar, or rollback/abort posture vague?
- Is any implementation architecture choice being delegated to `$plan` without a locked decision or safe default?
- Are open questions missing owner, default action, or consequence?
- Would two competent planners produce materially different plans from this packet?

If any answer is yes, set `PLAN_ALLOWED: false` or record the exact default/deferral that makes planning safe. If no material issue is found, report `fresh_eyes_check: pass`.
