# CI/CD integration — full pipeline templates

> Hooks catch violations locally; CI is the wall that stops bad commits
> from merging regardless of local config. This file gives you drop-in
> pipeline definitions for GitHub Actions (primary), GitLab CI, and
> CircleCI.

## Contents

1. [What CI must enforce](#what-ci-must-enforce)
2. [GitHub Actions — full workflow](#github-actions--full-workflow)
3. [GitLab CI — equivalent](#gitlab-ci--equivalent)
4. [CircleCI — equivalent](#circleci--equivalent)
5. [Branch protection rules](#branch-protection-rules)
6. [PR comment bot — score summary](#pr-comment-bot--score-summary)
7. [Per-repo tuning](#per-repo-tuning)

---

## What CI must enforce

For any PR that claims to be a refactor:

1. **Build passes** (cargo build / npm run build / go build / etc.).
2. **Full test suite passes**, with EXACT same pass-count as base branch
   (not just "no failures"; the count must match).
3. **Warning ceiling not exceeded** — `lint_ceiling.sh check` green.
4. **Goldens byte-identical** — diff against base branch is 0 bytes.
5. **No forbidden filenames added** — `_v2`, `_new`, `tmp_`, `_backup`.
6. **No forbidden substrings introduced** — net-new `any`, `unwrap()`,
   `@ts-ignore`, bare `except:`.
7. **No deleted tests** unless explicitly justified in commit body.
8. **LOC delta ≤ 0** (for refactor PRs; feature PRs are exempt).
9. **Card file exists** at `refactor/artifacts/<run-id>/cards/ISO-*.md`
   referenced by the commit body.

## GitHub Actions — full workflow

`.github/workflows/refactor-gates.yml`:

```yaml
name: refactor-gates

on:
  pull_request:
    branches: [main]
    paths:
      - 'src/**'
      - 'refactor/**'
      - '.claude/skills/**'

jobs:
  meta:
    runs-on: ubuntu-latest
    outputs:
      is_refactor: ${{ steps.detect.outputs.is_refactor }}
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - id: detect
        run: |
          if git log --format=%s origin/main..HEAD | grep -qE '^refactor\('; then
            echo "is_refactor=true" >> $GITHUB_OUTPUT
          else
            echo "is_refactor=false" >> $GITHUB_OUTPUT
          fi

  build-and-test:
    needs: meta
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # Language-specific setup — pick one:
      - uses: actions-rs/toolchain@v1
        with: { toolchain: stable, components: rustfmt,clippy }
      - run: cargo build --all-targets
      - run: cargo test --no-fail-fast 2>&1 | tee test-output.txt
      - name: Compare test pass count to base
        if: needs.meta.outputs.is_refactor == 'true'
        run: |
          base_count=$(git show origin/main:refactor/artifacts/last-good-passcount.txt 2>/dev/null || echo 0)
          head_count=$(grep -oE '[0-9]+ passed' test-output.txt | awk '{s+=$1} END{print s+0}')
          if [[ "$head_count" -ne "$base_count" ]]; then
            echo "Test pass count changed: $base_count → $head_count"
            echo "A refactor must not change the test pass count."
            exit 1
          fi

  warning-ceiling:
    needs: meta
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check warning ceiling
        run: ./.claude/skills/simplify-and-refactor-code-isomorphically/scripts/lint_ceiling.sh check

  golden-diff:
    needs: meta
    if: needs.meta.outputs.is_refactor == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - name: Diff goldens against base
        run: |
          git fetch origin main
          if ! git diff --quiet origin/main -- refactor/artifacts/*/goldens/ 2>/dev/null; then
            echo "Goldens differ from main. A refactor must preserve goldens byte-identically."
            git diff --stat origin/main -- refactor/artifacts/*/goldens/
            exit 1
          fi

  forbidden-patterns:
    needs: meta
    if: needs.meta.outputs.is_refactor == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - name: Forbidden filenames
        run: |
          git fetch origin main
          new=$(git diff --name-only --diff-filter=A origin/main)
          if echo "$new" | grep -E '(_v2|_new|tmp_|_backup)\.' >/dev/null; then
            echo "Forbidden filename pattern in added files"
            exit 1
          fi
      - name: Forbidden substrings added in diff
        run: |
          added=$(git diff -U0 origin/main | grep '^+' | grep -v '^+++')
          fail=0
          echo "$added" | grep -E ':\s*any\b|\bas any\b' && fail=1
          echo "$added" | grep -E '\.unwrap\(\)|\.expect\(' && fail=1
          echo "$added" | grep -E '@ts-ignore|@ts-expect-error' && fail=1
          if [[ $fail -eq 1 ]]; then
            echo "Net-new forbidden patterns introduced"
            exit 1
          fi

  loc-delta:
    needs: meta
    if: needs.meta.outputs.is_refactor == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - name: Compute LOC delta
        run: |
          git fetch origin main
          delta=$(./.claude/skills/simplify-and-refactor-code-isomorphically/scripts/loc_delta.sh --net-only origin/main HEAD)
          echo "LOC delta: $delta"
          if [[ "$delta" -gt 0 ]]; then
            echo "Refactor PRs must not increase LOC. Delta: +$delta"
            exit 1
          fi

  card-exists:
    needs: meta
    if: needs.meta.outputs.is_refactor == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Verify isomorphism card referenced
        run: |
          msg=$(git log origin/main..HEAD --format=%B)
          card_ref=$(echo "$msg" | grep -oE 'refactor/artifacts/[^ )]+/cards/ISO-[0-9]+\.md' | head -1)
          if [[ -z "$card_ref" ]]; then
            echo "Commit body must reference an isomorphism card path."
            exit 1
          fi
          if [[ ! -f "$card_ref" ]]; then
            echo "Referenced card does not exist: $card_ref"
            exit 1
          fi
```

Wire these jobs as required status checks in branch protection so the PR
can't merge until all are green.

## GitLab CI — equivalent

`.gitlab-ci.yml` (abbreviated):

```yaml
stages: [refactor-gates]

.refactor-only:
  rules:
    - if: '$CI_COMMIT_MESSAGE =~ /^refactor\(/'

refactor:build-test:
  stage: refactor-gates
  script:
    - cargo build --all-targets
    - cargo test --no-fail-fast

refactor:warning-ceiling:
  extends: .refactor-only
  stage: refactor-gates
  script:
    - ./.claude/skills/simplify-and-refactor-code-isomorphically/scripts/lint_ceiling.sh check

refactor:golden-diff:
  extends: .refactor-only
  stage: refactor-gates
  script:
    - git diff --quiet origin/main -- refactor/artifacts/*/goldens/

refactor:forbidden-patterns:
  extends: .refactor-only
  stage: refactor-gates
  script:
    - ./ci/check-forbidden.sh origin/main

refactor:loc-delta:
  extends: .refactor-only
  stage: refactor-gates
  script:
    - delta=$(./.claude/skills/simplify-and-refactor-code-isomorphically/scripts/loc_delta.sh --net-only origin/main HEAD)
    - test "$delta" -le 0
```

## CircleCI — equivalent

`.circleci/config.yml` (abbreviated):

```yaml
version: 2.1

jobs:
  refactor-gates:
    docker: [{ image: cimg/rust:stable }]
    steps:
      - checkout
      - run:
          name: Build + test
          command: cargo test --no-fail-fast
      - run:
          name: Warning ceiling
          command: ./.claude/skills/simplify-and-refactor-code-isomorphically/scripts/lint_ceiling.sh check
      - run:
          name: Golden diff
          command: git diff --quiet origin/main -- refactor/artifacts/*/goldens/
      - run:
          name: LOC delta
          command: |
            delta=$(./.claude/skills/simplify-and-refactor-code-isomorphically/scripts/loc_delta.sh --net-only origin/main HEAD)
            test "$delta" -le 0

workflows:
  refactor:
    jobs:
      - refactor-gates:
          filters: { branches: { only: /^refactor\/.*/ } }
```

## Branch protection rules

In GitHub repo settings → Branches → `main`:

- [ ] Require pull request reviews before merging (≥ 1 reviewer)
- [ ] Dismiss stale reviews on new commits
- [ ] Require status checks to pass:
      - `build-and-test`
      - `warning-ceiling`
      - `golden-diff`
      - `forbidden-patterns`
      - `loc-delta`
      - `card-exists`
- [ ] Require branches to be up to date before merging
- [ ] Require signed commits (optional, recommended)
- [ ] Include administrators (yes — no bypass)

## PR comment bot — score summary

Optional but useful. After `refactor-gates` passes, a bot comments the
skill's dashboard summary on the PR:

```
## Refactor gate summary
✅ Build + tests
✅ Warning ceiling (delta: -3)
✅ Goldens byte-identical
✅ LOC delta: -42
✅ Card: refactor/artifacts/2026-05-14-pass-2/cards/ISO-014.md

Candidate: ISO-014 (type II, 3 sites, L-EXTRACT)
Lever applied: ✅
Drive-by scan: clean
```

Implement via `gh pr comment` in a final workflow step.

## Per-repo tuning

- **Monolithic repos**: run the gates in parallel, cache build artifacts.
- **Monorepos**: scope each job to changed packages only (use
  `turbo run --filter`, nx `affected`, pants `--changed-since=origin/main`).
  See [MONOREPO.md](MONOREPO.md).
- **Slow test suites**: split `build-and-test` into fast-unit and
  full-integration jobs; require fast-unit always, full only for
  `refactor(*)` commits touching `src/`.
- **Monorepos with strict perf**: add a `perf-diff` job that runs a
  micro-benchmark subset and fails on ≥ 2σ regression. See
  [PERF-AWARE-REFACTOR.md](PERF-AWARE-REFACTOR.md).

See also [HOOKS.md](HOOKS.md) and [GIT-HOOKS.md](GIT-HOOKS.md) for the
local layers that complement CI.
