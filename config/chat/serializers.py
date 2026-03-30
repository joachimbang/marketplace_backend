from rest_framework import serializers
from .models import Conversation, Message
from accounts.models import User
from products.models import Product

class ConversationListSerializer(serializers.ModelSerializer):
    other_participant = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    product_details = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'other_participant', 'last_message', 'product_details', 'updated_at']

    def get_other_participant(self, obj):
        # On récupère l'utilisateur qui n'est pas "moi" (l'utilisateur connecté)
        request_user = self.context['request'].user
        other = obj.participants.exclude(id=request_user.id).first()
        if other:
            return {
                "id": other.id,
                "username": other.username,
                "avatar": other.profile_picture.url if hasattr(other, 'profile_picture') and other.profile_picture else None
            }
        return None

    def get_last_message(self, obj):
        # On récupère le tout dernier message de cette conversation
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return {
                "content": last_msg.content,
                "sender_id": last_msg.sender.id,
                "created_at": last_msg.created_at,
                "is_read": last_msg.is_read
            }
        return None

    def get_product_details(self, obj):
        return {
            "id": obj.product.id,
            "title": obj.product.title,
            "price": obj.product.price
        }
class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.ReadOnlyField(source='sender.username')
    is_me = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_username', 'content', 'is_me', 'is_read', 'created_at']

    def get_is_me(self, obj):
        # Permet à Flutter de savoir s'il doit afficher la bulle à droite ou à gauche
        return obj.sender == self.context['request'].user