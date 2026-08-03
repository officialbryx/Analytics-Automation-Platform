from social_core.exceptions import AuthForbidden
from django.contrib.auth import get_user_model

def validate_user(strategy, details, backend, response, user=None, *args, **kwargs):
    """
    Validates the user during the authentication process.

    Args:
        strategy (object): The authentication strategy.
        details (dict): The user details.
        backend (object): The authentication backend.
        response (dict): The authentication response.
        user (object, optional): The user object. Defaults to None.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Raises:
        AuthForbidden: If the user's email is not allowed.
    """
    Users = get_user_model()

    if not Users.objects.filter(email=response["email"]).exists():
        raise AuthForbidden(backend)
