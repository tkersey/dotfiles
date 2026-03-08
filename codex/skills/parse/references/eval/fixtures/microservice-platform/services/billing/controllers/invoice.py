from services.invoice_service import fetch_invoices


def list_invoices(account_id: str) -> list[dict]:
    return fetch_invoices(account_id)
