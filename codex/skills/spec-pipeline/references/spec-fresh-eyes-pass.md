# Spec Fresh-Eyes Pass

Before Execution Handoff, reread the final spec against the original authoritative brief, Evidence Brief, Gate Result, and `spec_decision_packet`.

Look for:
- objective drift;
- missing non-goals;
- smuggled implementation choices;
- vague proof commands;
- scaffold-only proof where runtime proof is required;
- rollback or abort gaps;
- requirements without tests;
- plan-shaped execution waves leaking into the spec;
- stale defaults or assumptions that should be locked, deferred, or returned to `$grill-me`.

Rules:
- If any material issue is found, revise only the affected sections and rerun Spec Lint before handoff.
- If the pass changes the spec, record changed sections and why the revision preserves the authoritative brief.
- If no material issue is found, emit `fresh_eyes_delta: none`.
