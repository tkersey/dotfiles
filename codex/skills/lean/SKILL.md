---
name: lean
description: "Use for deliberate Lean 4 work: proof repair, theorem development, verified programs, model/specification design, external-code models, state-machine or trace invariants, termination proofs, Std/mathlib theorem discovery, Lake/toolchain diagnosis, and high-assurance trust audits. Do not use for Lean process management, other proof assistants, or informal pseudocode unless translation to Lean 4 is requested."
---
# Lean

## Mission

Produce a checked Lean artifact or an exact project-aware diagnostic. Prose is
secondary and must not claim more than Lean checked.

## Always-live contract

1. The repository's `lean-toolchain`, Lake files, lock state, imports, and nearby
   style are authoritative.
2. Identify the artifact under proof, exact theorem claim, trusted assumptions,
   and what remains outside Lean.
3. Reproduce the smallest real failure before changing the proof.
4. Confirm theorem names, imports, syntax, and tactic availability locally.
5. Do not silently weaken a false or mismatched theorem; give the counterexample
   or minimal corrected statement.
6. Leave no hidden `sorry`, `admit`, new `axiom`, unsolved goal, or intentionally
   broken declaration unless the user explicitly requests a sketch.
7. Surface trust-expanding features and external boundaries.
8. Check the changed artifact with the smallest project-aware command, then run
   the required broader build.

## Common proof-repair path

1. Inspect `lean-toolchain`, Lake configuration, target imports, namespace, and
   nearby lemmas.
2. Run the smallest failing `lake env lean` or `lake build +Module` command.
3. Use `#check`, `#print`, and local source search to interrogate the
   environment.
4. Normalize first with `rfl`, `simp`, `simpa`, or explicit structure.
5. Match induction to data or recursion; generalize accumulators or state when
   the public theorem is too weak.
6. Use domain tactics only when imported and after simplifying the goal.
7. Replace fragile broad automation with named helper lemmas when the result
   supports a correctness claim.
8. Re-run the project-aware command and report the exact proof boundary.

## Route selection

Choose one route:

```text
proof-repair
verified-lean-program
external-code-model
stateful-or-trace-verification
termination-repair
build-toolchain-diagnosis
trust-audit
exploratory-learning
```

Simple proof repair should not load every specialist route.

## Conditional disclosure

The complete pre-split contract is preserved byte-for-byte in
[FULL_CONTRACT.md](FULL_CONTRACT.md). Do not load it for routine proof repair.

Load it only for:

- spec/implementation/refinement architecture for verified programs;
- external implementation correspondence and adapter boundaries;
- state-machine, monadic, protocol, or trace modeling;
- totality, well-founded recursion, or explicit fuel;
- theorem-discovery and simplifier discipline beyond the common path;
- trust audits, `#print axioms`, native evaluation, unsafe/runtime, generated
  code, IO, FFI, or compiler boundaries;
- Lake cache, dependency, namespace, or toolchain diagnostics;
- an unported edge route.

Its frontmatter is archived source, not a second skill definition.

## Reporting boundary

Say exactly what Lean proved, under which toolchain and assumptions, and what it
did not prove. Never write that external software is proved correct unless a
checked refinement or semantics link actually establishes that claim.
