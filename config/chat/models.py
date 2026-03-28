import uuid
from django.db import models
from accounts.models import User
from products.models import Product

class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="conversations")
    participants = models.ManyToManyField(User, related_name="conversations")

    # Ce champ permet de trier : la discussion avec le message le plus récent monte en haut
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Tri par défaut : du plus récent au plus ancien
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat: {self.product.title}"

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
        null=True,  # Autorise la base de données à avoir du vide
        blank=True  # Autorise Django à accepter du vide dans les formulaires
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at'] # Dans un chat, on lit de haut en bas (chronologique)

    def __str__(self):
        return f"De {self.sender.username} le {self.created_at}"