#!/usr/bin/env bash
set -euo pipefail
name="${1:-abstraction}"
language="${2:-agnostic}"
cat <<OUT
# Sheafification Certificate: ${name} (${language})

## Abstraction
Name:
Files:
Current representation:
Semantic load:

## Site
Local contexts:
Covering assumption:
Overlaps:

## Local sections
| Context | Local meaning |
|---|---|
| | |

## Compatibility
Overlap checks:
Compatibility failures:

## Gluing
Existence:
Uniqueness:
Missing global cases:
Redundant global cases:
Obstructions:

## Possibility envelope
Possible states:
Impossible states currently admitted:
Valid states currently omitted:
Redundant meanings:
Hidden obligations:

## Canonical repair
Construction:
Why this construction:
Nearby alternatives rejected:

## Replacement artifact
Type / IR / schema / state machine / effect signature / observation vocabulary:

## Interpreter / projection / lowering
Function:
Owner:
Bypass prevention:

## Law tests
Local compatibility law:
Global existence law:
Global uniqueness / normalization law:
Falsifier:

## Migration
First witness slice:
Backward compatibility:
Rollback:

## Status
planned / implemented / verified / obstructed / primitive exception
OUT
