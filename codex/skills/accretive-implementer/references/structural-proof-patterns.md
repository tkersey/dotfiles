# Structural proof patterns

Use the lightest fitting proof when the change alters representation, normalization, or combination behavior.

## Good fits
- exhaustive handling for variant boundaries
- round-trip for parse/serialize or constructor/eliminator pairs
- idempotence for canonicalization or normalization
- identity or associativity for combine operations
- regression checks for likely caller misuse after an API change

## Selection rule
Pick the cheapest proof that would fail if the new structure were wrong.
Do not add a heavier harness when a lighter one already closes the risk.
