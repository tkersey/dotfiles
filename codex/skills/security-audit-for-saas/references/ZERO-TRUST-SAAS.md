# Zero Trust for SaaS

Zero trust is a security model: **never trust, always verify**. Every request,
every time, regardless of origin. It's the opposite of perimeter security ("if
you're inside the network, you're trusted").

This file translates zero trust principles into concrete SaaS patterns.

---

## The Five Principles of Zero Trust

### 1. Verify Explicitly
Authenticate and authorize on every request, not just at the network boundary.

**SaaS application:**
- Every API request validates the session, not just the first
- Every DB query includes tenant/user scoping (via RLS + app layer)
- Every webhook signature is verified, not just the first webhook

### 2. Least Privilege Access
Give users (and services) the minimum permissions they need, and revoke them
when no longer needed.

**SaaS application:**
- Service accounts have minimum IAM roles
- User tiers (viewer < member < admin < owner) each have explicit capabilities
- Temporary elevation (JIT access) for sensitive operations
- Regular access review

### 3. Assume Breach
Design as if the network is already compromised.

**SaaS application:**
- Every internal service call is authenticated (mTLS or signed tokens)
- Secrets are rotated regularly (not "if compromised, rotate")
- Detection runs on every layer (not just perimeter)
- Logs include all access, not just failures

### 4. Micro-Segmentation
Break the system into small zones. Attackers can't easily pivot between zones.

**SaaS application:**
- Admin API on separate subdomain with separate auth
- Payment processing in its own service with minimal database access
- User data isolated per tenant via RLS
- CI/CD secrets scoped per pipeline

### 5. Continuous Verification
Trust decisions are re-evaluated continuously, not once at login.

**SaaS application:**
- Session validity checked on every request
- MFA challenge on high-risk actions (even within session)
- Device fingerprint validation on sensitive operations
- Anomaly detection triggers re-authentication

---

## Zero Trust Patterns

### Pattern 1: No Ambient Authority
Every action must present explicit authorization. No "I'm in this network, so
I can do X."

**Anti-pattern:**
```typescript
// BAD: internal request, assumed trusted
if (request.headers.get('x-internal-service') === 'true') {
  return processRequest(); // No auth check
}
```

**Zero trust:**
```typescript
// GOOD: every request signed with service-specific key
const token = await verifyServiceToken(request.headers.get('authorization'));
if (!token || !token.scopes.includes('process_request')) {
  return Response.json({ error: 'Forbidden' }, { status: 403 });
}
```

### Pattern 2: Continuous Session Validation
Don't trust a session just because it was valid yesterday.

```typescript
async function validateSessionWithContext(session: Session, request: Request) {
  // Basic validation
  if (session.revokedAt || session.expiresAt < new Date()) return null;

  // Risk-based re-authentication
  const risk = calculateRisk({
    knownDevice: matchesDeviceFingerprint(session, request),
    knownIp: matchesLocationProfile(session, request),
    timeOfDay: isUnusualHour(new Date()),
    recentActivity: session.lastActivityAt,
  });

  if (risk.score > THRESHOLD) {
    return { user: null, mfaRequired: true };
  }

  return session;
}
```

### Pattern 3: mTLS Between Services
Services authenticate each other with client certificates.

```typescript
const agent = new https.Agent({
  cert: fs.readFileSync('./client-cert.pem'),
  key: fs.readFileSync('./client-key.pem'),
  ca: fs.readFileSync('./ca-cert.pem'),
  rejectUnauthorized: true,
});

await fetch('https://internal-service.example.com', { agent });
```

### Pattern 4: Workload Identity (no long-lived secrets)
Use federated identity (OIDC) instead of API keys for service-to-service auth.

**AWS IRSA (IAM Roles for Service Accounts):**
```yaml
serviceAccountName: my-app
roleArn: arn:aws:iam::123:role/my-app
# No AWS credentials — IAM role assumed via service account
```

