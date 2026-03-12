# TK Examples

## Canonical examples (translate into repo dialect)

### Example A: Parse, don’t validate
- Contract: invalid input rejected at the boundary; core never re-checks.
- Invariant: downstream code only receives refined values.
- Incision: add a parser/smart constructor that returns the refined value (not `()`), and make the core accept the refined type.
- Why inevitable: once the type can’t represent invalid states, the “impossible” paths vanish and the rule lives in one place.

### Example C: Commuting migration diagram
- Contract: old and new behavior agree on supported inputs (or the delta is explicitly defined).
- Invariant: adapters preserve meaning.
- Incision: introduce `toNew`/`fromNew` adapters so two paths “commute”:
  - `old(x)` equals `fromNew(new(toNew(x)))` for representative inputs.
- Why inevitable: you get incremental replacement with a proof signal that is local, executable, and reviewable.

## Exemplars (synthetic)
Copy the shape, then translate into repo dialect (errors, tests, paths, and naming).
Exemplars below show the expected Incision summary format (no diffs).
Keep these synthetic; real session transcripts belong in `references/eval/`, not here.

### Exemplar 1 (Brownfield): Parse at the boundary, stop scattered validation (TypeScript)

````text
**Contract**
- `/signup` rejects invalid email and passes a normalized email to the service.

**Invariants**
- `parseEmail` is the only place that decides email validity for this flow.
- Downstream code only sees trimmed, lowercased emails (no re-validation).
- Invalid emails never reach `userService.createUser`.

**Cut Rationale**
- Stable boundary: `src/routes/signup.ts` is where untrusted input enters.
- Not smaller: Another inline `if (...)` check keeps validation scattered and inconsistent.
- Not larger: Making every email in the repo a branded type is a rewrite; this keeps the cut local.
- Proof signal: Unit tests for `parseEmail` + existing signup handler tests.

**Incision**
- Introduce a refined email boundary (`parseEmail`) that normalizes (trim/lowercase) and rejects invalid shape.
- Move signup validation to the boundary so downstream code only sees refined/normalized emails (delete inline checks).
- Add unit coverage for normalization + rejection.

**Proof**
- Ran: `pnpm test src/domain/Email.test.ts` -> PASS
- Ran: `pnpm test` -> PASS
````

### Exemplar 1A (Brownfield): Delete wrapper ladders, keep one normalizer (Python)

````text
**Contract**
- Request header normalization happens once in `normalize_header`; callers stop layering cleanup wrappers.

**Invariants**
- `normalize_header` is the only place that trims, lowercases, and collapses internal whitespace for this flow.
- Callers receive one canonical representation.
- Comments do not restate cleanup rules that the code can encode directly.

**Cut Rationale**
- Stable boundary: `normalize_header(raw)` already sits at ingress for the request path.
- Not smaller: Adding a fourth alias helper preserves the same drift under a new name.
- Not larger: A `HeaderNormalizer` class is ceremony when the rule is one pure transform.
- Proof signal: Unit tests for header normalization + existing request handler tests.

**Incision**
- Collapse `clean_header`, `safe_header`, and `canonical_header` into the existing `normalize_header`.
- Reuse built-in string operations (`strip`, `lower`, `split`, `join`) at the boundary instead of adding a new wrapper.
- Delete caller-side comments that only describe the whitespace cleanup the code now performs directly.

**Proof**
- Ran: `pytest tests/test_headers.py -q` -> PASS
- Ran: `pytest tests/test_requests.py -q` -> PASS
````

### Exemplar 1B (Brownfield): Keep the canonical repo seam, do not bypass it (Go)

````text
**Contract**
- Account IDs are parsed through `accountid.Parse`; the endpoint stops re-implementing cleanup inline.

**Invariants**
- `accountid.Parse` remains the sole owner of trimming, case normalization, and validity for account IDs.
- Handlers never pass raw account ID strings deeper into the core.
- Lean code does not mean bypassing the repo's canonical boundary.

**Cut Rationale**
- Stable boundary: `accountid.Parse` is the repo's shared ingress for account ID validity.
- Not smaller: Inline `strings.TrimSpace` plus a regex is a second policy path, not a simplification.
- Not larger: Rebuilding the parser package or changing every caller is unnecessary.
- Proof signal: Focused parser tests + the handler test that exercises the endpoint path.

**Incision**
- Route the endpoint through `accountid.Parse` and delete the local trim/regex cleanup.
- Keep the repo's existing refined `AccountID` type as the thing the core receives.
- Leave any migration note only if it captures cross-service rollout context that the code cannot encode.

**Proof**
- Ran: `go test ./internal/accountid ./internal/http/...` -> PASS
````

Lean note:
- If the repo already has one canonical boundary, lean means using it; raw stdlib is only "leaner" when it does not create a second rule owner.

