from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, PermissionDenied
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from utils.api_response import error_response


def custom_exception_handler(exc, context):

    # récupérer la réponse par défaut de DRF
    response = exception_handler(exc, context)

    # erreurs JWT
    if isinstance(exc, (InvalidToken, TokenError)):
        return error_response(
            "Session expirée ou token invalide",
            code=401
        )

    # utilisateur non connecté
    if isinstance(exc, NotAuthenticated):
        return error_response(
            "Authentification requise",
            code=401
        )

    # erreur login
    if isinstance(exc, AuthenticationFailed):
        return error_response(
            "Email ou mot de passe incorrect",
            code=401
        )

    # accès refusé
    if isinstance(exc, PermissionDenied):
        return error_response(
            "Accès refusé",
            code=403
        )

    # autres erreurs DRF
    if response is not None:

        message = None

        if isinstance(response.data, dict):

            # cas {"detail": "..."}
            if "detail" in response.data:
                message = response.data["detail"]

            # cas erreurs serializer
            else:
                field = list(response.data.keys())[0]
                message = response.data[field][0]

        if not message:
            message = "Une erreur est survenue"

        return error_response(message, response.status_code)

    return response