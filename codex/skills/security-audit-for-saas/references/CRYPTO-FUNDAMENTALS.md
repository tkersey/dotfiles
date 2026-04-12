# Cryptographic Fundamentals for SaaS

Cryptography is a minefield of tradeoffs, version pinning, and "don't roll
your own." This file is the SaaS engineer's guide to getting crypto right —
what to use, what to avoid, and what to audit.

---

## The First Rule

**Don't write crypto.** Use library primitives.

- `crypto` (Node.js built-in)
- `libsodium` / `tweetnacl` (curve25519, NaCl constructions)
- `@noble/curves`, `@noble/hashes` (modern, audited)
- `bcrypt`, `argon2`, `scrypt` (password hashing)
- `jose` (JWT/JWE/JWS)

**Never** reimplement AES, HMAC, SHA, or any primitive yourself.

---

## Password Hashing

### The Choice
Use one of: **argon2id** (best), **scrypt** (good), **bcrypt** (acceptable).
Never use MD5, SHA-1, SHA-256, SHA-512 for passwords.

### Argon2id (Recommended)
```typescript
import { hash, verify } from '@node-rs/argon2';

// Hash
const hashedPassword = await hash(password, {
  memoryCost: 19456,  // 19 MiB
  timeCost: 2,        // 2 iterations
  parallelism: 1,
});

// Verify
const isValid = await verify(hashedPassword, password);
```

**Parameter tuning:** OWASP recommends `memoryCost: 19456 KiB`, `timeCost: 2`.
Test on your hardware; target ~200ms per hash.

### Bcrypt (If you must)
```typescript
import { hash, compare } from 'bcrypt';

const hashedPassword = await hash(password, 12); // cost factor 12
const isValid = await compare(password, hashedPassword);
```

**Cost factor:** Target ~300ms per hash. Rule of thumb: cost 12 in 2024, cost 13+
in 2026+.

### Scrypt
```typescript
import { scrypt } from 'crypto';
// ... more setup required; see Node docs
```

Good but less common. If you have existing scrypt, don't migrate without reason.

### The Iteration Count Problem
Hash iteration counts must increase over time as CPUs get faster. Store the
cost factor alongside the hash:

```
$argon2id$v=19$m=19456,t=2,p=1$<salt>$<hash>
```

When a user logs in, check the cost. If it's below current target, re-hash on
login with new cost.

**Historical failure:** LastPass had users with 5,000 PBKDF2 iterations. Modern
recommendation is 600,000+. The low count enabled brute-force after the 2022
breach.

---

## Symmetric Encryption

### Choose AES-256-GCM

```typescript
import { createCipheriv, createDecipheriv, randomBytes } from 'crypto';

const KEY = Buffer.from(env.ENCRYPTION_KEY, 'hex'); // 32 bytes

function encrypt(plaintext: string): string {
  const iv = randomBytes(12); // 96 bits for GCM
  const cipher = createCipheriv('aes-256-gcm', KEY, iv);
  const encrypted = Buffer.concat([cipher.update(plaintext, 'utf8'), cipher.final()]);
  const authTag = cipher.getAuthTag();
  // Format: iv(12) + authTag(16) + ciphertext
  return Buffer.concat([iv, authTag, encrypted]).toString('base64');
}

function decrypt(ciphertext: string): string {
  const buf = Buffer.from(ciphertext, 'base64');
  const iv = buf.subarray(0, 12);
  const authTag = buf.subarray(12, 28);
  const encrypted = buf.subarray(28);
  const decipher = createDecipheriv('aes-256-gcm', KEY, iv);
  decipher.setAuthTag(authTag);
  return Buffer.concat([decipher.update(encrypted), decipher.final()]).toString('utf8');
}
```

### Critical: Never reuse (key, IV) pairs
For AES-GCM, reusing the same (key, IV) catastrophically breaks the cipher.
Always use a fresh random IV per encryption.

### Don't use AES-CBC or AES-ECB
- **CBC:** Vulnerable to padding oracle attacks without HMAC
- **ECB:** Identical plaintext blocks produce identical ciphertext (meme: the
  ECB penguin)
- **CTR:** Fine but no authentication
- **GCM:** Provides confidentiality AND authentication — the right choice

### Don't use RSA for encryption
RSA encryption has many footguns. Use ECIES or hybrid encryption (ECDH +
symmetric) instead.

