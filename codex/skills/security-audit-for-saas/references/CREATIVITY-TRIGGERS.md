# Creativity Triggers — Breaking Out of Checklist Mode

Checklists find the bugs you already know exist. They are useless for finding the
bugs that haven't been invented in your codebase yet. This file is a library of
provocations — questions, prompts, and thought experiments that force the audit out
of mechanical checking and into creative hunting.

**When to use:** The 15-domain sweep has completed. The operators have been applied.
All obvious checks pass. Before declaring "clean," walk through these triggers.

---

## The Invisible Vulnerabilities

Vulnerabilities that don't appear in the code because they appear in the absence
of code, in silent side effects, or in implicit assumptions.

### What changes silently?
- **Tokens refresh** — is the refresh token rotation audited? Can an attacker
  replay a rotated token?
- **Permissions expire** — what happens at the expiry moment? Is there a race?
- **Caches invalidate** — who else can trigger invalidation? Can an attacker
  force repeated invalidation for DoS?
- **Logs rotate** — does log rotation remove audit trails an attacker wants to hide?
- **Sessions expire** — what happens to pending operations at expiry?
- **Cron secrets rotate** — is the old secret still accepted during overlap?
- **DNS TTL expires** — can an attacker re-point a domain during a narrow window?

### What happens at the boundary?
- **80+ characters** — URL length limits (Cloudflare ~8KB path), email limits (RFC 5321 ~254),
  username limits, cookie value limits
- **0 bytes** — empty strings passing `.length > 0` via `.length >= 0`
- **Negative numbers** — prices, counts, offsets
- **Zero bytes in strings** — null terminator bypass for C-extensions
- **Unicode edge cases** — `"Ⓐdmin"`, homograph attacks, zero-width joiners
- **Base64 padding variations** — canonical vs non-canonical encoding
- **Integer overflow** — `Number.MAX_SAFE_INTEGER`, BigInt boundaries

### What's the default nobody changes?
- API keys still at "sk_test_..." in production
- DB passwords still at installation default
- TLS certs from staging
- Admin emails from the template
- Cron secrets from the example
- CORS origin still at `localhost`
- Feature flags still defaulting to "open"

### What runs outside normal UX?
- Admin CLI access
- Batch import/export
- Webhook replay endpoints
- Reconciliation crons
- Data migrations
- Database backup restore
- Debug/staging flags still in prod

---

## The Layered Attack Paths

No single bug gets you owned. Compositions do.

### Escalation ladders
- **viewer → member:** what verification is needed to upgrade role?
- **member → admin:** can an admin invite themselves via a bug?
- **admin → owner:** can an admin modify billing without owner approval?
- **owner → service role:** can an owner access service_role key via admin UI?
- **user → cross-tenant:** can a user in Org A access Org B via shared resources?

### Timing compositions
- **Token rotation window:** old token valid for N seconds after rotation → grab it
- **Grace period expiry:** subscription canceled but still has grace → last-minute use
- **Rate limit reset:** bucket empties at specific second → sync attack
- **Cache TTL boundary:** stale read just before refresh
- **Check vs act:** permission check at T0, action at T1, revocation at T0.5

### State machine bypasses
- **Forbidden sequences:** pending → active skipping verification
- **Backward transitions:** active → pending (via partial refund?)
- **Parallel states:** can a user be both "paid" and "canceled" simultaneously?
- **Zombie states:** user deleted but subscription active

---

## The Hidden Surface Scan

Every integration is a trust boundary. Audit them all.

### Integrations to enumerate
- Payment processors (Stripe, PayPal, Braintree, Paddle)
- Auth providers (Auth0, Supabase, Clerk, Google OAuth)
- Email (Resend, SendGrid, Postmark, AWS SES)
- Analytics (PostHog, Mixpanel, Amplitude)
- Error tracking (Sentry, Datadog)
- Rate limiting (Upstash, Cloudflare)
- CDN (Vercel, Cloudflare, Fastly)
- File storage (S3, R2, Vercel Blob)
- Search (Algolia, Meilisearch, Pinecone)
- CI/CD (GitHub Actions, Vercel, CircleCI)

