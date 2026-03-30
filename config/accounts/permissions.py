from rest_framework.permissions import BasePermission

class IsAuthenticated(BasePermission):
    message = "Authentification requise."
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

class IsAdmin(BasePermission):
    message = "Accès refusé : Vous n'avez pas le rôle administrateur."

    def has_permission(self, request, view):
        print("--- TENTATIVE DE PERMISSION ADMIN ---") # Si ça n'affiche rien, authentication_classes manque dans la view

        if not (request.user and request.user.is_authenticated):
            print("ECHEC: Utilisateur non authentifié")
            return False

        user_role = str(getattr(request.user, 'role', "")).strip().lower()
        print(f"DEBUG: User={request.user.email} | Role={user_role}")

        return user_role == "admin"

class IsSeller(BasePermission):
    message = "Accès refusé : Réservé aux vendeurs."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        # Utilise soit le champ 'role', soit le booléen selon ton modèle User
        return getattr(request.user, 'is_seller', False) or getattr(request.user, 'role', None) == "seller"

class IsBuyer(BasePermission):
    message = "Accès refusé : Réservé aux acheteurs."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return getattr(request.user, 'is_buyer', False) or getattr(request.user, 'role', None) == "buyer"

class IsOwner(BasePermission):
    message = "Accès refusé : Vous n'êtes pas le propriétaire de cet objet."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Un admin peut tout voir
        if getattr(request.user, 'role', None) == "admin":
            return True

        # On vérifie dynamiquement si l'objet appartient à l'user
        owner = getattr(obj, 'user', getattr(obj, 'owner', getattr(obj, 'sender', None)))
        return owner == request.user