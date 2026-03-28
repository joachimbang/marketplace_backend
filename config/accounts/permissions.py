from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication

def force_authenticate(request):
    """
    Moteur d'authentification centralisé.
    Répare le request.user si DRF l'a laissé en AnonymousUser.
    """
    if request.user and request.user.is_authenticated:
        return True

    auth = JWTAuthentication()
    header = auth.get_header(request)
    if header:
        raw_token = auth.get_raw_token(header)
        try:
            validated_token = auth.get_validated_token(raw_token)
            user = auth.get_user(validated_token)
            if user:
                request.user = user
                return True
        except:
            return False
    return False

# --- CLASSES DE PERMISSIONS FACTORISÉES ---

class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return force_authenticate(request)

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if force_authenticate(request):
            return getattr(request.user, 'role', None) == "admin"
        return False

class IsSeller(BasePermission):
    def has_permission(self, request, view):
        if force_authenticate(request):
            return getattr(request.user, 'is_seller', False)
        return False

class IsBuyer(BasePermission):
    def has_permission(self, request, view):
        if force_authenticate(request):
            return getattr(request.user, 'is_buyer', False)
        return False

class IsOwner(BasePermission):
    """
    Vérifie si l'utilisateur est le propriétaire de l'objet ou un admin.
    """
    def has_permission(self, request, view):
        return force_authenticate(request)

    def has_object_permission(self, request, view, obj):
        if not force_authenticate(request):
            return False

        # Un admin a un droit de regard partout
        if getattr(request.user, 'role', None) == "admin":
            return True

        # Vérifie si l'objet appartient à l'utilisateur (champ 'user' ou 'owner')
        owner = getattr(obj, 'user', getattr(obj, 'owner', None))
        return owner == request.user