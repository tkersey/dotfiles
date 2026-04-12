# Email Security — DKIM, SPF, DMARC, and Beyond

Email is the #1 attack vector for phishing, and SaaS apps send lots of email
(transactional, marketing, notifications). Poor email authentication enables
attackers to impersonate your domain and phish your customers.

---

## The Three Pillars

### SPF (Sender Policy Framework)
Declares which mail servers are authorized to send email from your domain.

```dns
example.com. TXT "v=spf1 include:_spf.google.com include:sendgrid.net ~all"
```

**Flags:**
- `+all` — allow all (USELESS, never use)
- `~all` — soft fail (receivers may mark as suspicious)
- `-all` — hard fail (receivers should reject)
- `?all` — neutral

**Use `-all` in production.** `~all` during rollout to verify no legitimate mail is blocked.

**Common mistakes:**
- Too many `include:` (DNS lookup limit is 10)
- Forgetting to add Stripe/SendGrid/etc.
- Using `+all` "just to fix the issue"

### DKIM (DomainKeys Identified Mail)
Cryptographically signs emails. Receivers verify the signature against a public
key in DNS.

```dns
default._domainkey.example.com. TXT "v=DKIM1; k=rsa; p=MIGfMA0GCSq..."
```

**Best practice:**
- Key rotation every 6-12 months
- Multiple selectors for gradual rotation
- 2048-bit RSA minimum (1024-bit is weak)

### DMARC (Domain-based Message Authentication, Reporting, and Conformance)
Policy on what to do when SPF or DKIM fail. Also provides reporting.

```dns
_dmarc.example.com. TXT "v=DMARC1; p=reject; rua=mailto:dmarc@example.com; ruf=mailto:dmarc-failures@example.com; fo=1"
```

**Policies:**
- `p=none` — monitor only (start here)
- `p=quarantine` — mark suspicious
- `p=reject` — reject failing mail

### The DMARC Rollout
1. **Phase 1 (weeks 1-4):** `p=none`, collect reports, identify legitimate senders
2. **Phase 2 (weeks 5-8):** `p=quarantine; pct=25`, test on 25% of failing mail
3. **Phase 3 (weeks 9-12):** `p=quarantine; pct=100`, then `p=reject; pct=25`
4. **Phase 4 (week 13+):** `p=reject; pct=100`

---

## Subdomain Strategy

### Never send email from your apex
Don't send from `example.com`. Send from `mail.example.com` or similar.

**Why:**
- Isolates reputation (marketing bounces don't hurt transactional)
- Allows different SPF for different purposes
- Subdomain takeover of `mail.example.com` is contained

### Recommended structure
```
example.com           → Apex, no mail (p=reject to prevent spoofing)
mail.example.com      → Transactional (SendGrid, Resend)
news.example.com      → Marketing (Mailchimp)
notify.example.com    → Notifications
```

Each subdomain has its own SPF, DKIM, DMARC records.

### Apex DMARC for spoofing prevention
```dns
_dmarc.example.com. TXT "v=DMARC1; p=reject;"
```

If you don't send from apex, `p=reject` prevents anyone from spoofing it.

---

## Implementing with Popular Providers

### SendGrid
1. Add your sending domain in SendGrid dashboard
2. SendGrid provides CNAME records for DKIM + SPF
3. Add CNAMEs to your DNS
4. Verify in SendGrid
5. Add DMARC separately

### Resend (modern alternative)
```dns
# Resend provides:
mail._domainkey.example.com.   CNAME mail.resend.com.
send.example.com.              MX    feedback-smtp.us-east-1.amazonses.com. 10
send.example.com.              TXT   "v=spf1 include:amazonses.com ~all"
```

### Amazon SES
1. Verify domain in SES
2. Add provided DKIM records (3 CNAMEs)
3. Add MAIL FROM domain
4. Add custom SPF

---

## BIMI (Brand Indicators for Message Identification)

Display your logo in supporting email clients. Requires:
1. DMARC with `p=quarantine` or `p=reject`
2. Verified Mark Certificate (VMC) from a CA ($$)
3. Logo as SVG meeting specific requirements

```dns
default._bimi.example.com. TXT "v=BIMI1; l=https://example.com/logo.svg; a=https://example.com/vmc.pem"
```

**Mainly cosmetic**, but signals security maturity.

---

## Email Header Injection

### The attack
User input flows into email headers. Attacker injects newlines + headers.

```typescript
// VULNERABLE
const subject = `Password reset for ${user.email}`;
await sendMail({ to: user.email, subject, body });
```

If `user.email === "victim@example.com\r\nBcc: attacker@evil.com"`, the
attacker gets BCC'd on the password reset.

### The fix
Validate email format strictly (no newlines).

```typescript
function validateEmail(email: string): boolean {
  if (email.length > 254) return false;
  if (/[\r\n]/.test(email)) return false;
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
```

Better: use the email library's API properly (don't concatenate strings).

---

