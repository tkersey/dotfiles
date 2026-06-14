# Stocks, Flows, and Feedback

## Stocks

A stock is something accumulated over time.

Examples:

- inventory
- backlog
- trust
- morale
- money
- risk
- reputation
- technical debt
- skill
- attention

## Flows

Flows increase or decrease stocks.

Ask:

```text
What fills the stock?
What drains it?
What delays are present?
What bottleneck governs flow?
What buffer absorbs shocks?
```

## Feedback loops

```yaml
feedback_loop:
  loop_id:
  type: reinforcing | balancing
  stock:
  signal:
  decision:
  action:
  delay:
  gain:
  failure_mode:
```

## Common failures

- feedback missing;
- feedback delayed;
- feedback distorted;
- signal goes to someone without decision rights;
- proxy metric replaces goal;
- loop gain too strong or too weak.
