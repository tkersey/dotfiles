# Domain Checklists

Use these as starting points. Tailor the audit to the stack, threat model, and user-provided scope.

## Security

### Checklist

- [ ] Input validation and output encoding
- [ ] SQL/NoSQL/LDAP/template injection prevention
- [ ] XSS and unsafe DOM rendering
- [ ] CSRF protection for state-changing browser actions
- [ ] Authentication and authorization checks on every sensitive path
- [ ] Multi-tenant isolation and ownership checks
- [ ] Secrets management and credential exposure
- [ ] Path traversal, arbitrary file read/write, and archive extraction safety
- [ ] Command injection and unsafe subprocess calls
- [ ] SSRF and unsafe outbound fetches
- [ ] Deserialization and parser risks
- [ ] Error message information leakage
- [ ] Crypto, token, session, and cookie settings
- [ ] Dependency vulnerabilities and risky transitive packages

### Quick Grep

```bash
# Rust panics / unsafe error paths
rg -n "unwrap\(\)|expect\(|panic!|unreachable!" --type rust

# Code injection primitives
rg -n "eval\(|exec\(|Function\(|child_process|subprocess|os\.system|popen" --type js --type ts --type py

# DOM injection
rg -n "innerHTML|outerHTML|dangerouslySetInnerHTML|v-html" --type ts --type tsx --type js --type jsx --type vue

# Hardcoded secrets
rg -n "password|secret|api_key|private_key|token|bearer" --type-not lock -i
rg -n "sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{36}|xox[baprs]-" --type-not lock

# SQL construction
rg -n "format!.*SELECT|SELECT.*\{|execute.*\+|query.*\+" --type rust --type js --type ts
rg -n "f\"SELECT|f'SELECT|\.format\(.*SELECT" --type py

# Filesystem traversal candidates
rg -n "readFile|writeFile|createReadStream|open\(|File\(|PathBuf|join\(|resolve\(" --type js --type ts --type py --type rust
```

### Tools

```bash
cargo audit
npm audit --json
pnpm audit --json
bandit -r . -f json
semgrep --config=p/security-audit .
gitleaks detect --source .
```

## UX / Accessibility

### Checklist

- [ ] Keyboard navigation works end-to-end
- [ ] Focus indicators are visible and logical
- [ ] Screen reader support: labels, landmarks, ARIA used correctly
- [ ] Color contrast and non-color affordances
- [ ] Forms have clear labels, validation, and recovery paths
- [ ] Loading, empty, error, and success states guide the user
- [ ] Mobile/responsive behavior is accounted for
- [ ] Destructive actions have clear confirmation and undo/recovery when appropriate
- [ ] User flows match likely intent and do not dead-end

### Quick Grep

```bash
# Missing alt text candidates
rg -n "<img(?![^>]*alt=)" --type html --type tsx --type jsx

# Interactive elements with possible missing labels
rg -n "<button[^>]*(></button>|aria-label=\"\")|role=\"button\"" --type tsx --type jsx --type html

# ARIA/focus candidates
rg -n "aria-hidden=\"true\"|tabIndex|tabindex|autoFocus" --type tsx --type jsx --type html

# Form fields
rg -n "<input|<select|<textarea" --type tsx --type jsx --type html
```

### Tools

```bash
npx axe-cli http://localhost:3000
npx lighthouse --only-categories=accessibility http://localhost:3000
```

## Performance

### Checklist

- [ ] N+1 query patterns avoided
- [ ] Frequently queried columns are indexed
- [ ] Large lists are paginated or virtualized
- [ ] Expensive work is cached or memoized where safe
- [ ] Async code does not contain avoidable serial waits
- [ ] No blocking I/O in async hot paths
- [ ] Memory is bounded; large allocations and leaks are avoided
- [ ] Bundle size, lazy loading, and asset optimization for frontend code
- [ ] Background jobs and retries have limits/backoff

### Quick Grep

