# Testing playbook

Prefer the repo's existing test stack.

Proof signals:

- compile/typecheck;
- targeted unit test;
- table-driven fixtures;
- invalid fixture rejection;
- round-trip encode/decode;
- old/new parity;
- differential test;
- exhaustive handling check;
- observation coherence;
- projection/lift realization;
- explicit IR interpreter equivalence.

Never add new property-testing or effect libraries without explicit approval.
