---
name: bmad
description: BMAD (Best, Most Appropriate, Design) method for technology decisions; use for stack selection, vendor comparison, TCO and lock-in analysis, architecture tradeoffs, and "best vs most appropriate" evaluations.
---

# BMAD Method

## When to use
- Choose between competing technologies, vendors, or architectures.
- Decide on stack components (database, cloud, frameworks, data tooling).
- Produce decision records, TCO comparisons, or risk assessments.
- Pressure-test "popular" vs "appropriate for our constraints" claims.

## Core philosophy
Technology decisions should not be made only because something is popular, novel, or familiar. BMAD forces a balance between:
- Industry best practices.
- Your specific context (team, budget, timeline, scale).
- Long-term architectural alignment.

## BMAD framework

### Best (industry gold standard)
Question: What is considered best practice in the industry?

Criteria:
- Battle-tested at scale.
- Widely adopted by successful teams.
- Strong feature depth and ecosystem.
- Clear documentation and operational guidance.

Examples:
- Database: PostgreSQL (ACID, reliability, JSON support)
- Message queue: Apache Kafka (throughput, durability, replay)
- Cloud: AWS (breadth of services, enterprise features)
- Backend: Express or Fastify (maturity, ecosystem)

When Best matters most:
- Enterprise or mission-critical systems.
- Long-lived products (5+ years).
- Large teams needing stability.
- Regulatory or compliance-heavy contexts.

### Most Appropriate (context fit)
Question: What is most appropriate for your specific situation?

Context factors:
1) Team
   - Size: 2-5 vs 10-50 vs 100+
   - Expertise: what the team already knows
   - Learning capacity and ramp time
2) Financial
   - Budget: free tier vs hundreds vs thousands per month
   - Funding stage: bootstrap vs seed vs enterprise
   - Cost predictability: fixed vs variable
3) Timeline
   - POC: 1-2 weeks
   - MVP: 1-3 months
   - Production: 6-12 months
4) Scale
   - Current: 100 vs 10k vs 1M users
   - Projected: 6-12 month growth
   - Growth rate: steady vs exponential

Examples:
- Startup (5 people, $200/mo): Firebase (fast, managed, cheap)
- Scale-up (20 people, $5k/mo): PostgreSQL + Redis
- Enterprise (100 people, $50k/mo): PostgreSQL (RDS) + Kafka + Redis

When Most Appropriate overrides Best:
- Constrained budgets or short deadlines.
- Mismatch between team skills and "best" tech.
- Compliance requirements that narrow options.

### Design (architectural alignment)
Question: How does this fit your system design and long-term vision?

Considerations:
1) Vendor lock-in
   - Open source vs proprietary
   - Standard protocols vs vendor APIs
   - Export and migration options
2) Ecosystem coherence
   - Fit with existing stack and tooling
   - Shared patterns across teams
3) Migration path
   - Can you switch later?
   - Migration cost and risk
4) Future-proofing
   - Technology trajectory
   - Vendor viability and community health

Examples:
- Low lock-in: PostgreSQL (standard SQL, portable)
- Medium lock-in: MongoDB (proprietary protocol, well-supported)
- High lock-in: DynamoDB (AWS-specific, migration cost)

When Design is critical:
- Long-term projects (3+ years)
- Multi-vendor strategy
- Data sovereignty or regulatory concerns
- Risk-averse organizations

## Decision matrix template
```markdown
## Technology Decision: [Category]

### Context
- Team Size: [number]
- Budget: $[amount]/month
- Timeline: [duration]
- Current Scale: [users/requests]
- Target Scale (12mo): [projected growth]

### Requirements
Must Have:
- [ ] Requirement 1
- [ ] Requirement 2

Nice to Have:
- [ ] Feature 1
- [ ] Feature 2

Constraints:
- [ ] Constraint 1 (e.g., GDPR, open-source)

### BMAD Analysis

Best: [Technology]
- Strengths:
- Ecosystem:
- Proven at:

Most Appropriate: [Technology]
- Team Fit:
- Budget Fit:
- Timeline Fit:
- Scale Fit:

Design: [Technology]
- Lock-in Risk: Low | Medium | High
- Migration Path:
- Ecosystem Fit:
- Future-Proofing:

### Recommendation
Choose: [Technology]

Rationale:
1. [Reason 1]
2. [Reason 2]
3. [Reason 3]

Alternative Paths:
- If [condition]: consider [alternative]
- If [condition]: consider [alternative]

### Implementation Plan
- Week 1:
- Week 2:
- Week 3:
```

## Common decision patterns

### Databases
Best: PostgreSQL (ACID, robustness, JSON, ecosystem)

Most Appropriate:
- Startup (<$500/mo): Supabase (managed PostgreSQL)
- Scale-up ($1k-5k/mo): AWS RDS PostgreSQL
- Enterprise (>$10k/mo): Aurora PostgreSQL or CockroachDB

