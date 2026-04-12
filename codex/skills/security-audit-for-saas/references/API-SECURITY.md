# API Security for SaaS

Every API endpoint is an attack surface. This file is the deep checklist for
auditing API security in SaaS applications — input validation, output masking,
mass assignment, pagination, and more.

---

## The Input Validation Contract

Every API route must validate input via Zod (or equivalent type-safe validator).
No exceptions.

### The Pattern

```typescript
import { z } from "zod";

const createPackSchema = z.object({
  title: z.string().min(1).max(200),
  description: z.string().max(2000).optional(),
  visibility: z.enum(["private", "public"]),
  tags: z.array(z.string().max(50)).max(10),
}).strict(); // CRITICAL: reject unknown fields

export async function POST(req: Request) {
  const session = await requireAuth(req);
  const body = await req.json();

  const parsed = createPackSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json(
      { error: "Invalid input", issues: parsed.error.issues },
      { status: 400 }
    );
  }

  // Continue with parsed.data (typed and validated)
}
```

### Anti-Patterns

```typescript
// BAD: unsafe cast
const title = formData.get("title") as string;

// BAD: passthrough() allows unknown fields
const schema = z.object({ title: z.string() }).passthrough();

// BAD: manual validation
if (typeof body.title === "string" && body.title.length < 200) { /* ... */ }

// BAD: no length limit
z.object({ description: z.string() }) // Attacker can send 100MB
```

### Strict Mode Is Non-Negotiable

`.strict()` rejects unknown fields. This prevents mass assignment attacks (see
below) and future-proofs against schema drift.

---

## Mass Assignment Prevention

**Attack:** Client sends extra fields that map to privileged columns.

```typescript
// VULNERABLE: spread operator
export async function PATCH(req: Request) {
  const body = await req.json();
  await db.update(users).set(body).where(eq(users.id, session.userId));
}
```

Attacker sends:
```json
{
  "displayName": "New Name",
  "isAdmin": true,
  "subscriptionStatus": "active",
  "email": "victim@example.com"
}
```

All fields flow into the UPDATE.

**Fix 1: Zod `.strict()` + explicit schema**

```typescript
const updateProfileSchema = z.object({
  displayName: z.string().max(100),
  bio: z.string().max(500).optional(),
}).strict();

const parsed = updateProfileSchema.parse(body);
await db.update(users).set(parsed).where(eq(users.id, session.userId));
```

**Fix 2: Explicit column allowlist**

```typescript
const ALLOWED_COLUMNS = ["displayName", "bio"] as const;
const allowedData = Object.fromEntries(
  Object.entries(body).filter(([k]) => ALLOWED_COLUMNS.includes(k as any))
);
await db.update(users).set(allowedData).where(eq(users.id, session.userId));
```

**Fix 3: Explicit field-by-field update**

```typescript
await db.update(users).set({
  displayName: parsed.displayName,
  bio: parsed.bio ?? null,
}).where(eq(users.id, session.userId));
```

Fix 3 is most robust — there's no way for an extra field to sneak in.

---

## Output Field Masking

API responses must not expose internal fields.

**Vulnerable:**
```typescript
const user = await db.query.users.findFirst({ where: eq(users.id, userId) });
return NextResponse.json({ user });
```

Response includes: `stripeCustomerId`, `passwordHash`, `lastLoginIp`, `isAdmin`,
`referralSource`, `internalNotes`.

**Safe:** explicit allowlist of response fields.

```typescript
const user = await db.query.users.findFirst({
  where: eq(users.id, userId),
  columns: {
    id: true,
    email: true,
    displayName: true,
    createdAt: true,
    // Everything NOT listed is excluded
  },
});
return NextResponse.json({ user });
```

Or use a response schema:

```typescript
const userResponseSchema = z.object({
  id: z.string(),
  email: z.string(),
  displayName: z.string(),
}).strict();

return NextResponse.json({ user: userResponseSchema.parse(user) });
```

### Audit Pattern

