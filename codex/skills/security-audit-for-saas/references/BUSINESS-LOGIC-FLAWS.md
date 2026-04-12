# Business Logic Flaws

The vulnerabilities that static analyzers can't find. These are bugs in how
the business operates, not in how the code is written. Every SaaS has them.

This file catalogs 40+ business logic flaws specific to SaaS with billing.

---

## Category 1: Payment & Billing Flaws

### BL-01: Free $0 Checkout
**Description:** User creates a checkout for $0 and receives the product.
**Attack:** Craft a Stripe checkout session with price ID of the free plan but
products of a paid plan.
**Detection:** Audit: does price match product in checkout handler?
**Fix:** Verify price matches expected catalog entry.

### BL-02: Price Parameter Tampering
**Description:** Client-side JavaScript sends price to backend; backend trusts it.
**Attack:** Modify request body to include lower price.
**Detection:** Grep route handlers for `body.amount`, `body.price`.
**Fix:** Prices server-side only.

### BL-03: Coupon Code Stacking
**Description:** Multiple coupons applied simultaneously exceed the maximum
discount.
**Attack:** Apply `SAVE20` + `FREESHIP` + `STUDENT` on the same order.
**Detection:** Audit coupon application logic: is there a max-one-coupon check?
**Fix:** Single coupon per order, or cumulative discount cap.

### BL-04: Referral Bonus Farming
**Description:** User refers themselves (via multiple accounts) to earn bonuses.
**Attack:** Create 50 accounts with different emails, refer self, claim bonuses.
**Detection:** Audit: is there anti-self-referral logic (IP, device, payment
method)?
**Fix:** Multi-signal anti-farming (device fingerprint, payment method, behavior).

### BL-05: Trial Reset via Email Alias
**Description:** Gmail `+tag` aliases or sub-addressing lets same person
repeatedly sign up for free trials.
**Attack:** `user@gmail.com`, `user+1@gmail.com`, `user+2@gmail.com` all get
separate trials.
**Detection:** Audit email normalization before uniqueness check.
**Fix:** Normalize email (strip Gmail dots and `+tags`) before dedup.

### BL-06: Pro-Rata Refund on Annual Plan
**Description:** User pays annually, cancels after 1 day, expects full refund
but system calculates 1/365 used.
**Attack/Bug:** User refunded wrong amount (too much or too little).
**Detection:** Test annual plan cancellation refund math.
**Fix:** Clear refund policy enforced in code. Document "no refund after 14
days" or similar.

### BL-07: Subscription Upgrade Exploit
**Description:** Upgrading from monthly to annual gives free trial.
**Attack:** Subscribe monthly, use for a month, "upgrade" to annual, get fresh
trial.
**Detection:** Test upgrade flows for trial re-triggering.
**Fix:** Upgrades inherit trial state; no fresh trial on change.

### BL-08: Chargeback Abuse
**Description:** User makes purchase, uses product, initiates chargeback.
**Attack:** Buy premium for 30 days, chargeback on day 29.
**Detection:** Not a detection issue; a process issue.
**Fix:** Dispute handling: lock account on chargeback, require support contact
to unlock. Track chargeback rate per user.

### BL-09: Bulk Credit Purchase Fraud
**Description:** Credit-based systems where credits are purchased in bulk can be
exploited via stolen credit cards.
**Attack:** Use stolen cards to buy credits, use credits immediately, original
cardholder disputes, you eat the loss.
**Detection:** Velocity checks on bulk credit purchases.
**Fix:** Flag large bulk purchases for manual review. Delay credit delivery
for new accounts.

### BL-10: Currency Manipulation
**Description:** Prices in different currencies can be inconsistent.
**Attack:** Switch to a weak currency for a cheaper price, then get value in
strong currency.
**Detection:** Test all supported currencies.
**Fix:** Currency is set at account level, not per-transaction. Don't allow
switching.

### BL-11: Tax Avoidance via Address Fraud
**Description:** User enters address in tax-free jurisdiction.
**Attack:** Fake address in Delaware (US tax-free state) to avoid sales tax.
**Detection:** Cross-check billing address with payment method country.
**Fix:** Tax calculated based on payment method country, not claimed address.

