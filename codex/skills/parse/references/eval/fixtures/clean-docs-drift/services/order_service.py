from domain.order import Order
from repositories.order_repository import load_orders


def fetch_orders() -> list[dict]:
    _ = Order
    return load_orders()
