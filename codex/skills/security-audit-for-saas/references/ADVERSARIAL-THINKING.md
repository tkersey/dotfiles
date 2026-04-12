# Adversarial Thinking — Mental Models for Security Auditors

Security audits fail when the auditor thinks like a defender. The best findings
come from thinking like an attacker. This file is a library of mental models,
frameworks, and cognitive primitives for adversarial thinking.

Use this for:
- Breaking out of checklist-mode
- Training new security reviewers
- Finding novel attack vectors
- Red team exercise design
- Cross-training between audit modes

---

## The Nine Mental Models

### 1. Kill Chain (Lockheed Martin)

**Definition:** Linear sequence of 7 steps an attacker takes from reconnaissance
to objective completion.

**Steps:**
1. **Reconnaissance** — gather info about target
2. **Weaponization** — create exploit + payload
3. **Delivery** — transmit the weapon
4. **Exploitation** — trigger the vulnerability
5. **Installation** — establish persistence
6. **Command & Control** — remote attacker control
7. **Actions on Objectives** — achieve goals

**Strengths:**
- Simple, memorable
- Emphasizes early detection (stop at recon/weaponization, not after breach)
- Useful for training

**Weaknesses:**
- Linear — modern attacks are non-linear, parallel
- Assumes external attacker (doesn't model insiders well)
- Doesn't capture cloud/SaaS-specific patterns

**SaaS application:**
1. Recon: OSINT on SaaS (DNS records, subdomains, API enumeration)
2. Weaponization: Craft a phishing email or credential stuffing list
3. Delivery: Email / login attempt
4. Exploitation: Compromised account
5. Installation: Create new API key, add backdoor user
6. C&C: Use API to maintain access
7. Actions: Exfiltrate data, pivot to customer data

**When most useful:** Communicating with non-security stakeholders about the
attack lifecycle.

### 2. MITRE ATT&CK

**Definition:** Knowledge base of adversary tactics and techniques based on
real-world observations. 14 tactics, 200+ techniques.

**Strengths:**
- Comprehensive, constantly updated
- Based on real-world data
- Common vocabulary for defenders
- SaaS-specific matrix available

**Weaknesses:**
- Can be overwhelming for beginners
- Descriptive (what attackers do), not prescriptive (how to defend)
- Doesn't model novel attacks well

**SaaS application:** See [MITRE-ATTACK-MAPPING.md](MITRE-ATTACK-MAPPING.md)

**When most useful:** Detection engineering, mapping findings to known
techniques, red team exercise planning.

### 3. Attack Trees (Schneier)

**Definition:** Tree structure where the root is an attacker goal, and branches
are sub-goals that decompose into leaves (specific attacks).

**Structure:**
```
GOAL: Access Premium Features Without Paying
├── AND: Direct Exploitation
│   ├── Bypass subscription check (OR)
│   │   ├── TOCTOU in permission check
│   │   ├── Cache staleness
│   │   └── RLS missing on subscription table
│   └── Forge webhook (OR)
│       ├── Compromise Stripe webhook secret
│       └── Forge signature via timing attack
├── OR: Indirect Exploitation
│   ├── Steal paying customer's session
│   │   ├── XSS
│   │   └── Session fixation
│   └── Social engineer support
└── OR: Fraud
    ├── Chargeback after use
    └── Trial abuse via email aliases
```

**Strengths:**
- Explicit decomposition
- Each branch can be probability-weighted
- Visualizes attack paths clearly

**Weaknesses:**
- Can be tedious for complex systems
- Requires good imagination (missed branches = missed attacks)

**SaaS application:** Build an attack tree for each critical asset (e.g., "access
paying features," "read cross-tenant data," "admin takeover").

**When most useful:** Structured threat modeling of specific assets or
high-value features.

### 4. STRIDE

**Definition:** Six threat categories for threat modeling. Acronym:
- **S**poofing
- **T**ampering
- **R**epudiation
- **I**nformation disclosure
- **D**enial of service
- **E**levation of privilege

**Strengths:**
- Easy to apply per asset or per feature
- Covers most threat categories
- Works well with data flow diagrams

**Weaknesses:**
- Can miss business logic flaws
- Overlapping categories (spoofing + elevation)
- Doesn't prioritize

**SaaS application:**
For each feature, walk through STRIDE:
- **S:** Can I impersonate another user in this flow?
- **T:** Can I modify data I shouldn't?
- **R:** Can I deny I took an action?
- **I:** Can I read data I shouldn't?
- **D:** Can I make this unavailable?
- **E:** Can I gain higher privileges?

**When most useful:** Threat modeling a specific feature or data flow.

### 5. PASTA (Process for Attack Simulation and Threat Analysis)

**Definition:** Seven-stage risk-centric threat modeling methodology.

**Stages:**
1. Define objectives (business and compliance)
2. Define technical scope (architecture)
3. Application decomposition (data flows)
4. Threat analysis (intelligence-informed)
5. Vulnerability analysis (specific weaknesses)
6. Attack analysis (realistic scenarios)
7. Risk analysis (impact + likelihood)

**Strengths:**
- Business-aligned
- Uses threat intelligence
- Produces actionable risk data

**Weaknesses:**
- Heavyweight for small teams
- Requires trained threat modelers
- Time-consuming

**SaaS application:** Appropriate for mature security teams doing annual threat
model reviews.

**When most useful:** Large enterprises with dedicated security teams.

### 6. DREAD

**Definition:** Five-factor rating system for threats. (Deprecated by Microsoft
but still widely used.)

**Factors (each rated 1-10):**
- **D**amage — how bad if exploited?
- **R**eproducibility — how reliably exploitable?
- **E**xploitability — how hard to exploit?
- **A**ffected users — how many impacted?
- **D**iscoverability — how easy to find?

**Score:** (D+R+E+A+D) / 5

**Strengths:**
- Simple numerical scoring
- Forces multi-dimensional thinking
- Familiar to many auditors

**Weaknesses:**
- Subjective scoring
- Not calibrated across raters
- Microsoft deprecated due to inconsistency

**Modern replacement:** Use [FAIR](#9-fair) for quantitative analysis or a
simple severity matrix for qualitative.

### 7. VAST (Visual, Agile, Simple Threat modeling)

**Definition:** Threat modeling scaled for DevOps. Uses two models:
- Application threat models (for devs)
- Operational threat models (for ops)

**Strengths:**
- Integrates with DevOps workflow
- Scales to many teams
- Tool-friendly (ThreatModeler product)

**Weaknesses:**
- Tool-dependent
- Less familiar than STRIDE
- Can become checkbox compliance

**SaaS application:** Appropriate for SaaS with CI/CD-driven development.

**When most useful:** Regular threat modeling integrated with sprints.

### 8. OCTAVE

**Definition:** Operationally Critical Threat, Asset, and Vulnerability
Evaluation. Risk-based security assessment methodology from CMU.

**Strengths:**
- Operational focus
- Considers organizational context
- Self-directed (no external consultant required)

**Weaknesses:**
- Very heavyweight
- Document-heavy
- Dated (from 2001)

**When most useful:** Large enterprises doing formal risk assessments.

### 9. FAIR (Factor Analysis of Information Risk)

**Definition:** Quantitative risk model. Calculates risk in dollars.

**Inputs:**
- Loss event frequency (LEF)
- Loss magnitude (LM)

**Decomposition:**
- LEF = Threat Event Frequency × Vulnerability
- LM = Primary Loss + Secondary Loss

**Strengths:**
- Translates security to business language
- Enables cost/benefit analysis
- Defensible to executives

**Weaknesses:**
- Requires data (often lacking)
- Complex to apply
- Can encourage false precision

**SaaS application:** Quantify the business impact of security gaps. "We have
a 20% annual risk of an entitlement bypass affecting 50K users × $10/month
lost revenue = $1.2M annual expected loss."

**When most useful:** Board-level security communication, cyber insurance
justification.

---

## 13 Mental Primitives Auditors Actually Use

Beyond formal frameworks, experienced auditors use these mental primitives
intuitively. Make them explicit.

### Primitive 1: Money-Flow Tracing
"Follow the money." Trace every dollar from user to bank. Wherever money enters
or leaves the system is a high-value target.

**Question to ask:** Where does revenue enter? Where do refunds exit?

### Primitive 2: Trust Boundary Crossings
Every place data crosses between systems (user→app, app→DB, app→third party,
client→server, service→service) is a trust boundary. Each crossing needs
validation.

**Question to ask:** What validation happens at each arrow in the data flow?

### Primitive 3: Assume Compromised Credentials
Start the audit assuming one valid user session has been compromised. What
damage can that user do? What can't they do? What stops them?

**Question to ask:** If I had a valid free-tier account, what couldn't I access?

### Primitive 4: Concurrency as Security Primitive
Single-threaded reasoning misses race conditions. Always ask: "What if two
requests arrive at the same time?"

**Question to ask:** Is this check-then-act atomic?

### Primitive 5: Denial of Wallet (DoW)
Beyond DoS, attackers can inflict costs by triggering expensive operations.
LLM calls, email sends, image generation, DB queries — all cost money.

**Question to ask:** What's the most expensive operation a user can trigger?
How do I rate-limit by cost, not requests?

### Primitive 6: Unexpected Input Types
Every input has a type. What if the wrong type arrives? What if JSON arrives in
a form field? What if a number arrives as a string? What if a string is an
emoji? What if it's 10MB?

**Question to ask:** What's the most unexpected thing I could put here?

### Primitive 7: Recursive Trust
User X trusts system A trusts service B trusts database C. A compromise at C
propagates up to X. Audit the full chain.

**Question to ask:** What does this feature transitively trust?

### Primitive 8: The "What If It Already Happened" Lens
Stop asking "can this be exploited" and start asking "what if it already was."
What would the signs look like? Would you see them?

**Question to ask:** If this vulnerability had been exploited yesterday, how
would I know?

### Primitive 9: Stored vs Reflected
For every data mutation, ask: where does this data go? If it's stored, every
user who views it is affected. If it's reflected, only the current user is.

**Question to ask:** Is this XSS/injection stored or reflected?

### Primitive 10: The Envelope of Acceptable Behavior
Define what normal behavior looks like, then ask: what's just outside the
envelope? Usually, that's where the bugs are.

**Question to ask:** What's the weirdest request a legitimate user would make?
What's just beyond that?

### Primitive 11: Privilege Monotonicity
Privileges should only go down over time, never up (without explicit grant).
Reconciliation that raises privilege is always a bug.

**Question to ask:** Does this code path ever raise a user's privilege?

### Primitive 12: Opacity vs Transparency
Security through obscurity is weak but sometimes appropriate. Know which you're
relying on. If the only thing protecting the endpoint is "nobody knows about
it," it will be found.

**Question to ask:** Would this still be secure if the design were public?

### Primitive 13: Cost of Discovery vs Cost of Attack
Even if an attack exists, if discovery costs more than the payoff, it won't be
found. Balance security investment accordingly.

**Question to ask:** Who would bother finding this? What's their payoff?

---

## The Selection Guide: Which Model When?

| Situation | Use Model |
|-----------|-----------|
| Communicating to non-security leaders | Kill Chain |
| Building detection rules | MITRE ATT&CK |
| Threat modeling specific features | STRIDE + Attack Trees |
| Board risk quantification | FAIR |
| DevOps threat modeling | VAST + STRIDE |
| Enterprise risk assessment | PASTA or OCTAVE |
| Red team planning | MITRE ATT&CK + Attack Trees |
| Creative vulnerability hunting | Mental Primitives |
| Incident post-mortem | Kill Chain + MITRE ATT&CK |
| Training new auditors | STRIDE (teach first) |

---

## The Attacker Mindset Principles

### Principle 1: Laziness is Fitness
Attackers take the path of least resistance. If your authentication is strong
but your password reset is weak, they'll target the reset. Always ask: "What's
the easiest way in?"

### Principle 2: Patience is Free
State actors have unlimited time. They'll wait years for the right opportunity.
Assume they're always watching. Short-lived credentials, regular key rotation,
and monitoring across long time horizons are defenses.

### Principle 3: One Vulnerability Wins
Defenders must cover all paths. Attackers need one. This asymmetry is why
defense-in-depth matters — no single control can win the battle.

### Principle 4: Trust Nothing
Zero trust isn't a product; it's a worldview. Assume the network is compromised,
the vendor is compromised, the user is compromised. Validate at every layer.

### Principle 5: Exploit Complexity
Complex systems have emergent behaviors. The bug the developer didn't
anticipate is usually at the seam between two complex subsystems. Hunt at
interfaces.

### Principle 6: Automate Relentlessly
Attackers automate. One script can try 100,000 passwords. Your defenses must
assume automation. Rate limits, MFA, monitoring must scale to automated attacks.

### Principle 7: Economics Rules
If an attack costs $100 and the payoff is $1000, it will happen. If it costs
$1M and the payoff is $10K, it won't. Know your economics.

---

## The Five Questions to Ask Every Feature

Before every feature ships, ask these five questions. If any answer is
uncomfortable, investigate.

### 1. What's the worst thing a malicious user could do with this?
Forces you to think about impact, not just functionality.

### 2. What assumptions does this feature make?
Make implicit assumptions explicit. Each assumption is a potential bug.

### 3. Who would want to attack this?
Understanding motivation reveals attack vectors.

### 4. What signal would tell us we're under attack?
If you can't answer, you have no detection.

### 5. If this were compromised, what's the blast radius?
Limits your damage. If the answer is "all user data," you have a problem.

---

## The Three Attacker Types (Simplified)

### Opportunist
- Goal: Any valuable data, any vulnerable system
- Skill: Low to medium
- Motivation: Money
- Defense: Basic security hygiene is enough

### Targeted
- Goal: YOUR specific data
- Skill: Medium to high
- Motivation: IP theft, espionage, competition
- Defense: Advanced detection, incident response readiness

### State Actor
- Goal: Strategic access, persistence
- Skill: Very high
- Motivation: National security, geopolitical
- Defense: Defense-in-depth, supply chain security, assume compromise

Most SaaS should assume opportunist defense. Rising threats may require targeted
defense. State actor defense is extraordinary and usually not justified for
small SaaS.

---

## How to Practice Adversarial Thinking

### Daily exercise (5 minutes)
Pick one feature in your product. Walk through the 5 questions above. Write
down the answers. Revisit next week.

### Weekly exercise (30 minutes)
Read one CVE from a similar product. Ask: "Could this happen to us?" Research
for 10 minutes.

### Monthly exercise (2 hours)
Red team one feature. Set an explicit goal ("get free access," "read another
user's data"). Try to achieve it without privileged access.

### Quarterly exercise (full day)
Tabletop incident response exercise. Pick a case study. Walk through detection,
containment, recovery, communication.

### Yearly exercise (full week)
External red team engagement. Pay professionals to try to breach your system.
Compare their findings to your internal audits.

---

## The Mental Shift

Most engineers think: "How do I make this work?"
Security engineers think: "How do I make this work, AND not break?"
Security auditors think: "How can I break this?"
Good security auditors think: "How can I break this in a way the developer
didn't anticipate?"
Great security auditors think: "What does the developer not know they don't
know about this?"

The difference between good and great is the willingness to assume you're
wrong and investigate why.