### Exemplar 2 (Brownfield): Add a seam (Clock), delete flaky sleeps (Go)

````text
**Contract**
- Renewal logic uses an injected clock; production behavior is unchanged; tests are deterministic.

**Invariants**
- All time comparisons use `Clock.Now()` (no direct `time.Now()` in the core).
- Production default is system time.
- Tests can freeze time without sleeping.

**Cut Rationale**
- Stable boundary: Time is an effect; a `Clock` seam isolates it.
- Not smaller: Adding sleeps/retries makes tests slower and still flaky.
- Not larger: A full scheduler/state-machine refactor is unnecessary for determinism.
- Proof signal: `go test ./...` (no sleeps).

**Incision**
- Add a `Clock` seam and default `SystemClock` so production behavior stays the same.
- Inject clock into the renewal core and delete direct `time.Now()` usage to make time an explicit dependency.
- Make tests deterministic with a `fakeClock` (no sleeps).

**Proof**
- Ran: `go test ./...` -> PASS
````

### Exemplar 3 (Greenfield): Pick a normal form + prove idempotence (TypeScript)

````text
**Contract**
- `normalizeTags` returns tags in a canonical form (trimmed, lowercased, unique, sorted).

**Invariants**
- Output contains no empty strings.
- Output is sorted, unique, lowercased.
- Idempotence: `normalizeTags(normalizeTags(x))` equals `normalizeTags(x)`.

**Cut Rationale**
- Stable boundary: The boundary is the constructor/normalizer; everything downstream can assume the invariant.
- Not smaller: Sprinkling `trim()/toLowerCase()` in callers guarantees drift.
- Not larger: A dedicated class + fluent API is ceremony until there are 3+ distinct operations.
- Proof signal: Unit test for idempotence + a couple of examples.

**Incision**
- Add `normalizeTags` as the single canonicalizer (trim/lowercase, drop empties, unique, sort).
- Prove idempotence with a focused unit test.

**Proof**
- Ran: `pnpm test src/domain/TagSet.test.ts` -> PASS
````

### Exemplar 4 (Blocked): Ask one question, include a recommended default

````text
**Contract**
- Invoice totals round to cents in a way that matches customer-facing expectations.

**Invariants**
- Rounding happens in one place (no per-call-site rounding).
- Totals are deterministic across services and platforms.

**Cut Rationale**
- Stable boundary: The money parser/constructor is where the rounding rule belongs.
- Not smaller: Tweaking one caller fixes a symptom and keeps the bug class alive.
- Not larger: A full money library migration is too much until we agree on semantics.
- Proof plan: Characterization tests against a handful of real invoices (including half-cent cases).

**Question**
- For half-way values (e.g., 1.005), do we want half-up (recommended default) or half-even (banker's rounding)?
````

### Exemplar 5 (Migration): Commuting replacement behind the same API (TypeScript)

````text
**Contract**
- `normalizePhone` preserves legacy behavior while introducing a refined `PhoneNumber` core.

**Invariants**
- Callers still call `normalizePhone(raw: string): string`.
- New core uses one parser (`parsePhoneNumber`) for validity + normalization.
- Migration leash: `normalizePhone(raw)` equals `legacyNormalizePhone(raw)` for representative inputs.

**Cut Rationale**
- Stable boundary: `normalizePhone` is the boundary that all callers already use.
- Not smaller: Tweaking a couple of call sites won't stop drift; the rule must live at the boundary.
- Not larger: Changing every call site to a new type is a repo-wide rewrite.
- Proof signal: A migration equivalence test + existing unit tests.

**Incision**
- Introduce a refined `PhoneNumber` core with one parser (`parsePhoneNumber`) for validity + normalization.
- Keep the public API stable by re-implementing `normalizePhone(raw)` via the new core, while preserving the legacy behavior behind `legacyNormalizePhone`.
- Add an equivalence test that leashes the migration (`normalizePhone(raw) === legacyNormalizePhone(raw)`).

**Proof**
- Ran: `pnpm test src/legacy/normalizePhone.migration.test.ts` -> PASS
````

### Exemplar 6 (Strict-output worker mode): patch-only external contract (Python)

````text
```diff
diff --git a/src/slug.py b/src/slug.py
--- a/src/slug.py
+++ b/src/slug.py
@@
-def slugify(value: str) -> str:
-    return value.strip().lower().replace(" ", "-")
+def normalize_slug(raw: str) -> str:
+    value = raw.strip().lower()
+    return "-".join(part for part in value.split() if part)
+
+
+def slugify(value: str) -> str:
+    return normalize_slug(value)
```
````

Notes:
- TK still runs internal cut selection before this external contract is emitted.
- The external contract wins, so only the patch artifact is emitted.
