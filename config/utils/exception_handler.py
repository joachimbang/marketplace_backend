# from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, PermissionDenied
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from utils.api_response import error_response

# 1. LA CLASSE ADAPTATRICE (Le "Garde" intelligent)
class SafeJWTAuthentication(JWTAuthentication):
    """
    Cette classe intercepte les erreurs brutes de SimpleJWT
    pour les transformer en exceptions que DRF peut traiter.
    """
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except InvalidToken as e:
            # On extrait le message interne (ex: "Token is expired")
            # pour le passer au handler
            detail = e.args[0] if e.args else "Invalid token"
            raise AuthenticationFailed(detail=detail)

# 2. LE GESTIONNAIRE D'EXCEPTIONS (Le "Réceptionniste")
def custom_exception_handler(exc, context):
    from rest_framework.views import exception_handler
    # On récupère la réponse brute de DRF
    response = exception_handler(exc, context)

    # Debug
    print(f"--- EXCEPTION DIAGNOSTIC ---")
    print(f"Type: {type(exc)}")
    print(f"Detail: {str(exc)}")

    # Gestion des erreurs de Token (via SafeJWT ou direct)
    if isinstance(exc, (InvalidToken, TokenError, AuthenticationFailed)):
        message = "Session expirée ou jeton invalide"

        # On fouille dans la structure complexe de SimpleJWT si elle existe
        if response is not None and isinstance(response.data, dict):
            # Cas A : Structure avec liste 'messages'
            jwt_messages = response.data.get("messages", [])
            if jwt_messages and isinstance(jwt_messages, list):
                detail_msg = jwt_messages[0].get("message", "").lower()
                if "expired" in detail_msg:
                    message = "Votre session a expiré, veuillez vous reconnecter."
                elif "invalid" in detail_msg:
                    message = "Token invalide ou corrompu."

            # Cas B : Message direct dans 'detail' (venant de SafeJWT)
            elif "detail" in response.data:
                detail_str = str(response.data["detail"]).lower()
                if "expired" in detail_str:
                    message = "Votre session a expiré, veuillez vous reconnecter."
                elif "invalid" in detail_str:
                    message = "Token invalide."

        return error_response(message, code=401)

    # Utilisateur non connecté
    if isinstance(exc, NotAuthenticated):
        return error_response("Authentification requise pour cette action.", code=401)

    # Accès refusé (Permissions IsAdmin, IsOwner, etc.)
    if isinstance(exc, PermissionDenied):
        return error_response(str(exc), code=403)

    # Gestion générique (Validation de formulaires / serializers)
    if response is not None:
        message = "Une erreur est survenue"
        if isinstance(response.data, dict):
            if "detail" in response.data:
                message = response.data["detail"]
            else:
                # On prend la première erreur de champ
                try:
                    field = list(response.data.keys())[0]
                    error_val = response.data[field]
                    message = error_val[0] if isinstance(error_val, list) else error_val
                except:
                    pass

        return error_response(str(message), code=response.status_code)

    return response