from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet  # <--- Importe la VIEW, pas le Serializer

router = DefaultRouter()
# ERREUR PROBABLE : tu avais mis ConversationListSerializer ici
router.register(r'', ConversationViewSet, basename='conversations')

urlpatterns = [
    path('', include(router.urls)),
]