---

## Asymmetric Encryption & Signatures

### Signatures: Ed25519 (preferred) or ECDSA P-256
```typescript
import { sign, verify } from '@noble/ed25519';

// Generate keypair
const privateKey = ed25519.utils.randomPrivateKey();
const publicKey = await ed25519.getPublicKeyAsync(privateKey);

// Sign
const signature = await ed25519.signAsync(message, privateKey);

// Verify
const isValid = await ed25519.verifyAsync(signature, message, publicKey);
```

**Why Ed25519:** Fast, side-channel resistant, smaller signatures, simpler API.

### RSA: If you must
- Minimum 2048 bits, prefer 3072 or 4096
- Use RSA-PSS for signatures, not PKCS#1 v1.5
- Use RSA-OAEP for encryption, not PKCS#1 v1.5
- Never generate below 2048 bits

### ECDH for key exchange
```typescript
// Curve25519 (fastest, simplest)
import { x25519 } from '@noble/curves/ed25519';

const aliceSecret = randomBytes(32);
const alicePublic = x25519.getPublicKey(aliceSecret);

const bobSecret = randomBytes(32);
const bobPublic = x25519.getPublicKey(bobSecret);

// Both compute the same shared secret
const shared1 = x25519.getSharedSecret(aliceSecret, bobPublic);
const shared2 = x25519.getSharedSecret(bobSecret, alicePublic);
// shared1 === shared2

// Use HKDF to derive encryption keys from the shared secret
```

---

## Hashing

### SHA-256 (default)
```typescript
import { createHash } from 'crypto';

const hash = createHash('sha256').update(data).digest('hex');
```

### SHA-3 (alternative)
Similar security to SHA-256 but different construction. Use if you need
diversity for domain separation.

### BLAKE3 (faster)
```typescript
import { blake3 } from '@noble/hashes/blake3';
const hash = blake3(data);
```

BLAKE3 is faster than SHA-256 and parallelizable. Use for high-throughput
hashing.

### Never use for security
- MD5 (broken)
- SHA-1 (broken)
- Unsalted hashes for passwords

---

## HMAC

### The Pattern
```typescript
import { createHmac } from 'crypto';

function hmacSign(message: string, secret: string): string {
  return createHmac('sha256', secret).update(message).digest('hex');
}

function hmacVerify(message: string, signature: string, secret: string): boolean {
  const expected = hmacSign(message, secret);
  return timingSafeCompare(expected, signature);
}
```

### Key sizes
HMAC key should be at least as long as the hash output:
- HMAC-SHA256 → 32+ byte key
- HMAC-SHA512 → 64+ byte key

### Never use MD5 or SHA-1 in HMAC
Even though HMAC-MD5 and HMAC-SHA1 aren't broken (HMAC resists collisions
better than the underlying hash), use HMAC-SHA256 minimum for new work.

---

## Key Derivation

### HKDF (for deriving keys from keys)
```typescript
import { hkdfSync } from 'crypto';

const derivedKey = hkdfSync(
  'sha256',
  sourceKey,      // source key material (e.g., ECDH output)
  salt,           // random salt
  info,           // context string (domain separation)
  32              // output length in bytes
);
```

**Use cases:** Deriving encryption keys from ECDH shared secrets, deriving
subkeys from a master key.

### PBKDF2 (don't use for passwords in new code)
Still OK for legacy but argon2id is strictly better for passwords.

### scrypt / argon2 (for passwords or password-like inputs)
See password hashing section.

---

## Random Number Generation

### Cryptographically secure random
```typescript
import { randomBytes, randomUUID } from 'crypto';

// Random bytes
const key = randomBytes(32);

// Random UUID (v4)
const uuid = randomUUID();

// Random int in range
const randomInt = crypto.randomInt(0, 100); // [0, 100)
```

### Never use Math.random() for security
`Math.random()` is predictable and not cryptographically secure.

### Modulo bias
When generating random numbers in a range, watch for modulo bias:
```typescript
// BAD — modulo bias
const index = randomBytes(1)[0] % 26; // 256 % 26 != 0 → uneven distribution

// GOOD — use crypto.randomInt (handles bias correctly)
const index = crypto.randomInt(0, 26);

// OR — rejection sampling
function secureRandomIndex(max: number): number {
  const mask = Math.pow(2, Math.ceil(Math.log2(max))) - 1;
  while (true) {
    const n = randomBytes(1)[0] & mask;
    if (n < max) return n;
  }
}
```

