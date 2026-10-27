# Sheafification Certificates

A Sheafification Certificate is the reviewable output of Track G. It certifies that a replacement abstraction repairs a concrete gluing failure over a real usage site.

## Template

```text
Abstraction
  Name:
  Files:
  Current representation:
  Semantic load:

Site
  Local contexts:
  Covering assumption:
  Overlaps:

Local sections
  Context -> local meaning:

Compatibility
  Overlap checks:
  Compatibility failures:

Gluing
  Existence:
  Uniqueness:
  Missing global cases:
  Redundant global cases:
  Obstructions:

Possibility envelope
  Possible states:
  Impossible states currently admitted:
  Valid states currently omitted:
  Redundant meanings:
  Hidden obligations:

Canonical repair
  Construction:
  Why this construction:
  Nearby alternatives rejected:

Replacement artifact
  Type / IR / schema / state machine / effect signature / observation vocabulary:

Interpreter / projection / lowering
  Function:
  Owner:
  Bypass prevention:

Law tests
  Local compatibility law:
  Global existence law:
  Global uniqueness / normalization law:
  Falsifier:

Migration
  First witness slice:
  Backward compatibility:
  Rollback:

Status
  proposed / implemented / verified / obstructed / primitive exception
```

## Review questions

1. What is the usage site?
2. What local sections were actually observed?
3. Which overlaps failed, if any?
4. Does compatible local behavior glue to a global abstraction?
5. Is the global abstraction unique up to intended equivalence?
6. What impossible states are removed?
7. What valid states are newly representable?
8. What law and falsifier prove the repair has teeth?
