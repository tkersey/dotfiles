# Rust/Swift examples

Keep examples idiomatic for Rust/Swift.

Universalist examples should show:

- one smell;
- one seam;
- one smallest honest construction;
- one proof signal.

Track D examples should show a canonical boundary artifact only when it changes code shape:

- AST plus interpreter;
- observation enum plus runner;
- generation path plus lowerer;
- realizer plus projection;
- obligation IR plus satisfier;
- first-order case plus apply.

For lift-shaped cases, name the projection `P` and add a test that projection of the realizer satisfies required behavior.
