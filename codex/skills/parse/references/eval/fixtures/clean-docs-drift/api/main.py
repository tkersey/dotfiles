from controllers.orders import list_orders


def handle() -> list[dict]:
    return list_orders()
