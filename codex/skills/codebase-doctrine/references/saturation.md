# Search Saturation

Saturation means more search is unlikely to change a material doctrine decision.
It never means every file was read.

```yaml
saturation:
  lanes_required: []
  lanes_covered: []
  open_questions: []
  contradictions_remaining: []
  last_material_model_change_ref:
  additional_search_would_change:
    repository_fingerprint: yes | no
    authority_map: yes | no
    governing_laws: yes | no
    proof_map: yes | no
    knowledge_routes: yes | no
    skill_portfolio: yes | no
  verdict: saturated | targeted_search_required | blocked
  next_targeted_queries: []
```

`saturated` requires:

- every required lane covered;
- no open or blocked search question;
- no route-changing open question;
- no unresolved material contradiction;
- all `additional_search_would_change` values are no;
- all durable active claims routed.

On `targeted_search_required`, name exact questions and methods. On `blocked`,
name missing access or unavailable evidence.
