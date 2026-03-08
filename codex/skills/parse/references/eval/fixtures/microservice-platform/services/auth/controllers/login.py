from services.login_service import login_user


def login(user_id: str) -> dict:
    return login_user(user_id)
