from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from accounts.permissions import IsAdmin, IsAuthenticated
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    UpdateUserSerializer,
    VerifyUserSerializer
)

from core_selectors.user_selectors import (
    get_user_by_email,
    get_all_users
)

from services.auth_services import login_user

from utils.api_response import (
    success_response,
    error_response,
    get_serializer_error
)

from accounts.models import User

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
class UserViewSet(viewsets.ViewSet):
    # POST /api/accounts/register/
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def register(self, request):

        data = request.data

        if get_user_by_email(data.get("email")):
            return error_response("Email déjà utilisé.")

        if User.objects.filter(username=data.get("username")).exists():
            return error_response("Nom d'utilisateur déjà utilisé.")

        if data.get("phone") and User.objects.filter(phone=data.get("phone")).exists():
            return error_response("Téléphone déjà utilisé.")

        serializer = RegisterSerializer(data=data)

        if not serializer.is_valid():
            return error_response(get_serializer_error(serializer))

        user = serializer.save()

        return success_response(
            "Utilisateur créé avec succès",
            UserSerializer(user).data,
            status.HTTP_201_CREATED
        )
    # POST /api/accounts/login/
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request):

        email = request.data.get("email")
        password = request.data.get("password")

        result = login_user(email, password)

        if result is None:
            return error_response(
                "Email ou mot de passe incorrect",
                status.HTTP_401_UNAUTHORIZED
            )

        serializer = UserSerializer(result["user"])

        return success_response(
            "Connexion réussie",
            {
                "user": serializer.data,
                "tokens": result["tokens"]
            }
        )


    # GET /api/accounts/profile/
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def profile(self, request):

        serializer = UserSerializer(request.user)

        return success_response(
            "Profil récupéré",
            serializer.data
        )

    # PUT /api/accounts/update_profile/
    @action(detail=False, methods=["put"], permission_classes=[IsAuthenticated])
    def update_profile(self, request):

        serializer = UpdateUserSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return success_response(
                "Profil mis à jour",
                serializer.data
            )

        error_message = get_serializer_error(serializer)
        return error_response(error_message)


    # GET /api/accounts/users/
    @action(detail=False, methods=["get"], permission_classes=[IsAdmin])
    def users(self, request):
        # --- LE FIX DE SECOURS (Si DRF est capricieux) ---
        if request.user.is_anonymous:
            from rest_framework_simplejwt.authentication import JWTAuthentication
            user_auth_tuple = JWTAuthentication().authenticate(request)
            if user_auth_tuple:
                request.user = user_auth_tuple[0]

        print(f"User final: {request.user}") # Pour confirmer dans ton terminal Goma

        # --- LA LOGIQUE DE LA VUE ---
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)

        # TRÈS IMPORTANT : Il faut toujours un RETURN
        return success_response(
            "Liste des utilisateurs récupérée avec succès",
            serializer.data
        )
    # @action(detail=False, methods=["get"], permission_classes=[AllowAny]) # On ouvre tout temporairement

    # def users(self, request):
    #     # Affiche TOUS les headers dans ton terminal Goma
    #     print("--- HEADERS REÇUS ---")
    #     print(f"Authorization: {request.headers.get('Authorization')}")
    #     print(f"User: {request.user}")

    #     token_id = "80581a80-bc6a-4ebc-8c80-6d3ec0f0da8f"
    #     user_exists = User.objects.filter(id=token_id).exists()

    #     print(f"--- DEBUG GOMA ---")
    #     print(f"L'utilisateur existe-t-il en base ? : {user_exists}")
    #     print(f"ID cherché : {token_id}")

    #     users = User.objects.all()
    #     serializer = UserSerializer(users, many=True)
    #     return success_response("Liste des utilisateurs", serializer.data)

    # def users(self, request):
    #     auth = JWTAuthentication()
    #     header = auth.get_header(request)

    #     print("--- DIAGNOSTIC GOMA ---")
    #     if header is None:
    #         print("Erreur: Pas de header Authorization trouvé")
    #     else:
    #         raw_token = auth.get_raw_token(header)
    #         try:
    #             validated_token = auth.get_validated_token(raw_token)
    #             user = auth.get_user(validated_token)
    #             print(f"Utilisateur trouvé par SimpleJWT: {user}")
    #         except Exception as e:
    #             print(f"ÉCHEC AUTHENTIFICATION: {str(e)}")

    #     users = User.objects.all()
    #     serializer = UserSerializer(users, many=True)
    #     return success_response("Liste des utilisateurs", serializer.data)

    # Dans ton ViewSet
    # def users(self, request):
    #     # Si DRF a échoué mais que le token est valide
    #     if request.user.is_anonymous:
    #         from rest_framework_simplejwt.authentication import JWTAuthentication
    #         user_auth_tuple = JWTAuthentication().authenticate(request)
    #         if user_auth_tuple:
    #             request.user = user_auth_tuple[0] # On force l'utilisateur

    #     # Maintenant request.user est admin2@example.com
    #     print(f"User final: {request.user}")
    #



    # PUT /api/accounts/verify_users/
    @action(detail=False, methods=["put"], permission_classes=[IsAdmin])
    def verify_users(self, request):

        user_ids = request.data.get("user_ids")
        user_id = request.data.get("user_id")

        # gérer 1 utilisateur ou plusieurs
        if user_ids:
            ids = user_ids
        elif user_id:
            ids = [user_id]
        else:
            return error_response(
                "Aucun utilisateur spécifié",
                status.HTTP_400_BAD_REQUEST
            )

        users = User.objects.filter(id__in=ids)

        if not users.exists():
            return error_response(
                "Aucun utilisateur trouvé",
                status.HTTP_404_NOT_FOUND
            )

        users.update(is_verified=True)

        serializer = VerifyUserSerializer(users, many=True)

        return success_response(
            "Utilisateurs vérifiés avec succès",
            serializer.data
        )