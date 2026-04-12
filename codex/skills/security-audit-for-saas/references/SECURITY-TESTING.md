# Security Testing Strategy

You can't fix bugs you don't find. This file covers proactive security testing:
fuzzing, property-based testing, pen-testing, and CI-integrated security gates.

See also: [testing-fuzzing](../../testing-fuzzing/) skill for fuzzing harnesses.

---

## The Security Testing Pyramid

```
            ┌─────────────┐
            │  Red Team   │  Quarterly
            │  Exercises  │
            └─────────────┘
           ┌───────────────┐
           │   Pen Tests   │  Semi-annual
           │  (external)   │
           └───────────────┘
         ┌───────────────────┐
         │  Fuzzing &        │  Continuous in CI
         │  Property Tests   │
         └───────────────────┘
       ┌───────────────────────┐
       │   Integration Tests   │  Every PR
       │  (security scenarios) │
       └───────────────────────┘
     ┌───────────────────────────┐
     │      Unit Tests           │  Every commit
     │  (security functions)     │
     └───────────────────────────┘
   ┌─────────────────────────────┐
   │    Static Analysis          │  Every commit
   │  (SAST, dep audit, secrets) │
   └─────────────────────────────┘
```

Each layer catches a different class of bugs. You need all of them.

---

## Layer 1: Static Analysis (SAST)

Runs in CI on every commit.

### Secret Detection

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
```

Also: `gitleaks`, `trufflehog`.

### Dependency Scanning

```yaml
# .github/workflows/security.yml
- run: npm audit --audit-level=high
- run: pnpm audit --audit-level=high
- uses: sigstore/cosign-installer@v3
- run: cosign verify ...
```

Fail build on high/critical findings.

### Code Scanning

Semgrep with security rulesets:

```yaml
- uses: returntocorp/semgrep-action@v1
  with:
    config: p/security-audit p/owasp-top-ten p/javascript p/typescript
