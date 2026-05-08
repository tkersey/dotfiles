# CI-INTEGRATION — PR-time drift guards

> **Status: partly aspirational.** The hooks at `scripts/aerg-hooks/*.sh`
> referenced below are documented in `HOOKS-INTEGRATION.md` but not yet
> implemented. The CI workflow templates here are usable today for any
> hook scripts you implement; the `assets/ci/agent-ergonomics-check/`
> composite action (used in this skill) IS implemented and works.

PR-time checks for agent-ergonomic regression. Catches drift before it merges.

GitHub Actions workflow templates for the most common languages, plus equivalent for GitLab CI.

The workflows reference `audit/regression_tests/` (the durable test suite produced by Phase 5). They run on every PR, plus optionally on a schedule for slow drift detection.

---

## GitHub Actions — Rust + cargo

`.github/workflows/agent-ergo-regression.yml`:

```yaml
name: Agent-Ergo Regression Tests

on:
  pull_request:
    paths:
      - 'src/**'
      - 'audit/**'
      - 'Cargo.lock'
      - 'Cargo.toml'
      - '.github/workflows/agent-ergo-regression.yml'
  schedule:
    - cron: '0 6 * * 1'  # weekly Monday 06:00 UTC

jobs:
  agent-ergo:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4

      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2

      - name: Build release binary
        run: cargo build --release

      - name: Capabilities schema pin
        run: |
          export TOOL_BIN=$(pwd)/target/release/mytool
          got=$("$TOOL_BIN" capabilities --json | jq -S .)
          want=$(cat audit/regression_tests/capabilities-golden.json | jq -S .)
          diff <(echo "$got") <(echo "$want") || {
            echo "::error::capabilities --json drifted; bump contract_version OR update golden if intentional"
            exit 1
          }

      - name: Run all regression tests
        run: |
          export TOOL_BIN=$(pwd)/target/release/mytool
          failed=0
          for t in audit/regression_tests/R-*.test.sh; do
            echo "::group::$t"
            if bash "$t"; then
              echo "::endgroup::"
            else
              echo "::endgroup::"
              echo "::error::regression test failed: $t"
              failed=$((failed + 1))
            fi
          done
          [ "$failed" -gt 0 ] && exit 1

      - name: Help footer audit
        run: bash scripts/aerg-hooks/check-help-footer.sh

      - name: Mutating-verb gate audit
        run: bash scripts/aerg-hooks/check-mutating-verb-gates.sh

      - name: NO_COLOR / non-TTY discipline
        run: |
          export TOOL_BIN=$(pwd)/target/release/mytool
          # Pipes must not contain ANSI
          out=$("$TOOL_BIN" list | cat)
          if echo "$out" | grep -qE $'\x1b\['; then
            echo "::error::ANSI escapes leaked into piped stdout"
            exit 1
          fi
          # NO_COLOR=1 must suppress
          out=$(NO_COLOR=1 "$TOOL_BIN" list)
          if echo "$out" | grep -qE $'\x1b\['; then
            echo "::error::NO_COLOR=1 ignored"
            exit 1
          fi

      - name: Determinism check
        run: |
          export TOOL_BIN=$(pwd)/target/release/mytool
          export SOURCE_DATE_EPOCH=1234567890
          run1=$("$TOOL_BIN" list --json)
          run2=$("$TOOL_BIN" list --json)
          # Strip volatile fields
          norm() { jq 'del(.meta.request_id, .meta.ts)' <<< "$1"; }
          if [ "$(norm "$run1")" != "$(norm "$run2")" ]; then
            echo "::error::output not deterministic across re-runs"
            diff <(norm "$run1") <(norm "$run2")
            exit 1
          fi

      - name: Upload test artifacts on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: aerg-regression-failures
          path: |
            audit/scorecard*.md
            audit/regression_alerts.md
```

---

## GitHub Actions — Go + go test

`.github/workflows/agent-ergo-regression-go.yml`:

```yaml
name: Agent-Ergo Regression (Go)

on: [pull_request]

jobs:
  agent-ergo:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with: { go-version: 'stable' }

      - run: go build -o ./mytool ./cmd/mytool

      - name: Capabilities + footer + verb gates
        run: |
          export TOOL_BIN=$(pwd)/mytool
          bash audit/regression_tests/capabilities-pin.test.sh
          bash scripts/aerg-hooks/check-help-footer.sh
          bash scripts/aerg-hooks/check-mutating-verb-gates.sh

      - name: All regression tests
        run: |
          export TOOL_BIN=$(pwd)/mytool
          for t in audit/regression_tests/R-*.test.sh; do bash "$t" || exit 1; done
```

---

## GitHub Actions — Python + pytest

```yaml
name: Agent-Ergo Regression (Python)

on: [pull_request]

jobs:
  agent-ergo:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }

      - run: pip install -e .

      - name: Capabilities pin
        run: |
          got=$(mytool capabilities --json | jq -S .)
          want=$(cat audit/regression_tests/capabilities-golden.json | jq -S .)
          diff <(echo "$got") <(echo "$want")

      - name: Pytest regression tests
        run: pytest audit/regression_tests/ -v

      - name: Shell regression tests
        run: |
          for t in audit/regression_tests/R-*.test.sh; do bash "$t" || exit 1; done
```

