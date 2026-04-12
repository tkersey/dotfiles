# Modern Browser Security APIs

A survey of browser-level security mechanisms beyond CSP and CORS that
every production SaaS should adopt. These are mostly zero-cost
defense-in-depth controls that stop entire bug classes when enabled.

Related: [CSP-PATTERNS.md](CSP-PATTERNS.md), [CORS-DEEP.md](CORS-DEEP.md),
[WEB.md](WEB.md), [WEBAUTHN-PASSKEYS.md](WEBAUTHN-PASSKEYS.md).

---

## The modern defense-in-depth stack

A fully-hardened SaaS web surface uses all of these:

1. **HTTPS + HSTS** (transport)
2. **CSP** (XSS + injection defense)
3. **Trusted Types** (DOM-XSS elimination)
4. **COOP / COEP / CORP** (cross-origin isolation)
5. **Permissions-Policy** (feature surface restriction)
6. **Fetch Metadata** (request context validation)
7. **Referrer-Policy** (URL leak prevention)
8. **Subresource Integrity** (supply chain defense)
9. **Clear-Site-Data** (logout hygiene)
10. **CORS + SameSite cookies** (authenticated request control)

If your app uses fewer than 7 of these, you have headroom.

---

## Cross-origin isolation: COOP / COEP / CORP

These three headers work together to give your origin a **hard isolation
boundary**, enabling access to powerful APIs (`SharedArrayBuffer`,
high-precision `performance.now()`) while closing entire attack classes
like Spectre and cross-origin window access.

### Cross-Origin-Opener-Policy (COOP)

Controls whether your window can interact with windows from other
origins opened from or to yours.

```http
Cross-Origin-Opener-Policy: same-origin
```

**Effects:**
- `window.opener` returns `null` for cross-origin openers (no more
  tabnabbing)
- Popups from other origins cannot communicate with your page
- Prevents `window.opener.location = 'evil'` attacks from links you
  open

**Always safe to set** `same-origin` on auth pages and admin surfaces.
Use `same-origin-allow-popups` if you open third-party popups (OAuth
flows) and need `window.open` to still work.

### Cross-Origin-Embedder-Policy (COEP)

Controls whether cross-origin resources can be loaded into your page
without explicit opt-in.

```http
Cross-Origin-Embedder-Policy: require-corp
```

**Effects:**
- Every embedded resource (image, script, iframe, fetch) must send
  `Cross-Origin-Resource-Policy: cross-origin` or a CORS response
- Eliminates speculative cross-origin reads (Spectre class attacks)
- Required for `SharedArrayBuffer` access

**Cost:** breaks naive `<img src="https://cdn.other.com/logo.png">`
unless the CDN opts in. Adoption requires auditing every third-party
embed.

Alternative: `credentialless` (Chrome 96+) — loads cross-origin
resources without credentials, avoiding the opt-in requirement for
non-credentialed fetches.

### Cross-Origin-Resource-Policy (CORP)

Controls whether other origins can embed **your** resources.

```http
Cross-Origin-Resource-Policy: same-origin
```

**Effects:**
- Prevents `<img src>`, `<script src>`, etc. from other origins
  loading your resource
- Stops cross-origin bandwidth theft
- Mitigates Spectre-style side-channel reads

**Recommendation:** set `same-origin` on all API responses. Set
`cross-origin` only for public static assets that need to be embeddable.

### The full isolation trio

```http
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
Cross-Origin-Resource-Policy: same-origin
```

Together they give you "cross-origin isolation." You can now use:
- `SharedArrayBuffer` (needed for WebAssembly threads)
- High-precision `performance.now()`
- `crossOriginIsolated` flag is true

If you don't need these APIs, you still benefit from the isolation.

---

## Trusted Types

DOM-based XSS happens when untrusted strings reach sinks like
`innerHTML`, `document.write`, `eval`, or `setAttribute('on*', ...)`.
Trusted Types enforces at the browser level that these sinks only
accept typed objects, not raw strings.

```http
Content-Security-Policy: require-trusted-types-for 'script'
Content-Security-Policy: trusted-types default myapp
```

Now this throws:
```javascript
element.innerHTML = userInput; // TypeError: Failed to set 'innerHTML'
```

You must create a policy that vets strings:
```javascript
const policy = trustedTypes.createPolicy('myapp', {
  createHTML: (s) => DOMPurify.sanitize(s),
});
element.innerHTML = policy.createHTML(userInput);
```

**Impact:** eliminates DOM-XSS almost entirely. Google's YouTube and
Gmail use Trusted Types to enforce this at billion-user scale.

**Rollout strategy:**

1. Start with `Content-Security-Policy-Report-Only` to measure
   violations
2. Fix call sites incrementally (wrap with DOMPurify or a library
   like `safevalues`)
3. Enforce once violation rate is zero
4. Use reporting endpoint to catch regressions

### Library support

- React: render paths are safe; escape hatches (`dangerouslySetInnerHTML`)
  are the hot spots
