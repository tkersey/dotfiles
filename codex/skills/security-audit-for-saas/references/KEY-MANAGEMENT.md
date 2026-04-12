# Secrets Management Checklist

Preventing secret exposure across the SaaS stack.

---

## Environment Variable Architecture

### The Single-Module Pattern
All environment variable access must go through one `env.ts` file:

```typescript
// env.ts (using @t3-oss/env-nextjs + Zod)
export const env = createEnv({
  server: {
    STRIPE_SECRET_KEY: z.string().startsWith('sk_'),
    SUPABASE_SERVICE_ROLE_KEY: z.string(),
    DATABASE_URL: z.string().url(),
    // ...
  },
  client: {
    NEXT_PUBLIC_SUPABASE_URL: z.string().url(),
    NEXT_PUBLIC_SUPABASE_ANON_KEY: z.string(),
    NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: z.string().startsWith('pk_'),
    // ...
  },
});
```

### Audit Checklist
- [ ] Single `env.ts` module with Zod validation for all environment variables
- [ ] Server variables: no `NEXT_PUBLIC_` prefix
- [ ] Client variables: only `NEXT_PUBLIC_` prefix, only safe values (publishable keys, DSNs, measurement IDs)
- [ ] `NEXT_PUBLIC_APP_URL` is REQUIRED in production (fallback to localhost causes payment redirects to localhost)
- [ ] No direct `process.env` usage outside `env.ts`
- [ ] No server-only module imports from `"use client"` components

### Safe Client-Side Variables
These are safe to expose:
- `NEXT_PUBLIC_SUPABASE_URL` (public endpoint)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` (anon key, limited by RLS)
- `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` (publishable, not secret)
- `NEXT_PUBLIC_POSTHOG_KEY` (analytics, write-only)
- `NEXT_PUBLIC_SENTRY_DSN` (error reporting, write-only)
- `NEXT_PUBLIC_TURNSTILE_SITE_KEY` (captcha, public)
- `NEXT_PUBLIC_GA_MEASUREMENT_ID` (analytics, public)

### Never Expose Client-Side
- `STRIPE_SECRET_KEY` / `PAYPAL_CLIENT_SECRET`
- `SUPABASE_SERVICE_ROLE_KEY`
- `DATABASE_URL`
- `JWT_SECRET`
- `GOOGLE_CLIENT_SECRET`
- `ADMIN_API_KEY`
- Any Resend/Upstash/external API tokens

---

## Git History & Committed Files

### Audit
- [ ] `.env`, `.env.local` NOT in git (check `git log --all --diff-filter=A -- .env*`)
- [ ] `.gitignore` includes: `.env`, `.env.local`, `.env.*.local`
- [ ] No `.env.e2e` or `.env.test` with real secrets (use `.env.example` with placeholders)
- [ ] Pre-commit hooks include secret detection (e.g., `detect-secrets`, `gitleaks`)

### If Secrets Were Committed
1. **Rotate ALL exposed secrets immediately** -- key, connection string, token, everything
2. Use `git filter-repo` to remove from history (not just deleting the file)
3. Force-push (with team coordination)
4. Check if the secret was ever deployed or cached by CI

---

## Health Check & Admin Endpoints

### Information Disclosure
- [ ] Health checks show key prefix only for environment confirmation (e.g., `sk_live_...`)
- [ ] NEVER show suffix (reduces search space for brute-force)
- [ ] Admin health checks require authentication
- [ ] Error responses don't include stack traces in production
- [ ] 404 pages don't reveal framework/version information

---

## SSO Configuration Redaction

API responses for SSO settings must use redacted types:

```typescript
// Types that EXCLUDE secrets
type RedactedOidcSsoConfig = {
  clientId: string;
  issuerUrl: string;
  // clientSecret: EXCLUDED
  configFingerprint: string; // Hash prefix, not secret
};

type RedactedSamlSsoConfig = {
  entityId: string;
  ssoUrl: string;
  // certificate: EXCLUDED
  configFingerprint: string;
};
```

- [ ] SSO config API returns redacted types only
- [ ] Config fingerprint uses hash prefix, not full secret
- [ ] OIDC client secret never returned to frontend
- [ ] SAML certificate never returned to frontend

---

## Service Role Key Isolation

```typescript
// createAdminClient() -- service role key usage
export function createAdminClient() {
  return createServerClient<Database>(
    env.NEXT_PUBLIC_SUPABASE_URL,
    env.SUPABASE_SERVICE_ROLE_KEY,  // Bypasses RLS
    {
      cookies: {
        getAll() { return []; },     // No cookies
        setAll() {},                  // No cookies
      },
      auth: { autoRefreshToken: false, persistSession: false },
    }
  );
}
```

- [ ] Service role key only used in `createAdminClient()` function
- [ ] Cookies disabled for admin client (no session leakage)
- [ ] Regular server client uses anon key + RLS
- [ ] Admin client never instantiated in API routes that don't require admin auth

---

## API Key Patterns

- [ ] All secret access funneled through single module (e.g., `resolve_auth_header()`)
- [ ] API keys use identifiable prefixes (e.g., `jsm_` for jeffreys-skills.md)
- [ ] Key hash stored in DB, not raw key
- [ ] Key rotation doesn't invalidate immediately (grace period for migration)
- [ ] Revoked keys return 401 immediately (no cache delay)
