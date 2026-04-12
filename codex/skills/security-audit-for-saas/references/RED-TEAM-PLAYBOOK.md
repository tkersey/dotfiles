# Red Team Playbook for SaaS

How to think and act like an attacker on your own product. A red team is not
a pen test — pen tests are bounded and scoped; red teams are adversarial and
goal-oriented.

---

## The Red Team Mission

**Goal:** Achieve an objective (exfiltrate data, escalate privilege, disrupt
service) without detection, using any means available.

**Constraints:**
- Stay within authorized scope
- Don't damage production
- Don't affect real customers
- Document everything

**Success metric:** Not "did we find bugs", but "could we achieve the objective?"

---

## The Red Team Kill Chain (for SaaS)

Adapted from Lockheed Martin Cyber Kill Chain for SaaS:

```
1. Reconnaissance    — Map the attack surface
2. Weaponization     — Choose attack vectors
3. Delivery          — Get initial access
4. Exploitation      — Execute the attack
5. Installation      — Establish persistence
6. Command & Control — Maintain access
7. Actions on Objective — Achieve the goal
```

Break the chain at any step and the attack fails. Defenders need to win once;
attackers need to win every step.

---

## Phase 1: Reconnaissance

### Passive recon (no touching the target)
- WHOIS domain records
- DNS enumeration (subdomains)
- Certificate transparency logs (crt.sh)
- GitHub search for org repos, contributor emails
- LinkedIn for employees
- Wayback Machine for old versions
- Public S3 buckets
- Public error messages (Stack Overflow)
- Shodan for exposed services
- Google dorking (`site:example.com filetype:log`)

### Active recon (touching the target)
- Port scanning
- Service enumeration (nmap -sV)
- Directory brute forcing (ffuf, feroxbuster)
- Subdomain brute forcing
- Web crawl (gospider, katana)
- API enumeration

### SaaS-specific recon
- Look for `/.well-known/security.txt`
- Check `/.git/HEAD` for exposed git
- Look for `sitemap.xml`, `robots.txt`
- Enumerate subdomains for staging/dev
- Find API documentation

---

## Phase 2: Weaponization

Based on recon, choose tactics. For a typical SaaS:

### High-value targets
1. **Billing flow** — payment bypass = direct financial impact
2. **Admin panel** — privilege escalation = full compromise
3. **Customer data** — GDPR-sized exfiltration = reputation damage
4. **API tokens** — persistent access = long-term control
5. **Webhook endpoints** — untrusted input = pivot point

### Common weaponization
- **Phishing emails** for employee credentials
- **Credential stuffing** with leaked passwords
- **Supply chain** (fake package, malicious PR)
- **API abuse** (business logic flaws)
- **SSRF** for internal access

---

## Phase 3: Delivery

### Legitimate entry points
- Sign up as a free user
- Upgrade to paid plan
- Use a test credit card (Stripe test mode)
- Invite yourself to an org
- Enable features via API

### Social engineering (if in scope)
- Phishing emails to employees
- Pretexting to support team
- Impersonating vendors

### Technical delivery
- Exploit public vulnerability
- Weak authentication
- Misconfigured cloud services
- Exposed admin panels

---

## Phase 4: Exploitation

Pick your objective. Here are common SaaS scenarios:

### Objective A: Cross-tenant data read
1. Sign up as two orgs (Alice Corp, Bob Corp)
2. Find a multi-tenant resource
3. Try to read Bob's data as Alice
4. Test for:
   - IDOR on IDs
   - GraphQL introspection across tenants
   - RLS bypass in Supabase
   - Shared cache bleed
   - SSO org binding flaws

### Objective B: Privilege escalation
1. Sign up as free user
2. Try to become admin:
   - Mass assignment (`PATCH /users/me {role: admin}`)
   - Invite link manipulation
   - Email change to admin whitelist
   - SSO provisioning race
   - Token manipulation
3. Verify actual admin access

### Objective C: Payment bypass
1. Start checkout flow
2. Intercept webhook
3. Forge webhook signature
4. Or: manipulate client-side price
5. Or: replay old webhook
6. Or: timing attack on subscription check

### Objective D: Data exfiltration
1. Find API endpoint with data access
2. Enumerate IDs
3. Extract data at scale
4. Bypass rate limits:
   - Multiple API tokens
   - Multiple accounts
   - Distributed sources
5. Measure detection: did they notice?

### Objective E: DoS / cost amplification
1. Find expensive operations
2. Trigger them at high rate
3. Or: find amplification factor (1 req → N internal ops)
4. Measure: at what rate does service degrade?
5. Consider denial of wallet (LLM, cloud costs)

---

## Phase 5: Installation / Persistence

### For SaaS, "persistence" means:
- Long-lived API tokens
- OAuth grants that survive password resets
- SSH keys in CI/CD
- Backdoor admin users
- Webhooks pointing to attacker
- Scheduled tasks

### Example: Persistence via API token
1. Compromise user account
2. Create API token
3. Even if password changed, token remains valid
4. Defense: revoke all tokens on password change

### Example: Persistence via OAuth
1. Compromise account briefly
2. Grant yourself OAuth access
3. OAuth grant persists after password reset
4. Defense: revoke OAuth on security events

### Example: Persistence via webhook
1. Set webhook URL to attacker server
2. Every event triggers attacker
3. Defense: webhook URLs are read-only by default

---

## Phase 6: Command & Control

Less relevant for SaaS, but:
- Attacker needs to keep connection alive
- Tokens must be refreshed
- Detection must be avoided

