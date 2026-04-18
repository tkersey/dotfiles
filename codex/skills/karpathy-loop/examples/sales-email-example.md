# Sales Email Prompt Optimization Example

```text
Run a Karpathy loop on this sales email prompt.

Target prompt:
Write a cold outbound email for the prospect. Make it friendly and persuasive.

Goal:
Generate concise outbound emails that are personalized, specific, and end with a low-friction CTA.

Test cases:
1. Prospect: CFO at a 200-person SaaS company. Pain: manual forecasting.
2. Prospect: VP Sales at a cybersecurity company. Pain: low outbound reply rates.
3. Prospect: Head of Ops at a logistics startup. Pain: delayed reporting.
4. Prospect: Founder of an AI tooling startup. Pain: onboarding dropoff.
5. Prospect: RevOps lead at a fintech company. Pain: CRM hygiene.

Success checks:
1. Is the email under 120 words?
2. Does it mention a specific prospect-relevant pain?
3. Does it avoid generic phrases like “hope you’re well”?
4. Does it end with one clear question?
5. Does it avoid unsupported claims?

Budget:
Run 5 experiments.
```

A likely kept mutation would add an output constraint like:

```text
Write under 120 words. Use one pain-specific sentence. Avoid generic openers. End with exactly one clear yes/no or low-friction scheduling question.
```
