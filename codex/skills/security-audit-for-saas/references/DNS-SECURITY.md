# DNS Security

DNS is a critical attack surface that most SaaS teams ignore. DNS compromise
enables: subdomain takeover, phishing, certificate fraud, email spoofing,
traffic hijacking.

---

## The Top DNS Threats for SaaS

1. **Subdomain takeover** — attacker claims an abandoned CNAME
2. **DNS hijacking** — attacker controls DNS to redirect traffic
3. **DNS rebinding** — time-based attack to bypass same-origin policy
4. **Cache poisoning** — attacker injects false DNS responses
5. **Dangling DNS** — old records pointing to decommissioned infrastructure
6. **Zone transfer leaks** — attacker dumps entire DNS zone
7. **NS delegation hijacking** — attacker takes over a subdomain's nameservers

---

## Subdomain Takeover

### The attack
1. You create `blog.example.com` → `example.herokuapp.com`
2. You later abandon the Heroku app
3. The DNS CNAME remains
4. Attacker claims `example.herokuapp.com` on Heroku
5. Attacker now controls `blog.example.com` (serves their content, steals cookies)

### Common vulnerable services
- Heroku apps
- AWS S3 buckets
- Azure sites
- GitHub Pages
- Shopify stores
- Zendesk / Freshdesk
- Fastly
- Zendesk subdomains
- Various CDNs

### Detection
```bash
# Tools to find dangling CNAMEs
subjack -w subdomains.txt -t 100 -timeout 30
subzy run --targets subdomains.txt
```

### Prevention
- **Audit:** Quarterly review of all DNS records
- **Ownership:** Track which team owns which record
- **Deprovisioning checklist:** Remove DNS when removing the service
- **Automated checks:** CI job that tests all CNAMEs still resolve

---

## DNS Hijacking / Account Compromise

### The attack
Attacker compromises your registrar account → changes nameservers → redirects
all traffic.

**Recent examples:**
- Multiple crypto exchanges hit by registrar compromise
- GoDaddy customers targeted via social engineering

### Prevention

**Registrar security:**
- [ ] MFA enabled (U2F preferred, not SMS)
- [ ] Registry lock enabled (prevents unauthorized transfers)
- [ ] Unique, strong password
- [ ] Contact info is an alias, not personal email
- [ ] Separate account for DNS (not used for anything else)
- [ ] Multiple admins (bus factor + cross-check)

**Domain settings:**
- [ ] `clientTransferProhibited` status
- [ ] `clientDeleteProhibited` status
- [ ] `clientUpdateProhibited` status (if feasible)
- [ ] WHOIS privacy enabled

**Monitoring:**
- [ ] Daily check of WHOIS info
- [ ] Alert on DNS record changes
- [ ] Alert on nameserver changes

---

## DNS Rebinding (CORS/SOP Bypass)

### The attack
Attacker controls `evil.com`. Victim visits `evil.com`.
1. DNS resolves `evil.com` to attacker's IP (first resolution)
2. JavaScript fetches `evil.com/something`
3. Attacker serves response with short TTL
4. JavaScript makes second request; DNS re-resolves
5. DNS now returns `127.0.0.1` or internal IP
6. Browser thinks it's still same-origin, sends cookies
7. Attacker's JS now interacts with victim's localhost

### Prevention (defender side — websites shouldn't rely on this)
In applications, **validate the Host header** and **check origin** rather than
trusting "same-origin" for internal services.

```typescript
const ALLOWED_HOSTS = ['api.example.com', 'app.example.com'];

export function middleware(req: Request) {
  const host = req.headers.get('host');
  if (!ALLOWED_HOSTS.includes(host)) {
    return new Response('Invalid host', { status: 400 });
  }
}
```

