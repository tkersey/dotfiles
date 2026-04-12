# Multi-Tenant Isolation

Multi-tenancy is where data from Tenant A must be invisible to Tenant B. It's also
where SaaS security failures cost the most reputation per incident. This file is
the complete checklist for verifying tenant isolation.

---

## The Two-Layer Model

**Axiom:** RLS alone is insufficient. App-layer checks alone are insufficient.
Both layers must enforce the boundary.

**Why both?**
- **RLS only:** Service role key bypasses it. Any code path using admin client
  silently accesses all tenants. Developers forget.
- **App-layer only:** One missing `requireOrgRole()` call leaks everything. Junior
  devs won't know to add it. Code review may miss it.
- **Both:** Belt-and-suspenders. Each catches the other's mistakes.

---

## Layer 1: RLS Policies

### Per-Tenant Data Pattern

```sql
-- Every tenant-scoped table has these three policies
CREATE POLICY tenant_data_select ON public.tenant_data
  FOR SELECT TO authenticated
  USING (
    org_id IN (
      SELECT organization_id FROM organization_members
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY tenant_data_insert ON public.tenant_data
  FOR INSERT TO authenticated
  WITH CHECK (
    org_id IN (
      SELECT organization_id FROM organization_members
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY tenant_data_update ON public.tenant_data
  FOR UPDATE TO authenticated
  USING (
    org_id IN (
      SELECT organization_id FROM organization_members
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY tenant_data_all_service ON public.tenant_data
  FOR ALL TO service_role
  USING (true);
```

### Common RLS Mistakes

**Mistake 1: Subquery against a table with its own RLS**
```sql
-- BAD: if organization_members has RLS that excludes this user,
-- the subquery returns nothing, policy denies legit access
CREATE POLICY ... USING (
  org_id IN (
    SELECT organization_id FROM organization_members
    WHERE user_id = auth.uid()
  )
);
```

Fix: ensure the subquery table's RLS allows the user to see their own memberships.

**Mistake 2: Using `auth.jwt()->>'org_id'` without validation**
```sql
-- BAD: JWT custom claims may be modifiable or stale
CREATE POLICY ... USING (org_id = (auth.jwt()->>'org_id')::uuid);
```

Fix: use `app_metadata` (server-set), not `user_metadata` (user-modifiable). Better:
look up memberships from the table.

**Mistake 3: Missing WITH CHECK on INSERT/UPDATE**
```sql
-- BAD: USING prevents reads but not writes
CREATE POLICY ... FOR UPDATE USING (org_id IN (...));
```

Fix: always pair USING with WITH CHECK for mutations.

**Mistake 4: Policy references denormalized org_id that can drift**
```sql
-- BAD: org_id stored on the row. If code updates other fields, org_id may be left wrong.
CREATE POLICY ... USING (org_id IN (...));
```

Fix: derive tenant via a JOIN when possible, or enforce org_id immutability via
triggers.

---

## Layer 2: App-Layer Checks

### The Pattern

```typescript
// Every tenant-scoped operation starts with this
async function requireOrgRole(
  userId: string,
  orgId: string,
  minRole: OrgRole
): Promise<OrgMember> {
  const member = await db.query.organizationMembers.findFirst({
    where: and(
      eq(organizationMembers.userId, userId),
      eq(organizationMembers.orgId, orgId)
    ),
  });

  if (!member) {
    throw new Error("NOT_A_MEMBER");
  }
  if (!hasMinRole(member.role, minRole)) {
    throw new Error("INSUFFICIENT_PRIVILEGE");
  }
  return member;
}
```

### Critical: OrgId Must Come from Server State

**Vulnerable:**
```typescript
export async function updateOrgSettings(req: Request) {
  const body = await req.json();
  const member = await requireOrgRole(session.userId, body.orgId, "admin");
  await db.update(organizations)
    .set({ name: body.name })
    .where(eq(organizations.id, body.orgId));
}
```

