# Testing playbook

Use the fastest credible proof signal:

- compile/typecheck for ADT exhaustiveness;
- targeted unit tests for constructors;
- invalid fixture rejection;
- parity tests against old behavior;
- differential tests during migration;
- observation coherence tests;
- projection realization tests;
- free-builder projection tests;
- negative witness tests.

For Track D, include a falsifier: a case where the artifact catches a bug the old shape could miss.
