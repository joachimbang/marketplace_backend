import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    ROLE_CHOICES = (
        ("buyer", "Buyer"),
        ("seller", "Seller"),
        ("admin", "Admin"),
    )

    email = models.EmailField(unique=True)

    username = models.CharField(max_length=150)

    phone = models.CharField(max_length=20, blank=True)

    avatar = models.ImageField(upload_to="avatars/", blank=True)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
    )

    is_verified = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()
    # Set email as the unique identifier for authentication instead of username
    USERNAME_FIELD = "email"
    # Make username a required field when creating a user
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    @property
    def is_active(self):
        return True # Nécessaire pour que le token soit reconnu

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_seller(self):
        return self.role == "seller"

    @property
    def is_buyer(self):
        return self.role == "buyer"

    # Pour la compatibilité interne Django (Admin/Permissions)
    @property
    def is_staff(self):
        return self.is_admin