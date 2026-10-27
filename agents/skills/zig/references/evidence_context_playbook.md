# Validation evidence, provenance, and reuse

This reference owns evidence freshness across the Zig playbooks. A mention of
"proof epoch", "final context", or a reproduction record elsewhere means this
input-sensitive contract, not a requirement for a new packet or repeated test.

## What a result establishes

Distinguish source-level reasoning, compiler-enforced properties, executed test
cases, fuzz exploration, measurements, and recommendations not yet executed.
Tests and fuzzing can falsify claims and supply empirical evidence; neither is a
universal proof of parser totality or semantic completeness.

Preserve enough context to reproduce consequential results: command and cwd,
relevant source content, compiler/version, target/CPU, optimize mode/options,
dependencies/forks, generated inputs, environment/caches/sandbox when material,
inputs/seeds and outcome. Reuse an enclosing workflow's evidence rather than
creating a parallel Zig store or final report.

## Reuse and invalidation

Reuse validation only when its relevant inputs and assumptions remain established.
Changed source semantics, a relevant generated artifact, dependency, toolchain,
backend, target, option, input, or execution assumption invalidates affected
results. Unknown relevance calls for conservative rerunning, not invented certainty.
Repository-required checks and active workflow review/reset rules still apply.

A commit, message amendment, unchanged-content rebase, or worktree relocation can
change provenance without changing a particular check's inputs. Update provenance;
do not automatically rerun expensive checks. Verify content and assumptions first:
builds embedding the commit ID, path-sensitive generators, dependency overrides,
and different cache/sandbox permissions can make those events relevant inputs.
Likewise, `zig fmt` may change the bytes relevant to an artifact check even when
runtime behavior is unchanged. Decide per check, not from the operation's name.

Content identity alone is insufficient if environment or dependencies changed.
A dirty working tree is not a universal blocker: isolate the subject and preserve
concurrent user edits. A clean branch is not a reviewed diff without a baseline.

## Choosing checks

Use the repository harness where modules/options/dependencies matter. A focused
check diagnoses a narrow uncertainty; aggregate checks establish their advertised
coverage, not every possible property. Add modes/targets for optimizer, ABI, endian,
pointer-width, layout, or runtime-safety assumptions, not by rote.

`zig ast-check` is not semantic compilation. Invoke it per file when useful,
for example `find ... -print0 | xargs -0 -n 1 zig ast-check`; prefer the repository's
file set and handle an empty set in its harness. Avoid sweeping dependency trees.
`zig fmt --check` establishes formatting, not behavior.

## Environment diagnostics

Keep the actual command, diagnostic, and failing resource. A `PermissionDenied`
during validation is not itself a code defect or proof of a global-cache problem.
Retry the same command with a writable global cache only when cache access is the
identified failure. Do not bypass repository filesystem/security requirements or
silently change the test's semantics to obtain a green result.

When a required lane cannot run, report its reason and continue independent
in-scope work. Use the receiving workflow's labels; existing consumers may use:
`VERSION_MISMATCH`, `LINT_UNAVAILABLE`, `TEST_UNAVAILABLE`, `FUZZ_UNAVAILABLE`,
`PROFILE_UNAVAILABLE`, `COMPTIME_PROOF_UNAVAILABLE`, `HAZARD_AUDIT_UNAVAILABLE`,
`SAFETY_PROOF_UNAVAILABLE`, `REPO_CLOSURE_UNAVAILABLE`, `TIGER_STYLE_UNAVAILABLE`,
`CACHE_REVIEW_SANDBOX_PERMISSION_DENIED`, or `UNMEASURED`. Do not emit every label
or fill an unavailable-lanes form when it adds no information.

## Completion

Finish authorized implementation and required validation; fix introduced failures
and rerun affected checks. A report template is not the deliverable. Report exact
commands/outcomes, genuine unavailable lanes and residual risk once, using the
receiving workflow's format. Never imply an unexecuted check or benchmark passed.