```

---

## Layer 2: Unit Tests for Security Functions

Every security-critical function has tests that specifically try to break it.

### Example: `validateCsrf`

```typescript
describe("validateCsrf", () => {
  it("accepts requests with valid origin", async () => {
    const req = mockRequest({ method: "POST", origin: "https://example.com" });
    const result = await validateCsrf(req);
    expect(result.valid).toBe(true);
  });

  it("rejects requests with missing origin", async () => {
    const req = mockRequest({ method: "POST" });
    const result = await validateCsrf(req);
    expect(result.valid).toBe(false);
  });

  it("rejects requests with malformed origin", async () => {
    const req = mockRequest({ method: "POST", origin: "not-a-url" });
    const result = await validateCsrf(req);
    expect(result.valid).toBe(false);
  });

  it("rejects cross-origin origin", async () => {
    const req = mockRequest({ method: "POST", origin: "https://evil.com" });
    const result = await validateCsrf(req);
    expect(result.valid).toBe(false);
  });

  it("exempts webhook endpoints", async () => {
    const req = mockRequest({ method: "POST", path: "/api/stripe/webhook" });
    const result = await validateCsrf(req);
    expect(result.valid).toBe(true);
  });

  it("does NOT exempt CLI tokens when session cookie present (CRITICAL)", async () => {
    const req = mockRequest({
      method: "POST",
      headers: { authorization: "Bearer jsm_xxx" },
      cookies: { session: "validSession" },
    });
    const result = await validateCsrf(req);
    expect(result.valid).toBe(false); // Must validate origin, not bypass
  });
});
```

---

## Layer 3: Integration Tests for Security Scenarios

Run every PR. Test actual attack scenarios against the running application.

### Example: Multi-Tenant Isolation

```typescript
describe("Multi-tenant isolation", () => {
  let userA: TestUser, userB: TestUser;
  let dataA: TestData, dataB: TestData;

  beforeAll(async () => {
    ({ userA, userB, dataA, dataB } = await setupTwoTenantFixtures());
  });

  it("userA can access their own data", async () => {
    const res = await apiRequest("GET", `/api/data/${dataA.id}`, { user: userA });
    expect(res.status).toBe(200);
  });

  it("userA cannot access userB's data", async () => {
    const res = await apiRequest("GET", `/api/data/${dataB.id}`, { user: userA });
    expect(res.status).toBe(404); // 404 not 403 to avoid existence enum
  });

  it("userA cannot modify userB's data", async () => {
    const res = await apiRequest("PATCH", `/api/data/${dataB.id}`,
      { user: userA, body: { name: "hacked" } });
    expect(res.status).toBe(404);
    // Verify data wasn't actually modified
    const check = await db.query.data.findFirst({ where: eq(data.id, dataB.id) });
    expect(check.name).not.toBe("hacked");
  });

  it("userA cannot delete userB's data", async () => {
    const res = await apiRequest("DELETE", `/api/data/${dataB.id}`, { user: userA });
    expect(res.status).toBe(404);
    const check = await db.query.data.findFirst({ where: eq(data.id, dataB.id) });
    expect(check).not.toBeNull();
  });

  it("userA cannot list userB's data via search", async () => {
    const res = await apiRequest("GET", `/api/data?q=${dataB.name}`, { user: userA });
    const items = await res.json();
    expect(items.find((i: any) => i.id === dataB.id)).toBeUndefined();
  });

  it("admin client (service role) bypass still audited", async () => {
    // Verify even service role operations are logged
    const logs = await getAuditLogs({ actorType: "admin" });
    expect(logs.length).toBeGreaterThan(0);
  });
});
```

### Example: Billing Bypass

```typescript
describe("Billing bypass prevention", () => {
  it("free user cannot access premium endpoints", async () => {
    const freeUser = await createFreeUser();
    const res = await apiRequest("GET", "/api/premium/content", { user: freeUser });
    expect(res.status).toBe(402); // Payment required
  });

  it("free user cannot create checkout with victim's userId as metadata", async () => {
    const attacker = await createFreeUser();
    const victim = await createFreeUser();
    const res = await apiRequest("POST", "/api/stripe/create-checkout", {
      user: attacker,
      body: { metadata: { userId: victim.id } },
    });
    // The checkout can be created, but the metadata must be ignored or
    // overwritten server-side with the authenticated user's ID
    const session = await res.json();
    // Simulate webhook
    await sendWebhook("checkout.session.completed", { session });
    // Verify victim did NOT get upgraded
    const victimUpdated = await db.query.users.findFirst({ where: eq(users.id, victim.id) });
    expect(victimUpdated.subscriptionStatus).not.toBe("active");
  });

  it("webhook with invalid signature is rejected", async () => {
    const res = await fetch("/api/stripe/webhook", {
      method: "POST",
      body: JSON.stringify({ fake: "event" }),
      headers: { "stripe-signature": "invalid_signature" },
    });
    expect(res.status).toBe(401);
  });

  it("webhook with missing signature is rejected", async () => {
    const res = await fetch("/api/stripe/webhook", {
      method: "POST",
      body: JSON.stringify({ fake: "event" }),
    });
    expect(res.status).toBe(400);
  });

  it("duplicate webhook is idempotent (no double credit)", async () => {
    const event = validStripeEvent("checkout.session.completed");
    const res1 = await sendSignedWebhook(event);
    const res2 = await sendSignedWebhook(event); // Same event
    expect(res1.status).toBe(200);
    expect(res2.status).toBe(200);
    // Verify user was only upgraded once
    const events = await db.query.paymentEvents.findMany({
      where: eq(paymentEvents.eventId, event.id),
    });
    expect(events.length).toBe(1);
  });
});
```

### Example: Rate Limiting

```typescript
describe("Rate limiting", () => {
  it("blocks anonymous after 60 req/min", async () => {
    const responses = [];
    for (let i = 0; i < 70; i++) {
      responses.push(await fetch("/api/public"));
    }
    const blocked = responses.filter(r => r.status === 429);
    expect(blocked.length).toBeGreaterThanOrEqual(10);
  });

  it("short-circuits for subscribers (never hits Redis)", async () => {
    const sub = await createSubscriberUser();
    const redisSpy = jest.spyOn(redis, "eval");
    for (let i = 0; i < 100; i++) {
      await apiRequest("GET", "/api/public", { user: sub });
    }
    expect(redisSpy).not.toHaveBeenCalled();
  });

  it("auth endpoints fail-closed when Redis is down", async () => {
    await simulateRedisOutage();
    const res = await apiRequest("POST", "/api/auth/login", {
      body: { email: "test@example.com", password: "pass" },
    });
    expect(res.status).toBe(503); // Service unavailable, not 200
  });

  it("promo code endpoint gives constant response regardless of validity", async () => {
    const responses = await Promise.all([
      apiRequest("POST", "/api/promo/check", { body: { code: "valid" } }),
      apiRequest("POST", "/api/promo/check", { body: { code: "invalid" } }),
      apiRequest("POST", "/api/promo/check", { body: { code: "expired" } }),
    ]);
    // Same status + same body shape for enumeration resistance
    expect(new Set(responses.map(r => r.status)).size).toBe(1);
  });
});
```

---

## Layer 4: Property-Based Testing

Generate random inputs, assert invariants. Finds edge cases unit tests miss.

```typescript
import fc from "fast-check";

