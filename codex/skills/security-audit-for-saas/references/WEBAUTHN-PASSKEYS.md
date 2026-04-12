# WebAuthn & Passkeys — Phishing-Resistant Authentication

WebAuthn (FIDO2) is the first widely-deployed authentication method that
resists phishing, credential stuffing, and most common attacks. Passkeys are
WebAuthn credentials synced via Apple/Google/Microsoft account.

For SaaS, adoption of WebAuthn is the single highest-impact security
improvement you can make. It prevents:
- Password reuse compromises
- Phishing (even on fake domains)
- Credential stuffing from breaches
- SMS-based 2FA attacks
- MFA fatigue (push bombing)

---

## Why WebAuthn Beats Everything Else

| Attack | Password | TOTP | SMS | Push MFA | WebAuthn |
|--------|----------|------|-----|----------|----------|
| Phishing | ❌ | ❌ | ❌ | ❌ | ✅ Blocks |
| Credential stuffing | ❌ | Partial | Partial | Partial | ✅ Blocks |
| SIM swap | ✅ | ✅ | ❌ | ✅ | ✅ |
| MFA fatigue | ✅ | ✅ | ✅ | ❌ | ✅ |
| Man-in-the-middle | ❌ | ❌ | ❌ | ❌ | ✅ Blocks |
| Keylogger | ❌ | Partial | Partial | ✅ | ✅ |
| Server breach (password leaks) | ❌ | ✅ | ✅ | ✅ | ✅ |

WebAuthn blocks everything in the column.

---

## How WebAuthn Works (Simplified)

### Registration
1. User clicks "Add passkey"
2. Browser generates a **new** keypair bound to the current origin
3. Private key stays on device (or in secure enclave)
4. Public key sent to server
5. Server stores public key with user ID

### Authentication
1. User visits login
2. Server sends a challenge (random bytes)
3. Browser asks the device to sign the challenge
4. User authenticates to the device (biometric, PIN)
5. Device returns signed challenge
6. Server verifies signature with stored public key

**Critical property:** The signature is bound to the current domain. A phishing
site on `evil-acme.com` can't trick the authenticator into signing for
`acme.com`. This is the phishing resistance.

---

## Implementation

### Server-side (using @simplewebauthn/server)

```typescript
import {
  generateRegistrationOptions,
  verifyRegistrationResponse,
  generateAuthenticationOptions,
  verifyAuthenticationResponse,
} from '@simplewebauthn/server';

const rpName = 'Acme Corp';
const rpID = 'acme.com'; // The domain — CRITICAL for phishing resistance
const origin = `https://${rpID}`;

// Registration
export async function POST_register_start(req: Request) {
  const user = await requireAuth(req);

  const options = await generateRegistrationOptions({
    rpName,
    rpID,
    userID: Buffer.from(user.id),
    userName: user.email,
    attestationType: 'none', // Or 'indirect' for stronger verification
    authenticatorSelection: {
      residentKey: 'preferred',    // Prefer discoverable credentials (passkeys)
      userVerification: 'preferred',
      authenticatorAttachment: 'platform', // OR 'cross-platform' for hardware keys
    },
    excludeCredentials: user.authenticators.map(a => ({
      id: a.credentialID,
      type: 'public-key',
      transports: a.transports,
    })),
  });

  // Store challenge for verification
  await db.insert(webauthnChallenges).values({
    userId: user.id,
    challenge: options.challenge,
    type: 'registration',
    expiresAt: new Date(Date.now() + 5 * 60 * 1000),
  });

  return Response.json(options);
}

export async function POST_register_finish(req: Request) {
  const user = await requireAuth(req);
  const body = await req.json();

  const challenge = await db.query.webauthnChallenges.findFirst({
    where: and(
      eq(webauthnChallenges.userId, user.id),
      eq(webauthnChallenges.type, 'registration')
    ),
  });
  if (!challenge) return Response.json({ error: 'No challenge' }, { status: 400 });

  const verification = await verifyRegistrationResponse({
    response: body,
    expectedChallenge: challenge.challenge,
    expectedOrigin: origin,
    expectedRPID: rpID,
  });

  if (!verification.verified) {
    return Response.json({ error: 'Verification failed' }, { status: 400 });
  }

  const { registrationInfo } = verification;
  await db.insert(authenticators).values({
    userId: user.id,
    credentialID: registrationInfo.credentialID,
    credentialPublicKey: registrationInfo.credentialPublicKey,
    counter: registrationInfo.counter,
    transports: body.response.transports,
  });

  // Delete the used challenge
  await db.delete(webauthnChallenges).where(eq(webauthnChallenges.id, challenge.id));

  return Response.json({ verified: true });
}
```

### Authentication
```typescript
export async function POST_auth_start(req: Request) {
  const { email } = await req.json();
  const user = await db.query.users.findFirst({ where: eq(users.email, email) });

  // Return options even if user doesn't exist (prevents enumeration)
  const authenticators = user
    ? await db.query.authenticators.findMany({ where: eq(authenticators.userId, user.id) })
    : [];

  const options = await generateAuthenticationOptions({
    rpID,
    userVerification: 'preferred',
    allowCredentials: authenticators.map(a => ({
      id: a.credentialID,
      type: 'public-key',
      transports: a.transports,
    })),
  });

  await db.insert(webauthnChallenges).values({
    userId: user?.id,
    challenge: options.challenge,
    type: 'authentication',
    expiresAt: new Date(Date.now() + 5 * 60 * 1000),
  });

  return Response.json(options);
}

