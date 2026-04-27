# Database & SQL Profiling

> Profile database workloads at three layers: query plan (the SQL side), storage (the WAL/buffer side), and application interaction (connection pool, prepared statement cache). This reference is DB-specific; generic profiling lives elsewhere.

## Contents

1. [Decision tree — which layer is slow?](#decision-tree--which-layer-is-slow)
2. [Postgres](#postgres)
3. [SQLite](#sqlite)
4. [MySQL / MariaDB](#mysql--mariadb)
5. [ClickHouse / DuckDB / analytical](#clickhouse--duckdb--analytical)
6. [Application-side: connection pool, prepared-statement cache](#application-side-connection-pool-prepared-statement-cache)
7. [Cross-DB common patterns](#cross-db-common-patterns)
8. [Supabase-specific](#supabase-specific)
9. [Artifacts to capture](#artifacts-to-capture)

---

## Decision tree — which layer is slow?

```
User says "DB is slow"
      │
      ▼
Is one query slow, or everything?
  ├─ One query       → Query plan layer (EXPLAIN ANALYZE)
  └─ Everything      → Storage or app layer
        │
        ▼
   Is latency bad at low load?
     ├─ Yes → Storage (WAL, fsync, checkpoint, buffer pool)
     └─ No, only under load → App (pool saturation, N+1, lock)
```

---

## Postgres

### The three most useful queries

```sql
-- 1. What's slow right now (live)?
SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state
FROM pg_stat_activity
WHERE state != 'idle' AND query NOT LIKE '%pg_stat_activity%'
ORDER BY duration DESC;

-- 2. What's slow historically?
-- Requires pg_stat_statements extension: CREATE EXTENSION pg_stat_statements;
SELECT
  round(total_exec_time::numeric, 2) AS total_ms,
  calls,
  round(mean_exec_time::numeric, 2) AS mean_ms,
  round((100 * total_exec_time / sum(total_exec_time) OVER ())::numeric, 2) AS pct,
  query
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;

-- 3. What indexes are missing / unused?
SELECT schemaname, relname, idx_scan, seq_scan, n_live_tup
FROM pg_stat_user_tables
WHERE seq_scan > idx_scan AND n_live_tup > 10000
ORDER BY seq_scan DESC;
```

### EXPLAIN ANALYZE — how to read

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders o JOIN customers c ON o.customer_id = c.id
WHERE o.created_at > NOW() - INTERVAL '30 days';
```

Output anatomy:
```
Nested Loop  (cost=0.43..12345.67 rows=1000 width=120)
             (actual time=0.123..456.789 rows=987 loops=1)
  Buffers: shared hit=100 read=500 dirtied=2
  -> Index Scan using orders_created_at_idx on orders o
       ...
  -> Index Scan using customers_pkey on customers c
       ...
Planning Time: 0.234 ms
Execution Time: 457.123 ms
```

Read:
- **`actual time=X..Y`** — X is "time to first row," Y is "time to last row." Big gap → slow per-row work.
- **`rows=N loops=M`** — rows × loops = total rows processed by this node. Multiply to find the actual work.
- **`Buffers: shared hit=H read=R`** — hit from buffer pool vs read from disk. Read >> hit = cold cache or undersized shared_buffers.
- **`dirtied=N`** — pages modified by reads (hint bits, etc.). Large = warm up needed.
- **`cost=X..Y`** — planner estimate; use the ratio (actual_time / cost) across nodes to find planner misestimates.

### Plan types and their fixes

| Node type | Means | Fix if slow |
|-----------|-------|-------------|
| Seq Scan | Full-table scan | Add index, or accept if table is small |
| Index Scan | Index for filtering, heap for rows | Usually fine; check BUFFERS |
| Index Only Scan | Fully from index | Best case |
| Bitmap Heap Scan | Many index hits, batched heap fetch | Often best for medium selectivity |
| Nested Loop | M × N row comparison | Prefer Hash Join for large inputs |
| Hash Join | Build hash from one side | Good for large inputs; watch work_mem |
| Merge Join | Both sides sorted | Good for large pre-sorted inputs |
| Sort | Explicit sort | Add index matching ORDER BY, or raise work_mem |
| Hash Aggregate | GROUP BY via hash | Good; raise work_mem if spilling |

### Tuning shared_buffers and work_mem

```sql
-- Buffer hit ratio — should be > 99% for warm workloads
SELECT
  sum(heap_blks_hit) / nullif(sum(heap_blks_hit + heap_blks_read), 0) AS hit_ratio
FROM pg_statio_user_tables;

-- If < 99%, consider raising shared_buffers
SHOW shared_buffers;

-- work_mem per query; raise if you see "Sort Method: external merge" in EXPLAIN ANALYZE
SHOW work_mem;
```

### auto_explain — for production "slow query" logging

```
postgresql.conf:
  shared_preload_libraries = 'auto_explain'
  auto_explain.log_min_duration = '500ms'
  auto_explain.log_analyze = true
  auto_explain.log_buffers = true
```

Then slow queries appear in the log with full EXPLAIN ANALYZE output. Grep, ingest, profile.

### Postgres extension: pg_prewarm

```sql
CREATE EXTENSION pg_prewarm;
-- Fill buffer cache with a table
SELECT pg_prewarm('orders', 'buffer');
-- Or whole schema in a startup script
```

Use during deploy / after a restart to avoid cold-cache first-request cliff.

### Locks and contention

```sql
-- Active locks
SELECT pid, mode, locktype, relation::regclass, granted
FROM pg_locks
WHERE NOT granted;

-- Long-held locks
SELECT pid, now() - xact_start AS duration, state, query
FROM pg_stat_activity
WHERE state != 'idle in transaction' AND xact_start < now() - INTERVAL '1 minute';
```

### WAL and checkpoint pressure

```sql
SELECT * FROM pg_stat_wal;
SELECT * FROM pg_stat_bgwriter;

-- Checkpoint behavior
SHOW checkpoint_timeout;     -- default 5min
SHOW max_wal_size;            -- default 1GB
SHOW checkpoint_completion_target;  -- default 0.9 (spread I/O)
```

If checkpoints are too frequent, raise `max_wal_size`. If too slow to flush, lower `checkpoint_completion_target` or faster storage.

---

## SQLite

### PRAGMA-driven introspection

```sql
-- Stats on disk usage
PRAGMA page_count;
PRAGMA page_size;
PRAGMA freelist_count;

-- Journal mode (WAL is usually best)
PRAGMA journal_mode;             -- DELETE / WAL / MEMORY
PRAGMA synchronous;              -- FULL (safe) / NORMAL (fast, safe-ish) / OFF (danger)

-- Cache size (negative = KiB, positive = pages)
PRAGMA cache_size = -65536;      -- 64 MiB

-- mmap for large DB (bypasses pager)
PRAGMA mmap_size = 268435456;    -- 256 MiB

-- Autovacuum
PRAGMA auto_vacuum;              -- 0=none, 1=full, 2=incremental
```

### Tuning recipes

```sql
-- Write-heavy OLTP: WAL + NORMAL sync + big cache
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -65536;       -- 64 MB
PRAGMA temp_store = MEMORY;
PRAGMA wal_autocheckpoint = 1000; -- pages before auto checkpoint

-- Read-heavy with occasional write
PRAGMA journal_mode = WAL;
PRAGMA mmap_size = 1073741824;    -- 1 GiB mmap
PRAGMA cache_size = -262144;      -- 256 MB

-- Batch ingest (danger mode, crash loses data but fast):
PRAGMA journal_mode = MEMORY;
PRAGMA synchronous = OFF;
PRAGMA locking_mode = EXCLUSIVE;
-- BEGIN / ... / COMMIT in bulk
```

### Profiling a SQLite query

```sql
EXPLAIN QUERY PLAN SELECT ... ;    -- high-level plan (prefer indexes)
EXPLAIN SELECT ... ;               -- byte-code (per-opcode)
```

For the VDBE (virtual machine) perspective:

```bash
# sqlite3 CLI builtin
.explain on
SELECT ...;
```

Opcode-level profiling attributes each VDBE instruction. Use when you need to differentiate between "parse cost" and "execute cost" inside the DB engine.

### SQLite stats extensions

```sql
-- ANALYZE updates sqlite_stat1 for the planner
ANALYZE;

-- Query planner uses sqlite_stat4 if present (more selective)
PRAGMA analysis_limit = 1000;
ANALYZE;
```

Rerun `ANALYZE` after large data changes; a stale planner is a common "why did my query get slow" root cause.

### Lock contention in SQLite

Only one writer at a time (WAL allows readers during write). Symptoms:
- `SQLITE_BUSY` errors
- High p99 on writes even at low QPS

Fixes:
- Move to WAL mode (read-vs-write isolation)
- Batch writes: `BEGIN ... COMMIT` around many inserts, not one-per
- For true concurrent writes across processes: you likely need Postgres

See also `rust-cli-with-sqlite` skill for broader SQLite design patterns.

---

## MySQL / MariaDB

### Performance schema queries

```sql
-- Top slow statements
SELECT DIGEST_TEXT, COUNT_STAR, AVG_TIMER_WAIT / 1e9 AS avg_ms
FROM performance_schema.events_statements_summary_by_digest
ORDER BY SUM_TIMER_WAIT DESC LIMIT 20;

-- Live queries
SELECT * FROM performance_schema.processlist WHERE STATE IS NOT NULL;

-- I/O wait by table
SELECT OBJECT_SCHEMA, OBJECT_NAME,
       COUNT_READ, COUNT_WRITE, SUM_TIMER_READ / 1e9 AS read_ms
FROM performance_schema.table_io_waits_summary_by_table
ORDER BY SUM_TIMER_WAIT DESC LIMIT 20;
```

### EXPLAIN ANALYZE (MySQL 8.0+)

```sql
EXPLAIN ANALYZE SELECT ... ;
```

Read same as Postgres: actual timing per node, rows examined vs rows filtered.

### InnoDB buffer pool

```sql
SHOW ENGINE INNODB STATUS\G
-- key field: BUFFER POOL AND MEMORY
-- hit rate = 1 - (pages read / requests)

SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool%';
```

---

## ClickHouse / DuckDB / analytical

### ClickHouse

```sql
-- Live slow queries
SELECT query_start_time, query_duration_ms, read_rows, read_bytes, query
FROM system.query_log
WHERE type = 'QueryFinish' AND query_duration_ms > 500
ORDER BY query_start_time DESC LIMIT 50;

-- EXPLAIN with profiling
EXPLAIN PIPELINE SELECT ... ;
EXPLAIN ESTIMATE SELECT ... ;
EXPLAIN SYNTAX SELECT ... ;

-- Materialized view hit stats
SELECT database, table, parts, rows, bytes_on_disk
FROM system.parts
WHERE active
ORDER BY bytes_on_disk DESC LIMIT 20;
```

ClickHouse rewards vectorized, columnar operations; avoid per-row UDFs on hot paths.

### DuckDB

```sql
-- Built-in profiling
PRAGMA enable_profiling;
PRAGMA profiling_output = 'profile.json';
-- Run query
SELECT ... ;
```

DuckDB is excellent for local analytical work; profile is JSON for easy post-processing.

---

## Application-side: connection pool, prepared-statement cache

### Connection pool saturation

Symptoms: latency jumps when concurrent requests > pool size; "timeout waiting for connection" in logs.

Diagnostics (per-language):

**Rust `sqlx` / `deadpool`**:
```rust
let pool = sqlx::PgPool::connect_with(PgPoolOptions::new()
    .max_connections(20)
    .acquire_timeout(Duration::from_millis(500))
    .after_connect(|conn, _| Box::pin(async move { /* warmup */ Ok(()) }))
    ... ).await?;

// Metric: pool.size(), pool.num_idle()
```

**Go `database/sql`**:
```go
db.SetMaxOpenConns(20)
db.SetMaxIdleConns(10)
db.SetConnMaxLifetime(time.Hour)
db.SetConnMaxIdleTime(5*time.Minute)
// Stats: db.Stats()  → InUse / Idle / WaitCount / WaitDuration
```

**Node `pg`**:
```js
const pool = new Pool({ max: 20, idleTimeoutMillis: 30000 });
// pool.totalCount / pool.idleCount / pool.waitingCount
```

**Python `asyncpg`**:
```python
pool = await asyncpg.create_pool(dsn, min_size=5, max_size=20, command_timeout=60)
```

### Prepared statement cache

Most drivers cache prepared statements per-connection. The cache misses when:
- Query string differs (via `format!()` or concatenation) → **always parameterize**
- Pool closes and re-opens connection
- Size limit reached (tune with driver option)

From CASE-STUDIES.md §Case 7 ("Benchmark truthfulness"):

> "Ad hoc `format!()` SQL in mixed-path benches prevents cache hits on the FrankenSQLite side."

The fix: always use `?1`, `?2`, `$1`, `$2` parameter binding. String-formatting SQL kills the cache.

### N+1 pattern detection

```
-- Bad
for id in ids:
    row = query(f"SELECT * FROM t WHERE id = {id}")

-- Good — one query
rows = query("SELECT * FROM t WHERE id IN ($1)", ids)

-- Better — prepared + ANY
rows = query("SELECT * FROM t WHERE id = ANY($1)", ids_array)
```

Detection: in your tracing, if you see N DB spans per HTTP request where N scales with a list size, that's N+1.

---

## Cross-DB common patterns

### Index check

```
-- Postgres
CREATE INDEX CONCURRENTLY ON table (column) WHERE predicate;

-- Check usage
SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0;

-- SQLite
PRAGMA index_list('table');
PRAGMA index_info('index_name');

-- MySQL
SHOW INDEX FROM table;
```

Rule: an index that's never used is just dead weight; drop it or figure out why the planner isn't picking it.

### JOIN selectivity

```sql
-- How many rows does each JOIN step produce?
EXPLAIN ANALYZE ...

-- Look at the row counts at each level
-- If a JOIN multiplies rows 1M → 100M → 10B, that's the bottleneck
```

### Batch vs single write

| Pattern | Latency per row | Throughput | Use when |
|---------|-----------------|------------|----------|
| one INSERT per row | high | low | interactive |
| multi-row INSERT ($1,$2,$3), ($4,$5,$6), ... | medium | medium | mix |
| COPY FROM STDIN | low | very high | bulk ingest |
| UNNEST() with array params | low | high | programmatic bulk |

### fsync at commit

Every `COMMIT` in a durable DB implies an fsync. Batch: group commits reduce fsync count. Postgres has `synchronous_commit`:

```sql
SET synchronous_commit = off;   -- per-session; faster commits, accepts small loss on crash
```

Use for bulk-ingest; NEVER for critical writes.

---

## Supabase-specific

Supabase uses Postgres. Everything above applies. Supabase-specific adds:

- **PgBouncer pooler**: transaction-mode by default; cannot use session-level features (prepared statements, temp tables) across transactions.
- **Connection string**: `pooler.supabase.com:6543` (transaction) vs `:5432` (direct). Use 5432 for apps that need prepared statements.
- **Row-Level Security (RLS) cost**: every row evaluated with `auth.uid()` etc. Use `SECURITY INVOKER` and index on the policy expression.

See the `supabase` skill and `supabase:supabase-postgres-best-practices` for deeper guidance; this skill hands off to those for Supabase-specific tuning.

---

## Artifacts to capture

Per DB profiling run, save to `tests/artifacts/perf/<run-id>/db/`:

```
db/
├── explain_analyze_<query>.txt      # EXPLAIN (ANALYZE, BUFFERS) output
├── pg_stat_statements_top20.csv     # or equivalent per DB
├── slow_query_log.txt               # auto_explain or performance_schema digest
├── connection_pool_stats.json       # pool size, in-use, wait queue over time
├── buffer_hit_ratio_over_time.csv
├── wal_checkpoint_activity.csv      # Postgres
├── pragma_dump.txt                  # SQLite
└── schema.sql                       # table / index / MV definitions at profile time
```

Reference in hotspot_table.md — every row citing a DB hotspot names one of these files.

---

## Anti-patterns

- **Trusting `EXPLAIN` without `ANALYZE`** — it shows the planner's estimate, not actual. Use `EXPLAIN ANALYZE` except on queries you're afraid to actually run.
- **Running `EXPLAIN ANALYZE` on DELETE / UPDATE in prod** — it executes. Wrap in `BEGIN; EXPLAIN ANALYZE ...; ROLLBACK;`.
- **Ignoring `BUFFERS`** — you don't know if slowness is compute or I/O without it.
- **Measuring from the client without `RETURN NEXT`** — server-side `EXPLAIN ANALYZE` is authoritative; client-timed queries include network + serialization.
- **Optimizing one slow query when pg_stat_statements shows 100 slightly-slow queries dominate** — total time, not per-query.
- **Dropping an "unused" index without checking partial / conditional usage** — pg_stat might be reset or the index serves a rare-but-critical path.
