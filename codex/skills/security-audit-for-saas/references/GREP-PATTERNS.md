# Grep Patterns for Quick Security Scanning

Use these patterns for rapid triage before deep-diving into specific domains.

---

## Payment & Billing

```bash
# Webhook signature verification
rg -n "constructEvent|verify-webhook-signature|webhooks\.construct" --type ts
rg -n "paypal-transmission-id|paypal-transmission-sig" --type ts

# Client-submitted pricing (should NOT exist)
rg -n "body\.(amount|price|unit_amount)" --type ts
rg -n "req\.body\.(amount|price)" --type ts

# Idempotency handling
rg -n "ON CONFLICT|payment_events|idempotency" --type ts --type sql

# Race condition protection
rg -n "FOR UPDATE|advisory_lock|forUpdate" --type ts

# Stripe type safety (potential as-string bugs)
rg -n "as string" --type ts | grep -i "customer\|subscription\|invoice\|price"

# PayPal custom_id validation
rg -n "custom_id|validatePayPalUserId" --type ts

# Pending checkout state
rg -n "pendingCheckout|pending_checkout" --type ts

# Cache invalidation for subscriptions
rg -n "subscription.*cache\|cache.*subscription\|after\(\)" --type ts
```

## Auth & Authorization

```bash
# TOCTOU: permission checks outside transactions
# Look for auth checks NOT inside db.transaction()
rg -n "requireOrgPermission|requireAdmin|requireUser" --type ts -A 5 | grep -v "transaction"

# CSRF protection
rg -n "csrf|CSRF|origin.*referer|validateOrigin" --type ts

# Timing-safe comparisons (should use timingSafeEqual)
rg -n "timingSafeEqual|timingSafeCompare|timing.safe" --type ts
# Find NON-timing-safe secret comparisons (potential bugs)
rg -n '(secret|token|key|hash|hmac)\s*[!=]=\s' --type ts

# Rate limiting on auth endpoints
rg -n "rateLimit|rateLimiter|Ratelimit" --type ts
rg -n "auth/token|auth/refresh|auth/revoke|cli/verify" --type ts -l

# Session auth fallback (CSRF bypass risk)
rg -n "getSession.*fallback\|cookie.*fallback" --type ts

# Admin route protection
rg -n "requireAdmin\|isAdmin" --type ts
rg -n "api/admin" --type ts -l
```

## Secrets & Environment

```bash
# Environment variable access outside env.ts
rg -n "process\.env\." --type ts | grep -v "env\.ts\|node_modules\|\.next"

# NEXT_PUBLIC_ in server-only code (should be in client code only)
rg -n "NEXT_PUBLIC_" --type ts -l

# Hardcoded secrets
rg -n "(sk_live|sk_test|rk_live|whsec_|sbp_|eyJ)" --type ts --type env

# Service role key usage
rg -n "SERVICE_ROLE_KEY\|service_role" --type ts

# Health check information disclosure
rg -n "health.*check\|healthCheck\|/health" --type ts -A 10 | grep -i "key\|secret\|token"

# SSO config exposure
rg -n "SsoConfig\|clientSecret\|client_secret" --type ts
```

## Database / RLS

```bash
# Tables without RLS (check migrations)
rg -n "CREATE TABLE" --type sql | grep -v "CREATE TABLE IF"
rg -n "ENABLE ROW LEVEL SECURITY\|enable_rls" --type sql

# Overly permissive policies
rg -n "USING\s*\(true\)" --type sql

# Anon role access
rg -n "TO anon\|TO public" --type sql

# Raw SQL (potential injection if not parameterized)
rg -n "sql\`.*\$\{" --type ts  # Drizzle tagged template (safe)
rg -n '"\s*SELECT\s.*\+\s' --type ts  # String concatenation (UNSAFE)

# Service role client creation
rg -n "createAdminClient\|createServiceClient" --type ts
```

## Web Security

```bash
# Open redirect vulnerabilities
rg -n "redirect\(|redirect:\s|Location.*header" --type ts
rg -n "returnTo\|returnUrl\|redirect_uri\|callback_url" --type ts
rg -n "getSafeRedirectPath\|isSafeRedirect" --type ts

# SSRF - webhook URL fetching
rg -n "fetch\(|axios\.\|got\(" --type ts | grep -i "webhook\|url\|endpoint"
rg -n "validateWebhookUrl\|isInternalIp\|isPrivateIp" --type ts

# XSS - dangerous HTML
rg -n "dangerouslySetInnerHTML\|innerHTML\|v-html" --type ts --type tsx
rg -n "rehype-sanitize\|DOMPurify\|sanitize" --type ts

# Security headers
rg -n "Strict-Transport-Security\|X-Content-Type-Options\|X-Frame-Options" --type ts
rg -n "Content-Security-Policy\|Referrer-Policy\|Permissions-Policy" --type ts

# CORS
rg -n "Access-Control-Allow-Origin\|cors" --type ts

# Cookie security
rg -n "httpOnly\|sameSite\|secure.*cookie\|cookie.*secure" --type ts
```

## Infrastructure

```bash
# In-memory state in serverless (likely broken)
rg -n "new Map\(\)|new Set\(\)|const.*=\s*\{\}" --type ts | grep -i "rate\|limit\|cache\|session"

# Shell command construction
rg -n 'exec\.Command\("sh"\s*,\s*"-c"' --type go  # Go: unsafe shell exec
rg -n "child_process\|execSync\|exec\(" --type ts  # Node: shell execution

# Batch processing limits
rg -n "LIMIT\s+\d{4,}" --type ts --type sql  # Large LIMIT values
rg -n "maxDuration" --type ts  # Serverless timeout budget

# after() callback usage (unreliable in serverless)
rg -n "after\(\)" --type ts -A 3

# Abuse detection
rg -n "abuse.*detect\|trackAbuse\|abuseSignal" --type ts
```

---

## Quick Scan Sequence

Run these in order for a rapid security triage:

```bash
# 1. Secrets exposure (fastest, highest impact)
rg -n "(sk_live|sk_test|password|secret)" --type ts --type env | grep -v node_modules

# 2. Missing auth on routes
rg -rn "export.*async.*function.*(GET|POST|PUT|DELETE|PATCH)" --type ts src/app/api/ \
  | grep -v "webhook\|cron\|health"

# 3. Webhook handlers
rg -l "webhook" --type ts src/app/api/

# 4. Direct DB access patterns
rg -n "from.*users\|from.*organizations\|from.*subscriptions" --type ts

# 5. Redirect handling
rg -n "redirect\(" --type ts | head -20
```
