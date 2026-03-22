from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """Autorise uniquement les utilisateurs connectés avec le rôle admin"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"

class IsSeller(BasePermission):
    """Autorise uniquement les utilisateurs connectés avec le rôle seller"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "seller"

class IsBuyer(BasePermission):
    """Autorise uniquement les utilisateurs connectés avec le rôle buyer"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "buyer"

class IsOwner(BasePermission):
    """Autorise uniquement le propriétaire de l'objet"""
    def has_object_permission(self, request, view, obj):
        # Vérifie aussi que l'utilisateur est connecté
        return request.user.is_authenticated and obj.user == request.user