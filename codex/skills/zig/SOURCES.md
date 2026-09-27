# Source anchors

## Official sources

- Zig 0.16.0 language reference: https://ziglang.org/documentation/0.16.0/
- Zig 0.16.0 release notes: https://ziglang.org/download/0.16.0/release-notes.html
- Zig build system guide: https://ziglang.org/learn/build-system/
- Zig download/release index: https://ziglang.org/download/index.json
- LLVM LTO design: https://llvm.org/docs/LinkTimeOptimization.html
- OpenAI, Rethinking skills and prompts for GPT-6 Astra (2026-09-11): https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra
- Codex skills documentation: https://developers.openai.com/codex/skills

Relevant Zig areas include allocators/ownership, pointer/sentinel/alignment
contracts, Illegal Behavior/runtime safety, errors, atomics, ABI/layout, build
modes, targets/linkers/LTO, comptime/reflection, Smith fuzzing, explicit I/O,
process initialization, C translation and packages. Check the installed toolchain
and repository pins rather than treating these links as version-independent recipes.

Retain repository-compatible Zlinter/zprof references and Matklad's Zig formatter
guidance in the relevant playbooks. Exact compatible versions remain repo-pinned.

## Historical operational evidence

The 2026-06-20 local `$seq` report identified recurring signatures involving claim
binding, lifetime escape, fallible mutation, verifier completeness, repository
closure, evidence freshness and cache/sandbox mismatches. It established recurring
signatures and outcomes, not causal influence from `$zig`.

These distinctions remain available as non-exhaustive semantic lenses. Witness
construction, owner-first invariants, small hazardous cores, independent reference
paths and repository-specific validation remain useful engineering approaches;
their presence in prose does not itself prove correctness or model effectiveness.

## This revision's rationale

The Astra article motivates concise discovery, progressive disclosure, revisiting
prescriptive recipes and stop conditions, and clear completion. The revision
separates that operating contract from Zig expertise; it does not assert that a
shorter prompt is necessarily better. Use the matched behavioral probes for that
question. Local helper regressions and compiler/example tests establish only their
specific advertised coverage. Report actual execution separately in the PR.