test("RBAC: no user can modify owner's role", () => {
  fc.assert(
    fc.property(
      fc.constantFrom("viewer", "member", "admin", "owner") as any,
      fc.constantFrom("viewer", "member", "admin") as any,
      (actorRole, newRole) => {
        const actor = { role: actorRole };
        const target = { role: "owner" };
        expect(canChangeRole(actor.role, target.role, newRole)).toBe(false);
      }
    )
  );
});

test("JWT: tampered tokens always reject", () => {
  fc.assert(
    fc.property(fc.string(), (tamperedBytes) => {
      const validToken = makeValidJwt();
      const tampered = validToken.slice(0, -4) + tamperedBytes.slice(0, 4);
      expect(() => jwt.verify(tampered, publicKey)).toThrow();
    })
  );
});

test("Rate limit: count never exceeds limit", () => {
  fc.assert(
    fc.asyncProperty(fc.integer({ min: 1, max: 1000 }), async (requestCount) => {
      const allowed = await simulateRequests(requestCount, { limit: 60 });
      expect(allowed).toBeLessThanOrEqual(60);
    })
  );
});
```

---

## Layer 5: Fuzzing

Use for: parsers, decoders, input validators, cryptographic primitives.

See [testing-fuzzing](../../testing-fuzzing/) skill for harness design.

Targets for a SaaS:
- CSV import parser
- Markdown sanitizer
- URL validator
- Email validator
- JWT decoder
- Webhook signature verifier
- OAuth state parser
- Pagination cursor decoder

---

## Layer 6: Pen Testing

External pen test semi-annually. Internal red team quarterly.

### Red Team Exercises

From [ATTACK-SCENARIOS.md](ATTACK-SCENARIOS.md):
- Exercise 1: "The $0 Premium Exploit" (2 hours)
- Exercise 2: "The Cross-Tenant Leak" (4 hours)
- Exercise 3: "The Admin Takeover" (4 hours)
- Exercise 4: "The Webhook Forgery" (2 hours)
- Exercise 5: "The Slow Burn" (8 hours)

### Pen Test Preparation

Before paying for an external pen test:
- [ ] Fix all known HIGH and CRITICAL issues
- [ ] Document scope (in-scope URLs, out-of-scope services)
- [ ] Provide test accounts (regular user, admin)
- [ ] Provide API documentation
- [ ] Set up staging environment
- [ ] Define success criteria

Don't pay for a pen test that just finds what your static analysis would catch.

---

## CI Integration

```yaml
# .github/workflows/security.yml
name: Security
on: [push, pull_request]

jobs:
  static-analysis:
    steps:
      - uses: actions/checkout@v4
      - name: Secret detection
        uses: gitleaks/gitleaks-action@v2
      - name: Dependency audit
        run: pnpm audit --audit-level=high
      - name: Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: p/security-audit p/owasp-top-ten

  unit-tests:
    steps:
      - run: pnpm test -- --coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  integration-tests:
    services:
      postgres:
        image: postgres:16
      redis:
        image: redis:7
    steps:
      - run: pnpm test:integration
      - run: pnpm test:security # Security-specific scenarios

  rls-coverage:
    steps:
      - run: psql -f scripts/rls-coverage.sql

  webhook-tests:
    steps:
      - run: pnpm test:webhooks # Real webhook signatures
```

---

## Test Coverage Targets

| Category | Target Coverage |
|----------|----------------|
| Security functions (auth, CSRF, rate limit) | 100% |
| Webhook handlers | 100% |
| Billing flows | 100% |
| RLS policies | 95%+ (via integration tests with 2 tenants) |
| API input validation | 90%+ |
| Overall | 80%+ |

---

## What NOT to Test

- Third-party library internals (trust their tests)
- Framework-level security (trust Next.js CSRF, etc.)
- Cryptographic algorithms themselves (trust Node's `crypto`)

Focus test effort on YOUR code's correctness, not the libraries you depend on.

---

## Audit Checklist

### CI pipeline
- [ ] Secret scanning enabled
- [ ] Dependency audit (fail on high/critical)
- [ ] Semgrep or equivalent SAST
- [ ] Code coverage reported
- [ ] Security-specific test suite

### Test suites
- [ ] Unit tests for every security function
- [ ] Integration tests for every attack scenario
- [ ] Property-based tests for invariant verification
- [ ] Fuzz tests for parsers and validators
- [ ] Multi-tenant fixtures in every integration test
- [ ] Webhook replay and idempotency tests

### Pen testing
- [ ] Red team exercises quarterly
- [ ] External pen test semi-annually
- [ ] Pen test prep checklist followed
- [ ] Findings tracked in beads

### Culture
- [ ] New features require security test coverage
- [ ] Security bugs have regression tests
- [ ] PR template asks "did you add security tests?"
