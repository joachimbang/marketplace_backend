from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from accounts.permissions import IsAdmin, IsAuthenticated
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    UpdateUserSerializer,
    VerifyUserSerializer
)
from core_selectors.user_selectors import get_user_by_email
from services.auth_services import login_user
from utils.api_response import (
    success_response,
    error_response,
    get_serializer_error
)
from accounts.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication

class UserViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]

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
            return error_response("Email ou mot de passe incorrect", status.HTTP_401_UNAUTHORIZED)

        serializer = UserSerializer(result["user"])
        return success_response(
            "Connexion réussie",
            {
                "user": serializer.data,
                "tokens": result["tokens"]
            }
        )

        # POST /api/accounts/logout/
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return error_response("Le refresh token est requis", status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return success_response("Déconnexion réussie")
        except TokenError:
            return error_response("Token invalide ou déjà expiré", status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return error_response(f"Une erreur est survenue: {str(e)}", status.HTTP_400_BAD_REQUEST)

    # GET /api/accounts/profile/
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def profile(self, request):
        serializer = UserSerializer(request.user)
        return success_response("Profil récupéré", serializer.data)

    # PUT /api/accounts/update_profile/
    @action(detail=False, methods=["put"], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        serializer = UpdateUserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response("Profil mis à jour", serializer.data)

        return error_response(get_serializer_error(serializer))

    # GET /api/accounts/list-users/
    @action(detail=False, methods=["get"], url_path="list-users", permission_classes=[IsAdmin])
    def users(self, request):
        """
        Liste tous les utilisateurs pour l'Admin.
        """
        # On affiche ce que l'API voit REELLEMENT
        print(f"--- DIAGNOSTIC ---")
        print(f"User: {request.user.email}")
        print(f"Role brut: '{request.user.role}'")
        print(f"Est admin ?: {request.user.role == 'admin'}")
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return success_response("Liste des utilisateurs récupérée avec succès", serializer.data)

    # PUT /api/accounts/verify_users/
    @action(detail=False, methods=["put"], permission_classes=[IsAdmin])
    def verify_users(self, request):
        user_ids = request.data.get("user_ids")
        user_id = request.data.get("user_id")

        if user_ids:
            ids = user_ids
        elif user_id:
            ids = [user_id]
        else:
            return error_response("Aucun utilisateur spécifié", status.HTTP_400_BAD_REQUEST)

        users = User.objects.filter(id__in=ids)
        if not users.exists():
            return error_response("Aucun utilisateur trouvé", status.HTTP_404_NOT_FOUND)

        users.update(is_verified=True)
        serializer = VerifyUserSerializer(users, many=True)
        return success_response("Utilisateurs vérifiés avec succès", serializer.data)