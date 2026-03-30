from django.urls import path, include
from django.conf.urls.static import static
from . import settings
# Ajoute cet import pour récupérer les vues de rafraîchissement
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Route pour obtenir un nouvel Access Token à partir du Refresh Token
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("api/accounts/", include("accounts.urls")),
    path("api/products/", include("products.urls")),
    path("api/chat/", include("chat.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)