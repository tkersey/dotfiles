# Review Distillation Mode

Review Distillation Mode splits the work:

```text
Review Lab       = messy exploratory evidence branch/worktree
Delivery Branch  = clean rederived patch from frozen base
```

Core rule:

```text
The lab learns. The delivery branch forgets.
```

Trigger when:

- same_cluster_findings >= 2;
- same cluster reappears after fix;
- dirty tree contains multiple review repairs;
- route would add public/fallback/compatibility/tolerance surface;
- prior universalist-not-needed was falsified;
- prior selected normal form was falsified;
- CAS keeps finding adjacent issues after green local proof.

Do not deliver lab history. Deliver only the distilled normal form.