The problem: `body.orgId` is client-controlled. An attacker in Org A can send
`body.orgId = "org_B_id"`. If they're also a member of Org B (with a lower role),
the `requireOrgRole` check passes, and they can update Org B's settings.

Wait — that's actually fine because requireOrgRole checks their role in org B.
The real problem is when the URL param is used:

```typescript
export async function PATCH(req: Request, { params }: { params: { orgId: string } }) {
  const member = await requireOrgRole(session.userId, params.orgId, "admin");
  // ...
}
```

Still fine IF requireOrgRole actually checks the user's membership in the URL's orgId.
The bug is usually:

```typescript
// BUG: checks membership against session's "default org" but acts on URL's org
export async function PATCH(req: Request, { params }: { params: { orgId: string } }) {
  const member = await requireOrgRole(session.userId, session.defaultOrgId, "admin");
  await db.update(organizations).set({...}).where(eq(organizations.id, params.orgId));
}
```

**Fix:** Always check authorization against the EXACT resource being accessed, not
a "current org" or "default org" from session.

### Shared Resource Access

Some resources are shared across tenants (e.g., skill packs, templates, public
profiles). These need explicit `visibility` fields:

```typescript
async function canViewSkillPack(userId: string, packId: string): Promise<boolean> {
  const pack = await db.query.skillPacks.findFirst({
    where: eq(skillPacks.id, packId),
  });
  if (!pack) return false;

  if (pack.visibility === "public") return true;
  if (pack.visibility === "organization") {
    // Only org members can view
    const isMember = await isOrgMember(userId, pack.orgId);
    return isMember;
  }
  if (pack.visibility === "private") {
    return pack.authorId === userId;
  }
  return false; // Unknown visibility → deny
}
```

---

## Aggregate Query Leakage

Aggregate queries (counts, averages, sums) can leak other-tenant data by inference
even when RLS prevents direct reads.

### Example: Hidden Growth Leak

```typescript
// Looks safe: count your own org's users
const count = await db.$count(users, eq(users.orgId, session.orgId));

// But this endpoint is public analytics!
export async function GET(req: Request) {
  const totalUsers = await db.$count(users); // Counts ALL users across ALL tenants
  return { totalUsers };
}
```

An attacker polls `totalUsers` over time and infers competitor growth rate.

**Fix:** Aggregate queries must be explicitly scoped. Add bucketing/rounding for
public dashboards:

```typescript
const bucket = Math.floor(totalUsers / 1000) * 1000;
return { approxUsers: `${bucket}+` };
```

### Example: Top Users Leak

```typescript
// Internal admin dashboard shows top users
const topUsers = await db.select()
  .from(users)
  .orderBy(desc(users.activityCount))
  .limit(10);
```

If accessible without tenant scoping, this leaks who the heaviest users are across
all tenants (their usernames, activity levels, maybe their employers).

**Fix:** Restrict to tenant admin role, or remove usernames from cross-tenant aggregates.

---

## Cache Poisoning Across Tenants

Shared caches keyed by a non-tenant-specific key can serve Tenant A's data to
Tenant B.

**Vulnerable:**
```typescript
// Cache key based on feature name only
const cached = await cache.get(`top_skills_${featureName}`);
```

If Org A has private skills cached, Org B gets them.

**Fix:** Include tenant ID in every cache key for tenant-scoped data:
```typescript
const cached = await cache.get(`top_skills_${orgId}_${featureName}`);
```

Or use separate cache namespaces per tenant.

---

## Tenant Deletion (GDPR)

When a tenant is deleted, ALL tenant data must be removed. This is hard because
data lives in many places.

### The Deletion Checklist