### BL-12: Invoice Metadata Manipulation
**Description:** Users can modify invoice description or line items via API.
**Attack:** Edit invoice to remove their company name, disrupt accounting.
**Detection:** Test invoice edit permissions.
**Fix:** Invoice fields are read-only after generation.

---

## Category 2: Identity & Access Flaws

### BL-13: Email Verification Skip
**Description:** Some flows (OAuth sign-in) don't require email verification,
others do.
**Attack:** Sign up via OAuth with an email you don't own; receive emails for
the legitimate user.
**Detection:** Check if OAuth flow verifies email matches IdP claim.
**Fix:** Verify email ownership regardless of signup method.

### BL-14: Account Pre-Registration
**Description:** An attacker registers an account with a target's email BEFORE
the target signs up. When target signs up, accounts merge, attacker has access.
**Attack:** Register `ceo@target-corp.com` before they use the service.
**Detection:** Check signup flow for account collision handling.
**Fix:** Require email verification before granting access. Pre-existing
accounts with unverified emails expire.

### BL-15: SSO Domain Takeover
**Description:** SSO auto-joins users to an org based on email domain.
**Attack:** Buy a subdomain like `acme.com.evil.com`, configure SSO, claim to be
Acme Corp users.
**Detection:** Check SSO provisioning logic.
**Fix:** Domain verification (TXT record, email round trip) before enabling
SSO.

### BL-16: Password Reset Token Reuse
**Description:** Password reset token isn't invalidated after use.
**Attack:** Reset password, then use the same token again to reset again.
**Detection:** Test if reset token is one-time-use.
**Fix:** Token invalidated on first use.

### BL-17: Magic Link Email Forwarding
**Description:** Magic links are often automatically forwarded by email clients
or shared.
**Attack:** User forwards confirmation email with magic link; recipient gains
access.
**Detection:** Review magic link lifecycle.
**Fix:** Bind magic link to browser session. Short expiry (5 min).

### BL-18: Impersonation Without Audit
**Description:** Admin impersonation feature has no audit or rate limit.
**Attack:** Malicious admin impersonates 1000 users to read their data.
**Detection:** Audit impersonation logging.
**Fix:** Every impersonation audited with justification. Rate limited.

### BL-19: Just-in-Time Provisioning Abuse
**Description:** SSO auto-creates users on first login.
**Attack:** Forge SAML assertion for `admin@target.com`, get auto-provisioned
as admin.
**Detection:** Check SSO auto-provisioning RBAC defaults.
**Fix:** Auto-provisioned users default to minimum role. Admin role requires
explicit grant.

### BL-20: Account Recovery Social Engineering
**Description:** Support can reset passwords or MFA based on "proof" like last
4 of card.
**Attack:** Attacker knows last 4 digits (from stolen card), calls support,
gets password reset.
**Detection:** Audit account recovery procedures.
**Fix:** Multi-factor recovery: require current device OR multiple verifications.

---

## Category 3: Feature Access Flaws

### BL-21: Team Plan Used as Individual
**Description:** Team plan is cheaper per-seat than individual but less
verification.
**Attack:** Buy team plan for 1 user, get team features at personal cost.
**Detection:** Compare team plan min seats vs pricing.
**Fix:** Minimum team size (e.g., 3 seats) for team plans.

### BL-22: Trial Feature Leakage
**Description:** Trial users have access to all features; expiry only blocks
some.
**Attack:** Use trial, extract data, export via endpoint not subject to trial
expiry.
**Detection:** Audit all features against trial expiry check.
**Fix:** Trial expiry gates all paid features consistently.

### BL-23: Beta Feature Flag Leak
**Description:** Beta features accessible via direct URL even without flag.
**Attack:** Find beta feature URL, access directly, bypass waitlist.
**Detection:** Audit feature flag enforcement.
**Fix:** Server-side check on every request, not client-side rendering.

### BL-24: Export Feature Ransom
**Description:** Free users can create data, paid users can export.
**Attack:** Create 100GB of data as free user, then refuse to upgrade until
discount is offered.
**Detection:** Not exploitable, but a business risk.
**Fix:** Export is free; usage is metered. Or: free tier has data size limits.

### BL-25: API Rate Limit vs UI Action
**Description:** API has strict rate limits but UI doesn't count against them.
**Attack:** Drive UI programmatically to bypass API limits.
**Detection:** Audit: same endpoint serves UI and API?
**Fix:** All code paths go through the same limiter.

