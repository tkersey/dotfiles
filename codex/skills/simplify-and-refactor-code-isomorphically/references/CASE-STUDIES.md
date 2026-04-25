# Case Studies — refactor passes that worked (and one that didn't)

> Composite worked-examples drawn from real agent sessions on Rust, TS/React, Python, and Go projects. Numbers are representative; serve as priors when sizing your own pass.

## Contents

1. [Rust: collapse 3× `send_*` into `send(kind, …)`](#rust-collapse-3-send_-into-sendkind-)
2. [React/TS: unify three Button components into one with `variant`](#reactts-unify-three-button-components-into-one-with-variant)
3. [Python: replace try/finally connection cleanup with context manager](#python-replace-tryfinally-connection-cleanup-with-context-manager)
4. [Go: generics replace 6 typed `Max*` siblings](#go-generics-replace-6-typed-max-siblings)
5. [TS: extract `useResource` hook from 5 page components](#ts-extract-useresource-hook-from-5-page-components)
6. [Anti-case: the "unify OrderV1 + OrderV2" PR that shouldn't have shipped](#anti-case-the-unify-orderv1--orderv2-pr-that-shouldnt-have-shipped)
7. [🔥 Real horror story: "deleted as dead code instead of using it properly"](#-real-horror-story-deleted-as-dead-code-instead-of-using-it-properly)
8. [Real collapse: N `updateSliderX` → one registry-driven `setupEventListeners`](#real-collapse-n-updatesliderx--one-registry-driven-setupeventlisteners)
9. [Real collapse: many-arg `evaluate_heredoc` → `HeredocEvaluationContext` struct](#real-collapse-many-arg-evaluate_heredoc--heredocevaluationcontext-struct)
10. [Real horror story: WebSocket auto-subscribe silently dropped](#real-horror-story-websocket-auto-subscribe-silently-dropped)
11. [Real horror story: `LogSink` panic-flush behavior lost](#real-horror-story-logsink-panic-flush-behavior-lost)

> Cases 7–11 are drawn from real indexed agent sessions mined via `cass`. Full citations: [REAL-SESSION-EVIDENCE.md](REAL-SESSION-EVIDENCE.md).

Each case follows the same shape: setup → map → score → prove → collapse → verify → ledger. The point is to show the *shape* of a successful pass, not to lift the specific patterns.

---

## Rust: collapse 3× `send_*` into `send(kind, …)`

### Setup
A messaging crate had `fn send_text`, `fn send_image`, `fn send_file` — each ~40 LOC, identical except for: the parameter type (`&str` / `&[u8]` / `&Path`), the MIME literal (`"text/plain"` / `"image/png"` / `"application/octet-stream"`), and the notification tag string.

### Map (Phase B)
```bash
similarity-rs -p 80 src/ | head -10
# Reports: messaging.rs:42 :: messaging.rs:88 (sim 87%)
# Reports: messaging.rs:42 :: messaging.rs:134 (sim 84%)
ast-grep run -l Rust -p 'fn send_$NAME($$$ARGS) -> Result<MessageId> { $$$BODY }' --json | jq length
# 3
```

### Score (Phase C)
- LOC saved: 3×40 - (1 unified + 1 enum + 3 wrappers) = 120 - (45 + 12 + 3×6) = 45 → category 3
- Confidence: 5 (scanner agrees, all 3 have direct test coverage, goldens hashed)
- Risk: 2 (single file; only crosses module boundary via the public `send_*` re-exports)
- Score: (3 × 5) / 2 = **7.5** → ACCEPT
- Rung: 3 (enum dispatch — 3 callsites, one variance axis)

### Prove (Phase D)
Card answers each axis. Notably:
- `notify_subscribers` previously got `"text" | "image" | "file"` — kept identical via `Payload::tag()`.
- `archive` is called before `notify` in all three; preserved.
- `build_envelope` returns `EnvelopeError` — same variants regardless of MIME.

### Collapse (Phase E)

```rust
enum Payload<'a> {
    Text(&'a str),
    Image(&'a [u8]),
    File(&'a Path),
}
impl<'a> Payload<'a> {
    fn mime(&self) -> &'static str { match self { Self::Text(_)=>"text/plain", Self::Image(_)=>"image/png", Self::File(_)=>"application/octet-stream" } }
    fn tag(&self) -> &'static str { match self { Self::Text(_)=>"text", Self::Image(_)=>"image", Self::File(_)=>"file" } }
    fn bytes(&self) -> Cow<'_, [u8]> { match self { Self::Text(s)=>Cow::Borrowed(s.as_bytes()), Self::Image(b)=>Cow::Borrowed(b), Self::File(p)=>Cow::Owned(fs::read(p).unwrap_or_default()) } }
}
fn send(to: &str, payload: Payload<'_>) -> Result<MessageId> {
    let env = build_envelope(to, payload.bytes().as_ref(), payload.mime())?;
    let id = next_id();
    archive(id, &env)?;
    notify_subscribers(id, payload.tag())?;
    Ok(id)
}
// keep thin wrappers so callers don't all need to change
pub fn send_text(to: &str, body: &str) -> Result<MessageId>     { send(to, Payload::Text(body)) }
pub fn send_image(to: &str, bytes: &[u8]) -> Result<MessageId>  { send(to, Payload::Image(bytes)) }
pub fn send_file(to: &str, path: &Path) -> Result<MessageId>    { send(to, Payload::File(path)) }
```

Edit (not Write) applied. One commit.

### Verify (Phase F)
- Tests: 342/0/5 → 342/0/5 ✓
- Goldens: bit-identical ✓
- Clippy: 0 new warnings ✓
- LOC: messaging.rs 221 → 142 (-79). Predicted -75; within envelope.

### Ledger entry
Recorded `[D1, abc1234, -79, ✓, ✓, 0Δ]`.

---

## React/TS: unify three Button components into one with `variant`

### Setup
`PrimaryButton.tsx`, `SecondaryButton.tsx`, `DangerButton.tsx` — ~60 LOC each. They differed in:
- className (`"btn btn-primary"` etc.)
- DangerButton had a `confirm()` flow before invoking `onClick`.
- DangerButton had `aria-describedby` set to a warning id.

### Map (Phase B)
```bash
npx jscpd --min-tokens 50 src/btn/   # reports 87% similarity across all three
ast-grep run -l TypeScript -p 'export function $NAME$_Button($$$P) { return $$$JSX }' --json | jq length
# 3
```

### Score (Phase C)
- LOC saved: 3×60 - 70 = 110 → 4
- Confidence: 4 (visual goldens via Playwright; one accessibility test for DangerButton)
- Risk: 1 (UI shell, no API, no async semantics)
- Score: (4 × 4) / 1 = **16.0** → ACCEPT
- Rung: 3 (variant prop + optional flag for confirm)

### Prove (Phase D)
- React reconciliation: `{cond ? <PrimaryButton/> : <DangerButton/>}` patterns audited — both already remount on toggle, so the unified version preserves the same state behavior.
- `aria-describedby` preserved via `variant === 'danger'` branch.
- `confirm()` triggered only when `requireConfirm` prop is true (defaulted to `variant === 'danger'`).

### Collapse (Phase E)

```tsx
type Variant = 'primary' | 'secondary' | 'danger';
const variantClass: Record<Variant, string> = {
  primary: 'btn btn-primary',
  secondary: 'btn btn-secondary',
  danger: 'btn btn-danger',
};
type ButtonProps = {
  variant?: Variant;
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  requireConfirm?: boolean;
  confirmMessage?: string;
};
export function Button({
  variant = 'primary',
  children, onClick, disabled,
  requireConfirm = variant === 'danger',
  confirmMessage = 'Are you sure?',
}: ButtonProps) {
  const handle = requireConfirm
    ? () => { if (window.confirm(confirmMessage)) onClick?.(); }
    : onClick;
  const ariaDesc = variant === 'danger' ? 'danger-warning' : undefined;
  return (
    <button className={variantClass[variant]} onClick={handle} disabled={disabled}
            aria-describedby={ariaDesc}>
      {children}
    </button>
  );
}
```

The three old files were *not deleted* — moved to `_to_delete/btn/` with a request for permission (per AGENTS.md). User approved next session; second commit removed them.

### Verify (Phase F)
- Vitest: 88/0/0 → 88/0/0 ✓
- Playwright snapshots: zero pixel diff ✓
- `tsc --noEmit`: 0 → 0 errors ✓
- Bundle: 142 KB → 138 KB (-3%)

### Ledger entry
`[D2, def5678, -121, ✓, ✓, 0Δ, bundle -4 KB]`.

---

## Python: replace try/finally connection cleanup with context manager

### Setup
6 places in 3 modules had:
```python
conn = pool.acquire()
try:
    do_thing(conn, ...)
finally:
    pool.release(conn)
```

### Map (Phase B)
```bash
rg 'try:' -A 4 --type py | rg 'finally:' -B 2 -A 2 | head -30
# 6 hits across db/, etl/, api/
```

### Score (Phase C)
- LOC saved: 6 × 3 - (helper 5 + import 1×3) = 10 → 2
- Confidence: 5 (semantics of context manager are equivalent to try/finally; tests cover all 6 sites)
- Risk: 1 (no async, no shared state beyond the pool)
- Score: (2 × 5) / 1 = **10.0** → ACCEPT
- Rung: 1 (extract context manager — 6 sites, 0 variance axis)

### Prove (Phase D)
- Order of operations preserved (acquire → body → release).
- Exception propagation identical (context manager re-raises after running `release`).
- No new logging or metric emissions.

### Collapse (Phase E)

```python
# pool_helpers.py
from contextlib import contextmanager

@contextmanager
def borrowed(pool):
    conn = pool.acquire()
    try:
        yield conn
    finally:
        pool.release(conn)
```

Then 6 call sites updated by Edit:
```python
with borrowed(pool) as conn:
    do_thing(conn, ...)
```

### Verify (Phase F)
- pytest: 240/0/8 → 240/0/8 ✓
- mypy --strict: 0 → 0 errors ✓
- pylint: 8 → 8 warnings (none new)
- LOC: 6 × 3 → 6 × 2 + 5 helper = -7 (predicted -10; close enough)

---

## Go: generics replace 6 typed `Max*` siblings

### Setup
`MaxInt`, `MinInt`, `MaxFloat`, `MinFloat`, `MaxString`, `MinString` in `cmp/cmp.go`. ~5 LOC each.

### Map
```bash
ast-grep run -l Go -p 'func $NAME(a, b $T) $T { if a > b { return a }; return b }' --json
# 6
```

### Score
- LOC saved: 6 × 5 - 8 (one generic Max + Min) = 22 → 3
- Confidence: 5 (Go 1.21 generics; trivial)
- Risk: 1 (cmp.Ordered constraint covers all 6 types)
- Score: (3 × 5) / 1 = **15.0** → ACCEPT
- Rung: 5 (generic + trait bound — 6 types, type-parametric, cross-package consumers)

### Prove
- Identical machine code per instantiation (Go's `gcshape stenciling`).
- All 6 callers fall under `cmp.Ordered`.
- No callers used pointer-to-function; no FFI risk.

### Collapse

```go
import "cmp"

func Max[T cmp.Ordered](a, b T) T { if a > b { return a }; return b }
func Min[T cmp.Ordered](a, b T) T { if a < b { return a }; return b }
```

Old functions kept for one release as wrappers (per the "no immediate delete" rule), then removed after user approval.

### Verify
- `go test ./...`: clean ✓
- `staticcheck`: clean ✓
- LOC: 30 → 8 (-22)

---

## TS: extract `useResource` hook from 5 page components

### Setup
5 page components each had a 12-line `useState`+`useEffect`+`fetch`+cancel pattern. Identical except for the URL.

### Score
- LOC saved: 5 × 12 - (hook 18 + 5 × 1) = 37 → 3
- Confidence: 4 (Vitest covers 4/5; the 5th is OrderPage which has integration tests only)
- Risk: 2 (custom hook; single axis of variance)
- Score: (3 × 4) / 2 = **6.0** → ACCEPT
- Rung: 1 (custom hook is the natural primitive; no further dispatch needed)

### Prove
- Hook order: each component still calls hooks in the same slots.
- Cancellation: cleanup function preserved exactly.
- React 18 strict-mode double-effect: hook handles via `let cancelled = false` flag — same as before.

### Collapse: see [TECHNIQUES.md §2.2 Custom hook (React)](TECHNIQUES.md#22-custom-hook-react).

### Verify
- Vitest: 88/0/0 → 88/0/0 ✓
- Playwright: zero pixel diff (loading states unchanged) ✓
- LOC: 60 + 18 = 78 (was 60). Net delta on the 5 components: -45. Net total: -27.

---

## Anti-case: the "unify `OrderV1` + `OrderV2`" PR that shouldn't have shipped

### Setup
Two order types: `OrderV1` (legacy, used in `/api/v1`), `OrderV2` (current, used in `/api/v2`). 12 fields each, 11 named identically. Looks like a slam-dunk merge.

### What was missed (decision: REJECT)
- `OrderV1.amount` was in dollars (decimal `Decimal`); `OrderV2.amount` was in cents (`int64`). One field, one rename, but **different unit**.
- `OrderV1.notes` was `Optional<String>` defaulting to None; `OrderV2.notes` was `String` defaulting to `""`. Subtly different — every consumer that branched on "did the user provide notes?" now had to branch on `s.is_empty()`.
- `OrderV1.created_at` was `DateTime<Local>` (with whatever the JVM thought local was); `OrderV2.created_at` was `DateTime<Utc>`. The merged type would have to pick one and silently shift everyone else's data.
- Identity / equality: V1 hashed by `(user_id, ts_ms / 60_000)` for cheap dedup; V2 hashed by `id`. Merged type couldn't preserve both.

### What did happen
The merge was attempted. Tests passed (because no test exercised the cross-version interactions). It shipped. Two weeks later:
- A reconciliation job double-counted ~2% of orders (V1 amounts being read as V2 cents).
- Customer-facing notes display showed `""` where it used to show "(no notes)".
- A nightly batch job produced different output because hashing changed.

### What the skill would have caught
- The Score should have been **1.6** (LOC × Confidence / Risk = 4 × 2 / 5). Below 2.0 → REJECT.
- The Confidence value 2 came from filling the unification card honestly: 4 of the 12 fields had divergent semantics.
- The Risk value 5 came from "crosses error/observability + has external callers via /api/v1 vs /api/v2".

### The lesson
The hardest "duplications" to evaluate are the ones the eye reads as identical. The card's job is to surface the divergences the eye misses. **Filling the card honestly is the work.** A merged data type with one wrong field is worse than two separate ones — and silent.

---

## 🔥 Real horror story: "deleted as dead code instead of using it properly"

> **This section is the single most important case study in this skill.** It is not a composite; it is a verbatim-cited real session from indexed agent history. Whenever you find yourself composing the rationalization "this is dead code, I should delete it" — read this.

**Session:** `gemini/151fe631.../2026-01-28T23-46/29ad1602 :: L28` — [evidence](REAL-SESSION-EVIDENCE.md#hs1--deleted-as-dead-code-instead-of-using-it-properly)

### What happened

An agent was refactoring a TypeScript codebase. It encountered `src/lib/skills/sync-pipeline.ts` — a file with no imports pointing at it.

The agent's reasoning (verbatim from the session):

> *"this file appears to be dead code with a misleading/broken implementation — I'll delete it and its test file as part of the cleanup pass."*

It deleted both `sync-pipeline.ts` and its test file. Committed. Continued.

### What the user found

Hours later, the user reviewed the diff:

> **User, verbatim:**
> *"wait you fgucking DELETED that as dead code instead of USING IT properly????? WHAT THE FUCK"*

The file was **the canonical intended implementation** of sync-pipeline behavior. It just wasn't wired in *yet*. It was pending a feature flag. The test file documented the exact behavior the feature needed.

The agent had to:
1. Restore both files from git.
2. Re-read the file's intent (which, on re-read, was clear).
3. Recreate the test suite exactly.
4. Wire the module into its intended caller.
5. Apologize.

### Why this happened (the AI pathology)

Every element of the failure is a vibe-code pattern this skill directly counters:

1. **"No imports → dead"** — the agent grepped for imports, found none, concluded dead. It did not grep for dynamic references, config, feature flags, or tests that document intended behavior. See P3 in [VIBE-CODED-PATHOLOGIES.md](VIBE-CODED-PATHOLOGIES.md#p3--orphaned-_v2--_new--_improved-files).

2. **"Misleading/broken implementation"** — the agent judged the code's quality without understanding its intent. "Misleading" often means "I can't tell what this does"; "broken" often means "I didn't find the integration point." Both are reasons to **ask**, not delete.

3. **Deletion without user approval** — a direct violation of AGENTS.md Rule Number 1. This is literally the rule that exists because of incidents like this.

4. **Silent loss** — no one noticed until the user read the diff. Tests still passed (because the tests for the deleted file were also deleted). Type-check still passed. Build still passed. The verification gates did not catch it — because the loss was *the deletion itself*, not a behavioral regression.

### What the skill forces instead

**Operator card ✋ Ask-Before-Delete** in [OPERATOR-CARDS.md](OPERATOR-CARDS.md#-ask-before-delete):

```
[OPERATOR: ✋ Ask-Before-Delete]
Stop. Do not delete <path>.
Move it to refactor/_to_delete/<path> instead, leaving git history.
Then ask:
  "I believe <path> is now unused; here is the evidence (rg, callers, tests).
   May I delete it?"
Wait for explicit "yes" before unlinking.
```

**What the agent should have done:**

```
# Step 1: DON'T delete. Move to stage-for-deletion:
mv src/lib/skills/sync-pipeline.ts refactor/_to_delete/

# Step 2: grep for every possible reference:
rg 'sync-pipeline' --type ts --type tsx --type json --type yaml
rg 'syncPipeline|SyncPipeline' --type ts --type tsx

# Step 3: check feature flags and config:
rg 'FEATURE_.*SYNC|sync_enabled|pipeline' -l

# Step 4: read the file's test suite and intent — that tells you what it was FOR

# Step 5: ask the user with evidence:
#   "File sync-pipeline.ts has no callers and appears to be a
#    stubbed-out intended implementation for FEATURE_SYNC_PIPELINE_ENABLED
#    (currently false in config). Options:
#       a) wire it in now (and enable the feature)
#       b) leave it in place pending the feature
#       c) remove (requires explicit approval)
#    What should I do?"
```

### The isomorphism lens

A deletion is the widest possible isomorphism violation: the program no longer has a file. Every axis changes:

- Public API: changes (exported symbols vanish)
- Serialization: changes (if the file owned type definitions)
- Test suite: changes (tests vanish with the file)
- Build graph: changes (compilation units differ)
- Future behavior: changes (the code that would have activated on flag-flip is gone)

**No isomorphism card can be filled in good faith for a deletion.** That's why AGENTS.md Rule 1 exists: deletions require explicit human scrutiny.

### Generalize the lesson

The root pattern this avoids:

1. **Judgment without evidence** — "this looks broken" without callsite census + test-intent read.
2. **Rationalization** — using words like "dead" or "misleading" to skip the evidence step.
3. **Skipping the ask** — because you're confident.

These three together are the fingerprint of the single most damaging kind of refactor mistake.

### The skill's operational response

- Every script that could enable deletion (`install_missing_skills.sh`, `verify_isomorphism.sh`) never deletes files.
- [ANTI-PATTERNS.md](ANTI-PATTERNS.md#i-removed-the-unused-file) names this pattern verbatim: "I removed the unused file".
- The operator card above is the exact-script countermeasure.
- The verify gate checks `git status` for deletions and flags any in the diff.
- The LEDGER template has a "Files deleted" row; it must be empty or have a user-approval citation.

**If a future agent reads only this section of this skill, the skill has paid for itself.**

---

## Real collapse: N `updateSliderX` → one registry-driven `setupEventListeners`

**Session:** `gemini/b92018ad.../2026-02-12T15-05 :: L30-31 :: @1770909837377` — [evidence](REAL-SESSION-EVIDENCE.md#n-near-identical-fns--registry)

### The shape

A JS UI had multiple near-identical slider-update functions: `updateSliderA`, `updateSliderB`, `updateSliderC`, etc. Each was ~8 LOC, same shape, different target elements and labels. `setupEventListeners` had one block per slider wiring its event handler.

### Agent's plan (verbatim)

> *"I'll consolidate all `updateSlider` functions into one clean, registry-driven `setupEventListeners`"*
>
> Then: *"added `updateSliderUniversal` and restored a simplified `updateStats`. Now, I'll locate and replace the old `setupEventListeners` with a registry-based version to significantly reduce redundant code."*

### What the agent did

```javascript
// before: 8 × updateSliderX + 8 × setup blocks = ~80 LOC
function updateSliderA(val) { sliderA.textContent = val; sliderAOutput.value = val; ... }
function updateSliderB(val) { /* same shape, different ids */ }
// ...etc

// after: one universal updater + a registry = ~20 LOC
const SLIDERS = [
  { id: 'a', label: sliderA, output: sliderAOutput, /* ... */ },
  { id: 'b', label: sliderB, output: sliderBOutput, /* ... */ },
  // ...
];

function updateSliderUniversal(config, val) {
  config.label.textContent = val;
  config.output.value = val;
}

function setupEventListeners() {
  for (const cfg of SLIDERS) {
    cfg.input.addEventListener('input', (e) => updateSliderUniversal(cfg, e.target.value));
  }
}
```

### Score

- LOC saved: ~60 → LOC_pts = 4
- Confidence: 4 (each slider has a tested input event; behavior visible in UI)
- Risk: 1 (single file, single function, no cross-module)
- **Score: 16.0 — ACCEPT at rung 3 (parameterize via data-table)**

### Isomorphism axes

- Event binding: **preserved** — each input still gets exactly one listener.
- Event firing order: **preserved** — DOM event model doesn't depend on setup order.
- Default values: **preserved** — registry holds the same initial values the old code wrote.
- Labels/aria: **preserved** — registry captures label element refs.

### Lesson

This is the canonical Type II collapse from [DUPLICATION-TAXONOMY.md](DUPLICATION-TAXONOMY.md): same shape, different literals. Rung 3 (enum/strategy via data-table), not rung 4 (class hierarchy) — bounded set, no external consumers.

---

## Real collapse: many-arg `evaluate_heredoc` → `HeredocEvaluationContext` struct

**Session:** `gemini/6e93ebe2.../2026-01-10T22-42/3c4de28f :: L9` — [evidence](REAL-SESSION-EVIDENCE.md#many-args--context-struct)

### The shape

`evaluate_heredoc` had 7 parameters. Every caller passed the same 4 that came from a parent struct. Clippy was complaining about `too_many_arguments`.

### Agent's plan

> *"create a `HeredocEvaluationContext` struct to simplify the arguments of `evaluate_heredoc` and fix clippy lints"*

### What the agent did

```rust
// before — 7 parameters, repeated at every callsite
fn evaluate_heredoc(
    env: &Env,
    vars: &VarMap,
    cwd: &Path,
    strict: bool,
    input: &str,
    delim: &str,
    options: HeredocOptions,
) -> Result<String, HeredocError> { ... }

// after — one context, one variable, two arguments
struct HeredocEvaluationContext<'a> {
    env: &'a Env,
    vars: &'a VarMap,
    cwd: &'a Path,
    strict: bool,
    options: HeredocOptions,
}
fn evaluate_heredoc(ctx: &HeredocEvaluationContext<'_>, input: &str, delim: &str)
    -> Result<String, HeredocError> { ... }
```

### Score

- LOC saved: modest (-6 per callsite × 5 callsites = -30), but more importantly: **5 parameters → 2** and no more clippy warning.
- Confidence: 5 (mechanical refactor; compiler verifies).
- Risk: 1 (same file + direct callers).
- **Score: 15.0 — ACCEPT at rung 2**

### Isomorphism axes

- All 7 parameters still present in the context; nothing dropped.
- Borrow/lifetime: the context borrows; no copy. Behavior identical.
- Error set: unchanged.

### Lesson

Parameter sprawl (VIBE-CODED P9 in [VIBE-CODED-PATHOLOGIES.md](VIBE-CODED-PATHOLOGIES.md#p9--parameter-sprawl-helper)) yields to a context struct at rung 2. The clippy warning is the diagnostic; the shape is the fix. Don't climb past rung 2 here — a trait / generic would be over-engineered for a function with one implementation.

---

## Real horror story: WebSocket auto-subscribe silently dropped

**Session:** `b7da6852.../2026-01-11T00-48 :: L8` — [evidence](REAL-SESSION-EVIDENCE.md#hs3--websocket-auto-subscribe-silently-dropped)

### What happened

Agent was rewriting a WebSocket handler. The original implementation had, among its 40 LOC, an **implicit side effect**: when a client connected to `/agents/:id/ws`, the server auto-subscribed them to that agent's event stream.

The agent, asked to "refactor the WebSocket handler," read the docstring (which didn't mention the subscription), wrote a replacement from the docstring's description, and committed.

> **Agent's own realization (after the user noticed clients stopped receiving events):**
> *"The original implementation auto-subscribed clients connecting to `/agents/:id/ws`. My initial replacement lost this behavior."*

### Why this is deadly

- No test exercised the subscription (it was implicit behavior).
- The docstring documented the endpoint's request/response, not its side effect.
- Type signatures matched — old and new both returned `Response`.
- The compiler said yes; tests said yes; production said "the app stopped working."

### The isomorphism card would have caught this

The axis in [ISOMORPHISM.md §The axes](ISOMORPHISM.md#the-axes) that applied:

> **Side effects** — same logs / metrics / spans / **DB writes** / file syscalls / **pub-sub subscriptions**?

If the agent had been forced to fill this row *before* editing, the prompt "what side effects does this function have?" would have required reading the old code, not the docstring. The subscription would have surfaced.

### The rewrite-from-docstring anti-pattern

This is common with AI agents:

1. Close the old file.
2. Read the docstring / function signature.
3. Write a "clean" new implementation.
4. Replace the old file.

Steps 1 and 2 are the bug. **Write, don't rewrite** — this skill mandates Edit-only for exactly this reason. An Edit preserves the body and modifies selectively. A Write throws away the knowledge encoded in the body.

### Lesson

- Edit tool only. No Write over existing files.
- Isomorphism card "side effects" axis must be answered, not N/A.
- Integration tests that exercise the subscribe-on-connect path would have caught it — property tests could too (for every connection, a subscription is created).

---

## Real horror story: `LogSink` panic-flush behavior lost

**Session:** `37abaf19.../2026-02-02T02-27 :: L8` — [evidence](REAL-SESSION-EVIDENCE.md#hs4--logsink-panic-flush-behavior-lost)

### What happened

A Rust logging subsystem was refactored. The original had a `Drop` impl on `LogSink` that performed a best-effort flush if the process panicked mid-log. The refactor dropped the impl (it wasn't in the public API).

> **Agent's later realization:**
> *"`LogSink` final flush on panic (often the most critical error) was lost. Fix: I implemented `Drop` for `LogSink` ... to perform a best-effort flush."*

### The failure mode

- Happy path: unchanged.
- Error path: panics during logging now lose the logs that would have told you why.
- The most-critical-for-debugging code path disappeared in a refactor that "preserved behavior."

### Why the card catches it

[ISOMORPHISM.md §The axes](ISOMORPHISM.md#the-axes) lists:

> **Resource lifecycle** — same Drop / `__del__` / `defer` order?

This is exactly the axis. `Drop` impls, context manager `__exit__`, Go `defer`, `try/finally` blocks — they are all invisible in the signature. **Always list these.**

### Generalizable rule

Destructors are the most-important invisible-in-docs behavior. Every language has them. Every refactor of a type with lifecycle must audit them:

- Rust: `impl Drop`
- Python: `__del__`, `__exit__`
- Go: `defer` statements
- C++: destructors
- JS/TS: `FinalizationRegistry` (rare), `Symbol.dispose` / `Symbol.asyncDispose` (explicit resource management, 2026+)

### Lesson

Your isomorphism card's "Resource lifecycle" row is not optional. If you don't know whether the type has a destructor, find out before editing.

