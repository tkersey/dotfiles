# Example Exploration Sessions

These are repeatable walkthroughs for common repository shapes.

## Example 1: Next.js SaaS

```bash
cat AGENTS.md README.md 2>/dev/null | head -120
find . -maxdepth 2 -type f \( -name 'package.json' -o -name '.env.example' -o -name 'next.config.*' \) -print
find app src/app pages src/pages -maxdepth 4 -type f 2>/dev/null | head -120
rg -n "export async function (GET|POST|PUT|DELETE)|NextResponse|generateMetadata|createRoot|use server|use client" app src pages
rg -n "prisma|drizzle|db\.|createClient|server action|fetch\(|axios|tRPC|trpc" src app packages
rg -n "process\.env|auth\(|NextAuth|clerk|supabase|middleware" src app middleware.ts
```

Deliverable: route map, server/client split, core schemas, auth boundary, and database/API flow.

## Example 2: Rust CLI

```bash
rg -n "fn main\(|#\[tokio::main\]|derive\(.*Parser|Subcommand|Args" src crates
rg -n "^pub (struct|enum|trait) |impl .* for |thiserror|anyhow|eyre" src crates
rg -n "reqwest|Client::new|sqlx|rusqlite|File::|fs::|serde::Deserialize|std::env" Cargo.toml src crates
```

Deliverable: map from CLI args → command handler → domain/service → HTTP/db/file output.

## Example 3: Python FastAPI

```bash
rg -n "FastAPI\(|APIRouter|@app\.|@router\.|include_router" src app
rg -n "BaseModel|@dataclass|class .*Service|def .*_service|Depends\(" src app
rg -n "BaseSettings|os\.getenv|sqlalchemy|session\.|redis|requests\.|httpx|pytest|TestClient" src app tests
```

Deliverable: app factory, route modules, Pydantic schemas, service layer, persistence adapters, and test coverage.

## Example 4: Go HTTP service

```bash
rg -n "func main\(|http\.HandleFunc|gin\.Default|chi\.NewRouter|mux\.NewRouter|ListenAndServe" .
rg -n "^type [A-Z].* struct|database/sql|gorm|sqlx|pgx|Repository|Store" .
rg -n "os\.Getenv|viper|envconfig|func Test|httptest" .
```

Deliverable: route → handler → service → store flow, config sources, and test strategy.

## Example 5: Monorepo

```bash
find . -maxdepth 3 -type f \( -name 'package.json' -o -name 'Cargo.toml' -o -name 'go.mod' -o -name 'pyproject.toml' \) -print
find . -maxdepth 2 -type d \( -name apps -o -name packages -o -name services -o -name crates -o -name libs \) -print
rg -n "turbo|nx|bazel|pants|workspace|workspaces|members" package.json pnpm-workspace.yaml Cargo.toml WORKSPACE BUILD.bazel pyproject.toml
rg -n "main|route|router|command|handler|service|repository" apps services packages crates
```

Deliverable: package graph, app/service entry points, shared libraries, dependency direction, and suggested next package to inspect.