### BL-26: Deletion Doesn't Cascade
**Description:** User deletes account, but backup, logs, or references retain
their data.
**Attack:** Not a direct attack, but a GDPR violation.
**Detection:** Full data mapping exercise.
**Fix:** Deletion sweep touches every table that references the user.

### BL-27: Shadow Data Retention
**Description:** Soft-delete keeps data "forever."
**Attack:** GDPR DSAR reveals data supposedly deleted.
**Detection:** Audit soft-delete vs hard-delete policies.
**Fix:** Hard delete after grace period (30 days). Document retention.

### BL-28: Public/Private Visibility Confusion
**Description:** Feature has multiple visibility modes (public, private, org).
Default mode is inconsistent.
**Attack:** Create private content, later discover it was public due to
default drift.
**Detection:** Audit all content types for visibility defaults.
**Fix:** Default to private. Public requires explicit opt-in with warning.

---

## Category 4: Workflow Flaws

### BL-29: State Machine Bypass
**Description:** Resource has state machine `draft → review → approved →
published`. Attacker skips `review`.
**Attack:** Modify `state` field directly via PATCH endpoint.
**Detection:** Audit state transitions for unchecked mutations.
**Fix:** State changes only via explicit transition functions with validation.

### BL-30: Concurrent Action Race
**Description:** Two concurrent actions that should be mutually exclusive both
succeed.
**Attack:** Approve AND deny the same item concurrently, end up in both states.
**Detection:** Concurrent test of mutual-exclusive actions.
**Fix:** Advisory lock or optimistic concurrency on state changes.

### BL-31: Approval Workflow Self-Approval
**Description:** User submits request, user (in admin role) approves it.
**Attack:** Admin submits expense report, approves it themselves.
**Detection:** Audit: does approver == submitter?
**Fix:** Submitter and approver must be different users.

### BL-32: 2-Person Rule Bypass
**Description:** Operation "requires 2 admin approvals" but the check counts
the same admin twice.
**Attack:** Admin approves, log out, log back in with same account, "approves"
again.
**Detection:** Audit 2-person logic.
**Fix:** Count distinct user IDs, not distinct sessions.

### BL-33: Expired Invitation Accepted
**Description:** Invitation has expiry but code doesn't check it.
**Attack:** Use an expired invitation.
**Detection:** Test expired invitation acceptance.
**Fix:** Check expiry on every use.

### BL-34: Invitation Recipient Change
**Description:** Invitation issued to `alice@example.com`, accepted by anyone
who knows the link.
**Attack:** Attacker intercepts email (or guesses link), accepts invitation,
joins victim's org.
**Detection:** Test invitation acceptance by different email.
**Fix:** Invitation binds to the expected email. Recipient must verify
ownership.

### BL-35: Pending Changes Auto-Apply
**Description:** Changes are saved as "pending" and auto-apply after timeout.
**Attack:** Make change, leave before approval, change applies after time.
**Detection:** Audit auto-apply logic.
**Fix:** Require explicit approval action. Timeout cancels, not applies.

---

## Category 5: Data Integrity Flaws

### BL-36: Counter Race Condition
**Description:** "Inventory" counter decremented after check passes.
**Attack:** Concurrent requests all pass "stock > 0" check, all decrement
stock, oversold.
**Detection:** Load test inventory decrement.
**Fix:** Atomic `UPDATE inventory SET count = count - 1 WHERE count > 0 AND id
= ?`

### BL-37: Float Precision Billing
**Description:** Money amounts in floating point.
**Attack:** Accumulate rounding errors over thousands of transactions.
**Detection:** Audit money types in DB schema.
**Fix:** Money in integer cents. Never floats.

### BL-38: Time Zone Inconsistency
**Description:** Billing period calculated in different time zones in different
code paths.
**Attack:** Operation at midnight UTC vs midnight local time gives different
results.
**Detection:** Audit time zone handling.
**Fix:** UTC everywhere. Display in user TZ only at the UI layer.

### BL-39: Leap Second / Leap Day Bugs
**Description:** Date math fails on Feb 29 or leap seconds.
**Attack:** Schedule recurring task on Feb 29; fails in non-leap years.
**Detection:** Test date arithmetic against edge dates.
**Fix:** Use date library that handles leaps correctly. Test Feb 29, Dec 31,
DST transitions.

