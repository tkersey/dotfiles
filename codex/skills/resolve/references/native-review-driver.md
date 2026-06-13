# Native Fallback Review Driver

Native review is fallback-only after recorded CAS preflight/failure or explicit user request.

Base discovery order:

1. associated PR base branch;
2. remote default branch from `origin/HEAD`;
3. `origin/main` or `origin/master`;
4. local `main` or `master` as last resort.

Resolve selected base to merge-base SHA and pin it for the streak.
