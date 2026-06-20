# Skill Candidacy

## Portfolio shape

Default:

```text
one root repository skill
zero to five focused skills
```

The root routes work and references doctrine.

Focused skills own independently triggered decisions.

## Gate

```yaml
skill_candidacy:
  recurring_trigger: yes | no
  consequential_decision: yes | no
  stable_governing_law: yes | no
  independent_activation: yes | no
  standalone_workflow: yes | no
  observable_success_and_failure: yes | no
  better_as_code: yes | no
  better_as_test: yes | no
  better_as_tooling: yes | no
  better_as_docs: yes | no
  accepted: yes | no
```

Accepted requires:

```text
first six yes
all better_as_* no
```

## Candidate

```yaml
focused_skill_candidate:
  candidate_id:
  proposed_name:
  governing_law_ids: []
  trigger_examples: []
  non_triggers: []
  consequential_decisions: []
  prohibited_routes: []
  required_artifacts: []
  success_signals: []
  failure_signals: []
  standalone_use_cases: []
  candidacy:
  evidence_refs: []
```

## Rejection reasons

```text
mechanical rule
better type/test/tool/docs
unstable law
no independent trigger
duplicates root skill
directory-shaped taxonomy
too little evidence
too narrow/one-off
```

## Creation handoff

Only accepted candidates receive CBSH-v1.

`$ms` creates packages only after explicit user authorization.