### BL-40: Integer Overflow
**Description:** Counter overflows 2^31 or 2^53.
**Attack:** Create enough records to trigger overflow in counting.
**Detection:** Use BigInt for potentially-large counters.
**Fix:** 64-bit integers or BigInt for counts that can exceed 2B.

---

## Category 6: Trust Boundary Flaws

### BL-41: Webhook Event Replay
**Description:** Webhook from provider is retried; handler processes twice.
**Attack:** No attack needed — normal provider behavior.
**Detection:** Test webhook retry scenarios.
**Fix:** Event ID deduplication (see [IDEMPOTENCY.md](IDEMPOTENCY.md))

### BL-42: Cross-Provider Webhook Confusion
**Description:** Stripe and PayPal webhooks handled by different routes, but
internal code paths merge.
**Attack:** Send Stripe-formatted payload to PayPal webhook endpoint.
**Detection:** Audit webhook routing.
**Fix:** Provider-specific handlers with explicit validation.

### BL-43: API Client Version Assumption
**Description:** Backend assumes all clients are latest version.
**Attack:** Old client sends deprecated field interpretation; backend processes
wrongly.
**Detection:** Check for version pinning in API.
**Fix:** API version in URL or header; handlers are versioned.

### BL-44: Third-Party Callback Trust
**Description:** OAuth callback URL called by third party, handler trusts all
data in request.
**Attack:** Manually call callback URL with forged data.
**Detection:** Review OAuth callback validation.
**Fix:** Validate state parameter, nonce, exchange code for token via back
channel.

### BL-45: CDN Cache Poisoning via Header
**Description:** CDN caches based on path but passes through some headers.
**Attack:** Send request with malicious header that becomes part of cached
response.
**Detection:** Review CDN cache key configuration.
**Fix:** Explicit cache key excludes untrusted headers.

---

## How to Find Business Logic Flaws

### 1. Walk the money path
Trace every dollar. Money flows in (checkout, subscription), money flows out
(refunds, credits, payouts). Each arrow is a potential flaw.

### 2. Walk the state machine
Draw every resource's state machine. Check every transition for:
- Who can trigger it?
- What validation happens?
- What if it fails partway?
- What if it's triggered twice?
- What if two users trigger the same transition?

### 3. Ask "can I skip a step?"
For every multi-step flow (signup → verify → onboard, checkout → pay → fulfill,
request → review → approve), ask: can I skip a step?

### 4. Ask "can I duplicate an entity?"
For every uniqueness constraint (email, username, order number), ask: can I
make two?

### 5. Ask "can I do this without paying?"
For every paid feature, ask: can I access it for free?

### 6. Ask "can I do this as someone else?"
For every authenticated action, ask: can I do this on behalf of another user?

### 7. Look at provider behavior
Study how Stripe, PayPal, etc. behave. Their quirks (out-of-order webhooks,
retries, partial data) are your attack surface.

---

## Tools for Business Logic Testing

### Manual exploration
No tool replaces thinking. Walk through flows manually, asking "what if..."

### Burp Suite Intruder
Modify requests systematically to find validation gaps.

### Property-based testing
Define invariants (e.g., "sum of credits + sum of usages = current balance")
and test with random inputs.

### Fuzzing
For parsers and validators.

### Formal methods
For state machines. TLA+ or Alloy can prove invariants hold.

---

## The Big Question

Most business logic flaws boil down to: **"Did the developer test the
unhappy path?"**

Happy path: user does what they're supposed to do.
Unhappy path: user does something weird, unexpected, or malicious.

Most developers test the happy path thoroughly. Few test the unhappy path
systematically. Business logic flaws live in the unhappy path.

When auditing, spend 80% of your time on unhappy paths. That's where the bugs
are.

---

## See Also

- [ATTACK-SCENARIOS.md](ATTACK-SCENARIOS.md) — walk-throughs for many of these
- [BILLING.md](BILLING.md) — payment-specific logic
- [CREATIVITY-TRIGGERS.md](CREATIVITY-TRIGGERS.md) — how to find the unhappy
  paths
- [OPERATORS.md](OPERATORS.md) — cognitive tools for hunting logic bugs
