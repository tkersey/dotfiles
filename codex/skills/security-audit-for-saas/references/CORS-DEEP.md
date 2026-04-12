# CORS Deep Dive

CORS is one of the most misunderstood web security mechanisms. It is
not an authorization system — it is a browser-enforced relaxation of
the same-origin policy. Getting it wrong turns your API into a
cross-origin free-for-all.

Related: [WEB.md](WEB.md), [CSP-PATTERNS.md](CSP-PATTERNS.md),
[SESSION-MANAGEMENT.md](SESSION-MANAGEMENT.md).

---

## What CORS actually does

CORS (Cross-Origin Resource Sharing) tells browsers when it is safe to
allow JavaScript running on origin A to read a response from origin B.

Critical properties:

1. **CORS does not protect your API.** An attacker with curl doesn't
   care about CORS. CORS protects the *user's browser* from a malicious
   website reading your API using the user's credentials.
2. **Same-origin is still default.** CORS only applies when the request
   is cross-origin.
3. **Credentials mode matters.** `withCredentials: true` changes
   everything.
4. **Preflight is advisory.** A permissive preflight doesn't block
   damage from a "simple" request.

---

## The request lifecycle

### Simple requests

A request is "simple" if it uses `GET`, `HEAD`, or `POST` with
standard headers and a whitelist content type (`text/plain`,
`application/x-www-form-urlencoded`, `multipart/form-data`).

**Simple requests are sent without preflight.** The browser sends the
request, receives the response, and *then* decides whether JavaScript
can read it based on `Access-Control-Allow-Origin`.

**Implication:** a simple POST can be sent by a malicious site. If
it has side effects (e.g., form submission), the damage is done even
if the browser blocks the response read. This is classic CSRF territory.

### Preflighted requests

Non-simple requests (custom headers, JSON, PUT/DELETE) trigger a
preflight `OPTIONS` request. The browser asks the server "can I make
this request?" and only proceeds if the response approves.

Preflight caches based on `Access-Control-Max-Age`. Attackers cannot
bypass preflight — but a permissive preflight policy gives them wide
latitude.

---

## The attack surface

### 1. Origin reflection with credentials

The classic bug. The server echoes `Origin` into `Access-Control-Allow-Origin`
and sets `Access-Control-Allow-Credentials: true`.

```http
Request:
  Origin: https://evil.com

Response:
  Access-Control-Allow-Origin: https://evil.com   ← BAD
  Access-Control-Allow-Credentials: true          ← CATASTROPHIC
```

Impact: any origin can make credentialed requests to your API and
*read* the response. Full account takeover from any malicious site.

**Audit:**
```
grep -rn "Access-Control-Allow-Origin.*req\.\|origin\|header" src/
```

Look for any code that dynamically sets the header from request data
and doesn't validate against an allowlist.

### 2. Null origin bypass

Some servers treat `Origin: null` as "not cross-origin" or allow it
explicitly. `null` origin happens when:

- File:// origin
- Sandboxed iframe without `allow-same-origin`
- Redirect chain from data:// URL

**Attack:** put your exploit in a sandboxed iframe on a phishing page,
and the browser sends `Origin: null`. If the server allows it,
credentials flow.

**Never allow `null` origin with credentials.** Period.

### 3. Wildcard with credentials (spec bypass)

```http
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

The spec says browsers should reject this combination. Most do. But:

- Old browsers may not
- Proxies and middleware sometimes reorder or strip headers
- WebView-based apps behave inconsistently
- Some servers send `*` only when `Origin` is absent but credentials
  still flow through cached proxies

Just don't do it.

### 4. Subdomain regex bugs

Common pattern: "allow anything on *.mycompany.com."

Buggy implementation:
```javascript
if (origin.endsWith('mycompany.com')) { allow(origin); }
// Attacker: https://evilmycompany.com ← bypasses
```

Correct:
```javascript
const url = new URL(origin);
if (ALLOWED_HOSTS.has(url.hostname)) { allow(origin); }
```

Also problematic:
```javascript
if (/^https:\/\/.*\.mycompany\.com$/.test(origin)) // ← unbounded
// Attacker: https://x.mycompany.com.evil.com ← bypasses
```

Correct:
```javascript
if (/^https:\/\/[a-z0-9-]+\.mycompany\.com$/.test(origin))
```

### 5. Protocol downgrade

Allowing `http://` for development and never removing it in production:

