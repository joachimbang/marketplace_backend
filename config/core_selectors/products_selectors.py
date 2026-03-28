from products.models import Category, Product


def get_all_products():

    return (
        Product.objects
        # Utilisation de select_related pour les relations ForeignKey (seller, category)
        .select_related("seller", "category")
        # Utilisation de prefetch_related pour les relations ManyToMany ou reverse ForeignKey (images)
        .prefetch_related("images")
        .order_by("-created_at")
    )

def get_all_categories():
    return (
        Category.objects
        .all()
        .order_by("-created_at")
    )

def get_product_by_id(product_id):

    return (
        Product.objects
        .select_related("seller", "category")
        .prefetch_related("images")
        .filter(id=product_id)
        .first()
    )


def get_products_by_user(user):

    return (
        Product.objects
        .select_related("seller", "category")
        .prefetch_related("images")
        .filter(seller=user)
    )