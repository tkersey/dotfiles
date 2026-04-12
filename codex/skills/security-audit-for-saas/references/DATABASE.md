# Database Access Control (RLS) Checklist

Ensuring Supabase Row-Level Security actually protects data.

---

## RLS Coverage Verification

### The Migration Gap Problem
RLS repair migrations often cover "new" tables but MISS critical core tables that had policies defined in earlier migrations that may not have been re-applied.

**Script-verify coverage:**
```sql
-- Find tables with RLS enabled but NO policies
SELECT schemaname, tablename
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename NOT IN (
    SELECT tablename FROM pg_policies WHERE schemaname = 'public'
  );

-- Find tables with RLS NOT enabled
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
  AND NOT rowsecurity;
```

### Priority Tables (Must Have RLS)
- [ ] `users` (email, isAdmin, subscriptionStatus, suspendedAt)
- [ ] `organizations` (billing info, SSO config, Stripe/PayPal IDs)
- [ ] `organization_members` (role assignments)
- [ ] `subscriptions` (payment status, provider IDs)
- [ ] `external_identities` (SSO/OAuth links)
- [ ] Any table with PII, billing data, or auth credentials

### Tables That Can Skip RLS
Public read-only reference tables:
- Subscription tiers / pricing plans (public data)
- Feature flags (public configuration)
- Public skill catalogs / templates

---

## RLS Policy Patterns

### User-Scoped Data
```sql
-- Users can only see their own data
CREATE POLICY "users_own_data" ON public.user_data
  FOR ALL TO authenticated
  USING (auth.uid() = user_id);
```

### Organization-Scoped Data
```sql
-- Members can see their org's data
CREATE POLICY "org_member_data" ON public.org_data
  FOR SELECT TO authenticated
  USING (
    org_id IN (
      SELECT organization_id FROM organization_members
      WHERE user_id = auth.uid()
    )
  );
```

### Admin-Only Data
```sql
-- Only admins can access
CREATE POLICY "admin_only" ON public.admin_data
  FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE id = auth.uid() AND "isAdmin" = true
    )
  );
```

**Warning:** Admin-only policies that subquery the `users` table will silently fail if the `users` table has RLS policies that block the authenticated user's own query. Test this interaction.

---

## Overly Permissive Policies

### Audit For
- [ ] No `USING (true)` on tables with sensitive data
- [ ] Skill packs / content readable by "any authenticated" -- is this intentional?
- [ ] INSERT/UPDATE/DELETE policies exist (not just SELECT)
- [ ] Policies aren't so restrictive they break admin workflows

### Example of Overly Permissive
```sql
-- BAD: any authenticated user can read all skill packs
CREATE POLICY skill_packs_select_all
  ON public.skill_packs
  FOR SELECT TO authenticated
  USING (true);

-- BETTER: only published packs are public; drafts require ownership
CREATE POLICY skill_packs_select
  ON public.skill_packs
  FOR SELECT TO authenticated
  USING (
    visibility = 'public'
    OR author_id = auth.uid()
  );
```

---

## Anon Role Lockdown

- [ ] All table privileges revoked from `anon` role
- [ ] All sequence privileges revoked from `anon` role
- [ ] Default privileges prevent future anon access
- [ ] INSERT/UPDATE/DELETE/TRUNCATE revoked from authenticated on tables that don't need direct writes
- [ ] pg_graphql extension disabled (if not used)
- [ ] PostgREST schemas properly configured

```sql
-- Verify anon lockdown
SELECT grantee, table_schema, table_name, privilege_type
FROM information_schema.table_privileges
WHERE grantee = 'anon' AND table_schema = 'public';
-- Should return 0 rows
```

---

## Supabase Auth Security

### getClaims() vs getSession()
- [ ] Use `supabase.auth.getUser()` (server-side API call, validates JWT) -- not `getSession()` (decodes locally without validation)
- [ ] Use `app_metadata` for tenant_id and roles (not `user_metadata` which is user-modifiable)

### Service Role Client
- [ ] `SUPABASE_SERVICE_ROLE_KEY` only in server-side code
- [ ] Service role client has no cookies (can't be hijacked via session)
- [ ] Service role client only instantiated in admin-authenticated handlers

### Cookie Configuration
```typescript
const SUPABASE_AUTH_COOKIE_OPTIONS = {
  path: "/",
  sameSite: "lax",
  httpOnly: false,    // Required by Supabase JS client -- known constraint
  secure: true,       // Always in production
  maxAge: 400 * 24 * 60 * 60,
};
```

- [ ] `httpOnly: false` is documented as known Supabase SSR requirement
- [ ] `secure: true` in production
- [ ] `sameSite: "lax"` (not "none")
- [ ] XSS mitigations in place (since cookie is readable by JS)

---

## Drizzle ORM Safety

- [ ] All queries use Drizzle query builder or `sql` tagged template literals (auto-parameterized)
- [ ] No raw SQL string concatenation
- [ ] Advisory lock calls use parameterized queries
- [ ] Migration files don't contain user-controlled interpolation