```javascript
const ALLOWED = ['https://app.mycompany.com', 'http://localhost:3000'];
// localhost:3000 in prod config ← subtle bypass via DNS rebinding
```

DNS rebinding attacks can make `localhost` resolve to an attacker IP
momentarily. If the API trusts `http://localhost:*`, the attack works.

**Rule:** never allow `http://` in production CORS. Ever. Not even
for localhost.

### 6. Port confusion

`https://app.mycompany.com:443` vs `https://app.mycompany.com`. Same
origin per the spec (default ports). But some code normalizes one and
not the other, creating mismatches.

If your CORS middleware computes an allowlist, make sure it normalizes
ports.

### 7. Allow-list via prefix match

```javascript
if (ALLOWED.some(a => origin.startsWith(a))) // ← prefix bug
// ALLOWED = 'https://app.mycompany.com'
// Attacker: https://app.mycompany.com.evil.com
```

Always compare full origin strings, not prefixes.

### 8. Credentialed preflight with permissive headers

```http
Access-Control-Allow-Origin: https://trusted.com
Access-Control-Allow-Credentials: true
Access-Control-Allow-Headers: *          ← BAD
Access-Control-Allow-Methods: *          ← BAD
```

`Access-Control-Allow-Headers: *` means "allow any custom header." An
attacker can now include `Authorization: Bearer <stolen-token>` on a
credentialed request. Enumerate headers explicitly.

### 9. Access-Control-Expose-Headers leaking sensitive response headers

```http
Access-Control-Expose-Headers: X-Total-Count, X-Internal-Debug-Info
```

`X-Internal-Debug-Info` is now readable by JavaScript cross-origin.
If it contains user IDs, session data, or internal state, you've leaked
it. Only expose headers the client legitimately needs.

### 10. CORS vs CSRF confusion

Many teams disable CSRF protection because "we have CORS." This is
wrong. CORS does not prevent:

- Simple POST requests (no preflight, side effects execute)
- GET requests (always allowed)
- Requests from native apps (no CORS enforcement)
- Requests from tools (curl, scripts, proxies)

**You need both CORS and CSRF protection.** See [WEB.md](WEB.md).

---

## The correct CORS pattern

```javascript
// Express/Node example
const ALLOWED_ORIGINS = new Set([
  'https://app.mycompany.com',
  'https://admin.mycompany.com',
]);

app.use((req, res, next) => {
  const origin = req.headers.origin;

  // No origin: not a CORS request, skip CORS headers entirely
  if (!origin) return next();

  // Strict allowlist check
  if (!ALLOWED_ORIGINS.has(origin)) {
    // Don't set CORS headers — browser will block
    return next();
  }

  res.setHeader('Access-Control-Allow-Origin', origin);
  res.setHeader('Vary', 'Origin'); // cache correctness
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-CSRF-Token');
  res.setHeader('Access-Control-Max-Age', '600');

  if (req.method === 'OPTIONS') return res.sendStatus(204);
  next();
});
```

Key correctness points:

- **Allowlist, not reflection.** Origin is only echoed if it's in a
  pre-declared set.
- **`Vary: Origin`** is critical. Without it, CDNs and browsers can
  serve a cached response with the wrong `Allow-Origin`.
- **Explicit methods and headers.** No wildcards.
- **Opt-in credentials.** Only on routes that need it.
- **Omit headers entirely** if origin isn't allowed. Don't echo a
  rejection — just don't send the headers.

---

## Per-route CORS policies

Not every API route needs the same CORS policy. A `/api/public/ping`
endpoint is different from `/api/user/delete`.

Recommended split:

| Route type | CORS policy |
|------------|-------------|
| Public health checks, static content | `Allow-Origin: *`, no credentials |
| Public unauthenticated APIs | Allowlist, no credentials |
| Authenticated user APIs | Allowlist, credentials enabled |
| Admin APIs | No CORS (admin.mycompany.com only, same-origin) |
| Webhook receivers | No CORS (server-to-server only) |

---

## CORS + cookies: the cookie-specific pitfalls

CORS interacts with cookies in surprising ways:

1. **SameSite=Lax blocks most cross-origin POSTs** even if CORS allows
   them. Your API's auth cookies should be `SameSite=Lax` or `Strict`
   by default.
2. **SameSite=None requires Secure.** Modern browsers drop the cookie
   otherwise.
