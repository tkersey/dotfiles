# Cost model and false positives

Run the Universalist boundary pass whenever implementation or resolution considers a code boundary. Activation does not require a refactor.

A stronger construction is worth it when it reduces semantic drift, invalid states, duplicated validation, branch complexity, projection sprawl, or integration ambiguity.

Avoid escalation when:

- a local helper would solve the issue;
- the domain rules are not stable;
- the stronger model would increase onboarding cost more than it reduces bug risk;
- the chosen construction cannot be tested;
- public API or persistence changes are not acceptable.

Always compare to the nearby boring alternative. Preserving an already exact boundary is a valid Universalist result.