Design:
- Low lock-in: self-hosted PostgreSQL or RDS
- High flexibility: PostgreSQL (relational + JSON)
- NoSQL alternative: MongoDB (document model fit)

### Cloud providers
Best: AWS (most mature, broadest services)

Most Appropriate:
- Startup: Vercel/Netlify + Supabase
- Scale-up: GCP (Kubernetes) or Hetzner (cost)
- Enterprise: AWS or Azure (Microsoft-heavy orgs)

Design:
- Multi-cloud: Kubernetes + Terraform
- Cost-sensitive: Hetzner or DigitalOcean
- Vendor-neutral: avoid Lambda, use containers

### Frontend frameworks
Best: Next.js (React) or Nuxt (Vue)

Most Appropriate:
- Content-heavy: Astro
- App-heavy: Next.js or SvelteKit
- Rapid prototyping: Remix

Design:
- Framework-agnostic: Astro
- React ecosystem: Next.js
- Performance-first: SvelteKit or Qwik

## Cost analysis

### 3-year TCO template
```markdown
| Component              | Option A | Option B | Option C |
|------------------------|----------|----------|----------|
| Infrastructure         |          |          |          |
| - Hosting              | $X       | $Y       | $Z       |
| - Backup/DR            | $X       | $Y       | $Z       |
| - Monitoring           | $X       | $Y       | $Z       |
| Engineering            |          |          |          |
| - Initial setup        | $X       | $Y       | $Z       |
| - Training             | $X       | $Y       | $Z       |
| - Ongoing maintenance  | $X       | $Y       | $Z       |
| Risk costs             |          |          |          |
| - Vendor lock-in       | $X       | $Y       | $Z       |
| - Migration potential  | $X       | $Y       | $Z       |
| Total                  | $X       | $Y       | $Z       |
```

Hidden costs to consider:
1) Learning curve and productivity dip
2) Maintenance burden (patching, upgrades)
3) Vendor lock-in and migration cost
4) Opportunity cost (time-to-market impact)

## Risk assessment

### Risk matrix
```markdown
| Risk                | Probability | Impact | Mitigation              | Decision |
|---------------------|-------------|--------|-------------------------|----------|
| Vendor shutdown     | 10%         | High   | Use open-source fork    | Accept   |
| Cost explosion      | 30%         | High   | Set billing alerts      | Mitigate |
| Performance issues  | 15%         | Medium | Load testing early      | Mitigate |
| Team skill gap      | 40%         | Medium | Training + pairing      | Mitigate |
| Lock-in constraints | 80%         | Low    | Abstract vendor APIs    | Accept   |
```

Mitigation strategies:
1) Vendor lock-in
   - Use abstraction layers.
   - Prefer standard protocols (SQL, S3, AMQP).
   - Test exports and backups regularly.
2) Cost explosion
   - Set billing alerts at 50/75/90% of budget.
   - Plan scaling tiers (what happens at 10x users?).
3) Knowledge gaps
   - Pairing and internal training.
   - Hire consultants for initial setup if needed.

## Real-world examples

### Example 1: Database for e-commerce startup
Context:
- Team: 5 engineers
- Budget: $500/month
- Timeline: 3 months to MVP
- Scale: 1,000 users to 50,000 in 12 months

BMAD:
- Best: PostgreSQL
- Most Appropriate: Supabase PostgreSQL
- Design: low lock-in, migration to RDS later

Decision: Supabase PostgreSQL
Rationale: SQL skills, budget fit, fast setup.

### Example 2: Message queue for IoT platform
Context:
- Team: 20 engineers
- Budget: $5,000/month
- Timeline: 6 months
- Scale: 100k messages/sec, 1-year retention

BMAD:
- Best: Kafka
- Most Appropriate: Confluent Cloud
- Design: standard Kafka protocol, migration path

Decision: Confluent Cloud
Rationale: known tech, manageable cost, fast setup.

### Example 3: Auth provider for SaaS
Context:
- Team: 10 engineers
- Budget: $1,000/month
- Requirements: SOC2, GDPR, SSO, MFA
- Timeline: 2 months

BMAD:
- Best: Auth0
- Most Appropriate: Clerk
- Design: medium lock-in, standard OAuth

Decision: Clerk
Rationale: cheaper, modern DX, compliance-ready.

## Best practices
- Document decisions as ADRs.
- Re-evaluate on a cadence (quarterly costs, annual full BMAD).
- Build escape hatches for lock-in.
- Start managed for speed, plan for self-hosting later.

## Activation keywords
- "best vs most appropriate"
- "BMAD method"
- "technology decision framework"
- "stack selection"
- "database choice"
- "cloud provider comparison"
- "architecture tradeoffs"
- "TCO analysis"
- "vendor lock-in"
- "migration strategy"

## Resources
- ADR templates: https://adr.github.io/
- TCO calculators: AWS, GCP, and Azure pricing calculators
- Technology radar: https://www.thoughtworks.com/radar
- Community: https://reddit.com/r/ExperiencedDevs
