# Mesh Batch Anti-Patterns

Use `$mesh` for uniform batch jobs, not as a general-purpose orchestration layer.

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

- routing ordinary implementation work to `$mesh` just because multiple agents exist

Why it fails:

- you lose the advantages of native collab tools, reusable agent context, and flexible delegation

Better path:

- stay local by default; use `$teams` for heterogeneous delegation and `$mesh` only for true batch fanout
