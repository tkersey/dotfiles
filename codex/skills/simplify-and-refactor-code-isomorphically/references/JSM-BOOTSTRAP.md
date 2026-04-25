# JSM Bootstrap — install sibling skills on demand

## Contents

1. [The graceful-degradation invariant](#the-graceful-degradation-invariant)
2. [Sibling-skill matrix](#sibling-skill-matrix)
3. [Bootstrap flow (Phase 0)](#bootstrap-flow-phase-0)
4. [Installing jsm](#installing-jsm)
5. [Logging in to jsm](#logging-in-to-jsm)
6. [Headless / SSH workflows](#headless--ssh-workflows)
7. [Subscription detection](#subscription-detection)
8. [Installing missing skills](#installing-missing-skills)
9. [Fallbacks when jsm / subscription unavailable](#fallbacks-when-jsm--subscription-unavailable)
10. [Scripts this skill ships](#scripts-this-skill-ships)

---

> This skill references many siblings ([extreme-software-optimization](../../extreme-software-optimization/SKILL.md), [multi-pass-bug-hunting](../../multi-pass-bug-hunting/SKILL.md), [ubs](../../ubs/SKILL.md), [cass](../../cass/SKILL.md), [codebase-archaeology](../../codebase-archaeology/SKILL.md), and more). If any are missing, the user's paid [jeffreys-skills.md](https://jeffreys-skills.md) subscription ($20/mo) lets us `jsm install <name>` on the fly. If the user isn't subscribed, we degrade gracefully — every sibling reference has an inline fallback.

## The graceful-degradation invariant

> **No phase of this skill should require any other skill to run.**
> Every sibling reference has an inline fallback (in the referenced section or file). Siblings are *accelerants*, not prerequisites.

Don't stall the user because a sibling isn't installed. Check → log → proceed with fallback → offer install.

---

## Sibling-skill matrix

Siblings this skill invokes or cites. Grouped by phase.

| Phase | Sibling | What it contributes | Inline fallback if missing |
|-------|---------|---------------------|----------------------------|
| Baseline | [cass](../../cass/SKILL.md) | mine prior refactor sessions for precedent | skip; [CASE-STUDIES.md](CASE-STUDIES.md) has composite examples |
| Baseline | [codebase-archaeology](../../codebase-archaeology/SKILL.md) | build a mental model of unfamiliar code | [METHODOLOGY.md §Phase A](METHODOLOGY.md#phase-a--baseline) has the prompt inline |
| Map | [mock-code-finder](../../mock-code-finder/SKILL.md) | find stubs/mocks/TODOs (often duplicated) | `rg 'TODO\|FIXME\|unimplemented' -n` suffices |
| Map | [ubs](../../ubs/SKILL.md) | surface bug-smells that often *are* the duplicate code | language-native linters (clippy, eslint, pylint, vet) work too |
| Map | [cass](../../cass/SKILL.md) | find prior duplicate-extraction precedent | duplication scanners cover 80% |
| Score | [multi-model-triangulation](../../multi-model-triangulation/SKILL.md) | second opinion on Risk/Confidence | filling the isomorphism card honestly suffices |
| Prove | [testing-golden-artifacts](../../testing-golden-artifacts/SKILL.md) | capture goldens per shape (CLI, HTTP, SQL, UI) | [ISOMORPHISM.md §capture goldens](ISOMORPHISM.md#how-to-capture-goldens-per-language) has patterns |
| Prove | [testing-metamorphic](../../testing-metamorphic/SKILL.md) | metamorphic relations when goldens are expensive | simpler property tests cover many cases |
| Prove | [testing-fuzzing](../../testing-fuzzing/SKILL.md) | fuzz the refactored surface to catch silent diffs | not strictly needed for most passes |
| Collapse | [cc-hooks](../../cc-hooks/SKILL.md) | install PreToolUse hooks to block `sed`/codemod | AGENTS.md rule is the manual check |
| Collapse | [agent-mail](../../agent-mail/SKILL.md) | file reservations when running swarm | single-agent mode if absent |
| Collapse | [ntm](../../ntm/SKILL.md) | orchestrate the parallel refactor swarm | run sequentially if absent |
| Collapse | [br](../../br/SKILL.md) / [beads-workflow](../../beads-workflow/SKILL.md) | track candidates as beads | append to ledger markdown instead |
| Verify | [ubs](../../ubs/SKILL.md) | post-edit scan for real bugs introduced | clippy / eslint / mypy / vet |
| Verify | [multi-pass-bug-hunting](../../multi-pass-bug-hunting/SKILL.md) | depth bug hunt after major pass | skip; re-run tests |
| Verify | [deadlock-finder-and-fixer](../../deadlock-finder-and-fixer/SKILL.md) | concurrency-semantics check | tsan/rts can substitute |
| Verify | [testing-perfect-e2e-integration-tests-with-logging-and-no-mocks](../../testing-perfect-e2e-integration-tests-with-logging-and-no-mocks/SKILL.md) | exercise real services post-refactor | playwright / pytest integration tests |
| Verify | [e2e-testing-for-webapps](../../e2e-testing-for-webapps/SKILL.md) | playwright golden screenshot suite | inline playwright pattern |
| Ledger | [readme-writing](../../readme-writing/SKILL.md) | polish the PR body | standard commit template |
| Ledger | [de-slopify](../../de-slopify/SKILL.md) | de-slop the PR description | manual prose |
| Profiling-adjacent | [profiling-software-performance](../../profiling-software-performance/SKILL.md) | confirm no perf regression | `hyperfine` smoke test |
| Profiling-adjacent | [extreme-software-optimization](../../extreme-software-optimization/SKILL.md) | if the refactor reveals hot paths | see sibling's loop |
| Meta | [sc](../../sc/SKILL.md) / [sw](../../sw/SKILL.md) / [operationalizing-expertise](../../operationalizing-expertise/SKILL.md) | for evolving THIS skill — not runtime | — |
| Cross-cutting | [frankensearch-integration-for-rust-projects](../../frankensearch-integration-for-rust-projects/SKILL.md) | if the project embeds search | doc-only reference |
| Cross-cutting | [porting-to-rust](../../porting-to-rust/SKILL.md) | if post-refactor the user wants to port | doc-only reference |
| Cross-cutting | [supabase](../../supabase/SKILL.md) / [vercel](../../vercel/SKILL.md) / [tanstack](../../tanstack/SKILL.md) | stack-specific idiom awareness | fallback to general TS/React patterns in [LANGUAGE-GUIDES.md](LANGUAGE-GUIDES.md) |

**Usage rule:** read this matrix at Phase 0; run `./scripts/check_skills.sh` to get a JSON inventory; offer `jsm install` for any missing siblings; if declined, proceed with inline fallbacks.

---

## Bootstrap flow (Phase 0)

Run this before any refactor work. It's fast and non-destructive.

```bash
# 1. Check which siblings are installed and jsm state
./scripts/check_skills.sh
# → writes refactor/artifacts/<run-id>/skill_inventory.json
# → prints human-readable table

# 2. If jsm is missing and user wants premium skills:
#    (the script offers; don't force)
./scripts/install_jsm.sh   # curl-to-bash installer

# 3. Authenticate jsm (user-gated; opens browser OAuth or API key)
jsm login
# or: jsm auth    (API key path — for headless)

# 4. Install any missing siblings the user wants
./scripts/install_missing_skills.sh
# → reads skill_inventory.json
# → runs `jsm install <name>` per missing entry
# → idempotent; subscription gate handled gracefully
# → logs to refactor/artifacts/<run-id>/missing_skills.md

# 5. Proceed to Phase A — Baseline
```

The three scripts are **idempotent** and **non-blocking**. Re-run them as many times as needed.

---

## Installing jsm

### Is it already installed?

```bash
command -v jsm >/dev/null && jsm --version || echo "jsm not installed"
```

If installed → skip to [authentication](#logging-in-to-jsm).

### Install (Linux / macOS)

```bash
curl -fsSL https://jeffreys-skills.md/install.sh | bash
```

Per the [installer-workmanship](../../installer-workmanship/SKILL.md) patterns, the official installer:
- downloads a pinned version
- verifies a checksum
- installs to `~/.local/bin/jsm` (user-local; no sudo)
- prints PATH setup instructions if `~/.local/bin` isn't in PATH

Add to PATH if needed:
```bash
export PATH="$HOME/.local/bin:$PATH"
# persist in ~/.bashrc or ~/.zshrc
```

### Install (Windows PowerShell)

```powershell
irm https://jeffreys-skills.md/install.ps1 | iex
```

Drops binary at `%LOCALAPPDATA%\jsm\jsm.exe`.

### Verify

```bash
jsm --version
jsm doctor            # non-destructive health check
jsm doctor --fix      # auto-repair config paths, PATH shims
jsm doctor            # re-run; should be clean except maybe auth
```

---

## Logging in to jsm

### Standard (desktop with browser)

```bash
jsm login
# → prints a URL; user opens it; signs in with the Google account
#   tied to their jeffreys-skills.md subscription
```

Credentials stored encrypted at `~/.config/jsm/credentials.enc`.

### Verify

```bash
jsm whoami
# → email + subscription tier (active / trial / free / expired)
```

---

## Headless / SSH workflows

**Option 1 — API key** (recommended for CI and remote shells):

```bash
jsm auth
# → interactive prompt; paste API key from https://jeffreys-skills.md/dashboard
```

**Option 2 — OAuth URL forwarding**:

```bash
jsm login --print-url
# → prints a URL; copy and open on your laptop; credentials land back
#   via OAuth callback to the headless machine
```

**Option 3 — env-var passphrase** (for automation):

```bash
export JSM_ALLOW_ENV_PASSPHRASE=1
export JSM_CREDENTIALS_PASSPHRASE='<your-passphrase>'
```

Only set these in session-local env. Never commit. Prefer an API key for CI.

---

## Subscription detection

```bash
jsm whoami --json | jq -r '.subscription.status'
# → "active" | "trial" | "free" | "expired"
```

**active** — can install any skill.
**trial** — time-limited, most skills installable.
**free / expired** — only free/public skills; premium returns `SUBSCRIPTION_REQUIRED`.

The `check_skills.sh` script captures the status into `skill_inventory.json`, so downstream phases don't need to re-query.

---

## Installing missing skills

### One at a time

```bash
jsm install cass
jsm install ubs
jsm install multi-pass-bug-hunting
```

Installed skills land at `~/.claude/skills/<name>/`. Claude Code discovers them per-invocation — no restart needed.

### In bulk via this skill's script

```bash
./scripts/install_missing_skills.sh
# reads skill_inventory.json; tries every missing entry; logs results
```

### With dependencies

```bash
jsm install <name> --related
# install plus any related/required siblings (jsm knows the dep graph)
```

### Pinning versions

```bash
jsm install cass@0.3.6     # exact version
jsm install cass@^0.3       # semver range
jsm list --installed       # see what versions you have
jsm outdated               # see what has updates
```

Pin when reproducibility matters (CI, bisect-friendly refactor runs). Otherwise `jsm install <name>` takes latest.

---

## Fallbacks when jsm / subscription unavailable

### Script contract

Both `check_skills.sh` and `install_missing_skills.sh` **exit 0** even when:
- jsm is not installed
- jsm is not authenticated
- the user has no paid subscription
- a specific skill isn't in the catalog
- network is offline

They emit `missing_skills.md` listing each sibling with its inline-fallback pointer. The refactor pass proceeds with those fallbacks.

### Per-sibling fallback

| Missing sibling | Inline fallback |
|-----------------|-----------------|
| `cass` | skip session-mining; use [CASE-STUDIES.md](CASE-STUDIES.md) composite examples |
| `ubs` | run `cargo clippy --all-targets -- -D warnings` / `eslint` / `mypy --strict` / `staticcheck` |
| `codebase-archaeology` | read the prompt from [METHODOLOGY.md §Phase A](METHODOLOGY.md#phase-a--baseline) + do a manual `rg`/`ast-grep` tour |
| `testing-golden-artifacts` | [ISOMORPHISM.md §goldens per language](ISOMORPHISM.md#how-to-capture-goldens-per-language) |
| `multi-pass-bug-hunting` | re-run tests, rg for `TODO`/`FIXME`, run the language linter |
| `agent-mail` + `ntm` + `br` | serialize: one candidate at a time, one commit each, no swarm |
| `multi-model-triangulation` | fill the isomorphism card twice, once strict, once devil's-advocate |
| `profiling-software-performance` / `extreme-software-optimization` | `hyperfine --runs 20` as a perf smoke test |
| `mock-code-finder` | `rg 'TODO\|FIXME\|mock\|stub\|unimplemented' -t <lang>` |

### What NOT to do when a sibling is missing

- Don't pause for input loop — log and proceed.
- Don't re-prompt the user for the same subscription every turn.
- Don't silently skip the phase — the fallback runs, and the ledger notes which sibling would have improved the pass.

---

## Scripts this skill ships

| Script | Purpose | Exit 0 even on missing? |
|--------|---------|-------------------------|
| `scripts/check_skills.sh` | detect installed siblings + jsm state; emit `skill_inventory.json` | yes |
| `scripts/install_jsm.sh` | run the official installer; offer user consent before downloading | yes (respects declination) |
| `scripts/install_missing_skills.sh` | bulk `jsm install` for missing siblings; log failures | yes |

See [ARTIFACTS.md](ARTIFACTS.md) for the `skill_inventory.json` schema.

---

## Quick reference

```bash
# Full Phase 0 bootstrap
./scripts/check_skills.sh refactor/artifacts/2026-04-23-pass-1
./scripts/install_jsm.sh           # only runs if user consents
jsm login                           # user-gated
./scripts/install_missing_skills.sh refactor/artifacts/2026-04-23-pass-1

# Verify
jsm whoami --json | jq
jsm list --installed
cat refactor/artifacts/2026-04-23-pass-1/skill_inventory.json | jq '.skills[] | select(.status=="missing")'
```
