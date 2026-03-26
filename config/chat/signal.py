from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message

@receiver(post_save, sender=Message)
def update_conversation_timestamp(sender, instance, created, **kwargs):
    """
    À chaque fois qu'un nouveau message est enregistré,
    on force la mise à jour du champ 'updated_at' de la conversation.
    """
    if created:
        conversation = instance.conversation
        # .save() mettra à jour le champ auto_now=True de la Conversation
        conversation.save()