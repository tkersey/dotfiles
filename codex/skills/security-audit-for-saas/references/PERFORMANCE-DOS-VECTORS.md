# Performance as Security — DoS Vectors

Performance bugs can be security bugs. An O(n²) search becomes a Slowloris-
style DoS. A large-response endpoint becomes a Denial-of-Wallet (DoW). Every
"optimize later" has security implications.

---

## The Concept: Denial of Wallet (DoW)

Traditional DoS makes your service unavailable. Denial of Wallet makes it
expensive. For serverless/pay-per-use SaaS, DoW can be more damaging than DoS.

**Examples:**
- LLM API calls at $0.01 each × 100K requests = $1K bill
- Image generation × 1K requests = provider bill
- Large DB queries × N requests = RDS bill
- Email sends × N = SendGrid bill

**Defense:** Rate limit by COST, not just request count.

---

## DoS Vector Categories

### 1. Algorithmic Complexity (ReDoS, hash collisions, N+1)

**Pattern:** Input causes O(n²) or worse behavior.

**Examples:**
- Regex with catastrophic backtracking: `/^(a+)+$/` on `"aaaaa...X"`
- Hash table collision attack: inputs that all hash to the same bucket
- N+1 query: fetch users, then for each user fetch their orders

**Defense:**
- Use linear-time regex engines (RE2, not PCRE)
- Use `re2` library in Node, not built-in regex
- Use query builders that DataLoader / batch fetching

### 2. Unbounded Resource Allocation

**Pattern:** Attacker triggers allocation proportional to their input.

**Examples:**
- `JSON.parse(body)` with 100MB body
- `await request.text()` without size limit
- Creating N database rows per request
- Spawning N sub-requests per request

**Defense:**
- Body size limits at proxy AND app layer
- Explicit max size on every allocation
- Bounded pagination

### 3. Pagination DoS

**Pattern:** Endpoint returns unbounded results.

```typescript
// BAD
const results = await db.select().from(users); // All users!

// ALSO BAD
const offset = parseInt(req.query.offset); // offset=99999999
const results = await db.select().from(users).limit(50).offset(offset);
```

**Defense:** Cursor-based pagination with hard max page size.

### 4. Zipbomb / Decompression Bombs

**Pattern:** Small input expands to huge output.

- 1KB gzip → 10GB decompressed
- 100-byte XML → 10GB entity expansion
- Deeply nested JSON → stack overflow on parse

**Defense:**
- Decompression limits (check size before/during)
- XML parsing without entity resolution
- JSON depth limits

### 5. LLM Token Budget

**Pattern:** Attacker triggers expensive LLM calls.

```typescript
// VULNERABLE
const response = await llm.complete(userInput); // $0.01-$1 per call

// Each request is a denial-of-wallet attack if not rate-limited
```

**Defense:**
- Per-user daily token budget
- Per-request max input length
- Per-request max output length
- Input length ≈ output length (LLMs respond proportionally)

### 6. External API Amplification

**Pattern:** One user request triggers multiple external API calls.

```typescript
// VULNERABLE
for (const item of userRequest.items) {
  await stripe.prices.retrieve(item.priceId); // N API calls per request
}
```

**Defense:**
- Batch external API calls where possible
- Cache external data aggressively
- Rate limit by external API cost

### 7. Slow Query DoS

**Pattern:** Attacker crafts query that's slow.

```sql
-- Slow: full table scan
SELECT * FROM users WHERE email LIKE '%a%';

-- Slow: no index
SELECT * FROM orders WHERE DATE(created_at) = '2024-01-01';
```

**Defense:**
- Query timeout (1-5 sec max)
- Query plan analysis in CI
- Explicit indexes for all query patterns

### 8. File Upload DoS

**Pattern:** Attacker uploads huge files or many files.

**Defense:**
- Size limit per upload (at proxy AND app)
- Count limit per request
- Per-user daily upload quota
- Storage quota per account

### 9. Retry Storm DoS

**Pattern:** A failing operation is retried exponentially.

**Example:** Webhook fails → retried 10× → each retry does expensive work.

**Defense:**
- Max retry count
- Exponential backoff (actually implement it)
- Circuit breaker when downstream is failing

### 10. State Bloat DoS

**Pattern:** Attacker causes state growth without cleanup.