---

## GitHub Actions — TypeScript + bun / npm

```yaml
name: Agent-Ergo Regression (TS)

on: [pull_request]

jobs:
  agent-ergo:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v1
      - run: bun install
      - run: bun run build

      - name: Vitest regression tests
        run: bun test audit/regression_tests/

      - name: Shell regression tests
        run: |
          export TOOL_BIN=$(pwd)/dist/cli.js
          for t in audit/regression_tests/R-*.test.sh; do bash "$t" || exit 1; done

      - name: Capabilities + footer
        run: bash scripts/aerg-hooks/check-help-footer.sh
```

---

## GitLab CI equivalent

`.gitlab-ci.yml`:

```yaml
agent-ergo-regression:
  stage: test
  image: rust:latest
  script:
    - cargo build --release
    - export TOOL_BIN=$(pwd)/target/release/mytool
    - bash audit/regression_tests/capabilities-pin.test.sh
    - for t in audit/regression_tests/R-*.test.sh; do bash "$t" || exit 1; done
    - bash scripts/aerg-hooks/check-help-footer.sh
  artifacts:
    when: on_failure
    paths:
      - audit/scorecard*.md
      - audit/regression_alerts.md
```

---

## Periodic re-audit (scheduled)

For tools that ship continuously, schedule a weekly Pass-N+1 re-audit:

```yaml
name: Weekly Agent-Ergo Re-Audit

on:
  schedule:
    - cron: '0 12 * * 0'  # Sunday noon UTC

jobs:
  reaudit:
    runs-on: ubuntu-latest
    timeout-minutes: 90
    steps:
      - uses: actions/checkout@v4

      # ... build the binary ...

      - name: Re-score Pass N+1
        run: |
          # invokes the agent-ergonomics audit skill in re-score mode
          # (assumes the audit workspace is committed at <repo>__agent_ergonomics_audit/)
          bash audit/scripts/rescore.sh

      - name: Open issue if regression detected
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Agent-Ergo regression detected on weekly re-audit`,
              body: `Weekly re-audit found a regression in agent-ergonomic surfaces.\n\nSee CI run for details.`
            })
```

---

## CI badge

Add to README:

```markdown
[![Agent-Ergo](https://github.com/<org>/<repo>/actions/workflows/agent-ergo-regression.yml/badge.svg)](https://github.com/<org>/<repo>/actions/workflows/agent-ergo-regression.yml)
```

The badge advertises that the tool is agent-friendly. (Some agents check for this badge to prioritize integration!)

---

## Failure messages with `::error::`

GitHub Actions' annotation format makes failures clickable in the PR diff:

```yaml
- name: Drift check
  run: |
    if /* drift */ ; then
      echo "::error file=src/cli.rs,line=42::capabilities schema drifted on flag --json"
      exit 1
    fi
```

The `file=...,line=...` produces an inline annotation on the PR diff at exactly the offending line.

---

## Caching

To keep CI fast, cache the build artifact + capabilities golden:

```yaml
- name: Cache release binary
  uses: actions/cache@v4
  with:
    path: target/release/mytool
    key: bin-${{ hashFiles('Cargo.lock', 'src/**') }}
```

Then only re-build when source changes.

---

## Failing-fast vs collecting all failures

Two strategies:

**Fail-fast** (simpler, faster):

```bash
for t in audit/regression_tests/R-*.test.sh; do
  bash "$t" || exit 1
done
```

**Collect-all** (richer feedback to PR author):

```bash
failed=()
for t in audit/regression_tests/R-*.test.sh; do
  bash "$t" || failed+=("$t")
done
if [ ${#failed[@]} -gt 0 ]; then
  echo "::error::${#failed[@]} regression tests failed:"
  printf '  %s\n' "${failed[@]}"
  exit 1
fi
```

The collect-all version is preferred for PR feedback (catches all issues in one cycle); fail-fast is acceptable for nightly / cron jobs.

---

## Combining with other CI

Don't add a separate `agent-ergo` job if the existing test job is fast enough. Instead, add the regression tests as a step in the existing job:

```yaml
- name: Tests
  run: |
    cargo test
    bash audit/regression_tests/capabilities-pin.test.sh
    bash scripts/aerg-hooks/check-help-footer.sh
    for t in audit/regression_tests/R-*.test.sh; do bash "$t" || exit 1; done
```

Saves CI minutes; same protection.

---

## What NOT to do

- **Don't** make agent-ergo CI a check that bypasses the rest. It's a quality gate, not a "skip if everything else passes."
- **Don't** auto-update the golden file in CI. The whole point of a pin is that it's intentional.
- **Don't** silently skip tests that fail. Fail loudly; let humans triage.
- **Don't** require the audit workspace to be a separate repo if you can avoid it. Committing `audit/regression_tests/` directly into the target repo is simpler.

---

## Related

- `HOOKS-INTEGRATION.md` — pre-commit guards (run before push, in addition to CI)
- `references/rubric/REGRESSION-TEST-PATTERNS.md` — the test-author's playbook
- `methodology/CONTINUOUS-IMPROVEMENT.md` — periodic re-audits beyond pass-N