---

## JWT Best Practices

### Use a good library
- `jose` (modern, TypeScript, audited)
- `jsonwebtoken` (old but widely used)

### Always use `verify`, never `decode`
```typescript
// BAD
const payload = jwt.decode(token); // No signature check!

// GOOD
const payload = await jwt.verify(token, publicKey, {
  algorithms: ['RS256'],          // Lock to specific algorithm
  issuer: 'https://auth.example.com',
  audience: 'https://api.example.com',
  maxTokenAge: '1h',
});
```

### Lock the algorithm
```typescript
// NEVER use the "any algorithm" fallback
const payload = await jwt.verify(token, key, {
  algorithms: ['RS256'], // Explicit list
});
```

**Why:** `alg: none` attack, RS256-to-HS256 confusion attack, `kid` header
manipulation.

### Set short expiry
```typescript
const token = await jwt.sign({ sub: userId }, privateKey, {
  algorithm: 'RS256',
  expiresIn: '1h',     // Access token: 1 hour max
  issuer: 'https://auth.example.com',
  audience: 'https://api.example.com',
});
```

### Refresh tokens in DB, not JWT
JWTs can't be revoked. Use short-lived JWT + long-lived refresh token (stored
in DB).

---

## Secret Rotation

### The Principle
Every key has a rotation schedule. When you rotate:
1. Generate new key
2. Deploy new key alongside old
3. Verify new key works
4. Revoke old key
5. Clean up old key references

### The Overlap Period
For keys used to sign outgoing data (JWTs, HMAC), you need an overlap period
where both old and new keys verify:

```typescript
const keys = [
  { id: 'key-2026-04', key: NEW_KEY, active: true },
  { id: 'key-2026-01', key: OLD_KEY, active: false }, // Still verify, don't sign
];

function signJwt(payload: object): string {
  const activeKey = keys.find(k => k.active);
  return jwt.sign(payload, activeKey.key, { keyid: activeKey.id });
}

function verifyJwt(token: string): object {
  const decoded = jwt.decode(token, { complete: true });
  const key = keys.find(k => k.id === decoded.header.kid);
  if (!key) throw new Error('Unknown key');
  return jwt.verify(token, key.key);
}
```

### Rotation Schedule
- JWT signing keys: quarterly
- API keys: annually (or on demand)
- Database passwords: quarterly
- OAuth client secrets: annually
- Service-to-service tokens: monthly (automated)

---

## Key Storage

### Never in source code
Keys go in environment variables or secret managers.

### Environment variables
OK for simple cases. Use a good secret manager in production.

### Secret managers
- AWS Secrets Manager, Azure Key Vault, GCP Secret Manager
- HashiCorp Vault
- Vercel/Netlify env vars (encrypted at rest)

### Hardware Security Modules (HSMs)
For high-value keys (root signing keys, CA keys). Use AWS KMS, GCP Cloud KMS,
or dedicated HSMs.

### Key loading
```typescript
// At startup, load keys from secret manager
const keys = await loadKeysFromVault();

// Never log keys
console.log('Loaded key:', keys.encryptionKey.substring(0, 4) + '...'); // Only prefix
```

---

## TLS / HTTPS

### Minimum TLS 1.2
TLS 1.0 and 1.1 are deprecated (PCI-DSS requires 1.2+).
TLS 1.3 is preferred.

### Certificate Validation
```typescript
// Default: Node verifies certificates
const response = await fetch('https://api.example.com');

// NEVER disable verification (except maybe local dev)
const response = await fetch('https://api.example.com', {
  // agent: new https.Agent({ rejectUnauthorized: false }) // NEVER IN PROD
});
```

### HSTS
```typescript
response.headers.set(
  'Strict-Transport-Security',
  'max-age=31536000; includeSubDomains; preload'
);
```

### Certificate Pinning
Pin certificates for critical API calls (OAuth, payment):
```typescript
const agent = new https.Agent({
  checkServerIdentity: (host, cert) => {
    if (cert.fingerprint256 !== EXPECTED_FINGERPRINT) {
      return new Error('Certificate pinning failure');
    }
  },
});
```

