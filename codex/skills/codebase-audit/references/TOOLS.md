# Tools and Signals

Favor tools already present in the repository. Do not install new tools or hit the network unless the user asked and the current Codex approval/sandbox policy allows it.

## General

- `rg`: fast code search for entry points, risky constructs, and user-facing text
- `git grep`: fallback when ripgrep is unavailable
- `git diff`, `git status`: understand current worktree and avoid reporting already-fixed issues
- language tests and linters already configured by the repo
- AST-aware tools such as `ast-grep` when already installed

## Security

- `cargo audit`, `npm audit`, `pnpm audit`, `pip-audit`, `bundle audit`
- `semgrep` security rules
- `bandit` for Python
- `gitleaks` for secret discovery
- framework-specific route and middleware review

## UX / Accessibility

- manual component/flow inspection
- `axe-core` / `axe-cli`
- Lighthouse accessibility category
- Storybook and component tests when present

## Performance

- query plans and slow query logs when available
- profilers: `perf`, flamegraphs, pprof, Chrome DevTools
- frontend bundle analyzers
- benchmarks already present in the repo

## API

- OpenAPI/Swagger validators
- contract tests
- schema validators such as zod, joi, pydantic, serde, JSON Schema
- route maps and API integration tests

## Copy

- user-facing string search
- docs and UI snapshots
- localization catalogs
- spelling/grammar tooling already present

## CLI

- direct `--help`, `--version`, bad flag, and pipe behavior checks
- snapshot tests for CLI output
- shellcheck for shell scripts
- completion tests when present
