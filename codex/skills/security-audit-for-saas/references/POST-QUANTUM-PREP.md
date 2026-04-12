# Post-Quantum Cryptography Preparation

A sufficiently large quantum computer breaks all currently-deployed
public-key cryptography. This is not hypothetical — the NIST PQC
standards have landed and "harvest now, decrypt later" attacks are
already happening. Every SaaS storing long-lived sensitive data needs
a migration plan.

Related: [CRYPTO-FUNDAMENTALS.md](CRYPTO-FUNDAMENTALS.md),
[KEY-MANAGEMENT.md](KEY-MANAGEMENT.md), [SUPPLY-CHAIN-DEEP.md](SUPPLY-CHAIN-DEEP.md).

---

## What's at risk and what's not

### Broken by quantum (Shor's algorithm)

- RSA — any key size
- DSA, ECDSA, Ed25519 — all elliptic curve signatures
- ECDH, X25519 — all elliptic curve key exchange
- Diffie-Hellman (classic)
- Any scheme where security reduces to factoring or discrete log

### Not broken by quantum (but weaker)

- AES-256 — effectively halved to AES-128 security (Grover's algorithm).
  Still fine. AES-128 drops to ~2^64, which is concerning.
- SHA-256, SHA-3 — halved collision resistance. Still safe if you use
  256-bit output.
- HMAC — symmetric, safe.

**Rule:** symmetric crypto (AES, ChaCha, HMAC) is fine at 256-bit
keys. All public-key crypto needs migration.

---

## "Harvest now, decrypt later" (HNDL)

Attackers are currently **recording encrypted traffic** and storing
it. When quantum computers mature, they decrypt the stockpile. Data
with multi-year secrecy requirements is already exposed.

### Who should care today

If any of these apply, HNDL affects you:

- Customer data must remain confidential for >10 years (health, legal,
  IP, PII)
- You handle state secrets, defense, or critical infrastructure
- You have a regulatory obligation for long-term confidentiality
- Your threat model includes nation-state adversaries
- Your SaaS is a supply chain dependency for the above

If none apply, HNDL is less urgent — but you still need a migration
plan because the certificate ecosystem is moving.

---

## The NIST PQC standards (finalized)

As of 2024–2025, NIST has published FIPS standards:

| Standard | Algorithm | Purpose | Replaces |
|----------|-----------|---------|----------|
| FIPS 203 | ML-KEM (CRYSTALS-Kyber) | Key encapsulation | ECDH, RSA-KEM |
| FIPS 204 | ML-DSA (CRYSTALS-Dilithium) | Digital signatures | ECDSA, RSA sign |
| FIPS 205 | SLH-DSA (SPHINCS+) | Stateless hash sigs | Fallback signature |
| Draft | FN-DSA (Falcon) | Compact signatures | ECDSA (when size matters) |

Additional rounds are ongoing for code-based and isogeny-based
alternatives. Don't deploy those yet; stick with ML-KEM and ML-DSA.

### Key sizes and performance

| Algorithm | Public key | Signature/Ciphertext | Relative perf |
|-----------|-----------|----------------------|---------------|
| RSA-2048 | 256 B | 256 B | 1x baseline |
| Ed25519 | 32 B | 64 B | 3–5x faster than RSA |
| ML-KEM-768 | 1184 B | 1088 B | ~same as Ed25519 |
| ML-DSA-65 | 1952 B | 3309 B | ~2x slower than Ed25519 |
| SLH-DSA-128 | 32 B | 7856 B | 10–100x slower |

**Tradeoff:** PQ algorithms have much larger keys and signatures. This
matters for:
- TLS handshake (certificate chain size)
- JWT tokens (signature size)
- Smart card / HSM storage
- Mobile and IoT where bandwidth is scarce

---

## Hybrid schemes (the transition strategy)

Nobody wants to bet the farm on a new algorithm. **Hybrid** schemes
combine a classical algorithm (ECDH) with a PQ algorithm (ML-KEM),
deriving session keys from both. If either is broken, the other
holds.

### Hybrid key exchange

```
shared_secret = HKDF(ECDH_secret || MLKEM_secret)
```

The first is fast and proven; the second is quantum-resistant. Most
early PQ deployments use this pattern — Cloudflare, Google, Apple all
use hybrid TLS.

### Hybrid signatures

```
signature = ECDSA(msg) || MLDSA(msg)
verify = ECDSA_verify AND MLDSA_verify
```

Both must verify. Slower but safer during transition. CAs are moving
to hybrid certificates in 2026–2028.

---

## TLS and the PQ transition

### TLS 1.3 with ML-KEM

ML-KEM is approved for TLS 1.3. Chromium and Firefox shipped support
in 2024. Cloudflare enabled ML-KEM-768 globally. To check your TLS
stack:

```bash
openssl s_client -connect example.com:443 -groups X25519MLKEM768
```

If the handshake succeeds and `Negotiated group: X25519MLKEM768` shows
up, you're already doing hybrid PQ key exchange.

### Certificate roll

PQ certificates are not yet default. CAs are piloting them in 2025.
Expect production PQ cert issuance by 2027–2028. Plan for:

- Larger cert chains (3x–10x current size)
- HTTP/2 HPACK pressure
- Mobile data costs
- Hardware offload (TLS terminators may need upgrades)

### Signed Certificate Timestamps (SCT)

SCTs in CT logs are currently ECDSA. A PQ-SCT story is still being
defined. Expect churn here.

---

## Application-level migration targets

Inventory every place you use public-key crypto:

| Use case | Current algorithm | PQ target |
|----------|------------------|-----------|
| TLS (inbound) | ECDHE + ECDSA cert | Hybrid KEM + hybrid cert |
| TLS (outbound) | same | same |
| JWT signing | ES256, RS256, EdDSA | ML-DSA-65 or hybrid |
| Signed URLs | HMAC or ECDSA | HMAC unchanged; switch ECDSA |
| Webhook signatures | HMAC-SHA256 | unchanged |
| Software updates | ECDSA or Ed25519 | SLH-DSA (hash-based, conservative) |
| Package signing | PGP (RSA) or Ed25519 | ML-DSA or SLH-DSA |
| Secrets at rest | AES-256-GCM | unchanged |
| KMS envelope keys | RSA-OAEP wrap | ML-KEM wrap |
| SSH keys | Ed25519 | ML-DSA (when OpenSSH supports it) |
| VPN (IKEv2) | ECDH | Hybrid KEM |

**HMAC-based schemes are unaffected.** If you can reduce a use case to
HMAC (shared secret, not public key), you already have PQ security.

---

## Code-level impact

### Library readiness (2026)

- **BoringSSL** — ML-KEM-768, ML-DSA-65 support. Used by Chrome, Cloudflare.
- **OpenSSL 3.5+** — PQ support via providers. Still maturing.
- **libsodium** — no PQ as of 2026; use liboqs alongside.
- **liboqs** — reference library from Open Quantum Safe. Production
  ready for ML-KEM and ML-DSA.
- **Node.js `node:crypto`** — no direct PQ yet; use `@openquantumsafe/liboqs-js`.
- **Python `cryptography`** — no PQ yet; use `pqcrypto` package.
- **Go `crypto`** — ML-KEM in `crypto/mlkem` (Go 1.24+).
- **Rust `ring`** — no PQ yet. Use `pqc_kyber` or `ml-kem` crates.

### Crypto agility: the code pattern

You want your code to be **algorithm-agile** — switching from ECDSA to
ML-DSA should be a config change, not a rewrite.

Bad:
```rust
fn sign(key: &Ed25519Key, msg: &[u8]) -> [u8; 64] {
    ed25519_dalek::sign(key, msg)
}
```

Good:
```rust
trait Signer {
    fn sign(&self, msg: &[u8]) -> Vec<u8>;
    fn verify(&self, msg: &[u8], sig: &[u8]) -> bool;
    fn alg(&self) -> &'static str;
}
```

Include the algorithm identifier in **every artifact** you sign or
encrypt. Old artifacts can still be verified with the old algorithm;
new ones use the new.

```
signature = {
  alg: "ml-dsa-65",
  value: <bytes>,
  kid: "2026-key-1",
}
```

---

## JOSE / JWT considerations

The `alg` parameter in JWT headers is about to get crowded. Upcoming
values:

- `ML-DSA-44`, `ML-DSA-65`, `ML-DSA-87`
- `SLH-DSA-SHA2-128s`, `SLH-DSA-SHAKE-256f`
- Hybrid compositions still being standardized

**Action items:**
- Audit your JWT verification code for a strict `alg` allowlist.
  Rejecting unknown `alg` is mandatory to prevent algorithm confusion
  attacks. This is classic advice but becomes essential when algorithm
  churn increases.
- Plan for larger JWTs — ML-DSA signatures are 3309 bytes. Current
  JWTs averaging 1KB will 3–5x in size.
- Consider detached signatures or CBOR Web Tokens (CWT) for
  size-sensitive paths.

---

## Key management roll plan

### Dual-signing transition

1. **Generate PQ keys alongside classical keys.** Publish both in
   verification materials (JWKS, CT logs).
2. **Start dual-signing.** Every artifact is signed with both algorithms.
3. **Migrate verifiers.** Update all consuming code to accept either
   signature.
4. **Flip preference.** Start signing with PQ first, classical as
   fallback.
5. **Retire classical.** Once no verifier needs classical, stop
   signing with it.

Expect this process to take 12–24 months for a large ecosystem. Start
planning now.

### HSM considerations

Most HSMs (Gemalto, Thales, YubiHSM, CloudHSM) do not support PQ
algorithms as of 2026. Plan for:

- HSM firmware updates
- Key import from software-only PQ keys
- Dual-key operations during transition (one HSM per algorithm)
- Budget for HSM replacement

Cloud KMS:
- **AWS KMS** — PQ key types in preview (2026)
- **GCP KMS** — ML-KEM in alpha
- **Azure Key Vault** — roadmap only

---

## Auditable state

For audit purposes, keep records of:

1. **Crypto inventory** — every public-key use case, algorithm, key
   size, rotation schedule, PQ plan
2. **Long-lived confidential data** — what's encrypted, with what, how
   long it must remain secret
3. **Vendor PQ status** — which of your SaaS dependencies have PQ
   roadmaps
4. **Hybrid deployment metrics** — % of traffic using hybrid KEM, % of
   artifacts dual-signed
5. **Key expiry calendar** — when do classical keys expire, when do
   PQ keys start signing

SOC 2 and ISO 27001 auditors are starting to ask about PQ readiness.
Be ready to show a migration plan even if you haven't executed it yet.

---

## The threat model decision tree

```
Does your data need to remain confidential >10 years?
├── Yes → Start HNDL-defending now (hybrid KEM, upgrade long-term secrets)
└── No
    └── Does your threat model include nation states?
        ├── Yes → Same as above
        └── No
            └── Are you a supply chain dependency for critical infra?
                ├── Yes → Follow critical-infra PQ timeline
                └── No → Wait for ecosystem maturity, plan for 2027–2028 migration
```

Most SaaS are in the bottom branch. **Don't panic-migrate** — plan for
crypto agility, watch the ecosystem, migrate with it.

---

## Common mistakes in early PQ adoption

1. **Switching without hybrid.** ML-KEM has <5 years of real-world
   scrutiny vs ECDH's 20+. A novel attack could invalidate it. Hybrid
   hedges.
2. **Ignoring key/signature size.** A 3309-byte signature in a QR code
   or URL fragment is a product problem, not a security problem.
3. **Assuming HMAC is "done."** HMAC is fine; but the **key delivery**
   for HMAC (usually via asymmetric crypto) is not.
4. **Not auditing verification code.** Algorithm confusion attacks
   become more common during transitions.
5. **Forgetting software updates.** Update signing keys are
   long-lived; rolling them during a breach requires infrastructure
   most teams lack.
6. **Overlooking supply chain.** Your package manager, container
   registry, CI/CD signing all need PQ plans.

---

## Action checklist for a SaaS team

Immediate (0–3 months):
- [ ] Inventory every public-key use case
- [ ] Identify data with >10-year secrecy requirements
- [ ] Check TLS terminator PQ support (Cloudflare, AWS ELB, nginx)
- [ ] Audit JWT verification for strict `alg` allowlist
- [ ] Add crypto agility to new code (algorithm in artifact metadata)

Near term (3–12 months):
- [ ] Turn on hybrid TLS KEM where supported
- [ ] Start dual-signing critical artifacts (releases, updates)
- [ ] Update crypto libraries to PQ-capable versions
- [ ] Request PQ status from vendors (KMS, HSM, cert provider)
- [ ] Document PQ migration plan for audits

Medium term (1–3 years):
- [ ] Migrate JWT signing to ML-DSA or hybrid
- [ ] Migrate software update signing to SLH-DSA (conservative choice)
- [ ] Roll out PQ certificates as CAs offer them
- [ ] Upgrade HSMs or move to PQ-capable KMS
- [ ] Run end-to-end PQ handshake across all workloads

Long term (3–10 years):
- [ ] Retire classical public-key algorithms
- [ ] Monitor for PQ cryptanalysis advances
- [ ] Plan for the next transition (PQ algorithms may also fall)

The hardest lesson from SHA-1 and MD5 retirements: **crypto
transitions take far longer than you think**. Start now.
