from products.models import Product, ProductImage


def create_product(user, validated_data):

    images = validated_data.pop("images", [])

    product = Product.objects.create(
        seller=user,
        **validated_data
    )

    image_objects = [
        ProductImage(product=product, image=image)
        for image in images
    ]

    ProductImage.objects.bulk_create(image_objects)

    return product


def update_product(product, validated_data):

    images = validated_data.pop("images", None)

    for attr, value in validated_data.items():
        setattr(product, attr, value)

    product.save()

    if images:
        ProductImage.objects.filter(product=product).delete()

        image_objects = [
            ProductImage(product=product, image=image)
            for image in images
        ]

        ProductImage.objects.bulk_create(image_objects)

    return product


def delete_product(product):

    product.delete()