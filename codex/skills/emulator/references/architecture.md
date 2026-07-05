# Emulator Architecture

`$emulator` is the runtime companion to `$ghost`.

```text
$grill-me  ->  emulator_subject_packet / ESP-v1
$ghost     ->  Ghost scenario package
$emulator  ->  synthetic implementations + emulator_execution_report / EER-v1
```

## Responsibility split

| Skill | Owns | Does not own |
|---|---|---|
| `$grill-me` | Material user judgments, scope, proof bar, and failure priorities | Specs, implementation, repository analysis beyond discoverable context |
| `$ghost` | Portable behavior contract, scenario tests, verification/provenance | Executable emulator runtime |
| `$emulator` | Executable synthetic implementations, runs, mutation, traces, divergence reports | Deciding what matters, writing Ghost contracts, editing skills |
| `$tune` | Optional downstream skill-change diagnosis | Core emulator lifecycle |
| `$refine` | Optional downstream authorized edits | Core emulator lifecycle |

## Canonical flow

1. `$grill-me` is used only when the subject is materially under-specified.
2. `$ghost` converts the chosen subject into a portable scenario-layout contract.
3. `$emulator` reads that contract and generates one or more executable implementations.
4. `$emulator` runs, mutates, and compares those implementations.
5. `$emulator` emits EER-v1 and concrete artifacts.
6. Optional consumers use the report: human review, CI, eval generation, Ghost repair, or skill tuning.

## Non-core downstream route

Use this route only when explicitly requested:

```text
EER-v1 -> $tune -> $refine
```

Emulator evidence is behavioral evidence. It becomes skill-improvement evidence only after the user asks to improve a skill from it and the existing tuning/refinement gates accept the handoff.
