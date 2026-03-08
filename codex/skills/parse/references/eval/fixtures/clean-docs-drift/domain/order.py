from repositories.order_repository import load_orders


class Order:
    def load(self) -> list[dict]:
        return load_orders()
