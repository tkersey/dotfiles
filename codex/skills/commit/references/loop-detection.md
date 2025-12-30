# Tight Loop Detection (Heuristics)

Goal: run at least one fast, relevant signal before committing. Prefer the smallest loop that still exercises the change.

## Selection Order
1. Project-provided task runner (just/Make/Task/npm scripts)
2. Language-native test runner
3. Lint/typecheck/static analysis
4. Minimal runtime log or smoke check

## Task Runners (fastest wins)
- justfile: look for `test`, `check`, `lint`, `ci` recipes; run `just <recipe>`.
- Makefile: look for `test`, `check`, `lint`; run `make <target>`.
- Taskfile.yml: look for `test`, `check`, `lint`; run `task <task>`.
- package.json scripts: prefer `test`, then `check`, then `lint`.
  - Pick package manager via lockfile:
    - `pnpm-lock.yaml` -> `pnpm <script>`
    - `yarn.lock` -> `yarn <script>`
    - `package-lock.json` -> `npm run <script>`
    - `bun.lockb` -> `bun <script>`

## Language Defaults (if no task runner)
- Python: `uv run pytest` if pytest config or dependencies present.
- Go: `go test ./...`
- Rust: `cargo test`
- Node (no scripts): `npm test` if `test` script exists, otherwise ask.
- Java: `./mvnw test` if `mvnw` exists, else `mvn test`.
- Gradle: `./gradlew test` if `gradlew` exists, else `gradle test`.
- .NET: `dotnet test`
- Elixir: `mix test`
- Ruby: `bundle exec rspec` if `spec/` exists; otherwise ask.

## When in doubt
- Prefer the smallest signal that exercises the change.
- If the command is unclear or risky, ask the user for the preferred check.
