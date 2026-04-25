# Dead-Code Safety Gauntlet — preventing the horror story

> Named after HS#1 in [REAL-SESSION-EVIDENCE.md](REAL-SESSION-EVIDENCE.md) — the session where an agent deleted `sync-pipeline.ts` as "dead code" and the user replied: *"wait you fgucking DELETED that as dead code instead of USING IT properly????? WHAT THE FUCK"*. This file is the systematic countermeasure. Run this gauntlet every single time you think code is dead.

## Contents

1. [Why this exists](#why-this-exists)
2. [The 12-step safety gauntlet](#the-12-step-safety-gauntlet)
3. [Per-step detailed instructions](#per-step-detailed-instructions)
4. [Ambiguity resolution — who to ask](#ambiguity-resolution--who-to-ask)
5. [Staged removal (move, don't delete)](#staged-removal-move-dont-delete)
6. [Language-specific dynamic-reference patterns](#language-specific-dynamic-reference-patterns)
7. [The rollback contract](#the-rollback-contract)

---

## Why this exists

**"Dead code"** is the most dangerous phrase an AI agent can compose. In the horror-story session, every step looked reasonable:

1. Agent greps for imports of `sync-pipeline.ts` → zero hits.
2. Agent reads the file → "misleading/broken implementation."
3. Agent concludes: dead code.
4. Agent deletes the file + its tests.
5. Tests still pass (because the tests were deleted with the file).
6. Build still passes. Typecheck still passes.
7. **The user notices, hours later, that a critical feature was supposed to live there.**

Every verification gate in the skill's verify phase passed. The failure was in the judgment of whether the code was actually dead — a call the agent didn't have the information to make.

**This gauntlet is designed to answer one question: "is there ANY reason to believe this code was intended to be used?"** A single yes means don't delete.

---

## The 12-step safety gauntlet

Before declaring any file, function, class, module, or symbol dead:

| # | Check | Pass condition | Script help |
|---|-------|----------------|-------------|
| 1 | Source imports | zero hits in source files | `rg <symbol>` |
| 2 | Dynamic references | zero `import(...)`, `require(...)`, `importlib`, `dlopen` hits | ([patterns below](#language-specific-dynamic-reference-patterns)) |
| 3 | String references | zero hits as a plain string in config / JSON / YAML / TOML / TS / Python | `rg '"<symbol>"' .` |
| 4 | Test references | zero hits in `tests/`, `spec/`, `__tests__/` | `rg <symbol> tests/ __tests__/ spec/` |
| 5 | Build references | zero hits in `package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, `*.yml`, `Dockerfile`, `Makefile` | build-file grep |
| 6 | Feature flag lookup | zero references in a flag system (`LaunchDarkly`, `config/features.*`, env vars, `.env*`) | config-file grep |
| 7 | Doc references | zero references in `README.md`, `docs/`, `ADR/`, `CHANGELOG.md` | doc grep |
| 8 | Git history signal | last touch was NOT "feature in progress" / "initial commit" / "scaffolding" | `git log --follow <path>` |
| 9 | Companion file signal | no `<name>.test.*`, `<name>.stories.*`, `<name>.md` describing the intent | file pattern search |
| 10 | Named intent signal | name doesn't include `intended`, `future`, `planned`, `todo`, `stub`, `wip`, `scaffold` | filename inspection |
| 11 | Owner check | git blame's most-frequent author has been asked | `git log --format='%an' <path> \| sort \| uniq -c \| sort -rn \| head -1` |
| 12 | Explicit user approval | the user said "yes, delete" with full evidence in front of them | conversation record |

**All 12 must pass before deletion. ANY fail → do not delete. Move to `refactor/_to_delete/` and ask.**

---

## Per-step detailed instructions

### Step 1 — Source imports

```bash
rg -F "from '<path>'" .
rg -F 'from "<path>"' .
rg -F "import '<path>'" .
rg -F "import \"<path>\"" .
rg -F "require('<path>')" .
rg -F 'require("<path>")' .
rg -F 'use <crate>::<module>' .          # Rust
rg -F 'from <module> import' .          # Python
rg -F '"<package>/<module>"' .          # Go
rg -F '#include "<path>"' .              # C/C++
```

**Trap:** imports can resolve via path aliases (`@/`, `~/`, `src/`). Check your tsconfig `paths`, Go module replace directives, Cargo workspace aliases.

### Step 2 — Dynamic references

| Language | Dynamic-import pattern |
|----------|------------------------|
| TS / JS | `import(...)`, `require(...)`, `eval(...)`, computed property access (`x[name]`) |
| Python | `importlib.import_module`, `__import__`, `getattr` on module, `pkgutil.iter_modules` |
| Rust | `dlopen`, `libloading`, `const fn` registration tables, `inventory::submit!`, `ctor` crate |
| Go | `plugin.Open`, reflection, struct tag lookup |
| C / C++ | `dlopen`, `LoadLibrary`, function pointer tables registered elsewhere |

```bash
rg 'import\(|require\(' -t ts -t tsx
rg 'importlib|__import__|getattr\(\s*\w+,\s*["\']' -t py
rg 'libloading|dlopen|inventory::submit!|#\[ctor' -t rust
rg 'plugin\.Open' -t go
```

### Step 3 — String references

Names also appear as strings — for routing, config, logs, telemetry, analytics events.

```bash
# Your symbol in any string literal anywhere
rg -F '"MySymbol"' --glob '!node_modules' --glob '!target' --glob '!vendor'
rg -F "'MySymbol'" --glob '!node_modules'
# YAML / TOML / JSON / ini specifically
rg -F 'MySymbol' --type yaml --type toml --type json
```

**Example catches:**
- A function named `handleSignup` referenced in a Rails-style routes file as `action: 'handleSignup'`
- A React component registered in a CMS as `"ComponentName"`
- A class name referenced in a plugin manifest
- An event name sent to analytics

### Step 4 — Test references

```bash
rg -F <symbol> tests/ __tests__/ spec/ test/
rg -F <symbol> --type-add 'test:*{_test.go,_spec.ts,.test.ts,.test.tsx,.spec.ts,_test.py,_test.rs}' -t test
```

**Trap:** if you are about to delete a file AND its tests, step 4 passes trivially. It's not meaningful unless you preserve tests and check.

### Step 5 — Build references

```bash
# JS/TS
rg -F <symbol> package.json pnpm-workspace.yaml package-lock.json yarn.lock
rg -F <symbol> turbo.json nx.json .github/workflows/ Dockerfile

# Rust
rg -F <symbol> Cargo.toml Cargo.lock rust-toolchain.toml build.rs

# Python
rg -F <symbol> pyproject.toml setup.py setup.cfg MANIFEST.in

# Go
rg -F <symbol> go.mod go.sum Makefile

# Infrastructure
rg -F <symbol> terraform/ k8s/ helm/ ansible/ .env*
```

### Step 6 — Feature flag lookup

```bash
# Flag system references
rg -F <symbol> --type-add 'cfg:*{config.*,features.*,flags.*,.env*,.envrc}' -t cfg

# Conditional feature flags in code
rg '(FEATURE|FLAG|ENABLE|DISABLE|NEW|LEGACY)_\w+' -n | rg -i <symbol>
```

**If the flag system is external** (LaunchDarkly, Statsig, Split.io, Optimizely): query it. Names appear there literally. Ask the user if you don't have access.

### Step 7 — Documentation references

```bash
rg -F <symbol> README.md docs/ ADR/ CHANGELOG.md CONTRIBUTING.md
rg -F <symbol> --type md
```

**Documentation signals intent even if the feature isn't wired.** If ADR-042 says "we decided to implement `sync-pipeline.ts` in Q2," the file is pre-work, not dead.

### Step 8 — Git history signal

```bash
git log --follow --format='%h %s' <path> | head -10
```

Look at:
- **Last commit message:** "scaffold", "initial", "wip", "placeholder" → almost certainly intended-future code.
- **Age:** if the file is <30 days old, it's likely pre-work.
- **Frequency:** files touched once and never since are either done-and-stable or abandoned-and-stubbed.
- **Recent deletion attempts:** `git log --follow --diff-filter=D -- <path>` — was there a recent revert? Someone already tried to delete this and it came back. Don't be the second attempt.

### Step 9 — Companion file signal

Dead code usually has no companions. Intended-future code often has:

```bash
# For a file sync-pipeline.ts:
ls sync-pipeline.test.ts sync-pipeline.spec.ts
ls sync-pipeline.stories.* sync-pipeline.mdx sync-pipeline.md
ls __tests__/sync-pipeline*
```

A file with a sibling test/doc/story file is **never** dead in the "delete freely" sense — the companion file encodes expectation.

### Step 10 — Named intent signal

Filenames that include these tokens are not dead, they are TODO:

```
intended, future, planned, todo, stub, wip, scaffold, placeholder, pending, draft, next, new, v2, v3
```

```bash
# Flag names that signal intent:
find . -type f | grep -iE '(intended|future|planned|todo|stub|wip|scaffold|placeholder|pending|draft|_v[0-9]|_new)'
```

These are usually the opposite of dead — they are *uncommitted* live code.

### Step 11 — Owner check

```bash
git log --format='%an' <path> | sort | uniq -c | sort -rn | head -3
```

The most-frequent author is the person who knows what the file was for. Mentioning "I'm about to delete X; is that OK?" to them takes 30 seconds and costs 0 bugs.

If you're in a multi-agent session, Agent Mail gives you a direct channel:
```
send_message(to_agent=<owner>, subject="about to delete <path> — OK?", body=<evidence>)
```

### Step 12 — Explicit user approval

After steps 1–11 pass (every single check green), ask the user:

```
I have verified that <path> appears unused:

  - No source imports (step 1): <count> hits
  - No dynamic references (step 2): <count> hits
  - No string references in config/docs/tests (step 3-7): <count> hits
  - Git history: <last commit>, <age>, <author>
  - Companion files: <none / list>
  - Naming doesn't signal "intended": <yes/no>
  - Owner <name> has not been asked.

Proposed action:
  1. Move to refactor/_to_delete/<path> (reversible; preserves git history)
  2. Wait for your explicit "yes, delete" before `rm`.

Is that OK?
```

Wait for an affirmative response. Silence or "go ahead" without the specific word "yes" + the path is not sufficient.

---

## Ambiguity resolution — who to ask

If any of the 12 checks is ambiguous (not clearly 0, not clearly >0):

1. **First stop:** the owner (step 11).
2. **Second stop:** the user, with the evidence.
3. **Third stop:** if there's a multi-model setup, ask a second model ([multi-model-triangulation](../../multi-model-triangulation/SKILL.md)). A second opinion from Codex or Gemini is ~1 minute of work.
4. **Fourth stop:** file a bead saying "remove <path>" with all 11 check results attached, and leave it in the backlog.

**The wrong resolution strategy** is to decide for yourself and delete.

---

## Staged removal (move, don't delete)

Per AGENTS.md Rule Number 1 and the ✋ Ask-Before-Delete operator ([OPERATOR-CARDS.md](OPERATOR-CARDS.md)):

```bash
mkdir -p refactor/_to_delete/
# preserve directory structure
mkdir -p "refactor/_to_delete/$(dirname <path>)"
git mv <path> refactor/_to_delete/<path>
# companions too
for ext in .test.ts .spec.ts .stories.tsx .md; do
  [[ -f "<path-base>$ext" ]] && git mv "<path-base>$ext" "refactor/_to_delete/$(dirname <path>)/"
done

# commit the move separately — easy to revert
git commit -m "refactor: stage <path> for deletion (pending user approval)

Evidence: all 12 safety-gauntlet checks passed.
Verification: refactor/artifacts/<run>/dead_code_check_<symbol>.md

Waiting on: explicit user approval before rm."
```

The staged path:
- Preserves git history via `git mv`.
- Makes the code trivially restorable (`git mv back`).
- Leaves a clear marker for reviewers.
- Keeps the repo compilable (assuming no other code reaches into it).

**When the user approves:** ask the user to provide the exact destructive
deletion command in writing, with explicit acknowledgement of the irreversible
consequence. Do not suggest or run a generic `rm -rf` cleanup yourself.

**When the user declines or says "wire it in":** restore the path with `git mv` in the reverse direction and make it part of the refactor (or leave it in place if the intended behavior is future work).

---

## Language-specific dynamic-reference patterns

The traps that cause false-dead judgments:

### TypeScript / JavaScript

```typescript
// Dynamic imports resolve at runtime; grep doesn't see the module names.
const mod = await import(`./handlers/${name}.ts`);

// Computed property access, especially from strings
const registry = { handlerA, handlerB, handlerC };
const fn = registry[eventName];

// JSON config referring to modules by path or by symbol
{ "plugin": "my-plugin/src/index.ts" }
```

**Detection:**
```bash
rg 'import\([^)]*\$\{' -t ts         # template-literal dynamic imports
rg '\[\s*(\w+)\s*\]' -t ts -A 1 | grep 'registry\|handlers\|plugins'
rg '__filename|require\.resolve' -t ts
```

### Python

```python
# importlib + string composition
importlib.import_module(f"modules.{name}")

# Decorator registries populated at import time
@register
def handler(): ...

# Entry-point registration in pyproject.toml
[project.entry-points."my_plugin.handlers"]
foo = "my_package.handlers:foo"
```

**Detection:**
```bash
rg 'importlib|__import__|entry.points' -t py
rg '@register|@registry|@dispatcher' -t py
rg -F 'entry-points' pyproject.toml setup.cfg setup.py
```

### Rust

```rust
// Crates that auto-register via linker sections
use inventory;
inventory::submit!(MyHandler);   // discoverable at runtime; grep for static name

// ctor crate: runs code before main
#[ctor::ctor]
fn init_plugins() { register(...); }

// dynamic libraries loaded by libloading
libloading::Library::new("my_plugin.so")
```

**Detection:**
```bash
rg 'inventory::submit!|ctor::ctor|libloading::' -t rust
```

### Go

```go
// plugin package
plug, err := plugin.Open("handler.so")

// Reflection-based registration
reflect.TypeOf(handler{}).Method(0).Func.Call(...)

// Struct tag lookup at runtime
type X struct { Field string `json:"field" binding:"required"` }
```

**Detection:**
```bash
rg 'plugin\.Open|reflect\.TypeOf|reflect\.ValueOf' -t go
rg '`\w+:"[^"]+"' -t go    # struct tags
```

### C / C++

```cpp
// dlopen
void* handle = dlopen("./plugin.so", RTLD_NOW);
auto fn = (void(*)())dlsym(handle, "register_plugin");

// Self-registering singletons (common in legacy code)
static RegistrationHandle _reg = register_plugin();
```

**Detection:**
```bash
rg 'dlopen|dlsym|LoadLibrary|GetProcAddress' -t cpp -t c
rg 'static \w+ _\w+ = register' -t cpp
```

### Shell / scripts / CI

```yaml
# .github/workflows/*.yml — string references to module paths
- name: Run
  run: node src/worker/my-handler.js
```

```bash
rg <symbol> .github/workflows/
rg <symbol> scripts/ bin/
```

---

## The rollback contract

If you ever do delete something and discover later that you were wrong:

### If the PR hasn't merged

```bash
git revert --no-commit <move-commit-sha>  # stage inverse changes; do not rewrite history
# If manual restoration is needed after a staged move, use git mv back:
git mv refactor/_to_delete/<path> <path>
git commit -m "refactor: restore <path> (user requested; was not dead)"
```

### If the PR has merged

```bash
git log --oneline | head -20
# find the deletion commit
git show <sha>:<path> > <path>   # extract the file content from before deletion
git add <path>
git commit -m "fix: restore <path> (was not dead code; deleted by mistake in <sha>)"
```

### If the file has been gone for a while and has drift

- Extract the file as of the deletion.
- Diff against what you thought it was.
- Reconcile with any new code that assumed its absence.
- Ship as `fix:` with a full explanation.

---

## The ledger template (for dead-code decisions)

Every candidate-for-deletion that reaches this gauntlet gets a ledger row, whether you end up deleting or not:

```markdown
## Dead-code evaluation: <path>

| Step | Result | Notes |
|------|--------|-------|
| 1 source imports         | 0 | — |
| 2 dynamic references     | 0 | — |
| 3 string references      | 0 | — |
| 4 test references        | 2 | `sync-pipeline.test.ts` exists with 8 assertions |
| 5 build references       | 0 | — |
| 6 feature flag lookup    | 1 | `FEATURE_SYNC_PIPELINE_ENABLED` in `config/features.json` (currently `false`) |
| 7 doc references         | 1 | ADR-042 describes the intent |
| 8 git history            | — | last touch 2 weeks ago: "scaffold: sync pipeline per ADR-042" |
| 9 companion files        | 2 | `.test.ts`, `.md` |
| 10 named intent          | — | no "wip/stub" tokens |
| 11 owner check           | alice@org | not yet asked |
| 12 explicit user approval| N/A | — |

Decision: **DO NOT DELETE**. The file is pre-work for a feature planned in ADR-042, currently gated by `FEATURE_SYNC_PIPELINE_ENABLED=false`. Tests exist and pass. Leave in place; file a follow-up bead to track the flag flip.

Follow-up bead: br-XXX — "Enable FEATURE_SYNC_PIPELINE_ENABLED and wire sync-pipeline.ts".
```

This ledger row belongs in `refactor/artifacts/<run>/LEDGER.md` under a "Dead-code decisions" section. It prevents future passes from re-evaluating the same candidate from scratch.
