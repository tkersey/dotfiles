# Content Security Policy (CSP) Patterns

CSP is the browser's last line of defense against XSS. Done well, it blocks
entire classes of attacks. Done poorly, it either breaks the app or provides
false security. This file covers production CSP patterns.

---

## Why CSP Is Hard

### The Challenge
Modern web apps use: inline scripts, third-party services, dynamic imports,
React/Next.js client bundles, analytics scripts, payment iframes, OAuth
callbacks. Each wants permission in the CSP.

A strict CSP breaks the app. A permissive CSP doesn't protect anything.

### The Goal
Find the tightest CSP that doesn't break your app. Treat unblocked resources
as technical debt.

---

## CSP Directives Reference

### The Core Directives

```
default-src 'self'
  # Default for all resource types not explicitly listed.

script-src 'self' https://cdn.example.com
  # Where JavaScript can load from.

style-src 'self' 'unsafe-inline'
  # Where CSS can load from.

img-src 'self' data: https:
  # Where images can load from.

font-src 'self' https://fonts.gstatic.com
  # Where fonts can load from.

connect-src 'self' https://api.example.com wss://api.example.com
  # Where fetch/XHR/WebSocket can connect to.

frame-src 'none'
  # Where iframes can load.

frame-ancestors 'none'
  # Who can embed THIS page in an iframe (clickjacking protection).

form-action 'self'
  # Where forms can submit to.

base-uri 'self'
  # What <base> tags are allowed.

object-src 'none'
  # <object>, <embed>, <applet> — block these.

upgrade-insecure-requests
  # Automatically upgrade HTTP to HTTPS.
```

---

## The Three Presets

### Preset 1: API Endpoints (Strictest)

API endpoints shouldn't render HTML, so they should have the strictest CSP.

```
default-src 'none'
frame-ancestors 'none'
```

Nothing loads, nothing renders. If an attacker injects HTML into an API
response (content-sniffing attack), this blocks them.

### Preset 2: Documentation / Swagger UI

Docs pages use CDN-hosted assets:

```
default-src 'self'
script-src 'self' https://unpkg.com 'unsafe-inline'
style-src 'self' https://unpkg.com 'unsafe-inline'
font-src 'self' https://fonts.gstatic.com
connect-src 'self'
frame-ancestors 'none'
```

The `'unsafe-inline'` for scripts/styles is required by Swagger UI. Accept it
because docs don't handle sensitive data.

### Preset 3: App (SaaS UI)

The tightest practical CSP for the main app:

```
default-src 'self'
script-src 'self' 'nonce-<random>' https://vercel.live
style-src 'self' 'unsafe-inline'
img-src 'self' data: https: blob:
font-src 'self' data:
connect-src 'self' https://*.supabase.co wss://*.supabase.co https://api.stripe.com
frame-src https://checkout.stripe.com https://js.stripe.com
frame-ancestors 'none'
form-action 'self'
base-uri 'self'
object-src 'none'
upgrade-insecure-requests
```

### Notes on Each Directive

**`script-src 'nonce-<random>'`:**
Per-request nonce for inline scripts. Requires generating a nonce on each
request and passing it to every `<script>` tag.

**`script-src 'unsafe-inline'`:**
Allows all inline scripts. Weaker but simpler. Required if you use libraries
that generate inline scripts (many React libraries do).

**`'strict-dynamic'`:**
Allows scripts loaded by nonced scripts. Good in theory, breaks Next.js in
practice (see [FIELD-GUIDE.md](FIELD-GUIDE.md) Story 3).

**`style-src 'unsafe-inline'`:**
Required for styled-components, emotion, Tailwind JIT, and most CSS-in-JS.
Accept it — CSS injection is less severe than script injection.

**`img-src data: blob:`:**
Required for base64 images (Next.js image component), dynamically-generated
images (canvas), file upload previews.

**`connect-src https://*.supabase.co wss://*.supabase.co`:**
Supabase Realtime requires wss (WebSockets). Easy to miss.

**`frame-src https://checkout.stripe.com https://js.stripe.com`:**
Stripe Elements and Checkout embed via iframe. Add their domains.

**`frame-ancestors 'none'`:**
Prevents your app from being embedded in another site (clickjacking).

