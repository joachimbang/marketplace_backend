from rest_framework import serializers
from .models import Category, Product, ProductImage, Favorite, CategoryRequest

# ------------------------------
# Category Serializer
# ------------------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

# ------------------------------
# Product Image Serializer
# ------------------------------
class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["id", "image", "image_url"]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            # Construit l'URL complète : http://127.0.0.1:8000/media/
            return request.build_absolute_uri(obj.image.url)
        return None

# ------------------------------
# Product Serializer (Lecture / Liste)
# ------------------------------
class ProductSerializer(serializers.ModelSerializer):
    # Utilise le Serializer corrigé avec image_url
    images = ProductImageSerializer(many=True, read_only=True)
    seller = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "seller", "category", "title", "description",
            "price", "condition", "status", "views_count",
            "created_at", "images", "thumbnail"
        ]

    def get_thumbnail(self, obj):
        """Récupère l'URL de la première image pour les listes de produits"""
        first_image = obj.images.first()
        request = self.context.get('request')
        if first_image and request:
            return request.build_absolute_uri(first_image.image.url)
        return None

# ------------------------------
# Product Create/Update Serializer
# ------------------------------
class ProductCreateSerializer(serializers.ModelSerializer):
    # Champ pour recevoir une liste de fichiers images
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Product
        fields = [
            "id", "category", "title", "description",
            "price", "condition", "images"
        ]

    def create(self, validated_data):
        # On retire les images pour créer le produit d'abord
        images_data = validated_data.pop("images", [])

        # Le vendeur est récupéré directement depuis la requête (Token)
        user = self.context["request"].user
        product = Product.objects.create(seller=user, **validated_data)

        # Création des images liées en une seule requête SQL (Performance GEC)
        image_objects = [
            ProductImage(product=product, image=image)
            for image in images_data
        ]
        ProductImage.objects.bulk_create(image_objects)

        return product

# ------------------------------
# Autres Serializers (Inchangés mais vérifiés)
# ------------------------------
class CategoryRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryRequest
        fields = ["id", "user", "requested_name", "status", "reason", "created_at", "updated_at"]
        read_only_fields = ["user", "status", "created_at", "updated_at"]

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ["id", "product", "created_at"]