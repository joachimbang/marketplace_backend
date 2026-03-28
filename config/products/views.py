# to do next: create endpoint to delete category,image

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from accounts.permissions import IsSeller, IsAdmin

from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductCreateSerializer,
    CategoryRequestSerializer,
    ProductImageSerializer
)

from core_selectors.products_selectors import (
    get_all_categories,
    get_all_products,
    get_product_by_id,
    get_products_by_user
)

from services.products_services import (
    create_product,
    update_product,
    delete_product
)

from utils.api_response import success_response, error_response, get_serializer_error

from .models import CategoryRequest, Category, ProductImage


class ProductViewSet(viewsets.ViewSet):
    """
    ViewSet pour gérer les produits, images et catégories.
    """

    # =========================
    # ADMIN - CATEGORIES
    # =========================

    @action(detail=False, methods=["post"], permission_classes=[IsAdmin])
    def create_category(self, request):
        """
        POST /api/products/create_category/
        Gère la création d'une seule catégorie ou d'une liste de catégories.
        """
        data = request.data

        # Déterminer si on manipule une liste ou un objet unique
        is_many = isinstance(data, list)

        # Initialisation du serializer avec l'argument many dynamique
        serializer = CategorySerializer(data=data, many=is_many)

        if not serializer.is_valid():
            return error_response(
                get_serializer_error(serializer),
                status.HTTP_400_BAD_REQUEST
            )

        # Sauvegarde (crée un objet ou une liste d'objets)
        categories = serializer.save()

        # On renvoie la réponse en utilisant many=is_many pour éviter l'AttributeError
        return success_response(
            "Catégorie(s) créée(s) avec succès",
            CategorySerializer(categories, many=is_many).data,
            status.HTTP_201_CREATED
        )

    # ========================
    #  GET ALL CATEGORIES
    # ========================
    #
    @action(detail=False, methods=["get"],url_path="list_categories", permission_classes=[AllowAny])
    def list_categories(self, request):
        categories = get_all_categories()
        serializer = CategorySerializer(categories, many=True)
        return success_response("Liste des catégories", serializer.data)

    # =========================
    # PRODUITS PUBLICS
    # =========================

    @action(detail=False, methods=["get"], url_path="list", permission_classes=[AllowAny])
    def list_products(self, request):
        """
        GET /api/products/list/
        Liste tous les produits.
        """
        products = get_all_products()
        # On ajoute le contexte ici aussi pour que les images s'affichent dans la liste
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return success_response("Liste des produits", serializer.data)

    @action(detail=False, methods=["get"], url_path="detail/(?P<product_id>[^/.]+)")
    def product(self, request, product_id):
        """
        GET /api/products/detail/{id}/
        Détail d’un produit.
        """
        product = get_product_by_id(product_id)

        if not product:
            return error_response("Produit introuvable", status.HTTP_404_NOT_FOUND)

        # ✅ Le contexte est crucial pour générer les URLs d'images
        serializer = ProductSerializer(product, context={'request': request})
        return success_response("Produit récupéré", serializer.data)

    # =========================
    # PRODUITS (SELLER)
    # =========================

    @action(detail=False, methods=["post"], permission_classes=[IsSeller])
    def create_product(self, request):
        """
        POST /api/products/create/
        Créer un produit avec images.
        """
        print("Received data:", request.data)  # Debug print
        serializer = ProductCreateSerializer(
            data=request.data,
            context={"request": request}
        )

        if not serializer.is_valid():
            return error_response(get_serializer_error(serializer))

        product = create_product(request.user, serializer.validated_data)

        return success_response(
            "Produit créé avec succès",
            ProductSerializer(product).data,
            status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["put"], url_path="update/(?P<product_id>[^/.]+)", permission_classes=[IsSeller])
    def update_product(self, request, product_id):
        """
        PUT /api/products/update/{id}/
        Modifier un produit.
        """
        product = get_product_by_id(product_id)

        if not product:
            return error_response("Produit introuvable", status.HTTP_404_NOT_FOUND)

        if product.seller != request.user:
            return error_response("Permission refusée", status.HTTP_403_FORBIDDEN)

        serializer = ProductCreateSerializer(
            product,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if not serializer.is_valid():
            return error_response(get_serializer_error(serializer))

        product = update_product(product, serializer.validated_data)

        return success_response(
            "Produit mis à jour",
            ProductSerializer(product).data
        )

    @action(detail=False, methods=["delete"], url_path="delete/(?P<product_id>[^/.]+)", permission_classes=[IsSeller])
    def delete_product(self, request, product_id):
        """
        DELETE /api/products/delete/{id}/
        Supprimer un produit.
        """
        product = get_product_by_id(product_id)

        if not product:
            return error_response("Produit introuvable", status.HTTP_404_NOT_FOUND)

        if product.seller != request.user:
            return error_response("Permission refusée", status.HTTP_403_FORBIDDEN)

        delete_product(product)

        return success_response("Produit supprimé")

    @action(detail=False, methods=["get"],url_path="my-products", permission_classes=[IsSeller])
    def my_products(self, request):
        """
        GET /api/products/my-products/
        Produits du vendeur.
        """
        products = get_products_by_user(request.user)

        return success_response(
            "Produits du vendeur",
            ProductSerializer(products, many=True).data
        )
    # =========================
    #           IMAGES
    # =========================

    @action(detail=False, methods=["post"], permission_classes=[IsSeller])
    def add_images(self, request):
        product_id = request.data.get("product_id")
        # On utilise spécifiquement request.FILES pour les fichiers
        images = request.FILES.getlist("images")

        if not product_id:
            return error_response("product_id requis")

        if not images:
            return error_response("Aucune image reçue dans le champ 'images'")

        product = get_product_by_id(product_id)

        if not product:
            return error_response("Produit introuvable", status.HTTP_404_NOT_FOUND)

        if product.seller != request.user:
            return error_response("Permission refusée", status.HTTP_403_FORBIDDEN)

        # Création classique pour plus de sécurité que bulk_create
        created_count = 0
        for image in images:
            ProductImage.objects.create(product=product, image=image)
            created_count += 1

        return success_response(f"{created_count} image(s) ajoutée(s) avec succès")

    # =========================
    # CATEGORY REQUEST
    # =========================

    @action(detail=False, methods=["post"], permission_classes=[IsSeller])
    def request_category(self, request):
        """
        POST /api/products/request-category/
        Demande de nouvelle catégorie.
        """
        requested_name = request.data.get("requested_name")

        if not requested_name:
            return error_response("Veuillez fournir un nom de catégorie")

        category_request = CategoryRequest.objects.create(
            user=request.user,
            requested_name=requested_name
        )

        return success_response(
            "Demande envoyée",
            CategoryRequestSerializer(category_request).data
        )

    # =========================
    # ADMIN - VALIDATION
    # =========================

    @action(detail=False, methods=["get"], permission_classes=[IsAdmin])
    def pending_category_requests(self, request):
        """
        GET demandes en attente
        """
        requests = CategoryRequest.objects.filter(status="pending")

        return success_response(
            "Demandes en attente",
            CategoryRequestSerializer(requests, many=True).data
        )

    @action(detail=False, methods=["put"], url_path="verify-category-request/(?P<request_id>[^/.]+)", permission_classes=[IsAdmin])
    def verify_category_request(self, request, request_id):
        """
        Admin accepte ou refuse une demande.
        """
        category_request = CategoryRequest.objects.filter(
            id=request_id,
            status="pending"
        ).first()

        if not category_request:
            return error_response("Demande introuvable", status.HTTP_404_NOT_FOUND)

        status_action = request.data.get("status")
        reason = request.data.get("reason", "")

        if status_action not in ["approved", "rejected"]:
            return error_response("Status invalide")

        if status_action == "rejected" and not reason:
            return error_response("Raison obligatoire pour refus")

        # ✅ CORRECTION ICI
        if status_action == "approved":
            Category.objects.create(
                name=category_request.requested_name,
                slug=category_request.requested_name.lower().replace(" ", "-")
            )

        category_request.status = status_action
        category_request.reason = reason
        category_request.save()

        return success_response(
            "Demande traitée",
            CategoryRequestSerializer(category_request).data
        )