```bash
# Find routes returning DB rows without field masking
rg -n 'NextResponse\.json\(\{ (user|subscription|organization|invoice) \}\)' --type ts
```

Each hit is a candidate for field exposure.

---

## Pagination Safety

Cursor-based pagination prevents billion-row attacks and is consistent under
concurrent writes.

**Vulnerable: offset pagination**
```typescript
const offset = parseInt(req.nextUrl.searchParams.get("offset") ?? "0");
const items = await db.select().from(table).limit(50).offset(offset);
```

Attacker sets `offset=999999999`. DB scans a billion rows. Or: concurrent inserts
shift the window, causing skipped/duplicate results.

**Safe: cursor pagination**
```typescript
const cursor = req.nextUrl.searchParams.get("cursor");
const items = await db.select()
  .from(table)
  .where(cursor ? gt(table.id, cursor) : undefined)
  .orderBy(asc(table.id))
  .limit(50);

const nextCursor = items.length === 50 ? items[49].id : null;
return { items, nextCursor };
```

### Pagination Limits

- Hard max per page: 100
- Default page size: 20
- Total fetch limit (across all paginations): 10,000 per user per day (prevents
  bulk exfiltration)

---

## Batch Operation Safety

Endpoints that operate on many resources at once need careful auth.

**Vulnerable:**
```typescript
export async function POST(req: Request) {
  const { ids } = await req.json();
  await db.delete(items).where(inArray(items.id, ids));
}
```

Attacker sends `ids: ["other_users_item_id"]`. Items deleted without ownership check.

**Fix:**
```typescript
export async function POST(req: Request) {
  const session = await requireAuth(req);
  const { ids } = z.object({
    ids: z.array(z.string().uuid()).max(100),
  }).parse(await req.json());

  // Ownership check for ALL ids before operating
  const owned = await db.select({ id: items.id }).from(items)
    .where(and(inArray(items.id, ids), eq(items.ownerId, session.userId)));

  if (owned.length !== ids.length) {
    return NextResponse.json({ error: "Some items not owned" }, { status: 403 });
  }

  await db.delete(items).where(
    and(inArray(items.id, ids), eq(items.ownerId, session.userId))
  );
}
```

---

## Idempotency Keys

Mutating endpoints should accept idempotency keys to prevent duplicate operations
from retries.

```typescript
const idempotencyKey = req.headers.get("idempotency-key");

if (idempotencyKey) {
  const existing = await db.query.idempotencyRecords.findFirst({
    where: eq(idempotencyRecords.key, idempotencyKey),
  });
  if (existing) {
    return NextResponse.json(JSON.parse(existing.response));
  }
}

// Perform operation
const result = await performOperation();

// Store result for idempotent replays
if (idempotencyKey) {
  await db.insert(idempotencyRecords).values({
    key: idempotencyKey,
    response: JSON.stringify(result),
    expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000),
  });
}

return NextResponse.json(result);
```

---

## Error Response Safety

### Information Disclosure via Errors

**Vulnerable:**
```typescript
try {
  // ...
} catch (err) {
  return NextResponse.json({ error: err.message, stack: err.stack }, { status: 500 });
}
```

Stack traces reveal file paths, library versions, and internal structure.

**Safe:**
```typescript
try {
  // ...
} catch (err) {
  const errorId = crypto.randomUUID();
  logger.error({ err, errorId }, "Request failed");
  return NextResponse.json(
    { error: "Internal error", errorId }, // User can reference errorId in support
    { status: 500 }
  );
}
```

### Error Messages as Oracles

Distinct error messages for distinct states = enumeration oracle.

**Vulnerable:**
```typescript
if (!user) return { error: "User not found" };
if (!user.emailVerified) return { error: "Email not verified" };
if (user.passwordHash !== hash) return { error: "Wrong password" };
```

Attacker learns: which emails exist, which are verified, which have correct password
up to that point.

**Fix:** Identical error for any auth failure. See [FAIL-OPEN-PATTERNS.md](FAIL-OPEN-PATTERNS.md)
and [ATTACK-SCENARIOS.md](ATTACK-SCENARIOS.md).