### For each integration, ask:
- What data flows OUT to them?
- What data flows IN from them (webhooks, callbacks)?
- What credentials do they have?
- What permissions do they hold?
- If compromised, what do they give attacker access to?
- What happens if their API is down?
- What happens if their webhook is forged?

### Hidden administrative surfaces
- `/api/admin/*` — obvious, usually audited
- `/api/internal/*` — internal tools, often NOT audited
- `/api/debug/*` — debug endpoints, often forgotten
- `/api/telemetry/*` — analytics, may accept unauthenticated writes
- `/api/health/*` — health checks, often leak version/env info
- `/api/og-image/*` — image generation, often accepts arbitrary query params
- `/api/cron/*` — cron jobs, often authenticated by shared secret
- `/api/v1/*` — old API versions, may lack modern middleware

---

## The Trust Assumption Inversion

Every security mechanism has implicit trust assumptions. Invert each one.

### "Only legitimate users reach this"
- Is it publicly routable?
- Does it appear in robots.txt, sitemap.xml, or error pages?
- Is it linked from any public page?
- Does it appear in the client bundle as a string?
- Has it ever been in the git history of a public repo?

### "This input is validated upstream"
- Is upstream bypassable via another entry point?
- Does upstream validation use the same schema as downstream?
- If upstream is a proxy, does the origin trust the proxy's validation?
- If upstream is a type system, does the runtime actually enforce it?

### "This only stores non-sensitive data"
- Does it combine with other data to become sensitive? (username + timestamp = activity)
- Is the metadata sensitive even if the content isn't?
- Is the schema itself sensitive (reveals business logic)?
- Is the volume sensitive (reveals user count, revenue)?

### "This isn't exploitable without X"
- Is X easier than assumed? (e.g., "requires MITM" — but HTTPS misconfig is MITM)
- Can X be obtained via a separate lower-severity bug?
- Can X be social-engineered?
- Is X already publicly known?

### "The CDN/proxy handles that"
- Does it handle it on OPTIONS AND POST?
- Does it handle it for all paths or just matched ones?
- Does the origin accept requests bypassing the CDN?
- If it caches, does it cache per-user or globally?

### "Only paying customers have this feature"
- Is there a trial that bypasses payment?
- Is there an org-based subscription that bypasses individual?
- Is there an admin grant override?
- Can the subscription be spoofed via metadata?
- Does a canceled subscription lose access immediately?

---

## Attacker Personas — 5 Lenses for the Same Code

Each persona sees different vulnerabilities. Walk through all 5.

### 1. The Bored User ("What happens if I do this weird thing?")
- Breaks inputs with emojis, RTL text, zero-width chars
- Tests UI limits: very long names, nested quotes, special chars
- Clicks rapidly, reloads during operations
- Tries to do X before Y when UX expects Y before X
- Finds crashes that become DoS vectors

### 2. The Financial Fraudster ("How do I get free service?")
- Promo code stacking, referral abuse, trial reset
- Price manipulation via metadata
- Refund-and-use pattern (buy → refund → still have access)
- Chargeback abuse
- Multi-account exploitation
- Subscription hijacking via metadata