- Angular: has a built-in Trusted Types compatible sanitizer
- Vue: manual work needed for `v-html`
- Lit: safe by default

---

## Permissions-Policy

The successor to Feature-Policy. Restricts which browser features your
page and its iframes can use.

```http
Permissions-Policy:
  accelerometer=(),
  camera=(),
  geolocation=(self),
  microphone=(),
  payment=(self),
  usb=(),
  gyroscope=(),
  magnetometer=(),
  clipboard-read=(),
  interest-cohort=()
```

**Why this matters:**

- Reduces your fingerprint surface (fewer unique identifiers)
- Prevents iframe-based feature abuse
- Blocks FLoC / Topics API data leakage (`interest-cohort=()`)
- Disables features you don't use, shrinking the XSS→feature-abuse
  chain

### Common SaaS baseline

```http
Permissions-Policy:
  camera=(),
  microphone=(),
  geolocation=(),
  payment=(self "https://js.stripe.com"),
  usb=(),
  serial=(),
  bluetooth=(),
  accelerometer=(),
  gyroscope=(),
  magnetometer=(),
  ambient-light-sensor=(),
  autoplay=(self),
  encrypted-media=(self),
  fullscreen=(self),
  picture-in-picture=(self),
  clipboard-read=(self),
  clipboard-write=(self),
  cross-origin-isolated=(self)
```

Adjust by feature. Never allow more than you actually use.

---

## Fetch Metadata headers

Browsers automatically send `Sec-Fetch-*` headers describing the
request context. These are **server-side attacker-unforgeable** (they
come from the browser, not user JS).

| Header | Values | Meaning |
|--------|--------|---------|
| `Sec-Fetch-Site` | same-origin, same-site, cross-site, none | Relationship of request initiator |
| `Sec-Fetch-Mode` | cors, navigate, no-cors, same-origin, websocket | How the request was made |
| `Sec-Fetch-Dest` | document, script, image, iframe, ... | What the response will be used as |
| `Sec-Fetch-User` | ?1 (present if user-initiated) | User gesture? |

### Defense pattern: Resource Isolation Policy

Block requests that don't make sense for the endpoint type:

```javascript
function rip(req, res, next) {
  const site = req.headers['sec-fetch-site'];
  const mode = req.headers['sec-fetch-mode'];
  const dest = req.headers['sec-fetch-dest'];

  // API endpoints should never be loaded as documents
  if (req.path.startsWith('/api/') && dest === 'document') {
    return res.status(403).end();
  }

  // Admin endpoints only from same-origin
  if (req.path.startsWith('/admin/') && site !== 'same-origin' && site !== 'none') {
    return res.status(403).end();
  }

  // Sensitive POSTs require user gesture on navigate
  if (req.method === 'POST' && mode === 'navigate' && !req.headers['sec-fetch-user']) {
    return res.status(403).end();
  }

  next();
}
```

This stops CSRF, clickjacking, and a whole family of confused-deputy
attacks with near-zero code.

---

## Referrer-Policy

Controls what the browser sends in `Referer` on outbound navigation
and requests.

```http
Referrer-Policy: strict-origin-when-cross-origin
```

**Common values:**

- `no-referrer` — send nothing. Maximum privacy, may break analytics.
- `same-origin` — referrer only on same-origin requests.
- `strict-origin` — origin only (no path), and only over HTTPS.
- `strict-origin-when-cross-origin` — **recommended default**. Full URL
  for same-origin, origin only for cross-origin, nothing for downgrade.
- `no-referrer-when-downgrade` — old default, unsafe.
- `unsafe-url` — never use.

**Why it matters:** URLs often contain session IDs, reset tokens, or
user data in query strings. A bad `Referrer-Policy` leaks these to
third parties (analytics, fonts, CDNs).

---

## Subresource Integrity (SRI)

Pin third-party script hashes. If the CDN serves a different file, the
browser refuses to execute it.

```html
<script src="https://cdn.example.com/library.js"
        integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8wC"
        crossorigin="anonymous"></script>
```

**Use when:** loading any third-party script that isn't under your
control. Particularly critical for analytics, A/B testing, CMS widgets.

**Gotchas:**
- If the library updates, you must update the hash. Build this into
  your dependency management.
- SRI only works on scripts and stylesheets, not arbitrary fetches.
- Library providers sometimes publish unhashed "rolling" versions.
  Use pinned version URLs.

See also [SUPPLY-CHAIN-DEEP.md](SUPPLY-CHAIN-DEEP.md) for the broader
supply chain angle.

---

## Clear-Site-Data

On logout, tell the browser to wipe all local state:

```http
Clear-Site-Data: "cache", "cookies", "storage", "executionContexts"
```

**Effects:**
- Clears all cookies for the origin
- Clears localStorage, sessionStorage, IndexedDB, SW caches
- Terminates and reloads execution contexts
- No more "log out but session ghosts in localStorage"

**When to set:**
- Explicit logout endpoints
- Password change endpoints
- After administrative session termination
- Account deletion

