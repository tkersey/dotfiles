#!/usr/bin/env bash
set -euo pipefail
law="${1:-law}"
language="${2:-agnostic}"
cat <<OUT
# Property Test Plan: ${law} (${language})

## Property

## Carrier generators

## Operation sequence

## Observation function

## Expected law / non-law

## Counterexample shape

## Shrinking target

## Implementation hook

## Architecture implication if false
OUT
