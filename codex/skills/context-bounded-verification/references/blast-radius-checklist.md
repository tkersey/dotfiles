# Blast-Radius Checklist

Use this checklist when a change could affect behavior outside the edited file.

## Code dependency surface

- Direct callers and callees
- Transitive callers for public functions
- Interface/type/schema consumers
- Generated clients or generated code
- Test fixtures and snapshots
- Error handling and retry paths
- Default values and fallback behavior

## Runtime and operational surface

- Scheduled jobs, cron, workers, queues
- Caches, TTLs, cache keys, invalidation
- Webhooks and asynchronous consumers
- Feature flags and environment-specific behavior
- Logs, metrics, traces, alert names
- Deployment order and rollback path
- Staging/production data differences

## Contract surface

- Public API request/response shape
- Status codes and error messages
- Serialization formats and ordering
- Database schemas and migrations
- Authn/authz and permission checks
- Billing, metering, quotas, entitlements
- Legal/compliance text or audit trails

## Edge cases

- Empty, null, missing, malformed, and duplicate inputs
- Time zones, DST, leap years, month boundaries
- Currency, locale, Unicode, casing
- Pagination, sorting, ordering stability
- Concurrency and idempotency
- Partial failure and retry behavior
- Backward compatibility with old clients