**`upgrade-insecure-requests`:**
Rewrites http:// to https:// automatically. Safe to enable unless running
local dev over HTTP.

---

## Per-Path CSP Mounting

Mount different CSPs on different routes:

```typescript
// middleware.ts or proxy.ts

const API_CSP = `
  default-src 'none';
  frame-ancestors 'none';
`;

const DOCS_CSP = `
  default-src 'self';
  script-src 'self' https://unpkg.com 'unsafe-inline';
  style-src 'self' https://unpkg.com 'unsafe-inline';
  font-src 'self' https://fonts.gstatic.com;
  connect-src 'self';
  frame-ancestors 'none';
`;

const APP_CSP = `
  default-src 'self';
  script-src 'self' 'unsafe-inline' https://vercel.live;
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https: blob:;
  font-src 'self' data:;
  connect-src 'self' https://*.supabase.co wss://*.supabase.co https://api.stripe.com;
  frame-src https://checkout.stripe.com https://js.stripe.com;
  frame-ancestors 'none';
  form-action 'self';
  base-uri 'self';
  object-src 'none';
  upgrade-insecure-requests;
`;

export function middleware(req: NextRequest) {
  const pathname = req.nextUrl.pathname;

  let csp: string;
  if (pathname.startsWith('/api/')) {
    csp = API_CSP;
  } else if (pathname.startsWith('/docs') || pathname.startsWith('/redoc')) {
    csp = DOCS_CSP;
  } else {
    csp = APP_CSP;
  }

  const response = NextResponse.next();
  response.headers.set('Content-Security-Policy', csp.replace(/\s+/g, ' ').trim());
  return response;
}
```

### Development Overrides

Local dev often can't use the same CSP:

```typescript
const isProduction = process.env.NODE_ENV === 'production';

const CSP = isProduction
  ? STRICT_PRODUCTION_CSP
  : RELAXED_DEV_CSP; // Allows localhost, http://, etc.
```

---

## Nonce-Based CSP

### The Pattern

```typescript
// middleware.ts
export function middleware(req: NextRequest) {
  const nonce = crypto.randomBytes(16).toString('base64');
  const csp = `script-src 'self' 'nonce-${nonce}'`;

  const response = NextResponse.next();
  response.headers.set('Content-Security-Policy', csp);

  // Pass nonce to the page via header
  response.headers.set('x-nonce', nonce);
  return response;
}
```

In the page:
```tsx
// app/layout.tsx
import { headers } from 'next/headers';

export default function RootLayout({ children }) {
  const nonce = headers().get('x-nonce');

  return (
    <html>
      <body>
        <script nonce={nonce}>
          // This inline script is allowed
          window.dataLayer = window.dataLayer || [];
        </script>
        {children}
      </body>
    </html>
  );
}
```

### The Next.js Reality

Next.js dynamic imports don't carry nonces automatically. This breaks
`'strict-dynamic'`. Workarounds:
1. Use Next.js's built-in CSP integration (experimental)
2. Don't use `'strict-dynamic'`
3. Use `'unsafe-inline'` for scripts (weaker)

The current recommended approach: `'unsafe-inline'` for scripts, strict for
everything else. Accept the tradeoff.

---

## CSP Report-Only Mode

### Testing New CSPs
```
Content-Security-Policy-Report-Only: <policy>;
  report-uri https://your-csp-endpoint.example.com/csp-report
```

Browser reports violations but doesn't enforce. Perfect for testing a new
policy before enforcing.

### Reporting Endpoint
```typescript
// POST /api/csp-report
export async function POST(req: Request) {
  const report = await req.json();

  // Filter out common false positives
  if (isKnownBrowserExtensionViolation(report)) return Response.json({});

  // Log to monitoring
  logger.warn({
    type: 'csp_violation',
    documentUri: report['csp-report']['document-uri'],
    violatedDirective: report['csp-report']['violated-directive'],
    blockedUri: report['csp-report']['blocked-uri'],
    sourceFile: report['csp-report']['source-file'],
  }, 'CSP violation reported');

  return Response.json({}, { status: 204 });
}
```

### Gradual Rollout
1. Deploy new CSP in `report-only` mode
2. Monitor reports for 1-2 weeks
3. Fix legitimate violations, ignore browser extension noise
4. Switch to enforcing
5. Monitor for a few days, roll back if needed

