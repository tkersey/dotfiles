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

### Exemplar 1 (Brownfield): Parse at the boundary, stop scattered validation (TypeScript)

````text
**Contract**
- `/signup` rejects invalid email and passes a normalized email to the service.

**Invariants**
- `parseEmail` is the only place that decides email validity for this flow.
- Downstream code only sees trimmed, lowercased emails (no re-validation).
- Invalid emails never reach `userService.createUser`.

**Creative Frame**
- Reframe: First principles
- Technique: Lotus blossom
- Representation shift: Replace `string` email with refined `Email` at the boundary.

**Why This Solution**
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

### Exemplar 2 (Brownfield): Add a seam (Clock), delete flaky sleeps (Go)

````text
**Contract**
- Renewal logic uses an injected clock; production behavior is unchanged; tests are deterministic.

**Invariants**
- All time comparisons use `Clock.Now()` (no direct `time.Now()` in the core).
- Production default is system time.
- Tests can freeze time without sleeping.

**Creative Frame**
- Reframe: Inversion
- Technique: SCAMPER
- Representation shift: Replace implicit global time with an explicit dependency.

**Why This Solution**
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

**Creative Frame**
- Reframe: Constraint extremes
- Technique: Morphological analysis
- Representation shift: Represent tags as a canonical list (normal form), not "whatever the caller sends".

**Why This Solution**
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

**Creative Frame**
- Reframe: First principles
- Technique: TRIZ
- Representation shift: Treat money as integer cents end-to-end; choose rounding only at the parse/boundary.

**Why This Solution**
- Stable boundary: The money parser/constructor is where the rounding rule belongs.
- Not smaller: Tweaking one caller fixes a symptom and keeps the bug class alive.
- Not larger: A full money library migration is too much until we agree on semantics.
- Proof signal: Characterization tests against a handful of real invoices (including half-cent cases).

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

**Creative Frame**
- Reframe: Analogy transfer
- Technique: TRIZ
- Representation shift: Keep the old API stable; migrate by commuting adapters.

**Why This Solution**
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