```bash
# Await in loops / serial async candidates
rg -n "for .*await|await .*for|\.await.*for|for.*\.await" --type js --type ts --type py --type rust

# Unbounded SQL candidates
rg -n "SELECT .* FROM|findMany\(|find\(\{" | grep -vi "limit\|take\|cursor\|offset\|count\|exists"

# Blocking I/O in Rust async contexts
rg -n "std::fs::|std::io::|std::thread::sleep" --type rust

# Large allocations
rg -n "Vec::with_capacity\([0-9]{5,}\)|new Array\([0-9]{5,}\)|Buffer\.alloc\([0-9]{6,}\)" --type rust --type js --type ts

# Frontend bundle/import candidates
rg -n "import \* as|from ['\"]lodash|from ['\"]moment|dynamic\(|lazy\(" --type js --type ts --type jsx --type tsx
```

### Tools

```bash
cargo flamegraph
node --prof app.js
EXPLAIN ANALYZE SELECT ...
npx webpack-bundle-analyzer
npx vite-bundle-visualizer
```

## API

### Checklist

- [ ] HTTP methods match semantics
- [ ] Status codes are precise and consistent
- [ ] Error response shape is consistent and actionable
- [ ] Input validation is explicit and close to the boundary
- [ ] Authn/authz behavior is consistent across endpoints
- [ ] List endpoints have pagination, sorting, and filtering limits
- [ ] Idempotency for retries on creates/payment-like operations
- [ ] Versioning and deprecation strategy
- [ ] OpenAPI/Swagger/schema docs match implementation
- [ ] Rate limiting and abuse protection exist where needed

### Quick Grep

```bash
# Routes / handlers
rg -n "router\.|app\.(get|post|put|patch|delete)|Route::|axum::|fastapi|@app\.|Controller" --type js --type ts --type py --type rust

# Status codes
rg -n "status\(|StatusCode::|HTTP_[0-9]{3}|Response\(" --type js --type ts --type py --type rust

# Error shapes
rg -n "error|message|code|details" --type js --type ts --type py --type rust

# Pagination candidates
rg -n "GET|list|findMany|SELECT" | grep -vi "limit\|page\|cursor\|offset\|take"
```

### Tools

```bash
npx @stoplight/spectral-cli lint openapi.yaml
npx @apidevtools/swagger-cli validate openapi.yaml
```

## Copy

### Checklist

- [ ] Tone is consistent across UI and docs
- [ ] CTAs describe the action and outcome
- [ ] Error messages explain what happened and how to recover
- [ ] No avoidable jargon in user-facing text
- [ ] Inclusive, precise language
- [ ] No placeholder/TODO/lorem ipsum text in shipped surfaces
- [ ] Empty states have guidance
- [ ] Loading and success messages set correct expectations
- [ ] Strings are ready for localization where relevant

### Quick Grep

```bash
# Placeholder/TODO text
rg -n "lorem|ipsum|TODO|FIXME|placeholder|coming soon" -i --type tsx --type jsx --type html --type md

# Vague errors
rg -n "Something went wrong|Error occurred|failed|invalid|try again" --type tsx --type jsx --type js --type ts --type py

# User-facing hardcoded strings
rg -n ">[A-Z][^<]{8,}<|title=\"|aria-label=\"|placeholder=\"" --type tsx --type jsx --type html
```

## CLI

### Checklist

- [ ] `--help` exists, is discoverable, and covers commands/options
- [ ] `--version` works
- [ ] Unknown commands/flags produce useful diagnostics
- [ ] Exit codes distinguish success and failure
- [ ] stdout is machine-readable when appropriate; diagnostics go to stderr
- [ ] Color respects TTY, `NO_COLOR`, and `FORCE_COLOR`
- [ ] Progress output does not break pipes or CI logs
- [ ] Config/env var precedence is documented and predictable
- [ ] Shell completion/docs are present for mature CLIs

### Quick Commands

```bash
./tool --help | head -40
./tool --version
./tool --bad-flag 2>&1; echo "Exit: $?"
./tool nonexistent 2>&1; echo "Exit: $?"
NO_COLOR=1 ./tool --help | cat -v
./tool --help | grep -Ei "usage|options|commands"
```

### Quick Grep

```bash
rg -n "exit\(|process\.exit\(|std::process::exit|ExitCode" --type rust --type js --type ts --type py
rg -n "NO_COLOR|FORCE_COLOR|isatty|is_terminal|stderr|stdout" --type rust --type js --type ts --type py
rg -n "clap|commander|yargs|click|argparse|cobra" --type rust --type js --type ts --type py --type go
rg -n "progress|spinner|indicatif|ora|cli-progress" --type rust --type js --type ts --type py
```
