from controllers.user_controller import get_user


def handle_request(user_id: str) -> dict:
    return get_user(user_id)
