# Ablation Activation

Ablation must be visible when review adjudication could otherwise turn a valid
comment into additive code.

## Triggers

Emit an `Ablation Activation Receipt` when any comment or selected action involves:

- adding a helper, wrapper, adapter, fallback, flag, knob, state variant, public symbol, branch, compatibility path, or abstraction;
- preserving a dominated, subsumed, vestigial, uninhabited, pass-through, duplicate, non-canonical, or temporary-scaffold surface;
- multiple local comments that might share one governing invariant;
- routing to `$fixed-point-driver` for closure, repeated review/fix loops, or PR resolution.

## Receipts

A valid receipt is one of:

- custom `review_ablative_surface_authority` packet;
- root-equivalent ablative packet with the same fields;
- explicit `not-required` receipt proving no mutation-capable or keep-surface decision exists.

`address` without this receipt is not implementation permission.