---

## PATCH Semantics

PATCH should be partial update. Distinguish missing fields from explicit-null.

```typescript
const patchSchema = z.object({
  displayName: z.string().max(100).optional(),
  bio: z.string().max(500).nullable().optional(),
}).strict();

// Usage:
// { displayName: "New" }       → update displayName only
// { bio: null }                → set bio to null
// { bio: undefined }           → leave bio unchanged (not sent)
// { displayName: "", bio: "" } → update both to empty string
```

Don't accept PATCH requests that contain fields not in the schema (strict mode).

---

## API Versioning

### The Version Tax

Every API version you still support is an attack surface. Old versions may lack
modern security middleware.

**Audit every deprecated version:**
- Is it still routable?
- Does it have the same auth middleware as the current version?
- Does it have the same rate limits?
- Does it have the same input validation?

If any answer is "no," either fix it or disable the route entirely.

### Sunset Header

```typescript
// In the old version handler:
return new Response(JSON.stringify({ error: "API v1 is deprecated" }), {
  status: 410, // Gone
  headers: {
    "Sunset": "Wed, 31 Dec 2026 23:59:59 GMT",
    "Deprecation": "true",
    "Link": '</api/v2>; rel="successor-version"',
  },
});
```

---

## Unknown Field Rejection (Strict DTOs)

The `.strict()` setting rejects unknown fields with an error. This is a security
feature, not a convenience: it prevents:
- Mass assignment
- Forward-compat drift (client sends `isAdmin: true`, server added the column later)
- Schema confusion (two API versions diverge)

**Make strict the default.** Use `.passthrough()` only for explicitly unversioned
metadata fields, and even then only in non-security-sensitive contexts.

---

## Content-Type Validation

```typescript
export async function POST(req: Request) {
  const contentType = req.headers.get("content-type") ?? "";
  if (!contentType.startsWith("application/json")) {
    return NextResponse.json(
      { error: "Content-Type must be application/json" },
      { status: 415 }
    );
  }
  // ...
}
```

Why: prevents confusion attacks (e.g., sending form-encoded data that gets parsed
as JSON differently by different layers).

---

## Request Body Size Limits

```typescript
const MAX_BODY_SIZE = 1_000_000; // 1MB

const contentLength = parseInt(req.headers.get("content-length") ?? "0");
if (contentLength > MAX_BODY_SIZE) {
  return NextResponse.json({ error: "Body too large" }, { status: 413 });
}

// Also: the framework should enforce this, but defense-in-depth
```

Next.js App Router has a default body size limit; verify it's appropriate for
your use case.

---

## Audit Checklist

### Every route:
- [ ] Input validated via Zod `.strict()` schema
- [ ] Auth check via `requireAuth()` / `requireOrgRole()` / similar
- [ ] Auth check uses the EXACT resource's tenant, not session default
- [ ] Response fields explicitly allowlisted (no DB row spread)
- [ ] Error messages don't leak schema, existence, or internal state
- [ ] Content-Type validated
- [ ] Body size limited

### List/search endpoints:
- [ ] Cursor-based pagination (not offset)
- [ ] Hard max page size (e.g., 100)
- [ ] Total fetch limit per user per day

### Batch endpoints:
- [ ] Ownership check for ALL items BEFORE operating
- [ ] Operation itself also scoped by ownership (defense in depth)
- [ ] Max batch size enforced

### Mutating endpoints (POST/PUT/PATCH/DELETE):
- [ ] Idempotency key support (header or body field)
- [ ] Mass assignment prevented via explicit allowlist
- [ ] PATCH semantics respect "missing vs null"
- [ ] CSRF protection (see [AUTH.md](AUTH.md))

### Deprecated endpoints:
- [ ] Return 410 Gone
- [ ] Include Sunset and Deprecation headers
- [ ] Link to successor version
- [ ] Same auth/rate limits as current version (if still routable)