**Vercel OIDC:**
```typescript
// Vercel function gets a signed JWT automatically
const token = process.env.VERCEL_OIDC_TOKEN;
// Use token to assume cloud provider IAM role
```

### Pattern 5: Just-in-Time Privileged Access
Admins don't have admin privileges by default. They request them for specific
tasks.

```typescript
// Request temporary elevation
const elevation = await db.insert(elevations).values({
  userId: admin.id,
  justification: 'Investigating user report #1234',
  durationMinutes: 30,
  requestedAt: new Date(),
});

// Slack notification to security team for approval
await notifySecurityTeam(elevation);

// After approval:
// - Admin role temporarily granted
// - Expires automatically after duration
// - All actions audit logged with elevation ID
```

---

## The Zero Trust Audit

### Questions to Answer
1. **Can any request reach a sensitive operation without authentication?**
   Grep for unauthenticated routes. Each one should be justified.

2. **Are "internal" endpoints actually internal?**
   Test reaching internal endpoints from outside the VPC. Often possible via
   misconfigured ingress.

3. **Does every microservice authenticate callers?**
   Or is there a "we're behind the VPN" assumption somewhere?

4. **Are secrets rotated automatically or only on compromise?**
   If the latter, you're not doing zero trust.

5. **Is MFA required for ALL privileged actions, or just login?**
   Zero trust says "verify for every action."

6. **Is database access limited to the queries each service needs?**
   Or does every service have `ALL PRIVILEGES`?

7. **What percentage of traffic goes through a verified identity?**
   In full zero trust, 100%. Realistically, aim for 99%+ for critical paths.

### The Maturity Scale

**Level 0: Perimeter security only**
- Firewall, VPN, network zones
- "Inside = trusted"
- Most legacy enterprises

**Level 1: Authenticated but ambient authority**
- Users authenticate at login
- But internal services trust each other
- Most SaaS startups

**Level 2: Authentication at every service boundary**
- Services authenticate each other (mTLS or tokens)
- But permissions are coarse
- Growing SaaS

**Level 3: Least privilege + continuous verification**
- Every service has minimum necessary permissions
- Sessions re-verified continuously
- Regular access reviews
- Mature SaaS

**Level 4: Full zero trust**
- Every request explicitly authorized
- JIT privileged access
- All secrets ephemeral
- Rare

Most SaaS should aim for Level 2-3. Level 4 is aspirational for most.

---

## Common Zero Trust Misconceptions

### Misconception 1: "Zero trust = no trust"
Zero trust means no IMPLICIT trust. You still trust explicit authentication.
The difference: trust is granted per-request, not once-per-session.

### Misconception 2: "Zero trust is a product"
Vendors sell "zero trust solutions." Zero trust is a principle, not a product.
You can't buy it; you implement it.

### Misconception 3: "Zero trust replaces authentication"
It augments authentication. You still need strong auth (MFA, etc.); you just
also need authorization at every step.

### Misconception 4: "Zero trust means slower"
Well-designed zero trust doesn't add noticeable latency. Auth can be cached
(with short TTL), mTLS is fast, signed tokens are fast.

---

## The Minimum Zero Trust for SaaS

If you can't do full zero trust, do these:

1. **Auth on every request**, not just the first
2. **RLS + app-layer auth** (both layers, always)
3. **Service-to-service auth** (not "internal = trusted")
4. **Secrets rotation** on a schedule
5. **MFA for admin actions**, not just login
6. **Audit log for every privileged action**
7. **Short-lived sessions** with refresh
8. **Tenant isolation** verified at DB and app layer

Hit these eight, and you're at Level 2. That covers most real-world attacks.

---

## See Also

- [DEFENSE-IN-DEPTH.md](DEFENSE-IN-DEPTH.md) — complementary layered approach
- [AUTH.md](AUTH.md)
- [MULTI-TENANT.md](MULTI-TENANT.md)
- NIST SP 800-207: https://csrc.nist.gov/publications/detail/sp/800-207/final
