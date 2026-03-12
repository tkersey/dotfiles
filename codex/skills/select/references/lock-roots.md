# Lock Root Contract

Use this contract anywhere orchestration decisions need exclusive write scopes: `$select`, `$teams`, `$mesh`, `selector`, and `$st` claim/reclaim flows.

## Canonical algorithm

1. Normalize each `scope` entry:
   - trim whitespace
   - drop a leading `./`
   - collapse repeated `/`
   - remove trailing `/`
2. Drop a terminal `/**` or `/**/*`.
3. Truncate at the first glob metacharacter: `*`, `?`, `[`.
4. Treat overlap as true when:
   - the lock roots are equal, or
   - one lock root is a path-prefix of the other.
5. Treat these as overlapping everything and therefore single-wave only:
   - `""`, `.`, `./`, `/`, `*`, `**`, `**/*`

## Usage notes

- Prefer file or module globs over broad directory roots when you can state ownership precisely.
- Missing or broad scopes are valid, but they collapse safe fanout and should usually produce a warning.
- If two otherwise-ready tasks serialize only because lock roots overlap, prefer an explicit `depends_on` edge so the ordering is intentional.
