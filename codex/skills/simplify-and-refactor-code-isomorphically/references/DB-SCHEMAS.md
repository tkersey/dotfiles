# Database + Schema Refactors

> Data-layer refactors break production more often than any other kind. Every field, every column, every enum variant is a contract between writer and reader, with the DB itself as the longest-lived participant.

## Contents

1. [The DB isomorphism axes](#the-db-isomorphism-axes)
2. [Safe column rename](#safe-column-rename)
3. [Safe column drop](#safe-column-drop)
4. [Safe table split / merge](#safe-table-split--merge)
5. [Type change (INT → BIGINT, TEXT → JSONB, etc.)](#type-change)
6. [Enum / discriminator refactors](#enum--discriminator-refactors)
7. [Index refactor](#index-refactor)
8. [Denormalization / normalization swaps](#denormalization--normalization-swaps)
9. [Query shape refactor](#query-shape-refactor)
10. [ORM / query-builder-specific](#orm--query-builder-specific)
11. [Migration rollback patterns](#migration-rollback-patterns)

---

## The DB isomorphism axes

| Axis | Breaker |
|------|---------|
| **Column nullability** | `NOT NULL` added → existing writers that passed NULL now fail |
| **Default value** | changes what absent columns read as |
| **Collation / charset** | affects sort order; silent behavior change |
| **Unique constraint** | new constraint rejects existing duplicate data |
| **Foreign key ON DELETE** | `CASCADE` vs `SET NULL` vs `RESTRICT` changes observable behavior |
| **Index existence** | query plan changes; may cause perf regression |
| **Trigger behavior** | invisible to most readers; preserve carefully |
| **Stored procedure signature** | RPC callers break |
| **View definition** | downstream query semantics change |
| **Row-level security policy** | access control shifts |
| **Check constraint** | tighter check rejects existing data |
| **Generated column formula** | historical values don't back-fill automatically |
| **Partition scheme** | moves data physically; long lock |
| **Replica lag tolerance** | reads from replicas see different shape during migration |

---

## Safe column rename

**Wrong way:** `ALTER TABLE users RENAME COLUMN email_addr TO email;` in one migration. Old app code reads `email_addr` and crashes.

**Right way: 3-phase migration.**

### Phase 1 — additive
```sql
ALTER TABLE users ADD COLUMN email TEXT;
-- backfill (batched, safe to retry)
UPDATE users SET email = email_addr WHERE email IS NULL;
-- keep both columns in sync via trigger
CREATE FUNCTION sync_email() RETURNS TRIGGER AS $$
BEGIN
  IF NEW.email IS NULL AND NEW.email_addr IS NOT NULL THEN NEW.email := NEW.email_addr; END IF;
  IF NEW.email_addr IS NULL AND NEW.email IS NOT NULL THEN NEW.email_addr := NEW.email; END IF;
  RETURN NEW;
END; $$ LANGUAGE plpgsql;
CREATE TRIGGER email_sync BEFORE INSERT OR UPDATE ON users FOR EACH ROW EXECUTE FUNCTION sync_email();
```

### Phase 2 — app cutover
Deploy new app code that reads `email`. Old code still reads `email_addr`; trigger keeps them aligned. Run for at least one full business cycle.

### Phase 3 — drop old
```sql
DROP TRIGGER email_sync ON users;
DROP FUNCTION sync_email();
ALTER TABLE users DROP COLUMN email_addr;
```

**Per AGENTS.md: wait for user approval before Phase 3.** The old column being gone is a deletion.

---

## Safe column drop

Similarly 3-phase.

1. Deploy new app code that neither reads nor writes the column. Leaves DB intact.
2. Wait a full cycle; verify no queries hit the column (log slow queries on it for a week).
3. `ALTER TABLE ... DROP COLUMN ...` with user approval.

**Isomorphism pitfall:** the column may be read by analytics queries, reporting tools, ETL jobs you didn't know about. `pg_stat_statements` helps: `SELECT query, calls FROM pg_stat_statements WHERE query ILIKE '%email_addr%';`

---

## Safe table split / merge

**Merging two tables** (e.g., `users` + `user_profiles` that drifted apart):

### Option A — dual-write, dual-read, cut over
Too complex for most cases. Use only when both tables have ongoing heavy writes.

### Option B — view shim
```sql
CREATE TABLE user_merged AS SELECT u.*, p.bio, p.avatar_url FROM users u LEFT JOIN user_profiles p ON u.id = p.user_id;
CREATE VIEW users AS SELECT id, email, ..., /* NOT bio or avatar */ FROM user_merged;
CREATE VIEW user_profiles AS SELECT user_id, bio, avatar_url FROM user_merged;
-- app reads/writes still work; migrate gradually
```

**Pitfall:** views are read-only by default in Postgres. You need `INSTEAD OF` triggers for writes, which is a lot of code. Usually simpler to cut over in one maintenance window.

---

## Type change

### INT → BIGINT (extending)
```sql
ALTER TABLE orders ALTER COLUMN id TYPE BIGINT;
```
Safe to widen. Rewrites the table in Postgres for pre-v11; online for v12+.

### TEXT → JSONB (restructuring)
Most risky. Requires app-level migration.
1. Add `payload_jsonb JSONB`.
2. Backfill: `UPDATE t SET payload_jsonb = payload::jsonb WHERE payload_jsonb IS NULL;`
3. App cutover.
4. Drop `payload`.

Pitfall: `TEXT` is opaque to DB indexes; `JSONB` query patterns differ. Test every query that reads the column.

### TIMESTAMP → TIMESTAMP WITH TIME ZONE
Semantics change. Verify all writers understand UTC vs local. Ship as behavior change.

---

## Enum / discriminator refactors

### Add a variant (safe)
```sql
ALTER TYPE order_status ADD VALUE 'refunded';
-- cannot be done in a transaction in some DBs; plan accordingly
```

### Remove a variant (risky)
Production may still hold rows with that variant. Migrate them first:
```sql
UPDATE orders SET status = 'cancelled' WHERE status = 'obsolete_variant';
-- then — in a later migration, once no rows have the variant:
CREATE TYPE order_status_v2 AS ENUM ('pending', 'shipped', 'cancelled', 'refunded');
ALTER TABLE orders ALTER COLUMN status TYPE order_status_v2 USING status::text::order_status_v2;
DROP TYPE order_status;
ALTER TYPE order_status_v2 RENAME TO order_status;
```

### Rename a variant
Usually: add the new name, migrate data, drop the old. Same 3-phase pattern.

---

## Index refactor

### Add an index online
```sql
CREATE INDEX CONCURRENTLY idx_orders_user_id ON orders(user_id);
```

CONCURRENTLY avoids locking the table. If it fails partway through, you get an `INVALID` index — drop and retry.

### Drop an index safely
```sql
DROP INDEX CONCURRENTLY idx_orders_user_id;
```

### Replace an index
```sql
CREATE INDEX CONCURRENTLY idx_orders_user_id_new ON orders(user_id, created_at);
DROP INDEX CONCURRENTLY idx_orders_user_id;
ALTER INDEX idx_orders_user_id_new RENAME TO idx_orders_user_id;
```

Pitfall: query planner needs to re-choose. Run `EXPLAIN` on key queries before and after.

---

## Denormalization / normalization swaps

### Inline a 1:1 table (denormalize)
```sql
-- before: users + user_settings
-- after: users with settings_* columns
ALTER TABLE users
  ADD COLUMN setting_email_digest BOOLEAN,
  ADD COLUMN setting_dark_mode BOOLEAN;
UPDATE users u SET setting_email_digest = s.email_digest, setting_dark_mode = s.dark_mode
  FROM user_settings s WHERE s.user_id = u.id;
-- app cutover
-- DROP TABLE user_settings;   -- only after approval
```

### Extract a 1:1 table (normalize)
Reverse. Rarely wins; extra JOIN cost. Do when:
- the sub-table is only read in specific flows
- it's often NULL on the main table
- you want per-row locking granularity

---

## Query shape refactor

### N+1 elimination
See [TECHNIQUES.md §1.2](TECHNIQUES.md#12-collapse-type-ii-clones-same-shape-different-literals) and [VIBE-CODED-PATHOLOGIES.md §P19](VIBE-CODED-PATHOLOGIES.md#p19--n1-queries-generated-by-helpful-autocomplete).

```typescript
// before — N+1
for (const order of orders) {
  const user = await db.user(order.user_id);
}
// after — 1 query
const userIds = [...new Set(orders.map(o => o.user_id))];
const users = await db.users({ id: { in: userIds } });
const userMap = new Map(users.map(u => [u.id, u]));
```

**Isomorphism:** ordering is preserved if callers consume `orders` in the same order afterward (they always do, it's a local array). Error semantics change — one failed user previously failed one order; now a failed batch either all-fails or all-succeeds depending on driver.

### `SELECT *` → specific columns
Reduces IO, changes row shape downstream. Audit each consumer.

### CTE (`WITH`) inline vs materialized
Postgres 12+ inlines CTEs by default, changing query plan. Use `WITH ... AS MATERIALIZED (...)` to restore pre-12 behavior if plans regress.

---

## ORM / query-builder-specific

### Prisma
```typescript
// before — implicit join via include
const orders = await prisma.order.findMany({ include: { user: true } });
// after — explicit select
const orders = await prisma.order.findMany({
  select: { id: true, total: true, user: { select: { id: true, name: true } } },
});
```
Δ: fewer columns over the wire. **Behavior change:** downstream code now sees a narrower type. Compile error if it tried to read dropped fields — good.

### Drizzle
```typescript
// before — named query
const usersWithOrders = await db.query.users.findMany({ with: { orders: true } });
// after — explicit join
const usersWithOrders = await db.select().from(users).leftJoin(orders, eq(users.id, orders.userId));
```

### TypeORM / Sequelize
Similar choices. Generally: explicit > implicit; named queries > chained queries for readability.

### Dynamic query builders
```typescript
// before — builders that build different queries per branch
const q = builder.select('*').from('users');
if (activeOnly) q.where('active', true);
if (sortBy)    q.orderBy(sortBy);
// result: ad-hoc query per request — hard to cache, hard to index-plan
```
Consider replacing with a small set of named queries.

---

## Migration rollback patterns

Every migration must have a thought-out rollback. For a schema change:

```sql
-- migration 0042_add_email_column.sql
BEGIN;
ALTER TABLE users ADD COLUMN email TEXT;
COMMIT;

-- migration 0042_down.sql
BEGIN;
ALTER TABLE users DROP COLUMN email;
COMMIT;
```

If the up-migration backfilled data, the down-migration **loses that data**. Snapshot to a backup table first:

```sql
-- up
CREATE TABLE users_backup_0042 AS SELECT * FROM users;
ALTER TABLE users ADD COLUMN email TEXT;
UPDATE users SET email = email_addr WHERE email IS NULL;

-- down
ALTER TABLE users DROP COLUMN email;
DROP TABLE users_backup_0042;    -- after verifying no need
```

**Per AGENTS.md: rollback runs only with explicit user approval.** The migration framework can run "down" silently; add a manual step.

---

## Integration with this skill's loop

Map (Phase B) — scanning for DB-refactor candidates:

```bash
# Find DB-touching code to map duplication
rg 'prisma\.\w+\.(findMany|findFirst|findUnique)' -t ts -n
rg 'sqlx::(query|query_as)' -t rust -n
rg 'session\.(query|execute)' -t python -n
rg 'tx\.Query|tx\.Exec' -t go -n

# Near-identical query functions
rg 'SELECT.*FROM users' -A 5 -B 0 | head -80
```

Score (Phase C): DB refactors are **always Risk ≥ 3**. Never land as "one-lever" commits for a whole migration — the `up.sql` is one commit, the app-code cutover is another, the `drop column` after approval is a third.

Prove (Phase D): in addition to the isomorphism card, add:
```markdown
### DB migration contract
- Forward migration: reversible? (yes/no, how)
- Backfill: atomic? batched? maximum duration?
- Read-path compatibility: old app + new schema works? (yes/no)
- Write-path compatibility: new app + old schema works? (yes/no)
- Replica lag tolerance: OK with what delay?
- Rollback runbook: step-by-step
```

If any row is not "yes" with a rationale, split the migration into more phases.