3. **Third-party cookie blocking** (Safari ITP, Firefox ETP) will
   silently strip cookies on cross-origin requests, making users
   "log out" on every navigation. Design for same-origin auth if
   possible.

---

## Preflight caching gotchas

`Access-Control-Max-Age` caches preflight results. This seems like a
performance win but has a footgun: **if you change your CORS policy,
browsers will keep using the old cached decision** until `Max-Age`
expires.

- Chrome caps at 2 hours
- Firefox caps at 24 hours
- Safari caps at 10 minutes

Safe values: 600 (10 minutes) for policies that change, 86400 (24h)
for stable policies. Avoid 0 (disables cache, forces preflight on
every request).

---

## CORS with multiple subdomains

If you have `app.mycompany.com`, `admin.mycompany.com`, and
`api.mycompany.com`, you have two options:

**Option 1: Same-origin via path routing.** All UI and API share
`app.mycompany.com` with API at `/api/*`. No CORS needed.

**Option 2: Explicit allowlist per subdomain.** API at
`api.mycompany.com` allows both `app.*` and `admin.*` by explicit
match. This is the common pattern.

Avoid regex matchers like `*.mycompany.com` — they enable subdomain
takeover attacks to become account takeover (see
[DNS-SECURITY.md](DNS-SECURITY.md)).

---

## Fetch Metadata as a CORS supplement

The `Sec-Fetch-Site`, `Sec-Fetch-Mode`, `Sec-Fetch-Dest`, and
`Sec-Fetch-User` headers tell the server the *context* of a request.
They are attacker-unforgeable in the browser.

Use them as a second line of defense:

```javascript
app.use((req, res, next) => {
  const site = req.headers['sec-fetch-site'];
  const mode = req.headers['sec-fetch-mode'];

  // Block cross-site credentialed requests that aren't expected
  if (site === 'cross-site' && mode === 'cors' && !PUBLIC_ROUTES.has(req.path)) {
    return res.status(403).end();
  }
  next();
});
```

Fetch Metadata is a zero-cost defense-in-depth layer. Adopt it.

---

## CORS misconfiguration checklist

- [ ] No route echoes origin without allowlist validation
- [ ] Allowlist is a strict set of full origin strings (not prefixes,
      not regexes)
- [ ] No `*` with credentials, ever
- [ ] No `null` origin accepted
- [ ] No `http://` in production CORS allowlist
- [ ] `Vary: Origin` set on all CORS responses
- [ ] `Access-Control-Allow-Headers` is an explicit list, not `*`
- [ ] `Access-Control-Expose-Headers` only includes client-safe headers
- [ ] CSRF protection is independent of CORS (don't rely on CORS
      alone)
- [ ] Cookies are `SameSite=Lax` minimum for auth
- [ ] Preflight `Max-Age` is bounded (<24h)
- [ ] Admin surfaces have no CORS (same-origin only)
- [ ] Fetch Metadata headers are consulted as defense-in-depth

---

## Testing your CORS policy

Manual test harness:

```bash
# Origin reflection test
curl -i -X GET https://api.mycompany.com/v1/me \
  -H "Origin: https://evil.com" \
  -H "Cookie: session=..."

# Expected: no Access-Control-Allow-Origin header, or != evil.com

# Null origin test
curl -i -X POST https://api.mycompany.com/v1/user \
  -H "Origin: null" \
  -H "Content-Type: application/json"

# Expected: no CORS headers returned

# Preflight for sensitive method
curl -i -X OPTIONS https://api.mycompany.com/v1/user \
  -H "Origin: https://evil.com" \
  -H "Access-Control-Request-Method: DELETE"

# Expected: 204 with no Access-Control-Allow-Methods: DELETE,
# or no CORS headers at all
```

Automate this for every API route in CI. A single misconfigured route
can break the whole security model.

---

## Real-world incidents

- **Twitter 2015:** CORS misconfiguration on an API let attackers read
  DMs from any site.
- **Facebook 2019:** regex-based subdomain allow enabled bypass via
  `evilfacebook.com`.
- **JetBrains 2020:** IDE update check reflected origin, allowing
  arbitrary JavaScript to read update manifests.
- **Numerous startups:** "Access-Control-Allow-Origin: *" on a
  credentialed API endpoint, found by bounty hunters in minutes.

The common thread: dynamic origin handling without strict validation.
Every one of these would have been prevented by the allowlist pattern.
