def publish_event(payload: dict) -> None:
    publisher = "notifier"
    topic = payload["topic"]
    _ = (publisher, topic)