**Example:**
- Create 10M expired sessions
- Upload 10M pending files that never get confirmed
- Register 10M pending accounts

**Defense:**
- Expiry cron for pending state
- Limits per user account
- Garbage collection on failed/abandoned operations

---

## The Audit Approach

### Step 1: Identify Expensive Operations
For each endpoint, ask:
- What's the worst-case cost of one request?
- What's the cost in CPU?
- What's the cost in memory?
- What's the cost in external API calls?
- What's the cost in storage?

### Step 2: Check Rate Limits
For each expensive operation:
- Is there a rate limit?
- Is the rate limit by COST or by REQUEST COUNT?
- Can an attacker split one attack into many cheap-looking requests?

### Step 3: Check Resource Limits
For each resource:
- Bounded?
- Enforced where?
- Recovered when?

### Step 4: Stress Test
- Concurrent requests to the most expensive endpoints
- Large-payload requests
- Deeply-nested input requests
- Malformed input that might trigger fallback code paths

---

## Specific Patterns to Audit

### Regex ReDoS
```bash
# Find regex patterns that could be catastrophic
grep -rn 'new RegExp\|/.*\+.*\+' --include='*.ts'
```

Test each with:
```typescript
import safeRegex from 'safe-regex';
if (!safeRegex(pattern)) console.warn('Unsafe regex:', pattern);
```

### JSON.parse on User Input
```bash
grep -rn 'JSON\.parse' src/
```

Each should have a size limit before it.

### Loops with Async Operations
```bash
grep -rn 'for.*await\|await.*for' src/
```

Each is a potential N+1 or amplification vector.

### Unbounded Queries
```bash
grep -rn '\.findMany\|\.select().*from' src/ | grep -v 'limit'
```

Any query without `.limit()` is a potential DoS.

---

## Rate Limiting by Cost

Traditional: N requests per minute.

Better: X cost units per minute, where expensive operations consume more.

```typescript
const COST_PER_ENDPOINT = {
  '/api/search': 1,
  '/api/export': 10,
  '/api/llm/chat': 5,
  '/api/image/generate': 20,
  '/api/batch-import': 50,
};

async function checkCostBudget(userId: string, endpoint: string): Promise<boolean> {
  const cost = COST_PER_ENDPOINT[endpoint] ?? 1;
  const used = await redis.incrby(`cost:${userId}:${today()}`, cost);
  return used <= DAILY_COST_BUDGET;
}
```

Now an attacker can't just spam cheap endpoints — they must pay the budget
for expensive ones.

---

## The Economic Attacker

A rational attacker calculates cost:payoff. You want to make the cost:payoff
ratio > 1 for attacks.

**Cost of attack:** How much compute/network/time does the attacker spend?
**Payoff:** What do they gain from the attack?

**Examples:**
- Brute force login (high cost, variable payoff) — rate limiting raises cost
- Credential stuffing (low cost, high payoff) — MFA lowers payoff
- LLM DoW (low cost, costs YOU money, zero payoff) — rate limit by cost

Make each attack economically irrational.

---

## Audit Checklist

### Endpoints
- [ ] Every endpoint has an explicit max input size
- [ ] Every endpoint has a query timeout
- [ ] Every endpoint has a rate limit
- [ ] Expensive endpoints have higher rate limit cost

### Queries
- [ ] Every query has `.limit()` or pagination
- [ ] Slow queries have query plan analysis in CI
- [ ] N+1 queries are detected and fixed

### Input
- [ ] JSON/XML/etc. have depth limits
- [ ] Regex uses linear-time engine (RE2)
- [ ] File upload has size and count limits
- [ ] Decompression has expansion limits

### LLM / External APIs
- [ ] Per-user token budget for LLMs
- [ ] External API calls are cached where possible
- [ ] Circuit breaker on failing external APIs

### State
- [ ] Pending state has TTL
- [ ] Expired state cleaned up by cron
- [ ] Per-user storage quota

---

## See Also

- [RATE-LIMITING.md](RATE-LIMITING.md) — per-cost rate limiting
- [API-SECURITY.md](API-SECURITY.md) — pagination safety
- [LLM-SECURITY.md](LLM-SECURITY.md) — token budget
- [extreme-software-optimization skill](../../extreme-software-optimization/) — for performance hotspots
