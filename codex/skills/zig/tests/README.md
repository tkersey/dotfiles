# Zig skill regression checks

Requirements: Python 3.11+, Git and `uv`; Zig 0.16.0 for compiler checks. The helper
tests use disposable temporary directories and stub Zig/process discovery. They
have no production access. Run them, fix introduced failures, and rerun affected
checks without a new confirmation for each fixture operation.

From this skill directory:

```bash
uv run python3 -m unittest discover -s tests -p 'test_*.py'
uv run python3 tests/check_zig_examples.py --zig zig --optimize Debug
uv run python3 tests/check_zig_examples.py --zig zig --optimize ReleaseSafe
```

The compiler runner checks the three selected reference files (comptime patterns,
policy traversal and scaling) plus forced diagnostic-specific negative fixtures.
Other reference snippets remain available; this runner does not claim to validate
every generic instantiation or every example in the library. Missing/wrong-version
compilers return unavailable (exit 2), test/diagnostic failures return 1, and only
completed checks return 0. Tests using a fake compiler verify runner classification,
not Zig correctness. Report those two kinds of evidence separately.

The helper tests exercise dry-run and destructive success, dependency/worktree
preservation, global-path identity, age/descendant behavior, symlink/tracked-file
protection, process-check failure, exact unusual filenames, renames, clean-branch
review scope, partial scan coverage and meaningful status codes. Source-contract
checks cover referential integrity and the absence of required routing artifacts;
they do not grade prose quality or model intelligence.

Optional build-cost experiment:

```bash
uv run python3 tests/measure_comptime.py --zig zig --sizes 8 32 128 --samples 3
```

It records compile wall time and object bytes for exported runtime-input kernels,
with fresh per-sample compiler caches and rotated strategy order. It does not
measure runtime latency or peak compiler memory. See the comptime playbook for
interpretation and the behavioral probes for matched model evaluations. Neither
experiment is a required ordinary-use stage or a substitute for functional checks.