```typescript
async function deleteTenant(orgId: string) {
  await db.transaction(async (tx) => {
    // Primary data
    await tx.delete(tenantData).where(eq(tenantData.orgId, orgId));
    await tx.delete(tenantSettings).where(eq(tenantSettings.orgId, orgId));
    await tx.delete(organizationMembers).where(eq(organizationMembers.orgId, orgId));

    // Referenced data
    await tx.delete(subscriptions).where(eq(subscriptions.orgId, orgId));
    await tx.delete(invoices).where(eq(invoices.orgId, orgId));
    await tx.delete(auditLogs).where(eq(auditLogs.orgId, orgId));

    // Finally: delete the org itself
    await tx.delete(organizations).where(eq(organizations.id, orgId));
  });

  // External cleanup (outside transaction)
  await deleteStripeCustomer(orgId);
  await deletePaypalCustomer(orgId);
  await invalidateAllSessions(orgId);
  await deleteS3Files(`tenants/${orgId}/`);
  await removeCacheEntries(`org:${orgId}:*`);
  await removeFromSearchIndex(orgId);
  await notifyAnalyticsDeletion(orgId);
}
```

### Audit the Deletion

A script should verify deletion was complete:

```sql
-- Post-deletion verification
SELECT count(*) FROM tenant_data WHERE org_id = $deleted_org_id; -- Should be 0
SELECT count(*) FROM organizations WHERE id = $deleted_org_id; -- Should be 0
-- Run for every table with org_id column
```

---

## Test Fixtures Must Use 2+ Tenants

Many tenant isolation bugs exist only because tests use a single tenant. Fixtures
MUST include at least 2 tenants:

```typescript
// tests/fixtures/multi-tenant.ts
export async function setupMultiTenantFixtures() {
  const orgA = await createOrg({ name: "Org A" });
  const orgB = await createOrg({ name: "Org B" });
  const userA = await createUser({ orgId: orgA.id });
  const userB = await createUser({ orgId: orgB.id });
  const dataA = await createData({ orgId: orgA.id });
  const dataB = await createData({ orgId: orgB.id });
  return { orgA, orgB, userA, userB, dataA, dataB };
}

// Every endpoint test should include:
describe("GET /api/data/:id", () => {
  it("allows userA to access dataA", async () => {
    const res = await fetch(`/api/data/${dataA.id}`, { headers: userAHeaders });
    expect(res.status).toBe(200);
  });

  it("DENIES userA access to dataB", async () => {
    const res = await fetch(`/api/data/${dataB.id}`, { headers: userAHeaders });
    expect(res.status).toBe(403); // Critical: must not be 200 or 404 with data
  });

  it("returns 404 for dataB as userA (not 403 to prevent existence enumeration)", async () => {
    const res = await fetch(`/api/data/${dataB.id}`, { headers: userAHeaders });
    expect(res.status).toBe(404); // Or consistent with "not found" for non-existent
  });
});
```

---

## Audit Checklist

### RLS layer
- [ ] RLS enabled on every tenant-scoped table
- [ ] Policies use subqueries that don't themselves get blocked by RLS
- [ ] `app_metadata` used instead of `user_metadata` for tenant claims
- [ ] WITH CHECK present on INSERT/UPDATE policies
- [ ] Service role has explicit separate policy

### App layer
- [ ] Every tenant-scoped route calls `requireOrgRole()` with the EXACT resource's orgId
- [ ] No route trusts `session.defaultOrgId` when acting on a specific org
- [ ] Admin client (service role) only used in admin-authenticated handlers

### Data boundaries
- [ ] Aggregate queries tenant-scoped
- [ ] Public aggregates bucketed/rounded
- [ ] Cache keys include tenant ID
- [ ] Shared resources have explicit visibility field
- [ ] Cross-tenant references (e.g., impersonation) heavily logged

### Deletion
- [ ] Script-driven tenant deletion across ALL tables
- [ ] Post-deletion verification queries exist
- [ ] External services cleaned up (Stripe, email, search, analytics)

### Tests
- [ ] Fixtures include 2+ tenants
- [ ] Tests verify cross-tenant access is denied
- [ ] Tests verify 404 vs 403 correctly (avoid existence enumeration)

### Red team validation
- [ ] Spin up 2 test tenants, try to cross the boundary from every endpoint
- [ ] Run the "Cross-Tenant Leak" scenario from [ATTACK-SCENARIOS.md](ATTACK-SCENARIOS.md)
