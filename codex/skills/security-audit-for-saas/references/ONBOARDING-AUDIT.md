# Security Onboarding Audit — The First Week

You've just joined a project (new job, new contract, new consultancy). You
need to assess the security posture without boiling the ocean. This file is
the week-one audit playbook.

---

## Day 1 (2 hours): The Scan

Run these in order. Don't dig into findings yet — just collect data.

### 1.1 Repository inventory (20 min)
```bash
# What languages?
cloc src/

# What framework?
cat package.json | jq '.dependencies'

# Database?
grep -r 'postgres\|mysql\|mongodb\|supabase' package.json src/lib/db/

# Third-party integrations?
grep -rn 'stripe\|paypal\|auth0\|clerk\|sentry' package.json
```

### 1.2 Secret scan (30 min)
```bash
# Run the secret scanner
./scripts/leak-scan.sh .

# Git history
git log --all --full-history --pretty=format: --name-only --diff-filter=A | grep -E '^\.env' | sort -u

# .gitignore sanity
cat .gitignore | grep -E '\.env|secrets'
```

### 1.3 Route inventory (20 min)
```bash
# All API routes
find src/app/api -name 'route.ts' | wc -l

# Webhook endpoints
find src/app/api -path '*webhook*'

# Admin endpoints
find src/app/api -path '*admin*'

# Cron endpoints
find src/app/api -path '*cron*'
```

### 1.4 Auth inventory (20 min)
```bash
# What auth library?
grep -rn 'getServerSession\|supabase.auth\|clerk\|auth0\|NextAuth' src/lib/auth/

# Find auth middleware
cat src/proxy.ts src/middleware.ts 2>/dev/null | head -100

# Session storage
grep -rn 'sessionCookie\|jwt\|refresh_token' src/lib/
```

### 1.5 Database inventory (20 min)
```bash
# Migrations
ls supabase/migrations/ 2>/dev/null
ls src/db/migrations/ 2>/dev/null

# RLS policies
grep -r 'CREATE POLICY\|ENABLE ROW LEVEL SECURITY' supabase/

# Schema
find . -name 'schema.ts' -o -name 'schema.sql'
```

### 1.6 Test inventory (10 min)
```bash
# Security tests
find . -path '*test*security*' -type f
find . -path '*security*test*' -type f

# Integration tests
find . -path '*integration*' -type f | head -20
```

---

## Day 2 (2 hours): The Kernel Check

Go through the 10 axioms and check each.

### Axiom 1: Fail-open patterns
```bash
./scripts/find-fail-open.sh .
```
**Finding count:** ___

### Axiom 2: Duplicate parsers
- Does proxy match paths differently from rate limiter? ___
- Does Stripe handler diverge from PayPal handler? ___
- Does frontend Zod match backend Zod? ___

### Axiom 3: Normalize before validate
```bash
grep -rn 'z\.string()\.min' src/
```
For each, check if normalization happens before. Count issues: ___

### Axiom 4: Self-heal down
```bash
grep -rn 'isAdmin.*true\|role.*admin\|upgrade.*role' src/
```
Any auto-promotion? ___

### Axiom 5: Error oracles
```bash
# Different error messages for different states?
grep -rn 'Invalid password\|User not found\|No account' src/app/api/
```

### Axiom 6: Presence-only header checks
```bash
grep -rn 'headers.*has\|headers.*get.*truthy' src/
```

### Axiom 7: Recovery paths
```bash
# Find all cron jobs
find src/app/api/cron -type f
# For each, check if it re-enforces invariants
```

### Axiom 8: Surface enumeration
Run api-auth-mapper.sh. Count unauthenticated routes: ___

### Axiom 9: Server-side pricing
```bash
# Client-submitted prices (should be zero hits)
grep -rn 'body\.amount\|body\.price\|body\.unit_amount' src/
```

### Axiom 10: Multi-tenant both layers
```bash
# RLS + app layer checks
grep -rn 'requireOrgRole\|requireOrgPermission' src/
```

