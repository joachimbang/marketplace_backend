from django.db import models
from accounts.models import User

# Create your models here.
# Category model
class Category(models.Model):

    name = models.CharField(max_length=100)

    slug = models.SlugField(unique=True)

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Product model
class Product(models.Model):

    CONDITION_CHOICES = (
        ("new", "New"),
        ("used", "Used"),
        ("refurbished", "Refurbished"),
    )

    STATUS_CHOICES = (
        ("available", "Available"),
        ("sold", "Sold"),
        ("inactive", "Inactive"),
    )

    seller = models.ForeignKey(User, on_delete=models.CASCADE)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)

    description = models.TextField()

    price = models.DecimalField(max_digits=10, decimal_places=2)

    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")

    views_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# Product images
class ProductImage(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    image = models.ImageField(upload_to="products/")

    created_at = models.DateTimeField(auto_now_add=True)

# Favorite model
class Favorite(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)