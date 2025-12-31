# BMAD Trigger Regression Prompts

Use this prompt set to sanity-check when BMAD should or should not trigger.

## Should trigger BMAD
1) "We need to pick between Postgres and DynamoDB. Which is the best fit for a 6-person team and a $1k/month budget?"
2) "Kafka vs RabbitMQ for our event pipeline - what should we choose given 50k msg/sec?"
3) "Is AWS or GCP more appropriate for a bootstrapped SaaS with tight runway?"
4) "We are debating Next.js vs SvelteKit. Which is best for an app-heavy product on a 3-month timeline?"
5) "Help us choose an auth provider with SOC2 and SSO requirements; compare Auth0, Clerk, and Okta."
6) "We want to switch data warehouses. Snowflake vs BigQuery vs Redshift: tradeoffs and lock-in risk?"
7) "Best database for a 2-year roadmap: managed Postgres vs self-hosted - consider migration cost."
8) "We need a message queue. What's most appropriate given a small team and strict SLA?"
9) "Which architecture should we choose: monolith or microservices, given our scale and staffing?"
10) "Do a TCO comparison for hosting on Vercel vs AWS for the next 3 years."

## Should NOT trigger BMAD
1) "Explain what Kafka is and how it works."
2) "Show me how to set up Postgres locally on macOS."
3) "What is vendor lock-in?"
4) "Give me a tutorial on SvelteKit routing."
5) "Summarize the latest AWS announcements."
6) "Fix this TypeScript error in my code."
7) "How do I migrate a database from MySQL to Postgres?"
8) "List the pros and cons of microservices in general."
9) "What are the pricing tiers for Auth0?"
10) "Draft an ADR template for technology decisions."
