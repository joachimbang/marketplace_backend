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

    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)

    is_verified = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email