# Supply Chain Security — Deep Dive

Your code is <10% of what runs in production. The other 90% is dependencies,
build tools, CI/CD, deployment platforms, and third-party services. Each is
a supply chain attack surface.

---

## The Supply Chain Layers

```
Source code (you)
  ↓
Dependencies (npm, pypi, etc.)
  ↓
Build tools (bundlers, compilers, linters)
  ↓
CI/CD pipeline (GitHub Actions, CircleCI)
  ↓
Build artifacts (Docker images, static files)
  ↓
Deployment platform (Vercel, AWS, etc.)
  ↓
Runtime environment (Node, Deno, Python)
  ↓
OS / container base
  ↓
Kernel
  ↓
Hardware
```

At every layer, a compromise affects everything downstream.

---

## Direct Dependencies

### The problem
Your `package.json` probably lists 50-200 direct dependencies. Each has its
own dependencies. Transitive total: 500-5000 packages. Each is written by
strangers.

### Mitigations

**1. Minimize dependencies**
- Do you really need lodash? (ES6 covers most uses)
- Do you really need moment? (Date-fns is smaller)
- Can you copy the 10 lines you need?

**2. Pin versions**
```json
{
  "dependencies": {
    "stripe": "14.10.0"  // Not "^14.10.0" which allows minor bumps
  }
}
```

**3. Use lock files in CI**
- `npm ci` (not `npm install`)
- `pnpm install --frozen-lockfile`
- `yarn install --immutable`

**4. Hash-pin critical deps**
```json
{
  "dependencies": {
    "stripe": "14.10.0",
    "@prisma/client": "5.7.1 #sha256:abc123..."
  }
}
```

**5. Audit regularly**
```bash
npm audit --audit-level=high
pnpm audit --audit-level=high
cargo audit
pip-audit
```

---

## Typosquatting Defense

**Attack:** Malicious package with name close to legitimate (`reqeust` for
`request`, `cross-env.js` for `cross-env`).

**Defense:**
- Copy-paste package names from official docs, not from memory
- Use Socket.dev or similar to flag suspicious packages
- Review `package.json` diffs in PRs manually

### The checklist for new dependencies
Before adding a new dependency:
1. Who maintains it? (GitHub profile, activity)
2. How many downloads? (weekly)
3. Last updated? (active or abandoned)
4. Dependencies? (transitive risk)
5. Known CVEs?
6. Does it do what you need, or more?
7. Can you read the source in 30 min?

---

## Dependency Confusion

**Attack:** Your internal package `@company/internal-utils` is registered on
public npm by attacker with a higher version. Package manager fetches the
malicious public version.

**Defense:**
- **Scope registration:** register `@company/*` on public npm (even if unpublished), preventing attacker registration
- **Private registry:** use a private npm registry with scoped package resolution
- **Explicit registry:** `.npmrc` with scope-specific registry URLs

```ini
# .npmrc
@company:registry=https://npm.company.internal/
```

---

## Malicious Postinstall Scripts

**Attack:** Package includes `postinstall` script that runs on `npm install`.
The script exfiltrates env vars, `~/.ssh`, etc.

**Defense:**

**Global disable:**
```bash
npm config set ignore-scripts true
```

Then enable per-package only when needed (native extensions, etc.).

**Audit postinstall scripts:**
```bash
# List packages with postinstall
npm ls --parseable --depth=999 | xargs -I {} sh -c 'node -e "const pkg = require(\"{}/package.json\"); if (pkg.scripts && pkg.scripts.postinstall) console.log(pkg.name + \": \" + pkg.scripts.postinstall)"'
```

---

## SBOM (Software Bill of Materials)

An SBOM is a machine-readable list of every component in your software.
Required by EO 14028 for US federal contractors, increasingly required by
customers.

### Formats
- **CycloneDX** — OWASP standard
- **SPDX** — Linux Foundation standard

### Generation
```bash
# Node.js
npx @cyclonedx/cyclonedx-npm --output-file sbom.json

# Python
cyclonedx-py -r -o sbom.json

# Go
cyclonedx-gomod mod -o sbom.json

# Rust
cargo-cyclonedx --output-cdx
```

### Publishing
- Include in release artifacts
- Attach to Docker image
- Publish to security dashboard
- Share with customers on request

---

## Sigstore / Cosign — Signing Everything

Sigstore (sigstore.dev) provides free cryptographic signing for software
artifacts. Proves: "this artifact was built from this source by this
identity."

### Signing container images
```bash
# Sign
cosign sign --yes ghcr.io/company/app:v1.2.3

# Verify
cosign verify ghcr.io/company/app:v1.2.3 \
  --certificate-identity-regexp='https://github.com/company/.*' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com'
```

### Signing arbitrary artifacts
```bash
# Sign a tarball
cosign sign-blob --yes myapp.tar.gz > myapp.tar.gz.sig

# Verify
cosign verify-blob myapp.tar.gz \
  --signature myapp.tar.gz.sig \
  --certificate-identity-regexp='...' \
  --certificate-oidc-issuer='...'
```

### The keyless flow
Sigstore uses short-lived certificates tied to OIDC identity (GitHub Actions,
GitLab, etc.). No private keys to manage — the CI job's identity IS the
signing authority.

---

## SLSA (Supply-chain Levels for Software Artifacts)