**Tradeoff:** Breaks when the provider rotates certs. Have a rotation plan.

---

## Common Cryptographic Mistakes

### 1. Fixed IV / nonce reuse
```typescript
// BAD
const iv = Buffer.alloc(16); // All zeros
const cipher = createCipheriv('aes-256-cbc', key, iv);

// GOOD
const iv = randomBytes(16);
```

### 2. ECB mode
```typescript
// BAD
createCipheriv('aes-256-ecb', key, null);

// GOOD
createCipheriv('aes-256-gcm', key, randomBytes(12));
```

### 3. Non-timing-safe comparison
See [TIMING-SAFE.md](TIMING-SAFE.md).

### 4. Short keys
- AES: 256 bits minimum (for long-term storage)
- RSA: 2048 bits minimum, prefer 3072+
- ECC: 256 bits (P-256) minimum

### 5. Weak random sources
```typescript
// BAD
const token = Math.random().toString(36);

// GOOD
const token = randomBytes(32).toString('base64url');
```

### 6. Storing passwords reversibly
Never encrypt passwords. Always hash.

### 7. Not using KDF
If you derive keys from a user-chosen password, use PBKDF2/scrypt/argon2.
Never use SHA-256 directly.

### 8. Custom crypto
If the audit findings include "custom HMAC implementation," it's a bug. Use
`crypto.createHmac`.

### 9. Truncating crypto outputs
```typescript
// BAD — birthday attack at 2^32 operations
const fingerprint = sha256(data).substring(0, 8);

// GOOD — full output
const fingerprint = sha256(data);
```

### 10. Reusing keys across contexts
The same key should not be used for both encryption and signing. Use domain
separation via HKDF:
```typescript
const encKey = hkdf(masterKey, 'encryption', 32);
const signKey = hkdf(masterKey, 'signing', 32);
```

---

## Cryptographic Agility

Design so crypto primitives can be swapped:

```typescript
// Metadata: which algorithm was used
const encrypted = {
  version: 'v2',
  algorithm: 'aes-256-gcm',
  kid: 'key-2026-04',
  iv: iv.toString('hex'),
  tag: authTag.toString('hex'),
  ct: ciphertext.toString('hex'),
};
```

When you need to upgrade (e.g., from AES-CBC to AES-GCM, or from PBKDF2 to
Argon2), you can handle both during the transition.

---

## Audit Checklist

### Libraries
- [ ] No custom crypto implementations
- [ ] Libraries are audited and actively maintained
- [ ] Library versions are pinned

### Algorithms
- [ ] Passwords hashed with argon2id, scrypt, or bcrypt
- [ ] Symmetric encryption uses AES-256-GCM (not ECB, not CBC without HMAC)
- [ ] Signatures use Ed25519 or RSA-PSS (not RSA-PKCS#1 v1.5)
- [ ] Hashing uses SHA-256 or better (not MD5, SHA-1)
- [ ] HMAC uses SHA-256 or better

### Keys
- [ ] Keys stored in secret manager, not source code
- [ ] Rotation schedule documented
- [ ] Key loading logs prefix only, never full key
- [ ] Different keys for different purposes (encryption vs signing vs HMAC)
- [ ] Key sizes are adequate (AES-256, RSA-2048+, ECC-256+)

### Random
- [ ] All random values use crypto.randomBytes or crypto.randomUUID
- [ ] No Math.random() for security purposes
- [ ] Modulo bias handled (use crypto.randomInt)

### JWT
- [ ] Algorithm explicitly locked (no `alg: none` possible)
- [ ] Expiry enforced
- [ ] Issuer and audience validated
- [ ] Using `verify`, not `decode`, for security decisions

### TLS
- [ ] TLS 1.2 minimum, prefer 1.3
- [ ] Certificate validation enabled everywhere
- [ ] HSTS header set
- [ ] Certificate pinning for critical providers (where feasible)

### Rotation
- [ ] Rotation plan documented
- [ ] Overlap period for signing keys
- [ ] Old key cleanup
- [ ] Audit log on rotation events

---

## See Also

- [TIMING-SAFE.md](TIMING-SAFE.md) — constant-time comparison
- [KEY-MANAGEMENT.md](KEY-MANAGEMENT.md) — secret management
- [AUTH.md](AUTH.md) — authentication patterns
- https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
