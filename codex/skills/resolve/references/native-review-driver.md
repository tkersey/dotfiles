# Native Fallback Review Driver

Native Codex review is fallback-only.

Do not invoke native review until CAS preflight/failure or explicit user request is recorded.

## Base discovery order

1. Fetch remote refs.
2. If current branch has an associated PR, use that PR's base branch.
3. Otherwise use remote default branch from `origin/HEAD`.
4. Otherwise use `origin/main` or `origin/master` if present.
5. Otherwise use local `main` or `master` only as last resort.
6. Resolve selected base to merge-base SHA with `HEAD`.
7. Pin that merge-base SHA for the clean-review streak.

## Driver requirements

The native fallback driver must capture:

- current branch;
- working-tree status;
- selected base ref;
- merge-base SHA;
- current `HEAD` SHA;
- applicable language/tool skill guidance;
- exact native review command;
- sandbox mode;
- raw output path;
- exit status;
- parsed findings/comments.

A native review is clean only if it completed, parsed reliably, and produced zero findings/comments/notes against the pinned base/head.

## Sandbox note

When using `codex --yolo review`, record sandbox mode as `danger-full-access/yolo` and explain that trusted local `$resolve` review subprocesses may need repository validation probes and writable caches. Do not hide this in the final ledger.
