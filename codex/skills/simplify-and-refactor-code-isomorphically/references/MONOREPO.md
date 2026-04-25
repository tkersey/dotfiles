# Monorepo Refactors — cross-package simplification

> Monorepos (Turborepo, Nx, pnpm workspaces, Cargo workspaces, Go multi-module, Bazel, Buck2) multiply the skill's value and its risks. This file is the monorepo-specific playbook.

## Contents

1. [The monorepo isomorphism axes](#the-monorepo-isomorphism-axes)
2. [Cross-package duplication detection](#cross-package-duplication-detection)
3. [Shared-utility extraction patterns](#shared-utility-extraction-patterns)
4. [Version pinning invariants](#version-pinning-invariants)
5. [CI matrix implications](#ci-matrix-implications)
6. [The 5 canonical monorepo refactor shapes](#the-5-canonical-monorepo-refactor-shapes)
7. [Per-tooling specifics](#per-tooling-specifics)
8. [Splitting a monorepo (and its reverse)](#splitting-a-monorepo-and-its-reverse)

---

## The monorepo isomorphism axes

Beyond the general axes, monorepo-specific:

| Axis | What changes if you break it |
|------|------------------------------|
| **Package boundary** | internal API becomes public API; semver obligations apply |
| **Shared dep resolution** | two packages pinning different versions causes bundle duplication |
| **Task graph (CI)** | parallelization changes; cache hit rates move |
| **Affected set** | Nx/Turbo "affected" algorithms determine what runs on PR |
| **Build cache keys** | a util-file touch invalidates every downstream package |
| **Release cadence** | merged releases vs. independent per-package |
| **Import depth** | inter-package imports create new coupling |
| **`peerDependencies`** | changes to a shared package's peer deps ripple |
| **Workspace protocols** (`workspace:*`, `workspace:^`) | version resolution at publish time |

---

## Cross-package duplication detection

Single-package `jscpd` / `similarity-*` don't see across package boundaries. Multi-package detection:

### TS / JS monorepos

```bash
# Turborepo / pnpm workspace
for pkg in packages/*/src apps/*/src; do
  [ -d "$pkg" ] || continue
  echo "=== $pkg ==="
done

# Cross-package jscpd
npx jscpd --min-tokens 50 packages/*/src apps/*/src

# Cross-package similarity-ts with shared output
similarity-ts -p 80 packages/ apps/ > cross_pkg_similarity.txt
```

### Rust workspaces

```bash
# Cross-crate similarity
for crate in crates/*/src; do
  cat "$crate"/**/*.rs 2>/dev/null
done > /tmp/all_rust.txt
# Then use similarity-rs on the combined or individual per-crate

similarity-rs -p 80 crates/*/src/
```

### Go multi-module

```bash
# Each module independent; dupl across modules:
find . -name go.mod -exec dirname {} \; | while read mod; do
  dupl -threshold 50 "$mod/..."
done
```

### The findings

Cross-package duplication is typically:
- Utility functions reimplemented in each package (date formatting, error wrapping, type converters).
- Sibling components across apps that should share a UI package.
- Per-package logging / tracing boilerplate.
- Per-package test fixtures.

These are usually **high-score candidates** because:
- Impact: N packages × same helper = large LOC saved.
- Confidence: utility functions rarely have divergent invariants.
- Risk: moderate (cross-package refactor).

---

## Shared-utility extraction patterns

### The 3-level monorepo structure (canonical)

```
packages/
├── core/           # no deps on siblings; pure logic
├── shared-utils/   # depends on core only
├── ui/             # depends on core + shared-utils
├── db/             # depends on core + shared-utils
└── ...

apps/
├── web/            # depends on packages/*
├── mobile/         # depends on packages/*
└── api/            # depends on packages/*
```

Refactoring duplication follows the arrow downward: extract to the lowest common dependency.

### Pattern: extracting a util to `shared-utils`

```bash
# Before: apps/web/src/format/date.ts AND apps/api/src/date.ts — same function
# After:  packages/shared-utils/src/date.ts, with apps/web + apps/api importing

# Steps:
# 1. Create packages/shared-utils/src/date.ts with the canonical implementation
# 2. Add to packages/shared-utils/src/index.ts exports
# 3. Update each app's import:
#    apps/web/src/format/date.ts        →  import { formatDate } from '@org/shared-utils'
#    apps/api/src/date.ts               →  import { formatDate } from '@org/shared-utils'
# 4. Delete the duplicates (after safety gauntlet + user approval)
# 5. Bump @org/shared-utils version per workspace protocol
```

**Isomorphism axes:**
- Import path changes everywhere → every caller.
- Tree-shaking: if `shared-utils` exports many functions, apps that import just `formatDate` may pull more code unless `sideEffects: false` is set in package.json.
- Version: workspace:^ pinning means next publish is coordinated.

### Pattern: promoting inter-app code to a package

```typescript
// apps/web/src/hooks/useCart.ts (5 screens use it)
// apps/mobile/src/hooks/useCart.ts (4 screens use it)
// → packages/hooks/src/useCart.ts
```

Rule of 3 applies across the monorepo: 2 apps using the same hook is coincidence; 3+ is a package.

### Anti-pattern: `common` / `shared` as a dumping ground

Same as VIBE-CODED-PATHOLOGIES.md P4, amplified. Don't create `packages/common` that imports from everywhere and is imported by everything. That's a circular-dep timebomb.

**Better:** packages named by domain (`time`, `currency`, `url`, `auth`). Each is narrow.

---

## Version pinning invariants

### Pinning conventions

| Form | Meaning | Use for |
|------|---------|---------|
| `"zod": "4.5.2"` | exact | production deps in apps |
| `"zod": "^4.5.2"` | compatible (4.x.x) | libraries that want updates |
| `"zod": "workspace:*"` | internal workspace | inter-package refs |
| `"zod": "workspace:^"` | workspace with range | inter-package refs that need publishing |
| `"zod": "*"` | anything | **never — P37** |

### Refactor: sync versions across the monorepo

```bash
# Find pkgs with divergent zod versions
rg '"zod":\s*"[^"]*"' --type json packages/ apps/
# → probably packages/api uses "^4.5.2" while apps/web uses "^4.2.1"
```

Align. One commit per package family (e.g., "bump zod to 4.5.2 in all packages"). One lever.

### The duplicate-bundle-size signal

If the production bundle has two copies of `zod` (or `react`, or `lodash`), that's a version mismatch:

```bash
pnpm why zod
# shows which packages resolve to which versions
```

Fixing is a P37 cleanup — pin all to the same version.

---

## CI matrix implications

### Turborepo / Nx affected algorithms

Both compute "what changed" to decide what to rebuild/test. Refactoring a shared package invalidates every downstream package's cache.

**Implication for the skill:**
- A refactor in `packages/core` triggers a rebuild of every app.
- Budget accordingly: a Tier-1 extraction might run CI for 30 minutes.
- **Batch refactor commits touching `packages/core`** — one PR with 5 commits still triggers 5 full CI runs; consider squashing to one.

### Per-package release

If the monorepo uses per-package releases (changesets, rush):

- Refactor commits that don't change public API of a published package → patch bump (or no bump with `changesets`).
- Refactor commits that DO change public API → major bump; breaking.

**Isomorphism card addition for published packages:**
```markdown
### Publishing impact
- Which packages does this commit affect in terms of public API?
- Changeset type: patch / minor / major / none
- Breaking changes (list): —
```

---

## The 5 canonical monorepo refactor shapes

### M-1: Lift a duplicated utility

Already covered above. Canonical shape 1.

### M-2: Merge two drifted shared packages

Two packages (`utils-v1`, `utils-v2`) exist because someone started a migration and stopped. Merge them.

**Plan:**
1. Pick one (the newer / more-maintained) as canonical.
2. For each export in the other, evaluate: identical in canonical? If yes, point consumers at canonical. If different, pick one per symbol with the user.
3. Delete (with approval) the obsolete package.
4. Update every `package.json`.

This is Tier-3. Planning doc mandatory.

### M-3: Split an over-shared package

`packages/common` has 80 exports. 20 are used by one consumer each; 30 by two; 30 by many.

**Plan:**
1. For each export, find consumers.
2. For single-consumer exports: move into that consumer (or a narrow package they own).
3. For multi-consumer exports: promote to a more-focused package.
4. Shrink `common` to only the truly-common.

### M-4: Introduce a package for cross-cutting concerns

A concept (logging, auth, error handling) is duplicated or near-duplicated across apps/packages. Create a new package.

**Plan:**
1. Propose the package name + surface in a planning doc.
2. Create the package; implement the first canonical version.
3. Migrate one consumer; prove isomorphism.
4. Migrate subsequent consumers one per commit.
5. Remove legacy implementations (with approval) per safety gauntlet.

### M-5: Rationalize task graph

Nx/Turbo task configs accumulate. Example: `build:test` and `test:build` are the same thing; three different `lint` variants exist; `dev` and `serve` do the same thing.

This is a **refactor of config, not code**. Still apply the loop:
- Baseline: which targets actually run in CI? In local dev?
- Score: collapsing duplicate targets is Tier-1 if no semantics differ.
- Isomorphism: task graph equivalence — every scheduled task post-change equals pre-change.

---

## Per-tooling specifics

### Turborepo

`turbo.json` drives the task graph. Refactors:

- Consolidate `pipeline` entries (same `dependsOn` / `outputs`).
- Remove unused `globalDependencies`.
- Set `outputs` correctly — wrong outputs kill cache hit rate (a Tier-1 fix with massive CI-time savings).

### Nx

`nx.json` + per-project `project.json`. Refactors:

- Consolidate targets across projects via `targetDefaults`.
- Use `@nx/js:tsc` instead of per-project custom builds where possible.
- Rationalize `implicitDependencies`.

### pnpm workspace

`pnpm-workspace.yaml` + `package.json[workspaces]`. Refactors:

- Collapse shared devDeps into root (pnpm hoists by default; leaf-level devDeps are redundant).
- Use `pnpm catalog` (pnpm 9+) to pin shared dep versions once.

### Cargo workspace

`Cargo.toml [workspace]`. Refactors:

- Use `[workspace.dependencies]` to pin shared versions once.
- Use `[workspace.package]` for shared metadata (authors, license, rust-version).
- `cargo-hakari` can generate a workspace-hack crate to improve build times — itself a refactor candidate.

### Go multi-module

Each module has its own go.mod. Refactors:

- `go mod tidy` across all modules.
- Consolidate redundant replace directives.
- For shared code: either a published module or a git-subtree, depending on scale.

### Bazel / Buck2

Opposite tradeoffs from the others: rigid but fast, fine-grained deps, hermetic. Refactors:

- Consolidate `BUILD` rules that are identical.
- Use macros (not codegen) to reduce BUILD-file LOC.
- Audit `visibility` — overly-broad visibility is coupling.

---

## Splitting a monorepo (and its reverse)

### Split: monorepo → many repos

When: one package's team is drifting from the others; release cadence mismatch; legal/compliance separation.

**Tier-3, multi-week project.** Planning:

1. Identify the subtree to extract.
2. Use `git subtree` or `git filter-repo` to preserve history.
3. Create the new repo.
4. Leave a placeholder package in the monorepo that depends on the extracted package (published).
5. Migrate consumers over weeks; remove placeholder (with approval).

### Merge: multi-repo → monorepo

When: coupling was artificial; shared dependencies duplicate; release coordination is painful.

**Tier-3, multi-week project.** Planning:

1. Pick target monorepo structure.
2. `git subtree add` each source repo into the monorepo subdirectory.
3. Rewrite imports package-by-package.
4. Consolidate shared deps; align versions.
5. Sunset the old repos (with approval; "archive" not "delete").

Both directions are rare and high-risk. Not a weekly-pass activity. They belong in the monthly deep pass's Tier-3 planning.

---

## Integration with the skill's main loop

### Phase B in a monorepo

```bash
# Per-package dup scan
for pkg in packages/*/src apps/*/src; do
  ./scripts/dup_scan.sh "${pkg##*/}-pass" "$pkg"
done

# Cross-package dup scan
similarity-ts -p 80 packages/ apps/ > cross_pkg_similarity.txt
```

### Phase C in a monorepo

Score candidates with Monorepo multipliers:

- **Cross-package candidate:** LOC_saved is higher (N packages × shared helper).
- **Shared-package refactor:** Risk is higher (invalidates more caches).

### Per-package ledger

If refactoring multiple packages in one pass, ledger per package:

```
refactor/artifacts/<run-id>/
  ledger.md                  # overall
  packages/core/ledger.md    # per-package
  packages/ui/ledger.md
  apps/web/ledger.md
```

Easier for per-package PR review.

### Swarm in a monorepo

Per [AGENT-COORDINATION.md](AGENT-COORDINATION.md), reserve per package:
```
file_reservation_paths(... paths=["packages/core/**"] ...)
```

Different workers can refactor different packages in parallel. Workers touching shared packages coordinate or serialize.
