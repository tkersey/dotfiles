from repositories.user_repository import load_user


def fetch_user(user_id: str) -> dict:
    return load_user(user_id)