**Gotcha:** `Clear-Site-Data` is aggressive. If your logout endpoint
is cached by a CDN, you'll nuke every visitor. Make sure logout
responses are `Cache-Control: no-store`.

---

## Strict-Transport-Security (HSTS)

The foundation. Forces HTTPS for your origin.

```http
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
```

- `max-age=63072000` — 2 years
- `includeSubDomains` — applies to all subdomains
- `preload` — registers in the browser's preload list
  (https://hstspreload.org)

**Preload carefully.** Once you're in the list, removal takes months.
Test with `max-age=3600` first, then promote.

---

## Cookie security flags (full list)

Auth cookies should have every hardening flag set:

```http
Set-Cookie: session=abc;
  Secure;           # HTTPS only
  HttpOnly;         # No JS access
  SameSite=Lax;     # CSRF mitigation
  Path=/;           # Scope to whole site
  Domain=.mycompany.com;   # Optional, only if needed
  Max-Age=3600;     # Bounded lifetime
  __Host-session=abc  # Prefix: requires Secure, no Domain, Path=/
```

The `__Host-` prefix is a modern hardening: the cookie is only valid
if served over HTTPS, has no `Domain`, and has `Path=/`. Prevents
subdomain cookie attacks.

---

## Origin Private File System (OPFS)

If you need client-side file storage, OPFS is sandboxed to the origin
and inaccessible to other origins. Safer than exposing local
filesystem APIs.

```javascript
const root = await navigator.storage.getDirectory();
const file = await root.getFileHandle('draft.txt', { create: true });
```

Use for drafts, offline caches, temporary files. Never store secrets
here — it's accessible to XSS.

---

## Storage Access API

If your site needs third-party cookies (e.g., for embedded widgets),
the Storage Access API lets you request them explicitly after user
gesture. Mandatory with modern browser third-party cookie blocking.

```javascript
if (await document.hasStorageAccess() === false) {
  await document.requestStorageAccess();
}
```

---

## Private State Tokens (Trust Tokens)

New API for anti-fraud and bot detection without cross-site tracking.
Lets a trusted issuer sign tokens that downstream sites can verify
without learning user identity.

```javascript
const token = await fetch('https://issuer.com/issue', {
  trustToken: { type: 'token-request', issuer: 'https://issuer.com' }
});
```

Still early, but worth watching for bot-detection use cases (see
Vercel BotID from the platform knowledge update).

---

## Deprecation watch

These APIs are dying — audit and remove:

| API | Status | Replacement |
|-----|--------|-------------|
| `document.domain` | Deprecated, removed in 2025 | postMessage |
| `X-Frame-Options` | Superseded by `frame-ancestors` in CSP | CSP frame-ancestors |
| `X-XSS-Protection` | Removed by all browsers | CSP |
| `Expect-CT` | Deprecated | Built into TLS |
| `Public-Key-Pins (HPKP)` | Removed | Expect-CT, SCT |
| `Feature-Policy` | Deprecated | Permissions-Policy |
| `Application Cache` | Removed | Service Workers |

Remove these from your headers if present. They may conflict with
modern equivalents.

---

## Header bundle for a hardened SaaS

Drop this into your framework middleware:

```http
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
Content-Security-Policy: default-src 'self'; [see CSP-PATTERNS.md]
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: credentialless
Cross-Origin-Resource-Policy: same-origin
Permissions-Policy: [see baseline above]
Referrer-Policy: strict-origin-when-cross-origin
X-Content-Type-Options: nosniff
Cache-Control: no-store (on auth routes)
```

And on the response for auth routes:
```http
Clear-Site-Data: "cache", "cookies", "storage"
```

---

## Testing your headers

Automated tools:

- [securityheaders.com](https://securityheaders.com) — grading
- [observatory.mozilla.org](https://observatory.mozilla.org) — grading + advice
- [crossoriginisolated.com](https://crossoriginisolated.com) — COOP/COEP check
- Chrome DevTools → Security tab → per-origin report

Aim for A+ on securityheaders.com and A on Mozilla Observatory.
Anything less means you have low-hanging hardening fruit.

---

## Audit checklist

- [ ] HSTS with `max-age ≥ 1 year` + `includeSubDomains`
- [ ] CSP enforced (not just Report-Only)
- [ ] Trusted Types enforced on script sinks
- [ ] COOP `same-origin` on auth/admin pages
- [ ] COEP `credentialless` or `require-corp` where possible
- [ ] CORP `same-origin` on all API responses
- [ ] Permissions-Policy disables every unused feature
- [ ] Fetch Metadata validation enforced server-side
- [ ] Referrer-Policy `strict-origin-when-cross-origin` or stricter
- [ ] SRI on all third-party scripts
- [ ] Clear-Site-Data on logout
- [ ] `__Host-` prefix on session cookies
- [ ] No legacy `X-XSS-Protection`, `X-Frame-Options`, or `document.domain` usage
- [ ] Header grade A+ on external scanners

Every missing item is a defense-in-depth layer you're not using.
