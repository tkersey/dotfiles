# Threat Modeling for SaaS

A threat model is the attacker's perspective, explicitly written down. Most SaaS
vulnerabilities exist because nobody wrote one. This file provides a lightweight
threat modeling methodology tailored to SaaS with billing.

---

## The SaaS Threat Model Template

Copy this template at the start of every audit. Fill it in before you touch code.

```markdown
# Threat Model: [Project Name]
# Date: [YYYY-MM-DD]
# Auditor: [Name]

## 1. What Are We Protecting?

### Assets (in order of value)
- [ ] Customer payment data (PII + financial)
- [ ] Customer personal data (names, emails, usage)
- [ ] Revenue flow (ability to charge customers correctly)
- [ ] Authentication credentials (passwords, tokens, API keys)
- [ ] Business logic / IP (proprietary algorithms, skill packs, templates)
- [ ] Brand reputation (uptime, error-free experience)
- [ ] Internal operational secrets (admin access, CI/CD tokens)

### Crown Jewels (the 3 things whose loss would end the business)
1. [e.g., Customer PII for 100K users]
2. [e.g., Production Stripe secret key]
3. [e.g., Admin access to billing system]

## 2. Who Are the Attackers?

Rank by relevance (for this project):

| Persona | Motivation | Skill | Budget | Persistence |
|---------|-----------|-------|--------|-------------|
| Opportunistic hacker | Fun, bragging | Low | Low | Low |
| Script kiddie | Credentials, defacement | Low | Low | Low |
| Financial fraudster | Free service, refund fraud | Medium | Medium | High |
| Competitor | Data, disruption | Medium | Medium | Medium |
| Disgruntled ex-employee | Revenge, IP theft | High | Low | High |
| Organized crime | Ransomware, PII resale | High | High | High |
| Nation-state | Long-term access, supply chain | Very high | Very high | Very high |

**For this project, the most likely attackers are:**
- [Primary persona and why]
- [Secondary persona and why]

## 3. Attack Surfaces

Enumerate EVERY entry point:

### Public internet-facing
- [ ] `/` (homepage)
- [ ] `/api/*` (all API routes — list each group)
- [ ] Webhook endpoints (Stripe, PayPal, etc.)
- [ ] OAuth/SSO callbacks
- [ ] OG image / thumbnail generators
- [ ] File upload endpoints
- [ ] Search endpoints
- [ ] Anonymous telemetry endpoints
- [ ] Health check endpoints
- [ ] robots.txt, sitemap.xml, manifest.json

### Authenticated user
- [ ] User dashboard
- [ ] User settings
- [ ] User API
- [ ] Export/import
- [ ] Billing portal
- [ ] Support/help endpoints

### Admin/internal
- [ ] Admin dashboard
- [ ] Admin API
- [ ] Support/impersonation tools
- [ ] Batch operations
- [ ] Debug endpoints (if live)

### System/cron
- [ ] Cron jobs
- [ ] Reconciliation crons
- [ ] Background workers
- [ ] Webhook replay

### Supply chain
- [ ] npm/pip/cargo dependencies
- [ ] CI/CD pipelines
- [ ] Deployment platform (Vercel, AWS, etc.)
- [ ] Third-party SaaS integrations

## 4. Trust Boundaries

Draw the data flow. At each arrow, mark trust transitions:

```
[Internet] --→ [CDN/Proxy] --→ [Middleware] --→ [Route Handler] --→ [DB]
    ↓              ↓                ↓                ↓              ↓
  untrusted    partially      authenticated    validated    row-level-
                trusted                                       secured
```

**Key questions at each boundary:**
- What validation happens here?
- What if it fails?
- What assumptions does the next layer make?

## 5. STRIDE Applied to Each Surface

For each attack surface, walk through STRIDE:

| Threat | Question |
|--------|----------|
| **S**poofing | Can I impersonate another user? |
| **T**ampering | Can I modify data I shouldn't? |
| **R**epudiation | Can I deny an action I took? |
| **I**nformation disclosure | Can I read data I shouldn't? |
| **D**enial of service | Can I make it unavailable? |
| **E**levation of privilege | Can I gain higher permissions? |

## 6. SaaS-Specific Threats

Beyond STRIDE, SaaS-specific:

| Threat | Question |
|--------|----------|
| Billing bypass | Can I get paid service for free? |
| Subscription hijacking | Can I take over another user's subscription? |
| Tenant leak | Can Tenant A see Tenant B's data? |
| Rate limit bypass | Can I exhaust limits on another user's behalf? |
| Abuse detection bypass | Can I act maliciously without triggering signals? |
| Refund fraud | Can I get refunds without losing access? |
| Seat bypass | Can I add unlimited users without paying? |
| Free trial reset | Can I get unlimited trial periods? |
| Entitlement staleness | Can I keep access after losing entitlement? |
| Cache poisoning | Can I inject data into another user's cache? |

## 7. Assume Breach Scenarios

Assume each of the following has already happened. What's the damage?

- [ ] Attacker has a valid session for one free user
- [ ] Attacker has a valid session for one paid user
- [ ] Attacker has a valid admin session
- [ ] Attacker has read access to production DB
- [ ] Attacker has write access to production DB
- [ ] Attacker has access to GitHub repo (read)
- [ ] Attacker has access to GitHub repo (write, force-push)
- [ ] Attacker has access to one env var (e.g., STRIPE_SECRET_KEY)
- [ ] Attacker controls a dependency (npm package compromise)
- [ ] Attacker controls DNS (temporarily)

For each: what's the blast radius? What would contain it?

## 8. Security Properties Required

What properties MUST hold? (If any can be violated, it's CRITICAL.)

- [ ] No user can access another user's data without explicit permission
- [ ] No user can gain higher privilege without explicit grant from admin
- [ ] Paid features are gated server-side (not client-side)
- [ ] All webhooks are signature-verified
- [ ] All secrets are server-side only
- [ ] All security-critical logs are append-only
- [ ] All auth decisions fail-closed on error
- [ ] All cross-tenant operations are blocked by default
- [ ] All prices come from server configuration
- [ ] All identity claims are cross-verified

## 9. Open Questions

Things you don't know the answer to. These are where bugs live.

- [ ] How does the Stripe webhook handle disputes?
- [ ] What happens if the reconciliation cron misses a day?
- [ ] Can a user's email be changed to match another user's?
- [ ] Is there a way to export data via public OG image generation?
- [ ] Are there any old API versions still reachable?
```

---

## How to Use the Template

### Step 1: Fill in Sections 1-3 BEFORE reading any code.
Your mental model is fresh. Bias-free. Write what SHOULD be true.

### Step 2: Fill in Sections 4-5 with the code open.
Verify your model matches reality. Every discrepancy is a potential bug.

### Step 3: Use Section 6 as a checklist during domain audit.
Each domain in SKILL.md maps to these threats.

### Step 4: Use Section 7 (assume breach) as a red team exercise.
For each scenario, would you know? Could you contain it?

### Step 5: Use Section 8 as the success criteria.
The audit is complete when you've verified each security property holds.

### Step 6: Use Section 9 as investigation tasks.
Open questions are the most productive part of the audit.

---

## Example Threat Model: A Completed One

```markdown
# Threat Model: jeffreys-skills.md (SaaS with Stripe + PayPal)
# Date: 2026-04-05
# Auditor: Security Team

## 1. Assets
Crown jewels:
1. Paying customer revenue (~$20K MRR)
2. Stripe live secret key (enables full billing control)
3. Skill pack IP (curated content that took years to build)

## 2. Attackers
Most likely:
- Financial fraudster (trying to get free premium)
- Disgruntled ex-employee (knows code, held credentials)
- Competitor (skill packs are valuable)

## 3. Attack Surfaces
Enumerated 73 endpoints across: /api/auth, /api/billing, /api/skills, /api/admin,
/api/webhooks, /api/cron. Old /api/v1 still exists (concern).

## 4. Trust Boundaries
Vercel → proxy.ts (CSRF, rate limit) → route handler (auth) → Drizzle → Supabase (RLS)

## 5. STRIDE Findings
- S: PayPal custom_id can be spoofed (FOUND, FIXED via validatePayPalUserId)
- T: Admin email self-heal (NOT present — verified)
- R: Audit log complete
- I: Missing RLS on users table (FOUND via RLS audit)
- D: Rate limiter fails open on Redis outage (FOUND, accepted risk)
- E: TOCTOU in team member addition (FOUND, FIXED via FOR UPDATE)

## 6. SaaS-Specific Findings
- Billing bypass via Stripe metadata: NOT present (price validated server-side)
- Subscription hijacking: FIXED via validatePayPalUserId
- Trial abuse: Email normalization doesn't strip + tags (LOW — acceptable)
- Seat bypass: FIXED via advisory lock

## 7. Assume Breach
- One valid user session: RLS limits blast radius to that user
- Admin session: full damage, manual recovery via DB access
- Stripe key: catastrophic, assume total refund/chargeback fraud
- GitHub write: catastrophic, review CI/CD access controls

## 8. Security Properties
All 10 verified except:
- [ ] "All cross-tenant operations blocked by default" — one endpoint allows
  inferring other-tenant user count via pagination. MEDIUM.

## 9. Open Questions
- Does /api/og/[userId] leak PII? YES — investigated, now redacted
- Is there a way to export data via a hidden admin endpoint? NO
- Are old API versions reachable? /api/v1 exists but only serves 410 Gone (OK)
```

---

## Lightweight Threat Model (10 minutes)

If you don't have time for the full template, use this minimum:

1. **What am I protecting?** (1 line: crown jewel)
2. **Who's attacking?** (1 line: top attacker persona)
3. **How would they get in?** (3 lines: top entry points)
4. **What if they succeeded?** (1 line: worst case)
5. **What's my weakest assumption?** (1 line: implicit trust)

5 sentences. 10 minutes. Catches 60% of what the full template catches.

---

## Threat Modeling as a Continuous Practice

Threat modeling is not a one-time audit activity. It should happen:

- **Feature design:** Before writing code for a new feature
- **Code review:** When reviewing security-critical PRs
- **Incident response:** After every incident, update the model
- **Quarterly:** Refresh for drift, new threats, new surfaces
- **Before launch:** Full audit against the latest model

The threat model is a living document. When it diverges from reality, you have bugs.
