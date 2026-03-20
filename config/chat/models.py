from django.db import models
from accounts.models import User
from products.models import Product


class Message(models.Model):

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")

    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    content = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)