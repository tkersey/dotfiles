# Search Saturation

Saturation does not mean every file was read.

It means additional search is unlikely to change a material doctrine decision.

## Material changes

```text
architecture classification
authority owner
governing law
invariant boundary
failure family
proof gap
knowledge destination
skill acceptance/rejection
```

## Receipt

```yaml
saturation:
  lanes_required: []
  lanes_covered: []
  open_questions: []
  contradictions_remaining: []
  last_material_model_change:
  additional_search_would_change:
    repository_fingerprint:
    authority_map:
    governing_laws:
    proof_map:
    knowledge_routes:
    skill_portfolio:
  verdict:
    saturated |
    targeted_search_required |
    blocked
  next_targeted_queries: []
```

## Deep-mode challenge

The saturation auditor should attempt to find:

- an unsearched evidence lane;
- a high-impact unsupported claim;
- a contradiction hidden by terminology;
- a skill candidate based on weak evidence;
- a proof gap that changes routing.

## Stop

Stop on `saturated`.

On `targeted_search_required`, name exact questions and methods.

On `blocked`, name missing access or unavailable evidence.

Do not continue broad exploration without a route-changing question.
