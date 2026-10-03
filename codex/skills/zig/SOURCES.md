# Source anchors

## Official sources

- Zig 0.17.0 language reference: https://ziglang.org/documentation/0.17.0/
- Zig 0.17.0 release notes: https://ziglang.org/download/0.17.0/release-notes.html
- Zig download/release index: https://ziglang.org/download/index.json
- Zig build system guide (match examples to the selected release): https://ziglang.org/learn/build-system/
- LLVM LTO design: https://llvm.org/docs/LinkTimeOptimization.html
- OpenAI, Rethinking skills and prompts for GPT-6 Astra (2026-09-11): https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra
- Codex skills documentation: https://developers.openai.com/codex/skills

The 0.17 release notes own the migration delta; the versioned language reference,
installed help and matching stdlib source own exact signatures and behavior.
A release index entry is not compiler execution evidence. A repository's selected
pin still governs unless an upgrade is requested. Distinguish minimum support,
development snapshots and exact releases.

Relevant areas include ownership, pointer/sentinel/alignment contracts, Illegal
Behavior/runtime safety, errors, atomics, layout, build caches, targets/linkers/LTO,
reflection, fuzzing, explicit I/O and packages. Zlinter and zprof are independently
versioned; retain compatible repository pins rather than installing historical
0.16 recipes or assuming a compiler upgrade proves third-party compatibility.

## Historical operational evidence

The 2026-06-20 local `$seq` report identified recurring signatures involving claim
binding, lifetime escape, fallible mutation, verifier completeness, repository
closure, evidence freshness and cache/sandbox mismatches. It established recurring
signatures and outcomes, not causal influence from `$zig`.

These remain non-exhaustive semantic lenses. Witness construction, owner-first
invariants, small hazardous cores, independent reference paths and repository-
specific validation remain useful; their presence in prose is not correctness or
model-efficacy evidence.

## Revision rationale and evidence boundaries

Version 3.1 updated executable reflection examples, migration guidance and
version/mode selection, expanded example discovery and protected custom package
locations. Version 3.2 carries the adaptive operating contract through hazard,
boundary, concurrency, I/O, testing, linting and profiling references. It removes
compulsory classification/reporting sequences and lock substitution based on an
unfilled template, while retaining technical obligations and detailed audit support
when requested. It fixes documented runner arguments and distinguishes skill
maintenance from validation of the user's actual project.

The Astra article motivates contextual reference loading, concise activation,
reconsidering inherited procedures and preserving authorized completion. It does
not establish that these edits improve model outcomes. The existing behavioral
probes now separate technical corrections from instruction-shaping experiments;
keep facts, examples and deterministic tools matched when testing that hypothesis.

Helper regressions test tools, documented CLI arguments and failure classification.
Real Zig example checks cover instantiated behavior; cross-compilation is not
execution. The build-cost driver does not measure runtime, peak memory, warm
configuration hits or persistent incremental compilation. Source comparisons and
compiler conformance do not measure Astra quality. Report actual execution and
unmeasured claims separately in the PR.