---

## Day 3 (3 hours): The Critical Path Audit

Focus on the 3 highest-value flows:
1. **Payment** (how does money enter?)
2. **Authentication** (how do users log in?)
3. **Data access** (how is tenant data protected?)

### Payment Audit (1 hour)
Read every file in these paths:
- `src/app/api/*/webhook/*` (Stripe, PayPal, etc.)
- `src/app/api/*/checkout/*`
- `src/lib/services/subscription*`
- `src/lib/services/billing*`

For each, apply the BILLING.md checklist. Count findings: ___

### Auth Audit (1 hour)
Read every file in:
- `src/lib/auth/*`
- `src/app/api/auth/*`
- `src/app/api/*/login*`
- `src/lib/csrf.ts`

Apply AUTH.md checklist. Count findings: ___

### Data Access Audit (1 hour)
- Run `scripts/rls-coverage.sql`
- Read random sample of 10 data-access routes
- Verify each uses correct client (user vs admin)
- Check for `requireOrgRole` / RLS combination

---

## Day 4 (2 hours): Dependencies + Infrastructure

### Dependency audit
```bash
pnpm audit --audit-level=high
# or: npm audit --audit-level=high
# or: pip-audit
# or: cargo audit
```

### Deployment config
- Vercel / AWS / GCP settings
- Environment variables list (no values)
- Secret storage location
- Backup configuration
- Monitoring setup

### CI/CD audit
- `.github/workflows/*` — any workflows with secrets?
- `pull_request` vs `pull_request_target`
- Dependabot enabled?
- SAST in CI?

---

## Day 5 (2 hours): Write the Report

Use the AUDIT-REPORT-TEMPLATE.md format.

### Structure
1. **Executive Summary** — 3 bullet points
2. **Findings** — prioritized by severity
3. **Positive Findings** — things done well
4. **Quick Wins** — fixes that take <1 day
5. **Longer-term** — fixes that take >1 week

### Presentation
Present to engineering leadership. Keep it to 30 min:
- 5 min: context
- 15 min: top 5 findings (with proposed fixes)
- 5 min: compliance/risk overview
- 5 min: Q&A

---

## What to Skip in Week 1

- **Pen testing** (too early; fix obvious issues first)
- **Formal threat modeling** (do after you have context)
- **Compliance gap analysis** (needs more time)
- **Architecture review** (needs trust with team first)
- **Security training** (needs management buy-in)

---

## The Output

By end of week 1, you should have:
- [ ] An inventory of all attack surfaces
- [ ] A list of critical findings with proposed fixes
- [ ] A list of quick wins (things to fix immediately)
- [ ] A rough maturity assessment (Level 1-5)
- [ ] A 30-day plan for deeper audit

## Things NOT to do in Week 1

### DON'T try to fix everything
You're assessing, not fixing. Note findings, propose fixes, let the team
prioritize.

### DON'T trust the team's self-assessment
They'll tell you "we're secure." Verify.

### DON'T ignore the easy stuff
Sometimes the easy finding (commit with secrets, missing MFA) is the most
important.

### DON'T overwhelm with findings
100 findings is useless. Cluster into 5-10 themes with 3-5 exemplars each.

### DON'T bury the lede
Lead with the scariest finding. Engineering leaders have 30 seconds of
attention.

---

## The Week-1 Deliverables

1. **Findings spreadsheet** (for tracking)
2. **Executive summary** (1 page)
3. **Detailed report** (5-10 pages)
4. **30-day plan** (2 pages)
5. **Presentation deck** (10-15 slides)

---

## See Also

- [AUDIT-REPORT-TEMPLATE.md](../assets/AUDIT-REPORT-TEMPLATE.md)
- [SECURITY-MATURITY.md](SECURITY-MATURITY.md) — assess current level
- [THREAT-MODELING.md](THREAT-MODELING.md) — use for deeper audits
- [scripts/audit-quick.sh](../scripts/audit-quick.sh) — automation
