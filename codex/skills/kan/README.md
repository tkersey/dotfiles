# kan

Drop-in replacement skill for detailed Kan mechanics inside universal architecture.

Use `$universalist` first to decide whether a seam deserves a canonical artifact. Use `$kan` when the selected boundary needs detailed Kan extension/lift, Freyd/AFT, Yoneda/Coyoneda, defunctionalization, codensity, or law-test mechanics.

## Install

From your `dotfiles` repo root:

```bash
rm -rf codex/skills/kan
unzip kan-world-boundaries-dropin.zip -d .
cd codex/skills/kan
chmod +x scripts/*.sh
./scripts/check_skill.sh
```

## Central rule

```text
universalist chooses the artifact.
kan elaborates the categorical mechanics.
```

Do not begin detailed mechanics until worlds, boundary kind, known side, unknown location, witness slice, and proof signal are named.

## Composition Certificate alignment

`kan` elaborates Composition Certificates selected by `universalist`. It maps certificate fields to categorical mechanics: worlds become categories/posets/schemas; boundaries become `K` or `P`; artifacts become `Lan`, `Ran`, `Delta`, `Lft`, `Rft`, Yoneda, Coyoneda, defunctionalized IR, Freyd builders, or obstruction reports.

## Codensity presentation update

This version adds codensity presentation mode: when a semantic artifact is too large or infinitary for a useful algebraic presentation, use a small dense world of probes plus a dual/observation bridge and reconstruction law.

Useful command:

```bash
./scripts/emit_codensity_presentation.sh report agnostic
```

## Exact Context / context compilation

This version adds context-compilation mechanics for semantic-consumption boundaries. Use `./scripts/emit_context_compilation_report.sh` when a model, human, policy engine, planner, tool selector, or agent step must receive a task-indexed, schema-shaped, provenance-preserving context object rather than raw retrieval results.
