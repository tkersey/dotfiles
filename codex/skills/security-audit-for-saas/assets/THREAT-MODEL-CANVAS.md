# Threat Model Canvas — One-Page Sketch

Use this template to quickly sketch a threat model for a new feature or system.
It takes 15-30 minutes. Use it before writing code.

---

## System: [Name]
## Date: [YYYY-MM-DD]
## Author: [name]

---

## 1. What are we protecting? (3 min)

**Crown jewels (what would be catastrophic to lose):**
- [ ] Customer PII
- [ ] Payment data
- [ ] Revenue flow
- [ ] Intellectual property
- [ ] Admin credentials
- [ ] Customer trust

**Not-crown jewels (low-value data):**
- [ ] Public marketing content
- [ ] Aggregated analytics
- [ ] Feature flags (non-gating)

---

## 2. Who's attacking? (3 min)

Check all that apply (most likely first):

- [ ] **Opportunist** — low skill, money-motivated
- [ ] **Financial fraudster** — medium skill, wants free service/refunds
- [ ] **Competitor** — medium skill, wants data or disruption
- [ ] **Disgruntled ex-employee** — high knowledge, known backdoors
- [ ] **Organized crime** — high skill, ransomware/data resale
- [ ] **Nation-state** — very high skill, long-term persistence

**Primary persona for this feature:** [one]

---

## 3. Entry points (5 min)

List EVERY way to reach the feature:

- [ ] Public API: [routes]
- [ ] Authenticated API: [routes]
- [ ] Admin API: [routes]
- [ ] Webhooks: [providers]
- [ ] CLI: [commands]
- [ ] UI: [pages]
- [ ] Batch import: [formats]
- [ ] Cron: [jobs]
- [ ] Old API versions: [if still active]

---

## 4. Trust boundaries (5 min)

Draw the data flow. At each arrow, ask: "What validation happens?"

```
[User]
  ↓ (TLS, CSRF, rate limit)
[Proxy]
  ↓ (auth, tenant check)
[Handler]
  ↓ (Zod validation)
[Service]
  ↓ (business logic)
[DB]
  ↑ (RLS)
```

---

## 5. STRIDE for this feature (5 min)

- **Spoofing:** Can someone pretend to be another user? ___
- **Tampering:** Can someone modify data they shouldn't? ___
- **Repudiation:** Can someone deny their actions? ___
- **Information disclosure:** Can someone read data they shouldn't? ___
- **Denial of service:** Can someone make it unavailable? ___
- **Elevation of privilege:** Can someone gain higher permissions? ___

---

## 6. SaaS-specific threats (3 min)

- **Billing bypass:** Can a free user access this? ___
- **Subscription hijacking:** Can I hijack someone's subscription? ___
- **Tenant leak:** Can Tenant A see Tenant B's data? ___
- **Rate limit bypass:** Can I bypass rate limits? ___
- **Refund fraud:** Can I refund and keep access? ___
- **Seat bypass:** Can I add members without paying? ___

---

## 7. Security properties required (3 min)

What MUST be true? If any can be violated, it's CRITICAL.

- [ ] [Property 1]
- [ ] [Property 2]
- [ ] [Property 3]

---

## 8. Open questions (3 min)

Things I don't know yet:
- [ ] [Question 1]
- [ ] [Question 2]
- [ ] [Question 3]

---

## Decision

- [ ] Safe to implement as designed
- [ ] Implement with changes: [list]
- [ ] Redesign required
- [ ] Needs security review before coding

---

## Notes

[Free-form notes]