### 3. The Competitor ("How do I exfiltrate or disrupt?")
- Rate limit on sensitive endpoints (find gaps)
- Scraping patterns (bulk data collection)
- User enumeration (find all customers)
- Tenant leak (infer competitor's data)
- Business logic probing (how does pricing work?)
- SEO poisoning (if site has user-generated content)

### 4. The Disgruntled Ex-Employee ("What backdoors do I know?")
- Hardcoded admin emails
- Cron secrets in environment
- Git history with credentials
- Deploy tokens never rotated
- Slack webhooks in config
- Debug flags they added
- Test accounts with elevated privileges

### 5. The Nation-State ("What persistent access do I plant?")
- Supply chain: inject into npm dependencies
- Build pipeline: inject into CI/CD
- Backdoor via "support" access
- Long-lived OAuth tokens
- Certificate authority compromise
- DNS control
- Admin impersonation via SSO misconfig

---

## The Impossible Questions Technique

Write down 10 questions you believe have no answer. Then search the code for the
answer. Trust the code, not your belief.

### Payment/billing impossible questions
1. Can a free user create a Stripe checkout for $0 successfully?
2. Can a user receive premium access by reusing a canceled subscription ID?
3. Can a webhook signed for Tenant A update Tenant B's subscription status?
4. Can the price for a plan be overridden via request metadata?
5. Can a deleted user still receive subscription status updates?

### Authentication impossible questions
6. Can a user's JWT be accepted as a different user's session after signing out?
7. Can a stale session persist after password change?
8. Can a disabled account still receive password reset emails?
9. Can an expired API key be "renewed" via the revocation endpoint?
10. Can a magic link link to a different user's account?

### Authorization impossible questions
11. Can a viewer become a member by repeatedly clicking "request access"?
12. Can an admin remove another admin's admin flag and then re-elevate themselves?
13. Can the owner role be assigned to a non-member?
14. Can a user call admin endpoints with a missing session (hoping for null-check bugs)?

### Data exposure impossible questions
15. Can an unauthenticated user list all user IDs via a bulk endpoint?
16. Can an error response leak the SQL query?
17. Can the OG-image generator be tricked into generating an image of another user's data?
18. Can pagination reach rows the filter should exclude?
19. Can aggregate queries (counts, sums) leak other-tenant data by inference?

### System impossible questions
20. Can an attacker trigger all users' password reset emails via a bulk operation?
21. Can a malformed webhook crash the entire webhook processor?
22. Can a large request body exhaust memory (no `io.LimitReader`)?
23. Can a symlink in an uploaded zip escape the extraction directory?
24. Can a user's username inject HTML into the admin dashboard?

---

## The Red Team Exercises

Formalized hunt scenarios. Pick one per audit.

### Exercise 1: "The $0 Premium Exploit"
**Goal:** Get premium features without paying.
**Time:** 2 hours
**Rules:** No social engineering. Only protocol-level attacks.
**Deliverable:** Written exploit chain + fix.

### Exercise 2: "The Cross-Tenant Leak"
**Goal:** As Tenant A, read any data belonging to Tenant B.
**Time:** 4 hours
**Rules:** Both tenants are legitimate paying customers.
**Deliverable:** Data exposure proof + RLS coverage analysis.

### Exercise 3: "The Admin Takeover"
**Goal:** As a regular user, gain admin privileges.
**Time:** 4 hours
**Rules:** Start from a free account.
**Deliverable:** Escalation path + RBAC audit.

### Exercise 4: "The Webhook Forgery"
**Goal:** Forge a webhook that activates a subscription for a victim.
**Time:** 2 hours
**Rules:** Attack any payment provider in use.
**Deliverable:** Forged webhook + signature verification audit.

### Exercise 5: "The Slow Burn"
**Goal:** Plant persistent access that survives a security patch.
**Time:** 8 hours
**Rules:** Persistence mechanism must survive a full redeploy.
**Deliverable:** Persistence technique + detection strategy.

---

## The Meta-Creativity Prompts

When even the creativity triggers feel stale:

### "What would make the security team cry?"
What finding would, if true, cause a 2am page-out, a customer refund campaign, a
press release, and a security PM meeting? Hunt for exactly that finding.

### "What did the developer forget?"
Read the git history. Find the rushed commits. Find the comments like "TODO:
improve this later." Find the code reviewed by nobody. That's where bugs live.

### "What's 'too obvious to check'?"
Many of the worst bugs are ones everyone assumed someone else had checked.
Verify the assumptions everyone made. The bugs nobody looks for are the bugs
nobody finds.

### "What breaks if the infrastructure is adversarial?"
Assume Cloudflare is lying about the IP. Assume AWS is serving forged TLS certs.
Assume Redis is returning attacker-controlled data. Assume the DB has been
rollback-replayed. What fails?

### "What happens if two bugs agree with each other?"
Two bugs in isolation may each be dismissed as "not exploitable." Together they
may form a chain. Compose every pair of open findings.

---

## Usage Protocol

1. Do a checklist-based audit first (domains, operators, kernel)
2. When it comes back clean OR you've found low-hanging fruit only:
3. Allocate 30-60 minutes for creative hunting
4. Walk through this file start to finish, spending 1-3 minutes per prompt
5. For any prompt that triggers a "huh, actually..." → investigate immediately
6. Record each creative prompt that led to a finding (refines your instincts)

**The best audits spend 30% of their time on creativity triggers.** This is not
padding. This is where non-obvious bugs live.
