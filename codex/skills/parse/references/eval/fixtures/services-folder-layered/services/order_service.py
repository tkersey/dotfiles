from repositories.order_repository import load_orders


def fetch_orders() -> list[dict]:
    return load_orders()