---

## CSP Bypass Patterns to Avoid

### 1. `unsafe-inline` + `unsafe-eval`
Together they defeat the purpose of CSP. Avoid `unsafe-eval` unless absolutely
necessary (e.g., for code generation libraries).

### 2. Overly Broad CDN Allowlists
```
script-src https://*.cloudflare.com
```

This allows any subdomain, including attacker-controlled ones. Use specific
subdomains:
```
script-src https://cdnjs.cloudflare.com
```

### 3. User-Controllable CSP
Don't let user input influence the CSP. Attackers will find a way to inject
their own sources.

### 4. Missing `frame-ancestors`
Without `frame-ancestors 'none'` or `'self'`, attackers can embed your page in
their site for clickjacking.

### 5. Missing `object-src`
`<object>` and `<embed>` can execute Flash or plugin content. Always `'none'`
unless you specifically need it.

### 6. Not Testing Report-Only
Rolling out a strict CSP without testing will break the app for real users.
Always use report-only first.

---

## Stripe-Specific CSP

Stripe has specific CSP requirements. Their docs:
https://docs.stripe.com/security/guide#content-security-policy

### Minimum for Stripe Elements
```
script-src 'self' https://js.stripe.com
frame-src https://js.stripe.com https://hooks.stripe.com
```

### Minimum for Stripe Checkout (redirect)
```
connect-src 'self' https://api.stripe.com
```

### Minimum for Stripe Radar (fraud detection)
```
script-src 'self' https://m.stripe.network
frame-src https://m.stripe.network
```

---

## Supabase-Specific CSP

```
connect-src 'self' https://<project-ref>.supabase.co wss://<project-ref>.supabase.co
```

The `wss://` is required for Realtime. Easy to forget.

---

## Cloudflare Turnstile (CAPTCHA)

```
script-src 'self' https://challenges.cloudflare.com
frame-src https://challenges.cloudflare.com
```

---

## Sentry (Error Tracking)

```
connect-src 'self' https://<org>.ingest.sentry.io
```

---

## PostHog (Analytics)

```
script-src 'self' https://app.posthog.com https://us-assets.i.posthog.com
connect-src 'self' https://app.posthog.com https://us.i.posthog.com
```

---

## Measuring CSP Effectiveness

### The Success Metric
Count CSP violations per month. Lower is better.

### The Baseline
On day 1 of enforcement, you'll get many reports from browser extensions and
unusual clients. Filter those out.

### The Trend
Over time, violation count should approach zero. If it's not, you have either:
- An app bug (resource loading from wrong place)
- A new feature that needs CSP updates
- An attack in progress (rare but worth investigating)

### Alert on Spikes
A sudden spike in CSP violations may indicate an attack or regression.

---

## The CSP Checklist

### Deployment
- [ ] CSP is set on every response (middleware, not per-route)
- [ ] Different CSPs for API, docs, and app
- [ ] `frame-ancestors 'none'` for clickjacking protection
- [ ] `object-src 'none'` to block plugins
- [ ] `base-uri 'self'` to prevent base tag injection
- [ ] `form-action 'self'` to prevent form hijacking

### Third-party integrations
- [ ] Stripe (if used): scripts and iframes allowlisted
- [ ] Supabase (if used): wss:// allowed
- [ ] Analytics: specific domains, not wildcards
- [ ] CDN: specific subdomains, not wildcards

### Testing
- [ ] CSP tested in report-only mode for 1-2 weeks before enforcing
- [ ] Violation reporting endpoint exists
- [ ] Browser extension false positives filtered
- [ ] Alert on violation spikes

### Documentation
- [ ] CSP decisions documented (why `'unsafe-inline'` is used, etc.)
- [ ] Upgrade path documented (what would need to change for stricter CSP)
- [ ] Per-path differences documented

---

## See Also

- [WEB.md](WEB.md) — other security headers
- [FIELD-GUIDE.md](FIELD-GUIDE.md) — Story 3 (strict-dynamic Next.js regret)
- [FIELD-GUIDE.md](FIELD-GUIDE.md) — Story 7 (per-path CSP)
- https://csp-evaluator.withgoogle.com/ — test your CSP
- https://content-security-policy.com/ — directive reference
