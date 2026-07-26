# Spec Fresh-Eyes Pass

Before Execution Handoff, reread the final spec against the original authoritative
brief, Evidence Brief, Gate Result, `spec_decision_packet`, and Architectonic Thread.

Look for:

- objective drift;
- missing non-goals;
- smuggled implementation choices;
- consequential architecture hidden in implementation prose rather than a named
  seam;
- file-shaped factorization or architecture theater;
- abstraction proliferation, duplicated owners, or shadow truth;
- validators, caches, correlation, compatibility branches, or bypasses that
  reconstruct information the selected representation should retain;
- an implementation sequence that realizes a quotiented, ablated, normalized, or
  superseded factor;
- migration or rollback that does not preserve required observations;
- missing architectural law, falsifier, residual obligation, or invalidator;
- a failed or missing specification square where process and architecture change
  both compose;
- vague proof commands;
- scaffold-only proof where runtime proof is required;
- rollback or abort gaps;
- requirements without owner, enforcement, and proof traceability;
- plan-shaped execution waves leaking into the spec;
- stale defaults or assumptions that should be locked, deferred, or returned to
  `$grill-me`;
- missing No-Grill Justification when `grill_rounds: 0`;
- unaccounted subagents;
- mutation allowed before challenge and execution handoff.

Rules:

- If any material issue is found, revise only the affected sections before handoff.
- An architectonic change also regenerates every implementation-spec section derived
  from the changed seam.
- If the pass changes the spec, record changed sections and why the revision
  preserves the authoritative brief.
- If no material issue is found, emit `fresh_eyes_delta: none`.
