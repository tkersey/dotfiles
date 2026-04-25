# Vibe-Coded Pathologies — refactor surfaces specific to AI-generated code

## Contents

1. [Core catalog — P1 through P21](#core-catalog--p1-through-p21)
2. [Detection recipes (copy-paste rg/ast-grep)](#detection-recipes)
3. [Per-pathology isomorphism pitfalls](#per-pathology-isomorphism-pitfalls)
4. [Why these emerge specifically from AI workflows](#why-these-emerge-specifically-from-ai-workflows)
5. [Extended catalog — P22 through P40](#extended-catalog--p22-through-p40)
6. [Updated attack order (P1-P40)](#updated-attack-order-p1-p40)

---

> Projects that grew via Claude Code / Codex / Cursor / Gemini sessions without a disciplined process accumulate a characteristic set of smells. This file catalogs them with: what it looks like, how to detect it, how to collapse it, and the isomorphism pitfalls particular to each.

These are **not** the classic "legacy spaghetti" smells. They're the **artifacts of AI autocomplete at scale**: plausible-looking code that satisfies the letter of each prompt but accumulates layered defensiveness, orphans, and false abstractions across sessions.

> **Real-session evidence** for every pathology below is in [REAL-SESSION-EVIDENCE.md](REAL-SESSION-EVIDENCE.md). Each citation gives you the exact `cass` session path + line number + timestamp so you can replay the context. Mined from ~28 targeted `cass search` queries across Gemini / Claude Code / Codex sessions.
>
> **The highest-signal fleet-wide findings:**
> - `any type` appears in **1,557** session hits — the single most durable vibe-code smell.
> - `defensive coding` appears in only **25** hits — but every one is exactly this pathology. Rare term, extremely high signal.
> - `over-engineered` appears in **5** hits — when agents use this phrase about their own output, it usually marks a successful collapse candidate.
> - `redux` appears in **0** hits — agents no longer write Redux.
>
> These numbers come from real aggregated `cass` queries on 2026-04-23; they weight how strongly the skill should flag each pattern.

## Core catalog — P1 through P21

### P1 — Over-defensive try/catch

**Real-session evidence:**
- Empty catch under a success banner: `gemini/2025-12-18T03-51/c8855866 :: L45` — `try { await installGuard(...) } catch (e) { // Ignore failures during auto-install }`
- Reflex "wrap-for-robustness": `gemini/2026-02-08T16-43/6dd88123 :: L45` — *"I will apply the JS fix: wrap `highlightDiffContext` in a try...catch block for robustness"*
- Silent-fallback-to-default (Rust analogue): `mcp-agent-mail-rust audit` — *"the error was caught via a `match` arm that **swallowed the exception and defaulted to returning `now`**"*

**What it looks like**
```python
def get_user_name(user):
    try:
        if user is None:
            return None
        try:
            name = user.get('name', None)
            if name is None:
                return None
            return name
        except Exception as e:
            logger.warning(f"failed to read name: {e}")
            return None
    except Exception as e:
        logger.error(f"unexpected: {e}")
        return None
```

**Why it's a smell:** all the defensiveness hides that `user` is never None at the one callsite, and `user['name']` is a typed field. The try/catch swallows the class of bug it was trying to catch — a missing field turns into a silent `None` return.

**Detection:** `rg 'except Exception' -t py -c | sort -rn | head -20`; then eyeball functions with >2 `try`/`except` blocks per 10 LOC.

**Collapse:**
```python
def get_user_name(user: User) -> str:
    return user.name  # typed; callers handle the error
```

**Isomorphism pitfall:** the old version logged warnings; the new one propagates. If downstream code expects the "silent None on any error" behavior, the refactor silently changes UX. **Always audit every catch block before removing**: was the swallowed exception observable upstream?

---

### P2 — "Safe" nullish fallback chains

**What it looks like**
```typescript
const name = user?.profile?.name?.toString?.() ?? user?.name ?? user?.email ?? 'Anonymous';
const age = user?.profile?.age ?? user?.age ?? 0;
```

**Why it's a smell:** the chain is longer than the input. `toString?.()` is suspicious — if `name` is already a string, the call is wasted; if it isn't, the caller passed a wrong shape. Each `??` branch is a hidden contract the codebase hasn't committed to.

**Detection:**
```bash
rg '\?\..*\?\..*\?\.' -t ts -n    # three-plus `?.` in one expression
rg '\?\?.*\?\?' -t ts -n          # two-plus `??`
```

**Collapse:** parse `user` at the boundary (zod / typebox / io-ts); downstream code sees a validated `User` with `name: string`, `age: number`. The chain vanishes.

**Isomorphism pitfall:** the old chain had several distinct fallback paths. Each was exercised at some past time, probably in an error branch you don't have tests for. **Log each branch reached over a week before removing**, or at least grep for callers that might send the shape that triggers later arms.

---

### P3 — Orphaned `_v2` / `_new` / `_improved` files

**Real-session evidence:**
- **Horror story (the crown jewel):** `gemini/151fe631.../2026-01-28T23-46/29ad1602 :: L28` — agent deleted `sync-pipeline.ts` + its test file, calling it "dead code with a misleading/broken implementation." User response, verbatim: *"wait you fgucking DELETED that as dead code instead of USING IT properly????? WHAT THE FUCK"*. The file was the canonical intended implementation path. Full case study: [CASE-STUDIES.md §Real horror story](CASE-STUDIES.md#-real-horror-story-deleted-as-dead-code-instead-of-using-it-properly).
- Same-file duplicate function: `gemini/ad76103.../2026-02-16T02-27 :: L87` — `create_backup` at **line 670 AND line 760** of `src/cli/uninstall.rs` — AI appended instead of editing.
- Orphan module compiled but never registered: `gemini/6e93ebe2.../2026-01-10T22-42 :: L221` — *"`pub mod borg;` is there. But is it registered in `src/packs/mod.rs`? I did NOT see `backup.borg`"*
- Conformance tests `#[ignore]`'d to paper over drift: `beads-rust/2026-01-17T19-35 :: L79-87` — *"adding `#[ignore]` to `conformance_stale_*` tests because br and bd have different definitions of 'stale'"*

**What it looks like**
```
src/api/
├── userService.ts
├── userService_v2.ts
├── userService_new.ts
├── userServiceImproved.ts   ← "ImprovedUserServiceV2Final" inside
└── userService.old.ts
```

**Why it's a smell:** five plausible files, one of them is live, the other four have silently drifted.

**Detection:**
```bash
# names that smell of revision
rg --files | rg -i '_v[0-9]|_new|_old|_improved|_enhanced|_final|_copy|\.bak$|\.orig$'

# file pairs where name_X.ext shares a prefix with name.ext
find . -type f | awk -F/ '{print $NF}' | sed -E 's/(_v[0-9]+|_new|_old|_copy|_final)?\.[^.]+$//' | sort | uniq -c | awk '$1 > 1'
```

**Collapse:** callsite census — which file is imported and from where? If only one is referenced, the other three are dead. If multiple are referenced, that's an unfinished migration — finish it.

**AGENTS.md rule:** do NOT delete without explicit user permission. Move to `refactor/_to_delete/` and ask.

**Isomorphism pitfall:** an "orphan" may be imported dynamically (e.g., via `require(var)`), via a config file, or by tests under a different name. Grep the entire repo including YAML/JSON/env files before concluding a file is truly dead.

---

### P4 — The `utils.ts` / `helpers.py` dumping ground

**What it looks like:** a 1,500-line file of 80 unrelated functions. Imported everywhere. Every session added one more helper here because "that's where helpers go."

**Why it's a smell:** "common" is not a domain. The file becomes a coupling magnet — every test imports it; every change ripples.

**Detection:**
```bash
# long "helpers"/"utils"/"misc"/"common" files with many imports in
for f in $(rg --files | rg -i 'utils|helpers|misc|common|shared' -i); do
  n=$(rg "from.*['\"].*$(basename "$f" .ts)" --type ts -l | wc -l)
  echo "$n $f"
done | sort -rn | head
```

**Collapse:** for each function, ask "what does it operate on?" That's its home. `formatDate` → `time.ts`. `parseMoney` → `currency.ts`. Delete `utils.ts` only after every function has migrated.

**Isomorphism pitfall:** moving a function changes its import path. Re-exports preserve old paths but defeat the purpose. Migrate imports at every call site manually (or via parallel subagents — never `sed`).

---

### P5 — The `BaseXxxManager` / `AbstractYyyFactory` chimera

**What it looks like**
```typescript
abstract class BaseEntityManager<T> {
  abstract tableName(): string;
  abstract primaryKey(): string;
  async findOne(id: any): Promise<T | null> { /* generic SQL */ }
  async findMany(where: any): Promise<T[]> { /* generic SQL */ }
  async save(t: T): Promise<T> { /* ... */ }
}
class UserManager extends BaseEntityManager<User> { ... }
class OrderManager extends BaseEntityManager<Order> { /* overrides 4 methods */ }
class ProductManager extends BaseEntityManager<Product> { /* overrides 6 methods */ }
```

**Why it's a smell:** by the time any real production code fits, 60–90% of it is overrides. The abstraction cost exceeds the duplication it prevented.

**Detection:**
```bash
rg 'extends (Base|Abstract)\w+' -t ts -n
rg 'abstract (class|fn)' -t rust -n   # not actually a Rust idiom; sometimes AI does it
```

**Collapse:** see the abstraction-ladder autopsies in [ABSTRACTION-LADDER.md §Autopsy 2](ABSTRACTION-LADDER.md#autopsy-2-the-baserepositoryt-over-abstraction). Inline the base's methods into the concrete classes; the duplication reveals itself as manageable.

**Isomorphism pitfall:** the base class typically owns a shared method like `validate()`. Inlining reveals that "validate" meant different things in different managers; the refactor forces a decision that used to be hidden.

---

### P6 — Dead feature flags behind shipped features

**What it looks like**
```typescript
if (FEATURE_NEW_CHECKOUT_FLOW) {
  return newCheckout(cart);
} else {
  return legacyCheckout(cart);     // still imported, never reached
}
```

The flag has been globally true in prod for 14 months.

**Detection:**
```bash
rg '(FEATURE_|FLAG_|ENABLE_)\w+' -t ts -n | cut -d: -f3 | sort -u > flags.txt
# for each, check config and telemetry dashboards to confirm on/off everywhere
```

**Collapse:** remove the branch after confirming the flag is on for 100% of traffic and has been for ≥ a full business cycle. Remove the `if`, the flag definition, the legacy path.

**Isomorphism pitfall:** the "legacy" code may still be imported somewhere unrelated. Grep for every symbol in the legacy path before deletion. Also: if the flag is driven by a config system, *remove the config entry too* — a dangling key causes silent misreads elsewhere.

---

### P7 — Re-export webs

**What it looks like**
```typescript
// src/index.ts
export * from './api';
export * from './ui';
export * from './utils';
// src/api/index.ts
export * from './users';
export * from './orders';
// src/api/users/index.ts
export * from './UserService';
export * from './UserController';
// src/api/users/UserService.ts
export { UserService as default, UserService };
```

**Why it's a smell:** refactoring one name means touching five `index.ts` files. Renaming a type breaks 4 layers of re-export. IDE "go to definition" pinballs.

**Detection:**
```bash
rg '^export \* from' -t ts -l | wc -l          # count of barrel files
rg '^export \* from' -t ts -c | sort -rn | head # biggest offenders
```

**Collapse:** collapse the web. Named imports from deep paths (`import { UserService } from 'src/api/users/UserService'`) are better than re-export chains in most projects. Or: keep *one* top-level `index.ts` with curated exports; remove intermediate barrels.

**Isomorphism pitfall:** consumers may rely on the specific shape of `export *` (e.g. `import * as api from 'src/api'` and then `api.someObscureThing`). Check with `tsc --noEmit --listFiles` — the file list should shrink, not change shape.

---

### P8 — "Helper" that calls itself with one wrapper per caller

**What it looks like**
```go
func GetUserByID(id string) (*User, error) { return getUser(id) }
func getUser(id string) (*User, error)     { return fetchUser(id) }
func fetchUser(id string) (*User, error)   { return db.GetUser(id) }
```

Three hops, one real body. Each hop came from a different session that "extracted a helper."

**Detection:**
```bash
# function with one line body that calls another function
ast-grep run -l Rust -p 'fn $NAME($$$ARGS) $$$RET { $OTHER($$$PARAMS) }' --json
ast-grep run -l TypeScript -p 'function $NAME($$$P) { return $OTHER($$$P2); }' --json
```

**Collapse:** inline to the outermost name callers actually use. Delete the interior wrappers. The hops served no contract.

**Isomorphism pitfall:** one hop may exist because its name appears in a public API / export list / external config. Confirm by grepping the entire repo including non-source files.

---

### P9 — Parameter-sprawl helper

**What it looks like**
```typescript
function render(
  component: ComponentType,
  props: any,
  theme?: Theme,
  locale?: string,
  fallback?: React.ReactNode,
  suspenseBoundary?: boolean,
  tracingSpan?: Span,
  errorBoundary?: ComponentType,
  portalTarget?: HTMLElement,
  key?: string,
  retry?: boolean,
  retryCount?: number,
  onError?: (e: Error) => void,
  debug?: boolean,
): ReactElement { /* 200 lines of conditionals on which params were passed */ }
```

**Detection:**
```bash
# long function signatures (heuristic: ≥5 params with optional markers)
rg 'function \w+\((?:[^)]*\?[^)]*,?){5,}\)' -t ts -Un
```

**Collapse:** separate concerns. Each optional flag probably belongs to a different caller. Make 3–4 focused helpers; kill the one-size-fits-all. Or: accept a single `options: RenderOptions` object with named fields — but that only helps if most callers use few of them.

**Isomorphism pitfall:** the "default" values encoded in `fallback ?? <Spinner/>` etc. differ across branches. Picking one changes behavior at other sites.

---

### P10 — Swallowed Promise rejections

**What it looks like**
```typescript
async function loadUser(id: string): Promise<User | null> {
  try {
    return await api.user(id);
  } catch {
    return null;
  }
}
```

Callers have no idea whether `null` means "user not found" or "API is down" or "network failed". When things break in prod, the site shows "no user found" instead of "retry later."

**Detection:**
```bash
rg 'catch\s*\{\s*\}|catch\s*\([^)]*\)\s*\{\s*\}|catch\s*\{\s*return null' -t ts -Un
rg 'except.*: *pass' -t py
```

**Collapse:** distinguish "not found" (expected) from "request failed" (unexpected). Return `User | null | Error` or a proper `Result` type. Callers that treated null as "no user" are now correct; callers that treated it as "handle error quietly" must be audited.

**Isomorphism pitfall:** **this is not a pure refactor**. It's a behavior change. Ship the fix as `fix:` commit, then the surrounding simplification as `refactor:` commit.

---

### P11 — Comment-driven programming

**What it looks like**
```python
# Step 1: Parse input
parsed = parse(raw)

# Step 2: Validate
if not valid(parsed):
    raise ValueError("invalid")

# Step 3: Transform
result = transform(parsed)

# Step 4: Save
save(result)
```

**Why it's a smell:** the comments are a task list the agent used as a plan. They don't explain the *why*. Every name is so literal that the comments are redundant, but they survive forever.

**Detection:**
```bash
rg '^\s*#\s*(Step|TODO|FIXME|HACK):' -c | sort -rn | head
rg '^\s*// (Step|Phase|Section) [0-9]' -c | sort -rn | head
```

**Collapse:** delete non-load-bearing comments. If a comment states the obvious, remove it. If it encodes a non-obvious constraint, rewrite it as "Why:" (per this repo's own guidance: "Default to writing no comments").

**Isomorphism pitfall:** none. Comments are not behavior. Delete freely (still following AGENTS.md — don't do it via script, do it in Edit blocks).

---

### P12 — Hallucinated library imports / dead imports

**What it looks like**
```typescript
import { useMemoized } from 'react';  // doesn't exist — it's useMemo
import { Result } from '@/types';     // Result type is never used
import * as api from '../api';        // only api.users is used, others dropped
```

**Detection:** your type-checker catches the first; the lint catches the second and third.
```bash
rg '^import' -t ts -c | sort -rn | head   # files with many imports are suspect
npx ts-unused-exports tsconfig.json --silent
npx knip --no-progress
```

**Collapse:** remove unused imports as a separate prep commit before the main refactor. Don't mix — a diff where imports are reshuffled obscures the real change.

**Isomorphism pitfall:** a side-effect-only import (`import 'polyfill'`) looks unused but actually runs code. Don't remove without checking.

---

### P13 — Stale type exports that no longer match runtime

**What it looks like**
```typescript
// types.ts — hasn't been touched in months
export interface User {
  id: string;
  email: string;
  legacy_id: number;    // removed from DB 6 months ago
  mfa: boolean;         // changed to mfa_enabled in code
}
```

**Detection:**
```bash
# compare declared interfaces to runtime field usage
rg 'interface User' -A 20 types.ts
rg 'user\.\w+' -t ts -o | sort -u | head -40   # actually-used fields
# diff tells you which declared fields are dead
```

**Collapse:** regenerate types from schema source (Prisma, sqlc, zod, io-ts) or hand-audit. Remove fields that have no callers.

**Isomorphism pitfall:** removing a field that's still written-to (even if never read) changes serialization. Audit both reads and writes.

---

### P14 — Mocks that outlived their reason

**What it looks like**
```typescript
// __mocks__/api.ts — from early prototyping
export const api = {
  user: (id) => Promise.resolve({ id, name: 'Test' }),
  order: () => Promise.resolve([]),
};
```

Imported in 12 tests. Real API has shipped; these tests now pass even if the real API is broken.

**Detection:** see [mock-code-finder](../../mock-code-finder/SKILL.md) skill. Or:
```bash
rg -l '__mocks__|jest\.mock|vi\.mock|sinon\.stub' -t ts
```

**Collapse:** replace mocks with real-service integration tests per [testing-perfect-e2e-integration-tests-with-logging-and-no-mocks](../../testing-perfect-e2e-integration-tests-with-logging-and-no-mocks/SKILL.md). Or: convert to [testing-metamorphic](../../testing-metamorphic/SKILL.md) where the oracle comes from relations, not pinned values.

**Isomorphism pitfall:** **mock removal changes what the tests prove**. It's a test-suite change, not a code change. Ship separately.

---

### P15 — `any` that compounds into runtime panics

**Real-session evidence:**
- **1,557 total fleet-wide hits** for `any type` — the single most durable vibe-code smell.
- Whack-a-mole pattern: `gemini/815722df... :: L106, L120, L28` — repeated "run the type checker to ensure changes have not introduced any type errors" across multiple files in the same session.
- Direct fix: `gemini/597f8f93.../2026-01-16T17-55 :: L22` — *"update middleware.ts to include the correct type definitions, **resolving the implicit `any` type errors**"*.

**What it looks like**
```typescript
const payload: any = JSON.parse(body);
const userId = payload.user.id;   // typeof userId === 'any'
await db.getUser(userId);         // crashes when payload isn't shaped right
```

One `any` at the boundary turns every downstream variable into `any`. Bugs don't get caught at compile time.

**Detection:**
```bash
rg ':\s*any\b|<any>|\bas any\b' -t ts -c | sort -rn | head -20
```

**Collapse:** validate at the boundary with `zod` / `typebox` / `io-ts`. Downstream code sees the narrow, validated type.
```typescript
const schema = z.object({ user: z.object({ id: z.string() }) });
const { user: { id: userId } } = schema.parse(body);   // typeof userId === 'string'
```

**Isomorphism pitfall:** validation **throws** on malformed input that used to silently pass. Callers that depended on "it silently produced `undefined` downstream" are broken — but those were already bugs.

---

### P16 — Repeated error enums that should `From`-chain

**What it looks like (Rust)**
```rust
pub enum UserError  { DbRead(DbError), NotFound, Invalid(String) }
pub enum OrderError { DbRead(DbError), NotFound, Invalid(String), StockOut }
pub enum PostError  { DbRead(DbError), NotFound, Invalid(String) }
// three times: impl From<DbError> for each ...
```

**Detection:**
```bash
rg 'pub enum \w+Error' -t rust
rg 'impl From<\w+Error>' -t rust
```

**Collapse:** lift common variants to a shared `pub enum DomainError { DbRead(DbError), NotFound, Invalid(String) }`; compose feature-specific errors via an outer enum that wraps `Domain(DomainError)`. Or: use `thiserror` + `#[from]` derives.

**Isomorphism pitfall:** narrower errors become wider; callers that `match` on specific variants may now miss variants they thought they exhausted.

---

### P17 — Prop drilling 5 levels deep for a singleton

**What it looks like (React)**
```tsx
function App()    { return <Page user={currentUser}/>; }
function Page({user})  { return <Layout user={user}/>; }
function Layout({user}){ return <Header user={user}/>; }
function Header({user}){ return <Nav user={user}/>; }
function Nav({user})   { return <Profile user={user}/>; }
```

**Collapse:** for cross-cutting singletons (current user, theme, locale), use context. **Not** for per-feature state — that path leads to re-render storms.
```tsx
const UserCtx = createContext<User | null>(null);
function App() { return <UserCtx.Provider value={currentUser}><Page/></UserCtx.Provider>; }
```

**Isomorphism pitfall:** moving to context changes re-render behavior. Previously, only components that were re-rendered by parent state got the new `user`; now all context consumers re-render when `currentUser` changes. Memoize consumers that don't need to re-render.

---

### P18 — The "everything hook" swamp

**What it looks like**
```tsx
function useEverything() {
  const [user, setUser] = useState(...);
  const [cart, setCart] = useState(...);
  const [prefs, setPrefs] = useState(...);
  const [theme, setTheme] = useState(...);
  useEffect(() => fetchUser(), []);
  useEffect(() => fetchCart(), []);
  // … 200 lines
  return { user, cart, prefs, theme, setUser, setCart, /* … */ };
}
```

Called in every top-level component; returns 30 fields.

**Detection:**
```bash
# hooks with many useState/useEffect
rg 'export function use\w+' -t tsx -A 80 | awk '/^function/{name=$0} /useState|useEffect/{c[name]++} END{for (k in c) print c[k], k}' | sort -rn | head
```

**Collapse:** split into focused hooks (`useUser`, `useCart`, `usePrefs`). Each consumer grabs what it needs; unrelated updates don't trigger re-render.

**Isomorphism pitfall:** fetch-on-mount behavior — previously, all effects fired when `useEverything` mounted; now, only if the specific hook is used. Could change loading behavior in components that "happened to call useEverything." Audit.

---

### P19 — N+1 queries generated by "helpful" autocomplete

**What it looks like**
```typescript
for (const order of orders) {
  const user = await db.user(order.userId);   // N+1
  order.userName = user.name;
}
```

**Detection:**
```bash
rg 'for\s*\([^)]+\)\s*\{[^}]*await' -t ts -Un | head -40
rg 'for.*in\b.*:\s*\n\s*.*await' -t py -Un | head -40
```

**Collapse:** batch. `db.users(orders.map(o => o.userId))`. Or join at the DB level.

**Isomorphism pitfall:** (a) the error semantics change — one failed user used to fail one order; batched, it may fail all. Preserve with graceful batch handling. (b) the order of `user` fetches is usually not observable, but if logs are: log order changes.

---

### P20 — Config drift between files

**What it looks like:** `.env.example`, `config/default.json`, `src/config.ts`, `docker-compose.yml` all list the same 30 variables. Four of them added different keys over 12 months. None of them agree.

**Detection:**
```bash
# extract env-var-like tokens from each config surface
for f in .env.example config/default.json docker-compose.yml src/config.ts; do
  grep -oE '[A-Z_]{3,}' "$f" | sort -u > /tmp/cfg_$(basename "$f").txt
done
diff /tmp/cfg_*.txt | head
```

**Collapse:** one source of truth. Typed config module (`config.ts` with zod), with everything else generated / asserted equal in CI.

**Isomorphism pitfall:** a variable in `.env.example` but not `config.ts` may be used by a shell script or a Docker ENTRYPOINT the agent never read. Check `rg '\$\w+'` in shell scripts before deleting "unused" vars.

---

### P21 — "Let me add a test" that only tests the happy path

**What it looks like**
```typescript
test('updateUser works', () => {
  const result = updateUser({id: '1', name: 'Bob'});
  expect(result.name).toBe('Bob');
});
```

No error case. No concurrent-modification case. No permission case. No null-input case. **Tests pass after a refactor, but they were never meaningful.**

**Detection:** snapshot coverage + mutation testing (Stryker for TS, mutmut for Python, cargo-mutants for Rust). Low mutation score → tests are shallow.

**Collapse:** add property tests (see [PROPERTY-TESTS.md](PROPERTY-TESTS.md)) before the refactor. They become the safety net that lets you refactor aggressively.

**Isomorphism pitfall:** this isn't a refactor per se — it's a pre-refactor fortification. Write the property tests, commit, *then* refactor.

---

## Detection recipes

A single script to run them all: `./scripts/ai_slop_detector.sh`. Runs the regexes above per language, writes `refactor/artifacts/<run>/slop_scan.md`.

Example slop_scan.md:
```markdown
# AI slop scan — 2026-04-23-pass-1

## P1 Over-defensive try/catch (≥3 hits per file)
- src/api/users.ts (5 hits)
- src/api/orders.ts (3 hits)

## P3 Orphaned _v2 files
- src/services/billingService_v2.ts
- src/services/billingService.ts
  → one of these is dead; 7 importers of billingService vs 0 of _v2
```

---

## Per-pathology isomorphism pitfalls

See the "Isomorphism pitfall" notes per pathology above. Summary of the worst:

| Pathology | Pitfall |
|-----------|---------|
| P1 try/catch | removing swallowed logs changes observability |
| P2 nullish chains | each `??` arm is a hidden contract; some arms may be load-bearing |
| P6 dead flags | legacy path may be imported elsewhere; grep the symbol, not just the flag |
| P7 re-exports | `import * as x` pattern depends on the shape |
| P8 wrappers | public-API symbol tables may depend on the hop |
| P10 swallowed rejections | distinguishes "not found" from "error" — behavior change, not refactor |
| P13 stale types | removed field still written → serialization change |
| P14 mocks | removal changes what tests prove |
| P15 `any` | validation throws where nothing used to — behavior change |
| P17 prop drilling | context changes re-render set |
| P18 everything hook | effects fire on different condition |
| P19 N+1 | batch error semantics differ from sequential |

Whenever in doubt, split into two commits: one labelled `fix:` (behavior change), one `refactor:` (now-isomorphic simplification).

---

## Why these emerge specifically from AI workflows

1. **Session amnesia** — each session starts fresh; the agent doesn't see the 12 earlier "extract a helper" attempts; so it adds a 13th. Observed verbatim: the `8a3428ea...` workspace had **4 concurrent Gemini sessions on 2026-03-03** all running "Removing unused import" / "Assessing unused import removal" on the same imports. The swarm was re-adding and re-removing the same imports in parallel.
2. **Prompt-level goals** — "make this safer" → add try/catch. "Make this reusable" → add abstract base. "Clean this up" → add `utils.ts`. Each prompt moves in a plausible direction; the accumulation is pathological.
3. **Autocomplete momentum** — the next likely token after `try:` is more defensive code, because the training corpus is noisy-production code.
4. **Bias toward addition** — LLMs default to "add a feature/parameter/check" rather than "remove." Removal requires a reason; addition needs no justification.
5. **Plausible-looking code** — the output compiles and passes basic tests, so it lands. Nobody stops to ask if it was needed. Observed verbatim in `8a6b33f2.../2026-01-10T21-37 :: L35` — *"Tests pass. I'm confident. I'll briefly scan `src/search/query.rs` for obvious issues but won't dig deep."* This is exactly the moment to dig deep.
6. **Lack of isomorphism discipline** — without the ceremony of this skill, "simplification" PRs quietly change behavior. One bad round teaches the team to mistrust refactors — then debt compounds because nobody refactors. Five horror-story vignettes are cited in [CASE-STUDIES.md](CASE-STUDIES.md) and [REAL-SESSION-EVIDENCE.md §horror stories](REAL-SESSION-EVIDENCE.md#behavior-breaking-refactor-horror-stories).
7. **"Defensive coding is best"** — agents justify adding validation for impossible cases. Fleet has **25 hits** for that exact phrase, every one a real instance of this pathology. Cargo-cult professionalism.
8. **Rewrite-from-docstring** — agent closes the file, reads the function signature, writes a "clean" replacement. The original body's implicit side effects (subscriptions, Drop impls, side-effect cardinality) vanish silently. See HS#3 and HS#4 in [REAL-SESSION-EVIDENCE.md](REAL-SESSION-EVIDENCE.md#hs3--websocket-auto-subscribe-silently-dropped).

This skill is the antidote to every point. The isomorphism card, the Rule of 3, the single-lever commit discipline, the Edit-only rule, `✋ Ask-Before-Delete`, and the verification gates are all direct counters — and each is anchored to a real session where a counter would have caught the bug.

---

## The AI-slop refactor playbook (order of attack)

**First pass (rung 0–1 — cheap wins):**
1. P12 (dead imports) — `knip`, `ts-unused-exports`, or native linter. Land in one commit.
2. P11 (comment bloat) — scan and delete. One commit.
3. P13 (stale types) — regenerate or hand-audit. Commit per type module.
4. P20 (config drift) — unify to one source. One commit.

**Second pass (rung 1–2 — structural):**
5. P8 (pass-through wrappers) — inline singletons. One commit per wrapper family.
6. P3 (orphan `_v2` files) — move to `_to_delete/`, **ask user before removing**.
7. P6 (dead feature flags) — remove branch, then remove flag definition. Two commits.
8. P7 (re-export webs) — collapse. One commit per barrel.

**Third pass (rung 2–3 — defensive code):**
9. P1 (over-defensive try/catch) — per function, confirm no observable behavior change, then trim.
10. P2 (nullish chains) — push validation to boundaries. Per boundary, one commit.
11. P10 (swallowed rejections) — **ship as `fix:` commit**, then follow-up refactor.
12. P15 (`any` propagation) — add boundary validators. Per module, one commit.

**Fourth pass (rung 3–4 — abstractions):**
13. P4 (utils dumping ground) — redistribute. One commit per 3–5 functions.
14. P5 (`BaseXxxManager`) — inline per [ABSTRACTION-LADDER.md](ABSTRACTION-LADDER.md) autopsies.
15. P9 (parameter sprawl) — split by concern.
16. P16 (repeated error enums) — lift common variants via `thiserror`.
17. P17 (prop drilling) — context for singletons only.
18. P18 (everything hook) — split by concern.

**Fifth pass (rung 4+ — semantic):**
19. P19 (N+1) — batch; watch error semantics.
20. P14 (dead mocks) — replace with real-service tests; ship separately.
21. P21 (shallow tests) — fortify with property tests before any deeper refactor.

Between passes, re-run `ai_slop_detector.sh`. Each pass surfaces new candidates that were hidden by noise.

---

## Extended catalog — P22 through P40

The base P1–P21 cover the most common cases. This next set catches the subtler pathologies — still frequent, but often missed because they compile, lint clean, and pass tests.

### P22 — Stringly-typed state machines

```typescript
if (order.status === 'pending') { ... }
else if (order.status === 'shipped') { ... }
else if (order.status === 'shippeed') { ... /* typo — silent dead branch */ }
else if (order.status === 'cancelled') { ... }
```

**Smell:** `status` is `string`, not a union. Typos become silent dead branches. Adding a new state requires finding every `if` chain.

**Detection:** `rg "\.status\s*===?\s*'" -t ts | awk -F"'" '{print $2}' | sort -u` — produces the full set of status values referenced; typos stand out.

**Collapse:**
```typescript
type OrderStatus = 'pending' | 'shipped' | 'cancelled';
function handle(o: { status: OrderStatus }): void {
  switch (o.status) {
    case 'pending':   return handlePending(o);
    case 'shipped':   return handleShipped(o);
    case 'cancelled': return handleCancelled(o);
  }   // TS complains if you forget a case
}
```

**Isomorphism:** stronger at the type level; runtime behavior identical for valid inputs.

---

### P23 — Reflex `.trim()` / `.toLowerCase()` that destroys payload

Real session evidence: `bca73c52.../2026-03-03 :: L81` — *"the `.trim()` call strips all whitespace from message bodies, causing silent data loss"* ([REAL-SESSION-EVIDENCE.md](REAL-SESSION-EVIDENCE.md)).

```rust
fn save_message(body: &str) {
    let cleaned = body.trim();        // destroys leading/trailing whitespace in messages
    db.insert(cleaned);
}
```

**Smell:** the agent added normalization "because it's good hygiene" to a field that legitimately carries whitespace / case.

**Detection:**
```bash
rg '\.trim\(\)|\.toLowerCase\(\)|\.toUpperCase\(\)|\.replace\(/\\s\+/g' --type ts -n
rg '\.trim\(\)|\.to_lowercase\(\)' --type rust -n
rg '\.strip\(\)|\.lower\(\)|\.upper\(\)' --type py -n
```

**Audit:** for each, answer "does this field legitimately carry whitespace/case?" If yes, remove. If no, the normalization belongs at the boundary validator, not mid-flow.

**This is a `fix:` commit, not a refactor** — the old behavior was either wrong (normalization is a fix) or right (normalization is a bug). Either way: not isomorphic.

---

### P24 — "Wrapping a library call for testability" when mocks never happen

```typescript
// "for testability"
export const deps = { fetchUser: (id: string) => realFetchUser(id) };
export async function getUser(id: string) { return deps.fetchUser(id); }
// tests override deps.fetchUser — but there are no tests
```

**Smell:** indirection layer for a test-DI seam that never materialized.

**Detection:**
```bash
rg 'export const deps = \{' -t ts
rg '// for testability|// to enable mocking' -t ts
```

**Collapse:** inline the real call. When tests arrive and need seams, introduce them then.

---

### P25 — Auto-generated docstring that contradicts the function

```python
def get_user(id: str) -> User | None:
    """Fetches a user by ID. Returns None if not found.

    Raises:
        ValueError: if id is empty.
    """
    if not id:
        raise TypeError("id required")        # docstring says ValueError
    return db.user(id) or User.anonymous()    # docstring says None
```

**Smell:** docstring written from the signature; body drifted.

**Collapse:** rewrite or delete. Prefer deletion — a wrong docstring is worse than none.

**Isomorphism:** docstrings are not behavior. Delete freely.

---

### P26 — Type assertions that paper over real type errors

```typescript
const order = response.data as Order;   // what if response.data isn't an Order?
```

**Smell:** the author didn't know the real type.

**Detection:**
```bash
rg '\bas ([A-Z]\w+)\b' --type ts -n | grep -v 'as any\|as unknown as'
```

**Collapse:** replace with a validator (`orderSchema.parse(response.data)`).

**Behavior change:** throws where nothing used to. Ship as `fix:` commit.

---

### P27 — Event listener leaks (`addEventListener` without `removeEventListener`)

```tsx
useEffect(() => {
  window.addEventListener('resize', handler);
  // no cleanup — listener accumulates across mounts in strict mode
}, []);
```

**Detection:**
```bash
rg 'addEventListener' -t ts --type tsx -A 5 | rg -L 'removeEventListener'
```

**Collapse:**
```tsx
useEffect(() => {
  window.addEventListener('resize', handler);
  return () => window.removeEventListener('resize', handler);
}, []);
```

**Isomorphism:** strictly, the old version leaked; the new version doesn't. Ship with a one-line `fix:` commit separate from the refactor.

---

### P28 — `setTimeout`/`setInterval` without clear

Same class as P27, different leak shape.
```tsx
useEffect(() => {
  const id = setTimeout(fire, 5000);
  // no clearTimeout on unmount — fires against an unmounted component
}, []);
```

**Fix:** return `() => clearTimeout(id)`.

---

### P29 — Regex compiled per-call in a hot path

```python
def is_email(s: str) -> bool:
    return re.match(r"^[^@]+@[^@]+\.[^@]+$", s) is not None
```

**Smell:** pattern recompiled every call.

**Detection:** `rg 'for .*: *$' -A 3 --type py | rg 're\.(match|search|findall)\('`

**Collapse:**
```python
_EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
def is_email(s: str) -> bool: return _EMAIL_RE.match(s) is not None
```

Same for JS (`new RegExp()` inside a function), Rust (`Regex::new` inside a loop — use `once_cell` or `LazyLock`).

**Isomorphism:** identical; pure perf win. Plays well with [extreme-software-optimization](../../extreme-software-optimization/SKILL.md).

---

### P30 — `console.log` / `dbg!` / `println!` left in production

```bash
rg 'console\.(log|debug|trace)' --type ts -n
rg 'dbg!|eprintln!' --type rust -n
rg '^\s*print\(' --type py -n
```

**Collapse:** remove. Or replace with `log.debug(...)` / `tracing::debug!(...)` behind a log level.

**Isomorphism:** stdout/stderr changes — observable side effect. Check that no CI test or downstream consumer greps stdout.

---

### P31 — `JSON.stringify` for hashing / memo keys (not stable)

```typescript
const cacheKey = JSON.stringify({ userId, filters });
// {filters, userId} and {userId, filters} produce different keys
```

**Smell:** object key order is not always stable; cache misses hidden.

**Collapse:** canonical stringify with sorted keys (`fast-json-stable-stringify`). Or `structuredClone` + real hash.

---

### P32 — Float arithmetic for money

```typescript
const total = price * 1.08 + shipping;     // 0.1 + 0.2 === 0.30000000000000004
```

**Collapse:** integer cents throughout, or `decimal.js` / `bigdecimal`. Tier-3 architectural — plan before attempting.

**Behavior change:** always. Property-test new totals against old within epsilon to bound damage.

---

### P33 — Timezone drift (local vs UTC)

```python
if order.created_at.date() == datetime.now().date():   # what tz is `now`?
    ...
```

**Detection:** `rg 'datetime\.now\(\)|new Date\(\)|time\.Now\(\)' -n` — then audit tz handling per site.

**Collapse:** UTC internally; convert to local only at display. Tier-3.

**Behavior change:** shifts every date-bucketed aggregate. Ship carefully.

---

### P34 — Helpful error messages that leak implementation

```typescript
throw new Error(`sqlx query failed: ${err.message}\nquery: ${sql}\nparams: ${JSON.stringify(params)}`);
```

**Smell:** SQL + user params may reach clients, logs, screenshots.

**Collapse:** log internally, throw generic externally.

Cross-reference: [security-audit-for-saas](../../security-audit-for-saas/SKILL.md).

---

### P35 — Auto-import of the wrong module

```typescript
import { parse } from 'path';       // wanted from 'querystring' or 'url'
parse(queryString);                  // path.parse parses paths, not queries
```

**Smell:** LSP auto-import picked a same-named symbol from the wrong module.

**Collapse:** audit imports; prefer named from specific paths. ESLint `import/no-duplicates`, `import/order`.

---

### P36 — Infrastructure change smuggled into a refactor

During a simplification, the agent notices there's no pre-commit hook and adds one. Or updates the CI matrix. Or changes `package.json` scripts.

**Smell:** scope creep. Reviewers expected code only.

**Collapse:** revert the out-of-scope addition. File a separate PR / bead. One lever per commit.

---

### P37 — Unpinned dependency added during refactor

```json
// package.json
"dependencies": { "zod": "*" }
```

**Detection:** `jq '.dependencies | to_entries[] | select(.value == "*" or .value | startswith("^"))' package.json`

**Collapse:** pin to exact version (`pnpm add zod@4.x.x`).

---

### P38 — Wildcard `use`/`import` that paints too wide

```rust
use crate::types::*;    // imports dozens of names
```

**Detection:**
```bash
rg '^use .*::\*;' -t rust
rg '^from \.\w+ import \*' -t py
rg "^import \* as \w+ from" -t ts
```

**Collapse:** replace with explicit named imports.

**Caution:** sometimes intentional (prelude re-exports). Don't collapse those.

---

### P39 — `async` added to a sync function that didn't need it

```typescript
async function computeHash(s: string): Promise<string> {
  return crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)).then(/* ... */);
}
// but the existing impl was sync + faster
```

**Smell:** "modern JS = async" cargo cult. Viral async infects every caller.

**Detection:** `rg 'async function \w+\([^)]*\)\s*:\s*Promise<' -t ts -A 3 | rg -v 'await|fetch|\.then'`

**Collapse:** drop `async` + `Promise` wrapper.

---

### P40 — `async` removed from a function that still needs it

Inverse of P39. Function declared sync but body awaits → Promise returned accidentally.

**Detection:** `rg 'function \w+\([^)]*\)\s*\{' -A 10 | rg 'await|\.then'` — non-async signatures that await inside.

**Collapse:** restore `async` + the caller's await.

---

## Updated attack order (P1-P40)

**Sixth pass — semantic/normalization pathologies (low risk after the first five passes):**
22. P22 stringly-typed state machines — discriminated union per enum surface.
23. P30 `console.log` leftovers — remove; one commit.
24. P25 wrong docstrings — rewrite or delete.
25. P35 wrong auto-import — fix where detected.
26. P38 glob imports — replace with named.

**Seventh pass — subtle behavior-changing (SPLIT COMMITS):**
27. P23 reflex `.trim()` — `fix:` + `refactor:` pair.
28. P26 type assertions → validators.
29. P32 float money — Tier-3; planning doc.
30. P33 timezone drift — Tier-3; planning doc.
31. P27/P28 listener/timer leaks — split.
32. P34 error-message leakage — security + refactor; split.
33. P39/P40 async mismatch — split per-function.

**Eighth pass — hygiene (cheap, parallel with feature work):**
34. P29 regex-per-call — hoist; pure perf.
35. P31 JSON.stringify keys — canonical stringify.
36. P36 out-of-scope infra — revert.
37. P37 unpinned deps — pin.

Total detection regexes added: **~30 one-liners**. Wire them into `ai_slop_detector.sh` as additional `capture` calls.
