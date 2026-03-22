from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


def generate_tokens(user):

    refresh = RefreshToken.for_user(user)
    refresh["email"] = user.email
    refresh["role"] = user.role

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token)
    }


def login_user(email, password):

    user = authenticate(email=email, password=password)

    if user is None:
        return None

    tokens = generate_tokens(user)

    return {
        "user": user,
        "tokens": tokens
    }