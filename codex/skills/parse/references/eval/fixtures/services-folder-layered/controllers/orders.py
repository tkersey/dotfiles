from services.order_service import fetch_orders


def list_orders() -> list[dict]:
    return fetch_orders()
