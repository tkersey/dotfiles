# Mesh Batch Anti-Patterns

Use `$mesh` for uniform batch jobs and repeated leaf execution, not as a general-purpose orchestration layer.

## 1) Heterogeneous work in a row runner

Anti-pattern:

- using `$mesh` for research, review, design, or mixed implementation tasks

Why it fails:

- rows stop being interchangeable and the instruction template becomes vague

Better path:

- use `$teams` or direct `spawn_agent` delegation for heterogeneous work

## 2) Dependent rows

Anti-pattern:

- one row needs another row's output before it can proceed

Why it fails:

- `spawn_agents_on_csv` is built for independent items, not dependency-aware scheduling

Better path:

- do the dependency shaping locally or with `$teams`, then run only the independent batch portion in `$mesh`

## 3) Overlapping write scopes

Anti-pattern:

- multiple rows mutate the same files or the same shared state

Why it fails:

- workers race, clobber results, or produce hard-to-integrate outputs

Better path:

- keep mesh rows read-only or give each row a disjoint output scope

## 4) Ambiguous result payloads

Anti-pattern:

- workers return long narratives instead of stable structured fields

Why it fails:

- exported CSV output becomes hard to compare, filter, or consume later

Better path:

- keep `report_agent_job_result.result` small, structured, and schema-aligned

## 5) Reusing the same input and output path

Anti-pattern:

- setting `csv_path` and `output_csv_path` to the same location

Why it fails:

- exported results can overwrite or confuse the input source of truth

Better path:

- keep input and output CSV paths distinct

## 6) Treating `$mesh` as the default

Anti-pattern:

- routing unshaped implementation work to `$mesh` just because multiple agents exist

Why it fails:

- you lose the advantages of native collab tools, reusable agent context, and flexible delegation

Better path:

- shape the work with `$teams` or locally, then prefer `$mesh` once the remaining units are repeated leaf work

## 7) Synthetic evidence waves

Anti-pattern:

- launching a late batch of near-no-op rows just to prove mesh usage or lane completeness

Why it fails:

- concurrency numbers go up while unique work stays flat
- tokens and review time are spent on evidence theater instead of useful execution

Better path:

- treat primary substantive rows as sufficient evidence and only add follow-up rows for blocker or proof-failure cases

## 8) Cartesian lane multiplication on the same scope

Anti-pattern:

- expanding one unit into coder, reducer, fixer, prover, and integrator rows on the same scope before any blocker exists

Why it fails:

- workers duplicate effort, inflate fanout metrics, and create misleading signs of progress
- integration cost rises without adding new substantive coverage

Better path:

- start with one primary row per substantive unit and add secondary rows only after a concrete blocker, failed proof, or non-trivial diff justifies them
