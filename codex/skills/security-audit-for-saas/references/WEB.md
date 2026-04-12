# Web Security Checklist

Standard web attack vector mitigations specific to SaaS applications.

---

## Open Redirect Prevention

### The Protocol-Relative URL Bypass
`startsWith("/")` alone allows `//evil.com` which redirects to the attacker's domain.

```typescript
// BAD - allows //evil.com
if (url.startsWith("/")) return redirect(url);

// GOOD - blocks protocol-relative URLs
if (url.startsWith("/") && !url.startsWith("//")) return redirect(url);
```

### Shared Safe Redirect Function
Create ONE function, use it everywhere:

```typescript
export function getSafeRedirectPath(path: string): string {
  if (!path) return "/";
  if (!path.startsWith("/")) return "/";
  if (path.startsWith("//")) return "/";
  if (path.includes("://")) return "/";
  if (path.includes("\\")) return "/";
  return path;
}
```

### Audit All Redirect Points
- [ ] Auth callback redirects
- [ ] SSO entry/callback redirects
- [ ] Subscribe page `returnTo` parameter
- [ ] Post-login redirects
- [ ] Post-checkout redirects
- [ ] Email verification redirects
- [ ] Password reset redirects

**Every redirect from user input must go through `getSafeRedirectPath()`.**

---

## CSRF Protection

### Implementation
- [ ] Origin/Referer header validation for state-changing requests (POST, PUT, DELETE, PATCH)
- [ ] Development allowances for localhost
- [ ] Webhook endpoints properly exempted
- [ ] API key auth requests skip CSRF

### Critical Rule
**Never fall back to session auth when Authorization header is present.**

```typescript
// BAD - allows CSRF with fake bearer token
if (authHeader) {
  user = await validateToken(authHeader);
  if (!user) user = await getSessionUser(cookies); // CSRF bypass!
}

// GOOD - no fallback when auth header present
if (authHeader) {
  user = await validateToken(authHeader);
  if (!user) return unauthorized();
} else {
  // Session auth with CSRF validation
  validateCsrf(request);
  user = await getSessionUser(cookies);
}
```

---

## SSRF Prevention

Webhook delivery and any user-provided URL fetching must block internal addresses.

### Blocked Ranges
```
127.0.0.0/8       (loopback)
10.0.0.0/8        (private)
172.16.0.0/12     (private)
192.168.0.0/16    (private)
169.254.0.0/16    (link-local / AWS metadata)
::1               (IPv6 loopback)
fc00::/7          (IPv6 private)
```

### Dual Validation
- [ ] Config-time validation: `validateWebhookUrlForConfig()` when user saves URL
- [ ] Delivery-time validation: `validateWebhookDeliveryTarget()` when actually sending
- [ ] Both validations use the SAME shared function (prevent divergence)
- [ ] DNS rebinding protection: resolve hostname and check IP BEFORE connecting

---

## Content Security

### User-Generated Markdown
- [ ] Sanitized with allowlist approach (not blocklist)
- [ ] Use `rehype-sanitize` or equivalent
- [ ] Test coverage for: script injection, `javascript:` protocol, event handlers, iframe/embed, style/CSS attacks, SVG attacks
- [ ] External links use `rel="noreferrer noopener"`
- [ ] No raw `dangerouslySetInnerHTML` on user content

### Input Validation
- [ ] All user input validated with Zod schemas (not `as string` casts)
- [ ] Max-length constraints on all string fields
- [ ] Feedback/comment fields have length limits (prevent log bloat attacks)
- [ ] File upload size limits enforced server-side

---

## HTTP Security Headers

### Required Headers
- [ ] `Strict-Transport-Security: max-age=31536000; includeSubDomains` (HSTS)
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `X-Frame-Options: DENY`
- [ ] `Referrer-Policy: strict-origin-when-cross-origin`
- [ ] `Permissions-Policy: camera=(), microphone=(), geolocation=()`
- [ ] `Content-Security-Policy` (appropriate for the application)

### Cookie Security
- [ ] `secure: true` in production
- [ ] `sameSite: "lax"` minimum
- [ ] `httpOnly: true` where possible (Supabase auth cookies are a known exception)
- [ ] Locale/preference cookies should use `httpOnly: true`

---

## CORS Configuration

### Audit
- [ ] No global `Access-Control-Allow-Origin: *` in Next.js config
- [ ] Individual endpoints with `*` are intentional and documented (e.g., public telemetry, anonymous install endpoint)
- [ ] Endpoints with `*` do NOT set `Access-Control-Allow-Credentials`
- [ ] Authenticated endpoints restrict origin to known domains

### Safe Pattern for Public Endpoints
```typescript
// Only for truly public, anonymous endpoints
headers: {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
  // NO Access-Control-Allow-Credentials
}
```

---

## Rate Limiting Architecture

### Tiered by Auth Level
| Tier | Example Limit | Scope |
|------|--------------|-------|
| Anonymous | 60 req/min | Per IP |
| Authenticated | 120 req/min | Per user |
| Subscriber | 300 req/min | Per user |
| CLI (API key) | 600 req/min | Per key |

### Endpoint-Specific Limits
- [ ] Admin endpoints have additional per-endpoint limits
- [ ] Catalog/search endpoints have separate limits
- [ ] Auth endpoints have strict independent limits (see AUTH.md)

### Implementation
- [ ] Redis-backed (not in-memory) in serverless environments
- [ ] Graceful degradation when Redis unavailable (allow, don't block)
- [ ] IP detection uses trusted header (`x-real-ip` on Vercel is safe; document deployment constraint)

---

## Abuse Detection

Multi-signal behavioral analysis:

| Signal | Threshold (example) | Action |
|--------|---------------------|--------|
| `download_denied` | 10/10min | Flag + alert |
| `webhook_signature_failed` | 5/10min | Block + alert |
| `upload_rejected` | 5/1hr | Cooldown |
| `auth_failed` | 10/5min | Temporary block |
| `sequential_enumeration` | 20/1min | Block + alert |
| `scraping_pattern` | 50/5min | Rate limit |

- [ ] Redis-backed with cooldowns and alert flags
- [ ] Abuse signals tracked across related endpoints
- [ ] Alerts for anomalous patterns (burst of webhook failures = potential attack)
