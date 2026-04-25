# Security-Aware Refactor — when the code touches auth, secrets, or attack surface

> Cross-links: [security-audit-for-saas](../../security-audit-for-saas/SKILL.md) for the audit side. This file is the refactor side: what to preserve, what extra axes apply, and what to NEVER simplify.

## Contents

1. [When to use this file](#when-to-use-this-file)
2. [Security isomorphism axes](#security-isomorphism-axes)
3. [Never-simplify list](#never-simplify-list)
4. [Authentication refactors](#authentication-refactors)
5. [Authorization / RLS refactors](#authorization--rls-refactors)
6. [Input-validation / boundary refactors](#input-validation--boundary-refactors)
7. [Rate-limiting / abuse-prevention refactors](#rate-limiting--abuse-prevention-refactors)
8. [Secret / credential handling](#secret--credential-handling)
9. [CSP / CORS / security headers](#csp--cors--security-headers)
10. [Session / cookie refactors](#session--cookie-refactors)
11. [Audit-log preservation](#audit-log-preservation)
12. [Security-aware isomorphism card (template)](#security-aware-isomorphism-card-template)

---

## When to use this file

Any refactor touching:
- `src/auth/`, `src/session/`, `src/login/`, `src/passwords/`
- Anything that reads/writes `JWT`, `session_token`, `api_key`, `refresh_token`
- Row-level-security (RLS) policies
- `zod` schemas / `pydantic` models used at API boundaries
- Rate-limit middleware
- CSRF / SameSite / HTTPOnly cookie handling
- Webhook signature verification
- Environment variables containing secrets
- Any function whose name contains `Admin`, `Verify`, `Authorize`, `CheckPermission`

Add to the isomorphism card the security-specific axes (below). If in doubt, treat the refactor as security-critical.

---

## Security isomorphism axes

In addition to the general axes, security-critical:

| Axis | What changes if you break it |
|------|------------------------------|
| **Authorization check location** | moving it can expose endpoints |
| **Authorization check coverage** | a refactored endpoint may skip the check |
| **Input validation strictness** | relaxing accepts attack payloads |
| **Error message information disclosure** | specific errors aid attackers (see P34) |
| **Timing side-channel** | constant-time comparison matters for secrets |
| **Secret lifetime** | leaking a secret into a log retention window is catastrophic |
| **Rate-limit key composition** | changing keys can let attackers bypass |
| **CSRF token generation / validation** | subtle changes can invalidate tokens |
| **Cookie attributes** (Secure, HttpOnly, SameSite) | downgrading any is a regression |
| **Session revocation** | refactors may break logout / password-change flows |
| **Webhook signature verification** | constant-time compare; algorithm version |
| **Audit log completeness** | every security-relevant action must still emit |
| **RLS policy** | postgres RLS silently allows/blocks depending on policy eval order |
| **TLS/SSL enforcement** | refactored middleware may drop HSTS or HTTPS redirect |

---

## Never-simplify list

Code that looks simplifiable but must NEVER be touched without security-aware review:

### 1. Constant-time comparisons

```rust
// DO NOT "simplify" to ==
use subtle::ConstantTimeEq;
if user_provided.as_bytes().ct_eq(expected.as_bytes()).into() { ... }

// Python: hmac.compare_digest(a, b), not a == b
```

The `==` comparison short-circuits and leaks timing. Attackers exploit it. Never collapse to `==`.

### 2. Authorization checks at every endpoint

```typescript
// DO NOT extract to a middleware that some routes might skip
export async function handleAdmin(req) {
    const user = await authenticate(req);
    if (!user.isAdmin) throw new ForbiddenError();
    // ...
}
```

"This is duplicated on 30 handlers, let me extract" is correct in general, WRONG here. Either use a router-level middleware that's applied to every admin route (not individual handlers), or keep the check inline. The risk is one handler accidentally not wired into the middleware.

### 3. Token generation randomness

```python
# DO NOT swap for random.randint or Math.random
import secrets
token = secrets.token_hex(32)
```

`random` (non-cryptographic) is predictable. Never switch.

### 4. Password hash parameters

```rust
// DO NOT change the iteration count "to simplify"
let hash = argon2::hash_encoded(pw, salt, &Argon2::default())?;
```

Iteration counts are tuned for a specific security level. Lowering is a regression.

### 5. Webhook signature algorithm

```typescript
// DO NOT "modernize" from hex to base64, or change HMAC algorithm
const expected = crypto.createHmac('sha256', secret).update(body).digest('hex');
```

The format is a contract with the sender. Never refactor without coordinating.

### 6. RLS policies in SQL

```sql
CREATE POLICY users_self_only ON users FOR SELECT
  USING (auth.uid() = id);
```

RLS refactors have silently leaked data before. Never refactor without [supabase](../../supabase/SKILL.md) or equivalent RLS review.

### 7. CSRF / CORS / security headers

```typescript
// DO NOT loosen CORS origin checks during a refactor
app.use(cors({ origin: 'https://app.example.com', credentials: true }));
```

Changing `origin: true` or `origin: '*'` during refactor is a serious regression.

---

## Authentication refactors

### Safe: extracting a validator

```typescript
// before — every handler does JWT decode + expiry check inline
if (!req.headers.authorization) throw 401;
const token = req.headers.authorization.split(' ')[1];
const decoded = jwt.verify(token, SECRET);
if (decoded.exp < Date.now()/1000) throw 401;

// after
async function requireAuth(req): Promise<User> {
  const token = extractBearerToken(req);
  const decoded = jwt.verify(token, SECRET);
  if (decoded.exp < Date.now()/1000) throw new AuthError('expired');
  return loadUser(decoded.sub);
}
```

**Isomorphism card additions:**
- Authentication happens on every path? (Yes — via router-level middleware).
- JWT algorithm / secret / kid unchanged? (Yes).
- Error types unchanged? (Yes — still 401).
- Timing constant for invalid vs valid token? (Verify with `hyperfine`).

### Risky: moving authentication to middleware

If some routes previously auth'd and some didn't, middleware requires *every* route to handle the auth header (or explicitly skip). A route that accidentally skips is an open door.

**Rule:** before the refactor, enumerate every route. Tag each "auth-required" vs "public." After the refactor, the middleware applies to auth-required routes only, and the tagging is explicit (e.g., a `@public` decorator, or routes registered on a separate router).

### Never: rolling your own crypto

Don't migrate from a well-known library (jose, jsonwebtoken, jwt-rs) to a hand-rolled implementation.

---

## Authorization / RLS refactors

### Pattern: extract an authorize helper

```rust
// before — every handler
let user = get_user(req).await?;
if !user.is_admin() && user.id != requested_resource_owner {
    return Err(Forbidden);
}

// after
fn authorize(user: &User, resource: &Resource) -> Result<(), Forbidden> {
    if user.is_admin() || user.id == resource.owner_id { Ok(()) } else { Err(Forbidden) }
}
```

**Isomorphism:** same decision function. Verify by property test:
```rust
proptest! {
    #[test]
    fn authorize_matches_old(user: User, resource: Resource) {
        prop_assert_eq!(
            authorize(&user, &resource),
            old_inline_check(&user, &resource)
        );
    }
}
```

### RLS refactors: always ask a reviewer

Postgres RLS evaluates policies in specific order. Changing policy names, reordering, or consolidating can shift eval semantics. Always:

1. Snapshot current policies: `\d+ users` in psql.
2. Apply refactor.
3. Snapshot again.
4. Diff. The diff goes into the commit message.

---

## Input-validation / boundary refactors

### Canonical collapse (safe)

Use [boundary_validator_scaffold.sh](../scripts/boundary_validator_scaffold.sh) for validator scaffolding.

Pair it with [TYPE-SHRINKS.md](TYPE-SHRINKS.md) when shrinking public data types. Moving `any` / `dict` / `interface{}` parsing behind a zod/pydantic/serde validator is a huge win.

**Security isomorphism:**
- Validation strictness: same or *stricter*. Never loosen.
- Rejection path: throws where before passed → generally good (previously accepted invalid input).
- Error messages: validator library defaults may leak field names; use custom error handling at the boundary.

### Specific: never loosen regex validators

```python
# before
email_re = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
# DO NOT "simplify"
email_re = re.compile(r'.*@.*')   # matches anything with @
```

### Specific: never remove SQL parameterization

```typescript
// before — parameterized
await db.query('SELECT * FROM users WHERE id = $1', [userId]);
// DO NOT "simplify"
await db.query(`SELECT * FROM users WHERE id = ${userId}`);  // SQL injection
```

If you see a refactor that changes `?` / `$1` / `:id` placeholder style: alarm.

---

## Rate-limiting / abuse-prevention refactors

### Pattern: unifying two rate-limit middlewares

```typescript
// before — two different impls
app.use('/api/v1', rateLimitV1);
app.use('/api/v2', rateLimitV2);
// after — one impl
app.use('/api', rateLimit({ windowMs: 60_000, max: 60 }));
```

**Isomorphism axes:**
- Key composition: both old impls used `req.ip`? Or one used `user.id`? Changing keys during refactor can let attackers get two windows instead of one.
- Window size: same (60s in this case).
- Rejection action: same (429, same headers).
- Storage: Redis key prefix must not change (in-flight windows would double-count or reset).

Default: don't refactor rate-limit middleware without reviewing against [security-audit-for-saas](../../security-audit-for-saas/SKILL.md).

---

## Secret / credential handling

### Pattern: collapsing env-var reads

```python
# before
JWT_SECRET = os.environ["JWT_SECRET"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
STRIPE_KEY = os.environ["STRIPE_KEY"]

# after — typed config
@dataclass(frozen=True)
class Secrets:
    jwt_secret: str
    db_password: str
    stripe_key: str
    @classmethod
    def from_env(cls) -> 'Secrets':
        return cls(
            jwt_secret=os.environ["JWT_SECRET"],
            db_password=os.environ["DB_PASSWORD"],
            stripe_key=os.environ["STRIPE_KEY"],
        )
secrets = Secrets.from_env()
```

**Isomorphism:** same env vars read, same error on missing. Bonus: typed access downstream.

**Never:**
- Default secrets to empty string or `None` silently. Missing secret must crash loudly at startup.
- Log the Secrets object (`__repr__` should redact).
- Serialize to JSON (`to_dict` must redact).

```python
@dataclass(frozen=True)
class Secrets:
    jwt_secret: str
    def __repr__(self) -> str: return "Secrets(...redacted...)"
```

### Pattern: rotating secret handling

If refactoring to support secret rotation (e.g., multiple active keys during rotation window):

- Old: one secret, fail if invalid.
- New: primary + secondaries; try primary, then fallback to each secondary.

**Behavior change.** Ship as a feature with explicit rollout, not as a refactor.

---

## CSP / CORS / security headers

### Headers are contracts

Every HTTP response header is a contract with:
- Browsers (Content-Security-Policy, X-Frame-Options, Strict-Transport-Security)
- Downstream services (CORS Allow-*)
- Monitoring / probes (Server, X-Request-ID)

**Refactor rule:** identical bytes coming out. If a middleware refactor changes any header string, it's a behavior change. Snapshot headers before/after with a tool like:

```bash
curl -sI https://app.example.com/ > before.txt
# refactor
curl -sI https://app.example.com/ > after.txt
diff before.txt after.txt
```

---

## Session / cookie refactors

### Cookie attribute axes

Every cookie has attributes: `Domain`, `Path`, `Expires`/`Max-Age`, `Secure`, `HttpOnly`, `SameSite`, `Priority`, `Partitioned`.

Changing any during a refactor breaks clients in specific, hard-to-reproduce ways:

- `SameSite=Lax` → `SameSite=Strict`: cross-site POSTs stop working (logins from email links fail).
- `HttpOnly: true` → `HttpOnly: false`: XSS can now steal the cookie.
- `Secure: true` → not set: HTTP requests carry it (session hijacking risk on public wifi).

**Rule:** a refactor touching cookie code must preserve every attribute exactly. The isomorphism card has a Cookie Attributes row:

```
### Cookie attributes
- Domain:   same
- Path:     same
- Max-Age:  same
- Secure:   same (true)
- HttpOnly: same (true)
- SameSite: same (Lax)
```

### Session revocation

If the session store refactors, check:
- Logout still invalidates the session (not just clears the cookie).
- Password change revokes all other sessions of the user.
- Admin "force logout" still works.

These are often implicit; easy to lose in a refactor.

---

## Audit-log preservation

Security-relevant events that MUST still log after refactor:

- Login attempts (success + failure)
- Password changes
- Permission grants / revokes
- Admin actions
- Bulk data access
- API key creation / revocation
- Webhook signature failures
- Rate-limit hits

Grep your audit log emitters before refactor:
```bash
rg 'auditLog|audit_log|SecurityEvent|logSecurityEvent' -n
```

Diff against after-refactor. Missing lines = regression.

---

## Security-aware isomorphism card (template)

For any refactor in the when-to-use-this-file scope, append these rows to the standard card:

```markdown
### Security axes
- Auth check location:   [same / moved — describe]
- Auth check coverage:   [100% of protected routes still checked — verified by X]
- Input validation:      [same or stricter; regexes unchanged]
- Error messages:        [unchanged; no new info disclosure]
- Timing constant:       [if secret comparison — verified]
- Secret lifetime:       [no new logs containing secrets]
- Rate-limit keys:       [same composition]
- CSRF handling:         [same]
- Cookie attributes:     [Domain/Path/Max-Age/Secure/HttpOnly/SameSite all preserved]
- Session revocation:    [logout/password-change/admin-revoke paths unaffected]
- RLS policies:          [policy names + eval order unchanged]
- CSP / CORS / headers:  [HTTP response bytes identical (curl -I before/after)]
- Audit log emitters:    [all grep'd before/after; diff empty]
- Webhook sig algo:      [unchanged]
- TLS/HSTS enforcement:  [unchanged]
```

If any row can't be answered "same/unchanged," the refactor is not a refactor — it's a security change. Ship as a planned security-approved PR, not a simplification.

---

## Integration with the loop

### Phase B (map)

When scanning, flag security-adjacent files. Score them with Risk = 5 by default:
```bash
# Security-adjacent files in the dup scan
rg -l 'authenticate|authorize|validate|secret|token|crypto|rlimit|rate.?limit|csrf|cors' src/
```

These need security review before any refactor, regardless of score.

### Phase D (prove)

Append the security isomorphism axes to every card for these files.

### Phase F (verify)

Add a security-specific verify step:
```bash
./scripts/verify_isomorphism.sh <run>
# + security-specific
diff <(curl -sI https://staging/... ) refactor/artifacts/<run>/headers_before.txt
```

### Post-verify

For security-touching refactors, **always request a second-agent review via [code-review-gemini-swarm-with-ntm](../../code-review-gemini-swarm-with-ntm/SKILL.md)** or [multi-model-triangulation](../../multi-model-triangulation/SKILL.md) before merging. Second opinion is cheap insurance.
