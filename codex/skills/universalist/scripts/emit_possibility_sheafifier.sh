#!/usr/bin/env bash
set -euo pipefail
focus="${1:-abstraction}"
language="${2:-agnostic}"
cat <<OUT
# Possibility Sheafifier (${focus}, ${language})

## Current abstraction

- name:
- files:
- current representation:
- semantic load:

## Usage site

- local contexts:
- covering assumption:
- overlaps:

## Local sections

- context -> local meaning:

## Compatibility checks

- overlap:
- expected agreement:
- actual agreement/failure:

## Gluing analysis

- existence of global representation:
- uniqueness up to intended equivalence:
- missing global cases:
- redundant global cases:
- obstructions:

## Possibility envelope

- impossible states currently admitted:
- valid states currently omitted:
- redundant meanings:
- hidden obligations:

## Canonical repair

- construction:
- replacement artifact:
- interpreter/projection/lowering:
- nearby alternatives rejected:

## Law tests

- local compatibility law:
- global existence law:
- global uniqueness/normalization law:
- falsifier:

## Migration

- first witness slice:
- backwards compatibility:
- stop point:
OUT
