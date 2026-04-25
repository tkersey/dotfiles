# Rejection Log — candidates considered but not collapsed

> Keep this forever. The point is not bookkeeping; it's to stop future scans
> (and future you) from re-proposing the same bad idea.

## Format

Each entry:

```
### <ID> — <short name>
- **Detected:** yyyy-mm-dd, run <run-id>
- **Sites:** <file:line, file:line, ...>
- **Proposed collapse:** <one sentence>
- **Clone-type classification:** I / II / III / IV / V
- **Rejection reason:** (pick one or more)
  - Accidental rhyme (clone type V)
  - Below score threshold (<2.0)
  - Risk > benefit (size of blast radius, security boundary, perf hot path)
  - Sites diverging in observable contract (error mode / timing / side effects)
  - Sibling call sites expected to disappear soon (premature collapse)
- **Notes:** <anything that would make a future agent reconsider>
```

## Entries

### ISO-003 — `parse_header` in TCP vs TLS paths
- **Detected:** 2026-04-01, run 2026-04-01-pass-1
- **Sites:** `src/net/tcp.rs:87`, `src/net/tls.rs:141`
- **Proposed collapse:** extract `parse_header(bytes) -> Result<Header>` and call from both paths.
- **Clone-type classification:** V (accidental rhyme)
- **Rejection reason:** Sites diverge in observable contract — TCP path tolerates trailing whitespace and logs at INFO; TLS path rejects whitespace and logs at WARN per spec RFC-XXXX §4.2. Collapsing would have changed the observable error mode for the TLS path.
- **Notes:** If the spec changes (see linked TODO), reconsider.

### ISO-007 — `UserDTO` vs `AccountDTO`
- **Detected:** 2026-04-12, run 2026-04-12-pass-2
- **Sites:** `src/api/users.rs:23`, `src/api/accounts.rs:31`
- **Proposed collapse:** extract a shared `PrincipalDTO` with a tagged discriminator.
- **Clone-type classification:** II
- **Rejection reason:** Score 1.8 (24 LOC saved × 0.75 conf / 10 risk). Below threshold.
- **Notes:** Revisit when `billing.rs` adds its own near-duplicate — the Rule-of-3 triggers at that point.
