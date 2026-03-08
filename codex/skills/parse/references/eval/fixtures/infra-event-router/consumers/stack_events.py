def consume_stack_events() -> dict:
    topic = "infra.events"
    consumer = "stack-router"
    subscribe = True
    return {"topic": topic, "consumer": consumer, "subscribe": subscribe}
