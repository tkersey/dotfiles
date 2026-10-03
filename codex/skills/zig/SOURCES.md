# Source anchors

## Official sources

- Zig 0.17.0 language reference: https://ziglang.org/documentation/0.17.0/
- Zig 0.17.0 release notes: https://ziglang.org/download/0.17.0/release-notes.html
- Zig download/release index: https://ziglang.org/download/index.json
- Zig build system guide (check its examples against the selected release): https://ziglang.org/learn/build-system/
- LLVM LTO design: https://llvm.org/docs/LinkTimeOptimization.html
- OpenAI, Rethinking skills and prompts for GPT-6 Astra (2026-09-11): https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra
- Codex skills documentation: https://developers.openai.com/codex/skills

The 0.17 release notes own the migration delta; the versioned language reference,
installed help and matching stdlib source own exact signatures and behavior.
A release index entry is not compiler execution evidence. An older repository pin
still governs its project unless an upgrade is requested. Do not equate a minimum
supported version, a development snapshot and an exact release pin.

Relevant areas include allocation/ownership, pointer/sentinel/alignment contracts,
Illegal Behavior/runtime safety, errors, atomics, layout, build caches, targets,
linkers/LTO, comptime/reflection, Smith fuzzing, explicit I/O, C translation and
packages. Retain repository-compatible Zlinter/zprof and formatter guidance; exact
compatible versions remain repository-pinned rather than assumed from Zig alone.

## Historical operational evidence

The 2026-06-20 local `$seq` report identified recurring signatures involving claim
binding, lifetime escape, fallible mutation, verifier completeness, repository
closure, evidence freshness and cache/sandbox mismatches. It established recurring
signatures and outcomes, not causal influence from `$zig`.

These remain non-exhaustive semantic lenses. Witness construction, owner-first
invariants, small hazardous cores, independent reference paths and repository-
specific validation remain useful; their presence in prose is not correctness or
model-efficacy evidence.

## This revision's rationale

Version 3.1 preserves the adaptive v3 operating contract. It updates executable
reflection examples, version/mode selection and migration guidance, then adds
semantic regression examples and discovers all reference test files automatically.
Release-specific detail stays behind the reference map; ordinary work does not
acquire a mandatory migration checklist or additional orchestration stages.

Helper regressions test tools and failure classification. Real Zig example checks
test only instantiated language behavior; cross-compilation is not execution.
The build-cost driver does not measure runtime, peak memory, warm configuration
hits or persistent incremental compilation. Matched behavioral probes remain the
way to investigate skill efficacy; neither prose shortening nor compiler success
establishes a model-quality improvement. Report actual execution in the PR.
