# AI Slop Patterns — Complete Reference

## Table of Contents
- [Emdash Patterns](#emdash-patterns)
- [Here's Why Family](#heres-why-family)
- [Contrast Formulas](#contrast-formulas)
- [Forced Enthusiasm](#forced-enthusiasm)
- [Pseudo-Profound Openers](#pseudo-profound-openers)
- [Unnecessary Hedges](#unnecessary-hedges)
- [Integration with Workflow](#integration-with-workflow)

---

## Emdash Patterns

LLMs use emdashes disproportionately. Consider alternatives:

| Original | Alternatives |
|----------|--------------|
| `X—Y—Z` | `X; Y; Z` or `X, Y, Z` |
| `The tool—which is powerful—works well` | `The tool, which is powerful, works well` |
| `We built this—and it works` | `We built this, and it works` |
| `Here's the thing—it matters` | `Here's the thing: it matters` or recast entirely |

Sometimes the best fix is to split into two sentences or restructure entirely.

---

## "Here's Why" Family

These should be eliminated or recast:

| Pattern | Fix |
|---------|-----|
| "Here's why" | Just explain why directly |
| "Here's why it matters" | Explain the importance inline |
| "Here's the thing" | Usually can be deleted entirely |
| "Here's what you need to know" | Just tell them |

---

## Contrast Formulas

| Pattern | Fix |
|---------|-----|
| "It's not X, it's Y" | "This is Y" or explain differently |
| "It's not just X, it's also Y" | "This does X and Y" |
| "It's not about X, it's about Y" | Just explain Y |

---

## Forced Enthusiasm

| Pattern | Fix |
|---------|-----|
| "Let's dive in!" | Just start |
| "Let's get started!" | Just start |
| "Excited to share..." | Just share it |
| "We're thrilled to announce..." | Just announce it |
| "Get ready to..." | Just tell them what to do |

---

## Pseudo-Profound Openers

| Pattern | Fix |
|---------|-----|
| "At its core..." | Usually can be deleted |
| "Fundamentally..." | Often unnecessary |
| "In essence..." | Just say the essence |
| "At the end of the day..." | Delete or recast |
| "When it comes to..." | Delete or recast |

---

## Unnecessary Hedges

| Pattern | Fix |
|---------|-----|
| "It's worth noting that..." | Just note it |
| "It's important to remember..." | Just state the fact |
| "Keep in mind that..." | Often deletable |
| "It should be noted that..." | Just note it |
| "It goes without saying..." | Then don't say it |

---

## Integration with Workflow

### As Part of Bead Workflow

```bash
br create "De-slopify README.md" -t docs -p 3
br create "De-slopify API documentation" -t docs -p 3
```

### As Final Pass Before Commit

```
Now, before we commit, please read through README.md and look for any telltale
signs of "AI slop" style writing...
```

### Files to Check

- README.md
- CONTRIBUTING.md
- API documentation
- Blog posts
- Any public-facing text

---

## When to Keep Patterns

Some things are fine even if they seem "AI-like":

- **Technical accuracy** — Don't sacrifice correctness for style
- **Necessary structure** — Headers, lists, etc. are fine
- **Clear explanations** — Being thorough isn't slop
- **Code examples** — Focus on prose, not code
- **Occasional emdash** — One or two per document is fine
