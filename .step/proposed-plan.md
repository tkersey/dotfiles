# Plan: Add Codex Hook-Aware Control to `$cas`

## Summary

Implement hook-aware `$cas` by adding `--hooks inherit|off|require-observed` across CAS lanes, passing hook policy into `codex app-server`, capturing `hook/started` and `hook/completed`, summarizing outcomes in JSON, and classifying hook failures with explicit `failureCode` values. Codex remains the only hook executor; CAS controls, observes, classifies, and reports.

## Implementation Brief

- step=Add shared hook policy model; owner=engineering; success_criteria=all CAS lane CLIs parse `--hooks`, reject invalid modes, and preserve default `inherit`.
- step=Add Codex launch/config wiring; owner=engineering; success_criteria=stdio and managed websocket app-server paths accept hook policy, with `off` passing `--disable codex_hooks`.
- step=Add support preflight and classifier; owner=engineering; success_criteria=`off`/`require-observed` fail with `hooks_unsupported` on unsupported runtimes and classify hook statuses deterministically.
- step=Add hook accumulator/output; owner=engineering; success_criteria=JSON includes compact `hookSummary` and local `hookLogPath`, while raw records stay in NDJSON artifacts.
- step=Wire all CAS lanes; owner=engineering; success_criteria=smoke, instance, review, and conformance lanes expose consistent policy and verdict behavior.
- step=Validate locally; owner=engineering; success_criteria=`zig build test-cas`, `zig build build-cas -Doptimize=ReleaseFast`, integration smoke, and `$cas` skill quick-validate pass.
- step=Release and publish; owner=operations; success_criteria=version bump, tag, release workflow assets, tap formula SHA update, `brew audit`, `brew upgrade`, `brew test`, and installed `cas --version`/help proofs pass.

## Locked Decisions

- `--hooks inherit` is the default and preserves existing behavior.
- `--hooks off` is best-effort disable through Codex runtime configuration; observed bad hook status still blocks the CAS verdict.
- `--hooks require-observed` fails with `hook_not_observed` when no hook notifications appear.
- Bad hook statuses produce blocking failure codes with precedence `blocked > failed > stopped`.
- Raw hook notifications remain in local CAS artifact logs; JSON responses include summaries and log paths only.
- Unsupported hook control for `off` or `require-observed` fails with `hooks_unsupported`; `inherit` remains supported.
