from django.urls import path, include
from django.conf.urls.static import static
from . import settings

urlpatterns = [

    path("api/accounts/", include("accounts.urls")),

    path("api/products/", include("products.urls")),

]

# Cette ligne permet d'accéder aux images via ton navigateur ou ton app mobile
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)