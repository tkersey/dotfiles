# Skill Obligation Matrix

Distinguish expected skills from merely mentioned skills.

```yaml
skill_obligation_matrix:
  - skill:
    trigger_observed:
    expected: yes | no | conditional
    evidence:
      skill_read: yes | no
      assistant_declaration: yes | no
      receipt: yes | no
      root_equivalent: yes | no
    verdict: satisfied | omitted | covered_by_other_skill | conditional_not_required | unclear
    impact_if_omitted: high | medium | low
    next_report_check:
```

Do not grade by mention count. Grade by obligation and route impact.
