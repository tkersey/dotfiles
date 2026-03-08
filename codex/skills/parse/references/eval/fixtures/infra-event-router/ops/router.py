from consumers.stack_events import consume_stack_events
from publishers.notify import publish_event


def route() -> None:
    publish_event(consume_stack_events())