SLSA is a security framework for supply chain. 4 levels:

- **Level 1:** Build is automated, metadata captured
- **Level 2:** Version controlled, authenticated builds
- **Level 3:** Hardened build platform, non-falsifiable provenance
- **Level 4:** Two-person review, hermetic builds, reproducible

**Starting point:** Get to Level 2 with GitHub Actions + artifact attestation.

```yaml
# .github/workflows/build.yml
permissions:
  contents: read
  id-token: write
  attestations: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pnpm install --frozen-lockfile
      - run: pnpm build
      - uses: actions/attest-build-provenance@v1
        with:
          subject-path: 'dist/**'
```

---

## Reproducible Builds

The same source should produce the same binary every time. Deviations indicate
compromise.

### Obstacles to reproducibility
- Build timestamps in artifacts
- Random ordering of object files
- Username/hostname in compiler output
- Non-deterministic optimizations
- Timezone-dependent output

### Tools
- `reprotest` (Debian) — automated reproducibility testing
- `diffoscope` — compares builds byte-by-byte
- Buildpacks with pinned base images

---

## Private Package Distribution

### The problem
Internal packages need to be shared between projects without exposing source.

### Options
1. **Private npm registry:** Verdaccio (self-hosted), npm Pro (hosted)
2. **GitHub Packages:** integrated with GitHub
3. **Git submodules:** direct git dependencies
4. **Yarn/pnpm workspaces:** monorepo-native

### Access control
- Minimum necessary permissions
- Per-package access tokens
- Rotation schedule
- Audit logs on access

---

## Vendored Dependencies

Instead of fetching from registry at build time, commit the dependencies to
your repo.

**Pros:**
- No network dependency during build
- Bit-for-bit reproducible
- Immune to registry outages or package deletion
- Review dependency changes in PRs

**Cons:**
- Repo size grows
- Updates require more work
- Tooling expects registry

**When to use:** Mission-critical systems where supply chain is a top
concern.

**Tools:**
- `pnpm` with `node-linker=hoisted`
- `npm pack` + local install
- `vendir` (Carvel) for generic vendoring

---

## CI/CD Hardening

### GitHub Actions
```yaml
permissions:
  contents: read  # Default minimum
  # Add only what's needed per job

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4  # Pin with SHA, not tag
      # OR: - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683

      - name: Install
        run: npm ci  # Not npm install
```

### Secret management
- `pull_request_target` only if you MUST use secrets on PRs
- Fork PRs get NO secrets
- Scope secrets to specific workflows
- Rotate quarterly

### OIDC to cloud
```yaml
permissions:
  id-token: write  # For OIDC
  contents: read

jobs:
  deploy:
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/deploy
          aws-region: us-east-1
      # No long-lived AWS credentials needed
```

---

## Dependency Review Automation

### Dependabot
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: 'npm'
    directory: '/'
    schedule:
      interval: 'weekly'
    groups:
      dev-dependencies:
        dependency-type: 'development'
      production-dependencies:
        dependency-type: 'production'
```

### Socket.dev
Scans PRs for supply chain risks:
- New typosquatting packages
- Packages with install scripts
- Packages with unusual permissions

### Snyk / GitHub Advanced Security
Commercial vulnerability scanning with remediation suggestions.

---

## The Compromise Recovery Playbook

If you suspect a supply chain compromise:

1. **Identify the compromised package** (CVE, vendor notification, internal discovery)
2. **Assess impact**: Was it used in production? Which services?
3. **Rotate secrets** that may have been exposed (CI secrets, API keys, etc.)
4. **Rollback** deployments that used the compromised version
5. **Scan logs** for exfiltration attempts
6. **Notify customers** if data exposure is possible
7. **Post-mortem**: How did this package get in? How do we prevent next time?

---

## Audit Checklist

### Dependencies
- [ ] Minimized dependency count
- [ ] Pinned versions (no `^` or `~`)
- [ ] Lock files committed
- [ ] `npm ci` (not `install`) in CI
- [ ] `postinstall` disabled globally
- [ ] Dependency scanning in CI (Snyk, Socket, Dependabot)
- [ ] SBOM generated on every build

### Build
- [ ] Build is reproducible
- [ ] Build artifacts signed with Sigstore
- [ ] SLSA Level 2 or higher
- [ ] Build runs in isolated environment (no secrets unless needed)

### CI/CD
- [ ] Minimum permissions per job
- [ ] Actions pinned to SHA (not tag)
- [ ] OIDC for cloud access (no long-lived creds)
- [ ] Fork PRs have no secrets
- [ ] Secrets rotated quarterly

### Distribution
- [ ] Private packages use private registry
- [ ] Scope names reserved on public registries
- [ ] Access tokens rotated
- [ ] Audit logs on package access

### Monitoring
- [ ] Alert on new dependencies in PRs
- [ ] Alert on version bumps >N points
- [ ] Alert on unusual install times (indicator of postinstall attack)

---

## See Also

- [THIRD-PARTY.md](THIRD-PARTY.md)
- [INFRASTRUCTURE.md](INFRASTRUCTURE.md)
- [gh-actions/references/SECURITY-CORE.md](../../gh-actions/references/SECURITY-CORE.md)
- https://slsa.dev/
- https://sigstore.dev/
- https://www.cisa.gov/sbom