### Avoiding detection
- Use low-volume queries
- Match legitimate traffic patterns
- Use multiple accounts/IPs
- Exponential backoff on errors
- User-agent matching real clients

---

## Phase 7: Actions on Objective

Achieve the goal you set in Phase 2. Document:
- What did you accomplish?
- How long did it take?
- Were you detected?
- What bypassed your defenses?

---

## Red Team Output

### The report structure

```markdown
# Red Team Engagement: [Name]
Duration: [dates]
Scope: [in-scope systems]
Objective: [what we tried to achieve]

## Executive Summary
[3 sentences: what we found, why it matters, what to fix]

## Timeline
[When we did what, what we discovered]

## Successful Attack Paths
### Path 1: [Name]
1. Step 1: [Action, result]
2. Step 2: [Action, result]
...
Objective achieved: YES/NO
Detection level: None / Partial / Full

## Failed Attack Paths
[Things we tried that didn't work — also valuable!]

## Detection Gaps
[Things we did that weren't detected but should have been]

## Recommendations
[Prioritized list of fixes]
```

---

## Red Team vs Blue Team Exercises

### Purple team (both at once)
Red team attacks in real-time while blue team watches. Everyone learns.

### Tabletop exercises
Simulate an incident on paper. Walk through response.

### Capture the flag
Red team plants "flags" in specific places. Blue team finds them.

---

## The Red Team Mindset

### 1. Goal over method
Don't use cool techniques. Use whatever works. Phishing is often more
effective than 0-days.

### 2. Least resistance
Find the weakest link. Humans > software > infrastructure.

### 3. Think adjacent
Can't break auth directly? Break password reset. Can't break password reset?
Break the password reset email. Can't break email? Steal the DNS.

### 4. Everything is in scope
If it affects the target, it's in scope (within authorization).

### 5. Document everything
Every command, every response, every decision. For the report and for
learning.

---

## Red Team Tooling

### Reconnaissance
- **Amass** — subdomain enumeration
- **Subfinder** — subdomain enumeration
- **Nuclei** — vulnerability scanning
- **httpx** — HTTP probing
- **feroxbuster** — directory brute force

### Exploitation
- **Burp Suite** — web proxy
- **OWASP ZAP** — alternative to Burp
- **sqlmap** — SQL injection
- **ffuf** — fuzzer
- **Intruder/Repeater** in Burp

### Post-exploitation
- **Metasploit** — exploitation framework
- **Cobalt Strike** — commercial, powerful
- **Sliver** — open-source C2
- **Mythic** — alternative C2

### Phishing
- **GoPhish** — phishing framework
- **Evilginx** — transparent phishing proxy
- **King Phisher** — spear-phishing

### Cloud
- **Pacu** — AWS exploitation
- **ScoutSuite** — cloud auditing
- **Prowler** — cloud security scanner

---

## Red Team Rules of Engagement

### Must have in writing
- **Scope:** in-scope / out-of-scope systems
- **Time window:** when red team is authorized
- **Restrictions:** no destructive actions, no DoS, no data theft
- **Emergency contacts:** who to call if something goes wrong
- **Authorization:** signed by executive team
- **Legal:** safe harbor from prosecution

### Must avoid
- Affecting real customers
- Destroying data
- Reading actual customer PII
- Legal boundaries
- Detection-tripping actions the blue team isn't ready for

---

## Self-Red-Team Exercises

Even solo/small teams can red team their own stuff:

### Exercise 1: "The curious intern"
Pretend you just joined the company as an intern. What data could you see?
What could you modify? What could you exfiltrate?

### Exercise 2: "The disgruntled ex-employee"
You just quit. Your sessions are still valid. What damage could you do
before they notice?

### Exercise 3: "The stolen laptop"
Your laptop is stolen. It has active sessions, saved passwords, SSH keys.
What can the thief do?

### Exercise 4: "The phished employee"
One employee was phished. You have their session cookie. Can you pivot to
admin? To production? To customer data?

### Exercise 5: "The compromised dependency"
A library you use is compromised. What does it have access to? How would you
know?

---

## Post-Red-Team: Blue Team Follow-up

After every engagement:
1. Fix every CRITICAL and HIGH finding
2. Add detections for every successful attack path
3. Update runbooks with lessons learned
4. Re-run the attack in 30 days (did you actually fix it?)
5. Measure improvement over time

---

## The Red Team Checklist

### Pre-engagement
- [ ] Rules of engagement signed
- [ ] Scope documented
- [ ] Emergency contacts listed
- [ ] Goals defined
- [ ] Test accounts/infrastructure set up

### During engagement
- [ ] Every action logged
- [ ] Daily status to blue team lead
- [ ] Respect scope boundaries
- [ ] Stop if unexpected damage occurs

### Post-engagement
- [ ] Written report delivered
- [ ] Findings prioritized
- [ ] Re-test after fixes
- [ ] Lessons learned documented
- [ ] Metrics published (time to detect, fix)

---

## See Also

- [ATTACK-SCENARIOS.md](ATTACK-SCENARIOS.md) — specific scenarios
- [ATTACK-SCENARIO-GENEALOGY.md](ATTACK-SCENARIO-GENEALOGY.md) — compose bugs
- [MITRE-ATTACK-MAPPING.md](MITRE-ATTACK-MAPPING.md) — TTP framework
- [SECURITY-TESTING.md](SECURITY-TESTING.md) — testing strategy
- [BUG-BOUNTY.md](BUG-BOUNTY.md) — external red teamers
- [subagents/red-team-agent.md](../subagents/red-team-agent.md)
