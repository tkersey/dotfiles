from services.user_service import fetch_user


def get_user(user_id: str) -> dict:
    return fetch_user(user_id)