### Prevention (SSRF context)
When fetching user-provided URLs, resolve the hostname and verify it's not
private BEFORE making the request. Also pin the resolved IP for the actual
connection (see Round 4 finding #2 — DNS rebinding TOCTOU).

```typescript
async function safeFetch(url: string) {
  const parsed = new URL(url);
  const { lookup } = await import('dns/promises');
  const addresses = await lookup(parsed.hostname, { all: true });

  for (const addr of addresses) {
    if (isPrivateIp(addr.address)) throw new Error('Private IP');
  }

  // Use the FIRST resolved IP directly to prevent rebinding
  const ip = addresses[0].address;
  return fetch(`https://${ip}${parsed.pathname}`, {
    headers: { Host: parsed.hostname }, // Preserve SNI/virtual host
    // ... careful with TLS (cert validation must use original hostname)
  });
}
```

This is tricky with TLS. Safer: validate twice, use short-lived resolution,
accept that DNS rebinding is a residual risk for webhook delivery.

---

## DNSSEC

DNSSEC cryptographically signs DNS records, preventing cache poisoning and
forged responses.

### Benefits
- Prevents DNS cache poisoning
- Prevents DNS response forgery
- Enables DANE (TLS certificates via DNS)
- Required for some compliance regimes

### Costs
- Setup complexity
- Key rotation required
- Not all registrars support it
- Misconfiguration can take your domain offline

### Recommendation
**Enable DNSSEC** for production domains. Use a registrar that manages the
keys (Cloudflare, Google Domains, AWS Route53). DIY DNSSEC is risky.

---

## CAA (Certification Authority Authorization)

CAA records declare which CAs are allowed to issue certificates for your
domain. Prevents misissuance.

```dns
example.com. CAA 0 issue "letsencrypt.org"
example.com. CAA 0 issue "digicert.com"
example.com. CAA 0 iodef "mailto:security@example.com"
```

**Effects:**
- Other CAs will refuse to issue certs for `example.com`
- Unauthorized issuance attempts report to `iodef` email

---

## Zone Transfer Leaks

### The attack
DNS zone transfers (AXFR) dump entire zone contents. If misconfigured, anyone
can enumerate all your subdomains.

### Test
```bash
dig AXFR example.com @ns1.example.com
```

If it returns data, you have a leak.

### Fix
Configure nameservers to only allow zone transfers from secondary
nameservers (not the public).

---

## Subdomain Enumeration (Attacker OSINT)

Attackers enumerate your subdomains to find:
- Internal apps accidentally exposed
- Staging/dev environments with weaker security
- Forgotten services with vulnerabilities

### Attacker tools
- `sublist3r`, `amass`, `subfinder`, `assetfinder`
- Certificate transparency logs (`crt.sh`)
- DNS brute-force with wordlists

### Defender response
1. **Know your subdomains** — inventory them before attackers do
2. **Minimize exposure** — don't create subdomains for internal tools
3. **Use subdomains for isolation** — different risk = different subdomain
4. **Monitor CT logs** — alert on new cert issuance for your domain

### Monitoring CT logs
```bash
# Use crt.sh API or similar
curl -s "https://crt.sh/?q=example.com&output=json" | jq '.[].name_value'
```

Set up a weekly job to detect new subdomains.

---

## DNS Provider Security

### Choosing a DNS provider
- **Cloudflare** — good default, DDoS protection, fast
- **Route53** — if you're on AWS
- **Google Cloud DNS** — if on GCP
- **Azure DNS** — if on Azure
- **NS1** — high-end, programmable
- **DNSimple** — developer-friendly

**Avoid:**
- Cheap registrars without security features
- Your hosting provider's free DNS (often weak)

### Provider security checklist
- [ ] MFA on account
- [ ] API keys rotated
- [ ] Audit logs available
- [ ] SLA for uptime
- [ ] Support responsiveness
- [ ] Anycast network (geographic resilience)

---

## DNS as Monitoring Signal

Anomalies in your DNS queries indicate attacks:

### Patterns to watch
- **Spike in NXDOMAIN** responses — attacker probing
- **Spike in queries for non-existent subdomains** — enumeration
- **Unusual query sources** — reconnaissance from new regions
- **Zone transfer attempts** — probing for misconfig

### Tools
- Cloudflare Analytics → DNS query patterns
- Passive DNS services (PDNS)
- Custom logging from authoritative servers

---

## The DNS Audit Checklist

### Registrar
- [ ] MFA enabled (U2F preferred)
- [ ] Registry lock enabled
- [ ] `clientTransferProhibited` status
- [ ] WHOIS privacy enabled
- [ ] Multiple admins

### Records
- [ ] All records inventoried and owned
- [ ] CNAMEs verified to resolve (no dangling)
- [ ] No zone transfer to public
- [ ] CAA records declare allowed CAs
- [ ] SPF, DKIM, DMARC for email (see EMAIL-SECURITY.md)
- [ ] DNSSEC enabled
- [ ] MX records accurate
- [ ] PTR (reverse DNS) matches

### Monitoring
- [ ] Daily check of WHOIS info
- [ ] Alert on DNS record changes
- [ ] Alert on nameserver changes
- [ ] CT log monitoring for new certs
- [ ] Weekly subdomain scan

### Audit
- [ ] Quarterly review of all DNS records
- [ ] Deprovisioning checklist includes DNS cleanup
- [ ] Subdomain takeover scan quarterly

---

## See Also

- [EMAIL-SECURITY.md](EMAIL-SECURITY.md) — SPF/DKIM/DMARC
- [WEB.md](WEB.md) — open redirect prevention
- [INFRASTRUCTURE.md](INFRASTRUCTURE.md)
- https://tools.ietf.org/html/rfc8659 (CAA)
- https://dnssec.net/ (DNSSEC resources)