export async function POST_auth_finish(req: Request) {
  const body = await req.json();
  // ... verify challenge, find authenticator, verify signature
  const verification = await verifyAuthenticationResponse({
    response: body,
    expectedChallenge: challenge.challenge,
    expectedOrigin: origin,
    expectedRPID: rpID,
    authenticator: {
      credentialID: auth.credentialID,
      credentialPublicKey: auth.credentialPublicKey,
      counter: auth.counter,
    },
  });

  if (!verification.verified) return Response.json({ error: 'Bad signature' }, { status: 401 });

  // Update counter (detects cloned authenticators)
  if (verification.authenticationInfo.newCounter <= auth.counter) {
    // CRITICAL: potential cloned credential, alert security
    logger.error({ userId: auth.userId }, 'WebAuthn counter replay detected');
    return Response.json({ error: 'Cloned credential suspected' }, { status: 401 });
  }
  await db.update(authenticators)
    .set({ counter: verification.authenticationInfo.newCounter })
    .where(eq(authenticators.id, auth.id));

  // Create session
  const session = await createSession(auth.userId);
  return Response.json({ verified: true, sessionId: session.id });
}
```

---

## The Counter Rollback Attack

The WebAuthn spec includes a counter that increments on every use. Cloned
authenticators will have a desynced counter.

**Detection:**
```typescript
if (newCounter <= storedCounter) {
  // Either: (a) authenticator was cloned, or (b) counter is stuck at 0 (some implementations)
  if (newCounter === 0 && storedCounter === 0) {
    // OK — some devices don't implement counters
  } else {
    // CRITICAL: clone suspected
    revokeCredential(credentialID);
    notifyUser('Possible credential cloning detected on your account');
  }
}
```

---

## Passkeys vs Hardware Keys

**Passkeys:**
- Synced across Apple/Google/Microsoft devices
- User-friendly (biometric unlock)
- Moderate security (anyone who compromises the user's cloud can potentially get them)
- Best for consumer SaaS

**Hardware keys (YubiKey, etc):**
- Not synced
- Higher security (physical token required)
- Better for admin/privileged accounts
- Require backup keys (loss = lockout)

**Best practice:** Offer both. Regular users use passkeys. Admins use hardware keys.

---

## Migration Strategy

### Phase 1: Add WebAuthn as an option
- Users can add passkeys in settings
- Passwords still work
- Encourage but don't require

### Phase 2: Promote WebAuthn
- Passkey as primary on login page
- Password hidden behind "use password instead"
- Notifications to users with weak passwords

### Phase 3: Require WebAuthn for high-privilege accounts
- Admins required to use passkey/hardware key
- MFA fallback removed for admins
- Break-glass recovery with physical token

### Phase 4: Passwordless everywhere
- New accounts default to passkeys
- Legacy password accounts migrated
- Passwords only for account recovery

---

## The "What if they lose their device?" Problem

Recovery scenarios:
1. **Passkey synced to cloud:** User signs into new device with their Apple/Google account, passkeys appear
2. **Multiple passkeys registered:** User has phone + laptop, loses phone but laptop still works
3. **Hardware key lost:** User had backup hardware key, uses it; original is revoked
4. **Nothing works:** Account recovery flow — slower, more verification

Always require users to register AT LEAST 2 authenticators at signup.

---

## Common Mistakes

### 1. Wrong `rpID`
`rpID` must match the domain exactly. If you change domains (even subdomains),
passkeys break. Document this.

### 2. Forgetting the counter check
Cloned credentials can't be detected without counter verification.

### 3. Not handling `userVerification` failures
If the user fails biometric 3 times, the device locks and WebAuthn fails. Have
a good error message and fallback.

### 4. Enumeration on registration
`excludeCredentials` reveals if a user has already registered. For registration
pages linked from "sign up" (public), consider not providing `excludeCredentials`.

### 5. No fallback authenticator
If a user has only one passkey and loses it, they're locked out. Require 2+.

---

## Audit Checklist

- [ ] WebAuthn is available as an auth method
- [ ] `rpID` and `origin` match production domain
- [ ] Counter verification implemented
- [ ] Counter replay detection triggers alert
- [ ] Users must register 2+ authenticators
- [ ] Challenge storage has TTL (5-10 min)
- [ ] Challenge is deleted after use (no replay)
- [ ] Authentication endpoint constant-time (no user enumeration)
- [ ] Recovery flow exists and is tested
- [ ] Admin accounts REQUIRE WebAuthn (not optional)
- [ ] Hardware key support for highest-privilege accounts
- [ ] Passkey UX tested on iOS Safari, Chrome, Firefox, Edge

---

## See Also

- [AUTH.md](AUTH.md)
- [SESSION-MANAGEMENT.md](SESSION-MANAGEMENT.md)
- https://webauthn.guide/
- https://simplewebauthn.dev/
- https://passkeys.dev/