## Open Redirect in Transactional Emails

### The attack
Email contains `https://example.com/verify?token=xxx&redirect=https://evil.com`.
After verifying, app redirects to `evil.com`.

### The fix
Validate the redirect parameter against an allowlist, or ignore it entirely
for security-sensitive flows.

---

## Link Tracking and Security

### Problem
Marketing tools rewrite links for tracking: `https://track.example.com/click?url=https://example.com/reset&uid=xxx`.

For security-critical emails (password reset, MFA codes), this:
- Makes the link longer (worse UX)
- Exposes the token to the tracking service
- Can break the token if URL-encoded incorrectly
- Creates an open redirect surface

### Solution
Disable tracking for security emails:
```typescript
await sendMail({
  to: user.email,
  subject: 'Reset your password',
  body: template,
  trackingSettings: {
    clickTracking: { enable: false },  // CRITICAL for security emails
    openTracking: { enable: false },
  },
});
```

---

## Rate Limiting Email Sending

### Per-user send limits
Prevent email bombing (attacker signs up with victim's email, triggers many emails).

```typescript
const EMAIL_RATE_LIMITS = {
  password_reset: { max: 3, windowMinutes: 60 },
  verification: { max: 5, windowMinutes: 60 },
  notification: { max: 50, windowMinutes: 60 },
};

async function canSendEmail(email: string, type: EmailType): Promise<boolean> {
  const key = `email:${type}:${email}`;
  const count = await redis.incr(key);
  if (count === 1) await redis.expire(key, EMAIL_RATE_LIMITS[type].windowMinutes * 60);
  return count <= EMAIL_RATE_LIMITS[type].max;
}
```

### Global send rate
Prevent account compromise → mass mailing.

```typescript
const GLOBAL_DAILY_LIMIT = 100_000;
const sent = await redis.incr('email:global:' + today());
if (sent > GLOBAL_DAILY_LIMIT) {
  alertSecurityTeam('Global email limit exceeded');
  throw new Error('Rate limited');
}
```

---

## Anti-Spoofing for Customer Domains (ARC)

If your SaaS sends email on behalf of customers using their domain (SendGrid-
style), use ARC (Authenticated Received Chain) to maintain DKIM signatures
across forwarding.

Most SaaS don't need this, but it's critical for email infrastructure providers.

---

## Email as Attack Vector

### Phishing via your domain
If your SPF/DKIM/DMARC are weak, attackers can spoof your domain to phish
your customers. The attack works because:
1. Recipient sees "From: no-reply@acme.com"
2. Content mimics your real emails
3. Link goes to "acme-secure.com"
4. Customer enters credentials

**Defense:** Strict DMARC (`p=reject`) prevents most spoofing.

### Display name spoofing
`From: "Support <support@acme.com>"`
If the display name matches your brand but the email is `support@acme.com.evil.ru`,
users may not notice.

**Defense:** User training + brand indicator programs (BIMI).

### Reply-to hijacking
`From: noreply@acme.com, Reply-To: attacker@evil.com`
Replies go to attacker.

**Defense:** Validate Reply-To during email composition. Show it clearly in
the email preview.

---

## Email Audit Checklist

### DNS records
- [ ] SPF record exists with `-all` (strict)
- [ ] DKIM record exists with 2048-bit key
- [ ] DMARC record with `p=reject` (or `p=quarantine` minimum)
- [ ] DMARC reports going to monitored inbox
- [ ] Apex domain has `p=reject` (if not used for sending)
- [ ] Subdomain strategy documented (mail., news., notify.)

### Application
- [ ] Email addresses validated (no newlines, proper format)
- [ ] No header injection possible
- [ ] Transactional emails have click tracking DISABLED
- [ ] Rate limiting on password reset emails
- [ ] Rate limiting on verification emails
- [ ] Global daily send limit with alerts

### Providers
- [ ] Provider credentials rotated
- [ ] Provider webhooks signature-verified
- [ ] Provider access logs monitored
- [ ] Separate providers for transactional vs marketing

### Monitoring
- [ ] DMARC reports ingested and analyzed
- [ ] Alerts on unusual spike in bounces
- [ ] Alerts on failed SPF/DKIM
- [ ] Monitor for lookalike domain registrations

### Customer-facing
- [ ] Unsubscribe links work (CAN-SPAM)
- [ ] Physical address in footer (CAN-SPAM)
- [ ] GDPR consent for marketing
- [ ] Easy way to report phishing to your security team

---

## Tools

- **dmarcian.com** — free DMARC record generator + analyzer
- **mxtoolbox.com** — DNS record lookups, SPF/DKIM check
- **postmark DMARC reports** — free DMARC monitoring
- **valimail.com** — commercial DMARC management

---

## See Also

- [THIRD-PARTY.md](THIRD-PARTY.md) — email provider security
- [DNS-SECURITY.md](DNS-SECURITY.md)
- https://www.ietf.org/rfc/rfc7489.txt (DMARC spec)
